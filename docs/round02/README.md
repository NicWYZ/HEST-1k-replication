# Round 2, from replication to project motivation (16 to 21 September 2026)

Round 2 took the finished HEST-1k replication and the oversight review of it, and tested which of its apparent problems were real, so that the two candidate research directions (Topic A and Topic B) rested on measurements instead of assumptions. It ran from the execution plan of 16 September to the closeout of 19 September. The deck for the advisors and the numeric-claim gate that followed the closeout ran on 20 and 21 September, and the deck was presented through slide 6 of 14 on 21 September.

**Tracks.** exec (stages R0, R1, R1b, R2, R3, R4, R5, R5b, R5c, R6, R7, R8 and the closeout), deck (the deck figures and repository refresh, then the numeric-claim gate). No branch names appear in the sources, and work was committed directly to `main`. **Started from** commit `eb670fa`, the repository state the review and the execution plan were written against.

## Gates

No gate in this round has a pull request number. The sources give none, and the first pull request in the repository history is #1 of 30 September, in round 4. Report-and-wait gates in the plan were at R1, R3 and R5. The R5 decision memo then finished the round in one interval ending at R8.

| Date | Track | Gate | Report | Answered by | Tag | Pull request |
|---|---|---|---|---|---|---|
| 17 Sep | exec | R0 and R1 | `i01/exec/round2_R0_R1_stage_report.md` | `i02/exec/round2_R1_decisions.md` | none | none |
| 18 Sep | exec | R3 | `i02/exec/round2_R3_stage_report.md` | `i03/exec/round2_R3_decisions.md` | none | none |
| 18 Sep | exec | R5 | `i03/exec/round2_R5_stage_report.md` | `i04/exec/round2_R5_decisions.md` | none | none |
| 19 Sep | exec | R8 | `i04/exec/round2_R8_stage_report.md` | `i05/exec/round2_closeout_decisions.md` | none | none |
| 19 Sep | exec | closeout | `i05/exec/round2_closeout_report.md` | none; no closing memo answered this report | `round2-final` | none |
| 21 Sep | deck | numeric-claim gate, section 2.6 | `i01/deck/closeout_gate_report.md` | `i02/deck/post_deck_repo_instructions.md` | `round2-final-deck` | none |
| 21 Sep | deck | numeric-claim gate closed | `i02/deck/docs_clean_report.md` | none in this folder | `round2-docs-clean` | none |

## Documents

| Document | Date | Role |
|---|---|---|
| `masterplan.md` | 9 Oct (at migration) | the round's plan note, pointing to the documents that served as its plan |
| `00_prep/HEST_replication_review.md` | 16 Sep | oversight audit of round 1 that produced round 2; closed record |
| `i01/deck/deck_figures_and_repo_update.md` | 20 Sep | instruction for the seven deck figures and the repository refresh; supplied by Nicolas and committed in round 3 |
| `i01/deck/closeout_gate_report.md` | 21 Sep | gate report on the numeric-claim sweep; corrects the gate accounting in its own commit message |
| `i01/exec/round2_execution_plan.md` | 16 Sep | instruction and plan, stages R0 to R8; its section 13 is the report format; closed record |
| `i01/exec/round2_R0_R1_stage_report.md` | 17 Sep | report on R0 and R1 (the intercept and the $R^2$ ladder); carries the relabelling of round 1 |
| `i02/deck/post_deck_repo_instructions.md` | 21 Sep | instruction closing the gate that the closeout gate report left open |
| `i02/deck/docs_clean_report.md` | 21 Sep | report on how the claim gate was closed at zero; tag `round2-docs-clean` |
| `i02/exec/round2_R1_decisions.md` | 17 Sep | decision memo on the R0 and R1 report, revision 2; directives for R1b to R3 |
| `i02/exec/round2_R3_stage_report.md` | 18 Sep | report on R0 to R3, including the split decomposition |
| `i03/exec/r5_idc_provenance.md` | 18 Sep | reading task on the four IDC Xenium samples; its TENX95 row is superseded |
| `i03/exec/round2_R3_decisions.md` | 18 Sep | decision memo on the R3 report; restates the gate rule; directives for R4 to R7 |
| `i03/exec/round2_R5_stage_report.md` | 18 Sep | report on R4 and R5 (probes and provenance) |
| `i04/exec/round2_R5_decisions.md` | 19 Sep | decision memo on the R5 report; adds the donor audit R5b and the replicate-leak extension R5c; finishes the round in one interval |
| `i04/exec/round2_R8_stage_report.md` | 19 Sep | report on R5b to R8 (donor audit, replicate leak, variance components, per-gene results, raw heads) |
| `i05/exec/round2_closeout_decisions.md` | 19 Sep | closeout memo; accepts the round, closes loose ends, orders the freeze |
| `i05/exec/round2_closeout_report.md` | 19 Sep | closeout report; freeze at `round2-final` |
| `i05/exec/round2_results_synthesis.md` | 19 Sep | every result of rounds 1 and 2 ranked by significance; the basis of the deck |
| `i05/exec/hest_bench_issue_draft.md` | undated, with a note of 23 Sep | draft issue to the HEST authors; unsent, and its item 1 is struck |
| `tracks/deck/deck_master_outline.md` | 20 Sep | the deck's outline, twelve main slides and two backup slides |
| `tracks/deck/deck_speaker_scripts.md` | 20 to 22 Sep | full speaker scripts for the deck |
| `tracks/deck/deck_round2/` | presented 21 Sep | the deck. The PowerPoint file is the authoritative copy, and `deck_round2_slides.md`, `deck.json` and the `slides` folder are a text export as of 22 Sep that may lag later edits |
| `tracks/deck/.verify-exceptions-deck` | 21 Sep | the numeric-claim checker's exceptions file for the deck outline, kept beside it |
| `tracks/deck/deck_round2/deck_round2_slides.md` | 22 Sep | text export of the slides with speaker notes; presented through slide 6, and the next presentation resumes at slide 7 |

## What the round established

- The patient split does not measure generalisation to an unseen patient on at least two of ten tasks. The partner TENX slide in IDC is worth $+0.065$ within-slide Pearson, positive in 6 of 6 cells and 54% of IDC's gap, and READ's replicate gives $+0.090$, positive in 12 of 12 (`i05/exec/round2_results_synthesis.md`, `i04/exec/round2_R8_stage_report.md`).
- Ignoring slide boundaries is worth $0.159$ within-slide Pearson, 1.6 times the spread of $0.098$ between the best and worst of twelve encoders (`i05/exec/round2_results_synthesis.md`, `i02/exec/round2_R3_stage_report.md`).
- The benchmark head has no intercept. The fold-median $R^2$ climbs from $-0.95$ to $-0.16$ to $+0.03$ to $+0.10$, and predictions are over-dispersed by 1.84 (`i05/exec/round2_results_synthesis.md`, `i02/exec/round2_R3_stage_report.md`).
- Encoders carry a scan-session signature, decodable at 0.98, that is in the features and not in the expression (`i03/exec/round2_R5_stage_report.md`, `i04/exec/round2_R8_stage_report.md`).
- The audit of all 72 samples gave 58 verified, 9 unverifiable and 5 contradicted donor labels, and produced the `donor_id` column used from here on (`i04/exec/round2_R8_stage_report.md`).
- Table A13's ranking follows embedding width, with Spearman $-0.95$ on `raw_ridge` and $+0.73$ on `pca_ridge`. Negative binomial without zero inflation is the observation model (`i05/exec/round2_results_synthesis.md`).
- The pooled between-donor estimate is 0.376 (`i05/exec/round2_closeout_decisions.md`, `i05/exec/round2_closeout_report.md`).
- The numeric-claim sweep is now required before a document leaves the project. The closeout reports 296 claims verified, 0 unresolved and 99 uncited, and the final combined sweep reports zero unresolved (`i05/exec/round2_closeout_report.md`, `i01/deck/closeout_gate_report.md`).

## Corrections and withdrawn readings

- The "institution shift" scalar of 0.0419 from round 1 was withdrawn, because the two arms never differed by institution (`i01/exec/round2_R0_R1_stage_report.md`). The COAD same-patient reading was also withdrawn, since COAD's folds hold out several donors at once, which is the opposite direction (`i05/exec/round2_results_synthesis.md`).
- The `TENX95` row of the table in `i03/exec/r5_idc_provenance.md` is wrong, and stage D3 of round 3 governs. Item 1 of `i05/exec/hest_bench_issue_draft.md` is struck for the same reason, so the draft must not be sent as written.
- The R3 report's IDC figure of 0.1361 was confounded by training-set size, and the controlled value replaces it (`i04/exec/round2_R5_decisions.md`, section 1.6). That value appears as $+0.0651$ in `i03/exec/round2_R5_stage_report.md` and as $+0.0652$ in `i04/exec/round2_R8_stage_report.md` and `i05/exec/round2_closeout_report.md`.
- Probe 2's per-fold statistic equalled a constant majority-class predictor and was replaced by a pooled one, and probe 1's either-or rule was retired (`i04/exec/round2_R5_decisions.md`, sections 1.4 and 1.5).
- The unresolved-claim totals of 437 and 688 are dated snapshots, and the current total is zero (`i02/deck/docs_clean_report.md`, `i01/deck/closeout_gate_report.md`). Six document errors were corrected during the triage, each with a changelog line in its own document (`i02/deck/docs_clean_report.md`).
- The two width-score correlations of $-0.954$ and $-0.950$ come from an eleven-encoder and a twelve-encoder cohort, and both are kept with an `n_encoders` column (`i05/exec/round2_closeout_report.md`).
- The pooled estimate of 0.122 from pairing CCRCC with PRAD is an artefact of a truncated zero and stays beside 0.376 only as a flagged substitution (`i05/exec/round2_closeout_decisions.md`).
- The `round2-final-deck` tag points at commit `6acbef2`, while `i01/deck/closeout_gate_report.md` says it was written against commit `a220974` and that tag.
- `i02/exec/round2_R1_decisions.md` carries a banner that the round 3 handoff wrongly recorded this memo as never saved.

## Carried forward

- The IDC same-donor attribution was left unresolved at the close, because every fetch returned HTTP 429 (`i05/exec/round2_closeout_report.md`). Round 3's stage D3 later settled it against the round 2 reading (`i05/exec/hest_bench_issue_draft.md`).
- The decision on the benchmark findings, whether a note, an issue to the authors or the first section of the Topic A paper, belongs to Nicolas and David, and the draft remains unsent (`i05/exec/round2_results_synthesis.md`).
- Whether to pull full HEST-1k breast and brain for an institution axis is open (`i05/exec/round2_results_synthesis.md`).
- `raw_xgb` for H-Optimus-1 was closed unrun at 70 minutes per split (`i05/exec/round2_closeout_decisions.md`).
- Not checked were donor identity for the 9 unverifiable samples, bootstrap intervals on the variance components, and diagnostics for the nested ANOVA. The between-session result rests on one patient, PRAD patient 2 (`i04/exec/round2_R8_stage_report.md`).
- The deck resumes at slide 7 at the next presentation (`tracks/deck/deck_round2/deck_round2_slides.md`).
- The first question for round 3 is Topic A's first experiment, split conformal and CQR on the float64 head under three fold designs (`i05/exec/round2_results_synthesis.md`).

## Read first next round

- `docs/round02/i05/exec/round2_results_synthesis.md`, the ranked results and where Topics A and B stand.
- `docs/round02/i05/exec/round2_closeout_report.md`, the freeze and what was left open.
- `docs/round02/i04/exec/round2_R8_stage_report.md`, the donor audit, replicate leak and variance components.
- `docs/round02/i05/exec/round2_closeout_decisions.md`, the closeout rulings and the two rules to carry forward.
- `docs/round02/i02/deck/docs_clean_report.md`, how the claim gate was closed and what the sweep does not cover.
