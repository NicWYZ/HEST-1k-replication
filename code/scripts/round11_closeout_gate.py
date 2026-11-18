"""Round 11, track closeout: gate bookkeeping, run as a job on Longleaf before each gate push.

1. provenance_index.csv: every PROVENANCE.txt under the track's results root (this track's jobs and the B1 sub-agent's),
   with its Slurm id, partition, status, snapshot commit, whether that commit is an ancestor of the gate commit in the
   track's clone, and for each script it lists whether its md5 equals the md5 of that path at the commit
   (`git show <commit>:<path>`). Scripts not in the repository at that commit (the B1 sub-agent's, which ran from
   b1/scripts/) are checked against the md5 of the file of the same name under code/scripts/ at the gate commit.
2. job_ledger.csv: one row per Slurm id found in a PROVENANCE.txt or a slurm stdout under _slurm/, with sacct's state,
   partition, node, submit, start, end, elapsed, requested memory and MaxRSS.
3. code_deliveries.csv: one row per snapshot under _snapshots/ (commit, creation time, md5 of every file in MD5SUMS).
4. b1_width_ratio_medians.csv: the B1 sub-agent's per-gene fix1/classical width ratios (b1/h3/b1_h3_width_ratio_by_gene.csv)
   as the median over genes per task, which its summary left empty.
Writes gate_summary.json first.
Usage: round11_closeout_gate.py <results_root> <clone> <gate_commit>
"""
import csv, glob, hashlib, json, os, re, subprocess, sys
import pandas as pd


def md5b(b):
    return hashlib.md5(b).hexdigest()


def git(clone, *a):
    return subprocess.run(['git', '--no-optional-locks', '-C', clone] + list(a), capture_output=True)


def parse_prov(p):
    d, scripts, mode = {}, [], None
    for line in open(p, errors='replace'):
        line = line.rstrip('\n')
        if line.startswith('scripts'):
            mode = 's'; continue
        if line.startswith('inputs') or line.startswith('input_files'):
            mode = 'i'; continue
        if mode == 's' and line.startswith('  '):
            parts = line.split()
            if len(parts) >= 2:
                scripts.append((parts[0], parts[1]))
            continue
        if ':' in line and not line.startswith(' '):
            k, v = line.split(':', 1); d[k.strip()] = v.strip()
    return d, scripts


def main():
    root, clone, gate = sys.argv[1:4]
    rows, ids = [], set()
    for p in sorted(glob.glob(f'{root}/**/PROVENANCE.txt', recursive=True)):
        if '/_snapshots/' in p:
            continue
        d, scripts = parse_prov(p)
        jid = d.get('slurm_job_id') or d.get('job_id') or ''
        if jid:
            ids.add(jid)
        com = d.get('snapshot_commit', '')
        anc = git(clone, 'merge-base', '--is-ancestor', com, gate).returncode == 0 if com else None
        bad, n = [], 0
        for m, s in scripts:
            n += 1
            rel = s if s.startswith('code/') else None
            if com and rel:
                b = git(clone, 'show', f'{com}:{rel}')
                ok = b.returncode == 0 and md5b(b.stdout) == m
            else:
                name = os.path.basename(s)
                b = git(clone, 'show', f'{gate}:code/scripts/round11_closeout_{name}' if not name.startswith('round11') else f'{gate}:code/scripts/{name}')
                ok = b.returncode == 0 and md5b(b.stdout) == m
            if not ok:
                bad.append(s)
        rows.append(dict(provenance=os.path.relpath(p, root), slurm_job_id=jid, partition=d.get('slurm_job_partition', ''),
                         status=d.get('status', d.get('exit_status', '')), commit=com, commit_is_ancestor=anc,
                         scripts=n, scripts_md5_mismatch=';'.join(bad)))
    for p in glob.glob(f'{root}/_slurm/*_*.out'):
        m = re.search(r'_(\d+)\.out$', p)
        if m:
            ids.add(m.group(1))
    P = pd.DataFrame(rows)
    out = subprocess.run(['sacct', '-j', ','.join(sorted(ids)), '-n', '-P', '-o',
                          'JobID,JobName%40,State,Partition,NodeList,Submit,Start,End,Elapsed,ReqMem,MaxRSS,Account'],
                         capture_output=True, text=True).stdout
    led = {}
    for line in out.strip().splitlines():
        f = line.split('|')
        base = f[0].split('.')[0]
        r = led.setdefault(base, dict(slurm_job_id=base))
        if '.' not in f[0]:
            r.update(name=f[1], state=f[2], partition=f[3], node=f[4], submit=f[5], start=f[6], end=f[7], elapsed=f[8],
                     req_mem=f[9], account=f[11])
        elif f[10]:
            r['max_rss'] = f[10]
    L = pd.DataFrame(sorted(led.values(), key=lambda r: r['slurm_job_id']))
    D = []
    for s in sorted(glob.glob(f'{root}/_snapshots/*/MD5SUMS')):
        c = os.path.basename(os.path.dirname(s))
        for line in open(s):
            m, f = line.split(None, 1)
            D.append(dict(commit=c, created=os.path.getmtime(os.path.dirname(s)), file=f.strip(), md5=m))
    C = pd.DataFrame(D)
    W = None
    wp = f'{root}/b1/h3/b1_h3_width_ratio_by_gene.csv'
    if os.path.exists(wp):
        x = pd.read_csv(wp)
        W = x.groupby('task').agg(genes=('gene', 'size'), median_wr=('wr', 'median')).reset_index()
    summ = dict(gate_commit=gate, provenance_files=len(P), commits_not_ancestor=int((P.commit_is_ancestor == False).sum()),
                files_with_md5_mismatch=int((P.scripts_md5_mismatch != '').sum()), jobs=len(L),
                jobs_by_state=L.state.str.split().str[0].value_counts().to_dict() if len(L) else {},
                snapshots=int(C.commit.nunique()) if len(C) else 0)
    json.dump(summ, open('gate_summary.json', 'w'), indent=1)
    P.to_csv('provenance_index.csv', index=False); L.to_csv('job_ledger.csv', index=False); C.to_csv('code_deliveries.csv', index=False)
    if W is not None:
        W.to_csv('b1_width_ratio_medians.csv', index=False)
    print(json.dumps(summ, indent=1)); print(P[P.scripts_md5_mismatch != ''].to_string()); print(W)


if __name__ == '__main__':
    main()
