#!/usr/bin/env python
"""Round 4 conformal C3, unit 'CCRCC K': o = 0 methods (pooled, hcp, one_per) over the K axis.

One job = one (donor set, encoder, K subset). Uses round4_conf_c3 (md5 checked) unchanged.
Run: c3_ccrcc_k.py --task CCRCC:24 --encoder uni_v2 --ks 4,6,8 --out out/<tag> --tag <tag>
Writes c3_o_sweep / c3_full / c3_by_fold / c3_K_sweep tables for the tag, row-count and column
checks (c3_checks__<tag>.csv), the K = 10 comparison with round 3 a4b_hcp_K10 when K = 10 is in
the subset, node_info.txt (CPU vendor), and stamps the directory.
"""
import argparse, hashlib, os, sys, time
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import round4_conf_c3 as C
import round4_conf_io as IO

CORE_MD5 = "2d8418677cf8290eec89a14c315b92cd"
MAP = {"pooled": "pooled", "hcp": "hcp", "one_per": "dwr"}


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def cpu_vendor():
    v, m = "unknown", "unknown"
    try:
        for ln in open("/proc/cpuinfo"):
            if ln.startswith("vendor_id") and v == "unknown":
                v = ln.split(":")[1].strip()
            if ln.startswith("model name") and m == "unknown":
                m = ln.split(":")[1].strip()
    except Exception:
        pass
    return v, m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True)
    ap.add_argument("--encoder", required=True)
    ap.add_argument("--ks", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tag", required=True)
    a = ap.parse_args()
    ks = [int(k) for k in a.ks.split(",")]
    assert md5(C.__file__) == CORE_MD5, f"core module md5 {md5(C.__file__)}"
    IO.check_harness()
    os.makedirs(a.out, exist_ok=True)
    IO.code_head = C._read_head
    IO.stamp(a.out, track="conformal-C3-CCRCC-K", note=f"CCRCC K sweep o=0 {a.tag}")
    ven, mod = cpu_vendor()
    open(f"{a.out}/node_info.txt", "w").write(
        f"host={os.uname().nodename}\ncpu_vendor={ven}\ncpu_model={mod}\n"
        f"partition={os.environ.get('SLURM_JOB_PARTITION','')}\njob={os.environ.get('SLURM_JOB_ID','')}\n"
        f"core_md5={md5(C.__file__)}\nscript_md5={md5(os.path.abspath(__file__))}\n")
    T = C.load_task(a.task, a.encoder)
    nf = len(T.fold_names())
    rows, checks, t0 = [], [], time.time()
    for K in ks:
        specs = T.specs(K, n_cal_draws=C.N_CAL_DRAWS, folds=T.fold_names())
        krows = []
        for i, sp in enumerate(specs):
            fit = T.fit(sp)
            krows += C.o0_rows(fit, alphas=C.ALPHAS, methods=C.O0_METHODS, dwr_reps=C.DWR_REPS)
            if (i + 1) % 12 == 0:
                print(f"K={K} {i+1}/{len(specs)} fits {time.time()-t0:.0f}s", flush=True)
        rows += krows
        d = pd.DataFrame(krows)
        exp = len(specs) * len(C.O0_METHODS) * len(C.ALPHAS)
        checks.append(dict(check=f"rowcount_K{K}", value=len(d), expected=exp, passed=len(d) == exp,
                           note=f"{nf} folds, {len(specs)} fold x draw specs, 3 methods, 2 alphas"))
        checks.append(dict(check=f"o_all_zero_K{K}", value=int((d.o != 0).sum()), expected=0,
                           passed=bool((d.o == 0).all()), note=""))
        checks.append(dict(check=f"K_col_K{K}", value=float(d.K.mean()), expected=K,
                           passed=bool((d.K == K).all()), note="K column equals design K"))
        pd.DataFrame(rows)[C.FIXED_COLS + C.EXTRA_COLS].to_csv(f"{a.out}/partial_rows__{a.tag}.csv", index=False)
        if K == 10:
            ref = pd.read_csv(f"{C.IO.DATA_ROOT}/results/round3/A4_scores/a4b_hcp_K10__{a.encoder}.csv")
            ref["fold"] = ref["fold"].astype(str); ref["donor_set"] = ref["donor_set"].astype(str)
            ds = C.TASKS[a.task]["donor_set"]
            for m, rm in MAP.items():
                x = d[(d.method == m) & (d.alpha == 0.1)].copy(); x["fold"] = x["fold"].astype(str)
                r = ref[(ref.arm == "K10") & (ref.donor_set == ds) & (ref.method == rm)].rename(columns=lambda c: c + "_ref")
                j = x.merge(r, left_on=["fold", "cal_draw"], right_on=["fold_ref", "draw_ref"])
                okn = len(j) == len(x) == len(r)
                for col in ("coverage", "width_mean", "width_median"):
                    dd = float((j[col] - j[col + "_ref"]).abs().max()) if len(j) else np.nan
                    checks.append(dict(check=f"K10_vs_a4b_{rm}_{col}", value=dd, expected=0.0,
                                       passed=bool(okn and dd <= 1e-12),
                                       note=f"tol 1e-12; within 1e-9: {bool(okn and dd <= 1e-9)}; n={len(j)} cpu={ven}"))
                nfin = int((j["finite"] != j["finite_ref"]).sum()) if len(j) else -1
                checks.append(dict(check=f"K10_finite_flag_{rm}", value=nfin, expected=0, passed=bool(okn and nfin == 0), note=""))
                for mc, rc in (("n_T_donors", "n_T_donors"), ("n_T_matched", "n_T_spots_matched"), ("n_C", "n_C"), ("K", "n_cal_units")):
                    dd = float((j[mc] - j[rc + "_ref"]).abs().max()) if len(j) else np.nan
                    checks.append(dict(check=f"K10_design_{rm}_{mc}", value=dd, expected=0.0, passed=bool(okn and dd == 0), note=""))
    tot = pd.DataFrame(rows)
    assert list(C.to_c3(rows).columns) == C.FIXED_COLS
    checks.append(dict(check="fixed_columns_exact", value=len(C.FIXED_COLS), expected=15,
                       passed=list(C.to_c3(rows).columns) == C.FIXED_COLS, note=",".join(C.FIXED_COLS)))
    ck = pd.DataFrame(checks)
    ck.to_csv(f"{a.out}/c3_checks__{a.tag}.csv", index=False)
    C.write_frag(rows, a.out, a.tag, stage="C3_CCRCC_K", script=os.path.abspath(__file__),
                 cfg=dict(task=a.task, encoder=a.encoder, ks=ks, alphas=list(C.ALPHAS), dwr_reps=C.DWR_REPS,
                          cal_draws=C.N_CAL_DRAWS, cpu_vendor=ven),
                 note=f"CCRCC K sweep o=0 {a.tag}")
    os.remove(f"{a.out}/partial_rows__{a.tag}.csv")
    print(ck[["check", "value", "expected", "passed"]].to_string(index=False))
    print(f"done {len(tot)} rows {time.time()-t0:.0f}s")
    return 0 if bool(ck.passed.all()) else 5


if __name__ == "__main__":
    sys.exit(main())
