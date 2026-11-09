"""Round 10, track final-runs, stage F1.4b: the inputs of the donor-label audit (read only).

For every sample of the candidate corpus tasks (organ and platform groups with at least 10 source donor labels,
f1_data_groups.csv of F1.4a), one row with what the files say about its donor: the corpus donor_id and donor_status,
HEST's own metadata fields (patient, subseries, dataset_title, study_link, download_page_link1, disease_comment,
tissue, preservation_method, data_publication_date), and any label the record has already audited (round 2's
results/round2/R5b_audit/donor_verdicts.csv, and the donor_id of the HEST tasks' prediction files, which carry the
audits of rounds 2 to 4). No verdict is assigned here. Also writes one row per study (center) with its sample count and
the distinct values of each field, which is the unit of the evidence search.
Usage: round10_final_runs_f1_audit_inputs.py <corpus_data_dir> <f1_data_groups.csv> <f1_data_hest_match.csv>
       <r5b_donor_verdicts.csv> <outdir>
"""
import json, os, sys
import numpy as np, pandas as pd

FIELDS = ['patient', 'subseries', 'dataset_title', 'study_link', 'download_page_link1', 'disease_comment', 'tissue',
          'preservation_method', 'data_publication_date', 'disease_state', 'license']


def main():
    corpus, groups, match, r5b, out = sys.argv[1:6]
    os.makedirs(out, exist_ok=True)
    s = pd.read_parquet(os.path.join(corpus, 'registry/samples.parquet'))
    c = pd.read_parquet(os.path.join(corpus, 'registry/centers.parquet'))
    g = pd.read_csv(groups)
    keep = {(r.organ, r.platform) for r in g.itertuples() if r.pass_donor10}
    cand = s[[(o, p) in keep for o, p in zip(s.organ, s.platform)]].copy()
    rows = []
    for r in cand.itertuples():
        p = os.path.join(corpus, 'hest/metadata', f'{r.sample_id}.json')
        m = json.load(open(p)) if os.path.exists(p) else {}
        d = dict(organ=r.organ, platform=r.platform, sample_id=r.sample_id, center_id=r.center_id,
                 vendor_lab=r.vendor_lab, corpus_donor_id=r.donor_id, corpus_donor_status=r.donor_status,
                 hest_metadata=os.path.exists(p))
        for k in FIELDS:
            v = m.get(k, None)
            d[f'hest_{k}'] = None if v is None or (isinstance(v, float) and np.isnan(v)) else str(v).strip()
        rows.append(d)
    a = pd.DataFrame(rows)
    hm = pd.read_csv(match)
    hm = hm[hm.task.isin(['CCRCC', 'INDIANA_KIDNEY', 'LUNG_XENIUM'])][['sample_id', 'task', 'donor_id']]
    hm = hm.rename(columns={'task': 'record_task', 'donor_id': 'record_audited_donor_id'})
    a = a.merge(hm, on='sample_id', how='left')
    v = pd.read_csv(r5b)
    vcols = [k for k in ('sample_id', 'task', 'donor_id', 'donor_label_status') if k in v.columns]
    v = v[vcols].rename(columns={'task': 'r5b_task', 'donor_id': 'r5b_donor_id', 'donor_label_status': 'r5b_status'})
    a = a.merge(v, on='sample_id', how='left')
    a = a.merge(c[['center_id', 'n_donors']].rename(columns={'n_donors': 'center_n_donors'}), on='center_id', how='left')
    a = a.merge(s[['sample_id', 'dataset_title', 'download_page']].rename(
        columns={'dataset_title': 'corpus_dataset_title', 'download_page': 'corpus_download_page'}), on='sample_id', how='left')
    a = a.sort_values(['organ', 'platform', 'center_id', 'sample_id'])
    a.to_csv(os.path.join(out, 'f1_audit_inputs.csv'), index=False)
    st = []
    for (o, pl, cid), x in a.groupby(['organ', 'platform', 'center_id']):
        st.append(dict(organ=o, platform=pl, center_id=cid, samples=len(x),
                       corpus_donors=x.corpus_donor_id.nunique(),
                       hest_patient_values=x.hest_patient.nunique(), hest_patient_missing=int(x.hest_patient.isna().sum()),
                       hest_subseries_values=x.hest_subseries.nunique(),
                       record_audited=int(x.record_audited_donor_id.notna().sum()), r5b_audited=int(x.r5b_donor_id.notna().sum()),
                       title=';'.join(sorted(set(x.corpus_dataset_title.dropna().astype(str))))[:300],
                       download_page=';'.join(sorted(set(x.corpus_download_page.dropna().astype(str))))[:300],
                       study_link=';'.join(sorted(set(x.hest_study_link.dropna())))[:300]))
    st = pd.DataFrame(st)
    st.to_csv(os.path.join(out, 'f1_audit_studies.csv'), index=False)
    print(st.drop(columns=['title', 'study_link', 'download_page']).to_string())
    print('samples', len(a), 'studies', len(st))


if __name__ == '__main__':
    main()
