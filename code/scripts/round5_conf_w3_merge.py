#!/usr/bin/env python
"""Round 5, prediction-set track, W3 merge and acceptance (docs/round5_conf_plan.md section 2, W3,
and section 6.5).

Reads every w3_full__*.csv.gz under ROOT (the unit directories of results/round5/conformal/W3_real/,
skipping smoke/ and any --exclude substring), with the CPU model from the PROVENANCE.txt beside each
file, and the round-4 references under R4 (results/round4/conformal/C3_real/). Writes into OUT:

  w3_o_sweep.csv.gz      part 1 rows, the fifteen c3_o_sweep columns plus n_T_donors
  w3_K_sweep.csv.gz      part 2 rows, the same columns
  w3_fixed_head.csv.gz   part 3 rows, the same columns
  w3_by_fold.csv         mean over calibration and label draws per (part, task, encoder, method,
                         alpha, o, K, fold), round4_conf_c3.by_fold_table's definition plus part
  w3_map_by_task.csv     the fixed format the inference track reads: task, part, alpha, K,
                         n_T_donors, o, method, valid, coverage, coverage_sd_folds, width_mean,
                         finite, narrowest_valid
  w3_reproduction.csv    acceptance check 1, per reference table and column
  w3_repro_mismatch_rows.csv  every reproduced row whose coverage, n_test or finiteness differs,
                         or whose width differs by more than the tolerance, with the W3 CPU model
                         and source file. The round-4 CPU of a flagged row is read from that
                         fragment's node record by the lead and given in the report.
  w3_within_coverage.csv acceptance checks 2 and 3, per (task, part, K, alpha, o, method)
  w3_acceptance.csv      all checks in one table, with the merge's own completeness checks
  w3_merge_inputs.json   files read, their rows and CPU model

RULES, written before the merge runs on production rows
  Reproduction (check 1, memo section 4 of the W2 decisions as plan 6.5 item 1). A W3 row is matched
  to a round-4 row on (task, label_set, encoder, method, score, alpha, o, K, fold, draw). Sources:
  c3_o_sweep.csv.gz (K = 10, o in {0, 5, 10, 25, 50, 100}), c3_K_sweep.csv (o = 0, K from 10) and
  frag_CCRCC_K/ghcp_o25/c3_full_ghcp_o25__CCRCC.csv (o = 25, K from 10). Only round-4 rows whose
  method, o and K are in W3's grid for that part are expected. Coverage, n_test and finite must agree
  exactly. width_mean and width_median must agree within 1.91e-8 (relative to 1 where the width is
  below 1, absolute otherwise; both infinite counts as equal). Part 3 rows at K = 20 are part 2's
  K = 20 design and are also compared with part 2 (exactly the same computation).
  Within-donor coverage (checks 2 and 3). For each (task, part, K, alpha, o) the mean coverage of
  within_plain and within_full over encoders, folds, calibration draws and label draws, where the
  method is finite in every row, is within 0.005 of ceil((o + 1)(1 - alpha))/(o + 1); within uses
  n = o - floor(o/2) in place of o.
  Map. Coverage and width are means over encoders of the mean over folds of the per-fold mean over
  draws, as round 4. coverage_sd_folds is the sd over folds of the per-fold coverage, averaged over
  encoders. finite is the share of rows with a finite interval. valid is True for methods with a
  finite-sample guarantee under hierarchical exchangeability (hcp, one_per, ghcp, ghcp_noad, within,
  within_plain, within_full) and False for pooled and recentred. hcp and one_per do not use labelled
  spots; their o = 0 values are repeated at every o of the part so that they are on the map at each o.
  narrowest_valid marks, per (task, part, alpha, K, o), the valid method finite in every row with the
  smallest width_mean, excluding one_per, whose width is an average over 200 single-subsampling sets
  rather than the width of one set. n_T_donors is the median over folds (it is constant within a fold
  and is in w3_by_fold.csv per fold).
"""
import argparse
import glob
import json
import math
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import round4_conf_c3 as C  # noqa: E402

KEY = ["task", "label_set", "encoder", "method", "score", "alpha", "o", "K", "fold", "draw"]
WTOL = 1.91e-8
VALID = {"hcp", "one_per", "ghcp", "ghcp_noad", "within", "within_plain", "within_full"}
O_FREE = ("hcp", "one_per", "pooled")
GRID = {1: dict(K={10}, o={0, 3, 5, 9, 10, 12, 15, 17, 20, 25, 50, 100}),
        2: dict(K={10, 12, 14, 16, 18, 20}, o={0, 5, 10, 15, 17, 25, 50}),
        3: dict(K={10, 12, 14, 16, 18, 20}, o={0, 5, 10, 15, 17, 25, 50})}
METHODS = {"pooled", "hcp", "one_per", "ghcp", "ghcp_noad", "within", "within_plain", "within_full",
           "recentred"}


def prov_field(path, field):
    p = os.path.join(os.path.dirname(path), "PROVENANCE.txt")
    if not os.path.exists(p):
        return ""
    val = ""
    for line in open(p):
        if line.split(":", 1)[0].strip() == field:
            val = line.split(":", 1)[1].strip()
    return val


def expected(n, a):
    return math.ceil((n + 1) * (1 - a) - 1e-9) / (n + 1)


def load(root, excl):
    fs = [f for f in sorted(glob.glob(os.path.join(root, "**", "w3_full__*.csv.gz"), recursive=True))
          if "/smoke/" not in f and not any(e in f for e in excl)]
    parts, info = [], []
    for f in fs:
        d = pd.read_csv(f, dtype={"fold": str})
        d["cpu_model"] = prov_field(f, "cpu_model")
        d["snapshot_commit"] = prov_field(f, "snapshot_commit")
        d["src"] = os.path.relpath(f, root)
        parts.append(d)
        info.append(dict(file=os.path.relpath(f, root), rows=len(d), cpu_model=d.cpu_model.iloc[0],
                         snapshot_commit=d.snapshot_commit.iloc[0]))
    return pd.concat(parts, ignore_index=True), info


def r4_refs(r4):
    """Round-4 references. Accepts the repository layout (c3_o_sweep.csv.gz, one merged
    c3_full_ghcp_o25__CCRCC.csv) and the Longleaf results layout (c3_o_sweep.csv, and the
    o = 25 rows in the shard files frag_CCRCC_K/ghcp_o25/*/c3_full__*.csv)."""
    p = os.path.join(r4, "c3_o_sweep.csv.gz")
    o = pd.read_csv(p if os.path.exists(p) else os.path.join(r4, "c3_o_sweep.csv"), dtype={"fold": str})
    k = pd.read_csv(os.path.join(r4, "c3_K_sweep.csv"), dtype={"fold": str})
    g25 = os.path.join(r4, "frag_CCRCC_K", "ghcp_o25")
    p = os.path.join(g25, "c3_full_ghcp_o25__CCRCC.csv")
    fs = [p] if os.path.exists(p) else sorted(glob.glob(os.path.join(g25, "*", "c3_full__*.csv")))
    if not fs:
        raise FileNotFoundError(f"no round-4 o = 25 rows under {g25}")
    g = pd.concat([pd.read_csv(f, dtype={"fold": str}) for f in fs], ignore_index=True)
    return {"c3_o_sweep": o, "c3_K_sweep": k[k.K >= 10], "ghcp_o25": g[g.K >= 10]}


def wdiff(a, b):
    a, b = a.astype(float).to_numpy(), b.astype(float).to_numpy()
    both_inf = np.isinf(a) & np.isinf(b) & (np.sign(a) == np.sign(b))
    both_nan = np.isnan(a) & np.isnan(b)
    d = np.abs(a - b) / np.maximum(1.0, np.abs(b))
    d[both_inf | both_nan] = 0.0
    d[np.isnan(d)] = np.inf
    return d


def reproduce(D, refs):
    out, bad = [], []
    for name, ref in refs.items():
        for part in (1, 2):
            g = GRID[part]
            new = D[D.part == part]
            r = ref[ref.method.isin(METHODS) & ref.o.isin(g["o"]) & ref.K.isin(g["K"]) &
                    ref.task.isin(new.task.unique())]
            if name == "c3_o_sweep" and part == 2:
                r = r[r.K == 10]
            if len(r) == 0:
                continue
            m = r.merge(new, on=KEY, how="left", suffixes=("_r4", ""), indicator=True)
            missing = int((m._merge == "left_only").sum())
            b = m[m._merge == "both"]
            dcov = (b.coverage_r4.astype(float) - b.coverage.astype(float)).abs()
            dcov = dcov.where(~(b.coverage_r4.isna() & b.coverage.isna()), 0.0)
            dw = wdiff(b.width_mean, b.width_mean_r4)
            dwm = wdiff(b.width_median, b.width_median_r4)
            dn = (b.n_test_r4 != b.n_test)
            df = (b.finite_r4.astype(bool) != b.finite.astype(bool))
            flag = (dcov > 0) | (dw > WTOL) | (dwm > WTOL) | dn | df
            out.append(dict(reference=name, part=part, rows_expected=len(r), rows_missing=missing,
                            rows_matched=len(b), coverage_max_abs_diff=float(dcov.max()) if len(b) else np.nan,
                            width_mean_max_diff=float(dw.max()) if len(b) else np.nan,
                            width_median_max_diff=float(dwm.max()) if len(b) else np.nan,
                            n_test_mismatch=int(dn.sum()), finite_mismatch=int(df.sum()),
                            rows_flagged=int(flag.sum())))
            if flag.any():
                x = b[flag].copy()
                x["reference"] = name
                bad.append(x[KEY + ["part", "reference", "coverage_r4", "coverage", "width_mean_r4",
                                    "width_mean", "cpu_model", "src"]])
    return pd.DataFrame(out), (pd.concat(bad) if bad else pd.DataFrame())


def p3_vs_p2(D):
    a = D[(D.part == 3) & (D.K == 20)]
    b = D[(D.part == 2) & (D.K == 20) & D.task.isin(a.task.unique())]
    if len(a) == 0 or len(b) == 0:
        return dict(check="p3_K20_equals_p2_K20", value=np.nan, tol=0, passed=None, note="not both present")
    m = a.merge(b, on=KEY, suffixes=("_p3", "_p2"))
    d = max(float(wdiff(m.width_mean_p3, m.width_mean_p2).max()),
            float((m.coverage_p3 - m.coverage_p2).abs().max()))
    return dict(check="p3_K20_equals_p2_K20", value=d, tol=0.0, passed=bool(d == 0.0),
                note=f"{len(m)} rows of {len(a)}")


def within_cov(D):
    rows = []
    for (task, part, K, a, o, meth), g in D[D.method.isin(["within", "within_plain", "within_full"])
                                             & (D.o > 0)].groupby(["task", "part", "K", "alpha", "o", "method"]):
        if not g.finite.astype(bool).all():
            continue
        n = o - o // 2 if meth == "within" else o
        e = expected(n, a)
        cov = float(g.coverage.mean())
        rows.append(dict(task=task, part=part, K=K, alpha=a, o=o, method=meth, coverage=cov,
                         expected=e, diff=cov - e, within_0005=bool(abs(cov - e) <= 0.005),
                         n_rows=len(g), wf_frac_not_interval_max=float(g.wf_frac_not_interval.max())
                         if meth == "within_full" else np.nan))
    return pd.DataFrame(rows)


def by_fold(D):
    keys = ["part", "task", "label_set", "encoder", "method", "score", "alpha", "o", "K", "fold",
            "n_T_donors"]
    g = D.groupby(keys, dropna=False)
    return g.agg(coverage=("coverage", "mean"), width_mean=("width_mean", "mean"),
                 width_median=("width_median", "mean"), n_test=("n_test", "mean"),
                 finite_frac=("finite", "mean"), n_draws=("draw", "nunique")).reset_index()


def map_by_task(BF):
    rows = []
    gk = ["task", "part", "alpha", "K", "o", "method"]
    bf = BF.copy()
    bf["wfin"] = np.where(bf.finite_frac == 1.0, bf.width_mean, np.nan)
    enc = bf.groupby(gk + ["encoder"]).agg(cov=("coverage", "mean"), sd=("coverage", "std"),
                                         w=("wfin", "mean"), fin=("finite_frac", "mean"),
                                         nT=("n_T_donors", "median")).reset_index()
    for k, g in enc.groupby(gk):
        r = dict(zip(gk, k))
        r.update(n_T_donors=float(g.nT.median()), valid=r["method"] in VALID,
                 coverage=float(g["cov"].mean()), coverage_sd_folds=float(g.sd.mean()),
                 width_mean=float(g.w.mean()) if g.fin.min() == 1.0 else np.inf,
                 finite=float(g.fin.mean()))
        rows.append(r)
    M = pd.DataFrame(rows)
    # o-free methods on the map at every o of the part
    add = []
    for part, g in GRID.items():
        base = M[(M.part == part) & (M.o == 0) & M.method.isin(O_FREE)]
        for o in sorted(g["o"] - {0}):
            add.append(base.assign(o=o))
    if add:
        M = pd.concat([M] + add, ignore_index=True)
    M["narrowest_valid"] = False
    for k, g in M.groupby(["task", "part", "alpha", "K", "o"]):
        c = g[g.valid & (g.method != "one_per") & (g.finite == 1.0) & np.isfinite(g.width_mean)]
        if len(c):
            M.loc[c.width_mean.idxmin(), "narrowest_valid"] = True
    cols = ["task", "part", "alpha", "K", "n_T_donors", "o", "method", "valid", "coverage",
            "coverage_sd_folds", "width_mean", "finite", "narrowest_valid"]
    return M[cols].sort_values(["task", "part", "alpha", "K", "o", "method"]).reset_index(drop=True)


def main(a):
    os.makedirs(a.out, exist_ok=True)
    D, info = load(a.root, a.exclude or [])
    D["part"] = D.part.astype(int)
    acc = []
    dup = int(D.duplicated(KEY + ["part"]).sum())
    acc.append(dict(check="merge_duplicated_keys", value=dup, tol=0, passed=dup == 0, note=""))
    for part in (1, 2, 3):
        d = D[D.part == part]
        if len(d):
            acc.append(dict(check=f"merge_part{part}_tasks", value=len(d), tol=np.nan, passed=None,
                            note=json.dumps({t: int(n) for t, n in d.groupby("task").size().items()})))
    cols15 = C.FIXED_COLS + ["n_T_donors"]
    for part, name in ((1, "w3_o_sweep.csv.gz"), (2, "w3_K_sweep.csv.gz"), (3, "w3_fixed_head.csv.gz")):
        D[D.part == part][cols15].to_csv(os.path.join(a.out, name), index=False)
    R, bad = reproduce(D, r4_refs(a.r4))
    R.to_csv(os.path.join(a.out, "w3_reproduction.csv"), index=False)
    bad.to_csv(os.path.join(a.out, "w3_repro_mismatch_rows.csv"), index=False)
    for _, r in R.iterrows():
        acc.append(dict(check=f"1_reproduce_{r.reference}_part{r.part}", value=r.rows_flagged, tol=0,
                        passed=bool(r.rows_flagged == 0 and r.rows_missing == 0),
                        note=f"{r.rows_matched} matched of {r.rows_expected}, {r.rows_missing} missing; "
                             f"max cov diff {r.coverage_max_abs_diff}, max width diff {r.width_mean_max_diff:.3g}"))
    acc.append(p3_vs_p2(D))
    W = within_cov(D)
    W.to_csv(os.path.join(a.out, "w3_within_coverage.csv"), index=False)
    for meth, ch in (("within_plain", "2"), ("within", "2"), ("within_full", "3")):
        w = W[W.method == meth]
        nf = int((~w.within_0005).sum()) if len(w) else 0
        acc.append(dict(check=f"{ch}_{meth}_cov_within_0.005", value=nf, tol=0, passed=nf == 0,
                        note=f"{len(w)} cells; max |diff| {w['diff'].abs().max() if len(w) else float('nan'):.4f}"))
    BF = by_fold(D)
    BF.to_csv(os.path.join(a.out, "w3_by_fold.csv"), index=False)
    map_by_task(BF).to_csv(os.path.join(a.out, "w3_map_by_task.csv"), index=False)
    pd.DataFrame(acc).to_csv(os.path.join(a.out, "w3_acceptance.csv"), index=False)
    json.dump(dict(exclude=a.exclude or [], files=info), open(os.path.join(a.out, "w3_merge_inputs.json"), "w"), indent=1)
    print(pd.DataFrame(acc).to_string())


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True)
    p.add_argument("--r4", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--exclude", action="append")
    main(p.parse_args())
