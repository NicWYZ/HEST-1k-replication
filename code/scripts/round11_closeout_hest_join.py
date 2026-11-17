"""Round 11, track closeout, Part A: a new predictor's held-out predictions on a HEST task (CCRCC, CCRCC_merged,
INDIANA_KIDNEY, LUNG_XENIUM), written in the layout of the task's committed prediction file so that round 10's
cluster-value, diagnostic and design-simulation scripts read it unchanged.

The task's file of record (round 3's or round 4's b1_predictions__<task>__<encoder>.parquet) carries y__<symbol>,
f__<symbol> on log(1 + y), the morphology columns theta3 needs and the identifiers. This script copies it and replaces
every f__<symbol> by the new file's f_log1p__<ensembl id> for the same (sample_id, barcode), the symbol-to-id map being
the order of the new summary's gene_symbols (round11_closeout_predict.py with --genes-from-parquet). Checks, all
written to <out>.join.json before the parquet: every row of the file of record finds exactly one row of the new file;
y__<symbol> equals y_log1p__<id> within 1e-6 on every matched row; the donor partition of the samples agrees. If a
check fails, nothing is written but the JSON, and the script exits non-zero.
With --scale lognorm, the checks are the same (on log(1 + y)) and both y__<symbol> and f__<symbol> are then taken from
the new file's y_lognorm__<id> and f_lognorm__<id> (log(1 + 1e4 y / n), n the spot's total over its full measured
panel, as round 10's corpus files define it), so the output is that task's file on the normalised scale.
Usage: round11_closeout_hest_join.py <record.parquet> <new_pred.parquet> <new_summary.json> <out.parquet> [--scale lognorm]
"""
import json, sys
import numpy as np, pandas as pd, pyarrow as pa, pyarrow.parquet as pq


def main():
    rec_p, new_p, summ_p, out = sys.argv[1:5]
    scale = sys.argv[sys.argv.index('--scale') + 1] if '--scale' in sys.argv else 'log1p'
    rec = pq.read_table(rec_p); R = rec.to_pandas()
    S = json.load(open(summ_p)); syms = S['gene_symbols']
    new = pq.read_table(new_p).to_pandas()
    ens = [c[len('f_log1p__'):] for c in new.columns if c.startswith('f_log1p__')]
    assert len(ens) == len(syms), (len(ens), len(syms))
    rep = dict(record=rec_p, new=new_p, rows_record=int(len(R)), rows_new=int(len(new)), genes=len(syms))
    key = ['sample_id', 'barcode']
    R['_i'] = np.arange(len(R)); new['_j'] = np.arange(len(new))
    R['sample_id'] = R['sample_id'].astype(str); R['barcode'] = R['barcode'].astype(str)
    new['sample_id'] = new['sample_id'].astype(str); new['barcode'] = new['barcode'].astype(str)
    dup = int(new.duplicated(key).sum()); rep['dup_keys_new'] = dup
    m = R[key + ['_i']].merge(new[key + ['_j']], on=key, how='left')
    rep['matched'] = int(m['_j'].notna().sum()); rep['unmatched'] = int(m['_j'].isna().sum())
    rep['unmatched_by_sample'] = m[m['_j'].isna()].sample_id.value_counts().to_dict()
    ok = dup == 0 and rep['unmatched'] == 0 and len(m) == len(R)
    worst = np.nan
    if ok:
        j = m['_j'].astype(int).to_numpy()
        worst = 0.0
        for s, e in zip(syms, ens):
            d = np.abs(R[f'y__{s}'].to_numpy(np.float64) - new[f'y_log1p__{e}'].to_numpy(np.float64)[j])
            worst = max(worst, float(np.nanmax(d)))
        rep['y_max_abs_diff'] = worst
        ok = worst < 1e-6
    if ok and 'donor_id' in R.columns:
        a = R.groupby('sample_id').donor_id.first(); b = new.groupby('sample_id').donor_id.first()
        pa_ = sorted(tuple(sorted(a[a == v].index)) for v in set(a))
        pb_ = sorted(tuple(sorted(b[b == v].index)) for v in set(b[a.index]))
        rep['donor_partition_agrees'] = pa_ == pb_
        ok = ok and pa_ == pb_
    rep['passed'] = bool(ok)
    json.dump(rep, open(out + '.join.json', 'w'), indent=1, default=str)
    print(json.dumps(rep, indent=1, default=str))
    if not ok:
        sys.exit(2)
    j = m['_j'].astype(int).to_numpy()
    cols = {}
    for f in rec.schema:
        if f.name[:3] in ('f__', 'y__') and f.name[3:] in syms and (f.name[0] == 'f' or scale != 'log1p'):
            e = ens[syms.index(f.name[3:])]
            cols[f.name] = pa.array(new[f'{f.name[0]}_{scale}__{e}'].to_numpy(np.float64)[j].astype(f.type.to_pandas_dtype()), type=f.type)
        else:
            cols[f.name] = rec.column(f.name)
    missing = [f.name for f in rec.schema if f.name.startswith('f__') and f.name[3:] not in syms]
    assert not missing, f'f columns without a new prediction: {missing[:5]}'
    pq.write_table(pa.Table.from_pydict(cols, schema=rec.schema), out)


if __name__ == '__main__':
    main()
