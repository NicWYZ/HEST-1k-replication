# Round 6 extension, the cheatsheet track, closing memo

13 October 2026. Written by the oversight chat after the C7 report (pull request #26). This memo closes the extension and sits alone in its interval.

**What was read and checked.** The C7 report `docs/round06/i05/cheatsheet/round06_cheatsheet_C7_report.md` in full. On branch `round6-cheatsheet-ext`, the grid (`results/round6/cheatsheet_ext/C7_report/grid.csv`, all ten sizes with per-slide and pooled values), the spread and rank correlation (`spread.json`, recomputed here as $-0.017$), the combined session (`combined.json`) and the cost totals (`cost_by_role.csv`, 15.99 US dollars over 35 sessions). The numbers below were read back from these files.

**The gate rule.** Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. Contact with anyone outside the project is never the session's decision.

## 1. Acceptance

C6 and C7 are accepted and the extension is closed. All 35 sessions ended with a valid output, none was excluded, and every final cheatsheet passed its audit. Nicolas decided on 13 October that the round closes here and nothing further is pursued.

## 2. Readings for the record

1. **Zero-shot.** On three held-out CCRCC patients, Opus 5.5 from images alone scored $-0.009$ on the mean within-slide Pearson.
2. **Size does not matter.** Every one of nine rubric-bound cheatsheets beat the baseline, scoring 0.041 to 0.158, and the metric does not rise with size (rank correlation $-0.017$). A 248-byte cheatsheet scored 0.105.
3. **Against the pathology model.** No cheatsheet reached the `uni_v2` head on the same 3,500 spots, at 0.184. The best, at 8,192 bytes, was 0.026 below it.
4. **Noise.** Seven of the nine sizes lie within 0.052, about the 0.059 by which the size-matched codebook moves from 512 bytes up with no agent. The two low sizes, 4,096 and 65,536 bytes, cannot be told from session noise with one trial each.
5. **The rubric held.** No code, model recipe or computed image measurement appeared in any version. Five violations at the three largest sizes, mostly stain colour as a cue, were each fixed in one revision.
6. **What the bytes carried.** From 1,024 bytes up, cheatsheets described section types that correspond to the seven training patients, with their gene levels. A patient's level is constant across its spots, so it does not enter a within-slide correlation. The rule that carried the within-slide signal, that expression tracks cellularity, fits in a few hundred bytes.
7. **Labels in hand.** The combined session scored 0.194 by fitting a model on image features it built itself, level with the `uni_v2` head within noise and above every cheatsheet.

## 3. Answers to the open questions

- **Q1, section types that are the training patients.** Within the rubric, which allows patient variation described by appearance, and every checker passed it. It is reported as reading 6, not as a breach.
- **Q2, replication.** None. Nicolas decided not to add replicates at C5 and closes the round here.
- **Q3, within-slide against pooled.** Noted. The pooled value is reported at every size, as the instruction asked.
- **Two audits reading stain-colour phrases differently.** Recorded. It shows that rule F6 left room for both readings, and it changes no result.
- **E2 and E3.** `INT24`'s sample stands as reported. The billing check stays with Nicolas.

## 4. What comes next

Nothing in this track. The short summary is `docs/round06/oversight/round06_cheatsheet_ext_summary.md`. Whether it goes to David with the first summary is Nicolas's decision (R6-3). The project returns to the PPI paper as round 7.
