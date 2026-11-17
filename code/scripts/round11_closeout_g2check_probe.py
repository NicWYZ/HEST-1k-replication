import pandas as pd, glob, json, pyarrow.parquet as pq
R='/work/users/w/e/weiyang/hest_replication/results/'
C=R+'round11/closeout/'
files=[C+'anchor/CCRCC__R10_v2/regimeA/regimeA_cells.parquet', C+'anchor/CCRCC__R10_v2/cv/cluster_values__CCRCC.parquet',
 R+'round10/final_runs/F2/regimeA/CCRCC__uni_v2/regimeA_cells.parquet', R+'round10/final_runs/F2/cluster_values_v1/cluster_values__CCRCC.parquet',
 C+'anchor/CCRCC__record/regimeA/regimeA_cells.parquet', R+'round3/B1_ppi/b1_predictions__CCRCC__uni_v2.parquet']
files+=sorted(glob.glob(C+'predict/LUNG_XENIUM__P__donor/pred__*.parquet'))
for f in files:
    s=pq.read_schema(f); print('==',f, pq.ParquetFile(f).metadata.num_rows); print(list(s.names)[:30], len(s.names))
for f in files[:6]:
    d=pd.read_parquet(f) if 'b1_pred' not in f else pd.read_parquet(f).iloc[:3]
    print('==',f); print(d.head(3).T)
    for c in d.columns:
        if d[c].dtype==object and d[c].nunique()<40: print(c, sorted(d[c].unique().tolist()))
        elif c in ('n','n_L','R','arm'): print(c, sorted(d[c].unique().tolist())[:40])
for f in glob.glob(C+'anchor/*/regimeA/config.json')+glob.glob(C+'anchor/*/cv/config.json'): print(f, open(f).read())
