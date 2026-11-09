"""Round 10, track final-runs: write PROVENANCE.txt for a job's output directory, on the node.

Usage: round10_final_runs_provenance.py <outdir> <stage> <unit> <snapshot_commit> <snapshot_dir> <start_iso> <status>
        --command "<command line>" --config '<json>' --scripts <path relative to snapshot> ... --inputs <abs path> ...
Fields follow docs/EXECUTION_RULES.md section 4 (job id, partition actually used, node, date, snapshot commit, command
line, config with its sha256, PYTHONHASHSEED, md5 of every script that ran and of every input).
"""
import argparse, datetime, hashlib, json, os, platform, socket, sys


def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as fh:
        for b in iter(lambda: fh.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    for a in ('outdir', 'stage', 'unit', 'commit', 'snapshot', 'start', 'status'):
        ap.add_argument(a)
    ap.add_argument('--command', required=True); ap.add_argument('--config', default='{}')
    ap.add_argument('--scripts', nargs='*', default=[]); ap.add_argument('--inputs', nargs='*', default=[])
    a = ap.parse_args()
    cfg = json.dumps(json.loads(a.config), sort_keys=True, separators=(',', ':'))
    import numpy, pandas, scipy
    try:
        import pyarrow; pav = pyarrow.__version__
    except Exception:
        pav = 'absent'
    env = os.environ.get
    end = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
    lines = [
        'platform: Longleaf',
        f"slurm_job_id: {env('SLURM_JOB_ID', '')}",
        f"slurm_job_partition: {env('SLURM_JOB_PARTITION', '')}",
        f"slurm_job_account: {env('SLURM_JOB_ACCOUNT', '')}",
        f"slurm_cpus_on_node: {env('SLURM_CPUS_ON_NODE', '')}",
        f"slurm_mem_per_node: {env('SLURM_MEM_PER_NODE', '')}",
        f'node: {socket.getfqdn()}',
        'track: final-runs (round 10)', 'job_prefix: claude-science-<uuid8> (set by the submission route; jobs identified by Slurm id)',
        f'stage: {a.stage}', f'unit: {a.unit}',
        'frame_id: fc04d488-f9cc-4e63-99fc-f3a50dbc17ed',
        f"PYTHONHASHSEED: {env('PYTHONHASHSEED', '')}",
        f'host: {platform.platform()}',
        f'python: {platform.python_version()} at {sys.executable}',
        f'versions: numpy {numpy.__version__} pandas {pandas.__version__} scipy {scipy.__version__} pyarrow {pav}',
        f'snapshot_commit: {a.commit}', f'snapshot: {a.snapshot}',
        f'command: {a.command}', f'config: {cfg}',
        f"config_sha256: {hashlib.sha256(cfg.encode()).hexdigest()}",
        f'start: {a.start}', f'end: {end}', f'status: {a.status}',
        'scripts_executed (md5, path relative to snapshot):']
    lines += [f'  {md5(os.path.join(a.snapshot, s))}  {s}' for s in a.scripts]
    lines += ['inputs (md5, path):'] + [f'  {md5(p)}  {p}' for p in a.inputs]
    with open(os.path.join(a.outdir, 'PROVENANCE.txt'), 'w') as fh:
        fh.write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()
