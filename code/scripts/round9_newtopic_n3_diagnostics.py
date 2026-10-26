"""Round 9, track newtopic, step N3: data-first diagnostics of the per-spot prediction files.

Runs on Longleaf. For each task and slide (sample), with the leave-donor-out predictions of three encoders:
  D1  within-slide correlation of prediction with label (per encoder) and of predictions between encoders;
  D2  Moran's I on a six-nearest-neighbour graph of the label, the uni_v2 prediction and its residual;
  D3  PC1 share of the gene-by-gene correlation matrix of uni_v2 residuals (and of labels), and the
      correlation of the PC1 score with log total counts (from the h5ad) and log panel depth.
Writes aggregates only (per task x sample x gene, and per task x sample). Predictions written before the
run are in results/round9/newtopic/n3_predictions_before_run.md.
Usage: python round9_newtopic_n3_diagnostics.py <repo_root> <outdir>
"""
import sys, json, glob, itertools, numpy as np, pandas as pd, anndata as ad, scipy.sparse as sp
from scipy.spatial import cKDTree

ENC = ["hoptimus0", "resnet50", "uni_v2"]
PQDIR = {"CCRCC": "results/round3/B1_ppi", "IDC": "results/round3/B1_ppi", "LYMPH_IDC": "results/round3/B1_ppi",
         "PRAD": "results/round3/B1_ppi",
         "INDIANA_KIDNEY": "results/round4/ppi/Q2_theory/predictions_INDIANA_KIDNEY",
         "LUNG_XENIUM": "results/round4/ppi/Q2_theory/predictions"}
K_NN = 6


def corr(a, b):
    a = a - a.mean(); b = b - b.mean()
    d = np.sqrt((a * a).sum() * (b * b).sum())
    return np.nan if d == 0 else float((a * b).sum() / d)


def moran(x, nbr):
    """Moran's I with row-standardised k-NN weights; nbr is an (n, k) index array."""
    z = x - x.mean()
    den = (z * z).sum()
    if den == 0:
        return np.nan
    lag = z[nbr].mean(1)
    return float(len(z) * (z * lag).sum() / (len(z) * den))  # weights sum to n, so I = sum z*lag / sum z^2


def pc1(M):
    M = M[:, M.std(0) > 0]
    Z = (M - M.mean(0)) / M.std(0)
    U, S, Vt = np.linalg.svd(Z, full_matrices=False)
    return float(S[0] ** 2 / (S ** 2).sum()), U[:, 0] * S[0]


def main(R, out):
    gene_rows, slide_rows, checks = [], [], []
    for t, pqd in PQDIR.items():
        tds = [p for p in glob.glob(R + "/results/**/" + t + ".json", recursive=True)
               if "pre_P8" not in p and "paths" in json.load(open(p))]
        tmpl = json.load(open(tds[0]))["paths"]["adata"]
        dfs = {}
        for e in ENC:
            f = f"{R}/{pqd}/b1_predictions__{t}__{e}.parquet"
            dfs[e] = pd.read_parquet(f).set_index(["sample_id", "barcode"])
        base = dfs["uni_v2"]
        genes = [c[3:] for c in base.columns if c.startswith("y__")]
        for e in ENC:
            dfs[e] = dfs[e].reindex(base.index)
            ydiff = np.nanmax(np.abs(dfs[e][["y__" + g for g in genes]].values - base[["y__" + g for g in genes]].values))
            checks.append(dict(task=t, encoder=e, n_spots=len(base), n_missing=int(dfs[e]["f__" + genes[0]].isna().sum()),
                               max_abs_label_diff_vs_uni=float(ydiff), task_def=tds[0].replace(R + "/", "")))
        for sid in sorted(set(base.index.get_level_values(0))):
            m = base.index.get_level_values(0) == sid
            bcs = base.index.get_level_values(1)[m].astype(str)
            a = ad.read_h5ad(R + "/" + tmpl.format(sample_id=sid))
            pos = pd.Index(a.obs_names.astype(str)).get_indexer(bcs)
            if (pos < 0).any() or "spatial" not in a.obsm:
                checks.append(dict(task=t, encoder="coords", sample=sid, n_unmatched=int((pos < 0).sum()),
                                   has_spatial="spatial" in a.obsm))
                continue
            xy = np.asarray(a.obsm["spatial"])[pos].astype(float)
            X = a.X
            tot = (np.asarray(X.sum(1)).ravel() if sp.issparse(X) else np.asarray(X).sum(1))[pos]
            Y = base.loc[m, ["y__" + g for g in genes]].values.astype(float)
            Fs = {e: dfs[e].loc[m, ["f__" + g for g in genes]].values.astype(float) for e in ENC}
            ok = np.isfinite(Y).all(1) & np.all([np.isfinite(Fs[e]).all(1) for e in ENC], axis=0) & (tot > 0)
            Y = Y[ok]; Fs = {e: v[ok] for e, v in Fs.items()}; xy = xy[ok]; tot = tot[ok]
            n = len(Y)
            if n < 30:
                continue
            nbr = cKDTree(xy).query(xy, k=K_NN + 1)[1][:, 1:]
            donor = str(base.loc[m, "donor_id"].iloc[0])
            res = Y - Fs["uni_v2"]
            panel = np.log(np.expm1(Y).sum(1) + 1.0)
            loglib = np.log(tot)
            for j, g in enumerate(genes):
                row = dict(task=t, sample=sid, donor=donor, gene=g, n=n, sd_y=float(Y[:, j].std()))
                for e in ENC:
                    row[f"r_fy__{e}"] = corr(Fs[e][:, j], Y[:, j])
                for e1, e2 in itertools.combinations(ENC, 2):
                    row[f"r_ff__{e1}__{e2}"] = corr(Fs[e1][:, j], Fs[e2][:, j])
                row["moran_y"] = moran(Y[:, j], nbr)
                row["moran_f_uni"] = moran(Fs["uni_v2"][:, j], nbr)
                row["moran_res_uni"] = moran(res[:, j], nbr)
                gene_rows.append(row)
            s_res, sc_res = pc1(res)
            s_y, sc_y = pc1(Y)
            slide_rows.append(dict(task=t, sample=sid, donor=donor, n=n, n_genes=len(genes),
                                   pc1_share_res=s_res, abs_r_pc1res_loglib=abs(corr(sc_res, loglib)),
                                   abs_r_pc1res_panel=abs(corr(sc_res, panel)),
                                   pc1_share_y=s_y, abs_r_pc1y_loglib=abs(corr(sc_y, loglib)),
                                   abs_r_pc1y_panel=abs(corr(sc_y, panel)),
                                   r_loglib_panel=corr(loglib, panel)))
        print(t, "done", flush=True)
    pd.DataFrame(gene_rows).to_csv(out + "/n3_gene_slide.csv.gz", index=False)
    pd.DataFrame(slide_rows).to_csv(out + "/n3_slide.csv", index=False)
    pd.DataFrame(checks).to_csv(out + "/n3_checks.csv", index=False)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
