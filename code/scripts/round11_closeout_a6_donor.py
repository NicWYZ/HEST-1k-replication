"""Round 11, track closeout, A6: the donor-level quantities of one (task, arm), by a chain of round 10's scripts run
unchanged (round11_closeout_chain.py runs the steps; this file only writes the chain's spec).

Tasks and their inputs (Longleaf paths in TASKS below):
  kidney__Visium, bowel__Visium   the arm's A5 prediction file (predict/<task>__<arm>__donor[_v2]/); round 10's
                                  morphology file joins m_std for theta3.
  LUNG_XENIUM                     A5's prediction file, joined onto round 4's file of record.
  CCRCC, INDIANA_KIDNEY           a new prediction (round11_closeout_predict.py through the corpus task kidney__Visium,
                                  with the file of record's genes), joined onto round 3's (CCRCC) or round 4's
                                  (INDIANA_KIDNEY) file of record.
For the joined tasks the join runs twice, on log1p and with --scale lognorm, and each joined file is a population of
its own scale. Steps: [predict] -> [join log1p, join lognorm] -> D12 (round10_final_runs_f1_donor_diag.py) ->
cluster values (round10_final_runs_f2_cluster_values.py) -> regime A (round10_final_runs_f2_regimeA.py, theta3 and mu,
n_L 4, 8 and 16, R 20000, no bootstrap). The cluster values carry the encoder label uni_v2 for every arm, so regime A's
crc32 seeds give every arm the same draws. On CCRCC under R10 a last step checks that the new predictions equal the A2
anchor's (anchor/CCRCC__R10_v2/predict), largest absolute difference below 1e-10.
Usage: round11_closeout_a6_donor.py <task> <arm>          (in the job's output directory)
       round11_closeout_a6_donor.py compare <a.parquet> <b.parquet> <tol>
"""
import glob, json, os, sys
import numpy as np, pandas as pd

ROOT = '/work/users/w/e/weiyang/hest_replication'
B = f'{ROOT}/results/round11/closeout'
R10 = f'{ROOT}/results/round10/final_runs'
CT = '/work/users/w/e/weiyang/st_fed_learn/data/tasks'
HM = f'{R10}/F1/data_registry/f1_data_hest_match.csv'
ARMS = {'R10': 'uni_v2:none:r10', 'P': 'uni_v2:ring1:ridgecv', 'E': 'uni_v2+hoptimus0+virchow2:ring1:r10'}
CCRCC_SAMPLES = ','.join(f'INT{i}' for i in range(1, 25))
TASKS = {
    'kidney__Visium': dict(kind='corpus', morph=f'{R10}/F2/morphology/kidney__Visium/morphology__kidney__Visium.parquet'),
    'bowel__Visium': dict(kind='corpus', morph=f'{R10}/F2/morphology/bowel__Visium/morphology__bowel__Visium.parquet'),
    'LUNG_XENIUM': dict(kind='hest', record=f'{ROOT}/results/round4/ppi/Q2_theory/predictions/b1_predictions__LUNG_XENIUM__uni_v2.parquet'),
    'CCRCC': dict(kind='hest', record=f'{ROOT}/results/round3/B1_ppi/b1_predictions__CCRCC__uni_v2.parquet',
                  predict=['--map-task', 'CCRCC', '--samples', CCRCC_SAMPLES], max_unmatched='0.01'),
    'INDIANA_KIDNEY': dict(kind='hest', record=f'{ROOT}/results/round4/ppi/Q2_theory/predictions_INDIANA_KIDNEY/b1_predictions__INDIANA_KIDNEY__uni_v2.parquet',
                           predict=['--map-task', 'INDIANA_KIDNEY', '--only-mapped'], max_unmatched='0.01'),
}


def tag(arm):
    return ARMS[arm].replace(':', '__').replace('+', '-')


def a5_files(task, arm):
    d = sorted(glob.glob(f'{B}/predict/{task}__{arm}__donor*'))
    d = [x for x in d if os.path.basename(x) in (f'{task}__{arm}__donor', f'{task}__{arm}__donor_v2')]
    d = d[-1]   # a rerun's directory carries _v2 and supersedes the first
    p = glob.glob(f'{d}/pred__*.parquet'); s = glob.glob(f'{d}/pred_summary__*.json')
    assert len(p) == 1 and len(s) == 1, (d, p, s)
    return p[0], s[0]


def spec(task, arm):
    t = TASKS[task]; steps = []
    if t['kind'] == 'corpus':
        pred, _ = a5_files(task, arm)
        steps.append(dict(name='d12', script='round10_final_runs_f1_donor_diag.py', args=[pred, f'{arm}_{task}', '.']))
        pops = [dict(task=task, encoder='uni_v2', path=pred, morph_path=t['morph'],
                     scales=[dict(name='log1p', y_prefix='y_log1p__', f_prefix='f_log1p__'),
                             dict(name='lognorm', y_prefix='y_lognorm__', f_prefix='f_lognorm__')])]
    else:
        if 'predict' in t:
            steps.append(dict(name='predict', script='round11_closeout_predict.py',
                              args=[f'{CT}/kidney__Visium.json', HM, 'donor', '.', '--arm', ARMS[arm], '--tag', task,
                                    '--genes-from-parquet', t['record']] + t['predict']))
            pred = f'{{OUT}}/predict/pred__{task}__{tag(arm)}__donor.parquet'
            summ = f'{{OUT}}/predict/pred_summary__{task}__{tag(arm)}__donor.json'
        else:
            pred, summ = a5_files(task, arm)
        pops = []
        for sc in ('log1p', 'lognorm'):
            j = f'{{OUT}}/join_{sc}/b1_predictions__{task}__uni_v2.parquet'
            extra = ['--max-unmatched', t['max_unmatched']] if 'max_unmatched' in t else []
            extra += ['--scale', 'lognorm'] if sc == 'lognorm' else []
            steps.append(dict(name=f'join_{sc}', script='round11_closeout_hest_join.py', args=[t['record'], pred, summ, j] + extra))
            steps.append(dict(name=f'd12_{sc}', script='round10_final_runs_f1_donor_diag.py', args=[j, f'{arm}_{task}_{sc}', '.']))
            pops.append(dict(task=task, encoder='uni_v2', path=j, lib_task=task,
                             scales=[dict(name=sc, y_prefix='y__', f_prefix='f__')]))
    steps.append(dict(name='cv', script='round10_final_runs_f2_cluster_values.py', args=['{CONFIG}', '.'],
                      config=dict(stage='A6', unit=f'cluster_values_{task}_{arm}', repo_root=ROOT, populations=pops)))
    steps.append(dict(name='regimeA', script='round10_final_runs_f2_regimeA.py', args=['{CONFIG}', '.'],
                      config=dict(stage='A6', unit=f'regimeA_{task}_{arm}', cluster_values=[f'{{OUT}}/cv/cluster_values__{task}.parquet'],
                                  select=dict(task=[task], encoder=['uni_v2'], estimand=['theta3', 'mu']),
                                  n_grid=[4, 8, 16], extra_n={}, R=20000, R_boot=0, B=999, boot_select={})))
    if task == 'CCRCC' and arm == 'R10':
        steps.append(dict(name='check_anchor', script='round11_closeout_a6_donor.py',
                          args=['compare', pred, f'{B}/anchor/CCRCC__R10_v2/predict/pred__CCRCC__{tag(arm)}__donor.parquet', '1e-10']))
    return dict(note=f'A6 donor-level quantities, {task}, arm {arm}', steps=steps)


def compare(a, b, tol):
    A = pd.read_parquet(a); Bq = pd.read_parquet(b)
    k = ['sample_id', 'barcode']
    m = A.merge(Bq, on=k, suffixes=('_a', '_b'), validate='one_to_one')
    fc = [c for c in A.columns if c.startswith('f_')]
    d = max(float(np.nanmax(np.abs(m[c + '_a'].to_numpy(float) - m[c + '_b'].to_numpy(float)))) for c in fc)
    rep = dict(a=a, b=b, rows_a=len(A), rows_b=len(Bq), rows_matched=len(m), f_columns=len(fc), max_abs_diff=d, tol=tol,
               passed=bool(len(m) == len(A) == len(Bq) and d < tol))
    json.dump(rep, open('compare.json', 'w'), indent=1); print(json.dumps(rep, indent=1))
    return 0 if rep['passed'] else 2


def main():
    if sys.argv[1] == 'compare':
        sys.exit(compare(sys.argv[2], sys.argv[3], float(sys.argv[4])))
    task, arm = sys.argv[1], sys.argv[2]
    sp = spec(task, arm)
    json.dump(sp, open('a6_spec.json', 'w'), indent=1)
    import round11_closeout_chain as C
    sys.argv = ['round11_closeout_chain.py', 'a6_spec.json']
    C.main()


if __name__ == '__main__':
    main()
