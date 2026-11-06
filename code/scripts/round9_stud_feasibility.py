"""Round 9 (claude-science) step S4: cross-gene studentized prediction sets for a new donor.

Runs on Longleaf next to the gated per-spot prediction files; writes aggregates only.
Methods (alpha level, one calibration spot per reference donor, finite-sample valid A-D under donor exchangeability
and within-donor exchangeability, because every donor's transform is built by the same rule from its own block and
from quantities that are symmetric functions of all donors' blocks):
  A hcp   : score |r|
  B own   : split conformal on the target's o block spots, score |r|
  C pergene: |r| / sigma_hat_gj, sigma_hat_gj = RMS of donor g's block residuals for gene j (floored)
  D xgene : |r| / (sigma_j * c_g), sigma_j = RMS of gene j over all donors' blocks; c_g = median over genes of
            (RMS of donor g's block residuals for gene j) / sigma_j
  E oracle: |r| / s_gj with s_gj the donor's full-data RMS (not valid; reference)
Usage: python round9_stud_feasibility.py <parquet> <task> <outdir> [reps]
"""
import sys, numpy as np, pandas as pd

ALPHA = 0.1
OS = [1, 2, 3, 5, 9, 15]

def kth(x, k):
    return np.inf if k > len(x) else np.partition(x, k - 1)[k - 1]

def main(pq, task, outdir, reps=40):
    df = pd.read_parquet(pq)
    genes = [c[3:] for c in df.columns if c.startswith("y__")]
    R = df[["y__" + g for g in genes]].values - df[["f__" + g for g in genes]].values
    donors = df.donor_id.astype(str).values
    ud = sorted(set(donors)); idx = {d: np.where(donors == d)[0] for d in ud}
    G, J = len(ud), len(genes)
    full_rms = np.array([np.sqrt((R[idx[d]] ** 2).mean(0)) for d in ud])          # G x J
    # Q5: factor share of log within-donor residual SD
    S = np.log(np.array([R[idx[d]].std(0) for d in ud]) + 1e-9)
    Z = (S - S.mean(0)) / (S.std(0) + 1e-12)
    sv = np.linalg.svd(Z - Z.mean(0), compute_uv=False)
    fac = pd.DataFrame([dict(task=task, G=G, J=J, pc1_share_log_resid_sd=sv[0] ** 2 / (sv ** 2).sum())])
    rng = np.random.default_rng(abs(hash(task)) % (2 ** 32))
    rows = []
    for t, dt in enumerate(ud):
        refs = [d for d in ud if d != dt]; K = len(refs)
        kq = int(np.ceil((1 - ALPHA) * (K + 1)))
        for o in OS:
            if len(idx[dt]) <= o + 5: continue
            for rep in range(reps):
                blocks, cal = {}, {}
                for d in ud:
                    perm = rng.permutation(idx[d])
                    blocks[d] = perm[:o]
                    if d != dt: cal[d] = perm[o]
                test = np.setdiff1d(idx[dt], blocks[dt])
                Bstack = np.vstack([R[blocks[d]] for d in ud])                       # (G*o) x J, symmetric
                sig_j = np.sqrt((Bstack ** 2).mean(0)) + 1e-6
                blk_rms = {d: np.sqrt((R[blocks[d]] ** 2).mean(0)) for d in ud}       # J per donor
                floor = 0.1 * sig_j
                c_g = {d: np.median(np.maximum(blk_rms[d], 1e-6) / sig_j) for d in ud}
                Rt = np.abs(R[test])                                                  # n_test x J
                calR = np.abs(np.vstack([R[cal[d]] for d in refs]))                   # K x J
                res = {}
                # A
                qA = np.array([kth(calR[:, j], kq) for j in range(J)]); res["hcp"] = (qA, qA)
                # B
                kb = int(np.ceil((1 - ALPHA) * (o + 1)))
                qB = np.array([kth(np.abs(R[blocks[dt], j]), kb) for j in range(J)]); res["own"] = (qB, qB)
                # C
                sc_ref = np.vstack([np.maximum(blk_rms[d], floor) for d in refs])
                qC = np.array([kth(calR[:, j] / sc_ref[:, j], kq) for j in range(J)])
                hwC = qC * np.maximum(blk_rms[dt], floor); res["pergene"] = (hwC, hwC)
                # D
                sd_ref = np.array([c_g[d] for d in refs])[:, None] * sig_j[None, :]
                qD = np.array([kth(calR[:, j] / sd_ref[:, j], kq) for j in range(J)])
                hwD = qD * c_g[dt] * sig_j; res["xgene"] = (hwD, hwD)
                # E oracle
                so_ref = np.vstack([full_rms[ud.index(d)] for d in refs])
                qE = np.array([kth(calR[:, j] / so_ref[:, j], kq) for j in range(J)])
                hwE = qE * full_rms[t]; res["oracle"] = (hwE, hwE)
                for m, (hw, _) in res.items():
                    cov = (Rt <= hw[None, :]).mean(0)                                  # per gene
                    fin = np.isfinite(hw)
                    rows.append(dict(task=task, target=dt, o=o, rep=rep, method=m, K=K,
                                     coverage=cov.mean(), frac_inf=1 - fin.mean(),
                                     mean_hw_finite=hw[fin].mean() if fin.any() else np.nan,
                                     median_hw_finite=np.median(hw[fin]) if fin.any() else np.nan))
        print(task, dt, flush=True)
    out = pd.DataFrame(rows)
    out.to_csv(f"{outdir}/stud_reps__{task}.csv.gz", index=False)
    fac.to_csv(f"{outdir}/stud_factor__{task}.csv", index=False)

if __name__ == "__main__":
    a = sys.argv
    main(a[1], a[2], a[3], int(a[4]) if len(a) > 4 else 40)
