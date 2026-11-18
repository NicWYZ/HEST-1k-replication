"""fcheck: donor-level quantities (report sections 6.2, headline H3, 5.3 A6.1/A6.2), recomputed from
regimeA_cells.parquet, cluster_values parquet, d12 per-gene csv and spot-level prediction parquets.
Own code; no project module imported."""
import glob, json, os
import numpy as np, pandas as pd
from scipy.stats import spearmanr
R = "/work/users/w/e/weiyang/hest_replication/results/round11/closeout"
TASKS = ["CCRCC", "INDIANA_KIDNEY", "LUNG_XENIUM", "kidney__Visium", "bowel__Visium"]
ARMS = ["R10", "P", "E"]
inputs = []
def rd(p, **kw):
    inputs.append(p); return pd.read_parquet(p, **kw)

def spot_pearson(task, arm):
    """per (scale, gene) Pearson over all spots of the file the chain fed to cluster_values."""
    spec = json.load(open(f"{R}/a6/donor/{task}__{arm}/a6_spec.json"))
    cvstep = [s for s in spec["steps"] if s["name"] == "cv"][0]
    out = {}
    for pop in cvstep["config"]["populations"]:
        path = pop["path"].replace("{OUT}", f"{R}/a6/donor/{task}__{arm}")
        for sc in pop["scales"]:
            cols = None
            import pyarrow.parquet as pq
            names = pq.ParquetFile(path).schema_arrow.names
            ys = [c for c in names if c.startswith(sc["y_prefix"])]
            genes = [c[len(sc["y_prefix"]):] for c in ys]
            fs = [sc["f_prefix"] + g for g in genes]
            d = rd(path, columns=ys + fs)
            Y = d[ys].to_numpy(float); F = d[fs].to_numpy(float)
            ok = np.isfinite(F).all(1) & np.isfinite(Y).all(1)
            Y = Y[ok]; F = F[ok]
            Yc = Y - Y.mean(0); Fc = F - F.mean(0)
            r = (Yc * Fc).sum(0) / np.sqrt((Yc ** 2).sum(0) * (Fc ** 2).sum(0))
            for g, v in zip(genes, r):
                out[(sc["name"], g)] = v
            print(f"[spot] {task} {arm} {sc['name']} file={os.path.basename(path)} spots={ok.sum()} of {len(ok)} genes={len(genes)}")
    return out

rows = []; pergene = []
for task in TASKS:
    for arm in ARMS:
        base = f"{R}/a6/donor/{task}__{arm}"
        c = rd(f"{base}/regimeA/regimeA_cells.parquet")
        c = c[c.variance == "fpc"]
        cvf = glob.glob(f"{base}/cv/cluster_values__*.parquet"); assert len(cvf) == 1
        cv = rd(cvf[0])
        r2c = {}; sdf = {}
        for (sc, est, g), gg in cv.groupby(["scale", "estimand", "gene"]):
            gg = gg.dropna(subset=["z", "f"])
            r2c[(sc, est, g)] = np.corrcoef(gg.z.to_numpy(float), gg.f.to_numpy(float))[0, 1] ** 2
            sdf[(sc, est, g)] = np.std(gg.f.to_numpy(float), ddof=1)
        sp = spot_pearson(task, arm)
        fx = c[c.arm == "fix1"].set_index(["scale", "estimand", "gene", "n"])
        cl = c[c.arm == "classical"].set_index(["scale", "estimand", "gene", "n"])
        j = fx[["median_width", "coverage", "coverage_se"]].join(cl[["median_width", "coverage"]], rsuffix="_cl", how="inner")
        assert len(j) == len(fx) == len(cl), (task, arm, len(j), len(fx), len(cl))
        j["wr"] = j.median_width / j.median_width_cl
        j = j.reset_index()
        j["R2c"] = [r2c[(a, b, g)] for a, b, g in zip(j.scale, j.estimand, j.gene)]
        j["sd_f"] = [sdf[(a, b, g)] for a, b, g in zip(j.scale, j.estimand, j.gene)]
        j["pearson_spot"] = [sp.get((a, g), np.nan) for a, g in zip(j.scale, j.gene)]
        j["task"] = task; j["arm"] = arm
        pergene.append(j)
pg = pd.concat(pergene, ignore_index=True)
pg.to_csv("fcheck_donor_pergene.csv", index=False)
print("pergene rows", len(pg), "missing pearson", pg.pearson_spot.isna().sum())

ref = pg[pg.arm == "R10"].set_index(["task", "scale", "estimand", "gene", "n"])
out = []
for (task, arm, sc, est, n), g in pg.groupby(["task", "arm", "scale", "estimand", "n"]):
    rec = dict(task=task, arm=arm, scale=sc, estimand=est, n=n, genes=len(g),
               wr_median=g.wr.median(), cov_fix1_median=g.coverage.median(), cov_cl_median=g.coverage_cl.median(),
               mcse_fix1_median=g.coverage_se.median(), R2c_median=g.R2c.median(),
               pearson_spot_median=g.pearson_spot.median(), sd_f_median=g.sd_f.median(),
               rho_wr_R2c=spearmanr(g.wr, g.R2c).correlation,
               rho_wr_pearson=spearmanr(g.wr, g.pearson_spot).correlation)
    r = ref.loc[[(task, sc, est, gg, n) for gg in g.gene]]
    d = g.wr.to_numpy() - r.wr.to_numpy()
    rec.update(wr_diff_median=np.median(d), wr_diff_q25=np.quantile(d, 0.25), wr_diff_q75=np.quantile(d, 0.75))
    ratio = g.sd_f.to_numpy() / r.sd_f.to_numpy()
    rec.update(sdf_ratio_median_of_ratios=np.median(ratio), sdf_ratio_of_medians=g.sd_f.median() / r.sd_f.median(),
               R2c_median_R10=r.R2c.median())
    out.append(rec)
o = pd.DataFrame(out); o.to_csv("fcheck_donor_cells.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40); pd.set_option("display.max_rows", 400)
print(o[(o.scale == "log1p") & (o.estimand == "theta3") & (o.n == 8)][["task", "arm", "genes", "wr_median", "wr_diff_median", "wr_diff_q25", "wr_diff_q75", "R2c_median", "cov_fix1_median", "mcse_fix1_median", "pearson_spot_median", "rho_wr_R2c", "rho_wr_pearson"]].to_string())
th = o[o.estimand == "theta3"]; mu = o[o.estimand == "mu"]
print("theta3 cells", len(th), "rho_R2c < rho_pearson in", int((th.rho_wr_R2c < th.rho_wr_pearson).sum()), "range rho_R2c", th.rho_wr_R2c.min(), th.rho_wr_R2c.max())
print("mu cells", len(mu), "rho_R2c < rho_pearson in", int((mu.rho_wr_R2c < mu.rho_wr_pearson).sum()))
print(mu[~(mu.rho_wr_R2c < mu.rho_wr_pearson)][["task", "arm", "scale", "n", "rho_wr_R2c", "rho_wr_pearson"]].to_string())
c15 = th[(th.scale == "log1p") & (th.n == 8)]
print("A6.2(d) 15 cells: rho_R2c range", c15.rho_wr_R2c.min(), c15.rho_wr_R2c.max(), "rho_pearson range", c15.rho_wr_pearson.min(), c15.rho_wr_pearson.max(), "held", int((c15.rho_wr_R2c < c15.rho_wr_pearson).sum()))
print("--- mu log1p n8 (A6.1, R2c changes)")
print(mu[(mu.scale == "log1p") & (mu.n == 8)][["task", "arm", "R2c_median", "R2c_median_R10", "sdf_ratio_median_of_ratios", "sdf_ratio_of_medians", "cov_fix1_median"]].to_string())
print("--- fix1 coverage, n in 8,16, all")
print(o[o.n.isin([8, 16])][["task", "arm", "scale", "estimand", "n", "cov_fix1_median", "cov_cl_median"]].to_string())
print("--- lognorm theta3 wr")
print(o[(o.scale == "lognorm") & (o.estimand == "theta3")][["task", "arm", "n", "wr_median"]].to_string())
# D12
d12 = []
for task in TASKS:
    for arm in ARMS:
        for f in glob.glob(f"{R}/a6/donor/{task}__{arm}/d12*/d12_lodo_r2__*.csv"):
            inputs.append(f); d = pd.read_csv(f)
            for sc, g in d.groupby("scale"):
                d12.append(dict(task=task, arm=arm, scale=sc, genes=len(g), file=os.path.basename(f), R2_loo_const_median=g.R2_loo_const.median()))
d12 = pd.DataFrame(d12).sort_values(["task", "scale", "arm"]); d12.to_csv("fcheck_d12.csv", index=False)
print(d12.to_string())
open("inputs.txt", "w").write("\n".join(sorted(set(inputs))) + "\n")
