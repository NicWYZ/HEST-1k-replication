#!/usr/bin/env python
"""Round 5, W2 part 1: acceptance 2 (wrapper against launcher) and acceptance 4 (within-group checks).

Inputs: the wrapper's row files (round5_conf_w2_wrapper.py) and the launcher's raw results, either the
merged file (--launcher-raw, the launcher's own *_multialpha_raw_results_complete.csv) or the chunk
pickles of a run (--launcher-pkl-dir, files e0_w<chunk>.pkl that round4_conf_c1_ghcp_repro.py stores).

w2_wrapper_check.csv: one row per (design, K, alpha, o, wrapper method, launcher columns). It holds the
number of replicates compared, the number whose coverage indicators differ, the number whose
finiteness differs, and the largest absolute difference of finite widths. Pass means zero of each and
a width difference of at most 1e-9. Rows for this track's `ghcp` are information only: its residual
form is not the released shrunken-prediction form (see the wrapper docstring), so it is expected to
differ and it is not part of the pass condition. The rows `hcp` (this track's hcp_q, standard tie convention) and `ghcp` are information only; the pass condition is the three released methods.

w2_within_check.csv: for within_plain and within_full, per (design, K, alpha, o), the finiteness
pattern against the one W1 acceptance check 2 and check 4 expect, and the coverage against
ceil((o+1)(1-alpha))/(o+1) in units of the Monte Carlo standard error sqrt(e(1-e)/n) of that expected
value e (W1 acceptance checks 3 and 4; limit 3). within_full's exact set and its hull are both reported.

w2_part1_summary.csv: per (design, K, alpha, o, method), the replicates, the number infinite, the
coverage with its standard error, and the mean and standard deviation of finite widths.
"""
import argparse
import glob
import math
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PAIRS = {
    "released_hcp": ("coverage_hcp", "width_hcp", True),
    "hcp": ("coverage_hcp", "width_hcp", False),
    "released_ghcp": ("coverage_donor_hcp_randomized", "width_donor_hcp_randomized", True),
    "released_stdcp": ("coverage_stdcp", "width_stdcp", True),
    "ghcp": ("coverage_donor_hcp_randomized", "width_donor_hcp_randomized", False),
}


def load_launcher(a):
    if a.launcher_raw:
        return pd.read_csv(a.launcher_raw)
    fs = sorted(glob.glob(os.path.join(a.launcher_pkl_dir, "e0_w*.pkl")))
    assert fs, f"no chunk pickles in {a.launcher_pkl_dir}"
    return pd.concat([pd.read_pickle(f) for f in fs], ignore_index=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--wrapper-dir", required=True)
    p.add_argument("--launcher-raw", default="")
    p.add_argument("--launcher-pkl-dir", default="")
    p.add_argument("--out", required=True)
    p.add_argument("--tag", default="")
    a = p.parse_args()
    os.makedirs(a.out, exist_ok=True)
    W = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(os.path.join(a.wrapper_dir, "**", "w2_wrapper_rows__*.csv"), recursive=True))],
                  ignore_index=True)
    W.to_csv(os.path.join(a.out, f"w2_wrapper_rows_all{a.tag}.csv.gz"), index=False)
    L = load_launcher(a)
    L = L.rename(columns={"o_observed": "o"})
    L["alpha"] = L["alpha"].astype(float)
    W["alpha"] = W["alpha"].astype(float)
    out = []
    for (design, K), Wd in W.groupby(["design", "K"]):
        for meth, (ccol, wcol, in_pass) in PAIRS.items():
            Wm = Wd[Wd.method == meth]
            if not len(Wm):
                continue
            keys = ["alpha", "experiment", "o"]
            if meth in ("released_hcp",):
                Wm = Wm.drop(columns="o")
                Lm = L[L.o == 0][["alpha", "experiment", ccol, wcol]]
                keys = ["alpha", "experiment"]
            else:
                Lm = L[["alpha", "experiment", "o", ccol, wcol]]
            M = Wm.merge(Lm, on=keys, how="left", indicator=True)
            for gk, g in M.groupby(["alpha", "o"] if "o" in M.columns else ["alpha"]):
                alpha = gk[0]
                o = gk[1] if len(gk) > 1 else "all"
                found = g[ccol].notna()
                gg = g[found]
                cov_l = (gg[ccol] > 0.5).astype(int)
                cov_mis = int((gg["covered"].astype(int) != cov_l).sum())
                wl, ww = gg[wcol].to_numpy(float), gg["width"].to_numpy(float)
                fin_l, fin_w = np.isfinite(wl), np.isfinite(ww)
                fin_mis = int((fin_l != fin_w).sum())
                both = fin_l & fin_w
                mx = float(np.max(np.abs(wl[both] - ww[both]))) if both.any() else 0.0
                ok = (cov_mis == 0 and fin_mis == 0 and mx <= 1e-9 and len(gg) == len(g))
                out.append(dict(design=design, K=K, alpha=alpha, o=o, wrapper_method=meth,
                                launcher_columns=f"{ccol}|{wcol}", n_wrapper_rows=len(g), n_compared=len(gg),
                                n_missing_in_launcher=int(len(g) - len(gg)), n_coverage_mismatch=cov_mis,
                                n_finiteness_mismatch=fin_mis, max_abs_width_diff=mx,
                                n_finite_wrapper=int(fin_w.sum()), n_finite_launcher=int(fin_l.sum()),
                                part_of_pass_condition=in_pass, passed=bool(ok) if in_pass else "information"))
    C = pd.DataFrame(out)
    C.to_csv(os.path.join(a.out, f"w2_wrapper_check{a.tag}.csv"), index=False)
    gate = C[C.part_of_pass_condition == True]  # noqa: E712
    print("wrapper check rows", len(C), "pass-condition rows", len(gate), "failed", int((~gate.passed.astype(bool)).sum()))

    # ---- within-group checks
    rows = []
    for (design, K, alpha, o), g in W[W.method.isin(["within_plain", "within_full"])].groupby(
            ["design", "K", "alpha", "o"]):
        for meth, gm in g.groupby("method"):
            n = len(gm)
            nfin = int(gm.finite.sum())
            need = 9 if abs(alpha - 0.1) < 1e-12 else 4 if abs(alpha - 0.2) < 1e-12 else math.ceil((1 - alpha) / alpha)
            exp_fin = o >= need
            pattern_ok = (nfin == n) if exp_fin else (nfin == 0)
            e = math.ceil((o + 1) * (1 - alpha) - 1e-9) / (o + 1)
            cov = float(gm.covered.mean())
            se = math.sqrt(e * (1 - e) / n)
            z = (cov - e) / se if se > 0 else float("nan")
            r = dict(design=design, K=K, alpha=alpha, o=o, method=meth, n=n, n_finite=nfin,
                     expected_finite_from_o=need, pattern_ok=pattern_ok, expected_cov=e, coverage=cov,
                     mc_se_at_expected=se, z=z, coverage_within_3se=(abs(z) <= 3) if exp_fin else "n/a (infinite)")
            if meth == "within_full":
                r["exact_set_coverage"] = float(gm.exact_cov.mean())
                r["exact_set_z"] = (r["exact_set_coverage"] - e) / se if se > 0 else float("nan")
                r["share_one_interval"] = float(gm.is_interval.mean())
            rows.append(r)
    Wc = pd.DataFrame(rows)
    Wc.to_csv(os.path.join(a.out, f"w2_within_check{a.tag}.csv"), index=False)

    # ---- summary
    rows = []
    for gk, g in W.groupby(["design", "K", "alpha", "o", "method"]):
        fw = g.width[np.isfinite(g.width)]
        cov = float(g.covered.mean())
        rows.append(dict(design=gk[0], K=gk[1], alpha=gk[2], o=gk[3], method=gk[4], n=len(g),
                         n_infinite=int((~np.isfinite(g.width)).sum()), coverage=cov,
                         coverage_se=math.sqrt(cov * (1 - cov) / len(g)),
                         width_mean_finite=float(fw.mean()) if len(fw) else float("nan"),
                         width_sd_finite=float(fw.std(ddof=1)) if len(fw) > 1 else float("nan")))
    pd.DataFrame(rows).to_csv(os.path.join(a.out, f"w2_part1_summary{a.tag}.csv"), index=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
