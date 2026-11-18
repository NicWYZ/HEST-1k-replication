"""b1, H1(a): ratio of the donor-clustered to the i.i.d. standard error of the spot mean, per gene, median over genes.

Definition (round10_final_runs_f2_diagnostics.py docstring, D9): for a gene with spot values y_i, i = 1..N, in
G donors, the spot mean ybar has
  i.i.d. SE      s / sqrt(N), s the sample standard deviation (ddof 1);
  clustered SE   sqrt( G/(G-1) * sum_g (sum_{i in g} (y_i - ybar))^2 ) / N   (CR1 small-sample factor G/(G-1)).
The ratio is clustered / i.i.d.; the table reports its median and 10%/90% quantiles over genes per
(task, encoder, scale). This implementation forms the donor sums with pandas groupby on the centred values and
also reports the ratio without the G/(G-1) factor (CR0). The spot files and column prefixes are the ones round 10's
config lists (only paths and prefixes are read from it).
usage: b1_h1a.py <out_dir>
"""
import json, os, sys
import numpy as np, pandas as pd, pyarrow.parquet as pq
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b1_common as C

out = sys.argv[1]
cfgp = C.note_input(C.CLONE + "/results/round10/final_runs/F2/configs/f2_diagnostics_v2.json")
cfg = json.load(open(cfgp))
rows = []
for sf in cfg["spot_files"]:
    p = sf["path"]
    if not os.path.exists(p):
        print("MISSING", p, flush=True); continue
    C.note_input(p)
    sch = pq.read_schema(p).names
    dcol = sf.get("donor_col", "donor_id")
    for sc in sf["scales"]:
        ycols = [c for c in sch if c.startswith(sc["y_prefix"])]
        need = [dcol] + ycols + (["joined"] if sf.get("joined_only") else [])
        df = pq.read_table(p, columns=need).to_pandas()
        if sf.get("joined_only"):
            df = df[df["joined"].astype(bool)]
        don = df[dcol].astype(str)
        Y = df[ycols].astype(np.float64)
        N = len(Y); G = don.nunique()
        dev = Y - Y.mean(axis=0)
        S = dev.groupby(don.to_numpy()).sum()          # G x genes donor sums of centred values
        ss = (S ** 2).sum(axis=0)
        se_cl1 = np.sqrt(G / (G - 1) * ss) / N
        se_cl0 = np.sqrt(ss) / N
        se_iid = Y.std(axis=0, ddof=1) / np.sqrt(N)
        r1 = (se_cl1 / se_iid).to_numpy(); r0 = (se_cl0 / se_iid).to_numpy()
        ok = np.isfinite(r1) & (se_iid.to_numpy() > 0)
        rows.append(dict(task=sf["task"], encoder=sf["encoder"], scale=sc["name"], n_spots=N, G=G, genes=int(ok.sum()),
                         median=float(np.median(r1[ok])), q10=float(np.quantile(r1[ok], 0.1)),
                         q90=float(np.quantile(r1[ok], 0.9)), median_cr0=float(np.median(r0[ok])), path=p))
        print(json.dumps(rows[-1]), flush=True)
        del df, Y, dev, S
R = pd.DataFrame(rows)
ref = pd.read_csv(C.note_input(C.CLONE + "/results/round10/final_runs/F2/report_tables/r10b_d9_by_task.csv"))
M = R.merge(ref, on=["task", "encoder", "scale"], how="outer", suffixes=("", "_record"), indicator=True)
M["abs_diff_median"] = (M["median"] - M["median_record"]).abs()
M.to_csv(os.path.join(out, "b1_h1a_d9_by_task.csv"), index=False)
summ = dict(rows=len(R), matched=int((M._merge == "both").sum()), max_abs_diff_median=float(M.abs_diff_median.max()),
            log1p_min=R[R.scale == "log1p"].sort_values("median").iloc[0][["task", "encoder", "median"]].to_dict(),
            log1p_max=R[R.scale == "log1p"].sort_values("median").iloc[-1][["task", "encoder", "median"]].to_dict())
json.dump(summ, open(os.path.join(out, "b1_h1a_summary.json"), "w"), indent=1, default=str)
C.write_inputs(out)
print(json.dumps(summ, indent=1, default=str))
