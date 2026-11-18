"""b1, H2: kidney Visium prediction across donors and centers, and HCP coverage by held-out center.

Pearson: per gene, Pearson correlation of y_log1p and f_log1p over all spots of the file, median over genes
(F1's formula as round 10's institution docstring states it), for the donor- and center-design files of
uni_v2, hoptimus0, resnet50.
HCP (Lee, Barber and Willett's hierarchical conformal, as round 10's F3 institution docstring defines its two arms),
on the uni_v2 center-design file, log1p, alpha 0.2 (nominal 0.80) and 0.25:
  for each held-out center u (unit = the file's fold column, checked against center_id), the calibration spots are
  all spots of the other centers, with residual score |y - f|. Calibration groups are the other centers
  (hcp_center) or the donors of the other centers (hcp_donor); with K groups, each spot of group g carries weight
  1/((K+1) N_g) and an atom of mass 1/(K+1) sits at +inf. The threshold q is the (1 - alpha) quantile of that
  distribution, q = inf{t : F(t) >= 1 - alpha}. Coverage of center u for a gene = share of u's spots with
  |y - f| <= q; per center the median over genes, then the median over the centers.
Three readings of the quantile at an exact tie are computed and reported:
  exact_lower  F(t) >= beta with beta * (1 - 1e-12) (round 10's QTOL reading, resolves a tie downward);
  exact_upper  F(t) >= beta * (1 + 1e-12) (resolves an exact tie upward; the released GHCP code's reading);
  rational     F evaluated exactly with integer arithmetic over the common denominator, then F(t) >= beta with
               beta = 1 - alpha given as a fraction (4/5, 3/4): an exact tie counts as reaching beta.
usage: b1_h2.py <out_dir>
"""
import json, os, sys
from fractions import Fraction
from math import lcm
import numpy as np, pandas as pd, pyarrow.parquet as pq
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b1_common as C

out = sys.argv[1]
P = C.F + "/F1/predict/kidney__Visium__{e}/pred__kidney__Visium__{e}__{d}.parquet"
res = {"pearson": {}}
prow = []
for e in ("uni_v2", "hoptimus0", "resnet50"):
    for d in ("donor", "center"):
        p = C.note_input(P.format(e=e, d=d))
        sch = pq.read_schema(p).names
        genes = [c[len("y_log1p__"):] for c in sch if c.startswith("y_log1p__")]
        df = pq.read_table(p, columns=[f"y_log1p__{g}" for g in genes] + [f"f_log1p__{g}" for g in genes]).to_pandas()
        r = []
        for g in genes:
            y = df[f"y_log1p__{g}"].to_numpy(np.float64); f = df[f"f_log1p__{g}"].to_numpy(np.float64)
            yc, fc = y - y.mean(), f - f.mean()
            den = np.sqrt((yc @ yc) * (fc @ fc))
            r.append(float(yc @ fc / den) if den > 0 else np.nan)
        r = np.array(r)
        res["pearson"][f"{e}|{d}"] = dict(spots=len(df), genes=len(genes), median=float(np.nanmedian(r)))
        prow += [dict(encoder=e, design=d, gene=g, pearson=v) for g, v in zip(genes, r)]
pd.DataFrame(prow).to_csv(os.path.join(out, "b1_h2_pearson_by_gene.csv"), index=False)

# ---------------- HCP
p = P.format(e="uni_v2", d="center")
sch = pq.read_schema(p).names
genes = [c[len("y_log1p__"):] for c in sch if c.startswith("y_log1p__")]
df = pq.read_table(p, columns=["fold", "center_id", "donor_id"] + [f"y_log1p__{g}" for g in genes]
                   + [f"f_log1p__{g}" for g in genes]).to_pandas()
fold = df["fold"].astype(str).to_numpy(); cen = df["center_id"].astype(str).to_numpy()
don = df["donor_id"].astype(str).to_numpy()
pairs = sorted(set(zip(fold, cen)))
res["fold_center_pairs"] = pairs
Y = df[[f"y_log1p__{g}" for g in genes]].to_numpy(np.float64)
Fp = df[[f"f_log1p__{g}" for g in genes]].to_numpy(np.float64)
S = np.abs(Y - Fp)
units = sorted(set(fold.tolist()))
res["units"] = {u: dict(spots=int((fold == u).sum()), donors=len(set(don[fold == u]))) for u in units}
res["donors_in_two_units"] = int(sum(len({u for u, dd in zip(fold, don) if dd == x}) > 1 for x in set(don.tolist())))


def hcp_threshold(s_cal, grp, beta_frac):
    """Returns dict reading -> (q per gene). s_cal (n, G), grp (n,) labels, beta_frac a Fraction."""
    names, inv, cnt = np.unique(grp, return_inverse=True, return_counts=True)
    K = len(names)
    beta = float(beta_frac)
    # integer weights over the common denominator D = (K+1) * lcm(N_g): spot of g has D/((K+1)N_g) = L/N_g
    L = 1
    for c in cnt:
        L = lcm(L, int(c))
    wi = np.array([L // int(c) for c in cnt], dtype=object)[inv]      # exact integer weights (python ints)
    tot_int = L * (K + 1)                                               # all mass incl. the inf atom (L)
    wf = 1.0 / ((K + 1) * cnt[inv].astype(np.float64))
    q = {k: np.full(s_cal.shape[1], np.inf) for k in ("exact_lower", "exact_upper", "rational")}
    target_int = beta_frac * tot_int                                    # Fraction
    for j in range(s_cal.shape[1]):
        o = np.argsort(s_cal[:, j], kind="mergesort")
        ss = s_cal[o, j]
        cw = np.cumsum(wf[o])
        i1 = int(np.searchsorted(cw, beta * (1 - 1e-12), side="left"))
        i2 = int(np.searchsorted(cw, beta * (1 + 1e-12), side="left"))
        if i1 < len(ss): q["exact_lower"][j] = ss[i1]
        if i2 < len(ss): q["exact_upper"][j] = ss[i2]
        # rational: cumulative integer weight; find first index with cum >= target
        wo = wi[o]
        # python-int cumsum in chunks (object array cumsum is exact)
        ci = np.cumsum(wo)
        idx = None
        # binary search over the exact cumulative weights
        lo, hi = 0, len(ci)
        while lo < hi:
            mid = (lo + hi) // 2
            if Fraction(int(ci[mid])) >= target_int:
                hi = mid
            else:
                lo = mid + 1
        if lo < len(ss): q["rational"][j] = ss[lo]
    return q, K


rows, gene_rows = [], []
for alpha, beta_frac in ((0.2, Fraction(4, 5)), (0.25, Fraction(3, 4))):
    for arm in ("hcp_center", "hcp_donor"):
        for u in units:
            E = fold == u; Cm = ~E
            grp = fold[Cm] if arm == "hcp_center" else don[Cm]
            q, K = hcp_threshold(S[Cm], grp, beta_frac)
            for reading, qq in q.items():
                cov = (S[E] <= qq[None, :]).mean(axis=0)
                rows.append(dict(alpha=alpha, arm=arm, center=u, K=K, reading=reading, n_spots=int(E.sum()),
                                 n_cal=int(Cm.sum()), coverage_median_gene=float(np.median(cov)),
                                 finite_share=float(np.isfinite(qq).mean()),
                                 width_median_gene=float(np.median(2 * qq))))
                gene_rows += [dict(alpha=alpha, arm=arm, center=u, reading=reading, gene=g, q=float(a), coverage=float(c))
                              for g, a, c in zip(genes, qq, cov)]
            print(json.dumps(rows[-1]), flush=True)
B = pd.DataFrame(rows)
B.to_csv(os.path.join(out, "b1_h2_hcp_by_center.csv"), index=False)
pd.DataFrame(gene_rows).to_csv(os.path.join(out, "b1_h2_hcp_by_gene.csv.gz"), index=False)
res["hcp_median_over_centers"] = {f"{a}|{arm}|{rd}": float(g.coverage_median_gene.median())
                                  for (a, arm, rd), g in B.groupby(["alpha", "arm", "reading"])}
res["hcp_S0006"] = {f"{a}|{arm}|{rd}": float(g[g.center == "S0006"].coverage_median_gene.iloc[0])
                    for (a, arm, rd), g in B.groupby(["alpha", "arm", "reading"]) if (g.center == "S0006").any()}
json.dump(res, open(os.path.join(out, "b1_h2_summary.json"), "w"), indent=1, default=str)
C.write_inputs(out)
print(json.dumps(res, indent=1, default=str))
