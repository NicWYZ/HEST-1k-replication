*16 November 2026. Reviewed as tagged at round11-record. What stands now: docs/round11/README.md.*

# Round 11, masterplan

*Written on 16 November 2026 by the oversight session through the `project-record` skill. Living while the round runs.*

## Why this round

Round 10 closed with the numbers of an applied paper and without a draft (`../round10/README.md`). On 16 November Nicolas asked for an assessment of the project as a whole. The oversight session's reading, given in the session, was that the results an outside reader would care about are the measured facts about histology-predicted expression (the donor and the center as the unit of uncertainty, what predictions buy for cohort-level inference, the benchmark's label errors), that one paper with that one message is worth finishing, and that the advisors should see it before more is built. That reading is `[proposed]`. Nicolas then decided the next steps: an execution session tries a stronger predictor and ties up the loose ends, and after it the oversight session drafts the outline for presenting the project to Dr. Zhu and Dr. Zhang.

## Goal

The headline results of the project stated on final numbers, tested against a stronger predictor, and an outline for presenting the project to the advisors.

## Tracks

| Track | Who | Branch | Brief | Writes to | Final gate |
|---|---|---|---|---|---|
| `closeout` | one execution track under `docs/EXECUTION_RULES.md`, every job on Longleaf | `round11-closeout` | `closeout/round11_closeout_brief.md` | `docs/round11/closeout/`, `results/round11/closeout/`, `code/scripts/round11_closeout_*` | `G-final`, the final report with its headline table and one pull request |
| the advisor outline | the oversight session, after `G-final` is merged | none | none | `docs/round11/oversight/` | Nicolas's review of the outline |

The outline follows `docs/WAYS_OF_WORKING.md`, "Decks". It presents the project as a whole and puts to the advisors the decisions that wait on them (D5, Q1, and the framing and venue of the paper).

## Who decides the gates

For this round Nicolas has the oversight session review each gate of track `closeout` and reply so that the track goes on, and relay a summary to him. The track stops for Nicolas himself only on a substantive issue or problem: a headline result that changes, a request for a download, a failed anchor, a doubt about the correctness of a number, or anything `docs/EXECUTION_RULES.md` lists as never the session's decision. Pull requests remain his to merge.

## Expectations

Written before any run of the round, and scored on the predictor the track designates as primary before it reads that predictor's held-out results (brief, section 4). Unless a line says otherwise the reference is round 10's `uni_v2` ridge head, the scale $\log(1 + y)$, the estimand $\theta_3$ and the nominal level 0.90.

- **P11.1.** The primary predictor raises the donor-held-out median spot-level Pearson by at least 0.02 over the reference on at least two of kidney Visium, bowel Visium and LUNG_XENIUM. The reference values are 0.471, 0.511 and 0.619 (`results/round10/final_runs/F2/report_tables/r10_buy_uni_v2_primary_n8.csv`, column `median_pearson_spot`). If it does not, P11.2 to P11.4 are scored "not tested".
- **P11.2.** With the primary predictor, the median width ratio of `fix1` to `classical` at 8 labelled donors stays above 0.80 on CCRCC, INDIANA_KIDNEY and kidney Visium, and the leave-one-donor-out median $R^2$ of the donor mean against the leave-one-out constant stays below 0.15 on CCRCC. The reference ratios are 0.878, 0.957 and 0.937 (the same file), and the reference $R^2$ is 0.021 (`results/round10/final_runs/F1/diagnostics/d12_lodo_r2_medians__r3_CCRCC_uni_v2.csv`).
- **P11.3.** Held out by center on kidney Visium, the primary predictor's median Pearson stays below 0.20 and at least 0.25 below its own donor-held-out value. Round 10's three encoders give 0.004 to 0.123 held out by center and 0.412 to 0.483 held out by donor (`results/round10/final_runs/F1/aggregate/f1_predictions.csv`).
- **P11.4.** For the primary predictor, split conformal coverage with the absolute score is lower under round 3's design `donor` than under `random` on every task where both are run, and on kidney Visium coverage under a center design is at least 0.05 below coverage under `random`.
- **P11.5.** Under equal allocation, with `fix1`, $\theta_3$ and the cost ratio 10, regime B is narrower than regime A in more than 6 of the 12 cost-matched comparisons on ACS by state. Under proportional allocation round 10 found 3 of 12 (`results/round10/final_runs/F4/paper_numbers.csv`, keys `E1.ACS_STATES.*`).

## Open questions

| Question | Default | Who decides |
|---|---|---|
| The paper's framing: the applied paper of round 10's writing plan, or one paper on the headline results | `[proposed]` the second, not adopted | Nicolas, with the advisors |
| D5, Q1, Q3, O5 | as `CLAUDE.md`'s state block carries them | Nicolas, D5 and Q1 with the advisors |
| Whether a stronger predictor may use a download | no download | Nicolas, at gate G1 if the track stops there |

## What closes the round

The track's pull request merged, the outline reviewed by Nicolas, and the skill's Close.
