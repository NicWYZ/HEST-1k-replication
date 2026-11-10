"""Round 10, track final-runs, stage F1: the aggregates the F1 report quotes, from the stamped F1 outputs.

Reads <base>/F1/... on Longleaf and writes small tables to <outdir> (copied into results/round10/final_runs/F1/):
  f1_module.csv          the acceptance summary of F1.1;
  f1_anchors.csv         the two anchor cells of F1.2, file value against rerun;
  f1_fr1.csv             F1.3 at n = 8 per task: median width and coverage of R5_lin, R5, W_within, FIX1, the ratio of
                         median widths R5_lin / W_within and R5 / W_within, and the median over genes of the per-gene
                         width ratio R5_lin / W_within with its 10% and 90% quantiles; FR1 holds where the ratio of
                         medians is at most 1.15 on every task;
  f1_fr1_all_n.csv       the same ratios at every n;
  f1_pred_anchor.csv     the prediction-file anchor: per gene, round 3's spot-level Pearson on CCRCC (log1p) against this
                         track's, on the genes both carry, with the median difference (prediction: at most 0.01).
  f1_predictions.csv     F1.4c, one row per corpus task, encoder and design (F1/predict/*/pred_summary__*.json): spots,
                         spots predicted, samples, donors, centers, folds, the held-out center groups, and per scale the
                         median, 10% and 90% quantiles over genes of the spot-level Pearson; check columns say whether
                         every spot is predicted and whether the folds equal the donors or the center groups;
  f1_d12.csv             D12 per task, encoder and scale (F1/diag_corpus_tasks/d12_lodo_r2__*.csv): median, 10% and 90%
                         quantiles over genes of R2_loo_const, R2_full_mean and R2_rawpred_loo_const, with the number of
                         donors G, and a check that the medians equal the script's own medians file;
  f1_d13_kidney.csv      D13 and INT5 on kidney Visium, every donor, for the three encoders;
  f1_task_list.csv       the proposed corpus tasks: the audited counts of f1_audit_task_counts.csv (read from
                         F1/audit_verdicts/) joined to the spots of the uni_v2 donor-design file.
Every section is skipped, and says so, when its inputs are absent.
Usage: round10_final_runs_f1_aggregate.py <base> <outdir> [--r3-ccrcc <b1_predictions__CCRCC__uni_v2.parquet>]
"""
import argparse, glob, json, os
import numpy as np, pandas as pd, pyarrow.parquet as pq


def pearson(a, b):
    a = a - a.mean(); b = b - b.mean(); d = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / d) if d > 0 else float('nan')


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('base'); ap.add_argument('out'); ap.add_argument('--r3-ccrcc', default='')
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); F1 = os.path.join(a.base, 'F1'); log = []
    p = os.path.join(F1, 'module_check/f1_module_check_summary.json')
    if os.path.exists(p):
        pd.DataFrame([json.load(open(p))]).to_csv(os.path.join(a.out, 'f1_module.csv'), index=False)
    else:
        log.append('module summary absent')
    rows = []
    for tag in ('r5', 'r7'):
        q = os.path.join(F1, f'anchor_{tag}/compare_v2/anchor_cell.json')
        if not os.path.exists(q):
            log.append(f'anchor {tag} absent'); continue
        j = json.load(open(q))
        for k, v in j.items():
            if isinstance(v, dict) and 'file' in v:
                rows.append(dict(anchor=tag, cell=json.dumps(j['cell'], sort_keys=True), quantity=k, file=v['file'],
                                 rerun=v['rerun'], abs_diff=v['abs_diff'], exact=v.get('exact', v.get('exact_at_10g')),
                                 binomial_mcse=v.get('binomial_mcse'), scripts_all_match=j['scripts_all_match'],
                                 tables_identical=j['tables_identical'], tables_compared=j['tables_compared']))
    pd.DataFrame(rows).to_csv(os.path.join(a.out, 'f1_anchors.csv'), index=False)
    S = []
    for mode in ('hest', 'acs'):
        q = os.path.join(F1, f'inflation/i34_williams_summary_{mode}.csv')
        if os.path.exists(q):
            S.append(pd.read_csv(q))
    if S:
        s = pd.concat(S)
        w = s.pivot_table(index=['task', 'n'], columns='form', values='median_width')
        cv = s.pivot_table(index=['task', 'n'], columns='form', values='median_cov')
        g = []
        for mode in ('hest', 'acs'):
            q = os.path.join(F1, f'inflation/i34_williams_{mode}.csv')
            if os.path.exists(q):
                d = pd.read_csv(q); x = d.pivot_table(index=['task', 'gene', 'n'], columns='form', values='width')
                x['gr'] = x['R5_lin'] / x['W_within']
                g.append(x.groupby(['task', 'n'])['gr'].agg(gene_ratio_median='median',
                                                            gene_ratio_q10=lambda v: v.quantile(.1),
                                                            gene_ratio_q90=lambda v: v.quantile(.9), genes='size'))
        t = pd.DataFrame({'w_R5_lin': w['R5_lin'], 'w_R5': w['R5'], 'w_W_within': w['W_within'], 'w_FIX1': w['FIX1'],
                          'cov_R5_lin': cv['R5_lin'], 'cov_R5': cv['R5'], 'cov_W_within': cv['W_within'], 'cov_FIX1': cv['FIX1']})
        t['ratio_R5_lin_over_W_within'] = t.w_R5_lin / t.w_W_within
        t['ratio_R5_over_W_within'] = t.w_R5 / t.w_W_within
        if g:
            t = t.join(pd.concat(g))
        t = t.reset_index()
        t.to_csv(os.path.join(a.out, 'f1_fr1_all_n.csv'), index=False)
        t8 = t[t.n == 8].copy(); t8['fr1_cell_holds'] = t8.ratio_R5_lin_over_W_within <= 1.15
        t8.to_csv(os.path.join(a.out, 'f1_fr1.csv'), index=False)
        log.append(f'FR1 holds on {int(t8.fr1_cell_holds.sum())} of {len(t8)} tasks')
    pa_ = sorted(glob.glob(os.path.join(F1, 'predict_anchor_CCRCC*/pred_summary__*.json')))
    if pa_ and a.r3_ccrcc and os.path.exists(a.r3_ccrcc):
        r3 = pq.read_table(a.r3_ccrcc).to_pandas()
        rows = []
        for q in pa_:
            j = json.load(open(q)); syms = j.get('gene_symbols')
            ens = list(j['pearson']['log1p'].keys())
            m = dict(zip(syms, ens)) if syms else {}
            for sym, e in m.items():
                if f'y__{sym}' in r3 and f'f__{sym}' in r3:
                    rr = r3[[f'y__{sym}', f'f__{sym}']].dropna()
                    rows.append(dict(run=os.path.basename(os.path.dirname(q)), gene=sym, ensembl=e,
                                     pearson_r3=pearson(rr.iloc[:, 0].to_numpy(), rr.iloc[:, 1].to_numpy()),
                                     pearson_r10=j['pearson']['log1p'][e], spots_r3=len(rr), spots_r10=j['spots_predicted']))
        d = pd.DataFrame(rows)
        if len(d):
            d['diff'] = d.pearson_r10 - d.pearson_r3
            d.to_csv(os.path.join(a.out, 'f1_pred_anchor.csv'), index=False)
            for run, x in d.groupby('run'):
                log.append(f'{run}: {len(x)} genes, median Pearson r3 {x.pearson_r3.median():.4f} r10 {x.pearson_r10.median():.4f}, '
                           f'difference of medians {x.pearson_r10.median() - x.pearson_r3.median():.4f}, median per-gene difference {x["diff"].median():.4f}')
    else:
        log.append('prediction anchor absent or round 3 file not given')
    q = lambda v, x: float(np.nanquantile(np.asarray(v, dtype=float), x)) if len(v) else float('nan')
    P = []
    for fn in sorted(glob.glob(os.path.join(F1, 'predict', '*', 'pred_summary__*.json'))):
        j = json.load(open(fn)); cg = j.get('center_groups')
        r = dict(task=j['task'], encoder=j['encoder'], design=j['design'], unit_dir=os.path.basename(os.path.dirname(fn)),
                 spots=j['spots'], spots_predicted=j['spots_predicted'], samples=j['samples'], donors=j['donors'],
                 centers=j['centers'], folds=j['folds'], center_groups=';'.join(cg) if cg else '', n_genes=j['n_genes'],
                 seconds_per_fold=j['seconds_per_fold'])
        for sc, d in j['pearson'].items():
            v = [x for x in d.values() if x == x]
            r[f'pearson_{sc}_median'] = float(np.median(v)); r[f'pearson_{sc}_q10'] = q(v, .1); r[f'pearson_{sc}_q90'] = q(v, .9)
        r['check_all_spots'] = j['spots'] == j['spots_predicted']
        r['check_folds'] = j['folds'] == (j['donors'] if j['design'] == 'donor' else (len(cg) if cg else j['centers']))
        P.append(r)
    if P:
        P = pd.DataFrame(P).sort_values(['task', 'encoder', 'design']); P.to_csv(os.path.join(a.out, 'f1_predictions.csv'), index=False)
        log.append(f'predictions: {len(P)} files, all spots predicted in {int(P.check_all_spots.sum())}, folds as expected in {int(P.check_folds.sum())}')
    else:
        log.append('prediction files absent')
    DG = os.path.join(F1, 'diag_corpus_tasks'); R = []
    for fn in sorted(glob.glob(os.path.join(DG, 'd12_lodo_r2__*.csv'))):
        d = pd.read_csv(fn); name = d['name'].iloc[0]
        med = pd.read_csv(os.path.join(DG, f'd12_lodo_r2_medians__{name}.csv')).set_index('scale')
        for sc, x in d.groupby('scale'):
            r = dict(name=name, scale=sc, G=int(x['G'].iloc[0]), genes=len(x))
            for k in ('R2_loo_const', 'R2_full_mean', 'R2_rawpred_loo_const'):
                r[f'{k}_median'] = float(x[k].median()); r[f'{k}_q10'] = q(x[k], .1); r[f'{k}_q90'] = q(x[k], .9)
            r['check_medians_file'] = bool(np.isclose(r['R2_loo_const_median'], med.loc[sc, 'R2_loo_const'], rtol=0, atol=1e-12))
            R.append(r)
    if R:
        R = pd.DataFrame(R); R.to_csv(os.path.join(a.out, 'f1_d12.csv'), index=False)
        log.append(f'D12: {R.name.nunique()} files, {len(R)} rows, medians file agrees in {int(R.check_medians_file.sum())}')
    else:
        log.append('D12 files absent')
    K = [pd.read_csv(fn) for fn in sorted(glob.glob(os.path.join(DG, 'd13_donor_diagnostics__kidney__Visium__*.csv')))]
    if K:
        K = pd.concat(K, ignore_index=True); K.to_csv(os.path.join(a.out, 'f1_d13_kidney.csv'), index=False)
        i5 = K[K.donor_id.str.endswith(':INT5')]
        for _, x in i5.iterrows():
            log.append(f"INT5 in {x['name']}: rank avg_y {int(x.rank_avg_y)}, resid_scale {int(x.rank_resid_scale)}, pred_out {int(x.rank_pred_out)}, "
                       f"lib_median {int(x.rank_lib_median)} (z {x.z_lib_median:.3f}), detected_median {int(x.rank_detected_median)} of {K[K['name'] == x['name']].shape[0]}")
    tc = os.path.join(F1, 'audit_verdicts', 'f1_audit_task_counts.csv')
    if os.path.exists(tc) and len(P):
        t = pd.read_csv(tc); t['task'] = t.organ + '__' + t.platform.str.replace(' ', '_')
        u = P[(P.encoder == 'uni_v2') & (P.design == 'donor')][['task', 'spots']]
        t = t.merge(u, on='task', how='left'); t.to_csv(os.path.join(a.out, 'f1_task_list.csv'), index=False)
        log.append(f'task list: {int(t.pass_donor10.sum())} of {len(t)} groups pass 10 donors, {int(t.spots.notna().sum())} have prediction files')
    open(os.path.join(a.out, 'f1_aggregate_log.txt'), 'w').write('\n'.join(log) + '\n')
    print('\n'.join(log))


if __name__ == '__main__':
    main()
