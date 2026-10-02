#!/usr/bin/env python
"""Round 4, conformal track, stage C2: merge the candidate fragments and apply the fixed criterion.

docs/round4_conf_plan.md section 6 (C2, "The criterion, fixed here") with the conventions of
section 7 item 5 and addendum 1 (section 10). At alpha = 0.1, for each candidate variant and each o
at which it is defined, over every C1 cell:

  (a) the cell's mean coverage over replicates is at least 0.89 in every cell;
  (b) price <= 1 + (pi_ref - 1)/2 in at least two thirds of the cells, pi_ref the reference
      method's price in the same cell, HCP at o = 0 and GHCP (primary, method 'ghcp') at o > 0.
      Where pi_ref is infinite the bound is infinite. Primary reading: such a cell meets (b) when
      the candidate is finite in it (frac_infinite = 0) and not otherwise. Secondary reading: such
      cells are left out of the two-thirds count. The verdict uses the primary reading;
  (c) a stated guarantee, finite-sample under hierarchical exchangeability or model-based with the
      model named. (c) is not computed; it is the assessment recorded in each candidate's
      definition, entered in GUARANTEE below with its source.

Verdict: 'goes forward' if (a), (b) and (c); 'heuristic' if (a) and (b) without (c); otherwise
'does not go forward'. A candidate price that is infinite against a finite bound fails (b) in that
cell.

Inputs: --c1 (results/round4/conformal/C1_testbed/c1_grid.csv) and --c2-root (the C2_candidates
directory, holding frag_<K>/c2_grid__<K>.csv). Outputs in --c2-root: c2_grid.csv (candidate rows
plus the reference rows at alpha = 0.1), c2_criterion.csv, c2_report_numbers.csv.
"""
import argparse
import glob
import math
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import round4_conf_io as IO  # noqa: E402

ALPHA = 0.1
GUARANTEE = {
    "k1_smoothed": ("met", "finite-sample under hierarchical exchangeability: HCP at a randomised "
                    "level, coverage >= 1 - alpha over data, test spot and U "
                    "(candidate_definition_K1.md)"),
    "k4_a050": ("met (model-based)", "model named: q_k normal and exchangeable across donors "
                "(candidate_definition_K4.md); the semireal normality check does not support it"),
    "k4_a025": ("met (model-based)", "as k4_a050"),
    "k4_a010": ("met (model-based)", "as k4_a050"),
    "k5_hcp": ("met", "the host's, HCP, unchanged (candidate_definition_K5.md)"),
    "k5_ghcp": ("met", "the host's, GHCP Theorem 2.1, with the scale built by one rule in every "
                "group from its own block (appendix B.1) (candidate_definition_K5.md)"),
    "k6_switch": ("unmet", "no finite-sample guarantee and no named model; the repaired rule of "
                  "docs/round4_conf_lower_bound.md section 8.3 is a proposal and was not run"),
}
KEYS = ["cell_id", "o"]


def load(c1, c2_root):
    C1 = pd.read_csv(c1)
    C1 = C1[np.isclose(C1.alpha, ALPHA)]
    files = sorted(glob.glob(os.path.join(c2_root, "frag_K?", "c2_grid__K?.csv")))
    C2 = pd.concat([pd.read_csv(f).assign(source=os.path.relpath(f, c2_root)) for f in files],
                   ignore_index=True)
    C2 = C2[np.isclose(C2.alpha, ALPHA)]
    dup = int(C2.duplicated(KEYS + ["method"]).sum())
    return C1, C2, files, dup


def ref_price(C1):
    h = C1[(C1.method == "hcp") & (C1.o == 0)][["cell_id", "price", "frac_infinite", "coverage",
                                                "halfwidth_mean"]]
    g = C1[(C1.method == "ghcp") & (C1.o > 0)][["cell_id", "o", "price", "frac_infinite",
                                                "coverage", "halfwidth_mean"]]
    return h, g


def criterion(C1, C2):
    h, g = ref_price(C1)
    rows, per_cell = [], []
    for (m, o), d in C2.groupby(["method", "o"]):
        if o == 0:
            r = d.merge(h, on="cell_id", suffixes=("", "_ref"))
            ref = "hcp"
        else:
            r = d.merge(g, on=["cell_id", "o"], suffixes=("", "_ref"))
            ref = "ghcp"
        n = len(r)
        cov_ok = r.coverage >= 0.89
        ref_inf = ~np.isfinite(r.price_ref) | (r.frac_infinite_ref > 0)
        cand_inf = ~np.isfinite(r.price) | (r.frac_infinite > 0)
        bound = 1 + 0.5 * (r.price_ref - 1)
        meets = np.where(ref_inf, ~cand_inf, (~cand_inf) & (r.price <= bound + 1e-12))
        prim = float(meets.mean()) if n else float("nan")
        fin = ~ref_inf
        sec = float(meets[fin].mean()) if fin.any() else float("nan")
        a = bool(cov_ok.all())
        b = bool(prim >= 2 / 3)
        b_sec = bool(sec >= 2 / 3) if not math.isnan(sec) else False
        cst, csrc = GUARANTEE.get(m, ("not stated", ""))
        c = cst.startswith("met")
        verdict = ("goes forward" if (a and b and c) else "heuristic" if (a and b) else
                   "does not go forward")
        rows.append(dict(method=m, o=int(o), reference=ref, n_cells=n,
                         a_min_coverage=float(r.coverage.min()), a_cells_below_0p89=int((~cov_ok).sum()),
                         a=a, b_share_primary=prim, b_primary=b, b_cells_ref_infinite=int(ref_inf.sum()),
                         b_share_secondary=sec, b_secondary=b_sec, c=cst, c_source=csrc,
                         verdict=verdict))
        r = r.assign(meets_b=meets, ref_infinite=ref_inf, bound=bound)
        per_cell.append(r[["cell_id", "gen", "K", "N", "share", "tau", "method", "o", "coverage",
                           "price", "frac_infinite", "price_ref", "frac_infinite_ref", "bound",
                           "meets_b", "ref_infinite"]])
    return pd.DataFrame(rows), pd.concat(per_cell, ignore_index=True)


def report_numbers(C1, C2, PC):
    """Numbers the C2 report cites, one row each (prediction, quantity, scope, value)."""
    R = []

    def add(pred, qty, scope, val):
        if isinstance(val, str) and " / " in val:
            names = qty.split(" / ") if " / " in qty else None
            for i, v in enumerate(val.split(" / ")):
                q = qty + (" (first)" if i == 0 else " (second)")
                R.append(dict(prediction=pred, quantity=q, scope=scope, value=float(v)))
            return
        R.append(dict(prediction=pred, quantity=qty, scope=scope, value=val))

    h, g = ref_price(C1)
    pooled = C1[(C1.method == "pooled") & (C1.o == 0)][["cell_id", "halfwidth_mean"]]
    # C2.1: K1 share of the HCP-to-pooled gap recovered at K = 10, finite cells
    k1 = C2[C2.method == "k1_smoothed"].merge(h, on="cell_id", suffixes=("", "_hcp")).merge(
        pooled, on="cell_id", suffixes=("", "_pool"))
    k1 = k1[(k1.K == 10) & (k1.frac_infinite == 0) & (k1.frac_infinite_hcp == 0)]
    gap = k1.halfwidth_mean_hcp - k1.halfwidth_mean_pool
    rec = (k1.halfwidth_mean_hcp - k1.halfwidth_mean) / gap.where(gap > 0)
    add("C2.1", "share of HCP-pooled half-width gap recovered by K1, median over cells", "K=10",
        float(rec.median()))
    add("C2.1", "same, maximum over cells", "K=10", float(rec.max()))
    add("C2.1", "cells", "K=10", int(rec.notna().sum()))
    # C2.2: K4 coverage and price by variant, tail, share
    for m in ["k4_a050", "k4_a025", "k4_a010"]:
        d = C2[C2.method == m]
        for gen in ["normal", "t3", "semireal"]:
            e = d[d.gen == gen]
            add("C2.2", f"{m} coverage min / max", gen, f"{e.coverage.min():.4f} / {e.coverage.max():.4f}")
            fin = e[e.frac_infinite == 0]
            add("C2.2", f"{m} price min / max (finite cells)", gen,
                f"{fin.price.min():.4f} / {fin.price.max():.4f}")
        e = d[(d.gen == "t3") & np.isclose(d.share, 0.5)]
        add("C2.2", f"{m} coverage mean, t3 share 0.5", "all K, N, tau", float(e.coverage.mean()))
    # C2.3: K5 inside GHCP, tau = 0.3, width ratio and coverage difference against ghcp
    k5 = C2[C2.method == "k5_ghcp"].merge(g, on=["cell_id", "o"], suffixes=("", "_g"))
    for tau in [0.0, 0.3]:
        e = k5[np.isclose(k5.tau, tau) & (k5.frac_infinite == 0) & (k5.frac_infinite_g == 0)]
        ratio = e.halfwidth_mean / e.halfwidth_mean_g
        add("C2.3", "k5_ghcp / ghcp mean half-width, median over cells", f"tau={tau}", float(ratio.median()))
        add("C2.3", "same, 10th and 90th percentile", f"tau={tau}",
            f"{ratio.quantile(0.1):.4f} / {ratio.quantile(0.9):.4f}")
        add("C2.3", "k5_ghcp minus ghcp coverage, min / max", f"tau={tau}",
            f"{(e.coverage - e.coverage_g).min():.4f} / {(e.coverage - e.coverage_g).max():.4f}")
        add("C2.3", "cells", f"tau={tau}", int(len(e)))
    e = k5[np.isclose(k5.tau, 0.3) & (k5.frac_infinite == 0) & (k5.frac_infinite_g == 0)]
    for o, f in e.groupby("o"):
        add("C2.3", "k5_ghcp / ghcp mean half-width, median over cells", f"tau=0.3, o={o}",
            float((f.halfwidth_mean / f.halfwidth_mean_g).median()))
    k1w = C2[C2.method == "k1_smoothed"].merge(h, on="cell_id", suffixes=("", "_hcp"))
    k1w = k1w[(k1w.frac_infinite == 0) & (k1w.frac_infinite_hcp == 0)]
    add("C2.1", "k1 / hcp mean half-width, median over finite cells", "all K",
        float((k1w.halfwidth_mean / k1w.halfwidth_mean_hcp).median()))
    add("C2.1", "k1 minus hcp coverage, min / max", "all K",
        f"{(k1w.coverage - k1w.coverage_hcp).min():.4f} / {(k1w.coverage - k1w.coverage_hcp).max():.4f}")
    # C2.6: K6 meets (b) by share; price equal to HCP's at shares 0.3, 0.5
    k6 = PC[PC.method == "k6_switch"]
    for s in sorted(k6.share.dropna().unique()):
        e = k6[np.isclose(k6.share, s) & (k6.gen != "semireal")]
        add("C2.6", "k6 share of cells meeting (b), primary", f"share={s}, normal and t3",
            float(e.meets_b.mean()))
    e = k6[k6.gen == "semireal"]
    add("C2.6", "k6 share of cells meeting (b), primary", "semireal", float(e.meets_b.mean()))
    k6h = C2[C2.method == "k6_switch"].merge(h, on="cell_id", suffixes=("", "_hcp"))
    for s in [0.3, 0.5]:
        e = k6h[np.isclose(k6h.share, s) & (k6h.frac_infinite == 0) & (k6h.frac_infinite_hcp == 0)]
        add("C2.6", "k6 price minus HCP price, max |.|", f"share={s}",
            float((e.price - e.price_hcp).abs().max()))
        add("C2.6", "k6 coverage min", f"share={s}", float(e.coverage.min()))
    add("C2.6", "k6 coverage min, all cells", "all", float(C2[C2.method == "k6_switch"].coverage.min()))
    return pd.DataFrame(R)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--c1", required=True)
    p.add_argument("--c2-root", required=True)
    a = p.parse_args(argv)
    C1, C2, files, dup = load(a.c1, a.c2_root)
    assert dup == 0, f"{dup} duplicated candidate keys"
    refs = C1[((C1.method == "hcp") & (C1.o == 0)) | ((C1.method == "ghcp") & (C1.o > 0)) |
              ((C1.method == "pooled") & (C1.o == 0))].assign(source="C1_testbed/c1_grid.csv")
    pd.concat([C2, refs], ignore_index=True).drop(columns=["source"]).to_csv(
        f"{a.c2_root}/c2_grid.csv", index=False)
    crit, pc = criterion(C1, C2)
    crit.to_csv(f"{a.c2_root}/c2_criterion.csv", index=False)
    pc.to_csv(f"{a.c2_root}/c2_criterion_by_cell.csv", index=False)
    report_numbers(C1, C2, pc).to_csv(f"{a.c2_root}/c2_report_numbers.csv", index=False)
    print(len(files), len(C2), crit[["method", "o", "a", "b_share_primary", "b_share_secondary",
                                      "c", "verdict"]].to_string(index=False))
    IO.write_provenance(a.c2_root, "C2", __file__, dict(stage="C2 merge and criterion", c1=a.c1,
                                                        fragments=[os.path.relpath(f, a.c2_root) for f in files]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
