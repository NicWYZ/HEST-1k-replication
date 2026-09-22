# Round 3, A1 stage report

22 September 2026. Covers interval 1: S0, A0, A1 and D0. Written against
`docs/round3_execution_plan.md`, which is this session's transcription of
`docs/decisions/round3_execution_handoff.md`. Report-and-wait gate. Nothing after A1 has been
started, set up, staged or piloted, and nothing will be until the decision comes back.

Numbers are quoted at the precision the comparison needs and every one of them was read back from
the file named beside it. Full precision stays in the files.

---

## 1. Stage and status

| stage | status |
|---|---|
| S0, housekeeping and the task definitions | complete |
| A0, the conformal harness and its acceptance checks | complete, all four checks pass |
| A1, marginal coverage across designs | complete, 12 encoders, 11 task files, 4 designs, 2 scores |
| D0, inventory and expansion proposal | complete, proposal in `docs/round3_d0_expansion_proposal.md` |

The headline is that the harness is sound and the coverage failure is real, large, and driven by
something more specific than the fold design. What predicts coverage is the level at which the fold
could form a calibration set. Where a fold could calibrate at donor or slide level it loses about
five points of coverage; where the pool forced calibration down to spatial blocks within a single
slide it loses about twenty-one. That is a factor of four, and it is the result.

## 2. What was run

`code/scripts/round3_a0_harness.py`, written in A0 and run unchanged at A1 scale, plus
`code/scripts/round3_task_defs.py` and `code/scripts/round3_d0_inventory.py` for the inputs and
`code/scripts/round3_a1_tables.py` for the report tables. Repository commits `fce1ad8` (plan and
task-definition schema), `e32e1d5` (task definitions, document index, memo banners),
`de99340` (A0 acceptance evidence), `9f86dbd` (D0 tables), `40dda80` (D0 proposal).

A1 ran as 12 Slurm jobs, one per encoder, each making two harness invocations: 11 task files over
designs `random`, `patient` and `donor`, then `slide_out` over the three task files where that
design is not degenerate. Accounting per job is in
`results/round3/A1_coverage/a1_job_accounting.csv`, one row per job with the encoder it ran:

| quantity | value |
|---|---|
| jobs | 12, all `COMPLETED`, exit `0:0` |
| partition actually used | `spill` for all 12, though `general` was requested |
| queue wait | 32 s to 184 s |
| elapsed | 00:12:31 to 01:46:25 |
| peak `max_rss_gb` | 6.31 to 11.98 against a 32 GB ask |
| CPUs | 4 requested and 4 recorded |

Two things worth carrying forward. The 32 GB ask was roughly three times what the work needed, so
A3 and A4 should ask 16 GB. And the `#SBATCH` directives written into the submitted command string
are honoured here, `sacct` recording 4 CPUs and 32 GB as requested; an earlier suspicion that they
were being dropped came from one job and did not generalise.

Every output directory carries `PROVENANCE.txt` with the job id, the partition actually used, node,
date, commit, command line, config hash with the config it hashes, and `PYTHONHASHSEED`.

## 3. Acceptance checks

All four A0 checks pass. Counts below are recomputed from the committed files, not copied from the
run that produced them, and the rollup is in
`results/round3/A1_coverage/a1_acceptance_summary.csv`, one row per check with its statistic,
tolerance, cell count and pass count.

**H1, the anchor to the prior result.** `results/round3/A0_smoke/h1_by_task__*__h1.csv`. With the
calibration fraction set to zero on the `patient` design, the harness reproduces R1b's
`intercept_f64` per-task Pearson on **30 of 30** encoder-task cells, three encoders over all ten
shipped tasks. Largest absolute difference $1.1 \times 10^{-16}$ against a tolerance of $10^{-6}$.
That is agreement at floating-point resolution rather than merely inside a threshold, which is the
strongest form this check can take. Each row names the R1b file it was checked against in its
`r1b_source` column.

**H2, harness correctness.** `results/round3/A0_smoke/h2_coverage__*__h2.csv`. On `random` with the
`abs` score, pooled marginal coverage passes on **30 of 30** cells. Pooled coverage ranges 0.8986 to
0.9018 and the worst deviation from nominal is 0.0018, on HCC with `uni_v2`, against a tolerance of
0.02. No fold produced an infinite conformal quantile.

**H3, disjointness.** 542 fold rows in A0 and a further 5,844 in A1, covering all four designs
(`results/round3/A0_smoke/h3_disjointness__*.csv`,
`results/round3/A1_coverage/h3_disjointness__*.csv`). Every row has $T$, $C$ and $E$ disjoint on
(sample id, barcode), and the scaler and PCA fit-row count equal to $|T|$ with zero difference
between the fitted means and variances and those of $T$.

**H4, engineering.** Explicit `pa.schema` on every parquet, summary CSVs written before the
parquets, `zlib.crc32` seeding, provenance with config hash and `PYTHONHASHSEED`, and the two-fold
one-task smoke run before any full job. The one part not evidenced is a byte-identical rerun; see
section 8.

**An aggregation point that the two checks make visible, and which matters for reading section 6.**
H2 measures coverage pooled over every test point. The A1 tables instead follow the project's metric
convention, per slide, then mean over slides, then over genes, then over folds. On the same three
encoders these give 0.9002 pooled against 0.8937 slide-mean
(`results/round3/A1_coverage/a1_aggregation_note.csv`, 30 pooled cells and 33 slide-mean cells),
the pooled figure being the higher of the two.
Small slides carry equal weight in the second and they are noisier, so the `random` design reads
very slightly below nominal in every table in section 6. That is an aggregation property and not
under-coverage, and no conclusion below rests on it.

## 4. What differs between the arms of each design

Written out before the terms are named, per the standing rule.

**`random`.** Test spots are drawn from the same slides, donors, sessions and scanners as training
and calibration spots. What differs between arms is spatial position within a slide and nothing
else. Spots adjacent to training spots are included, so this arm carries the adjacency advantage
that round 2's R3 measured, and it is a ceiling rather than a realistic deployment condition.

**`patient`.** Arms differ in HEST `patient` label, and with it in slide, in section, and in
whatever scan session and scanner settings that slide was acquired under. On COAD the label is
known wrong, so its arms differ in donor too but not in the way the label claims. On READ the arms
are same-specimen replicate pairs, so the contrast is a specimen-level one rather than a donor one.
Training-set size is held equal by subsampling.

**`donor`.** Arms differ in `donor_id` from the round-2 audit, and therefore in slide, section,
session and scanner, and additionally in the biological donor. On the three tasks whose donor
labels are entirely `unverifiable` the arm definition rests on labels no source confirmed.

**`slide_out`.** Arms differ in slide and in the session and scanner settings that came with it,
and do not differ in donor where the held-out slide's donor has other slides in training. This is
the only design in which donor is held fixed across arms, and it is available on only three task
files for that reason.

## 5. Predictions against outcomes

The six A1 predictions were written into `docs/round3_execution_plan.md` section 4.3 before the
sweep was submitted. Outcomes are read from
`results/round3/A1_coverage/a1_acceptance_summary.csv`,
`results/round3/A1_coverage/a1_coverage_by_design.csv`,
`results/round3/A1_coverage/a1_coverage_by_task_design.csv`,
`results/round3/A1_coverage/a1_coverage_by_calibration_unit.csv`,
`results/round3/A1_coverage/a1_encoder_quality_correlation.csv`,
`results/round3/A1_coverage/a1_slideout_donor_sharing.csv` and
`results/round3/A1_coverage/a1_idc_label_sets.csv`.

| # | prediction | outcome | verdict |
|---|---|---|---|
| 1 | `random` at nominal for every task and encoder | pooled 0.8986 to 0.9018 over 30 cells, worst deviation 0.0018 | held |
| 2 | `patient` and `donor` under-cover, worst on PRAD and SKCM patient folds and COAD under shipped labels; COAD improves under `donor` | under-coverage held, 0.786 and 0.802 against 0.894. COAD improved from 0.721 to 0.866. SKCM is among the worst at 0.687. PRAD is among the best at 0.875, not the worst | partly held, and the PRAD half is wrong |
| 3 | coverage at or near nominal under `donor` only where `calibration_unit = donor`; slide or block folds under-cover | donor-calibrated 0.851, slide 0.849, block 0.686 | held, and it is the strongest result in the stage |
| 4 | `slide_out` sits between `random` and `donor`; folds whose calibration slide shares the test donor do better | 0.859 against 0.894 and 0.802. Donor-sharing folds 0.9223 against 0.7795 | held on both halves, with the caveat in section 6 |
| 5 | under-coverage larger for weaker encoders in absolute terms, same ordering across designs for every encoder | ordering holds for all 12 encoders without exception. The quality relationship does not: correlation between benchmark Pearson and coverage is $-0.04$ under `donor` and $+0.20$ under `patient` | half held, half refuted |
| 6 | IDC under audited labels under-covers more than under shipped labels | audited is $+0.005$ higher, not lower, higher in 9 of 12 encoders, sd across encoders 0.009 | refuted, and the effect is small |

## 6. Results

### 6.1 The coverage table across designs

`results/round3/A1_coverage/a1_coverage_by_design.csv`, over 132 task-encoder cells per design and
score, except `slide_out` which has 36.

| design | score | coverage | sd across cells | shortfall | mean width |
|---|---|---|---|---|---|
| `random` | `abs` | 0.894 | 0.010 | 0.006 | 1.95 |
| `random` | `scaled` | 0.899 | 0.003 | 0.001 | 2.29 |
| `slide_out` | `abs` | 0.859 | 0.029 | 0.042 | 2.67 |
| `slide_out` | `scaled` | 0.871 | 0.026 | 0.029 | 9.14 |
| `donor` | `abs` | 0.802 | 0.085 | 0.098 | 2.76 |
| `donor` | `scaled` | 0.804 | 0.074 | 0.096 | 16.50 |
| `patient` | `abs` | 0.786 | 0.077 | 0.114 | 2.63 |
| `patient` | `scaled` | 0.7895 | 0.074 | 0.111 | 11.60 |

The ordering is `random`, then `slide_out`, then `donor`, then `patient`, and it holds for every one
of the 12 encoders separately (`a1_coverage_by_encoder.csv`). The spread across cells grows with the
shortfall, from 0.010 under `random` to 0.085 under `donor`, so the designs that fail also fail
unevenly.

### 6.2 The calibration unit, which is what actually predicts coverage

`results/round3/A1_coverage/a1_coverage_by_calibration_unit.csv`, `abs` score, excluding the
`random` design because its unit is always the spot and it is the no-shift control.

| calibration unit | cells | coverage | sd | shortfall |
|---|---|---|---|---|
| donor | 72 | 0.851 | 0.028 | 0.049 |
| slide | 84 | 0.849 | 0.034 | 0.051 |
| patient | 60 | 0.834 | 0.026 | 0.066 |
| block and slide mixed | 12 | 0.721 | 0.017 | 0.179 |
| block | 72 | 0.686 | 0.057 | 0.214 |

This is the finding. Donor-level and slide-level calibration are indistinguishable from each other
at about five points of shortfall. Block-level calibration, which the rule falls back to when the
training pool holds a single slide, costs twenty-one points. The rule that produced this structure
was part of the design rather than a result, and the handoff said so in advance: which folds could
calibrate at which level is itself the finding.

Per task (`a1_coverage_by_task_design.csv`, `abs`, mean over 12 encoders), the three tasks that fall
to block-level calibration are exactly the three two-sample tasks, and they are the three worst:

| task | random | patient | donor | slide_out | donor-design calibration unit |
|---|---|---|---|---|---|
| PAAD | 0.8930 | 0.8686 | 0.8945 | | donor |
| PRAD | 0.904 | 0.875 | 0.871 | 0.897 | slide |
| COAD | 0.896 | 0.721 | 0.866 | | donor |
| CCRCC | 0.881 | 0.856 | 0.864 | | donor |
| READ | 0.898 | 0.810 | 0.811 | 0.844 | slide |
| LYMPH_IDC | 0.900 | 0.804 | 0.818 | | donor |
| IDC audited | 0.877 | 0.821 | 0.833 | 0.834 | donor |
| IDC shipped | 0.878 | 0.820 | 0.828 | | donor |
| HCC | 0.902 | 0.760 | 0.750 | | block |
| SKCM | 0.902 | 0.687 | 0.673 | | block |
| LUNG | 0.900 | 0.627 | 0.619 | | block |

COAD is the clearest single case for the audit. Its `patient` design covers 0.721, its `donor`
design 0.866, a recovery of 0.145 from nothing but correcting the grouping variable.

### 6.3 Encoder quality does not predict coverage under shift

`results/round3/A1_coverage/a1_encoder_quality_correlation.csv`, built from
`a1_coverage_by_encoder.csv` and `a1_vs_benchmark_pearson.csv`. Correlations between an encoder's
benchmark Pearson and its mean coverage: $+0.740$ under `random`, $+0.603$ under `slide_out`,
$+0.197$ under `patient`, and $-0.037$ under `donor`. The coverage range across all 12 encoders is
narrow under every design, 0.7795 to 0.7949 under `patient` and 0.7967 to 0.8116 under `donor`,
against a benchmark Pearson range of 0.3252 to 0.4229. A better encoder does not buy calibrated
intervals under donor shift.

### 6.4 The scaled score buys nothing at this stage

From `results/round3/A1_coverage/a1_coverage_by_design.csv` and
`results/round3/A1_coverage/a1_sigma_diagnostics__*__main.csv`.

The `scaled` score gives coverage within 0.004 of `abs` under `patient` and `donor` while its mean
width goes from 2.63 to 11.60 under `patient` and from 2.76 to 16.50 under `donor`, which is four
to six times wider for no coverage gain. Under `random`, where there is no shift, the two are close,
1.95 against 2.29.

The widening is not the variance floor firing. The median fraction of test points sitting at the
$10^{-3}$ floor is 0.005 under `patient` and 0.0004 under `donor`, with a maximum of 0.26, and the
smallest median test sigma is 0.18, which is two orders of magnitude above the floor. So the
residual model is genuinely predicting large dispersion on shifted features rather than degenerating
numerically. Whether `scaled` is narrower at matched coverage is A4's comparison and this is not it,
but at equal nominal level it is much wider and no better covered.

### 6.5 Donor sharing under `slide_out`, with the caveat that matters

`results/round3/A1_coverage/a1_slideout_donor_sharing.csv`. Folds whose calibration slide shares
the test slide's donor cover 0.9223 over 216 folds, against 0.7795 over 36 folds where it does not.
The difference is about fourteen points of coverage and in the predicted direction.

It is not a within-task contrast. The same file broken out by task shows PRAD supplying all 216
donor-sharing folds at 0.9223, and IDC at 0.7972 over 24 folds and READ at 0.7440 over 12 folds
supplying every non-sharing one. Donor sharing is therefore perfectly confounded with task identity
here, and the headline difference is a between-task comparison wearing a within-design label. A
further 120 folds were excluded because the flag varied across the three calibration draws inside
the fold, which the file records. The prediction is consistent with the data and is not established
by it.

### 6.6 The IDC label sets

`results/round3/A1_coverage/a1_idc_label_sets.csv`, four rows, one per design and score.

Under the `donor` design with the `abs` score, audited labels cover 0.0051 higher than shipped, not
lower, higher in 9 of 12 encoders, with a standard deviation across encoders of 0.0093. The
prediction was that merging TENX95 and TENX99 would remove a leak and make coverage worse.

The effect is not stable enough to carry a sign. Across the four design-and-score combinations the
difference is $+0.0011$, $+0.0058$, $+0.0051$ and $-0.0092$, so the `donor` and `scaled` combination
reverses it, and every one of the four is smaller than its own spread across encoders. The honest
reading is that merging the pair does not move marginal coverage measurably at this resolution, in
either direction, and the prediction is refuted only in the weak sense that the expected drop did
not appear.

## 7. Discrepancies, open questions and escalations

Handled under the decision boundaries and recorded here rather than interrupting the interval.

1. **`slide_out` is degenerate on eight of the eleven task files.** Proven by set equality of the
   test partitions, not sampled: on CCRCC, COAD, HCC, IDC shipped, LUNG, LYMPH_IDC, PAAD and SKCM
   the `slide_out` folds are exactly the `donor` folds, because each donor has one slide. The design
   is distinct only on PRAD, READ and IDC-audited. A1 ran it on those three. The handoff named COAD
   and LYMPH_IDC as multi-slide tasks and they are not. This is a change to a design's arm
   definitions and is flagged as such.
2. **COAD's TENX111 spot count disagrees between two repository sources**, 6,138 rows in the AnnData
   against 6,643 in `sample_metadata.csv`, a difference of 505. The task files carry the AnnData
   count, which is what round 2's per-gene tables were computed on. Which is right is unresolved.
3. **The benchmark's `lab` field is a cohort title, not an audited institution.** It is
   `dataset_title` copied verbatim, with `lab_label_status` `unverified` on all 72 samples. Nothing
   is grouped by it before D3.
4. **Three tasks have no verified donor label on any sample.** LUNG, PAAD and SKCM are entirely
   `unverifiable` and COAD is `contradicted` on three of four. Their `donor` design rows rest on
   labels no source confirmed, and the tables carry `donor_label_status` so this is visible.
5. **The numeric-claim sweep command printed in `WAYS_OF_WORKING.md` does not reproduce the gate.**
   It omits `--derived .verify-derived` and `--always results/summary/deck_numbers.csv`, which
   `code/scripts/sweep_table.py` passes. Run as printed over the README and `docs/*.md` it reports
   65 unresolved claims; run correctly it reports 46, of which 41 sit in `docs/r5_idc_provenance.md`.
   Reported rather than fixed, per the instruction to flag rather than change silently.
6. **A derived-claim formula that cites a gitignored parquet cannot resolve in a clone**, so the
   gate is only fully reproducible where the working files exist. One such formula exists, in
   `round2_R3_stage_report.md`.
7. **The round-3 handoff's premise about the memos was overtaken.** All six round-2 decision memos
   are present, including `round2_R1_decisions.md`, which the handoff recorded as never saved.
   Nothing was reconstructed. The companion `round3_oversight_handoff.md` is also in the repository
   and its action items are transcribed into the operating plan.

## 8. What was not checked

- **Determinism.** No A1 job was rerun, so the byte-identical rerun that H4 would be completed by
  has not been demonstrated. Every design is integer or crc32 seeded by construction and round 2's
  AST sweep established the codebase carries no `hash()` seeding, but that is an argument, not a
  measurement.
- **Conditional coverage.** Everything here is marginal. Whether the shortfall is concentrated or
  diffuse, and whether it is a centring error or a width error, is A2 and is not addressed.
- **Whether donor sharing under `slide_out` is a real effect**, for the confounding reason in
  section 6.5.
- **Whether the three block-calibrated tasks fail because of the calibration unit or because they
  are two-sample tasks.** Those two properties coincide exactly in the benchmark, so this stage
  cannot separate them. It is the most important thing A2 should try to separate, and it may not be
  separable without the expansion data.
- **The `scaled` score at matched coverage**, which is A4.
- **COAD's spot-count disagreement**, reported and not resolved.
- **Anything about lab.** No lab grouping was done anywhere in this stage.
- **Per-gene results.** The per-gene parquets were written and are on Longleaf, but no per-gene
  analysis was run; the R7 join is A2.

## 9. Proposed next step

Interval 2 as planned, which is A2 and A3 with D1 to D3 alongside, subject to the gate.

Two things I would put to the oversight chat as part of that decision.

First, A2's main question should be reframed around the calibration unit rather than the design. The
design ordering in section 6.1 is almost entirely explained by which calibration level each fold
could reach, and the interesting question is now whether block-level calibration fails because the
calibration set is small, because it is spatially adjacent to the test spots, or because a single
slide cannot represent the shift. Those have different repairs.

Second, A3's premise is weakened by section 6.3. Weighted conformal corrects for covariate shift
between calibration and test features, and the density-ratio estimator is the same classifier round
2 used to show slides are decodable. That still applies. But the coverage deficit does not track
encoder quality at all under `donor`, which suggests the deficit is not mostly a feature-space
shift the weights can see. The calibration-support diagnostic $n_{\text{eff}}$ is the thing to watch,
and the honest prediction is now that reweighting helps on the slide-level folds and does little on
the block-level ones.

**Track D.** `docs/round3_d0_expansion_proposal.md` carries the proposal, with the storage ask of
86 samples and 47.7 GB and four options. Its headline is that the institution criterion in the
handoff, three laboratories with three or more donors each, is not satisfiable anywhere in HEST-1k
on current labels: across 46 organ-by-technology cells the maximum is two. It also finds that in the
proposed kidney set the `resolution_uncertain` flag is constant within each laboratory, and
asymmetrically so, meaning every lab contrast with donors on both sides is also a pixel-size
provenance contrast while the one contrast free of the flag has no donors in one arm. D1 needs
Nicolas's approval of the sets and the storage ask in addition to this gate.
