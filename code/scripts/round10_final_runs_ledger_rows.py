"""Round 10, track final-runs: job-ledger rows for jobs whose PROVENANCE.txt is under a stage directory
and whose Slurm id is not yet in the committed job_ledger.csv.

Usage: round10_final_runs_ledger_rows.py <clone> <stage_dir> <stage> <out_csv>
The unit is the output directory relative to <stage_dir>, with '/' written as '__'. The harness id is taken
from the stage's committed harness tables where the output directory can be matched, and left empty otherwise.
Account, partition, node, times, state, elapsed and requested memory come from sacct's job row, and MaxRSS is
the largest over the job's steps.
"""
import csv, glob, os, subprocess, sys

clone, stage_dir, stage, out_csv = sys.argv[1:5]
res = os.path.join(clone, 'results/round10/final_runs')
ledger = os.path.join(res, 'job_ledger.csv')
have = {r['slurm_job_id'] for r in csv.DictReader(open(ledger))}
cols = next(csv.reader(open(ledger)))

harness = {}  # output dir relative to the stage dir -> harness id
for p in glob.glob(os.path.join(res, os.path.basename(stage_dir.rstrip('/')), '*harness*.csv')) + \
        glob.glob(os.path.join(res, 'F2', '*harness*.csv')):
    for r in csv.DictReader(open(p)):
        hid = r.get('harness_job_id', '')
        if r.get('output_dir'):
            harness[r['output_dir'].split('/', 1)[1]] = hid
        elif r.get('kind'):
            k, u = r['kind'], r['unit']
            sub = {'regimeB': 'regimeB/' + u, 'refit': 'refit_norm/' + u, 'regimeA_norm_refit': 'regimeA/' + u,
                   'diagnostics': 'diagnostics/' + u, 'aggregate': u, 'cluster_values': u}.get(k)
            if sub:
                harness[sub] = hid

found = []
for p in sorted(glob.glob(os.path.join(stage_dir, '**', 'PROVENANCE*.txt'), recursive=True)):
    f = {}
    for line in open(p):
        if ':' in line and not line.startswith(' '):
            k, v = line.split(':', 1); f[k.strip()] = v.strip()
    jid = f.get('slurm_job_id', '')
    if not jid or jid in have:
        continue
    rel = os.path.relpath(os.path.dirname(p), stage_dir).replace(os.sep, '/')
    found.append((jid, rel, f.get('snapshot_commit', ''), f.get('status', '')))
seen = set(); uniq = []
for x in found:
    if x[0] not in seen:
        seen.add(x[0]); uniq.append(x)
print(f'{len(uniq)} Slurm ids not in the ledger', flush=True)

acct = {}
ids = [x[0] for x in uniq]
for i in range(0, len(ids), 100):
    o = subprocess.run(['sacct', '-j', ','.join(ids[i:i + 100]), '-P', '-n', '--format=JobIDRaw,Account,Partition,'
                        'NodeList,Submit,Start,End,State,Elapsed,ReqMem,MaxRSS'], capture_output=True, text=True).stdout
    for line in o.splitlines():
        a = line.split('|')
        if len(a) < 11:
            continue
        base = a[0].split('.')[0]
        d = acct.setdefault(base, {'rss': 0})
        if '.' not in a[0]:
            d.update(dict(zip(['account', 'partition', 'node', 'submit', 'start', 'end', 'state', 'elapsed', 'req_mem'], a[1:10])))
        r = a[10].strip()
        if r:
            mult = {'K': 1, 'M': 1024, 'G': 1024 ** 2}.get(r[-1], 1 / 1024)
            val = float(r[:-1]) if r[-1] in 'KMG' else float(r)
            d['rss'] = max(d['rss'], int(val * mult))

with open(out_csv, 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(cols)
    for jid, rel, commit, status in uniq:
        d = acct.get(jid, {})
        w.writerow([stage, rel.replace('/', '__'), harness.get(rel, ''), jid, d.get('account', ''), d.get('partition', ''),
                    d.get('node', ''), d.get('submit', ''), d.get('start', ''), d.get('end', ''), d.get('state', ''),
                    d.get('elapsed', ''), d.get('req_mem', ''), f"{d['rss']}K" if d.get('rss') else '', commit,
                    f'PROVENANCE status {status}' + ('' if d else '; no sacct record')])
print(f'wrote {out_csv}: {len(uniq)} rows; {sum(1 for j in ids if j in acct)} with sacct records')
