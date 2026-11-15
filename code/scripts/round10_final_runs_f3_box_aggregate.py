"""Round 10, track final-runs, F3.3 (ii) and F3.5: aggregation of the box units (question V) and the score of FR7.

usage: round10_final_runs_f3_box_aggregate.py <units_root> <production_index.json> <f2_summary.csv> <f2_gene_diag.parquet> <out_dir>
Reads every box unit's box_genes.csv (chunk 0) and box_coverage_genes.parquet (mu, C_fix1, the m grid of 5d.3 (ii)).
Writes (summaries first):
  f3_box_checks.json          completeness, gene counts, the FR7 verdicts;
  f3_box_units.csv            per unit: PROVENANCE status, box rows, coverage rows;
  f3_box_task_summary.csv     per (task, encoder, scale, lambda, gene scope): genes; Lambda0 median; median bounded and
                              unbounded requirement (a requirement above the grid's 2000 counts as infinite in the median
                              and is counted); the share of genes whose requirement is within the coverage grid (<= 500);
                              median coverage at the smallest grid m at or above each requirement, with its median Monte
                              Carlo standard error; median largest regime B share and median G*_B at each requirement;
                              F2's regime A kappa(e) and G*_e (mu, same task, encoder and scale) medians, labelled as
                              regime A's; Spearman correlations over genes of that coverage with G*_B (and with G*_e);
  f3_box_genes.csv.gz         the gene-level table behind it (stays with the bulk outputs);
  f3_box_coverage_summary.csv per (task, encoder, scale, m): median, 10% and 90% coverage, median E(V)/Var of mu, C_fix1;
  f3_fr7_clause1.csv          FR7 clause 1 cells: F2's regime B rows (C_fix1, theta3 on uni_v2 and log(1 + y) for CCRCC,
                              INDIANA_KIDNEY and LUNG_XENIUM, CCRCC_merged beside; ACS by state theta3 and mu), m >= 6,
                              with F3's mu rows (uni_v2, log(1 + y); ACS) at m >= 6 beside;
  f3_fr7_clause2.csv          per task (uni_v2, log(1 + y), mu, lambda = 1; ACS: pkg, log income) the medians over genes
                              of the two columns.
Gene scopes: 'all'; for LUNG_XENIUM also 'r9g42', round 9's subset (zlib.crc32(gene) % 7 == 0).
FR7 clause 1 holds if every clause-1 cell's median coverage is within 0.03 of 0.90; clause 2 holds if the unbounded
median is strictly larger than the bounded median on every task.
"""
import json, os, sys
import numpy as np, pandas as pd
from scipy import stats

root, idxp, f2sum, gdiag, out = sys.argv[1:6]
os.makedirs(out, exist_ok=True)
idx = json.load(open(idxp))
GRID = [3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50, 75, 100, 150, 200, 300, 500]
HEST3 = ["CCRCC", "INDIANA_KIDNEY", "LUNG_XENIUM"]


def status(d):
    pv = os.path.join(d, "PROVENANCE.txt")
    if not os.path.exists(pv):
        return "missing"
    return next((l.split(":", 1)[1].strip() for l in open(pv) if l.startswith("status:")), "no status")


units, bx, cv = [], [], []
for u in idx["units"]:
    if u["item"] != "box":
        continue
    d = os.path.join(root, u["unit"]); st = status(d)
    row = dict(unit=u["unit"], task=u["task"], status=st)
    if st == "COMPLETED":
        bp, cp = os.path.join(d, "box_genes.csv"), os.path.join(d, "box_coverage_genes.parquet")
        if os.path.exists(bp) and os.path.getsize(bp) > 2:
            b = pd.read_csv(bp); bx.append(b); row["box_rows"] = len(b)
        if os.path.exists(cp):
            x = pd.read_parquet(cp); cv.append(x); row["coverage_rows"] = len(x)
    units.append(row)
U = pd.DataFrame(units)
res = dict(units_expected=len(U), units_completed=int((U.status == "COMPLETED").sum()),
           units_not_completed=U[U.status != "COMPLETED"].unit.tolist())
json.dump(res, open(os.path.join(out, "f3_box_checks.json"), "w"), indent=1, default=str)
U.to_csv(os.path.join(out, "f3_box_units.csv"), index=False)
BX = pd.concat(bx, ignore_index=True); CV = pd.concat(cv, ignore_index=True)
CV = CV[(CV.estimand == "mu") & (CV.form == "C_fix1")]
res["box_rows"] = len(BX); res["coverage_rows"] = len(CV)
res["coverage_duplicates"] = int(CV.duplicated(subset=["task", "encoder", "scale", "gene", "m"]).sum())

KCOV = ["task", "encoder", "scale", "gene"]
cov = CV.set_index(KCOV + ["m"])[["coverage", "coverage_se", "ev_over_var"]]
B = BX[BX.get("note").isna()] if "note" in BX else BX
B = B.copy()


def grid_m(r):
    if pd.isna(r):
        return np.nan
    g = [m for m in GRID if m >= r]
    return float(g[0]) if g else np.nan


for col in ("bounded", "unbounded"):
    B[f"grid_m_{col}"] = B[f"m_min_B_{col}"].map(grid_m)
    key = [(t, e, s_, g, int(m)) if np.isfinite(m) else None
           for t, e, s_, g, m in zip(B.task, B.encoder, B.scale, B.gene, B[f"grid_m_{col}"])]
    vals = [cov.loc[k].to_numpy(float).ravel()[:3] if (k is not None and k in cov.index) else np.full(3, np.nan) for k in key]
    vals = np.array(vals) if vals else np.zeros((0, 3))
    B[f"coverage_at_{col}"] = vals[:, 0]; B[f"coverage_se_at_{col}"] = vals[:, 1]; B[f"ev_over_var_at_{col}"] = vals[:, 2]
GD = pd.read_parquet(gdiag)
gcols = [c for c in ("task", "encoder", "scale", "estimand", "gene", "kappa_e", "Gstar_e") if c in GD.columns]
GD = GD[gcols]; GD = GD[GD.estimand == "mu"].drop_duplicates(subset=["task", "encoder", "scale", "gene"]).drop(columns=["estimand"])
B = B.merge(GD, on=["task", "encoder", "scale", "gene"], how="left")
B.to_csv(os.path.join(out, "f3_box_genes.csv.gz"), index=False)
res["genes_with_regimeA_kappa"] = int(B.kappa_e.notna().sum()) if "kappa_e" in B else 0


def med_inf(s):
    x = s.fillna(np.inf).to_numpy(float)
    return float(np.median(x)) if len(x) else np.nan


def sp(a, b):
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 3 or np.std(a[ok]) == 0 or np.std(b[ok]) == 0:
        return np.nan, np.nan, int(ok.sum())
    r = stats.spearmanr(a[ok], b[ok]); return float(r.correlation), float(r.pvalue), int(ok.sum())


rows = []
scopes = [("all", B)] + [("r9g42", B[(B.task == "LUNG_XENIUM") & (B.r9g42.astype(bool))])]
for scope, S in scopes:
    for k, g in S.groupby(["task", "encoder", "scale", "lambda"]):
        r = dict(zip(["task", "encoder", "scale", "lambda"], k), scope=scope, genes=len(g), Lambda0_median=float(g.Lambda0.median()))
        for col in ("bounded", "unbounded"):
            r[f"median_m_{col}"] = med_inf(g[f"m_min_B_{col}"])
            r[f"n_none_{col}"] = int(g[f"m_min_B_{col}"].isna().sum())
            r[f"share_within_grid_{col}"] = float((g[f"m_min_B_{col}"] <= 500).mean())
            r[f"median_coverage_at_{col}"] = float(g[f"coverage_at_{col}"].median())
            r[f"median_mcse_at_{col}"] = float(g[f"coverage_se_at_{col}"].median())
            r[f"n_coverage_at_{col}"] = int(g[f"coverage_at_{col}"].notna().sum())
            r[f"median_v_max_at_{col}"] = float(g[f"v_max_at_m_{col}"].median())
            r[f"median_Gstar_B_at_{col}"] = float(g[f"Gstar_B_at_m_{col}"].median())
            rho, p, n = sp(g[f"coverage_at_{col}"].to_numpy(float), g[f"Gstar_B_at_m_{col}"].to_numpy(float))
            r[f"spearman_cov_GstarB_{col}"] = rho; r[f"spearman_p_{col}"] = p; r[f"spearman_n_{col}"] = n
            if "Gstar_e" in g:
                rho, p, n = sp(g[f"coverage_at_{col}"].to_numpy(float), g["Gstar_e"].to_numpy(float))
                r[f"spearman_cov_Gstar_e_regimeA_{col}"] = rho
        if "kappa_e" in g:
            r["median_kappa_e_regimeA"] = float(g.kappa_e.median()); r["median_Gstar_e_regimeA"] = float(g.Gstar_e.median())
        rows.append(r)
T = pd.DataFrame(rows); T.to_csv(os.path.join(out, "f3_box_task_summary.csv"), index=False)
q = lambda p: (lambda s: s.quantile(p))
CS = CV.groupby(["task", "encoder", "scale", "m"]).agg(genes=("gene", "size"), median_coverage=("coverage", "median"),
                                                       q10_coverage=("coverage", q(0.1)), q90_coverage=("coverage", q(0.9)),
                                                       median_coverage_se=("coverage_se", "median"),
                                                       median_ev_over_var=("ev_over_var", "median")).reset_index()
CS.to_csv(os.path.join(out, "f3_box_coverage_summary.csv"), index=False)

# FR7 clause 1
f2 = pd.read_csv(f2sum)
c1 = f2[(f2.form == "C_fix1") & (f2.m >= 6) & (((f2.task.isin(HEST3 + ["CCRCC_merged"])) & (f2.encoder == "uni_v2") & (f2.scale == "log1p")
                                                & (f2.estimand == "theta3")) | ((f2.task == "ACS_STATES") & (f2.estimand.isin(["theta3", "mu"]))))].copy()
c1["source"] = "F2 regime B"; c1["primary"] = c1.task != "CCRCC_merged"
f3 = CS[(CS.m >= 6) & (((CS.task.isin(HEST3 + ["CCRCC_merged"])) & (CS.encoder == "uni_v2") & (CS.scale == "log1p")) | (CS.task == "ACS_STATES"))].copy()
f3["estimand"] = "mu"; f3["form"] = "C_fix1"; f3["source"] = "F3 mu coverage cells"; f3["primary"] = False
cols = ["source", "primary", "task", "encoder", "scale", "estimand", "m", "form", "genes", "median_coverage", "q10_coverage", "q90_coverage"]
C1 = pd.concat([c1[cols], f3[cols]], ignore_index=True)
C1["dev"] = (C1.median_coverage - 0.90).abs(); C1["within_0_03"] = C1.dev <= 0.03
C1.to_csv(os.path.join(out, "f3_fr7_clause1.csv"), index=False)
p1 = C1[C1.primary]
cl1 = dict(cells=len(p1), within=int(p1.within_0_03.sum()), max_abs_dev=float(p1.dev.max()) if len(p1) else None,
           cov_range=[float(p1.median_coverage.min()), float(p1.median_coverage.max())] if len(p1) else None,
           verdict="held" if len(p1) and p1.within_0_03.all() else "refuted",
           beside=dict(CCRCC_merged=dict(cells=int((C1.task.eq("CCRCC_merged") & C1.source.eq("F2 regime B")).sum()),
                                         within=int((C1.task.eq("CCRCC_merged") & C1.source.eq("F2 regime B") & C1.within_0_03).sum())),
                       f3_mu=dict(cells=int(C1.source.eq("F3 mu coverage cells").sum()),
                                  within=int((C1.source.eq("F3 mu coverage cells") & C1.within_0_03).sum()),
                                  max_abs_dev=float(C1[C1.source.eq("F3 mu coverage cells")].dev.max()) if C1.source.eq("F3 mu coverage cells").any() else None)))
# FR7 clause 2
sel = T[(T["lambda"] == 1.0) & (T.scope == "all") & (((T.encoder == "uni_v2") & (T.scale == "log1p")) | (T.task == "ACS_STATES"))]
C2 = sel[["task", "encoder", "scale", "genes", "median_m_bounded", "median_m_unbounded", "n_none_bounded", "n_none_unbounded"]].copy()
C2["unbounded_strictly_larger"] = C2.median_m_unbounded > C2.median_m_bounded
C2.to_csv(os.path.join(out, "f3_fr7_clause2.csv"), index=False)
cl2 = dict(tasks=len(C2), strictly_larger=int(C2.unbounded_strictly_larger.sum()),
           verdict="held" if len(C2) and C2.unbounded_strictly_larger.all() else "refuted")
res["fr7"] = dict(clause1=cl1, clause2=cl2,
                  verdict=("held" if cl1["verdict"] == "held" and cl2["verdict"] == "held" else
                           ("partly held" if "held" in (cl1["verdict"], cl2["verdict"]) else "refuted")))
json.dump(res, open(os.path.join(out, "f3_box_checks.json"), "w"), indent=1, default=str)
print(json.dumps(res, indent=1, default=str))
