#!/usr/bin/env python
"""C3 core debug and timing run: one fold per task, every code path, plus the spec-generation
equalities (Indiana against round3_d4_sets.a4b_specs; lung against the task definition's
expansion.a4b_k10 and a4b_specs). Prints only; writes nothing."""
import resource
import sys
import time

import numpy as np

import round4_conf_c3 as C
import round4_conf_io as IO

enc = sys.argv[1]
keys = sys.argv[2].split(",")
for key in keys:
    t0 = time.time()
    T = C.load_task(key, enc)
    print(f"[{key}] load {time.time()-t0:.0f}s, rss {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1e6:.2f} GB", flush=True)
    folds = T.fold_names()
    print(f"[{key}] {len(folds)} folds, first {folds[:3]}, n_match {T.n_match}", flush=True)
    if key in ("INDIANA_KIDNEY", "LUNG_XENIUM"):
        D4 = T.D4
        ref = D4.a4b_specs(T.td, T.samp, T.meta, D4.HArgs())
        mine = T.specs(10, 3)
        same = (len(ref) == len(mine) and all((a["C"] == b["C"]).all() and (a["T"] == b["T"]).all() and a["fold"] == b["fold"] and a["cal_draw"] == b["cal_draw"] for a, b in zip(ref, mine)))
        print(f"[{key}] specs(10) equal to D4.a4b_specs: {same} ({len(mine)} specs)", flush=True)
        if key == "LUNG_XENIUM":
            ex = T.td["expansion"]["a4b_k10"]["folds"]
            okx = all(sorted(set(T.samp[m["C"]])) == sorted(e["calibration_samples"]) for m, e in zip(mine, ex))
            print(f"[{key}] calibration samples equal to expansion.a4b_k10: {okx} ({len(ex)})", flush=True)
            Yr = T.Y
            print(f"[{key}] Y genes {Yr.shape[1]}, max {Yr.max():.3f}, min {Yr.min():.3f}; dropped {T.drop_rec.get('NCBI865')}", flush=True)
    for K in (10, 6):
        sp = T.specs(K, 1, folds=folds[:1])
        if not sp:
            print(f"[{key}] K={K}: no spec"); continue
        t1 = time.time()
        fit = T.fit(sp[0])
        tf = time.time() - t1
        t1 = time.time(); r0 = C.o0_rows(fit, dwr_reps=20); t0r = time.time() - t1
        t1 = time.time(); r1 = C.o_rows(fit, label_draws=range(2)); t1r = time.time() - t1
        print(f"[{key}] K={K} fold {fit.fold}: n_T_donors {fit.n_T_donors} nT {fit.n_T_matched}/{fit.n_T_natural} n_C {fit.n_C} ({fit.n_C_donors} donors) n_E {fit.n_E} G {len(fit.genes)} fit {tf:.1f}s o0(20 dwr) {t0r:.1f}s o(2 draws,6 o) {t1r:.1f}s skipped_o {fit.skipped_o} rss {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1e6:.2f} GB", flush=True)
        if K == 10:
            for r in C.selftest(fit):
                print("   selftest", r, flush=True)
    del T
