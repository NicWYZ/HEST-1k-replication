#!/usr/bin/env python
"""Independent recomputation: 5 random donors straight from the raw parquet (pyarrow filter, per-row loops) and raw h5."""
import json, random, numpy as np, pandas as pd, pyarrow.parquet as pq, pyarrow.compute as pc, h5py
R = "/work/users/w/e/weiyang/hest_replication"; OUT = f"{R}/results/round4/ppi/Q5_joint"
inp = json.load(open(f"{OUT}/q5_input_md5.json"))
main = pd.read_csv(f"{OUT}/q5_cluster_table.csv"); L = pd.read_csv(f"{OUT}/q5_cluster_residuals_long.csv.gz")
# check 1: counts
exp = {"CCRCC": 24, "CCRCC_merged": 23, "INDIANA_KIDNEY": 25, "LUNG_XENIUM": 15}
for t, n in exp.items():
    for a in ["hoptimus0", "uni_v2", "resnet50"]:
        s = main[(main.task == t) & (main.arm == a)]
        pf = [k for k in inp if f"b1_predictions__{t}__{a}.parquet" in k][0]
        tot = pq.ParquetFile(pf).metadata.num_rows
        print(t, a, "rows", len(s), "expected", n, "spots", int(s.spot_count.sum()), "parquet rows", tot, "OK" if len(s) == n and int(s.spot_count.sum()) == tot else "MISMATCH")
        assert len(s) == n and int(s.spot_count.sum()) == tot
print("duplicate keys main", main.duplicated(["task", "donor", "arm"]).sum(), "long", L.duplicated(["task", "donor", "arm", "gene"]).sum())
# check 2: 5 random rows recomputed independently
random.seed(20261002)
pick = main.sample(5, random_state=7)
tdp = {"CCRCC": f"{R}/results/round3/task_defs/CCRCC.json", "CCRCC_merged": f"{R}/results/round3/task_defs/CCRCC.json"}
worst = 0
for _, r in pick.iterrows():
    pf = [k for k in inp if f"b1_predictions__{r.task}__{r.arm}.parquet" in k][0]
    tdf = [k for k in inp if k.endswith(".json") and (r.task in k or (r.task == "CCRCC_merged" and "CCRCC.json" in k))][0]
    td = json.load(open(tdf))
    t = pq.read_table(pf, filters=[("donor_id", "=", r.donor)])
    names = t.column_names; genes = [c[3:] for c in names if c.startswith("y__")]
    samp = t.column("sample_id").to_pylist(); bcs = t.column("barcode").to_pylist(); jn = t.column("joined").to_pylist()
    yy = {g: t.column(f"y__{g}").to_pylist() for g in genes}; ff = {g: t.column(f"f__{g}").to_pylist() for g in genes}
    n = len(samp); assert n == r.spot_count
    jidx = [i for i in range(n) if jn[i]]
    sub = L[(L.task == r.task) & (L.donor == r.donor) & (L.arm == r.arm)].set_index("gene")
    dm = dv = 0.0
    for g in genes:
        res = [float(np.float32(yy[g][i])) - float(np.float32(ff[g][i])) for i in jidx]
        mu = sum(res) / len(res); var = sum((x - mu) ** 2 for x in res) / (len(res) - 1)
        dm = max(dm, abs(mu - sub.loc[g, "mean_residual_joined"])); dv = max(dv, abs(var - sub.loc[g, "residual_var_joined"]) / max(var, 1e-12))
    # embedding mean from raw h5
    acc = None; cnt = 0
    for sid in sorted(set(samp)):
        with h5py.File(f"{R}/{td['paths']['embeddings'].format(encoder=r.arm, sample_id=sid)}", "r") as f:
            k = "barcodes" if "barcodes" in f else "barcode"
            b = [x.decode() if isinstance(x, (bytes, np.bytes_)) else str(x) for x in np.asarray(f[k][:]).reshape(-1)]
            X = f["embeddings"][:]
        pos = {x: i for i, x in enumerate(b)}
        for i in jidx:
            if samp[i] == sid:
                v = X[pos[bcs[i]]].astype(np.float64); acc = v if acc is None else acc + v; cnt += 1
    emb = pd.read_parquet(f"{OUT}/q5_mean_embeddings__{r.task}__{r.arm}.parquet").set_index("donor").loc[r.donor]
    de = np.abs(acc / cnt - np.array(emb.mean_embedding, dtype=np.float64)).max()
    med_ok = abs(np.median([sub.loc[g, "mean_residual_joined"] for g in genes]) - r.median_over_genes_mean_residual)
    print(f"CHECK {r.task} {r.arm} {r.donor}: n={n} joined={len(jidx)} max|dmean_resid|={dm:.2e} max rel dvar={dv:.2e} max|d mean_emb|={de:.2e} med diff={med_ok:.1e}")
    worst = max(worst, dm, dv, de)
print("worst", worst); assert worst < 1e-5
