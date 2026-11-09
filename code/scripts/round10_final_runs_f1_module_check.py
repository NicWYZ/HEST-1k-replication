"""Round 10, track final-runs, stage F1.1: acceptance of the estimator module.

Part 1. Exact enumeration. For the ledger's three toy populations (results/round10/ledger/checks/
  l3_split_variance_check.py, populations rebuilt from its seed 20261107 with the same generator calls), every sample
  of size n and every assignment to folds of sizes floor/ceil is enumerated, the module's `crossfit` is evaluated on
  all of them at once, and the six statistics are compared with every row of l3_split_variance_check_output.txt.
  A row passes when each unrounded statistic is within 5e-7 (+1e-9) of the printed six-decimal value.
Part 2. Draw-for-draw replay of round 9 (code/scripts/round9_fewcluster_williams.py) on CCRCC. Round 9's `run_pop`
  source is executed unchanged except for one inserted line that hands its local arrays to a callback before scoring;
  the callback recomputes FIX1, W_within and FOLD with the module on the same draws. CCRCC's genes are first in round
  9's groupby order, so its generator stream is reproduced exactly. Pass: |module - round 9| <= 1e-12 (1 + |round 9|)
  for every estimate and variance, and the summary rows equal i34_williams_summary_hest.csv for CCRCC to 1e-12.
Part 3. The module's bh, bh_t, bh_t_fpc against round 7's bh3_parts on the same CCRCC draws (first 5 genes).
Usage: round10_final_runs_f1_module_check.py <l3_output.txt> <c0_cluster_summaries.csv.gz> <r9_summary_hest.csv> <outdir>
"""
import ast, inspect, itertools, json, os, sys, textwrap
import numpy as np, pandas as pd
import round10_final_runs_estimators as E
import round9_fewcluster_williams as R9


def part1(l3_out_path):
    rng = np.random.default_rng(20261107)
    pops = {}
    X1 = rng.gamma(2.0, 1.0, 10); pops["nonlinear_N10"] = (np.exp(0.6 * X1) + rng.normal(0, 0.5, 10), X1)
    X2 = rng.normal(5, 1, 12); pops["skewed_N12"] = (0.7 * X2 + rng.lognormal(0, 1, 12), X2)
    X3 = rng.normal(0, 1, 12); Y3 = 0.8 * X3 + rng.normal(0, 0.6, 12); Y3[0] += 4.0
    pops["one_outlier_N12"] = (Y3, X3)
    ref = {}
    for line in open(l3_out_path):
        line = line.strip()
        if not line:
            continue
        name, rule, nn, KK, rest = line.split(' ', 4)
        ref[(name, rule, int(nn[2:]), int(KK[2:]))] = ast.literal_eval(rest)
    rows = []
    for (name, rule, n, K), want in ref.items():
        Y, X = pops[name]; N = len(Y)
        sizes = [n // K + (1 if i < n % K else 0) for i in range(K)]
        labs = np.array(sorted(set(itertools.permutations(sum([[k] * sizes[k] for k in range(K)], [])))))
        samples = np.array(list(itertools.combinations(range(N), n)))
        S = np.repeat(samples, len(labs), axis=0); Lab = np.tile(labs, (len(samples), 1))
        folds = []
        for k in range(K):
            order = np.argsort(Lab != k, axis=1, kind='stable')[:, :sizes[k]]
            folds.append(np.take_along_axis(S, order, axis=1))
        o = E.crossfit(Y, X, folds, rule=rule)
        T, V, VC, VW = o['est'], o['V'], o['V_cons'], o['V_w']
        var = T.var()
        got = dict(bias=T.mean() - Y.mean(), V_ratio=V.mean() / var, Vcons_ratio=VC.mean() / var,
                   Vwithin_ratio=VW.mean() / var, frac_V_negative=(V < 0).mean(),
                   frac_V_below_quarter_Vcons=(V < 0.25 * VC).mean())
        for fld, wv in want.items():
            d = abs(got[fld] - wv)
            rows.append(dict(population=name, rule=rule, n=n, K=K, field=fld, ledger=wv, module=got[fld],
                             module_rounded=float(np.round(got[fld], 6)), abs_diff=d, n_cases=len(T),
                             passed=bool(d <= 5e-7 + 1e-9)))
    return pd.DataFrame(rows)


def part2(c0_path, r9_summary_path, bh_genes=5):
    src = textwrap.dedent(inspect.getsource(R9.run_pop))
    anchor = "        for k, (est, v, tq) in forms.items():\n"
    assert src.count(anchor) == 1
    src = src.replace(anchor, "        _CB(n, forms, dict(L=L, A=A, B=B, U=U, ua=ua, lA=lA, lB=lB))\n" + anchor)
    ns = dict(vars(R9)); exec(compile(src, 'round9_run_pop_instrumented', 'exec'), ns)
    d = pd.read_csv(c0_path)
    d = d[(d.encoder == 'uni_v2') & d.task.isin(['CCRCC', 'INDIANA_KIDNEY', 'LUNG_XENIUM'])]
    groups = list(d.groupby(['task', 'gene']))
    assert groups[0][0][0] == 'CCRCC'
    rng = np.random.default_rng(20261027)
    rep, bhrows, rows = [], [], []
    import round7_ppi_s2_comparators as R7
    for gi, ((task, gene), g) in enumerate(groups):
        if task != 'CCRCC':
            break
        g = g.sort_values('donor')
        z = g.mean_y.to_numpy(float); f = g.mean_f.to_numpy(float); G = len(z)

        def cb(n, forms, a):
            L, A, B, U, ua, lA, lB = (a[k] for k in ('L', 'A', 'B', 'U', 'ua', 'lA', 'lB'))
            fx = E.difference_fixed(z, f, L, 1.0)
            cf = E.crossfit(z, f, [A, B], rule='r5')
            fo = E.fold_r9(z, f, A, B, U, ua, cf['b_k'][1], cf['b_k'][0])
            for form, (me, mv) in (('FIX1', (fx['est'], fx['v'])), ('W_within', (cf['est'], cf['V_w'])),
                                   ('FOLD', (fo['est'], fo['v']))):
                re_, rv, _ = forms[form]
                for q, a1, b1 in (('est', me, re_), ('var', mv, rv)):
                    dd = np.abs(a1 - b1); tol = 1e-12 * (1 + np.abs(b1))
                    rep.append(dict(gene=gene, n=n, form=form, quantity=q, max_abs_diff=float(dd.max()),
                                    max_diff_over_tol=float((dd / tol).max()), passed=bool((dd <= tol).all())))
            # the coefficients themselves
            rep.append(dict(gene=gene, n=n, form='coef', quantity='lA_lB',
                            max_abs_diff=float(max(np.abs(cf['b_k'][0] - lB).max(), np.abs(cf['b_k'][1] - lA).max())),
                            max_diff_over_tol=np.nan, passed=bool(np.allclose(cf['b_k'][0], lB, rtol=0, atol=1e-13)
                                                                and np.allclose(cf['b_k'][1], lA, rtol=0, atol=1e-13))))
            if gi < bh_genes:
                R = L.shape[0]
                Lm = np.zeros((R, G), bool); np.put_along_axis(Lm, L, True, axis=1)
                Z3 = np.broadcast_to(z[None, :, None], (R, G, 1)); F3 = np.broadcast_to(f[None, :, None], (R, G, 1))
                th, TL, TU, nn = R7.bh3_parts(Z3, F3, Lm[:, :, None])
                mv = E.bh_variants(z, f, L)
                ref = dict(bh=(th[:, 0], (TL + TU)[:, 0]), bh_t=(th[:, 0], (TL * nn / (nn - 1) + TU)[:, 0]),
                           bh_t_fpc=(th[:, 0], ((TL * nn / (nn - 1) + TU) * (1 - n / G))[:, 0]))
                for form, (rt, rv) in ref.items():
                    for q, a1, b1 in (('est', mv[form]['est'], rt), ('var', mv[form]['v'], rv)):
                        dd = np.abs(a1 - b1); tol = 1e-12 * (1 + np.abs(b1))
                        bhrows.append(dict(gene=gene, n=n, form=form, quantity=q, max_abs_diff=float(dd.max()),
                                           passed=bool((dd <= tol).all())))
        ns['_CB'] = cb
        for r in ns['run_pop'](z, f, rng):
            rows.append({'task': task, 'gene': gene, **r})
    r = pd.DataFrame(rows)
    r['bias_z'] = r.bias / r.mcse_bias; r['bias_rel'] = r.bias.abs() / r.sd
    summ = r.groupby(['task', 'form', 'n']).agg(pops=('gene', 'size'), median_cov=('coverage', 'median'),
                                                 median_width=('width', 'median'), median_rmse=('rmse', 'median'),
                                                 frac_bias_z_lt3=('bias_z', lambda x: float((x.abs() < 3).mean())),
                                                 median_bias_rel=('bias_rel', 'median'),
                                                 q90_bias_rel=('bias_rel', lambda x: float(x.quantile(.9)))).reset_index()
    want = pd.read_csv(r9_summary_path); want = want[want.task == 'CCRCC']
    m = summ.merge(want, on=['task', 'form', 'n'], suffixes=('', '_r9'), how='outer', indicator=True)
    cols = ['pops', 'median_cov', 'median_width', 'median_rmse', 'frac_bias_z_lt3', 'median_bias_rel', 'q90_bias_rel']
    for cname in cols:
        m[f'd_{cname}'] = (m[cname] - m[f'{cname}_r9']).abs()
    m['passed'] = (m['_merge'] == 'both') & np.logical_and.reduce(
        [m[f'd_{cname}'] <= 1e-12 * (1 + m[f'{cname}_r9'].abs()) for cname in cols])
    return pd.DataFrame(rep), pd.DataFrame(bhrows), m


def main():
    l3, c0, r9s, out = sys.argv[1:5]
    os.makedirs(out, exist_ok=True)
    p1 = part1(l3)
    p1.to_csv(os.path.join(out, 'f1_module_check_diff.csv'), index=False)
    rep, bh, summ = part2(c0, r9s)
    res = dict(
        part1_rows=int(p1.groupby(['population', 'rule', 'n', 'K']).ngroups),
        part1_fields=int(len(p1)), part1_fields_passed=int(p1.passed.sum()),
        part1_max_abs_diff=float(p1.abs_diff.max()),
        part2_checks=int(len(rep)), part2_checks_passed=int(rep.passed.sum()),
        part2_max_diff_over_tol=float(np.nanmax(rep.max_diff_over_tol)),
        part2_genes=int(rep.gene.nunique()),
        part2_summary_rows=int(len(summ)), part2_summary_rows_passed=int(summ.passed.sum()),
        part3_checks=int(len(bh)), part3_checks_passed=int(bh.passed.sum()),
        part3_max_abs_diff=float(bh.max_abs_diff.max()) if len(bh) else None)
    res['all_passed'] = bool(res['part1_fields'] == res['part1_fields_passed'] and res['part1_rows'] == 30
                             and res['part2_checks'] == res['part2_checks_passed']
                             and res['part2_summary_rows'] == res['part2_summary_rows_passed']
                             and res['part3_checks'] == res['part3_checks_passed'])
    with open(os.path.join(out, 'f1_module_check_summary.json'), 'w') as fh:
        json.dump(res, fh, indent=1)
    rep.to_csv(os.path.join(out, 'f1_r9_replay.csv'), index=False)
    bh.to_csv(os.path.join(out, 'f1_bh_compare.csv'), index=False)
    summ.to_csv(os.path.join(out, 'f1_r9_summary_compare.csv'), index=False)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
