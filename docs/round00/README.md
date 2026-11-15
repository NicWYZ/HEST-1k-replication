# Round 0, the framing before round 1 (September 2026)

Round 0 is the framing the project started from, written before anything ran. It has no plan, no runs and no gates. Its two documents are the source of the project's two questions and of the first replication plan.

## What the round established, as it now stands

- **The two questions.** The proposal posed Topic A, calibrated per-spot, per-gene prediction intervals for histology-predicted expression and their coverage under cohort shift, and Topic B, a valid confidence interval for a population quantity such as the correlation of nuclear area with a gene's expression, from a few labelled spots and many unlabelled ones (`first_year_ST_project_proposal.md`, sections 3 and 4). These two questions are still the aim of the project as Nicolas reframed it on 6 November (`docs/round10/00_prep/round10_reframing.md`, section 1). `docs/round10/00_prep/round10_findings_survey.md`, section 1, restates them and section 2 lists what later rounds found on each.
- **The framing as written no longer stands in three places.** The proposal took institution or site as the shift axis for Topic A. HEST-1k has no institution axis (`docs/round10/00_prep/round10_findings_survey.md`, finding D7; `docs/round03/README.md`), and the round 2 measurements put the shift in slide, scan session and donor instead (`docs/round02/README.md`). The proposal took the slide as the unit of inference for Topic B, and round 2 found it is the donor, with slides nested inside (`docs/round02/README.md`). And Topics A and B as framed here were retired after round 3 (`docs/round04/00_prep/round3_directions.md`).
- **The literature landscape** ranked post-prediction inference on predicted spatial expression first and conformal prediction under shift fifth for the first paper (`literature_landscape.md`, ranked shortlist and recommendations). Its claims about what was open are dated mid-2026 and rest on sources not read in full by the project. Later checks found much of the methodology classical or in print: the mean estimator of prediction-powered inference is the survey-sampling difference estimator (`docs/round04/00_prep/round4_originality_check.md`), and the second advisor deck refreshed its literature slide from a new search (`docs/round05/00_prep/deck2/deck2_outline.md`, slide 2).

## Expectations and their scores

No plan of record was written for this round. Two expectations in the proposal were later tested.

| Expectation, as the proposal wrote it | Score | Where |
|---|---|---|
| Spots within a slide are dependent, so naive prediction-powered inference with an i.i.d. variance will undercover (section 4.2) | held. In round 3's semi-synthetic runs a spot i.i.d. interval covers the donor-level quantity 0.044 of the time at nominal 0.90 (mean over 6306 cells), against 0.913 for a donor-clustered interval | `docs/round03/i03/exec/round3_final_report.md`; `results/round3/B1_ppi/b1b2_report_numbers.csv` |
| Leave-site-out is a usable shift regime on HEST (sections 3.3 and 6.4) | refuted. HEST-bench has no clean institution contrast, and full HEST-1k has no two-laboratory cell with disease held fixed | `docs/round02/README.md`; `docs/round10/00_prep/round10_findings_survey.md`, D7 |

## What was tried and did not work

Nothing was run in this round.

## What reached the advisors and has changed since

The record does not show whether the proposal itself was given to the advisors. Its landscape became slide 7 of the round 2 deck, which was not reached when that deck was presented on 21 September (`docs/round02/README.md`), and a refreshed version opened the second deck of 7 October (`docs/round05/00_prep/deck2/deck2_outline.md`). The institution shift axis and the slide as the unit of inference, both in the proposal's framing, were changed by round 2.

## Open threads

None of the round's own. The proposal's two questions are the aim of round 10.

## Documents kept

| Document | What it is for |
|---|---|
| `first_year_ST_project_proposal.md` | the project's framing, Topics A and B, and the replication plan that became round 1's instruction |
| `literature_landscape.md` | the mid-2026 landscape and ranked shortlist that produced Topics A and B, with its source URLs |
