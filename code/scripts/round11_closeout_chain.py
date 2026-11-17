"""Round 11, track closeout: run a short chain of steps in one job, each in its own subdirectory of the job's output
directory, stopping at the first failure.

The spec is a JSON file: {"steps": [{"name": <subdir>, "script": <file in the snapshot's code/scripts>,
"args": [...], "config": <optional dict written to <subdir>/config.json and appended to args as that path>}]}.
In args, the token {OUT} is replaced by the job's output directory, {SNAP} by the snapshot's code/scripts and {CONFIG}
by the step's config path (appended at the end when no arg names it). Every
script runs with the same Python, PYTHONPATH and environment as the job. Writes chain_status.json after each step.
Usage: round11_closeout_chain.py <spec.json>
"""
import json, os, subprocess, sys, time


def main():
    spec = json.load(open(sys.argv[1])); out = os.getcwd()
    snap = os.environ['PYTHONPATH'].split(os.pathsep)[0]
    status = []
    for st in spec['steps']:
        d = os.path.join(out, st['name']); os.makedirs(d, exist_ok=False)
        args = [a.replace('{OUT}', out).replace('{SNAP}', snap) for a in st.get('args', [])]
        if 'config' in st:
            cp = os.path.join(d, 'config.json')
            cfg = json.loads(json.dumps(st['config']).replace('{OUT}', out).replace('{SNAP}', snap))
            json.dump(cfg, open(cp, 'w'), indent=1)
            args = [a.replace('{CONFIG}', cp) for a in args] if any('{CONFIG}' in a for a in args) else args + [cp]
        t0 = time.time()
        with open(os.path.join(d, 'stdout.log'), 'w') as fh:
            rc = subprocess.run([sys.executable, '-u', os.path.join(snap, st['script'])] + args, cwd=d,
                                stdout=fh, stderr=subprocess.STDOUT).returncode
        status.append(dict(step=st['name'], script=st['script'], args=args, rc=rc, seconds=round(time.time() - t0, 1)))
        json.dump(status, open(os.path.join(out, 'chain_status.json'), 'w'), indent=1)
        print(json.dumps(status[-1]), flush=True)
        if rc != 0:
            sys.exit(rc)


if __name__ == '__main__':
    main()
