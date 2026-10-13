# Round 6 extension, the cheatsheet track, decision at the C5 gate

12 October 2026. Written by the oversight chat for the execution session on Nicolas's Mac. It answers `docs/round06/i04/cheatsheet/round06_cheatsheet_C5_report.md` (pull request #25) and opens interval i05.

**What was read and checked.** The C5 report in full. On branch `round6-cheatsheet-ext`, the comparator table and the anchor (`results/round6/cheatsheet_ext/C4_comparators/tables/comparators.csv`, `anchor.csv`), the representativeness table (`results/round6/cheatsheet_ext/C4_package/representativeness.csv`), the pilot's scores and per-gene cells (`results/round6/cheatsheet_ext/C5_pilot/scores.csv`, `scores/*_cells.csv`) and its cheatsheet (`results/round6/cheatsheet_ext/C5_pilot/cheatsheets/d35a522f_v1.txt`). The builder's mapping from predictor IDs back to barcodes and slides and the scorer's alignment (`code/scripts/round6_cheatsheet_ext_build.py`, `round6_cheatsheet_ext_run.py`, `round6_cheatsheet_ext_score.py`) were read to rule out a mapping fault behind the near-zero agent scores. None was found. Every number below was read back from these files.

**The gate rule.** Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. Contact with anyone outside the project is never the session's decision.

## 1. Acceptance

C4 and C5 are accepted, and the harness is accepted unchanged. The pilot's three sessions (the baseline `eb295869`, the writer `d35a522f` with its audit `727d88f6`, and the predictor `e64d3aba`) count as grid sessions (Q2).

## 2. What was checked

- The anchor reproduces round 1 within 0.000006 for `uni_v2` and 0.00012 for `virchow2` (`anchor.csv`).
- The draws match the plan. Training slides `INT14`, `INT16`, `INT18`, `INT19`, `INT20`, `INT22`, `INT23`, test slides `INT13`, `INT15`, `INT24` (`draws.json`).
- `INT24` fails the representativeness check on 9 genes and the other nine slides on 0 to 3 (`representativeness.csv`).
- The pilot's values are the report's, with the baseline at $-0.009$, the cheatsheet predictor at $0.041$ and the `uni_v2` head on the 3,500 writer spots at $0.184$, within slides (`scores.csv`, `comparators.csv`).

## 3. Readings for the record

1. Within a slide, these 50 genes carry little that either the agents or the heads can predict. The `uni_v2` head reaches 0.184 on the 3,500 writer spots and 0.221 on all 31,075 patched spots. The writer's own cheatsheet notes that 45 to 70% of spots have zero counts for most genes and that sections differ about 3-fold in overall level while the within-section association is weak. Most of what it wrote describes differences between sections, which the within-slide metric removes. This is why its pooled value (0.080) is above its within-slide value (0.041).
2. The size-matched codebook, which involves no agent, moves between 0.092 and 0.151 across sizes from 512 bytes up without a trend (`comparators.csv`). Differences of that size between neighbouring grid points will not be readable from single trials.
3. `virchow2` is below `uni_v2` on these slides at both training sizes, although round 1 found it the better encoder on CCRCC.

## 4. The next interval

Nicolas decided on 12 October that C6 runs as the instruction plans it, with no second predictor and no change to the metric or the prompts. The pooled value is reported beside the within-slide one, as section 6.7 already says.

**C6.** The remaining eight writers with their audit loops (256, 512, 1,024, 2,048, 8,192, 16,384, 32,768 and 65,536 bytes), their eight predictors, and the combined session. Up to four sessions at once. The scanner runs after each batch.

**C7.** As the instruction's section 7 says. In the comparison of sizes, give the codebook's spread across sizes (reading 2) beside the agents' curve, so the reader can judge how much of the curve's shape one fit or one trial can move. Report per-slide values throughout, with `INT24`'s failed representativeness check noted beside them.

**Files.** The C7 report goes to `docs/round06/i05/cheatsheet/round06_cheatsheet_C7_report.md`, results to `results/round6/cheatsheet_ext/C6_grid/` and `results/round6/cheatsheet_ext/C7_report/`, transcripts to `NicWYZ/hest-r6-data` under `transcripts/ext/C6/`. Tag `round6-cheatsheet-C7`. Transcribe this memo into your plan before C6 starts.

**Predictions.** X.1 is refuted at $-0.009$ and X.8 at a gap of 0.037. The other six stand as written in the instruction's section 8 and are scored at C7.

## 5. Answers to escalations and open questions

- **E1. Data preparation and comparators on the Mac.** Accepted. It was Nicolas's decision in chat on 12 October. The instruction, the masterplan and `CLAUDE.md` record it. The Longleaf code clone and the empty folder in the project tree may stay as they are.
- **E2. `INT24`'s sample.** Accepted and kept, as section 6.1 says. Report it as in section 4 above.
- **E3. Billing.** Nicolas checks his usage page. It does not block C6.
- **Readings R1 to R9 of the plan.** Accepted. In particular, the checker sees only the files of section 6.2, so the mechanical report is not shown to it, and the instruction's phrase "an input to the checker" is read as the harness's record, not the checker's input. A session that stops at its turn cap with a valid output is used, with its stop reason recorded.
- **Q1. Predictors writing feature scripts after a few montages.** This is the behaviour the fixed prompts allow, and the baseline measures the same behaviour. No prompt changes.
- **Q2.** Yes, the pilot counts (section 1).
- **Q3. `curl`.** Not needed. A trial's network namespace has no route out whatever tool it uses, and the image has no `curl` for a trial to use either.
- **Token in the I2 transcript.** Accepted as handled, with both md5s recorded.
