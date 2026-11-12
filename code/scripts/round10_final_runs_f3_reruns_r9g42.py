"""Round 10, track final-runs, F3 open point 6 (plan, section 5d.6 item 6): LUNG_XENIUM on round 9's 42-gene subset as
a second gene scope, LUNG_XENIUM_r9g42, in the regime A, limits, regime B and diagnostics aggregates and in the scores.

usage: round10_final_runs_f3_reruns_r9g42.py <clone> <base> <snapshot_scripts_dir> <out_dir>
The gene filter is zlib.crc32(gene.encode()) % 7 == 0, as round10_final_runs_f2_regimeA.py line 143 applies it.
The F2 aggregation scripts run unchanged (from <snapshot_scripts_dir>, by subprocess) on LUNG_XENIUM-only inputs at
two scopes:
  all     the F2 bulk files of every LUNG_XENIUM unit as they are (regime A unit directories linked, limits and regime B
          read in place through LUNG-only config directories, the LUNG cluster values and spot files). This is the
          anchor: every output must equal the LUNG_XENIUM rows of the committed F2 aggregates, and the scores run on
          the committed aggregates with their LUNG rows replaced by this scope's must equal the committed f2_scores.csv.
  r9g42   filtered copies of the same files, keeping only the genes of the subset, with the same layout.
The task label stays LUNG_XENIUM while the scripts run (round 9's references are keyed on it) and becomes
LUNG_XENIUM_r9g42 in the tables written here. Writes f3_r9g42_summary.json first, then per scope the raw outputs
under scope_<scope>/, and under compare/ one table per aggregate with the LUNG_XENIUM rows at both scopes
(column gene_scope).
"""
import glob, hashlib, json, os, shutil, subprocess, sys, time, zlib
import numpy as np, pandas as pd, pyarrow as pa, pyarrow.parquet as pq

clone, base, snap, out = sys.argv[1:5]
os.makedirs(out, exist_ok=True)
F2c = os.path.join(clone, 'results/round10/final_runs/F2')
F2b = os.path.join(base, 'F2')
T = 'LUNG_XENIUM'; T42 = 'LUNG_XENIUM_r9g42'
keep = lambda g: zlib.crc32(g.encode()) % 7 == 0
summ = dict(script='round10_final_runs_f3_reruns_r9g42.py', gene_filter='zlib.crc32(gene.encode()) % 7 == 0',
            started=time.strftime('%Y-%m-%dT%H:%M:%S'))
sp = os.path.join(out, 'f3_r9g42_summary.json')
dump = lambda: json.dump(summ, open(sp, 'w'), indent=1, default=str)
dump()


def filt_parquet(src, dst):
    t = pq.read_table(src)
    m = pa.array([keep(g) for g in t.column('gene').to_pylist()])
    t2 = t.filter(m)
    pq.write_table(t2, dst)
    return t.num_rows, t2.num_rows, sorted(set(t2.column('gene').to_pylist()))


def sh(script, args, cwd, log):
    t0 = time.time()
    with open(log, 'w') as fh:
        rc = subprocess.call([sys.executable, '-u', os.path.join(snap, script)] + args, cwd=cwd, stdout=fh, stderr=subprocess.STDOUT)
    return dict(script=script, rc=rc, seconds=round(time.time() - t0, 1))


reg_units = [u for u in pd.read_csv(os.path.join(F2c, 'aggregate/f2_units.csv')).unit if u.startswith(T + '__')]
lim_cfgs = sorted(glob.glob(os.path.join(F2c, 'configs/limits', f'f2_limits__{T}__*.json')))
rb_cfgs = sorted(glob.glob(os.path.join(F2c, 'configs/regimeB', f'f2_regimeB__{T}__*.json')))
cfg2 = json.load(open(os.path.join(F2c, 'configs/f2_diagnostics_v2.json')))
cv_paths = [p for p in cfg2['cluster_values'] if os.path.basename(p) == f'cluster_values__{T}.parquet']
spots = [s for s in cfg2['spot_files'] if s['task'] == T]
summ['units'] = dict(regimeA=reg_units, limits=len(lim_cfgs), regimeB=[os.path.basename(p) for p in rb_cfgs],
                     cluster_values=cv_paths, spot_files=len(spots))
dump()

genes_kept = {}
for scope in ('all', 'r9g42'):
    S = os.path.join(out, f'scope_{scope}'); W = os.path.join(S, 'work'); os.makedirs(W, exist_ok=True)
    runs = []
    # regime A root with the LUNG units only
    ra_root = os.path.join(W, 'regimeA'); os.makedirs(ra_root, exist_ok=True)
    for u in reg_units:
        src = os.path.join(F2b, 'regimeA', u)
        if scope == 'all':
            os.symlink(src, os.path.join(ra_root, u))
        else:
            d = os.path.join(ra_root, u); os.makedirs(d)
            shutil.copy(os.path.join(src, 'regimeA_summary.json'), d)
            n0, n1, gk = filt_parquet(os.path.join(src, 'regimeA_cells.parquet'), os.path.join(d, 'regimeA_cells.parquet'))
            genes_kept[f'regimeA/{u}'] = dict(rows=n0, rows_kept=n1, genes=len(gk))
    # limits and regime B: LUNG-only config dirs; roots in place (all) or filtered copies (r9g42)
    lcfg = os.path.join(W, 'limits_configs'); os.makedirs(lcfg); bcfg = os.path.join(W, 'regimeB_configs'); os.makedirs(bcfg)
    for p in lim_cfgs:
        shutil.copy(p, lcfg)
    for p in rb_cfgs:
        shutil.copy(p, bcfg)
    if scope == 'all':
        l_root, b_root = os.path.join(F2b, 'limits'), os.path.join(F2b, 'regimeB')
    else:
        l_root, b_root = os.path.join(W, 'limits'), os.path.join(W, 'regimeB')
        for p in lim_cfgs:
            u = os.path.basename(p)[len('f2_limits__'):-5]; src = os.path.join(F2b, 'limits', u); d = os.path.join(l_root, u); os.makedirs(d)
            for f in ('limits_summary.json', 'PROVENANCE.txt'):
                shutil.copy(os.path.join(src, f), d)
            for f in ('limits_cells.parquet', 'limits_diag.parquet'):
                n0, n1, gk = filt_parquet(os.path.join(src, f), os.path.join(d, f))
                genes_kept[f'limits/{u}/{f}'] = dict(rows=n0, rows_kept=n1, genes=len(gk))
        for p in rb_cfgs:
            u = os.path.basename(p)[len('f2_regimeB__'):-5]; src = os.path.join(F2b, 'regimeB', u); d = os.path.join(b_root, u); os.makedirs(d)
            for f in ('regimeB_summary.json', 'PROVENANCE.txt'):
                shutil.copy(os.path.join(src, f), d)
            n0, n1, gk = filt_parquet(os.path.join(src, 'regimeB_genes.parquet'), os.path.join(d, 'regimeB_genes.parquet'))
            genes_kept[f'regimeB/{u}'] = dict(rows=n0, rows_kept=n1, genes=len(gk))
    # cluster values
    cvs = []
    for p in cv_paths:
        if scope == 'all':
            cvs.append(p)
        else:
            d = os.path.join(W, 'cv_' + os.path.basename(os.path.dirname(p))); os.makedirs(d, exist_ok=True)
            q = os.path.join(d, os.path.basename(p)); n0, n1, gk = filt_parquet(p, q); cvs.append(q)
            genes_kept[f'cluster_values/{os.path.basename(os.path.dirname(p))}'] = dict(rows=n0, rows_kept=n1, genes=len(gk), gene_list=gk)
    dc = dict(cfg2); dc.update(unit=f'f3_r9g42_diagnostics_{scope}', cluster_values=cvs, regimeA_root=ra_root, spot_files=spots)
    dcp = os.path.join(W, 'diagnostics_config.json'); json.dump(dc, open(dcp, 'w'), indent=1)
    A = os.path.join(S, 'aggregate'); L = os.path.join(S, 'aggregate_limits'); B = os.path.join(S, 'aggregate_regimeB')
    D = os.path.join(S, 'diagnostics'); SC = os.path.join(S, 'scores')
    runs.append(sh('round10_final_runs_f2_aggregate.py', [ra_root, A], S, os.path.join(S, 'log_aggregate.txt')))
    runs.append(sh('round10_final_runs_f2_limits_aggregate.py', [l_root, A, lcfg, L], S, os.path.join(S, 'log_limits_aggregate.txt')))
    runs.append(sh('round10_final_runs_f2_regimeB_aggregate.py', [b_root, bcfg, B], S, os.path.join(S, 'log_regimeB_aggregate.txt')))
    runs.append(sh('round10_final_runs_f2_diagnostics.py', [dcp, D], S, os.path.join(S, 'log_diagnostics.txt')))
    # scores on the committed aggregates with the LUNG rows replaced by this scope's
    M = os.path.join(W, 'merged_aggregate'); os.makedirs(M)
    for name, comm in (('f2_regimeA_summary.csv', 'f2_regimeA_summary.csv.gz'), ('f2_switch_rule.csv', 'f2_switch_rule.csv'),
                       ('f2_fix1_cost.csv', 'f2_fix1_cost.csv')):
        c = pd.read_csv(os.path.join(F2c, 'aggregate', comm)); o = pd.read_csv(os.path.join(A, name))
        pd.concat([c[c.task != T], o[c.columns]], ignore_index=True).to_csv(os.path.join(M, name), index=False)
    runs.append(sh('round10_final_runs_f2_scores.py', [M, os.path.join(clone, 'results/round5/ppi/E4b_rejective/e4b_grid.csv'), SC],
                   S, os.path.join(S, 'log_scores.txt')))
    summ[f'runs_{scope}'] = runs; dump()
    print(scope, json.dumps(runs), flush=True)
summ['genes_kept'] = genes_kept
gl = [v.get('gene_list') for k, v in genes_kept.items() if k.startswith('cluster_values/')]
summ['subset_genes'] = dict(count=[len(x) for x in gl], same_in_all_cluster_value_files=all(x == gl[0] for x in gl), genes=gl[0] if gl else None)
dump()

# comparisons: scope all against the committed LUNG rows; both scopes side by side
TABLES = [('aggregate', 'f2_regimeA_summary.csv', 'f2_regimeA_summary.csv.gz'), ('aggregate', 'f2_switch_rule.csv', None),
          ('aggregate', 'f2_fix1_cost.csv', None), ('aggregate_limits', 'f2_limits_summary.csv', None),
          ('aggregate_limits', 'f2_limits_vs_regimeA.csv', None), ('aggregate_limits', 'f2_limits_diag.csv', None),
          ('aggregate_regimeB', 'f2_regimeB_summary.csv', None), ('aggregate_regimeB', 'f2_regimeB_fix1_vs_ppi.csv', None),
          ('diagnostics', 'f2_shortfall.csv', None), ('diagnostics', 'f2_buy.csv', None), ('diagnostics', 'f2_superpop.csv', None),
          ('diagnostics', 'f2_scale_diff.csv', None), ('diagnostics', 'f2_pc1_share.csv', None), ('diagnostics', 'f2_d9.csv', None),
          ('diagnostics', 'f2_anchor_r9_kappa.csv', None), ('diagnostics', 'f2_anchor_r9_c0.csv', None),
          ('diagnostics', 'f2_anchor_r9_pc1.csv', None)]
KC = ['task', 'encoder', 'scale', 'estimand', 'n', 'm', 'gene', 'arm', 'variance', 'form', 'other_scale', 'ref', 'label']


def compare(ref, ours):
    keys = [k for k in KC if k in ref.columns and k in ours.columns]
    cols = [c for c in ref.columns if c in ours.columns]
    extra_ref = [c for c in ref.columns if c not in ours.columns]
    extra_ours = [c for c in ours.columns if c not in ref.columns]
    r = ref.sort_values(keys, key=lambda s: s.astype(str)).reset_index(drop=True)
    o = ours.sort_values(keys, key=lambda s: s.astype(str)).reset_index(drop=True)
    d = dict(rows_ref=len(r), rows_ours=len(o), keys=keys, extra_cols_ref=extra_ref, extra_cols_ours=extra_ours,
             extra_ref_all_nan=bool(r[extra_ref].isna().all().all()) if extra_ref else True)
    if len(r) != len(o):
        d.update(equal=False); return d
    num = [c for c in cols if pd.api.types.is_numeric_dtype(r[c]) and pd.api.types.is_numeric_dtype(o[c])]
    oth = [c for c in cols if c not in num]
    d['non_numeric_equal'] = bool((r[oth].astype(str).to_numpy() == o[oth].astype(str).to_numpy()).all()) if oth else True
    a, b = r[num].to_numpy(float), o[num].to_numpy(float)
    d['nan_pattern_equal'] = bool((np.isnan(a) == np.isnan(b)).all())
    fin = np.isfinite(a) & np.isfinite(b)
    d['max_abs_diff'] = float(np.abs(a - b)[fin].max()) if fin.any() else 0.0
    d['inf_equal'] = bool(((a == b) | ~(np.isinf(a) | np.isinf(b))).all())
    d['equal'] = bool(d['non_numeric_equal'] and d['nan_pattern_equal'] and d['max_abs_diff'] == 0.0 and d['inf_equal'] and d['extra_ref_all_nan'])
    return d


anc = {}
CMP = os.path.join(out, 'compare'); os.makedirs(CMP, exist_ok=True)
for sub, name, comm in TABLES:
    ref = pd.read_csv(os.path.join(F2c, sub, comm or name), float_precision='round_trip')
    ref = ref[ref.task == T] if 'task' in ref.columns else ref
    pa_, pb_ = os.path.join(out, 'scope_all', sub, name), os.path.join(out, 'scope_r9g42', sub, name)
    if not (os.path.exists(pa_) and os.path.exists(pb_)):
        anc[name] = dict(equal=False, missing=[p for p in (pa_, pb_) if not os.path.exists(p)]); continue
    xa, xb = pd.read_csv(pa_, float_precision='round_trip'), pd.read_csv(pb_, float_precision='round_trip')
    xa = xa[xa.task == T] if 'task' in xa.columns else xa
    xb = xb[xb.task == T] if 'task' in xb.columns else xb
    anc[name] = compare(ref, xa)
    both = pd.concat([xa.assign(gene_scope='all'), xb.assign(gene_scope='r9g42', task=T42)], ignore_index=True)
    ext = '.csv.gz' if name == 'f2_regimeA_summary.csv' else '.csv'
    both.to_csv(os.path.join(CMP, 'f3_r9g42__' + name[:-4] + ext), index=False)
# scores: the whole file
ref = pd.read_csv(os.path.join(F2c, 'aggregate/f2_scores.csv'))
sa = pd.read_csv(os.path.join(out, 'scope_all/scores/f2_scores.csv')); sb = pd.read_csv(os.path.join(out, 'scope_r9g42/scores/f2_scores.csv'))
same = ref.shape == sa.shape and list(ref.columns) == list(sa.columns) and bool((ref.astype(str).to_numpy() == sa.astype(str).to_numpy()).all())
anc['f2_scores.csv'] = dict(equal=bool(same), rows_ref=len(ref), rows_ours=len(sa))
sc = sa.copy(); sc.insert(0, 'gene_scope_of_LUNG_rows', 'all')
sd = sb.copy(); sd.insert(0, 'gene_scope_of_LUNG_rows', 'r9g42')
if 'task' in sd.columns:
    sd.loc[sd.task == T, 'task'] = T42
pd.concat([sc, sd], ignore_index=True).to_csv(os.path.join(CMP, 'f3_r9g42__f2_scores.csv'), index=False)
# the LUNG clauses side by side
k = ['prediction', 'clause']
lung = sa[sa.get('task', pd.Series(dtype=str)).astype(str).eq(T) | sa.prediction.eq('FR2')]
side = lung.merge(sb, on=k, how='left', suffixes=('__all', '__r9g42'))
side.to_csv(os.path.join(CMP, 'f3_r9g42_scores_side_by_side.csv'), index=False)
summ['anchor_scope_all'] = anc
summ['anchor_pass'] = bool(all(v.get('equal') for v in anc.values()))
summ['finished'] = time.strftime('%Y-%m-%dT%H:%M:%S')
dump()
print(json.dumps(dict(anchor_pass=summ['anchor_pass'], subset_genes=summ['subset_genes']['count'],
                      unequal=[k for k, v in anc.items() if not v.get('equal')]), indent=1))
