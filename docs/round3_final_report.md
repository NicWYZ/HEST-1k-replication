# Round 3, end-of-round report

24 September 2026. Covers interval 3: H1, A4 (A4a and A4b), B1, B2 and D4. Written against
`docs/round3_execution_plan.md`, whose section 13 is this session's transcription of
`docs/decisions/round3_A3_decisions.md`. This report is the round's last gate. After it the
repository is tagged `round3-final` and work stops; the round-4 plan is the oversight chat's to
write.

**Revision 2, 24 September 2026 (tag `round3-final-r2`).** The first version (tag `round3-final`,
commit `8a16020`) repeated a false floating-point example from the A4b hand-back in section 3. This
revision corrects that sentence and adds section 7 item 18. No number changed.

Numbers are quoted at the precision the comparison needs, and every one was read back from the file
named beside it. Full precision stays in the files. Every pooled number is computed by a script into
a committed table, one per track: `results/round3/A4_scores/a4b_summary.csv`,
`results/round3/B1_ppi/b1b2_report_numbers.csv`, `results/round3/D4_expansion/d4_pooled_numbers.csv`
and `results/round3/A4_scores/a4_report_numbers.csv`, with the numbers pooled across committed tables in `results/round3/final_report/final_report_numbers.csv`.

Two limitations apply to every source term in this report and are stated here once. HEST-1k has no
organ-by-technology cell with three laboratories at three or more donors each, and, the stronger of
the two, no two-laboratory cell with disease held fixed (`README.md` known limitation 14,
`results/round3/D0_inventory/organ_technology_ranking.csv`). No round-3 document carries a laboratory
term. The kidney contrast in section 6.5 is a population-and-source shift and is named as one.

---

## 1. Stage and status

| stage | status |
|---|---|
| H1, housekeeping from the A3 escalations | complete inside its one-day cap; `A3_report_numbers.csv` byte-identical after tagging; the Immunity patient table unreachable |
| A4a, scores and the model-based comparator | complete at a declared reduced scope (CQR on 6 of 50 genes, NB on 16); anchor passes; one merge defect found by the lead and fixed before commit |
| A4b, HCP with $K = 10$ exchangeable donors on CCRCC | complete; anchor passes; HCP finite in every cell and over-covers at about twice the pooled width |
| B1, prediction-powered inference with donor-clustered variance | complete; the anchor to H1 holds in 12 of 12 cells; three of four acceptance checks are exact identities and the fourth cannot hold as written (section 7) |
| B2, semi-synthetic coverage | complete; 200 labelled-donor draws in each of 13 settings |
| D4.1, the layout anchor | complete, and it passes; D4's other arms may be read beside benchmark results through it |
| D4.2 to D4.4, the expansion sets | complete on three encoders; one schema extension and one panel-size correction escalated |

The interval's result is a single statement, reached from four directions. **The number of donors
limits every uncertainty statement this project can make, and the number of spots does not.**
Spot-level standard errors on CCRCC are 29 to 68 times too small, and a spot i.i.d. interval covers
the donor-level quantity 0.044 of the time at nominal 0.90, against 0.913 for a donor-clustered
interval with a $t_{G-1}$ reference (`results/round3/B1_ppi/b1b2_report_numbers.csv`). Hierarchical
conformal prediction becomes finite once $K + 1 \ge 1/\alpha$ and then over-covers, 0.9692 at
1.947 times the pooled width on CCRCC (`results/round3/A4_scores/a4b_summary.csv`). The pooled quantile
stays at 0.8644 whether 6 or 10 donors calibrate it, so its shortfall is not a $K$ effect. On a
second multi-donor task, where laboratory, instrument and preservation are fixed, donor shift costs
about a point of coverage, with a fold-to-fold scatter about a third of CCRCC's
(`results/round3/D4_expansion/d4_pooled_numbers.csv`).

## 2. What was run

Repository commits this interval: `471161d` (the A3 memo and its transcription as plan section 13),
`a181326` (`donor_audit_r3.csv`, built by the lead before fan-out), `d4ed0e7` (H1), `2c97d81` (A4b),
`93b5d32` (B1 and B2), `d22cf44` (D4), `7027cab` (A4a), and the commit that carries this report.
Every track was dispatched from `a181326`.

The work ran as five parallel tracks, per plan section 13.9: Housekeeping (H1), Scores (A4a), HCP
(A4b), Inference (B1 then B2) and Expansion (D4). Sub-agents ran no git command, including
read-only queries. The local clone was the only committer, and every sub-agent result was checked by
the lead against its primary tables before commit (section 3).

**Scripts.** Every new script imports `code/scripts/round3_a0_harness.py` unmodified (md5
`0ad7ae8efe554c1f285e5f384a9fb7f5` in every PROVENANCE file this interval). H1:
`code/scripts/round3_h1_build_audit_r3.py`, `code/scripts/round3_h1_tag_superseded.py`. A4a:
`code/scripts/round3_a4_scores.py`. A4b: `code/scripts/round3_a4b_hcp.py`. B1 and B2:
`code/scripts/round3_b1_ppi.py`, `code/scripts/round3_b2_semisynthetic.py`. D4:
`code/scripts/round3_d4_task_defs.py`, `round3_d4_layout_anchor.py`, `round3_d4_sets.py`,
`round3_d4_probe.py`, `round3_d4_consolidate.py`, `round3_d4_check_barcodes.py` and
`round3_d4_r2_gene_check.py`, all in `code/scripts/`.

**Jobs.** All jobs were CPU-only and charged to `rc_htzhu_pi`. Every job requested `general` and
landed on `spill`. The job table for the interval, with node, elapsed time, limit, requested memory
and peak memory from `sacct`, is `results/round3/final_report/interval3_jobs.csv`, built from the raw
dump `results/round3/final_report/interval3_sacct.txt` by `code/scripts/round3_final_report_numbers.py`.
H1 ran no job. Counts from `results/round3/final_report/final_report_numbers.csv`: 48 jobs, 48 on
`spill` and 48 charged to `rc_htzhu_pi`. A4a ran 16 (11 completed; three were cancelled before
running and resubmitted when the lead asked for matched-subset tables), A4b 7 (6 completed; the
failure is a smoke run whose anchors fail by design on truncated folds), B1 and B2 5 (5 completed),
and D4 20 (17 completed; the three failures are accounted for in
`results/round3/D4_expansion/d4_job_accounting.csv`, and no reported number comes from them). Peak
memory by track was 9.0 GB for A4a, 6.09 GB for A4b, 11.2 GB for B1 and B2, and 15.50 GB for D4.
Every reported number comes from a completed job.

**Script md5s against committed files.** Plan section 13.4 item 5 (iii) asks that provenance record
the md5 of the executed script, and it does in every job. In three tracks the committed file differs
from the file a job executed, because reporting or figure code was added after the runs. Each track
compared the two copies function by function and found no difference on any path that computes a
number, so the tables were kept and the difference is declared here rather than rerun.
A4b's encoder jobs ran `f66159d6d52dbeddc2f35542f3c4ef91`, against the committed
`56bf3621ae53efe41140c439164b5534` (`results/round3/A4_scores/a4b_PROVENANCE__resnet50.txt`). B1's
prediction jobs ran `268b171490ab2cb996a77551621c2998` and its estimate job
`6095a793dce3dbf2a2242f255bc17f20`, against the committed `544721f07cb3d74dc5b92456d61fe450`; the
estimate job was rerun on the final estimator and reproduced every acceptance value and estimate row to zero
(`results/round3/B1_ppi/PROVENANCE__estimate.txt`). D4's layout-anchor jobs ran a copy one line
older than the committed `round3_d4_layout_anchor.py` (the `bp['head']` fix);
`round3_d4_sets.py` and `round3_d4_probe.py` match their PROVENANCE md5s exactly
(`results/round3/D4_expansion/PROVENANCE__d4_indiana__resnet50.txt`). A4a's nine production jobs ran `1efae3e0295e13cae00b18e572ebec3e`, against the committed
`541bca01159e06d971419391415c734c`. The difference is anchor, reporting and figure bookkeeping plus the
merge fix of section 3, and every scoring, fitting, interval, oracle, PIT and decile-aggregation
function is byte-identical (`results/round3/A4_scores/A4a_SCRIPT_VERSIONS.txt`). The A4a hand-back
names its two timing probes as jobs `2288730` and `2288756`; `sacct` has no such jobs, and the probes
are jobs 2289207 and 2290678 (`results/round3/final_report/interval3_sacct.txt`).

## 3. Acceptance checks

**H1.** `results/round3/A3_report_numbers.csv` is byte-identical after the tagging run: 388 rows, 0
cells differing, maximum absolute difference 0.0
(`results/round3/H1_housekeeping/a3_report_numbers_rerun_comparison.csv`). That carries A2b's A1
anchor through unchanged. The `superseded_label_set` column is on 229 CSVs, 14,149 rows True, with 0
violations of the rule that it is True exactly when the task is IDC and the label set `audited`
(`results/round3/H1_housekeeping/superseded_tag_manifest.csv`). The lead checked independently that
each tagged file equals its committed version with the one column appended. `donor_audit_r3.csv`
regenerates at 148 rows with 48 cells changed, all in the citation column, and the conflicts file
regenerates byte-identical. The override guard fixture accepts 3 of 12 cases and refuses 9
(`results/round3/H1_housekeeping/h1_override_guard_fixture.csv`).

**A4a.** `abs` and `scaled` through the A4a script reproduce A1's committed per-cell coverage to
4.4e-16 on 2,640 cells, 12 of 12 checks at tolerance 1e-12 (`results/round3/A4_scores/a4_acceptance.csv`).
The lead recomputed the per-fold version independently from `a4_by_fold.csv` against A1's by-fold
tables and found coverage equal to 3.3e-16 on every fold row of all three encoders, with widths
inside the cross-node tolerance because the first calibration draw ran on a different node. CQR on
`random` covers within 0.0131 of nominal on every task. The NB convergence guard passes on every
fit, 21,120 of 21,120 (`results/round3/A4_scores/a4_nb_guard.csv`). The NB PIT is close to uniform on
`random` for CCRCC, median KS 0.0228 to 0.0274, and not on the nine smaller tasks, 0.0672 to 0.0720,
against the stage's own threshold of 0.05; plan section 4.6 asks for the statistic, not a level.

**A merge defect, found by the lead and fixed before commit.** The merged predicted-value-decile
table kept, for `abs` on the full gene set, the rows of the CQR job, which aggregate only the first
calibration draw, because duplicate keys were resolved in filename order. The Scores track fixed the
merge by source preference and reran only the merge and the report numbers, with no fit. Four values
in `results/round3/A4_scores/a4_report_numbers.csv` changed. The corrected `abs` top-decile coverage, 0.6945 under `donor`, 0.6670
under `patient` and 0.6019 under `slide_out`, now equals A2's committed baseline exactly, which
closes the track's own escalation of an unexplained gap. The by-fold, width-at-coverage and oracle
tables and the figure came back byte-identical. Because the merge now chooses between jobs, the
per-job decile fragments are committed beside the merged table.

**A4b.** The $K = 6$ arm reproduces A1's CCRCC `donor` coverage to $2.2 \times 10^{-16}$ over 72
fold-encoder rows, which the lead checked against `results/round3/A1_coverage/a1_by_fold__<enc>__main.csv`;
HCP and the one-per-group interval are finite in every cell (`results/round3/A4_scores/a4b_anchor.csv`).
$K = 10$ was obtained through the harness's own calibration routine by passing
$(K - 0.5)/n_{\text{units}}$, whose ceiling is $K$ for every pool size, rather than
$K/n_{\text{units}}$, whose ceiling exceeds $K$ in floating point for some pool sizes (`7/25 * 25`
evaluates to `7.000000000000001`). The A4b hand-back and the docstring of
`code/scripts/round3_a4b_hcp.py` give `10/23 * 23` as the example; that product is exactly 10.0 in
floating point, so the example is wrong, while the guard is sound and no A4b number depends on it
(section 7 item 18).

**B1.** The calibration-fraction-zero `patient` predictions reproduce A0's H1 in 12 of 12
encoder-task cells, maximum difference $1.1 \times 10^{-11}$, before any `donor` prediction was made
(`results/round3/B1_ppi/b1b2_report_numbers.csv`, keys `anchor_cells_passed` and
`anchor_max_abs_diff_vs_a0_h1`). Of plan section 4.7's four acceptance checks
(`results/round3/B1_ppi/b1_acceptance.csv`), three hold as identities. With $U$ empty PPI equals
classical exactly in 22 of 22 cells. With predictions equal to the measurements PPI equals the
full-data value to $8.9 \times 10^{-16}$ at the identity $\lambda$. With one spot per donor the
cluster variance equals the i.i.d. one to $1.4 \times 10^{-12}$ in 34 of 34 cells. The fourth, that
the permuted predictor's interval is at least as wide as the classical one, passes in 59 of 104
cells. Every failure is in the spot-weighted population, for the reason given in section 7 item 4.

**B2.** The lead recomputed the three pooled classical coverages from
`results/round3/B2_semisynthetic/b2_coverage.csv`: 0.044 spot i.i.d., 0.913 donor cluster-robust and
0.711 donor bootstrap. The Monte Carlo standard error of one cell's coverage at 200 draws is about
0.021.

**D4.** The layout anchor's benchmark-layout arm reproduces A1's CCRCC rows in 66 of 66 checks,
coverage exactly and widths to $2.1 \times 10^{-11}$, with no fold unmatched
(`results/round3/D4_expansion/d4_layout_anchor_a1_check.csv`); the lead checked those rows against
A1's committed tables. All four expansion task definitions pass the relaxed v1 schema and the
extension schema (`results/round3/D4_expansion/d4_task_defs_validation.csv`). The barcode integrity
check passes on 104 of 104 samples (`results/round3/D4_expansion/d4_barcode_integrity.csv`). All 55
Indiana fold gene selections hold 50 genes, none off-panel.

## 4. What differs between the arms of each comparison

Each list was written before the term was named, in the script docstring or the task definition,
and is reproduced from there.

**A4a.** All six scores share the task, design, fold, repeat, calibration draw,
proper-training set, calibration and test sets, base predictor, $\alpha$ and aggregation. `scaled`
adds a per-spot scale to `abs`. `scaled_clip` differs from `scaled` only in clipping that scale to
the 1st and 99th percentiles of the calibration set's own $\hat\sigma$. `cqr` replaces the symmetric
interval with two quantile regressions on the same features, conformalised on the same calibration
set. `nb` replaces the conformal quantile with a model level and is the only row without a
split-conformal guarantee. `nb_conformal` differs from `nb` only in reading the level off the
calibration set. Because CQR and NB ran on gene subsets, scores are compared on `cqr_matched`, the
cells and six genes CQR ran on, where the score function is the only difference but for one
residual: decile boundaries for `abs` and `cqr` come from the CQR job and for the other four scores
from the main job (`results/round3/A4_scores/a4_difference_lists.csv`). The HCP row differs from the
A4a rows in level and weighting; the oracle row differs from `abs` in using the test slide's own
offset and order statistic, both from test labels.

**A4b, the four intervals.** Identical: task, fold, proper-training set, base head, calibration
spots, test spots, the `abs` score, $\alpha = 0.10$ and the aggregation chain. Different: only what is
done with the calibration scores. The pooled quantile ignores donors. HCP gives each of the $K$
calibration donors and the test point equal mass. The Dunn-Wasserman-Ramdas interval keeps one spot
per donor. The `random` control is the same three with the spot as the unit, where they coincide.
**$K = 6$ against $K = 10$.** Identical: folds, seeds, the permutation of donors, the matched
training-spot count. Different: four donors move from training to calibration, so training falls
from 17 donors to 13 (plan section 13.10 item 1) at the same number of training spots. **24 donors
against `INT4` and `INT24` merged.** Different: 23 folds instead of 24, 22 donors in the pool instead
of 23, 12 training donors instead of 13; the fold sets are not paired.

**B1.** Classical against PPI differ only in whether the unlabelled donors' predictions enter
through the rectifier; PPI at $\lambda = 0$ is the classical estimator. The three variances differ
only in how the same per-spot influence contributions are aggregated and in the reference
distribution. The permuted arm differs from the encoder arms only in the order of resnet50's
predictions across spots. The spot-weighted and donor-weighted populations differ in the population
over which the estimand is defined, and so in the design constants and the influence function.
**B2, PRAD donor masking against slide masking.** Different: the masked unit, whether $U$ and $L$
are disjoint at donor level, the cluster count, and so the cluster-variance form.

**D4.1, benchmark layout against HEST-1k layout.** Identical: the 24 samples, folds, donor grouping,
50 genes, seeds, calibration rule, size-match target, base predictor, $\alpha$, aggregation, and the
expression, with maximum count difference 0.0 on every shared barcode. Different: the pixels, and
the spot sets, since the HEST-1k layout drops 407 of the benchmark's 74,220 CCRCC spots and adds none
(`results/round3/final_report/final_report_numbers.csv`). No arm separates the two.

**D4.2, Indiana `donor`.** Different: donor, disease (reference, diabetic kidney disease, acute
kidney injury), region where stated, section and capture area. Fixed: laboratory, instrument,
objective, preservation and pixel size.

**D4.3, kidney `population_out`.** Nine differences at once, listed before the term was named
(`results/round3/D4_expansion/task_defs/KIDNEY_POP54.json`): tissue state, anatomical region,
disease, preservation in part, laboratory, instrument, objective, pixel size, and the pixel-size
provenance flag. It is therefore a population-and-source shift and never a laboratory term.

**D4.4, breast Xenium `donor`.** Different: donor, disease, block source, instrument generation for
some pairs, run date and slide. Fixed: laboratory, platform, panel family and preservation. No source
term is reported from this set.

## 5. Predictions against outcomes

The round's predictions come from three documents: the execution handoff, transcribed as plan
sections 4.3 to 4.10; the A1 memo's section 9; and the A3 memo's section 10. Each was written into
the plan before the stage it concerns ran. Rows are grouped by source and quote the prediction in its
source's wording, shortened only where marked. Verdicts are **held**, **partly held**, **refuted** or
**not tested**, with the reason for the last.

### 5.1 The execution handoff (plan sections 4.3 to 4.10)

A1's six rows were scored in `docs/round3_A1_stage_report.md` section 5 from
`results/round3/A1_coverage/a1_coverage_by_design.csv`,
`results/round3/A1_coverage/a1_coverage_by_calibration_unit.csv`,
`results/round3/A1_coverage/a1_encoder_quality_correlation.csv` and
`results/round3/A1_coverage/a1_idc_label_sets.csv`, and are carried unchanged.

| # | stage | prediction | outcome | verdict |
|---|---|---|---|---|
| H1 | A1 | `random` at nominal for every task and encoder | pooled 0.8986 to 0.9018 over 30 cells | held |
| H2 | A1 | `patient` and `donor` under-cover, worst on PRAD and SKCM patient folds and COAD under shipped labels; COAD improves under `donor` | under-coverage and the COAD half held; PRAD is among the best tasks, not the worst | partly held |
| H3 | A1 | coverage near nominal under `donor` only where the calibration unit is the donor | donor-calibrated 0.851, block 0.686 | held |
| H4 | A1 | `slide_out` between `random` and `donor`; donor-sharing calibration does better | held on both halves | held |
| H5 | A1 | under-coverage larger for weaker encoders; same ordering across designs | ordering held for all 12 encoders; the quality relationship did not | partly held |
| H6 | A1 | IDC under audited labels under-covers more than under shipped labels | audited covers higher, not lower; the audited label set is now superseded | refuted |

A2's four rows are read from `docs/round3_A3_stage_report.md` sections 6.3, 6.4 and 6.7, whose
sources are `results/round3/A2_conditional/a2_level_scale.csv`,
`results/round3/A2_conditional/a2_by_stratum.csv` and
`results/round3/A2_conditional/a2_pergene_join.csv`. The A3 rows are read from
`results/round3/A3_report_numbers.csv`.

| # | stage | prediction | outcome | verdict |
|---|---|---|---|---|
| H7 | A2 | shortfall under `donor` is mostly level | the larger share is scale in all five groups | refuted |
| H8 | A2 | gene-level shortfall correlates positively with the per-gene split penalty | Spearman positive on 6 task files and negative on 5, from −0.1853 to +0.4694 | refuted |
| H9 | A2 | coverage is worse in the predicted-value tails | worse in the upper tail only, 0.6777 in the top decile against 0.8825 in the bottom | partly held |
| H10 | A2 | session-unsupported folds on PRAD and SKCM are the worst stratum | session is recorded only for PRAD's patient 2, so the stratum cannot be formed for SKCM; sharing a session has no consistent sign | not tested as stated |
| H11 | A3 | reweighting restores coverage where $n_{\text{eff}}$ stays high and not where it collapses | $n_{\text{eff}}$ collapsed everywhere, a median 2.13% of calibration size | refuted |
| H12 | A3 | coverage gain is monotone in $n_{\text{eff}}$ | there is no high-$n_{\text{eff}}$ range to test it on | not tested |
| H13 | A3 | W1 beats W2 within a covariate cell and they agree between cells | W2 has no support in 18 of 18 cells on each of PRAD and SKCM `patient` | not tested |
| H14 | A3 | the scaled score narrows intervals at matched coverage | at matched coverage `scaled` is 14.83 wide against 2.69 for `abs`, and `scaled_clip` 14.71 | refuted |

A4's handoff rows are A4a's, read from `results/round3/A4_scores/a4_report_numbers.csv`, `results/round3/A4_scores/a4_width_at_coverage.csv` and `results/round3/A4_scores/a4_by_decile.csv`. B2's rows are read from
`results/round3/B1_ppi/b1b2_report_numbers.csv` and `results/round3/B2_semisynthetic/b2_coverage.csv`.

| # | stage | prediction | outcome | verdict |
|---|---|---|---|---|
| H15 | A4 | NB intervals under-cover under `donor` in the same pattern as the conformal ones, and conformalising restores marginal coverage | under `donor` NB covers 0.7104 against 0.8392 for `abs`, with the same ordering across designs; `nb_conformal` covers 0.9066 on `random` | held |
| H16 | A4 | CQR and `scaled` are narrower than `abs` at matched coverage, most on the Xenium tasks | CQR 2.6461 against 2.6930 for `abs` at matched coverage; `scaled` 14.83; the Xenium contrast was not computed | partly held; the `scaled` clause is refuted |
| H17 | A4 | conditional dispersion is well below the marginal Fano factor but far from zero | $\hat\alpha_g$ below the marginal dispersion in every fit, median ratio 0.0468, and exactly zero in 10.58% of fits | partly held |
| H18 | B2 | spot i.i.d. intervals cover far below 0.90 for both estimators | 0.044 over all classical cells | held |
| H19 | B2 | donor cluster-robust intervals cover near 0.90 for $n_L \ge 8$ and below for $n_L$ of 4 or 6 unless the $t$ reference is used | with the $t$ reference, 0.898 to 0.900 at $n_L = 6$ and 0.938 to 0.949 at $n_L = 12$ on CCRCC | held, with over-coverage at $n_L = 12$ |
| H20 | B2 | the donor bootstrap behaves similarly | 0.711 against the cluster-robust 0.913 | refuted |
| H21 | B2 | the PPI width ratio is below 1 only for the better encoders and approaches 1 as the between-donor share grows; the permuted predictor's ratio is at or above 1 everywhere | first two clauses held in the donor-weighted population; the permuted ratio is 0.984 there and 0.760 spot-weighted | partly held |

D4's handoff rows were written for a `lab_out` decomposition that the A3 memo's decision 4 removed.
They are scored against what D4 ran, from `results/round3/D4_expansion/d4_pooled_numbers.csv` and
`results/round3/D3_audit/donor_audit_r3.csv`.

| # | stage | prediction | outcome | verdict |
|---|---|---|---|---|
| H22 | D4 | the lab term is at least as large as the patient-identity term on the benchmark | no laboratory term exists in HEST-1k with disease fixed; no `lab_out` arm was run | not tested |
| H23 | D4 | it is not explained by tissue composition; the morphology adjustment removes a minority | for the kidney population-and-source contrast, morphology removes 31% to 34% of the above-chance probe signal | held, for a population-and-source term rather than a laboratory term |
| H24 | D4 | lab is decodable from embeddings well above chance under spatial-block CV | population is decodable at balanced accuracy 0.99997 under both spatial blocks and slide hold-out | held, for population rather than laboratory |
| H25 | D4 | some of HEST's lab or donor labels in the sets are wrong | `TENX95` was misassigned in round 2; Indiana's embedded pixel size is contradicted; four papilla samples are contradicted mixtures | held |

### 5.2 The A1 memo (section 9)

Scored in `docs/round3_A3_stage_report.md` section 5 from `results/round3/A3_report_numbers.csv` and
the A2 files named there, and carried unchanged. Row 7 is summarised; the A3 report gives each clause.

| # | stage | prediction (shortened) | outcome | verdict |
|---|---|---|---|---|
| M1.1 | A2b | block calibration under-covers by 0.10 to 0.20; unit calibration reproduces A1 | unit reproduces A1; block is lower in 138 of 138 cells but in the band in 31.9% | partly held |
| M1.2 | A2c | shortfall grows with the between-unit share and shrinks with $K$; the simulation reproduces fold means; block folds sit below | first clause wrong in sign; second and third held | partly held |
| M1.3 | A2a | `scaled` has lower across-slide sd than `abs` on every task; PRAD's under-covering fold is calibrated on patient 2 and has the smaller share | 10 of 11 task files; the fold is right; its share is the larger | partly held |
| M1.4 | A2d | same-donor calibration covers a few points higher within PRAD | two contrasts disagree and measure different things | not settled |
| M1.5 | A2e | width orders with Pearson under every design; coverage range under 0.02 | held for mean width and for the range; not for median width | partly held |
| M1.6 | A2f | block folds fail on level; unit folds without a consistent sign | block folds fail on scale; unit folds carry a positive miss asymmetry | refuted |
| M1.7 | A3 | W1 collapses $n_{\text{eff}}$; W1b does not; W2 has no support on PRAD and SKCM `patient`; W3 as stated; nothing repairs the two-sample tasks | W1 and W2 clauses held; W1b and the W3 parenthetical failed; the two-sample clause held in substance | partly held |
| M1.8 | D3 | the breast source is one laboratory; `TENX98` and `TENX99` are the replicate pair; the Washington University samples split into healthy and diseased donors | first two held; the third was overtaken, the samples are from Indiana | partly held |

### 5.3 The A3 memo (section 10)

A4a's rows are read from `results/round3/A4_scores/a4_report_numbers.csv`, `results/round3/A4_scores/a4_width_at_coverage.csv` and `results/round3/A4_scores/a4_by_decile.csv`; row 5 from `results/round3/A4_scores/a4b_summary.csv`; rows 6
and 7 from `results/round3/B1_ppi/b1b2_report_numbers.csv` and `results/round3/final_report/final_report_numbers.csv`; rows 8 to 11 from
`results/round3/D4_expansion/d4_pooled_numbers.csv`.

| # | stage | prediction | outcome | verdict |
|---|---|---|---|---|
| 1 | A4a | `scaled_clip` narrows the mean width of `scaled` by more than half at equal coverage; the median barely moves | mean width ratio 0.9887; 1 of 1,320 cells narrows by more than half; median 2.2419 to 2.2322 | refuted; the median clause held |
| 2 | A4a | the top-decile shortfall (0.68 under `abs`) closes to within 0.05 of nominal under `cqr` and `nb_conformal` and stays under `abs` | on matched cells `abs` 0.7224, `cqr` 0.8747, `nb_conformal` 0.8668; the margin is missed only by `cqr` under `donor` (0.8479) and `nb_conformal` under `slide_out` (0.8105) | held pooled, with two per-design exceptions |
| 3 | A4a | NB intervals under-cover under `donor` in the same pattern as `abs`; conformalising restores marginal coverage; $\hat\alpha_g$ is well below the marginal Fano factor and above zero | NB 0.7104 against `abs` 0.8392 under `donor`; `nb_conformal` 0.9066 on `random` and 0.8542 under `donor`; $\hat\alpha_g$ at a median 0.0468 of the marginal but exactly zero in 10.58% of fits | held, except that $\hat\alpha_g$ is zero rather than above it in a tenth of fits |
| 4 | A4a | the recentred oracle is 20 to 40% narrower than `abs` at 90% on unit-calibrated slides | width ratio to `abs` 0.8617 on unit-calibrated folds and 1.4717 on block-calibrated folds | refuted in magnitude, right in direction |
| 5 | A4b | HCP finite in every fold, mean coverage 0.92 to 0.95, width ratio 1.2 to 1.6 to the pooled quantile; the pooled quantile stays near 0.86; one-per-group covers at nominal with wide dispersion | finite in every cell; coverage 0.9692, inside the $[0.90, 0.90 + 2/11)$ bound but above 0.92 to 0.95; width ratio 1.947; pooled 0.8644; one-per-group 0.9109 | partly held; the width clause is refuted |
| 6 | B1 | spot i.i.d. standard errors are smaller than donor-clustered ones by a factor of five or more on CCRCC; $\lambda$ between 0.3 and 0.9 for the encoders and near 0 for the permuted predictor | factor 29.0 to 67.6; $\lambda$ 0.63 to 0.74 at $n_L = 6$, falling below 0.3 at 8 and 12; permuted $\lambda$ exactly 0 donor-weighted and 0.61 spot-weighted | partly held |
| 7 | B2 | spot i.i.d. intervals cover under 0.6; cluster-robust with $t$ covers 0.85 to 0.92 at $n_L \ge 8$; PPI width ratio below 1 only for the better encoders and rising toward 1 as the share grows | 0.044; 0.906 and 0.925 at $n_L = 8$, 0.938 and 0.949 at 12; the ratio clauses hold donor-weighted and fail spot-weighted | partly held |
| 8 | D4.1 | the layout anchor moves Pearson by less than 0.01 and coverage by less than its across-fold dispersion | largest Pearson move 0.0064, largest coverage move 0.0019, both inside in 9 of 9 cells | held |
| 9 | D4.2 | Indiana `donor` at 25% covers 0.85 to 0.88; HCP at $K = 10$ finite and at or above 0.90 | 0.8778, in the band for 3 of 3 encoders; HCP finite in 225 of 225 cells at 0.9882 | held |
| 10 | D4.3 | `population_out` covers at or under 0.70; the population probe is at ceiling and composition explains a majority of it | 0.7032 testing on ccRCC and 0.9053 testing on Indiana; probe 0.99997; composition explains 31% to 34% | partly held; the composition clause is refuted |
| 11 | D4.4 | breast `donor` covers 0.82 to 0.87; prototype-instrument test slides cover lower when calibration has no prototype slide | 0.8861, above the band; prototype 0.8104 against production 0.8948 | half held |

## 6. Results

### 6.1 H1

`README.md` property 1 is rewritten per the memo. IDC's four samples are four donors, and the
`TENX95` against `TENX99` partner confusion is read as two donors from one laboratory, instrument,
panel and pixel size run three weeks apart, the session signature of finding 3 in a second task.
R5c's $+0.0652$ is kept and renamed as the value of a same-laboratory, same-instrument slide in the
training pool across donors; READ's $+0.0901$ is the only same-specimen replicate figure. Property 11
records the D2 layout difference and, from this report, the layout anchor's outcome (section 6.5).
Known limitations 14 to 18 are added. `docs/hest_bench_issue_draft.md` has its IDC item struck with a
dated note and stays unsent. `docs/WAYS_OF_WORKING.md` gains the three notes of plan section 13.4 item
5. `docs/r5_idc_provenance.md` gains a one-line banner and is otherwise unedited.

The two reading items settled less than hoped. The Immunity paper (Meylan et al. 2022, doi
10.1016/j.immuni.2022.02.001) is not reachable by any open route tried, so no patient table was read.
GEO series GSE175540 lists 24 samples with 24 distinct titles and maps one to one onto CCRCC's
`INT1` to `INT24`, but carries no donor field. CCRCC's count of 24 is corroborated at sample level
and not at donor level, and `donor_audit_r3.csv` says exactly that
(`results/round3/D3_audit/donor_audit_r3_overrides.csv`). Whether `INT4` and `INT24` are one donor
stays open, which is why every CCRCC analysis in B1, B2 and A4b ran both ways.

### 6.2 A4a, scores and the model-based comparator

From `results/round3/A4_scores/a4_report_numbers.csv`, `results/round3/A4_scores/a4_width_at_coverage.csv`,
`results/round3/A4_scores/a4_by_decile.csv`, `results/round3/A4_scores/a4_oracle_recentred.csv` and
figure `results/round3/A4_scores/fig_a4_width_at_coverage.png`. CQR ran on 6 of 50 genes and NB on
16, so every CQR and NB number below is at that scope (section 7 item 10), and scores are compared on
the matched subset unless stated.

**The first comparison.** Over 1,320 cells on the full gene set, `abs` covers 0.8562 at mean width
2.2117 and median 2.0807; `scaled` covers 0.8630 at 3.9416 and 2.2419; `scaled_clip` covers 0.8629 at
3.8882 and 2.2322. The mean per-cell width ratio of `scaled_clip` to `scaled` is 0.9887, so the clip
removes about a hundredth of the width. The clip binds on almost every fold and changes almost
nothing, because it acts at the 1st percentile of $\hat\sigma$ while the width is driven by small
$\hat\sigma$ values above that percentile (`results/round3/A4_scores/a4_sigma_clip.csv`). The gap
between `scaled`'s mean and median width is where the defect lives.

**Width at matched coverage, the primary table.** On the matched subset at the nominal level,
`abs` covers 0.8357 at mean width 2.4401 and median 2.2428, `cqr` 0.8381 at 2.3919 and 2.1943, and
`nb_conformal` 0.8528 at 1.8552 and 1.7475. At the level whose realised coverage is 0.90, a
diagnostic because that level is chosen with test labels, `abs` is 2.6930 wide in the mean, `cqr`
2.6461, `nb_conformal` 1.9556, and `scaled` 14.8325. The NB pair at 0.90 rests on 20 of 96 cells,
because the NB model level never reaches 0.90 on the rest, and is provisional. HCP at
$\alpha = 0.20$ on CCRCC `donor`, taken from A3's table without a rerun, covers 0.9143 at mean width
2.7613.

**The predicted-value deciles.** In the top decile on identical cells and genes, `abs` covers
0.7224, `scaled` 0.8290, `scaled_clip` 0.8205, `cqr` 0.8747, `nb` 0.7405 and `nb_conformal` 0.8668.
The upper-tail failure A2 found is the one place where an adaptive score buys a large gain.

**The NB head.** Under `donor` the model-based interval covers 0.7104 at width 1.3181, against
`abs` at 0.8392 and 2.6348 and `nb_conformal` at 0.8542 and 1.9196. The estimated dispersion
$\hat\alpha_g$ has median 0.2082 and is below the marginal dispersion in every fit, but it is
exactly zero in 10.58% of fits, concentrated on the smaller tasks. The mechanism is the in-sample
residual the plan specifies. On those tasks the mean head absorbs more than Poisson noise, and the
same estimator on calibration residuals has median 0.7434 (`results/round3/A4_scores/a4_nb_dispersion.csv`).

**The recentred oracle.** Recentring `abs` on the test slide's own offset $b_s$ and giving it the
half-width that yields 0.90 on that slide leaves it 0.8617 as wide as `abs` on unit-calibrated
folds, over 66,000 slide-gene cells, and 1.4717 as wide on block-calibrated folds. On unit-calibrated
slides the mean $|b_s|/s_y$ is 0.5245, reproducing A2. Block folds need a wider interval, not a
recentred one, which is A2's scale finding seen from the oracle side.

### 6.3 A4b, HCP with $K = 10$ on CCRCC

`results/round3/A4_scores/a4b_summary.csv`, `results/round3/A4_scores/a4b_hcp_K10.csv`, figure
`results/round3/A4_scores/fig_a4b_hcp_K10.png`.

With 24 donors, 216 fold-draw-encoder cells at $K = 10$: the pooled quantile covers 0.8644 at mean
width 2.111; HCP covers 0.9692 at width 4.109, a ratio of 1.947 to pooled; the one-per-group
subsample covers 0.9109 at a ratio of 1.430. The pooled quantile at $K = 6$ on the same folds covers
0.8642, so four more calibration donors move it by $+0.0003$. With `INT4` and `INT24` merged the three
cover 0.8604, 0.9662 and 0.9047; the merge does not change the reading. Every HCP and one-per-group
cell is finite. The `random` control reproduces the pooled quantile, as it must when every group is
one spot.

Three readings follow. First, HCP's guarantee is real and costly. At $K = 10$ it is finite and inside
its theoretical bound $[1 - \alpha, 1 - \alpha + 2/(K+1))$, but it over-covers by about seven points
at about twice the pooled width. Second, the pooled quantile's shortfall of about 3.6 points is not a
$K$ effect, which settles the A3 memo's reading of mechanism (a) from a second direction. Third, the
cost of taking four donors out of training is small in the mean, $-0.0052$ in Pearson over three
encoders, but at fold level more than a third of fold-draw-encoder cells move by more than 0.02.

### 6.4 B1 and B2, prediction-powered inference under donor clustering

**Positioning.** Two 2026 papers put prediction-powered inference in a spatial setting and neither
covers the case measured here. Salerno, Wu and McCormick (arXiv:2603.11368) take labels missing at
random and derive a jackknife spatial HAC variance that separates spatial dependence from the
correlation cross-fitting induces; units nested in groups are not treated. Shirota
(arXiv:2608.10356) recasts PPI design-based, with exact design variances under simple and
stratified sampling, and refers clustered labelling to other work. Neither mentions spatial
transcriptomics. Here the label is a whole donor, the unit of inference is the donor, and the donor
count is 24 at best and 2 at worst. The nearest relative is Fisch et al. (arXiv:2406.04291), read
first as plan section 13.6 requires. StratPPI assumes every stratum holds both labelled and
unlabelled examples, and under the donor design that fails by construction, because a donor is
labelled or it is not. The donor is a cluster, not a stratum. B1 therefore keeps one scalar
$\lambda$ and puts the donor structure in the variance, summing influence contributions within a
donor, applying the $G/(G-1)$ correction separately to the disjoint $U$ and $L$ terms, and using a
$t_{G-1}$ reference, following Cameron and Miller (2015) and MacKinnon, Nielsen and Webb (2023).

**The size of the problem.** From `results/round3/B1_ppi/b1b2_report_numbers.csv` and
`results/round3/B1_ppi/b1_estimates.csv`: on CCRCC $\theta_3$ the median ratio of the donor-clustered
to the spot i.i.d. standard error is 29.0, 35.8 and 32.0 at $n_L = 6$, 8 and 12 in the spot-weighted
population and 44.9, 67.6 and 54.9 in the donor-weighted one. IDC's $\theta_1$, the correlation of
mean nuclear area with GATA3 under the four-donor labels, is the illustration. Per slide it is
−0.456, −0.701, +0.526 and +0.872, four intervals that each exclude zero, two of each sign. Pooled
it is +0.372, with a spot i.i.d. interval of width 0.0185 and a donor-clustered interval of width
1.084 on 3 degrees of freedom, 59 times wider and spanning zero
(`results/round3/B1_ppi/b1_theta1_by_slide.csv`, figure `results/round3/B1_ppi/fig_b1_intervals.png`).

**$n_{\text{eff}}$ beside the $K \ge 9$ condition.** With $m$ spots per donor and between-donor
share $\rho$, the variance of a mean is inflated by $1 + (m-1)\rho$, so $n_{\text{donors}} \times m$
spots are worth about $n_{\text{donors}}/\rho$ donor-equivalents. Read backwards from B1's two
variances, CCRCC's implied share is 0.30 to 0.32 spot-weighted, giving 20 to 38 donor-equivalents
from 6 to 12 labelled donors. HCP needs $K + 1 \ge 1/\alpha$ exchangeable groups, $K \ge 9$ at
$\alpha = 0.1$, and no number of spots inside a group substitutes for a group. The same integer
limits both stages, and A4b measures its conformal side: at $K = 10$ on CCRCC, HCP is finite in every
cell and covers 0.9692, where at $K = 6$ it was infinite (`results/round3/A4_scores/a4b_summary.csv`,
`results/round3/A3_report_numbers.csv`).

**PPI's $\lambda$.** Median over genes on CCRCC $\theta_3$, spot-weighted, it is 0.63 to 0.74 at
$n_L = 6$ over the three encoders and falls to 0.29 to 0.34 at 8 and 12. Donor-weighted it is 0.44 to
0.54 at 6 and 0.09 to 0.22 above. The permuted arm's $\lambda$ is exactly 0 donor-weighted and 0.61,
0.29 and 0.23 spot-weighted, indistinguishable from the encoders, for the reason in section 7 item 4
(`results/round3/B1_ppi/b1b2_report_numbers.csv`).

**B2 coverage.** From `results/round3/B2_semisynthetic/b2_coverage.csv`, recomputed by setting in
`results/round3/final_report/final_report_numbers.csv`, and figure
`results/round3/B2_semisynthetic/fig_b2_coverage.png`, 200 crc32-seeded labelled-donor sets per
setting, pooled over 6,306 classical cells: spot i.i.d. 0.044, donor cluster-robust 0.913, donor
bootstrap 0.711. On CCRCC the cluster interval covers 0.900, 0.925 and 0.949 spot-weighted and 0.898,
0.906 and 0.938 donor-weighted at $n_L = 6$, 8 and 12; with `INT4` and `INT24` merged it covers 0.902,
0.934 and 0.947 and 0.901, 0.905 and 0.941. LYMPH_IDC at $n_L = 2$ covers 0.888 and 0.872 under the
cluster variance and 0.560 and 0.557 under the bootstrap. PRAD at $n_L = 1$ covers 0.000 under every
variance; with one donor degree of freedom nothing is available, as Cameron and Miller state. The
PRAD slide-masking variant keeps both donors labelled and covers 0.769, 0.948 and 0.981 at 4, 8 and
12 labelled slides, too short at one end and too long at the other.

**B2 width.** From `results/round3/B2_semisynthetic/b2_width_ratio.csv`, pooled by arm in
`results/round3/final_report/final_report_numbers.csv`: for $\theta_3$ the mean PPI-to-classical
cluster width ratio over genes and $n_L$ on CCRCC donor-weighted is 0.845 (uni_v2), 0.874 (hoptimus0), 0.891 (resnet50)
and 0.984 (permuted), and spot-weighted 0.717, 0.718, 0.733 and 0.760. A gene's donor-design Pearson
and its $\theta_3$ width ratio correlate at −0.60 to −0.72 by Spearman over 200 arm-gene cells at
each $n_L$ (`results/round3/B1_ppi/b1b2_report_numbers.csv`), so better-predicted genes gain more. On
LYMPH_IDC, where the leave-one-donor-out predictor is worse than the mean, the spot-weighted ratio is
1.78 to 2.06.

### 6.5 D4, the expansion

**The layout anchor, first** (`results/round3/D4_expansion/d4_layout_anchor.csv`, figure
`results/round3/D4_expansion/fig_d4_layout_anchor.png`). Moving CCRCC from the benchmark's embeddings
to HEST-1k-layout embeddings moves coverage by at most 0.0019 and within-slide Pearson by at most
0.0064 over nine encoder-design cells. Every coverage move is inside its own across-fold dispersion.
Under `donor` the mean coverage goes from 0.8642 to 0.8629. The expression is identical on every
shared barcode, and the HEST-1k layout keeps 99.45% of the benchmark's spots, a strict subset
(`results/round3/final_report/final_report_numbers.csv`). No
benchmark result moves with the layout, so D2's layout finding stays a property of the public data,
and D4's other arms can be set beside benchmark numbers through this anchor. README property 11 is
extended with this outcome.

The remaining numbers come from `results/round3/D4_expansion/d4_pooled_numbers.csv`, figure
`results/round3/D4_expansion/fig_d4_expansion_arms.png`.

**Indiana, the second multi-donor task.** 25 donor units from one laboratory, instrument and
objective, fresh frozen throughout. `random` covers 0.8883; `donor` at the 25% rule covers 0.8778,
0.8766 to 0.8786 over encoders, with a mean across-fold sd of 0.0416. At CCRCC's A4b design with
$K = 10$ the pooled quantile covers 0.8871 and HCP 0.9882 at 1.907 times the width, finite in 225 of
225 cells. Donor shift here costs about one point of coverage, against about four on CCRCC. The
per-gene penalty from `random` to `donor` tracks the gene's between-donor variance share at Spearman
0.623. Set beside the anchor, the fold-to-fold scatter under `donor` is about a third of CCRCC's.
With laboratory, instrument and preservation fixed, donor novelty costs less coverage and less
variance than it does on CCRCC. That is a contrast between two tasks that differ in many ways, not a
measured source effect.

**Kidney `population_out`, a population-and-source shift.** Size-matched at 22,212 training spots.
Trained on the Cordeliers ccRCC samples and tested on Indiana's non-tumour samples, coverage is
0.9053. Trained on Indiana and tested on ccRCC it is 0.7032, with misses above the interval at
0.2543 against 0.0425 below. The asymmetry is the finding. The population probe separates the two at
balanced accuracy 0.99997 under slide hold-out and under spatial blocks. The eight morphology
covariates bring it to 0.8288 and 0.8443, removing 34% and 31% of the above-chance signal, a majority
in none of the three encoders. The two populations differ in nine ways at once (section 4), and the
probe's ceiling is a statement about all nine together.

**Breast Xenium, one laboratory, two instrument generations.** `donor` covers 0.8861 and `random`
0.8877. Prototype-instrument test slides cover 0.8104 against 0.8948 for production-instrument
slides, lower for all three encoders. The stratum gives the same reading by sample (3 against 15)
and by donor group (2 against 13), per plan section 13.10 item 3. This is round 2's session finding in
a fourth setting. By disease, coverage is 0.9208 for columnar cell hyperplasia with DCIS, 0.8831 for
DCIS and 0.8751 for IDC.

## 7. Discrepancies, open questions and escalations

Handled under the decision boundaries (plan section 13.8) during the interval and recorded here, as
the gate rule requires. None stopped work.

1. **Plan section 13.10's five flags, as they resolved.** (i) A4b trains on 17 donors, not 18, and
   falls to 13; with `INT4` and `INT24` merged, to 12. (ii) The round-3 audit file duplicates 28
   samples, and after the memo's own IDC correction the two rows disagree on 26, not 28, because
   `TENX95` and `TENX99` now agree across origins (`results/round3/D3_audit/donor_audit_r3_conflicts.csv`).
   Section 13.10 item 2 says 28 and is left as transcribed. (iii) The breast stratum is 3 against 15
   samples and 2 against 13 donor groups; both are reported. (iv) README property 11 cites the
   per-encoder anchor files and `A3_report_numbers.csv`, not the resnet50-only consolidated file.
   (v) The four contradicted papilla samples stay in the `population_out` test set as spots and in
   no donor unit.
2. **`results/round2/R5c_leak/r5c_leak_summary.csv` still records IDC's
   `leak_realised_in_shipped_split` as True**, and its `share_of_gap` label is now the wrong name for
   a correct number. It is a frozen round-2 file. README records the corrected reading; whether to
   correct round-2 files is above this session.
3. **README known limitation 8** still describes the H-Optimus-1 `raw_ridge` cell as a dash, while
   the table above it shows 0.2859. H1 was told to leave that sentence untouched, so it needs an edit
   by whoever owns it.
4. **B1's fourth acceptance check cannot hold as a strict inequality**, because $\hat\lambda$
   minimises the estimated variance and $\lambda = 0$ is feasible. More substantively, a permutation
   cannot build a useless predictor for a covariance-type estimand. $\theta_3$'s and $\theta_2$'s
   spot-weighted influence functions multiply the outcome by a known covariate weight that permuting
   the predictions leaves in place. In the donor-weighted population, whose unit is Topic B's, the
   check passes with $\lambda$ exactly 0.
5. **Four B1 method choices a reader could have made differently.** $\lambda$ is tuned on the
   spot-level variance, since tuning on donor-clustered residuals drives the variance to zero at
   $G_L = 2$. The donor-weighted $\lambda$ is fixed at 0 below four labelled donors. The classical
   estimator uses the known-design moments. 4.6% of spots lack a morphology row and are excluded.
6. **D4's task-definition schema had to be extended.** The committed v1 schema forbids additional
   properties, so the columns plan section 13.7 requires could not be added. D4 wrote
   `results/round3/D4_expansion/task_defs/task_def_ext.schema.json` and validated against both.
   Whether v1 or a v2 absorbs them is above this session.
7. **The memo's breast panel size is wrong.** It says 280 genes. The 18 samples share 151
   (`results/round3/D4_expansion/task_defs/BREAST_XENIUM.json`), and after
   HEST's 10% minimum-cells filter 90 remain on every fold
   (`results/round3/D4_expansion/d4_breast_fold_genes.csv`). No D4 number rests on 280.
8. **Two D4 memo statements are refuted beside their predictions.** Indiana's scatter is not "the same
   as CCRCC" but about a third of it. `population_out` is not "a floor for coverage" in the
   Cordeliers-to-Indiana direction, which at 0.9053 is easier than CCRCC's own `donor` design.
9. **Script md5 mismatches**, declared in section 2 and accepted as output-neutral rather than rerun.
10. **A4a's reduced scope.** CQR ran on 6 of 50 genes and on the first calibration draw and repeat of each fold,
    with the training set subsampled to 2,500 spots where it was larger, against the plan's
    20,000-spot fallback, and resnet50 CCRCC `donor` reached 11 of 24 folds inside its budget
    (`results/round3/A4_scores/a4_cqr_fits.csv`). The NB head ran on 16 of 50 genes with the
    newton-cholesky solver. Every CQR and NB number in this report is at that scope.
11. **The Immunity paper is unreachable**, so CCRCC's donor count is unsourced at donor level
    (section 6.1).
12. **Cross-node determinism.** The memo's "about $3 \times 10^{-6}$ in widths" is, in the file,
    9.5e-07 in widths and 2.9e-06 over all compared columns
    (`results/round3/H0_determinism/determinism_diff.csv`). `docs/WAYS_OF_WORKING.md` records the
    file's numbers.
13. **`d3_notes.md` says "five weeks"** between the `TENX95` and `TENX97` runs, while its own table
    gives 22 days. The memo's "three weeks" agrees with the table; `d3_notes.md` is not edited.
14. **Longleaf facts for whoever maintains the compute notes.** Under the job-submission route used
    here, `$SLURM_SUBMIT_DIR` is the home directory, not the job's working directory, and two D4 jobs
    lost their outputs to it. `jsonschema` is not installed in the project environment. The
    per-provider compute notes are full and refused both facts.
15. **A4a's decile merge** kept one job's partial aggregate where two jobs wrote the same key, and
    was fixed before commit (section 3). Two residuals remain inside the matched subset: decile
    boundaries differ between the CQR job's scores and the other four, and `abs` carries fold rows
    the CQR job never reached. Both are measured in the A4a hand-back and are small beside the
    top-decile gaps reported. A4a's NB PIT also fails the stage's own uniformity threshold on the
    nine smaller tasks, which is reported rather than adjusted.
16. **Two job ids in the A4a hand-back do not exist in `sacct`** (section 2). The job table in
    `results/round3/final_report/interval3_jobs.csv` is built from `sacct` and is authoritative.
17. **`rc_tengfei_pi`.** Nicolas was added to this account on 23 September. His Slurm association did
    not list it at transcription time, and no job used it.
18. **A false floating-point example in the A4b record.** The A4b hand-back and the docstring of
    `code/scripts/round3_a4b_hcp.py` justify passing $(K - 0.5)/n_{\text{units}}$ to the harness by
    saying `10/23 * 23` evaluates to `10.000000000000002`. It evaluates to exactly 10.0. The hazard
    the guard protects against is real for other pool sizes, and the guard is correct for all of
    them, so no A4b number is affected. The docstring is left as committed, because editing it would
    change the md5 recorded in section 2. A background review flagged the claim after the first
    version of this report was tagged.

## 8. What was not checked

- Why HEST-1k's patching drops a spot, per the memo's decision 3.
- Whether the layout anchor's 0.0019 coverage move comes from the pixels or from the 0.55% spot
  subset; an arm on the shared spots only would separate them.
- The CCRCC per-gene split penalty, so prediction 9's clause "smaller than CCRCC's" is unevaluated.
- Any score other than `abs` in A4b and D4, any $\alpha$ other than 0.10 in A4b, and any $K$ other
  than 6 and 10.
- Whether HCP's over-coverage is level, scale or asymmetry; `miss_above` and `miss_below` are in
  every A4b row and were not decomposed.
- B2 coverage against a superpopulation parameter. B2's coverage is of the full-data value of this
  donor set over repeated labelling, a design-based statement.
- Any studentised or bias-corrected bootstrap; the percentile bootstrap's small-$G$ failure says
  nothing about BCa.
- A cross-fitted $\lambda$, and any sensitivity to $\theta_2$'s thresholds of 0.7 and 0.3.
- The Indiana pixel size, taken from the audit's estimate rather than re-derived, and CellViT
  segmentation quality on the expansion samples.
- Whether `INT4` and `INT24` are one donor.
- The handoff's Xenium contrast for adaptive scores; A4a's interval-score and miss-asymmetry
  columns; residual diagnostics for the quantile and Poisson fits; and whether dropping the folds CQR
  never reached would change the matched comparison.
- Any statistical test on a difference in this report. The dispersions quoted are descriptive.

## 9. Proposed next step

None from this session. The round is tagged `round3-final` with this report and stops. The round-4
plan is the oversight chat's to write, and the escalations in section 7 are its inputs.

---

## What round 3 established

A spot-level uncertainty statement about histology-predicted expression is off by an order of
magnitude, because the unit that carries the variance is the donor. A donor-clustered standard
error is 29 to 68 times the spot i.i.d. one on CCRCC, and the i.i.d. interval covers 0.044 at nominal
0.90 (`results/round3/B1_ppi/b1b2_report_numbers.csv`). A donor cluster-robust interval with a
$t_{G-1}$ reference covers 0.913 pooled, and the donor bootstrap 0.711
(`results/round3/B2_semisynthetic/b2_coverage.csv`).

Conformal intervals under donor shift under-cover because of the calibration unit, not the
calibration size. Calibrating on held-out donors covers 0.8562 and on spatial blocks 0.7442, block
lower in 138 of 138 cells, and block intervals fail by being too narrow rather than misplaced
(`results/round3/A3_report_numbers.csv`, `results/round3/A2_conditional/a2_level_scale.csv`).

The pooled quantile's remaining shortfall is not a $K$ effect. It covers 0.8644 whether 6 or 10
donors calibrate it (`results/round3/A4_scores/a4b_summary.csv`).

Hierarchical conformal prediction is the valid fix once $K + 1 \ge 1/\alpha$, and it is conservative.
At $K = 10$ on CCRCC it covers 0.9692 at 1.947 times the pooled width
(`results/round3/A4_scores/a4b_summary.csv`), and on Indiana 0.9882 at 1.907 times
(`results/round3/D4_expansion/d4_pooled_numbers.csv`).

Feature-based weighting cannot repair donor or slide shift in this data, because calibration and
test slides are almost perfectly separable, with held-out AUC at least 0.9747, and the weights
collapse the effective calibration size to a median 2.13% (`results/round3/A3_report_numbers.csv`).

Adaptive scores buy little width at matched coverage. Clipping leaves the scaled score's
mean width at 0.9887 of itself, and CQR is 2.6461 wide against 2.6930 for `abs`. The one large gain
is in the upper tail, where CQR and conformalised NB lift top-decile coverage from 0.7224 to 0.8747
and 0.8668 (`results/round3/A4_scores/a4_report_numbers.csv`).

The benchmark's results do not move with HEST-1k's patch layout. Coverage moves by at most 0.0019 and
Pearson by at most 0.0064 (`results/round3/D4_expansion/d4_layout_anchor.csv`).

On a second multi-donor task with laboratory, instrument and preservation fixed, donor shift costs
about one point of coverage, 0.8883 against 0.8778, with a third of CCRCC's fold scatter
(`results/round3/D4_expansion/d4_pooled_numbers.csv`).

The kidney population-and-source shift is asymmetric. Training on ccRCC and testing on non-tumour
kidney covers 0.9053, the reverse 0.7032, and morphology explains about a third of a perfectly
separable probe signal (`results/round3/D4_expansion/d4_pooled_numbers.csv`). No laboratory term can
be measured in HEST-1k with disease held fixed (`README.md` known limitation 14).

Instrument generation is a session-like axis. On breast Xenium from one laboratory, prototype-instrument
slides cover 0.8104 against 0.8948 for production (`results/round3/D4_expansion/d4_pooled_numbers.csv`).

IDC's four benchmark samples are four donors, and the round-2 replicate-leak reading of IDC is
withdrawn (`results/round3/D3_audit/donor_audit_r3.csv`, `README.md` property 1).
