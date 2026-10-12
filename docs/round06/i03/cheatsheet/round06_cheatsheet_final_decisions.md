# Round 6, the cheatsheet track, closing memo

12 October 2026. Written by the oversight chat after Nicolas merged pull request #24. This memo closes the track and sits alone in its third interval.

**What was read and checked.** The final report `docs/round06/i02/cheatsheet/round06_cheatsheet_final_report.md` in full. Against the files, the grid (`results/round6/cheatsheet/C3_report/grid.csv`, all fifteen arm and size values), the cost totals (`results/round6/cheatsheet/C3_report/cost_totals.csv`, 7.906 US dollars, 780 seconds from first start to last finish), and the comparators. The tags `round6-cheatsheet-C1` and `round6-cheatsheet-final` are on GitHub.

**The gate rule.** Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. Contact with anyone outside the project is never the session's decision.

## 1. Acceptance

C2 and C3 are accepted and the track is closed. All 20 grid sessions ran on Opus 5.5 at medium effort with valid outputs. The I2 and I3 isolation probes were rerun in the new container and held. I1 was not rerun, and it rests on interval 1's probe and on every C2 trial's init event. The four writers started before the prompt revision were stopped before writing anything and are not counted. Nicolas decided on 12 October that nothing further is pursued.

## 2. Readings for the record

1. **David's question.** On the slide the writer had seen, $\bar r$ reached 0.8 only at the largest size, 0.903 at 262,144 bytes. It got there by copying, because the cheatsheet listed every spot with 43 image features and its 50 gene values. So $b^*(0.8)$ lies between 32,768 and 262,144 bytes, and the cheatsheet must be large enough to hold the measurements (`results/round6/cheatsheet/C3_report/grid.csv`, `results/round6/cheatsheet/C3_report/cheatsheet_tags.csv`).
2. **Against the pathology model.** On unseen spots, no cheatsheet and no session holding the labels reached the `uni_v2` benchmark head fitted on the same spots. The best values were 0.621 against 0.757 on the unseen region and 0.672 against 0.683 on the second patient, the latter within the noise of one trial (`results/round6/cheatsheet/C3_report/grid.csv`).
3. **Where the gain sits.** On the second patient, 4,096 bytes lifted $\bar r$ from 0.345 to 0.647, and larger cheatsheets added 0.025 (`results/round6/cheatsheet/C3_report/grid.csv`).
4. **What large cheatsheets became.** From 32,768 bytes up they carried feature-extraction code, and at 262,144 bytes training tables, so the predictor ran a small hand-built image model (`results/round6/cheatsheet/C3_report/cheatsheet_tags.csv`).
5. **Effort.** Medium effort cost 0.43 times high effort at Opus's four pilot slots and scored lower by 0.014 to 0.075, which one trial per slot cannot separate from chance except at the baseline (`results/round6/cheatsheet/C3_report/effort.csv`).

Arm A's 0.903 is reported only as the copying check it is, never as a result on its own. This answers the report's open question 2.

## 3. Answers to the escalations and open questions

- **E10, branch name.** The work stays on `claude/beautiful-mccarthy-feog45`, already merged as #24. No rename. Claude Code cloud sessions name their own branch, so future instructions for such sessions should not fix one.
- **E11, the four early writers.** Accepted as interrupted trials.
- **E12, the rebuilt container.** Accepted. The filter's `start.sh` should have been committed in interval 1. That matters only if a cloud track runs again.
- **E13, how rule (b) reads credential contents.** Accepted.
- **E14 to E16.** Accepted, and carried into the round summary.
- **Correction.** The instruction's revision line of 02:20 rounds the pilot writers' sizes to 6,890 and 17,690 bytes. The manifest holds 6,892 and 17,688, as the C1 memo's revision quotes them. The instruction is left as it is and the correction is recorded here.

## 4. What comes next

Nothing in this track. The two-page summary for the advisors is `docs/round06/oversight/round06_cheatsheet_summary.md`. Whether and when it goes to David is Nicolas's decision (R6-3). The round closes with this memo, and the PPI paper's work resumes as round 7.
