#!/usr/bin/env python
"""Round 3, stage A4b: HCP with K = 10 exchangeable donors on CCRCC.

Stage: A4b (round3_execution_plan.md section 13.5.2, which transcribes
docs/decisions/round3_A3_decisions.md section 5.2; prediction 5 of the memo's section 10).
K = 10 is fixed by section 13.8 and is not a session choice. Section 13.10 item 1 governs the
training-size statement and the INT4/INT24 merge; section 13.10 item 2 governs the donor
grouping source.

THIS SCRIPT EDITS NEITHER round3_a0_harness.py NOR round3_a3_weighted.py. It imports both as
modules from the scripts directory and reuses them unchanged:

  from the harness  load_task, fit_base, choose_calibration, build_fold_specs,
                    size_match_groups, apply_size_match, unit_labels, conformal_quantile,
                    unit_hierarchy and the constants;
  from A3           weighted_quantile (with its QTOL = 1e-12 threshold tolerance), w3_weights,
                    n_eff, cell_metrics, fold_summary and harness_args.

So the HCP interval here is A3's W3 code path by construction rather than by copy, and every
A4b fold is an A1 fold because the enumeration is the harness's own.

REPRODUCING A1'S SPLITS. size_match_groups takes one n_match per task over every design
requested in the run, so the enumeration mirrors A1's main invocation for this task:
--designs random,patient,donor. n_match is then checked against A1's committed
n_match_target in a1_calibration_units__<enc>__main.csv before anything is fitted, and the
K = 10 specs are given that same n_match, so no arm is size-matched to a different target.
A1's slide_out invocation did not include CCRCC, so it is not mirrored.

THE TWO DONOR SETS (section 13.3, section 13.5.2).
  24          the 24 benchmark_r2 donors of results/round3/D3_audit/donor_audit_r3.csv. The
              script asserts row by row that those 24 rows agree with the CCRCC task
              definition's donor_id, so the grouping source is checked, not assumed. The
              expansion_d3 rows for the same 24 samples say `unverifiable` (section 13.10
              item 2); per that item benchmark tasks group by the benchmark_r2 rows and no
              status is chosen between them here.
  23_merged   INT4 and INT24 merged into one donor unit `INT4+INT24`. The donor folds are
              rebuilt by the same rule the task definition used (one held-out donor unit per
              fold, every other sample in the pool); the rule is verified by rebuilding the
              24-donor folds with it and asserting they equal the shipped ones. Pool 22,
              10 calibration, 12 training (section 13.10 item 1).

THE ARMS.
  a1_rule_K6  the anchor. Calibration by A1's own rule, 25% of the pool's donors, which is
              K = ceil(0.25 * 23) = 6 on the 24-donor set. Run on donor_set 24 only. Its
              pooled-quantile per-fold coverage must reproduce
              a1_by_fold__<enc>__main.csv's CCRCC donor `abs` rows.
  K10         K = 10 calibration donors, the rest training. Both donor sets.
  random      the control, A1's `random` design unchanged: the calibration unit is the spot,
              so K = n_C and HCP must coincide with the pooled quantile exactly.

HOW K = 10 IS OBTAINED WITHOUT TOUCHING THE HARNESS. choose_calibration takes k =
max(1, ceil(cal_frac_units * n_units)), so it is called with cal_frac_units =
(K - 0.5) / n_units, whose ceiling is K for any n_units > K. Passing K/n_units directly would
be wrong: 10/23 * 23 evaluates to 10.000000000000002 in binary floating point and its ceiling
is 11. The seed key and draw index are the harness's own, f"{task}|donor|{fold}" with
crc32(f"{key}|cal{draw}"), so the K = 10 calibration set at draw d is the first ten of the
SAME donor permutation whose first six are A1's calibration set at draw d. A1's calibration
donors are therefore nested in A4b's, which the anchor table checks on every fold and draw;
the two arms differ in which donors train, not in how they were drawn.

THE FOUR INTERVALS, alpha = 0.10, score `abs` (section 13.5.2). Difference list first: all
four use the same fold, the same proper-training set T, the same base head fitted on T, the
same calibration spots C and the same test spots E. They differ only in what is done with
C's scores.
  pooled  A1's pooled spot-level conformal quantile: the ceil((n_C+1)(1-alpha))/n_C order
          statistic of the pooled calibration scores, ignoring which donor a score came from.
          Computed with the harness's own conformal_quantile, and checked against A3's
          weighted_quantile at equal weights in the anchor table, so the two code paths are
          shown to agree rather than assumed to.
  hcp     A3's W3: calibration spot i in donor k with N_k spots carries w_i = 1/N_k and the
          test point carries 1, so each of the K calibration donors and the test point holds
          1/(K+1) of the normalised mass. Sees the donor structure of C and no features. The
          level is attainable exactly when K + 1 >= 1/alpha, which is why K = 10 is the
          experiment and K = 6 is not: at K = 6 the interval is infinite and is RECORDED as
          infinite, never replaced by a finite one.
  dwr     Dunn, Wasserman and Ramdas: one calibration spot per donor drawn at random, giving
          K exchangeable scores which with the test point make K + 1 = 11, and the ordinary
          conformal quantile of those K scores. 200 repetitions with crc32 seeds; the width
          is averaged over repetitions and the coverage is reported per repetition in
          a4b_one_per_group_reps.csv so its dispersion is visible, with the mean and standard
          deviation over repetitions in the main table. On the `random` design each unit is a
          single spot, so the subsample is the whole calibration set and the repetition is
          degenerate: one repetition is run there and the equality with `pooled` is what the
          control checks.

THE K COLUMN carries the number of exchangeable units the method's quantile rests on, which
is not the same quantity for all three: n_C for `pooled`, whose scores are spots; the number
of calibration donors for `hcp` and `dwr`. n_cal_units and n_C are carried beside it in every
row so the three are never read off one column.

TRAINING SIZE (section 13.10 item 1). A1's CCRCC donor folds have 23 donors in the pool and
6 in calibration, so they train on 17 donors, not the memo's 18; at K = 10 they train on 13,
and on the merged set on 12. Every row carries n_T_donors beside n_T_spots_natural and
n_T_spots_matched. Because A1 size-matched T within the task, the matched spot count is the
same 35,996 in both arms wherever the natural |T| exceeds it, so the K = 6 to K = 10
comparison is a comparison of donor count at equal spot count, and that is how it is reported.

PEARSON. Per-gene Pearson of prediction against observation pooled over the whole test fold,
then the mean over the task's 50 genes, which is the harness's H1 convention
(round3_a0_harness.py, the args.h1_anchor block). It is a property of (T, E) alone, so it is
identical across the four intervals and is carried once per fold, draw and arm.

PROVENANCE runs no git command: this session is barred from git on both the local clone and
the Longleaf working copy, so the commit is supplied on the command line with --commit and
recorded as supplied. The md5 of every file actually executed (this script, the harness, the
A3 module) is computed inside the job, per the round-3 standing rule.

Outputs under results/round3/A4_scores/, summaries before anything else, every name a4b_*
because the Scores track owns every other name in that directory:
  a4b_anchor__<enc>.csv            the anchor and acceptance checks, written and printed FIRST
  a4b_hcp_K10__<enc>.csv           per (donor_set, arm, fold, draw, method)
  a4b_one_per_group_reps__<enc>.csv  per DWR repetition
  a4b_PROVENANCE__<enc>.txt
and, from --merge, the deliverable names a4b_anchor.csv, a4b_hcp_K10.csv,
a4b_one_per_group_reps.csv; from --figures, fig_a4b_hcp_K10.png; from --summary,
a4b_summary.csv, which holds every pooled number the stage report quotes so that none of them
is retyped from a console.

Usage:
  round3_a4b_hcp.py <encoder> --task-def results/round3/task_defs/CCRCC.json --commit <sha>
  round3_a4b_hcp.py --merge   [--out-root <dir>] [--out-dir <dir>]
  round3_a4b_hcp.py --summary [--out-root <dir>] [--out-dir <dir>]
  round3_a4b_hcp.py --figures [--out-root <dir>] [--out-dir <dir>]

A4B_SCRIPTS_DIR overrides where the harness and the A3 module are imported from; it defaults
to this file's own directory, which is what holds once the script is committed beside them.
"""
import argparse
import hashlib
import importlib.util
import json
import os
import sys
import time
import zlib

import numpy as np
import pandas as pd
from scipy.stats import pearsonr

# ------------------------------------- import the harness and the A3 module, unedited
_HERE = os.path.dirname(os.path.abspath(__file__))
_SCRIPTS = os.environ.get("A4B_SCRIPTS_DIR", _HERE)


def _import(name):
    path = os.path.join(_SCRIPTS, f"{name}.py")
    assert os.path.exists(path), f"{path} not found; set A4B_SCRIPTS_DIR"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


H = _import("round3_a0_harness")
A3 = _import("round3_a3_weighted")

ROOT = H.ROOT
A1DIR = "results/round3/A1_coverage"
AUDIT = "results/round3/D3_audit/donor_audit_r3.csv"

TASK = "CCRCC"
K_TARGET = 10                      # section 13.8: fixed, not a session choice
ALPHA = 0.10
SCORE = "abs"
N_DWR_REPS = 200
MERGE_PAIR = ("INT4", "INT24")
MERGED_ID = "INT4+INT24"
DONOR_SETS = ("24", "23_merged")
METHODS = ("pooled", "hcp", "dwr")

DIFFERENCE_LIST = {
    "pooled": "the pooled spot-level conformal quantile of C's scores; sees no unit "
              "structure at all, so a donor with many spots carries more mass than one with "
              "few. This is A1's interval.",
    "hcp": "A3's W3 weighted quantile with w_i = 1/N_k inside calibration donor k and test "
           "weight 1, so each calibration donor and the test point carries 1/(K+1) of the "
           "mass; sees which donor each calibration spot belongs to and how many spots that "
           "donor has, and no features.",
    "dwr": "one calibration spot per donor, drawn at random, and the ordinary conformal "
           "quantile of those K exchangeable scores; sees the donor partition of C and "
           "discards all but K of its spots, so it buys exchangeability at the cost of "
           "calibration size.",
}

ARM_DIFFERENCE_LIST = {
    "a1_rule_K6": "A1's calibration rule, 25% of the pool's donor units, K = 6 on the "
                  "24-donor set. Identical to A1 in task definition, fold list, seeds, "
                  "enumeration, size-match target, base head and score; this is the anchor "
                  "arm and nothing in it is new.",
    "K10": "identical to the anchor arm in task definition, fold list, seeds, size-match "
           "target, base head and score. It differs in one thing: the calibration set is the "
           "first TEN donors of the same permutation instead of the first six, so four "
           "donors move from T to C and n_T_donors falls from 17 to 13 (12 on the merged "
           "set) at the same matched training-spot count.",
    "random": "A1's `random` design unchanged, where the calibration unit is the spot. K is "
              "the calibration spot count, so HCP's weights are all equal and its interval "
              "must be the pooled one; that equality is the control.",
}


# ------------------------------------------------------------------- arguments
def parse_args(argv):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("encoder", nargs="?", default=None,
                   help="required unless --merge or --figures is given")
    p.add_argument("--task-def", action="append", dest="task_def", default=None)
    p.add_argument("--out-dir", default="results/round3/A4_scores")
    p.add_argument("--out-root", default=ROOT,
                   help="where OUTPUTS go; the data always comes from the harness's ROOT")
    p.add_argument("--tag", default="")
    p.add_argument("--designs", default="random,patient,donor",
                   help="A1's main invocation, mirrored so size matching reproduces A1's "
                        "per-task n_match")
    p.add_argument("--donor-sets", default=",".join(DONOR_SETS))
    p.add_argument("--arms", default="a1_rule_K6,K10,random")
    p.add_argument("--K", type=int, default=K_TARGET)
    p.add_argument("--alpha", type=float, default=ALPHA)
    p.add_argument("--alpha-store", type=float, default=0.20)
    p.add_argument("--n-cal-draws", type=int, default=3)
    p.add_argument("--spot-cal-draws", type=int, default=1)
    p.add_argument("--n-repeats", type=int, default=None)
    p.add_argument("--max-folds", type=int, default=None)
    p.add_argument("--dwr-reps", type=int, default=N_DWR_REPS)
    p.add_argument("--size-match", default="task", choices=("task", "fold", "none"))
    p.add_argument("--a1-dir", default=A1DIR)
    p.add_argument("--audit", default=AUDIT)
    p.add_argument("--commit", default="unrecorded",
                   help="the working copy's HEAD, supplied because this session runs no git "
                        "command")
    p.add_argument("--anchor-tol", type=float, default=1e-12)
    p.add_argument("--merge", action="store_true",
                   help="merge the per-encoder tables into the deliverable names and exit")
    p.add_argument("--figures", action="store_true",
                   help="render fig_a4b_hcp_K10.png from the merged tables and exit")
    p.add_argument("--summary", action="store_true",
                   help="compute every pooled number the report quotes into a4b_summary.csv "
                        "from the merged tables and exit")
    a = p.parse_args(argv)
    if not (a.merge or a.figures or a.summary):
        assert a.encoder, "an encoder is required unless --merge or --figures is given"
        assert a.task_def, "--task-def is required unless --merge or --figures is given"
    return a


# --------------------------------------------------------------- donor grouping
def audit_donor_map(audit_path, task, td):
    """The task's donor grouping, taken from donor_audit_r3.csv's benchmark_r2 rows and
    CHECKED against the task definition row by row rather than assumed to agree.

    Returns (sample -> donor, record dict). The record carries what the expansion_d3 rows say
    about the same samples, which section 13.10 item 2 requires be reported and not chosen
    between.
    """
    d = pd.read_csv(audit_path)
    for c in ("row_origin", "task", "sample_id", "donor_id"):
        assert c in d.columns, f"{audit_path}: no {c} column"
    b = d[(d["row_origin"] == "benchmark_r2") & (d["task"] == task)]
    m = dict(zip(b["sample_id"].astype(str), b["donor_id"].astype(str)))
    tdm = {s["sample_id"]: str(s["donor_id"]) for s in td["samples"]}
    assert set(m) == set(tdm), (f"{audit_path}: benchmark_r2 {task} samples differ from the "
                                f"task definition's")
    bad = {k: (m[k], tdm[k]) for k in tdm if m[k] != tdm[k]}
    assert not bad, f"{audit_path}: donor_id disagrees with the task definition on {bad}"
    same = d[(d["row_origin"] == "expansion_d3")
             & (d["sample_id"].astype(str).isin(m))]
    rec = dict(audit_rows_benchmark_r2=int(len(b)),
               n_donors=int(len(set(m.values()))),
               statuses=";".join(sorted(set(b["donor_label_status"].astype(str)))),
               expansion_d3_rows_for_same_samples=int(len(same)),
               expansion_d3_statuses=";".join(
                   sorted(set(same["donor_label_status"].astype(str)))) or "none")
    return m, rec


def donor_folds(donor_of, sample_ids):
    """One held-out donor unit per fold, every other sample in the pool: the rule the task
    definition's `donor` folds follow. Rebuilt here so the merged set's folds are built by the
    same rule, and verified against the shipped folds on the unmerged set."""
    groups = {}
    for s in sorted(sample_ids):
        groups.setdefault(donor_of[s], []).append(s)
    out = []
    for d in sorted(groups):
        test = sorted(groups[d])
        out.append(dict(fold=str(d), test=test,
                        train=sorted(s for s in sample_ids if s not in test)))
    return out


# ------------------------------------------------------------------- enumeration
def a1_enumeration(td, samp, xy, meta, args, designs):
    """A1's specs for this task, and the per-task n_match they imply."""
    hargs = A3.harness_args(args, designs)
    specs = H.build_fold_specs(td, samp, xy, designs, meta, hargs)
    H.size_match_groups(specs, args.size_match)
    nm = {s["n_match"] for s in specs}
    assert len(nm) == 1, f"more than one n_match for {td['task']}: {sorted(nm)}"
    return specs, int(nm.pop())


def k_specs(td, samp, xy, meta, folds, K, n_match, args):
    """The K-donor calibration specs, built with the harness's own choose_calibration on the
    harness's own seed key, with cal_frac_units set so that its ceiling is exactly K."""
    of_sample = {s: (samp == s) for s in np.unique(samp)}

    def mask_of(ids):
        m = np.zeros(len(samp), bool)
        for s in ids:
            m |= of_sample[s]
        return m

    task = td["task"]
    specs = []
    fl = folds[:args.max_folds] if args.max_folds else folds
    for fd in fl:
        E, pool = mask_of(fd["test"]), mask_of(fd["train"])
        assert not (E & pool).any(), f"{task} donor {fd['fold']}: train/test overlap"
        n_units = len({meta["donor_of"][s] for s in fd["train"]})
        assert n_units > K, (f"{task} donor {fd['fold']}: pool has {n_units} donors, "
                             f"K = {K} leaves nothing to train on")
        frac = (K - 0.5) / n_units
        for draw in range(args.n_cal_draws):
            key = f"{task}|donor|{fd['fold']}"
            T, C, info = H.choose_calibration("donor", pool, E, samp, xy, meta, key, draw,
                                              frac, H.CAL_SPOT_FRAC)
            assert info["calibration_unit"] == "donor", (
                f"{task} {fd['fold']} draw{draw}: calibration unit fell through to "
                f"{info['calibration_unit']}")
            assert info["n_cal_units"] == K, (
                f"{task} {fd['fold']} draw{draw}: got K = {info['n_cal_units']}, wanted {K}")
            specs.append(dict(task=task, design="donor", fold=str(fd["fold"]), repeat=-1,
                              cal_draw=draw, T=T, C=C, E=E, pool=pool, info=info,
                              n_match=n_match))
    return specs


# ------------------------------------------------------------------- the engine
def unit_lab_of_C(spec, samp, xy, meta):
    """The calibration unit label of each calibration spot, by the harness's own unit_labels,
    with A3's spot-level convention where the unit is the spot."""
    Cm = spec["C"]
    lvl = spec["info"]["calibration_unit"]
    if lvl == "spot":
        return np.array([f"spot{i}" for i in range(int(Cm.sum()))], dtype=object)
    ul = H.unit_labels(lvl, Cm, spec.get("pool", Cm | spec["T"]), samp, xy, meta)
    return ul[Cm]


def dwr_pick(lab, rng):
    """One index per unit, drawn uniformly at random within the unit. Units are taken in
    sorted order, so the draw is a function of the seed alone.

    Grouped by a stable argsort rather than a membership test per unit: on the `random`
    design every calibration spot is its own unit, and a per-unit np.flatnonzero over n_C
    labels is quadratic in n_C (about 2e8 element comparisons at n_C = 14,600). A unit of
    size one consumes no random number, which keeps the donor-level draws identical whether
    or not singleton units are present.
    """
    s = np.asarray(lab, dtype=object).astype(str)
    order = np.argsort(s, kind="stable")
    su = s[order]
    starts = np.flatnonzero(np.concatenate(([True], su[1:] != su[:-1])))
    counts = np.diff(np.append(starts, len(su)))
    offs = np.array([int(rng.integers(c)) if c > 1 else 0 for c in counts], dtype=int)
    return np.sort(order[starts + offs])


def run_spec(spec, arm, donor_set, X, Y, samp, xy, genes, meta, enc, td, args, state):
    """Fit one fold and draw, then form the three intervals on it."""
    task, label_set = td["task"], td["label_set"]
    Tm = H.apply_size_match(spec, task)
    Cm, Em, info = spec["C"], spec["E"], spec["info"]
    n_C, n_E = int(Cm.sum()), int(Em.sum())
    if int(Tm.sum()) < H.MIN_T_SPOTS or n_C < H.MIN_C_SPOTS:
        print(f"  [skip] {donor_set} {arm} {spec['fold']} draw{spec['cal_draw']}: "
              f"|T|={int(Tm.sum())} |C|={n_C} ({info['cal_status']})", flush=True)
        return

    pipe, A, reg, ridge_alpha = H.fit_base(X[Tm], Y[Tm])
    A_C = pipe.transform(X[Cm].astype(np.float64, copy=False))
    B = pipe.transform(X[Em].astype(np.float64, copy=False))
    P_C, P_E = reg.predict(A_C), reg.predict(B)
    Y_C = Y[Cm].astype(np.float64, copy=False)
    Y_E = Y[Em].astype(np.float64, copy=False)
    samp_E = samp[Em]
    S_C = np.abs(Y_C - P_C)

    # per-gene Pearson pooled over the fold, then the mean over genes: the harness's H1
    # convention. A property of (T, E), so it is the same for all three intervals.
    rs = [float(pearsonr(P_E[:, j], Y_E[:, j])[0])
          if np.std(Y_E[:, j]) > 0 and np.std(P_E[:, j]) > 0 else np.nan
          for j in range(len(genes))]
    rs = np.asarray(rs, dtype=float)

    don_T = sorted({meta["donor_of"][s] for s in np.unique(samp[Tm])})
    don_C = sorted({meta["donor_of"][s] for s in np.unique(samp[Cm])})
    lab_C = unit_lab_of_C(spec, samp, xy, meta)
    w_hcp, w_E_hcp, K_hcp = A3.w3_weights(lab_C, n_E)

    base = dict(task=task, label_set=label_set, encoder=enc, donor_set=donor_set, arm=arm,
                design=spec["design"], fold=spec["fold"], repeat=spec["repeat"],
                draw=spec["cal_draw"], alpha=args.alpha, score=SCORE,
                calibration_unit=str(info["calibration_unit"]),
                n_units_in_pool=int(info["n_units_in_pool"]),
                n_cal_units=int(info["n_cal_units"]),
                n_T=int(Tm.sum()), n_T_spots_natural=int(spec["n_train_natural"]),
                n_T_spots_matched=int(spec["n_train_matched"]),
                n_match_target=(int(spec["n_match"]) if spec["n_match"] else -1),
                n_T_donors=len(don_T), n_C=n_C, n_C_donors=len(don_C), n_E=n_E,
                n_E_slides=int(len(np.unique(samp_E))),
                cal_donors=";".join(map(str, don_C)),
                pearson_mean=float(np.nanmean(rs)),
                pearson_n_genes=int(np.isfinite(rs).sum()))

    # ---- (a) pooled: the harness's own conformal_quantile, A1's interval ----------
    q_pool, pool_inf = H.conformal_quantile(S_C, args.alpha)
    q_alt, alt_inf = A3.weighted_quantile(S_C, np.ones(n_C), np.ones(n_E), args.alpha)
    dq = float(np.max(np.abs(q_alt - q_pool[None, :]))) if not pool_inf else 0.0
    state["codepath"].append(dict(**{k: base[k] for k in (
        "encoder", "donor_set", "arm", "fold", "draw")},
        max_abs_q_conformal_minus_weighted=dq,
        pooled_infinite=bool(pool_inf),
        weighted_infinite_points=int(alt_inf.sum())))
    half = np.broadcast_to(q_pool[None, :], (n_E, len(genes)))
    _record(state, base, "pooled", Y_E, P_E - half, P_E + half, samp_E, genes, args,
            K=float(n_C), n_eff=A3.n_eff(np.ones(n_C)))

    # ---- (b) HCP, A3's W3 group-equal weights -------------------------------------
    q_hcp, hcp_inf = A3.weighted_quantile(S_C, w_hcp, w_E_hcp, args.alpha)
    _record(state, base, "hcp", Y_E, P_E - q_hcp, P_E + q_hcp, samp_E, genes, args,
            K=float(K_hcp), n_eff=A3.n_eff(w_hcp), n_inf_points=int(hcp_inf.sum()))

    # ---- (c) the one-score-per-group subsample ------------------------------------
    nrep = 1 if info["calibration_unit"] == "spot" else args.dwr_reps
    cov, wm, wmd, isc, ninf, ma, mb = [], [], [], [], [], [], []
    fs = None
    for rep in range(nrep):
        seed_tag = (f"{task}|{donor_set}|{arm}|donor|{spec['fold']}|"
                    f"draw{spec['cal_draw']}|dwr{rep}")
        rng = np.random.default_rng(zlib.crc32(seed_tag.encode()))
        sel = dwr_pick(lab_C, rng)
        q, _ = H.conformal_quantile(S_C[sel], args.alpha)
        h = np.broadcast_to(q[None, :], (n_E, len(genes)))
        cells, _, wmd_sg, n_i, _ = A3.cell_metrics(Y_E, P_E - h, P_E + h, args.alpha,
                                                   samp_E, genes, H.MIN_SLIDE_SPOTS)
        fs = A3.fold_summary(cells)
        cov.append(fs["coverage"])
        wm.append(fs["width_mean"])
        wmd.append(wmd_sg)                 # the spot-gene median, as `pooled` and `hcp` use
        isc.append(fs["interval_score"])
        ma.append(fs["miss_above"])
        mb.append(fs["miss_below"])
        ninf.append(n_i)
        state["reps"].append(dict(**{k: base[k] for k in (
            "task", "encoder", "donor_set", "arm", "design", "fold", "draw", "alpha")},
            rep=rep, seed_tag=seed_tag, K=int(len(sel)), n_scores=int(len(sel)),
            coverage=fs["coverage"], width_mean=fs["width_mean"],
            width_median=fs["width_median_of_cells"], interval_score=fs["interval_score"],
            miss_above=fs["miss_above"], miss_below=fs["miss_below"], n_infinite=int(n_i)))
    state["rows"].append(dict(
        **base, method="dwr", difference_list=DIFFERENCE_LIST["dwr"],
        arm_difference_list=ARM_DIFFERENCE_LIST[arm],
        coverage=float(np.mean(cov)),
        coverage_sd_over_reps=(float(np.std(cov, ddof=1)) if nrep > 1 else np.nan),
        width_mean=float(np.mean(wm)),
        width_sd_over_reps=(float(np.std(wm, ddof=1)) if nrep > 1 else np.nan),
        width_median=float(np.mean(wmd)), interval_score=float(np.mean(isc)),
        miss_above=float(np.mean(ma)), miss_below=float(np.mean(mb)),
        K=float(len(set(map(str, lab_C.tolist())))),
        n_eff=float(np.nan), n_eff_frac=float(np.nan),
        n_infinite=int(np.sum(ninf)), n_spot_gene=int(n_E * len(genes) * nrep),
        frac_infinite=float(np.sum(ninf) / (n_E * len(genes) * nrep)),
        n_test_points_infinite=0,
        finite=bool(np.sum(ninf) == 0), n_reps=nrep,
        n_cells=int(fs["n_cells"]), n_slides=int(fs["n_slides"])))
    print(f"  [{donor_set}/{arm}] {spec['fold']} draw{spec['cal_draw']} "
          f"K={K_hcp} n_T={int(Tm.sum())}({len(don_T)}d) n_C={n_C}({len(don_C)}d) "
          f"n_E={n_E} r={np.nanmean(rs):.4f}", flush=True)


def _record(state, base, method, Y_E, lo, hi, samp_E, genes, args, K, n_eff,
            n_inf_points=0):
    cells, wm_sg, wmd_sg, n_inf, n_tot = A3.cell_metrics(
        Y_E, lo, hi, args.alpha, samp_E, genes, H.MIN_SLIDE_SPOTS)
    fs = A3.fold_summary(cells)
    state["rows"].append(dict(
        **base, method=method, difference_list=DIFFERENCE_LIST[method],
        arm_difference_list=ARM_DIFFERENCE_LIST[base["arm"]],
        coverage=fs["coverage"], coverage_sd_over_reps=np.nan,
        width_mean=fs["width_mean"], width_sd_over_reps=np.nan,
        width_median=wmd_sg, interval_score=fs["interval_score"],
        miss_above=fs["miss_above"], miss_below=fs["miss_below"],
        K=float(K), n_eff=float(n_eff), n_eff_frac=float(n_eff / max(base["n_C"], 1)),
        n_infinite=int(n_inf), n_spot_gene=int(n_tot),
        frac_infinite=float(n_inf / n_tot) if n_tot else np.nan,
        n_test_points_infinite=int(n_inf_points),
        finite=bool(n_inf == 0), n_reps=1,
        n_cells=fs["n_cells"], n_slides=fs["n_slides"],
        width_mean_spotgene=wm_sg))


# ------------------------------------------------------------------- per encoder
def run_encoder(td, enc, args, state):
    t0 = time.time()
    task = td["task"]
    donor_audit, audit_rec = audit_donor_map(f"{ROOT}/{args.audit}", task, td)
    state["audit"] = audit_rec
    print(f"[audit] {json.dumps(audit_rec, sort_keys=True)}", flush=True)

    X, Y, samp, bc, xy, genes = H.load_task(td, enc)
    print(f"[load] {task} {enc}: {X.shape[0]:,} spots x {X.shape[1]} dims, "
          f"{len(genes)} genes, {time.time()-t0:.0f}s", flush=True)
    state["n_spots"][task] = int(X.shape[0])
    state["dims"][task] = int(X.shape[1])

    ids = sorted(s["sample_id"] for s in td["samples"])
    designs = [d for d in args.designs.split(",") if d]
    arms = [a for a in args.arms.split(",") if a]
    sets = [s for s in args.donor_sets.split(",") if s]

    # the fold-rebuild rule, verified on the unmerged set before it is used on the merged one
    rebuilt = donor_folds(donor_audit, ids)
    shipped = [dict(fold=str(f["fold"]), test=sorted(f["test"]), train=sorted(f["train"]))
               for f in td["folds"]["donor"]]
    assert rebuilt == shipped, (
        "the rebuilt 24-donor folds differ from the task definition's shipped donor folds; "
        "the merged-set folds cannot be trusted to follow A1's rule")
    state["fold_rule_verified"] = True

    for ds in sets:
        if ds == "24":
            donor_of = dict(donor_audit)
        elif ds == "23_merged":
            donor_of = {s: (MERGED_ID if donor_audit[s] in MERGE_PAIR else donor_audit[s])
                        for s in ids}
        else:
            raise ValueError(ds)
        meta = dict(donor_of=donor_of,
                    patient_of={s["sample_id"]: s["hest_patient"] for s in td["samples"]},
                    resgroup_of={s["sample_id"]: s["resolution_group"]
                                 for s in td["samples"]},
                    session_of={s["sample_id"]: s.get("session") for s in td["samples"]})
        folds = donor_folds(donor_of, ids)
        tdv = dict(td)
        tdv["folds"] = dict(td["folds"])
        tdv["folds"]["donor"] = folds
        a1specs, n_match = a1_enumeration(tdv, samp, xy, meta, args, designs)
        state["enum"].append(dict(encoder=enc, donor_set=ds, n_specs=len(a1specs),
                                  n_match=n_match, n_donor_folds=len(folds),
                                  n_donors=len({v for v in donor_of.values()})))
        print(f"[enum] {ds}: {len(a1specs)} A1 specs, n_match={n_match}, "
              f"{len(folds)} donor folds, {len({v for v in donor_of.values()})} donors",
              flush=True)

        if "a1_rule_K6" in arms and ds == "24":
            for sp in a1specs:
                if sp["design"] == "donor":
                    run_spec(sp, "a1_rule_K6", ds, X, Y, samp, xy, genes, meta, enc, td,
                             args, state)
        if "random" in arms and ds == "24":
            for sp in a1specs:
                if sp["design"] == "random":
                    run_spec(sp, "random", ds, X, Y, samp, xy, genes, meta, enc, td, args,
                             state)
        if "K10" in arms:
            for sp in k_specs(tdv, samp, xy, meta, folds, args.K, n_match, args):
                run_spec(sp, "K10", ds, X, Y, samp, xy, genes, meta, enc, td, args, state)

    del X, Y
    return time.time() - t0


# ------------------------------------------------------------------- anchors
def _row(rows, check, scope, n, stat, value, tol, passed, note=""):
    rows.append(dict(check=check, scope=scope, n_cells=n, statistic=stat, value=value,
                     tol=tol, passed=passed, note=note))


def anchors(state, args, enc):
    """The anchor and acceptance checks, in the order the report names them."""
    rows, ok = [], True
    d = pd.DataFrame(state["rows"])
    if not len(d):
        return pd.DataFrame(), True

    # ---- 0. the size-match target reproduces A1's committed n_match_target -------
    src = f"{ROOT}/{args.a1_dir}/a1_calibration_units__{enc}__main.csv"
    if os.path.exists(src):
        cu = pd.read_csv(src)
        q = cu[(cu["task"] == TASK) & (cu["design"] == "donor")]
        ref = sorted(set(q["n_match_target"].dropna().astype(int).tolist()))
        mine = sorted({int(x) for x in d["n_match_target"] if int(x) > 0})
        passed = (len(ref) == 1 and mine == ref)
        ok &= bool(passed)
        _row(rows, "A0_n_match_reproduces_A1", "every arm", len(d),
             "n_match_target mine vs A1's", float(mine[0]) if mine else np.nan, 0.0, passed,
             f"mine {mine}, A1 {ref}; source {os.path.relpath(src, ROOT)}")
    else:
        _row(rows, "A0_n_match_reproduces_A1", "every arm", 0, "source absent", np.nan, 0.0,
             None, f"{src} not found")

    # ---- 1. the anchor: pooled at K = 6 reproduces a1_by_fold --------------------
    src = f"{ROOT}/{args.a1_dir}/a1_by_fold__{enc}__main.csv"
    mine = d[(d["arm"] == "a1_rule_K6") & (d["method"] == "pooled")]
    if os.path.exists(src) and len(mine):
        a1 = pd.read_csv(src)
        a1 = a1[(a1["task"] == TASK) & (a1["design"] == "donor") & (a1["score"] == SCORE)]
        g = (mine.groupby(["task", "label_set", "design", "fold"])
             [["coverage", "width_mean"]].mean().reset_index())
        j = g.merge(a1[["task", "label_set", "design", "fold", "coverage", "width_mean"]],
                    on=["task", "label_set", "design", "fold"],
                    suffixes=("_a4b", "_a1")).dropna()
        dc = float((j["coverage_a4b"] - j["coverage_a1"]).abs().max()) if len(j) else np.nan
        dw = float((j["width_mean_a4b"] - j["width_mean_a1"]).abs().max()) if len(j) else np.nan
        passed = bool(len(j) == a1["fold"].nunique() and dc <= args.anchor_tol)
        ok &= passed
        _row(rows, "A1_anchor_pooled_K6_reproduces_a1_by_fold", "arm a1_rule_K6, donor_set 24",
             len(j), "max |dcoverage| against a1_by_fold", dc, args.anchor_tol, passed,
             f"max |dwidth| {dw:.3e}; {len(j)} of {a1['fold'].nunique()} A1 folds matched; "
             f"source {os.path.relpath(src, ROOT)}")
    else:
        _row(rows, "A1_anchor_pooled_K6_reproduces_a1_by_fold", "arm a1_rule_K6", 0,
             "source or arm absent", np.nan, args.anchor_tol, None, f"{src}")

    # ---- 2. pooled at K = 10 set beside A1's CCRCC donor row ---------------------
    src = f"{ROOT}/{args.a1_dir}/a1_by_task__{enc}__main.csv"
    k10 = d[(d["arm"] == "K10") & (d["method"] == "pooled") & (d["donor_set"] == "24")]
    if os.path.exists(src) and len(k10):
        bt = pd.read_csv(src)
        r = bt[(bt["task"] == TASK) & (bt["design"] == "donor") & (bt["score"] == SCORE)]
        a1cov = float(r["coverage_mean"].iloc[0]) if len(r) else np.nan
        a1w = float(r["width_mean"].iloc[0]) if len(r) else np.nan
        mycov = float(k10["coverage"].mean())
        myw = float(k10["width_mean"].mean())
        _row(rows, "A2_pooled_K10_beside_A1_donor_row", "arm K10, donor_set 24", len(k10),
             "coverage at K=10 minus A1's CCRCC donor coverage", mycov - a1cov, np.nan, None,
             f"K=10 pooled coverage {mycov:.6f} width {myw:.6f}; A1 {a1cov:.6f} / {a1w:.6f}; "
             f"source {os.path.relpath(src, ROOT)}")

    # ---- 3. the control: on `random`, HCP is the pooled interval -----------------
    r = d[d["arm"] == "random"]
    if len(r):
        key = ["encoder", "donor_set", "fold", "repeat", "draw"]
        a = r[r["method"] == "hcp"]
        b = r[r["method"] == "pooled"]
        j = a.merge(b, on=key, suffixes=("_hcp", "_pool"))
        dc = float((j["coverage_hcp"] - j["coverage_pool"]).abs().max())
        dw = float((j["width_mean_hcp"] - j["width_mean_pool"]).abs().max())
        kbad = int((j["K_hcp"] != j["n_C_hcp"]).sum())
        passed = bool(kbad == 0 and dc <= args.anchor_tol and dw <= args.anchor_tol)
        ok &= passed
        _row(rows, "A3_random_control_hcp_equals_pooled", "arm random", len(j),
             "max |dcoverage|, max |dwidth|", max(dc, dw), args.anchor_tol, passed,
             f"max |dcoverage| {dc:.3e}, max |dwidth| {dw:.3e}, K != n_C on {kbad} of "
             f"{len(j)} cells")
        jd = r[r["method"] == "dwr"].merge(b, on=key, suffixes=("_dwr", "_pool"))
        dcd = float((jd["coverage_dwr"] - jd["coverage_pool"]).abs().max())
        passed = bool(dcd <= args.anchor_tol)
        ok &= passed
        _row(rows, "A3b_random_control_dwr_equals_pooled", "arm random", len(jd),
             "max |dcoverage|", dcd, args.anchor_tol, passed,
             "on `random` the unit is the spot, so one score per group is every score and "
             "the subsample is degenerate; one repetition is run")

    # ---- 4. the two pooled code paths agree exactly ------------------------------
    cp = pd.DataFrame(state["codepath"])
    if len(cp):
        v = float(cp["max_abs_q_conformal_minus_weighted"].max())
        passed = bool(v == 0.0)
        ok &= passed
        _row(rows, "A4_pooled_two_code_paths_agree", "every fold and draw", len(cp),
             "max |conformal_quantile - weighted_quantile at equal weights|", v, 0.0, passed,
             "the harness's conformal_quantile against A3's weighted_quantile with unit "
             "weights, per gene and test point")

    # ---- 5. K, the pool, and the training donor count ----------------------------
    for ds, npool, ndon in (("24", 23, 13), ("23_merged", 22, 12)):
        q = d[(d["arm"] == "K10") & (d["donor_set"] == ds) & (d["method"] == "hcp")]
        if not len(q):
            continue
        bad_k = int((q["K"] != args.K).sum())
        bad_pool = int((q["n_units_in_pool"] != npool).sum())
        bad_don = int((q["n_T_donors"] != ndon).sum())
        passed = bool(bad_k == 0 and bad_pool == 0 and bad_don == 0)
        ok &= passed
        _row(rows, "A5_K_pool_and_training_donors", f"arm K10, donor_set {ds}", len(q),
             f"cells with K != {args.K}, pool != {npool} or n_T_donors != {ndon}",
             float(bad_k + bad_pool + bad_don), 0.0, passed,
             f"n_T_donors {sorted(set(q['n_T_donors']))}, n_C_donors "
             f"{sorted(set(q['n_C_donors']))}, pool {sorted(set(q['n_units_in_pool']))}")

    # ---- 6. A1's six calibration donors are nested in A4b's ten ------------------
    a6 = d[(d["arm"] == "a1_rule_K6") & (d["method"] == "pooled")][["fold", "draw",
                                                                    "cal_donors"]]
    a10 = d[(d["arm"] == "K10") & (d["donor_set"] == "24")
            & (d["method"] == "pooled")][["fold", "draw", "cal_donors"]]
    if len(a6) and len(a10):
        j = a6.merge(a10, on=["fold", "draw"], suffixes=("_k6", "_k10"))
        nest = [set(str(x).split(";")).issubset(set(str(y).split(";")))
                for x, y in zip(j["cal_donors_k6"], j["cal_donors_k10"])]
        bad = int(len(nest) - sum(nest))
        passed = bool(bad == 0)
        ok &= passed
        _row(rows, "A6_A1_calibration_donors_nested_in_K10", "donor_set 24", len(j),
             "folds and draws where A1's 6 donors are not a subset of A4b's 10", float(bad),
             0.0, passed,
             "both are prefixes of the same crc32-seeded donor permutation, so the arms "
             "differ in which donors train and not in how they were drawn")

    # ---- 7. the level is attainable at K = 10 and is not at K = 6 ----------------
    for arm, expect_finite in (("K10", True), ("a1_rule_K6", False)):
        q = d[(d["arm"] == arm) & (d["method"].isin(["hcp", "dwr"]))]
        if not len(q):
            continue
        nfin = int(q["finite"].sum())
        passed = bool(nfin == len(q)) if expect_finite else bool(nfin == 0)
        ok &= passed
        _row(rows, "A7_level_attainable", f"arm {arm}, methods hcp and dwr", len(q),
             "cells with a finite interval", float(nfin), float(len(q) if expect_finite else 0),
             passed,
             f"K + 1 >= 1/alpha holds at K = {args.K} and fails at K = 6, so every K = 6 "
             f"hcp and dwr interval is recorded as infinite")
    return pd.DataFrame(rows), ok


# ------------------------------------------------------------------- outputs
MAIN_COLS = ["task", "label_set", "encoder", "donor_set", "arm", "design", "fold", "repeat",
             "draw", "method", "alpha", "score", "coverage", "width_mean", "width_median",
             "K", "n_T", "n_C", "finite", "coverage_sd_over_reps", "width_sd_over_reps",
             "interval_score", "miss_above", "miss_below", "n_eff", "n_eff_frac",
             "n_infinite", "n_spot_gene", "frac_infinite", "n_test_points_infinite",
             "n_reps", "calibration_unit", "n_units_in_pool", "n_cal_units", "n_C_donors",
             "n_T_donors", "n_T_spots_natural", "n_T_spots_matched", "n_match_target",
             "n_E", "n_E_slides", "n_cells", "n_slides", "pearson_mean", "pearson_n_genes",
             "cal_donors", "difference_list", "arm_difference_list"]


def write_outputs(out, suf, state, args, enc, acc, ok):
    os.makedirs(out, exist_ok=True)
    written = []
    if len(acc):
        acc.to_csv(f"{out}/a4b_anchor{suf}.csv", index=False)
        written.append(f"a4b_anchor{suf}.csv")
        print(f"\n=== A4b ANCHORS, encoder {enc} ===")
        print(acc.to_string(index=False), flush=True)
        print(f"ANCHORS: {'PASS' if ok else 'FAIL'}", flush=True)
    d = pd.DataFrame(state["rows"])
    if len(d):
        for c in MAIN_COLS:
            if c not in d.columns:
                d[c] = np.nan
        d = d[MAIN_COLS + [c for c in d.columns if c not in MAIN_COLS]]
        d.to_csv(f"{out}/a4b_hcp_K10{suf}.csv", index=False)
        written.append(f"a4b_hcp_K10{suf}.csv")
        print(f"[write] a4b_hcp_K10{suf}.csv ({len(d)} rows)", flush=True)
        show = (d[d["arm"] != "random"]
                .groupby(["donor_set", "arm", "method"], dropna=False)
                .agg(n=("fold", "size"), coverage=("coverage", "mean"),
                     width_mean=("width_mean", "mean"),
                     width_median=("width_median", "mean"),
                     K=("K", "median"), n_T_donors=("n_T_donors", "median"),
                     n_T=("n_T", "median"), n_C=("n_C", "median"),
                     finite=("finite", "all"), pearson=("pearson_mean", "mean"))
                .reset_index())
        print(show.round(5).to_string(index=False), flush=True)
    if state["reps"]:
        r = pd.DataFrame(state["reps"])
        r.to_csv(f"{out}/a4b_one_per_group_reps{suf}.csv", index=False)
        written.append(f"a4b_one_per_group_reps{suf}.csv")
        print(f"[write] a4b_one_per_group_reps{suf}.csv ({len(r)} rows)", flush=True)
    if state["codepath"]:
        pd.DataFrame(state["codepath"]).to_csv(
            f"{out}/a4b_codepath_check{suf}.csv", index=False)
        written.append(f"a4b_codepath_check{suf}.csv")
    return written


def _md5(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def provenance(out, suf, cfg, blob, chash, state, wall, written, ok, args):
    p = f"{out}/a4b_PROVENANCE{suf}.txt"
    exe = os.path.abspath(__file__)
    with open(p, "w") as f:
        f.write(f"{'='*78}\n"
                f"Round 3, stage A4b - HCP with K = {args.K} exchangeable donors on "
                f"{TASK}, encoder {cfg['encoder']}\n"
                f"plan            : round3_execution_plan.md sections 13.5.2, 13.10 items "
                f"1 and 2, 13.8\n"
                f"slurm_job_id    : {os.environ.get('SLURM_JOB_ID','NA')}\n"
                f"slurm_partition : {os.environ.get('SLURM_JOB_PARTITION','NA')}\n"
                f"node            : {os.environ.get('SLURMD_NODENAME','NA')}\n"
                f"gpu             : {os.environ.get('CUDA_VISIBLE_DEVICES','none')}\n"
                f"date            : {time.strftime('%Y-%m-%dT%H:%M:%S%z')}\n"
                f"commit          : {args.commit}  (SUPPLIED on the command line; this "
                f"stage runs no git command, so the field is not read from the working "
                f"copy)\n"
                f"script          : code/scripts/round3_a4b_hcp.py\n"
                f"script_file     : {exe}\n"
                f"script_md5      : {_md5(exe)}\n"
                f"harness_file    : {os.path.join(_SCRIPTS, 'round3_a0_harness.py')}\n"
                f"harness_md5     : {_md5(os.path.join(_SCRIPTS, 'round3_a0_harness.py'))}"
                f"  (imported unmodified)\n"
                f"a3_module_file  : {os.path.join(_SCRIPTS, 'round3_a3_weighted.py')}\n"
                f"a3_module_md5   : {_md5(os.path.join(_SCRIPTS, 'round3_a3_weighted.py'))}"
                f"  (imported unmodified)\n"
                f"command_line    : {' '.join(sys.argv)}\n"
                f"pythonhashseed  : {os.environ.get('PYTHONHASHSEED','unset')}\n"
                f"data_root       : {ROOT}\n"
                f"out_root        : {args.out_root}\n"
                f"n_spots_by_task : {json.dumps(state['n_spots'], sort_keys=True)}\n"
                f"embedding_dim   : {json.dumps(state['dims'], sort_keys=True)}\n"
                f"donor_audit     : {json.dumps(state.get('audit', {}), sort_keys=True)}\n"
                f"fold_rule_check : rebuilt 24-donor folds equal the shipped ones: "
                f"{state.get('fold_rule_verified')}\n"
                f"enumeration     : {json.dumps(state['enum'], sort_keys=True)}\n"
                f"n_rows          : {len(state['rows'])}\n"
                f"n_dwr_rep_rows  : {len(state['reps'])}\n"
                f"wall_seconds    : {wall:.0f}\n"
                f"anchors         : {'PASS' if ok else 'FAIL'}\n"
                f"files_written   : {', '.join(written)}\n"
                f"config_hash     : sha256/16 {chash}\n"
                f"config          : {blob}\n")
    print(f"[write] a4b_PROVENANCE{suf}.txt (config_hash {chash})", flush=True)
    return os.path.basename(p)


# ------------------------------------------------------------------- merge
def merge_tables(args):
    import glob as _glob
    out = f"{args.out_root}/{args.out_dir}"
    written = []
    for stem in ("a4b_anchor", "a4b_hcp_K10", "a4b_one_per_group_reps",
                 "a4b_codepath_check"):
        src = sorted(f for f in _glob.glob(f"{out}/{stem}__*.csv"))
        if not src:
            continue
        m = pd.concat([pd.read_csv(f).assign(_source=os.path.basename(f)) for f in src],
                      ignore_index=True)
        m.to_csv(f"{out}/{stem}.csv", index=False)
        written.append(f"{stem}.csv")
        print(f"[write] {stem}.csv ({len(m)} rows from {len(src)} files)", flush=True)
    return written


# ------------------------------------------------------------------- figure
def _style():
    """Three font sizes mapped to role (8 label and title, 7 legend and annotation, 6 tick),
    outward ticks, frameless legends, 300 dpi."""
    import matplotlib as mpl
    mpl.use("Agg")
    mpl.rcParams.update({
        "figure.dpi": 300, "savefig.dpi": 300, "savefig.bbox": "tight",
        "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8,
        "legend.fontsize": 7, "xtick.labelsize": 6, "ytick.labelsize": 6,
        "axes.titlelocation": "left", "axes.titleweight": "normal",
        "axes.spines.top": False, "axes.spines.right": False,
        "xtick.direction": "out", "ytick.direction": "out",
        "legend.frameon": False, "axes.grid": False, "lines.linewidth": 1.0,
    })


# Okabe-Ito, which stays separable under deuteranopia: the four series are grey, vermillion,
# blue and bluish green, and marker shape carries the distinction a second time.
PAL = {"pooled": "#999999", "hcp": "#D55E00", "dwr": "#0072B2", "random": "#009E73"}
LBL = {"pooled": "pooled spot-level quantile (A1's interval)",
       "hcp": "HCP, group-equal donor weights",
       "dwr": "one score per donor, 200 repetitions",
       "random": "control: `random` design, K = calibration spots"}


def figure(args):
    """fig_a4b_hcp_K10.png: coverage against width for the four intervals, with A1's
    committed CCRCC donor point marked, one panel per encoder."""
    _style()
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    out = f"{args.out_root}/{args.out_dir}"
    d = pd.read_csv(f"{out}/a4b_hcp_K10.csv")
    encs = [e for e in ("resnet50", "uni_v2", "hoptimus0") if e in set(d["encoder"])]
    encs += [e for e in sorted(set(d["encoder"])) if e not in encs]
    fig, axes = plt.subplots(1, len(encs), figsize=(2.45 * len(encs), 3.0), sharey=True)
    axes = np.atleast_1d(axes)
    a1 = {}
    for enc in encs:
        p = f"{ROOT}/{args.a1_dir}/a1_by_task__{enc}__main.csv"
        if os.path.exists(p):
            t = pd.read_csv(p)
            t = t[(t["task"] == TASK) & (t["design"] == "donor") & (t["score"] == SCORE)]
            if len(t):
                a1[enc] = (float(t["width_mean"].iloc[0]),
                           float(t["coverage_mean"].iloc[0]))
    for ax, enc in zip(axes, encs):
        e = d[d["encoder"] == enc]
        for meth in ("pooled", "hcp", "dwr"):
            for ds, mk in (("24", "o"), ("23_merged", "^")):
                q = e[(e["arm"] == "K10") & (e["method"] == meth) & (e["donor_set"] == ds)
                      & np.isfinite(e["width_mean"])]
                if len(q):
                    ax.scatter(q["width_mean"], q["coverage"], s=9, marker=mk,
                               color=PAL[meth], alpha=0.6, edgecolors="none")
        q = e[(e["arm"] == "random") & (e["method"] == "pooled")]
        if len(q):
            ax.scatter(q["width_mean"], q["coverage"], s=9, marker="s",
                       color=PAL["random"], alpha=0.7, edgecolors="none")
        ax.axhline(1 - ALPHA, color="0.55", lw=0.7, ls="--")
        if enc == encs[0]:
            ax.annotate(f"nominal {1-ALPHA:.2f}", xy=(0.98, 1 - ALPHA),
                        xycoords=("axes fraction", "data"), ha="right", va="bottom",
                        fontsize=7, color="0.35")
        # the extreme the reader will ask about: the worst-covered pooled fold
        pk = e[(e["arm"] == "K10") & (e["method"] == "pooled") & (e["donor_set"] == "24")]
        if len(pk):
            w = pk.loc[pk["coverage"].idxmin()]
            ax.annotate(f"held-out donor {w['fold']}",
                        xy=(float(w["width_mean"]), float(w["coverage"])),
                        xytext=(9, 4), textcoords="offset points", fontsize=7,
                        color=PAL["pooled"], ha="left", va="center",
                        arrowprops=dict(arrowstyle="-", lw=0.5, color=PAL["pooled"],
                                        shrinkA=0, shrinkB=2))
        if enc in a1:
            ax.scatter([a1[enc][0]], [a1[enc][1]], marker="*", s=110, color="black",
                       zorder=5)
            ax.annotate("A1", xy=a1[enc], xytext=(5, -9), textcoords="offset points",
                        fontsize=7, color="black")
        ax.set_title(enc)
        ax.set_xlabel("mean interval width")
        ax.margins(0.09)
    axes[0].set_ylabel("coverage")
    handles = [Line2D([], [], marker="o", ls="", color=PAL[m], label=LBL[m], markersize=4)
               for m in ("pooled", "hcp", "dwr")]
    handles += [Line2D([], [], marker="s", ls="", color=PAL["random"], label=LBL["random"],
                       markersize=4),
                Line2D([], [], marker="*", ls="", color="black",
                       label="A1's committed CCRCC donor row", markersize=8),
                Line2D([], [], marker="^", ls="", color="0.45",
                       label="INT4 and INT24 merged, 23 donors", markersize=4)]
    # The legend goes BELOW the panels: every panel carries points from coverage 0.26 to
    # 1.00 across the whole width range, so there is no in-panel whitespace that does not
    # cover data.
    fig.legend(handles=handles, loc="lower center", ncol=3, handletextpad=0.4,
               columnspacing=1.6, labelspacing=0.35, bbox_to_anchor=(0.5, -0.01))
    fig.suptitle("Group-equal weights buy the guarantee at K = 10 and pay for it in width; "
                 "one score per donor lands nearest nominal.\nEach point is one fold and "
                 "calibration draw: 24 x 3 donor folds, 23 x 3 with INT4 and INT24 merged, "
                 "6 x 5 for the control.", x=0.005, ha="left", fontsize=8)
    fig.tight_layout(rect=(0, 0.17, 1, 0.92))
    p = f"{out}/fig_a4b_hcp_K10.png"
    fig.savefig(p)

    # ---- geometric self-check, printed so the job log carries it ----------------
    r = fig.canvas.get_renderer()
    texts = [(t, t.get_window_extent(r)) for t in fig.findobj(mpl.text.Text)
             if t.get_text().strip() and t.get_visible()]
    spines = [(s, s.get_window_extent(r)) for ax in fig.axes
              for s in ax.spines.values() if s.get_visible()]
    tl = {ax: set(ax.get_xticklabels(which="both") + ax.get_yticklabels(which="both"))
          for ax in fig.axes}
    ov = [(a.get_text()[:28], b.get_text()[:28])
          for i, (a, ba) in enumerate(texts) for b, bb in texts[i + 1:] if ba.overlaps(bb)]
    ov += [(t.get_text()[:28], f"spine of {s.axes.get_title()}") for t, bt in texts
           for s, bs in spines if bt.overlaps(bs) and t not in tl[s.axes]]
    outside = [t.get_text()[:28] for t, bt in texts if not fig.bbox.containsx(bt.x0)
               or not fig.bbox.containsy(bt.y0)]
    print(f"[fig] text overlaps: {len(ov)} {ov}", flush=True)
    print(f"[fig] text boxes outside the figure: {len(outside)} {outside}", flush=True)
    plt.close(fig)
    print("[write] fig_a4b_hcp_K10.png", flush=True)
    return ["fig_a4b_hcp_K10.png"]


# ------------------------------------------------------------------- summary
def summary(args):
    """Every pooled number the stage report quotes, computed here into a4b_summary.csv so no
    figure in the report is retyped from a console. Long format: one row per quantity."""
    out = f"{args.out_root}/{args.out_dir}"
    d = pd.read_csv(f"{out}/a4b_hcp_K10.csv")
    reps = pd.read_csv(f"{out}/a4b_one_per_group_reps.csv")
    rows = []

    def add(metric, scope, value, n, note=""):
        rows.append(dict(metric=metric, scope=scope, value=value, n=n, note=note))

    # ---- the four intervals, per donor set, pooled over encoders and over folds -----
    for (ds, arm, meth), g in d.groupby(["donor_set", "arm", "method"]):
        sc = f"donor_set={ds} arm={arm} method={meth}"
        add("coverage_mean", sc, float(g["coverage"].mean()), len(g),
            "mean over folds, draws and encoders of the per-fold coverage")
        add("coverage_sd_across_cells", sc, float(g["coverage"].std(ddof=1)), len(g), "")
        add("width_mean", sc, float(g["width_mean"].mean()), len(g), "")
        add("width_median", sc, float(g["width_median"].mean()), len(g), "")
        add("frac_cells_at_or_above_nominal", sc,
            float((g["coverage"] >= 1 - ALPHA).mean()), len(g),
            f"fraction of cells with coverage >= {1-ALPHA:.2f}")
        add("frac_cells_finite", sc, float(g["finite"].mean()), len(g), "")
        add("n_T_donors_median", sc, float(g["n_T_donors"].median()), len(g), "")
        add("n_T_spots_matched_median", sc, float(g["n_T_spots_matched"].median()), len(g),
            "")
        add("n_T_spots_natural_median", sc, float(g["n_T_spots_natural"].median()), len(g),
            "")
        add("n_C_median", sc, float(g["n_C"].median()), len(g), "")
        add("K_median", sc, float(g["K"].median()), len(g), "")
        for enc, ge in g.groupby("encoder"):
            add("coverage_mean_by_encoder", f"{sc} encoder={enc}",
                float(ge["coverage"].mean()), len(ge), "")
            add("width_mean_by_encoder", f"{sc} encoder={enc}",
                float(ge["width_mean"].mean()), len(ge), "")

    # ---- Pearson: the K = 6 head against the K = 10 head, paired by fold and draw ----
    p = (d[(d["method"] == "pooled") & (d["donor_set"] == "24")]
         [["encoder", "arm", "fold", "draw", "pearson_mean", "n_T_donors"]])
    a = p[p["arm"] == "a1_rule_K6"]
    b = p[p["arm"] == "K10"]
    j = a.merge(b, on=["encoder", "fold", "draw"], suffixes=("_k6", "_k10"))
    j["delta"] = j["pearson_mean_k10"] - j["pearson_mean_k6"]
    for enc, g in j.groupby("encoder"):
        add("pearson_K6", f"encoder={enc} arm=a1_rule_K6 (17 training donors)",
            float(g["pearson_mean_k6"].mean()), len(g),
            "per-gene Pearson pooled over the fold, mean over 50 genes, then over folds "
            "and draws")
        add("pearson_K10", f"encoder={enc} arm=K10 (13 training donors)",
            float(g["pearson_mean_k10"].mean()), len(g), "")
        add("pearson_delta_K10_minus_K6", f"encoder={enc}", float(g["delta"].mean()),
            len(g), "paired by fold and draw")
        add("pearson_delta_worst_fold", f"encoder={enc}", float(g["delta"].min()), len(g),
            f"most negative paired difference, at fold "
            f"{g.loc[g['delta'].idxmin(), 'fold']}")
    add("pearson_delta_K10_minus_K6", "all three encoders", float(j["delta"].mean()), len(j),
        "the memo's prediction 5 quantity: the cost in Pearson of training on 13 donors "
        "instead of 17")
    add("pearson_delta_abs_max", "all three encoders", float(j["delta"].abs().max()), len(j),
        "largest absolute paired difference over every fold, draw and encoder")
    add("pearson_delta_frac_within_0.02", "all three encoders",
        float((j["delta"].abs() < 0.02).mean()), len(j), "")

    # ---- width ratios against the pooled quantile, the memo's prediction-5 quantity --
    for ds in sorted(set(d[d["arm"] == "K10"]["donor_set"])):
        q = d[(d["arm"] == "K10") & (d["donor_set"] == ds)]
        base = float(q[q["method"] == "pooled"]["width_mean"].mean())
        for meth in ("hcp", "dwr"):
            w = float(q[q["method"] == meth]["width_mean"].mean())
            add("width_ratio_over_pooled", f"donor_set={ds} arm=K10 method={meth}",
                w / base, int((q["method"] == meth).sum()),
                f"mean width {w:.6f} over mean pooled width {base:.6f}, both pooled over "
                f"folds, draws and encoders")
        for enc, ge in q.groupby("encoder"):
            b2 = float(ge[ge["method"] == "pooled"]["width_mean"].mean())
            for meth in ("hcp", "dwr"):
                add("width_ratio_over_pooled_by_encoder",
                    f"donor_set={ds} arm=K10 method={meth} encoder={enc}",
                    float(ge[ge["method"] == meth]["width_mean"].mean()) / b2,
                    int((ge["method"] == meth).sum()), "")
        h = q[q["method"] == "hcp"]
        add("hcp_coverage_within_0.92_0.95", f"donor_set={ds} arm=K10", float(
            ((h["coverage"] >= 0.92) & (h["coverage"] <= 0.95)).mean()), len(h),
            "the memo's 'most likely 0.92 to 0.95' band, as a fraction of cells")
        add("hcp_coverage_upper_bound_0.90_plus_2_over_11", f"donor_set={ds} arm=K10",
            float((h["coverage"] < 0.90 + 2.0 / 11.0).mean()), len(h),
            "fraction of cells below 0.90 + 2/11 = 1.081818")

    # ---- the pooled quantile at K = 10 against the same fold at K = 6 ---------------
    pp = (d[(d["method"] == "pooled") & (d["donor_set"] == "24")]
          [["encoder", "arm", "fold", "draw", "coverage", "width_mean"]])
    ja = pp[pp["arm"] == "a1_rule_K6"].merge(
        pp[pp["arm"] == "K10"], on=["encoder", "fold", "draw"], suffixes=("_k6", "_k10"))
    add("pooled_coverage_K10_minus_K6", "donor_set=24, paired by encoder, fold and draw",
        float((ja["coverage_k10"] - ja["coverage_k6"]).mean()), len(ja),
        "the memo's 'unchanged by the larger K' quantity")
    add("pooled_coverage_K10_minus_K6_abs_max",
        "donor_set=24, paired by encoder, fold and draw",
        float((ja["coverage_k10"] - ja["coverage_k6"]).abs().max()), len(ja), "")
    add("pooled_width_K10_minus_K6", "donor_set=24, paired by encoder, fold and draw",
        float((ja["width_mean_k10"] - ja["width_mean_k6"]).mean()), len(ja), "")

    # ---- the merged donor set beside the unmerged one, same method ------------------
    for meth in ("pooled", "hcp", "dwr"):
        q = d[(d["arm"] == "K10") & (d["method"] == meth)]
        m24 = q[q["donor_set"] == "24"]
        m23 = q[q["donor_set"] == "23_merged"]
        if len(m24) and len(m23):
            add("coverage_merged_minus_24", f"arm=K10 method={meth}",
                float(m23["coverage"].mean() - m24["coverage"].mean()),
                len(m23) + len(m24), "both pooled over encoders; the fold sets differ by "
                                     "one fold, so this is not a paired difference")
            add("width_merged_minus_24", f"arm=K10 method={meth}",
                float(m23["width_mean"].mean() - m24["width_mean"].mean()),
                len(m23) + len(m24), "")

    # ---- the one-score-per-group repetition dispersion ------------------------------
    r = reps[reps["arm"] == "K10"]
    if len(r):
        g = r.groupby(["encoder", "donor_set", "fold", "draw"])["coverage"]
        add("dwr_coverage_sd_within_cell_mean", "arm=K10, over 200 repetitions",
            float(g.std(ddof=1).mean()), int(g.ngroups),
            "mean over cells of the standard deviation of coverage across the 200 "
            "repetitions")
        add("dwr_coverage_sd_within_cell_max", "arm=K10, over 200 repetitions",
            float(g.std(ddof=1).max()), int(g.ngroups), "")
        add("dwr_coverage_range_within_cell_mean", "arm=K10, over 200 repetitions",
            float((g.max() - g.min()).mean()), int(g.ngroups), "")
        add("dwr_coverage_p5_mean", "arm=K10, over 200 repetitions",
            float(g.quantile(0.05).mean()), int(g.ngroups), "")
        add("dwr_coverage_p95_mean", "arm=K10, over 200 repetitions",
            float(g.quantile(0.95).mean()), int(g.ngroups), "")
        add("dwr_n_rep_rows", "arm=K10", float(len(r)), len(r), "")

    # ---- the control -----------------------------------------------------------------
    rc = d[d["arm"] == "random"]
    if len(rc):
        for meth in ("pooled", "hcp", "dwr"):
            q = rc[rc["method"] == meth]
            add("control_coverage_mean", f"arm=random method={meth}",
                float(q["coverage"].mean()), len(q), "")
            add("control_width_mean", f"arm=random method={meth}",
                float(q["width_mean"].mean()), len(q), "")

    s = pd.DataFrame(rows)
    s.to_csv(f"{out}/a4b_summary.csv", index=False)
    print(f"[write] a4b_summary.csv ({len(s)} rows)", flush=True)
    key = s[s["metric"].isin(["coverage_mean", "width_mean", "width_median",
                              "pearson_delta_K10_minus_K6", "frac_cells_finite"])]
    print(key.to_string(index=False), flush=True)
    return ["a4b_summary.csv"]


# ------------------------------------------------------------------- main
def main(argv=None):
    args = parse_args(argv or sys.argv[1:])
    if args.merge:
        merge_tables(args)
        return 0
    if args.figures:
        figure(args)
        return 0
    if args.summary:
        summary(args)
        return 0
    t0 = time.time()
    enc = args.encoder
    tds = []
    for p in args.task_def:
        td = json.load(open(p))
        assert td["task_def_version"] == 1, f"{p}: task_def_version {td['task_def_version']}"
        assert td["task"] == TASK, f"{p}: A4b is a {TASK} stage, got {td['task']}"
        td["_path"] = p
        tds.append(td)
    assert len(tds) == 1, "A4b runs on the CCRCC task definition alone"

    out = f"{args.out_root}/{args.out_dir}"
    suf = f"__{enc}{args.tag}"
    cfg = dict(stage="round3_A4b", script="code/scripts/round3_a4b_hcp.py", encoder=enc,
               task=f"{tds[0]['task']}/{tds[0]['label_set']}",
               task_def=os.path.relpath(os.path.abspath(tds[0]["_path"]), ROOT),
               donor_sets=args.donor_sets, arms=args.arms, K=args.K, alpha=args.alpha,
               score=SCORE, methods=list(METHODS), dwr_reps=args.dwr_reps,
               merge_pair=list(MERGE_PAIR), merged_id=MERGED_ID,
               designs_enumerated=args.designs, size_match=args.size_match,
               n_cal_draws=args.n_cal_draws, spot_cal_draws=args.spot_cal_draws,
               n_repeats=args.n_repeats, max_folds=args.max_folds,
               cal_frac_units_rule="(K - 0.5) / n_units, whose ceiling is K",
               donor_grouping="donor_audit_r3.csv row_origin=benchmark_r2, checked against "
                              "the task definition",
               quantile_rel_tol=A3.QTOL, min_slide_spots=H.MIN_SLIDE_SPOTS,
               min_T_spots=H.MIN_T_SPOTS, min_C_spots=H.MIN_C_SPOTS,
               base_predictor="imported unmodified from round3_a0_harness.fit_base",
               weighted_quantile="imported unmodified from round3_a3_weighted",
               seed_source="zlib.crc32 via the harness")
    blob = json.dumps(cfg, sort_keys=True)
    chash = hashlib.sha256(blob.encode()).hexdigest()[:16]
    print(f"[config] sha256/16 {chash}\n{blob}", flush=True)

    state = dict(rows=[], reps=[], codepath=[], enum=[], dims={}, n_spots={})
    run_encoder(tds[0], enc, args, state)
    acc, ok = anchors(state, args, enc)
    written = write_outputs(out, suf, state, args, enc, acc, ok)
    written.append(provenance(out, suf, cfg, blob, chash, state, time.time() - t0,
                              written, ok, args))
    print(f"\n[done] {time.time()-t0:.0f}s  anchors="
          f"{'PASS' if ok else 'FAIL'}", flush=True)
    return 0 if ok else 5


if __name__ == "__main__":
    sys.exit(main())
