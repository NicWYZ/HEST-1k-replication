#!/usr/bin/env python
"""Round 7 federated learning track, V3: the cost of spot-level differential privacy
(plan amendment A8), on V2(b) for CCRCC with uni_v2.

Clip norms C_x and C_y are the 95th percentiles of the embedding norms and of the expression-vector
norms over the training spots of the first center of the first partition, fixed before any noise is
drawn. In the private arms every spot is clipped to these norms before its center's sums are formed.
Each center releases once n, sum x, sum y, the upper triangle of sum x x^T and sum x y^T, with
independent Gaussian noise of standard deviation sigma(eps, delta, Delta) from the analytic Gaussian
mechanism (Balle and Wang 2018), Delta = sqrt(1 + C_x^2 + C_y^2 + C_x^4 + C_x^2 C_y^2). The ridge
penalty becomes lambda + 2 sigma_tot sqrt(256) / s^2, sigma_tot = sigma sqrt(number of centers) and
s the median pooled standard deviation of the noisy sums. A failed Cholesky factorisation is
recorded, not repaired. Scored on the held-out donors within centers, as V2's within scheme.

Writes into its working directory (results/round7/fedlearn/V3/): v3_calibration.json,
v3_summary.csv and v3_paired.csv first, then v3_rows.csv, PROVENANCE.txt and _provenance.json.
"""
import argparse
import json
import os
import sys
import time

import numpy as np
import pandas as pd
from scipy.stats import norm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import round7_fedlearn_common as C  # noqa: E402
import round7_fedlearn_design as D  # noqa: E402
import round7_fedlearn_head as H  # noqa: E402
import round7_fedlearn_v2 as V2  # noqa: E402

TASK, ENC = "CCRCC", "uni_v2"
EPS = (0.5, 1.0, 2.0, 5.0, 10.0)
DELTA = 1e-5
N_NOISE = 20
CLIP_PCT = 95.0


def agm_delta(sigma, eps, sens):
    """delta achieved by Gaussian noise sigma at (eps, sens), Balle and Wang (2018) Theorem 8."""
    a = sens / (2 * sigma)
    b = eps * sigma / sens
    return norm.cdf(a - b) - np.exp(eps + norm.logcdf(-a - b))


def agm_sigma(eps, delta, sens, tol=1e-12):
    lo, hi = 1e-6 * sens, 1.0 * sens
    while agm_delta(hi, eps, sens) > delta:
        hi *= 2
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if agm_delta(mid, eps, sens) > delta:
            lo = mid
        else:
            hi = mid
        if hi - lo < tol * hi:
            break
    return hi


def clip_rows(A, c):
    n = np.linalg.norm(A, axis=1, keepdims=True)
    return A * np.minimum(1.0, c / np.maximum(n, 1e-300))


def noisy(st, sigma, rng):
    p = st.Sxx.shape[0]
    E = rng.normal(0.0, sigma, size=(p, p))
    U = np.triu(E)
    Sym = U + np.triu(U, 1).T
    return H.Stats(st.n + rng.normal(0.0, sigma), st.sx + rng.normal(0.0, sigma, st.sx.shape),
                   st.sy + rng.normal(0.0, sigma, st.sy.shape), st.Sxx + Sym,
                   st.Sxy + rng.normal(0.0, sigma, st.Sxy.shape))


def fit_private(tot, sigma_tot):
    mx, sd, V, Cz = H.basis_from(tot)
    s = float(np.median(sd))
    lam = H._lam(len(tot.sy), V.shape[1]) + 2.0 * sigma_tot * np.sqrt(V.shape[1]) / s ** 2
    N = tot.n
    my = tot.sy / N
    Czy = (tot.Sxy - N * np.outer(mx, my)) / sd[:, None]
    A = V.T @ Cz @ V + lam * np.eye(V.shape[1])
    B = H._solve(A, V.T @ Czy)
    return H.Head(mx, sd, V, B, my, "private"), lam, s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame-id", required=True)
    ap.add_argument("--clone", default=C.CLONE)
    a = ap.parse_args()
    out = os.getcwd()
    C.stamp_dir(out, a.frame_id, note="round 7 fedlearn V3 differential privacy")
    t0 = time.time()
    td = H.load_td(a.clone, D.TASKS[TASK])
    sids = D.task_samples(td)
    des = V2.designs(TASK, td, sids)
    genes = list(td["target_genes"]["list"])
    data = H.load_samples(td, sids, ENC, genes)
    # clip norms from the first center of the first partition, training spots only
    c0 = sorted(des[0]["train"])[0]
    X0 = np.vstack([data[s][0] for s in des[0]["train"][c0]]).astype(np.float64)
    Y0 = np.vstack([data[s][1] for s in des[0]["train"][c0]]).astype(np.float64)
    Cx = float(np.percentile(np.linalg.norm(X0, axis=1), CLIP_PCT))
    Cy = float(np.percentile(np.linalg.norm(Y0, axis=1), CLIP_PCT))
    sens = float(np.sqrt(1 + Cx ** 2 + Cy ** 2 + Cx ** 4 + Cx ** 2 * Cy ** 2))
    sig = {e: agm_sigma(e, DELTA, sens) for e in EPS}
    calib = dict(task=TASK, encoder=ENC, clip_center=f"partition 0, {c0}", clip_pct=CLIP_PCT,
                 n_clip_spots=len(X0), C_x=Cx, C_y=Cy, Delta=sens, delta=DELTA,
                 sigma={str(e): sig[e] for e in EPS},
                 achieved_delta={str(e): float(agm_delta(sig[e], e, sens)) for e in EPS})
    json.dump(calib, open("v3_calibration.json", "w"), indent=2)
    clipped = {s: H.Stats.of(clip_rows(data[s][0].astype(np.float64), Cx),
                             clip_rows(data[s][1].astype(np.float64), Cy)) for s in sids}
    raw = {s: H.Stats.of(data[s][0], data[s][1]) for s in sids}
    rows = []
    for d in des:
        centers = sorted(d["train"])
        tests = {c: (np.vstack([data[s][0] for s in d["held"][c]]), np.vstack([data[s][1] for s in d["held"][c]]),
                     np.concatenate([[s] * len(data[s][0]) for s in d["held"][c]])) for c in centers}
        st_raw = {c: H.total([raw[s] for s in d["train"][c]]) for c in centers}
        st_clip = {c: H.total([clipped[s] for s in d["train"][c]]) for c in centers}

        def score_head(h):
            sc = [V2.score(tests[c][1], h.predict(tests[c][0]), tests[c][2]) for c in centers]
            return {m: float(np.mean([x[m] for x in sc])) for m in ("within_slide", "pooled_pearson")}
        base = dict(task=TASK, encoder=ENC, partition=d["draw"])
        rows.append({**base, "arm": "nonprivate_unclipped", "eps": np.nan, "noise_draw": -1, "failed": False,
                     "lam": H._lam(len(genes)), **score_head(H.fit_exact(H.total(list(st_raw.values()))))})
        rows.append({**base, "arm": "nonprivate_clipped", "eps": np.nan, "noise_draw": -1, "failed": False,
                     "lam": H._lam(len(genes)), **score_head(H.fit_exact(H.total(list(st_clip.values()))))})
        for e in EPS:
            for r in range(N_NOISE):
                rel = [noisy(st_clip[c], sig[e], H.rng_for("V3-noise", d["draw"], e, r, c)) for c in centers]
                try:
                    h, lam, s = fit_private(H.total(rel), sig[e] * np.sqrt(len(centers)))
                    res, failed = score_head(h), False
                except np.linalg.LinAlgError:
                    res, failed, lam, s = dict(within_slide=np.nan, pooled_pearson=np.nan), True, np.nan, np.nan
                rows.append({**base, "arm": "private", "eps": e, "noise_draw": r, "failed": failed,
                             "lam": lam, "s_median_sd": s, **res})
        print("partition", d["draw"], "done", round(time.time() - t0), flush=True)
    R = pd.DataFrame(rows)
    priv = R[R.arm == "private"]
    per_part = priv.groupby(["partition", "eps"])[["within_slide", "pooled_pearson"]].mean().reset_index()
    S = (priv.groupby("eps").agg(n_rows=("noise_draw", "size"), n_failed=("failed", "sum"),
                                 within_slide_mean=("within_slide", "mean"), within_slide_sd=("within_slide", "std"),
                                 pooled_pearson_mean=("pooled_pearson", "mean"),
                                 pooled_pearson_sd=("pooled_pearson", "std"), lam_median=("lam", "median"))
         .reset_index())
    for arm in ("nonprivate_unclipped", "nonprivate_clipped"):
        g = R[R.arm == arm]
        S = pd.concat([S, pd.DataFrame([dict(eps=np.nan, arm=arm, n_rows=len(g), n_failed=0,
                                             within_slide_mean=g.within_slide.mean(), within_slide_sd=g.within_slide.std(),
                                             pooled_pearson_mean=g.pooled_pearson.mean(),
                                             pooled_pearson_sd=g.pooled_pearson.std())])], ignore_index=True)
    S["arm"] = S["arm"].fillna("private")
    prs = []
    for ref in ("nonprivate_unclipped", "nonprivate_clipped"):
        rf = R[R.arm == ref].set_index("partition")
        for e in EPS:
            pe = per_part[per_part.eps == e].set_index("partition")
            for m in ("within_slide", "pooled_pearson"):
                dlt = pe[m] - rf.loc[pe.index, m]
                prs.append(dict(eps=e, minus=ref, metric=m, n_partitions=len(dlt), mean_diff=dlt.mean(),
                                sd_diff=dlt.std(), n_below=int((dlt < 0).sum())))
    rc = R[R.arm == "nonprivate_clipped"].set_index("partition")
    ru = R[R.arm == "nonprivate_unclipped"].set_index("partition")
    for m in ("within_slide", "pooled_pearson"):
        dlt = rc[m] - ru[m]
        prs.append(dict(eps=np.nan, minus="nonprivate_unclipped", metric=m, n_partitions=len(dlt),
                        mean_diff=dlt.mean(), sd_diff=dlt.std(), n_below=int((dlt < 0).sum()),
                        note="clipping alone"))
    S.to_csv("v3_summary.csv", index=False)
    pd.DataFrame(prs).to_csv("v3_paired.csv", index=False)
    R.to_csv("v3_rows.csv", index=False)
    C.write_provenance(out, "V3", a.frame_id, " ".join([sys.executable] + sys.argv),
                       dict(task=TASK, encoder=ENC, eps=list(EPS), delta=DELTA, n_noise=N_NOISE, clip_pct=CLIP_PCT,
                            k=H.K_PC, lam_num=H.LAM_NUM),
                       [os.path.abspath(__file__), C.__file__, H.__file__, D.__file__, V2.__file__])
    print("wall", round(time.time() - t0, 1))


if __name__ == "__main__":
    main()
