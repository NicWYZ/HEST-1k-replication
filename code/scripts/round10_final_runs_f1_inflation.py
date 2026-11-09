"""Round 10, track final-runs, stage F1.3: did the intervals of rounds 5 to 7 carry the level-dependent variance?

Reruns round 9's comparison (code/scripts/round9_fewcluster_williams.py, run_pop, seed 20261027, the same populations in
the same order, so every original arm reproduces round 9's files draw for draw) with two added arms scored by round 9's
own loop on the same draws:
  R5_lin        round 5's interval textbook_t|fpc|lin|xf from round 5's own code,
                round5_ppi_estimator.design_whole_clusters('donor', ..., lin=True, xf=True), with lamL_g the other half's
                clipped slope (lB on half A, lA on half B), cU = (lA + lB)/2, and t on n - 1 (round 5's df);
  R5_code_nolin the same call with lin=False, which should equal round 9's R5 (the reading of ledger L1 S4, section 0).
round5_ppi_estimator is imported from the snapshot named by --r5-scripts (round 5's commit), not from this track's code.
Outputs: i34_williams_<mode>.csv and i34_williams_summary_<mode>.csv in round 9's format with the two arms added,
f1_inflation_identity_<mode>.csv (per population and n: max |theta_R5_lin - theta_R5|, max |v_R5_code_nolin - v_R5|),
f1_inflation_r9_compare_<mode>.csv (each original summary row against round 9's file).
Usage: round10_final_runs_f1_inflation.py <acs|hest> <input> <r9_summary.csv> <outdir> --r5-scripts <dir>
"""
import argparse, importlib.util, inspect, os, sys, textwrap, zlib
import numpy as np, pandas as pd
import round9_fewcluster_williams as R9


def load_r5(path):
    sys.path.insert(0, path)
    spec = importlib.util.spec_from_file_location('round5_ppi_estimator', os.path.join(path, 'round5_ppi_estimator.py'))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def instrumented(R5, ident, tag):
    src = textwrap.dedent(inspect.getsource(R9.run_pop))
    anchor = "        for k, (est, v, tq) in forms.items():\n"
    assert src.count(anchor) == 1
    src = src.replace(anchor, "        _CB(n, forms, locals())\n" + anchor)
    ns = dict(vars(R9))

    def cb(n, forms, loc):
        z, f, A, B, L, lA, lB, cp, t1 = (loc[k] for k in ('z', 'f', 'A', 'B', 'L', 'lA', 'lB', 'cp', 't1'))
        G = len(z); Rn = L.shape[0]; cols = np.arange(Rn)[:, None]
        Lm = np.zeros((G, Rn), bool); Lm[L.T, np.arange(Rn)[None, :]] = True
        lamL = np.zeros((G, Rn)); lamL[A.T, np.arange(Rn)[None, :]] = lB[None, :]; lamL[B.T, np.arange(Rn)[None, :]] = lA[None, :]
        zb = np.broadcast_to(z[:, None], (G, Rn)).copy(); fb = np.broadcast_to(f[:, None], (G, Rn)).copy()
        lam = dict(lamL=lamL, cU=cp)
        o1 = R5.design_whole_clusters('donor', zb, fb, Lm, lam, lin=True, xf=True)
        o0 = R5.design_whole_clusters('donor', zb, fb, Lm, lam, lin=False, xf=True)
        r5est, r5v, _ = forms['R5']
        ident.append(dict(pop=tag[0], n=n, d_theta_lin_vs_r5=float(np.abs(o1['theta'] - r5est).max()),
                          d_var_nolin_vs_r5=float(np.abs(o0['var'] - r5v).max()),
                          rel_var_nolin_vs_r5=float((np.abs(o0['var'] - r5v) / np.maximum(np.abs(r5v), 1e-300)).max()),
                          df_r5_code=float(np.unique(o1['df'])[0])))
        forms['R5_lin'] = (o1['theta'], o1['var'], t1)
        forms['R5_code_nolin'] = (o0['theta'], o0['var'], t1)
    ns['_CB'] = cb
    exec(compile(src, 'round9_run_pop_instrumented', 'exec'), ns)
    return ns['run_pop']


def summarise(rows):
    r = pd.DataFrame(rows)
    r['bias_z'] = r.bias / r.mcse_bias; r['bias_rel'] = r.bias.abs() / r.sd
    return r, r.groupby(['task', 'form', 'n']).agg(pops=('gene', 'size'), median_cov=('coverage', 'median'),
                                                    median_width=('width', 'median'), median_rmse=('rmse', 'median'),
                                                    frac_bias_z_lt3=('bias_z', lambda x: float((x.abs() < 3).mean())),
                                                    median_bias_rel=('bias_rel', 'median'),
                                                    q90_bias_rel=('bias_rel', lambda x: float(x.quantile(.9)))).reset_index()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mode'); ap.add_argument('src'); ap.add_argument('r9_summary'); ap.add_argument('out')
    ap.add_argument('--r5-scripts', required=True)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    R5 = load_r5(a.r5_scripts)
    rng = np.random.default_rng(20261027); rows = []; ident = []; tag = ['']
    run_pop = instrumented(R5, ident, tag)
    if a.mode == 'acs':
        s = pd.read_csv(a.src)
        x = s[s['lambda'] == 0.0].set_index('ST'); y = s[s['lambda'] == 1.0].set_index('ST')
        z = x.mean_e.to_numpy(); f = (x.mean_e - y.mean_e).to_numpy()
        tag[0] = 'ACS_STATES|log_income'
        for r in run_pop(z, f, rng):
            rows.append({'task': 'ACS_STATES', 'gene': 'log_income', **r})
    else:
        d = pd.read_csv(a.src)
        d = d[(d.encoder == 'uni_v2') & d.task.isin(['CCRCC', 'INDIANA_KIDNEY', 'LUNG_XENIUM'])]
        for (task, gene), g in d.groupby(['task', 'gene']):
            if task == 'LUNG_XENIUM' and (zlib.crc32(gene.encode()) % 7 != 0):
                continue
            g = g.sort_values('donor'); tag[0] = f'{task}|{gene}'
            for r in run_pop(g.mean_y.to_numpy(float), g.mean_f.to_numpy(float), rng):
                rows.append({'task': task, 'gene': gene, **r})
    # summary first, bulk after
    r, summ = summarise(rows)
    summ.to_csv(os.path.join(a.out, f'i34_williams_summary_{a.mode}.csv'), index=False)
    pd.DataFrame(ident).to_csv(os.path.join(a.out, f'f1_inflation_identity_{a.mode}.csv'), index=False)
    want = pd.read_csv(a.r9_summary)
    m = summ.merge(want, on=['task', 'form', 'n'], suffixes=('', '_r9'), how='inner')
    cols = ['pops', 'median_cov', 'median_width', 'median_rmse', 'frac_bias_z_lt3', 'median_bias_rel', 'q90_bias_rel']
    m['max_abs_diff'] = np.max([(m[k] - m[k + '_r9']).abs().to_numpy() for k in cols], axis=0)
    m['passed'] = m['max_abs_diff'] <= 1e-12
    m.to_csv(os.path.join(a.out, f'f1_inflation_r9_compare_{a.mode}.csv'), index=False)
    r.drop(columns=['bias_z', 'bias_rel']).to_csv(os.path.join(a.out, f'i34_williams_{a.mode}.csv'), index=False)
    s8 = summ[summ.n == 8].pivot(index='task', columns='form', values=['median_width', 'median_cov'])
    print(s8.to_string())
    print('r9 rows compared', len(m), 'passed', int(m.passed.sum()), 'of', len(want))
    idf = pd.DataFrame(ident)
    print('max d_theta_lin_vs_r5', idf.d_theta_lin_vs_r5.max(), 'max rel_var_nolin_vs_r5', idf.rel_var_nolin_vs_r5.max())


if __name__ == '__main__':
    main()
