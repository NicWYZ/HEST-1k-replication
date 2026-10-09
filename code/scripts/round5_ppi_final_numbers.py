"""Numbers for docs/round5_ppi_final_report.md that no other committed file states.

Writes results/round5/ppi/E5_joint/e5_report_numbers.csv (name,value).
Run from the repository root: python3 code/scripts/round5_ppi_final_numbers.py
"""
import glob, hashlib, os
import pandas as pd

R = 'results/round5/ppi'
rows = []
def put(name, value):
    rows.append((name, value))

# E4b unit ledgers
led = []
for f in sorted(glob.glob(f'{R}/E4b_rejective/*/e4b_job_ledger__*.csv')):
    d = pd.read_csv(f); d['unit'] = os.path.basename(os.path.dirname(f)); led.append(d)
led = pd.concat(led, ignore_index=True)
def secs(s):
    s = str(s); d = 0
    if '-' in s: d, s = s.split('-'); d = int(d)
    h, m, x = (list(map(int, s.split(':'))) + [0, 0, 0])[:3]
    return d * 86400 + h * 3600 + m * 60 + x
led['sec'] = led.elapsed.map(secs)
put('e4b_jobs_total', len(led))
put('e4b_jobs_completed', int((led.state == 'COMPLETED').sum()))
put('e4b_jobs_not_completed', int((led.state != 'COMPLETED').sum()))
put('e4b_jobs_partitions', '/'.join(sorted(led.partition.unique())))
for u, g in led.groupby('unit'):
    put(f'e4b_jobs|{u}', len(g))
    put(f'e4b_jobs_failed|{u}', int((g.state != 'COMPLETED').sum()))
    put(f'e4b_max_rss_gb|{u}', round(float(g.max_rss_gb.max()), 3))
    put(f'e4b_max_elapsed_min|{u}', round(g.sec.max() / 60, 1))
i = led.max_rss_gb.idxmax()
put('e4b_max_rss_gb', round(float(led.max_rss_gb.max()), 3)); put('e4b_max_rss_job', int(led.job_id[i]))
i = led.sec.idxmax()
put('e4b_max_elapsed_min', round(led.sec.max() / 60, 1)); put('e4b_max_elapsed_job', int(led.job_id[i]))

lead = pd.read_csv(f'{R}/r5ppi_slurm_jobs.csv')
l3 = lead[lead.stage == 'E4b']
put('lead_e4b_jobs', len(l3))
put('lead_e4b_jobs_completed', int((l3.state == 'COMPLETED').sum()))
put('lead_threshold_jobs', int(l3.purpose.str.contains('thresholds').sum()))

loc = pd.read_csv(f'{R}/r5ppi_local_runs.csv')
put('local_runs_total', len(loc))
put('local_runs_e4b', int((loc.stage == 'E4b').sum()))

dl = pd.read_csv(f'{R}/code_deliveries.csv')
put('deliveries_total', len(dl))

# md5 of the scripts interval 3 added or changed
for s in ['round5_ppi_balance.py', 'round5_ppi_run.py', 'round5_ppi_common.py', 'round5_ppi_e4b_rejective.py',
          'round5_ppi_e4b_sim.py', 'round5_ppi_e4b_tests.py', 'round5_ppi_e4b_threshold.py',
          'round5_ppi_e4b_stamp_check.py', 'round5_ppi_e4b_merge.py', 'round5_ppi_e5_allocation.py',
          'round5_ppi_e5_joint.py', 'round5_ppi_e5_theta2_drops.py', 'round5_ppi_e5_superpop.py',
          'round5_ppi_final_numbers.py']:
    p = f'code/scripts/{s}'
    if os.path.exists(p):
        put(f'md5|{s}', hashlib.md5(open(p, 'rb').read()).hexdigest())

# joint design table, regime B cells failing the smallest-units rule
j = pd.read_csv(f'{R}/E5_joint/e5_joint_design.csv')
inf = j[j.block == 'inference']
put('joint_inference_rows', len(inf))
put('joint_inference_min_units_false', int((inf.min_units_ok == False).sum()))
put('joint_pset_rows', int((j.block == 'prediction_set').sum()))

# allocation: lung/census rho_c at n_L 8, and kidney
a = pd.read_csv(f'{R}/E5_joint/e5_allocation.csv')
a8 = a[a.n_L == 8]
kid = a8[a8.vtag.isin(['CCRCC', 'CCRCC_merged', 'INDIANA_KIDNEY'])]
oth = a8[a8.vtag.isin(['LUNG_XENIUM', 'ACS_STATES', 'ACS_CA_PUMA'])]
put('alloc_rho_c_nL8_kidney_min', round(kid.rho_c.min(), 2)); put('alloc_rho_c_nL8_kidney_max', round(kid.rho_c.max(), 2))
put('alloc_rho_c_nL8_other_min', round(oth.rho_c.min(), 2)); put('alloc_rho_c_nL8_other_max', round(oth.rho_c.max(), 2))
put('alloc_rows', len(a))

import sys
sys.path.insert(0, 'code/scripts')
import round5_ppi_balance as bal
for k in (1, 2):
    for pa in (0.1, 0.01):
        put(f'va|k{k}|p_a{pa}', float(bal.va_nominal(k, pa)))

pd.DataFrame(rows, columns=['name', 'value']).to_csv(f'{R}/E5_joint/e5_report_numbers.csv', index=False)
print(len(rows))
