#!/usr/bin/env python
"""Write figures/deck/README.md -- one entry per deck figure.

Stage: deck rendering (deck_figures_and_repo_update.md section 1.1, third rule).

The entry for each figure carries its file name, the CSVs its script reads, the
script itself, a one-line description, and the exact numbers annotated on it.
Those numbers are READ from results/summary/deck_numbers.csv here rather than
copied out of the figures, so the README cannot drift from the figures the way a
hand-maintained caption list does: if a source table changes, rebuilding the
numbers table and re-running this script moves both together.

Each figure declares which deck_numbers rows it annotates, by slide and by an
exact label. A label that no longer exists in the table is an error rather than
a silently omitted line -- that is the whole point of generating the file.
"""
import os
import sys
import time

import pandas as pd

ROOT = os.environ.get("HEST_ROOT", "/work/users/w/e/weiyang/hest_replication")
NUMBERS = f"{ROOT}/results/summary/deck_numbers.csv"
OUT = f"{ROOT}/figures/deck/README.md"

# (file, script, slide, description, sources, [labels annotated on the figure])
FIGS = [
    ("fig01_fidelity", "code/figures/fig01_fidelity.py", 3,
     "Average Pearson over the nine paper tasks per encoder: ours, the paper's "
     "printed Table 1, and the live leaderboard.",
     ["results/summary/results_encoder.csv",
      "results/summary/scaling_law_inputs.csv",
      "results/summary/hest_leaderboard_030426.csv"],
     ["ResNet50 average over the nine paper tasks",
      "H-Optimus-1 average over the nine paper tasks"]),
    ("fig02_replicate_leak", "code/figures/fig02_replicate_leak.py", 4,
     "Per held-out slide, within-slide Pearson with and without the same-donor "
     "partner in a training set of identical size.",
     ["results/round2/R5c_leak/r5c_replicate_leak.csv",
      "results/round2/R5c_leak/r5c_leak_summary.csv"],
     ["IDC replicate leak, mean over encoder-slide cells",
      "IDC encoder-slide cells measured",
      "IDC cells with a positive leak",
      "IDC leak as a share of its random-minus-patient gap",
      "IDC random-minus-patient gap",
      "READ replicate leak, mean over encoder-slide cells",
      "READ encoder-slide cells measured",
      "READ cells with a positive leak"]),
    ("fig03_split_staircase", "code/figures/fig03_split_staircase.py", 5,
     "Additive decomposition of the random-minus-patient gap into nested split "
     "designs, over ten tasks and over the three multi-slide tasks, with the "
     "block-grid sensitivity of the buffered and unbuffered splits.",
     ["results/round2/R3_splits/r3_decomposition_terms.csv",
      "results/round2/R3_splits/r3_per_task_terms.csv",
      "results/round2/R3_splits/split_v4__*.csv",
      "results/summary/results_encoder.csv"],
     ["training-set size term", "spatial adjacency term",
      "residual adjacency term removed only by a buffer",
      "slide-and-patient identity term", "total random-minus-patient gap",
      "novel-slide term", "novel-patient term",
      "between-encoder spread on the benchmark protocol",
      "grid-size spread of the unbuffered blocked split",
      "grid-size spread of the buffered blocked split"]),
    ("fig04_raw_head_width", "code/figures/fig04_raw_head_width.py", 6,
     "Rank on the PCA-256 head against rank on the raw-embedding head, coloured "
     "by embedding width, with the two width correlations annotated.",
     ["results/round2/R8_raw_heads/r8_raw_head_leaderboard.csv",
      "results/round2/R8_raw_heads/r8_width_correlations.csv"],
     ["Spearman(embedding width, score) on the raw ridge head, 12-encoder cohort",
      "Spearman(embedding width, score) on the PCA ridge head, 12-encoder cohort",
      "H-Optimus-1 rank on the PCA-256 head",
      "H-Optimus-1 rank on the raw-embedding head"]),
    ("fig05_r2_ladder", "code/figures/fig05_r2_ladder.py", 9,
     "Four rungs of fold-median R2 for the benchmark head, pooled and per task, "
     "with the prediction-to-target scale ratio per encoder.",
     ["results/round2/R1b_heads/r1b_ladder_pooled.csv",
      "results/round2/R1b_heads/r1b_ladder_by_task.csv",
      "results/round2/R1b_heads/r1b_ladder_by_encoder.csv"],
     ["pooled fold-median R2, head as shipped",
      "pooled fold-median R2 with a training-mean intercept",
      "pooled fold-median R2 with the test fold's own mean",
      "pooled fold-median R2 with an oracle level and optimal scale",
      "prediction-to-target scale ratio, pooled",
      "largest scale ratio (ResNet50)", "smallest scale ratio (UNI2-h)"]),
    ("fig06_session_signature", "code/figures/fig06_session_signature.py", 10,
     "What a linear probe recovers from frozen features inside one PRAD patient, "
     "how much of it is tissue composition, and how much of the measured "
     "expression the same session axis explains.",
     ["results/round2/R4_probes/r4_probes_v2.csv",
      "results/round2/R6_variance/r6_prad_session_variance.csv"],
     ["slide identity probe, lowest of three encoders",
      "slide identity probe, highest of three encoders",
      "slide identity probe chance level",
      "session probe, lowest of three encoders",
      "session probe, highest of three encoders",
      "resolution probe, lowest of three encoders",
      "resolution probe, highest of three encoders",
      "resolution probe majority-class baseline",
      "morphology adjustment removes, within PRAD patient 2",
      "morphology adjustment removes, smallest cross-patient task",
      "morphology adjustment removes, largest cross-patient task",
      "genes whose between-session variance is at or below zero",
      "target genes in the decomposition"]),
    ("fig07_theta_and_variance", "code/figures/fig07_theta_and_variance.py", 11,
     "Theta1 per IDC slide with spot-bootstrap 95% intervals, and the nested "
     "variance shares per task on the audited donor labels.",
     ["results/round2/R6_theta/r6_theta_bootstrap_ci.csv",
      "results/round2/R6_variance/r6_theta_build_comparison.csv",
      "results/round2/R6_variance/r6_variance_by_task.csv",
      "results/round2/R6_variance/r6_pooled_between_donor.csv"],
     ["theta1 on NCBI785, current morphology build",
      "theta1 on NCBI783, current morphology build",
      "theta1 on TENX95, current morphology build",
      "theta1 on TENX99, current morphology build",
      "theta1 on NCBI785, round-1 morphology build",
      "between-donor variance share, CCRCC",
      "between-donor variance share, LYMPH_IDC",
      "pooled between-donor share over the well-powered tasks"]),
]


def fmt(v):
    """Enough digits to be checkable, not more than the value carries."""
    if float(v).is_integer() and abs(v) < 1e6:
        return f"{int(v)}"
    if abs(v) >= 1e6 or (v != 0 and abs(v) < 1e-4):
        return f"{v:.3e}"
    return f"{v:.4f}".rstrip("0").rstrip(".")


D = pd.read_csv(NUMBERS)
key = {(str(r.slide), r.label): r for r in D.itertuples()}

missing = []
lines = [
    "# Deck figures",
    "",
    "Seven figures for the round-2 deck, one script each under `code/figures/`, each",
    "reading only CSVs committed in this repository. `python code/figures/make_all.py`",
    "renders all of them and fails if any reports a text overlap.",
    "",
    "Output is PNG at 300 dpi and PDF, 10 x 5.6 in (16:9), fonts no smaller than 11 pt.",
    "No figure carries a title: the slide carries it. Encoder colours are fixed in",
    "`code/figures/_deckstyle.py` and are the same in every figure.",
    "",
    "Every number annotated on a figure is read from its source CSV inside the script.",
    "The values listed below are read from `results/summary/deck_numbers.csv`, which is",
    "itself built from the sources by `code/scripts/build_deck_numbers.py` -- so this",
    "file, the figures and the numbers table cannot drift apart.",
    "",
    "This file is generated by `code/figures/make_readme.py`. Do not edit it by hand.",
    "",
]

for name, script, slide, desc, srcs, labels in FIGS:
    lines += [f"## `{name}.png` / `.pdf`", "",
              f"**Slide** {slide}", "",
              f"**Script** [`{script}`]({os.path.relpath(script, 'figures/deck')})", "",
              desc, "", "**Sources**", ""]
    lines += [f"- `{s}`" for s in srcs]
    lines += ["", "**Numbers annotated on the figure**", "",
              "| quantity | value | source |", "|---|---|---|"]
    for lab in labels:
        r = key.get((str(slide), lab))
        if r is None:
            missing.append((name, lab))
            lines.append(f"| {lab} | **MISSING FROM deck_numbers.csv** | |")
            continue
        lines.append(f"| {lab} | {fmt(r.value)} | `{r.source_file}` "
                     f"({r.source_column_or_query}) |")
    lines += [""]

lines += ["---", "",
          f"Generated {time.strftime('%Y-%m-%d')} from "
          f"`results/summary/deck_numbers.csv` ({len(D)} rows).", ""]

os.makedirs(os.path.dirname(OUT), exist_ok=True)
body = "\n".join(lines)
with open(OUT, "w") as f:
    f.write(body)

print(f"wrote {OUT} ({len(body)} bytes), {len(FIGS)} figures, "
      f"{sum(len(g[5]) for g in FIGS)} annotated numbers")
if missing:
    print("\nLABELS NOT IN deck_numbers.csv -- fix the label or add the row:")
    for n, lab in missing:
        print(f"   {n}: {lab!r}")
    sys.exit(1)
print("every annotated number resolved against the numbers table")
