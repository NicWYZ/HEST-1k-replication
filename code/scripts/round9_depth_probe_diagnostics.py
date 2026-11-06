"""Round 9 (claude-science): does a donor-level depth auxiliary explain between-donor variation that the predictions do not?

Inputs (outside the repository, derived from gated data): C0 cluster summaries and C1 donor-mean embeddings (uni_v2).
For each task and gene j, leave-one-donor-out R^2 of the donor mean of gene j regressed on
(a) the donor mean prediction, (b) a depth proxy (the donor's average over the OTHER genes, full donor data, an
upper bound for a probe estimate), (c) both; and the skewness of the donor means and of the (c) residuals.
Usage: python round9_depth_probe_diagnostics.py <c0_csv_gz> <outdir>
"""
import sys, numpy as np, pandas as pd
from scipy import stats

def loo_r2(x, y):
    G = len(y); X = np.column_stack([np.ones(G), x]); res = []
    for h in range(G):
        tr = np.arange(G) != h
        b = np.linalg.lstsq(X[tr], y[tr], rcond=None)[0]; res.append(y[h] - X[h] @ b)
    res = np.array(res)
    return 1 - (res ** 2).sum() / ((y - y.mean()) ** 2).sum(), res

if __name__ == "__main__":
    c0 = pd.read_csv(sys.argv[1]); outdir = sys.argv[2]; rows = []
    for task in ["CCRCC", "INDIANA_KIDNEY", "LUNG_XENIUM"]:
        g = c0[(c0.task == task) & (c0.encoder == "uni_v2")]
        M = g.pivot(index="donor", columns="gene", values="mean_y"); Fm = g.pivot(index="donor", columns="gene", values="mean_f")
        for j in M.columns:
            y = M[j].values; dep = M.drop(columns=j).mean(1).values; f = Fm[j].values
            r_f, _ = loo_r2(f[:, None], y); r_d, _ = loo_r2(dep[:, None], y); r_df, res = loo_r2(np.column_stack([dep, f]), y)
            rows.append(dict(task=task, gene=j, R2_pred=r_f, R2_depth=r_d, R2_depth_pred=r_df,
                             skew_y=stats.skew(y), skew_res_depth_pred=stats.skew(res)))
    pr = pd.DataFrame(rows)
    pr.to_csv(f"{outdir}/probe_depth_auxiliary_by_gene.csv", index=False)
    pr.groupby("task")[["R2_pred", "R2_depth", "R2_depth_pred", "skew_y", "skew_res_depth_pred"]].median().round(3).reset_index().to_csv(f"{outdir}/probe_depth_auxiliary_medians.csv", index=False)
