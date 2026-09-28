#!/usr/bin/env python
"""Round 4, stage P, P6: training-only gene lists for the Visium tasks.

Stage: P6 (docs/round4_data_plan.md section 3 P6, transcribing docs/decisions/round4_data_pull.md
section 6 P6, with section 7 items 5 and 6).

WHAT THIS SCRIPT DOES NOT DO. It does not edit, copy or re-implement any round-2 or round-3 code,
and it writes nothing into any round-2 or round-3 output directory.

  * HEST's own gene selection is `round2_r2_gene_check.get_k_genes`, criteria='var',
    min_cells_pct=0.10, imported unmodified via `round3_d4_sets` (which imports it the same way).
  * The Indiana per-fold reproduction check is `round3_d4_sets.run_genes` itself, called
    unmodified with its `out` argument pointed at this stage's own directory, so the round-3
    file `results/round3/D4_expansion/d4_fold_genes__INDIANA_KIDNEY.json` is never touched.
  * Indiana's spot material and panel handling are `round3_d4_sets.patched_barcodes` and
    `round3_d4_sets.raw_patched_adata`, unmodified.
  * Fold enumeration follows `round3_a0_harness.build_fold_specs` (md5
    0ad7ae8efe554c1f285e5f384a9fb7f5) for the general-design branch: `folds[design]` in
    task-definition order, E = the fold's test samples, pool = the fold's train samples,
    train/test overlap asserted, a fold with no spots on either side skipped and reported.

FOLDS. The `donor` design only, which is leave-one-donor-out; a donor with two slides holds out
both, so a fold's training sample count is not always n_samples - 1.

SELECTION, and what "on the training samples only" is taken to mean, stated before the run. Per
fold and per size k in (50, 200, 500):

  1. get_k_genes(the fold's TRAINING samples, k=k) -> `raw`, the benchmark's own top-k, plus
     n_common, the min_cells-filtered gene intersection over those training samples.
  2. genes off the fold's presence panel are DROPPED, as round 2's R2 did and as round 3's D4
     did, and the number dropped is recorded per fold and per size. A fold that ends with fewer
     than k genes is reported with its count and never topped up. This is the step P6's
     acceptance ("every selected gene is present on every sample of its fold's training AND test
     sets") and prediction 4 ("drop below 500 present genes") both turn on.
  3. The presence panel is the intersection of `var_names` over every sample of the fold's
     training AND test sets, which for a leave-one-donor-out design is every sample of the task.
     `var_names`, not the min_cells-filtered set: presence is whether the sample's file can
     report the gene at all, which is round 2's PANEL_ALL and round 3 D4's candidate panel.

ORDER, and therefore what `rank` means. get_k_genes returns `var_names[highly_variable][:k]`
over the SORTED common-gene intersection (np.intersect1d sorts), so the benchmark's own emitted
order is alphabetical-after-intersection, not variance-ranked. `rank` is the 1-based position in
that emitted order, restricted to the genes kept at step 2 and renumbered contiguously. It is
the benchmark's order, and it is not a variance ranking; the variance ranking is only the
membership of the set. The k=50 set is a subset of the k=200 set and that of the k=500 set,
because scanpy flags the top n_top_genes of one dispersion ranking.

SPOT MATERIAL differs between the two arms, and this is not a choice made here: each arm keeps
the material its own reproduction check runs on.
  benchmark tasks  every spot of `bench_data/<task>/adata/<sample>.h5ad`, which is the spot set
                   round 2's R2 reproduced the shipped 50-gene lists on.
  INDIANA_KIDNEY   the patched spots only (the embedding files' barcode lists), which is the
                   spot set round 3's D4 selected on and the one this stage must reproduce.

STAGES.
  --stage check  the gate. For each benchmark task, get_k_genes on ALL samples must reproduce
                 the shipped var_50genes.json exactly, set AND order. For INDIANA_KIDNEY, which
                 has no shipped list (plan section 7 item 5), round3_d4_sets.run_genes must
                 reproduce d4_indiana_fold_genes.csv. Also records the intersection panel of
                 every benchmark Xenium task and of the breast Xenium expansion set, where gene
                 selection IS the panel (plan section 7 item 6).
  --stage lists  the per-fold lists at 50, 200 and 500. Refuses to run unless the check stage's
                 verdict files are present in the output directory and passing.
  --stage verify P6's acceptance, re-checked from the WRITTEN outputs and the samples' own
                 `var_names` only, so it shares no code path with the selection: every gene of
                 every list against every sample of its fold's training AND test sets, rank
                 contiguity, parquet against CSV, and no empty list at any size. Also merges the
                 per-job summary fragments into p6_gene_summary.csv, reporting collisions.

Outputs under results/round4/data/P6_genes/, summaries before bulk tables:
  p6_check_reproduction.csv, p6_check_indiana_folds.csv, p6_check_verdict.json
  p6_acceptance.csv, p6_verify_verdict.json, p6_gene_summary.csv (merged from the fragments)
  p6_xenium_panels.csv, p6_xenium_panel_genes.csv
  p6_gene_summary__<tag>.csv           one fragment per lists job; the lead merges
  genes__<task>__<size>.csv            the repository copy
  genes__<task>__<size>.parquet        explicit pa.schema, stays on Longleaf
  PROVENANCE.txt, PROVENANCE__p6_<stage>_<tag>.txt

Usage:
  round4_data_p6_genes.py --stage check --out <dir>
  round4_data_p6_genes.py --stage lists --tasks CCRCC --out <dir> --tag ccrcc
  round4_data_p6_genes.py --stage verify --out <dir>
"""
import argparse
import hashlib
import importlib.util
import json
import os
import sys
import time

import anndata as ad
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import scanpy as sc

# The round-3 modules are imported from the repository's own code/scripts, unmodified and in
# place. `R4_SCRIPTS_DIR` exists so that this script can run from a job workdir without being
# copied into the repository tree (the Longleaf working copy is pull-only this stage, and an
# untracked file at a path the lead is about to commit would block its next pull).
_HERE = os.environ.get("R4_SCRIPTS_DIR") or os.path.dirname(os.path.abspath(__file__))


def _mod(name):
    """round3_d4_sets.py's own loader, so the round-3 modules are imported exactly as round 3
    imports them: by file, from code/scripts, unmodified."""
    spec = importlib.util.spec_from_file_location(name, os.path.join(_HERE, f"{name}.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


D4 = _mod("round3_d4_sets")          # imports round3_a0_harness, round3_a3_weighted, round2_r2_gene_check
H = D4.H                             # the frozen harness
GC = D4.GC                           # round2_r2_gene_check, holding get_k_genes

ROOT = H.ROOT
SIZES = (50, 200, 500)
BENCH_TASKS = ("CCRCC", "PRAD", "READ", "LYMPH_IDC", "HCC")
XENIUM_BENCH = ("IDC", "PAAD", "SKCM", "COAD", "LUNG")
EXT_TASKS = ("INDIANA_KIDNEY",)          # the P6 Visium tasks that are expansion sets
# every task definition that lives under the D4 directory rather than results/round3/task_defs
EXT_TD_NAMES = ("INDIANA_KIDNEY", "KIDNEY_POP54", "BREAST_XENIUM", "CCRCC_hest_layout")
TD_BENCH = f"{ROOT}/results/round3/task_defs"
TD_EXT = f"{ROOT}/results/round3/D4_expansion/task_defs"
BREAST_ST = f"{ROOT}/hest_ext/institution_breast_xenium/st"
D4_INDIANA_CSV = f"{ROOT}/results/round3/D4_expansion/d4_indiana_fold_genes.csv"
ENCODERS = ("hoptimus0", "uni_v2", "resnet50")

# Expected values, read from committed round-2/round-3 records before this ran, so that every
# check compares against a number rather than against nothing. Sources:
#   results/round2/R2_fold_hvg/r2_panel_heterogeneity.csv   (panel_intersection)
#   results/round2/R2_fold_hvg/d2_reproduction_check__adata.csv (n_common_genes, all samples)
EXPECT_PANEL = {"CCRCC": 17943, "PRAD": 33538, "READ": 36601, "HCC": 36601, "LYMPH_IDC": 33931,
                "IDC": 500, "PAAD": 159, "SKCM": 343, "COAD": 412, "LUNG": 259}
EXPECT_COMMON_ALL = {"CCRCC": 2248, "PRAD": 1228, "READ": 8828, "HCC": 9940, "LYMPH_IDC": 10276}


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def load_td(task):
    p = f"{TD_EXT}/{task}.json" if task in EXT_TD_NAMES else f"{TD_BENCH}/{task}.json"
    return json.load(open(p)), p


def bench_material(td):
    """Every spot of the benchmark adata, per sample, in sorted sample order (load_task's order).
    Returns {sid: AnnData(raw)} and {sid: set(var_names)}."""
    ids = sorted(s["sample_id"] for s in td["samples"])
    ads, panel = {}, {}
    for sid in ids:
        A = sc.read_h5ad(f"{ROOT}/{td['paths']['adata'].format(sample_id=sid)}")
        ads[sid] = A
        panel[sid] = set(map(str, A.var_names))
    return ids, ads, panel


def ext_material(td):
    """INDIANA_KIDNEY's material: the patched spots, via round3_d4_sets unmodified."""
    ids = sorted(s["sample_id"] for s in td["samples"])
    bc_of = {}
    for sid in ids:
        lists = []
        for enc in ENCODERS:
            b, _, _ = D4.patched_barcodes(td, sid, enc)
            lists.append(b)
        assert lists[0] == lists[1] == lists[2], f"{sid}: encoders disagree on the patch list"
        bc_of[sid] = lists[0]
    ads, panel = {}, {}
    for sid in ids:
        A = D4.raw_patched_adata(td, sid, bc_of[sid])
        ads[sid] = A
        panel[sid] = set(map(str, A.var_names))
    return ids, ads, panel


def donor_folds(td, ads):
    """The `donor` design folds, enumerated as round3_a0_harness.build_fold_specs enumerates the
    general-design branch: task-definition order; E the test samples, pool the train samples;
    train/test overlap asserted; a fold with no spots on either side skipped and reported."""
    task = td["task"]
    out, skipped = [], []
    for fd in td["folds"]["donor"]:
        train = [s for s in fd["train"]]
        test = [s for s in fd["test"]]
        assert not (set(train) & set(test)), f"{task} donor {fd['fold']}: train/test overlap"
        n_tr = sum(int(ads[s].n_obs) for s in train if s in ads)
        n_te = sum(int(ads[s].n_obs) for s in test if s in ads)
        if n_te == 0 or n_tr == 0:
            skipped.append(dict(fold=str(fd["fold"]), n_train_spots=n_tr, n_test_spots=n_te))
            print(f"  [skip] {task} donor fold={fd['fold']}: n_train_spots={n_tr} "
                  f"n_test_spots={n_te}", flush=True)
            continue
        out.append(dict(fold=str(fd["fold"]), train=sorted(train), test=sorted(test),
                        n_train_spots=n_tr, n_test_spots=n_te))
    return out, skipped


# ------------------------------------------------------------------------------ check stage
def stage_check(out):
    os.makedirs(out, exist_ok=True)
    t_all = time.time()

    # --- 1. the benchmark reproduction gate -------------------------------------------------
    rows = []
    for task in BENCH_TASKS:
        td, tdp = load_td(task)
        t0 = time.time()
        ids, ads, panel = bench_material(td)
        shipped_path = f"{ROOT}/{td['paths']['target_genes']}"
        shipped = list(json.load(open(shipped_path))["genes"])
        assert list(td["target_genes"]["list"]) == shipped, \
            f"{task}: task definition gene list disagrees with {shipped_path}"
        got, n_common = GC.get_k_genes([ads[s] for s in ids], k=50)
        panel_all = set.intersection(*[panel[s] for s in ids])
        row = dict(task=task, st_technology=td["st_technology"], spot_set="adata",
                   n_samples=len(ids), n_spots_total=sum(int(ads[s].n_obs) for s in ids),
                   n_common_genes=int(n_common),
                   n_common_genes_expected=EXPECT_COMMON_ALL[task],
                   panel_intersection=len(panel_all),
                   panel_intersection_expected=EXPECT_PANEL[task],
                   panel_min=min(len(panel[s]) for s in ids),
                   panel_max=max(len(panel[s]) for s in ids),
                   n_shipped=len(shipped), n_reproduced=len(got),
                   n_intersect=len(set(got) & set(shipped)),
                   set_equal=bool(set(got) == set(shipped)), order_equal=bool(got == shipped),
                   shipped_all_present=bool(all(g in panel_all for g in shipped)),
                   missing=";".join(sorted(set(shipped) - set(got))),
                   extra=";".join(sorted(set(got) - set(shipped))),
                   task_def=os.path.relpath(tdp, ROOT), seconds=round(time.time() - t0, 1))
        rows.append(row)
        print(f"[{task}] {len(ids)} samples, {row['n_spots_total']:,} spots, common "
              f"{n_common} (expected {EXPECT_COMMON_ALL[task]}), panel_intersection "
              f"{len(panel_all)} (expected {EXPECT_PANEL[task]}) -> set_equal={row['set_equal']} "
              f"order_equal={row['order_equal']}  [{row['seconds']}s]", flush=True)
        if not row["order_equal"]:
            print(f"    missing {row['missing']}\n    extra {row['extra']}", flush=True)
        del ads, panel
    rep = pd.DataFrame(rows)
    rep.to_csv(f"{out}/p6_check_reproduction.csv", index=False)
    print(f"[write] {out}/p6_check_reproduction.csv  exact {int(rep.order_equal.sum())}/{len(rep)}",
          flush=True)

    # --- 2. the Xenium intersection panels (gene selection there IS the panel) ---------------
    xrows, xgenes = [], []
    for task in XENIUM_BENCH:
        td, _ = load_td(task)
        ids = sorted(s["sample_id"] for s in td["samples"])
        panel = {}
        for sid in ids:
            A = sc.read_h5ad(f"{ROOT}/{td['paths']['adata'].format(sample_id=sid)}")
            panel[sid] = set(map(str, A.var_names))
            del A
        inter = sorted(set.intersection(*[panel[s] for s in ids]))
        union = set().union(*[panel[s] for s in ids])
        shipped = list(td["target_genes"]["list"])
        xrows.append(dict(set_name=task, kind="benchmark_task", source="bench_data",
                          n_samples=len(ids), panel_min=min(len(panel[s]) for s in ids),
                          panel_max=max(len(panel[s]) for s in ids),
                          panel_intersection=len(inter),
                          panel_intersection_expected=EXPECT_PANEL[task],
                          panel_union=len(union),
                          panels_identical=bool(len({frozenset(panel[s]) for s in ids}) == 1),
                          shipped_all_on_intersection=bool(all(g in set(inter) for g in shipped)),
                          note="gene selection is the panel"))
        xgenes += [dict(set_name=task, rank=i + 1, gene=g) for i, g in enumerate(inter)]
        print(f"[xenium {task}] {len(ids)} samples, intersection {len(inter)} "
              f"(expected {EXPECT_PANEL[task]}), union {len(union)}", flush=True)

    tdb, _ = load_td("BREAST_XENIUM") if os.path.exists(f"{TD_EXT}/BREAST_XENIUM.json") else (None, None)
    bids = sorted(f[:-5] for f in os.listdir(BREAST_ST) if f.endswith(".h5ad"))
    bpanel = {}
    for sid in bids:
        A = sc.read_h5ad(f"{BREAST_ST}/{sid}.h5ad")
        bpanel[sid] = set(map(str, A.var_names))
        del A
    binter = sorted(set.intersection(*[bpanel[s] for s in bids]))
    bunion = set().union(*[bpanel[s] for s in bids])
    bexp = int(tdb["target_genes"]["n"]) if tdb else -1
    xrows.append(dict(set_name="BREAST_XENIUM", kind="expansion_set",
                      source="hest_ext/institution_breast_xenium", n_samples=len(bids),
                      panel_min=min(len(bpanel[s]) for s in bids),
                      panel_max=max(len(bpanel[s]) for s in bids),
                      panel_intersection=len(binter), panel_intersection_expected=bexp,
                      panel_union=len(bunion),
                      panels_identical=bool(len({frozenset(bpanel[s]) for s in bids}) == 1),
                      shipped_all_on_intersection=(
                          bool(set(tdb["target_genes"]["list"]) == set(binter)) if tdb else None),
                      note="gene selection is the panel; candidate panel of the D4 task def"))
    xgenes += [dict(set_name="BREAST_XENIUM", rank=i + 1, gene=g) for i, g in enumerate(binter)]
    print(f"[xenium BREAST_XENIUM] {len(bids)} samples, intersection {len(binter)} "
          f"(task-def candidate panel {bexp}), union {len(bunion)}", flush=True)
    pd.DataFrame(xrows).to_csv(f"{out}/p6_xenium_panels.csv", index=False)
    pd.DataFrame(xgenes).to_csv(f"{out}/p6_xenium_panel_genes.csv", index=False)
    print(f"[write] {out}/p6_xenium_panels.csv, {out}/p6_xenium_panel_genes.csv", flush=True)

    # --- 3. INDIANA: round3_d4_sets.run_genes, unmodified, against the shipped D4 CSV -------
    td, _ = load_td("INDIANA_KIDNEY")
    args = D4.HArgs()
    scratch = f"{out}/d4_rerun"
    os.makedirs(scratch, exist_ok=True)
    p = D4.run_genes(td, "indiana", args, (1, 1), scratch)
    mine = json.load(open(p))["selections"]
    ref = pd.read_csv(D4_INDIANA_CSV)
    irows = []
    for _, r in ref.iterrows():
        key = f"{r['design']}|{r['fold']}|{r['repeat']}"
        got = mine.get(key)
        ref_genes = [] if pd.isna(r["genes"]) else str(r["genes"]).split(";")
        g = got["genes"] if got else []
        irows.append(dict(design=r["design"], fold=str(r["fold"]), repeat=int(r["repeat"]),
                          present_in_rerun=bool(got is not None),
                          n_ref=len(ref_genes), n_rerun=len(g),
                          n_intersect=len(set(g) & set(ref_genes)),
                          set_equal=bool(set(g) == set(ref_genes)), order_equal=bool(g == ref_genes),
                          n_common_ref=int(r["n_common_genes"]),
                          n_common_rerun=int(got["n_common_genes"]) if got else -1,
                          common_equal=bool(got is not None
                                            and int(got["n_common_genes"]) == int(r["n_common_genes"])),
                          missing=";".join(sorted(set(ref_genes) - set(g))),
                          extra=";".join(sorted(set(g) - set(ref_genes)))))
    extra_keys = sorted(set(mine) - {f"{r['design']}|{r['fold']}|{r['repeat']}"
                                     for _, r in ref.iterrows()})
    ic = pd.DataFrame(irows)
    ic.to_csv(f"{out}/p6_check_indiana_folds.csv", index=False)
    print(f"[write] {out}/p6_check_indiana_folds.csv  exact {int(ic.order_equal.sum())}/{len(ic)}; "
          f"selections only in the rerun: {extra_keys}", flush=True)

    ok = bool(rep.order_equal.all()) and bool(ic.order_equal.all()) and not extra_keys
    json.dump(dict(stage="check", passed=ok,
                   bench_exact=int(rep.order_equal.sum()), bench_n=len(rep),
                   indiana_exact=int(ic.order_equal.sum()), indiana_n=len(ic),
                   indiana_pool_exact=int(ic[ic.design == "pool"].order_equal.sum()),
                   indiana_pool_n=int((ic.design == "pool").sum()),
                   extra_keys=extra_keys, seconds=round(time.time() - t_all, 1)),
              open(f"{out}/p6_check_verdict.json", "w"), indent=1)
    print(f"\n=== P6 check verdict: passed={ok} "
          f"(benchmark {int(rep.order_equal.sum())}/{len(rep)} exact, "
          f"Indiana {int(ic.order_equal.sum())}/{len(ic)} exact) ===", flush=True)
    return 0 if ok else 5


# ------------------------------------------------------------------------------ lists stage
def gate(out, tasks):
    """The per-fold lists are not trusted, and not written, unless the check stage passed."""
    vp = f"{out}/p6_check_verdict.json"
    assert os.path.exists(vp), f"the check stage has not run: {vp} is missing"
    v = json.load(open(vp))
    assert v["passed"], f"the check stage did not pass: {v}"
    rep = pd.read_csv(f"{out}/p6_check_reproduction.csv")
    for t in tasks:
        if t in BENCH_TASKS:
            r = rep[rep.task == t]
            assert len(r) == 1 and bool(r.order_equal.iloc[0]), \
                f"{t}: the shipped 50-gene list was not reproduced exactly"
        else:
            ic = pd.read_csv(f"{out}/p6_check_indiana_folds.csv")
            assert bool(ic[ic.design == "pool"].order_equal.all()), \
                f"{t}: D4's per-fold lists were not reproduced exactly"
    return v


def stage_lists(out, tasks, tag):
    os.makedirs(out, exist_ok=True)
    v = gate(out, tasks)
    print(f"[gate] check stage passed: {v['bench_exact']}/{v['bench_n']} benchmark, "
          f"{v['indiana_exact']}/{v['indiana_n']} Indiana", flush=True)

    summ, lists, skips = [], {}, []
    for task in tasks:
        td, tdp = load_td(task)
        t0 = time.time()
        if task in EXT_TASKS:
            ids, ads, panel = ext_material(td)
            material = "patched_spots_of_samples"
            cand = set(td["target_genes"]["list"])
            shipped = None
        else:
            ids, ads, panel = bench_material(td)
            material = "all_spots_of_bench_adata"
            cand = None
            shipped = list(td["target_genes"]["list"])
        print(f"[{task}] {len(ids)} samples loaded, material={material}, "
              f"{time.time()-t0:.0f}s", flush=True)

        folds, skipped = donor_folds(td, ads)
        skips += [dict(task=task, **s) for s in skipped]
        assert folds, f"{task}: no usable donor fold"

        for fspec in folds:
            f0 = time.time()
            tr, te = fspec["train"], fspec["test"]
            fold_ids = sorted(set(tr) | set(te))
            present = set.intersection(*[panel[s] for s in fold_ids])
            if cand is not None:
                assert present == cand, (
                    f"{task} {fspec['fold']}: the fold's var_names intersection "
                    f"({len(present)}) is not the task definition's candidate panel ({len(cand)})")
            row = dict(task=task, design="donor", fold=fspec["fold"],
                       st_technology=td["st_technology"], selection_material=material,
                       n_train_samples=len(tr), n_test_samples=len(te),
                       n_train_spots=fspec["n_train_spots"], n_test_spots=fspec["n_test_spots"],
                       panel_min=min(len(panel[s]) for s in fold_ids),
                       panel_max=max(len(panel[s]) for s in fold_ids),
                       panel_union=len(set().union(*[panel[s] for s in fold_ids])),
                       n_present_all_fold_samples=len(present))
            train_ads = [ads[s] for s in tr]
            top50 = None
            for k in SIZES:
                raw, n_common = GC.get_k_genes(train_ads, k=k)
                dropped = [g for g in raw if g not in present]
                kept = [g for g in raw if g in present]
                assert kept, f"{task} {fspec['fold']} k={k}: every selected gene is off panel"
                lists.setdefault((task, k), []).extend(
                    dict(fold=fspec["fold"], rank=i + 1, gene=g) for i, g in enumerate(kept))
                row[f"n_common_genes_{k}"] = int(n_common)
                row[f"n_raw_{k}"] = len(raw)
                row[f"n_selected_{k}"] = len(kept)
                row[f"n_off_panel_{k}"] = len(dropped)
                row[f"genes_off_panel_{k}"] = ";".join(dropped)
                if k == 50:
                    top50 = kept
            assert top50 is not None and 50 in SIZES, "SIZES must contain 50"
            row["overlap_top50_shipped"] = (len(set(top50) & set(shipped))
                                            if shipped is not None else -1)
            row["n_shipped"] = len(shipped) if shipped is not None else -1
            row["shipped_all_present"] = (bool(all(g in present for g in shipped))
                                          if shipped is not None else None)
            row["nested_50_in_200"] = bool(set(
                [d["gene"] for d in lists[(task, 50)] if d["fold"] == fspec["fold"]]).issubset(
                {d["gene"] for d in lists[(task, 200)] if d["fold"] == fspec["fold"]}))
            row["nested_200_in_500"] = bool({
                d["gene"] for d in lists[(task, 200)] if d["fold"] == fspec["fold"]}.issubset(
                {d["gene"] for d in lists[(task, 500)] if d["fold"] == fspec["fold"]}))
            row["seconds"] = round(time.time() - f0, 1)
            summ.append(row)
            print(f"  [{task} {fspec['fold']}] train {len(tr)} samples / "
                  f"{fspec['n_train_spots']:,} spots, present {len(present)}, "
                  f"kept {row['n_selected_50']}/50 {row['n_selected_200']}/200 "
                  f"{row['n_selected_500']}/500, off-panel "
                  f"{row['n_off_panel_50']}/{row['n_off_panel_200']}/{row['n_off_panel_500']}, "
                  f"top50 shares {row['overlap_top50_shipped']} with shipped  "
                  f"[{row['seconds']}s]", flush=True)
        del ads, panel

    # summaries before bulk tables (round-4 convention, plan section 2)
    S = pd.DataFrame(summ)
    S.to_csv(f"{out}/p6_gene_summary__{tag}.csv", index=False)
    print(f"[write] {out}/p6_gene_summary__{tag}.csv ({len(S)} rows)", flush=True)
    if skips:
        pd.DataFrame(skips).to_csv(f"{out}/p6_skipped_folds__{tag}.csv", index=False)

    schema = pa.schema([pa.field("fold", pa.string()), pa.field("rank", pa.int32()),
                        pa.field("gene", pa.string())])
    for (task, k), rws in sorted(lists.items()):
        d = pd.DataFrame(rws)[["fold", "rank", "gene"]]
        d["rank"] = d["rank"].astype("int32")
        d.to_csv(f"{out}/genes__{task}__{k}.csv", index=False)
        pq.write_table(pa.Table.from_pandas(d, schema=schema, preserve_index=False),
                       f"{out}/genes__{task}__{k}.parquet")
        back = pq.read_table(f"{out}/genes__{task}__{k}.parquet")
        assert back.schema.equals(schema) and back.num_rows == len(d), \
            f"genes__{task}__{k}.parquet did not read back as written"
        print(f"[write] genes__{task}__{k}.{{csv,parquet}}: {len(d)} rows, "
              f"{d.fold.nunique()} folds, read-back {back.num_rows} rows", flush=True)

    # acceptance, computed here so the numbers are in the job log as well as the CSV
    print("\n=== P6 lists acceptance ===", flush=True)
    for k in SIZES:
        c = S[f"n_selected_{k}"]
        print(f"  k={k}: folds {len(S)}, empty lists {int((c == 0).sum())}, "
              f"short of k {int((c < k).sum())}, min {int(c.min())}, max {int(c.max())}",
              flush=True)
    b = S[S.overlap_top50_shipped >= 0]
    if len(b):
        print("  top-50 overlap with the shipped 50, by task:", flush=True)
        print(b.groupby("task").overlap_top50_shipped.agg(["size", "mean", "std", "min", "max"])
              .round(2).to_string(), flush=True)
    print(f"  nested 50-in-200 on every fold: {bool(S.nested_50_in_200.all())}; "
          f"200-in-500: {bool(S.nested_200_in_500.all())}", flush=True)
    return 0


# ------------------------------------------------------------------------------ verify stage
def stage_verify(out):
    """Independent re-check of P6's acceptance, reading only the WRITTEN outputs and the
    samples' own `var_names`, so it does not share a code path with the selection. Also merges
    the per-job summary fragments into p6_gene_summary.csv, reporting collisions."""
    import glob
    frags = sorted(glob.glob(f"{out}/p6_gene_summary__*.csv"))
    assert frags, f"no summary fragments in {out}"
    parts = [pd.read_csv(p) for p in frags]
    S = pd.concat(parts, ignore_index=True)
    key = ["task", "design", "fold"]
    dup = S[S.duplicated(key, keep=False)]
    print(f"[merge] {len(frags)} fragments -> {len(S)} rows; collisions on {key}: {len(dup)}",
          flush=True)
    if len(dup):
        print(dup[key].to_string(index=False), flush=True)
    assert len(dup) == 0, "two fragments claim the same (task, design, fold)"
    S = S.sort_values(["task", "fold"]).reset_index(drop=True)
    S.to_csv(f"{out}/p6_gene_summary.csv", index=False)
    print(f"[write] {out}/p6_gene_summary.csv ({len(S)} rows, "
          f"{S.task.nunique()} tasks)", flush=True)

    rows = []
    for task in sorted(S.task.unique()):
        td, _ = load_td(task)
        ids = sorted(s["sample_id"] for s in td["samples"])
        panel = {}
        for sid in ids:
            A = ad.read_h5ad(f"{ROOT}/{td['paths']['adata'].format(sample_id=sid)}", backed="r")
            panel[sid] = set(map(str, A.var_names))
            del A
        fold_of = {str(fd["fold"]): (sorted(fd["train"]), sorted(fd["test"]))
                   for fd in td["folds"]["donor"]}
        for k in SIZES:
            cp = f"{out}/genes__{task}__{k}.csv"
            pp = f"{out}/genes__{task}__{k}.parquet"
            d = pd.read_csv(cp, dtype={"fold": str})
            tb = pq.read_table(pp)
            par = tb.to_pandas()
            par["fold"] = par["fold"].astype(str)
            # compared value by value, not with DataFrame.equals: `rank` is int32 in the parquet
            # (the declared schema) and int64 off the CSV reader, which equals() calls a
            # difference. The declared schema is checked separately, at write time and below.
            same = bool(d["fold"].tolist() == par["fold"].tolist()
                        and [int(x) for x in d["rank"]] == [int(x) for x in par["rank"]]
                        and d["gene"].tolist() == par["gene"].tolist())
            n_checked = n_absent = n_dupgene = 0
            absent = []
            short = []
            for fold, g in d.groupby("fold"):
                tr, te = fold_of[fold]
                genes = g.sort_values("rank").gene.tolist()
                assert list(g.sort_values("rank")["rank"]) == list(range(1, len(genes) + 1)), \
                    f"{task} k={k} fold {fold}: rank is not 1..n contiguous"
                n_dupgene += len(genes) - len(set(genes))
                if len(genes) < k:
                    short.append(f"{fold}:{len(genes)}")
                for sid in tr + te:
                    for gg in genes:
                        n_checked += 1
                        if gg not in panel[sid]:
                            n_absent += 1
                            absent.append(f"{fold}/{sid}/{gg}")
            rows.append(dict(
                task=task, size=k, n_folds=int(d.fold.nunique()), n_rows=len(d),
                n_folds_in_task_def=len(fold_of),
                list_len_min=int(d.groupby("fold").size().min()),
                list_len_max=int(d.groupby("fold").size().max()),
                n_empty_folds=int((d.groupby("fold").size() == 0).sum()),
                n_folds_short_of_k=len(short), folds_short_of_k=";".join(short),
                n_gene_sample_checks=n_checked, n_absent=n_absent,
                absent_examples=";".join(absent[:10]), n_duplicate_genes_in_a_fold=n_dupgene,
                parquet_matches_csv=same,
                parquet_schema_as_declared=bool(tb.schema.equals(pa.schema([
                    pa.field("fold", pa.string()), pa.field("rank", pa.int32()),
                    pa.field("gene", pa.string())]))),
                parquet_schema=str(tb.schema).replace("\n", " ")))
            print(f"  [{task} k={k}] {d.fold.nunique()} folds, {len(d)} rows, "
                  f"{n_checked:,} gene-sample presence checks, absent {n_absent}, "
                  f"short of k {len(short)} {short}, parquet==csv {same}", flush=True)
        del panel
    V = pd.DataFrame(rows)
    V.to_csv(f"{out}/p6_acceptance.csv", index=False)
    # `n_folds_short_of_k` is deliberately NOT part of this gate. P6's acceptance is that no
    # fold's list is EMPTY at any size (plan section 3 P6), and a list shorter than k is the
    # off-panel drop of step 2 working as specified: the fold's training-only top-k named genes
    # the fold's own samples cannot all report, and topping the list back up to k is forbidden.
    # A short fold is therefore a RESULT, not a failure, and it is the evidence prediction 4 is
    # scored against ("the 500-gene lists are present on every sample in every fold on CCRCC and
    # Indiana"). It is named here and in p6_acceptance.csv so it cannot pass unnoticed.
    short_all = sorted({x for s in V.folds_short_of_k if isinstance(s, str) and s
                        for x in s.split(";") if x})
    if short_all:
        print(f"[note] lists shorter than k, by design (off-panel drop, never topped up): "
              f"{short_all}", flush=True)
    ok = bool((V.n_absent == 0).all() and (V.n_empty_folds == 0).all()
              and V.parquet_matches_csv.all() and V.parquet_schema_as_declared.all()
              and (V.n_duplicate_genes_in_a_fold == 0).all())
    print(f"\n=== P6 acceptance ===\n"
          f"  gene-sample presence checks: {int(V.n_gene_sample_checks.sum()):,}, "
          f"absent {int(V.n_absent.sum())}\n"
          f"  folds with an empty list at any size: {int(V.n_empty_folds.sum())}\n"
          f"  files whose parquet and csv disagree: {int((~V.parquet_matches_csv).sum())}\n"
          f"  folds short of k: {int(V.n_folds_short_of_k.sum())} "
          f"({';'.join(x for x in V.folds_short_of_k if x)})\n"
          f"  passed={ok}", flush=True)
    json.dump(dict(stage="verify", passed=ok,
                   n_gene_sample_checks=int(V.n_gene_sample_checks.sum()),
                   n_absent=int(V.n_absent.sum()),
                   n_empty_folds=int(V.n_empty_folds.sum()),
                   n_folds_short_of_k=int(V.n_folds_short_of_k.sum()),
                   folds_short_of_k=short_all,
                   short_of_k_is_a_gate=False,
                   short_of_k_note=("a list shorter than k is the specified off-panel drop, "
                                    "never topped up; it is a result and the evidence "
                                    "prediction 4 is scored against, not an acceptance failure"),
                   n_parquet_csv_mismatches=int((~V.parquet_matches_csv).sum()),
                   n_parquet_schema_mismatches=int((~V.parquet_schema_as_declared).sum()),
                   n_summary_rows=len(S), n_fragments=len(frags)),
              open(f"{out}/p6_verify_verdict.json", "w"), indent=1)
    return 0 if ok else 5


# ------------------------------------------------------------------------------ provenance
def provenance(out, stage, tag, argv, rc):
    cfg = (f"stage={stage} tag={tag} sizes={SIZES} design=donor "
           f"selection=get_k_genes(criteria=var,min_cells_pct={GC.MIN_CELLS_PCT}) "
           f"off_panel=dropped_against_fold_var_names_intersection "
           f"material=bench:all_spots_of_bench_adata|ext:patched_spots_of_samples "
           f"fold_enumeration=round3_a0_harness.build_fold_specs_general_branch "
           f"indiana_check=round3_d4_sets.run_genes_unmodified")
    chash = hashlib.md5(cfg.encode()).hexdigest()[:12]
    me = os.path.abspath(__file__)
    p = f"{out}/PROVENANCE__p6_{stage}_{tag}.txt"
    with open(p, "w") as f:
        f.write(f"Round 4, stage P, P6 ({stage}), tag {tag}\n"
                f"slurm_job_id      : {os.environ.get('SLURM_JOB_ID','NA')}\n"
                f"slurm_partition   : {os.environ.get('SLURM_JOB_PARTITION','NA')}\n"
                f"node              : {os.environ.get('SLURMD_NODENAME','NA')}\n"
                f"date              : {time.strftime('%Y-%m-%dT%H:%M:%S%z')}\n"
                f"repo_commit       : {os.environ.get('R4_COMMIT','NA')} "
                f"(recorded by the job from the environment; no git command is run "
                f"by this stage)\n"
                f"script            : code/scripts/{os.path.basename(me)}\n"
                f"script_md5        : {md5(me)}\n"
                f"imported_md5      : round3_a0_harness {md5(f'{_HERE}/round3_a0_harness.py')}; "
                f"round3_d4_sets {md5(f'{_HERE}/round3_d4_sets.py')}; "
                f"round2_r2_gene_check {md5(f'{_HERE}/round2_r2_gene_check.py')}\n"
                f"command_line      : {' '.join(argv)}\n"
                f"pythonhashseed    : {os.environ.get('PYTHONHASHSEED','unset')}\n"
                f"config_hash       : {chash}\n"
                f"config            : {cfg}\n"
                f"scanpy_version    : {sc.__version__}\n"
                f"pyarrow_version   : {pa.__version__}\n"
                f"numpy_version     : {np.__version__}\n"
                f"exit_code         : {rc}\n"
                f"decisions         : docs/decisions/round4_data_pull.md section 6 P6; "
                f"docs/round4_data_plan.md section 3 P6 and section 7 items 5 and 6; "
                f"docs/decisions/round4_data_P1_decision.md\n")
    print(f"[write] {p} (config_hash {chash})", flush=True)


def main(argv=None):
    argv = list(sys.argv if argv is None else argv)
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=("check", "lists", "verify"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--tasks", default="", help="comma-separated; lists stage only")
    ap.add_argument("--tag", default="", help="fragment tag; lists stage only")
    a = ap.parse_args(argv[1:])
    if a.stage == "check":
        rc = stage_check(a.out)
        provenance(a.out, "check", a.tag or "all", argv, rc)
        return rc
    if a.stage == "verify":
        rc = stage_verify(a.out)
        provenance(a.out, "verify", a.tag or "all", argv, rc)
        return rc
    tasks = [t for t in a.tasks.split(",") if t] or list(BENCH_TASKS) + list(EXT_TASKS)
    for t in tasks:
        assert t in BENCH_TASKS or t in EXT_TASKS, f"unknown task {t}"
    tag = a.tag or "_".join(t.lower() for t in tasks)
    rc = stage_lists(a.out, tasks, tag)
    provenance(a.out, "lists", tag, argv, rc)
    return rc


if __name__ == "__main__":
    sys.exit(main())
