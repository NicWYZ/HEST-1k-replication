# Round 6, the cheatsheet track, decision at the C1 gate

12 October 2026. Written by the oversight chat after Nicolas merged pull request #23 and asked for medium reasoning effort. This memo opens interval 2 of the track. The instruction `docs/round06/i01/cheatsheet/round06_cheatsheet_track.md` and the masterplan are updated on `main` to match, each with a dated line, so the instruction stays the one document to run from.

**Revisions.**
- 12 October, 02:20. One sentence added to the writer prompt, "Use as much of the allowed size as helps; more detail is generally better." In the pilot no writer came near its 32,768-byte allowance (Haiku 6,990, Sonnet 6,892, Opus 17,688 bytes, `results/round6/cheatsheet/C1_pilot/manifest.csv`), so without it the larger sizes might not differ from the smaller ones. C3 reports bytes written beside the allowance and plots accuracy against both.
- 12 October, 02:10. Nicolas cut the grid to Opus alone at medium effort with one replicate per cell, 20 sessions (sections 3.4, 3.5 and 4). Haiku's and Sonnet's pilot trials stay as high-effort reference points at their four slots each and are not rerun. (Corrected at the round's close, which had read "their twelve slots", the total over three models.)

**What was read and checked.** The C1 report `docs/round06/i01/cheatsheet/round06_cheatsheet_C1_report.md` in full. Against the files, the pilot manifest (19 attempts, 11 done and 8 excluded, 5.1957 US dollars over all attempts, `results/round6/cheatsheet/C1_pilot/manifest.csv`), the per-attempt scores and the scan hits behind E4 (`scan_hits.csv`), the comparator table and the anchor (`results/round6/cheatsheet/C0_comparators/comparators.csv`, `anchor.csv`), and the projection totals (`results/round6/cheatsheet/C1_pilot/c1_projection_totals.csv`). Every number quoted below was read back from those files.

**The gate rule.** Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. Contact with anyone outside the project is never the session's decision.

## 1. Acceptance

C0 and C1 are accepted. All four C0 exit items pass. The isolation probes held in both runs, the comparator anchor reproduces round 1 within 0.000068 in all four cells, and the scorer behaves as specified. The three changes to the command of 6.4 (the CA bundle bound after the tmpfs, `--disable-slash-commands`, output through pipes) were the session's to make and are kept. The transposed coordinates (E3) were caught by the session's own check and fixed before any trial used them, which is the kind of check the project asks for.

## 2. What the pilot shows

One replicate per cell, so these are readings to test, not results.

- At $b = 0$ Opus scored 0.502 on S1*, Haiku 0.260 and Sonnet 0.339. Prediction C.1 put Opus between 0.05 and 0.35, so it is refuted. Zero-shot prediction from the image is stronger than the oversight chat expected.
- In arm B at 32,768 bytes every model beat its own baseline (Haiku 0.545, Sonnet 0.400, Opus 0.600), and every one stayed below the `uni_v2` benchmark head fitted on the same 814 training-block spots, 0.757.
- The combined sessions ($b = \infty$) reached 0.669 for Sonnet and 0.705 for Opus, still below 0.757.
- None of the three cheatsheets holds values keyed to individual patches. All describe visual classes with per-class gene means, and Opus's adds coefficients and code.
- Opus is 43.39 of the 48.05 US dollars the full grid projects to at high effort.

## 3. Decisions

### 3.1 Reasoning effort is medium from here (Nicolas, 12 October)

Every C2 trial, for all three models and every role, runs at `--effort medium`, with `CLAUDE_CODE_EFFORT_LEVEL=medium`. The reason is the pilot's cost and run time.

Because effort is part of the condition, the eleven counted pilot trials do not count towards the grid. C2 runs every grid slot afresh at medium, the pilot's twelve slots included. The pilot's trials are kept as a high-effort reference at those twelve slots, which gives a small effort comparison for free (section 4, item 4).

### 3.2 The exclusion rule (E4)

Option (b) of the report is adopted for C2. A trial is excluded only for one of these:
- a canary string;
- a sample ID or other blinded name;
- credential contents in any output or transcript;
- a nested `claude` session, or a call to the API made outside the child's own process;
- any content that came back from a host other than the API.

Listing directories that are empty or absent, and network attempts that the filter refused, are recorded per trial and reported, but they do not exclude.

The isolation held in every case the pilot excluded. Each attempt failed at the network or found nothing, so none of them saw anything it should not have. Excluding them selected the counted trials on behaviour and left Haiku's combined slot empty after four attempts.

For the high-effort reference, re-read the pilot's attempts under rule (b). The first attempt in each slot that passes it is that slot's reference value, reported beside the value counted under the old rule.

### 3.3 One sentence added to every prompt

No C2 trial has run, so the prompts can still change for the whole grid. The last paragraph of each of the three prompts in instruction 6.3, the writer, the predictor with the baseline, and the combined session, gets this sentence before "When the file is written, stop."

> There is no internet access, and no pretrained models or files other than those in this directory are available.

In the pilot, agents spent turns looking for data in `/data`, `/home` and `/mnt` and trying to download models, and one Haiku combined attempt ran for 3,150 seconds. The sentence tells them what the confinement already enforces, so it removes wasted cost without changing what they can do. The high-effort reference was run without it, and the C3 report says so wherever the two are compared.

### 3.4 The grid

Opus 5.5 only, at medium effort, one replicate per cell (Nicolas, 12 October, to cut time and cost further). That is 20 sessions.

| sessions | count |
|---|---|
| baselines, one on S1* (serving arms A and B) and one on S2* (serving arm C) | 2 |
| writers, 3 sizes, for all of S1 (serving A and C) and for the training blocks (serving B) | 6 |
| predictors, 3 sizes, one each in arms A, B and C | 9 |
| combined sessions ($b = \infty$), one in each arm | 3 |
| **total** | **20** |

Opus's four pilot slots are rerun at medium as part of these 20. Haiku's and Sonnet's pilot trials are not rerun. They stay in the report as high-effort reference values at their slots.

**Order.** Writers before their predictors. Otherwise any order.

**Cost.** At high effort the pilot's Opus trials averaged about 1.08 US dollars each at API prices (4.32 over its four counted slots, `results/round6/cheatsheet/C1_pilot/c1_by_model_role.csv`), so 20 trials would be about 22 dollars at high effort and less at medium.

### 3.5 One session, more trials at once

The container has 4 CPUs and about 15 GB (E8). Run up to four trials at once. Measure memory per trial in the first batch, and drop to three if peak memory across the running trials passes 12 GB. With 20 trials and the dependency of predictors on writers, four at once should finish in a few hours, so the grid is not split across sessions. Open question R6-2 is settled this way.

### 3.6 Answers to the other escalations

- **E1, spot counts.** Accepted. Every arm uses the 1,741 patched S1 spots and the 1,293 patched S2 spots. The masterplan's scale note is corrected. The patched S1 matrix at one byte per value is 87,050 bytes, so 262,144 bytes can still hold all of it.
- **E2, the overview.** The patch mosaic is accepted as `overview.png`. The C3 report says the writers' overview is a mosaic of patches, not a scan of the section.
- **E3, transposed coordinates.** Accepted as fixed.
- **E5, credential folder.** Accepted. Keep scanning every committed file.
- **E6, I1 to the letter.** Accepted. The three built-in plugins appear by name in every trial, so they cannot bias one arm against another.
- **E7, E8, E9.** Noted. The C3 report states that costs are Claude Code's estimates at API prices.

## 4. Interval 2

**Stages.**
- C2 runs the grid of 3.4 under 3.1 to 3.5.
- C3 is the analysis and closing report of instruction section 7, unchanged, with four additions:
  1. Opus's four pilot slots at medium beside their high-effort references, with cost, turns and wall time, and Haiku's and Sonnet's high-effort pilot values shown as reference points.
  2. Per trial, the count of refused network attempts and empty-directory listings recorded under 3.2.
  3. The cost and wall time of C2 per model and role, against the C1 projection.
  4. An answer, for Opus's four pilot slots, to the question whether medium effort costs accuracy. With one trial per slot, say that a difference of under about 0.05 cannot be told from chance.

**Paths.** The final report goes to `docs/round06/i02/cheatsheet/round06_cheatsheet_final_report.md`. Results go under `results/round6/cheatsheet/C2_grid/` and `results/round6/cheatsheet/C3_report/`. The plan is `docs/round06/tracks/cheatsheet/round06_cheatsheet_plan.md`, where you transcribe this memo before starting C2. Commit this memo unchanged on your branch. The tag is `round6-cheatsheet-final`.

**Predictions.** With Opus alone and one replicate, the predictions are scored for Opus and on single values. C.2 to C.5 stand, read as statements about Opus. C.6, the ordering of models, cannot be tested and is reported as not tested. C.1 was scored at C1 and is scored again on Opus's medium-effort baseline. Two predictions are added.
- **C.7** At Opus's four pilot slots, its medium-effort score is within 0.08 of its high-effort reference.
- **C.8** Opus's cost per trial at medium effort is at most two thirds of its cost at high effort, averaged over those four slots.

## 5. What Nicolas does

1. Tell the session to check `main` for this memo, the instruction's revision list and the masterplan's amendments.
2. Nothing else until the final report, unless the session reports a usage limit.
