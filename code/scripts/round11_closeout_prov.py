"""Round 11, track closeout: provenance helpers, run on the node.

Two commands.
  write   PROVENANCE.txt for a job's output directory (docs/EXECUTION_RULES.md, section 4: job id, partition actually
          used, node, date, snapshot commit, command line, config with its sha256, PYTHONHASHSEED, md5 of every script
          that ran and of every input).
  whose   the ownership verdict of the longleaf-provenance skill for each input directory, as CSV rows.

The verdict logic is the skill's `whose()` (kernel.py), transcribed: mine (same frame), other_project (different
project id), sibling (same project, different frame), unstamped (no _provenance.json).

Usage:
  round11_closeout_prov.py write <outdir> <stage> <unit> <commit> <snapshot> <start_iso> <status>
        --command "<cmd>" --config '<json>' --scripts <rel path> ... --inputs <abs path> ...
  round11_closeout_prov.py whose <out.csv> <path> ...
"""
import argparse, csv, datetime, hashlib, json, os, platform, socket, sys

PROJECT_ID = 'proj_8450e231133d'
FRAME_ID = 'c9016697-c909-435e-82fc-ebfb9daaa857'


def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as fh:
        for b in iter(lambda: fh.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def read_stamp(path):
    d = path if os.path.isdir(path) else os.path.dirname(path)
    t = os.path.join(d, '_provenance.json')
    if not os.path.exists(t):
        return None
    try:
        return json.load(open(t))
    except Exception:
        return {}


def whose(path):
    s = read_stamp(path)
    if s is None:
        return 'unstamped', {}
    if s.get('frame_id') == FRAME_ID:
        return 'mine', s
    if s.get('project_id') and s['project_id'] != PROJECT_ID:
        return 'other_project', s
    if s.get('project_id') == PROJECT_ID:
        return 'sibling', s
    return 'foreign_session', s


def cmd_write(argv):
    ap = argparse.ArgumentParser()
    for a in ('outdir', 'stage', 'unit', 'commit', 'snapshot', 'start', 'status'):
        ap.add_argument(a)
    ap.add_argument('--command', required=True); ap.add_argument('--config', default='{}')
    ap.add_argument('--scripts', nargs='*', default=[]); ap.add_argument('--inputs', nargs='*', default=[])
    a = ap.parse_args(argv)
    cfg = json.dumps(json.loads(a.config), sort_keys=True, separators=(',', ':'))
    import numpy, pandas, scipy
    try:
        import pyarrow; pav = pyarrow.__version__
    except Exception:
        pav = 'absent'
    try:
        import sklearn; skv = sklearn.__version__
    except Exception:
        skv = 'absent'
    env = os.environ.get
    end = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
    lines = ['platform: Longleaf',
             f"slurm_job_id: {env('SLURM_JOB_ID', '')}",
             f"slurm_job_partition: {env('SLURM_JOB_PARTITION', '')}",
             f"slurm_job_account: {env('SLURM_JOB_ACCOUNT', '')}",
             f"slurm_cpus_on_node: {env('SLURM_CPUS_ON_NODE', '')}",
             f"slurm_mem_per_node: {env('SLURM_MEM_PER_NODE', '')}",
             f'node: {socket.getfqdn()}', 'track: closeout (round 11)',
             f'stage: {a.stage}', f'unit: {a.unit}', f'project_id: {PROJECT_ID}', f'frame_id: {FRAME_ID}',
             f"PYTHONHASHSEED: {env('PYTHONHASHSEED', '')}",
             f'host: {platform.platform()}', f'python: {platform.python_version()} at {sys.executable}',
             f'versions: numpy {numpy.__version__} pandas {pandas.__version__} scipy {scipy.__version__} '
             f'pyarrow {pav} sklearn {skv}',
             f'snapshot_commit: {a.commit}', f'snapshot: {a.snapshot}',
             f'command: {a.command}', f'config: {cfg}',
             f"config_sha256: {hashlib.sha256(cfg.encode()).hexdigest()}",
             f'start: {a.start}', f'end: {end}', f'status: {a.status}',
             'scripts_executed (md5, path relative to snapshot):']
    lines += [f'  {md5(os.path.join(a.snapshot, s))}  {s}' for s in a.scripts]
    lines += ['inputs (md5, path):']
    for p in a.inputs:
        lines.append(f'  {md5(p) if os.path.isfile(p) else "dir"}  {p}')
    with open(os.path.join(a.outdir, 'PROVENANCE.txt'), 'w') as fh:
        fh.write('\n'.join(lines) + '\n')


def cmd_whose(argv):
    out, paths = argv[0], argv[1:]
    with open(out, 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['path', 'verdict', 'stamp_project_id', 'stamp_frame_id', 'stamp_track', 'stamp_note'])
        for p in paths:
            v, s = whose(p)
            w.writerow([p, v, s.get('project_id', ''), s.get('frame_id', ''), s.get('track', ''), s.get('note', '')])


if __name__ == '__main__':
    {'write': cmd_write, 'whose': cmd_whose}[sys.argv[1]](sys.argv[2:])
