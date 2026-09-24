#!/usr/bin/env python
"""Round 3, stage D4 steps 2 to 4: the three expansion sets.

Stage: D4 (round3_execution_plan.md sections 13.7.2, 13.7.3 and 13.7.4, transcribing
docs/decisions/round3_A3_decisions.md sections 7.2 to 7.4).

NOTHING IN THIS SCRIPT MAY BE READ AGAINST A BENCHMARK NUMBER except through D4.1's layout
anchor (section 13.8's decision boundary). Every arm runs on HEST-1k-layout embeddings only, on
patched spots only, with donor_audit_r3.csv's `expansion_d3` rows as the grouping source, and
with NCBI563 to NCBI566 excluded from every donor unit.

THIS SCRIPT DOES NOT EDIT THE HARNESS. It imports round3_a0_harness.py and round3_a3_weighted.py
from its own directory as modules and reuses, unchanged: the harness's fit_base, fit_sigma,
build_fold_specs, size_match_groups, apply_size_match, choose_calibration, conformal_quantile,
unit_labels and constants, and A3's weighted_quantile, w3_weights, n_eff, cell_metrics and
fold_summary (so the HCP arm here is A3's W3 code path, not a second implementation of it).
HEST's own gene selection is imported from round2_r2_gene_check.get_k_genes, the reimplementation
round 2's R2 verified against the shipped lists.

THE ONE THING THE HARNESS CANNOT DO for these sets is a fixed target-gene list: section 13.7
requires the 50 genes to be chosen per fold on training samples only, so `load_task` (which takes
the gene list from the task definition) is replaced by `load_set` here, which loads the candidate
panel once and subsets per fold. Everything downstream of Y is the harness's.

ARMS.

  indiana         section 13.7.2. INDIANA_KIDNEY, 26 samples, 25 donor units. Designs:
                  `random` (5 repeats over the 6 grouped folds), `donor` at the 25% rule, and
                  `a4b_k10`, the A4b design of section 13.5.2 read for this set: one held-out
                  donor per fold, 10 of the remaining 24 donor units form C and the other 14
                  train, three calibration draws with crc32 seeds. On `a4b_k10` two intervals
                  are formed per fold and draw: the pooled spot-level quantile (A1's) and HCP
                  with group-equal weights (A3's W3). Score `abs`. Per-gene decomposition in
                  the R7 style.
  population_out  section 13.7.3. KIDNEY_POP54, both directions, calibration at donor level
                  within the training population, training-only gene selection on the
                  intersection panel. The four contradicted papilla samples may train and are
                  test spots, and are excluded from the donor-level calibration pool.
  breast          section 13.7.4. BREAST_XENIUM, 15 donor groups, `donor` at the 25% rule
                  (pool of 14 groups), score `abs`, strata by instrument generation (reported
                  BOTH by sample, 3 against 15, and by donor group, 2 against 13, per section
                  13.10 item 3) and by disease.

GENE SELECTION, and what "on training samples only" is taken to mean, stated before the run.
  donor / a4b_k10 / breast donor  one list per FOLD, chosen on the fold's POOL (every sample
      except the held-out donor unit's), shared by the designs and by all three calibration
      draws. C is carved out of the pool, and calibration data is not test data, so a pool-based
      selection is leakage-free with respect to the fold's test unit; sharing one list across
      `donor` and `a4b_k10` also means the two designs are compared on the same 50 genes, so the
      difference between them is the calibration structure and not the target.
  random  one list per (fold, repeat), chosen on that repeat's TRAINING SPOTS, because under
      `random` every sample contributes test spots and a sample-level selection would see them.
  population_out  one list per direction, chosen on the training population's samples.
  In every case: get_k_genes(criteria='var', k=50, min_cells_pct=0.10) on the selection
  material's PATCHED spots, then genes off the set's intersection panel are dropped as round 2's
  R2 did, and the number dropped is recorded per fold. A fold that ends with fewer than 50 genes
  is reported with its count, never topped up.

STAGES. `--stage genes` writes the per-fold gene lists (encoder-independent, so computed once);
`--stage fit` reads them and runs one encoder. The gene stage is shardable with
`--shard k/n` over the enumerated (design, fold, repeat) selection tasks.

Outputs under results/round3/D4_expansion/, summaries before parquets:
  d4_fold_genes__<TASK>[__shard<k>of<n>].json
  d4_indiana__<enc>.csv / d4_indiana_pergene__<enc>.csv
  d4_population_out__<enc>.csv
  d4_breast__<enc>.csv / d4_breast_strata__<enc>.csv
  d4_<arm>_by_fold__<enc>.csv, d4_<arm>_cells__<enc>.parquet (explicit pa.schema, stays on
  Longleaf), PROVENANCE__d4_<arm>__<enc>.txt

Usage:
  round3_d4_sets.py --arm indiana --stage genes [--shard 1/4]
  round3_d4_sets.py --arm indiana --stage fit --encoder hoptimus0
"""
import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time
import zlib

import anndata as ad
import h5py
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import scanpy as sc
from scipy.stats import pearsonr, spearmanr

_HERE = os.path.dirname(os.path.abspath(__file__))


def _mod(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(_HERE, f"{name}.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


H = _mod("round3_a0_harness")
A3 = _mod("round3_a3_weighted")
GC = _mod("round2_r2_gene_check")

ROOT = H.ROOT
OUTDIR = "results/round3/D4_expansion"
TD_DIR = f"{ROOT}/{OUTDIR}/task_defs"
K_GENES = 50
A4B_K = 10                      # section 13.5.2: fixed, not a session choice
A4B_DRAWS = 3
ALPHA = 0.10
ARMS = {"indiana": "INDIANA_KIDNEY", "population_out": "KIDNEY_POP54", "breast": "BREAST_XENIUM"}
ARM_DESIGNS = {"indiana": ["random", "donor"], "population_out": ["population_out"],
               "breast": ["random", "donor"]}


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


class HArgs:
    """The attribute set the harness's functions read off `args`; values are A1's."""
    def __init__(self, n_repeats=None, max_folds=None):
        self.n_repeats = n_repeats
        self.h1_anchor = False
        self.n_cal_draws = 3
        self.spot_cal_draws = 1
        self.max_folds = max_folds
        self.size_match = "task"
        self.alpha = ALPHA
        self.alpha_store = 0.20
        self.fit_designs = ""
        self.score_moments = False
        self.moments_only = False
        self.slide_gene_anatomy = False
        self.spot_strata = False
        self.a2b_intervention = False
        self.arm_label = "d4"


# ------------------------------------------------------------------------------ loading
def patched_barcodes(td, sid, enc):
    """The spot set every expansion arm runs on: the embedding file's barcode list, which is
    HEST-1k's patch barcode list (section 13.2 item 3, the subset relation). Read from the
    embedding file rather than the patch file so the spots are exactly the rows of X."""
    p = f"{ROOT}/{td['paths']['embeddings'].format(encoder=enc, sample_id=sid)}"
    with h5py.File(p, "r") as f:
        k = "barcodes" if "barcodes" in f else "barcode"
        b = np.asarray(f[k][:]).reshape(-1)
        bc = [x.decode() if isinstance(x, (bytes, np.bytes_)) else str(x) for x in b]
        X = np.asarray(f["embeddings"][:], dtype=np.float32)
        xy = np.asarray(f["coords"][:], dtype=np.float64)
    return bc, X, xy


def raw_patched_adata(td, sid, keep_bc):
    """The sample's RAW (un-logged) AnnData restricted to `keep_bc`, in that order. This is the
    material get_k_genes selects on, so the selection sees patched spots only."""
    A = ad.read_h5ad(f"{ROOT}/{td['paths']['adata'].format(sample_id=sid)}")
    sub = A[keep_bc].copy()
    assert sub.n_obs == len(keep_bc), (
        f"{sid}: selecting {len(keep_bc)} barcodes returned {sub.n_obs} rows; the expression "
        f"file's barcode index is not unique")
    return sub


def load_set(td, enc, genes_union):
    """X (patched spots x dims), Yraw (patched spots x |genes_union|, RAW counts), samp, bc, xy.

    Only `genes_union` is held in memory, which is why the fit stage can run on a candidate
    panel of 17,765 genes without materialising it.
    """
    ids = sorted(s["sample_id"] for s in td["samples"])
    Xs, Ys, samp, bcs, xys = [], [], [], [], []
    for sid in ids:
        bc, X, xy = patched_barcodes(td, sid, enc)
        A = ad.read_h5ad(f"{ROOT}/{td['paths']['adata'].format(sample_id=sid)}")
        assert set(bc) <= set(map(str, A.obs_names)), f"{sid}: patch barcode not in expression"
        sub = A[bc, genes_union]
        # A duplicated obs index would make A[bc] return one row per MATCH, silently
        # misaligning Y against X. anndata only warns, so the row count is asserted.
        assert sub.n_obs == len(bc), (
            f"{sid}: selecting {len(bc)} patch barcodes returned {sub.n_obs} expression rows; "
            f"the expression file's barcode index is not unique")
        Yr = sub.X.toarray() if hasattr(sub.X, "toarray") else np.asarray(sub.X)
        Xs.append(X)
        Ys.append(np.asarray(Yr, dtype=np.float32))
        samp += [sid] * len(bc)
        bcs += bc
        xys.append(xy)
        del A, sub
    return (np.vstack(Xs), np.vstack(Ys), np.array(samp), np.array(bcs, dtype=object),
            np.vstack(xys))


def log1p_cols(Yraw, cols):
    """log1p of the raw counts for the given column indices, float64, which is what
    load_task's sc.pp.log1p(A) then A[:, genes] produces."""
    return np.log1p(Yraw[:, cols].astype(np.float64))


# ---------------------------------------------------------------- fold enumeration helpers
def meta_of(td):
    return dict(donor_of={s["sample_id"]: s["donor_id"] for s in td["samples"]},
                patient_of={s["sample_id"]: s["hest_patient"] for s in td["samples"]},
                resgroup_of={s["sample_id"]: s["resolution_group"] for s in td["samples"]},
                session_of={s["sample_id"]: s["session"] for s in td["samples"]})


def selection_tasks(td, arm, args):
    """Every (design, fold, repeat) whose target genes must be chosen, with the SAMPLES or the
    spot predicate the selection may see. Enumerated before any selection runs so the gene
    stage can be sharded and so a missing list is an error rather than a silent fallback."""
    ids = sorted(s["sample_id"] for s in td["samples"])
    out = []
    if arm == "population_out":
        for fd in td["folds"]["population_out"]:
            out.append(dict(design="population_out", fold=str(fd["fold"]), repeat=-1,
                            samples=sorted(fd["train"]), spot_predicate="all_spots_of_samples"))
        return out
    for fd in td["folds"]["donor"]:
        out.append(dict(design="pool", fold=str(fd["fold"]), repeat=-1,
                        samples=sorted(fd["train"]), spot_predicate="all_spots_of_samples"))
    n_rep = args.n_repeats if args.n_repeats is not None else td["folds"]["random"]["n_repeats"]
    for fd in td["folds"]["patient"]:
        for rep in range(n_rep):
            out.append(dict(design="random", fold=str(fd["fold"]), repeat=rep, samples=ids,
                            spot_predicate="random_training_spots"))
    return out


def random_masks(td, samp, args):
    """The `random` design's test masks, reproduced from build_fold_specs' own seed recipe so
    the gene stage (which has no embeddings) and the fit stage agree spot for spot."""
    task = td["task"]
    n = len(samp)
    of_sample = {s: (samp == s) for s in np.unique(samp)}
    n_rep = args.n_repeats if args.n_repeats is not None else td["folds"]["random"]["n_repeats"]
    out = {}
    for fd in td["folds"]["patient"]:
        m = np.zeros(n, bool)
        for s in fd["test"]:
            m |= of_sample[s]
        sz = int(m.sum())
        for rep in range(n_rep):
            rng = np.random.default_rng(
                zlib.crc32(f"{task}|random|{fd['fold']}|rep{rep}".encode()))
            E = np.zeros(n, bool)
            E[rng.choice(n, size=sz, replace=False)] = True
            out[(str(fd["fold"]), rep)] = E
    return out


# ---------------------------------------------------------------------------- gene stage
def run_genes(td, arm, args, shard, out):
    task = td["task"]
    panel = set(td["target_genes"]["list"])
    tasks = selection_tasks(td, arm, args)
    k, nsh = shard
    mine = [t for i, t in enumerate(tasks) if i % nsh == (k - 1)]
    print(f"[genes] {task}: {len(tasks)} selection tasks, shard {k}/{nsh} takes {len(mine)}",
          flush=True)

    ids = sorted(s["sample_id"] for s in td["samples"])
    # the patched-spot barcode list per sample, taken from ONE encoder's embedding files: the
    # three encoders' barcode lists are the same patch list, asserted here rather than assumed
    bc_of = {}
    for sid in ids:
        lists = []
        for enc in ("hoptimus0", "uni_v2", "resnet50"):
            b, _, _ = patched_barcodes(td, sid, enc)
            lists.append(b)
        assert lists[0] == lists[1] == lists[2], f"{sid}: encoders disagree on the patch list"
        bc_of[sid] = lists[0]
    samp = np.array([sid for sid in ids for _ in bc_of[sid]])
    bcs = np.array([b for sid in ids for b in bc_of[sid]], dtype=object)
    rmask = random_masks(td, samp, args) if arm != "population_out" else {}

    res = {}
    for t in mine:
        t0 = time.time()
        if t["spot_predicate"] == "all_spots_of_samples":
            ads = [raw_patched_adata(td, sid, bc_of[sid]) for sid in t["samples"]]
            n_sel_spots = sum(a.n_obs for a in ads)
        else:
            E = rmask[(t["fold"], t["repeat"])]
            ads = []
            n_sel_spots = 0
            for sid in t["samples"]:
                keep = [b for b, s, e in zip(bcs, samp, E) if s == sid and not e]
                if not keep:
                    continue
                ads.append(raw_patched_adata(td, sid, keep))
                n_sel_spots += len(keep)
        raw, n_common = GC.get_k_genes(ads, k=K_GENES)
        dropped = [g for g in raw if g not in panel]
        genes = [g for g in raw if g in panel]
        assert genes, f"{task} {t['design']} {t['fold']}: every selected gene is off panel"
        res[f"{t['design']}|{t['fold']}|{t['repeat']}"] = dict(
            design=t["design"], fold=t["fold"], repeat=t["repeat"], genes=genes,
            n_genes=len(genes), n_selected=len(raw), n_off_panel=len(dropped),
            genes_off_panel=dropped, n_common_genes=int(n_common),
            n_selection_samples=len(ads), n_selection_spots=int(n_sel_spots),
            selection_material=t["spot_predicate"], seconds=round(time.time() - t0, 1))
        del ads
        print(f"  [{t['design']} {t['fold']} rep{t['repeat']}] {len(genes)}/50 genes kept, "
              f"{len(dropped)} off panel, common {n_common}, {n_sel_spots:,} spots, "
              f"{time.time()-t0:.0f}s", flush=True)
    tag = "" if nsh == 1 else f"__shard{k}of{nsh}"
    p = f"{out}/d4_fold_genes__{task}{tag}.json"
    json.dump(dict(task=task, arm=arm, k=K_GENES, min_cells_pct=GC.MIN_CELLS_PCT,
                   candidate_panel_n=len(panel), n_selection_tasks=len(tasks),
                   shard=[k, nsh], scanpy=sc.__version__,
                   script_md5=md5(os.path.abspath(__file__)),
                   selections=res), open(p, "w"), indent=1)
    print(f"[write] {p} ({len(res)} selections)", flush=True)
    return p


def read_genes(task, out):
    """Merge every shard, and fail loudly on a missing or duplicated selection."""
    import glob
    sel, meta = {}, []
    for p in sorted(glob.glob(f"{out}/d4_fold_genes__{task}*.json")):
        d = json.load(open(p))
        for k, v in d["selections"].items():
            assert k not in sel, f"selection {k} appears in two shards"
            sel[k] = v
        meta.append(dict(path=os.path.basename(p), shard=d["shard"],
                         n=len(d["selections"]), n_tasks=d["n_selection_tasks"]))
    assert sel, f"no gene-list file for {task}; run --stage genes first"
    want = meta[0]["n_tasks"]
    assert len(sel) == want, f"{task}: {len(sel)} selections, expected {want}"
    return sel, meta


# ----------------------------------------------------------------------- the A4b design
def a4b_specs(td, samp, meta, args):
    """Section 13.5.2 read for this set: one held-out donor unit per fold; from the remaining
    pool, A4B_K donor units form C and the rest train; A4B_DRAWS calibration draws with crc32
    seeds. Units come from the task definition's donor_id, and a sample flagged
    `excluded_from_donor_units` cannot be a calibration unit."""
    task = td["task"]
    n = len(samp)
    donor_of = meta["donor_of"]
    barred = {s["sample_id"] for s in td["samples"] if s.get("excluded_from_donor_units")}
    out = []
    for fd in td["folds"]["donor"]:
        E = np.isin(samp, fd["test"])
        pool = np.isin(samp, fd["train"])
        if not E.any() or not pool.any():
            continue
        units = sorted({donor_of[s] for s in fd["train"] if s not in barred})
        if len(units) <= A4B_K:
            print(f"  [skip] a4b fold={fd['fold']}: only {len(units)} eligible units",
                  flush=True)
            continue
        for draw in range(A4B_DRAWS):
            rng = np.random.default_rng(
                zlib.crc32(f"{task}|a4b_k10|{fd['fold']}|cal{draw}".encode()))
            pick = set(rng.permutation(np.array(units, dtype=object))[:A4B_K].tolist())
            cal_samples = [s for s in fd["train"]
                           if s not in barred and donor_of[s] in pick]
            C = np.isin(samp, cal_samples)
            T = pool & ~C
            info = dict(calibration_unit="donor", n_cal_units=len(pick),
                        n_units_in_pool=len(units), n_cal_spots=int(C.sum()),
                        n_pool_spots=int(pool.sum()), cal_status="ok",
                        n_blocks_total=None, n_train_buffer_dropped=0,
                        **H.sharing_flags(C, E, samp, meta))
            out.append(dict(task=task, design="a4b_k10", fold=str(fd["fold"]), repeat=-1,
                            cal_draw=draw, T=T, C=C, E=E, pool=pool, info=info))
    return out


def population_out_specs(td, samp, xy, meta, args):
    """Section 13.7.3: both directions, with calibration at DONOR level inside the training
    population and the four contradicted papilla samples barred from the calibration pool
    (section 13.10 item 5) while remaining eligible to train and remaining test spots."""
    task = td["task"]
    barred = {s["sample_id"] for s in td["samples"] if s.get("excluded_from_donor_units")}
    out = []
    for fd in td["folds"]["population_out"]:
        E = np.isin(samp, fd["test"])
        pool = np.isin(samp, fd["train"])
        cal_pool = np.isin(samp, [s for s in fd["train"] if s not in barred])
        assert E.any() and pool.any()
        for draw in range(args.n_cal_draws):
            key = f"{task}|population_out|{fd['fold']}"
            _, C, info = H.choose_calibration("donor", cal_pool, E, samp, xy, meta,
                                              key, draw, H.CAL_UNIT_FRAC, H.CAL_SPOT_FRAC)
            T = pool & ~C
            info = dict(info)
            info["n_pool_spots"] = int(pool.sum())
            info["n_cal_pool_spots"] = int(cal_pool.sum())
            info["n_barred_train_spots"] = int((pool & ~cal_pool).sum())
            out.append(dict(task=task, design="population_out", fold=str(fd["fold"]),
                            repeat=-1, cal_draw=draw, T=T, C=C, E=E, pool=pool, info=info))
    return out


# ------------------------------------------------------------------------------ fit stage
def genes_for(sel, design, fold, repeat):
    key = ("random" if design == "random" else
           "population_out" if design == "population_out" else "pool")
    rep = repeat if key == "random" else -1
    k = f"{key}|{fold}|{rep}"
    assert k in sel, f"no gene list for {k}"
    return sel[k]


def run_fit(td, arm, enc, args, sel, out):
    t0 = time.time()
    task = td["task"]
    meta = meta_of(td)
    panel = list(td["target_genes"]["list"])
    union = sorted({g for v in sel.values() for g in v["genes"]})
    col_of = {g: i for i, g in enumerate(union)}
    print(f"[genes] {task}: {len(union)} distinct genes over {len(sel)} per-fold lists",
          flush=True)

    X, Yraw, samp, bc, xy = load_set(td, enc, union)
    print(f"[load] {arm} {task} {enc}: {X.shape[0]:,} patched spots x {X.shape[1]} dims, "
          f"{len(np.unique(samp))} slides, {time.time()-t0:.0f}s", flush=True)

    if arm == "population_out":
        # The two directions are size-matched to each other, which is section 4.2's rule
        # ("subsampling to the smallest") applied within this task: the Cordeliers-trained
        # direction has about twice the training spots of the Indiana-trained one, and an
        # unmatched comparison would confound the shift with the training size. Both the
        # natural and the matched sizes are recorded per fold.
        specs = population_out_specs(td, samp, xy, meta, args)
        H.size_match_groups(specs, args.size_match)
    else:
        specs = H.build_fold_specs(td, samp, xy, ARM_DESIGNS[arm], meta, args)
        H.size_match_groups(specs, args.size_match)
        nmatch = specs[0]["n_match"] if specs else None
        extra = a4b_specs(td, samp, meta, args) if arm == "indiana" else []
        for s in extra:
            # A4b is not size-matched UP: apply_size_match only ever subsamples, so giving it
            # the task's n_match leaves its natural |T| alone when that is smaller, which is
            # section 13.5.2's "record the training-set size beside A1's".
            s["n_match"] = nmatch
        specs = specs + extra
    print(f"[specs] {arm}: {len(specs)} cells; designs "
          f"{sorted({s['design'] for s in specs})}", flush=True)

    cells_rows, fold_rows, pear_rows, cal_rows = [], [], [], []
    for i, sp in enumerate(specs):
        Tm = H.apply_size_match(sp, task)
        Cm, Em, info = sp["C"], sp["E"], sp["info"]
        gsel = genes_for(sel, sp["design"], sp["fold"], sp["repeat"])
        genes = gsel["genes"]
        cols = [col_of[g] for g in genes]
        cal_rows.append(dict(H._cal_row(enc, td, sp, info, Tm, Cm, Em, samp, args),
                             arm=arm, n_genes=len(genes),
                             n_off_panel=gsel["n_off_panel"]))
        if int(Tm.sum()) < H.MIN_T_SPOTS or int(Cm.sum()) < H.MIN_C_SPOTS:
            print(f"  [skip] {sp['design']} fold={sp['fold']} draw={sp['cal_draw']}: "
                  f"|T|={int(Tm.sum())} |C|={int(Cm.sum())}", flush=True)
            continue
        Y = log1p_cols(Yraw, cols)
        pipe, A, reg, ridge_alpha = H.fit_base(X[Tm], Y[Tm])
        B = pipe.transform(X[Em].astype(np.float64, copy=False))
        P_E, Y_E = reg.predict(B), Y[Em]
        A_C = pipe.transform(X[Cm].astype(np.float64, copy=False))
        P_C, Y_C = reg.predict(A_C), Y[Cm]
        S_C = np.abs(Y_C - P_C)
        samp_E = samp[Em]

        methods = [("pooled_quantile", None)]
        if sp["design"] == "a4b_k10":
            methods.append(("hcp_w3", "w3"))
        for mname, kind in methods:
            if kind is None:
                q, inf_flag = H.conformal_quantile(S_C, args.alpha)
                lo, hi = P_E - q[None, :], P_E + q[None, :]
                n_inf_pts, K, neff = (int(inf_flag) * int(Em.sum()), np.nan, float(len(S_C)))
                if inf_flag:
                    lo = np.full_like(lo, -np.inf)
                    hi = np.full_like(hi, np.inf)
            else:
                ul = H.unit_labels(info["calibration_unit"], Cm, sp["pool"], samp, xy, meta)
                w_C, w_E, K = A3.w3_weights(ul[Cm], int(Em.sum()))
                qw, infinite = A3.weighted_quantile(S_C, w_C, w_E, args.alpha)
                lo, hi = P_E - qw, P_E + qw
                n_inf_pts, neff = int(infinite.sum()), A3.n_eff(w_C)
            cells, wmean, wmed, n_inf_cells, n_cells_tot = A3.cell_metrics(
                Y_E, lo, hi, args.alpha, samp_E, genes, H.MIN_SLIDE_SPOTS)
            fs = A3.fold_summary(cells)
            fold_rows.append(dict(
                arm=arm, task=task, encoder=enc, design=sp["design"], method=mname,
                fold=str(sp["fold"]), repeat=sp["repeat"], cal_draw=sp["cal_draw"],
                calibration_unit=str(info["calibration_unit"]),
                n_T=int(Tm.sum()), n_C=int(Cm.sum()), n_E=int(Em.sum()),
                n_cal_units=info.get("n_cal_units"), n_units_in_pool=info.get("n_units_in_pool"),
                K=(int(K) if np.isfinite(K) else None), n_eff=neff,
                n_genes=len(genes), n_off_panel=gsel["n_off_panel"],
                width_mean_spotgene=wmean, width_median_spotgene=wmed,
                n_infinite_spotgene=n_inf_cells, n_spotgene=n_cells_tot,
                finite=bool(n_inf_cells == 0), n_infinite_test_points=n_inf_pts,
                cal_shares_donor_with_test=info.get("cal_shares_donor_with_test"),
                n_train_natural=sp.get("n_train_natural"),
                n_train_matched=sp.get("n_train_matched"), **fs))
            for _, r in cells.iterrows():
                cells_rows.append((arm, task, enc, sp["design"], mname, str(sp["fold"]),
                                   int(sp["repeat"]), int(sp["cal_draw"]), str(r.slide),
                                   str(r.gene), int(r.n_test), int(r.n_covered),
                                   float(r.coverage), float(r.width_mean),
                                   float(r.width_median), float(r.interval_score),
                                   float(r.miss_above), float(r.miss_below),
                                   int(r.n_infinite), bool(r.slide_ge_min_spots)))
        # per-gene Pearson, for the R7-style decomposition; encoder-specific, method-free
        for j, g in enumerate(genes):
            r_pool = (float(pearsonr(P_E[:, j], Y_E[:, j])[0])
                      if np.std(Y_E[:, j]) > 0 and np.std(P_E[:, j]) > 0 else np.nan)
            pear_rows.append(dict(arm=arm, task=task, encoder=enc, design=sp["design"],
                                  fold=str(sp["fold"]), repeat=sp["repeat"],
                                  cal_draw=sp["cal_draw"], gene=g, pearson_pooled=r_pool))
        print(f"  [{i+1}/{len(specs)}] {sp['design']} fold={sp['fold']} rep={sp['repeat']} "
              f"draw={sp['cal_draw']} unit={info['calibration_unit']} n_T={int(Tm.sum())} "
              f"n_C={int(Cm.sum())} n_E={int(Em.sum())} genes={len(genes)} "
              f"{time.time()-t0:.0f}s", flush=True)

    FOLD = pd.DataFrame(fold_rows)
    CAL = pd.DataFrame(cal_rows)
    PEAR = pd.DataFrame(pear_rows)
    CELLS = pd.DataFrame(cells_rows, columns=CELL_COLS)
    return FOLD, CAL, PEAR, CELLS, samp, Yraw, union, col_of, time.time() - t0


CELL_COLS = ["arm", "task", "encoder", "design", "method", "fold", "repeat", "cal_draw",
             "slide", "gene", "n_test", "n_covered", "coverage", "width_mean", "width_median",
             "interval_score", "miss_above", "miss_below", "n_infinite", "slide_ge_min_spots"]
CELL_SCHEMA = pa.schema([
    ("arm", pa.string()), ("task", pa.string()), ("encoder", pa.string()),
    ("design", pa.string()), ("method", pa.string()), ("fold", pa.string()),
    ("repeat", pa.int32()), ("cal_draw", pa.int32()), ("slide", pa.string()),
    ("gene", pa.string()), ("n_test", pa.int32()), ("n_covered", pa.int32()),
    ("coverage", pa.float32()), ("width_mean", pa.float32()), ("width_median", pa.float32()),
    ("interval_score", pa.float32()), ("miss_above", pa.float32()),
    ("miss_below", pa.float32()), ("n_infinite", pa.int32()),
    ("slide_ge_min_spots", pa.bool_())])


def by_design(FOLD):
    """Mean over repeats and calibration draws inside a fold, then over folds, which is
    a1_by_task's chain."""
    g = ["arm", "task", "encoder", "design", "method", "fold"]
    per_fold = FOLD.groupby(g, dropna=False)[
        ["coverage", "width_mean", "width_median_of_cells", "interval_score", "miss_above",
         "miss_below", "width_mean_spotgene", "width_median_spotgene", "n_T", "n_C",
         "n_eff"]].mean().reset_index()
    out = (per_fold.groupby(["arm", "task", "encoder", "design", "method"], dropna=False)
           .agg(n_folds=("fold", "nunique"),
                coverage_mean=("coverage", "mean"), coverage_sd=("coverage", "std"),
                coverage_min=("coverage", "min"), coverage_max=("coverage", "max"),
                width_mean=("width_mean", "mean"),
                width_median=("width_median_spotgene", "mean"),
                interval_score_mean=("interval_score", "mean"),
                miss_above_mean=("miss_above", "mean"),
                miss_below_mean=("miss_below", "mean"),
                n_T_mean=("n_T", "mean"), n_C_mean=("n_C", "mean"),
                n_eff_mean=("n_eff", "mean")).reset_index())
    fin = (FOLD.groupby(["arm", "task", "encoder", "design", "method"], dropna=False)
           .agg(n_cells=("fold", "size"), n_cells_finite=("finite", "sum"),
                n_infinite_spotgene=("n_infinite_spotgene", "sum"),
                n_spotgene=("n_spotgene", "sum")).reset_index())
    return out.merge(fin, on=["arm", "task", "encoder", "design", "method"], how="left"), per_fold


# --------------------------------------------------------- R6-style variance components
def nested_components(y, donor, slide):
    """Unbalanced two-level nested random-effects ANOVA, Henderson method of moments.

    Copied verbatim from code/scripts/round2_r6_donor_variance.py::nested_components so the
    between-donor share on this set is the same estimator round 2 reported for the benchmark
    tasks. That script is not importable as a module (it runs at import), hence the copy.
    """
    df = pd.DataFrame({"y": y, "d": donor, "s": slide})
    N = len(df)
    n_ds = df.groupby(["d", "s"]).y.agg(["count", "mean"])
    n_d = df.groupby("d").y.agg(["count", "mean"])
    D, S = len(n_d), len(n_ds)
    grand = df.y.mean()
    ss_spot = float(((df.y - df.set_index(["d", "s"]).index.map(n_ds["mean"])) ** 2).sum())
    ss_slide = float((n_ds["count"] * (n_ds["mean"]
                      - n_ds.index.get_level_values("d").map(n_d["mean"])) ** 2).sum())
    ss_donor = float((n_d["count"] * (n_d["mean"] - grand) ** 2).sum())
    df_spot, df_slide, df_donor = N - S, S - D, D - 1
    out = dict(n_spots=N, n_slides=S, n_donors=D, df_spot=df_spot, df_slide=df_slide,
               df_donor=df_donor)
    if df_spot <= 0:
        return None
    ms_spot = ss_spot / df_spot
    out["var_spot"] = ms_spot
    sq_over_nd = float(sum((n_ds.loc[d, "count"] ** 2).sum() / n_d.loc[d, "count"]
                           for d in n_d.index))
    sq_over_N = float((n_ds["count"] ** 2).sum() / N)
    nd_sq_over_N = float((n_d["count"] ** 2).sum() / N)
    if df_slide > 0:
        c1 = (N - sq_over_nd) / df_slide
        v_slide = (ss_slide / df_slide - ms_spot) / c1
        out.update(var_slide_raw=v_slide, var_slide=max(0.0, v_slide), c1=c1)
    else:
        out.update(var_slide_raw=np.nan, var_slide=np.nan, c1=np.nan)
    if df_donor > 0:
        c2 = (sq_over_nd - sq_over_N) / df_donor
        c3 = (N - nd_sq_over_N) / df_donor
        vs = out["var_slide"] if np.isfinite(out["var_slide"]) else 0.0
        v_donor = (ss_donor / df_donor - ms_spot - c2 * vs) / c3
        out.update(var_donor_raw=v_donor, var_donor=max(0.0, v_donor), c2=c2, c3=c3)
    else:
        out.update(var_donor_raw=np.nan, var_donor=np.nan, c2=np.nan, c3=np.nan)
    return out


def pergene_decomposition(td, PEAR, CELLS, samp, Yraw, col_of, meta, enc, arm, task):
    """The R7-style per-gene table: the split penalty per gene beside the between-donor
    variance share of that gene's expression, and the Spearman correlations between them."""
    p = (PEAR.groupby(["design", "gene"]).pearson_pooled.mean().unstack("design"))
    T = pd.DataFrame(index=p.index)
    for d in p.columns:
        T[f"pearson_{d}"] = p[d]
    if "random" in p and "donor" in p:
        T["random_minus_donor"] = p["random"] - p["donor"]
    if "random" in p and "a4b_k10" in p:
        T["random_minus_a4b_k10"] = p["random"] - p["a4b_k10"]
    cov = (CELLS[CELLS.slide_ge_min_spots]
           .groupby(["design", "method", "gene"]).coverage.mean().unstack(["design", "method"]))
    cov.columns = [f"coverage_{a}_{b}" for a, b in cov.columns]
    T = T.join(cov)

    barred = {s["sample_id"] for s in td["samples"] if s.get("excluded_from_donor_units")}
    keep = ~np.isin(samp, sorted(barred))
    donor = np.array([meta["donor_of"][s] for s in samp])
    rows = []
    for g in T.index:
        y = np.log1p(Yraw[keep, col_of[g]].astype(np.float64))
        c = nested_components(y, donor[keep], samp[keep])
        if c is None:
            continue
        tot = c["var_spot"] + (c["var_slide"] if np.isfinite(c["var_slide"]) else 0.0) \
            + (c["var_donor"] if np.isfinite(c["var_donor"]) else 0.0)
        rows.append(dict(gene=g, var_spot=c["var_spot"], var_slide=c["var_slide"],
                         var_donor=c["var_donor"],
                         frac_donor=(c["var_donor"] / tot if tot > 0 else np.nan),
                         frac_slide=(c["var_slide"] / tot if tot > 0 else np.nan),
                         n_donors=c["n_donors"], n_slides=c["n_slides"],
                         df_donor=c["df_donor"], df_slide=c["df_slide"]))
    V = pd.DataFrame(rows).set_index("gene")
    T = T.join(V).reset_index()
    T.insert(0, "encoder", enc)
    T.insert(0, "task", task)
    T.insert(0, "arm", arm)
    T["donor_units_excluded"] = ";".join(sorted(barred))

    pairs = [("random_minus_donor", "frac_donor"), ("random_minus_donor", "var_donor"),
             ("random_minus_a4b_k10", "frac_donor"),
             ("coverage_donor_pooled_quantile", "frac_donor"),
             ("coverage_donor_pooled_quantile", "random_minus_donor"),
             ("pearson_donor", "frac_donor")]
    crows = []
    for a, b in pairs:
        if a not in T or b not in T:
            continue
        v = T[[a, b]].dropna()
        if len(v) < 20:
            continue
        rho = spearmanr(v[a], v[b])
        crows.append(dict(arm=arm, task=task, encoder=enc, x=a, y=b, n=len(v),
                          spearman=float(rho.statistic), p=float(rho.pvalue)))
    return T, pd.DataFrame(crows)


def breast_strata(td, CELLS, FOLD):
    """Section 13.7.4's two strata, with the instrument-generation stratum reported BOTH by
    sample (3 prototype against 15 production) and by donor group (2 against 13), which is
    section 13.10 item 3's correction to the memo's 'three against twelve'."""
    gen = {s["sample_id"]: s["instrument_generation"] for s in td["samples"]}
    dis = {s["sample_id"]: s.get("disease_group", "NA") for s in td["samples"]}
    don = {s["sample_id"]: s["donor_id"] for s in td["samples"]}
    gen_of_donor = {}
    for s, d in don.items():
        gen_of_donor.setdefault(d, set()).add(gen[s])
    C = CELLS[CELLS.slide_ge_min_spots].copy()
    C["instrument_generation"] = C.slide.map(gen)
    C["disease_group"] = C.slide.map(dis)
    C["donor_group"] = C.slide.map(don)
    C["donor_group_generation"] = C.donor_group.map(
        lambda d: "prototype" if gen_of_donor[d] == {"prototype"} else
                  "production" if gen_of_donor[d] == {"production"} else "mixed")
    rows = []
    for key, col in (("instrument_generation_by_sample", "instrument_generation"),
                     ("instrument_generation_by_donor_group", "donor_group_generation"),
                     ("disease", "disease_group")):
        for (design, method, lvl), g in C.groupby(["design", "method", col]):
            rows.append(dict(
                stratum=key, level=lvl, design=design, method=method,
                n_slides=int(g.slide.nunique()), n_donor_groups=int(g.donor_group.nunique()),
                n_cells=len(g), coverage=float(g.coverage.mean()),
                width_mean=float(g.width_mean.mean()),
                interval_score=float(g.interval_score.mean()),
                miss_above=float(g.miss_above.mean()), miss_below=float(g.miss_below.mean()),
                slides=";".join(sorted(g.slide.unique()))))
    return pd.DataFrame(rows), C


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--arm", required=True, choices=sorted(ARMS))
    ap.add_argument("--stage", required=True, choices=("genes", "fit"))
    ap.add_argument("--encoder", default="")
    ap.add_argument("--shard", default="1/1")
    ap.add_argument("--n-repeats", type=int, default=None)
    ap.add_argument("--max-folds", type=int, default=None)
    a = ap.parse_args(argv or sys.argv[1:])
    arm = a.arm
    task = ARMS[arm]
    out = f"{ROOT}/{OUTDIR}"
    os.makedirs(out, exist_ok=True)
    td = json.load(open(f"{TD_DIR}/{task}.json"))
    assert td["task_def_version"] == 1 and td["task"] == task
    args = HArgs(a.n_repeats, a.max_folds)
    t_start = time.time()
    k, nsh = (int(x) for x in a.shard.split("/"))

    cfg = dict(stage=f"round3_D4_{arm}_{a.stage}", script="code/scripts/round3_d4_sets.py",
               arm=arm, task=task, encoder=a.encoder, designs=ARM_DESIGNS[arm],
               a4b_K=A4B_K, a4b_draws=A4B_DRAWS, k_genes=K_GENES,
               min_cells_pct=GC.MIN_CELLS_PCT, alpha=args.alpha,
               alpha_store=args.alpha_store, size_match=args.size_match,
               n_cal_draws=args.n_cal_draws, spot_cal_draws=args.spot_cal_draws,
               n_repeats=args.n_repeats, max_folds=args.max_folds, shard=[k, nsh],
               harness_md5=md5(os.path.join(_HERE, "round3_a0_harness.py")),
               a3_md5=md5(os.path.join(_HERE, "round3_a3_weighted.py")),
               gene_check_md5=md5(os.path.join(_HERE, "round2_r2_gene_check.py")),
               task_def=f"{OUTDIR}/task_defs/{task}.json",
               latent=H.LATENT, alpha_num=H.ALPHA_NUM, cal_unit_frac=H.CAL_UNIT_FRAC,
               cal_spot_frac=H.CAL_SPOT_FRAC, min_slide_spots=H.MIN_SLIDE_SPOTS,
               min_T_spots=H.MIN_T_SPOTS, min_C_spots=H.MIN_C_SPOTS,
               seed_source="zlib.crc32")
    blob = json.dumps(cfg, sort_keys=True)
    chash = hashlib.sha256(blob.encode()).hexdigest()[:16]
    print(f"[config] sha256/16 {chash}\n{blob}", flush=True)

    if a.stage == "genes":
        run_genes(td, arm, args, (k, nsh), out)
        print(f"[done] {time.time()-t_start:.0f}s", flush=True)
        return 0

    assert a.encoder, "--stage fit needs --encoder"
    enc = a.encoder
    sel, smeta = read_genes(task, out)
    FOLD, CAL, PEAR, CELLS, samp, Yraw, union, col_of, wall = run_fit(td, arm, enc, args, sel,
                                                                     out)
    suf = f"__{enc}"
    BD, PF = by_design(FOLD)
    # ---- summaries FIRST, parquet last (round 2 R3's lesson)
    BD.to_csv(f"{out}/d4_{arm}{suf}.csv", index=False)
    PF.to_csv(f"{out}/d4_{arm}_by_fold{suf}.csv", index=False)
    FOLD.to_csv(f"{out}/d4_{arm}_cells_by_fold{suf}.csv", index=False)
    CAL.to_csv(f"{out}/d4_{arm}_calibration_units{suf}.csv", index=False)
    pd.DataFrame([dict(task=task, arm=arm, **m) for m in smeta]).to_csv(
        f"{out}/d4_{arm}_gene_shards{suf}.csv", index=False)
    gl = pd.DataFrame([{k2: v2 for k2, v2 in v.items() if k2 != "genes"}
                       | dict(genes=";".join(v["genes"]),
                              genes_off_panel=";".join(v["genes_off_panel"]))
                       for v in sel.values()])
    gl.insert(0, "task", task)
    gl.to_csv(f"{out}/d4_{arm}_fold_genes{suf}.csv", index=False)
    print(f"\n[write] d4_{arm}{suf}.csv\n" + BD.round(5).to_string(index=False), flush=True)

    if arm == "indiana":
        PG, CORR = pergene_decomposition(td, PEAR, CELLS, samp, Yraw, col_of, meta_of(td),
                                         enc, arm, task)
        PG.to_csv(f"{out}/d4_indiana_pergene{suf}.csv", index=False)
        CORR.to_csv(f"{out}/d4_indiana_pergene_correlations{suf}.csv", index=False)
        print(f"[write] d4_indiana_pergene{suf}.csv ({len(PG)} genes)")
        print(CORR.round(4).to_string(index=False), flush=True)
    if arm == "breast":
        ST, _ = breast_strata(td, CELLS, FOLD)
        ST.to_csv(f"{out}/d4_breast_strata{suf}.csv", index=False)
        print(f"[write] d4_breast_strata{suf}.csv")
        print(ST.round(5).to_string(index=False), flush=True)

    d = CELLS.copy()
    for f in CELL_SCHEMA:
        if f.type == pa.string():
            d[f.name] = d[f.name].astype(str)
        elif f.type == pa.int32():
            d[f.name] = d[f.name].astype("int32")
        elif f.type == pa.float32():
            d[f.name] = d[f.name].astype("float32")
        elif f.type == pa.bool_():
            d[f.name] = d[f.name].astype(bool)
    pq.write_table(pa.Table.from_pandas(d[CELL_COLS], schema=CELL_SCHEMA,
                                        preserve_index=False),
                   f"{out}/d4_{arm}_cells{suf}.parquet", compression="snappy")
    print(f"[write] d4_{arm}_cells{suf}.parquet ({len(d):,} rows, explicit schema)", flush=True)

    with open(f"{out}/PROVENANCE__d4_{arm}{suf}.txt", "w") as f:
        f.write("=" * 78 + "\n"
                f"Round 3, stage D4 arm {arm}, encoder {enc}\n"
                f"slurm_job_id    : {os.environ.get('SLURM_JOB_ID', 'NA')}\n"
                f"slurm_partition : {os.environ.get('SLURM_JOB_PARTITION', 'NA')}\n"
                f"node            : {os.environ.get('SLURMD_NODENAME', 'NA')}\n"
                f"gpu             : none (CPU job)\n"
                f"date            : {time.strftime('%Y-%m-%dT%H:%M:%S%z')}\n"
                f"repo_commit     : "
                f"{subprocess.run(['git', '-C', ROOT, 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()}\n"
                f"script          : code/scripts/round3_d4_sets.py\n"
                f"script_md5      : {md5(os.path.abspath(__file__))}\n"
                f"harness_md5     : {cfg['harness_md5']}\n"
                f"a3_script_md5   : {cfg['a3_md5']}\n"
                f"gene_check_md5  : {cfg['gene_check_md5']}\n"
                f"command_line    : {' '.join(sys.argv)}\n"
                f"pythonhashseed  : {os.environ.get('PYTHONHASHSEED', 'unset')}\n"
                f"config_hash     : sha256/16 {chash}\n"
                f"config          : {blob}\n"
                f"gene_shards     : {json.dumps(smeta)}\n"
                f"n_fold_cells    : {len(FOLD)}\n"
                f"wall_seconds    : {time.time() - t_start:.0f}\n"
                f"plan            : round3_execution_plan.md section 13.7\n")
    print(f"\n[done] {time.time()-t_start:.0f}s", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
