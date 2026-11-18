"""Round 11, track closeout, A0: inventory of what a stronger predictor can be built from, read only.

Writes into the current directory (the job's output directory):
  inv_summary.json      written first: counts and the schema of the corpus registry's samples table
  inv_task_encoders.csv per corpus task (round 10's six) and encoder: samples in the task JSON, audited samples,
                        samples with an embedding file, embedding width, whether the file carries coords, and the
                        share of the task's expression spots (obs_names) matched by the embedding barcodes, on the
                        first 3 audited samples
  inv_tasks.csv         per corpus task: samples, audited samples, donors, centers; registry samples of the same
                        organ and platform not in the task JSON, and how many of those have embeddings
  inv_hest_map.csv      per HEST task (CCRCC, CCRCC_merged, INDIANA_KIDNEY, LUNG_XENIUM): each sample of round 10's
                        uni_v2 prediction file, whether the corpus has a sample of the same id, and the share of the
                        file's barcodes present in the corpus's uni_v2 and virchow2 embedding files
  inputs_whose.csv      whose() verdict of every input directory read (round11_closeout_prov.py)
Usage: round11_closeout_inventory.py
"""
import glob, json, os, sys
import h5py, numpy as np, pandas as pd, pyarrow.parquet as pq
import round11_closeout_prov as P

CORPUS = '/work/users/w/e/weiyang/st_fed_learn/data'
R10 = '/work/users/w/e/weiyang/hest_replication/results/round10/final_runs'
ENCODERS = ['uni_v2', 'hoptimus0', 'resnet50', 'virchow2', 'phikon_v2']
TASKS = {'kidney__Visium': f'{CORPUS}/tasks/kidney__Visium.json',
         'bowel__Visium': f'{CORPUS}/tasks/bowel__Visium.json',
         'brain__Visium': f'{CORPUS}/tasks/brain__Visium.json',
         'breast__Xenium': f'{CORPUS}/tasks/breast__Xenium.json',
         'lung__Xenium': f'{CORPUS}/tasks/lung__Xenium.json',
         'breast__Spatial_Transcriptomics': f'{R10}/F1/task_build_breast_ST/breast__Spatial_Transcriptomics.json'}
HEST = {'CCRCC': '/work/users/w/e/weiyang/hest_replication/results/round3/B1_ppi/b1_predictions__CCRCC__uni_v2.parquet',
        'CCRCC_merged': '/work/users/w/e/weiyang/hest_replication/results/round3/B1_ppi/b1_predictions__CCRCC_merged__uni_v2.parquet',
        'INDIANA_KIDNEY': '/work/users/w/e/weiyang/hest_replication/results/round4/ppi/Q2_theory/predictions_INDIANA_KIDNEY/b1_predictions__INDIANA_KIDNEY__uni_v2.parquet',
        'LUNG_XENIUM': '/work/users/w/e/weiyang/hest_replication/results/round4/ppi/Q2_theory/predictions/b1_predictions__LUNG_XENIUM__uni_v2.parquet'}


def barcodes(path):
    with h5py.File(path, 'r') as f:
        b = np.asarray(f['barcodes' if 'barcodes' in f else 'barcode'][:]).ravel()
        return [x.decode() if isinstance(x, bytes) else str(x) for x in b], int(f['embeddings'].shape[1]) if 'embeddings' in f else -1, 'coords' in f


def emb_path(sample, enc):
    return f'{CORPUS}/hest/embeddings/{enc}/{sample}.h5'


def main():
    summ = {}
    reg = pd.read_parquet(f'{CORPUS}/registry/samples.parquet')
    summ['registry_columns'] = {c: str(t) for c, t in reg.dtypes.items()}
    summ['registry_rows'] = int(len(reg))
    for c in reg.columns:
        if reg[c].dtype == object and reg[c].nunique() < 60:
            summ.setdefault('registry_small_columns', {})[c] = reg[c].value_counts().head(40).to_dict()
    summ['encoder_file_counts'] = {e: len(glob.glob(f'{CORPUS}/hest/embeddings/{e}/*.h5')) for e in ENCODERS}
    json.dump(summ, open('inv_summary.json', 'w'), indent=1, default=str)

    te_rows, t_rows = [], []
    for name, tp in TASKS.items():
        T = json.load(open(tp))
        dmp = f'{R10}/F1/audit_verdicts/donor_map__{name}.csv'
        dm = pd.read_csv(dmp, dtype=str).drop_duplicates('sample_id').set_index('sample_id')['donor_id']
        samples = [s for s in T['samples']]
        aud = [s for s in samples if s['sample_id'] in dm.index]
        organ = T.get('organ', name.split('__')[0]); platform = T.get('platform', name.split('__', 1)[1])
        t_rows.append(dict(task=name, json=tp, samples=len(samples), audited_samples=len(aud),
                           donors=dm[[s['sample_id'] for s in aud]].nunique(),
                           centers=len({s['center_id'] for s in aud}), n_genes=len(T['genes_top50']),
                           organ=organ, platform=platform))
        for e in ENCODERS:
            have = [s for s in aud if os.path.exists(s.get('emb_paths', {}).get(e, emb_path(s['sample_id'], e)))]
            dim, coords, share = -1, None, []
            for s in have[:3]:
                b, dim, coords = barcodes(s.get('emb_paths', {}).get(e, emb_path(s['sample_id'], e)))
                import anndata as ad
                A = ad.read_h5ad(s['expr_path'], backed='r')
                share.append(float(pd.Index(b).isin(A.obs_names).mean()))
            te_rows.append(dict(task=name, encoder=e, audited_samples=len(aud), with_embedding=len(have), dim=dim,
                                coords=coords, barcode_match_share_first3=float(np.mean(share)) if share else np.nan))
    pd.DataFrame(te_rows).to_csv('inv_task_encoders.csv', index=False)
    tdf = pd.DataFrame(t_rows)
    # registry rows of the same organ and platform not in the task JSON
    oc = next((c for c in reg.columns if c.lower() in ('organ', 'tissue')), None)
    pc = next((c for c in reg.columns if c.lower() in ('platform', 'st_technology', 'technology')), None)
    sc = next((c for c in reg.columns if c.lower() in ('sample_id', 'id')), reg.columns[0])
    extra = []
    for _, r in tdf.iterrows():
        T = json.load(open(r['json'])); ins = {s['sample_id'] for s in T['samples']}
        if oc and pc:
            plat = r['platform'].replace('_', ' ')
            m = reg[(reg[oc].astype(str).str.lower() == str(r['organ']).lower()) &
                    (reg[pc].astype(str).str.replace('_', ' ').str.lower() == plat.lower())]
            ids = [x for x in m[sc].astype(str) if x not in ins]
            extra.append((len(m), len(ids), sum(os.path.exists(emb_path(x, 'uni_v2')) for x in ids), ','.join(ids[:40])))
        else:
            extra.append((-1, -1, -1, 'registry has no organ/platform column'))
    tdf['registry_same_organ_platform'] = [x[0] for x in extra]
    tdf['registry_not_in_task'] = [x[1] for x in extra]
    tdf['not_in_task_with_uni_v2'] = [x[2] for x in extra]
    tdf['not_in_task_ids_first40'] = [x[3] for x in extra]
    tdf.to_csv('inv_tasks.csv', index=False)

    h_rows = []
    for task, p in HEST.items():
        D = pq.read_table(p, columns=['sample_id', 'barcode']).to_pandas() if 'barcode' in pq.read_schema(p).names \
            else pq.read_table(p, columns=['sample_id']).to_pandas()
        for s, g in D.groupby('sample_id'):
            row = dict(task=task, sample_id=s, spots=len(g))
            for e in ('uni_v2', 'virchow2'):
                ep = emb_path(s, e)
                row[f'corpus_{e}'] = os.path.exists(ep)
                if os.path.exists(ep) and 'barcode' in g:
                    b, _, _ = barcodes(ep)
                    row[f'share_in_corpus_{e}'] = float(g['barcode'].astype(str).isin(set(b)).mean())
            h_rows.append(row)
    pd.DataFrame(h_rows).to_csv('inv_hest_map.csv', index=False)

    dirs = sorted({os.path.dirname(p) for p in TASKS.values()} | {os.path.dirname(p) for p in HEST.values()} |
                  {f'{CORPUS}/hest', f'{CORPUS}/registry', f'{CORPUS}/stimage', f'{R10}/F1/audit_verdicts'} |
                  {f'{R10}/F1/predict/{d}' for d in os.listdir(f'{R10}/F1/predict')})
    P.cmd_whose(['inputs_whose.csv'] + dirs)
    print(json.dumps({k: v for k, v in summ.items() if k != 'registry_small_columns'}, indent=1, default=str))
    print(tdf.drop(columns=['json', 'not_in_task_ids_first40']).to_string())


if __name__ == '__main__':
    main()
