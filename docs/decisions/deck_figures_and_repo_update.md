# Instructions: deck figures and a full repository refresh

20 September 2026. For the execution session on `NicWYZ/HEST-1k-replication`. Two jobs, both due before Monday morning. No new analysis; everything here is rendering existing results and bringing the repository up to date with them. One short report when done.

Companion document: `deck_master_outline.md`, which names every figure and every number the deck will use.

---

## Part 1. Figures for the deck

### 1.1 Rules

- All figures are rendered by scripts committed under `code/figures/`, one script per figure, each reading only CSVs already in the repository. No figure is produced by hand or from a session artifact. A `code/figures/make_all.py` runs every one.
- Output to `figures/deck/` as both PNG (300 dpi) and PDF, 16:9-friendly proportions (width 10 in, height 5.6 in or 4.2 in for half-height panels). Fonts no smaller than 11 pt at that size. Titles are not baked into the figure; the slide carries the title.
- Each figure gets a `figures/deck/README.md` entry: file name, source CSVs, script, one-line description, and the exact numbers annotated on it.
- Every number annotated on a figure is read from the CSV inside the script, never typed.
- Colour: one accent for the quantity of interest, grey for reference. Three encoders where encoders are shown (`hoptimus0`, `uni_v2`, `resnet50`), consistently coloured across all figures.

### 1.2 The figures

**fig01_fidelity** (slide 3). Per-encoder average Pearson on the nine paper tasks: ours vs paper Table 1 vs live leaderboard, twelve encoders sorted by ours. Annotate the two exact hits (ResNet50, H-Optimus-1). Source: `results/summary/results_encoder.csv`, `results/summary/hest_leaderboard_030426.csv`, `results/summary/scaling_law_inputs.csv` for paper values. The round-1 `figures/fig_replication_fidelity.png` can be the starting point if its script exists; if it does not, write one.

**fig02_replicate_leak** (slide 4). For IDC and READ, per held-out slide and encoder, paired points for with-partner and without-partner within-slide Pearson connected by a line, three encoders. Right margin annotation: IDC mean +0.065, 6/6 positive, 54% of gap 0.121; READ mean +0.090, 12/12, counterfactual (folds group pairs). Source: `results/round2/R5c_leak/r5c_replicate_leak.csv`, `r5c_leak_summary.csv`. The existing `fig_r5c_replicate_leak.png` may already be this; regenerate under the rules above regardless.

**fig03_split_staircase** (slide 5). Main panel: a waterfall from `random` down to `patient` with the five steps (training-set size, spatial adjacency, residual adjacency past block edge, novel slide, patient identity), means over three encoders. Use the ten-task means for the first three steps and the three-multi-slide-task means for the last two, and say so in a footnote line inside the figure; alternatively draw the four-step ten-task version and the five-step three-task version side by side. A horizontal reference bar for the between-encoder spread (0.098) on the same axis. Inset or second panel: blocked accuracy vs grid size (4, 6, 10) with and without buffer, showing the 0.028 vs 0.010 spread. Source: `results/round2/R3_splits/r3_decomposition_terms.csv`, `r3_per_task_terms.csv`, `buffer_diagnostics__*.csv`, `results/summary/results_encoder.csv`.

**fig04_raw_head_width** (slide 6). Scatter of rank on PCA ridge (x) vs rank on raw ridge (y), twelve encoders, point colour by embedding width, labelled. Highlight H-Optimus-1 (1 → 7). Annotate Spearman(width, raw) = −0.95 and Spearman(width, PCA) = +0.73 with n = 12. Source: `results/round2/R8_raw_heads/r8_raw_head_leaderboard.csv`, `r8_width_correlations.csv`. The existing `fig_r8_raw_heads.png` may be close.

**fig05_r2_ladder** (slide 9). Left: the four rungs of fold-median $R^2$ (faithful, training-mean intercept, oracle level, oracle level and optimal scale) pooled, as a connected step plot with the gain per step annotated (+0.798, +0.185, +0.070). Right: the same four rungs per task as thin lines. Inset: $\rho / r$ by encoder, sorted, with 1.84 pooled marked. Source: `results/round2/R1b_heads/r1b_ladder_by_task.csv`, `r1b_ladder_by_encoder.csv` (if the latter is not in the repository, compute it from `head_intercept__*__f64.csv` and commit it).

**fig06_session_signature** (slide 10). Three panels. Left: bar chart of balanced accuracy for the three PRAD probes (slide identity within patient 2, session within patient 2, resolution class within patient 1) for three encoders, with chance lines (0.067, 0.5, 0.5). Middle: accuracy lost to morphology adjustment per task (PRAD, IDC, LUNG, PAAD, SKCM), three encoders. Right: stacked variance fractions for expression within PRAD patient 2 with session as top level (between-session, between-slide-within-session, within-slide), pooled over 50 genes. Source: `results/round2/R4_probes/r4_probes_v2.csv`, `results/round2/R6_variance/r6_prad_session_variance.csv`.

**fig07_theta_and_variance** (slide 11). Left: $\theta_1$ (nuclear area vs GATA3, raw counts) for the four IDC slides under the current morphology build with spot-bootstrap 95% intervals; if bootstrap intervals are not already in `results/round2/R6_theta/`, compute them (200 resamples) from the morphology and count parquets and commit the CSV. Right: per-task stacked variance fractions (between-donor, between-slide-within-donor, within-slide) on audited labels, tasks sorted by between-donor, with `df_donor` printed under each bar and the label-status flag as a marker. Source: `results/round2/R6_variance/r6_theta_build_comparison.csv`, `r6_variance_by_task.csv`, `donor_variance_components.csv`.

**Optional, if time allows: fig08_count_diagnostics** (slide A2). Regenerate `figures/fig_count_diagnostics.png` under the deck rules from `results/tailored/counts/count_diagnostics.csv`.

### 1.3 A single source of truth for the deck's numbers

Write `results/summary/deck_numbers.csv` with columns `slide, label, value, source_file, source_column_or_query`, one row per number that appears in `deck_master_outline.md`, generated by a script (`code/scripts/build_deck_numbers.py`) that reads each value from its source file. Then run `verify_numeric_claims.py` over `deck_master_outline.md` against that file and the sources, and fix any discrepancy in the outline by editing the outline, not the number. Report the count of claims verified and any that could not be.

---

## Part 2. Repository refresh

The repository is the record the deck points at. Everything below is a check that it says what the results say, as of the closeout.

### 2.1 README

- Status table: round 2 complete, closeout complete, tag `round2-final`, one commit past it for the closeout report. Remove any "in progress" or "blocked" wording.
- Headline result section: still the faithful replication; confirm the 108-cell figures match `discrepancy_table.csv`.
- Key findings: reorder to match the synthesis ranking (patient split and replicate leak; split design vs encoder; session signature; intercept and ladder; A13 width; panels and selection; NB; $\theta_1$ and variance components). Every number checked against its file. Remove anything that was withdrawn (institution scalar, the 0.1241 pooled slide term, "confound-free", the COAD same-patient reading, the either/or probe-1 rule, the 199× ratio).
- "Properties of HEST-bench found in this replication": one entry per property with file path, including the IDC same-donor pair (marked probable, unresolved), COAD, READ, panels, selection sensitivity, resolution alignment and its mechanism, inert penalty and A13, missing intercept, solver noise.
- Known limitations: add `raw_xgb` for H-Optimus-1 not run (70 min/split), IDC attribution unresolved, nine unverifiable donor labels, no bootstrap on variance components, no nested-ANOVA diagnostics, session result from one patient only.
- Repository layout: add `figures/deck/`, `code/figures/`, `docs/decisions/`, `results/round2/`.
- Reproducing: a section listing, in order, the scripts that regenerate round 2 from cached embeddings, and `code/figures/make_all.py`.

### 2.2 docs/

- Add the decision memos, which are currently absent: `round2_R1_decisions.md`, `round2_R3_decisions.md`, `round2_R5_decisions.md`, `round2_closeout_decisions.md`, under `docs/decisions/`. Nicolas will supply them; do not reconstruct.
- Add `docs/round2_results_synthesis.md` (final version, supplied by Nicolas) and `docs/literature_landscape_2026-09.md` (the research report, supplied by Nicolas).
- Add `docs/deck_master_outline.md` (this outline) and this instruction file.
- `docs/README.md` or an index section in the main README listing every document with one line each and its date, in chronological order.
- `WAYS_OF_WORKING.md`: confirm it carries the verification-sweep rule, the explicit-schema rule, cheapest-outputs-first, `PYTHONHASHSEED=0`, sizing from `sacct`, the arm-enumeration rule, and the grouping-variable audit rule.

### 2.3 Results and provenance

- Every directory under `results/round2/` has a `PROVENANCE.txt` (some currently have only per-encoder provenance files; add a directory-level one that lists the stage, the memo clause, the scripts, and the per-encoder files). `results/round2/R5b_audit/` and `results/round2/R6_theta/` should be checked in particular.
- Stale files: anything superseded and no longer referenced by a report or the README is removed, with its removal noted in the commit message. Candidates: `replicate_leak__*.csv` vs `replicate_leak_v2__*.csv` in `R3_splits/` (keep whichever the R5c summary was built from, remove or rename the other with a note); duplicate `donor_variance_components.csv` vs `r6_donor_variance_components.csv`; `pergene_correlations.csv` vs `r7_pergene_correlations.csv`. Where two files are both current, say in `PROVENANCE.txt` what distinguishes them.
- The fifteen evidence files the verification sweep found uncommitted are confirmed present.
- `results/summary/`: regenerate every derived table with `build_summary_tables.py` and confirm no diff, or commit the diff with an explanation.

### 2.4 MANIFEST

`MANIFEST.md` is dated 16 September and predates round 2. Regenerate it with `make_manifest.py` so it covers `instrumentation/round2_intercept/`, `morphology_v2`, the per-gene parquets and anything else round 2 added on Longleaf, with sizes and hashes.

### 2.5 Code

- `code/scripts/`: every script has a docstring stating the stage, the memo clause, inputs, outputs. Any script that was superseded (for example `split_comparison.py` if `split_decomposition.py` and `round2_split_v4.py` replaced it) is either removed or moved to `code/scripts/superseded/` with a one-line reason.
- `code/figures/` as in Part 1.
- `env/`: confirm `requirements.lock`, `conda_env.yaml` and `versions.txt` reflect the environment that ran round 2, and that TRIDENT's pinned commit is recorded.

### 2.6 Final checks

- Run `verify_numeric_claims.py` over README, every document in `docs/`, and the deck outline. Zero unresolved. Report the uncited count.
- `git status` clean; `git tag round2-final-deck` on the final commit and push.
- A three-paragraph report: what was regenerated, what was removed or renamed and why, and anything that could not be brought up to date.
