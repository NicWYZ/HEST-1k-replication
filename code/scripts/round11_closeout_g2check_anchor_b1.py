# Independent recomputation: section 3 (A2.2 anchors, join) and B1 table H2 Pearson / H3 / D12 lodo.
import glob, json
import numpy as np, pandas as pd, pyarrow.parquet as pq
R = '/work/users/w/e/weiyang/hest_replication/results/'
C = R + 'round11/closeout/'
F = R + 'round10/final_runs/'
inputs = []
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 30); pd.set_option('display.precision', 17)


def cells(path, task=None, enc='uni_v2', scale='log1p'):
    inputs.append(path)
    d = pd.read_parquet(path)
    d = d[(d.encoder == enc) & (d.scale == scale)]
    if task:
        d = d[d.task == task]
    return d


def wr(d, n=8, est='theta3'):
    d = d[(d.n == n) & (d.estimand == est) & (d.variance == 'fpc')]
    a = d[d.arm == 'fix1'].set_index('gene'); b = d[d.arm == 'classical'].set_index('gene')
    assert a.index.is_unique and b.index.is_unique, (a.index.duplicated().sum(), b.index.duplicated().sum(), sorted(d.R.unique()))
    r = (a.median_width / b.median_width.loc[a.index])
    return dict(genes=len(r), median_wr=float(r.median()), median_cov_fix1=float(a.coverage.median()),
                median_cov_classical=float(b.coverage.median()), median_mcse_fix1=float(a.coverage_se.median()),
                R=sorted(a.R.unique().tolist()))


def r2c(path, task, est='theta3'):
    inputs.append(path)
    d = pd.read_parquet(path)
    d = d[(d.encoder == 'uni_v2') & (d.scale == 'log1p') & (d.estimand == est) & (d.task == task)]
    corr2 = d.groupby('gene').apply(lambda g: np.corrcoef(g.z, g.f)[0, 1] ** 2)
    oos = d.groupby('gene').apply(lambda g: 1 - ((g.z - g.f) ** 2).sum() / ((g.z - g.z.mean()) ** 2).sum())
    return dict(donors=int(d.donor.nunique()), genes=int(d.gene.nunique()), median_corr2=float(corr2.median()),
                median_1mSSEoverSST=float(oos.median()))


print('=== A2.2 CCRCC anchor, theta3, n=8')
res = {}
for name, p in [('R11_R10_corpus', C + 'anchor/CCRCC__R10_v2/regimeA/regimeA_cells.parquet'),
                ('R11_control_record', C + 'anchor/CCRCC__record/regimeA/regimeA_cells.parquet'),
                ('round10_F2', F + 'F2/regimeA/CCRCC__uni_v2/regimeA_cells.parquet')]:
    res[name] = wr(cells(p, 'CCRCC')); print(name, res[name])
    print(name, 'mu:', wr(cells(p, 'CCRCC'), est='mu'))
print('diff corpus - round10 width ratio:', res['R11_R10_corpus']['median_wr'] - res['round10_F2']['median_wr'])

print('=== R2c (theta3) candidate definitions')
for name, p in [('R11_R10_corpus', C + 'anchor/CCRCC__R10_v2/cv/cluster_values__CCRCC.parquet'),
                ('R11_control_record', C + 'anchor/CCRCC__record/cv/cluster_values__CCRCC.parquet'),
                ('round10_F2', F + 'F2/cluster_values_v1/cluster_values__CCRCC.parquet')]:
    print(name, r2c(p, 'CCRCC'))

print('=== D12: median over genes of per-gene files')
for p in [C + 'anchor/CCRCC__R10_v2/d12/d12_lodo_r2__R10_CCRCC_uni_v2.csv', F + 'F1/diag_r3_CCRCC/d12_lodo_r2__r3_CCRCC_uni_v2.csv',
          F + 'F1/diag_corpus_tasks/d12_lodo_r2__kidney__Visium__uni_v2.csv']:
    inputs.append(p); d = pd.read_csv(p); d = d[d.scale == 'log1p']
    print(p.split('/')[-1], 'genes', d.gene.nunique(), 'rows', len(d), 'median R2_loo_const', d.R2_loo_const.median(),
          'median R2_rawpred_loo_const', d.R2_rawpred_loo_const.median())

print('=== D12 raw-prediction LODO R2 recomputed from spot predictions (CCRCC corpus R10, log1p)')
pp = glob.glob(C + 'anchor/CCRCC__R10_v2/predict/pred__*.parquet')[0]; inputs.append(pp)
names = pq.read_schema(pp).names
yc = [c for c in names if c.startswith('y_log1p__')]
df = pd.read_parquet(pp, columns=['donor_id'] + yc + ['f_log1p__' + c[9:] for c in yc])
vals = []
for c in yc:
    g = c[9:]
    m = df.groupby('donor_id')[[c, 'f_log1p__' + g]].mean()
    y = m[c].to_numpy(); f = m['f_log1p__' + g].to_numpy(); G = len(y)
    loo = (y.sum() - y) / (G - 1)
    vals.append(1 - ((y - f) ** 2).sum() / ((y - loo) ** 2).sum())
print('spots', len(df), 'donors', df.donor_id.nunique(), 'median raw-pred LOO-const R2', float(np.median(vals)))

print('=== join check: record (round 3) vs corpus R10 predictions')
rec_p = R + 'round3/B1_ppi/b1_predictions__CCRCC__uni_v2.parquet'; inputs.append(rec_p)
summ = json.load(open(glob.glob(C + 'anchor/CCRCC__R10_v2/predict/pred_summary__*.json')[0]))
rec = pd.read_parquet(rec_p)
new = pd.read_parquet(pp)
print('record rows', len(rec), 'new rows', len(new))
key = ['sample_id', 'barcode']
print('dup keys record', int(rec.duplicated(key).sum()), 'new', int(new.duplicated(key).sum()))
m = rec.merge(new, on=key, how='left', indicator=True, suffixes=('_rec', '_new'))
unm = int((m._merge == 'left_only').sum()); print('unmatched', unm, 'share', unm / len(rec))
print('new rows not in record', len(new) - int((m._merge == 'both').sum()))
mm = m[m._merge == 'both']
print('summary keys', list(summ.keys())[:40])
syms = summ.get('gene_symbols'); ids = summ.get('genes') or summ.get('gene_ids')
recy = [c for c in rec.columns if c.startswith('y__')]
mx = None
if all(('y_log1p__' + c[3:]) in new.columns for c in recy):
    mx = max(float(np.abs(mm[c].to_numpy() - mm['y_log1p__' + c[3:]].to_numpy()).max()) for c in recy)
elif syms is not None and ids is not None and len(syms) == len(ids):
    mp = dict(zip(syms, ids))
    mx = max(float(np.abs(mm[c].to_numpy() - mm['y_log1p__' + mp[c[3:]]].to_numpy()).max()) for c in recy)
print('max |y_record - y_new| over', len(recy), 'genes:', mx)
if 'donor_id_rec' in mm:
    print('donor partition: max new ids per record donor', mm.groupby('donor_id_rec').donor_id_new.nunique().max(),
          '; max record ids per new donor', mm.groupby('donor_id_new').donor_id_rec.nunique().max())

print('=== B1 H3 width ratio from round 10 regime A cells, theta3 n=8')
units = {'CCRCC': 'CCRCC__uni_v2', 'INDIANA_KIDNEY': 'INDIANA_KIDNEY__uni_v2', 'kidney__Visium': 'kidney__Visium__uni_v2',
         'bowel__Visium': 'bowel__Visium__uni_v2', 'LUNG_XENIUM': 'LUNG_XENIUM__uni_v2__theta3__log1p'}
for t, u in units.items():
    print(t, wr(cells(F + f'F2/regimeA/{u}/regimeA_cells.parquet', t)))
print('=== B1 H3 R2c from round 10 cluster values (theta3)')
for t in units:
    print(t, r2c(F + f'F2/cluster_values_v1/cluster_values__{t}.parquet', t))

print('=== B1 H2 kidney Pearson from round 10 F1 spot predictions')
for enc in ['uni_v2', 'hoptimus0', 'resnet50']:
    for des in ['donor', 'center']:
        p = F + f'F1/predict/kidney__Visium__{enc}/pred__kidney__Visium__{enc}__{des}.parquet'; inputs.append(p)
        nm = pq.read_schema(p).names
        yc = [c for c in nm if c.startswith('y_log1p__')]
        d = pd.read_parquet(p, columns=yc + ['f_log1p__' + c[9:] for c in yc])
        Y = d[yc].to_numpy(float); Fm = d[['f_log1p__' + c[9:] for c in yc]].to_numpy(float)
        Y = Y - Y.mean(0); Fm = Fm - Fm.mean(0)
        r = (Y * Fm).sum(0) / np.sqrt((Y * Y).sum(0) * (Fm * Fm).sum(0))
        print(enc, des, 'spots', len(d), 'genes', len(yc), 'median pearson', float(np.median(r)))
open('inputs.txt', 'w').write('\n'.join(inputs) + '\n')
