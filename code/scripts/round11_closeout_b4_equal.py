"""Round 11, track closeout, B4: regime B under equal allocation on ACS by state, beside the proportional allocation
round 10 ran (brief, section 5, item 4).

Round 10's regime comparison (round10_final_runs_f3_regcomp.py, imported unchanged) labels every state in regime B at
m_g = min(M_g, max(1, round(B' M_g / N))), proportional to the state's size, while theta3 weights states equally.
Equal allocation sets m_g = min(M_g, max(1, round(B' / G))) at the same B' (unit cost, and cost-matched at c = 10).
It is applied by wrapping round5_ppi_e3_twolevel.part_cells, so every other step, seed and estimator is round 10's.

Populations: round 10's ACS regcomp configs (F3/regimeB/regcomp__pk_ACS_STATES__pkg__log_income__p00 and p01), kept
when the cell is regime A, or regime B at unit cost or c = 10. The proportional run is the anchor: its regcomp_genes rows
must equal round 10's rows for the same cells (same seeds). The comparisons follow
round10_final_runs_f3_regcomp_aggregate.py's fix1 pair: regime A C_fix1 'twostage_t|fpc' against regime B C_fix1
'regB_t', ratio of mean widths, one comparison per (budget, n_L) at c = 10; regime B is narrower when the ratio < 1.
Writes b4_summary.json first, then b4_comparisons.csv, b4_anchor.csv, b4_genes__<alloc>.parquet, b4_alloc_sizes.csv.
Usage: round11_closeout_b4_equal.py <round10_regimeB_dir>
"""
import json, os, sys
import numpy as np, pandas as pd, pyarrow as pa, pyarrow.parquet as pq
import round5_ppi_e3_twolevel as E3
import round10_final_runs_f3_regcomp as RC

ORIG = E3.part_cells
STATE = dict(alloc='prop', sizes=[])


def part_cells_alloc(part, data, Tset):
    cells = ORIG(part, data, Tset)
    if STATE['alloc'] == 'equal':
        G = len(data['donors']); M = np.bincount(data['didx'], minlength=G).astype(float)
        for c in cells:
            if c['m'] == 'prop':
                c['mg'] = np.minimum(M, np.maximum(1, np.round(c['budget'] / G)))
    for c in cells:
        if c['m'] == 'prop':
            STATE['sizes'].append(dict(alloc=STATE['alloc'], budget=float(c['budget']), cost=c['cost'],
                                       total=float(np.sum(c['mg'])), m_min=float(np.min(c['mg'])),
                                       m_max=float(np.max(c['mg'])), m_median=float(np.median(c['mg']))))
    return cells


E3.part_cells = part_cells_alloc


def keep(pop):
    lab = pop.get('cell_label', '')
    return lab.startswith('A_') or lab.endswith('_unit') or '_c10_' in lab


def pairs(D):
    A = D[(D.regime == 'A') & (D.form == 'C_fix1') & (D.interval == 'twostage_t|fpc')]
    B = D[(D.regime == 'B') & (D.cost != 'unit') & (D.form == 'C_fix1') & (D.interval == 'regB_t')].copy()
    B['c'] = B.cost.str.extract(r'cd_cs_([0-9.]+)_vs')[0].astype(float)
    B['n_L_A'] = B.cost.str.extract(r'nL(\d+)_B')[0].astype(int)
    B['budget_A'] = B.cost.str.extract(r'_B(\d+)$')[0].astype(float)
    B = B[B.c == 10.0]
    a = A.rename(columns={'budget': 'budget_A', 'n_L': 'n_L_A'})[['estimand', 'gene', 'budget_A', 'n_L_A', 'mean_width', 'coverage', 'coverage_se']]
    j = a.merge(B[['estimand', 'gene', 'budget_A', 'n_L_A', 'budget', 'm_median', 'mean_width', 'coverage', 'coverage_se']],
                on=['estimand', 'gene', 'budget_A', 'n_L_A'], suffixes=('_A', '_B'))
    j['ratio_mean_width'] = j.mean_width_B / j.mean_width_A
    return j


def main():
    src = sys.argv[1]
    pops = []
    for p in ('p00', 'p01'):
        cfg = json.load(open(f'{src}/regcomp__pk_ACS_STATES__pkg__log_income__{p}/f3_regcomp__pk_ACS_STATES__pkg__log_income__{p}.json'))
        pops += [q for q in cfg['populations'] if keep(q)]
    R = 2000
    out, summ = {}, dict(n_populations=len(pops), R=R)
    json.dump(summ, open('b4_summary.json', 'w'), indent=1)
    for alloc in ('prop', 'equal'):
        STATE['alloc'] = alloc; sink = dict(rows=[], grows=[])
        for pop in pops:
            if alloc == 'equal' and not pop['cell_label'].startswith('B_'):
                continue
            RC.run_population(pop, {}, int(pop.get('R', R)), pop.get('cells', {}), sink, log=lambda s: None)
        G = pd.DataFrame(sink['grows'], columns=RC.RCSCHEMA.names)
        pq.write_table(pa.Table.from_pandas(G, schema=RC.RCSCHEMA, preserve_index=False), f'b4_genes__{alloc}.parquet')
        out[alloc] = G
        print(f'[b4] {alloc}: {len(G)} gene rows', flush=True)
    # anchor: the proportional rows against round 10's
    ref = pd.concat([pd.read_parquet(f'{src}/regcomp__pk_ACS_STATES__pkg__log_income__{p}/regcomp_genes.parquet') for p in ('p00', 'p01')])
    KC = ['regime', 'budget', 'cost', 'n_L', 'form', 'interval', 'estimand', 'gene']
    m = out['prop'].merge(ref, on=KC, suffixes=('', '_r10'), how='left', indicator=True)
    num = ['mean_width', 'median_width', 'coverage']
    m['max_abs_diff'] = np.max([np.abs(m[c] - m[c + '_r10']) for c in num], axis=0)
    m[KC + ['_merge', 'max_abs_diff']].to_csv('b4_anchor.csv', index=False)
    summ['anchor'] = dict(rows=int(len(m)), matched=int((m._merge == 'both').sum()), max_abs_diff=float(m.max_abs_diff.max()))
    # comparisons: regime A from the proportional run (identical under both allocations), regime B from each
    A = out['prop'][out['prop'].regime == 'A']
    rows = []
    for alloc in ('prop', 'equal'):
        D = pd.concat([A, out[alloc][out[alloc].regime == 'B']])
        j = pairs(D); j['alloc'] = alloc; rows.append(j)
        for est, je in j.groupby('estimand'):
            summ[f'{alloc}|{est}'] = dict(n=int(len(je)), B_narrower=int((je.ratio_mean_width < 1).sum()),
                                          median_ratio=float(je.ratio_mean_width.median()),
                                          cov_B_min=float(je.coverage_B.min()), cov_B_max=float(je.coverage_B.max()),
                                          cov_B_median=float(je.coverage_B.median()),
                                          mcse_cov_B_median=float(je.coverage_se_B.median()))
    J = pd.concat(rows); J.to_csv('b4_comparisons.csv', index=False)
    pd.DataFrame(STATE['sizes']).drop_duplicates().to_csv('b4_alloc_sizes.csv', index=False)
    json.dump(summ, open('b4_summary.json', 'w'), indent=1)
    print(json.dumps(summ, indent=1)); print(J.to_string())


if __name__ == '__main__':
    main()
