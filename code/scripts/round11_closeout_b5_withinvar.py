"""Round 11, track closeout, B5: are within-cluster variances equal across clusters, as round 10's allocation factor
assumes (F4-3b; brief, section 5, item 5)?

Regime B estimates each cluster's value as the mean of m_g sampled unit contributions, so for the fixed coefficient the
cluster's design variance is (1 - m_g/M_g) V_g / m_g with V_g the within-cluster variance of the residual contribution
r_i = z_i - w_i f_i (theta3: z_i = w_i y_i with round 3's slope weight w_i = (m_i - mu_g)/v_g from
round3_b1_ppi.build_z, so the cluster's slope is the mean of z_i; mu: w_i = 1). Under the equally weighted target and
ignoring the finite-population factor, size-proportional allocation (m_g = B M_g / N) against equal allocation
(m_g = B / G) inflates the variance by
    factor_measured = Mbar * sum_g (V_g / M_g) / sum_g V_g,
which equals round 10's factor Mbar * (1/G) sum_g 1/M_g (f4_alloc_by_task.csv) exactly when every V_g is equal. Per
task, scale, estimand and gene: both factors, the coefficient of variation of V_g over clusters, the ratio of the
largest to the smallest V_g, the Spearman correlation of V_g with M_g, and the Brown-Forsythe test of equal variances
of r_i across clusters (scipy.stats.levene, center='median'; with thousands of units per cluster any difference is
significant, so the size of the spread is what is read). Populations: round 10's F3 regcomp theta3 populations of the
HEST tasks (uni_v2, log1p) and ACS by state, loaded through round10_final_runs_f2_regimeB.load as round 10's allocation
reading loads them.
Writes b5_summary.json first, then b5_by_gene.csv, b5_by_task.csv, b5_clusters.csv (V_g and M_g per cluster).
Usage: round11_closeout_b5_withinvar.py <round10_regimeB_dir>
"""
import glob, json, os, sys
import numpy as np, pandas as pd
from scipy import stats
import round10_final_runs_f2_regimeB as F2
import round4_ppi_q2_masking as Q2

TASKS = [("CCRCC", "uni_v2", "log1p"), ("CCRCC_merged", "uni_v2", "log1p"), ("INDIANA_KIDNEY", "uni_v2", "log1p"),
         ("LUNG_XENIUM", "uni_v2", "log1p"), ("ACS_STATES", "pkg", "log_income")]


def find_pop(cdir, task, enc, sc):
    for p in sorted(glob.glob(os.path.join(cdir, f"regcomp__pk_{task}__{enc}__{sc}__p*", "f3_regcomp__*.json"))):
        for q in json.load(open(p))["populations"]:
            if "theta3" in q.get("estimands", []):
                return q
    raise FileNotFoundError(task)


def main():
    cdir = sys.argv[1]
    gr, cr, tr = [], [], []
    for task, enc, sc in TASKS:
        pop = find_pop(cdir, task, enc, sc)
        data = F2.load(pop)
        G = len(data["donors"]); didx = data["didx"]
        M = np.bincount(didx, minlength=G).astype(float)
        Y, P = np.asarray(data["Y"], float), np.asarray(data["P"], float)
        c = Q2.B1.design_consts(data["m"], data["neo"], didx, G)
        w3 = Q2.B1.build_z("theta3", np.ones((len(didx), 1)), data["m"], data["neo"], c, didx)[:, 0, 0]
        f_r10 = float(np.mean(M.mean() / M))
        for est, w in (("theta3", w3), ("mu", np.ones(len(didx)))):
            ok_units = np.isfinite(w)
            for j, gname in enumerate(data["genes"]):
                r = w * (Y[:, j] - P[:, j])
                V = np.full(G, np.nan); groups = []
                for g in range(G):
                    m = (didx == g) & ok_units
                    if m.sum() >= 2:
                        V[g] = r[m].var(ddof=1); groups.append(r[m])
                keep = np.isfinite(V) & (V > 0)
                Vk, Mk = V[keep], M[keep]
                fm = float(Mk.mean() * np.sum(Vk / Mk) / np.sum(Vk))
                fe = float(np.mean(Mk.mean() / Mk))
                bf = stats.levene(*groups, center="median") if len(groups) >= 2 else None
                gr.append(dict(task=task, encoder=enc, scale=sc, estimand=est, gene=gname, G=int(keep.sum()),
                               factor_equal_var=fe, factor_measured=fm, ratio_measured_over_equal=fm / fe,
                               cv_V=float(Vk.std(ddof=0) / Vk.mean()), max_over_min_V=float(Vk.max() / Vk.min()),
                               spearman_V_M=float(stats.spearmanr(Vk, Mk)[0]) if len(Vk) > 2 else np.nan,
                               bf_stat=float(bf.statistic) if bf else np.nan, bf_p=float(bf.pvalue) if bf else np.nan))
                if j < 3:
                    for g in range(G):
                        cr.append(dict(task=task, estimand=est, gene=gname, cluster=str(data["donors"][g]), M=M[g], V=V[g]))
        print(f"[b5] {task} done; round 10 factor {f_r10:.4f}", flush=True)
    D = pd.DataFrame(gr)
    T = D.groupby(["task", "encoder", "scale", "estimand"]).agg(
        G=("G", "first"), genes=("gene", "size"), factor_equal_var=("factor_equal_var", "first"),
        factor_measured_median=("factor_measured", "median"), factor_measured_q10=("factor_measured", lambda s: s.quantile(.1)),
        factor_measured_q90=("factor_measured", lambda s: s.quantile(.9)),
        ratio_median=("ratio_measured_over_equal", "median"), cv_V_median=("cv_V", "median"),
        max_over_min_V_median=("max_over_min_V", "median"), spearman_V_M_median=("spearman_V_M", "median"),
        share_bf_p_lt_001=("bf_p", lambda s: float((s < 0.001).mean()))).reset_index()
    acs = T[(T.task == "ACS_STATES") & (T.estimand == "theta3")]
    hest = T[(T.task != "ACS_STATES") & (T.estimand == "theta3")]
    summ = dict(by_task=T.to_dict("records"),
                acs_theta3_factor_measured_median=float(acs.factor_measured_median.iloc[0]) if len(acs) else None,
                hest_theta3_factor_measured_median_max=float(hest.factor_measured_median.max()) if len(hest) else None)
    json.dump(summ, open("b5_summary.json", "w"), indent=1)
    D.to_csv("b5_by_gene.csv", index=False); T.to_csv("b5_by_task.csv", index=False)
    pd.DataFrame(cr).to_csv("b5_clusters.csv", index=False)
    print(T.to_string())


if __name__ == "__main__":
    main()
