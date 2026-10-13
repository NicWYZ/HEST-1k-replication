"""Round 6 extension, cheatsheet track, C4.5: tests of the scorer.

  1. true values score exactly 1 on every slide and pooled
  2. values permuted across spots within each slide score near 0, within
     0.05 in absolute value on average over 20 permutations
  3. a file with one constant gene on one slide scores that gene 0 there
     and flags it
  4. a file missing a spot fails validation
  5. a gene whose measured values are constant on one slide is left out of
     that slide's mean and flagged

    python round6_cheatsheet_ext_score_test.py [TRUTH.parquet]

Without an argument it uses synthetic truth, 3 slides of 500 spots and 50
genes. With the package's test truth (columns spot, slide and the genes) it
runs the same tests on the real values. Prints one JSON object.
"""
import json
import os
import sys
import zlib

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import round6_cheatsheet_ext_score as S  # noqa: E402


def synthetic():
    rng = np.random.default_rng(zlib.crc32(b"round6ext-scoretest-truth"))
    genes = [f"G{i:02d}" for i in range(50)]
    y = np.log1p(rng.poisson(rng.gamma(2.0, 1.0, (1500, 1)) * rng.gamma(2.0, 1.0, (1, 50))))
    truth = pd.DataFrame(y.astype(float), columns=genes, index=[f"p{i:04d}" for i in range(1, 1501)])
    return truth, np.repeat(["a", "b", "c"], 500), genes


def main():
    if len(sys.argv) > 1:
        t = pd.read_parquet(sys.argv[1])
        slide = t["slide"].to_numpy()
        truth = t.drop(columns=["slide"]).set_index("spot")
        genes = list(truth.columns)
        source = sys.argv[1]
    else:
        truth, slide, genes = synthetic()
        source = "synthetic"
    out = {"truth": source, "n_spots": len(truth), "n_genes": len(genes)}

    r = S.score(truth.copy(), truth, slide)
    defined = r["cells"]["r"].dropna()
    out["t1_true_values"] = {"rbar": r["rbar"], "pooled": r["pooled"], "min_cell": float(defined.min()),
                             "pass": bool(abs(r["rbar"] - 1) < 1e-12 and abs(r["pooled"] - 1) < 1e-12
                                          and (defined > 1 - 1e-12).all())}

    rng = np.random.default_rng(zlib.crc32(b"round6ext-scoretest-permute"))
    vals = []
    for _ in range(20):
        idx = np.arange(len(truth))
        for s in sorted(set(slide.tolist())):
            m = np.flatnonzero(slide == s)
            idx[m] = rng.permutation(m)
        p = pd.DataFrame(truth.to_numpy()[idx], index=truth.index, columns=genes)
        vals.append(S.score(p, truth, slide)["rbar"])
    out["t2_permuted"] = {"mean_rbar": float(np.mean(vals)), "min": float(np.min(vals)), "max": float(np.max(vals)),
                          "pass": bool(abs(np.mean(vals)) <= 0.05)}

    p = truth.copy()
    s0 = sorted(set(slide.tolist()))[0]
    g0 = next(g for g in genes if np.ptp(truth[g].to_numpy()[slide == s0]) > 0)
    p.loc[slide == s0, g0] = 1.0
    r = S.score(p, truth, slide)
    c = r["cells"]
    cell = c[(c["slide"] == s0) & (c["gene"] == g0)].iloc[0]
    out["t3_constant_gene"] = {"slide": s0, "gene": g0, "r": float(cell["r"]), "flag": bool(cell["constant_pred"]),
                               "n_flagged": r["n_constant_pred_cells"],
                               "pass": bool(cell["r"] == 0.0 and cell["constant_pred"] and r["n_constant_pred_cells"] == 1)}

    df = truth.reset_index().rename(columns={truth.index.name or "index": "spot_id"})
    try:
        S.validate(df.iloc[1:], list(truth.index), genes)
        out["t4_missing_spot"] = {"pass": False, "reason": "validated"}
    except S.InvalidPredictions as e:
        out["t4_missing_spot"] = {"pass": True, "reason": str(e)}
    ok = S.validate(df, list(truth.index), genes)
    out["t4_full_file_validates"] = bool(ok.shape == truth.shape)

    t2 = truth.copy()
    t2.loc[slide == s0, g0] = 0.0
    r = S.score(truth.copy(), t2, slide)
    c = r["cells"]
    cell = c[(c["slide"] == s0) & (c["gene"] == g0)].iloc[0]
    n_def = int(c[(c["slide"] == s0)]["r"].notna().sum())
    out["t5_constant_truth"] = {"r_is_nan": bool(np.isnan(cell["r"])), "flag": bool(cell["constant_truth"]),
                                "genes_in_that_slides_mean": n_def,
                                "pass": bool(np.isnan(cell["r"]) and cell["constant_truth"]
                                             and n_def == int(c[c["slide"] == s0]["constant_truth"].eq(False).sum()))}
    out["all_pass"] = all(v["pass"] for k, v in out.items() if isinstance(v, dict))
    print(json.dumps(out, indent=1))
    sys.exit(0 if out["all_pass"] else 1)


if __name__ == "__main__":
    main()
