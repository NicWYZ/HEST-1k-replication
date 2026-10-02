#!/usr/bin/env python
"""Round 4 PPI Q5: per-donor cluster table (descriptive only). Reads Q2 B1 donor-mode prediction parquets."""
import os, sys, json, hashlib, time, glob
import numpy as np, pandas as pd, h5py, pyarrow as pa, pyarrow.parquet as pq
R = "/work/users/w/e/weiyang/hest_replication"
Q2 = f"{R}/results/round4/ppi/Q2_theory"
OUT = f"{R}/results/round4/ppi/Q5_joint"
os.makedirs(OUT, exist_ok=True)
ENCS = ["hoptimus0", "uni_v2", "resnet50"]
def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""): h.update(b)
    return h.hexdigest()
TASKS = {
 "CCRCC": dict(pq=lambda e: f"{R}/results/round3/B1_ppi/b1_predictions__CCRCC__{e}.parquet", td=lambda e: f"{R}/results/round3/task_defs/CCRCC.json", genes="td"),
 "CCRCC_merged": dict(pq=lambda e: f"{R}/results/round3/B1_ppi/b1_predictions__CCRCC_merged__{e}.parquet", td=lambda e: f"{R}/results/round3/task_defs/CCRCC.json", genes="td"),
 "INDIANA_KIDNEY": dict(pq=lambda e: f"{Q2}/predictions_INDIANA_KIDNEY/b1_predictions__INDIANA_KIDNEY__{e}.parquet", td=lambda e: f"{Q2}/recalibration/INDIANA_KIDNEY/INDIANA_KIDNEY__q2_50genes.json", genes="td"),
 "LUNG_XENIUM": dict(pq=lambda e: f"{Q2}/predictions/b1_predictions__LUNG_XENIUM__{e}.parquet", td=lambda e: f"{Q2}/predictions/LUNG_XENIUM__labelset__{e}.json", genes="td"),
}
EXPECT_DONORS = {"CCRCC": 24, "CCRCC_merged": 23, "INDIANA_KIDNEY": 25, "LUNG_XENIUM": 15}
# Q2 recalibration (leave-one-donor-out offset prediction), hoptimus0 only
RECAL = {("CCRCC", "hoptimus0"): f"{Q2}/recalibration/CCRCC/q2_recal_donor_offsets__CCRCC.csv",
         ("INDIANA_KIDNEY", "hoptimus0"): f"{Q2}/recalibration/INDIANA_KIDNEY/q2_recal_donor_offsets__INDIANA_KIDNEY.csv"}
main_rows, long_parts, log, inputs_md5 = [], [], [], {}
t0 = time.time()
for task, cfg in TASKS.items():
    for enc in ENCS:
        pp = cfg["pq"](enc); tdp = cfg["td"](enc)
        inputs_md5[pp] = md5(pp); inputs_md5[tdp] = md5(tdp)
        td = json.load(open(tdp))
        df = pd.read_parquet(pp)
        genes = [c[3:] for c in df.columns if c.startswith("y__")]
        assert genes == [c[3:] for c in df.columns if c.startswith("f__")]
        assert genes == list(td["target_genes"]["list"]), f"{task} {enc} gene list differs from task def"
        Y = df[[f"y__{g}" for g in genes]].to_numpy(np.float64); F = df[[f"f__{g}" for g in genes]].to_numpy(np.float64)
        Res = Y - F
        joined = df["joined"].to_numpy(bool)
        donor = df["donor_id"].astype(str).to_numpy()
        donors = sorted(set(donor)); assert len(donors) == EXPECT_DONORS[task], (task, len(donors))
        # embeddings: load per sample, align on barcode
        tpl = td["paths"]["embeddings"]
        samples = sorted(set(df["sample_id"]))
        dim = None; E = None
        key = pd.Series(np.arange(len(df)), index=pd.MultiIndex.from_arrays([df["sample_id"].astype(str), df["barcode"].astype(str)]))
        assert key.index.is_unique
        got = np.zeros(len(df), bool)
        for sid in samples:
            ep = f"{R}/{tpl.format(encoder=enc, sample_id=sid)}"
            with h5py.File(ep, "r") as f:
                k = "barcodes" if "barcodes" in f else "barcode"
                bc = [x.decode() if isinstance(x, (bytes, np.bytes_)) else str(x) for x in np.asarray(f[k][:]).reshape(-1)]
                X = np.asarray(f["embeddings"][:], dtype=np.float32)
            if E is None:
                dim = X.shape[1]; E = np.zeros((len(df), dim), np.float32)
            idx = key.reindex(pd.MultiIndex.from_arrays([[sid] * len(bc), bc])).to_numpy()
            ok = ~np.isnan(idx); idx = idx[ok].astype(int)
            E[idx] = X[ok]; got[idx] = True
        assert got.all(), f"{task} {enc}: {(~got).sum()} parquet spots without embedding"
        recal = None
        if (task, enc) in RECAL:
            inputs_md5[RECAL[(task, enc)]] = md5(RECAL[(task, enc)])
            recal = pd.read_csv(RECAL[(task, enc)], index_col=0)
            recal.index = recal.index.astype(str)
        emb_rows = []
        for d in donors:
            m_all = donor == d; m_j = m_all & joined
            nA, nJ = int(m_all.sum()), int(m_j.sum())
            mrJ = Res[m_j].mean(0); mrA = Res[m_all].mean(0)
            vJ = Res[m_j].var(0, ddof=1) if nJ > 1 else np.full(len(genes), np.nan)
            vA = Res[m_all].var(0, ddof=1) if nA > 1 else np.full(len(genes), np.nan)
            eJ = E[m_j].astype(np.float64).mean(0); eA = E[m_all].astype(np.float64).mean(0)
            emb_rows.append(dict(donor=d, n_spots=nA, n_joined=nJ, mean_embedding=eJ.astype(np.float32).tolist(), mean_embedding_all_spots=eA.astype(np.float32).tolist()))
            bhat = np.full(len(genes), np.nan); bq2 = np.full(len(genes), np.nan)
            if recal is not None:
                assert [c[6:] for c in recal.columns if c.startswith("bhat__")] == genes
                bhat = recal.loc[d, [f"bhat__{g}" for g in genes]].to_numpy(float)
                bq2 = recal.loc[d, [f"b__{g}" for g in genes]].to_numpy(float)
                log.append(f"{task} {enc} {d}: max|mean_resid_joined - Q2 b| = {np.abs(mrJ - bq2).max():.3e}")
            long_parts.append(pd.DataFrame(dict(task=task, donor=d, arm=enc, gene=genes, n_spots=nA, n_joined=nJ,
                mean_residual_joined=mrJ, residual_var_joined=vJ, mean_residual_all_spots=mrA, residual_var_all_spots=vA,
                loo_offset_pred=bhat, q2_offset_b_joined=bq2)))
            main_rows.append(dict(task=task, donor=d, arm=enc, spot_count=nA, n_joined_spots=nJ,
                mean_embedding_parquet=f"results/round4/ppi/Q5_joint/q5_mean_embeddings__{task}__{enc}.parquet", mean_embedding_row_key=d, embedding_dim=dim,
                n_genes=len(genes), median_over_genes_mean_residual=float(np.median(mrJ)),
                median_over_genes_within_donor_residual_var=float(np.nanmedian(vJ)) if nJ > 1 else np.nan,
                median_over_genes_mean_residual_all_spots=float(np.median(mrA)),
                median_over_genes_within_donor_residual_var_all_spots=float(np.nanmedian(vA)) if nA > 1 else np.nan,
                loo_offset_pred_median_over_genes=float(np.median(bhat)) if recal is not None else np.nan))
        edf = pd.DataFrame(emb_rows)
        pq.write_table(pa.Table.from_pandas(edf, preserve_index=False), f"{OUT}/q5_mean_embeddings__{task}__{enc}.parquet", compression="snappy")
        print(f"[{task} {enc}] spots {len(df)} joined {int(joined.sum())} donors {len(donors)} genes {len(genes)} dim {dim} {time.time()-t0:.0f}s", flush=True)
        del E, df, Y, F, Res
main = pd.DataFrame(main_rows)
assert not main.duplicated(["task", "donor", "arm"]).any()
main.to_csv(f"{OUT}/q5_cluster_table.csv", index=False)
L = pd.concat(long_parts, ignore_index=True)
assert not L.duplicated(["task", "donor", "arm", "gene"]).any()
L.to_csv(f"{OUT}/q5_cluster_residuals_long.csv.gz", index=False, compression="gzip")
open(f"{OUT}/q5_q2_b_vs_residual_check.txt", "w").write("\n".join(log) + "\n")
json.dump(inputs_md5, open(f"{OUT}/q5_input_md5.json", "w"), indent=1)
print("rows", len(main), "long rows", len(L))
