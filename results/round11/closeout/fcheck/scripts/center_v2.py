"""fcheck: held out by center (report 6.3, headline H2 Part A) from spot-level prediction parquets and
the institution run's per-gene table. Own code; no project module imported."""
import glob, json, os
import numpy as np, pandas as pd, pyarrow.parquet as pq
R = "/work/users/w/e/weiyang/hest_replication/results/round11/closeout"
inputs = []
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40); pd.set_option("display.max_rows", 400)
def pear(Y, F):
    Yc = Y - Y.mean(0); Fc = F - F.mean(0)
    return (Yc * Fc).sum(0) / np.sqrt((Yc ** 2).sum(0) * (Fc ** 2).sum(0))
rows = []
dirs = sorted(glob.glob(f"{R}/predict/kidney__Visium__*__center") + glob.glob(f"{R}/predict/brain__Visium__*__center")
              + [f"{R}/predict/kidney__Visium__{a}__donor" for a in ("R10", "P")] + [f"{R}/predict/kidney__Visium__E__donor_v2"])
for dd in dirs:
    p = glob.glob(f"{dd}/pred__*.parquet"); assert len(p) == 1, dd
    p = p[0]; inputs.append(p)
    names = pq.ParquetFile(p).schema_arrow.names
    meta = [c for c in names if not (c.startswith("y_") or c.startswith("f_"))]
    print(os.path.basename(dd), "meta cols:", meta)
    foldcol = [c for c in ("fold", "test_unit", "center", "heldout", "held_out") if c in names]
    ys = [c for c in names if c.startswith("y_log1p__")]
    genes = [c[len("y_log1p__"):] for c in ys]
    fs = ["f_log1p__" + g for g in genes]
    d = pd.read_parquet(p, columns=ys + fs + meta)
    ok = np.isfinite(d[fs].to_numpy(float)).all(1)
    d = d[ok]
    r = pear(d[ys].to_numpy(float), d[fs].to_numpy(float))
    rec = dict(dir=os.path.basename(dd), spots=len(d), genes=len(genes), median_pearson_log1p=np.median(r), foldcol=str(foldcol))
    if foldcol:
        fc = foldcol[0]; fm = []; nan_genes = []
        for k, g in d.groupby(fc):
            pr = pear(g[ys].to_numpy(float), g[fs].to_numpy(float)); nan_genes.append(int(np.isnan(pr).sum())); fm.append(np.nanmedian(pr))
        fm = np.array(fm)
        rec.update(n_folds=len(fm), fold_median=np.median(fm), fold_q25=np.quantile(fm, 0.25), fold_q75=np.quantile(fm, 0.75), nan_genes_per_fold=str(nan_genes))
    rows.append(rec)
o = pd.DataFrame(rows); o.to_csv("fcheck_center_pearson.csv", index=False); print(o.to_string())
# HCP
f = f"{R}/a6/inst/center_v1/inst_by_center.csv"; inputs.append(f)
ic = pd.read_csv(f)
for c in ["task", "encoder", "scale", "arm", "alpha"]:
    print("inst_by_center", c, sorted(map(str, ic[c].unique())))
g = f"{R}/a6/inst/center_v1/inst_by_gene.parquet"; inputs.append(g)
ig = pd.read_parquet(g)
print("inst_by_gene cols", list(ig.columns))
for c in ig.columns:
    if ig[c].dtype == object or ig[c].nunique() < 15:
        print("  ", c, sorted(map(str, ig[c].unique()))[:15])
covcol = [c for c in ig.columns if "cov" in c.lower()]
print("coverage cols", covcol)
keys = [c for c in ("task", "encoder", "scale", "arm", "alpha", "center_unit") if c in ig.columns]
gm = ig.groupby(keys)[covcol[0]].median().reset_index().rename(columns={covcol[0]: "cov_median_gene"})
m = gm.merge(ic[keys + ["coverage_median_gene"]], on=keys, how="left")
m["diff"] = m.cov_median_gene - m.coverage_median_gene
print("by-gene recompute vs inst_by_center: max abs diff", np.nanmax(np.abs(m["diff"])), "rows", len(m), "unmatched", m.coverage_median_gene.isna().sum())
sel = gm[(gm.task == "kidney__Visium") & (gm.scale == "log1p") & (np.isclose(gm.alpha, 0.2))]
summ = sel.groupby([k for k in keys if k not in ("center_unit",)]).agg(
    median_center=("cov_median_gene", "median"), n_centers=("cov_median_gene", "size")).reset_index()
s6 = sel[sel.center_unit == "S0006"][[k for k in keys if k != "center_unit"] + ["cov_median_gene"]].rename(columns={"cov_median_gene": "S0006"})
summ = summ.merge(s6, how="left")
summ.to_csv("fcheck_center_hcp.csv", index=False); print(summ.to_string())
print(sel.to_string())
open("inputs.txt", "w").write("\n".join(sorted(set(inputs))) + "\n")
