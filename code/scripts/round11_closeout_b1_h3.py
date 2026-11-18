"""b1, H3: what predictions buy for theta3 at 8 labelled donors, and the leave-one-donor-out R^2 of the donor mean.

(1) Width ratio: from round 10's regime A gene rows (regimeA_cells.parquet, every unit), task in the five, encoder
    uni_v2, scale log1p, estimand theta3, n = 8; per gene median_width of arm fix1 (variance fpc) over that of arm
    classical (variance fpc); median over genes.
(2) R2_c: donor values computed here from the spot files. theta3 of donor d = least-squares slope of the outcome on
    m_std within d, over d's spots with morphology: slope = sum (m - mbar_d) v / sum (m - mbar_d)^2, v = y (donor
    value z_d) or v = f (donor prediction f_d); donors with >= 2 such spots and positive denominator. R2_c per gene =
    squared Pearson correlation of z_d and f_d across donors; median over genes. Spots with morphology: round 3/4
    files carry m_std, area_mean, frac_neoplastic and joined (spot kept when joined and all three finite); the corpus
    files are joined to round 10's morphology table on (sample_id, barcode), a spot has morphology when area_mean and
    frac_neoplastic are finite and n_nuclei > 0, and m_std = area_mean standardised over those spots (ddof 0). The
    slope's scale does not affect R2_c.
(3) Leave-one-donor-out R^2 of the donor mean (D12): donor means y_d, f_d over all of d's spots; for each held-out
    donor h, OLS of y on f with intercept over the other donors, residual res_h = y_h - (a + b f_h);
    R2 = 1 - sum_h res_h^2 / sum_h (y_h - mean_{d != h} y_d)^2 (leave-one-out constant); also against the full mean.
    Median over genes.
usage: b1_h3.py <out_dir>
"""
import glob, json, os, sys
import numpy as np, pandas as pd, pyarrow.parquet as pq
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b1_common as C

out = sys.argv[1]
TASKS = ["CCRCC", "INDIANA_KIDNEY", "kidney__Visium", "bowel__Visium", "LUNG_XENIUM"]
SPOT = {
    "CCRCC": (C.R + "/round3/B1_ppi/b1_predictions__CCRCC__uni_v2.parquet", None, "y__", "f__"),
    "INDIANA_KIDNEY": (C.R + "/round4/ppi/Q2_theory/predictions_INDIANA_KIDNEY/b1_predictions__INDIANA_KIDNEY__uni_v2.parquet",
                       None, "y__", "f__"),
    "LUNG_XENIUM": (C.R + "/round4/ppi/Q2_theory/predictions/b1_predictions__LUNG_XENIUM__uni_v2.parquet", None, "y__", "f__"),
    "kidney__Visium": (C.F + "/F1/predict/kidney__Visium__uni_v2/pred__kidney__Visium__uni_v2__donor.parquet",
                       C.F + "/F2/morphology/kidney__Visium/morphology__kidney__Visium.parquet", "y_log1p__", "f_log1p__"),
    "bowel__Visium": (C.F + "/F1/predict/bowel__Visium__uni_v2/pred__bowel__Visium__uni_v2__donor.parquet",
                      C.F + "/F2/morphology/bowel__Visium/morphology__bowel__Visium.parquet", "y_log1p__", "f_log1p__"),
}
res = {}
# ---------------- (1) width ratio
fr = []
for p in sorted(glob.glob(C.F + "/F2/regimeA/*/regimeA_cells.parquet")):
    u = os.path.basename(os.path.dirname(p))
    if not any(u.startswith(t + "__") for t in TASKS) or "uni_v2" not in u:
        continue
    C.note_input(p)
    x = pq.read_table(p, columns=["task", "encoder", "scale", "estimand", "gene", "n", "arm", "variance",
                                  "median_width"]).to_pandas()
    x = x[(x.encoder == "uni_v2") & (x.scale == "log1p") & (x.estimand == "theta3") & (x.n == 8)
          & (((x.arm == "fix1") & (x.variance == "fpc")) | ((x.arm == "classical") & (x.variance == "fpc")))]
    x["unit"] = u
    fr.append(x)
W = pd.concat(fr, ignore_index=True)
res["width_rows"] = len(W)
res["width_dups"] = int(W.duplicated(["task", "gene", "arm"]).sum())
Wp = W.pivot_table(index=["task", "gene"], columns="arm", values="median_width", aggfunc="first").reset_index()
Wp["wr"] = Wp["fix1"] / Wp["classical"]
Wp.to_csv(os.path.join(out, "b1_h3_width_ratio_by_gene.csv"), index=False)
res["width_ratio"] = {t: dict(genes=int(len(g)), median=float(g.wr.median())) for t, g in Wp.groupby("task")}


# ---------------- (2) and (3) from spot files
def r2c_and_lodo(task):
    p, mp, yp, fp = SPOT[task]
    C.note_input(p)
    sch = pq.read_schema(p).names
    genes = [c[len(yp):] for c in sch if c.startswith(yp)]
    base = ["donor_id"]
    if mp is None:
        base += ["m_std", "area_mean", "frac_neoplastic", "joined"]
    else:
        base += ["sample_id", "barcode"]
    df = pq.read_table(p, columns=base + [yp + g for g in genes] + [fp + g for g in genes]).to_pandas()
    if mp is None:
        jn = (df["joined"].astype(bool) & np.isfinite(df.m_std.astype(float)) & np.isfinite(df.area_mean.astype(float))
              & np.isfinite(df.frac_neoplastic.astype(float))).to_numpy()
        m = df["m_std"].to_numpy(np.float64)
        info = dict(morph="in file")
    else:
        C.note_input(mp)
        mo = pq.read_table(mp, columns=["sample_id", "barcode", "n_nuclei", "area_mean", "frac_neoplastic"]).to_pandas()
        n0 = len(df)
        df = df.merge(mo, on=["sample_id", "barcode"], how="left", validate="one_to_one")
        assert len(df) == n0
        ar = df.area_mean.to_numpy(np.float64); nf = df.frac_neoplastic.to_numpy(np.float64)
        jn = np.isfinite(ar) & np.isfinite(nf) & (df.n_nuclei.fillna(0).to_numpy() > 0)
        m = (ar - ar[jn].mean()) / ar[jn].std(ddof=0)
        info = dict(morph="joined", join_rate=float(jn.mean()))
    don = df.donor_id.astype(str).to_numpy()
    Y = df[[yp + g for g in genes]].to_numpy(np.float64); F = df[[fp + g for g in genes]].to_numpy(np.float64)
    donors = sorted(set(don.tolist()))
    z, f, ym, fm = [], [], [], []
    for d in donors:
        ix = don == d
        ym.append(Y[ix].mean(0)); fm.append(F[ix].mean(0))
        j = ix & jn
        if j.sum() >= 2:
            mc = m[j] - m[j].mean(); den = mc @ mc
            if den > 0:
                z.append(mc @ Y[j] / den); f.append(mc @ F[j] / den)
    z, f = np.array(z), np.array(f)
    r2c = np.array([np.corrcoef(z[:, k], f[:, k])[0, 1] ** 2 for k in range(len(genes))])
    ym, fm = np.array(ym), np.array(fm)
    G = len(donors)
    res_h = np.zeros_like(ym); base_loo = np.zeros_like(ym)
    for h in range(G):
        o = np.arange(G) != h
        xo, yo = fm[o], ym[o]
        xb, yb = xo.mean(0), yo.mean(0)
        b = ((xo - xb) * (yo - yb)).sum(0) / ((xo - xb) ** 2).sum(0)
        a = yb - b * xb
        res_h[h] = ym[h] - (a + b * fm[h])
        base_loo[h] = ym[h] - yb
    sse = (res_h ** 2).sum(0)
    r2_loo = 1 - sse / (base_loo ** 2).sum(0)
    r2_full = 1 - sse / ((ym - ym.mean(0)) ** 2).sum(0)
    info.update(spots=len(df), genes=len(genes), donors=G, donors_theta3=len(z), spots_with_morph=int(jn.sum()),
                median_R2c=float(np.nanmedian(r2c)), lodo_R2_loo_const_median=float(np.median(r2_loo)),
                lodo_R2_full_mean_median=float(np.median(r2_full)))
    pd.DataFrame(dict(gene=genes, R2c=r2c, R2_loo_const=r2_loo, R2_full_mean=r2_full)).to_csv(
        os.path.join(out, f"b1_h3_genes__{task}.csv"), index=False)
    return info


for t in TASKS:
    res[t] = r2c_and_lodo(t)
    print(t, json.dumps(res[t]), flush=True)
json.dump(res, open(os.path.join(out, "b1_h3_summary.json"), "w"), indent=1, default=str)
C.write_inputs(out)
print(json.dumps(res, indent=1, default=str))
