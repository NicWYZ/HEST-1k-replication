"""Round 10, track final-runs, F2.0 step 3: refit of the HEST heads on the normalised outcome (plan, section 5.1).

The head of each HEST task is refitted with the code path that made its prediction file, on the same embeddings,
folds and genes, with the outcome replaced by log(1 + 1e4 y / n), n each spot's total count recovered as round 9's
C2 did (round9_c2_normalized_summaries.py: the sum over all genes of the sample's h5ad row). The code paths are
  CCRCC, CCRCC_merged  round3_b1_ppi.py --predict <enc> --task-def <CCRCC.json> --design donor [--variant CCRCC_merged]
  INDIANA_KIDNEY       round4_ppi_q2_indiana_predict_driver.py <enc> <out> <INDIANA_KIDNEY.json>
  LUNG_XENIUM          round4_ppi_q2_lung_predict_driver.py <enc> <out> <LUNG_XENIUM labelset copy>
run unchanged: round3_b1_ppi.main is wrapped so that, when it is called, the harness's current load_task (round 3's,
or the one a round 4 driver installed) is wrapped once more. In mode as_is the wrapper passes the outcome through
(the anchor); in mode norm it replaces Y = log1p(count) by log1p(count * 1e4 / n). The round 4 drivers run through
runpy with their own argv.

usage: round10_final_runs_f2_refit_norm.py refit <task> <encoder> <mode as_is|norm> <out_dir_rel_to_ROOT> [<driver arg>]
       round10_final_runs_f2_refit_norm.py compare <task> <encoder> <committed parquet> <as_is parquet> <norm parquet>
               <cluster_values parquet> <out_dir>
compare writes refit_compare.json: as_is against the committed file (every f__ and y__ column, joined on sample_id
and barcode; the anchor passes at 1e-5 absolute on every spot and gene), and the norm file's outcome donor means
against the cluster values' norm_r9pair mu (round 9's normalised outcome, which the refit must equal).
"""
import json, os, runpy, sys, time
import numpy as np, pandas as pd

LIB = {}


def lib_sizes(ROOT, tmpl, samp, bc):
    import anndata as ad, scipy.sparse as sp
    samp = np.asarray(samp).astype(str); bc = np.asarray(bc).astype(str)
    lib = np.full(len(samp), np.nan)
    for sid in sorted(set(samp.tolist())):
        idx = np.flatnonzero(samp == sid)
        a = ad.read_h5ad(f"{ROOT}/" + tmpl.format(sample_id=sid))
        X = a.X
        tot = np.asarray(X.sum(1)).ravel() if sp.issparse(X) else np.asarray(X).sum(1)
        pos = pd.Index(a.obs_names.astype(str)).get_indexer(bc[idx])
        lib[idx] = np.where(pos >= 0, tot[np.maximum(pos, 0)], np.nan)
    return lib


def adata_template(ROOT, td, task):
    if "paths" in td and "adata" in td["paths"]:
        return td["paths"]["adata"]
    import glob
    c = [p for p in glob.glob(ROOT + "/results/**/" + task + ".json", recursive=True)
         if "pre_P8" not in p and "paths" in json.load(open(p))]
    return json.load(open(sorted(c)[0]))["paths"]["adata"]


def install(B, mode, task, info):
    H = B.H
    real_main = B.main

    def main(argv=None):
        base = H.load_task

        def load_task(td, e):
            X, Y, samp, bc, xy, genes = base(td, e)
            if mode == "norm":
                lib = lib_sizes(B.ROOT, adata_template(B.ROOT, td, task), samp, bc)
                ok = np.isfinite(lib) & (lib > 0)
                cnt = np.expm1(Y.astype(np.float64))
                info.update(n_spots=int(len(Y)), frac_spots_with_lib=float(ok.mean()),
                            frac_integer_counts=float(np.mean(np.abs(cnt - np.round(cnt)) < 1e-3)))
                if not ok.all():
                    raise SystemExit(f"{task}: {int((~ok).sum())} spots without a library size; the refit stops")
                Y = np.log1p(cnt * (1e4 / lib)[:, None]).astype(Y.dtype)
            info["load_task_calls"] = info.get("load_task_calls", 0) + 1
            return X, Y, samp, bc, xy, genes
        H.load_task = load_task
        return real_main(argv)
    B.main = main


def refit(task, enc, mode, out_rel, extra):
    import round3_b1_ppi as B
    info = dict(task=task, encoder=enc, mode=mode, out_dir=out_rel, started=time.strftime("%Y-%m-%dT%H:%M:%S"))
    install(B, mode, task, info)
    sd = os.path.dirname(os.path.abspath(B.__file__))
    if task in ("CCRCC", "CCRCC_merged"):
        argv = ["--predict", enc, "--task-def", f"{B.ROOT}/results/round3/task_defs/CCRCC.json", "--design", "donor",
                "--out-dir", out_rel] + (["--variant", "CCRCC_merged"] if task == "CCRCC_merged" else [])
        rc = B.main(argv)
    else:
        drv = {"INDIANA_KIDNEY": "round4_ppi_q2_indiana_predict_driver.py", "LUNG_XENIUM": "round4_ppi_q2_lung_predict_driver.py"}[task]
        sys.argv = [drv, enc, out_rel, extra]
        try:
            runpy.run_path(os.path.join(sd, drv), run_name="__main__"); rc = 0
        except SystemExit as e:
            rc = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    info.update(rc=rc, finished=time.strftime("%Y-%m-%dT%H:%M:%S"))
    json.dump(info, open(f"refit_info__{mode}.json", "w"), indent=1)
    print(json.dumps(info), flush=True)
    return rc or 0


def compare(task, enc, committed, as_is, norm, cvp, out):
    os.makedirs(out, exist_ok=True)
    k = ["sample_id", "barcode"]
    a, b = pd.read_parquet(committed), pd.read_parquet(as_is)
    genes = [c[3:] for c in a.columns if c.startswith("y__")]
    m = a.merge(b, on=k, how="outer", suffixes=("_c", "_r"), indicator=True)
    both = m[m._merge == "both"]
    df_ = max(float(np.nanmax(np.abs(both[f"f__{g}_c"].to_numpy(float) - both[f"f__{g}_r"].to_numpy(float)))) for g in genes)
    dy = max(float(np.nanmax(np.abs(both[f"y__{g}_c"].to_numpy(float) - both[f"y__{g}_r"].to_numpy(float)))) for g in genes)
    res = dict(task=task, encoder=enc, genes=len(genes), spots_committed=len(a), spots_as_is=len(b),
               spots_matched=len(both), only_committed=int((m._merge == "left_only").sum()),
               only_as_is=int((m._merge == "right_only").sum()), max_abs_f=df_, max_abs_y=dy,
               anchor_pass=bool(len(both) == len(a) == len(b) and df_ <= 1e-5 and dy <= 1e-5))
    n = pd.read_parquet(norm)
    res["norm_spots"] = len(n); res["norm_genes_equal"] = [c[3:] for c in n.columns if c.startswith("y__")] == genes
    cv = pd.read_parquet(cvp)
    cv = cv[(cv.task == task) & (cv.encoder == enc) & (cv.scale == "norm_r9pair") & (cv.estimand == "mu")]
    if len(cv):
        nd = n.assign(donor=n.donor_id.astype(str)).groupby("donor")[[f"y__{g}" for g in genes]].mean()
        nd.columns = genes
        z = cv.pivot(index="donor", columns="gene", values="z").loc[nd.index, genes]
        rel = np.abs(nd.to_numpy() - z.to_numpy()) / np.maximum(1e-12, np.abs(z.to_numpy()))
        res.update(norm_vs_r9_donors=int(nd.shape[0]), norm_vs_r9_max_rel=float(np.nanmax(rel)),
                   norm_vs_r9_max_abs=float(np.nanmax(np.abs(nd.to_numpy() - z.to_numpy()))))
    fa = n[[f"f__{g}" for g in genes]].to_numpy(float); ya = n[[f"y__{g}" for g in genes]].to_numpy(float)
    res["norm_pearson_median"] = float(np.nanmedian([np.corrcoef(fa[:, j], ya[:, j])[0, 1] for j in range(len(genes))]))
    json.dump(res, open(os.path.join(out, "refit_compare.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))
    return 0 if res["anchor_pass"] else 2


if __name__ == "__main__":
    if sys.argv[1] == "refit":
        sys.exit(refit(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6] if len(sys.argv) > 6 else ""))
    sys.exit(compare(*sys.argv[2:9]))
