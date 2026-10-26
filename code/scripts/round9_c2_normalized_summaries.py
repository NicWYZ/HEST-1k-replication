"""Round 9 (claude-science) C2: donor-level summaries of library-size-normalized expression.

Runs on Longleaf. For each task (uni_v2 prediction file), recovers raw counts from y = log1p(count), reads each
sample's total counts per spot from its h5ad, forms y_norm = log1p(count * 1e4 / total), and writes donor x gene
means of y, y_norm and the prediction f, plus the donor mean of log total counts. Aggregates only.
Usage: python round9_c2_normalized_summaries.py <repo_root> <outdir>
"""
import sys, json, glob, numpy as np, pandas as pd, anndata as ad, scipy.sparse as sp

PQ = {"CCRCC": "results/round3/B1_ppi/b1_predictions__CCRCC__uni_v2.parquet",
      "INDIANA_KIDNEY": "results/round4/ppi/Q2_theory/predictions_INDIANA_KIDNEY/b1_predictions__INDIANA_KIDNEY__uni_v2.parquet",
      "LUNG_XENIUM": "results/round4/ppi/Q2_theory/predictions/b1_predictions__LUNG_XENIUM__uni_v2.parquet"}

def main(R, out):
    rows, checks = [], []
    for t, pq in PQ.items():
        td = [p for p in glob.glob(R + "/results/**/" + t + ".json", recursive=True)
              if "pre_P8" not in p and "paths" in json.load(open(p))][0]
        tmpl = json.load(open(td))["paths"]["adata"]
        df = pd.read_parquet(R + "/" + pq)
        genes = [c[3:] for c in df.columns if c.startswith("y__")]
        Y = df[["y__" + g for g in genes]].values.astype(float)
        cnt = np.expm1(Y)
        frac_int = np.mean(np.abs(cnt - np.round(cnt)) < 1e-3)
        lib = np.full(len(df), np.nan)
        for sid, idx in df.groupby("sample_id").indices.items():
            a = ad.read_h5ad(R + "/" + tmpl.format(sample_id=sid))
            X = a.X
            tot = np.asarray(X.sum(1)).ravel() if sp.issparse(X) else X.sum(1)
            pos = pd.Index(a.obs_names.astype(str)).get_indexer(df.barcode.iloc[idx].astype(str).values)
            lib[idx] = np.where(pos >= 0, tot[np.maximum(pos, 0)], np.nan)
        ok = np.isfinite(lib) & (lib > 0)
        checks.append(dict(task=t, frac_integer_counts=frac_int, frac_spots_with_lib=ok.mean(), n_spots=len(df)))
        Yn = np.log1p(cnt * (1e4 / lib)[:, None])
        F = df[["f__" + g for g in genes]].values.astype(float)
        d = df.donor_id.astype(str).values
        for don in sorted(set(d)):
            m = (d == don) & ok
            for j, g in enumerate(genes):
                rows.append((t, don, g, m.sum(), Y[m, j].mean(), Yn[m, j].mean(), F[m, j].mean(), np.log(lib[m]).mean()))
        print(t, checks[-1], flush=True)
    pd.DataFrame(rows, columns=["task", "donor", "gene", "n_spots", "mean_y", "mean_y_norm", "mean_f", "mean_log_lib"]).to_csv(out + "/c2_normalized_summaries.csv.gz", index=False)
    pd.DataFrame(checks).to_csv(out + "/c2_checks.csv", index=False)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
