#!/usr/bin/env python
"""Round 4, conformal track, stage C3, ACS K axis at o = 0 (fragment frag_ACS_K).

Task and predictor are those of frag_ACS_o (one design for both ACS units). ACS PUMS 2018 1-Year,
folktables ACSIncome filter (PPI Q0 task definition; N = 1,659,616), outcome log PINCP, groups = the
51 states (50 plus DC). Predictor = the PPI package predictor, HistGradientBoostingRegressor
cross-fitted over five state folds, fold = crc32(str(ST)) % 5; the PPI predictions file carries yhat
and fold. Residual r = log PINCP - yhat, score |r| (absolute). No labelled test spots (o = 0).

Two designs, written to separate files, because the five-fold cross-fitting limits how many
calibration states share one model with a test state.
  within  (primary, exact in the sense below). Test state t is any state; calibration states are K
          states drawn by a crc32-seeded permutation (key "ACS|Kcal|within|<ST>|<draw>") from the
          OTHER states of t's own fold. All of them received predictions from the same model, which
          never saw t or any of them, so given the model the K + 1 states are exchangeable under A1
          (group exchangeability). A fold with fewer than K + 1 states is skipped for that K (folds
          have 8 to 11 states, so K = 4 to 7 exist in every fold and K = 8, 9, 10 only in larger
          folds). n_train_groups = 51 - fold size, the number of states the fixed model was trained on.
  crossfold (extension, K up to 20; guarantee NOT exact). Calibration states are drawn from all 50
          other states (key "ACS|Kcal|crossfold|<ST>|<draw>"), each state's residuals coming from its
          own fold's cross-fitted model. Residuals then come from up to five different models, and the
          other-fold models were trained on t. This is the cross-fitting heuristic; the finite-sample
          guarantee below is a statement about the within design only. n_train_groups is that of
          t's own model; n_cal_same_fold records how many calibration states share it.

Methods (assumptions and guarantees written before running; this track's tie convention,
Q = inf{q : F(q) >= beta}, relative tolerance 1e-12, round4_conf_sim.wquantiles / split_qs):
  pooled  split conformal on all calibration spots with equal weights. No group-level guarantee.
  hcp     Lee-Barber-Willett weights 1/((K+1) N_k), test atom 1/(K+1) at +inf. Needs hierarchical
          exchangeability (A1 and within-group i.i.d. A3, size ignorability A2 NOT checked; state
          sizes differ by a factor of 60). Coverage >= 1 - alpha averaged over the draw of the groups
          and spots; infinite iff 1/(K+1) > alpha (K <= 9 at alpha 0.1, K <= 3 at alpha 0.2).
  dwr     Dunn-Wasserman-Ramdas single draw, as round 3's dwr: one uniformly drawn spot per
          calibration state (key "ACS|dwr|<design>|<ST>|<K>|<draw>"), split conformal on the K scores.
          Coverage >= 1 - alpha, finite iff K >= 1/alpha - 1 (K >= 9 at 0.1, K >= 4 at 0.2).
Released-code finiteness (floating-point cumsum compared without tolerance, scores.weighted_quantile
rule) is recorded beside this track's for hcp as finite_code in the by-state file; for pooled and dwr
the two rules coincide by construction here (split_qs has no float cumsum), so finite_code = finite.

Row definition (fixed format). One row per (method, alpha, K, fold, draw), fold = fold of the test
state. Coverage = mean over the fold's test states (those with K feasible) of each state's coverage
of all its N spots (an infinite interval covers). width_mean and width_median = mean and median of
the full width 2q over the fold's finite test states (inf if none). n_test = sum of N over those
states. finite = share of the fold's test states with a finite threshold. Every row uses draws
0..19; pooled and hcp depend on the draw through the calibration-state selection.
"""
import os, sys, math, zlib, json, time, hashlib, glob
import numpy as np
import pandas as pd

sys.path.insert(0, os.environ.get("R4CONF_SCRIPTS", "/work/users/w/e/weiyang/hest_code/round4-conformal/code/scripts"))
import round4_conf_sim as S

ALPHAS = (0.1, 0.2)
K_GRID = (4, 6, 8, 10, 12, 14, 16, 18, 20)
N_DRAWS = 20
TASK, LABEL_SET, ENC, SCORE = "ACS", "folktables_ACSIncome", "package", "absolute"
SIM_MD5 = "76fda34ee622e299bbaa806e5c8da98a"
PRED_MD5 = "cabb141ce4c4609eda500680b71848bf"


def crc(k):
    return zlib.crc32(k.encode())


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def code_q(scores, weights, inf_mass, beta):
    """Released code's rule (scores.weighted_quantile): sort, cumsum, searchsorted(1-alpha), floating
    point, no tolerance; weights as given."""
    if len(scores) == 0:
        return math.inf
    o = np.argsort(scores, kind="stable")
    cw = np.cumsum(weights[o])
    i = np.searchsorted(cw, beta, side="left")
    return math.inf if i >= len(cw) else float(scores[o][i])


def load(pred_path):
    pr = pd.read_parquet(pred_path, columns=["ST", "log_PINCP", "yhat", "fold"])
    pr["r"] = pr["log_PINCP"].to_numpy(float) - pr["yhat"].to_numpy(float)
    assert len(pr) == 1659616, len(pr)
    assert (pr["fold"].to_numpy() == np.array([crc(str(int(s))) % 5 for s in pr["ST"].to_numpy()])).all()
    res = {int(s): g["r"].to_numpy(float) for s, g in pr.groupby("ST")}
    fold = {int(s): int(f) for s, f in pr.groupby("ST")["fold"].first().items()}
    assert len(res) == 51
    return res, fold


def run_design(design, RES, FOLD, AB, ASRT):
    states = sorted(RES)
    fsize = {f: sum(1 for s in FOLD if FOLD[s] == f) for f in set(FOLD.values())}
    out = []
    for d in range(N_DRAWS):
        for t in states:
            f = FOLD[t]
            if design == "within":
                pool = [s for s in states if FOLD[s] == f and s != t]
            else:
                pool = [s for s in states if s != t]
            perm = np.random.default_rng(crc(f"ACS|Kcal|{design}|{t}|{d}")).permutation(len(pool))
            ordered = [pool[i] for i in perm]
            for K in K_GRID:
                if K > len(pool):
                    continue
                cs = ordered[:K]
                same = sum(1 for s in cs if FOLD[s] == f)
                sa = np.concatenate([AB[s] for s in cs])
                w = np.concatenate([np.full(len(AB[s]), 1.0 / ((K + 1) * len(AB[s]))) for s in cs])
                betas = [1 - a for a in ALPHAS]
                rows = []
                rows.append(("pooled", S.split_qs(sa, ALPHAS), None))
                rows.append(("hcp", S.wquantiles(sa, w, 1.0 / (K + 1), betas),
                             [code_q(sa, w, 1.0 / (K + 1), b) for b in betas]))
                rng = np.random.default_rng(crc(f"ACS|dwr|{design}|{t}|{K}|{d}"))
                sd = np.array([AB[s][rng.integers(len(AB[s]))] for s in cs])
                rows.append(("dwr", S.split_qs(sd, ALPHAS), None))
                at = ASRT[t]; n = len(at)
                for method, qs, qcs in rows:
                    for i, a in enumerate(ALPHAS):
                        q = qs[i]
                        qc = q if qcs is None else qcs[i]
                        cov = 1.0 if not math.isfinite(q) else float(np.searchsorted(at, q, side="right")) / n
                        out.append((f, t, K, fsize and (51 - fsize[f]), same, d, method, a, cov,
                                    2 * q if math.isfinite(q) else math.inf, n,
                                    int(math.isfinite(q)), int(math.isfinite(qc))))
    cols = ["fold", "state", "K", "n_train_groups", "n_cal_same_fold", "draw", "method", "alpha",
            "coverage", "width", "n_test", "finite", "finite_code"]
    return pd.DataFrame(out, columns=cols)


def fold_rows(df):
    g = df.groupby(["method", "alpha", "K", "n_train_groups", "fold", "draw"], sort=True)

    def agg(x):
        fw = x.loc[x.finite == 1, "width"]
        return pd.Series(dict(coverage=x.coverage.mean(),
                              width_mean=fw.mean() if len(fw) else math.inf,
                              width_median=fw.median() if len(fw) else math.inf,
                              n_test=int(x.n_test.sum()), finite=x.finite.mean(),
                              n_states=len(x)))
    sw = g.apply(agg, include_groups=False).reset_index()
    sw.insert(0, "task", TASK); sw.insert(1, "label_set", LABEL_SET); sw.insert(2, "encoder", ENC)
    sw.insert(4, "score", SCORE)
    return sw[["task", "label_set", "encoder", "method", "score", "alpha", "K", "n_train_groups", "fold",
               "draw", "coverage", "width_mean", "width_median", "n_test", "finite", "n_states"]]


def summary(df):
    """Over all states and draws: per (method, alpha, K): mean state coverage, share of
    finite thresholds, median finite width, and the sd over draws of the draw-level coverage."""
    rows = []
    for (m, a, K), x in df.groupby(["method", "alpha", "K"]):
        dl = x.groupby("draw").coverage.mean()
        fw = x.loc[x.finite == 1, "width"]
        rows.append(dict(method=m, alpha=a, K=K, n_states=x.state.nunique(), n_rows=len(x),
                         coverage=x.coverage.mean(), coverage_sd_over_draws=dl.std(),
                         finite=x.finite.mean(), finite_code=x.finite_code.mean(),
                         width_median=fw.median() if len(fw) else math.inf,
                         width_mean=fw.mean() if len(fw) else math.inf,
                         n_train_groups_min=x.n_train_groups.min(), n_train_groups_max=x.n_train_groups.max()))
    return pd.DataFrame(rows)


def main(pred_path, outdir, acs_dir):
    import round4_conf_io as IO
    IO.stamp(outdir, track="round4-conformal", note="C3 ACS K axis at o = 0 (frag_ACS_K)")
    checks = {"sim_md5": md5(S.__file__), "pred_md5": md5(pred_path)}
    assert checks["sim_md5"] == SIM_MD5, checks
    assert checks["pred_md5"] == PRED_MD5, checks
    man = os.path.join(acs_dir, "raw_manifest.json")
    bad, nchk = [], 0
    if os.path.exists(man):
        for r in json.load(open(man)):
            p = os.path.join(acs_dir, r["file"])
            if os.path.exists(p):
                nchk += 1
                if md5(p) != r["md5"]:
                    bad.append(r["file"])
    checks["raw_checked"], checks["raw_mismatch"] = nchk, len(bad)
    print("checks", checks, flush=True)
    assert not bad
    RES, FOLD = load(pred_path)
    AB = {s: np.abs(x) for s, x in RES.items()}
    ASRT = {s: np.sort(x) for s, x in AB.items()}
    print("fold sizes", sorted(pd.Series(FOLD).value_counts().to_dict().items()), flush=True)
    t0 = time.time()
    res = {}
    for design, fn in (("within", "c3_K_sweep__ACS.csv"), ("crossfold", "c3_K_sweep_crossfold__ACS.csv")):
        df = run_design(design, RES, FOLD, AB, ASRT)
        sw = fold_rows(df)
        sw.to_csv(os.path.join(outdir, fn), index=False)
        df.to_csv(os.path.join(outdir, fn.replace("c3_K_sweep", "c3_K_sweep_by_state")), index=False)
        summary(df).to_csv(os.path.join(outdir, fn.replace("c3_K_sweep", "c3_K_sweep_summary")), index=False)
        res[design] = (len(sw), len(df))
        print(design, "rows", len(sw), "state rows", len(df), "seconds", round(time.time() - t0), flush=True)
    try:
        IO.write_provenance(outdir, "C3_ACS_K", os.path.abspath(__file__),
                            dict(K_GRID=K_GRID, ALPHAS=ALPHAS, N_DRAWS=N_DRAWS),
                            extra={"checks": json.dumps(checks), "rows": json.dumps(res),
                                   "frame_id": os.environ.get("R4CONF_FRAME_ID", "")})
    except Exception as e:
        print("write_provenance failed", repr(e), flush=True)
        open(os.path.join(outdir, "PROVENANCE.txt"), "a").write(
            f"write_provenance failed: {e!r}\nchecks {checks}\nrows {res}\nslurm {os.environ.get('SLURM_JOB_ID')}\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
