"""Round 9 (claude-science) C0 diagnostics from cluster-level summaries.

Input: c0_cluster_summaries.csv.gz, built on Longleaf from the per-spot prediction parquets listed in
results/round9/diagnostics/c0_inputs.csv (gated data; the summaries stay outside the repository).
Outputs (aggregates over genes only): c0_gene_diagnostics.csv, c0_task_medians.csv, c0_shared_donor_factor.csv.
Usage: python code/scripts/round9_c0_diagnostics.py <c0_cluster_summaries.csv.gz> <outdir>
"""
import sys, numpy as np, pandas as pd
from scipy import stats

def gene_diag(g):
    r_mean = np.corrcoef(g.mean_y, g.mean_f)[0, 1]
    within = (g.cov_yf / np.sqrt(g.var_y * g.var_f)).mean()
    res = g.mean_y - np.polyval(np.polyfit(g.mean_f, g.mean_y, 1), g.mean_f)
    return pd.Series({"G": len(g), "R2c_mean": r_mean ** 2, "r_within": within,
                      "skew_meany": stats.skew(g.mean_y), "skew_resid_mean": stats.skew(res)})

def factor_rows(d):
    rows = []
    for (task, enc), g in d.groupby(["task", "encoder"]):
        if g.donor.nunique() < 10 or task.startswith("ACS"):
            continue
        M = g.pivot(index="donor", columns="gene", values="mean_y")
        Fm = g.pivot(index="donor", columns="gene", values="mean_f")
        Z = (M - M.mean()) / M.std()
        u, sv, vt = np.linalg.svd(Z.values - Z.values.mean(0), full_matrices=False)
        pc1 = u[:, 0] * sv[0]
        nz = g.pivot(index="donor", columns="gene", values="frac_nonzero_y").mean(1).values
        r2_pc1 = [np.corrcoef(pc1, Z[c].values)[0, 1] ** 2 for c in Z.columns]
        Zr = Z.values - np.outer(pc1, (pc1 @ Z.values) / (pc1 @ pc1))
        Fz = ((Fm - Fm.mean()) / Fm.std()).values
        r2a = np.nanmedian([np.corrcoef(Zr[:, j], Fz[:, j])[0, 1] ** 2 for j in range(Z.shape[1])])
        r2b = np.nanmedian([np.corrcoef(Z.values[:, j], Fz[:, j])[0, 1] ** 2 for j in range(Z.shape[1])])
        rows.append({"task": task, "encoder": enc, "G": len(M), "J": M.shape[1],
                     "pc1_share": sv[0] ** 2 / np.sum(sv ** 2),
                     "abs_r_pc1_avg_y": abs(np.corrcoef(pc1, M.mean(1).values)[0, 1]),
                     "abs_r_pc1_frac_nonzero": abs(np.corrcoef(pc1, nz)[0, 1]),
                     "median_gene_r2_on_pc1": np.median(r2_pc1),
                     "abs_r_pc1_avg_f": abs(np.corrcoef(pc1, Fm.mean(1).values)[0, 1]),
                     "median_r2c_before": r2b, "median_r2c_after_pc1": r2a})
    return pd.DataFrame(rows)

if __name__ == "__main__":
    src, outdir = sys.argv[1], sys.argv[2]
    d = pd.read_csv(src)
    gd = d.groupby(["task", "encoder", "gene"])[["mean_y", "mean_f", "var_y", "var_f", "cov_yf"]].apply(gene_diag).reset_index()
    gd.to_csv(f"{outdir}/c0_gene_diagnostics.csv", index=False)
    gd.groupby(["task", "encoder"])[["G", "R2c_mean", "r_within", "skew_meany", "skew_resid_mean"]].median().reset_index().to_csv(f"{outdir}/c0_task_medians.csv", index=False)
    factor_rows(d).to_csv(f"{outdir}/c0_shared_donor_factor.csv", index=False)
