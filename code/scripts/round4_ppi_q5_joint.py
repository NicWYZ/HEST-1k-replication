"""Round 4 PPI, Q5: the joint design table (plan section 3 Q5 and section 14.9, addendum 2 item 4).

Per task and m (labelled spots per donor in regime B), regime B's confidence-interval width ratio
(PPI over classical, c_crossfit, regB_t) from the Q4 main table, and from the conformal track's C3
o-sweep at o = m (nearest o at or below m, named in o_used) the coverage, mean width and finite share
of ghcp, within_plain and within at K = 10, alpha = 0.1, averaged over encoders, folds and draws.
Widths are averaged over finite sets only; the finite share is beside each. The cheapest valid set
follows the conformal track's rule: hcp at o = 0, ghcp for 0 < o < 9, within_plain for 9 <= o < 25,
within from o = 25. HEST width ratios are medians over the three encoders (the permuted arm is in a
separate column); ACS uses the package predictor. ACS_CA_PUMA has no C3 counterpart."""
import argparse
import numpy as np
import pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument("--main", required=True)
ap.add_argument("--c3", required=True)
ap.add_argument("--c3-commit", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--cluster", default=None)
ap.add_argument("--numbers", default=None)
a = ap.parse_args()

TASKMAP = {"CCRCC": "CCRCC", "CCRCC_merged": "CCRCC_23merged", "INDIANA_KIDNEY": "INDIANA_KIDNEY",
           "LUNG_XENIUM": "LUNG_XENIUM", "ACS_STATES": "ACS", "ACS_CA_PUMA": None}
OGRID = [0, 5, 10, 25, 50, 100, 200]
M = pd.read_csv(a.main, low_memory=False)
B = M[(M.regime == "B") & (M.lambda_rule == "c_crossfit") & (M.population == "donor") & (M.target == "design")]
c3 = pd.read_csv(a.c3)
c3 = c3[(c3.K == 10) & (c3.alpha == 0.1) & (c3.method.isin(["ghcp", "within_plain", "within", "hcp"]))]


def conf(task, o):
    out = {}
    for meth in ("ghcp", "within_plain", "within"):
        z = c3[(c3.task == task) & (c3.o == o) & (c3.method == meth)]
        fin = z[z.finite == 1]
        out[f"{meth}_coverage"] = z.coverage.mean() if len(z) else np.nan
        out[f"{meth}_width_mean_finite"] = fin.width_mean.mean() if len(fin) else np.nan
        out[f"{meth}_finite_share"] = z.finite.mean() if len(z) else np.nan
        out[f"{meth}_n_rows"] = len(z)
    return out


def cheapest(o):
    return "hcp" if o == 0 else "ghcp" if o < 9 else "within_plain" if o < 25 else "within"


rows = []
for (vt, cost, budget), z in B.groupby(["vtag", "cost", "budget"], dropna=False):
    enc = z[z.arm != "permuted"]
    perm = z[z.arm == "permuted"]
    m = float(enc.m.astype(float).median())
    r = dict(vtag=vt, c3_task=TASKMAP.get(vt), cost=cost, budget_B=budget, G=int(z.G.iloc[0]), m=m,
             n_arms=enc.arm.nunique())
    for est in ("theta3", "theta2"):
        e = enc[enc.estimand == est]
        p = perm[perm.estimand == est]
        r[f"regB_width_ratio_{est}"] = e.width_ratio_median.median() if len(e) else np.nan
        r[f"regB_coverage_{est}"] = e.coverage_median.median() if len(e) else np.nan
        r[f"regB_width_ratio_{est}_permuted"] = p.width_ratio_median.median() if len(p) else np.nan
    o = max(x for x in OGRID if x <= m)
    r["o_used"] = o
    r["o_matches_m"] = bool(o == m)
    r["cheapest_valid_set"] = cheapest(o)
    if r["c3_task"] is not None:
        r.update(conf(r["c3_task"], o))
        meth = r["cheapest_valid_set"]
        if meth != "hcp":
            r["cheapest_coverage"] = r[f"{meth}_coverage"]
            r["cheapest_width_mean_finite"] = r[f"{meth}_width_mean_finite"]
    else:
        r["note"] = "no C3 counterpart"
    rows.append(r)
J = pd.DataFrame(rows).sort_values(["vtag", "m", "cost"])
J["c3_commit"] = a.c3_commit
J.to_csv(a.out, index=False)
print(J[["vtag", "cost", "m", "o_used", "regB_width_ratio_theta3", "cheapest_valid_set", "ghcp_coverage",
         "within_plain_coverage", "within_coverage"]].to_string(index=False))

if a.numbers:
    nums = []
    for task in sorted(c3.task.unique()):
        for o, meth in ((5, "ghcp"), (10, "within_plain"), (10, "ghcp"), (5, "within_plain")):
            z = c3[(c3.task == task) & (c3.o == o) & (c3.method == meth)]
            fin = z[z.finite == 1]
            nums += [dict(name=f"c3|{task}|o{o}|{meth}|coverage_mean", value=z.coverage.mean()),
                     dict(name=f"c3|{task}|o{o}|{meth}|width_mean_finite", value=fin.width_mean.mean() if len(fin) else np.nan),
                     dict(name=f"c3|{task}|o{o}|{meth}|finite_share", value=z.finite.mean())]
    nums.append(dict(name="joint|rows", value=len(J)))
    if a.cluster:
        ct = pd.read_csv(a.cluster)
        nums.append(dict(name="cluster|rows", value=len(ct)))
        for k, z in ct.groupby("task"):
            nums.append(dict(name=f"cluster|rows|{k}", value=len(z)))
        nums.append(dict(name="cluster|rows_with_loo_offset", value=int(ct.loo_offset_pred_median_over_genes.notna().sum())))
    pd.DataFrame(nums, dtype=object).to_csv(a.numbers, index=False)
