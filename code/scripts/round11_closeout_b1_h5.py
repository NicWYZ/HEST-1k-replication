"""b1, H5: limits arms at four labelled clusters, from the gene-level cell files.

Definitions (round10_final_runs_f2_report_tables.py docstring and r02/r07 selectors in F4/paper_numbers.csv):
  a cell is one (task, encoder, scale, estimand, n, arm, variance); its value is the median over genes of the
  gene-level coverage; r07's Kluger value is the median over every cell of arm kluger_ptd, variance cluster_boot at
  n = 4 (all tasks); S6.bh.n4 and S6.bh_t.n4 are the median over the HEST and ACS cells (tasks not in the corpus) of
  arm bh (bh_t), variance own, n = 4, read from regime A's cells (paper_numbers' file is r02_regimeA_grid_ranges).
  The limits files are also searched for bh arms, in case the brief's reading (limits cell files) applies.
usage: b1_h5.py <out_dir>
"""
import glob, json, os, sys
import numpy as np, pandas as pd, pyarrow.parquet as pq
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b1_common as C

out = sys.argv[1]
CORPUS = {"kidney__Visium", "breast__Spatial_Transcriptomics", "bowel__Visium", "brain__Visium", "breast__Xenium",
          "lung__Xenium"}
COLS = ["task", "encoder", "scale", "estimand", "gene", "n", "arm", "variance", "coverage"]


def load(pattern, skip=()):
    fr, units = [], []
    for p in sorted(glob.glob(pattern)):
        u = os.path.basename(os.path.dirname(p))
        if u in skip:
            continue
        C.note_input(p)
        x = pq.read_table(p, columns=COLS).to_pandas()
        x["unit"] = u
        fr.append(x); units.append((u, len(x)))
    return pd.concat(fr, ignore_index=True), units


res = {}
# ---- limits
L, lu = load(C.F + "/F2/limits/*/limits_cells.parquet", skip=("smoke",))
res["limits_units"] = len(lu); res["limits_rows"] = len(L)
res["limits_arms"] = sorted(set(zip(L.arm, L.variance)))
key = ["task", "encoder", "scale", "estimand", "n", "arm", "variance"]
dup = L.duplicated(key + ["gene"]).sum()
res["limits_duplicate_gene_rows"] = int(dup)
Lc = L.groupby(key).agg(genes=("gene", "size"), med=("coverage", "median")).reset_index()
Lc.to_csv(os.path.join(out, "b1_h5_limits_cells.csv"), index=False)
kl = Lc[(Lc.arm == "kluger_ptd") & (Lc.variance == "cluster_boot")]
res["kluger_by_n"] = {int(n): dict(cells=int(len(g)), median=float(g.med.median()), min=float(g.med.min()),
                                   max=float(g.med.max())) for n, g in kl.groupby("n")}
bhL = Lc[Lc.arm.str.startswith("bh")]
res["limits_bh_cells_n4"] = {f"{a}|{v}": dict(cells=int(len(g)), median_HEST_ACS=float(g[~g.task.isin(CORPUS)].med.median())
                                              if (~g.task.isin(CORPUS)).any() else None)
                             for (a, v), g in bhL[bhL.n == 4].groupby(["arm", "variance"])}
del L
# ---- regime A
A, au = load(C.F + "/F2/regimeA/*/regimeA_cells.parquet")
res["regimeA_units"] = len(au); res["regimeA_rows"] = len(A)
res["regimeA_duplicate_gene_rows"] = int(A.duplicated(key + ["gene"]).sum())
sel = A[A.arm.isin(["bh", "bh_t", "bh_t_fpc"]) & (A.variance == "own")]
Ac = sel.groupby(key).agg(genes=("gene", "size"), med=("coverage", "median")).reset_index()
Ac["group"] = np.where(Ac.task.isin(CORPUS), "corpus", "HEST_ACS")
Ac.to_csv(os.path.join(out, "b1_h5_regimeA_bh_cells.csv"), index=False)
res["regimeA_bh"] = {f"{a}|{v}|n{int(n)}|{grp}": dict(cells=int(len(g)), median=float(g.med.median()),
                                                      min=float(g.med.min()), max=float(g.med.max()),
                                                      q10=float(g.med.quantile(0.1)))
                     for (a, v, n, grp), g in Ac.groupby(["arm", "variance", "n", "group"]) if int(n) in (4, 8)}
json.dump(res, open(os.path.join(out, "b1_h5_summary.json"), "w"), indent=1, default=str)
C.write_inputs(out)
print(json.dumps(res, indent=1, default=str))
