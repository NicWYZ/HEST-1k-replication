"""Round 10, track final-runs, F3.3 (iv) anchors: compare reruns of round 5's E4b and round 7's S4b with their files.

usage:
  round10_final_runs_f3_balance_anchor.py e4b <rerun_dir> <tag> <ref_ratios_csv> <ref_genes_csv_gz> <out_json>
      Recomputes round 5's width ratios (round5_ppi_e4b_merge.py, the block that writes e4b_rej_width_ratios.csv:
      gene rows with n_sub > 200, rej_t under D2 over D0's classical 'textbook_t|fpc|lin' and D0's tuned
      'textbook_t|fpc|lin|xf' widths, medians over genes per balance and p_a) from the rerun's gene file, compares them
      with the committed rows of the same task, arm, estimand and n_L, and compares every gene row of the rerun with
      round 5's own gene file.
  round10_final_runs_f3_balance_anchor.py s4b <rerun_genes_csv_gz> <ref_genes_csv_gz> <out_json>
      Compares every gene row of a rerun of round7_ppi_s4b_cube3.py masking with round 7's gene file.
"""
import json, sys
import numpy as np, pandas as pd

LIN, XF = "textbook_t|fpc|lin", "textbook_t|fpc|lin|xf"


def compare(a, b, keys):
    m = a.merge(b, on=keys, how="outer", suffixes=("", "_ref"), indicator=True)
    num = [c for c in b.columns if c not in keys and pd.api.types.is_numeric_dtype(b[c]) and c in a.columns]
    out = dict(rows_new=len(a), rows_ref=len(b), rows_both=int((m["_merge"] == "both").sum()), columns={})
    for c in num:
        x, y = m[c].to_numpy(float), m[c + "_ref"].to_numpy(float)
        both = np.isfinite(x) & np.isfinite(y)
        rel = np.abs(x - y)[both] / np.maximum(np.abs(y[both]), 1e-300)
        out["columns"][c] = dict(max_abs=float(np.abs(x - y)[both].max()) if both.any() else 0.0,
                                 max_rel=float(rel.max()) if both.any() else 0.0,
                                 nan_mismatch=int((np.isfinite(x) != np.isfinite(y)).sum()))
    out["exact"] = bool(out["rows_both"] == len(a) == len(b) and
                        all(v["max_abs"] == 0 and v["nan_mismatch"] == 0 for v in out["columns"].values()))
    return out, m


def ratios(genes):
    g = genes[genes["n_sub"] > 200]
    gk = ["vtag", "arm", "estimand", "n_L", "gene"]
    d0c = g[(g["design"] == "D0") & (g["rule"] == "none") & (g["interval"] == LIN)][gk + ["width", "emp_var", "coverage"]]
    d0t = g[(g["design"] == "D0") & (g["rule"] == "c_crossfit_design") & (g["interval"] == XF)][gk + ["width"]]
    rj = g[(g["design"] == "D2") & (g["interval"] == "rej_t")][gk + ["balance", "p_a", "width", "coverage", "emp_var"]]
    w = rj.merge(d0c, on=gk, suffixes=("", "_D0cl")).merge(d0t.rename(columns={"width": "width_D0tuned"}), on=gk)
    w["wr_D0cl"] = w["width"] / w["width_D0cl"]
    w["wr_D0tuned"] = w["width"] / w["width_D0tuned"]
    w["var_ratio"] = w["emp_var"] / w["emp_var_D0cl"]
    return (w.groupby(["vtag", "arm", "estimand", "n_L", "balance", "p_a"])
            .agg(wr_D0cl=("wr_D0cl", "median"), wr_D0tuned=("wr_D0tuned", "median"), var_ratio=("var_ratio", "median"),
                 coverage=("coverage", "median"), coverage_D0cl=("coverage_D0cl", "median"), n_genes=("gene", "nunique"))
            .reset_index())


def e4b(rerun_dir, tag, ref_ratios, ref_genes, out_json):
    new = pd.read_csv(f"{rerun_dir}/e4b_rejective_genes__{tag}.csv.gz")
    r = ratios(new)
    ref = pd.read_csv(ref_ratios)
    cell = r[["vtag", "arm", "estimand", "n_L"]].drop_duplicates()
    ref = ref.merge(cell, on=["vtag", "arm", "estimand", "n_L"])[r.columns]
    k = ["vtag", "arm", "estimand", "n_L", "balance", "p_a"]
    out = dict(ratios=compare(r, ref, k)[0])
    nm = r[(r.balance == "own") & np.isclose(r.p_a, 0.01)].iloc[0]
    rf = ref[(ref.balance == "own") & np.isclose(ref.p_a, 0.01)].iloc[0]
    out["named"] = dict(vtag=nm.vtag, arm=nm.arm, estimand=nm.estimand, n_L=int(nm.n_L), balance="own", p_a=0.01,
                        wr_D0cl=float(nm.wr_D0cl), wr_D0cl_ref=float(rf.wr_D0cl), coverage=float(nm.coverage),
                        coverage_ref=float(rf.coverage))
    old = pd.read_csv(ref_genes)
    gk = ["vtag", "arm", "estimand", "G", "n_L", "design", "balance", "p_a", "n_draws", "rule", "interval", "n_sub", "gene"]
    for d in (new, old):
        d["p_a"] = d["p_a"].round(6); d["balance"] = d["balance"].fillna("none")
    out["genes"] = compare(new, old, [c for c in gk if c in new.columns and c in old.columns])[0]
    out["pass"] = bool(out["named"]["wr_D0cl"] == out["named"]["wr_D0cl_ref"] and out["named"]["coverage"] == out["named"]["coverage_ref"])
    json.dump(out, open(out_json, "w"), indent=1, default=str)
    r.to_csv(out_json.replace(".json", "_ratios.csv"), index=False)
    print(json.dumps(out, indent=1, default=str))
    return 0 if out["pass"] else 1


def s4b(new_p, ref_p, out_json):
    a, b = pd.read_csv(new_p, low_memory=False), pd.read_csv(ref_p, low_memory=False)
    keys = ["vtag", "arm", "estimand", "G", "Gall", "n_L", "design", "balance", "estimator", "variance", "ref", "gene"]
    out, m = compare(a, b, keys)
    cells = a.groupby(["estimand", "n_L", "estimator", "variance", "ref"]).size().reset_index().shape[0]
    out["cells_estimator_variance"] = cells
    h = m[(m.estimator == "H") & (m.variance == "sim") & (m.ref == "res")]
    out["named_H_sim_res"] = {e: dict(coverage_median=float(x.coverage.median()), coverage_median_ref=float(x.coverage_ref.median()),
                                      width_median=float(x.width.median()), width_median_ref=float(x.width_ref.median()))
                              for e, x in h.groupby("estimand")}
    out["pass"] = out["exact"]
    json.dump(out, open(out_json, "w"), indent=1, default=str)
    print(json.dumps(out, indent=1, default=str))
    return 0 if out["pass"] else 1


if __name__ == "__main__":
    if sys.argv[1] == "e4b":
        raise SystemExit(e4b(*sys.argv[2:7]))
    raise SystemExit(s4b(*sys.argv[2:5]))
