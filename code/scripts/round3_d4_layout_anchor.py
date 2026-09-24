#!/usr/bin/env python
"""Round 3, stage D4.1: the layout anchor, and the anchor of the anchor.

Stage: D4 step 1 (round3_execution_plan.md section 13.7.1, transcribing
docs/decisions/round3_A3_decisions.md section 7.1). This runs FIRST and is a condition for
reading anything else in D4: section 13.8's decision boundary says any D4 result that would be
read against a benchmark result waits for this anchor and is reported beside it or not at all.

THIS SCRIPT DOES NOT EDIT THE HARNESS. It imports code/scripts/round3_a0_harness.py from its own
directory as a module, exactly as code/scripts/round3_a3_weighted.py does, and reuses load_task,
build_fold_specs, size_match_groups, apply_size_match, fit_base, conformal_quantile,
interval_metrics, _cal_row and _summaries unchanged. The aggregation chain that produces the
comparison numbers is therefore the harness's own `_summaries`, not a re-derivation of it, so an
arm that reproduces A1 reproduces it through the same code that wrote A1.

TWO ARMS, and the difference list between them, written before any result is named.

  bench   the committed benchmark task definition results/round3/task_defs/CCRCC.json:
          bench_data/CCRCC/adata/<sid>.h5ad expression, bench_data/CCRCC/patches/<sid>.h5
          patches, embeddings/CCRCC/<enc>/<sid>.h5 embeddings. This is the ANCHOR OF THE
          ANCHOR: it must reproduce A1's committed CCRCC rows exactly, because it is A1's
          inputs through A1's code.
  hest    results/round3/D4_expansion/task_defs/CCRCC_hest_layout.json: the same 24 samples,
          the same donor grouping (A1's, the benchmark_r2 rows), the same fold membership, the
          same 50 target genes, the same seeds, HEST-1k-layout inputs -- hest_ext/
          kidney_visium_cell/st/<sid>.h5ad expression, hest_ext/kidney_visium_cell/patches/
          <sid>.h5 patches, embeddings_ext/kidney_visium_cell/<enc>/<sid>.h5 embeddings.

  WHAT IS IDENTICAL between the arms: the 24 samples; the donor, patient and slide_out fold
  membership; the 50 target gene symbols and their order; the calibration-unit rule, the seeds,
  the size-match mode and the design list, hence the per-task n_match target is computed the
  same way; the base predictor; alpha; the aggregation chain. D1 established, and section 3 of
  this script's output re-establishes per sample, that the two layouts' EXPRESSION files carry
  the same counts on the barcodes they share.
  WHAT DIFFERS: (1) the pixels. D2 measured that the patch windows are the same region with the
  coordinate axes swapped and offset by half a patch, and that the pixel values differ by a few
  grey levels everywhere, correlation 0.96 to 0.99 per sample, which is a different resampling
  of the same image. (2) THE SPOT SETS DIFFER, not only the pixels: HEST-1k's patching keeps a
  different subset of the expression spots than the benchmark's, so the benchmark arm runs on
  74,220 CCRCC spots and the HEST-layout arm on fewer, per sample from 1,032 of 1,084 (INT1) up
  to all of them (INT13). Every downstream quantity -- the n_match target, the `random` design's
  test draws, which spots land in C, the per-slide means -- therefore differs for two reasons at
  once, and this script's output separates what it can (section 3 reports the spot-set overlap
  per sample) but cannot attribute the coverage or Pearson movement to one of the two.

  Because the spot sets differ, the `random` design's test set is a draw over a different
  population in the two arms even at the same seed; the donor and patient designs hold fold
  MEMBERSHIP fixed and differ only in which spots of those samples exist.

WHAT IS COMPARED (section 13.7.1: per-task Pearson and coverage).
  coverage, width_mean, interval_score  through the harness's own `_summaries`, so the `bench`
      arm's a1_by_fold and a1_by_task rows are directly comparable to
      results/round3/A1_coverage/a1_by_fold__<enc>__main.csv and a1_by_task__<enc>__main.csv.
  pearson_pooled  per gene over all test spots of the fold, mean over genes, mean over
      repeats and calibration draws, then mean over folds. This is the chain A1's H1 anchor
      used against R1b's intercept_f64 column.
  pearson_within_slide  per (test slide, gene) on slides with at least MIN_SLIDE_SPOTS spots,
      mean over slides, mean over genes, then as above. This is the benchmark's own chain, so
      the `patient` design's value is the one comparable to the committed benchmark Pearson in
      results/summary/results_task.csv (head pca_ridge, 6 splits).

DESIGNS. random, patient and donor are all ENUMERATED and all FIT. Section 13.7.1 asks for
random and donor; patient is enumerated regardless because A1's main invocation enumerated it
and size_match_groups() takes its per-task n_match over every design requested, so dropping it
would change n_match and break the anchor. It is also fit, at a cost of six folds, because the
committed benchmark Pearson is a 6-split `patient` number and a Pearson comparison against it
otherwise has no matching design. Score `abs` only: A1's `scaled` rows are unaffected by this
comparison and the sigma head consumes no randomness, so the `abs` rows of a scores=["abs"] run
are identical to the `abs` rows of A1's scores=["abs","scaled"] run.

Outputs under results/round3/D4_expansion/, summaries before parquets:
  d4_layout_anchor.csv            per (encoder, design): Pearson and coverage on both layouts,
                                  the differences, and the A1 and benchmark references
  d4_layout_anchor_by_fold.csv    the same per fold, for the across-fold dispersion the
                                  prediction is stated against
  d4_layout_anchor_a1_check.csv   the anchor of the anchor: max |bench arm - A1 committed| per
                                  (encoder, design, metric), over folds and over the task row
  d4_layout_spot_sets.csv         per sample, the two layouts' spot sets and expression identity
  _agg/a1_by_{slide,fold,task}__<enc>__<arm>.csv  the harness's own summary files, unedited
  PROVENANCE__d4_layout_anchor__<enc>.txt

Usage: round3_d4_layout_anchor.py <encoder> [--arms bench,hest]
"""
import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time

import anndata as ad
import h5py
import numpy as np
import pandas as pd
from scipy.stats import pearsonr

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "round3_a0_harness", os.path.join(_HERE, "round3_a0_harness.py"))
H = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(H)

ROOT = H.ROOT
OUTDIR = "results/round3/D4_expansion"
A1DIR = "results/round3/A1_coverage"
BENCH_TD = f"{ROOT}/results/round3/task_defs/CCRCC.json"
HEST_TD = f"{ROOT}/{OUTDIR}/task_defs/CCRCC_hest_layout.json"
BENCH_PEARSON = f"{ROOT}/results/summary/results_task.csv"
# ---------------------------------------------------------------- the anchor's tolerances
# H0 item 5 (results/round3/H0_determinism/) established that this pipeline is bit-for-bit
# reproducible on ONE node but agrees across nodes only to about 3e-6 absolute in widths, while
# every COUNT is exact. A1's committed CCRCC rows were produced on node b1011 and this job runs
# wherever Slurm puts it, so the anchor demands EXACTNESS of the quantities H0 found exact --
# coverage and the two one-sided miss rates, which are means of integer counts over a fixed spot
# set -- and H0's measured cross-node bound for the width, with the interval score allowed
# 2/alpha = 20 times that because its penalty term multiplies the width by exactly that factor.
# The realised differences are reported whatever the tolerance, so the numbers are readable
# without reference to the threshold. A DIFFERENT NODE IS NOT AN EXCUSE FOR A DIFFERENT SPLIT:
# n_folds and n_train_matched must match exactly, and a fold present in one table and not the
# other fails the check regardless of any tolerance.
W_TOL = 3e-6
TOL = {"coverage": 0.0, "miss_above": 0.0, "miss_below": 0.0,
       "width_mean": W_TOL, "interval_score": 20.0 * W_TOL,
       "coverage_mean": 0.0, "coverage_sd": 0.0, "width_sd": W_TOL,
       "interval_score_mean": 20.0 * W_TOL, "n_folds": 0.0, "n_train_matched": 0.0}
TOL_WHY = {k: ("exact: a mean of integer counts over a fixed spot set, and H0 found every "
               "count exact across nodes" if v == 0.0 else
               ("H0's measured cross-node bound, 3e-6 absolute in widths" if v == W_TOL else
                "20x H0's width bound: the Winkler penalty multiplies the width by 2/alpha"))
           for k, v in TOL.items()}

DESIGNS = ["random", "patient", "donor"]
SCORES = ["abs"]


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def parse_args(argv):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("encoder")
    p.add_argument("--arms", default="bench,hest")
    p.add_argument("--max-folds", type=int, default=None)
    return p.parse_args(argv)


class HArgs:
    """The attribute set the harness's functions read off `args`. Values are A1's."""
    def __init__(self, max_folds=None):
        self.n_repeats = None
        self.h1_anchor = False
        self.n_cal_draws = 3
        self.spot_cal_draws = 1
        self.max_folds = max_folds
        self.size_match = "task"
        self.alpha = 0.10
        self.alpha_store = 0.20
        self.fit_designs = ""
        self.score_moments = False
        self.moments_only = False
        self.slide_gene_anatomy = False
        self.spot_strata = False
        self.a2b_intervention = False
        self.arm_label = "a1"


def spot_sets(bench_td, hest_td, enc):
    """Section 3 of the difference list, measured per sample rather than asserted: the two
    layouts' patch barcode sets, their overlap, and whether the expression they carry for the
    shared barcodes on the 50 target genes is the same number."""
    genes = list(bench_td["target_genes"]["list"])
    rows = []
    for s in sorted(x["sample_id"] for x in bench_td["samples"]):
        def bcs(td):
            p = f"{ROOT}/{td['paths']['embeddings'].format(encoder=enc, sample_id=s)}"
            with h5py.File(p, "r") as f:
                k = "barcodes" if "barcodes" in f else "barcode"
                b = np.asarray(f[k][:]).reshape(-1)
            return [x.decode() if isinstance(x, (bytes, np.bytes_)) else str(x) for x in b]
        bb, hb = bcs(bench_td), bcs(hest_td)
        Ab = ad.read_h5ad(f"{ROOT}/{bench_td['paths']['adata'].format(sample_id=s)}")
        Ah = ad.read_h5ad(f"{ROOT}/{hest_td['paths']['adata'].format(sample_id=s)}")
        shared_expr = [b for b in Ab.obs_names if b in set(Ah.obs_names)]
        Xb = Ab[shared_expr, genes].X
        Xh = Ah[shared_expr, genes].X
        Xb = Xb.toarray() if hasattr(Xb, "toarray") else np.asarray(Xb)
        Xh = Xh.toarray() if hasattr(Xh, "toarray") else np.asarray(Xh)
        rows.append(dict(
            encoder=enc, sample_id=s, n_bench_patch=len(bb), n_hest_patch=len(hb),
            n_patch_shared=len(set(bb) & set(hb)),
            n_bench_only=len(set(bb) - set(hb)), n_hest_only=len(set(hb) - set(bb)),
            n_bench_expr=int(Ab.n_obs), n_hest_expr=int(Ah.n_obs),
            n_expr_shared=len(shared_expr),
            max_abs_count_diff_50genes=float(np.max(np.abs(Xb - Xh))) if len(shared_expr) else np.nan,
            expression_identical=bool(len(shared_expr) and np.array_equal(Xb, Xh))))
        del Ab, Ah
    return pd.DataFrame(rows)


def run_arm(td, enc, arm, args, out_agg):
    """One arm: the harness's own pipeline, with `abs` intervals and per-gene Pearson."""
    t0 = time.time()
    task, label_set = td["task"], td["label_set"]
    meta = dict(donor_of={s["sample_id"]: s["donor_id"] for s in td["samples"]},
                patient_of={s["sample_id"]: s["hest_patient"] for s in td["samples"]},
                resgroup_of={s["sample_id"]: s["resolution_group"] for s in td["samples"]},
                session_of={s["sample_id"]: s["session"] for s in td["samples"]})
    X, Y, samp, bc, xy, genes = H.load_task(td, enc)
    print(f"[load] {arm} {task} {enc}: {X.shape[0]:,} spots x {X.shape[1]} dims, "
          f"{len(genes)} genes, {len(np.unique(samp))} slides, {time.time()-t0:.0f}s", flush=True)

    specs = H.build_fold_specs(td, samp, xy, DESIGNS, meta, args)
    H.size_match_groups(specs, args.size_match)
    nm = sorted({s["n_match"] for s in specs})
    print(f"[specs] {arm}: {len(specs)} cells, n_match {nm}", flush=True)

    pg, cal, pear = [], [], []
    for i, sp in enumerate(specs):
        Tm = H.apply_size_match(sp, task)
        Cm, Em, info = sp["C"], sp["E"], sp["info"]
        if int(Tm.sum()) < H.MIN_T_SPOTS or int(Cm.sum()) < H.MIN_C_SPOTS:
            cal.append(H._cal_row(enc, td, sp, info, Tm, Cm, Em, samp, args))
            print(f"  [skip] {arm} {sp['design']} fold={sp['fold']}: |T|={int(Tm.sum())} "
                  f"|C|={int(Cm.sum())}", flush=True)
            continue
        keys = {nm_: set(zip(samp[m].tolist(), bc[m].tolist()))
                for nm_, m in (("T", Tm), ("C", Cm), ("E", Em))}
        assert not (keys["T"] & keys["C"]) and not (keys["T"] & keys["E"]) \
            and not (keys["C"] & keys["E"]), f"{arm} {sp['design']} {sp['fold']}: not disjoint"

        pipe, A, reg, ridge_alpha = H.fit_base(X[Tm], Y[Tm])
        E_idx = np.flatnonzero(Em)
        B = pipe.transform(X[Em].astype(np.float64, copy=False))
        P_E = reg.predict(B)
        Y_E = Y[Em].astype(np.float64, copy=False)
        A_C = pipe.transform(X[Cm].astype(np.float64, copy=False))
        P_C = reg.predict(A_C)
        Y_C = Y[Cm].astype(np.float64, copy=False)

        S_C = np.abs(Y_C - P_C)
        q_rep, inf_rep = H.conformal_quantile(S_C, args.alpha)
        q_sto, _ = H.conformal_quantile(S_C, args.alpha_store)
        half = q_rep[None, :] * np.ones_like(P_E)
        lo, hi = P_E - half, P_E + half

        base = (task, label_set, enc, sp["design"], sp["fold"], sp["repeat"], sp["cal_draw"])
        for j, g in enumerate(genes):
            r = (float(pearsonr(P_E[:, j], Y_E[:, j])[0])
                 if np.std(Y_E[:, j]) > 0 and np.std(P_E[:, j]) > 0 else np.nan)
            pear.append(base + (g, "pooled_fold", "__fold__", int(Em.sum()), r))
        for s in np.unique(samp[Em]):
            sl = samp[E_idx] == s
            if not sl.any():
                continue
            m = H.interval_metrics(Y_E[sl], lo[sl], hi[sl], args.alpha)
            nsl = int(sl.sum())
            for j, g in enumerate(genes):
                pg.append((task, label_set, enc, sp["design"], sp["fold"], sp["repeat"],
                           sp["cal_draw"], "abs", info["calibration_unit"], s, g, nsl,
                           int(m["n_cov"][j]), float(m["coverage"][j]),
                           float(m["width_mean"][j]), float(m["interval_score"][j]),
                           float(m["miss_above"][j]), float(m["miss_below"][j]),
                           float(q_rep[j]), float(q_sto[j]),
                           bool(nsl >= H.MIN_SLIDE_SPOTS), bool(inf_rep)))
                if nsl >= H.MIN_SLIDE_SPOTS:
                    r = (float(pearsonr(P_E[sl, j], Y_E[sl, j])[0])
                         if np.std(Y_E[sl, j]) > 0 and np.std(P_E[sl, j]) > 0 else np.nan)
                    pear.append(base + (g, "within_slide", s, nsl, r))
        cal.append(H._cal_row(enc, td, sp, info, Tm, Cm, Em, samp, args))
        print(f"  [{i+1}/{len(specs)}] {arm} {sp['design']} fold={sp['fold']} "
              f"rep={sp['repeat']} draw={sp['cal_draw']} unit={info['calibration_unit']} "
              f"n_T={int(Tm.sum())} n_C={int(Cm.sum())} n_E={int(Em.sum())} "
              f"{time.time()-t0:.0f}s", flush=True)

    PG = pd.DataFrame(pg, columns=H.PG_COLS)
    CAL = pd.DataFrame(cal)
    PEAR = pd.DataFrame(pear, columns=["task", "label_set", "encoder", "design", "fold",
                                       "repeat", "cal_draw", "gene", "scope", "slide",
                                       "n_test", "pearson"])
    os.makedirs(out_agg, exist_ok=True)
    suf = f"__{enc}__{arm}"
    CAL.to_csv(f"{out_agg}/a1_calibration_units{suf}.csv", index=False)
    H._summaries(out_agg, suf, PG, CAL, args)
    PEAR.to_csv(f"{out_agg}/d4_pearson_raw{suf}.csv", index=False)
    return PG, CAL, PEAR, time.time() - t0


def pearson_chain(PEAR):
    """Per (design, fold) then per (design) Pearson, both scopes, through the same
    fold-then-task chain `_summaries` uses for coverage."""
    out = {}
    for scope in ("pooled_fold", "within_slide"):
        d = PEAR[PEAR.scope == scope]
        if not len(d):
            continue
        # per (cell, gene): mean over slides (a no-op for pooled_fold, one row per gene)
        g1 = (d.groupby(["design", "fold", "repeat", "cal_draw", "gene"], dropna=False)
              .pearson.mean().reset_index())
        cell = (g1.groupby(["design", "fold", "repeat", "cal_draw"], dropna=False)
                .pearson.mean().reset_index())
        fold = cell.groupby(["design", "fold"], dropna=False).pearson.mean().reset_index()
        task = fold.groupby("design").pearson.agg(["mean", "std", "count"]).reset_index()
        out[scope] = (fold.rename(columns={"pearson": f"pearson_{scope}"}),
                      task.rename(columns={"mean": f"pearson_{scope}_mean",
                                           "std": f"pearson_{scope}_sd",
                                           "count": f"pearson_{scope}_n_folds"}))
    return out


def main(argv=None):
    args_cli = parse_args(argv or sys.argv[1:])
    enc = args_cli.encoder
    arms = [a for a in args_cli.arms.split(",") if a]
    args = HArgs(args_cli.max_folds)
    out = f"{ROOT}/{OUTDIR}"
    out_agg = f"{out}/_agg"
    os.makedirs(out_agg, exist_ok=True)
    t_start = time.time()

    tds = {}
    for arm, p in (("bench", BENCH_TD), ("hest", HEST_TD)):
        td = json.load(open(p))
        assert td["task_def_version"] == 1
        td["_path"] = p
        tds[arm] = td
    # the two arms must differ ONLY in `paths` and in the spot counts
    for key in ("task", "label_set", "st_technology", "flags", "folds", "target_genes"):
        a, b = tds["bench"][key], tds["hest"][key]
        assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True), \
            f"the two layout arms disagree on `{key}`; the anchor is not an anchor"
    assert ([s["sample_id"] for s in tds["bench"]["samples"]]
            == [s["sample_id"] for s in tds["hest"]["samples"]])
    assert ([s["donor_id"] for s in tds["bench"]["samples"]]
            == [s["donor_id"] for s in tds["hest"]["samples"]])
    print("[check] the two arms agree on task, label_set, technology, flags, folds, target "
          "genes, sample order and donor grouping", flush=True)

    config = dict(stage="round3_D4.1", script="code/scripts/round3_d4_layout_anchor.py",
                  encoder=enc, arms=arms, designs=DESIGNS, scores=SCORES,
                  alpha=args.alpha, alpha_store=args.alpha_store,
                  size_match=args.size_match, n_cal_draws=args.n_cal_draws,
                  spot_cal_draws=args.spot_cal_draws, max_folds=args.max_folds,
                  harness_md5=md5(os.path.join(_HERE, "round3_a0_harness.py")),
                  bench_task_def=os.path.relpath(BENCH_TD, ROOT),
                  hest_task_def=os.path.relpath(HEST_TD, ROOT),
                  latent=H.LATENT, alpha_num=H.ALPHA_NUM,
                  cal_unit_frac=H.CAL_UNIT_FRAC, cal_spot_frac=H.CAL_SPOT_FRAC,
                  min_slide_spots=H.MIN_SLIDE_SPOTS, min_T_spots=H.MIN_T_SPOTS,
                  min_C_spots=H.MIN_C_SPOTS, seed_source="zlib.crc32")
    blob = json.dumps(config, sort_keys=True)
    chash = hashlib.sha256(blob.encode()).hexdigest()[:16]
    print(f"[config] sha256/16 {chash}\n{blob}", flush=True)

    # ---------------------------------------------------- spot sets and expression identity
    SS = spot_sets(tds["bench"], tds["hest"], enc)
    SS.to_csv(f"{out}/d4_layout_spot_sets__{enc}.csv", index=False)
    print(f"[write] d4_layout_spot_sets__{enc}.csv\n" + SS.to_string(index=False), flush=True)

    res = {}
    for arm in arms:
        res[arm] = run_arm(tds[arm], enc, arm, args, out_agg)

    # ------------------------------------------------------------------ the comparison table
    A1F = pd.read_csv(f"{ROOT}/{A1DIR}/a1_by_fold__{enc}__main.csv")
    A1T = pd.read_csv(f"{ROOT}/{A1DIR}/a1_by_task__{enc}__main.csv")
    a1f = A1F[(A1F.task == "CCRCC") & (A1F.score == "abs")]
    a1t = A1T[(A1T.task == "CCRCC") & (A1T.score == "abs")]
    bp = pd.read_csv(BENCH_PEARSON)
    # bp["head"], never bp.head: `head` is a DataFrame METHOD, so the attribute form compares a
    # bound method to a string, selects nothing, and leaves the committed benchmark Pearson NaN.
    bp = bp[(bp["head"] == "pca_ridge") & (bp["encoder"] == enc) & (bp["task"] == "CCRCC")]
    bench_pearson = float(bp.pearson_mean.iloc[0]) if len(bp) else np.nan
    bench_pearson_sd = float(bp.pearson_std.iloc[0]) if len(bp) else np.nan

    fold_rows, task_rows, chk_rows = [], [], []
    for arm in arms:
        PG, CAL, PEAR, wall = res[arm]
        byf = pd.read_csv(f"{out_agg}/a1_by_fold__{enc}__{arm}.csv")
        byt = pd.read_csv(f"{out_agg}/a1_by_task__{enc}__{arm}.csv")
        pc = pearson_chain(PEAR)
        for design in sorted(byf.design.unique()):
            f_ = byf[(byf.design == design) & (byf.score == "abs")]
            t_ = byt[(byt.design == design) & (byt.score == "abs")]
            row = dict(encoder=enc, arm=arm, design=design, score="abs",
                       n_folds=int(t_.n_folds.iloc[0]),
                       coverage_mean=float(t_.coverage_mean.iloc[0]),
                       coverage_sd_across_folds=float(t_.coverage_sd.iloc[0]),
                       width_mean=float(t_.width_mean.iloc[0]),
                       interval_score_mean=float(t_.interval_score_mean.iloc[0]),
                       calibration_unit=str(t_.calibration_unit.iloc[0]),
                       n_train_matched=int(t_.n_train_matched.iloc[0]))
            for scope in ("pooled_fold", "within_slide"):
                if scope in pc:
                    tt = pc[scope][1]
                    r = tt[tt.design == design]
                    for c in r.columns:
                        if c != "design":
                            row[c] = float(r[c].iloc[0])
            task_rows.append(row)
            for _, fr in f_.iterrows():
                fold_rows.append(dict(encoder=enc, arm=arm, design=design, fold=str(fr.fold),
                                      coverage=float(fr.coverage),
                                      width_mean=float(fr.width_mean),
                                      interval_score=float(fr.interval_score),
                                      calibration_unit=str(fr.calibration_unit)))
        # ------------ the anchor of the anchor: bench arm against A1's committed rows
        if arm == "bench":
            m = byf[byf.score == "abs"].merge(
                a1f, on=["task", "label_set", "encoder", "design", "score", "fold"],
                suffixes=("_new", "_a1"), how="outer", indicator=True)
            for metric in ("coverage", "width_mean", "interval_score", "miss_above",
                           "miss_below"):
                for design in sorted(m.design.dropna().unique()):
                    mm = m[m.design == design]
                    d = (mm[f"{metric}_new"] - mm[f"{metric}_a1"]).abs()
                    chk_rows.append(dict(
                        check="bench_arm_reproduces_A1_by_fold", encoder=enc, design=design,
                        metric=metric, n_folds_matched=int((mm._merge == "both").sum()),
                        n_folds_new_only=int((mm._merge == "left_only").sum()),
                        n_folds_a1_only=int((mm._merge == "right_only").sum()),
                        max_abs_diff=float(d.max()) if len(d.dropna()) else np.nan,
                        tolerance=TOL[metric], tolerance_source=TOL_WHY[metric],
                        passed=bool(len(d.dropna()) and d.max() <= TOL[metric]
                                    and (mm._merge == "both").all())))
            mt = byt[byt.score == "abs"].merge(
                a1t, on=["task", "label_set", "encoder", "design", "score"],
                suffixes=("_new", "_a1"), how="outer", indicator=True)
            for metric in ("coverage_mean", "coverage_sd", "width_mean", "width_sd",
                           "interval_score_mean", "n_folds", "n_train_matched"):
                d = (mt[f"{metric}_new"] - mt[f"{metric}_a1"]).abs()
                chk_rows.append(dict(check="bench_arm_reproduces_A1_by_task", encoder=enc,
                                     design="all", metric=metric,
                                     n_folds_matched=int((mt._merge == "both").sum()),
                                     n_folds_new_only=int((mt._merge == "left_only").sum()),
                                     n_folds_a1_only=int((mt._merge == "right_only").sum()),
                                     max_abs_diff=float(d.max()) if len(d.dropna()) else np.nan,
                                     tolerance=TOL[metric], tolerance_source=TOL_WHY[metric],
                                     passed=bool(len(d.dropna()) and d.max() <= TOL[metric])))

    T = pd.DataFrame(task_rows)
    F = pd.DataFrame(fold_rows)
    CHK = pd.DataFrame(chk_rows)
    CHK.to_csv(f"{out}/d4_layout_anchor_a1_check__{enc}.csv", index=False)
    print(f"\n[write] d4_layout_anchor_a1_check__{enc}.csv  (THE ANCHOR OF THE ANCHOR)")
    print(CHK.to_string(index=False), flush=True)

    # per-design differences between the arms, with the A1 and benchmark references beside them
    if {"bench", "hest"} <= set(arms):
        b = T[T.arm == "bench"].set_index("design")
        h = T[T.arm == "hest"].set_index("design")
        fb = F[F.arm == "bench"]
        rows = []
        for design in sorted(set(b.index) & set(h.index)):
            a1r = a1t[a1t.design == design]
            disp = float(fb[fb.design == design].coverage.std())
            rows.append(dict(
                encoder=enc, design=design, score="abs",
                coverage_bench_layout=float(b.loc[design, "coverage_mean"]),
                coverage_hest_layout=float(h.loc[design, "coverage_mean"]),
                coverage_diff_hest_minus_bench=float(h.loc[design, "coverage_mean"]
                                                     - b.loc[design, "coverage_mean"]),
                coverage_sd_across_folds_bench=disp,
                coverage_sd_across_folds_hest=float(
                    F[(F.arm == "hest") & (F.design == design)].coverage.std()),
                coverage_move_within_fold_dispersion=bool(
                    abs(h.loc[design, "coverage_mean"] - b.loc[design, "coverage_mean"]) < disp),
                coverage_a1_committed=(float(a1r.coverage_mean.iloc[0]) if len(a1r) else np.nan),
                pearson_pooled_bench_layout=float(b.loc[design, "pearson_pooled_fold_mean"]),
                pearson_pooled_hest_layout=float(h.loc[design, "pearson_pooled_fold_mean"]),
                pearson_pooled_diff=float(h.loc[design, "pearson_pooled_fold_mean"]
                                          - b.loc[design, "pearson_pooled_fold_mean"]),
                pearson_within_slide_bench_layout=float(
                    b.loc[design, "pearson_within_slide_mean"]),
                pearson_within_slide_hest_layout=float(
                    h.loc[design, "pearson_within_slide_mean"]),
                pearson_within_slide_diff=float(h.loc[design, "pearson_within_slide_mean"]
                                                - b.loc[design, "pearson_within_slide_mean"]),
                pearson_move_under_0p01=bool(
                    abs(h.loc[design, "pearson_within_slide_mean"]
                        - b.loc[design, "pearson_within_slide_mean"]) < 0.01),
                benchmark_pearson_committed=bench_pearson,
                benchmark_pearson_sd=bench_pearson_sd,
                benchmark_pearson_source="results/summary/results_task.csv, head pca_ridge, "
                                         "6 splits, the `patient` design",
                width_bench_layout=float(b.loc[design, "width_mean"]),
                width_hest_layout=float(h.loc[design, "width_mean"]),
                n_train_matched_bench=int(b.loc[design, "n_train_matched"]),
                n_train_matched_hest=int(h.loc[design, "n_train_matched"]),
                n_folds=int(b.loc[design, "n_folds"])))
        ANC = pd.DataFrame(rows)
    else:
        ANC = T
    ANC.to_csv(f"{out}/d4_layout_anchor__{enc}.csv", index=False)
    T.to_csv(f"{out}/d4_layout_anchor_arms__{enc}.csv", index=False)
    F.to_csv(f"{out}/d4_layout_anchor_by_fold__{enc}.csv", index=False)
    print(f"\n[write] d4_layout_anchor__{enc}.csv")
    print(ANC.round(5).to_string(index=False), flush=True)

    with open(f"{out}/PROVENANCE__d4_layout_anchor__{enc}.txt", "w") as f:
        f.write(
            "=" * 78 + "\n"
            f"Round 3, stage D4.1 - the layout anchor, encoder {enc}\n"
            f"slurm_job_id    : {os.environ.get('SLURM_JOB_ID', 'NA')}\n"
            f"slurm_partition : {os.environ.get('SLURM_JOB_PARTITION', 'NA')}\n"
            f"node            : {os.environ.get('SLURMD_NODENAME', 'NA')}\n"
            f"gpu             : none (CPU job)\n"
            f"date            : {time.strftime('%Y-%m-%dT%H:%M:%S%z')}\n"
            f"repo_commit     : "
            f"{subprocess.run(['git', '-C', ROOT, 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()}\n"
            f"script          : code/scripts/round3_d4_layout_anchor.py\n"
            f"script_md5      : {md5(os.path.abspath(__file__))}\n"
            f"harness_md5     : {config['harness_md5']}\n"
            f"command_line    : {' '.join(sys.argv)}\n"
            f"pythonhashseed  : {os.environ.get('PYTHONHASHSEED', 'unset')}\n"
            f"config_hash     : sha256/16 {chash}\n"
            f"config          : {blob}\n"
            f"arms            : {arms}\n"
            f"wall_seconds    : {time.time() - t_start:.0f}\n"
            f"wall_by_arm     : "
            f"{json.dumps({a: round(res[a][3], 1) for a in arms})}\n"
            "plan            : round3_execution_plan.md section 13.7.1\n")
    print(f"\n[done] {time.time() - t_start:.0f}s", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
