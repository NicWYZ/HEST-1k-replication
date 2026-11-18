# Second part of anchor_b1.py (first run, Slurm 9528038, stopped at kidney cluster values): join y check with
# column-order gene mapping, R2c for the remaining tasks with filters printed, and H2 kidney Pearson.
import glob, json
import numpy as np, pandas as pd, pyarrow.parquet as pq
R = '/work/users/w/e/weiyang/hest_replication/results/'
C = R + 'round11/closeout/'
F = R + 'round10/final_runs/'
inputs = []

print('=== join y check')
pp = glob.glob(C + 'anchor/CCRCC__R10_v2/predict/pred__*.parquet')[0]; inputs.append(pp)
sp = glob.glob(C + 'anchor/CCRCC__R10_v2/predict/pred_summary__*.json')[0]; inputs.append(sp)
rec_p = R + 'round3/B1_ppi/b1_predictions__CCRCC__uni_v2.parquet'; inputs.append(rec_p)
summ = json.load(open(sp))
new = pd.read_parquet(pp); rec = pd.read_parquet(rec_p)
ny = [c for c in new.columns if c.startswith('y_log1p__')]
print('new y columns (first 5)', ny[:5], 'n', len(ny), '; gene_symbols n', len(summ['gene_symbols']), summ['gene_symbols'][:5])
print('pearson keys sample', list(summ['pearson'].keys())[:3] if isinstance(summ['pearson'], dict) else type(summ['pearson']))
mp = dict(zip(summ['gene_symbols'], [c[9:] for c in ny]))
recy = [c for c in rec.columns if c.startswith('y__')]
print('record genes', len(recy), 'all in symbols:', all(c[3:] in mp for c in recy))
m = rec.merge(new, on=['sample_id', 'barcode'], how='inner')
diffs = {c[3:]: float(np.abs(m[c].to_numpy() - m['y_log1p__' + mp[c[3:]]].to_numpy()).max()) for c in recy}
s = pd.Series(diffs)
print('matched rows', len(m), 'max |y diff|', s.max(), 'median per-gene max', s.median(), 'genes over 1e-6', int((s > 1e-6).sum()))

print('=== R2c (theta3) from round 10 cluster values')


def r2c(path, task):
    inputs.append(path)
    d = pd.read_parquet(path)
    print(path.split('/')[-1], 'tasks', d.task.unique().tolist(), 'encoders', d.encoder.unique().tolist(), 'scales', d.scale.unique().tolist(), 'estimands', d.estimand.unique().tolist())
    d = d[(d.encoder == 'uni_v2') & (d.scale == 'log1p') & (d.estimand == 'theta3')]
    vals = [np.corrcoef(g.z, g.f)[0, 1] ** 2 for _, g in d.groupby('gene')]
    return dict(rows=len(d), donors=int(d.donor.nunique()), genes=int(d.gene.nunique()), median_corr2=float(np.median(vals)) if vals else None)


for t in ['CCRCC', 'INDIANA_KIDNEY', 'kidney__Visium', 'bowel__Visium', 'LUNG_XENIUM']:
    print(t, r2c(F + f'F2/cluster_values_v1/cluster_values__{t}.parquet', t))

print('=== H2 kidney Pearson from round 10 F1 spot predictions')
for enc in ['uni_v2', 'hoptimus0', 'resnet50']:
    for des in ['donor', 'center']:
        p = F + f'F1/predict/kidney__Visium__{enc}/pred__kidney__Visium__{enc}__{des}.parquet'; inputs.append(p)
        nm = pq.read_schema(p).names
        yc = [c for c in nm if c.startswith('y_log1p__')]
        d = pd.read_parquet(p, columns=yc + ['f_log1p__' + c[9:] for c in yc])
        Y = d[yc].to_numpy(float); Fm = d[['f_log1p__' + c[9:] for c in yc]].to_numpy(float)
        Y = Y - Y.mean(0); Fm = Fm - Fm.mean(0)
        r = (Y * Fm).sum(0) / np.sqrt((Y * Y).sum(0) * (Fm * Fm).sum(0))
        print(enc, des, 'spots', len(d), 'genes', len(yc), 'median pearson', repr(float(np.median(r))))
open('inputs.txt', 'w').write('\n'.join(inputs) + '\n')
