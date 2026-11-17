"""Round 11, track closeout, A6 (and B2): the tables of A6 from the job directories under a6/ and predict/.

1. a6_donor_level.csv, per (task, arm, scale, estimand, n_L): from regime A's cells and the cluster values, computed as
   round11_closeout_g2_aggregate.buy does (per gene the ratio of fix1's to classical's median width, both with variance
   fpc, then the median over genes; median coverage of fix1 and classical and fix1's median Monte Carlo standard error;
   R2_c the squared correlation over donors of z_g with f_g, median over genes), with the median spot-level Pearson of
   the arm's prediction file on that scale, the Spearman correlations over genes of the width ratio with R2_c and with
   the spot-level Pearson (as round 10's f2_buy), the share of genes where fix1 is narrower than classical, and, against
   R10 on the same task, scale, estimand and n_L, the paired per-gene difference of the width ratio (median, quartiles,
   share of genes where the arm is narrower) and the difference of median R2_c.
2. a6_d12.csv: the leave-one-donor-out median R^2 of the donor mean against the leave-one-out constant (and against the
   full-sample mean), per (task, arm, scale), from round10_final_runs_f1_donor_diag.py's medians file.
3. a6_mechanism.csv (decision 3 at G2): for mu, per (task, arm, scale), per gene the standard deviation over donors of the
   donor-mean prediction f_g, its ratio to R10's for the same gene, and the ratio sd(f_g)/sd(z_g); medians and quartiles
   over genes, with median R2_c of arm and R10 beside them.
4. a6_center.csv: held out by center, per (task, arm): median Pearson on each scale with the spread over folds of the
   per-fold median, and from round10_final_runs_f3_institution.py's tables at alpha 0.2 the median-center coverage of
   hcp_donor and hcp_center and each center's coverage.
5. a6_conformal.csv: round 3's a1_by_task rows per (task, arm, scale, design), the center design relabelled from the
   harness's `donor`, with the difference to R10 on the same task, scale and design.
6. a6_anchors.json: the checks of prediction A6.0.
Writes a6_summary.json first. Usage: round11_closeout_a6_aggregate.py <closeout_root> <round10_final_runs_root>, the latter
the repository's results/round10/final_runs (round 10's committed tables: r10_buy, f1_predictions, inst_by_center).
"""
import glob, json, os, re, sys
import numpy as np, pandas as pd
from scipy import stats

WANT = {('fix1', 'fpc'): 'fix1', ('classical', 'fpc'): 'cl'}
ARMTAG = {'R10': 'uni_v2__none__r10', 'P': 'uni_v2__ring1__ridgecv', 'E': 'uni_v2-hoptimus0-virchow2__ring1__r10'}
INST_LABEL = {'uni_v2': 'R10', 'P': 'P', 'E_posthoc': 'E'}


def rho(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return float(stats.spearmanr(a, b, nan_policy='omit')[0]) if (np.isfinite(a) & np.isfinite(b)).sum() > 3 else np.nan


def pred_summary(root, task, arm):
    d = f'{root}/a6/donor/{task}__{arm}/predict'
    if not os.path.isdir(d):
        c = [x for x in sorted(glob.glob(f'{root}/predict/{task}__{arm}__donor*')) if re.search(r'__donor(_v\d+)?$', x)]
        d = c[-1]
    s = json.load(open(glob.glob(f'{d}/pred_summary__*.json')[0]))
    out = {}
    for sc in ('log1p', 'lognorm'):
        p = s['pearson'][sc]
        if s.get('gene_symbols'):
            ens = list(p.keys()); out[sc] = {sym: p[e] for sym, e in zip(s['gene_symbols'], ens)}
        else:
            out[sc] = dict(p)
    return out, s


def r2c_table(cv):
    C = pd.read_parquet(cv)
    g = C.groupby(['scale', 'estimand', 'gene'])
    r = g[['z', 'f']].apply(lambda x: float(np.corrcoef(x.z, x.f)[0, 1] ** 2) if x.z.std() > 0 and x.f.std() > 0 else np.nan).rename('R2c')
    sdf = g.f.std(ddof=1).rename('sd_f'); sdz = g.z.std(ddof=1).rename('sd_z')
    return pd.concat([r, sdf, sdz], axis=1).reset_index()


def donor_level(root):
    rows, per_gene, d12, mech = [], [], [], []
    for d in sorted(glob.glob(f'{root}/a6/donor/*__*')):
        task, arm = os.path.basename(d).rsplit('__', 1)
        cells, cv = f'{d}/regimeA/regimeA_cells.parquet', glob.glob(f'{d}/cv/cluster_values__*.parquet')
        if not os.path.exists(cells) or not cv:
            continue
        x = pd.read_parquet(cells)
        x = x[x.estimand.isin(['theta3', 'mu'])]
        x = x[[(a, v) in WANT for a, v in zip(x.arm, x.variance)]].copy()
        x['lab'] = [WANT[(a, v)] for a, v in zip(x.arm, x.variance)]
        W = x.pivot_table(index=['task', 'scale', 'estimand', 'gene', 'n'], columns='lab',
                          values=['median_width', 'coverage', 'coverage_se']).reset_index()
        W.columns = ['_'.join([c for c in col if c]) if isinstance(col, tuple) else col for col in W.columns]
        W['wr_fix1'] = W.median_width_fix1 / W.median_width_cl
        W = W.merge(r2c_table(cv[0]), on=['scale', 'estimand', 'gene'], how='left')
        ps, _ = pred_summary(root, task, arm)
        W['pearson_spot'] = [ps[s].get(g, np.nan) for s, g in zip(W.scale, W.gene)]
        W['arm'] = arm; per_gene.append(W)
        for f in glob.glob(f'{d}/d12*/d12_lodo_r2_medians__*.csv'):
            m = pd.read_csv(f); step = os.path.basename(os.path.dirname(f))
            if step != 'd12':   # a joined file of one scale: the medians file labels it log1p
                m['scale'] = step.split('_', 1)[1]
            m['task'] = task; m['arm'] = arm; d12.append(m)
    if not per_gene:
        return [pd.DataFrame()] * 3
    G = pd.concat(per_gene, ignore_index=True)
    key = ['task', 'scale', 'estimand', 'n', 'gene']
    ref = G[G.arm == 'R10'][key + ['wr_fix1', 'R2c', 'sd_f']].rename(columns={'wr_fix1': 'wr_R10', 'R2c': 'R2c_R10', 'sd_f': 'sd_f_R10'})
    G = G.merge(ref, on=key, how='left')
    G['wr_diff'] = G.wr_fix1 - G.wr_R10
    for k, g in G.groupby(['task', 'arm', 'scale', 'estimand', 'n']):
        r = dict(zip(['task', 'arm', 'scale', 'estimand', 'n'], k), genes=len(g),
                 median_wr_fix1=g.wr_fix1.median(), median_cov_fix1=g.coverage_fix1.median(), median_cov_cl=g.coverage_cl.median(),
                 median_mcse_fix1=g.coverage_se_fix1.median(), median_R2c=g.R2c.median(), median_pearson_spot=g.pearson_spot.median(),
                 rho_wr_fix1_R2c=rho(g.wr_fix1, g.R2c), rho_wr_fix1_pearson=rho(g.wr_fix1, g.pearson_spot),
                 share_fix1_narrower=float((g.wr_fix1 < 1).mean()))
        if k[1] != 'R10' and g.wr_R10.notna().any():
            dd = g.wr_diff.dropna()
            r.update(wr_diff_vs_R10_median=dd.median(), wr_diff_vs_R10_q25=dd.quantile(.25), wr_diff_vs_R10_q75=dd.quantile(.75),
                     share_genes_narrower_than_R10=float((dd < 0).mean()), median_R2c_R10=g.R2c_R10.median(),
                     R2c_median_diff_vs_R10=g.R2c.median() - g.R2c_R10.median())
        rows.append(r)
        if k[3] == 'mu' and k[4] == 8:
            rat = (g.sd_f / g.sd_f_R10).replace([np.inf, -np.inf], np.nan)
            mech.append(dict(zip(['task', 'arm', 'scale'], k[:3]), genes=len(g),
                             median_sd_f=g.sd_f.median(), median_sd_f_R10=g.sd_f_R10.median(),
                             median_ratio_sd_f_to_R10=rat.median(), q25_ratio_sd_f_to_R10=rat.quantile(.25), q75_ratio_sd_f_to_R10=rat.quantile(.75),
                             share_genes_sd_f_below_R10=float((rat < 1).mean()), median_sd_f_over_sd_z=(g.sd_f / g.sd_z).median(),
                             median_R2c=g.R2c.median(), median_R2c_R10=g.R2c_R10.median()))
    D12 = pd.concat(d12, ignore_index=True) if d12 else pd.DataFrame()
    return pd.DataFrame(rows), D12, pd.DataFrame(mech)


def center(root):
    rows = []
    for d in sorted(glob.glob(f'{root}/predict/*__*__center')):
        task, arm, _ = os.path.basename(d).rsplit('__', 2)
        s = json.load(open(glob.glob(f'{d}/pred_summary__*.json')[0]))
        r = dict(task=task, arm=arm, folds=s['folds'], spots=s['spots'])
        for sc in ('log1p', 'lognorm'):
            r[f'median_pearson_{sc}'] = s[f'median_pearson_{sc}']
            r.update({f'fold_{q}_{sc}': s[f'fold_median_pearson_{sc}'][q] for q in ('q25', 'median', 'q75')})
        rows.append(r)
    C = pd.DataFrame(rows)
    inst = f'{root}/a6/inst/center_v1'
    I = pd.DataFrame()
    if os.path.exists(f'{inst}/inst_summary.csv'):
        SU = pd.read_csv(f'{inst}/inst_summary.csv'); BC = pd.read_csv(f'{inst}/inst_by_center.csv')
        SU = SU[np.isclose(SU.alpha, 0.2)]; BC = BC[np.isclose(BC.alpha, 0.2)]
        out = []
        for k, g in SU.groupby(['task', 'encoder', 'scale', 'arm']):
            b = BC[(BC.task == k[0]) & (BC.encoder == k[1]) & (BC.scale == k[2]) & (BC.arm == k[3])].sort_values('center_unit')
            out.append(dict(task=k[0], arm=INST_LABEL.get(k[1], k[1]), scale=k[2], hcp=k[3], alpha=0.2,
                            coverage_median_center=float(g.coverage_median_center.iloc[0]), n_centers=int(g.n_centers.iloc[0]),
                            per_center=';'.join(f'{r.center_unit}:{r.coverage_median_gene:.6f}' for r in b.itertuples()),
                            min_center=b.center_unit.iloc[int(np.argmin(b.coverage_median_gene.to_numpy()))] if len(b) else '',
                            min_center_coverage=float(b.coverage_median_gene.min()) if len(b) else np.nan))
        I = pd.DataFrame(out)
    return C, I


def conformal(root):
    rows = []
    for d in sorted(glob.glob(f'{root}/a6/conformal/*__*__*')):
        task, arm, design = os.path.basename(d).rsplit('__', 2)
        for f in glob.glob(f'{d}/a1_by_task__*.csv'):
            m = re.search(r'__(log1p|lognorm)\.csv$', f)
            if not m:
                continue
            x = pd.read_csv(f); x = x[x.score == 'abs']
            for r in x.itertuples():
                rows.append(dict(task=task, arm=arm, scale=m.group(1), design='center' if design == 'center' else r.design,
                                 n_folds=r.n_folds, coverage_mean=r.coverage_mean, coverage_sd=r.coverage_sd, width_mean=r.width_mean,
                                 calibration_unit=r.calibration_unit, n_train_matched=r.n_train_matched))
    X = pd.DataFrame(rows)
    if len(X):
        ref = X[X.arm == 'R10'][['task', 'scale', 'design', 'coverage_mean']].rename(columns={'coverage_mean': 'coverage_R10'})
        X = X.merge(ref, on=['task', 'scale', 'design'], how='left'); X['coverage_diff_vs_R10'] = X.coverage_mean - X.coverage_R10
    return X


def anchors(root, r10, DL, C, I):
    A = {}
    an = glob.glob(f'{root}/a6/conformal/anchor_CCRCC_round3/a1_by_task__*.csv')
    if an:
        x = pd.read_csv(an[0]); x = x[(x.score == 'abs') & (x.task == 'CCRCC')]
        ref = {'random': 0.8809874361442861, 'donor': 0.8642708075597048}
        A['A6.0a'] = {d: dict(value=float(x[x.design == d].coverage_mean.iloc[0]), ref=v,
                              diff=float(x[x.design == d].coverage_mean.iloc[0] - v)) for d, v in ref.items() if (x.design == d).any()}
    st = f'{root}/a6/conformal/selftest_v1/stdout.log'
    if os.path.exists(st):
        A['A6.0b'] = [l.strip() for l in open(st) if l.startswith('selftest')]
    cj = f'{root}/a6/donor/CCRCC__R10/check_anchor/compare.json'
    if os.path.exists(cj):
        A['A6.0c'] = json.load(open(cj))
    b = pd.read_csv(f'{r10}/F2/report_tables/r10_buy_uni_v2_primary_n8.csv')
    out = []
    for t in ('kidney__Visium', 'bowel__Visium'):
        for e in ('theta3', 'mu'):
            o = DL[(DL.task == t) & (DL.arm == 'R10') & (DL.scale == 'log1p') & (DL.estimand == e) & (DL.n == 8)] if len(DL) else []
            rr = b[(b.task == t) & (b.estimand == e) & (b.encoder == 'uni_v2') & (b.scale == 'log1p')]
            if len(o) and len(rr):
                out.append(dict(task=t, estimand=e, wr=float(o.median_wr_fix1.iloc[0]), wr_ref=float(rr.median_wr_fix1.iloc[0]),
                                R2c=float(o.median_R2c.iloc[0]), R2c_ref=float(rr.median_R2c.iloc[0]),
                                max_abs_diff=max(abs(float(o.median_wr_fix1.iloc[0] - rr.median_wr_fix1.iloc[0])),
                                                 abs(float(o.median_R2c.iloc[0] - rr.median_R2c.iloc[0])))))
    A['A6.0d'] = out
    f1 = pd.read_csv(f'{r10}/F1/aggregate/f1_predictions.csv')
    e = []
    if len(C):
        for t in ('brain__Visium', 'kidney__Visium'):
            o = C[(C.task == t) & (C.arm == 'R10')]; rr = f1[(f1.task == t) & (f1.encoder == 'uni_v2') & (f1.design == 'center')]
            if len(o) and len(rr):
                e.append(dict(task=t, median_pearson_log1p=float(o.median_pearson_log1p.iloc[0]), ref=float(rr.pearson_log1p_median.iloc[0]),
                              diff=float(o.median_pearson_log1p.iloc[0] - rr.pearson_log1p_median.iloc[0])))
    ib = f'{root}/a6/inst/center_v1/inst_by_center.csv'
    if os.path.exists(ib):
        o = pd.read_csv(ib); o = o[o.encoder == 'uni_v2']
        rr = pd.read_csv(f'{r10}/F3/institution/production/inst_by_center.csv')
        k = ['task', 'encoder', 'scale', 'arm', 'alpha', 'center_unit']
        m = o.merge(rr[rr.task.isin(o.task.unique())], on=k, suffixes=('', '_ref'))
        num = [c for c in o.columns if c not in k and pd.api.types.is_numeric_dtype(o[c]) and c + '_ref' in m.columns]
        e.append(dict(inst_rows_matched=len(m), inst_rows_ours=len(o),
                      inst_max_abs_diff=float(max(np.nanmax(np.abs(m[c] - m[c + '_ref'])) for c in num)) if len(m) else np.nan))
    A['A6.0e'] = e
    return A


def main():
    root, r10 = sys.argv[1], sys.argv[2]
    DL, D12, M = donor_level(root); C, I = center(root); X = conformal(root)
    A = anchors(root, r10, DL, C, I)
    json.dump(dict(rows=dict(donor_level=len(DL), d12=len(D12), mechanism=len(M), center=len(C), inst=len(I), conformal=len(X)),
                   anchors=A), open('a6_summary.json', 'w'), indent=1, default=float)
    json.dump(A, open('a6_anchors.json', 'w'), indent=1, default=float)
    for n, T in (('a6_donor_level', DL), ('a6_d12', D12), ('a6_mechanism', M), ('a6_center', C), ('a6_center_hcp', I), ('a6_conformal', X)):
        T.to_csv(f'{n}.csv', index=False)
    print(json.dumps(A, indent=1, default=float))
    with pd.option_context('display.width', 250, 'display.max_columns', 40):
        for T in (DL, D12, M, C, I, X):
            print(T.to_string() if len(T) < 400 else T.head(400).to_string())


if __name__ == '__main__':
    main()
