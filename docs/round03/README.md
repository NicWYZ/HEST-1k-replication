# Round 3, the first experiments for both topics (22 to 24 September 2026)

Round 3 ran the first experiments for Topic A (conformal prediction under donor and slide shift) and Topic B (inference with donor-clustered variance), and started the data expansion. It ended with the finding that the donor is the unit that carries the uncertainty, on both the interval side and the prediction side.

**Tracks.** exec (stages S0, A0, A1, D0, H0, A2, A3, D1, D2, D3, H1, A4a, A4b, B1, B2, D4). **Started from** tag `round2-docs-clean` (commit `4da6b86`).

## Gates

| Date | Track | Gate | Report | Answered by | Tag | Pull request |
|---|---|---|---|---|---|---|
| 22 Sep | exec | A1 | `i01/exec/round3_A1_stage_report.md` | `i02/exec/round3_A1_decisions.md` | `round3-A1` | none |
| 23 Sep | exec | A3 | `i02/exec/round3_A3_stage_report.md` | `i03/exec/round3_A3_decisions.md` | `round3-A3`, then `round3-A3-r2` for revision 2 | none |
| 24 Sep | exec | final | `i03/exec/round3_final_report.md` | none inside round 3; the change of direction that followed is `docs/round04/00_prep/round3_directions.md` | `round3-final`, then `round3-final-r2` for revision 2 | none |

## Documents

| Document | Date | Role |
|---|---|---|
| `masterplan.md` | 9 Oct (at migration) | the round's plan note, pointing to the documents that served as its plan |
| `00_prep/round3_oversight_handoff.md` | 22 Sep | context for the oversight chat, with the reasoning behind the round 3 stages and the history of rounds 1 and 2 |
| `i01/exec/round3_execution_handoff.md` | 22 Sep | the round's instruction to the execution session, stages S0 to D4 |
| `i01/exec/round3_d0_expansion_proposal.md` | 22 Sep | stage D0, the proposal for an 86-sample download of about 48 GB, and the finding that the institution criterion cannot be met |
| `i01/exec/round3_A1_stage_report.md` | 22 Sep | report at the A1 gate, coverage across four fold designs |
| `i02/exec/round3_A1_decisions.md` | 22 Sep | decision memo at A1, which opens interval 2 and approves the expansion |
| `i02/exec/round3_A3_stage_report.md` | 23 Sep | report at the A3 gate, covering H0, A2, A3 and D1 to D3, in revision 2 |
| `i03/exec/round3_A3_decisions.md` | 23 Sep | decision memo at A3, which opens interval 3, the last of the round |
| `i03/exec/round3_final_report.md` | 24 Sep | end-of-round report covering H1, A4, B1, B2 and D4. Its closing page is the best one-page summary of the round |
| `tracks/exec/round3_execution_plan.md` | 22 Sep | the execution session's operating plan, a transcription of the instruction, updated as each memo arrived and now frozen |

## What the round established

- The donor carries the variance. A donor-clustered standard error is 29 to 68 times the spot i.i.d. one on CCRCC, and the i.i.d. interval covers 0.044 at nominal 0.90, while a donor cluster-robust interval with a $t_{G-1}$ reference covers 0.913 (`i03/exec/round3_final_report.md`, closing page).
- Conformal intervals under donor shift under-cover because of the calibration unit. Calibrating on held-out donors covers 0.8562 and on spatial blocks 0.7442 (`i03/exec/round3_final_report.md`).
- The shortfall of the pooled quantile is not a small-$K$ effect. It covers 0.8644 whether 6 or 10 donors calibrate it (`i03/exec/round3_final_report.md`).
- Hierarchical conformal prediction is valid once $K + 1 \ge 1/\alpha$ and is conservative. At $K = 10$ on CCRCC it covers 0.9692 at 1.947 times the pooled width (`i03/exec/round3_final_report.md`).
- Feature-based weighting cannot repair donor or slide shift here. Held-out AUC is at least 0.9747 and the effective calibration size falls to a median 2.13% (`i03/exec/round3_final_report.md`).
- The expansion gave a second multi-donor task, Indiana, and no institution axis. HEST-1k has no two-laboratory cell with disease held fixed (`i01/exec/round3_d0_expansion_proposal.md`, `i03/exec/round3_final_report.md`).
- The benchmark's results do not move with HEST-1k's patch layout. Coverage moves by at most 0.0019 (`i03/exec/round3_final_report.md`).

## Corrections and withdrawn readings

- The round 2 reading that IDC's replicate leak came from a shared donor is withdrawn. IDC's four samples are four donors, and READ's $+0.0901$ is the only same-specimen replicate figure (`i03/exec/round3_A3_decisions.md`, `i03/exec/round3_final_report.md`).
- `docs/superseded/round3_park_note.md` was the live note written when the session parked in interval 1. The A1 stage report and the D0 proposal replaced it, and its D0 leads were refined once the tables were built.
- Three errors in the A1 memo were acknowledged in the A3 memo. They were the W3 wording about CCRCC's design, the count of task files, and the mechanism-(a) prediction that A2c tested and rejected (`i03/exec/round3_A3_decisions.md`).
- The A3 report was reissued as revision 2 (`round3-A3-r2`). It replaced only the D2 passages, and no A2, A3, H0, D1 or D3 number changed (`i02/exec/round3_A3_stage_report.md`).
- The final report was reissued as revision 2 (`round3-final-r2`). It corrected a false floating-point example in the A4b record, and no number changed (`i03/exec/round3_final_report.md`, section 7 item 18).
- The A3 decision memo gave the breast panel size as 280 genes (`i03/exec/round3_A3_decisions.md`). The 18 samples share 151, and 90 remain after the minimum-cells filter (`i03/exec/round3_final_report.md`, section 7 item 7).

## Carried forward

- The direction after round 3 is set out in `docs/round04/00_prep/round3_directions.md`, which retires Topics A and B as framed. The round 4 plan was left to the oversight chat (`i03/exec/round3_final_report.md`, section 9).
- `results/round2/R5c_leak/r5c_leak_summary.csv` still records IDC's `leak_realised_in_shipped_split` as True, and whether to correct frozen round 2 files is undecided (`i03/exec/round3_final_report.md`, section 7 item 2).
- README known limitation 8 still shows the H-Optimus-1 `raw_ridge` cell as a dash, and someone needs to edit it (`i03/exec/round3_final_report.md`, section 7 item 3).
- Whether the v1 task-definition schema or a v2 absorbs the columns D4 needed is undecided (`i03/exec/round3_final_report.md`, section 7 item 6).
- A4a ran at reduced scope. CQR covered 6 of 50 genes and the NB head 16 of 50, so every CQR and NB number holds only at that scope (`i03/exec/round3_final_report.md`, section 7 item 10).
- The round 2 benchmark issue draft stays unsent, and the deck slide `issue1` is on the running correction list (`i03/exec/round3_A3_decisions.md`).
- Several checks were left undone, among them whether HCP over-coverage is level, scale or asymmetry, and any studentised or bias-corrected bootstrap (`i03/exec/round3_final_report.md`, section 8).

## Read first next round

- `docs/round03/i03/exec/round3_final_report.md`, the closing page "What round 3 established" and the escalations in section 7.
- `docs/round04/00_prep/round3_directions.md`, the change of direction that followed the round.
- `docs/round03/i03/exec/round3_A3_decisions.md`, the corrections to round 2 and the rules the round ran under.
