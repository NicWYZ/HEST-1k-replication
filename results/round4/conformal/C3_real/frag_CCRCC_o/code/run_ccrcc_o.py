#!/usr/bin/env python
"""C3 unit 'CCRCC o sweep': one (donor set, encoder, fold shard) of the CCRCC K = 10 o axis.

Uses round4_conf_c3 (md5 checked) unchanged. Per fit (fold x calibration draw): o = 0 rows
(pooled, hcp, one_per) at alphas 0.1 and 0.2, and the o > 0 rows (all O_METHODS) over O_GRID and 20
label draws. Row counts are checked against the design before anything is written.
Usage: run_ccrcc_o.py <task_key> <encoder> <shard> <n_shards> <outdir>
"""
import json, os, platform, sys, time
import numpy as np
import pandas as pd
import round4_conf_c3 as C

EXPECT_MD5 = "2d8418677cf8290eec89a14c315b92cd"
N_O0 = len(C.O0_METHODS) * len(C.ALPHAS)
N_O = (len([m for m in C.O_METHODS if m != "ghcp_r05code"]) * len(C.ALPHAS) + 1)  # per (o, ld)


def cpu_info():
    v = m = ""
    for line in open("/proc/cpuinfo"):
        if line.startswith("vendor_id") and not v:
            v = line.split(":", 1)[1].strip()
        if line.startswith("model name") and not m:
            m = line.split(":", 1)[1].strip()
    return dict(vendor=v, model=m, node=platform.node())


def main(task_key, enc, shard, n_shards, outdir):
    import hashlib
    md5 = hashlib.md5(open(C.__file__, "rb").read()).hexdigest()
    assert md5 == EXPECT_MD5, f"round4_conf_c3.py md5 {md5}"
    ds = task_key.split(":")[1]
    tag = f"ccrcc{ds}_{enc}_s{shard}of{n_shards}"
    out = os.path.join(outdir, tag)
    T = C.load_task(task_key, enc)
    names = T.fold_names()
    mine = names[shard::n_shards]
    specs = T.specs(K=10, n_cal_draws=C.N_CAL_DRAWS, folds=mine)
    print(f"{tag}: folds {len(mine)}/{len(names)}, fits {len(specs)}", flush=True)
    rows, exp, checks, skipped = [], 0, [], {}
    t0 = time.time()
    for i, sp in enumerate(specs):
        fit = T.fit(sp)
        if i == 0:
            for r in C.selftest(fit):
                checks.append(dict(check=r["check"], max_abs_diff=r["max_abs_diff"]))
        r0 = C.o0_rows(fit, alphas=C.ALPHAS)
        r1 = C.o_rows(fit, o_grid=C.O_GRID, label_draws=range(C.N_LABEL_DRAWS), alphas=C.ALPHAS)
        n_o = len(C.O_GRID) - len(fit.skipped_o)
        exp += N_O0 + n_o * C.N_LABEL_DRAWS * N_O
        assert len(r0) == N_O0, len(r0)
        assert len(r0) + len(r1) == N_O0 + n_o * C.N_LABEL_DRAWS * N_O, (len(r0), len(r1), n_o)
        skipped[f"{fit.fold}|cal{fit.cal_draw}"] = list(fit.skipped_o)
        rows += r0 + r1
        if (i + 1) % 6 == 0:
            print(f"  {i+1}/{len(specs)} fits, {(time.time()-t0)/(i+1):.1f}s per fit", flush=True)
    assert len(rows) == exp, (len(rows), exp)
    d = pd.DataFrame(rows)
    assert list(C.to_c3(rows).columns) == C.FIXED_COLS
    C.write_frag(rows, out, tag, stage="C3_CCRCC_o", script=os.path.abspath(__file__),
                 cfg=dict(task=task_key, enc=enc, shard=shard, n_shards=n_shards, K=10,
                          o_grid=list(C.O_GRID), label_draws=C.N_LABEL_DRAWS,
                          cal_draws=C.N_CAL_DRAWS, alphas=list(C.ALPHAS), c3_md5=md5),
                 note=f"CCRCC o sweep {tag}")
    json.dump(dict(tag=tag, rows=len(rows), expected=exp, fits=len(specs), folds=mine,
                   skipped_o=skipped, selftest=checks, cpu=cpu_info(),
                   seconds=round(time.time() - t0, 1), c3_md5=md5),
              open(os.path.join(out, "run_info.json"), "w"), indent=1)
    print("done", tag, len(rows), exp, cpu_info(), flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
