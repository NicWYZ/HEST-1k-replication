#!/usr/bin/env python
"""Give every results/round2/ stage a directory-level PROVENANCE.txt, and retire
the three duplicate file pairs.

Stage: closeout repository refresh (deck_figures_and_repo_update.md sections 2.3).

Run with --apply to make changes; without it, prints what it would do. Nothing is
deleted: a retired file is MOVED to a `superseded/` subdirectory inside its own
stage directory, so a citation that breaks is recoverable by path rather than
from git history.

The three pairs, each decided by reading the files rather than by their names:

  R3_splits/replicate_leak__*.csv  vs  replicate_leak_v2__*.csv
      Identical columns and identical designs. v1 covers IDC only (TENX95,
      TENX99, 20 rows per encoder); v2 covers IDC and READ (all six slides, 60
      rows). v2 is the same experiment extended, so v1 is superseded. Note that
      the CITATION in docs/hest_bench_issue_draft.md points at v1, and is
      corrected as part of this change: a path pointing at the narrower file
      would understate the evidence.

  R6_variance/donor_variance_components.csv  vs  r6_donor_variance_components.csv
      Byte-for-byte the same numbers; they differ only in how many significant
      digits were written (16 against 15). The r6_ prefix matches every other
      file in that directory, so the unprefixed copy is superseded.

  R7_pergene/pergene_{correlations,decomposition}.csv  vs  r7_*
      Same: decomposition is byte-identical, correlations differ only in the last
      written digit. The r7_ prefix matches the rest of the stage.

Provenance text is assembled per stage from a table below rather than scraped,
because the memo clause and the script that produced each stage are not
recoverable from the files themselves.
"""
import hashlib
import os
import subprocess
import sys

ROOT = os.environ.get("HEST_ROOT", "/work/users/w/e/weiyang/hest_replication")
APPLY = "--apply" in sys.argv

# stage -> (title, memo clause, scripts, what distinguishes files that look alike)
STAGES = {
    "R0_resolution": (
        "Scan-resolution columns",
        "round2_execution_plan.md stage R0 item 2",
        ["code/scripts/round2_r0_resolution_columns.py"],
        "",
    ),
    "R1_intercept": (
        "Intercept refit, float32 families only (11 encoders)",
        "round2_execution_plan.md stage R1",
        ["code/scripts/round2_head_intercept.py"],
        "Superseded by R1b_heads, which covers 12 encoders and three solver "
        "families. Kept as the record reported at the R1 gate.",
    ),
    "R1b_heads": (
        "Intercept refit including the float64 exact-solver head (12 encoders)",
        "round2_R1_decisions.md Decision 1 and Decision 2",
        ["code/scripts/round2_r1b_heads.py",
         "code/scripts/round2_r1b_ladder.py",
         "code/scripts/build_r1b_ladder_by_encoder.py"],
        "head_intercept__<encoder>.csv holds the two FLOAT32 families; "
        "head_intercept__<encoder>__f64.csv holds the float64 family and is the "
        "one the ladder and every Topic A quantity are built from. The "
        "unsuffixed files also contain a superseded float64 arm from the first "
        "pass, which was built on float32-derived features and must not be used; "
        "see the commit that added the family argument.",
    ),
    "R2_fold_hvg": (
        "Gene-selection reproduction and per-fold training-only selection",
        "round2_R1_decisions.md directive D2 and round2_execution_plan.md stage R2",
        ["code/scripts/round2_r2_gene_check.py",
         "code/scripts/round2_r2_fold_hvg.py",
         "code/scripts/round2_r2_rank_supplement.py"],
        "r2_leakage_summary.csv measures the SELECTION effect (which genes); "
        "r2_rank_supplement.csv isolates the RANKING effect on a fixed gene set. "
        "They answer different questions and both are current.",
    ),
    "R3_splits": (
        "Five split designs, buffered blocks, leave-one-slide-out",
        "round2_execution_plan.md stage R3",
        ["code/scripts/round2_split_v4.py"],
        "replicate_leak_v2__<encoder>.csv is the current file: IDC and READ, six "
        "slides. replicate_leak__<encoder>.csv covered IDC only and is under "
        "superseded/.",
    ),
    "R4_probes": (
        "Slide, session, resolution and composition-adjusted probes",
        "round2_R3_decisions.md decision 2.1 and directives 2.2 to 2.4",
        ["code/scripts/round2_r4_probes.py"],
        "probes_v2__hoptimus0.csv holds ALL THREE encoders: the script names its "
        "output after its first argument but accumulates every encoder it was "
        "given.",
    ),
    "R5b_audit": (
        "Donor provenance audit of all 72 samples against sources outside HEST",
        "round2_R5_decisions.md decision 1.2 and directive 2.1",
        ["(no single producing script: a source-reading task, not a computation)"],
        "THERE IS NO round2_r5b_audit.py. This stage was a reading task -- vendor "
        "dataset pages, GEO subseries strings and the upstream issue tracker -- "
        "so it has no one script to rerun, and an earlier version of this file "
        "named a script that does not exist. What makes it reproducible instead: "
        "hest_source_map.csv is the per-sample source mapping extracted from "
        "HEST's own HEST_v1_1_0.csv (column download_page_link1), donor_audit.csv "
        "carries one row per sample with donor_id, donor_label_status and a "
        "donor_statement giving the evidence for that row, and the two evidence "
        "files are verbatim captures of upstream issues 126 and 133 read through "
        "the GitHub API. Nine samples are recorded as unverifiable rather than "
        "inferred. docs/r5_idc_provenance.md is the narrative companion. "
        "donor_id is the grouping variable R6 and R7 use, so a change here "
        "changes those stages.",
    ),
    "R5c_leak": (
        "Replicate leak generalised to every known same-donor pair",
        "round2_R5_decisions.md directive 2.2",
        ["code/scripts/round2_r5c_replicate_leak.py",
         "code/scripts/round2_r5d_confusion.py"],
        "r5c_leak_summary.csv carries leak_realised_in_shipped_split, which is "
        "the distinction that matters: IDC's folds split its pair so the leak is "
        "realised in the published benchmark, READ's folds group each pair so "
        "READ's figure is a counterfactual.",
    ),
    "R6_theta": (
        "Slide-level estimand theta1 and its spot bootstrap",
        "round2_R5_decisions.md directive 2.4",
        ["code/scripts/round2_r6_theta.py",
         "code/scripts/build_r6_theta_bootstrap.py"],
        "theta_by_slide.parquet carries the point estimates and analytic "
        "standard errors; r6_theta_bootstrap_ci.csv adds percentile intervals "
        "from the same resampling, verified to reproduce those standard errors.",
    ),
    "R6_variance": (
        "Nested variance components on the audited donor labels",
        "round2_R5_decisions.md directive 2.3",
        ["code/scripts/round2_r6_donor_variance.py"],
        "r6_variance_by_task.csv is the per-task summary; "
        "r6_donor_variance_components.csv is the per-gene detail behind it. "
        "r6_pooled_between_donor.csv records THREE pooled definitions, because "
        "the directive's own definition mixes a well-determined component with "
        "an uninformative zero.",
    ),
    "R7_pergene": (
        "Per-gene decomposition: does the split penalty track donor biology",
        "round2_R5_decisions.md directive 2.5",
        ["code/scripts/round2_r7_pergene.py"],
        "r7_correlations_task_centred.csv is the file to read: the pooled "
        "correlations in r7_pergene_correlations.csv are confounded by task, and "
        "the within-task column is the estimate.",
    ),
    "R8_raw_heads": (
        "H-Optimus-1 on the raw-embedding heads, and the width correlations",
        "round2_R5_decisions.md directive 2.5 / execution plan stage R8",
        ["code/configs/raw_ridge__hoptimus1.yaml",
         "code/scripts/build_deck_numbers.py"],
        "r8_width_correlations.csv carries TWO cohorts: the 11-encoder one is "
        "round 1's, before H-Optimus-1 had raw-head cells, and the 12-encoder "
        "one is round 2's. Quoting either without naming the cohort is how the "
        "two documents came to disagree.",
    ),
}

RETIRE = {
    "R3_splits": ([f"replicate_leak__{e}.csv" for e in ("hoptimus0", "resnet50", "uni_v2")],
                  "covered IDC only; replicate_leak_v2__*.csv is the same design "
                  "extended to READ"),
    "R6_variance": (["donor_variance_components.csv"],
                    "byte-identical to r6_donor_variance_components.csv apart from "
                    "one fewer written significant digit"),
    "R7_pergene": (["pergene_correlations.csv", "pergene_decomposition.csv"],
                   "identical to the r7_-prefixed files apart from written precision"),
}


def _wrap(text, width=74):
    """Hard-wrap a note so PROVENANCE.txt stays readable in a terminal."""
    words, out, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width:
            out.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        out.append(cur)
    return out


def sha(path, n=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while (b := f.read(n)):
            h.update(b)
    return h.hexdigest()[:16]


def git(*a):
    return subprocess.run(["git", "-C", ROOT, *a], capture_output=True, text=True).stdout.strip()


commit = git("rev-parse", "HEAD")
moved, written = [], []

for stage, (title, clause, scripts, note) in STAGES.items():
    d = f"{ROOT}/results/round2/{stage}"
    if not os.path.isdir(d):
        print(f"[skip] {stage}: directory absent")
        continue

    # retire first, so the provenance file lists what is actually there
    if stage in RETIRE:
        files, why = RETIRE[stage]
        sup = f"{d}/superseded"
        for fn in files:
            src = f"{d}/{fn}"
            if not os.path.exists(src):
                continue
            if APPLY:
                os.makedirs(sup, exist_ok=True)
                os.replace(src, f"{sup}/{fn}")
            moved.append((stage, fn, why))
        if APPLY and os.path.isdir(sup):
            with open(f"{sup}/README.txt", "w") as f:
                f.write(f"Superseded outputs of stage {stage}.\n\n{why}.\n\n"
                        "Kept rather than deleted so a citation that breaks is "
                        "recoverable by path. Nothing here should be read as a "
                        "current result.\n")

    present = sorted(x for x in os.listdir(d)
                     if os.path.isfile(f"{d}/{x}") and not x.startswith("PROVENANCE"))
    per_enc = sorted(x for x in os.listdir(d) if x.startswith("PROVENANCE__"))

    lines = [f"Round 2, stage {stage} — {title}", "",
             f"memo clause     : {clause}",
             f"repo_commit     : {commit}",
             f"scripts         : {', '.join(scripts)}",
             f"files           : {len(present)}",
             f"per-run provenance: {len(per_enc)} PROVENANCE__* files in this directory"
             if per_enc else "per-run provenance: none (single-run stage)"]
    if note:
        lines += ["", "What distinguishes files that look alike:", ""]
        lines += ["  " + l for l in _wrap(note)]
    if stage in RETIRE:
        lines += ["", "Retired to superseded/:", ""]
        lines += [f"  {fn}" for fn in RETIRE[stage][0] if fn in
                  (os.listdir(f"{d}/superseded") if os.path.isdir(f"{d}/superseded") else [])]
    lines += ["", "Files and checksums (sha256, first 16 hex):", ""]
    for fn in present:
        p = f"{d}/{fn}"
        lines.append(f"  {sha(p)}  {os.path.getsize(p):>12,}  {fn}")
    lines += ["", "plan            : deck_figures_and_repo_update.md section 2.3", ""]

    if APPLY:
        with open(f"{d}/PROVENANCE.txt", "w") as f:
            f.write("\n".join(lines))
    written.append((stage, len(present)))

print(f"{'APPLIED' if APPLY else 'DRY RUN'}")
print(f"\nPROVENANCE.txt for {len(written)} stages:")
for s, n in written:
    print(f"  {s:<16} {n:>3} files")
print(f"\nretired {len(moved)} files to superseded/:")
for s, fn, why in moved:
    print(f"  {s}/{fn}")
    print(f"      {why}")
