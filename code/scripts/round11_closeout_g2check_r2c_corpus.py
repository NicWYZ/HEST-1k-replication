# R2c (median over genes of squared Pearson of donor values z and f, theta3, uni_v2 log1p) for kidney and bowel Visium
# from round 10's corpus cluster values (the regime A run for kidney__Visium names cluster_values_v2_corpus).
import numpy as np, pandas as pd
F = '/work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F2/cluster_values_v2_corpus/'
inputs = []
for t in ['kidney__Visium', 'bowel__Visium']:
    p = F + f'cluster_values__{t}.parquet'; inputs.append(p)
    d = pd.read_parquet(p)
    print(t, 'encoders', d.encoder.unique().tolist(), 'scales', d.scale.unique().tolist(), 'estimands', d.estimand.unique().tolist())
    d = d[(d.encoder == 'uni_v2') & (d.scale == 'log1p') & (d.estimand == 'theta3')]
    vals = [np.corrcoef(g.z, g.f)[0, 1] ** 2 for _, g in d.groupby('gene')]
    print(t, 'rows', len(d), 'donors', d.donor.nunique(), 'genes', d.gene.nunique(), 'median corr2', repr(float(np.median(vals))))
open('inputs.txt', 'w').write('\n'.join(inputs) + '\n')
