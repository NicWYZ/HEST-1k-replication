"""fcheck: rebuild a6/conformal per-fold coverage (a1_by_fold) from the per-gene parquet of each unit."""
import glob, os
import numpy as np, pandas as pd
R = "/work/users/w/e/weiyang/hest_replication/results/round11/closeout"
inputs = []
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 500)
# deeper check: rebuild the per-fold coverage from the per-gene parquet for every unit
pg_rows = []
for d in sorted(glob.glob(f"{R}/a6/conformal/*__*__*")):
    b = os.path.basename(d)
    for pf_ in glob.glob(f"{d}/pergene__*.parquet"):
        inputs.append(pf_)
        g = pd.read_parquet(pf_)
        g = g[g.score == "abs"].copy()
        g["scale"] = g.gene.str.split("|").str[0]
        for sc in ("log1p", "lognorm"):
            fo = f"{d}/a1_by_fold__" + os.path.basename(pf_)[len("pergene__"):-len(".parquet")] + f"__{sc}.csv"
            if not os.path.exists(fo): continue
            bf = pd.read_csv(fo)
            q = g[(g.scale == sc)]
            for nm, sub in (("all_rows_mean", q), ("ge_min_spots_mean", q[q.slide_ge_min_spots])):
                v = sub.groupby(["design", "fold"]).coverage.mean().rename("v").reset_index(); v["fold"] = v.fold.astype(str); bf["fold"] = bf.fold.astype(str)
                m = bf.merge(v, on=["design", "fold"], how="left")
                m = m[m.design.isin(v.design.unique())]
                pg_rows.append(dict(dir=b, scale=sc, variant=nm, folds=len(m), unmatched=int(m.v.isna().sum()), max_abs_diff=float((m.v - m.coverage).abs().max())))
P = pd.DataFrame(pg_rows); P.to_csv("fcheck_conformal_pergene_rebuild.csv", index=False)
print(P.groupby("variant").agg(units=("dir", "size"), max_abs_diff=("max_abs_diff", "max"), unmatched=("unmatched", "sum")).to_string())
open("inputs.txt", "w").write("\n".join(sorted(set(inputs))) + "\n")
print(P.to_string())
