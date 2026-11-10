"""Round 10, track final-runs, F2.0: donor-level cluster values for the design simulations (plan, section 5.1).

For each population (task, encoder, scale) and gene, the donor's value z_g of each estimand computed from the outcome
and the same functional f_g computed from the held-out predictions:
  mu      donor mean over all of the donor's spots in the file;
  theta3  least-squares slope on m_std within the donor, over spots with morphology (`joined`);
  theta2  mean over neoplastic-dominant spots (frac_neoplastic > 0.7) minus mean over stromal-dominant (< 0.3), joined
          spots, donors with both groups only;
  theta1  within-donor correlation of area_mean with the outcome, joined spots.
Morphology estimands are formed only where the file carries m_std, area_mean and frac_neoplastic.

usage: round10_final_runs_f2_cluster_values.py <config.json> <out_dir>
Writes f2_cluster_values_summary.json first, then cluster_values__<task>.parquet, and the anchor tables
f2_anchor_c0.csv and f2_anchor_c2.csv when the config names round 9's files.
"""
import glob, json, os, sys, time
import numpy as np, pandas as pd, pyarrow as pa, pyarrow.parquet as pq

NEO_HI, STR_LO = 0.7, 0.3
SCHEMA = pa.schema([("task", pa.string()), ("encoder", pa.string()), ("scale", pa.string()),
                    ("estimand", pa.string()), ("gene", pa.string()), ("donor", pa.string()),
                    ("n_spots", pa.int64()), ("n_a", pa.int64()), ("n_b", pa.int64()),
                    ("z", pa.float64()), ("f", pa.float64())])


def donor_values(Y, F, donor, morph):
    """Y, F: spots x genes float64. donor: array of str. morph: dict of arrays or None. Yields rows."""
    out = []
    for d in sorted(set(donor.tolist())):
        ix = donor == d
        Yd, Fd = Y[ix], F[ix]
        n = int(ix.sum())
        out.append(("mu", d, n, n, 0, Yd.mean(0), Fd.mean(0)))
        if morph is None:
            continue
        j = morph["joined"][ix]
        Yj, Fj = Yd[j], Fd[j]
        nj = int(j.sum())
        m = morph["m_std"][ix][j]
        mc = m - m.mean() if nj else m
        den = float(mc @ mc) if nj else 0.0
        if nj >= 2 and den > 0:
            out.append(("theta3", d, n, nj, 0, (mc @ Yj) / den, (mc @ Fj) / den))
        neo = morph["frac_neoplastic"][ix][j]
        a, b = neo > NEO_HI, neo < STR_LO
        if a.sum() >= 1 and b.sum() >= 1:
            out.append(("theta2", d, n, int(a.sum()), int(b.sum()),
                        Yj[a].mean(0) - Yj[b].mean(0), Fj[a].mean(0) - Fj[b].mean(0)))
        ar = morph["area_mean"][ix][j]
        if nj >= 3 and ar.std() > 0:
            ac = ar - ar.mean()
            def corr(M):
                Mc = M - M.mean(0)
                sd = np.sqrt((Mc ** 2).sum(0))
                return np.where(sd > 0, (ac @ Mc) / (np.sqrt(ac @ ac) * np.where(sd > 0, sd, 1)), np.nan)
            out.append(("theta1", d, n, nj, 0, corr(Yj), corr(Fj)))
    return out


def lib_sizes(repo_root, task, samp, bc):
    """Spot totals over the full measured panel, as round9_c2_normalized_summaries.py reads them."""
    import anndata as ad, scipy.sparse as sp
    td = [p for p in glob.glob(repo_root + "/results/**/" + task + ".json", recursive=True)
          if "pre_P8" not in p and "paths" in json.load(open(p))][0]
    tmpl = json.load(open(td))["paths"]["adata"]
    lib = np.full(len(samp), np.nan)
    for sid in sorted(set(samp.tolist())):
        idx = np.flatnonzero(samp == sid)
        a = ad.read_h5ad(repo_root + "/" + tmpl.format(sample_id=sid))
        X = a.X
        tot = np.asarray(X.sum(1)).ravel() if sp.issparse(X) else X.sum(1)
        pos = pd.Index(a.obs_names.astype(str)).get_indexer(bc[idx])
        lib[idx] = np.where(pos >= 0, tot[np.maximum(pos, 0)], np.nan)
    return lib, td


def main():
    cfg = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    summ = dict(config=cfg, populations=[], started=time.strftime("%Y-%m-%dT%H:%M:%S"))
    json.dump(summ, open(os.path.join(out, "f2_cluster_values_summary.json"), "w"), indent=1)
    tables = {}
    for pop in cfg["populations"]:
        t0 = time.time()
        task, enc, path = pop["task"], pop["encoder"], pop["path"]
        df = pd.read_parquet(path)
        donor = df[pop.get("donor_col", "donor_id")].astype(str).to_numpy()
        has_m = all(c in df.columns for c in ("m_std", "area_mean", "frac_neoplastic", "joined"))
        morph = None
        if has_m and pop.get("morphology", True):
            morph = {c: df[c].to_numpy(float) for c in ("m_std", "area_mean", "frac_neoplastic")}
            morph["joined"] = df["joined"].to_numpy(bool) & np.isfinite(morph["m_std"]) & \
                np.isfinite(morph["area_mean"]) & np.isfinite(morph["frac_neoplastic"])
        for sc in pop["scales"]:
            ypre, fpre = sc["y_prefix"], sc["f_prefix"]
            genes = [c[len(ypre):] for c in df.columns if c.startswith(ypre)]
            Y = df[[ypre + g for g in genes]].to_numpy(np.float64)
            F = df[[fpre + g for g in genes]].to_numpy(np.float64)
            info = dict(task=task, encoder=enc, scale=sc["name"], path=path, n_spots=len(df), n_genes=len(genes),
                        n_donors=len(set(donor.tolist())), morphology=morph is not None)
            if sc.get("normalise_from_log1p"):
                lib, td = lib_sizes(cfg["repo_root"], pop["lib_task"], df["sample_id"].astype(str).to_numpy(),
                                    df["barcode"].astype(str).to_numpy())
                ok = np.isfinite(lib) & (lib > 0)
                info.update(task_def=td, frac_spots_with_lib=float(ok.mean()))
                Y = np.log1p(np.expm1(Y) * (1e4 / lib)[:, None])
                keep = ok
            else:
                keep = np.ones(len(df), bool)
            mk = None if morph is None else {k: v[keep] for k, v in morph.items()}
            rows = donor_values(Y[keep], F[keep], donor[keep], mk)
            recs = []
            for est, d, n, na, nb, zv, fv in rows:
                for j, g in enumerate(genes):
                    recs.append((task, enc, sc["name"], est, g, d, n, na, nb, float(zv[j]), float(fv[j])))
            tables.setdefault(task, []).extend(recs)
            info["n_rows"] = len(recs); info["seconds"] = round(time.time() - t0, 1)
            info["estimands"] = sorted({r[0] for r in rows})
            summ["populations"].append(info); print(json.dumps(info), flush=True)
            json.dump(summ, open(os.path.join(out, "f2_cluster_values_summary.json"), "w"), indent=1)
        del df
    for task, recs in tables.items():
        d = pd.DataFrame(recs, columns=SCHEMA.names)
        pq.write_table(pa.Table.from_pandas(d, schema=SCHEMA, preserve_index=False),
                       os.path.join(out, f"cluster_values__{task}.parquet"))
    # anchors
    anchors = {}
    if cfg.get("c0"):
        c0 = pd.read_csv(cfg["c0"]); rows = []
        for task, recs in tables.items():
            d = pd.DataFrame(recs, columns=SCHEMA.names)
            for est, (zc, fc) in {"mu": ("mean_y", "mean_f"), "theta3": ("slope_y_mstd", "slope_f_mstd")}.items():
                a = d[(d.estimand == est) & (d.scale == cfg["c0_scale"].get(task, "log1p"))]
                b = c0[c0.task == task].rename(columns={"gene": "gene", "donor": "donor"})
                b = b.assign(donor=b.donor.astype(str))
                m = a.merge(b, on=["encoder", "gene", "donor"], how="inner", suffixes=("", "_c0"))
                m = m[np.isfinite(m[zc])] if len(m) else m
                if not len(m):
                    continue
                rel = lambda x, y: np.abs(x - y) / np.maximum(1e-12, np.abs(y))
                rows.append(dict(task=task, estimand=est, n_matched=len(m), n_ours=len(a),
                                 n_c0=int(np.isfinite(b[zc]).sum()),
                                 max_rel_z=float(rel(m.z, m[zc]).max()), max_rel_f=float(rel(m.f, m[fc]).max()),
                                 max_abs_z=float((m.z - m[zc]).abs().max()), max_abs_f=float((m.f - m[fc]).abs().max()),
                                 n_spots_equal=bool((m.n_spots == m.n_spots_c0).all())))
        pd.DataFrame(rows).to_csv(os.path.join(out, "f2_anchor_c0.csv"), index=False); anchors["c0"] = rows
    if cfg.get("c2"):
        c2 = pd.read_csv(cfg["c2"]); rows = []
        for task, recs in tables.items():
            d = pd.DataFrame(recs, columns=SCHEMA.names)
            a = d[(d.estimand == "mu") & (d.scale == "norm_r9pair") & (d.encoder == "uni_v2")]
            if not len(a):
                continue
            b = c2[c2.task == task].assign(donor=lambda x: x.donor.astype(str))
            m = a.merge(b, on=["gene", "donor"], how="inner", suffixes=("", "_c2"))
            rows.append(dict(task=task, n_matched=len(m), n_ours=len(a), n_c2=len(b),
                             max_rel_y_norm=float((np.abs(m.z - m.mean_y_norm) / np.abs(m.mean_y_norm).clip(1e-12)).max()),
                             max_rel_f=float((np.abs(m.f - m.mean_f) / np.abs(m.mean_f).clip(1e-12)).max()),
                             n_spots_equal=bool((m.n_spots == m.n_spots_c2).all())))
        pd.DataFrame(rows).to_csv(os.path.join(out, "f2_anchor_c2.csv"), index=False); anchors["c2"] = rows
    summ["anchors"] = anchors; summ["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    json.dump(summ, open(os.path.join(out, "f2_cluster_values_summary.json"), "w"), indent=1)
    print(json.dumps(anchors, indent=1))


if __name__ == "__main__":
    main()
