"""Round 10, track final-runs, stage F1.4c: merge the chunked prediction files of one task, encoder and design.

Reads pred__<tag>__part<i>of<k>.parquet for i = 0..k-1 from the chunk directories given, checks that the parts' held-out
units are disjoint and cover every unit of the task, that every (sample_id, barcode) appears exactly once, and that
each part's fold equals the spot's donor (design donor) or center (design center), then writes
pred__<tag>.parquet with the parts' schema and pred_summary__<tag>.json with spot-level Pearson per gene and scale over
the merged table.
Usage: round10_final_runs_f1_predict_merge.py <tag> <k> <outdir> <chunk_dir> [<chunk_dir> ...]
"""
import glob, json, os, sys
import numpy as np, pandas as pd, pyarrow as pa, pyarrow.parquet as pq


def pearson(a, b):
    a = a - a.mean(); b = b - b.mean(); d = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / d) if d > 0 else float('nan')


def main():
    tag, k, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]; dirs = sys.argv[4:]
    os.makedirs(out, exist_ok=True)
    files = {}
    for d in dirs:
        for f in glob.glob(os.path.join(d, f'pred__{tag}__part*of{k}.parquet')):
            i = int(os.path.basename(f).split('__part')[1].split('of')[0]); assert i not in files, f'part {i} twice'; files[i] = f
    assert sorted(files) == list(range(k)), f'parts found {sorted(files)} of {k}'
    tabs = [pq.read_table(files[i]) for i in range(k)]
    schema = tabs[0].schema
    assert all(t.schema.equals(schema) for t in tabs), 'schemas differ between parts'
    sums = [json.load(open(files[i].replace('pred__', 'pred_summary__').replace('.parquet', '.json'))) for i in range(k)]
    units = [u for s in sums for u in s['units']]
    assert len(units) == len(set(units)), 'a unit is in two parts'
    T = pa.concat_tables(tabs); df = T.to_pandas()
    dup = df.duplicated(['sample_id', 'barcode']).sum(); assert dup == 0, f'{dup} spots predicted twice'
    design = sums[0]['design']; col = 'donor_id' if design == 'donor' else 'center_id'
    assert (df['fold'] == df[col]).all(), 'fold differs from the held-out unit'
    assert set(df[col]) == set(units), 'units of the parts do not cover the task'
    assert len(df) == sums[0]['spots'], f"{len(df)} spots merged against {sums[0]['spots']} in the task"
    pq.write_table(T, os.path.join(out, f'pred__{tag}.parquet'))
    genes = sorted({c.split('__', 1)[1] for c in df.columns if c.startswith('y_log1p__')})
    summ = {kk: sums[0][kk] for kk in ('task', 'encoder', 'design', 'spots', 'samples', 'donors', 'centers', 'alpha', 'n_genes', 'gene_symbols')}
    summ.update(parts=k, folds=len(units), spots_predicted=len(df), seconds_per_fold=float(np.mean([s['seconds_per_fold'] for s in sums])))
    summ['pearson'] = {sc: {g: pearson(df[f'y_{sc}__{g}'].to_numpy(), df[f'f_{sc}__{g}'].to_numpy()) for g in genes} for sc in ('log1p', 'lognorm')}
    for sc in ('log1p', 'lognorm'):
        summ[f'median_pearson_{sc}'] = float(np.nanmedian(list(summ['pearson'][sc].values())))
    json.dump(summ, open(os.path.join(out, f'pred_summary__{tag}.json'), 'w'), indent=1)
    print(json.dumps({kk: v for kk, v in summ.items() if kk != 'pearson'}, indent=1))


if __name__ == '__main__':
    main()
