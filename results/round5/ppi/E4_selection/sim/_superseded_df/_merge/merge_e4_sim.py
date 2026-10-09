"""Merge the six E4 simulation shards (commit 3894ad6) and compute E4.1, E4.4, tabulation. Local, no tracked files edited."""
import glob, json, os, sys
import numpy as np, pandas as pd
base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sim = os.path.join(base, "sim")
files = sorted(glob.glob(f"{sim}/G*_[ns]/e4_sim__G*_[ns].csv"))
assert len(files) == 6, files
d = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
d.to_csv(f"{base}/e4_sim.csv", index=False)
d["skew"] = np.where(d.law == "normal", "normal", "skewed")
CL, FIN = "textbook_t|fpc|lin", "textbook_t|fpc|lin"
out = {"rows": len(d), "nan_cols": {c: int(v) for c, v in d.isna().sum().items() if v and c != "p_a"},
       "n_draws": sorted(d.n_draws.unique().tolist()), "n_L": sorted(d.n_L.unique().tolist())}
keys = ["G", "law", "lambda_star"]
# E4.1
e = d[(d.design == "D2") & (d.p_a == 0.01) & (d.rule == "none") & (d.interval == CL)].copy()
e["pred_fp"] = 1 - e.r2_fp_median; e["pred_R2"] = 1 - e.R2
e["diff_fp"] = e.var_ratio_to_D0_classical_mean - e.pred_fp
e["diff_R2"] = e.var_ratio_to_D0_classical_mean - e.pred_R2
e["in05_fp"] = e.diff_fp.abs() <= 0.05; e["in05_R2"] = e.diff_R2.abs() <= 0.05
def summ(g):
    return pd.Series(dict(cells=len(g), in05_fp=int(g.in05_fp.sum()), in05_R2=int(g.in05_R2.sum()),
        dmin_fp=g.diff_fp.min(), dmax_fp=g.diff_fp.max(), dmin_R2=g.diff_R2.min(), dmax_R2=g.diff_R2.max()))
e41 = {"overall": summ(e).to_dict(),
       "by_G_law_lambda": e.groupby(keys).apply(summ).reset_index().to_dict("records"),
       "by_nL": e.groupby("n_L").apply(summ).reset_index().to_dict("records"),
       "worst_fp": e.reindex(e.diff_fp.abs().sort_values(ascending=False).index).head(8)[["G","n_L","R2","lambda_star","law","r2_fp_median","pred_fp","var_ratio_to_D0_classical_mean","diff_fp","diff_R2"]].to_dict("records"),
       "worst_R2": e.reindex(e.diff_R2.abs().sort_values(ascending=False).index).head(8)[["G","n_L","R2","lambda_star","law","pred_R2","var_ratio_to_D0_classical_mean","diff_fp","diff_R2"]].to_dict("records")}
out["E4.1"] = e41
# E4.4
cell = ["G","n_L","R2","lambda_star","law"]
def rng(s): return dict(min=float(s.min()), max=float(s.max()), median=float(s.median()))
e44 = {}
for pa in (0.1, 0.01):
    c = d[(d.design=="D2")&(d.p_a==pa)&(d.rule=="none")&(d.interval==CL)]
    e44[f"D2_pa{pa}_classical_cov"] = dict(cells=len(c), ge093=int((c.coverage_mean>=0.93).sum()), **rng(c.coverage_mean))
    for iv in ("textbook_t|fpc|lin", "textbook_t|fpc|lin|xf"):
        f2 = d[(d.design=="D2")&(d.p_a==pa)&(d.rule=="c_crossfit_design")&(d.interval==iv)].set_index(cell).coverage_mean
        f0 = d[(d.design=="D0")&(d.rule=="c_crossfit_design")&(d.interval==iv)].set_index(cell).coverage_mean
        dd = (f2 - f0.reindex(f2.index)).dropna()
        e44[f"D2_pa{pa}_final_minus_D0_{iv}"] = dict(cells=len(dd), within002=int((dd.abs()<=0.02).sum()), **rng(dd), worst=dd.reindex(dd.abs().sort_values(ascending=False).index).head(3).reset_index().to_dict("records"))
for rule in ("none", "c_crossfit_design"):
    c = d[(d.design=="D1")&(d.rule==rule)&(d.interval=="strat_t")]
    e44[f"D1_strat_t_{rule}"] = dict(cells=len(c), in_088_092=int(c.coverage_mean.between(0.88,0.92).sum()), **rng(c.coverage_mean),
        by_G=c.groupby("G").coverage_mean.agg(["min","median","max"]).round(4).reset_index().to_dict("records"))
    if (c.coverage_mean<0.88).any() or (c.coverage_mean>0.92).any():
        e44[f"D1_strat_t_{rule}"]["outside_by_nL"] = c.assign(o=~c.coverage_mean.between(0.88,0.92)).groupby("n_L").o.sum().to_dict()
# for comparison: D0 coverage of classical
c = d[(d.design=="D0")&(d.rule=="none")&(d.interval==CL)]; e44["D0_classical_cov"] = rng(c.coverage_mean)
out["E4.4"] = e44
# tabulation
pri = d[d.interval.isin([CL, "strat_t"])]
tab = (pri.groupby(["skew","G","n_L","design","p_a","rule"], dropna=False).var_ratio_to_D0_classical_mean
       .agg(median="median", n_cells="size").reset_index())
tab.to_csv(f"{base}/e4_sim_tabulation.csv", index=False)
pc1 = e.assign(prediction="E4.1")[["prediction"]+cell+["design","p_a","rule","interval","r2_fp_median","pred_fp","pred_R2","var_ratio_to_D0_classical_mean","diff_fp","diff_R2","in05_fp","in05_R2"]]
pcs = [pc1]
for iv in ("textbook_t|fpc|lin","textbook_t|fpc|lin|xf"):
    for pa in (0.1, 0.01):
        f2 = d[(d.design=="D2")&(d.p_a==pa)&(d.rule=="c_crossfit_design")&(d.interval==iv)].set_index(cell)
        f0 = d[(d.design=="D0")&(d.rule=="c_crossfit_design")&(d.interval==iv)].set_index(cell).coverage_mean
        t = f2[["design","p_a","rule","interval","coverage_mean"]].copy(); t["cov_D0"]=f0.reindex(t.index); t["cov_diff"]=t.coverage_mean-t.cov_D0
        t["in_002"]=t.cov_diff.abs()<=0.02; t["prediction"]="E4.4_final_vs_D0"; pcs.append(t.reset_index())
cl = d[(d.design=="D2")&(d.rule=="none")&(d.interval==CL)][cell+["design","p_a","rule","interval","coverage_mean"]].assign(prediction="E4.4_classical_D2", in_093=lambda x: x.coverage_mean>=0.93)
pcs.append(cl)
s1 = d[(d.design=="D1")&(d.interval=="strat_t")][cell+["design","p_a","rule","interval","coverage_mean"]].assign(prediction="E4.4_D1_strat", in_088_092=lambda x: x.coverage_mean.between(0.88,0.92))
pcs.append(s1)
pd.concat(pcs, ignore_index=True).to_csv(f"{base}/e4_sim_prediction_cells.csv", index=False)
json.dump(out, open(f"{sim}/_merge/e4_sim_merge_summary.json","w"), indent=1, default=float)
print(json.dumps({k: out[k] for k in ("rows","nan_cols","n_draws","n_L")}))
