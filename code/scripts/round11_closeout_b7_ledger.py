"""Round 11, track closeout, B7: round 10 jobs that wrote no provenance file, as far as sacct still shows them.

Method. sacct lists every job of user weiyang submitted in round 10's window (2026-11-08 to 2026-11-16T12:00). A job
is attributed to round 10's track final-runs when its batch script names the track's tree
(`results/round10/final_runs` or `hest_code/round10-final-runs`): the script is the file its SubmitLine names (the
submission harness keeps it under .claude-science-scratch/.claude-science/jobs/<id>/job.sh), or, for jobs submitted
with a plain sbatch from a work directory under the tree, the work directory itself. Each attributed job is looked up
in round 10's job ledger (results/round10/final_runs/job_ledger.csv, column slurm_job_id). For a job not in the ledger,
the output directories its script names (paths under results/round10/final_runs that follow OUT= or are passed as an
argument) are checked for PROVENANCE.txt.

Writes into the current directory: b7_summary.json first, then b7_round10_jobs.csv (one row per attributed job) and
b7_unattributed.csv (jobs of the window whose script was not found, so attribution was impossible).
Usage: round11_closeout_b7_ledger.py <job_ledger.csv>
"""
import json, os, re, subprocess, sys
import pandas as pd

TREE = ('results/round10/final_runs', 'hest_code/round10-final-runs')
BASE = '/work/users/w/e/weiyang/hest_replication/results/round10/final_runs'


def main():
    ledger = pd.read_csv(sys.argv[1], dtype=str)
    in_ledger = set(ledger['slurm_job_id'].dropna().astype(str))
    out = subprocess.run(['sacct', '-u', 'weiyang', '-S', '2026-11-08', '-E', '2026-11-16T12:00', '-X', '-P', '-n',
                          '-o', 'JobID,JobName%60,State,Partition,Submit,Start,End,Elapsed,WorkDir%300,SubmitLine%500'],
                         capture_output=True, text=True, check=True).stdout
    rows = [l.split('|') for l in out.strip().splitlines()]
    cols = ['job_id', 'name', 'state', 'partition', 'submit', 'start', 'end', 'elapsed', 'workdir', 'submitline']
    J = pd.DataFrame([r[:9] + ['|'.join(r[9:])] for r in rows], columns=cols)
    att, unatt = [], []
    for _, r in J.iterrows():
        m = re.search(r'(\S+\.(?:sh|sbatch))\s*$', r['submitline'].strip())
        script = m.group(1) if m else ''
        if script and not script.startswith('/'):
            script = os.path.join(r['workdir'], script)
        text = ''
        if script and os.path.isfile(script):
            try:
                text = open(script, errors='replace').read()
            except Exception:
                text = ''
        hit = any(t in text for t in TREE) or any(t in r['workdir'] for t in TREE)
        if not text and not any(t in r['workdir'] for t in TREE):
            unatt.append(dict(job_id=r['job_id'], name=r['name'], state=r['state'], submit=r['submit'],
                              workdir=r['workdir'], script=script, script_exists=os.path.isfile(script) if script else False))
            continue
        if not hit:
            continue
        outs = sorted(set(re.findall(r'OUT=("?)(' + re.escape(BASE) + r'[^\s"]*)\1', text)))
        outs = sorted({o[1] for o in outs})
        if not outs:
            outs = sorted(set(re.findall(re.escape(BASE) + r'/[^\s"\'$]+', text)))
        jid = r['job_id'].split('_')[0]
        prov = [os.path.isfile(os.path.join(o, 'PROVENANCE.txt')) for o in outs]
        att.append(dict(job_id=r['job_id'], name=r['name'], state=r['state'], partition=r['partition'],
                        submit=r['submit'], end=r['end'], elapsed=r['elapsed'], in_ledger=jid in in_ledger,
                        n_out_dirs=len(outs), out_dirs_with_provenance=int(sum(prov)),
                        out_dirs=';'.join(outs[:6]), script=script))
    A = pd.DataFrame(att); U = pd.DataFrame(unatt)
    nl = A[~A['in_ledger']] if len(A) else A
    summ = dict(window=['2026-11-08', '2026-11-16T12:00'], jobs_in_window=int(len(J)), attributed_round10=int(len(A)),
                attributed_in_ledger=int(A['in_ledger'].sum()) if len(A) else 0,
                attributed_not_in_ledger=int(len(nl)),
                not_in_ledger_by_state=nl['state'].str.split().str[0].value_counts().to_dict() if len(nl) else {},
                not_in_ledger_without_any_provenance=int((nl['out_dirs_with_provenance'] == 0).sum()) if len(nl) else 0,
                unattributed_no_script=int(len(U)), ledger_rows=int(len(ledger)),
                ledger_ids_not_seen_in_window=int(len(in_ledger - set(J['job_id'].str.split('_').str[0]))))
    json.dump(summ, open('b7_summary.json', 'w'), indent=1)
    A.to_csv('b7_round10_jobs.csv', index=False); U.to_csv('b7_unattributed.csv', index=False)
    print(json.dumps(summ, indent=1))


if __name__ == '__main__':
    main()
