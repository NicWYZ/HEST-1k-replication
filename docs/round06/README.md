# Round 6, the cheatsheet experiment (opened 11 October 2026)

David proposed an experiment by email. An agent predicts the expression of 50 genes from H&E patches. A second agent, which saw the measured expression, writes a text cheatsheet of limited size that the first may use. The question is how large the cheatsheet must be for the predictions to reach a given accuracy. Nicolas decided on 11 October to run it as round 6, with the purpose of learning whether few-shot prediction with a general-purpose language model can beat pathology foundation models. The PPI paper's next round becomes round 7.

**Track.** cheatsheet (branch `round6-cheatsheet`, stages C0 to C3, run by a Claude Code cloud session, with one packaging job on Longleaf). **Starts from** `main` at the commit that carries the masterplan and the instruction.

## Gates

| Date | Track | Gate | Report | Answered by | Tag | Pull request |
|---|---|---|---|---|---|---|
| 12 Oct | cheatsheet | C1 | `i01/cheatsheet/round06_cheatsheet_C1_report.md` | `i02/cheatsheet/round06_cheatsheet_C1_decisions.md` | `round6-cheatsheet-C1` | #23 |
| pending | cheatsheet | C3 | to come in interval 2 | | `round6-cheatsheet-final` | |

## Documents

| Document | Date | Role |
|---|---|---|
| `masterplan.md` | 11 Oct | the round's plan, with the design, the trial count, the oversight chat's choices, the predictions and the open questions |
| `00_prep/round06_round5_results_explained.md` | 11 Oct | for Nicolas, the four main round-5 results explained with their theory (the level term in regime B, the cross-fitting term of the design-target interval, the full conformal set inside the target donor, balanced selection of the labelled clusters), the other results briefly, and what is not established |
| `i01/cheatsheet/round06_cheatsheet_track.md` | 11 Oct, living | instruction for the cheatsheet track, with the fixed prompts, the isolation properties and stages C0 to C3, revised in place with a dated list at its top |
| `i01/cheatsheet/round06_cheatsheet_C1_report.md` | 12 Oct | report at the C1 gate (C0 setup and the pilot of twelve slots at high effort) |
| `i02/cheatsheet/round06_cheatsheet_C1_decisions.md` | 12 Oct | decision at C1. Medium effort from here, exclusion only for leak signs, one sentence added to every prompt, then, at 02:10 the same night, the grid cut to Opus alone with one replicate, 20 sessions |
| `tracks/cheatsheet/round06_cheatsheet_plan.md` | 11 Oct onward, living | the session's operating plan, with flags F1 to F16 |
