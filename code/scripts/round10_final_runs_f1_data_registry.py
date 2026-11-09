"""Round 10, track final-runs, stage F1.4a: corpus task counts, licences and the kidney match (read only).

Reads the federated project's registry and task definitions (/work/users/w/e/weiyang/st_fed_learn/data/registry/,
tasks/), never writing there, and the HEST tasks' prediction files for their sample and donor columns only.
Writes to <outdir>:
  f1_data_groups.csv           every (organ, platform) group of samples.parquet: samples, centers, distinct donor_id,
                               donor_status counts, licence counts (none, Internal, other), the task file if one exists,
                               its gene-set sizes; and pass_donor10 (at least 10 donors, L0 scope section 3);
  f1_data_candidate_samples.csv  one row per sample of every group with >= 10 donors or named by the L0 scope, with
                               center, donor, donor_status, licence, spots, patches, title and download page (metadata only);
  f1_data_hest_match.csv     each sample of the HEST tasks CCRCC, CCRCC_merged, INDIANA_KIDNEY and LUNG_XENIUM against
                               the corpus: present, corpus donor_id, organ, platform, and whether the two donor
                               partitions agree (same grouping of samples into donors in both directions);
  f1_data_stamps.json          the _provenance.json stamps found on the inputs, for the whose() record.
Usage: round10_final_runs_f1_data_registry.py <corpus_data_dir> <hest_results_dir> <outdir>
"""
import glob, json, os, sys
import numpy as np, pandas as pd, pyarrow.parquet as pq

L0_NAMED = [('kidney', 'Visium'), ('lung', 'Xenium'), ('brain', 'Visium'), ('bowel', 'Visium'), ('breast', 'Xenium'),
            ('breast', 'Visium'), ('breast', 'ST'), ('skin', 'Visium'), ('heart', 'Visium')]


def lic_class(x):
    if x is None or (isinstance(x, float) and np.isnan(x)) or str(x).strip() == '':
        return 'none'
    return 'Internal' if str(x).strip().lower() == 'internal' else 'other'


def main():
    corpus, hest, out = sys.argv[1:4]
    os.makedirs(out, exist_ok=True)
    s = pd.read_parquet(os.path.join(corpus, 'registry/samples.parquet'))
    stamps = {}
    for p in [os.path.join(corpus, 'registry/_provenance.json'), os.path.join(corpus, 'tasks/_provenance.json'),
              os.path.join(corpus, 'expr/_provenance.json'), os.path.join(corpus, 'hest/_provenance.json')]:
        stamps[p] = json.load(open(p)) if os.path.exists(p) else None
    tasks = {}
    for f in sorted(glob.glob(os.path.join(corpus, 'tasks/*.json'))):
        if os.path.basename(f).startswith('_'):
            continue
        t = json.load(open(f))
        if t.get('organ') and t.get('platform'):
            tasks[(t['organ'], t['platform'])] = dict(file=os.path.basename(f), n_int=len(t.get('genes_intersection', [])),
                                                      n_top50=len(t.get('genes_top50', [])),
                                                      task_samples=len(t.get('samples', [])), task_centers=t.get('n_centers'))
    s['lic'] = s['license'].map(lic_class)
    rows = []
    for (org, plat), g in s.groupby(['organ', 'platform'], dropna=False):
        r = dict(organ=org, platform=plat, samples=len(g), centers=g.center_id.nunique(), donors=g.donor_id.nunique(),
                 donors_status=';'.join(f'{k}:{v}' for k, v in g.donor_status.value_counts().items()),
                 lic_none=int((g.lic == 'none').sum()), lic_internal=int((g.lic == 'Internal').sum()),
                 lic_other=int((g.lic == 'other').sum()), spots=int(g.n_spots.sum()), patches=int(g.n_patches.sum()))
        r.update(tasks.get((org, plat), dict(file='', n_int=np.nan, n_top50=np.nan, task_samples=np.nan, task_centers=np.nan)))
        r['pass_donor10'] = r['donors'] >= 10
        r['named_in_L0'] = (org, plat) in L0_NAMED
        rows.append(r)
    grp = pd.DataFrame(rows).sort_values(['donors', 'samples'], ascending=False)
    grp.to_csv(os.path.join(out, 'f1_data_groups.csv'), index=False)
    keep = {(r.organ, r.platform) for r in grp.itertuples() if r.pass_donor10 or r.named_in_L0}
    cand = s[[(o, p) in keep for o, p in zip(s.organ, s.platform)]]
    cols = ['organ', 'platform', 'sample_id', 'center_id', 'vendor_lab', 'donor_id', 'donor_status', 'license', 'lic',
            'disease', 'tissue', 'preservation', 'n_spots', 'n_patches', 'n_genes_measured', 'frac_mapped',
            'dataset_title', 'download_page']
    cand[cols].sort_values(['organ', 'platform', 'center_id', 'donor_id', 'sample_id']).to_csv(
        os.path.join(out, 'f1_data_candidate_samples.csv'), index=False)
    # kidney: HEST tasks against the corpus
    files = {'CCRCC': sorted(glob.glob(os.path.join(hest, 'round3/B1_ppi/b1_predictions__CCRCC__uni_v2.parquet'))),
             'CCRCC_merged': sorted(glob.glob(os.path.join(hest, 'round3/B1_ppi/b1_predictions__CCRCC_merged__uni_v2.parquet'))),
             'INDIANA_KIDNEY': sorted(glob.glob(os.path.join(hest, 'round4/ppi/Q2_theory/predictions_INDIANA_KIDNEY/*uni_v2*.parquet'))),
             'LUNG_XENIUM': sorted(glob.glob(os.path.join(hest, 'round4/ppi/Q2_theory/predictions/b1_predictions__LUNG_XENIUM__uni_v2.parquet')))}
    km = []
    sid = s.set_index('sample_id')
    for task, fl in files.items():
        if not fl:
            km.append(dict(task=task, note='prediction file not found')); continue
        h = pq.read_table(fl[0], columns=['sample_id', 'donor_id']).to_pandas().drop_duplicates()
        h['sample_id'] = h['sample_id'].astype(str); h['donor_id'] = h['donor_id'].astype(str)
        h['in_corpus'] = h.sample_id.isin(sid.index)
        h['corpus_donor_id'] = h.sample_id.map(sid['donor_id']); h['corpus_organ'] = h.sample_id.map(sid['organ'])
        h['corpus_platform'] = h.sample_id.map(sid['platform']); h['corpus_center'] = h.sample_id.map(sid['center_id'])
        h['corpus_donor_status'] = h.sample_id.map(sid['donor_status'])
        # partitions agree when every HEST donor maps to one corpus donor and every corpus donor to one HEST donor
        a = h.groupby('donor_id').corpus_donor_id.nunique(); b = h.groupby('corpus_donor_id').donor_id.nunique()
        h['hest_donor_maps_to_one'] = h.donor_id.map(a == 1)
        h['corpus_donor_maps_to_one'] = h.corpus_donor_id.map(b == 1)
        h['task'] = task; h['file'] = os.path.basename(fl[0])
        km.append(h)
    km = pd.concat([k if isinstance(k, pd.DataFrame) else pd.DataFrame([k]) for k in km], ignore_index=True)
    km.to_csv(os.path.join(out, 'f1_data_hest_match.csv'), index=False)
    kv = s[(s.organ == 'kidney') & (s.platform == 'Visium')]
    hk = km[(km.get('in_corpus', False) == True) & km.task.isin(['CCRCC', 'INDIANA_KIDNEY'])] if 'in_corpus' in km else km.iloc[0:0]
    summ = dict(groups=len(grp), groups_pass_donor10=int(grp.pass_donor10.sum()),
                kidney_visium=dict(samples=len(kv), centers=int(kv.center_id.nunique()), donors=int(kv.donor_id.nunique())),
                hest_tasks={t: dict(samples=int((km.task == t).sum()),
                                           in_corpus=int(((km.task == t) & (km.get('in_corpus') == True)).sum()),
                                           hest_donors=int(km.loc[km.task == t, 'donor_id'].nunique()) if 'donor_id' in km else 0,
                                           partitions_agree=bool(km.loc[km.task == t, ['hest_donor_maps_to_one', 'corpus_donor_maps_to_one']].fillna(False).all().all()))
                                   for t in files},
                kidney_visium_samples_in_hest_tasks=int(kv.sample_id.isin(hk.sample_id).sum()),
                kidney_visium_donors_in_hest_tasks=int(kv.loc[kv.sample_id.isin(hk.sample_id), 'donor_id'].nunique()))
    lx = s[(s.organ == 'lung') & (s.platform == 'Xenium')]
    summ['lung_xenium'] = dict(samples=len(lx), centers=int(lx.center_id.nunique()), donors=int(lx.donor_id.nunique()),
                               samples_in_LUNG_XENIUM=int(lx.sample_id.isin(km.loc[km.task == 'LUNG_XENIUM', 'sample_id']).sum()))
    json.dump(dict(stamps=stamps), open(os.path.join(out, 'f1_data_stamps.json'), 'w'), indent=1, default=str)
    json.dump(summ, open(os.path.join(out, 'f1_data_registry_summary.json'), 'w'), indent=1)
    print(json.dumps(summ, indent=1))
    print(grp.drop(columns=['donors_status']).head(30).to_string())


if __name__ == '__main__':
    main()
