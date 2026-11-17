"""Round 11, track closeout, B3: what makes center S0006's coverage low on kidney Visium, from the existing
center-design prediction files, with no new fit (brief, section 5, item 3).

For each encoder and scale of round 10's center-design files and alpha = 0.2, donor-level HCP pooled across centers
(`hcp_donor`) is formed exactly as round10_final_runs_f3_institution.py forms it (its hcp_q_groups, imported
unchanged): target center u held out, calibration groups the donors of the other centers. Per (center, gene):
  cov          coverage of |y - f| <= q over the center's spots (reproduces inst_by_center.csv);
  q            the HCP half-width;
  med_abs      median |y - f| over the center's spots (F4-4's quantity);
  q_own        the (1 - alpha) quantile of the center's own |y - f| (the half-width that would give 1 - alpha);
  bias         mean of y - f over the center's spots (a level shift of the center-out head on that center);
  cov_centered coverage of |(y - f) - bias| <= q (the coverage if the level shift were removed, same q);
  cov_q_other  coverage of the center's |y - f| at the median over the other centers of their own q (what the
               center's spots would get under the calibration the other centers face);
  cov_by_donor per donor of the center, coverage at q (to see whether a few donors carry the shortfall).
Per (encoder, scale, center) the medians over genes are written, and per center and donor the median over genes of
cov_by_donor. Writes b3_summary.json first, then b3_by_center.csv, b3_by_gene.csv, b3_by_donor.csv.
Usage: round11_closeout_b3_s0006.py <predict_dir_root>   (round 10's F1/predict)
"""
import json, os, sys
import numpy as np, pandas as pd, pyarrow.parquet as pq
import round10_final_runs_f3_institution as I

ALPHA = 0.2
ENCODERS = ('uni_v2', 'hoptimus0', 'resnet50')
SCALES = ('log1p', 'lognorm')


def main():
    root = sys.argv[1]
    gene_rows, cen_rows, don_rows, checks = [], [], [], []
    for enc in ENCODERS:
        p = f'{root}/kidney__Visium__{enc}/pred__kidney__Visium__{enc}__center.parquet'
        tab = pq.read_table(p)
        fold = tab.column('fold').to_numpy(zero_copy_only=False).astype(str)
        donor = tab.column('donor_id').to_numpy(zero_copy_only=False).astype(str)
        units = sorted(set(fold.tolist()))
        for sc in SCALES:
            genes = [c.split('__', 1)[1] for c in tab.column_names if c.startswith(f'y_{sc}__')]
            Y = np.column_stack([tab.column(f'y_{sc}__{g}').to_numpy() for g in genes]).astype(np.float64)
            F = np.column_stack([tab.column(f'f_{sc}__{g}').to_numpy() for g in genes]).astype(np.float64)
            R = Y - F; S = np.abs(R)
            per_u = {}
            for u in units:
                E = fold == u; C = ~E
                q, fc, K = I.hcp_q_groups(S[C], donor[C], [ALPHA])
                q = np.asarray(q[0], dtype=np.float64)
                SE, RE = S[E], R[E]
                cov = (SE <= q).mean(0)
                bias = RE.mean(0)
                cov_c = (np.abs(RE - bias) <= q).mean(0)
                q_own = np.quantile(SE, 1 - ALPHA, axis=0)
                per_u[u] = dict(q=q, q_own=q_own, cov=cov, cov_c=cov_c, bias=bias, med_abs=np.median(SE, 0), SE=SE,
                                don=donor[E], sd=RE.std(0), K=K)
            for u in units:
                d = per_u[u]
                q_other = np.median(np.vstack([per_u[v]['q_own'] for v in units if v != u]), axis=0)
                cov_qo = (d['SE'] <= q_other).mean(0)
                for j, g in enumerate(genes):
                    gene_rows.append(dict(encoder=enc, scale=sc, center=u, gene=g, cov=d['cov'][j], q=d['q'][j],
                                          q_own=d['q_own'][j], med_abs=d['med_abs'][j], bias=d['bias'][j],
                                          sd=d['sd'][j], cov_centered=d['cov_c'][j], cov_q_other=cov_qo[j]))
                cen_rows.append(dict(encoder=enc, scale=sc, center=u, n_spots=int(len(d['don'])),
                                     n_donors=len(set(d['don'].tolist())), K=d['K'],
                                     cov_median=float(np.median(d['cov'])), q_median=float(np.median(d['q'])),
                                     q_own_median=float(np.median(d['q_own'])),
                                     log_q_own_over_q_median=float(np.median(np.log(d['q_own'] / d['q']))),
                                     med_abs_median=float(np.median(d['med_abs'])),
                                     abs_bias_median=float(np.median(np.abs(d['bias']))),
                                     abs_bias_over_q_median=float(np.median(np.abs(d['bias']) / d['q'])),
                                     sd_median=float(np.median(d['sd'])),
                                     cov_centered_median=float(np.median(d['cov_c'])),
                                     cov_q_other_median=float(np.median(cov_qo))))
                for dn in sorted(set(d['don'].tolist())):
                    m = d['don'] == dn
                    cv = (d['SE'][m] <= d['q']).mean(0)
                    don_rows.append(dict(encoder=enc, scale=sc, center=u, donor=dn, n_spots=int(m.sum()),
                                         cov_median_gene=float(np.median(cv))))
            print(f'[b3] {enc} {sc} done', flush=True)
    C = pd.DataFrame(cen_rows)
    ref = pd.read_csv(sys.argv[2]) if len(sys.argv) > 2 else None
    if ref is not None:
        r = ref[(ref.task == 'kidney__Visium') & (ref.arm == 'hcp_donor') & (np.isclose(ref.alpha, ALPHA))]
        m = C.merge(r[['encoder', 'scale', 'center_unit', 'coverage_median_gene']],
                    left_on=['encoder', 'scale', 'center'], right_on=['encoder', 'scale', 'center_unit'])
        checks.append(dict(check='reproduces inst_by_center hcp_donor alpha 0.2 coverage_median_gene',
                           rows=int(len(m)), max_abs_diff=float((m.cov_median - m.coverage_median_gene).abs().max())))
    s6 = C[C.center == 'S0006'].set_index(['encoder', 'scale'])
    summ = dict(alpha=ALPHA, checks=checks,
                s0006=s6[['cov_median', 'q_median', 'q_own_median', 'med_abs_median', 'abs_bias_over_q_median',
                          'cov_centered_median', 'cov_q_other_median']].reset_index().to_dict('records'))
    json.dump(summ, open('b3_summary.json', 'w'), indent=1)
    C.to_csv('b3_by_center.csv', index=False)
    pd.DataFrame(gene_rows).to_csv('b3_by_gene.csv', index=False)
    pd.DataFrame(don_rows).to_csv('b3_by_donor.csv', index=False)
    print(json.dumps(summ, indent=1))
    print(C.to_string())


if __name__ == '__main__':
    main()
