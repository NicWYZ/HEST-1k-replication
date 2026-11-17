"""Round 11, track closeout, B6: store the two numbers round 10 could not find in a stored column
(round 10 final report, section 7, item 4).

1. D12's share of genes where the pooled head beats a constant (findings survey D12, "0.46 to 0.64"). From round 9's
   per-gene file results/round9/between/between_head_by_gene.csv, design `lodo`, per task and encoder, the share of
   genes with R2_pooled > R2_constant (the pooled head against round 9's constant, both on the full-sample-mean
   baseline that file uses), and beside it the share with R2_pooled > 0. From round 10's per-gene D12 files for the
   corpus tasks and CCRCC (F1/diagnostics, F1/diag_corpus_tasks), the share of genes with R2_loo_const > 0, the
   leave-one-out constant being round 10's primary baseline.
2. Round 9's E1 box numbers: each number of round 9's sentence with the file, the selector and the stored value
   (results/round9/fewcluster/strat/i32_acs_box.csv, i32_hest_box_summary.csv, i32_required_m_B.csv).
Writes b6_summary.json first, then b6_d12_share.csv and b6_e1_box_numbers.csv.
Usage: round11_closeout_b6_stored.py <repo_clone_root> <round10_final_runs_longleaf_root>
"""
import glob, json, os, sys
import numpy as np, pandas as pd


def main():
    repo, r10 = sys.argv[1], sys.argv[2]
    rows = []
    B = pd.read_csv(f'{repo}/results/round9/between/between_head_by_gene.csv')
    for (t, e), g in B[B.design == 'lodo'].groupby(['task', 'encoder']):
        rows.append(dict(source='round9_between_head_by_gene', task=t, encoder=e, scale='log1p', baseline='full_mean',
                         n_genes=len(g), share_pooled_gt_constant=float((g.R2_pooled > g.R2_constant).mean()),
                         share_pooled_gt_0=float((g.R2_pooled > 0).mean())))
    files = sorted(glob.glob(f'{r10}/F1/diag_corpus_tasks/**/d12_lodo_r2__*.csv', recursive=True) +
                   glob.glob(f'{r10}/F1/diag*/d12_lodo_r2__*.csv'))
    seen = set()
    for f in files:
        if os.path.basename(f) in seen:
            continue
        seen.add(os.path.basename(f))
        D = pd.read_csv(f)
        for (n, s), g in D.groupby(['name', 'scale']):
            rows.append(dict(source=os.path.relpath(f, r10), task=n, encoder='', scale=s, baseline='loo_const',
                             n_genes=len(g), share_loo_const_gt_0=float((g.R2_loo_const > 0).mean()),
                             share_full_mean_gt_0=float((g.R2_full_mean > 0).mean())))
    S = pd.DataFrame(rows)
    acs = pd.read_csv(f'{repo}/results/round9/fewcluster/strat/i32_acs_box.csv')
    hb = pd.read_csv(f'{repo}/results/round9/fewcluster/strat/i32_hest_box_summary.csv')
    rm = pd.read_csv(f'{repo}/results/round9/fewcluster/strat/i32_required_m_B.csv')
    e1 = []
    a1 = acs[acs['lambda'] == 1.0].iloc[0]
    e1.append(dict(claim='ACS regime B persons per state (box class, lambda 1)', file='results/round9/fewcluster/strat/i32_acs_box.csv',
                   selector='lambda==1.0, column m_min_B', value=float(a1.m_min_B)))
    e1.append(dict(claim='ACS regime A states of 51 (box class, lambda 1)', file='results/round9/fewcluster/strat/i32_acs_box.csv',
                   selector='lambda==1.0, column n_min_A', value=float(a1.n_min_A)))
    for t in ('CCRCC', 'INDIANA_KIDNEY', 'LUNG_XENIUM'):
        r = hb[(hb.task == t) & (hb['lambda'] == 1.0)].iloc[0]
        e1.append(dict(claim=f'{t} regime B median spots per donor (box, lambda 1)', file='results/round9/fewcluster/strat/i32_hest_box_summary.csv',
                       selector=f'task=={t}, lambda==1.0, column m_min_B_median', value=float(r.m_min_B_median)))
        e1.append(dict(claim=f'{t} regime A median donors (box, lambda 1)', file='results/round9/fewcluster/strat/i32_hest_box_summary.csv',
                       selector=f'task=={t}, lambda==1.0, column n_min_A_median', value=float(r.n_min_A_median)))
    u = rm[(rm.N == 2000) & (rm.v0 == 1.0)]
    for L in (3, 8):
        e1.append(dict(claim=f'units per cluster without a share bound (v0 1, N 2000, Lambda0 {L})', file='results/round9/fewcluster/strat/i32_required_m_B.csv',
                       selector=f'N==2000, v0==1.0, Lambda0=={L}, column m_min_B', value=float(u[u.Lambda0 == L].m_min_B.iloc[0])))
    E = pd.DataFrame(e1)
    summ = dict(d12_round9_uni_v2=S[(S.source == 'round9_between_head_by_gene') & (S.encoder == 'uni_v2')][
        ['task', 'share_pooled_gt_constant', 'share_pooled_gt_0']].to_dict('records'),
        d12_round9_range_all_encoders=[float(S.share_pooled_gt_constant.min()), float(S.share_pooled_gt_constant.max())],
        e1=E[['claim', 'value']].to_dict('records'), r10_files=len(seen))
    json.dump(summ, open('b6_summary.json', 'w'), indent=1)
    S.to_csv('b6_d12_share.csv', index=False); E.to_csv('b6_e1_box_numbers.csv', index=False)
    print(json.dumps(summ, indent=1)); print(S.to_string())


if __name__ == '__main__':
    main()
