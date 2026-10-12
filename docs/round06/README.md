# Round 6, the cheatsheet experiment (opened 11 October 2026)

David proposed an experiment by email. An agent predicts the expression of 50 genes from H&E patches. A second agent, which saw the measured expression, writes a text cheatsheet of limited size that the first may use. The question is how large the cheatsheet must be for the predictions to reach a given accuracy. Nicolas decided on 11 October to run it as round 6, with the purpose of learning whether few-shot prediction with a general-purpose language model can beat pathology foundation models. The PPI paper's next round becomes round 7.

**Track.** cheatsheet (branch `round6-cheatsheet`, stages C0 to C3, run by a Claude Code session on Longleaf). **Starts from** `main` at the commit that carries the masterplan and the instruction.

## Gates

| Date | Track | Gate | Report | Answered by | Tag | Pull request |
|---|---|---|---|---|---|---|
| pending | cheatsheet | C1 | to come in interval 1 | | `round6-cheatsheet-C1` | |
| pending | cheatsheet | C3 | to come in interval 2 | | `round6-cheatsheet-final` | |

## Documents

| Document | Date | Role |
|---|---|---|
| `masterplan.md` | 11 Oct | the round's plan, with the design, the trial count, the oversight chat's choices, the predictions and the open questions |
| `00_prep/round06_round5_results_explained.md` | 11 Oct | for Nicolas, the four main round-5 results explained with their theory (the level term in regime B, the cross-fitting term of the design-target interval, the full conformal set inside the target donor, balanced selection of the labelled clusters), the other results briefly, and what is not established |
| `i01/cheatsheet/round06_cheatsheet_track.md` | 11 Oct | instruction for the cheatsheet track, with the fixed prompts, the isolation properties and stages C0 to C3 |
