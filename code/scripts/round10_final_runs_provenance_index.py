"""Round 10, track final-runs: the provenance index checked before each gate push (rules, section 5).

Walks every PROVENANCE*.txt under <base>/F1 (and deeper), reads the snapshot commit and the md5 of every script
recorded as executed, and checks in the code clone that the commit is an ancestor of <ref> and that each recorded md5
equals the md5 of that path at that commit. Writes provenance_index.csv (one row per directory and script) and prints
the counts. Usage: round10_final_runs_provenance_index.py <base> <clone> <ref> <out.csv>
"""
import csv, hashlib, os, re, subprocess, sys


def git(clone, *args):
    return subprocess.run(['git', '--no-optional-locks', '-C', clone, *args], capture_output=True)


def main():
    base, clone, ref, out = sys.argv[1:5]
    rows = []
    for root, _, files in os.walk(os.path.join(base, 'F1')):
        for fn in sorted(files):
            if not (fn.startswith('PROVENANCE') and fn.endswith('.txt')):
                continue
            path = os.path.join(root, fn); txt = open(path).read()
            m = re.search(r'^snapshot_commit:\s*([0-9a-f]{40})', txt, re.M)
            jid = re.search(r'^slurm_job_id:\s*(\S+)', txt, re.M)
            st = re.search(r'^status:\s*(\S+)', txt, re.M)
            commit = m.group(1) if m else ''
            anc = bool(commit) and git(clone, 'merge-base', '--is-ancestor', commit, ref).returncode == 0
            sec = txt.split('scripts_executed', 1)[1] if 'scripts_executed' in txt else ''
            sec = sec.split('inputs', 1)[0]
            scripts = re.findall(r'^\s+([0-9a-f]{32})\s+(code/\S+)', sec, re.M)
            if not scripts:
                scripts = [('', '')]
            for md5, sp in scripts:
                at = ''
                if commit and sp:
                    g = git(clone, 'show', f'{commit}:{sp}')
                    at = hashlib.md5(g.stdout).hexdigest() if g.returncode == 0 else 'missing'
                rows.append(dict(provenance=os.path.relpath(path, base), slurm_job_id=jid.group(1) if jid else '',
                                 status=st.group(1) if st else '', commit=commit, commit_is_ancestor=anc, script=sp,
                                 md5_recorded=md5, md5_at_commit=at, md5_match=(md5 == at) if sp else ''))
    with open(out, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    dirs = {r['provenance'] for r in rows}
    no_commit = sorted({r['provenance'] for r in rows if not r['commit']})
    print(f'{len(dirs)} provenance files, {len(rows)} rows')
    print(f"commit recorded and ancestor of {ref}: {len({r['provenance'] for r in rows if r['commit_is_ancestor']})} files")
    print(f"script md5 rows: {sum(1 for r in rows if r['script'])}, matching: {sum(1 for r in rows if r['md5_match'] is True)}")
    print('files without a snapshot_commit line: ' + (', '.join(no_commit) if no_commit else 'none'))
    bad = [r for r in rows if r['script'] and r['md5_match'] is not True]
    for r in bad:
        print('MISMATCH', r['provenance'], r['script'], r['md5_recorded'], r['md5_at_commit'])


if __name__ == '__main__':
    main()
