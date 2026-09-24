#!/usr/bin/env python
"""Round 3, stage B1: prediction-powered inference with donor-clustered variance.

Stage: B1 (round3_execution_plan.md sections 4.7 and 12.5, as amended by section 13.6,
which transcribes docs/decisions/round3_A3_decisions.md). No gate; B2 follows and the
end-of-round report is the gate.

THIS SCRIPT DOES NOT EDIT THE HARNESS. It imports `round3_a0_harness.py` from the same
directory as a module and reuses its data loading, its base predictor, its fold
enumeration, its calibration-unit rule and its size matching unchanged, exactly as
`round3_a3_weighted.py` does.

INPUTS, section 13.6. B1 uses the harness's CALIBRATION-FRACTION-ZERO `donor` predictions,
which is the harness's H1 mode (`--h1-anchor`: cal_frac_units = cal_frac_spots = 0, so
C is empty, T is the whole pool, and no conformal quantile is formed) run on the `donor`
design instead of `patient`. Under that combination every spot of a task is predicted
exactly once, by a head fitted on all OTHER donors, so cross-fitting holds at donor level
and the prediction is independent of the spot's own donor's labels. H1 mode also sets
--size-match none, which is what A0's H1 check used, so the anchor below is exact.

ANCHOR (printed first, as every round-3 stage must be anchored to a committed number).
Run this script with --predict --design patient on the same task files: the per-task
Pearson it computes, aggregated mean-over-genes-within-fold then mean-over-folds, must
reproduce A0's H1 column `ours` in results/round3/A0_smoke/h1_by_task__<enc>__h1.csv to
--anchor-tol (1e-6). That file is itself the table that reproduced round 2 R1b's
`intercept_f64` Pearson, so reproducing it anchors B1's predictions to A1's base predictor
through A0. Only then is --design donor run.

COVARIATES. instrumentation/morphology_v2/<task>_morph.parquet, joined on
(sample_id, barcode). m is the STANDARDISED mean nuclear area: area_mean z-scored over the
task's joined spots, with the mean and sd recorded in b1_join.csv. Neoplastic fraction is
frac_neoplastic. Spots that do not join carry no m and no neoplastic fraction and are
EXCLUDED from every estimand; the join rate is recorded per task and per slide in
b1_join.csv and no estimand is computed over a task whose join rate is below --min-join.

ESTIMANDS, section 4.7, per task and gene g. Every one is written as theta = g(mu) with
mu a vector of means of a per-spot vector z(y, x) that is LINEAR in the outcome, so the
PPI++ estimating equation has a closed form and the whole stage reduces to algebra on
per-group sums of z and of z z'. The three:

  theta_3  primary. Slope of the outcome on m.
           z = (m, m^2, y, m*y),  g(mu) = (mu_4 - mu_1 mu_3) / (mu_2 - mu_1^2).
           Outcome log(1+y_g). Equal to Cov(m, y)/Var(m) over the population, which is the
           section 4.7 definition, and equal to the OLS slope of y on m with intercept.
  theta_2  Difference in mean outcome between neoplastic-dominant spots (frac_neoplastic
           > 0.7) and stromal-dominant spots (< 0.3).
           z = (1_neo, 1_neo*y, 1_str, 1_str*y),  g(mu) = mu_2/mu_1 - mu_4/mu_3.
           Spots in neither group enter with a zero z, which is why the ratios and not
           differences of means appear: mu_1 is the neoplastic SHARE of the population.
  theta_1  IDC only, the motivating example. Correlation of m with the RAW GATA3 count.
           z = (m, m^2, y, y^2, m*y),
           g(mu) = (mu_5 - mu_1 mu_3) / sqrt((mu_2 - mu_1^2)(mu_4 - mu_3^2)).
           Outcome is the raw count, so the predictor used for it is expm1 of the head's
           log1p prediction. PPI is valid for ANY predictor, biased or not, so a
           back-transformed prediction is a legitimate f; its bias shows up as a smaller
           lambda, never as a wrong interval. The raw counts are read from the AnnData
           before log1p and cross-checked against expm1 of the harness's y.

Two POPULATIONS, both reported (section 4.7).

  spot     theta = g(mean over the SPOTS of the set). One estimand per task.
  donor    theta = mean over DONORS of the donor-level value g(mean over the donor's own
           spots). This is the population whose unit is the donor. It is a mean of a
           donor-level scalar, so PPI applies to it in the scalar-mean form.

ESTIMATORS. Classical on L alone, and PPI++ in the estimating-equation form of section 4.7
(Angelopoulos, Duchi and Zrnic 2023, equation 4 of Fisch et al. arXiv:2406.04291),

  lambda/N sum_{i in U} psi(f_i, x_i; theta)
      + 1/n sum_{i in L} [ psi(y_i, x_i; theta) - lambda psi(f_i, x_i; theta) ] = 0,

which for a mu that is linear in the outcome gives mu_pp = lambda mu_U^f + mu_L
- lambda mu_L^f and theta_pp = g(mu_pp). lambda is estimated by minimising the DONOR-
CLUSTERED variance of theta_pp over lambda, which is a quadratic in lambda with a closed
form, and clipped to [0, 1] as PPI++ does. Where the donor-clustered variance is not
estimable (one donor in U or in L) lambda is estimated from the spot-i.i.d. variance
instead and `lambda_basis` records which. With U EMPTY lambda is 0 by construction, so
theta_pp equals theta_classical exactly, which is the first acceptance check.

VARIANCES, for both estimators (section 4.7). All three are built from ONE per-spot
influence contribution h_i, so the third acceptance check is an identity and not a
coincidence:

  spot-weighted population   h_i = grad g(mu_pp)' (z_i - mu) / n, the ordinary influence
                             function of a smooth function of a sample mean.
  donor-weighted population  h_i = (t_d - theta) / (G n_d) for spot i in donor d, the
                             donor-level deviation spread uniformly over the donor's spots.
                             This is the linearisation of an estimand whose unit IS the
                             donor; summing it within a donor returns the donor's own
                             deviation.

  (a) spot i.i.d.        V = n/(n-1) * sum_i h_i^2, the default in the PPI papers.
  (b) donor cluster-robust  V = G/(G-1) * sum_d (sum_{i in d} h_i)^2, formed SEPARATELY
                         for the U and the L term because the donor sets are disjoint
                         (each term gets its own G/(G-1) and its own donor set), with a t
                         reference on G_L - 1 degrees of freedom. When the donor sets are
                         NOT disjoint, which happens only in B2's PRAD slide-masking
                         variant, the two terms are summed WITHIN a donor first and one
                         G/(G-1) is applied; `cluster_variance_form` records which form
                         was used and the two are never mixed in one row.
  (c) donor bootstrap    donors resampled with replacement within U and within L
                         independently, --n-boot draws (500), percentile interval at
                         alpha; lambda held at its full-sample value, as PPI++ does.

With one spot per donor, n = G and each donor contributes one term, so (b) equals (a)
identically, including the small-sample factor: G/(G-1) = n/(n-1). That is acceptance
check 3 and it is checked numerically on a one-spot-per-donor subsample rather than
asserted.

ARMS. Three encoders (hoptimus0, uni_v2, resnet50) plus `permuted`, the deliberately
useless predictor: resnet50's per-spot predictions permuted across all spots of the task
under a crc32 seed, which destroys the relation to y and to m while leaving the marginal
distribution of f untouched. Two further arms exist only for acceptance:
`identity`, f := y exactly, constructed from the measured block of the sufficient
statistics; and the U-empty and one-spot-per-donor settings, which are settings rather
than arms.

TASKS AND SETTINGS, sections 4.7 and 13.6. CCRCC labelling 6, 8 and 12 donors, run TWICE:
with 24 donors, and with INT4 and INT24 merged into one donor unit (23 units), both
reported. LYMPH_IDC labelling 2 of 4. PRAD, two donors over 23 slides, run and reported
as the expected one-donor-degree-of-freedom failure. IDC carries theta_1 under the
four-donor labels of results/round3/D3_audit/donor_audit_r3.csv. IDC `audited` is
superseded and is not run. No expansion task.

OUTPUTS under results/round3/B1_ppi/, summaries before parquets:
  b1_acceptance.csv     the four checks, written and printed FIRST
  b1_estimates.csv      one row per (task, label variant, arm, estimand, population,
                        gene, n_L), section 4.7's columns plus the three variances
  b1_join.csv           morphology join rate per task and slide, and m's standardisation
  b1_pred_quality.csv   per-task and per-gene Pearson of the predictions actually used
  b1_h1_anchor.csv      the anchor to A0's H1 (--design patient only)
  b1_theta1_by_slide.csv  theta_1 per IDC slide and pooled
  fig_b1_intervals.png
  PROVENANCE__*.txt
Per-spot predictions go to b1_predictions__<task><variant>__<enc>.parquet with an
explicit pa.schema and STAY ON LONGLEAF (gitignored), as do the sufficient statistics
b1_suffstats__<task><variant>__<enc>.npz.

Usage:
  round3_b1_ppi.py --predict <encoder> --task-def <f> [--design donor|patient] [--merge ..]
  round3_b1_ppi.py --estimate
  round3_b1_ppi.py --figures
"""
import argparse
import copy
import glob as _glob
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time
import zlib

import anndata as ad
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from scipy import stats

# --------------------------------------------------- import the A0 harness, unedited
_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "round3_a0_harness", os.path.join(_HERE, "round3_a0_harness.py"))
H = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(H)

ROOT = H.ROOT
A0DIR = "results/round3/A0_smoke"
AUDIT = "results/round3/D3_audit/donor_audit_r3.csv"

ENCODERS = ("hoptimus0", "uni_v2", "resnet50")
PERMUTE_SOURCE = "resnet50"          # whose predictions the `permuted` arm permutes
NEO_HI, STR_LO = 0.7, 0.3            # section 4.7's theta_2 thresholds
THETA1_TASK, THETA1_GENE = "IDC", "GATA3"
ALPHA = 0.10                         # nominal 0.90 intervals
N_BOOT = 500                         # section 4.7 (c)
MIN_TUNE_G = 4                       # fewest labelled donors at which a donor-weighted
                                     # lambda is tuned at all; see cell_donor
MIN_JOIN = 0.80                      # a task whose morphology join rate falls below this
                                     # gets no estimand, rather than a table row computed
                                     # on an unstated subset

# n_L settings per task variant, sections 4.7 and 13.6.
NL_SETTINGS = {
    "CCRCC": (6, 8, 12),
    "CCRCC_merged": (6, 8, 12),
    "LYMPH_IDC": (2,),
    "PRAD": (1, 2),                  # 1 leaves U non-empty with G_L = 1; 2 empties U
    "IDC": (2,),
}

# The CCRCC label variant of section 13.3: INT4 and INT24 merged into one donor unit.
MERGES = {"CCRCC_merged": {"INT4": "INT4_INT24", "INT24": "INT4_INT24"}}


# ------------------------------------------------------------------- estimands
#
# DESIGN CONSTANTS, and why they are not estimated through PPI.
#
# m and the two neoplastic-fraction group indicators are computed from the H&E image by
# CellViT for EVERY spot of the task, labelled or not: they cost nothing and need no
# expression measurement. Topic B's whole premise is that the OUTCOME is expensive and the
# covariates are cheap. So the moments of the covariates -- mu_m, Var(m), and the
# population shares p_neo and p_str -- are label-free design constants, computed once from
# all joined spots of the population unit and used identically by the classical estimator,
# the PPI estimator and the full-data value. They are folded into z, which therefore
# carries ONLY outcome-bearing components.
#
# The consequence that matters: the labelled and unlabelled arms then differ in the
# outcome and in nothing else, so a useless predictor gets lambda_hat near zero and the
# section 4.7 acceptance check on the permuted arm tests what it was written to test. An
# earlier construction that estimated the covariate moments through PPI alongside the
# outcome gave the permuted arm a real, valid width reduction from the covariate
# components alone (median lambda_hat 0.41, width ratio 0.97), which is not a bug but
# makes the check vacuous. The price is that the classical estimator is the known-design
# form and not the L-internal one: theta_3's classical estimator divides by the
# POPULATION Var(m) rather than L's own, and theta_2's by the population group shares.
# Both are consistent for the population estimand; the L-internal (ordinary least squares
# on L, within-L group means) form is not what is reported.
#
# Per population unit u with constants mu_m[u], V_m[u], p_neo[u], p_str[u]:
#   theta_3  z = (m - mu_m) * y / V_m                           k = 1, theta = E[z]
#   theta_2  z = 1{neo>0.7} y / p_neo - 1{neo<0.3} y / p_str    k = 1, theta = E[z]
#   theta_1  z = (y, y^2, (m - mu_m) y / sd_m)                   k = 3,
#            theta = mu_3 / sqrt(mu_2 - mu_1^2)
# so theta_3 and theta_2 are plain means of a per-spot scalar -- the mean case of the PPI
# papers -- and only theta_1 needs the delta method.

def _val_mean(mu):
    return mu[..., 0]


def _grad_mean(mu):
    return np.ones_like(mu[..., :1])


def _val_theta1(mu):
    m1, m2, m3 = mu[..., 0], mu[..., 1], mu[..., 2]
    return m3 / np.sqrt(m2 - m1 * m1)


def _grad_theta1(mu):
    m1, m2, m3 = mu[..., 0], mu[..., 1], mu[..., 2]
    V = m2 - m1 * m1
    return np.stack([m3 * m1 * V ** -1.5,
                     -0.5 * m3 * V ** -1.5,
                     V ** -0.5], axis=-1)


ESTIMANDS = {
    "theta3": dict(k=1, value=_val_mean, grad=_grad_mean, outcome="log1p",
                   desc="Cov(m, log(1+y)) / Var(m), the slope of log(1+y) on the "
                        "standardised mean nuclear area m"),
    "theta2": dict(k=1, value=_val_mean, grad=_grad_mean, outcome="log1p",
                   desc="mean log(1+y) difference, neoplastic fraction >0.7 minus <0.3"),
    "theta1": dict(k=3, value=_val_theta1, grad=_grad_theta1, outcome="raw",
                   desc="correlation of m with the raw GATA3 count"),
}


def design_consts(m, neo, unit_idx, n_units):
    """The label-free design constants of each population unit, from ALL of that unit's
    joined spots. For the spot-weighted population there is one unit, the task; for the
    donor-weighted population one unit per donor. They never depend on which spots are
    labelled, which is what lets the one-spot-per-donor acceptance check be well defined.
    """
    c = {k: np.full(n_units, np.nan) for k in ("mu_m", "v_m", "p_neo", "p_str", "n")}
    for u in range(n_units):
        s = unit_idx == u
        if not s.any():
            continue
        c["mu_m"][u] = m[s].mean()
        c["v_m"][u] = m[s].var(ddof=0)
        c["p_neo"][u] = float((neo[s] > NEO_HI).mean())
        c["p_str"][u] = float((neo[s] < STR_LO).mean())
        c["n"][u] = int(s.sum())
    return c


def unit_valid(est, c):
    """Which population units admit the estimand at all, on label-free grounds."""
    if est == "theta2":
        return (c["p_neo"] > 0) & (c["p_str"] > 0)
    return c["v_m"] > 0


def build_z(est, y, m, neo, c, unit_idx):
    """The per-spot z vector for one estimand. y is (n, G); m and neo are (n,); c holds
    the design constants and unit_idx says which unit each spot belongs to.
    Returns (n, G, k)."""
    n, G = y.shape
    mu = c["mu_m"][unit_idx]
    vm = c["v_m"][unit_idx]
    if est == "theta3":
        w = ((m - mu) / np.where(vm > 0, vm, np.nan))[:, None]
        return (w * y)[:, :, None]
    if est == "theta1":
        w = ((m - mu) / np.sqrt(np.where(vm > 0, vm, np.nan)))[:, None]
        return np.stack([y, y * y, w * y], axis=-1)
    if est == "theta2":
        pn, ps = c["p_neo"][unit_idx], c["p_str"][unit_idx]
        hi = (neo > NEO_HI).astype(np.float64) / np.where(pn > 0, pn, np.nan)
        lo = (neo < STR_LO).astype(np.float64) / np.where(ps > 0, ps, np.nan)
        return ((hi - lo)[:, None] * y)[:, :, None]
    raise ValueError(est)


# ----------------------------------------------------------------- arguments
def parse_args(argv):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--predict", default="", metavar="ENCODER",
                   help="generate per-spot predictions and sufficient statistics")
    p.add_argument("--estimate", action="store_true")
    p.add_argument("--figures", action="store_true")
    p.add_argument("--report-numbers", action="store_true", dest="report_numbers")
    p.add_argument("--b2-dir", default="results/round3/B2_semisynthetic")
    p.add_argument("--task-def", action="append", dest="task_def", default=None)
    p.add_argument("--design", default="donor", choices=("donor", "patient"))
    p.add_argument("--variant", default="",
                   help="a key of MERGES, e.g. CCRCC_merged; empty means the shipped "
                        "donor labels of the task definition")
    p.add_argument("--out-dir", default="results/round3/B1_ppi")
    p.add_argument("--morph-dir", default=H.MORPH_DIR)
    p.add_argument("--a0-dir", default=A0DIR)
    p.add_argument("--alpha", type=float, default=ALPHA)
    p.add_argument("--n-boot", type=int, default=N_BOOT)
    p.add_argument("--min-join", type=float, default=MIN_JOIN)
    p.add_argument("--anchor-tol", type=float, default=1e-6)
    p.add_argument("--exact-tol", type=float, default=1e-10,
                   help="tolerance for the three exact acceptance identities")
    p.add_argument("--permuted-tol", type=float, default=0.05,
                   help="how far below 1 the permuted arm's width ratio may fall; the "
                        "ratio is not an identity, see acceptance()")
    p.add_argument("--gene-chunk", type=int, default=10)
    a = p.parse_args(argv)
    assert sum(bool(x) for x in (a.predict, a.estimate, a.figures,
                                a.report_numbers)) == 1, \
        "exactly one of --predict, --estimate, --figures, --report-numbers"
    if a.predict:
        assert a.task_def, "--predict needs at least one --task-def"
    return a


def harness_args(args, task_defs, design):
    """A harness argparse namespace in H1 mode: calibration fraction zero, no size
    matching, one calibration draw. Built through H.parse_args so a new harness flag with
    a split-relevant default cannot be missed here."""
    argv = [args.predict]
    for t in task_defs:
        argv += ["--task-def", t]
    argv += ["--designs", design, "--size-match", "none", "--h1-anchor"]
    return H.parse_args(argv)


# ------------------------------------------------------- task-definition variants
def apply_variant(td, variant):
    """Rewrite donor_id under a merge and rebuild the `donor` folds as leave-one-unit-out
    over the merged labels, in the sorted-unit order round3_task_defs.py used. Nothing
    else in the task definition is touched, and size matching is off, so the merged run
    differs from the 24-donor run in exactly one thing: which samples share a donor unit.
    """
    if not variant:
        return td, {}
    mp = MERGES[variant]
    td = copy.deepcopy(td)
    for s in td["samples"]:
        s["donor_id"] = mp.get(s["donor_id"], s["donor_id"])
    by = {}
    for s in td["samples"]:
        by.setdefault(s["donor_id"], []).append(s["sample_id"])
    ids = sorted(s["sample_id"] for s in td["samples"])
    td["folds"]["donor"] = [
        dict(fold=d, train=[i for i in ids if i not in set(by[d])], test=sorted(by[d]))
        for d in sorted(by)]
    return td, mp


def donor_labels_from_audit(task):
    """The benchmark_r2 rows of donor_audit_r3.csv, which are the grouping source for
    benchmark tasks (section 13.10 item 2). Returns {sample_id: donor_id}."""
    d = pd.read_csv(f"{ROOT}/{AUDIT}")
    d = d[(d["row_origin"] == "benchmark_r2") & (d["task"] == task)]
    return dict(zip(d["sample_id"].astype(str), d["donor_id"].astype(str)))


# --------------------------------------------------------------- morphology join
def load_morph(task, morph_dir):
    p = f"{ROOT}/{morph_dir}/{task}_morph.parquet"
    d = pq.read_table(p).to_pandas()
    for c in ("sample_id", "barcode", "area_mean", "frac_neoplastic"):
        assert c in d.columns, f"{p}: column {c} absent; have {list(d.columns)}"
    d["_k"] = d["sample_id"].astype(str) + "\t" + d["barcode"].astype(str)
    return (dict(zip(d["_k"], d["area_mean"].astype(float))),
            dict(zip(d["_k"], d["frac_neoplastic"].astype(float))),
            os.path.relpath(p, ROOT), len(d))


# ------------------------------------------------------------ raw counts for theta_1
def raw_counts(td, gene, samp, bc):
    """The RAW (pre-log1p) count of one gene, per spot, read from the AnnData directly.
    H.load_task applies sc.pp.log1p in place, so this is a second read of the same file
    rather than an inverse transform; expm1 of the harness's y is compared against it and
    the maximum absolute difference is reported."""
    out = np.full(len(samp), np.nan)
    for sid in sorted(set(samp.tolist())):
        A = ad.read_h5ad(f"{ROOT}/{td['paths']['adata'].format(sample_id=sid)}")
        sub = A[:, [gene]]
        v = sub.X.toarray().ravel() if hasattr(sub.X, "toarray") else np.asarray(sub.X).ravel()
        lut = dict(zip([str(b) for b in A.obs_names], v.astype(float)))
        m = samp == sid
        out[m] = [lut.get(str(b), np.nan) for b in bc[m]]
    return out


# =========================================================== PREDICT mode
def run_predict(args):
    enc = args.predict
    t0 = time.time()
    out = f"{ROOT}/{args.out_dir}"
    os.makedirs(out, exist_ok=True)
    tds = []
    for p in args.task_def:
        td = json.load(open(p))
        assert td["task_def_version"] == 1, f"{p}: task_def_version"
        assert td["label_set"] != "audited", \
            f"{p}: IDC audited is superseded (section 13.2 item 1); no stage runs it"
        td["_path"] = p
        tds.append(td)

    cfg = dict(stage="round3_B1_predict", script="code/scripts/round3_b1_ppi.py",
               encoder=enc, design=args.design, variant=args.variant,
               tasks=[f"{t['task']}/{t['label_set']}" for t in tds],
               task_defs=[os.path.relpath(os.path.abspath(t["_path"]), ROOT) for t in tds],
               harness_mode="h1_anchor (cal_frac_units=cal_frac_spots=0), size_match=none",
               morph_dir=args.morph_dir, neo_hi=NEO_HI, str_lo=STR_LO,
               permute_source=PERMUTE_SOURCE, min_join=args.min_join,
               merges=MERGES.get(args.variant, {}),
               base_predictor="imported unmodified from round3_a0_harness.fit_base",
               seed_source="zlib.crc32 via the harness")
    blob = json.dumps(cfg, sort_keys=True)
    chash = hashlib.sha256(blob.encode()).hexdigest()[:16]
    print(f"[config] sha256/16 {chash}\n{blob}", flush=True)

    state = dict(h1=[], quality=[], join=[], wall={}, n_spots={}, dims={}, files=[],
                 theta1_raw=[], consts=[])
    for td in tds:
        state["wall"][f"{td['task']}/{td['label_set']}"] = round(
            predict_task(td, enc, args, state, out), 1)

    suf = f"__{enc}" + (f"__{args.variant}" if args.variant else "") + \
          (f"__{args.design}" if args.design != "donor" else "")
    for name, rows in (("b1_join", state["join"]),
                       ("b1_pred_quality", state["quality"]),
                       ("b1_design_consts", state["consts"]),
                       ("b1_theta1_raw_check", state["theta1_raw"])):
        if rows:
            pd.DataFrame(rows).to_csv(f"{out}/{name}{suf}.csv", index=False)
            state["files"].append(f"{name}{suf}.csv")
            print(f"[write] {name}{suf}.csv ({len(rows)} rows)", flush=True)
    ok = True
    if args.design == "patient":
        ok = h1_anchor(out, suf, enc, state, args)
    provenance(out, f"predict{suf}", cfg, blob, chash, state, time.time() - t0, ok)
    print(f"\n[done] predict {time.time()-t0:.0f}s anchor={'PASS' if ok else 'n/a-or-FAIL'}",
          flush=True)
    return 0 if ok else 6


PRED_BASE = ["sample_id", "barcode", "donor_id", "fold"]


def predict_task(td0, enc, args, state, out):
    t0 = time.time()
    td, mp = apply_variant(td0, args.variant)
    task, label_set = td["task"], td["label_set"]
    vtag = args.variant if args.variant else task

    # Donor grouping is checked against the audit file rather than trusted from the task
    # definition. On IDC the audit renames both 10x donors; the PARTITION must agree.
    aud = donor_labels_from_audit(task)
    tdj = {s["sample_id"]: s["donor_id"] for s in td0["samples"]}
    part_td = sorted(tuple(sorted(k for k, v in tdj.items() if v == u))
                     for u in set(tdj.values()))
    part_au = sorted(tuple(sorted(k for k, v in aud.items() if v == u))
                     for u in set(aud.values()))
    assert part_td == part_au, (
        f"{task}: the task definition's donor partition disagrees with the benchmark_r2 "
        f"rows of {AUDIT}: {part_td} vs {part_au}")
    audit_name = {s: aud.get(s, tdj[s]) for s in tdj}
    print(f"[donors] {task}: partition agrees with {AUDIT}; audit donor names "
          f"{json.dumps({k: v for k, v in sorted(audit_name.items())}, sort_keys=True)}",
          flush=True)

    meta = dict(
        donor_of={s["sample_id"]: s["donor_id"] for s in td["samples"]},
        patient_of={s["sample_id"]: s["hest_patient"] for s in td["samples"]},
        resgroup_of={s["sample_id"]: s["resolution_group"] for s in td["samples"]},
        session_of={s["sample_id"]: s.get("session") for s in td["samples"]})

    X, Y, samp, bc, xy, genes = H.load_task(td, enc)
    n = X.shape[0]
    state["n_spots"][vtag] = n
    state["dims"][vtag] = X.shape[1]
    print(f"[load] {vtag}/{label_set} {enc}: {n:,} spots x {X.shape[1]} dims, "
          f"{len(genes)} genes, {len(np.unique(samp))} slides, {time.time()-t0:.0f}s",
          flush=True)

    hargs = harness_args(args, [td["_path"]], args.design)
    specs = H.build_fold_specs(td, samp, xy, [args.design], meta, hargs)
    H.size_match_groups(specs, "none")
    print(f"[specs] {vtag} {args.design}: {len(specs)} folds", flush=True)

    P = np.full(Y.shape, np.nan, dtype=np.float64)
    fold_of = np.full(n, "", dtype=object)
    ntimes = np.zeros(n, dtype=int)
    for i, sp in enumerate(specs):
        Tm = H.apply_size_match(sp, task)
        Em = sp["E"]
        assert sp["C"].sum() == 0, "calibration set is not empty; H1 mode not in force"
        assert not (Tm & Em).any(), f"{vtag} {sp['fold']}: T and E overlap"
        # The donor design's pool is every other donor, so this asserts the cross-fitting
        # property B1 needs, per fold, from the masks themselves.
        if args.design == "donor":
            dT = {meta["donor_of"][s] for s in np.unique(samp[Tm])}
            dE = {meta["donor_of"][s] for s in np.unique(samp[Em])}
            assert not (dT & dE), f"{vtag} {sp['fold']}: donor in both T and E"
        pipe, A, reg, ridge_alpha = H.fit_base(X[Tm], Y[Tm])
        B = pipe.transform(X[Em].astype(np.float64, copy=False))
        P[Em] = reg.predict(B)
        fold_of[Em] = str(sp["fold"])
        ntimes[Em] += 1
        print(f"  [{i+1}/{len(specs)}] {vtag} {args.design} fold={sp['fold']} "
              f"n_T={int(Tm.sum())} n_E={int(Em.sum())} {time.time()-t0:.0f}s", flush=True)

    predicted = ntimes > 0
    assert ntimes.max() <= 1, f"{vtag}: {int((ntimes > 1).sum())} spots predicted twice"
    if args.design == "donor":
        assert predicted.all(), (f"{vtag}: {int((~predicted).sum())} spots never "
                                 f"predicted under the donor design")

    # ---- H1 anchor rows: the harness's own aggregation, mean over genes then folds ----
    for sp in specs:
        Em = sp["E"]
        for j, g in enumerate(genes):
            yj, pj = Y[Em][:, j].astype(np.float64), P[Em][:, j]
            r = (float(stats.pearsonr(pj, yj)[0])
                 if np.std(yj) > 0 and np.std(pj) > 0 else np.nan)
            state["h1"].append(dict(encoder=enc, task=task, variant=vtag,
                                    design=args.design, fold=str(sp["fold"]), gene=g,
                                    pearson=r, n_test=int(Em.sum())))
    # ---- prediction quality actually used by B1: pooled over all predicted spots ----
    for j, g in enumerate(genes):
        yj, pj = Y[predicted][:, j].astype(np.float64), P[predicted][:, j]
        state["quality"].append(dict(
            encoder=enc, task=task, variant=vtag, design=args.design, gene=g,
            pearson_pooled=(float(stats.pearsonr(pj, yj)[0])
                            if np.std(yj) > 0 and np.std(pj) > 0 else np.nan),
            n_spots=int(predicted.sum())))

    if args.design != "donor":
        del X, Y
        return time.time() - t0

    # ---------------------------------------------------- morphology join
    am, nf, mpath, mrows = load_morph(task, args.morph_dir)
    keys = np.array([f"{s}\t{b}" for s, b in zip(samp, bc)], dtype=object)
    area = np.array([am.get(k, np.nan) for k in keys], dtype=float)
    neo = np.array([nf.get(k, np.nan) for k in keys], dtype=float)
    join = np.isfinite(area) & np.isfinite(neo) & predicted
    rate = float(join.sum()) / float(n)
    mu_a, sd_a = float(area[join].mean()), float(area[join].std(ddof=0))
    m = (area - mu_a) / sd_a
    print(f"[morph] {vtag}: {mpath} {mrows:,} rows; joined {int(join.sum()):,}/{n:,} = "
          f"{rate:.4f}; area_mean mean {mu_a:.4f} sd {sd_a:.4f}", flush=True)
    for s in sorted(set(samp.tolist())):
        ms = samp == s
        state["join"].append(dict(
            encoder=enc, task=task, variant=vtag, slide=s, n_spots=int(ms.sum()),
            n_joined=int((ms & join).sum()),
            join_rate=float((ms & join).sum()) / float(ms.sum()),
            n_neoplastic_gt=int((ms & join & (neo > NEO_HI)).sum()),
            n_stromal_lt=int((ms & join & (neo < STR_LO)).sum()),
            morph_file=mpath, area_mean_centre=mu_a, area_mean_scale=sd_a,
            task_join_rate=rate))
    assert rate >= args.min_join, (
        f"{vtag}: morphology join rate {rate:.4f} below --min-join {args.min_join}")

    # ---------------------------------------------------- per-spot prediction parquet
    write_predictions(out, vtag, enc, td, samp, bc, fold_of, join, m, neo, area,
                      Y, P, genes, meta, audit_name, state)

    # ---------------------------------------------------- sufficient statistics
    ests = ["theta3", "theta2"] + (["theta1"] if task == THETA1_TASK else [])
    yraw = None
    if task == THETA1_TASK:
        yraw = raw_counts(td, THETA1_GENE, samp, bc)
        jg = genes.index(THETA1_GENE)
        dev = float(np.nanmax(np.abs(np.expm1(Y[:, jg].astype(np.float64)) - yraw)))
        state["theta1_raw"].append(dict(task=task, gene=THETA1_GENE, encoder=enc,
                                        max_abs_expm1_minus_raw=dev,
                                        n_finite=int(np.isfinite(yraw).sum())))
        print(f"[theta1] raw {THETA1_GENE} counts read from AnnData; "
              f"max |expm1(y_log1p) - raw| = {dev:.3e}", flush=True)

    write_suffstats(out, vtag, enc, args, samp, bc, fold_of, join, m, neo, Y, P, genes,
                    meta, ests, yraw, state)
    del X, Y
    return time.time() - t0


def write_predictions(out, vtag, enc, td, samp, bc, fold_of, join, m, neo, area,
                      Y, P, genes, meta, audit_name, state):
    d = pd.DataFrame({
        "sample_id": samp.astype(str), "barcode": bc.astype(str),
        "donor_id": [meta["donor_of"][s] for s in samp],
        "donor_id_audit": [audit_name[s] for s in samp],
        "fold": fold_of.astype(str), "joined": join,
        "area_mean": area, "m_std": m, "frac_neoplastic": neo})
    fields = [(c, pa.string()) for c in ("sample_id", "barcode", "donor_id",
                                         "donor_id_audit", "fold")]
    fields += [("joined", pa.bool_())]
    fields += [(c, pa.float64()) for c in ("area_mean", "m_std", "frac_neoplastic")]
    for j, g in enumerate(genes):
        d[f"y__{g}"] = Y[:, j].astype(np.float32)
        d[f"f__{g}"] = P[:, j].astype(np.float32)
        fields += [(f"y__{g}", pa.float32()), (f"f__{g}", pa.float32())]
    schema = pa.schema(fields)
    path = f"{out}/b1_predictions__{vtag}__{enc}.parquet"
    pq.write_table(pa.Table.from_pandas(d[[f.name for f in schema]], schema=schema,
                                        preserve_index=False), path, compression="snappy")
    print(f"[write] {os.path.basename(path)} ({len(d):,} spots, explicit schema, "
          f"stays on Longleaf)", flush=True)
    state["files"].append(os.path.basename(path) + " (Longleaf only)")


def _suff_for(z, zf, grp_idx, n_grp, chunk):
    """Per-group sums of v = [z; zf] and of v v'. z, zf are (n, G, k)."""
    nsp, G, k = z.shape
    S1 = np.zeros((n_grp, G, 2 * k))
    S2 = np.zeros((n_grp, G, 2 * k, 2 * k))
    for a in range(0, G, chunk):
        b = min(a + chunk, G)
        V = np.concatenate([z[:, a:b, :], zf[:, a:b, :]], axis=2)
        for gi in range(n_grp):
            sel = grp_idx == gi
            if not sel.any():
                continue
            Vs = V[sel]
            S1[gi, a:b, :] += Vs.sum(axis=0)
            S2[gi, a:b, :, :] += np.einsum("ngi,ngj->gij", Vs, Vs)
    return S1, S2


def write_suffstats(out, vtag, enc, args, samp, bc, fold_of, join, m, neo, Y, P, genes,
                    meta, ests, yraw, state):
    """Slide-level sufficient statistics: everything B1 and B2 need is a function of
    per-group sums of z and of z z', so the per-spot table is read once here and never
    again. Groups are SLIDES -- the finest unit any B setting uses, because B2's PRAD
    variant masks slides inside donors -- and the donor is carried as a label per group.

    One set per POPULATION, because z carries that population unit's own design
    constants: the task's for the spot-weighted population, each donor's own for the
    donor-weighted one. Both are label-free.
    """
    js = np.flatnonzero(join)
    slides = sorted(set(samp[js].tolist()))
    gi_of = {s: i for i, s in enumerate(slides)}
    grp_idx = np.array([gi_of[s] for s in samp[js]])
    donor_of_grp = np.array([meta["donor_of"][s] for s in slides], dtype=object)
    n_per_grp = np.bincount(grp_idx, minlength=len(slides))
    donors = sorted(set(donor_of_grp.tolist()))
    don_of_spot = np.array([meta["donor_of"][s] for s in samp[js]], dtype=object)
    don_idx_spot = np.array([donors.index(d) for d in don_of_spot])
    zero_idx = np.zeros(len(js), dtype=int)

    rng = np.random.default_rng(zlib.crc32(f"{vtag}|onespot".encode()))
    one_sel = np.array(sorted(
        np.flatnonzero(don_idx_spot == u)[rng.integers(int((don_idx_spot == u).sum()))]
        for u in range(len(donors))))

    arms = {enc: P}
    if enc == PERMUTE_SOURCE:
        pr = np.random.default_rng(zlib.crc32(f"{vtag}|permute".encode()))
        arms["permuted"] = P[pr.permutation(len(samp))]
        print(f"[permute] `permuted` arm: {PERMUTE_SOURCE} predictions permuted over all "
              f"{len(samp):,} spots of {vtag} under crc32('{vtag}|permute')", flush=True)
        for j, g in enumerate(genes):
            yj = Y[js][:, j].astype(np.float64)
            pj = arms["permuted"][js][:, j].astype(np.float64)
            state["quality"].append(dict(
                encoder="permuted", task=vtag.split("_merged")[0], variant=vtag,
                design="donor", gene=g,
                pearson_pooled=(float(stats.pearsonr(pj, yj)[0])
                                if np.std(yj) > 0 and np.std(pj) > 0 else np.nan),
                n_spots=int(len(js))))

    c_task = design_consts(m[js], neo[js], zero_idx, 1)
    c_don = design_consts(m[js], neo[js], don_idx_spot, len(donors))
    blob = dict(slides=np.array(slides, dtype=object),
                donor_of_slide=donor_of_grp, n_per_slide=n_per_grp,
                onespot_donors=np.array(donors, dtype=object),
                onespot_n_per_donor=np.ones(len(donors), dtype=int))
    for nm, c in (("task", c_task), ("donor", c_don)):
        for key, v in c.items():
            blob[f"const|{nm}|{key}"] = v
    state["consts"].append(dict(
        task=vtag.split("_merged")[0], variant=vtag, encoder=enc, level="task",
        unit="ALL", mu_m=float(c_task["mu_m"][0]), v_m=float(c_task["v_m"][0]),
        p_neo=float(c_task["p_neo"][0]), p_str=float(c_task["p_str"][0]),
        n=int(c_task["n"][0])))
    for u, d in enumerate(donors):
        state["consts"].append(dict(
            task=vtag.split("_merged")[0], variant=vtag, encoder=enc, level="donor",
            unit=str(d), mu_m=float(c_don["mu_m"][u]), v_m=float(c_don["v_m"][u]),
            p_neo=float(c_don["p_neo"][u]), p_str=float(c_don["p_str"][u]),
            n=int(c_don["n"][u])))

    for est in ests:
        spec = ESTIMANDS[est]
        if est == "theta1":
            gl = [THETA1_GENE]
            Yv = yraw[js][:, None]
        else:
            gl = list(genes)
            Yv = Y[js].astype(np.float64)
        blob[f"genes|{est}"] = np.array(gl, dtype=object)
        for pop, c, uidx in (("spot", c_task, zero_idx), ("donor", c_don, don_idx_spot)):
            val = unit_valid(est, c)
            if pop == "spot":
                gvalid = np.full(len(slides), bool(val[0]))
                dvalid = np.full(len(donors), bool(val[0]))
            else:
                gvalid = np.array([bool(val[donors.index(d)]) for d in donor_of_grp])
                dvalid = val.astype(bool)
            blob[f"valid|{est}|{pop}|group"] = gvalid
            blob[f"valid|{est}|{pop}|one"] = dvalid
            if not gvalid.any():
                print(f"[suff] {vtag} {est} {pop}: no valid population unit; skipped",
                      flush=True)
                continue
            z = build_z(est, Yv, m[js], neo[js], c, uidx)
            for arm, Pa in arms.items():
                Pv = (np.expm1(Pa[js][:, [genes.index(THETA1_GENE)]].astype(np.float64))
                      if est == "theta1" else Pa[js].astype(np.float64))
                zf = build_z(est, Pv, m[js], neo[js], c, uidx)
                zz = np.nan_to_num(z, nan=0.0)
                zzf = np.nan_to_num(zf, nan=0.0)
                S1, S2 = _suff_for(zz, zzf, grp_idx, len(slides), args.gene_chunk)
                blob[f"full|{arm}|{est}|{pop}|S1"] = S1
                blob[f"full|{arm}|{est}|{pop}|S2"] = S2
                S1o, S2o = _suff_for(zz[one_sel], zzf[one_sel], don_idx_spot[one_sel],
                                     len(donors), args.gene_chunk)
                blob[f"one|{arm}|{est}|{pop}|S1"] = S1o
                blob[f"one|{arm}|{est}|{pop}|S2"] = S2o
            print(f"[suff] {vtag} {est} {pop}: {len(slides)} slides x {len(gl)} genes x "
                  f"{2*spec['k']} components, {int(gvalid.sum())} valid groups, "
                  f"arms {sorted(arms)}", flush=True)
    path = f"{out}/b1_suffstats__{vtag}__{enc}.npz"
    np.savez_compressed(path, **blob)
    print(f"[write] {os.path.basename(path)} (stays on Longleaf)", flush=True)
    state["files"].append(os.path.basename(path) + " (Longleaf only)")


def h1_anchor(out, suf, enc, state, args):
    """The anchor: our cal-fraction-zero `patient` per-task Pearson against A0's H1."""
    h1 = pd.DataFrame(state["h1"])
    ours = (h1.groupby(["task", "fold"])["pearson"].mean()
              .groupby("task").mean().rename("ours_b1").reset_index())
    src = f"{ROOT}/{args.a0_dir}/h1_by_task__{enc}__h1.csv"
    assert os.path.exists(src), f"{src} absent; the B1 anchor cannot be evaluated"
    a0 = pd.read_csv(src)[["task", "ours", "r1b_intercept_f64"]].rename(
        columns={"ours": "a0_h1_ours"})
    cmp = ours.merge(a0, on="task", how="left")
    cmp["abs_diff_vs_a0"] = (cmp["ours_b1"] - cmp["a0_h1_ours"]).abs()
    cmp["abs_diff_vs_r1b"] = (cmp["ours_b1"] - cmp["r1b_intercept_f64"]).abs()
    cmp["tol"] = args.anchor_tol
    cmp["passed"] = cmp["abs_diff_vs_a0"] < args.anchor_tol
    cmp["encoder"] = enc
    cmp["a0_source"] = os.path.relpath(src, ROOT)
    cmp.to_csv(f"{out}/b1_h1_anchor{suf}.csv", index=False)
    state["files"].append(f"b1_h1_anchor{suf}.csv")
    print(f"\n=== B1 ANCHOR: cal-fraction-zero `patient` Pearson vs A0 H1 ===")
    print(cmp.to_string(index=False), flush=True)
    npass, ntot = int(cmp["passed"].sum()), len(cmp)
    mx = float(cmp["abs_diff_vs_a0"].max())
    print(f"ANCHOR: {npass}/{ntot} task cells within {args.anchor_tol:g}; "
          f"max |diff| = {mx:.3e}  {'PASS' if npass == ntot else 'FAIL'}", flush=True)
    return npass == ntot


# =========================================================== the estimator core
def _agg(S1, S2, n_per, sel):
    """Sum sufficient statistics over the selected groups. Returns (T1, T2, n)."""
    if not np.any(sel):
        return None, None, 0
    return S1[sel].sum(axis=0), S2[sel].sum(axis=0), int(n_per[sel].sum())


def _lin(S1, S2, w):
    """Per group and gene: s1 = sum_i w'v_i and s2 = sum_i (w'v_i)^2, for w of shape
    (G, 2k). S1 is (n_grp, G, 2k) and S2 is (n_grp, G, 2k, 2k)."""
    s1 = np.einsum("sgi,gi->sg", S1, w)
    s2 = np.einsum("gi,sgij,gj->sg", w, S2, w)
    return s1, s2


def _infl(s1, s2, n_per, sel, n_tot):
    """Per-group influence totals q_g = sum_{i in g} h_i and per-group sums of squared
    per-spot influence, for h_i = (w'v_i - mean_set(w'v)) / n_tot."""
    mw = s1[sel].sum(axis=0) / n_tot
    q = (s1 - n_per[:, None] * mw[None, :]) / n_tot
    sq = (s2 - 2.0 * mw[None, :] * s1 + n_per[:, None] * mw[None, :] ** 2) / n_tot ** 2
    return q, sq


def _wv(grad):
    return np.concatenate([np.zeros_like(grad), grad], axis=-1)


def _wu(grad, lam):
    return np.concatenate([grad, -lam[:, None] * grad], axis=-1)


def cell_spot(S1, S2, n_per, donor_idx, Lg, Ug, est, alpha, n_boot, seed,
              lam_fixed=None, cluster_form="separate"):
    """One (estimand, gene-vector) cell under the SPOT-weighted population.

    Lg and Ug are boolean masks over GROUPS. Returns a dict of (G,) arrays.
    """
    spec = ESTIMANDS[est]
    k = spec["k"]
    T1L, _, nL = _agg(S1, S2, n_per, Lg)
    T1U, _, nU = _agg(S1, S2, n_per, Ug)
    T1A, _, nA = _agg(S1, S2, n_per, Lg | Ug)
    G = S1.shape[1]
    out = dict(n_L_spots=nL, n_U_spots=nU, n_spots=nA, status="ok")

    out["theta_full"] = spec["value"](T1A[:, :k] / nA)
    mu_L = T1L[:, :k] / nL
    muf_L = T1L[:, k:] / nL
    out["theta_classical"] = spec["value"](mu_L)

    donors_L = sorted(set(donor_idx[Lg].tolist()))
    donors_U = sorted(set(donor_idx[Ug].tolist())) if nU else []
    G_L, G_U = len(donors_L), len(donors_U)
    out["G_L"], out["G_U"] = G_L, G_U

    def by_donor(vals, mask, dl):
        return (np.stack([vals[mask & (donor_idx == d)].sum(axis=0) for d in dl], axis=0)
                if dl else np.zeros((0, G)))

    # ---- lambda ----------------------------------------------------------------
    # Tuned on the SPOT-LEVEL (independent-observations) variance decomposition, which is
    # PPI++'s own prescription, and NOT on the donor-clustered residuals that form the
    # reported interval. Measured reason, recorded rather than asserted: minimising the
    # donor-clustered variance over lambda fits one parameter to G_L donor-level
    # residuals, and at G_L = 2 the two residuals sum to zero, so lambda =
    # q_a,1 / q_b,1 drives the estimated clustered variance to exactly zero. On the
    # synthetic fixture that produced permuted-arm width ratios of 0.13 with
    # lambda_hat = 1, which is the small-G pathology Cameron and Miller (2015) and
    # MacKinnon, Nielsen and Webb (2023) describe, not a property of the data. The
    # cluster-tuned lambda is still computed and reported as `lambda_cluster_tuned` so
    # the size of that effect is a number in the table.
    #
    # Validity does not depend on the choice: the PPI estimating equation is unbiased for
    # ANY lambda and the variance is estimated at the lambda actually used, so tuning only
    # trades efficiency. With U empty lambda is 0 by construction.
    grad0 = spec["grad"](mu_L)
    zer = np.zeros_like(grad0)
    lam_clu = np.full(G, np.nan)
    if lam_fixed is not None:
        lam = np.full(G, float(lam_fixed))
        basis = "fixed"
    elif G_U == 0:
        lam = np.zeros(G)
        basis = "U_empty"
    else:
        s1v, s2v = _lin(S1, S2, _wv(grad0))
        s1u, s2u = _lin(S1, S2, np.concatenate([grad0, zer], axis=-1))
        qU, sqU = _infl(s1v, s2v, n_per, Ug, nU)
        qa, sqa = _infl(s1u, s2u, n_per, Lg, nL)
        qb, sqb = _infl(s1v, s2v, n_per, Lg, nL)
        # Polarisation identity: sum (a-abar)(b-bbar) = (Sa2 + Sb2 - S(a-b)2)/2.
        _, sqd = _infl(*_lin(S1, S2, np.concatenate([grad0, -grad0], axis=-1)),
                       n_per, Lg, nL)
        cov = 0.5 * (sqa[Lg].sum(0) + sqb[Lg].sum(0) - sqd[Lg].sum(0))
        fU = nU / (nU - 1.0) if nU > 1 else np.inf
        fL = nL / (nL - 1.0) if nL > 1 else np.inf
        num = fL * cov
        den = fU * sqU[Ug].sum(0) + fL * sqb[Lg].sum(0)
        basis = "spot_iid"
        lam = np.where(den > 0, np.clip(num / np.where(den > 0, den, 1.0), 0.0, 1.0), 0.0)
        if G_U > 1 and G_L > 1:
            cU, cL = G_U / (G_U - 1.0), G_L / (G_L - 1.0)
            dU, da, db = (by_donor(qU, Ug, donors_U), by_donor(qa, Lg, donors_L),
                          by_donor(qb, Lg, donors_L))
            nc = cL * (da * db).sum(axis=0)
            dc = cU * (dU ** 2).sum(axis=0) + cL * (db ** 2).sum(axis=0)
            lam_clu = np.where(dc > 0,
                               np.clip(nc / np.where(dc > 0, dc, 1.0), 0.0, 1.0), 0.0)
    out["lambda"] = lam
    out["lambda_basis"] = basis
    out["lambda_cluster_tuned"] = lam_clu

    mu_pp = (lam[:, None] * (T1U[:, k:] / nU) if nU else 0.0) \
        + mu_L - lam[:, None] * muf_L
    out["theta_pp"] = spec["value"](mu_pp)

    # ---- the three variances, for both estimators, from ONE influence function ----
    df = None
    for lm, key in ((np.zeros(G), "cl"), (lam, "pp")):
        grad = spec["grad"](mu_L if key == "cl" else mu_pp)
        qL, sqL = _infl(*_lin(S1, S2, _wu(grad, lm)), n_per, Lg, nL)
        if key == "pp" and nU:
            q0, s0 = _infl(*_lin(S1, S2, _wv(grad)), n_per, Ug, nU)
            qU = lm[None, :] * q0
            sqU = (lm[None, :] ** 2) * s0
        else:
            qU = np.zeros((S1.shape[0], G))
            sqU = np.zeros((S1.shape[0], G))
        fL = nL / (nL - 1.0) if nL > 1 else np.nan
        v_iid = fL * sqL[Lg].sum(0)
        if nU > 1:
            v_iid = v_iid + (nU / (nU - 1.0)) * sqU[Ug].sum(0)
        if cluster_form == "separate":
            dL = by_donor(qL, Lg, donors_L)
            cL = G_L / (G_L - 1.0) if G_L > 1 else np.nan
            v_clu = cL * (dL ** 2).sum(0)
            if G_U > 1:
                v_clu = v_clu + (G_U / (G_U - 1.0)) \
                    * (by_donor(qU, Ug, donors_U) ** 2).sum(0)
            elif G_U == 1 and key == "pp":
                v_clu = np.full(G, np.nan)
            df = G_L - 1
        else:
            dall = sorted(set(donor_idx[Lg | Ug].tolist()))
            tot = by_donor(qL, Lg, dall) + by_donor(qU, Ug, dall)
            Gc = len(dall)
            v_clu = ((Gc / (Gc - 1.0)) * (tot ** 2).sum(0) if Gc > 1
                     else np.full(G, np.nan))
            df = Gc - 1
        out[f"se_iid_{key}"] = np.sqrt(np.maximum(v_iid, 0.0))
        out[f"se_cluster_{key}"] = np.sqrt(np.maximum(v_clu, 0.0))
    out["df_cluster"] = df
    out["cluster_variance_form"] = cluster_form

    out.update(_boot_spot(S1, n_per, donor_idx, Lg, Ug, donors_L, donors_U, est, lam,
                          alpha, n_boot, seed))
    return out


def _boot_spot(S1, n_per, donor_idx, Lg, Ug, donors_L, donors_U, est, lam, alpha,
               n_boot, seed):
    """Donors resampled with replacement within L and, independently, within U; lambda
    held at its full-sample value, as PPI++ does. Vectorised over draws and genes."""
    spec = ESTIMANDS[est]
    k = spec["k"]
    rng = np.random.default_rng(zlib.crc32(str(seed).encode()))

    def draws(mask, dl):
        dS = np.stack([S1[mask & (donor_idx == d)].sum(axis=0) for d in dl], axis=0)
        dn = np.array([n_per[mask & (donor_idx == d)].sum() for d in dl], dtype=float)
        # Multinomial counts over the donors are the with-replacement donor bootstrap;
        # as a matmul it is two orders of magnitude cheaper than a fancy-index gather,
        # which matters because B2 calls this 40,000 times.
        cnt = rng.multinomial(len(dl), np.full(len(dl), 1.0 / len(dl)), size=n_boot)
        sh = dS.shape
        t = (cnt @ dS.reshape(sh[0], -1)).reshape(n_boot, sh[1], sh[2])
        return t, (cnt @ dn)[:, None, None]

    tL, nLb = draws(Lg, donors_L)
    muL, mufL = tL[:, :, :k] / nLb, tL[:, :, k:] / nLb
    cl = spec["value"](muL)
    if donors_U:
        tU, nUb = draws(Ug, donors_U)
        lm = lam[None, :, None]
        pp = spec["value"](lm * (tU[:, :, k:] / nUb) + muL - lm * mufL)
    else:
        pp = cl
    q = [100.0 * alpha / 2.0, 100.0 * (1.0 - alpha / 2.0)]
    return dict(boot_lo_cl=np.percentile(cl, q[0], axis=0),
                boot_hi_cl=np.percentile(cl, q[1], axis=0),
                boot_lo_pp=np.percentile(pp, q[0], axis=0),
                boot_hi_pp=np.percentile(pp, q[1], axis=0),
                se_boot_cl=cl.std(axis=0, ddof=1), se_boot_pp=pp.std(axis=0, ddof=1),
                n_boot=n_boot)


def cell_donor(S1, S2, n_per, donor_idx, Lg, Ug, est, alpha, n_boot, seed,
               lam_fixed=None, cluster_form="separate"):
    """One cell under the DONOR-weighted population: theta = mean over donors of the
    donor-level value. A scalar-mean PPI problem whose observations are donors."""
    spec = ESTIMANDS[est]
    k = spec["k"]
    G = S1.shape[1]
    dl_all = sorted(set(donor_idx.tolist()))
    donors_L = sorted(set(donor_idx[Lg].tolist()))
    donors_U = sorted(set(donor_idx[Ug].tolist())) if np.any(Ug) else []
    overlap = sorted(set(donors_L) & set(donors_U))
    out = dict(G_L=len(donors_L), G_U=len(donors_U),
               n_L_spots=int(n_per[Lg].sum()), n_U_spots=int(n_per[Ug].sum()),
               n_spots=int(n_per[Lg | Ug].sum()),
               cluster_variance_form=cluster_form)
    if overlap:
        out["status"] = "donor_partially_labelled_not_applicable"
        return out
    out["status"] = "ok"

    def dvals(mask, dl):
        t = np.full((len(dl), G), np.nan)
        tf = np.full((len(dl), G), np.nan)
        nd = np.zeros(len(dl))
        for i, d in enumerate(dl):
            sel = mask & (donor_idx == d)
            T1 = S1[sel].sum(axis=0)
            nn = float(n_per[sel].sum())
            nd[i] = nn
            t[i] = spec["value"](T1[:, :k] / nn)
            tf[i] = spec["value"](T1[:, k:] / nn)
        return t, tf, nd

    tL, tfL, ndL = dvals(Lg, donors_L)
    tA, _, ndA = dvals(Lg | Ug, dl_all)
    out["theta_full"] = np.nanmean(tA, axis=0)
    out["theta_classical"] = tL.mean(axis=0)
    G_L, G_U = len(donors_L), len(donors_U)
    if G_U:
        tU, tfU, ndU = dvals(Ug, donors_U)

    # lambda for a DONOR-weighted estimand can only be tuned on the G_L labelled donor
    # pairs (t_d, t_hat_d): there is no within-donor replication of a donor-level value.
    # With fewer than MIN_TUNE_G labelled donors that is one or two degrees of freedom and
    # minimising over lambda drives the estimated variance to zero, so no tuning is done
    # and lambda is 0, which makes PPI equal to classical and is reported as such. That is
    # itself the donor-limited-information result rather than a workaround.
    if lam_fixed is not None:
        lam = np.full(G, float(lam_fixed))
        basis = "fixed"
    elif G_U == 0:
        lam = np.zeros(G)
        basis = "U_empty"
    elif G_L < MIN_TUNE_G or G_U < 2:
        lam = np.zeros(G)
        basis = f"no_tuning_G_L_{G_L}_G_U_{G_U}_below_{MIN_TUNE_G}"
    else:
        aL = tL - tL.mean(axis=0)
        bL = tfL - tfL.mean(axis=0)
        dU = tfU - tfU.mean(axis=0)
        cU, cL = G_U / (G_U - 1.0), G_L / (G_L - 1.0)
        num = cL * (aL * bL).sum(0) / G_L ** 2
        den = cU * (dU ** 2).sum(0) / G_U ** 2 + cL * (bL ** 2).sum(0) / G_L ** 2
        basis = "donor_pairs"
        lam = np.where(den > 0, np.clip(num / np.where(den > 0, den, 1.0), 0.0, 1.0), 0.0)
    out["lambda"] = lam
    out["lambda_basis"] = basis
    out["lambda_cluster_tuned"] = lam.copy()
    out["theta_pp"] = (lam * tfU.mean(axis=0) + (tL - lam * tfL).mean(axis=0)
                       if G_U else tL.mean(axis=0))

    for name, lm, key in (("classical", np.zeros(G), "cl"), ("pp", lam, "pp")):
        th = out["theta_classical"] if name == "classical" else out["theta_pp"]
        devL = (tL - lm * tfL) - (tL - lm * tfL).mean(axis=0)
        cL = G_L / (G_L - 1.0) if G_L > 1 else np.nan
        fL = out["n_L_spots"] / (out["n_L_spots"] - 1.0)
        v_iid = fL * (devL ** 2 / ndL[:, None]).sum(0) / G_L ** 2
        v_clu = cL * (devL ** 2).sum(0) / G_L ** 2
        if name == "pp" and G_U:
            devU = tfU - tfU.mean(axis=0)
            cU = G_U / (G_U - 1.0) if G_U > 1 else np.nan
            fU = out["n_U_spots"] / (out["n_U_spots"] - 1.0)
            v_iid = v_iid + (lm ** 2) * fU * (devU ** 2 / ndU[:, None]).sum(0) / G_U ** 2
            v_clu = v_clu + (lm ** 2) * cU * (devU ** 2).sum(0) / G_U ** 2
        out[f"se_iid_{key}"] = np.sqrt(np.maximum(v_iid, 0.0))
        out[f"se_cluster_{key}"] = np.sqrt(np.maximum(v_clu, 0.0))
    out["df_cluster"] = G_L - 1

    rng = np.random.default_rng(zlib.crc32(str(seed).encode()))
    cL_ = rng.multinomial(G_L, np.full(G_L, 1.0 / G_L), size=n_boot) / float(G_L)
    cl = cL_ @ tL
    if G_U:
        cU_ = rng.multinomial(G_U, np.full(G_U, 1.0 / G_U), size=n_boot) / float(G_U)
        pp = lam[None, :] * (cU_ @ tfU) + (cL_ @ tL) - lam[None, :] * (cL_ @ tfL)
    else:
        pp = cl
    q = [100.0 * alpha / 2.0, 100.0 * (1.0 - alpha / 2.0)]
    out.update(boot_lo_cl=np.percentile(cl, q[0], axis=0),
               boot_hi_cl=np.percentile(cl, q[1], axis=0),
               boot_lo_pp=np.percentile(pp, q[0], axis=0),
               boot_hi_pp=np.percentile(pp, q[1], axis=0),
               se_boot_cl=cl.std(axis=0, ddof=1), se_boot_pp=pp.std(axis=0, ddof=1),
               n_boot=n_boot)
    return out


CELL = {"spot": cell_spot, "donor": cell_donor}


def intervals(res, alpha):
    """The three intervals per estimator, from the cell's SEs and bootstrap quantiles."""
    z = stats.norm.ppf(1.0 - alpha / 2.0)
    df = res.get("df_cluster", 0)
    tq = stats.t.ppf(1.0 - alpha / 2.0, df) if df and df > 0 else np.nan
    o = {}
    for key, nm in (("cl", "classical"), ("pp", "pp")):
        th = res["theta_classical"] if key == "cl" else res["theta_pp"]
        o[f"{nm}|iid|lo"] = th - z * res[f"se_iid_{key}"]
        o[f"{nm}|iid|hi"] = th + z * res[f"se_iid_{key}"]
        o[f"{nm}|cluster|lo"] = th - tq * res[f"se_cluster_{key}"]
        o[f"{nm}|cluster|hi"] = th + tq * res[f"se_cluster_{key}"]
        o[f"{nm}|boot|lo"] = res[f"boot_lo_{key}"]
        o[f"{nm}|boot|hi"] = res[f"boot_hi_{key}"]
    o["t_quantile"] = tq
    o["z_quantile"] = z
    return o


# ------------------------------------------------- loading sufficient statistics
def load_suff(out, vtag, arm, est, pop, block="full"):
    """Sufficient statistics for one (task variant, arm, estimand, population). The
    `identity` arm is constructed here from the measured block, so `f := y` exactly with
    no second run and no second parquet."""
    src = PERMUTE_SOURCE if arm in ("permuted", "identity") else arm
    p = f"{out}/b1_suffstats__{vtag}__{src}.npz"
    if not os.path.exists(p):
        return None
    z = np.load(p, allow_pickle=True)
    key_arm = "permuted" if arm == "permuted" else src
    k1 = f"{block}|{key_arm}|{est}|{pop}|S1"
    if k1 not in z:
        return None
    S1, S2 = z[k1], z[f"{block}|{key_arm}|{est}|{pop}|S2"]
    k = ESTIMANDS[est]["k"]
    if arm == "identity":
        S1 = np.concatenate([S1[:, :, :k], S1[:, :, :k]], axis=2)
        S2b = S2[:, :, :k, :k]
        S2 = np.concatenate([np.concatenate([S2b, S2b], axis=3),
                             np.concatenate([S2b, S2b], axis=3)], axis=2)
    if block == "full":
        slides, dos, npg = z["slides"], z["donor_of_slide"], z["n_per_slide"]
        valid = z[f"valid|{est}|{pop}|group"]
    else:
        slides = z["onespot_donors"]
        dos = z["onespot_donors"]
        npg = z["onespot_n_per_donor"]
        valid = z[f"valid|{est}|{pop}|one"]
    dl = sorted(set(dos.tolist()))
    didx = np.array([dl.index(d) for d in dos])
    vd = sorted({d for d, ok in zip(dos.tolist(), valid.tolist()) if ok})
    return dict(S1=S1, S2=S2, n_per=np.asarray(npg, dtype=float), donor_idx=didx,
                donors=np.array(dl, dtype=object), slides=slides, valid=np.asarray(valid),
                valid_donors=np.array(vd, dtype=object),
                genes=[str(g) for g in z[f"genes|{est}"]], path=os.path.basename(p))


def draw_L(donors, n_L, seed):
    rng = np.random.default_rng(zlib.crc32(seed.encode()))
    return sorted(rng.permutation(np.asarray(donors, dtype=object))[:n_L].tolist())


def group_mask(d, donor_names):
    return np.isin(d["donors"][d["donor_idx"]], list(donor_names))


# =========================================================== ESTIMATE mode
def run_estimate(args):
    t0 = time.time()
    out = f"{ROOT}/{args.out_dir}"
    variants = [v for v in NL_SETTINGS
                if os.path.exists(f"{out}/b1_suffstats__{v}__{PERMUTE_SOURCE}.npz")]
    assert variants, f"no b1_suffstats__*__{PERMUTE_SOURCE}.npz under {out}"
    print(f"[estimate] variants {variants}", flush=True)
    arms = list(ENCODERS) + ["permuted"]

    acc = acceptance(out, variants, args)
    pd.DataFrame(acc).to_csv(f"{out}/b1_acceptance.csv", index=False)
    print(f"\n=== B1 ACCEPTANCE (written first) ===")
    print(pd.DataFrame(acc).to_string(index=False), flush=True)

    rows = []
    for v in variants:
        for est in ("theta3", "theta2", "theta1"):
            for arm in arms:
                for pop in ("spot", "donor"):
                    d = load_suff(out, v, arm, est, pop)
                    if d is None:
                        continue
                    for n_L in NL_SETTINGS[v]:
                        Ld = draw_L(d["valid_donors"], n_L, f"{v}|nL{n_L}")
                        Lg = group_mask(d, Ld) & d["valid"]
                        Ug = (~group_mask(d, Ld)) & d["valid"]
                        res = CELL[pop](d["S1"], d["S2"], d["n_per"], d["donor_idx"],
                                        Lg, Ug, est, args.alpha, args.n_boot,
                                        f"{v}|{arm}|{est}|{pop}|{n_L}")
                        rows += emit(res, args, v, arm, est, pop, n_L, Ld, d)
        print(f"[estimate] {v}: {len(rows)} rows so far {time.time()-t0:.0f}s", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(f"{out}/b1_estimates.csv", index=False)
    print(f"[write] b1_estimates.csv ({len(df)} rows)", flush=True)

    t1 = theta1_by_slide(out, args)
    if t1 is not None:
        t1.to_csv(f"{out}/b1_theta1_by_slide.csv", index=False)
        print(f"[write] b1_theta1_by_slide.csv ({len(t1)} rows)", flush=True)

    cfg = dict(stage="round3_B1_estimate", script="code/scripts/round3_b1_ppi.py",
               variants=variants, arms=arms, alpha=args.alpha, n_boot=args.n_boot,
               nl_settings={k: list(v) for k, v in NL_SETTINGS.items()},
               neo_hi=NEO_HI, str_lo=STR_LO, estimands=sorted(ESTIMANDS),
               exact_tol=args.exact_tol, seed_source="zlib.crc32")
    blob = json.dumps(cfg, sort_keys=True)
    chash = hashlib.sha256(blob.encode()).hexdigest()[:16]
    st = dict(files=["b1_acceptance.csv", "b1_estimates.csv",
                     "b1_theta1_by_slide.csv"],
              wall={}, n_spots={}, dims={})
    ad = pd.DataFrame(acc)
    ev = ad[ad["evaluable"]] if "evaluable" in ad.columns else ad
    ok = bool(ev["passed"].all())
    nne = int((~ad["evaluable"]).sum()) if "evaluable" in ad.columns else 0
    print(f"[acceptance] {int(ev['passed'].sum())}/{len(ev)} evaluable checks passed; "
          f"{nne} rows not evaluable", flush=True)
    provenance(out, "estimate", cfg, blob, chash, st, time.time() - t0, ok)
    print(f"\n[done] estimate {time.time()-t0:.0f}s acceptance="
          f"{'PASS' if ok else 'FAIL'}", flush=True)
    return 0 if ok else 5


def emit(res, args, v, arm, est, pop, n_L, Ld, d):
    if res.get("status", "ok") != "ok":
        return [dict(variant=v, arm=arm, estimand=est, population=pop, n_L_donors=n_L,
                     gene=g, status=res["status"]) for g in d["genes"]]
    iv = intervals(res, args.alpha)
    rows = []
    for j, g in enumerate(d["genes"]):
        r = dict(variant=v, arm=arm, estimand=est, population=pop, gene=g,
                 status="ok", n_L_donors=int(res["G_L"]), n_U_donors=int(res["G_U"]),
                 n_L_spots=int(res["n_L_spots"]), n_U_spots=int(res["n_U_spots"]),
                 L_donors=";".join(map(str, Ld)),
                 theta_full=float(res["theta_full"][j]),
                 theta_classical=float(res["theta_classical"][j]),
                 theta_pp=float(res["theta_pp"][j]),
                 lam=float(res["lambda"][j]), lambda_basis=res["lambda_basis"],
                 lambda_cluster_tuned=float(res["lambda_cluster_tuned"][j]),
                 df_cluster=int(res["df_cluster"]),
                 cluster_variance_form=res["cluster_variance_form"],
                 t_quantile=float(iv["t_quantile"]), n_boot=int(res["n_boot"]),
                 suffstats_file=d["path"])
        for key, nm in (("cl", "classical"), ("pp", "pp")):
            r[f"se_iid_{nm}"] = float(res[f"se_iid_{key}"][j])
            r[f"se_cluster_{nm}"] = float(res[f"se_cluster_{key}"][j])
            r[f"se_boot_{nm}"] = float(res[f"se_boot_{key}"][j])
        for nm in ("classical", "pp"):
            for vr in ("iid", "cluster", "boot"):
                lo, hi = iv[f"{nm}|{vr}|lo"][j], iv[f"{nm}|{vr}|hi"][j]
                r[f"{nm}_{vr}_lo"] = float(lo)
                r[f"{nm}_{vr}_hi"] = float(hi)
                r[f"{nm}_{vr}_width"] = float(hi - lo)
                r[f"{nm}_{vr}_covers_full"] = bool(lo <= res["theta_full"][j] <= hi)
        for vr in ("iid", "cluster", "boot"):
            wc = r[f"classical_{vr}_width"]
            r[f"width_ratio_{vr}"] = float(r[f"pp_{vr}_width"] / wc) if wc > 0 else np.nan
        # Section 4.7's "why": with m spots per donor and between-donor variance share
        # rho, the variance of a mean is inflated by 1 + (m-1) rho over the i.i.d.
        # formula, so the effective sample size is about n_donors / rho. These three
        # columns are that identity read backwards from the two variances actually
        # computed, which is what the n_eff paragraph of the B1 report quotes.
        for nm in ("classical", "pp"):
            a, b = r[f"se_iid_{nm}"], r[f"se_cluster_{nm}"]
            infl = (b / a) ** 2 if (a > 0 and np.isfinite(b)) else np.nan
            mbar = res["n_L_spots"] / max(res["G_L"], 1)
            r[f"var_inflation_{nm}"] = float(infl)
            r[f"rho_implied_{nm}"] = (float((infl - 1.0) / (mbar - 1.0))
                                      if np.isfinite(infl) and mbar > 1 else np.nan)
            rho = r[f"rho_implied_{nm}"]
            r[f"n_eff_implied_{nm}"] = (float(res["G_L"] / rho)
                                        if np.isfinite(rho) and rho > 0 else np.nan)
        r["m_bar_spots_per_labelled_donor"] = float(
            res["n_L_spots"] / max(res["G_L"], 1))
        rows.append(r)
    return rows


def theta1_by_slide(out, args):
    """theta_1 per IDC slide and pooled, under the four-donor labels. Per slide there is
    one donor, so the donor-clustered interval has G = 1 and no degrees of freedom; that
    is the point of the illustration and is recorded rather than worked around."""
    rows = []
    for arm in list(ENCODERS) + ["permuted"]:
        d = load_suff(out, THETA1_TASK, arm, "theta1", "spot")
        if d is None:
            continue
        k = ESTIMANDS["theta1"]["k"]
        z = stats.norm.ppf(1.0 - args.alpha / 2.0)
        for i, s in enumerate(d["slides"]):
            T1 = d["S1"][i]
            nn = float(d["n_per"][i])
            mu, muf = T1[:, :k] / nn, T1[:, k:] / nn
            grad = ESTIMANDS["theta1"]["grad"](mu)
            w = np.concatenate([grad, np.zeros_like(grad)], axis=-1)
            one = np.array([True])
            _, sq = _infl(*_lin(d["S1"][i:i + 1], d["S2"][i:i + 1], w),
                          d["n_per"][i:i + 1], one, nn)
            se = np.sqrt(np.maximum(sq[0] * nn / (nn - 1.0), 0.0))
            for j, g in enumerate(d["genes"]):
                rows.append(dict(arm=arm, level="slide", slide=str(s),
                                 donor=str(d["donors"][d["donor_idx"][i]]),
                                 gene=g, n_spots=int(nn),
                                 theta=float(ESTIMANDS["theta1"]["value"](mu)[j]),
                                 theta_pred=float(ESTIMANDS["theta1"]["value"](muf)[j]),
                                 se_iid=float(se[j]),
                                 iid_lo=float(ESTIMANDS["theta1"]["value"](mu)[j]
                                              - z * se[j]),
                                 iid_hi=float(ESTIMANDS["theta1"]["value"](mu)[j]
                                              + z * se[j]),
                                 G=1, df_cluster=0,
                                 note="one donor per slide: no donor degrees of freedom"))
        for pop in ("spot", "donor"):
            dp = load_suff(out, THETA1_TASK, arm, "theta1", pop)
            Lg = dp["valid"].copy()
            res = CELL[pop](dp["S1"], dp["S2"], dp["n_per"], dp["donor_idx"], Lg, ~Lg,
                            "theta1", args.alpha, args.n_boot, f"theta1|pooled|{pop}")
            iv = intervals(res, args.alpha)
            for j, g in enumerate(d["genes"]):
                rows.append(dict(arm=arm, level=f"pooled_{pop}", slide="ALL",
                                 donor="ALL", gene=g, n_spots=int(res["n_spots"]),
                                 theta=float(res["theta_classical"][j]),
                                 theta_pred=np.nan,
                                 se_iid=float(res["se_iid_cl"][j]),
                                 iid_lo=float(iv["classical|iid|lo"][j]),
                                 iid_hi=float(iv["classical|iid|hi"][j]),
                                 se_cluster=float(res["se_cluster_cl"][j]),
                                 cluster_lo=float(iv["classical|cluster|lo"][j]),
                                 cluster_hi=float(iv["classical|cluster|hi"][j]),
                                 G=int(res["G_L"]), df_cluster=int(res["df_cluster"]),
                                 note="all donors labelled; U empty"))
    return pd.DataFrame(rows) if rows else None


# =========================================================== acceptance
def acceptance(out, variants, args):
    """The four section 4.7 checks. Every one is MEASURED and none asserted.

    Checks 1, 2 and 3 are exact algebraic identities of the estimator and are reported
    against --exact-tol. Check 4 is not an identity and is reported as such:

      - "the PPI interval is at least as wide as the classical one" cannot hold as a
        strict inequality for a lambda_hat that MINIMISES the estimated variance over
        lambda, because lambda = 0 (the classical estimator) is inside the feasible set,
        so any lambda_hat > 0 gives a narrower estimated interval. For a useless predictor
        the substantive statement is that lambda_hat is near zero and the ratio near one;
        the ratio is therefore checked against 1 - --permuted-tol and the realised
        lambda_hat is reported beside it.
      - "still covers" is a repeated-sampling statement and cannot be checked on one
        partition, where a valid 90% interval misses one gene in ten by construction. The
        per-gene coverage at this partition is reported, and the authoritative version of
        the check is B2's 200-draw coverage.
    """
    rows = []
    tol = args.exact_tol
    for v in variants:  # noqa: C901
        for est in ("theta3", "theta2", "theta1"):
            for pop in ("spot", "donor"):
                d = load_suff(out, v, PERMUTE_SOURCE, est, pop)
                if d is None:
                    continue
                # ---- 1. U empty: PPI equals classical exactly ----
                Lg = d["valid"].copy()
                r = CELL[pop](d["S1"], d["S2"], d["n_per"], d["donor_idx"], Lg, ~Lg,
                              est, args.alpha, 5, f"acc1|{v}|{est}|{pop}")
                dev = float(np.max(np.abs(r["theta_pp"] - r["theta_classical"])))
                rows.append(dict(check="1_U_empty_pp_equals_classical", variant=v,
                                 estimand=est, population=pop, arm=PERMUTE_SOURCE,
                                 statistic="max|theta_pp - theta_classical|",
                                 value=dev, tol=tol, passed=bool(dev <= tol),
                                 detail=f"lambda_basis={r['lambda_basis']}, "
                                        f"G_L={r['G_L']}, G_U={r['G_U']}"))
                # ---- 2. f == y: PPI equals the full-data value at the identity lambda --
                di = load_suff(out, v, "identity", est, pop)
                n_L = NL_SETTINGS[v][0]
                Ld = draw_L(di["valid_donors"], n_L, f"{v}|nL{n_L}")
                Lg = group_mask(di, Ld) & di["valid"]
                Ug = (~group_mask(di, Ld)) & di["valid"]
                nU = float(di["n_per"][Ug].sum())
                nLs = float(di["n_per"][Lg].sum())
                GU = len(set(di["donor_idx"][Ug].tolist()))
                GL = len(set(di["donor_idx"][Lg].tolist()))
                lam_id = (nU / (nU + nLs)) if pop == "spot" else (GU / (GU + GL))
                r = CELL[pop](di["S1"], di["S2"], di["n_per"], di["donor_idx"], Lg, Ug,
                              est, args.alpha, 5, f"acc2|{v}|{est}|{pop}",
                              lam_fixed=lam_id)
                dev = float(np.max(np.abs(r["theta_pp"] - r["theta_full"])))
                rows.append(dict(check="2_perfect_predictions_pp_equals_full", variant=v,
                                 estimand=est, population=pop, arm="identity",
                                 statistic="max|theta_pp - theta_full| at the identity "
                                           "lambda",
                                 value=dev, tol=tol, passed=bool(dev <= tol),
                                 detail=f"lambda={lam_id:.6f} (population weight of U), "
                                        f"n_L={n_L}"))
                rh = CELL[pop](di["S1"], di["S2"], di["n_per"], di["donor_idx"], Lg, Ug,
                               est, args.alpha, 5, f"acc2b|{v}|{est}|{pop}")
                devh = float(np.max(np.abs(rh["theta_pp"] - rh["theta_full"])))
                rows.append(dict(check="2b_perfect_predictions_at_estimated_lambda",
                                 variant=v, estimand=est, population=pop, arm="identity",
                                 statistic="max|theta_pp - theta_full| at the estimated "
                                           "lambda (reported, not a pass/fail identity)",
                                 value=devh, tol=np.nan, passed=True,
                                 detail=f"lambda_hat median "
                                        f"{float(np.median(rh['lambda'])):.6f}, "
                                        f"identity lambda {lam_id:.6f}, "
                                        f"basis={rh['lambda_basis']}"))
                # ---- 3. one spot per donor: cluster variance equals the i.i.d. one ----
                do = load_suff(out, v, PERMUTE_SOURCE, est, pop, block="one")
                if do is not None and int(do["valid"].sum()) >= 3:
                    n_L = min(max(2, NL_SETTINGS[v][0]), int(do["valid"].sum()) - 1)
                    Ld = draw_L(do["valid_donors"], n_L, f"{v}|one|nL{n_L}")
                    Lg = group_mask(do, Ld) & do["valid"]
                    Ug = (~group_mask(do, Ld)) & do["valid"]
                    r = CELL[pop](do["S1"], do["S2"], do["n_per"], do["donor_idx"], Lg,
                                  Ug, est, args.alpha, 5, f"acc3|{v}|{est}|{pop}")
                    for key, nm in (("cl", "classical"), ("pp", "pp")):
                        a, b = r[f"se_iid_{key}"], r[f"se_cluster_{key}"]
                        ok = np.isfinite(a) & np.isfinite(b) & (a > 0)
                        dev = (float(np.max(np.abs(b[ok] - a[ok]) / a[ok]))
                               if ok.any() else np.nan)
                        rows.append(dict(check="3_one_spot_per_donor_cluster_eq_iid",
                                         variant=v, estimand=est, population=pop,
                                         arm=f"{PERMUTE_SOURCE}/{nm}",
                                         statistic="max|se_cluster - se_iid|/se_iid",
                                         value=dev, tol=1e-9,
                                         passed=bool(np.isfinite(dev) and dev <= 1e-9),
                                         detail=f"n_L={n_L}, G={int(do['valid'].sum())}, "
                                                f"one spot per donor, "
                                                f"{int(ok.sum())}/{len(a)} genes "
                                                f"comparable"))
    # ---- 4. the permuted predictor ----
    for v in variants:
        for est in ("theta3", "theta2", "theta1"):
            for pop in ("spot", "donor"):
                d = load_suff(out, v, "permuted", est, pop)
                if d is None:
                    continue
                for n_L in NL_SETTINGS[v]:
                    Ld = draw_L(d["valid_donors"], n_L, f"{v}|nL{n_L}")
                    Lg = group_mask(d, Ld) & d["valid"]
                    Ug = (~group_mask(d, Ld)) & d["valid"]
                    if not Ug.any():
                        continue
                    r = CELL[pop](d["S1"], d["S2"], d["n_per"], d["donor_idx"], Lg, Ug,
                                  est, args.alpha, args.n_boot,
                                  f"acc4|{v}|{est}|{pop}|{n_L}")
                    if r.get("status", "ok") != "ok":
                        continue
                    iv = intervals(r, args.alpha)
                    for vr in ("iid", "cluster", "boot"):
                        lo, hi = iv[f"pp|{vr}|lo"], iv[f"pp|{vr}|hi"]
                        cov = float(np.mean((lo <= r["theta_full"])
                                            & (r["theta_full"] <= hi)))
                        wr = (hi - lo) / (iv[f"classical|{vr}|hi"]
                                          - iv[f"classical|{vr}|lo"])
                        rows.append(dict(
                            check="4_permuted_not_narrower_than_classical", variant=v,
                            estimand=est, population=pop, arm=f"permuted/{vr}",
                            statistic="median width ratio pp/classical over genes "
                                      "(the min over genes is a noise statistic; B2's "
                                      "mean over 200 draws is authoritative)",
                            value=float(np.nanmedian(wr)),
                            tol=1.0 - args.permuted_tol,
                            passed=bool(np.nanmedian(wr) >= 1.0 - args.permuted_tol),
                            detail=f"n_L={n_L}, min over genes "
                                   f"{float(np.nanmin(wr)):.4f}, max lambda_hat "
                                   f"{float(np.max(r['lambda'])):.2e}, basis "
                                   f"{r['lambda_basis']}"))
                        rows.append(dict(
                            check="4b_permuted_coverage_at_this_partition", variant=v,
                            estimand=est, population=pop, arm=f"permuted/{vr}",
                            statistic="fraction of genes whose PPI interval covers "
                                      "theta_full (one partition; B2 is authoritative)",
                            value=cov, tol=np.nan, passed=True,
                            detail=f"n_L={n_L}, nominal {1.0-args.alpha:.2f}"))
    # A check whose statistic could not be formed at all -- theta_1 with one spot per
    # donor, where the labelled outcome has zero variance and the correlation's delta
    # method has no denominator -- is marked not evaluable and excluded from the gate,
    # listed rather than counted as a pass or a failure.
    for r in rows:
        r["evaluable"] = bool(np.isfinite(r["value"]))
        if not r["evaluable"]:
            r["passed"] = False
            r["detail"] = r["detail"] + "; NOT EVALUABLE (statistic not finite)"
    return rows


# =========================================================== figure
def _style():
    import matplotlib as mpl
    mpl.use("Agg")
    mpl.rcParams.update({
        "figure.dpi": 300, "savefig.dpi": 300, "savefig.bbox": "tight",
        "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8,
        "legend.fontsize": 7, "xtick.labelsize": 6, "ytick.labelsize": 6,
        "axes.titlelocation": "left", "axes.titleweight": "normal",
        "axes.spines.top": False, "axes.spines.right": False,
        "xtick.direction": "out", "ytick.direction": "out",
        "legend.frameon": False, "axes.grid": False, "lines.linewidth": 1.2})


VAR_COL = {"iid": "#8C8C8C", "cluster": "#C44E52", "boot": "#4C72B0"}
ARM_SHOWN = "resnet50"      # the arm the two figures draw, named in the caption


def stage_figures(args):
    """fig_b1_intervals.png. Both panel titles are COMPUTED from the tables at render
    time, so a claim-title cannot drift from the numbers it claims."""
    _style()
    import matplotlib.pyplot as plt
    out = f"{ROOT}/{args.out_dir}"
    est = pd.read_csv(f"{out}/b1_estimates.csv")
    t1 = pd.read_csv(f"{out}/b1_theta1_by_slide.csv")

    fig = plt.figure(figsize=(7.2, 3.1))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.0], wspace=0.34)

    # ---- left: theta_1 on IDC, per slide against pooled, by variance ----------
    ax = fig.add_subplot(gs[0, 0])
    sl = t1[(t1["arm"] == ARM_SHOWN) & (t1["level"] == "slide")].sort_values("theta")
    po = t1[(t1["arm"] == ARM_SHOWN) & (t1["level"].str.startswith("pooled"))]
    labs, y = [], 0
    for _, r in sl.iterrows():
        ax.plot([r["iid_lo"], r["iid_hi"]], [y, y], color=VAR_COL["iid"], lw=1.4,
                solid_capstyle="butt", zorder=2)
        ax.plot([r["theta"]], [y], "o", ms=3.4, color=VAR_COL["iid"], zorder=3)
        labs.append(str(r["slide"]))
        y += 1
    y += 0.6
    ratios = []
    for _, r in po.iterrows():
        nm = "spots" if r["level"].endswith("spot") else "donors"
        ax.plot([r["iid_lo"], r["iid_hi"]], [y, y], color=VAR_COL["iid"], lw=2.6,
                solid_capstyle="butt", zorder=3)
        ax.plot([r["cluster_lo"], r["cluster_hi"]], [y, y], color=VAR_COL["cluster"],
                lw=1.2, solid_capstyle="butt", zorder=2)
        ax.plot([r["cluster_lo"], r["cluster_hi"]], [y, y], "|", ms=5,
                color=VAR_COL["cluster"], zorder=2)
        ax.plot([r["theta"]], [y], "s", ms=4.0, color=VAR_COL["cluster"], zorder=4)
        ratios.append((r["cluster_hi"] - r["cluster_lo"])
                      / (r["iid_hi"] - r["iid_lo"]))
        labs.append(f"pooled over {nm}")
        y += 1
    ax.axvline(0.0, color="#BBBBBB", lw=0.8, zorder=0)
    ax.set_yticks(range(len(labs)))
    ax.set_yticklabels(labs)
    ax.set_xlabel("correlation of nuclear area with raw GATA3 count")
    ax.set_title(f"One IDC estimate, two variances: the donor-clustered\n"
                 f"interval is {min(ratios):.0f} to {max(ratios):.0f} times wider")
    ax.margins(y=0.10)
    ax.set_xlim(-1.15, 1.35)
    ax.text(0.99, 0.30, "per slide, spot i.i.d.\n(bar narrower than the marker)",
            transform=ax.transAxes, ha="right", va="top", fontsize=7,
            color=VAR_COL["iid"])
    ax.text(0.99, 0.13, "pooled: thick grey spot i.i.d.,\nthin red donor-clustered",
            transform=ax.transAxes, ha="right", va="top", fontsize=7,
            color=VAR_COL["cluster"])

    # ---- right: theta_3 on CCRCC, interval width by variance estimator -------
    ax2 = fig.add_subplot(gs[0, 1])
    d = est[(est["variant"] == "CCRCC") & (est["estimand"] == "theta3")
            & (est["population"] == "spot") & (est["status"] == "ok")
            & (est["arm"] == ARM_SHOWN)]
    xs = sorted(d["n_L_donors"].unique())
    fac = []
    for vr, nm in (("iid", "spot i.i.d."), ("cluster", "donor cluster-robust"),
                   ("boot", "donor bootstrap")):
        for est_nm, ls in (("classical", "-"), ("pp", "--")):
            ys = [d[d["n_L_donors"] == x][f"{est_nm}_{vr}_width"].median() for x in xs]
            ax2.plot(xs, ys, ls=ls, marker="o" if est_nm == "classical" else "s",
                     ms=3.2, color=VAR_COL[vr], zorder=3)
            if est_nm == "classical":
                ax2.annotate(nm, (xs[-1], ys[-1]), xytext=(4, 0),
                             textcoords="offset points", va="center", fontsize=7,
                             color=VAR_COL[vr])
    for x in xs:
        s_ = d[d["n_L_donors"] == x]
        fac.append(s_["classical_cluster_width"].median()
                   / s_["classical_iid_width"].median())
    ax2.set_xticks(xs)
    ax2.set_xlim(min(xs) - 0.6, max(xs) + 6.2)
    ax2.set_yscale("log")
    ax2.set_xlabel("labelled donors $n_L$ (CCRCC, 24 donors)")
    ax2.set_ylabel("median interval width")
    ax2.set_title(f"CCRCC $\\theta_3$: the spot i.i.d. interval is {min(fac):.0f} to "
                  f"{max(fac):.0f} times\ntoo narrow at every labelled-donor count")
    ax2.text(0.04, 0.52, "circles, solid: classical\nsquares, dashed: PPI",
             transform=ax2.transAxes, fontsize=7, color="#333333")

    p = f"{out}/fig_b1_intervals.png"
    fig.savefig(p)
    figure_provenance(out, "figures", [f"{out}/b1_estimates.csv",
                                       f"{out}/b1_theta1_by_slide.csv"], [p])
    print(f"[write] {os.path.basename(p)}", flush=True)
    return 0


# =========================================================== report numbers
def report_numbers(args):
    """Every pooled number the B1 and B2 report quotes, computed here into one CSV so
    that no number in the prose is retyped from a table by hand."""
    out = f"{ROOT}/{args.out_dir}"
    b2 = f"{ROOT}/{args.b2_dir}"
    rows = []

    def add(key, value, unit, source, note=""):
        rows.append(dict(key=key, value=value, unit=unit, source=source, note=note))

    import glob as _g
    anc = pd.concat([pd.read_csv(f) for f in sorted(_g.glob(f"{out}/b1_h1_anchor__*.csv"))],
                    ignore_index=True)
    add("anchor_cells_total", len(anc), "count", "b1_h1_anchor__<enc>__patient.csv")
    add("anchor_cells_passed", int(anc["passed"].sum()), "count",
        "b1_h1_anchor__<enc>__patient.csv")
    add("anchor_max_abs_diff_vs_a0_h1", float(anc["abs_diff_vs_a0"].max()), "pearson",
        "b1_h1_anchor__<enc>__patient.csv", "tolerance 1e-6")
    add("anchor_max_abs_diff_vs_r1b_intercept_f64", float(anc["abs_diff_vs_r1b"].max()),
        "pearson", "b1_h1_anchor__<enc>__patient.csv")

    acc = pd.read_csv(f"{out}/b1_acceptance.csv")
    for ck, g in acc.groupby("check"):
        ev = g[g["evaluable"]]
        add(f"acceptance_{ck}_evaluable", len(ev), "count", "b1_acceptance.csv")
        add(f"acceptance_{ck}_passed", int(ev["passed"].sum()), "count",
            "b1_acceptance.csv")
        if len(ev):
            add(f"acceptance_{ck}_worst_value", float(ev["value"].max()), "statistic",
                "b1_acceptance.csv")
    add("acceptance_rows_not_evaluable", int((~acc["evaluable"]).sum()), "count",
        "b1_acceptance.csv")

    jn = pd.concat([pd.read_csv(f) for f in sorted(_g.glob(f"{out}/b1_join__*.csv"))],
                   ignore_index=True)
    for t, g in jn.groupby("variant"):
        gg = g[g["encoder"] == g["encoder"].iloc[0]]
        add(f"morphology_join_rate_{t}", float(gg["n_joined"].sum() / gg["n_spots"].sum()),
            "fraction", "b1_join__<enc>.csv")
    gg = jn[jn["encoder"] == "resnet50"]
    gg = gg[gg["variant"] != "CCRCC_merged"]
    add("morphology_join_rate_all_four_tasks",
        float(gg["n_joined"].sum() / gg["n_spots"].sum()), "fraction",
        "b1_join__resnet50.csv", "CCRCC, LYMPH_IDC, PRAD, IDC pooled")

    q = pd.concat([pd.read_csv(f) for f in sorted(_g.glob(f"{out}/b1_pred_quality__*.csv"))],
                  ignore_index=True)
    q = q[q["design"] == "donor"]
    for (v, e_), g in q.groupby(["variant", "encoder"]):
        add(f"donor_design_pearson_mean_over_genes_{v}_{e_}",
            float(g["pearson_pooled"].mean()), "pearson", "b1_pred_quality__<enc>.csv")

    est = pd.read_csv(f"{out}/b1_estimates.csv")
    ok = est[est["status"] == "ok"]
    for (v, p_, n), g in ok[(ok["estimand"] == "theta3")
                            & (ok["arm"] == ARM_SHOWN)].groupby(
            ["variant", "population", "n_L_donors"]):
        add(f"se_ratio_cluster_over_iid_theta3_{v}_{p_}_nL{n}",
            float((g["se_cluster_classical"] / g["se_iid_classical"]).median()),
            "ratio", "b1_estimates.csv", f"median over {len(g)} genes, arm {ARM_SHOWN}")
        add(f"rho_implied_theta3_{v}_{p_}_nL{n}",
            float(g["rho_implied_classical"].median()), "share", "b1_estimates.csv")
        add(f"n_eff_implied_theta3_{v}_{p_}_nL{n}",
            float(g["n_eff_implied_classical"].median()), "donor-equivalents",
            "b1_estimates.csv")
        add(f"m_bar_theta3_{v}_{p_}_nL{n}",
            float(g["m_bar_spots_per_labelled_donor"].median()), "spots per donor",
            "b1_estimates.csv")
    for (v, p_, a_, n), g in ok[ok["estimand"] == "theta3"].groupby(
            ["variant", "population", "arm", "n_L_donors"]):
        add(f"lambda_median_theta3_{v}_{p_}_{a_}_nL{n}", float(g["lam"].median()),
            "lambda", "b1_estimates.csv")
        add(f"width_ratio_cluster_theta3_{v}_{p_}_{a_}_nL{n}",
            float(g["width_ratio_cluster"].median()), "ratio", "b1_estimates.csv")

    t1 = pd.read_csv(f"{out}/b1_theta1_by_slide.csv")
    for _, r in t1[t1["arm"] == ARM_SHOWN].iterrows():
        tag = f"{r['level']}_{r['slide']}"
        add(f"theta1_{tag}", float(r["theta"]), "correlation",
            "b1_theta1_by_slide.csv", f"n_spots {int(r['n_spots'])}, G {int(r['G'])}")
        add(f"theta1_{tag}_iid_width", float(r["iid_hi"] - r["iid_lo"]), "width",
            "b1_theta1_by_slide.csv")
        if np.isfinite(r.get("cluster_hi", np.nan)):
            add(f"theta1_{tag}_cluster_width",
                float(r["cluster_hi"] - r["cluster_lo"]), "width",
                "b1_theta1_by_slide.csv")
    sl = t1[(t1["arm"] == ARM_SHOWN) & (t1["level"] == "slide")]
    add("theta1_n_slides_with_iid_interval_excluding_zero",
        int(((sl["iid_lo"] > 0) | (sl["iid_hi"] < 0)).sum()), "count",
        "b1_theta1_by_slide.csv", f"out of {len(sl)} IDC slides")
    add("theta1_n_slides_positive", int((sl["theta"] > 0).sum()), "count",
        "b1_theta1_by_slide.csv")
    add("theta1_slide_range_min", float(sl["theta"].min()), "correlation",
        "b1_theta1_by_slide.csv")
    add("theta1_slide_range_max", float(sl["theta"].max()), "correlation",
        "b1_theta1_by_slide.csv")

    cov = pd.read_csv(f"{b2}/b2_coverage.csv")
    cov = cov[cov["status"] == "ok"]
    for (st, n, p_, e_, vr), g in cov[cov["estimand"] == "theta3"].groupby(
            ["setting", "n_L", "population", "estimator", "variance"]):
        gg = g[g["arm"] != "permuted"]
        if not len(gg):
            continue
        add(f"b2_coverage_theta3_{st}_nL{n}_{p_}_{e_}_{vr}",
            float(gg["coverage"].mean()), "coverage",
            "b2_coverage.csv", f"mean over {len(gg)} (gene, encoder arm) cells, "
                               f"nominal 0.90")
    for vr in ("iid", "cluster", "boot"):
        g = cov[(cov["variance"] == vr) & (cov["arm"] != "permuted")
                & (cov["estimator"] == "classical")]
        add(f"b2_coverage_{vr}_classical_all_settings_mean", float(g["coverage"].mean()),
            "coverage", "b2_coverage.csv", f"{len(g)} cells over every setting, "
                                           f"estimand, population and gene")
        add(f"b2_cells_{vr}_classical_within_0.02_of_nominal",
            int(((g["coverage"] - 0.90).abs() <= 0.02).sum()), "count",
            "b2_coverage.csv", f"out of {len(g)}")
    wr = pd.read_csv(f"{b2}/b2_width_ratio.csv")
    wr = wr[wr["status"] == "ok"]
    for (st, n, p_), g in wr[wr["estimand"] == "theta3"].groupby(
            ["setting", "n_L", "population"]):
        gv = g.dropna(subset=["width_ratio_cluster", "pearson_gene"])
        if gv["arm"].nunique() >= 3 and len(gv) > 10:
            rho_s = stats.spearmanr(gv["pearson_gene"], gv["width_ratio_cluster"])
            add(f"b2_spearman_widthratio_vs_gene_pearson_theta3_{st}_nL{n}_{p_}",
                float(rho_s.statistic), "spearman rho", "b2_width_ratio.csv",
                f"{len(gv)} (arm, gene) cells, p={rho_s.pvalue:.3g}")
        for a_, ga in g.groupby("arm"):
            add(f"b2_width_ratio_cluster_theta3_{st}_nL{n}_{p_}_{a_}",
                float(ga["width_ratio_cluster"].mean()), "ratio", "b2_width_ratio.csv")
    add("b2_n_settings", int(cov.groupby(["setting", "n_L"]).ngroups), "count",
        "b2_coverage.csv")
    add("b2_n_draws_per_setting", int(cov["n_draws"].max()), "count", "b2_coverage.csv")

    d = pd.DataFrame(rows)
    p = f"{out}/b1b2_report_numbers.csv"
    d.to_csv(p, index=False)
    figure_provenance(out, "report_numbers",
                      [f"{out}/b1_estimates.csv", f"{out}/b1_acceptance.csv",
                       f"{out}/b1_theta1_by_slide.csv", f"{b2}/b2_coverage.csv",
                       f"{b2}/b2_width_ratio.csv"], [p])
    print(f"[write] b1b2_report_numbers.csv ({len(d)} rows)", flush=True)
    return 0


def figure_provenance(out, tag, inputs, outputs):
    """Provenance for the rendering steps, which read committed CSVs and run no model.
    They record the md5 of every input table and of the script, and say where they ran;
    there is no Slurm job id because there is no Slurm job."""
    import platform
    with open(os.path.abspath(__file__), "rb") as f:
        raw = f.read()
    lines = [f"{'='*78}",
             f"Round 3, stage B1 - {tag} (rendering step, no model fit)",
             f"host            : {platform.node() if os.environ.get('SLURM_JOB_ID') else 'session sandbox (not a Slurm job)'}",
             f"slurm_job_id    : {os.environ.get('SLURM_JOB_ID', 'NA - rendered outside Slurm')}",
             f"node            : {os.environ.get('SLURMD_NODENAME', 'NA')}",
             f"gpu             : none",
             f"date            : {time.strftime('%Y-%m-%dT%H:%M:%S%z')}",
             f"script          : code/scripts/round3_b1_ppi.py",
             f"script_md5      : {hashlib.md5(raw).hexdigest()}",
             f"command_line    : {' '.join(sys.argv)}",
             f"pythonhashseed  : {os.environ.get('PYTHONHASHSEED', 'unset')}"]
    for p in inputs:
        if os.path.exists(p):
            with open(p, "rb") as f:
                lines.append(f"input           : {os.path.basename(p)} md5 "
                             f"{hashlib.md5(f.read()).hexdigest()}")
    lines.append("outputs         : " + ", ".join(os.path.basename(p) for p in outputs))
    lines.append("plan            : round3_execution_plan.md sections 4.7, 4.8, 13.6")
    with open(f"{out}/PROVENANCE__{tag}.txt", "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"[write] PROVENANCE__{tag}.txt", flush=True)


# =========================================================== provenance
def provenance(out, tag, cfg, blob, chash, state, wall, ok):
    commit = subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"],
                            capture_output=True, text=True).stdout.strip()
    with open(os.path.abspath(__file__), "rb") as f:
        raw = f.read()
    ssha = hashlib.sha256(raw).hexdigest()[:16]
    smd5 = hashlib.md5(raw).hexdigest()
    with open(os.path.join(_HERE, "round3_a0_harness.py"), "rb") as f:
        hraw = f.read()
    p = f"{out}/PROVENANCE__{tag}.txt"
    with open(p, "w") as f:
        f.write(f"{'='*78}\n"
                f"Round 3, stage B1 - prediction-powered inference, {tag}\n"
                f"slurm_job_id    : {os.environ.get('SLURM_JOB_ID','NA')}\n"
                f"slurm_partition : {os.environ.get('SLURM_JOB_PARTITION','NA')}\n"
                f"node            : {os.environ.get('SLURMD_NODENAME','NA')}\n"
                f"gpu             : {os.environ.get('CUDA_VISIBLE_DEVICES','none')}\n"
                f"date            : {time.strftime('%Y-%m-%dT%H:%M:%S%z')}\n"
                f"repo_commit     : {commit}\n"
                f"script          : code/scripts/round3_b1_ppi.py\n"
                f"script_file     : {os.path.abspath(__file__)}\n"
                f"script_md5      : {smd5}\n"
                f"script_sha256   : sha256/16 {ssha}\n"
                f"harness_md5     : {hashlib.md5(hraw).hexdigest()}  "
                f"(imported unmodified, not edited)\n"
                f"harness_sha256  : sha256/16 {hashlib.sha256(hraw).hexdigest()[:16]}\n"
                f"command_line    : {' '.join(sys.argv)}\n"
                f"pythonhashseed  : {os.environ.get('PYTHONHASHSEED','unset')}\n"
                f"n_spots_by_task : {json.dumps(state.get('n_spots', {}), sort_keys=True)}\n"
                f"embedding_dim   : {json.dumps(state.get('dims', {}), sort_keys=True)}\n"
                f"wall_seconds    : {wall:.0f}\n"
                f"wall_by_task    : {json.dumps(state.get('wall', {}), sort_keys=True)}\n"
                f"acceptance      : {'PASS' if ok else 'FAIL or n/a'}\n"
                f"files_written   : {', '.join(state.get('files', []))}\n"
                f"config_hash     : sha256/16 {chash}\n"
                f"config          : {blob}\n"
                f"plan            : round3_execution_plan.md sections 4.7, 12.5, 13.6\n")
    print(f"[write] PROVENANCE__{tag}.txt (config_hash {chash})", flush=True)


def main(argv=None):
    args = parse_args(argv or sys.argv[1:])
    if args.figures:
        return stage_figures(args)
    if args.report_numbers:
        return report_numbers(args)
    if args.estimate:
        return run_estimate(args)
    return run_predict(args)


if __name__ == "__main__":
    sys.exit(main())
