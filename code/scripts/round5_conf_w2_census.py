#!/usr/bin/env python
"""Round 5 W2 part 2, item 4: the released census experiment with within_plain and within_full added.

docs/round5_conf_plan.md section 2, W2 part 2.

WHAT THIS DOES. It imports the released pipeline (GHCP code, commit d1a69f4a, unmodified, read from
/work/users/w/e/weiyang/hest_code/ghcp_code) and calls its own replicate function,
code.marginal.run_acs_experiments.run_one_replicate, once per replicate with the config that
run_acs_experiments.py's main() builds for the round-4 command line. So the PUMA draw
(seed 456 + 1009 b), the row permutation (456 + 1009 b + 811), the train/calibration split, every
random-number key, the GHCP interval (released name Donor-HCP), the HCP interval (released name HCP,
computed once at o = 0 and constant in o) and the Std-CP interval (studentized, randomized, as the
released recompute_acs_stdcp_randomized_min21.py computes it) are the released ones. Nothing is
re-implemented for those three. The only things set from outside are the number of calibration PUMAs
(config n_puma_groups, the released --n_puma_groups) and the list of o.

THE ADDED METHODS, assumptions and guarantee written before any run (docs/decisions/
round5_conformal_track.md section 2.3; round5_conf_w1_sim.py docstring).
 Score. The score is the released GHCP/HCP absolute residual |y - mu|. mu is the released global
 random forest of the HCP baseline, fitted by the released fit_global on the replicate's HCP training
 split of the calibration PUMAs (the model that HCP's own scores use). Labelled residuals are
 r_i = y_i - mu(x_i) for the first o rows of the permuted target PUMA, the target's residual is
 y_t - mu(x_t) at the released fixed index (default 20).
 within_plain  split conformal on |r_1|..|r_o|, uncentred. Assumes the o labelled rows and the target
               row are exchangeable inside the target PUMA, which the released row permutation makes
               true. Guarantee: coverage >= 1 - alpha, exactly ceil((o+1)(1-alpha))/(o+1) with
               distinct scores. Finite iff o >= (1-alpha)/alpha (o >= 9 at 0.1, o >= 4 at 0.2).
               Computed by round5_conf_w1_sim.f_within_plain.
 within_full   full conformal inside the PUMA with the mean as fitted model. Same assumption and the
               same expected coverage ceil((o+1)(1-alpha))/(o+1). Finite iff alpha(o+1) >= 1.
               Computed by round5_conf_w1_sim.f_within_full and wf_* (convex hull of the kept set;
               the exact set's coverage of the target and whether the set is one interval are recorded).
 Intervals are mu(x_t) + [centre - q, centre + q] in dollars (outcome scale income).
 Expected coverage of both within methods: ceil((o+1)(1-alpha))/(o+1), column expected_cov.
 Released methods: HCP is valid for any K; GHCP is valid under the paper's A1 to A3 with exchangeable
 PUMAs and rows; Std-CP is the paper's within-group split (studentized local RF), valid, finite only
 when the o/2 calibration rows allow it.

USAGE (one alpha and one number of calibration PUMAs per call; run from the job's own directory)
  python round5_conf_w2_census.py --alpha 0.1 --n-puma 20 --o 0,2,5,8,9,10,12,15,17,20 --B 1000 \
      --workers 4 --acs-csv <acs_data_all50states.csv> --out <dir> [--check-against <released detailed.csv>]
  --rep-from/--rep-to run a chunk of replicates; concatenate the *_detailed_* files and rerun summarize to merge.
"""
import argparse, hashlib, json, math, os, sys, time
import multiprocessing as mp
import numpy as np
import pandas as pd

# round4_conf_sim imports pyarrow only for its output schema; the released pipeline's venv has no pyarrow.
# numpy, pandas, scipy and scikit-learn stay those of the released venv; the project env's site-packages
# (same Python 3.11, same numpy 2.4.6) is appended AFTER them so that only pyarrow is taken from it.
HEST_SP = "/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/lib/python3.11/site-packages"
try:
    import pyarrow  # noqa: F401
except ImportError:
    sys.path.append(HEST_SP)
    import pyarrow  # noqa: F401
GHCP_ROOT = os.environ.get("GHCP_ROOT", "/work/users/w/e/weiyang/hest_code/ghcp_code")
O_GRID = (0, 2, 5, 8, 9, 10, 12, 15, 17, 20)
sys.path.insert(0, GHCP_ROOT)
sys.path.insert(0, os.path.join(GHCP_ROOT, "real_data"))
from code.marginal import run_acs_experiments as acs            # noqa: E402  (released, unmodified)
from acs.data_processing import build_design_matrix_acs, load_and_clean_acs_pums  # noqa: E402
import round4_conf_sim as SIM                                   # noqa: E402  (round 4, unmodified)
import round5_conf_w1_sim as W1                                 # noqa: E402  (round 5 W1, unmodified)
import round5_conf_io as IO                                     # noqa: E402

_G = None


def md5f(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def exp_cov(o, alpha):
    return math.ceil((o + 1) * (1 - alpha) - 1e-12) / (o + 1)


def build_config(args, o_values, eligible):
    """The config main() of run_acs_experiments.py builds for the round-4 command line."""
    return {
        "B": args.B, "seed": 456, "alpha": args.alpha, "alpha_selection": 0.5,
        "quantile_mode": "deterministic", "stdcp_quantile_mode": "randomized",
        "quantile_base_seed": 456, "n_repeated": 50, "n_puma_groups": args.n_puma,
        "n_calib_per_stratum": 5, "o_values": o_values, "eligible_groups": eligible,
        "n_workers": args.workers, "design": "uniform_one_target",
        "fixed_calib_groups": None, "fixed_test_groups": None, "truncate_n": None,
        "within_group": True, "permute_rows": True,
        "skip_stdcp": bool(args.skip_stdcp), "stdcp_o_values": None,
        "min_calib_puma_size": 21, "predictor": "rf", "pretrained_model": None,
        "outcome_scale": "income", "within_group_mode": "mean",
        "drop_top_income_fraction": 0.0, "yoep_min_year": 2000, "min_income": None,
        "stdcp_center": "local", "score_type": "absolute", "stdcp_score_type": "studentized",
        # a non-empty cache_dir makes run_one_replicate return the replicate's group data and HCP split
        # in result['_cache']; nothing is written to it (the released writer is not called here)
        "cache_dir": "unused",
    }


def load_cohort(csv):
    acs._set_target_index(20)
    df = load_and_clean_acs_pums(csv, states_keep=["CA"], age_min=25, age_max=54, yoep_min_year=2000,
                                 min_hours=40, min_income=None, drop_top_income_fraction=None,
                                 y_transform=acs._outcome_transform("income"))
    df = df.dropna(subset=["puma"]).copy()
    df["puma"] = df["puma"].astype(int)
    X = build_design_matrix_acs(df, exclude_entry_recency=True, exclude_cow=True, exclude_hours=False)
    counts = df.groupby("puma").size()
    eligible = counts[counts >= 21].index.to_numpy().tolist()
    share = acs.compute_group_share_baplus(df, "puma")
    strata = acs._build_share_baplus_strata(eligible_groups=eligible, group_share_baplus=share, n_strata=5)
    return df, X, eligible, strata, counts


def one_rep(b):
    df, X, eligible, strata, cfg, o_values, alpha = _G
    res = acs.run_one_replicate(df, X, eligible, strata, "puma", o_values, cfg, b)
    if res is None:
        return b, None
    rows = []
    T = acs.TARGET_INDEX
    cache = res.pop("_cache", None)

    def rec(method, o, r, extra=None):
        d = dict(replicate=b, alpha=alpha, n_puma=cfg["n_puma_groups"], o=o, method=method,
                 coverage=r["coverage"], width=r["width"], lower=r["lower"], upper=r["upper"],
                 finite=bool(np.isfinite(r["width"])), exact_cov=np.nan, is_interval=np.nan,
                 expected_cov=np.nan)
        if extra:
            d.update(extra)
        rows.append(d)

    h0 = res["baseline"]["HCP"].get(0)
    for o in o_values:
        if h0 is not None:
            rec("HCP", o, h0)
        g = res["hcp"]["Donor-HCP"].get(o)
        if g is not None:
            rec("GHCP", o, g)
        s = res["stdcp"]["Std-CP"].get(o)
        if s is not None and not cfg["skip_stdcp"]:
            rec("Std-CP", o, s)
    if cache is None:
        return b, rows
    # ---- the within-PUMA methods, on the released HCP global model's residuals ----
    gd = acs._deserialize_group_data(cache["group_data"])
    calib, test = cache["calib_groups"], cache["test_group"]
    Zc = [[{"X": gd[g]["X"][i], "Y": gd[g]["Y"][i]} for i in range(len(gd[g]["Y"]))] for g in calib]
    Uc = np.zeros((len(calib), 1))
    mu_b = acs._make_mu_baseline(cfg)
    model = mu_b["fit_global"](U_matrix=Uc, Z_list=Zc, group_index_vector=cache["baseline_split"]["train_idx"])
    u0 = np.zeros((1, 1))[0]
    Xt, Yt = gd[test]["X"], gd[test]["Y"]
    mu_t = float(mu_b["predict_global"](model, Xt[T], u0))
    true_y = float(Yt[T])
    r_t = true_y - mu_t
    mu_lab = np.array([float(mu_b["predict_global"](model, Xt[i], u0)) for i in range(max(o_values))])
    r_all = Yt[:max(o_values)] - mu_lab
    for o in o_values:
        if o == 0 or len(Yt) <= max(o, T):
            continue
        init = r_all[:o]
        rep = {"init": init, "test": np.array([r_t])}
        qp = W1.f_within_plain(None, rep, None, o, None, [alpha])["within_plain"][0]
        q = qp[0]
        iv = (mu_t - q, mu_t + q)
        r = acs._result_record(iv, true_y, outcome_scale="income")
        rec("within_plain", o, r, dict(expected_cov=exp_cov(o, alpha)))
        W1._WF_LOG.clear()
        qf = W1.f_within_full(None, rep, None, o, None, [alpha])["within_full"][0]
        _, _, exact, isint = W1._WF_LOG[-1]
        q, c = qf
        iv = (mu_t + c - q, mu_t + c + q) if np.isfinite(q) else (-np.inf, np.inf)
        r = acs._result_record(iv, true_y, outcome_scale="income")
        rec("within_full", o, r, dict(expected_cov=exp_cov(o, alpha), exact_cov=float(exact), is_interval=bool(isint)))
    return b, rows


def summarize(D):
    out = []
    for (m, o), g in D.groupby(["method", "o"]):
        w = g.width.astype(float)
        fin = np.isfinite(w)
        cov = float(g.coverage.mean())
        out.append(dict(method=m, o=o, alpha=g.alpha.iloc[0], n_puma=g.n_puma.iloc[0], n_rep=len(g),
                        coverage=cov, coverage_se=math.sqrt(max(cov * (1 - cov), 0) / len(g)),
                        finite_n=int(fin.sum()), width_mean_finite=float(w[fin].mean()) if fin.any() else np.nan,
                        width_median_finite=float(w[fin].median()) if fin.any() else np.nan,
                        expected_cov=float(g.expected_cov.iloc[0]) if g.expected_cov.notna().any() else np.nan,
                        exact_cov_mean=float(g.exact_cov.mean()) if g.exact_cov.notna().any() else np.nan,
                        interval_share=float(g.is_interval.astype(float).mean()) if g.is_interval.notna().any() else np.nan))
    return pd.DataFrame(out).sort_values(["method", "o"]).reset_index(drop=True)


def check(D, released_csv, stdcp_csv, out):
    """GHCP and HCP (and Std-CP when given) per replicate against the released run's detailed CSV."""
    R = pd.read_csv(released_csv)
    rows = []
    maps = {"GHCP": "Donor-HCP", "HCP": "HCP"}
    parts = [(R, maps)]
    if stdcp_csv and os.path.exists(stdcp_csv):
        parts.append((pd.read_csv(stdcp_csv), {"Std-CP": "Std-CP"}))
    for RR, mp_ in parts:
        for mine, rel in mp_.items():
            a = D[D.method == mine]
            b = RR[RR.method == rel]
            m = a.merge(b, on=["replicate", "o"], suffixes=("", "_rel"))
            if mine == "HCP":
                m = m[m.o == 0]            # the released run stores HCP at o = 0 only
            for o, g in m.groupby("o"):
                cov_eq = bool((g.coverage.astype(float).values == g.coverage_rel.astype(float).values).all())
                w, wr = g.width.astype(float).values, g.width_rel.astype(float).values
                both_inf = np.isinf(w) & np.isinf(wr) & (np.sign(w) == np.sign(wr))
                d = np.where(both_inf, 0.0, np.abs(w - wr))
                d = np.where(np.isnan(w) & np.isnan(wr), 0.0, d)
                rel = np.where(both_inf, 0.0, d / np.maximum(np.abs(wr), 1e-300))
                rows.append(dict(method=mine, o=o, n_pairs=len(g), n_rep_mine=int((a.o == o).sum()),
                                 n_rep_released=int((b.o == o).sum()), coverage_identical=cov_eq,
                                 max_abs_width_diff=float(np.nanmax(d)) if len(d) else np.nan,
                                 max_rel_width_diff=float(np.nanmax(rel)) if len(d) else np.nan,
                                 width_ok_abs_1e9=bool((d <= 1e-9).all()),
                                 width_ok_rel_1e9=bool((rel <= 1e-9).all())))
    C = pd.DataFrame(rows)
    C.to_csv(out, index=False)
    return C


def main(argv=None):
    global _G
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--alpha", type=float, required=True)
    p.add_argument("--n-puma", type=int, default=20)
    p.add_argument("--o", default=",".join(map(str, O_GRID)))
    p.add_argument("--B", type=int, default=1000)
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--rep-from", type=int, default=0, help="first replicate index (chunking; seeds depend on the index only)")
    p.add_argument("--rep-to", type=int, default=None, help="one past the last replicate index (default B)")
    p.add_argument("--acs-csv", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--skip-stdcp", action="store_true")
    p.add_argument("--check-against", default=None, help="released acs_true_marg_alpha*_detailed.csv")
    p.add_argument("--check-stdcp", default=None, help="released stdcp_studentized_randomized_*_detailed.csv")
    a = p.parse_args(argv)
    o_values = sorted(set(int(v) for v in a.o.split(",")))
    bad = [o for o in o_values if o not in O_GRID]
    assert not bad, f"o outside the W2 grid {O_GRID}: {bad}"
    os.makedirs(a.out, exist_ok=True)
    IO.stamp(a.out, "round5-conformal W2 part2", f"census wrapper alpha={a.alpha} n_puma={a.n_puma}")
    print("selftest within_full:", W1.selftest_within_full(), flush=True)
    df, X, eligible, strata, counts = load_cohort(a.acs_csv)
    print(f"cohort rows {len(df)}, PUMAs {len(counts)}, eligible (>=21) {len(eligible)}", flush=True)
    cfg = build_config(a, o_values, eligible)
    _G = (df, X, eligible, strata, cfg, o_values, a.alpha)
    rep_to = a.B if a.rep_to is None else a.rep_to
    t0, rows, nnone = time.time(), [], 0
    with mp.get_context("fork").Pool(a.workers) as pool:
        for i, (b, r) in enumerate(pool.imap_unordered(one_rep, range(a.rep_from, rep_to)), 1):
            if r is None:
                nnone += 1
            else:
                rows.extend(r)
            if i % 100 == 0 or i == rep_to - a.rep_from:
                print(f"  {i}/{rep_to - a.rep_from}  {time.time() - t0:.0f}s", flush=True)
    D = pd.DataFrame(rows).sort_values(["method", "o", "replicate"]).reset_index(drop=True)
    tag = f"alpha{int(round(a.alpha * 100)):02d}_K{a.n_puma}" + ("" if (a.rep_from == 0 and rep_to == a.B) else f"_r{a.rep_from}-{rep_to}")
    D.to_csv(os.path.join(a.out, f"w2_census_detailed_{tag}.csv"), index=False)
    S = summarize(D)
    S.to_csv(os.path.join(a.out, f"w2_census_summary_{tag}.csv"), index=False)
    print(S.to_string(), flush=True)
    chk = None
    if a.check_against:
        chk = check(D, a.check_against, a.check_stdcp, os.path.join(a.out, f"w2_census_check_{tag}.csv"))
        print(chk.to_string(), flush=True)
    released = [os.path.join(GHCP_ROOT, "code", "marginal", "run_acs_experiments.py"),
                os.path.join(GHCP_ROOT, "real_data", "acs", "data_processing.py"),
                os.path.join(GHCP_ROOT, "methods", "donor_hcp.py"), os.path.join(GHCP_ROOT, "scores.py")]
    IO.write_provenance(a.out, "W2p2_census", os.path.abspath(__file__),
                        {k: v for k, v in vars(a).items()},
                        extra=dict(input_csv_md5=md5f(a.acs_csv), replicates_none=nnone, runtime_s=round(time.time() - t0),
                                   released_md5s=json.dumps({os.path.relpath(q, GHCP_ROOT): md5f(q) for q in released}),
                                   pyarrow_from=pyarrow.__file__, numpy_from=np.__file__, pandas_version=pd.__version__, check_rows=("none" if chk is None else len(chk))))
    return D, S, chk


if __name__ == "__main__":
    main()
