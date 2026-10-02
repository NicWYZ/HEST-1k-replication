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

  3. Optionally (--subset / --merge), the launcher's process pool is replaced by one that runs
     only some of its RNG chunks. Every launcher builds a ProcessPoolExecutor per experiment and
     submits run_chunk(chunk_id, ...) once per chunk, and chunk i is seeded with
     BASE_SEED + 1000 i inside run_chunk, so a chunk's result does not depend on which process or
     job computes it. In subset mode (--subset 0,3 --store DIR) the chunks listed are computed for
     real and their returned DataFrames are pickled to DIR/e<executor>_w<chunk>.pkl; every other
     chunk is answered with a relabelled copy of a computed chunk so the launcher can finish, and
     everything the launcher writes goes to a scratch directory under --out that is not used.
     In merge mode (--merge --store DIR) no chunk is computed: each submit is answered with the
     stored DataFrame for that executor and chunk, and the launcher's own concatenation, sorting,
     summaries and CSV writing run unmodified into --out. The launcher arguments must be the same
     in every subset job and in the merge. Equality of subset+merge with a direct run is checked
     by a small-B test recorded with the reproduction.

Usage: round4_conf_c1_ghcp_repro.py <launcher> --ghcp-code DIR --out DIR
         [--subset I,J,... --store DIR | --merge --store DIR] -- <launcher args>
"""
import os
import glob
import hashlib
import pickle
import runpy
import threading
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def install_chunk_pool(mode, subset, store):
    """Replace concurrent.futures.ProcessPoolExecutor (see the module docstring, item 3)."""
    import concurrent.futures as CF
    import concurrent.futures.process as P
    Real = P.ProcessPoolExecutor
    counter = {"n": 0}
    os.makedirs(store, exist_ok=True)

    class ChunkPool(Real):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self._e = counter["n"]
            counter["n"] += 1
            self._lock = threading.Lock()
            self._template = None
            self._waiting = []

        def _path(self, wid):
            return os.path.join(store, f"e{self._e}_w{int(wid)}.pkl")

        def _answer(self, fut, wid):
            part = self._template.copy()
            if "worker_id" in part.columns:
                part["worker_id"] = int(wid)
            fut.set_result(part)

        def _computed(self, wid, real):
            part = real.result()
            with open(self._path(wid), "wb") as fh:
                pickle.dump(part, fh, protocol=pickle.HIGHEST_PROTOCOL)
            with self._lock:
                if self._template is None:
                    self._template = part
                    waiting, self._waiting = self._waiting, []
                else:
                    waiting = []
            for fut, w in waiting:
                self._answer(fut, w)

        def submit(self, fn, *args, **kwargs):
            wid = int(args[0])
            if mode == "merge":
                fut = CF.Future()
                path = self._path(wid)
                if not os.path.exists(path):
                    raise FileNotFoundError(f"merge: no stored chunk {path}")
                with open(path, "rb") as fh:
                    fut.set_result(pickle.load(fh))
                return fut
            if wid in subset:
                real = super().submit(fn, *args, **kwargs)
                real.add_done_callback(lambda f, w=wid: self._computed(w, f))
                return real
            fut = CF.Future()
            with self._lock:
                if self._template is None:
                    self._waiting.append((fut, wid))
                    return fut
            self._answer(fut, wid)
            return fut

    CF.ProcessPoolExecutor = ChunkPool
    P.ProcessPoolExecutor = ChunkPool
    return counter


def stored(store, mode, subset, counter):
    """md5 of each chunk pickle this run wrote (subset) or read (merge)."""
    if mode == "full":
        return None
    out = {}
    for f in sorted(glob.glob(os.path.join(store, "e*_w*.pkl"))):
        w = int(os.path.basename(f).split("_w")[1].split(".")[0])
        if mode == "merge" or w in subset:
            out[os.path.basename(f)] = hashlib.md5(open(f, "rb").read()).hexdigest()
    if mode == "subset":
        want = {f"e{e}_w{w}.pkl" for e in range(counter["n"]) for w in subset}
        missing = sorted(want - set(out))
        if missing:
            raise SystemExit(f"subset: chunks not stored {missing[:5]}")
    return out


def main():
    argv = sys.argv[1:]
    sep = argv.index("--")
    own, rest = argv[:sep], argv[sep + 1:]
    launcher = own[0]
    gc = own[own.index("--ghcp-code") + 1]
    out = own[own.index("--out") + 1]
    os.makedirs(out, exist_ok=True)
    mode, subset, store = "full", set(), None
    if "--store" in own:
        store = os.path.abspath(own[own.index("--store") + 1])
    if "--merge" in own:
        mode = "merge"
    elif "--subset" in own:
        mode = "subset"
        subset = {int(x) for x in own[own.index("--subset") + 1].split(",") if x.strip()}
    if mode != "full" and store is None:
        raise SystemExit("--subset and --merge need --store")
    sink = os.path.join(out, "subset_scratch") if mode == "subset" else out
    os.environ["HCP_PLOTS_MARGINAL"] = os.path.join(sink, "paper-results")
    os.environ["HCP_RESULTS_MARGINAL"] = os.path.join(sink, "results")
    head = subprocess.run(["git", "-C", gc, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    import round4_conf_io as IO
    import concurrent.futures.process as P
    P._check_system_limits = lambda: None
    counter = install_chunk_pool(mode, subset, store) if mode != "full" else None
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
                             ghcp_commit=head, mode=mode, subset=sorted(subset), store=store),
                        extra={"ghcp_commit": head, "launcher_md5": IO.md5(script),
                               "wall_seconds": round(time.time() - t0), "ok": ok,
                               "where": os.environ.get("R4CONF_WHERE", "unspecified"),
                               "slurm_job_id": os.environ.get("SLURM_JOB_ID", ""),
                               "executors": counter["n"] if counter else None,
                               "stored_chunks": stored(store, mode, subset, counter)})
    return 0 if ok else 5


if __name__ == "__main__":
    sys.exit(main())
