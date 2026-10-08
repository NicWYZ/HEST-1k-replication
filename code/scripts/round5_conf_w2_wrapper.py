#!/usr/bin/env python
"""Round 5, prediction-set track, stage W2 part 1: a wrapper around the released GHCP simulation.

docs/round5_conf_plan.md section 2 (W2), docs/decisions/round5_conformal_track.md section 2.3.
Nothing in the released code (github.com/soham-penn/hierarchical_CP, commit d1a69f4) is edited.

HOW IT REACHES THE GENERATOR
  The released launcher run_section_3_1.py is a public name for
  code/marginal/run_true_marginal_latent_intercept_rf_experiments.py, whose run_chunk(worker_id, n,
  offset, config) seeds numpy's global generator with BASE_SEED + 1000 * worker_id (BASE_SEED = 457),
  installs a generator by patch_fixed_size_generators or patch_poisson_generators (functions of the
  released module run_true_marginal_latent_intercept_experiments, imported here and called as the
  launcher calls them), and then calls code.shared.dgp.experiments.run_experiments_outer, whose
  run_one_experiment draws, for each replicate and in this order, the K calibration groups, then one
  test group, and then evaluates every method for every o in the launcher's grid
  (0, 5, 10, 15, 20, 25, 30, 35) and every alpha of the launcher's list (0.05, 0.1, 0.15, 0.2).
  This wrapper does the same chunk layout (fixedN21: 125 replicates per chunk, 8 chunks;
  poissonNmean25: 25 per chunk, 40 chunks; split_counts as the launcher), seeds each chunk the same
  way, builds the configuration with the released build_configs, and for each replicate calls the
  released generators in the released order. Within a replicate it calls the released functions
  compute_hcp_interval_radius, compute_donor_hcp_randomized_interval (GHCP, with the alphas list) and
  the released _compute_std_cp_interval, with the launcher's quantile seeds (make_quantile_seed with
  experiment_id = replicate index inside the chunk, starting at 1, as run_experiments_outer does).
  The only reason a later replicate could differ from the launcher's is a difference in how much of
  numpy's GLOBAL stream a replicate consumes. In the released methods the global stream is consumed
  only by compute_sample_hcp_randomized_interval (methods/sample_hcp.py lines 233 and 271:
  np.random.choice without replacement, once per pool group and once for the test group, for every
  alpha of the launcher's list and every o of the launcher's grid); every other released method uses
  its own default_rng. The wrapper does not run S-HCP. It makes the same np.random.choice calls with
  the same arguments (emulate_sr_draws), for the launcher's full o grid and alpha list, so that the
  stream at the start of the next replicate is the launcher's. This is verified by --selftest
  (the stream state after the released call equals the state after the emulation) and, in effect, by
  every replicate after the first agreeing with the launcher (the check in round5_conf_w2_check.py).
  The o values that are computed (--o-values) and written are independent of the launcher's grid; the
  number of calibration groups (--k) changes the draws, as a different K does in the launcher.

THE METHODS, with what each assumes and the guarantee it carries (written before any run)
  Scores are absolute residuals |y - mu_g(x, u)| of a global random forest mu_g (released
  fit_global of create_mu_method_random_forest_offset, 50 trees, node size 5, random_state 123).
  released_hcp    the released HCP (compute_hcp_interval_radius on the baseline model's calibration
                  scores, the model fitted on the o = 0 training groups). Assumes the K calibration
                  groups and the test group are exchangeable. Valid for any K, finite iff 1/(K'+1) <= alpha
                  with K' the number of calibration groups. Interval mu_g(x) +- q.
  released_ghcp   the released GHCP (eta = 0.5, adaptation on, code pool rule, deterministic quantile).
                  Assumes GHCP's A1 to A3 (hierarchical exchangeability, donor size). Valid.
  released_stdcp  the released Std-CP of run_one_experiment: a local random forest fitted on a random
                  half (o // 2) of the o labelled units' (x, y), calibrated on the other half with a
                  RANDOMIZED split-conformal quantile with an infinity atom. See FINDINGS in the check
                  script: it is exact coverage 1 - alpha over its own randomization, and infinite with
                  the randomization's probability. It is not `within` of instruction section 2.3.
  hcp             this track's round4_conf_sim.hcp_q on the same scores as released_hcp. Standard tie
                  convention (the ceil((n+1)(1-alpha))-th smallest, relative tolerance QTOL of round 4).
                  Guarantee as released_hcp. Expected to equal released_hcp to 1e-9.
  ghcp            this track's round4_conf_sim.ghcp_q with eta = 0.5, adaptation on, the paper's pool
                  rule (equation (8), one group smaller than the released code's), standard ties. The
                  residual form: for the pool and donor ghcp_q selects, a global forest is fitted on the
                  groups outside the pool (the released fit_global), e_ij = y_ij - mu_g(x_ij, u_j), the
                  test group's labelled units give init = e_i for i < o, the centre is
                  lambda * mean(init[:o//2]) with lambda = m / (n_glob + m), n_glob the number of groups
                  the forest was fitted on (the released w_g is N_comp / (N_comp + tau), the same
                  lambda). The released code shrinks the PREDICTION, w_g mu_g(x) + (1 - w_g) mean(y),
                  so its centre differs from this form by (1 - w_g) times the within-group variation of
                  mu_g(x); this is the one place the two are not the same construction and it is
                  quantified by the diagnostic rows (--diag-reps). Guarantee: valid under GHCP's A1 to A3
                  for the residual score, with the paper's pool. Interval mu_g(x) + c +- q.
  within_plain    round5_conf_w1_sim.f_within_plain on init[:o]: split conformal on the o labelled
                  absolute residuals, uncentred. Assumes the o labelled units and the target are
                  exchangeable within the test group (true here, units are iid given the group).
                  Coverage ceil((o+1)(1-alpha))/(o+1) with distinct scores; finite iff o >= 9 at
                  alpha 0.1 and o >= 4 at alpha 0.2.
  within_full     round5_conf_w1_sim.f_within_full on init[:o]: full conformal with the mean as fitted
                  model, reported as the convex hull of the kept set (width) with the exact set's
                  coverage of the target in column exact_cov and whether it is one interval in
                  is_interval. Same assumption and expected coverage as within_plain; finite iff
                  floor(alpha(o+1)) >= 1.
  The expected coverage of the two within-group methods is ceil((n+1)(1-alpha))/(n+1) with n = o,
  recorded in the column expected_cov.

CHOICES THE BRIEF LEAVES OPEN, recorded before the run
  1. The three methods that use labelled units (ghcp, within_plain, within_full) share one residual
     stream per (replicate, o): the residuals of the global forest fitted on the groups outside this
     track's paper pool. The released HCP keeps its own baseline forest, as the released code does.
  2. This track's ghcp uses eta = 0.5 (not the round-4 simulation's eta = 0): with a learned forest the
     groups outside the pool are what the forest is fitted on, and with eta = 0 there are none.
  3. If the pool is empty (o >= the group size in the fixed design) the forest is fitted on all K groups
     as the released code does and ghcp_q reduces to the within-group split (its Remark 2.2 branch).
  4. Width is twice the half-width. A non-finite half-width gives width inf and covered = 1.
  5. Rows are written for alpha in --alphas-out; the launcher's whole alpha list is always computed
     for the released methods and for the random stream.
  6. A pool group is chosen with a generator keyed by (design, K, chunk, replicate, o), so it is the same
     for every alpha of a replicate and o and the rows are paired.

Usage: round5_conf_w2_wrapper.py --ghcp-code DIR --design fixedN21 --chunks 0,1 --out DIR [--k 20]
         [--o-values 0,5,10,15,20] [--alphas-out 0.1,0.2] [--max-reps N] [--diag-reps N] [--selftest]
"""
import argparse
import copy
import math
import os
import sys
import time
import zlib

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

LAUNCHER_ALPHAS = (0.05, 0.1, 0.15, 0.2)
LAUNCHER_O = (0, 5, 10, 15, 20, 25, 30, 35)
PAPER_O = (0, 5, 10, 15, 20)
CHUNK_SIZE = {"fixedN21": 125, "poissonNmean25": 25}
ALPHA_SELECTION = 0.5
ETA = 0.5
TARGET_INDEX = 35


def crc(key):
    return zlib.crc32(key.encode())


def load_released(gc):
    """Import the released modules from gc, unmodified, in the way the launcher does."""
    gc = os.path.abspath(gc)
    if "code" in sys.modules and not hasattr(sys.modules["code"], "__path__"):
        for m in [k for k in sys.modules if k == "code" or k.startswith("code.")]:
            del sys.modules[m]      # the standard-library module of that name, not the released package
    sys.path.insert(0, gc)
    import importlib
    R = {}
    R["EXP"] = importlib.import_module("code.shared.dgp.experiments")
    R["LCH"] = importlib.import_module("code.marginal.run_true_marginal_latent_intercept_experiments")
    R["RFL"] = importlib.import_module("code.marginal.run_true_marginal_latent_intercept_rf_experiments")
    R["M"] = importlib.import_module("methods")
    R["DH"] = importlib.import_module("methods.donor_hcp")
    R["SH"] = importlib.import_module("methods.sample_hcp")
    R["BH"] = importlib.import_module("methods.baseline_hcp")
    R["SC"] = importlib.import_module("scores")
    assert R["EXP"].__file__.startswith(gc), R["EXP"].__file__
    return R


def emulate_sr_draws(R, N, K, o):
    """The np.random.choice calls compute_sample_hcp_randomized_interval makes for one (alpha, o)."""
    S_tilde = R["SH"]._select_s_tilde_with_tie_randomization(N=N, o_observed=o,
                                                             alpha_selection=ALPHA_SELECTION)
    if len(S_tilde) == 0:
        return
    tau = int(np.floor(o / 2))
    tau = max(tau, 0)
    if o > 0 and tau >= o:
        tau = o - 1
    for j in np.sort(np.concatenate([S_tilde, [K]])):
        if j < K:
            if N[j] < o + 1:
                continue
            np.random.choice(N[j], size=o + 1, replace=False)
        elif tau > 0:
            np.random.choice(o, size=tau, replace=False)


def state_equal(a, b):
    return a[0] == b[0] and np.array_equal(a[1], b[1]) and a[2:] == b[2:]


class Ctx:
    pass


def make_ctx(R, design, K, gamma=None):
    LCH, RFL, M = R["LCH"], R["RFL"], R["M"]
    cfgs = LCH.build_configs(total_replicates=1000, alpha=LAUNCHER_ALPHAS[0],
                             gamma=LCH.DEFAULT_GAMMA, quantile_mode="deterministic",
                             quantile_base_seed=LCH.BASE_SEED)
    cfg = dict(cfgs[design])
    cfg["alphas"] = list(LAUNCHER_ALPHAS)
    cfg["number_groups_k"] = int(K)
    assert list(cfg["o_values"]) == list(LAUNCHER_O) and cfg["target_index"] == TARGET_INDEX
    c = Ctx()
    c.R, c.cfg, c.design, c.K = R, cfg, design, int(K)
    c.mu_baseline = M.create_mu_method_random_forest_global_only(
        ntree=RFL.RF_NTREE, nodesize=RFL.RF_NODESIZE, random_state=RFL.RF_RANDOM_STATE)
    c.mu_hcp = M.create_mu_method_random_forest_offset(
        ntree=RFL.RF_NTREE, nodesize=RFL.RF_NODESIZE, random_state=RFL.RF_RANDOM_STATE, c=1.0)
    c.dgp = {"dimension": cfg["dimension"], "u_min": cfg["u_min"], "u_max": cfg["u_max"]}
    c.lamP = cfg.get("lambda_poisson", 21)
    return c


def install_generators(c):
    cfg, LCH = c.cfg, c.R["LCH"]
    if cfg["generation_mode"] == "fixed":
        LCH.patch_fixed_size_generators(fixed_n=cfg["fixed_n"], target_n=cfg["target_n"],
                                        dimension=cfg["dimension"], u_min=cfg["u_min"],
                                        u_max=cfg["u_max"], rho=float(cfg["rho"]),
                                        gamma=float(cfg["gamma"]))
    else:
        LCH.patch_poisson_generators(lambda_poisson=cfg["lambda_poisson"], dimension=cfg["dimension"],
                                     u_min=cfg["u_min"], u_max=cfg["u_max"], rho=float(cfg["rho"]),
                                     gamma=float(cfg["gamma"]),
                                     min_target_n=int(cfg["target_index"]) + 1,
                                     size_offset=int(cfg.get("size_offset", 1)))


def draw_replicate(c):
    """Calibration groups then one test group, as run_one_experiment draws them."""
    EXP = c.R["EXP"]
    cal = EXP.generate_calibration_data(number_groups=c.K, lambda_Poisson=c.lamP,
                                        dgp_specification=c.dgp)
    test = EXP.generate_test_group(lambda_Poisson=c.lamP, dgp_specification=c.dgp,
                                   o_observed=TARGET_INDEX)
    return cal, test


def group_arrays(Zg):
    return np.array([z["X"] for z in Zg], dtype=float), np.array([z["Y"] for z in Zg], dtype=float)


def residuals(c, model, U_cal, Z_cal, U_test, Z_test):
    """e_ij = y_ij - mu_g(x_ij, u_j) for the K calibration groups, the test group, and the target."""
    pg = c.mu_hcp["predict_global_batch"]
    cal = []
    for j in range(len(Z_cal)):
        X, y = group_arrays(Z_cal[j])
        cal.append(y - pg(model, X, U_cal[j, :]))
    X, y = group_arrays(Z_test)
    e_test = y - pg(model, X, U_test[0, :])
    return cal, e_test


def row(base, alpha, o, method, half, covered, **extra):
    d = dict(base)
    finite = bool(np.isfinite(half))
    d.update(alpha=alpha, o=o, method=method, covered=int(covered), finite=int(finite),
             width=(2.0 * half if finite else math.inf), **extra)
    return d


def interval_row(base, alpha, o, method, lo, hi, y_t, **extra):
    finite = bool(np.isfinite(lo) and np.isfinite(hi))
    d = dict(base)
    d.update(alpha=alpha, o=o, method=method, covered=int(lo <= y_t <= hi), finite=int(finite),
             width=(hi - lo if finite else math.inf), **extra)
    return d


def run_replicate(c, e, chunk, offset, o_out, alphas_out, diag):
    from round4_conf_sim import hcp_q, ghcp_q, restricted_pool
    import round4_conf_sim as SIM
    import round5_conf_w1_sim as W1
    R = c.R
    EXP, DH, BH, SC, SH = R["EXP"], R["DH"], R["BH"], R["SC"], R["SH"]
    eid = e + 1
    base_seed = R["LCH"].BASE_SEED
    K = c.K
    cal, test = draw_replicate(c)
    U_cal, Z_cal = cal["U_calibration"], cal["Z_calibration"]
    U_test, Z_test, N_test = test["U_test"], test["Z_test"], test["N_test"]
    assert N_test >= TARGET_INDEX + 1
    N = np.array([len(z) for z in Z_cal])
    sample_sizes = [len(zg) for zg in Z_cal]
    train_idx, calib_idx = DH.get_hcp_train_cal_split(sample_sizes=sample_sizes, o_observed=0,
                                                      alpha_selection=ALPHA_SELECTION)
    model_b = c.mu_baseline["fit_global"](U_matrix=U_cal, Z_list=Z_cal, group_index_vector=train_idx)
    scores_list = []
    for j in calib_idx:
        Zj, Uj = Z_cal[j], U_cal[j, :]
        yj = np.array([z["Y"] for z in Zj])
        Xj = np.array([z["X"] for z in Zj])
        muj = np.array([c.mu_baseline["predict_global"](model_b, Xj[i], Uj) for i in range(len(Xj))])
        scores_list.append(SC.absolute_residual_score(yj, muj))
    T_hcp = {a: BH.compute_hcp_interval_radius(
        scores_list, a, quantile_mode="deterministic",
        random_seed=SC.make_quantile_seed(base_seed, eid, TARGET_INDEX, 0, "hcp")) for a in LAUNCHER_ALPHAS}
    y_t = Z_test[TARGET_INDEX]["Y"]
    X_t = Z_test[TARGET_INDEX]["X"]
    mu_b_hat = c.mu_baseline["predict_global"](model_b, X_t, U_test[0, :])
    base = dict(design=c.design, K=K, chunk=chunk, experiment=eid + offset)
    rows = []
    abs_scores = [np.abs(s) for s in scores_list]
    for a in alphas_out:
        T = T_hcp[a]
        lo, hi = (mu_b_hat - T, mu_b_hat + T) if np.isfinite(T) else (-np.inf, np.inf)
        rows.append(interval_row(base, a, 0, "released_hcp", lo, hi, y_t))
    fit_cache = {}
    for o in LAUNCHER_O:
        if o in o_out:
            res = DH.compute_donor_hcp_randomized_interval(
                U_calibration=U_cal, Z_calibration=Z_cal, U_test=U_test, Z_test=Z_test,
                o_observed=o, alpha=LAUNCHER_ALPHAS[0], alpha_selection=ALPHA_SELECTION,
                mu_method=c.mu_hcp, test_index_target=TARGET_INDEX, quantile_mode="deterministic",
                quantile_random_seed=SC.make_quantile_seed(base_seed, eid, TARGET_INDEX, o, "donor_hcp"),
                alphas=list(LAUNCHER_ALPHAS), return_intermediates=bool(diag))
            x_hist = np.array([Z_test[i]["X"] for i in range(o)])
            y_hist = np.array([Z_test[i]["Y"] for i in range(o)])
            # this track's pool, global forest, residual stream
            rng_a = np.random.default_rng(crc(f"W2|{c.design}|K{K}|c{chunk}|e{e}|o{o}"))
            pool = restricted_pool(N, o, ETA, copy.deepcopy(rng_a), "paper")
            S_comp = np.setdiff1d(np.arange(K), pool) if len(pool) else np.arange(K)
            key = tuple(S_comp.tolist())
            if key not in fit_cache:
                model = c.mu_hcp["fit_global"](U_matrix=U_cal, Z_list=Z_cal,
                                               group_index_vector=list(S_comp)) if len(S_comp) else None
                fit_cache[key] = (model,) + residuals(c, model, U_cal, Z_cal, U_test, Z_test)
            model, cal_res, e_test = fit_cache[key]
            mu_t = c.mu_hcp["predict_global"](model, X_t, U_test[0, :])
            e_t = y_t - mu_t
            init = e_test[:o]
            n_glob = len(S_comp)
            for a in alphas_out:
                ra = res["by_alpha"][a]["interval"]
                rows.append(interval_row(base, a, o, "released_ghcp", ra[0], ra[1], y_t,
                                         donor=res["by_alpha"][a].get("donor_group_index"),
                                         pool_size=res["by_alpha"][a].get("number_selected_groups")))
                lo, hi = EXP._compute_std_cp_interval(
                    x_hist=x_hist, y_hist=y_hist, x_target=X_t, alpha=a, quantile_mode="randomized",
                    random_seed=SC.make_quantile_seed(base_seed, eid, TARGET_INDEX, o, "stdcp"),
                    rng=np.random.default_rng(SC.make_quantile_seed(base_seed, eid, TARGET_INDEX, o, "stdcp_split")))
                rows.append(interval_row(base, a, o, "released_stdcp", lo, hi, y_t))
                T = T_hcp[a]
                qh = hcp_q(abs_scores, a)
                lo, hi = (mu_b_hat - qh, mu_b_hat + qh) if np.isfinite(qh) else (-np.inf, np.inf)
                rows.append(interval_row(base, a, o, "hcp", lo, hi, y_t,
                                         released_finite=int(np.isfinite(T))))
                q, cen = ghcp_q(cal_res, init, o, a, copy.deepcopy(rng_a), True, ETA, n_glob, "paper")
                lo, hi = (mu_t + cen - q, mu_t + cen + q) if np.isfinite(q) else (-np.inf, np.inf)
                rows.append(interval_row(base, a, o, "ghcp", lo, hi, y_t, pool_size=len(pool),
                                         n_glob=n_glob))
            if o > 0:
                exp_cov = {a: math.ceil((o + 1) * (1 - a) - 1e-9) / (o + 1) for a in alphas_out}
                rep = {"init": init, "test": np.array([e_t])}
                wp = W1.f_within_plain(None, rep, None, o, None, list(alphas_out))["within_plain"]
                n0 = len(W1._WF_LOG)
                wf = W1.f_within_full(None, rep, None, o, None, list(alphas_out))["within_full"]
                logs = W1._WF_LOG[n0:]
                for a, p, f, lg in zip(alphas_out, wp, wf, logs):
                    q, cen = p
                    lo, hi = (mu_t + cen - q, mu_t + cen + q) if np.isfinite(q) else (-np.inf, np.inf)
                    rows.append(interval_row(base, a, o, "within_plain", lo, hi, y_t,
                                             expected_cov=exp_cov[a]))
                    q, cen = f
                    lo, hi = (mu_t + cen - q, mu_t + cen + q) if np.isfinite(q) else (-np.inf, np.inf)
                    rows.append(interval_row(base, a, o, "within_full", lo, hi, y_t,
                                             expected_cov=exp_cov[a], exact_cov=lg[2],
                                             is_interval=int(lg[3])))
                del W1._WF_LOG[:]
            if diag and len(res["intermediates"]["S_tilde"]) > 0:
                ims = res["intermediates"]
                S_t, donor, S_c = ims["S_tilde"], ims["donor"], ims["S_comp"]
                model_r = c.mu_hcp["fit_global"](U_matrix=U_cal, Z_list=Z_cal,
                                                 group_index_vector=list(S_c)) if len(S_c) else None
                cal_r, e_test_r = residuals(c, model_r, U_cal, Z_cal, U_test, Z_test)
                sub = [cal_r[j] for j in S_t]
                J0 = int(list(S_t).index(donor))
                for a in alphas_out:
                    q, cen = ghcp_q(sub, e_test_r[:o], o, a, np.random.default_rng(1), True, 0.0,
                                    len(S_c), "paper", J0=J0)
                    ra = res["by_alpha"][a]["interval"]
                    rel_half = (ra[1] - ra[0]) / 2.0 if np.isfinite(ra[0]) and np.isfinite(ra[1]) else math.inf
                    rel_c = (ra[1] + ra[0]) / 2.0 if np.isfinite(ra[0]) and np.isfinite(ra[1]) else math.nan
                    mu_r = c.mu_hcp["predict_global"](model_r, X_t, U_test[0, :])
                    rows.append(row(base, a, o, "diag_ghcp_codepool_residual_form", q,
                                    abs(y_t - (mu_r + cen)) <= q if np.isfinite(q) else True,
                                    released_half=rel_half, centre_diff=(mu_r + cen) - rel_c
                                    if np.isfinite(rel_c) else math.nan))
        for _a in LAUNCHER_ALPHAS:
            emulate_sr_draws(R, N, K, o)
    return rows


def selftest(R, design, K):
    """The stream after the released S-HCP call equals the stream after the emulation."""
    c = make_ctx(R, design, K)
    install_generators(c)
    np.random.seed(R["LCH"].BASE_SEED)
    cal, test = draw_replicate(c)
    U_cal, Z_cal, U_test, Z_test = cal["U_calibration"], cal["Z_calibration"], test["U_test"], test["Z_test"]
    N = np.array([len(z) for z in Z_cal])
    out = []
    for o in (0, 5, 10, 20, 35):
        s0 = np.random.get_state()
        R["SH"].compute_sample_hcp_randomized_interval(
            U_calibration=U_cal, Z_calibration=Z_cal, U_test=U_test, Z_test=Z_test, o_observed=o,
            alpha=0.1, alpha_selection=ALPHA_SELECTION, mu_method=c.mu_hcp, test_index_target=TARGET_INDEX,
            quantile_mode="deterministic")
        s1 = np.random.get_state()
        np.random.set_state(s0)
        emulate_sr_draws(R, N, c.K, o)
        s2 = np.random.get_state()
        out.append((o, state_equal(s1, s2), state_equal(s0, s1)))
        np.random.set_state(s1)
    return out


def write_prov(a, R, IO5, what):
    gc = os.path.abspath(a.ghcp_code)
    extra = {"ghcp_commit": IO5.clone_head(gc), "wrapper_md5": IO5.md5(os.path.abspath(__file__)),
             "wrapper_path": os.path.abspath(__file__), "R5CONF_FRAME_ID": os.environ.get("R5CONF_FRAME_ID", ""),
             "sklearn": __import__("sklearn").__version__, "what": what,
             "released_experiments_md5": IO5.md5(R["EXP"].__file__),
             "released_donor_hcp_md5": IO5.md5(R["DH"].__file__),
             "released_sample_hcp_md5": IO5.md5(R["SH"].__file__),
             "released_launcher_md5": IO5.md5(R["RFL"].__file__)}
    IO5.write_provenance(a.out, "W2p1_" + what, os.path.abspath(__file__), vars(a), extra=extra)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--ghcp-code", required=True)
    p.add_argument("--design", required=True, choices=sorted(CHUNK_SIZE))
    p.add_argument("--chunks", default="all")
    p.add_argument("--k", type=int, default=20)
    p.add_argument("--o-values", default=",".join(map(str, PAPER_O)))
    p.add_argument("--alphas-out", default="0.1,0.2")
    p.add_argument("--max-reps", type=int, default=0)
    p.add_argument("--diag-reps", type=int, default=0)
    p.add_argument("--total-replicates", type=int, default=1000)
    p.add_argument("--selftest", action="store_true")
    p.add_argument("--out", required=True)
    a = p.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    import round5_conf_io as IO5
    IO5.stamp(a.out, "W2 part 1", "wrapper run, design %s, K %d, chunks %s" % (a.design, a.k, a.chunks))
    os.environ["HCP_PLOTS_MARGINAL"] = os.path.join(a.out, "scratch_paper_results")
    os.environ["HCP_RESULTS_MARGINAL"] = os.path.join(a.out, "scratch_results")
    R = load_released(a.ghcp_code)
    if a.selftest:
        res = selftest(R, a.design, a.k)
        pd.DataFrame(res, columns=["o", "stream_equal_after_emulation", "stream_unchanged_by_call"]).to_csv(
            os.path.join(a.out, "w2_rng_selftest.csv"), index=False)
        print(res)
        write_prov(a, R, IO5, "selftest")
        return 0 if all(r[1] for r in res) else 6
    o_out = tuple(int(x) for x in a.o_values.split(","))
    alphas_out = tuple(float(x) for x in a.alphas_out.split(","))
    assert set(alphas_out) <= set(LAUNCHER_ALPHAS) and set(o_out) <= set(LAUNCHER_O)
    c = make_ctx(R, a.design, a.k)
    n_chunks = int(np.ceil(a.total_replicates / CHUNK_SIZE[a.design]))
    sizes = R["LCH"].split_counts(a.total_replicates, n_chunks)
    offsets = np.cumsum([0] + sizes[:-1]).tolist()
    chunks = list(range(n_chunks)) if a.chunks == "all" else [int(x) for x in a.chunks.split(",")]
    allrows = []
    t0 = time.time()
    for ch in chunks:
        np.random.seed(R["LCH"].BASE_SEED + 1000 * ch)
        install_generators(c)
        n = sizes[ch] if not a.max_reps else min(a.max_reps, sizes[ch])
        for e in range(n):
            allrows += run_replicate(c, e, ch, offsets[ch], o_out, alphas_out, diag=(e < a.diag_reps))
            if (e + 1) % 10 == 0:
                print(f"chunk {ch} replicate {e + 1}/{n}  {time.time() - t0:.0f}s", flush=True)
        df = pd.DataFrame([r for r in allrows if r["chunk"] == ch])
        df.to_csv(os.path.join(a.out, f"w2_wrapper_rows__{a.design}__K{a.k}__chunk{ch:02d}.csv"), index=False)
    write_prov(a, R, IO5, "wrapper")
    return 0


if __name__ == "__main__":
    sys.exit(main())
