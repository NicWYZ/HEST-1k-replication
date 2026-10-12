"""Round 6 cheatsheet track, C2: sample the container's memory while trials run.

The C1 memo (section 3.5) runs up to four trials at once and drops to three
if peak memory across the running trials passes 12 GB. This samples, every
INTERVAL seconds, the container's used memory (MemTotal - MemAvailable from
/proc/meminfo, which includes this session's own processes and so overstates
the trials' share) and the number of running trial sessions, and writes the
flag file FLAG once the used memory passes the limit. The runner reads the
flag before starting each trial.

    python round6_cheatsheet_memwatch.py OUT_CSV [--interval 10] [--limit-gb 12]
        [--flag /srv/r6_private/mem_over_limit]
"""
import argparse
import datetime
import os
import subprocess
import time


def meminfo():
    d = {}
    for line in open("/proc/meminfo"):
        k, v = line.split(":")
        d[k] = int(v.split()[0]) * 1024
    return d


def n_trials():
    out = subprocess.run(["pgrep", "-c", "-f", "^bwrap --unshare-all"], capture_output=True, text=True).stdout
    return int(out.strip() or 0)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--interval", type=float, default=10)
    ap.add_argument("--limit-gb", type=float, default=12)
    ap.add_argument("--flag", default="/srv/r6_private/mem_over_limit")
    a = ap.parse_args()
    new = not os.path.exists(a.out)
    with open(a.out, "a", buffering=1) as fh:
        if new:
            fh.write("utc,used_bytes,total_bytes,running_trials\n")
        while True:
            m = meminfo()
            used = m["MemTotal"] - m["MemAvailable"]
            t = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
            fh.write(f"{t},{used},{m['MemTotal']},{n_trials()}\n")
            if used > a.limit_gb * 1e9 and not os.path.exists(a.flag):
                open(a.flag, "w").write(f"{t} used {used}\n")
            time.sleep(a.interval)
