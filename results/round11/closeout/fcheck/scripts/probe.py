import json, glob, os
import pyarrow.parquet as pq
import pandas as pd
R = "/work/users/w/e/weiyang/hest_replication/results/round11/closeout"
inputs = []
def sch(p, nrows=3):
    inputs.append(p)
    f = pq.ParquetFile(p)
    names = f.schema_arrow.names
    print("==", p, "rows", f.metadata.num_rows, "ncols", len(names))
    print("cols (first 40):", names[:40])
    print("cols (last 10):", names[-10:])
    small = [c for c in names if not (c.startswith("y") or c.startswith("f_") or c.startswith("f__") or c.startswith("emb"))][:40]
    t = f.read_row_group(0, columns=small).to_pandas().head(nrows)
    with pd.option_context("display.width", 250, "display.max_columns", 60):
        print(t)
sch(f"{R}/a6/donor/kidney__Visium__P/regimeA/regimeA_cells.parquet")
sch(f"{R}/a6/donor/CCRCC__P/regimeA/regimeA_cells.parquet")
sch(f"{R}/a6/donor/kidney__Visium__P/cv/cluster_values__kidney__Visium.parquet")
sch(f"{R}/a6/donor/CCRCC__P/cv/cluster_values__CCRCC.parquet")
sch(f"{R}/a6/donor/CCRCC__P/join_log1p/b1_predictions__CCRCC__uni_v2.parquet")
sch(f"{R}/predict/kidney__Visium__P__donor/pred__kidney__Visium__uni_v2__ring1__ridgecv__donor.parquet")
sch(f"{R}/predict/kidney__Visium__P__center/pred__kidney__Visium__uni_v2__ring1__ridgecv__center.parquet")
sch(f"{R}/a6/inst/center_v1/inst_by_gene.parquet")
sch(f"{R}/a6/conformal/kidney__Visium__P__donor/pergene__P__kidney__Visium.parquet")
# full regimeA cells unique values
d = pd.read_parquet(f"{R}/a6/donor/kidney__Visium__P/regimeA/regimeA_cells.parquet")
for c in d.columns:
    if d[c].dtype == object or d[c].nunique() < 20:
        print(c, sorted(map(str, d[c].unique()))[:30])
cv = pd.read_parquet(f"{R}/a6/donor/kidney__Visium__P/cv/cluster_values__kidney__Visium.parquet")
for c in cv.columns:
    if cv[c].dtype == object or cv[c].nunique() < 30:
        print("cv", c, cv[c].nunique(), sorted(map(str, cv[c].unique()))[:10])
inst = pd.read_parquet(f"{R}/a6/inst/center_v1/inst_by_gene.parquet")
for c in inst.columns:
    if inst[c].dtype == object or inst[c].nunique() < 30:
        print("inst", c, sorted(map(str, inst[c].unique()))[:12])
ic = pd.read_csv(f"{R}/a6/inst/center_v1/inst_by_center.csv")
for c in ["task","encoder","scale","arm","alpha","center_unit"]:
    print("ibc", c, sorted(map(str, ic[c].unique())))
for p in sorted(glob.glob(f"{R}/a6/conformal/*/a1_by_task__*.csv")):
    print(p.split("/conformal/")[1])
with open("inputs.txt","w") as fh:
    fh.write("\n".join(inputs)+"\n")
