#!/usr/bin/env python
"""Round 4, conformal track, stage C3, ACS o rows (fragment frag_ACS_o).

Task. ACS PUMS 2018 1-Year person file, folktables ACSIncome filter (the PPI track's Q0 task
definition acs_pums_task_def.json: AGEP > 16, PINCP > 100, WKHP > 0, PWGTP >= 1; N = 1,659,616),
outcome log PINCP, groups = the 51 states (50 plus DC). Predictor = the PPI package predictor,
HistGradientBoostingRegressor cross-fitted over five state folds, fold = crc32(str(ST)) % 5; the
predictions file carries yhat and the fold. Residual r = log PINCP - yhat. Scores are absolute.

Design. Each fold is one cell: its 8 to 11 states all received predictions from the same model,
which never saw any of them, so their residuals are exchangeable at the group level given the
model. Each state of the fold is the test state in turn; the other states of the fold are the K
calibration groups (K = fold size - 1, between 7 and 10). n_glob, the number of groups the fixed
global predictor was trained on, is 51 - fold size. For draw d (0..19) every state's rows are
permuted with default_rng(crc32("ACS|perm|<ST>|<d>")); the test state's first o permuted rows are
its labelled spots (paired across o), the remaining N - o rows are evaluated. Calibration groups
use the same permuted order, so their first floor(o/2) rows are the recentring block.

Methods (assumption and guarantee written before running; all use this track's tie convention,
Q = inf{q : F(q) >= beta}, relative tolerance 1e-12, round4_conf_sim.wquantiles / split_qs):
  pooled        split conformal on all calibration spots, equal weights. No guarantee for a new
                group. Draw-independent: reported at draw 0 only.
  hcp           Lee-Barber-Willett weights 1/((K+1) N_k), test atom 1/(K+1) at +inf. Needs
                hierarchical exchangeability; coverage >= 1 - alpha; infinite iff 1/(K+1) > alpha.
                Draw-independent: reported at draw 0 only.
  dwr           Dunn-Wasserman-Ramdas single subsample: one random spot per calibration group,
                split conformal on the K scores. Coverage >= 1 - alpha, finite iff K >= 1/alpha - 1.
  ghcp*         round4_conf_sim.ghcp_fast (Algorithm 1). ghcp: eta 0, adaptation on; ghcp_noad:
                eta 0, off; ghcp_r05 / ghcp_r05_noad: eta 0.5 with the paper's pool rule, eq. (8)
                (primary for the paper's guarantee); ghcp_r05code / ghcp_r05code_noad: eta 0.5 with
                the released code's pool, one group larger (alpha 0.1 only). Assumptions A1 to A3
                (group exchangeability given the cross-fitted model, size ignorability, within-group
                i.i.d.); A2 is NOT checked here and state sizes differ by a factor of 60.
  within        split conformal inside the test state, Std-CP form of the GHCP paper: centre = mean
                of the first floor(o/2) labelled residuals, the other o - floor(o/2) calibrate.
  within_plain  All o labelled residuals calibrate the absolute score |r|, no recentring. Assumes
                the o labelled spots are exchangeable with the state's other spots (uniform draw,
                true by construction). Guarantee: coverage >= 1 - alpha for the remaining spots,
                the interval is [yhat - q, yhat + q] with q the ceil((o+1)(1-alpha))-th smallest of
                the o scores; finite iff o >= ceil(1/alpha) - 1 (o >= 9 at alpha 0.1, o >= 4 at 0.2).
  recentred     Cross-group pooled quantile q of the calibration groups' |r| (spot-level equal
                weights, as round 3's `donor` design), applied around the centre mean(first o
                labelled residuals). The calibration scores are not recentred. No guarantee.

Row definition (fixed format). One row per (method, alpha, o, fold, draw). Coverage is the mean over
the fold's test states of the state's coverage of its N - o remaining spots (an infinite interval
covers). width_mean and width_median are the mean and median over the fold's finite test states of
the full interval width 2 q (log-income units). n_test = sum over the fold's states of N - o.
finite = share of the fold's test states with a finite threshold. The per-state rows are written to
c3_o_sweep_by_state__ACS.csv, with the finiteness under the released code's tie rule
(floating-point comparison, no tolerance) beside this track's.
"""
import os, sys, math, zlib, json, time, hashlib
import numpy as np
import pandas as pd
import concurrent.futures.process as _P
_P._check_system_limits = lambda: None   # sandbox refuses os.sysconf(SC_SEM_NSEMS_MAX); guards only the semaphore limit
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get("R4CONF_SCRIPTS", "/Users/nicolaszhang/HEST-1k-replication-conformal/code/scripts"))
import round4_conf_sim as S

ALPHAS = (0.1, 0.2)
O_GRID = (0, 5, 10, 25, 50, 100, 200)
N_DRAWS = 20
TASK, LABEL_SET, ENC, SCORE = "ACS", "folktables_ACSIncome", "package", "absolute"
GHCP_VARIANTS = [("ghcp", True, 0.0, "paper"), ("ghcp_noad", False, 0.0, "paper"),
                 ("ghcp_r05", True, 0.5, "paper"), ("ghcp_r05_noad", False, 0.5, "paper"),
                 ("ghcp_r05code", True, 0.5, "code"), ("ghcp_r05code_noad", False, 0.5, "code")]


def crc(k):
    return zlib.crc32(k.encode())


def code_q(scores, weights, inf_mass, beta):
    """Released code's rule (scores.weighted_quantile): sort, cumsum, searchsorted(1-alpha) in
    floating point, no tolerance, weights taken as given (they sum to 1 - inf_mass)."""
    if len(scores) == 0:
        return math.inf
    o = np.argsort(scores, kind="stable")
    cw = np.cumsum(weights[o])
    i = np.searchsorted(cw, beta, side="left")
    return math.inf if i >= len(cw) else float(scores[o][i])


def ghcp_dual(prep, init, o, alphas, rng, adapt, eta, n_glob, rule):
    """Same as round4_conf_sim.ghcp_fast (this track's tolerance) plus the released code's tie
    rule threshold; the draws of rng are consumed identically."""
    N = prep.N
    m = (o // 2) if adapt else 0
    lamv = m / (n_glob + m) if m > 0 else 0.0
    Sp = S.restricted_pool(N, o, eta, rng, rule)
    c_test = lamv * float(np.mean(init[:m])) if m > 0 else 0.0
    betas = [1 - a for a in alphas]
    if len(Sp) == 0:
        held = np.abs(init[m:o] - c_test)
        L = o + 1 - m
        w = np.full(len(held), 1.0 / L)
        return ([S.wquantiles(held, w, 1.0 / L, betas)[i] for i in range(len(betas))],
                [code_q(held, w, 1.0 / L, b) for b in betas], c_test)
    J0 = Sp[rng.integers(len(Sp))]
    Scal = [j for j in Sp if j != J0]
    M = len(Scal) + 1
    sc, wt = [], []
    for j in Scal:
        cj = lamv * float(np.mean(prep.cal[j][:m])) if m > 0 else 0.0
        h = prep.held_abs(j, m, cj)
        sc.append(h); wt.append(np.full(len(h), 1.0 / (M * len(h))))
    Lt = N[J0] - m
    h = np.abs(init[m:o] - c_test)
    sc.append(h); wt.append(np.full(len(h), 1.0 / (M * Lt)))
    s = np.concatenate(sc); w = np.concatenate(wt); im = (N[J0] - o) / (M * Lt)
    return (S.wquantiles(s, w, im, betas), [code_q(s, w, im, b) for b in betas], c_test)


def load():
    pr = pd.read_parquet(sys.argv[1] if len(sys.argv) > 1 else os.environ["ACS_PRED"])
    pr["r"] = pr["log_PINCP"].to_numpy(float) - pr["yhat"].to_numpy(float)
    assert len(pr) == 1659616
    assert (pr["fold"].to_numpy() == np.array([crc(str(int(s))) % 5 for s in pr["ST"].to_numpy()])).all()
    return {int(s): g["r"].to_numpy(float) for s, g in pr.groupby("ST")}, \
           {int(s): int(f) for s, f in pr.groupby("ST")["fold"].first().items()}


def view(preps, states):
    p = S.Prep.__new__(S.Prep)
    p.cal = [preps[s].cal[0] for s in states]
    p.N = np.array([len(x) for x in p.cal])
    p.order = [preps[s].order[0] for s in states]
    p.xs = [preps[s].xs[0] for s in states]
    p.rank = [preps[s].rank[0] for s in states]
    return p


def cov_of(ev, q, c):
    return 1.0 if not math.isfinite(q) else float(np.mean(np.abs(ev - c) <= q))


def one_draw(d):
    RES, FOLD = DATA
    perm = {s: RES[s][np.random.default_rng(crc(f"ACS|perm|{s}|{d}")).permutation(len(RES[s]))] for s in RES}
    preps = {s: S.Prep([perm[s]]) for s in perm}
    out = []
    folds = sorted(set(FOLD.values()))
    for f in folds:
        fs = sorted(s for s in FOLD if FOLD[s] == f)
        n_glob = len(FOLD) - len(fs)
        for t in fs:
            cs = [s for s in fs if s != t]
            K = len(cs)
            prep = view(preps, cs)
            xt = perm[t]
            for o in O_GRID:
                init, ev = xt[:o], xt[o:]
                rows = []   # (method, alpha, q, qcode, c)

                def add(method, alphas, qs, c, qcs=None):
                    for i, a in enumerate(alphas):
                        if qs[i] is None:
                            continue
                        rows.append((method, a, qs[i], qs[i] if qcs is None else qcs[i], c))
                if o == 0:
                    if d == 0:
                        sa = np.concatenate([prep.held_abs(j, 0, 0.0) for j in range(K)])
                        add("pooled", ALPHAS, S.split_qs(sa, ALPHAS), 0.0)
                        w = np.concatenate([np.full(n, 1.0 / ((K + 1) * n)) for n in prep.N])
                        sj = np.concatenate([prep.held_abs(j, 0, 0.0) for j in range(K)])
                        betas = [1 - a for a in ALPHAS]
                        add("hcp", ALPHAS, S.wquantiles(sj, w, 1.0 / (K + 1), betas), 0.0,
                            [code_q(sj, w, 1.0 / (K + 1), b) for b in betas])
                    rng = np.random.default_rng(crc(f"ACS|dwr|{t}|{d}"))
                    sdw = np.array([abs(x[rng.integers(len(x))]) for x in prep.cal])
                    add("dwr", ALPHAS, S.split_qs(sdw, ALPHAS), 0.0)
                else:
                    # within (Std-CP form)
                    m = o // 2
                    c = float(np.mean(init[:m])) if m > 0 else 0.0
                    add("within", ALPHAS, S.split_qs(np.abs(init[m:o] - c), ALPHAS), c)
                    add("within_plain", ALPHAS, S.split_qs(np.abs(init), ALPHAS), 0.0)
                    qpool = POOLQ[(f, t)]
                    add("recentred", ALPHAS, qpool, float(np.mean(init)))
                for name, adapt, eta, rule in GHCP_VARIANTS:
                    al = [a for a in ALPHAS if rule == "paper" or abs(a - 0.1) < 1e-12]
                    if not al:
                        continue
                    rng = np.random.default_rng(crc(f"ACS|ghcp|{t}|{d}|{o}|{name}"))
                    qs, qcs, c = ghcp_dual(prep, init, o, al, rng, adapt, eta, n_glob, rule)
                    add(name, al, qs, c, qcs)
                for method, a, q, qc, c in rows:
                    out.append((f, t, K, d, o, method, a, cov_of(ev, q, c), 2 * q if math.isfinite(q) else math.inf,
                                len(ev), int(math.isfinite(q)), int(math.isfinite(qc))))
    return out


DATA = None
POOLQ = None


def init_worker(data, poolq):
    global DATA, POOLQ
    DATA, POOLQ = data, poolq


def pooled_q(data):
    RES, FOLD = data
    pq = {}
    for f in sorted(set(FOLD.values())):
        fs = sorted(s for s in FOLD if FOLD[s] == f)
        for t in fs:
            sa = np.abs(np.concatenate([RES[s] for s in fs if s != t]))
            pq[(f, t)] = S.split_qs(sa, ALPHAS)
    return pq


def main(outdir, ndraws=N_DRAWS, workers=8):
    data = load()
    poolq = pooled_q(data)
    t0 = time.time()
    with ProcessPoolExecutor(workers, initializer=init_worker, initargs=(data, poolq)) as ex:
        res = list(ex.map(one_draw, range(ndraws)))
    cols = ["fold", "state", "K", "draw", "o", "method", "alpha", "coverage", "width", "n_test", "finite", "finite_code"]
    df = pd.DataFrame([r for rr in res for r in rr], columns=cols)
    df.to_csv(os.path.join(outdir, "c3_o_sweep_by_state__ACS.csv"), index=False)
    g = df.groupby(["method", "alpha", "o", "fold", "draw"], sort=True)

    def agg(x):
        fw = x.loc[x.finite == 1, "width"]
        return pd.Series(dict(K=int(x.K.iloc[0]), coverage=x.coverage.mean(),
                              width_mean=fw.mean() if len(fw) else math.inf,
                              width_median=fw.median() if len(fw) else math.inf,
                              n_test=int(x.n_test.sum()), finite=x.finite.mean()))
    sw = g.apply(agg, include_groups=False).reset_index()
    sw.insert(0, "task", TASK); sw.insert(1, "label_set", LABEL_SET); sw.insert(2, "encoder", ENC)
    sw.insert(4, "score", SCORE)
    cols = ["task", "label_set", "encoder", "method", "score", "alpha", "o", "K", "fold", "draw",
            "coverage", "width_mean", "width_median", "n_test", "finite"]
    sw = sw[cols]
    sw.to_csv(os.path.join(outdir, "c3_o_sweep__ACS.csv"), index=False)
    print("rows", len(sw), "seconds", round(time.time() - t0))
    return sw, df


if __name__ == "__main__":
    main(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
