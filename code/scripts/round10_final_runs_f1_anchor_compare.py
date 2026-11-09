"""Round 10, track final-runs, stage F1.2: compare an anchor rerun with the unit that made the anchor cell.

Usage:
  round10_final_runs_f1_anchor_compare.py r5 <orig_unit_dir> <rerun_dir> <snapshot_dir> <e4b_grid.csv> <outdir>
  round10_final_runs_f1_anchor_compare.py r7 <orig_unit_dir> <rerun_dir> <snapshot_dir> <s5_matched_cells.csv> <outdir> <s5_snapshot_dir>
Checks, written to <outdir>:
  anchor_script_md5.csv    every script md5 recorded in the original PROVENANCE.txt against the rerun's snapshot;
  anchor_files.csv         every csv/csv.gz table of the original unit against the rerun (shape, columns, max absolute
                           difference over numeric columns, mismatches over the others);
  anchor_cell.json         the anchor cell recomputed from the rerun beside the file's value, exact-match flags, and the
                           binomial Monte Carlo standard error sqrt(p(1-p)/R) at the cell's draw count for coverage.
r5 cell: CCRCC, uni_v2, theta3, G 24, n_L 8, D0, c_crossfit_design, textbook_t|fpc|lin|xf, n_sub 2000.
r7 cell: ACS_STATES, package, theta3, n_L 8, D2_rej_t at p_a 0.01, with round 7's S5 functions (take, ratios, per_cell,
         from the S5 snapshot) applied to the rerun's s1m_genes table.
"""
import glob, hashlib, importlib.util, json, os, sys
import numpy as np, pandas as pd


def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()


def script_md5s(orig, snap):
    rows, on = [], False
    for line in open(os.path.join(orig, 'PROVENANCE.txt')):
        if line.startswith('scripts_executed'):
            on = True; continue
        if line.startswith('inputs'):
            on = False
        if on and line.strip():
            m, p = line.split()
            q = os.path.join(snap, p)
            got = md5(q) if os.path.exists(q) else 'missing'
            rows.append(dict(path=p, recorded=m, snapshot=got, match=m == got))
    return pd.DataFrame(rows)


def compare_tables(orig, new):
    rows = []
    for f in sorted(glob.glob(os.path.join(orig, '*.csv')) + glob.glob(os.path.join(orig, '*.csv.gz'))):
        b = os.path.basename(f)
        if b.startswith('_run_row'):
            continue
        g = os.path.join(new, b)
        if not os.path.exists(g):
            rows.append(dict(file=b, present=False)); continue
        a = pd.read_csv(f, low_memory=False); c = pd.read_csv(g, low_memory=False)
        r = dict(file=b, present=True, rows_orig=len(a), rows_new=len(c), same_columns=list(a.columns) == list(c.columns))
        if r['same_columns'] and len(a) == len(c):
            num = [k for k in a.columns if pd.api.types.is_numeric_dtype(a[k]) and pd.api.types.is_numeric_dtype(c[k])]
            oth = [k for k in a.columns if k not in num]
            dmax = 0.0; nan_mismatch = 0
            for k in num:
                x = a[k].to_numpy(float); y = c[k].to_numpy(float)
                nan_mismatch += int((np.isnan(x) != np.isnan(y)).sum())
                ok = ~np.isnan(x) & ~np.isnan(y)
                if ok.any():
                    dmax = max(dmax, float(np.abs(x[ok] - y[ok]).max()))
            r.update(max_abs_diff=dmax, nan_mismatch=nan_mismatch,
                     other_mismatch=int(sum((a[k].astype(str) != c[k].astype(str)).sum() for k in oth)))
            r['identical'] = bool(dmax == 0 and nan_mismatch == 0 and r['other_mismatch'] == 0)
        rows.append(r)
    return pd.DataFrame(rows)


def mcse(p, R):
    return float(np.sqrt(p * (1 - p) / R))


def cell_r5(new, grid):
    key = dict(vtag='CCRCC', arm='uni_v2', estimand='theta3', G=24, n_L=8, design='D0', rule='c_crossfit_design',
               interval='textbook_t|fpc|lin|xf', n_sub=2000)

    def pick(d):
        m = np.ones(len(d), bool)
        for k, v in key.items():
            m &= (d[k] == v).to_numpy()
        assert m.sum() == 1, m.sum()
        return d[m].iloc[0]
    f = pick(pd.read_csv(grid)); n = pick(pd.read_csv(glob.glob(os.path.join(new, 'e4b_rejective__*.csv'))[0]))
    out = dict(cell=key)
    for q in ('coverage_median', 'width_median'):
        out[q] = dict(file=float(f[q]), rerun=float(n[q]), abs_diff=float(abs(f[q] - n[q])), exact=bool(f[q] == n[q]))
    out['coverage_median']['binomial_mcse'] = mcse(float(f['coverage_median']), 2000)
    return out


def cell_r7(new, matched, s5snap):
    spec = importlib.util.spec_from_file_location('s5', os.path.join(s5snap, 'code/scripts/round7_ppi_s5_numbers.py'))
    S5 = importlib.util.module_from_spec(spec); spec.loader.exec_module(S5)
    g = pd.read_csv(glob.glob(os.path.join(new, 's1m_genes__*.csv.gz'))[0], low_memory=False)
    d0 = g['design'] == 'D0'; d2 = g['design'] == 'D2'
    L = pd.concat([S5.take(g, d0 & (g['estimator'] == 'classical') & (g['variance'] == S5.LIN), 'D0_classical'),
                   S5.take(g, d2 & (g['balance'] == 'own') & (g['estimator'] == 'classical') & (g['variance'] == 'rej_t'),
                           'D2_rej_t', pa='col')], ignore_index=True)
    L['coverage_all'] = np.where(L['share_formed'] > 0, L['coverage'].fillna(0) * L['share_formed'], 0.0)
    c = S5.per_cell(S5.ratios(L, 0.01))
    c = c[(c.estimand == 'theta3') & (c.n_L == 8) & (c.design == 'D2_rej_t')]
    assert len(c) == 1, len(c)
    m = pd.read_csv(matched)
    m = m[(m.vtag == 'ACS_STATES') & (m.arm == 'package') & (m.estimand == 'theta3') & (m.n_L == 8)
          & (m.design == 'D2_rej_t') & np.isclose(m.p_a, 0.01)]
    assert len(m) == 1, len(m)
    out = dict(cell=dict(vtag='ACS_STATES', arm='package', estimand='theta3', n_L=8, design='D2_rej_t', p_a=0.01))
    for q in ('coverage', 'wr_D0cl'):
        fv, nv = float(m[q].iloc[0]), float(c[q].iloc[0])
        # s5_matched_cells.csv is written with float_format %.10g, so compare at that precision too
        out[q] = dict(file=fv, rerun=nv, abs_diff=abs(fv - nv), exact_at_10g=bool(float('%.10g' % nv) == fv))
    nd = int(g.loc[d2 & (g['balance'] == 'own') & (g['variance'] == 'rej_t') & (g['estimand'] == 'theta3')
                   & np.isclose(g['p_a'], 0.01), 'n_draws'].iloc[0])
    out['coverage']['n_draws'] = nd
    out['coverage']['binomial_mcse'] = mcse(out['coverage']['file'], nd)
    return out


def main():
    mode, orig, new, snap, ref, outdir = sys.argv[1:7]
    os.makedirs(outdir, exist_ok=True)
    s = script_md5s(orig, snap); s.to_csv(os.path.join(outdir, 'anchor_script_md5.csv'), index=False)
    t = compare_tables(orig, new); t.to_csv(os.path.join(outdir, 'anchor_files.csv'), index=False)
    cell = cell_r5(new, ref) if mode == 'r5' else cell_r7(new, ref, sys.argv[7])
    cell['scripts_all_match'] = bool(s['match'].all()); cell['n_scripts'] = int(len(s))
    cell['tables_compared'] = int(len(t)); cell['tables_identical'] = int(t.get('identical', pd.Series(dtype=bool)).fillna(False).sum())
    with open(os.path.join(outdir, 'anchor_cell.json'), 'w') as fh:
        json.dump(cell, fh, indent=1)
    print(json.dumps(cell, indent=1)); print(t.to_string())


if __name__ == '__main__':
    main()
