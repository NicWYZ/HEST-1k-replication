"""fcheck: split conformal coverage (report 6.4, headline H1(b) Part A, A6.4 counted claims, B2),
from per-fold tables (and per-slide tables as a deeper check); round 3 uni_v2 shortfalls from the repo file.
Own code; no project module imported."""
import glob, os, re
import numpy as np, pandas as pd
R = "/work/users/w/e/weiyang/hest_replication/results/round11/closeout"
inputs = []
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40); pd.set_option("display.max_rows", 400)
rows = []; chk = []
for d in sorted(glob.glob(f"{R}/a6/conformal/*__*__*")):
    b = os.path.basename(d)
    if b.startswith("anchor") or b == "selftest_v1": continue
    for f in sorted(glob.glob(f"{d}/a1_by_fold__*.csv")):
        inputs.append(f)
        sc = "log1p" if f.endswith("__log1p.csv") else "lognorm"
        x = pd.read_csv(f)
        for (task, enc, design, score), g in x.groupby(["task", "encoder", "design", "score"]):
            rec = dict(dir=b, task=task, arm=enc.replace("_center", ""), scale=sc, design=design, score=score, n_folds=len(g),
                       coverage_mean=g.coverage.mean(), coverage_sd_ddof1=g.coverage.std(ddof=1), coverage_sd_ddof0=g.coverage.std(ddof=0))
            # per-slide reconstruction
            sf = f.replace("a1_by_fold__", "a1_by_slide__")
            if os.path.exists(sf):
                inputs.append(sf)
                s = pd.read_csv(sf); s = s[(s.design == design) & (s.score == score)]
                s50 = s[s.n_test >= 50]
                pf = s50.groupby("fold")[["coverage", "n_test"]].apply(lambda q: np.average(q.coverage, weights=q.n_test))
                rec.update(slide50_wmean_folds=len(pf), slide50_wmean_cov=pf.mean())
            tf = f.replace("a1_by_fold__", "a1_by_task__"); inputs.append(tf)
            t = pd.read_csv(tf); t = t[(t.design == design) & (t.score == score)]
            assert len(t) == 1
            rec.update(task_n_folds=int(t.n_folds.iloc[0]), task_cov_mean=float(t.coverage_mean.iloc[0]), task_cov_sd=float(t.coverage_sd.iloc[0]))
            rows.append(rec)
o = pd.DataFrame(rows)
o["d_mean"] = o.coverage_mean - o.task_cov_mean
o["d_sd1"] = o.coverage_sd_ddof1 - o.task_cov_sd
o["d_sd0"] = o.coverage_sd_ddof0 - o.task_cov_sd
print("cells", len(o), "dirs", o.dir.nunique())
print("max |mean - by_task|", o.d_mean.abs().max(), " max |sd(ddof1) - by_task|", o.d_sd1.abs().max(), " max |sd(ddof0) - by_task|", o.d_sd0.abs().max())
print("n_folds equal by_task:", (o.n_folds == o.task_n_folds).all())
if "slide50_wmean_cov" in o:
    print("slide>=50 n_test-weighted reconstruction: max |diff|", (o.slide50_wmean_cov - o.coverage_mean).abs().max())
o.to_csv("fcheck_conformal_cells.csv", index=False)
dup = o.groupby(["task", "arm", "scale", "design"]).size()
print("duplicated cells:", dup[dup > 1].to_dict())
o = o[o.score == "abs"]
# main design for every cell; center design = dir name ends with __center
o["D"] = np.where(o.dir.str.endswith("__center"), "center", o.design)
piv = o.pivot_table(index=["task", "arm", "scale"], columns="D", values="coverage_mean")
sd = o.pivot_table(index=["task", "arm", "scale"], columns="D", values="coverage_sd_ddof1")
nf = o.pivot_table(index=["task", "arm", "scale"], columns="D", values="n_folds")
print(piv.to_string()); print(sd.to_string()); print(nf.to_string())
p = piv.reset_index()
# (a)
p["rand_dev"] = (p["random"] - 0.90).abs()
print("(a) random within 0.01 of 0.90:", int((p.rand_dev <= 0.01).sum()), "of", len(p)); print(p[p.rand_dev > 0.01][["task", "arm", "scale", "random"]].to_string())
p["short"] = p["random"] - p["donor"]
print("(b) donor >= 0.02 below random:", int((p.short >= 0.02).sum()), "of", len(p))
print(p.sort_values("short")[["task", "arm", "scale", "random", "donor", "short"]].to_string())
mid = p[(p.short < 0.02) & (p.short > 0)]
print("   cells with 0 < short < 0.02:", len(mid), "range", mid.short.min(), mid.short.max())
neg = p[p.short <= 0]; print("   cells with donor above random:", len(neg), neg[["task", "arm", "scale", "short"]].to_string())
r10 = p[p.arm == "R10"].set_index(["task", "scale"])
oth = p[p.arm != "R10"].copy()
oth["d_vs_R10"] = [row.donor - r10.loc[(row.task, row.scale), "donor"] for row in oth.itertuples()]
print("(c) |donor(P/E) - donor(R10)| max", oth.d_vs_R10.abs().max(), "cells", len(oth)); print(oth[["task", "arm", "scale", "donor", "d_vs_R10"]].to_string())
sdd = sd.reset_index()
print("donor coverage_sd range over all 30 cells:", sdd["donor"].min(), sdd["donor"].max())
print("donor coverage_sd range over P/E 20 cells:", sdd[sdd.arm != "R10"]["donor"].min(), sdd[sdd.arm != "R10"]["donor"].max())
cc = p.dropna(subset=["center"]).copy(); cc["donor_minus_center"] = cc.donor - cc.center
print("(d) center < donor in", int((cc.donor_minus_center > 0).sum()), "of", len(cc)); print(cc[["task", "arm", "scale", "donor", "center", "donor_minus_center"]].to_string())
r = p[(p.arm == "R10") & (p.scale == "log1p")]
print("R10 log1p donor shortfall range", r.short.min(), r.short.max())
print("slide_out between donor and random (R10 log1p):"); print(r[["task", "donor", "slide_out", "random"]].to_string())
# round 3 uni_v2 rows
f3 = "/work/users/w/e/weiyang/hest_replication/results/round3/A1_coverage/a1_by_task__uni_v2__main.csv"; inputs.append(f3)
t3 = pd.read_csv(f3); t3 = t3[t3.score == "abs"]
q = t3.pivot_table(index=["task", "label_set"], columns="design", values="coverage_mean")
q["donors"] = t3[t3.design == "donor"].set_index(["task", "label_set"]).n_folds
q["shortfall"] = q["random"] - q["donor"]
print(q.to_string())
q.reset_index().to_csv("fcheck_round3_uni_v2_shortfalls.csv", index=False)
open("inputs.txt", "w").write("\n".join(sorted(set(inputs))) + "\n")
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
                v = sub.groupby(["design", "fold"]).coverage.mean().rename("v").reset_index()
                m = bf.merge(v, on=["design", "fold"], how="left")
                m = m[m.design.isin(v.design.unique())]
                pg_rows.append(dict(dir=b, scale=sc, variant=nm, folds=len(m), unmatched=int(m.v.isna().sum()), max_abs_diff=float((m.v - m.coverage).abs().max())))
P = pd.DataFrame(pg_rows); P.to_csv("fcheck_conformal_pergene_rebuild.csv", index=False)
print(P.groupby("variant").agg(units=("dir", "size"), max_abs_diff=("max_abs_diff", "max"), unmatched=("unmatched", "sum")).to_string())
open("inputs.txt", "w").write("\n".join(sorted(set(inputs))) + "\n")
