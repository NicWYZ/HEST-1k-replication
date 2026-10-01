#!/usr/bin/env python
"""Round 4, conformal track, stage C1: run the released GHCP code's simulation launchers.

docs/round4_conf_plan.md section 4 (C1, "GHCP reproduces every figure in its paper that its
stated settings allow") and section 10 item 2. The released code (soham-penn/hierarchical_CP) is
used unmodified at the commit given by --ghcp-code's HEAD, which is recorded. Two things are
done around it and nothing inside it:

  1. concurrent.futures.process._check_system_limits is replaced by a no-op before the launcher
     is imported, because this machine's sandbox refuses os.sysconf("SC_SEM_NSEMS_MAX") and the
     launchers always build a ProcessPoolExecutor. The check only guards the semaphore limit; the
     pool itself is unchanged.
  2. HCP_PLOTS_MARGINAL and HCP_RESULTS_MARGINAL point at --out, so the shipped paper-results/
     are not overwritten (code/paths.py reads these).

Usage: round4_conf_c1_ghcp_repro.py <launcher> --ghcp-code DIR --out DIR -- <launcher args>
"""
import os
import runpy
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    argv = sys.argv[1:]
    sep = argv.index("--")
    own, rest = argv[:sep], argv[sep + 1:]
    launcher = own[0]
    gc = own[own.index("--ghcp-code") + 1]
    out = own[own.index("--out") + 1]
    os.makedirs(out, exist_ok=True)
    os.environ["HCP_PLOTS_MARGINAL"] = os.path.join(out, "paper-results")
    os.environ["HCP_RESULTS_MARGINAL"] = os.path.join(out, "results")
    head = subprocess.run(["git", "-C", gc, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    import round4_conf_io as IO
    import concurrent.futures.process as P
    P._check_system_limits = lambda: None
    t0 = time.time()
    os.chdir(gc)
    script = os.path.join(gc, "code", "marginal", launcher)
    sys.argv = [script] + rest
    try:
        runpy.run_path(script, run_name="__main__")
        ok = True
    except SystemExit as e:
        ok = e.code in (0, None)
    IO.write_provenance(out, "C1", os.path.abspath(__file__),
                        dict(stage="C1 GHCP reproduction", launcher=launcher, args=rest,
                             ghcp_commit=head),
                        extra={"ghcp_commit": head, "launcher_md5": IO.md5(script),
                               "wall_seconds": round(time.time() - t0), "ok": ok,
                               "where": "local machine (Longleaf queue congested, per Nicolas)"})
    return 0 if ok else 5


if __name__ == "__main__":
    sys.exit(main())
