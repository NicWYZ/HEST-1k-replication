# Independent recomputation of G2 report section 6.1 / 5 (A5) / 3 (A2.1, R10 vs reference) numbers.
import glob, json, os
import numpy as np, pandas as pd
import pyarrow.parquet as pq
C = '/work/users/w/e/weiyang/hest_replication/results/round11/closeout/predict/'
units = []
for t in ['kidney__Visium', 'bowel__Visium', 'LUNG_XENIUM']:
    for a in ['R10', 'H', 'C', 'P', 'V', 'E']:
        d = f'{t}__{a}__donor' + ('_v2' if (t == 'kidney__Visium' and a == 'E') else '')
        units.append((t, a, 'donor', C + d))
units.append(('kidney__Visium', 'P', 'center', C + 'kidney__Visium__P__center'))
units.append(('kidney__Visium', 'R10', 'center', C + 'kidney__Visium__R10__center'))
inputs = []

def pearson_cols(Y, F):
    Y = Y - Y.mean(0); F = F - F.mean(0)
    num = (Y * F).sum(0); den = np.sqrt((Y * Y).sum(0) * (F * F).sum(0))
    with np.errstate(invalid='ignore', divide='ignore'):
        return num / den

rows = []; foldmed = {}; maxdiff = {}
for t, a, des, d in units:
    pf = glob.glob(d + '/pred__*.parquet'); ff = glob.glob(d + '/pred_folds__*.csv'); sf = glob.glob(d + '/pred_summary__*.json')
    assert len(pf) == len(ff) == len(sf) == 1, d
    inputs += [pf[0], ff[0], sf[0]]
    names = pq.read_schema(pf[0]).names
    ycols = [c for c in names if c.startswith('y_log1p__')]
    genes = [c[len('y_log1p__'):] for c in ycols]
    fcols = ['f_log1p__' + g for g in genes]
    assert all(c in names for c in fcols)
    df = pd.read_parquet(pf[0], columns=['fold'] + ycols + fcols)
    Y = df[ycols].to_numpy(float); F = df[fcols].to_numpy(float)
    nnan = int(np.isnan(Y).sum() + np.isnan(F).sum())
    r_all = pearson_cols(Y, F)
    med = float(np.nanmedian(r_all))
    # per-fold Pearson from the parquet
    pfold = {}
    for fo, idx in df.groupby('fold').indices.items():
        pfold[fo] = pearson_cols(Y[idx], F[idx])
    folds = pd.read_csv(ff[0]); folds = folds[folds.scale == 'log1p']
    # compare csv per-fold pearson to parquet recomputation
    gi = {g: i for i, g in enumerate(genes)}
    rec = np.array([pfold[r.fold][gi[r.gene]] for r in folds.itertuples()])
    diff = np.nanmax(np.abs(rec - folds.pearson.to_numpy()))
    fm = folds.groupby('fold').pearson.median()
    foldmed[(t, a, des)] = fm
    summ = json.load(open(sf[0]))
    rows.append(dict(task=t, arm=a, design=des, spots=len(df), genes=len(genes), nan_cells=nnan, folds=folds.fold.nunique(),
                     median_pearson_log1p_parquet=med, median_pearson_log1p_summaryjson=summ.get('median_pearson_log1p'),
                     max_abs_diff_foldcsv_vs_parquet=float(diff)))
    print(t, a, des, med, summ.get('median_pearson_log1p'), diff, flush=True)
res = pd.DataFrame(rows)
ref = {'kidney__Visium': 0.471, 'bowel__Visium': 0.511, 'LUNG_XENIUM': 0.619}
out = []
for r in res.itertuples():
    r10 = res[(res.task == r.task) & (res.arm == 'R10') & (res.design == r.design)].median_pearson_log1p_parquet.iloc[0]
    o = dict(r._asdict()); o.pop('Index')
    o['gain_vs_R10'] = r.median_pearson_log1p_parquet - r10
    o['gain_vs_reference'] = r.median_pearson_log1p_parquet - ref[r.task] if r.design == 'donor' else np.nan
    a = foldmed[(r.task, r.arm, r.design)]; b = foldmed[(r.task, 'R10', r.design)]
    assert set(a.index) == set(b.index)
    dd = (a - b.loc[a.index])
    o['paired_median'] = dd.median(); o['paired_q25'] = dd.quantile(0.25); o['paired_q75'] = dd.quantile(0.75)
    o['share_higher'] = float((dd > 0).mean()); o['n_folds_paired'] = len(dd)
    out.append(o)
out = pd.DataFrame(out)
C_ = out[(out.arm == 'C') & (out.design == 'donor')].set_index('task').median_pearson_log1p_parquet
E_ = out[(out.arm == 'E') & (out.design == 'donor')].set_index('task').median_pearson_log1p_parquet
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 30); pd.set_option('display.precision', 17)
out.to_csv('strength_recomputed.csv', index=False)
print(out.to_string())
print('E minus C:', (E_ - C_).to_dict())
open('inputs.txt', 'w').write('\n'.join(inputs) + '\n')
