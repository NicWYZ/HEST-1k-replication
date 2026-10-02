#!/usr/bin/env python
"""Round 4 conformal C3, CCRCC K sweep at o = 25 (revised C3.2, plan 12.3 change 3).

Methods ghcp (paper rule, eta 0, adaptation on), ghcp_noad, within_plain; o = 25; 20 label draws;
alphas 0.1 and 0.2; CCRCC:24; K in the given subset; 3 calibration draws; specs as the o = 0 K sweep.
Assumptions and guarantees of each method are those in the docstring of round4_conf_c3.py
(md5 2d8418677cf8290eec89a14c315b92cd), used unchanged.
Run: --task CCRCC:24 --encoder E --ks 10,12,14 --out out/TAG --tag TAG
"""
import argparse, hashlib, os, sys, time
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import round4_conf_c3 as C
import round4_conf_io as IO
CORE_MD5 = "2d8418677cf8290eec89a14c315b92cd"
METHODS = ("ghcp", "ghcp_noad", "within_plain")
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    for k in ("task", "encoder", "ks", "out", "tag"):
        ap.add_argument("--" + k, required=True)
    a = ap.parse_args()
    ks = [int(k) for k in a.ks.split(",")]
    assert md5(C.__file__) == CORE_MD5
    IO.check_harness()
    os.makedirs(a.out, exist_ok=True)
    IO.code_head = C._read_head
    IO.stamp(a.out, track="conformal-C3-CCRCC-K-ghcp-o25", note=f"CCRCC K sweep GHCP o=25 {a.tag}")
    vend = mod = "unknown"
    for ln in open("/proc/cpuinfo"):
        if ln.startswith("vendor_id") and vend == "unknown": vend = ln.split(":")[1].strip()
        if ln.startswith("model name") and mod == "unknown": mod = ln.split(":")[1].strip()
    open(f"{a.out}/node_info.txt", "w").write(
        f"host={os.uname().nodename}\ncpu_vendor={vend}\ncpu_model={mod}\npartition={os.environ.get('SLURM_JOB_PARTITION','')}\n"
        f"job={os.environ.get('SLURM_JOB_ID','')}\ncore_md5={md5(C.__file__)}\nscript_md5={md5(os.path.abspath(__file__))}\n")
    T = C.load_task(a.task, a.encoder)
    rows, checks, skipped, t0 = [], [], {}, time.time()
    for K in ks:
        specs = T.specs(K, n_cal_draws=C.N_CAL_DRAWS, folds=T.fold_names())
        kr, nskip = [], 0
        for i, sp in enumerate(specs):
            fit = T.fit(sp)
            kr += C.o_rows(fit, o_grid=(25,), label_draws=range(C.N_LABEL_DRAWS), alphas=C.ALPHAS, methods=METHODS)
            nskip += int(25 in fit.skipped_o)
            if (i + 1) % 12 == 0:
                print(f"K={K} {i+1}/{len(specs)} {time.time()-t0:.0f}s", flush=True)
        rows += kr
        d = pd.DataFrame(kr)
        exp = (len(specs) - nskip) * C.N_LABEL_DRAWS * 6
        checks.append(dict(check=f"rowcount_K{K}", value=len(d), expected=exp, passed=len(d) == exp,
                           note=f"{len(specs)} specs, {nskip} skipped (o=25 leaves <10 eval spots), 20 draws x (2 ghcp x 2 alpha + within_plain x 2)"))
        checks.append(dict(check=f"o_K_K{K}", value=float(d.o.mean()), expected=25, passed=bool((d.o == 25).all() and (d.K == K).all()), note="o=25 and K column"))
        pd.DataFrame(rows)[C.FIXED_COLS + C.EXTRA_COLS].to_csv(f"{a.out}/partial_rows__{a.tag}.csv", index=False)
    ck = pd.DataFrame(checks)
    checks.append(dict(check="fixed_columns_exact", value=15, expected=15, passed=list(C.to_c3(rows).columns) == C.FIXED_COLS, note=""))
    ck = pd.DataFrame(checks); ck.to_csv(f"{a.out}/c3_checks__{a.tag}.csv", index=False)
    C.write_frag(rows, a.out, a.tag, stage="C3_CCRCC_K_ghcp_o25", script=os.path.abspath(__file__),
                 cfg=dict(task=a.task, encoder=a.encoder, ks=ks, o=25, methods=list(METHODS), label_draws=C.N_LABEL_DRAWS,
                          alphas=list(C.ALPHAS), cal_draws=C.N_CAL_DRAWS, cpu_vendor=vend),
                 note=f"CCRCC K sweep GHCP o=25 {a.tag}")
    os.remove(f"{a.out}/partial_rows__{a.tag}.csv")
    print(ck[["check", "value", "expected", "passed"]].to_string(index=False), f"done {len(rows)} rows {time.time()-t0:.0f}s")
    return 0 if bool(ck.passed.all()) else 5


if __name__ == "__main__":
    sys.exit(main())
