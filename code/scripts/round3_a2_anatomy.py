#!/usr/bin/env python
"""Round 3, stage A2, the Anatomy track: the parts of A2 answerable from A1's committed
outputs without rerunning the harness.

Owned items, from docs/round3_execution_plan.md section 12.8:

  A2a  strata, for `abs` and `scaled` both: test slide; `resolution_group`; session;
       `cal_shares_session_with_test`; gene; `donor_label_status`; and K, the number of
       calibration units, as a stratum for every fold. Plus the `random` design's
       across-slide standard deviation of coverage per task and score, `abs` against
       `scaled`. Plus PRAD by fold under `patient` and `donor`, with the held-out patient,
       the calibration slides and their count K, the session structure of each side and the
       resolution class of each side written out.
  A2d  first half: per PRAD `slide_out` test slide, coverage of calibration draws whose
       calibration set contains a slide from the test slide's donor against draws whose
       calibration set does not, test slide and encoder held fixed, as a paired difference.
  A2e  mean and median `abs` width per encoder per design, joined to benchmark Pearson,
       and the coverage range across encoders per design.
  R7   within each task, Spearman between gene-level coverage shortfall under the `donor`
       design and R7's per-gene `random - patient` term.

Not owned by this track and not computed here: A2a's predicted-value decile and
neoplastic-fraction strata, A2b, A2c, A2d's new `slide_out_cal_other_donor` arm, A2f's
level-versus-scale decomposition, and both A2 figures. Those need a harness rerun (A1's
per-gene parquet carries coverage and misses per slide and gene but nothing at spot level
and no slide offset b_s or oracle width) and belong to the Mechanisms track.

TWO MODES, because the per-gene parquets are gitignored and live only on Longleaf.

  --mode gene   Runs in a Slurm job on Longleaf. Reads
                results/round3/A1_coverage/pergene__<enc>__{main,slideout}.parquet, collapses
                each to the (task, label_set, encoder, design, score, fold, gene) level under
                the project's aggregation convention, and writes a2_gene_by_fold.parquet plus
                a printed summary into the job's own workdir. Writes nothing into the Longleaf
                repository tree.

  --mode local  Runs in the local clone. Reads the A1 summary CSVs, the task definitions,
                R7, the benchmark table and the parquet brought back from --gene-dir, and
                writes the four A2 fragments this track owns plus PROVENANCE__anatomy.txt.

AGGREGATION CONVENTION. A1's own convention, from `_summaries` in
code/scripts/round3_a0_harness.py: per test slide, then over genes, then over calibration
draws and repeats inside a fold, then over folds. Every mean in this script follows it.
Two units of aggregation appear, and each stratum row records which one it used in
`agg_unit`:

  cell        (encoder, design, score, fold, repeat, cal_draw), coverage averaged over the
              test slides of that draw. This is A1's `per_cell`. Used where the stratum can
              change between draws inside a fold (`cal_shares_session_with_test`, K).
  cell_slide  (encoder, design, score, fold, slide), coverage averaged over the repeats and
              draws in which that slide was a test slide. Used for every stratum that is a
              property of the test slide.
  cell_gene   (encoder, design, score, fold, gene), coverage averaged over test slides then
              over repeats and draws. Used for the gene stratum and the R7 join.

Slides with fewer than `min_slide_spots` test spots are already dropped by the harness
(`slide_ge_min_spots`); the gene mode reapplies that filter, the local mode inherits it
because a1_by_slide is written from the filtered frame.

STRATUM ROWS POOL OVER ENCODERS. n_cells is the number of units of the stated kind that went
into the row, so a stratum row for a design with 12 encoders counts 12 times the number of
fold-by-slide (or fold-by-draw) combinations. coverage_sd is the standard deviation across
those units, which mixes encoder-to-encoder and fold-to-fold variation; it is a dispersion,
not a standard error.

Usage, gene mode, inside a Slurm job on Longleaf:

    PYTHONHASHSEED=0 $PY code/scripts/round3_a2_anatomy.py --mode gene \
        --a1-dir /work/users/w/e/weiyang/hest_replication/results/round3/A1_coverage \
        --out-dir $PWD

Usage, local mode, in the local clone:

    PYTHONHASHSEED=0 python code/scripts/round3_a2_anatomy.py --mode local \
        --repo-root . --gene-dir <dir holding a2_gene_by_fold.parquet> \
        --out-dir results/round3/A2_conditional
"""
import argparse
import datetime as dt
import glob
import hashlib
import json
import os
import platform
import subprocess
import sys
import zlib

import numpy as np
import pandas as pd

NOMINAL = 0.90
ENCODERS = ["conch_v1", "conch_v15", "ctranspath", "gigapath", "hoptimus0", "hoptimus1",
            "phikon", "resnet50", "uni_v1", "uni_v2", "virchow", "virchow2"]
RUNS = ["main", "slideout"]
CELL_KEY = ["task", "label_set", "encoder", "design", "score", "fold", "repeat", "cal_draw"]


# --------------------------------------------------------------------------- gene mode

def mode_gene(args):
    import pyarrow as pa
    import pyarrow.parquet as pq

    frames = []
    for enc in ENCODERS:
        for run in RUNS:
            p = f"{args.a1_dir}/pergene__{enc}__{run}.parquet"
            if not os.path.exists(p):
                print(f"[skip] {p} absent", flush=True)
                continue
            pg = pd.read_parquet(p)
            use = pg[pg["slide_ge_min_spots"].astype(bool)]
            if not len(use):
                use = pg
            # per slide -> per gene over slides
            g1 = (use.groupby(CELL_KEY + ["calibration_unit", "gene"], dropna=False)
                     [["coverage", "width_mean", "interval_score",
                       "miss_above", "miss_below"]].mean().reset_index())
            # over repeats and calibration draws inside a fold
            g2 = (g1.groupby(["task", "label_set", "encoder", "design", "score", "fold",
                              "calibration_unit", "gene"], dropna=False)
                    .agg(coverage=("coverage", "mean"),
                         width_mean=("width_mean", "mean"),
                         interval_score=("interval_score", "mean"),
                         miss_above=("miss_above", "mean"),
                         miss_below=("miss_below", "mean"),
                         n_draw_cells=("coverage", "size")).reset_index())
            frames.append(g2)
            print(f"[read] {os.path.basename(p)}: {len(pg):,} rows -> {len(g2):,} "
                  f"(encoder, fold, gene) rows", flush=True)
    assert frames, "no per-gene parquets found"
    d = pd.concat(frames, ignore_index=True)

    SCHEMA = pa.schema([
        ("task", pa.string()), ("label_set", pa.string()), ("encoder", pa.string()),
        ("design", pa.string()), ("score", pa.string()), ("fold", pa.string()),
        ("calibration_unit", pa.string()), ("gene", pa.string()),
        ("coverage", pa.float64()), ("width_mean", pa.float64()),
        ("interval_score", pa.float64()), ("miss_above", pa.float64()),
        ("miss_below", pa.float64()), ("n_draw_cells", pa.int32()),
    ])
    cols = [f.name for f in SCHEMA]
    for f in SCHEMA:
        if f.type == pa.string():
            d[f.name] = d[f.name].astype(str)
        elif f.type == pa.int32():
            d[f.name] = d[f.name].astype("int32")
        else:
            d[f.name] = d[f.name].astype("float64")
    os.makedirs(args.out_dir, exist_ok=True)
    out = f"{args.out_dir}/a2_gene_by_fold.parquet"
    pq.write_table(pa.Table.from_pandas(d[cols], schema=SCHEMA, preserve_index=False),
                   out, compression="snappy")
    print(f"\n[write] a2_gene_by_fold.parquet ({len(d):,} rows, explicit schema)", flush=True)

    # summaries before the bulk table is read anywhere else
    print("\n[summary] rows by design and score", flush=True)
    print(d.groupby(["design", "score"]).size().to_string(), flush=True)
    print("\n[summary] gene-level coverage, mean over (encoder, fold, gene) by design/score",
          flush=True)
    print(d.groupby(["design", "score"])["coverage"].agg(["mean", "std", "min", "max"])
           .round(4).to_string(), flush=True)
    print("\n[summary] abs, donor design, per task: mean gene coverage and its spread over genes",
          flush=True)
    dn = d[(d.design == "donor") & (d.score == "abs")]
    per_gene = dn.groupby(["task", "label_set", "gene"])["coverage"].mean().reset_index()
    print(per_gene.groupby(["task", "label_set"])["coverage"]
          .agg(n_genes="size", mean="mean", sd="std", min="min", max="max")
          .round(4).to_string(), flush=True)
    with open(f"{args.out_dir}/a2_gene_mode_summary.txt", "w") as fh:
        fh.write(f"rows {len(d)}\n")
        fh.write(d.groupby(["design", "score"]).size().to_string() + "\n")
    return 0


# --------------------------------------------------------------------------- local mode

def _read_a1(a1):
    def load(kind):
        fr = []
        for enc in ENCODERS:
            for run in RUNS:
                p = f"{a1}/a1_{kind}__{enc}__{run}.csv"
                if os.path.exists(p):
                    x = pd.read_csv(p)
                    x["run"] = run
                    fr.append(x)
        assert fr, f"no a1_{kind} files under {a1}"
        return pd.concat(fr, ignore_index=True)
    return {k: load(k) for k in ["by_slide", "by_fold", "by_task", "calibration_units"]}


def _samples(repo):
    rows = []
    for f in sorted(glob.glob(f"{repo}/results/round3/task_defs/*.json")):
        name = os.path.basename(f)[:-5]
        if name.endswith("schema"):
            continue
        d = json.load(open(f))
        if "samples" not in d:
            continue
        for s in d["samples"]:
            r = dict(s)
            r["task"] = d["task"]
            r["label_set"] = d["label_set"]
            r["task_file"] = name
            rows.append(r)
    S = pd.DataFrame(rows)
    assert len(S), "no task definitions read"
    return S


def _stratum(df, value_col, agg_unit, stratum, keys=("task", "label_set", "design", "score"),
             detail_cols=()):
    """One row per stratum level, from already-collapsed units.

    `detail_cols` names columns whose distinct values inside the row are written into
    `detail`. This is where a stratum records the other variables that move with it: K
    covaries with `calibration_unit`, for instance, because the folds with the largest K are
    the block-calibrated folds of the two-sample tasks, so a K row that did not name its
    calibration unit would be a confounded comparison presented as a clean one.
    """
    aggs = dict(n_cells=("coverage", "size"),
                coverage_mean=("coverage", "mean"),
                coverage_sd=("coverage", "std"),
                width_mean=("width_mean", "mean"),
                width_median=("width_mean", "median"))
    for i, c in enumerate(detail_cols):
        aggs[f"_d{i}"] = (c, lambda s: ";".join(sorted({str(x) for x in s.dropna()})))
    g = (df.groupby(list(keys) + [value_col], dropna=False).agg(**aggs).reset_index())
    g = g.rename(columns={value_col: "stratum_value"})
    g["stratum"] = stratum
    g["agg_unit"] = agg_unit
    if detail_cols:
        g["detail"] = [" | ".join(f"{c}={row[f'_d{i}']}" for i, c in enumerate(detail_cols))
                       for _, row in g.iterrows()]
        g = g.drop(columns=[f"_d{i}" for i in range(len(detail_cols))])
    else:
        g["detail"] = ""
    return g


ORDER = ["task", "label_set", "design", "score", "stratum", "stratum_value", "agg_unit",
         "n_cells", "coverage_mean", "coverage_sd", "width_mean", "width_median", "detail"]


def mode_local(args):
    repo = os.path.abspath(args.repo_root)
    a1 = f"{repo}/results/round3/A1_coverage"
    out = args.out_dir if os.path.isabs(args.out_dir) else f"{repo}/{args.out_dir}"
    os.makedirs(out, exist_ok=True)
    T = _read_a1(a1)
    S = _samples(repo)
    bs, bf, bt, cu = T["by_slide"], T["by_fold"], T["by_task"], T["calibration_units"]

    # ---- anchor: a1_by_slide collapsed to the cell level must reproduce a1_by_fold
    per_cell = (bs.groupby(CELL_KEY + ["calibration_unit"], dropna=False)
                  .agg(coverage=("coverage", "mean"), width_mean=("width_mean", "mean"),
                       n_slides=("slide", "nunique")).reset_index())
    chk = (per_cell.groupby(["task", "label_set", "encoder", "design", "score", "fold"],
                            dropna=False)[["coverage", "width_mean"]].mean().reset_index()
           .merge(bf, on=["task", "label_set", "encoder", "design", "score", "fold"],
                  suffixes=("_mine", "_a1")))
    dcov = float(np.abs(chk["coverage_mine"] - chk["coverage_a1"]).max())
    dwid = float(np.abs(chk["width_mean_mine"] - chk["width_mean_a1"]).max())
    print(f"[anchor] a1_by_slide -> per_fold against a1_by_fold: {len(chk)} folds, "
          f"max |dcoverage| {dcov:.3e}, max |dwidth| {dwid:.3e}", flush=True)
    anchor = dict(n_folds=int(len(chk)), max_abs_dcoverage=dcov, max_abs_dwidth=dwid,
                  tolerance=1e-9, passed=bool(dcov < 1e-9 and dwid < 1e-9))

    # ---- unit 1: cell_slide, one row per (encoder, design, score, fold, slide)
    cell_slide = (bs.groupby(["task", "label_set", "encoder", "design", "score", "fold",
                              "calibration_unit", "slide"], dropna=False)
                    .agg(coverage=("coverage", "mean"), width_mean=("width_mean", "mean"),
                         n_draw_cells=("coverage", "size"),
                         n_test=("n_test", "first")).reset_index())
    cov = S[["task", "label_set", "sample_id", "donor_id", "session", "resolution_group",
             "pixel_size_um", "resolution_uncertain", "donor_label_status"]].copy()
    cell_slide = cell_slide.merge(cov, left_on=["task", "label_set", "slide"],
                                  right_on=["task", "label_set", "sample_id"], how="left")
    miss = int(cell_slide["donor_id"].isna().sum())
    assert miss == 0, f"{miss} by_slide rows did not match a task-definition sample"

    # ---- unit 2: cell, one row per (encoder, design, score, fold, repeat, cal_draw)
    # a1_calibration_units has no `score` column: a calibration set is a property of the
    # (design, fold, repeat, draw) cell, and both scores are computed on it.
    cu_key = [k for k in CELL_KEY if k != "score"]
    flags = cu[cu_key + ["n_cal_units", "n_cal_slides", "cal_slides", "test_slides",
                         "cal_shares_donor_with_test", "cal_shares_session_with_test",
                         "cal_shares_resolution_group_with_test",
                         "cal_shares_exact_session_with_test"]]
    cell = per_cell.merge(flags, on=cu_key, how="left", validate="m:1")
    nmiss = int(cell["n_cal_units"].isna().sum())
    assert nmiss == 0, f"{nmiss} cells did not match a calibration-unit row"

    strata = []

    # A2a-1 test slide
    strata.append(_stratum(cell_slide, "slide", "cell_slide", "test_slide"))
    # A2a-2 resolution_group of the test slide
    strata.append(_stratum(cell_slide, "resolution_group", "cell_slide", "resolution_group"))
    # A2a-3 session of the test slide; recorded only for PRAD's patient-2 slides
    sess = cell_slide.copy()
    sess["session"] = sess["session"].fillna("not_recorded")
    strata.append(_stratum(sess, "session", "cell_slide", "session"))
    # A2a-4 donor_label_status of the test slide
    strata.append(_stratum(cell_slide, "donor_label_status", "cell_slide",
                           "donor_label_status"))
    # A2a-5 cal_shares_session_with_test
    css = cell.copy()
    css["cal_shares_session_with_test"] = css["cal_shares_session_with_test"].astype(str)
    # The harness defines this flag as (shares resolution_group) OR (shares exact session),
    # which is the plan's section 4.2 parenthetical. `session` is recorded only for PRAD's
    # patient-2 slides, so outside PRAD this column IS the resolution-group flag. Both halves
    # are written into `detail` so a row is not read as a session contrast when it is not one.
    strata.append(_stratum(css, "cal_shares_session_with_test", "cell",
                           "cal_shares_session_with_test",
                           detail_cols=("calibration_unit",
                                        "cal_shares_resolution_group_with_test",
                                        "cal_shares_exact_session_with_test")))
    # A2a-6 K, the number of calibration units, as a stratum for every fold. Under `random`
    # the calibration unit is the spot, so K there is the calibration spot count, not a
    # count of donors or slides; the `detail` column names the unit for every row.
    kk = cell.copy()
    kk["K"] = kk["n_cal_units"].astype("int64").astype(str)
    strata.append(_stratum(kk, "K", "cell", "n_cal_units_K",
                           detail_cols=("calibration_unit", "fold")))

    # A2a-7 gene, from the parquet brought back from Longleaf
    gene_note = ""
    gp = f"{args.gene_dir}/a2_gene_by_fold.parquet" if args.gene_dir else None
    gene = None
    if gp and os.path.exists(gp):
        gene = pd.read_parquet(gp)
        strata.append(_stratum(gene, "gene", "cell_gene", "gene"))
        gene_note = (f"gene stratum from {os.path.basename(gp)}, {len(gene):,} "
                     f"(encoder, fold, gene) rows")
    else:
        gene_note = "gene stratum NOT computed: a2_gene_by_fold.parquet absent"
        print(f"[warn] {gene_note}", flush=True)

    # A2a-8 the random design's across-slide sd of coverage, abs against scaled
    rnd = cell_slide[cell_slide.design == "random"]
    per_slide = (rnd.groupby(["task", "label_set", "encoder", "score", "slide"], dropna=False)
                   ["coverage"].mean().reset_index())
    per_slide_w = (rnd.groupby(["task", "label_set", "encoder", "score", "slide"], dropna=False)
                     ["width_mean"].mean().reset_index())
    per_slide = per_slide.merge(per_slide_w,
                               on=["task", "label_set", "encoder", "score", "slide"])
    sd_enc = (per_slide.groupby(["task", "label_set", "encoder", "score"], dropna=False)
                .agg(n_cells=("slide", "nunique"), coverage_mean=("coverage", "mean"),
                     coverage_sd=("coverage", "std"), width_mean=("width_mean", "mean"),
                     width_median=("width_mean", "median")).reset_index())
    sd_enc["design"] = "random"
    sd_enc["stratum"] = "random_across_slide_coverage_sd"
    sd_enc = sd_enc.rename(columns={"encoder": "stratum_value"})
    sd_enc["agg_unit"] = "slide (mean over folds, repeats, draws), one row per encoder"
    sd_enc["detail"] = "coverage_sd is the across-slide sd for this encoder"
    strata.append(sd_enc)
    sd_mean = (sd_enc.groupby(["task", "label_set", "design", "score"], dropna=False)
                 .agg(n_cells=("n_cells", "first"),
                      coverage_mean=("coverage_mean", "mean"),
                      coverage_sd=("coverage_sd", "mean"),
                      width_mean=("width_mean", "mean"),
                      width_median=("width_median", "mean"),
                      sd_min=("coverage_sd", "min"), sd_max=("coverage_sd", "max"))
                 .reset_index())
    sd_mean["stratum"] = "random_across_slide_coverage_sd"
    sd_mean["stratum_value"] = "MEAN_OVER_12_ENCODERS"
    sd_mean["agg_unit"] = "slide, then mean of the 12 encoders' across-slide sds"
    sd_mean["detail"] = sd_mean.apply(
        lambda r: f"across-slide sd over encoders: min {r.sd_min:.6f}, max {r.sd_max:.6f}",
        axis=1)
    strata.append(sd_mean.drop(columns=["sd_min", "sd_max"]))

    # A2a-9 PRAD by fold under patient and donor, written out
    prad = _prad_by_fold(cell, cell_slide, S)
    strata.append(prad)

    A = pd.concat(strata, ignore_index=True)
    A["stratum_value"] = A["stratum_value"].astype(str)
    A = A[ORDER].sort_values(["stratum", "task", "label_set", "design", "score",
                              "stratum_value"]).reset_index(drop=True)
    A.to_csv(f"{out}/a2_by_stratum__anatomy.csv", index=False)
    print(f"[write] a2_by_stratum__anatomy.csv ({len(A)} rows)", flush=True)
    print(A.groupby("stratum").size().to_string(), flush=True)

    # ---- A2d first half, the paired within-PRAD donor-sharing comparison
    D = _prad_donor_sharing(cell, cu)
    D.to_csv(f"{out}/a2_prad_donor_sharing__paired.csv", index=False)
    print(f"[write] a2_prad_donor_sharing__paired.csv ({len(D)} rows)", flush=True)

    # ---- A2e width by encoder
    W = _width_by_encoder(bf, bt, repo)
    W.to_csv(f"{out}/a2_width_by_encoder.csv", index=False)
    print(f"[write] a2_width_by_encoder.csv ({len(W)} rows)", flush=True)

    # ---- the R7 per-gene join
    J = _pergene_join(gene, repo)
    J.to_csv(f"{out}/a2_pergene_join.csv", index=False)
    print(f"[write] a2_pergene_join.csv ({len(J)} rows)", flush=True)

    _provenance(args, out, repo, a1, anchor, gene_note, A, D, W, J, gp)
    return 0


def _prad_by_fold(cell, cell_slide, S):
    """PRAD by fold under `patient` and `donor`, with the held-out patient, the calibration
    slides and their count K, the session structure of each side and the resolution class of
    each side written out."""
    P = S[(S.task == "PRAD")].set_index("sample_id")

    def describe(slides):
        sub = P.loc[[s for s in slides if s in P.index]]
        don = sorted(sub.donor_id.unique().tolist())
        sess = sub.session.fillna("not_recorded")
        sessu = sorted(sess.unique().tolist())
        res = sorted(sub.resolution_group.unique().tolist())
        px = sub.pixel_size_um
        return (f"donors {'+'.join(don)}; sessions {'+'.join(sessu)} "
                f"({len(sessu)} distinct); resolution_group {'+'.join(res)}; "
                f"pixel_size_um {px.min():.4f} to {px.max():.4f}")

    rows = []
    c = cell[(cell.task == "PRAD") & (cell.design.isin(["patient", "donor"]))]
    cs = cell_slide[(cell_slide.task == "PRAD") & (cell_slide.design.isin(["patient", "donor"]))]
    for (design, score, fold), g in c.groupby(["design", "score", "fold"]):
        cal = sorted({s for v in g.cal_slides.dropna() for s in str(v).split(";") if s})
        test = sorted({s for v in g.test_slides.dropna() for s in str(v).split(";") if s})
        Ks = sorted(g.n_cal_units.astype(int).unique().tolist())
        held = sorted(P.loc[[t for t in test if t in P.index]].donor_id.unique().tolist())
        # per-draw calibration sets, listed so the fold is reproducible from the row
        draws = (g[["encoder", "cal_draw", "cal_slides"]]
                 .drop_duplicates(subset=["cal_draw", "cal_slides"])
                 .sort_values("cal_draw"))
        drawtxt = "; ".join(f"draw {int(r.cal_draw)}: {r.cal_slides}"
                            for r in draws.itertuples())
        detail = (f"held-out donor(s) {'+'.join(held)} | K={'/'.join(map(str, Ks))} "
                  f"calibration units (unit = slide) | "
                  f"calibration slides used across draws: {','.join(cal)} | {drawtxt} | "
                  f"CALIBRATION SIDE: {describe(cal)} | TEST SIDE: {describe(test)}")
        sl = cs[(cs.design == design) & (cs.score == score) & (cs.fold == fold)]
        rows.append(dict(task="PRAD", label_set="shipped", design=design, score=score,
                         stratum="prad_fold", stratum_value=f"{design}:{fold}",
                         agg_unit="cell (encoder, fold, repeat, cal_draw)",
                         n_cells=int(len(g)),
                         coverage_mean=float(g.coverage.mean()),
                         coverage_sd=float(g.coverage.std()),
                         width_mean=float(g.width_mean.mean()),
                         width_median=float(g.width_mean.median()),
                         detail=detail))
        # the calibration set's own between-slide spread of coverage, the memo's section 2.5
        # reading: a slide-level dispersion of the calibration side is not available from A1's
        # outputs, so what is reported here is the TEST side's between-slide spread.
        rows[-1]["detail"] += (
            f" | test-side between-slide sd of coverage "
            f"{float(sl.groupby('slide').coverage.mean().std()):.4f} over "
            f"{sl.slide.nunique()} test slides")
    return pd.DataFrame(rows)


def _prad_donor_sharing(cell, cu):
    """A2d, first half. Per PRAD `slide_out` test slide and encoder, coverage of the draws
    whose calibration set contains a slide from the test slide's donor against the draws whose
    calibration set does not. Test slide and encoder are held fixed; the proper-training set is
    the same across draws within a fold, so the arms differ only in the calibration draw.

    DIFFERENCE LIST, written before the term is named. Between the two arms:
      1. whether the calibration set contains a slide from the test slide's donor;
      2. in PRAD, resolution class: patient 1's slides are `>0.50` and `0.15-0.23`, patient 2's
         are all `0.30-0.40`, so a calibration set drawn only from the other donor also changes
         resolution group;
      3. in PRAD, scanning session: `session` is recorded only for patient 2's slides
         (two sessions, MEND139-146 and MEND147-153) and is absent for patient 1's, so the
         arms also differ in whether session is recorded at all;
      4. the identity of the calibration slides, and hence the calibration spot count.
    Held fixed: task, encoder, test slide, design, proper-training set, K, score.
    The term is therefore a donor-sharing term confounded with resolution class and session.
    """
    c = cell[(cell.task == "PRAD") & (cell.design == "slide_out")].copy()
    c["shares"] = c["cal_shares_donor_with_test"].astype(str).str.lower()
    keep = (c.groupby(["encoder", "score", "fold"])["shares"].transform("nunique") > 1)
    both = c[keep]
    rows = []
    for (enc, score, fold), g in both.groupby(["encoder", "score", "fold"]):
        gs = g[g.shares == "true"]
        gn = g[g.shares == "false"]
        if not len(gs) or not len(gn):
            continue
        rows.append(dict(
            level="pair", task="PRAD", label_set="shipped", design="slide_out",
            encoder=enc, score=score, test_slide=fold,
            n_draws_share=int(len(gs)), n_draws_noshare=int(len(gn)),
            K_share=int(gs.n_cal_units.iloc[0]), K_noshare=int(gn.n_cal_units.iloc[0]),
            coverage_share=float(gs.coverage.mean()),
            coverage_noshare=float(gn.coverage.mean()),
            coverage_diff_share_minus_noshare=float(gs.coverage.mean() - gn.coverage.mean()),
            width_share=float(gs.width_mean.mean()),
            width_noshare=float(gn.width_mean.mean()),
            width_diff_share_minus_noshare=float(gs.width_mean.mean() - gn.width_mean.mean()),
            cal_slides_share=" | ".join(sorted(gs.cal_slides.astype(str))),
            cal_slides_noshare=" | ".join(sorted(gn.cal_slides.astype(str))),
            res_group_shared_share=";".join(sorted(
                gs.cal_shares_resolution_group_with_test.astype(str).unique())),
            res_group_shared_noshare=";".join(sorted(
                gn.cal_shares_resolution_group_with_test.astype(str).unique())),
            session_shared_share=";".join(sorted(
                gs.cal_shares_session_with_test.astype(str).unique())),
            session_shared_noshare=";".join(sorted(
                gn.cal_shares_session_with_test.astype(str).unique()))))
    P = pd.DataFrame(rows)
    assert len(P), "no PRAD slide_out fold had both donor-sharing arms"
    outs = [P]
    # per encoder, paired over test slides
    for score, g in P.groupby("score"):
        for enc, ge in g.groupby("encoder"):
            outs.append(pd.DataFrame([_paired_summary(
                ge, f"encoder:{enc}", score, "paired over test slides, one encoder")]))
        outs.append(pd.DataFrame([_paired_summary(
            g, "ALL_ENCODERS", score, "paired over (encoder, test slide)")]))
        # slide-level means over encoders first, then paired over the test slides
        m = (g.groupby("test_slide")
              .agg(coverage_share=("coverage_share", "mean"),
                   coverage_noshare=("coverage_noshare", "mean"),
                   width_share=("width_share", "mean"),
                   width_noshare=("width_noshare", "mean")).reset_index())
        m["coverage_diff_share_minus_noshare"] = m.coverage_share - m.coverage_noshare
        m["width_diff_share_minus_noshare"] = m.width_share - m.width_noshare
        outs.append(pd.DataFrame([_paired_summary(
            m, "MEAN_OVER_ENCODERS_THEN_SLIDES", score,
            "encoders averaged within a test slide, then paired over the 5 test slides")]))
    return pd.concat(outs, ignore_index=True)


def _paired_summary(g, label, score, how):
    d = g["coverage_diff_share_minus_noshare"].to_numpy(dtype=float)
    wd = g["width_diff_share_minus_noshare"].to_numpy(dtype=float)
    n = len(d)
    sd = float(np.std(d, ddof=1)) if n > 1 else float("nan")
    return dict(level="summary", task="PRAD", label_set="shipped", design="slide_out",
                encoder=label, score=score, test_slide=how,
                n_draws_share=int(n), n_draws_noshare=int(n),
                K_share=np.nan, K_noshare=np.nan,
                coverage_share=float(np.mean(g["coverage_share"])),
                coverage_noshare=float(np.mean(g["coverage_noshare"])),
                coverage_diff_share_minus_noshare=float(np.mean(d)),
                width_share=float(np.mean(g["width_share"])),
                width_noshare=float(np.mean(g["width_noshare"])),
                width_diff_share_minus_noshare=float(np.mean(wd)),
                cal_slides_share=f"n_pairs={n}; sd(diff)={sd:.6f}; "
                                 f"min={float(np.min(d)):.6f}; max={float(np.max(d)):.6f}",
                cal_slides_noshare=f"sd(width diff)="
                                   f"{float(np.std(wd, ddof=1)) if n > 1 else float('nan'):.6f}",
                res_group_shared_share="", res_group_shared_noshare="",
                session_shared_share="", session_shared_noshare="")


def _width_by_encoder(bf, bt, repo):
    """A2e. Mean and median `abs` width per encoder per design, joined to benchmark Pearson,
    plus the coverage range across encoders per design."""
    bench = pd.read_csv(f"{repo}/results/summary/results_encoder.csv")
    bench = bench[bench["head"] == "pca_ridge"][["encoder", "avg_paper9"]]
    f = bf[bf.score == "abs"]
    # pooled over every fold of every task file
    pooled = (f.groupby(["encoder", "design"])
                .agg(n_folds=("fold", "size"),
                     width_mean_pooled_over_folds=("width_mean", "mean"),
                     width_median_pooled_over_folds=("width_mean", "median"),
                     coverage_mean_pooled_over_folds=("coverage", "mean")).reset_index())
    # task-balanced: per task file first, then over task files
    t = bt[bt.score == "abs"]
    bal = (t.groupby(["encoder", "design"])
             .agg(n_task_files=("task", "size"),
                  width_mean_over_task_files=("width_mean", "mean"),
                  width_median_over_task_files=("width_mean", "median"),
                  coverage_mean_over_task_files=("coverage_mean", "mean")).reset_index())
    W = pooled.merge(bal, on=["encoder", "design"]).merge(bench, on="encoder", how="left")
    assert W["avg_paper9"].notna().all(), "an encoder is missing from results_encoder.csv"
    W = W.rename(columns={"avg_paper9": "benchmark_pca_ridge_avg_paper9"})
    rng = (W.groupby("design")["coverage_mean_over_task_files"]
             .agg(coverage_min_across_encoders="min",
                  coverage_max_across_encoders="max").reset_index())
    rng["coverage_range_across_encoders"] = (rng.coverage_max_across_encoders
                                             - rng.coverage_min_across_encoders)
    W = W.merge(rng, on="design")
    # Spearman of width against benchmark Pearson, per design
    sp = []
    for design, g in W.groupby("design"):
        sp.append(dict(design=design,
                       spearman_width_mean_vs_pearson=_spearman(
                           g.width_mean_over_task_files, g.benchmark_pca_ridge_avg_paper9),
                       spearman_width_median_vs_pearson=_spearman(
                           g.width_median_over_task_files, g.benchmark_pca_ridge_avg_paper9),
                       spearman_coverage_vs_pearson=_spearman(
                           g.coverage_mean_over_task_files, g.benchmark_pca_ridge_avg_paper9)))
    W = W.merge(pd.DataFrame(sp), on="design")
    return W.sort_values(["design", "benchmark_pca_ridge_avg_paper9"]).reset_index(drop=True)


def _spearman(a, b):
    a = pd.Series(np.asarray(a, dtype=float))
    b = pd.Series(np.asarray(b, dtype=float))
    ok = a.notna() & b.notna()
    if ok.sum() < 3:
        return float("nan")
    return float(a[ok].rank().corr(b[ok].rank()))


def _pergene_join(gene, repo):
    """Within each task, Spearman between gene-level coverage shortfall under the `donor`
    design and R7's per-gene `random - patient` term."""
    if gene is None:
        return pd.DataFrame([dict(level="NOT_COMPUTED", task="", label_set="", encoder="",
                                  n_genes=0, spearman=np.nan,
                                  note="a2_gene_by_fold.parquet absent")])
    r7 = pd.read_csv(f"{repo}/results/round2/R7_pergene/r7_pergene_decomposition.csv")
    r7 = r7[["encoder", "task", "gene", "random_minus_patient", "donor_label_status"]]
    g = gene[(gene.design == "donor") & (gene.score == "abs")].copy()
    g = (g.groupby(["task", "label_set", "encoder", "gene"])
          .agg(coverage=("coverage", "mean"), n_folds=("fold", "nunique")).reset_index())
    g["shortfall"] = NOMINAL - g["coverage"]
    J = g.merge(r7, on=["encoder", "task", "gene"], how="inner")
    rows = []
    for (task, ls, enc), gg in J.groupby(["task", "label_set", "encoder"]):
        rows.append(dict(level="task_encoder", task=task, label_set=ls, encoder=enc,
                         n_genes=int(len(gg)),
                         spearman=_spearman(gg.shortfall, gg.random_minus_patient),
                         mean_shortfall=float(gg.shortfall.mean()),
                         mean_random_minus_patient=float(gg.random_minus_patient.mean()),
                         note=""))
    for (task, ls), gg in J.groupby(["task", "label_set"]):
        rows.append(dict(level="task_pooled_over_3_r7_encoders", task=task, label_set=ls,
                         encoder="hoptimus0;resnet50;uni_v2", n_genes=int(len(gg)),
                         spearman=_spearman(gg.shortfall, gg.random_minus_patient),
                         mean_shortfall=float(gg.shortfall.mean()),
                         mean_random_minus_patient=float(gg.random_minus_patient.mean()),
                         note="items are (encoder, gene) pairs"))
        m = (gg.groupby("gene")[["shortfall", "random_minus_patient"]].mean().reset_index())
        rows.append(dict(level="task_encoder_averaged", task=task, label_set=ls,
                         encoder="MEAN_OVER_3_R7_ENCODERS", n_genes=int(len(m)),
                         spearman=_spearman(m.shortfall, m.random_minus_patient),
                         mean_shortfall=float(m.shortfall.mean()),
                         mean_random_minus_patient=float(m.random_minus_patient.mean()),
                         note="encoders averaged within a gene first"))
    return pd.DataFrame(rows).sort_values(["level", "task", "encoder"]).reset_index(drop=True)


def _cmdline():
    """The command line, with the multi-line --job-facts block elided: it is printed in full
    in its own PROVENANCE section, and inlining it here would wrap the field."""
    parts = []
    for a in [sys.executable] + sys.argv:
        parts.append("<--job-facts block, printed below>"
                     if ("\n" in a or " " in a) else a)
    return " ".join(parts)


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _provenance(args, out, repo, a1, anchor, gene_note, A, D, W, J, gp):
    cfg = dict(stage="round3_A2_anatomy", nominal_coverage=NOMINAL,
               script="code/scripts/round3_a2_anatomy.py",
               encoders=ENCODERS, runs=RUNS, scores=["abs", "scaled"],
               a1_dir="results/round3/A1_coverage",
               aggregation="per test slide, then over genes, then over repeats and "
                           "calibration draws inside a fold, then over folds",
               strata=sorted(A.stratum.unique().tolist()),
               r7="results/round2/R7_pergene/r7_pergene_decomposition.csv",
               benchmark="results/summary/results_encoder.csv head=pca_ridge "
                         "column=avg_paper9",
               seed_source="zlib.crc32 (no randomness used in this stage)")
    blob = json.dumps(cfg, sort_keys=True)
    ch = hashlib.sha256(blob.encode()).hexdigest()[:16]
    crc = format(zlib.crc32(blob.encode()) & 0xFFFFFFFF, "08x")
    try:
        commit = subprocess.run(["git", "-C", repo, "rev-parse", "HEAD"],
                                capture_output=True, text=True, check=True).stdout.strip()
    except Exception as e:  # pragma: no cover
        commit = f"unavailable ({e})"
    lines = [
        "=" * 78,
        "Round 3, stage A2, Anatomy track",
        "=" * 78,
        f"dir              : {out}",
        "stage            : round3 A2 (conditional coverage), the parts answerable from A1's",
        "                   committed outputs without rerunning the harness",
        "track            : Anatomy (docs/round3_execution_plan.md section 12.8)",
        "spec             : memo section 4.1 = plan section 12.4; original A2 = plan 4.4",
        "script           : code/scripts/round3_a2_anatomy.py",
        f"created          : {dt.datetime.now().astimezone().isoformat()}",
        "operator         : weiyang (Nicolas Weiyang Zhang)",
        f"repo_commit      : {commit}",
        # --job-facts is a multi-line block; it is printed in full in its own section below,
        # so the command line records only that it was supplied.
        f"command_line     : {_cmdline()}",
        f"pythonhashseed   : {os.environ.get('PYTHONHASHSEED', 'UNSET')}",
        f"platform         : {platform.platform()}",
        f"python           : {platform.python_version()}",
        f"numpy/pandas     : {np.__version__} / {pd.__version__}",
        f"config_hash      : sha256/16 {ch} crc32 {crc}",
        f"config           : {blob}",
        "",
        "LOCAL MODE. No Slurm job; the local clone's A1 CSVs are the whole input except the",
        "gene stratum and the R7 join, which need A1's per-gene parquets. Those are gitignored",
        "and exist only on Longleaf, so they were collapsed there by this same script in",
        "--mode gene inside a Slurm job, and only the collapsed table was brought back.",
        "",
        "LONGLEAF JOB (the gene mode) --------------------------------------------------",
    ]
    jf = args.job_facts
    lines += [f"  {ln}" for ln in (jf.splitlines() if jf else
                                   ["not supplied on the command line"])]
    lines += [
        "",
        "INPUTS -----------------------------------------------------------------------",
        f"  a1_dir                : {a1}",
        "  a1 files read         : a1_by_slide__<enc>__{main,slideout}.csv,",
        "                          a1_by_fold__..., a1_by_task__...,",
        "                          a1_calibration_units__... for 12 encoders",
        "  task definitions      : results/round3/task_defs/*.json (11 task files)",
        "  r7                    : results/round2/R7_pergene/r7_pergene_decomposition.csv",
        "  benchmark pearson     : results/summary/results_encoder.csv, head pca_ridge,",
        "                          column avg_paper9",
        f"  gene table            : {gp if gp else 'none'}",
        f"  gene table sha256     : {_sha(gp) if gp and os.path.exists(gp) else 'n/a'}",
        f"  gene table note       : {gene_note}",
        "",
        "ANCHOR TO A1 -----------------------------------------------------------------",
        "  a1_by_slide collapsed to the cell level, then over folds, must reproduce",
        "  a1_by_fold's coverage and width for every fold.",
        f"  n_folds {anchor['n_folds']}, max |dcoverage| {anchor['max_abs_dcoverage']:.3e}, "
        f"max |dwidth| {anchor['max_abs_dwidth']:.3e}, tolerance {anchor['tolerance']:.0e}, "
        f"passed {anchor['passed']}",
        "",
        "OUTPUTS ----------------------------------------------------------------------",
        f"  a2_by_stratum__anatomy.csv        {len(A)} rows, "
        f"{A.stratum.nunique()} strata: {', '.join(sorted(A.stratum.unique()))}",
        f"  a2_prad_donor_sharing__paired.csv {len(D)} rows "
        f"({int((D.level == 'pair').sum())} pairs, "
        f"{int((D.level == 'summary').sum())} summary rows)",
        f"  a2_width_by_encoder.csv           {len(W)} rows",
        f"  a2_pergene_join.csv               {len(J)} rows",
        "  PROVENANCE__anatomy.txt           this file",
        "",
        "  a2_by_stratum__anatomy.csv carries two columns beyond the six the task names:",
        "  `label_set`, because IDC appears twice (shipped and audited) under the same task",
        "  name, and `detail`, which is where the PRAD-by-fold rows write out the held-out",
        "  patient, the calibration slides and their K, the session structure of each side",
        "  and the resolution class of each side. `agg_unit` names the unit each row",
        "  aggregated over. A row's n_cells counts units pooled OVER THE 12 ENCODERS, and",
        "  coverage_sd is a dispersion across those units, not a standard error.",
        "",
        "DIFFERENCE LISTS ------------------------------------------------------------",
        "  Written out before any stratum here is named as a term, per the project rule.",
        "",
        "  n_cal_units_K. K covaries with `calibration_unit`. The folds with the largest K",
        "  are the block-calibrated folds of the two-sample tasks (HCC, LUNG, SKCM, COAD),",
        "  where calibration scores are within-slide residuals, so a K contrast pooled over",
        "  calibration units is also a within-slide-against-new-slide contrast. Every K row",
        "  names its calibration unit in `detail`; read K within a unit, not across units.",
        "  Under `random` the unit is the spot, so K there is the calibration SPOT count.",
        "",
        "  cal_shares_session_with_test. The harness defines it as (shares resolution_group)",
        "  OR (shares exact session). `session` is recorded only for PRAD's patient-2 slides,",
        "  so for the other ten task files this column IS the resolution-group flag and is",
        "  not a session contrast. Both halves are in `detail`.",
        "",
        "  resolution_group and session. Both are properties of the test slide, so within a",
        "  task file a resolution_group contrast is also a slide contrast, and in CCRCC and",
        "  PRAD a donor contrast as well. Across task files it is additionally an organ,",
        "  technology and study contrast. Rows are per (task, label_set, design, score), so",
        "  the task is fixed inside a row and free across rows.",
        "",
        "  donor_label_status. A property of the test slide's donor label, from",
        "  results/round2/R5b_audit/donor_audit.csv by way of the task definitions. It is",
        "  confounded with task: `contradicted` occurs only where the audit contradicted",
        "  HEST's label, `unverifiable` only where it could not be checked, so the arms also",
        "  differ in organ, study and slide count.",
        "",
        "  prad_fold. The two folds differ in held-out donor, in K (4 against 2), in the",
        "  session structure and resolution class of both sides, and in the calibration",
        "  slides' pixel-size spread. Every one of those is written into the row's `detail`.",
        "",
        "  A2d's paired donor-sharing arms. The full list is in the docstring of",
        "  `_prad_donor_sharing` in this script and is reproduced in the stage report: donor",
        "  sharing, resolution class, whether session is recorded at all, and the identity",
        "  and spot count of the calibration slides. Held fixed: task, encoder, test slide,",
        "  design, proper-training set, K and score.",
        "",
        "NOT COMPUTED HERE (Mechanisms track, needs a harness rerun) -------------------",
        "  A2a's predicted-value decile and neoplastic-fraction strata; A2b; A2c; A2d's",
        "  `slide_out_cal_other_donor` arm; A2f's level-versus-scale decomposition;",
        "  fig_a2_anatomy.png and fig_a2_coverage_vs_K.png. Also not computed: the",
        "  between-unit score share that the memo's prediction 3 pairs with the PRAD fold",
        "  comparison, which A2c writes.",
        "=" * 78,
    ]
    with open(f"{out}/PROVENANCE__anatomy.txt", "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"[write] PROVENANCE__anatomy.txt", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["gene", "local"], required=True)
    ap.add_argument("--a1-dir", default="results/round3/A1_coverage")
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--gene-dir", default=None)
    ap.add_argument("--out-dir", default="results/round3/A2_conditional")
    ap.add_argument("--job-facts", default=None,
                    help="text block describing the Longleaf gene-mode job, copied verbatim "
                         "into PROVENANCE__anatomy.txt")
    args = ap.parse_args()
    return mode_gene(args) if args.mode == "gene" else mode_local(args)


if __name__ == "__main__":
    sys.exit(main())
