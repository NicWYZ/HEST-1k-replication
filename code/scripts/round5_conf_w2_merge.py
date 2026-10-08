#!/usr/bin/env python
"""Round 5, prediction-set track, W2 merge (docs/round5_conf_plan.md section 2, W2).

Reads the per-replicate rows of the sim-design sweep (round5_conf_w2_wrapper.py, one directory per
unit under SIM_ROOT, rerun directories job*b only) and of the census PUMA sweep
(round5_conf_w2_census.py, one directory per PUMA count under CEN_ROOT), and writes into OUT.
Directories superseded by a node-class rerun are passed with --exclude; the node of every row file
read is recorded in w2_merge_inputs.json. Outputs:

  w2_sim_designs.csv       one row per (design, K, alpha, o, method): n_rep, coverage, coverage_mcse,
                           finite_frac, width_mean_finite, width_median_finite, expected_cov,
                           interval_share
  w2_census.csv            the same per (n_puma, alpha, o, method)
  w2_narrowest_valid.csv   one row per (setting, alpha, o): the narrowest valid method, runner-up,
                           paired margin and its Monte Carlo standard error
  w2_acceptance.csv        acceptance check 4 (W1 checks 2 to 4 for within_plain and within_full)
                           in these designs, and the merge's own completeness checks
  w2_coverage_z.csv        the z values behind check 4's coverage parts
  w2_report_numbers.csv    the numbers the W2 predictions are scored on

RULES, written before the merge was run on the production rows
  Coverage. For within_full the coverage is that of the exact full-conformal set (column exact_cov,
  per replicate 0/1); for every other method it is the interval indicator. A non-finite interval
  counts as covering.
  Narrowest valid method. Candidates are the valid methods: in the sim designs released_ghcp,
  released_stdcp, hcp, ghcp, within_plain, within_full; in the census GHCP, HCP, Std-CP,
  within_plain, within_full. A method is eligible at (setting, alpha, o) only if it is finite in
  every replicate there. The narrowest has the smallest mean width; the margin is the runner-up's
  mean width minus the narrowest's, with a paired Monte Carlo standard error (sd over replicates of
  the per-replicate difference over sqrt(n)). Ties within 1e-12 relative are listed. The width of
  within_full is the convex hull of its kept set, as in W1.
  Check 4. (2) within_plain finite in every replicate from o = 9 at alpha 0.1 and o = 4 at 0.2;
  (3) within_plain coverage within 3 MCSE of ceil((o+1)(1-alpha))/(o+1) where finite in every
  replicate; (4) within_full finite from o = 9 / o = 4 and its exact-set coverage within 3 MCSE of
  the same value, with the share of replicates whose set is not one interval reported. As in W1,
  a 3-MCSE check fails by chance in about 0.27% of cells, and the count expected by chance is
  reported beside the literal count. In the census the responses (incomes) can tie, which makes
  split and full conformal conservative; ties are counted and reported.
"""
import argparse
import glob
import json
import math
import os
import sys

import numpy as np
import pandas as pd

SIM_VALID = ("released_ghcp", "released_stdcp", "hcp", "ghcp", "within_plain", "within_full")
CEN_VALID = ("GHCP", "HCP", "Std-CP", "within_plain", "within_full")


def expected(o, a):
    return math.ceil((o + 1) * (1 - a) - 1e-9) / (o + 1)


def excluded(f, excl):
    return any(e and e in f for e in (excl or []))


def node_of(f):
    """Node line of the PROVENANCE.txt nearest to a row file (same directory, else parent)."""
    for d in (os.path.dirname(f), os.path.dirname(os.path.dirname(f))):
        p = os.path.join(d, "PROVENANCE.txt")
        if os.path.exists(p):
            for line in open(p):
                if line.strip().lower().startswith("node"):
                    return line.split(":", 1)[1].strip()
    return ""


def load_sim(root, excl=None):
    frames, files = [], []
    for unit in sorted(os.listdir(root)):
        if unit.startswith("regress") or not os.path.isdir(os.path.join(root, unit)):
            continue
        fs = sorted(glob.glob(os.path.join(root, unit, "job*[bc]", "**", "w2_wrapper_rows__*.csv"), recursive=True))
        for f in fs:
            if excluded(f, excl):
                continue
            d = pd.read_csv(f)
            d["unit"] = unit
            frames.append(d)
            files.append(f)
    if not frames:
        return None, files
    D = pd.concat(frames, ignore_index=True)
    D["rep"] = D.chunk.astype(str) + "_" + D.experiment.astype(str)
    D["cov"] = np.where((D.method == "within_full") & D.exact_cov.notna(), D.exact_cov, D.covered)
    D["finite"] = D.finite.astype(int)
    return D, files


def load_census(root, excl=None):
    frames, files = [], []
    for sub in sorted(glob.glob(os.path.join(root, "puma*"))):
        for f in sorted(glob.glob(os.path.join(sub, "**", "w2_census_detailed_*.csv"), recursive=True)):
            if excluded(f, excl):
                continue
            frames.append(pd.read_csv(f))
            files.append(f)
    if not frames:
        return None, files
    D = pd.concat(frames, ignore_index=True)
    D["rep"] = D.replicate.astype(str)
    D["finite"] = D.finite.astype(str).str.lower().isin(["true", "1", "1.0"]).astype(int)
    D["cov"] = np.where((D.method == "within_full") & D.exact_cov.notna(), D.exact_cov, D.coverage)
    D["covered"] = D.coverage
    return D, files


def summarise(D, keys):
    rows = []
    for k, g in D.groupby(keys + ["alpha", "o", "method"]):
        fin = g[g.finite == 1].width.astype(float)
        n = len(g)
        c = g["cov"].astype(float)
        r = dict(zip(keys + ["alpha", "o", "method"], k))
        r.update(n_rep=n, coverage=c.mean(), coverage_mcse=c.std(ddof=1) / math.sqrt(n) if n > 1 else np.nan,
                 hull_coverage=g.covered.astype(float).mean(), finite_frac=(g.finite == 1).mean(),
                 width_mean_finite=fin.mean() if len(fin) else np.nan,
                 width_median_finite=fin.median() if len(fin) else np.nan,
                 expected_cov=expected(int(r["o"]), float(r["alpha"])) if r["method"] in ("within_plain", "within_full") and r["o"] > 0 else np.nan,
                 interval_share=g.is_interval.astype(float).mean() if r["method"] == "within_full" else np.nan)
        rows.append(r)
    return pd.DataFrame(rows)


def narrowest(D, keys, valid, setting):
    out = []
    for k, g in D[D.method.isin(valid)].groupby(keys + ["alpha", "o"]):
        W = g.pivot_table(index="rep", columns="method", values="width", aggfunc="first")
        F = g.pivot_table(index="rep", columns="method", values="finite", aggfunc="first")
        elig = [m for m in valid if m in W.columns and F[m].notna().all() and (F[m] == 1).all()]
        r = dict(zip(keys + ["alpha", "o"], k), setting=setting, n_rep=len(W),
                 eligible=";".join(elig), n_eligible=len(elig))
        if not elig:
            out.append(dict(r, narrowest=None))
            continue
        means = W[elig].mean().sort_values()
        best = means.index[0]
        ties = [m for m in means.index[1:] if abs(means[m] - means[best]) <= 1e-12 * abs(means[best])]
        r.update(narrowest=best, narrowest_width=means[best], ties=";".join(ties))
        if len(means) > 1:
            ru = means.index[1]
            diff = (W[ru] - W[best]).astype(float)
            se = diff.std(ddof=1) / math.sqrt(len(diff))
            r.update(runner_up=ru, runner_up_width=means[ru], margin=diff.mean(), margin_mcse=se,
                     margin_gt_2se=bool(diff.mean() > 2 * se))
        out.append(r)
    return pd.DataFrame(out)


def check4(S, keys, label):
    acc, zrows = [], []
    for meth, thr in (("within_plain", {0.1: 9, 0.2: 4}), ("within_full", {0.1: 9, 0.2: 4})):
        for a, t in thr.items():
            d = S[(S.method == meth) & np.isclose(S.alpha, a) & (S.o >= t)]
            bad = d[d.finite_frac < 1.0]
            n_ck = "2" if meth == "within_plain" else "4"
            acc.append(dict(design=label, check=f"{n_ck}_{meth}_finite_from_o{t}_a{a}", value=len(bad), tol=0,
                            passed=len(bad) == 0, note=f"{len(d)} cells"))
        d = S[(S.method == meth) & (S.finite_frac == 1.0) & (S.o > 0)].copy()
        d = d[d.coverage_mcse > 0]
        d["z"] = (d.coverage - d.expected_cov) / d.coverage_mcse
        d["check"] = f"{'3' if meth == 'within_plain' else '4'}_{meth}_cov"
        zrows.append(d.assign(design=label))
        nf = int((d.z.abs() > 3).sum())
        acc.append(dict(design=label, check=f"{d.check.iloc[0] if len(d) else meth}_within_3se", value=nf, tol=0,
                        passed=nf == 0, note=f"{len(d)} cells; {0.0027 * len(d):.2f} expected by chance; "
                                             f"max |z| {d.z.abs().max() if len(d) else float('nan'):.2f}; "
                                             f"min z {d.z.min() if len(d) else float('nan'):.2f}"))
    wf = S[(S.method == "within_full") & (S.o > 0)]
    acc.append(dict(design=label, check="4_within_full_frac_not_interval_max",
                    value=float(1 - wf.interval_share.min()) if len(wf) else np.nan, tol=np.nan, passed=np.nan,
                    note="largest share of replicates in a cell whose kept set is not one interval"))
    return acc, zrows


def main(a):
    os.makedirs(a.out, exist_ok=True)
    acc, zrows, nv, numbers = [], [], [], []
    sim, sim_files = load_sim(a.sim_root, a.exclude) if a.sim_root else (None, [])
    cen, cen_files = load_census(a.cen_root, a.exclude) if a.cen_root else (None, [])
    if sim is not None:
        dup = int(sim.duplicated(["design", "K", "rep", "alpha", "o", "method"]).sum())
        acc.append(dict(design="sim", check="merge_duplicated_keys", value=dup, tol=0, passed=dup == 0))
        nrep = sim.groupby(["unit", "alpha"]).rep.nunique()
        acc.append(dict(design="sim", check="merge_replicates_per_unit_alpha", value=json.dumps({f"{u}|{al}": int(v) for (u, al), v in nrep.items()}),
                        tol=np.nan, passed=bool((nrep == 1000).all())))
        S = summarise(sim, ["design", "K"])
        S.to_csv(os.path.join(a.out, "w2_sim_designs.csv"), index=False)
        nv.append(narrowest(sim, ["design", "K"], SIM_VALID, "sim"))
        for (des, K), s in S.groupby(["design", "K"]):
            ac, zr = check4(s, ["design", "K"], f"{des}|K{K}")
            acc += ac
            zrows += zr
    if cen is not None:
        dup = int(cen.duplicated(["n_puma", "rep", "alpha", "o", "method"]).sum())
        acc.append(dict(design="census", check="merge_duplicated_keys", value=dup, tol=0, passed=dup == 0))
        nrep = cen.groupby(["n_puma", "alpha"]).rep.nunique()
        acc.append(dict(design="census", check="merge_replicates_per_puma_alpha", value=json.dumps({f"{p}|{al}": int(v) for (p, al), v in nrep.items()}),
                        tol=np.nan, passed=bool((nrep == 1000).all())))
        C = summarise(cen, ["n_puma"])
        C.to_csv(os.path.join(a.out, "w2_census.csv"), index=False)
        nv.append(narrowest(cen, ["n_puma"], CEN_VALID, "census"))
        for p, s in C.groupby("n_puma"):
            ac, zr = check4(s, ["n_puma"], f"census|puma{p}")
            acc += ac
            zrows += zr
    if nv:
        pd.concat(nv, ignore_index=True).to_csv(os.path.join(a.out, "w2_narrowest_valid.csv"), index=False)
    pd.DataFrame(acc).to_csv(os.path.join(a.out, "w2_acceptance.csv"), index=False)
    if zrows:
        pd.concat(zrows, ignore_index=True).to_csv(os.path.join(a.out, "w2_coverage_z.csv"), index=False)
    with open(os.path.join(a.out, "w2_merge_inputs.json"), "w") as fh:
        json.dump(dict(exclude=a.exclude or [],
                       sim_files={os.path.relpath(f, a.sim_root): node_of(f) for f in sim_files} if a.sim_root else {},
                       cen_files={os.path.relpath(f, a.cen_root): node_of(f) for f in cen_files} if a.cen_root else {}), fh, indent=1)
    print(pd.DataFrame(acc).to_string())


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--sim-root")
    p.add_argument("--cen-root")
    p.add_argument("--out", required=True)
    p.add_argument("--exclude", action="append", help="path substring of a superseded directory; repeatable")
    main(p.parse_args())
