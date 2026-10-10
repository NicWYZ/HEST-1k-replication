# Round 1, faithful replication and instrumentation (12 to 16 September 2026)

The round replicated the HEST-1k benchmark on UNC Longleaf as the advisors' first assignment, then built an instrumentation layer (joined prediction tables, split, site, count and morphology diagnostics) for the later work on calibrated uncertainty and inference. One execution report closed it, and the oversight audit of 16 September answered that report.

**Tracks.** exec (no branch recorded in the sources, stages 0 to 5, with stage 5 set up but not trained). **Started from** no tag. The repository's first commit is `23885066` of 13 September, and the instruction is dated 12 September.

## Gates

The round had one report and no gates. The table has one row for that report.

| Date | Track | Gate | Report | Answered by | Tag | Pull request |
|---|---|---|---|---|---|---|
| 16 Sep | exec | none (final report, revision 2) | `i01/exec/round1_final_stage_report.md` | `../round02/00_prep/HEST_replication_review.md` | none | none |

## Documents

| Document | Date | Role |
|---|---|---|
| `masterplan.md` | 9 Oct (at migration) | the round's plan note, pointing to the documents that served as its plan |
| `i01/exec/HEST_replication_handoff.md` | 12 Sep | the instruction. Project context, the staged replication plan (stages 0 to 5), pitfalls, decision boundaries and the reporting format. Closed record |
| `i01/exec/round1_final_stage_report.md` | 16 Sep | the final stage report, revision 2, generated from the saved result tables. Closed record, not maintained. It contains claims that round 2 withdrew, listed below, which should not be cited |

The oversight audit that answered this report, `docs/round02/00_prep/HEST_replication_review.md` (16 Sep), is filed with round 2 because it was written between this round's close and round 2's start.

## What the round established

- The pipeline reproduces the benchmark. Against the leaderboard, 12 of 12 encoders compare with mean $|{\rm diff}|$ of 0.00017 and none over the 0.03 threshold, and the 108 per-task cells have mean $|{\rm diff}|$ 0.00020 with 0 of 108 over the threshold (`i01/exec/round1_final_stage_report.md`, section 3.1).
- ResNet50 is exact at 0.3252, and `hoptimus1` is exact at 0.4229 on its first run, after the pipeline was fixed (`i01/exec/round1_final_stage_report.md`, section 3.1).
- Row identity of the 130,072,250 joined prediction rows was proven against the AnnData with a permutation control, which gave an aligned maximum difference of 4.4e-7 against about 8.0 permuted (`i01/exec/round1_final_stage_report.md`, section 2.4). The review called the instrumentation layer the asset the project would run on (`../round02/00_prep/HEST_replication_review.md`, section 1).
- Pooled Pearson inflates with test-set heterogeneity, by exactly 0.0000 for single-patient arms and +0.1920 for nine-patient random arms. Within-patient Pearson is therefore the metric used (`i01/exec/round1_final_stage_report.md`, sections 3.4 and 9).
- The benchmark's ridge penalty is inert, with $|{\rm diff}|$ against OLS at most 2.7e-4 at both feature scales. Table A13's encoder ranking follows embedding width, with Spearman $-0.954$ for the raw ridge head against $+0.735$ for PCA ridge (`i01/exec/round1_final_stage_report.md`, section 3.8 and D2).
- Plain negative binomial is the right observation model. ZINB beats NB in 14 of 474 pairs, and the median AIC difference is $-2.0019$ (`i01/exec/round1_final_stage_report.md`, section 3.7).
- The five imaging-based tasks have disjoint top-50 gene lists, and their panels share only 14 genes across all 15 samples (`i01/exec/round1_final_stage_report.md`, D5).
- The audit kept four results as new and defensible, which are the pooled versus within measurement, the inert penalty with the width-ranked Table A13, negative binomial without zero inflation, and the gene-list disjointness (`../round02/00_prep/HEST_replication_review.md`, section 1).

## Corrections and withdrawn readings

- The "slide-level signature" term (blocked minus patient, 0.1241) conflated slide and patient. The audit asked for it to be reframed, and round 2 added a leave-one-slide-out arm (`../round02/00_prep/HEST_replication_review.md`, sections 1 and 5.2; `docs/round03/00_prep/round3_oversight_handoff.md`, section 5.1).
- The "institution shift" scalar of 0.0419 was a resolution contrast within one lab, and the IDC "institution" contrast is not an institution contrast (`../round02/00_prep/HEST_replication_review.md`, section 5.4; `docs/round03/00_prep/round3_oversight_handoff.md`, section 5.1).
- The slide-identity probes were labelled as technical without evidence (`../round02/00_prep/HEST_replication_review.md`, section 5.5).
- The reading of COAD as same-patient leakage had the right mechanism and the wrong direction. Round 2 showed it came from a holdout removing several donors at once (`docs/round03/00_prep/round3_oversight_handoff.md`, section 6).
- Within the report itself, revision 2 corrected revision 1. The encoder spread is 0.0977 and not 0.0898, the leakage ratio is 1.61 times and not 1.75 times, and the leakage gap of 0.3143 was retracted for 0.1575 (`i01/exec/round1_final_stage_report.md`, section 9).
- The relabelling of round 1 claims was recorded in the round 2 report and not in this frozen report (`docs/round02/i01/exec/round2_R0_R1_stage_report.md`, section 5.5).

## Carried forward

- The 50 target genes per task were variance-ranked over every spot, test folds included, so every absolute number inherits this leakage. This is the report's most important unchecked item, and it led to the audit's request for within-fold gene selection (`i01/exec/round1_final_stage_report.md`, section 5, item 1).
- The head fitted with `fit_intercept=False` needs an intercept before Topic A can use it (`../round02/00_prep/HEST_replication_review.md`, section 1).
- Scan resolution varies across samples and is aligned with patient identity in three tasks, so it must be a covariate in later analyses (`../round02/00_prep/HEST_replication_review.md`, section 5.3).
- Whether embeddings encode institution is unresolved (Q1), and across-task shift is not identified as a scalar (Q2) (`i01/exec/round1_final_stage_report.md`, section 4).
- The report proposed running `hoptimus1` on the raw ridge head as a falsification test of D2 (`i01/exec/round1_final_stage_report.md`, section 7). Round 2 did this (`docs/round03/00_prep/round3_oversight_handoff.md`, section 6).
- STFlow training (stage 5) was set up and not run, because it needs its own environment and a GPU allocation (`i01/exec/round1_final_stage_report.md`, section 6).
- Three protocol deviations (OD1, OD3, OD4) were listed for sign-off. The sources read here do not record their sign-off, so it is left open.

## Read first next round

- `docs/round02/00_prep/HEST_replication_review.md`, the audit that answered this round and set round 2's work.
- `docs/round03/00_prep/round3_oversight_handoff.md`, section 5, for the history of rounds 1 and 2 in one place.
- `docs/round01/i01/exec/round1_final_stage_report.md`, sections 3.1 and 5, for the fidelity result and what was not checked.
