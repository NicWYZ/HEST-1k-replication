#!/usr/bin/env python3
"""ACS PUMS 2018 unit, step 2: filter, cross-fitted GBM predictor, inventory and task definition.
Usage: python acs_pums2018_analyze.py ACSDIR TASKDEF_PATH INVENTORY_PATH
ACSDIR holds what acs_pums2018_fetch.py wrote. No survey weights are used anywhere (PWGTP is used only in the filter)."""
import json, os, sys, zlib, hashlib, platform
import numpy as np, pandas as pd
import pyarrow as pa, pyarrow.parquet as pq
import sklearn
from sklearn.ensemble import HistGradientBoostingRegressor

acsdir, taskdef_path, inv_path = sys.argv[1:4]
FEATS = ['AGEP', 'COW', 'SCHL', 'MAR', 'OCCP', 'POBP', 'RELP', 'WKHP', 'SEX', 'RAC1P']
KEY = ['SERIALNO', 'SPORDER', 'ST', 'PUMA']
need = KEY + ['PINCP', 'PWGTP'] + [f for f in FEATS if f not in KEY]
pqfile = os.path.join(acsdir, 'acs_pums2018_all_columns.parquet')
pf = pq.ParquetFile(pqfile)
colinfo = [{'name': f.name, 'arrow_type': str(f.type)} for f in pf.schema_arrow]
df = pd.read_parquet(pqfile, columns=need)
manifest = json.load(open(os.path.join(acsdir, 'raw_manifest.json')))
info = json.load(open(os.path.join(acsdir, 'fetch_info.json')))
assert len(df) == pf.metadata.num_rows == info['n_rows']

before = df.groupby('ST').size()
assert len(before) == 51, len(before)
m = (df['AGEP'] > 16) & (df['PINCP'] > 100) & (df['WKHP'] > 0) & (df['PWGTP'] >= 1)
d = df[m].reset_index(drop=True)
after = d.groupby('ST').size()
N = len(d)
assert len(after) == 51
assert not d.duplicated(KEY).any(), 'person key not unique'
nan_counts = {f: int(d[f].isna().sum()) for f in FEATS + ['PINCP']}
y = np.log(d['PINCP'].to_numpy(dtype=np.float64))
assert np.isfinite(y).all()
X = d[FEATS].to_numpy(dtype=np.float64)

st = d['ST'].to_numpy()
fold_of_state = {int(s): zlib.crc32(str(int(s)).encode()) % 5 for s in np.unique(st)}
fold = np.array([fold_of_state[int(s)] for s in st])
yhat = np.full(N, np.nan)
fold_rec = []
params_rec = None
for f in range(5):
    te = fold == f
    tr = ~te
    assert te.sum() > 0
    rs = zlib.crc32(f'acs_pums2018_hgb_fold{f}'.encode())
    mod = HistGradientBoostingRegressor(random_state=rs)
    mod.fit(X[tr], y[tr])
    yhat[te] = mod.predict(X[te])
    states_f = sorted(s for s, ff in fold_of_state.items() if ff == f)
    fold_rec.append({'fold': f, 'n_states': len(states_f), 'states_ST': states_f, 'n_test_persons': int(te.sum()),
                     'n_train_persons': int(tr.sum()), 'random_state': rs, 'n_iter_fitted': int(mod.n_iter_),
                     'get_params': mod.get_params()})
    if f == 0:
        params_rec = mod.get_params()
    print('fold', f, int(te.sum()), int(mod.n_iter_), flush=True)
assert np.isfinite(yhat).all()

def r2_unit(y, p):
    return float(1 - ((y - p) ** 2).sum() / ((y - y.mean()) ** 2).sum())
ds = pd.DataFrame({'st': st, 'y': y, 'p': yhat})
gm = ds.groupby('st')[['y', 'p']].transform('mean')
yw, pw = ds['y'] - gm['y'], ds['p'] - gm['p']
r2_within = float(1 - ((yw - pw) ** 2).sum() / (yw ** 2).sum())
sm = ds.groupby('st')[['y', 'p']].mean()
r2_state = float(np.corrcoef(sm['y'], sm['p'])[0, 1] ** 2)
r2 = {'unit_level_R2': r2_unit(y, yhat),
      'within_state_R2': r2_within,
      'state_level_R2_squared_correlation_of_state_means': r2_state,
      'unit_level_squared_correlation': float(np.corrcoef(y, yhat)[0, 1] ** 2),
      'definitions': 'unit: 1-SSE/SST over all filtered persons; within-state: 1-SSE/SST after subtracting each state mean of y and of yhat; state-level: squared Pearson correlation of the 51 state means of y and yhat (unweighted by persons). Description only, not a Q2 result.'}

# predictions parquet
sch = pa.schema([('SERIALNO', pa.string()), ('SPORDER', pa.int64()), ('ST', pa.int64()), ('PUMA', pa.int64()),
                 ('log_PINCP', pa.float64()), ('yhat', pa.float64()), ('fold', pa.int64())])
out = pa.table({'SERIALNO': d['SERIALNO'].astype(str).to_numpy(), 'SPORDER': d['SPORDER'].to_numpy(dtype=np.int64),
                'ST': d['ST'].to_numpy(dtype=np.int64), 'PUMA': d['PUMA'].to_numpy(dtype=np.int64),
                'log_PINCP': y, 'yhat': yhat, 'fold': fold.astype(np.int64)}, schema=sch)
predpath = os.path.join(acsdir, 'acs_pums2018_predictions.parquet')
pq.write_table(out, predpath, compression='zstd')
pred_md5 = hashlib.md5(open(predpath, 'rb').read()).hexdigest()

# largest state and PUMAs
big = int(after.idxmax())
dbig = d[d['ST'] == big]
pc = dbig.groupby('PUMA').size()
pcs = pc.describe(percentiles=[.25, .5, .75])
age = d['AGEP'].to_numpy(dtype=np.float64)
age_mean, age_sd = float(age.mean()), float(age.std(ddof=0))
st_size = after.astype(int)

inventory = {
 'unit': 'ACS PUMS 2018 1-Year person file, 50 states and DC, through folktables',
 'folktables_version': info['folktables_version'], 'call': info['call'], 'dc_note': info['dc_note'],
 'versions': {'pandas': pd.__version__, 'pyarrow': pa.__version__, 'numpy': np.__version__,
              'sklearn': sklearn.__version__, 'python': platform.python_version()},
 'n_rows_raw': int(len(df)), 'n_columns': len(colinfo),
 'rows_per_state_before_and_after_filter': [
     {'ST': int(s), 'postal': next((x['state'] for x in manifest if int(x['fips']) == int(s)), None),
      'rows_before': int(before[s]), 'rows_after': int(after[s])} for s in before.index],
 'filter': 'AGEP > 16, PINCP > 100, WKHP > 0, PWGTP >= 1 (folktables ACSIncome adult_filter, read from folktables 0.0.12 source); survey weights not used',
 'N_after_filter': int(N), 'largest_state': {'ST': big, 'N_after_filter': int(st_size[big])},
 'n_states_with_persons_after_filter': int(len(after)),
 'min_state_N_after_filter': {'ST': int(st_size.idxmin()), 'N': int(st_size.min())},
 'columns': colinfo,
 'raw_files': manifest,
 'predictions_parquet': {'file': 'acs_pums2018_predictions.parquet', 'md5': pred_md5, 'rows': int(N)},
 'predictor': {
   'description': 'HistGradientBoostingRegressor (scikit-learn) of log(PINCP) on ' + ', '.join(FEATS) + ' (ST, PUMA and PWGTP not features), all features treated as numeric codes (no categorical_features), NaNs passed to the library unchanged; natural log; library defaults except random_state; no tuning',
   'library': 'scikit-learn', 'version': sklearn.__version__, 'get_params_fold0': params_rec,
   'feature_nan_counts_after_filter': nan_counts,
   'fold_rule': 'fold = zlib.crc32(str(int(ST)).encode()) % 5, ST the integer FIPS code as stored in the file (unpadded), so each state is held out of the model that predicts it',
   'random_state_rule': "zlib.crc32(('acs_pums2018_hgb_fold%d' % fold).encode()) per fold",
   'folds': fold_rec},
 'predictor_R2_description_only': r2,
}
json.dump(inventory, open(inv_path, 'w'), indent=1)

taskdef = {
 'task_def_version': 1, 'task': 'ACS_PUMS2018_INCOME', 'label_set': 'folktables_ACSIncome', 'source': 'folktables ACS PUMS 2018 1-Year person',
 'st_technology': 'not applicable (tabular ACS PUMS survey microdata)', 'repo_root_relative': True,
 'adaptation_note': 'A0 format adapted for tabular data as in results/round4/ppi/Q0_setup/acs_task_def.json: paths.adata/patches/embeddings and target_genes have no analogue and are replaced by paths.data and the outcome block; samples becomes clusters; the HEST donor folds are replaced by the five state folds of the predictor.',
 'paths': {'data': 'results/round4/ppi/Q0_setup/acs_pums2018/acs_pums2018_all_columns.parquet (Longleaf only, not committed)',
           'predictions': 'results/round4/ppi/Q0_setup/acs_pums2018/acs_pums2018_predictions.parquet (Longleaf only, not committed)',
           'predictions_md5': pred_md5, 'inventory': 'results/round4/ppi/Q0_setup/acs_pums2018_inventory.json',
           'person_key': KEY},
 'n_units': int(N),
 'population': {'filter': 'AGEP > 16, PINCP > 100, WKHP > 0, PWGTP >= 1 (folktables ACSIncome)',
                'survey_weights': 'NOT used. PWGTP enters only through the filter PWGTP >= 1. Every sampled person passing the filter counts once.',
                'design_based_target': 'the finite population of sampled persons that pass the filter (N = %d)' % N},
 'clusters': {
   'level_1': {'name': 'state', 'field': 'ST', 'status': 'present', 'n': int(len(after)),
               'rows_per_state_after_filter': {str(int(s)): int(v) for s, v in after.items()}},
   'level_2': {'name': 'PUMA', 'field': 'PUMA', 'status': 'present', 'nested_in': 'state (PUMA codes are unique only within a state)',
               'setting': 'second setting: PUMAs within the single state with most persons after the filter',
               'state_ST': big, 'state_N_after_filter': int(st_size[big]), 'n': int(len(pc)),
               'persons_per_PUMA': {k: float(pcs[k]) for k in ['min', '25%', '50%', '75%', 'max', 'mean', 'std']}}},
 'outcome': {'name': 'log PINCP', 'transform': 'natural log of PINCP; PINCP > 100 after the filter so the log is defined for every unit',
             'zero_or_negative_handling': 'not needed: the filter removes PINCP <= 100 before the outcome exists'},
 'covariates': {'theta_3': {'name': 'AGEP, standardised', 'raw_column': 'AGEP',
                'standardisation': 'z = (AGEP - mean) / sd over all %d filtered persons, sd with ddof=0' % N,
                'age_mean': age_mean, 'age_sd_ddof0': age_sd}},
 'estimands': {'theta_2': 'mean of log PINCP (person-weighted and cluster-weighted as in plan section Q4)',
               'theta_3': 'slope of log PINCP on standardised AGEP'},
 'predictor': {'present': True, 'fit_here': True, 'family': 'gradient-boosted regression of log PINCP',
               'library': 'scikit-learn HistGradientBoostingRegressor', 'version': sklearn.__version__,
               'features': FEATS, 'cross_fit': 'five folds of states, fold = zlib.crc32(str(int(ST)).encode()) % 5',
               'get_params_fold0': params_rec, 'defaults_no_tuning': True,
               'fold_sizes_persons': {str(r['fold']): r['n_test_persons'] for r in fold_rec},
               'fold_sizes_states': {str(r['fold']): r['n_states'] for r in fold_rec},
               'R2_description_only': r2},
 'flags': {'dc_added_to_folktables_tables': True},
 'provenance': {'generated_by': 'acs_pums2018_analyze.py', 'pythonhashseed': os.environ.get('PYTHONHASHSEED')},
}
json.dump(taskdef, open(taskdef_path, 'w'), indent=1)
print('N', N, 'largest', big, int(st_size[big]), 'pumas', len(pc), r2['unit_level_R2'], r2_within, r2_state)
