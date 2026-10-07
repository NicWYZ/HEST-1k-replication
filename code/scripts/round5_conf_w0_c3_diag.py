#!/usr/bin/env python
"""Round 5, prediction-set track, W0: breakdown of the c3 anchor's differences (diagnostic only).

The W0 c3 anchor (Slurm 4198244, Intel node) matched all 22,032 rows of CCRCC:24, uni_v2, K = 10,
o in {0, 25} against c3_o_sweep.csv.gz but exceeded the literal tolerances: coverage 1.1e-16
against 0.0, width_mean 1.9e-8 and width_median 1.3e-9 against 3e-10. Nicolas approved this
diagnostic in chat on 7 October 2026. It computes nothing new. It reads the anchor's returned rows
and the reference rows, attaches to each fold the CPU vendor of the round-4 shard that produced its
reference rows (frag_CCRCC_o/shards/ccrcc24_uni_v2_*/run_info.json, which partition the 24 folds),
and tabulates the differences by reference vendor, o and method.

Prediction written before it ran (docs/round5_conf_plan.md, W0 escalation). If the excess is
cross-vendor floating-point drift, the 6 folds whose reference ran on Intel agree within 3e-10
with coverage difference exactly 0, and every difference above tolerance is in the 18 folds
whose reference ran on AMD.
"""
import glob
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import round5_conf_io as IO5  # noqa: E402

R4 = os.path.join(IO5.CLONE, "results", "round4", "conformal", "C3_real")
KEY = ["task", "label_set", "encoder", "method", "score", "alpha", "o", "K", "fold", "draw"]


def main(rows_path, out, run_infos):
    os.makedirs(out, exist_ok=True)
    IO5.stamp(out, track="conformal-W0", note="W0 c3 anchor difference breakdown")
    vend = {}
    # The shard run_info.json files are gitignored in the clone and absent from the project tree;
    # they are passed in as staged copies from the local working copy, md5 recorded in PROVENANCE.
    for p in sorted(run_infos):
        d = json.load(open(p))
        for f in d["folds"]:
            assert f not in vend, f"fold {f} in two shards"
            vend[f] = (d["cpu"]["vendor"], d["tag"])
    new = pd.read_csv(rows_path, dtype={"fold": str})
    ref = pd.read_csv(os.path.join(R4, "c3_o_sweep.csv.gz"), dtype={"fold": str})
    ref = ref[(ref.task == "CCRCC") & (ref.encoder == "uni_v2") & (ref.K == 10) & ref.o.isin([0, 25])]
    m = ref.merge(new, on=KEY, suffixes=("_r4", "_r5"))
    assert len(m) == len(new) == len(ref), (len(m), len(new), len(ref))
    assert set(m.fold) <= set(vend), set(m.fold) - set(vend)
    m["ref_vendor"] = m.fold.map(lambda f: vend[f][0])
    m["ref_shard"] = m.fold.map(lambda f: vend[f][1])
    for c in ("coverage", "width_mean", "width_median"):
        a, b = m[f"{c}_r5"].astype(float), m[f"{c}_r4"].astype(float)
        d = (a - b).abs()
        d[a.isna() & b.isna()] = 0.0
        d[np.isinf(a) & np.isinf(b)] = 0.0
        m[f"d_{c}"] = d
    m["rel_width_mean"] = m.d_width_mean / m.width_mean_r4.abs().replace(0, np.nan)
    g = m.groupby(["ref_vendor", "o", "method"]).agg(
        n=("d_width_mean", "size"),
        max_d_coverage=("d_coverage", "max"), n_coverage_nonzero=("d_coverage", lambda x: int((x > 0).sum())),
        max_d_width_mean=("d_width_mean", "max"),
        n_width_mean_over_3e10=("d_width_mean", lambda x: int((x > 3e-10).sum())),
        max_d_width_median=("d_width_median", "max"),
        n_width_median_over_3e10=("d_width_median", lambda x: int((x > 3e-10).sum())),
        max_rel_width_mean=("rel_width_mean", "max")).reset_index()
    v = m.groupby("ref_vendor").agg(
        n=("d_width_mean", "size"), folds=("fold", "nunique"),
        max_d_coverage=("d_coverage", "max"), n_coverage_nonzero=("d_coverage", lambda x: int((x > 0).sum())),
        max_d_width_mean=("d_width_mean", "max"),
        n_width_mean_over_3e10=("d_width_mean", lambda x: int((x > 3e-10).sum())),
        max_d_width_median=("d_width_median", "max"),
        n_width_median_over_3e10=("d_width_median", lambda x: int((x > 3e-10).sum())),
        max_rel_width_mean=("rel_width_mean", "max")).reset_index()
    v.to_csv(os.path.join(out, "w0_c3_diag_by_vendor.csv"), index=False)
    g.to_csv(os.path.join(out, "w0_c3_diag_by_vendor_o_method.csv"), index=False)
    cols = KEY + ["ref_vendor", "ref_shard", "coverage_r4", "coverage_r5", "d_coverage", "width_mean_r4",
                  "width_mean_r5", "d_width_mean", "rel_width_mean", "d_width_median"]
    m.sort_values("d_width_mean", ascending=False)[cols].head(40).to_csv(
        os.path.join(out, "w0_c3_diag_worst_width.csv"), index=False)
    m[m.d_coverage > 0][cols].to_csv(os.path.join(out, "w0_c3_diag_coverage_nonzero.csv"), index=False)
    IO5.write_provenance(out, "W0_c3diag", __file__, dict(stage="W0 c3 diagnostic", rows=rows_path,
                         shards=sorted({s for _, s in vend.values()})),
                         extra=dict(rows=len(m), run_info_md5=";".join(f"{os.path.basename(p)}={IO5.md5(p)}" for p in sorted(run_infos))))
    print(v.to_string(), flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3:])
