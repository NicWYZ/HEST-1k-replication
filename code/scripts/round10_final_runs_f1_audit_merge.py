"""Round 10, track final-runs, stage F1.4b: donor-label audit verdicts and the audited donor maps.

Inputs: the four evidence tables gathered by sub-agents (results/round10/final_runs/F1/audit/evidence/*.csv, one row
per sample with proposed_donor_key and the kind of evidence), the lead's decisions
(f1_audit_lead_decisions.csv: exclusions, duplicate data and flags, each with its reason), and F1.4b's inputs table
(f1_audit_inputs.csv, the corpus labels and the record's audited labels).
Verdicts (donor_label_status), applied in this order:
  1. a lead decision on the sample (excluded_pooled, excluded_mixed, excluded_not_donor, excluded_unresolved,
     duplicate_data) wins, and the sample is left out of every donor-level task;
  2. evidence 'record audit' -> record_audit, the donor label of rounds 2 to 4 (the HEST tasks' donor_id where the
     record has one), with the sources found consistent;
  3. evidence 'positive statement' -> verified;
  4. evidence 'naming only' -> naming (kept, provisional);
  5. evidence 'none found' -> unverifiable and left out, except a study with a single sample, which is one donor by
     construction (single_section, kept, its identity across studies unknown).
A flag_kept decision keeps the sample under rules 2 to 5 and records the flag.
The audited donor_id is '<proposed_donor_key>' except where the record already audited the sample, where it is the
record's label, so the HEST tasks' folds are unchanged. Writes to <outdir>:
  f1_audit_verdicts.csv     one row per sample: corpus label, audited donor_id, status, included, the decision and reason;
  f1_audit_task_counts.csv  per organ and platform: samples in, samples out by reason, donors and centers before and
                            after the audit, corpus donors, and pass_donor10 (at least 10 audited donors, L0 scope);
  donor_map__<organ>__<platform>.csv  sample_id, donor_id, center_id of the included samples, for the prediction files.
Usage: round10_final_runs_f1_audit_merge.py <evidence_dir> <lead_decisions.csv> <f1_audit_inputs.csv> <outdir>
"""
import glob, os, re, sys
import numpy as np, pandas as pd

EXCL = {'excluded_pooled', 'excluded_mixed', 'excluded_not_donor', 'excluded_unresolved', 'duplicate_data'}


def main():
    evd, decf, inp, out = sys.argv[1:5]; os.makedirs(out, exist_ok=True)
    ev = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(os.path.join(evd, '*_donor_evidence.csv')))], ignore_index=True)
    assert not ev.sample_id.duplicated().any(), 'a sample appears in two evidence tables'
    dec = pd.read_csv(decf, dtype=str).fillna('')
    a = pd.read_csv(inp, dtype=str)
    assert set(a.sample_id) == set(ev.sample_id), 'evidence and inputs cover different samples'
    m = a[['organ', 'platform', 'sample_id', 'center_id', 'corpus_donor_id', 'record_task', 'record_audited_donor_id']].merge(
        ev[['sample_id', 'proposed_donor_key', 'evidence', 'read_level', 'source_url']], on='sample_id', how='left').merge(
        dec, on='sample_id', how='left')
    m[['decision', 'target', 'reason']] = m[['decision', 'target', 'reason']].fillna('')
    n_in_study = m.groupby('center_id').sample_id.transform('size')
    status, donor = [], []
    for r, nst in zip(m.itertuples(), n_in_study):
        if r.decision in EXCL:
            status.append(r.decision); donor.append(''); continue
        rec = r.record_audited_donor_id if isinstance(r.record_audited_donor_id, str) and r.record_audited_donor_id else ''
        key = r.proposed_donor_key if isinstance(r.proposed_donor_key, str) else ''
        if r.evidence == 'record audit':
            s = 'record_audit'
        elif r.evidence == 'positive statement':
            s = 'verified'
        elif r.evidence == 'naming only':
            s = 'naming'
        elif nst == 1:
            s = 'single_section'
        else:
            s = 'unverifiable'
        if s == 'unverifiable':
            status.append(s); donor.append(''); continue
        if rec:
            d = f'{r.center_id}:{rec}'
        elif key and not key.lower().startswith('unresolved'):
            d = key
        else:
            d = f'{r.center_id}:{r.sample_id}'
        status.append(s); donor.append(d)
    m['donor_label_status'] = status; m['donor_id'] = donor
    m['included'] = m.donor_id != ''
    m.to_csv(os.path.join(out, 'f1_audit_verdicts.csv'), index=False)
    rows = []
    for (o, p), g in m.groupby(['organ', 'platform']):
        inc = g[g.included]
        r = dict(organ=o, platform=p, samples=len(g), samples_in=len(inc), corpus_donors=g.corpus_donor_id.nunique(),
                 centers=g.center_id.nunique(), donors=inc.donor_id.nunique(), centers_in=inc.center_id.nunique(),
                 pass_donor10=inc.donor_id.nunique() >= 10)
        for s in sorted(set(m.donor_label_status)):
            r[f'n_{s}'] = int((g.donor_label_status == s).sum())
        r['donors_by_center'] = ';'.join(f'{c}:{k}' for c, k in inc.groupby('center_id').donor_id.nunique().items())
        r['n_flag_kept'] = int((g.decision == 'flag_kept').sum())
        rows.append(r)
        if len(inc):
            inc[['sample_id', 'donor_id', 'center_id']].to_csv(
                os.path.join(out, f"donor_map__{o}__{re.sub('[^A-Za-z0-9]+', '_', p)}.csv"), index=False)
    t = pd.DataFrame(rows).fillna(0).sort_values('donors', ascending=False)
    t.to_csv(os.path.join(out, 'f1_audit_task_counts.csv'), index=False)
    print(t.drop(columns=['donors_by_center']).to_string()); print(m.donor_label_status.value_counts().to_string())


if __name__ == '__main__':
    main()
