# H1(b): cell-weighted means over all task x label-set rows of b1_h1b_by_task.csv (abs score), to see what the 132 cells are;
# H2: HCP medians over kidney Visium's five centers (inst_by_center.csv filtered to the task).
import numpy as np, pandas as pd
R = '/work/users/w/e/weiyang/hest_replication/results/'
inputs = []
p = R + 'round11/closeout/b1/h1b_h4/b1_h1b_by_task.csv'; inputs.append(p)
bt = pd.read_csv(p); bt = bt[bt.score == 'abs']
for des, d in bt.groupby('design'):
    print('H1(b) all rows', des, 'rows', len(d), 'task-labelsets', d[['task', 'label_set']].drop_duplicates().shape[0],
          'cells', int(d.encoders.sum()), 'mean', repr(float((d.coverage_mean * d.encoders).sum() / d.encoders.sum())))
print(bt[bt.task == 'IDC'][['label_set', 'design', 'coverage_mean']].to_string())
p = R + 'round10/final_runs/F3/institution/production/inst_by_center.csv'; inputs.append(p)
ib = pd.read_csv(p)
for enc in ['uni_v2']:
    for arm in ['hcp_donor', 'hcp_center']:
        x = ib[(ib.task == 'kidney__Visium') & (ib.arm == arm) & np.isclose(ib.alpha, 0.2) & (ib.encoder == enc) & (ib.scale == 'log1p')].set_index('center_unit').coverage_median_gene
        print('H2', enc, arm, {k: repr(v) for k, v in x.items()}, 'median over', len(x), 'centers', repr(float(x.median())))
open('inputs.txt', 'w').write('\n'.join(inputs) + '\n')
