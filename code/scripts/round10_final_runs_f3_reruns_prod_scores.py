"""Round 10, track final-runs, F3 open points 3 and 4 (plan, section 5d.6): checks and prediction scores of the production
reruns, from the outputs of the unchanged F2 aggregators.

usage: round10_final_runs_f3_reruns_prod_scores.py <clone> <base> <out_dir>
Reads <out_dir>/aggregate_boot (round10_final_runs_f2_aggregate.py over <base>/F3/reruns/boot) and
<out_dir>/aggregate_limits_norm_refit (round10_final_runs_f2_limits_aggregate.py over <base>/F3/reruns/limits), the
committed F2 regime A summary and limits summary, and every part's boot_check.json and PROVENANCE.txt.
Checks: every bootstrap part COMPLETED with boot_check pass; the analytic rows of the bootstrap aggregate equal the
committed F2 summary rows of the same cells (the parts together cover every gene of the 30 units); every limits part
COMPLETED and the norm_refit limits cells match regime A's populations.
Item 3 prediction: each bootstrap arm's median coverage in a (task, scale, estimand, n_L) cell is within 0.02 of
uni_v2's in at least 0.8 of cells. Cells are those where uni_v2 has the arm; the share is given per arm over both
encoders (the clause), and per arm and encoder. Held if every arm reaches 0.8, partly held if some do, refuted if none.
Item 4 prediction: on norm_refit the ranking of the limits arms by median coverage at n = 4 and n = 8 is the one F2
found on the other scales (r07 of the F2 report tables: median over cells of each arm's median coverage), with
Kluger's cluster bootstrap lowest at n = 4. Ranks use the 'min' method, so arms with equal medians share a rank.
Held if both rankings are identical and Kluger is lowest at n = 4; partly held if only the Kluger clause holds or only
the rankings agree; refuted otherwise. The same is given against F2's HEST tasks only, and without the cells with
G - n_L = 1. Writes f3_prod_scores.json first, then the tables.
"""
import glob, json, os, sys
import numpy as np, pandas as pd

clone, base, out = sys.argv[1:4]
F2c = os.path.join(clone, 'results/round10/final_runs/F2')
K = ['task', 'encoder', 'scale', 'estimand', 'n']
summ = {}
sp = os.path.join(out, 'f3_prod_scores.json')
dump = lambda: json.dump(summ, open(sp, 'w'), indent=1, default=str)
dump()
rd = lambda p: pd.read_csv(p, float_precision='round_trip')


def status(d):
    p = os.path.join(d, 'PROVENANCE.txt')
    if not os.path.exists(p):
        return 'missing'
    return next((l.split(':', 1)[1].strip() for l in open(p) if l.startswith('status:')), 'no status')


# ------------------------------------------------------------------ item 3
parts = sorted(glob.glob(os.path.join(base, 'F3/reruns/boot', '*')))
rows = []
for d in parts:
    bc = os.path.join(d, 'check', 'boot_check.json')
    b = json.load(open(bc)) if os.path.exists(bc) else {}
    rows.append(dict(part=os.path.basename(d), status=status(d), check_pass=b.get('pass'), analytic_identical=b.get('analytic_identical'),
                     boot_complete=b.get('boot_complete'), boot_rows=b.get('new_boot_rows'), analytic_rows=b.get('new_analytic_rows')))
P = pd.DataFrame(rows); P.to_csv(os.path.join(out, 'f3_boot_parts.csv'), index=False)
summ['item3_parts'] = dict(parts=len(P), completed=int((P.status == 'COMPLETED').sum()), check_pass=int((P.check_pass == True).sum()),
                           boot_rows=int(P.boot_rows.fillna(0).sum()), analytic_rows=int(P.analytic_rows.fillna(0).sum()))
A = rd(os.path.join(out, 'aggregate_boot', 'f2_regimeA_summary.csv'))
F = rd(os.path.join(F2c, 'aggregate', 'f2_regimeA_summary.csv.gz'))
an = A[A.variance != 'boot']
ref = F.merge(an[K].drop_duplicates(), on=K)
ref = ref[ref.variance != 'boot']
m = an.merge(ref, on=K + ['arm', 'variance'], how='outer', suffixes=('', '_f2'), indicator=True)
num = ['G', 'genes', 'R', 'median_coverage', 'q10_coverage', 'q90_coverage', 'median_width', 'median_rmse', 'median_frac_no_interval', 'median_ev_over_var']
both = m[m._merge == 'both']
d = max(float(np.nanmax(np.abs(both[c].to_numpy(float) - both[c + '_f2'].to_numpy(float)))) if len(both) else 0.0 for c in num)
nan_eq = all(bool((both[c].isna() == both[c + '_f2'].isna()).all()) for c in num)
summ['item3_analytic_vs_F2'] = dict(rows=len(an), rows_f2=len(ref), unmatched=int((m._merge != 'both').sum()), max_abs_diff=d, nan_pattern_equal=nan_eq,
                                    cells=int(len(an[K].drop_duplicates())), tasks=sorted(an.task.unique().tolist()))
dump()
bo = A[A.variance == 'boot']
uv = F[(F.variance == 'boot') & (F.encoder == 'uni_v2')]
C = ['task', 'scale', 'estimand', 'n', 'arm']
cmp_ = bo[C + ['encoder', 'genes', 'median_coverage']].merge(uv[C + ['genes', 'median_coverage']], on=C, how='left', suffixes=('', '_uni_v2'))
cmp_['d_cov'] = cmp_.median_coverage - cmp_.median_coverage_uni_v2
cmp_['within_002'] = cmp_.d_cov.abs() <= 0.02
cmp_.to_csv(os.path.join(out, 'f3_boot_vs_uni_v2.csv'), index=False)
cc = cmp_.dropna(subset=['median_coverage_uni_v2'])
by_arm = cc.groupby('arm').agg(cells=('within_002', 'size'), share_within_002=('within_002', 'mean'), median_d=('d_cov', 'median'),
                               max_abs_d=('d_cov', lambda s: float(s.abs().max()))).reset_index()
by_ae = cc.groupby(['arm', 'encoder']).agg(cells=('within_002', 'size'), share_within_002=('within_002', 'mean'), median_d=('d_cov', 'median')).reset_index()
by_task = cc.groupby(['arm', 'task']).agg(cells=('within_002', 'size'), share_within_002=('within_002', 'mean'), median_d=('d_cov', 'median')).reset_index()
pd.concat([by_arm.assign(level='arm'), by_ae.assign(level='arm_encoder'), by_task.assign(level='arm_task')], ignore_index=True).to_csv(
    os.path.join(out, 'f3_boot_score_table.csv'), index=False)
ok = (by_arm.share_within_002 >= 0.8)
summ['item3_prediction'] = dict(text="each bootstrap arm's median coverage in a (task, scale, estimand, n_L) cell is within 0.02 of uni_v2's in at least 0.8 of cells",
                                cells_without_uni_v2=int(cmp_.median_coverage_uni_v2.isna().sum()),
                                by_arm=by_arm.to_dict('records'),
                                verdict='held' if ok.all() else ('partly held' if ok.any() else 'refuted'))
dump()
# ------------------------------------------------------------------ item 4
LU = rd(os.path.join(out, 'aggregate_limits_norm_refit', 'f2_limits_units.csv'))
LC = json.load(open(os.path.join(out, 'aggregate_limits_norm_refit', 'f2_limits_checks.json')))
LS = rd(os.path.join(out, 'aggregate_limits_norm_refit', 'f2_limits_summary.csv'))
nr = F[(F.scale == 'norm_refit') & (F.arm == 'classical') & (F.variance == 'fpc')][K + ['genes']]
lc = LS[LS.arm == 'r4_none'][K + ['genes']]
mm = nr.merge(lc, on=K, how='outer', suffixes=('_regimeA', '_limits'), indicator=True)
summ['item4_checks'] = dict(units=len(LU), completed=int((LU.status == 'COMPLETED').sum()), controls_max=LC.get('controls_max'),
                            duplicate_rows=LC.get('duplicate_rows'), norm_refit_cells_regimeA=len(nr), norm_refit_cells_limits=len(lc),
                            cells_unmatched=int((mm._merge != 'both').sum()),
                            cells_gene_count_differs=int((mm.dropna().genes_regimeA != mm.dropna().genes_limits).sum()),
                            scales_in_limits=sorted(LS.scale.unique().tolist()))
dump()
L2 = rd(os.path.join(F2c, 'aggregate_limits', 'f2_limits_summary.csv'))
HEST = ['CCRCC', 'CCRCC_merged', 'INDIANA_KIDNEY', 'LUNG_XENIUM']


def ranking(df, n):
    x = df[df.n == n].assign(av=lambda d: d.arm + '|' + d.variance).groupby('av').median_coverage.median()
    return x


def score(ref, new, lab):
    rows = []; res = {}
    for n in (4, 8):
        a, b = ranking(ref, n), ranking(new, n)
        if len(a) == 0 or len(b) == 0:
            res[f'n{n}'] = dict(ranking_identical=None, kendall_tau=None, kluger_lowest_norm_refit=None, kluger_lowest_ref=None, arms=0)
            continue
        t = pd.DataFrame({'median_ref': a, 'median_norm_refit': b})
        t['rank_ref'] = t.median_ref.rank(method='min'); t['rank_norm_refit'] = t.median_norm_refit.rank(method='min')
        same = bool((t.rank_ref == t.rank_norm_refit).all())
        kl = 'kluger_ptd|cluster_boot'
        lowest = bool(t.median_norm_refit.idxmin() == kl) if kl in t.index else None
        tau = float(t[['median_ref', 'median_norm_refit']].corr(method='kendall').iloc[0, 1])
        res[f'n{n}'] = dict(ranking_identical=same, kendall_tau=tau, kluger_lowest_norm_refit=lowest,
                            kluger_lowest_ref=bool(t.median_ref.idxmin() == kl), arms=len(t))
        rows.append(t.reset_index().rename(columns={'index': 'arm'}).assign(n=n, reference=lab))
    k = bool(res['n4']['kluger_lowest_norm_refit']); r_ = bool(res['n4']['ranking_identical']) and bool(res['n8']['ranking_identical'])
    res['verdict'] = 'held' if (k and r_) else ('partly held' if (k or r_) else 'refuted')
    return res, (pd.concat(rows, ignore_index=True) if rows else pd.DataFrame())


noG1 = lambda d: d[(d.G - d.n) != 1]
sc = {}; tabs = []
for lab, ref, new in (('F2_all_other_scales', L2, LS), ('F2_HEST_tasks_other_scales', L2[L2.task.isin(HEST)], LS),
                      ('F2_all_other_scales_noG1', noG1(L2), noG1(LS))):
    s, t = score(ref, new, lab); sc[lab] = s; tabs.append(t)
pd.concat(tabs, ignore_index=True).to_csv(os.path.join(out, 'f3_limits_norm_refit_ranking.csv'), index=False)
summ['item4_prediction'] = dict(text="on norm_refit, the ranking of the limits arms by median coverage at n = 4 and n = 8 is the one F2 found on the other scales, with Kluger's cluster bootstrap lowest at n = 4",
                                primary='F2_all_other_scales', scores=sc, verdict=sc['F2_all_other_scales']['verdict'])
summ['finished'] = True
dump()
print(json.dumps(summ, indent=1, default=str))
