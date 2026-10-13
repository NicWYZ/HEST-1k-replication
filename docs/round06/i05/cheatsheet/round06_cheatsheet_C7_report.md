# Round 6 extension, the cheatsheet track on held-out patients, report at the C7 gate

13 October 2026. Written by the execution session on Nicolas's Mac. This is the track's closing report. Every number is read back from the file named beside it. Paths are relative to the repository root, and `R` stands for `results/round6/cheatsheet_ext`.

## 1. Stage and status

C6 (the grid) and C7 (the analysis) are complete. All 31 sessions of C6 ended with a valid output on their first attempt, no session was excluded by the scanner, and every writer's final version passed its audit. With the pilot's four sessions, which the C5 memo counts as grid sessions, the grid has all ten sizes, nine audited cheatsheets and the combined session. The session stops here.

## 2. What was run

**Commits.** The branch `round6-cheatsheet-ext` was fast-forwarded to `main` at `509d9387`, the merge of pull request #25, and its commits since are listed by `git log 509d9387..round6-cheatsheet-C7`. The C5 decision memo was transcribed into the plan's section 4f before C6 started.

**Scripts.** The harness is unchanged since C5. The md5 of every script is in `R/C6_grid/PROVENANCE.txt` and `R/C7_report/PROVENANCE.txt`. One script is new, `code/scripts/round6_cheatsheet_ext_c7_analysis.py`.

**Where.** Everything ran on the Mac in the container of C4, with Claude Code 2.1.295 and `claude-opus-5-5` at medium effort for every session (`R/C7_report/sessions.csv`). No Longleaf job ran.

**Transcripts.** They are in `NicWYZ/hest-r6-data` at commit `ba02c81`, under `transcripts/ext/C6/`, with their md5s in `R/C6_grid/transcripts_pushed_md5.csv`. No transcript of C6 held the token.

**Batches.** Sizes 256 to 2,048 bytes ran four at once, then sizes 8,192 to 65,536 bytes four at once, then the combined session. Each size ran its writer, the audit loop and then its predictor. The scanner ran after each batch.

**Sessions, both stages** (`R/C7_report/cost_by_role.csv`).

| role | sessions | status |
|---|---|---|
| baseline | 1 | ok |
| writer | 9 | ok |
| writer revision, by resuming the writer | 3 | ok |
| checker | 12 | ok |
| predictor | 9 | ok |
| combined | 1 | ok |

## 3. Acceptance checks

- **Validity.** All 11 prediction files validate, with 1,500 spots and 50 genes each, and the analysis script recomputes every score from the raw file and matches the harness to within 1e-12 (`R/C7_report/scores_all.csv`). No prediction is constant on a slide, and no gene is constant in the measurements, so every slide's mean is over all 50 genes (`R/C7_report/grid.csv`, `R/C4_comparators/tables/constant_truth_genes.csv`).
- **Blinding.** Each of the 28 trial directories of C6 was scanned before its session started, with no hit (`R/C6_grid/blinding/clean.csv`).
- **Scanner.** No session of C6 is excluded. The only transcript hits are 425 recorded uses of system paths (`R/C6_grid/transcript_scan_hits.csv`). The filter allowed the API host only, and refused 147 requests to a telemetry host (`R/C6_grid/filter_log_summary.csv`). No committed file holds the token (`R/C6_grid/file_scan_hits.csv`).
- **Memory.** The container peaked at 2.42 GiB of 7.75 GiB with four sizes at once, so concurrency stayed at four (`R/C6_grid/memory_samples.csv`).
- **The revision path.** Three writers were resumed with the revision prompt. Each revised its file in its own directory, and a fresh checker passed the second version (`R/C7_report/audits.csv`). This is the path the pilot had not exercised.

## 4. Variables that differ between the arms of each comparison

**One size against another.** The allowance, and with it the writer session, the cheatsheet and the predictor session. Every cell is one writer and one predictor, each a separate session with its own random order of patients, spots and patches. The 4,096-byte cell ran in the pilot, a day before the others, alone and not beside three other sizes. Nothing else in its setup differs.

**A cheatsheet predictor against the baseline.** The cheatsheet and the prompt's second paragraph. Both are single sessions with different random orders.

**A cheatsheet predictor against a head.** As in the C5 report. The head sees labelled spots and a pretrained encoder's embeddings. The predictor sees image patches and text, and has no pretrained model.

**The combined session against a cheatsheet predictor.** The combined session has the 3,500 labelled spots, their patches, positions and overviews in its own directory, with no size limit and no rubric, and it is one session and not two. The cheatsheet predictor has only the text.

**The combined session against a head.** Both see the 3,500 labelled spots. The head uses a pretrained encoder's embeddings and a fixed recipe. The combined session has no pretrained model and chose its own features and model.

**The agents' curve against the codebook's.** The codebook has no agent. It differs across sizes only in its number of clusters, with one k-means fit per size.

**This extension against round 6's arm C.** The task (clear cell renal cell carcinoma, FFPE, against melanoma), the number of training patients (7 against 1) and of labelled spots, the number of test patients (3 against 1), the rubric and its audit (none in round 6), the effort level, the size grid, and the metric (the mean of three within-slide values against one slide's value).

## 5. Predictions against outcomes

| # | prediction | outcome | score |
|---|---|---|---|
| X.1 | at 0 bytes the metric lies between 0.03 and 0.20 | -0.009 | refuted |
| X.2 | the value at 4,096 bytes is above the value at 256 bytes, and the five values from 4,096 to 65,536 bytes span under 0.05 | 0.041 at 4,096 bytes against 0.105 at 256 bytes, and the five values span 0.117 | refuted, both parts |
| X.3 | no cheatsheet reaches the `uni_v2` head on the 3,500 writer spots | the best cheatsheet scores 0.158 against 0.184 | held |
| X.4 | the best cheatsheet is within 0.05 of that head | it is 0.026 below | held |
| X.5 | the writers at 32,768 and 65,536 bytes each write under 70% of their allowance in their final version | 81% and 90% | refuted |
| X.6 | at least three of the nine writers need a revision, and every final version passes | three needed one revision each, and all nine final versions passed | held |
| X.7 | the combined session scores below the best cheatsheet predictor | 0.194 against 0.158 | refuted |
| X.8 | the head on every patched spot beats the head on the sample by under 0.02 | 0.221 against 0.184, a gap of 0.037 | refuted |

Values are from `R/C7_report/grid.csv`, `R/C7_report/combined.json`, `R/C7_report/spread.json` and `R/C7_report/comparators.csv`. Five of eight are refuted. X.4 holds by a margin, 0.024, that is smaller than what one trial can resolve.

## 6. Results

### 6.1 The metric against the allowance

The metric is the mean over the three test slides of the within-slide mean Pearson over 50 genes. Each agent value is one trial, so a difference under about 0.05 cannot be told from chance. `INT24` failed the representativeness check on 9 genes of 50 (C5 report, E2), which bears on its column throughout. The table is `R/C7_report/grid.csv`, and the figure is `R/C7_report/rbar_vs_size.png`.

| allowance, bytes | bytes in the final version | share of allowance | revisions | metric | `INT13` | `INT15` | `INT24` | pooled | codebook, metric |
|---|---|---|---|---|---|---|---|---|---|
| 0 (baseline) | | | | -0.009 | -0.011 | -0.073 | 0.056 | -0.005 | |
| 256 | 248 | 97% | 0 | 0.105 | 0.174 | 0.017 | 0.125 | 0.103 | -0.041 |
| 512 | 502 | 98% | 0 | 0.110 | 0.181 | 0.022 | 0.126 | 0.114 | 0.092 |
| 1,024 | 1,018 | 99% | 0 | 0.119 | 0.204 | 0.043 | 0.110 | 0.092 | 0.147 |
| 2,048 | 2,047 | 100% | 0 | 0.136 | 0.220 | 0.009 | 0.178 | 0.083 | 0.134 |
| 4,096 | 4,096 | 100% | 0 | 0.041 | 0.103 | -0.022 | 0.041 | 0.080 | 0.115 |
| 8,192 | 8,189 | 100% | 0 | 0.158 | 0.248 | 0.065 | 0.160 | 0.091 | 0.139 |
| 16,384 | 14,573 | 89% | 1 | 0.106 | 0.137 | -0.002 | 0.183 | 0.069 | 0.151 |
| 32,768 | 26,699 | 81% | 1 | 0.123 | 0.194 | 0.089 | 0.087 | 0.095 | 0.119 |
| 65,536 | 58,845 | 90% | 1 | 0.049 | 0.076 | 0.015 | 0.056 | 0.054 | 0.129 |

The comparators and the combined session, from `R/C7_report/comparators.csv` and `R/C7_report/combined.json`.

| predictor | fitted on or given | metric | `INT13` | `INT15` | `INT24` | pooled |
|---|---|---|---|---|---|---|
| combined session | both folders | 0.194 | 0.248 | 0.105 | 0.229 | 0.178 |
| `uni_v2` head | 3,500 writer spots | 0.184 | 0.151 | 0.119 | 0.281 | 0.182 |
| `uni_v2` head | 31,075 patched spots | 0.221 | 0.187 | 0.154 | 0.321 | 0.219 |
| `virchow2` head | 3,500 writer spots | 0.126 | 0.082 | 0.042 | 0.253 | 0.125 |
| `virchow2` head | 31,075 patched spots | 0.180 | 0.126 | 0.099 | 0.315 | 0.196 |

Readings, each checked against every cell it covers.

- **Any cheatsheet helps, and size does not.** All nine cheatsheet predictors are above the baseline on the metric, by 0.050 to 0.167. The metric does not rise with the allowance. Its rank correlation with the allowance over the nine sizes is -0.017 (`R/C7_report/spread.json`). The best value is at 8,192 bytes, and a 248-byte cheatsheet scores 0.105.
- **Two sizes are low.** 4,096 and 65,536 bytes score 0.041 and 0.049. The other seven lie between 0.105 and 0.158, a span of 0.052.
- **How much one fit can move.** The codebook, which has no agent, moves between 0.092 and 0.151 from 512 bytes up, a span of 0.059, without a trend. The agents' seven higher values span about as much. The two low values lie outside that band, by 0.064 and 0.056 below its lowest point. One trial per size cannot say whether those two are properties of their sizes or of those two sessions. Section 6.4 gives what the transcripts show.
- **No cheatsheet reaches the `uni_v2` head on the metric.** On `INT13` alone, six of the nine cheatsheet predictors are above that head's 0.151. On `INT15` and `INT24` every one is below it.
- **The slides differ more than the sizes.** `INT13` is the highest of the three slides for eight of the nine cheatsheet predictors, and `INT15` the lowest for eight of the nine. On `INT15` no cheatsheet predictor exceeds 0.089.
- **Pooled against within-slide.** For the heads the two values are close. For the cheatsheet predictors from 1,024 to 32,768 bytes the pooled value is below the within-slide value, except at 4,096 bytes, where it is above. The pooled values lie between 0.054 and 0.114 at every size and vary less than the within-slide ones.

### 6.2 The size needed

`R/C7_report/bstar.csv`.

| threshold | value | size needed |
|---|---|---|
| `uni_v2` head on the 3,500 writer spots | 0.184 | not reached at any size up to 65,536 bytes |
| `virchow2` head on the 3,500 writer spots | 0.126 | between 1,024 and 2,048 bytes |

The second bracket is where the curve first crosses the threshold. The curve is not monotone. Only 2,048 and 8,192 bytes are at or above 0.126, and the four other sizes above 2,048 bytes are below it. With one trial per size and a codebook that moves by 0.059 on its own (`R/C7_report/spread.json`), the bracket is not a stable property of the curve.

### 6.3 The audit record

`R/C7_report/audits.csv`, with each verdict in `R/C5_pilot/verdicts/` and `R/C6_grid/verdicts/` and each version in the two `cheatsheets/` folders.

| allowance, bytes | bytes at version 1 | violations at audit 1 | rules broken | bytes at version 2 | violations at audit 2 | final version passed |
|---|---|---|---|---|---|---|
| 256 | 248 | 0 | | | | yes |
| 512 | 502 | 0 | | | | yes |
| 1,024 | 1,018 | 0 | | | | yes |
| 2,048 | 2,047 | 0 | | | | yes |
| 4,096 | 4,096 | 0 | | | | yes |
| 8,192 | 8,189 | 0 | | | | yes |
| 16,384 | 14,386 | 1 | F6 | 14,573 | 0 | yes |
| 32,768 | 26,959 | 3 | F3, F6, F6 | 26,699 | 0 | yes |
| 65,536 | 58,921 | 1 | F6 | 58,845 | 0 | yes |

No cheatsheet is flagged, so the row for flagged cheatsheets is empty. No writer exceeded its allowance, so nothing was cut. The mechanical check raised no flag on any version. No audit found code, a model recipe or a computed image measurement.

The five violations are of two kinds. At 16,384 bytes the cheatsheet told the reader to look at several patches of the same case to choose the tumour type. At 32,768 and 65,536 bytes it used the stain colour of a section, or blur, as a cue. The one F3 violation was a sentence on how one training section was stained. Each writer removed or reworded the passages in one revision.

A point for the reader of the rubric. The final 65,536-byte version still opens each of its seven section types with that section's stain colour, for example "Look: purple/lilac staining", and its checker passed it. The checker at 32,768 bytes had failed the same kind of phrase. The two audits were different sessions, and the rubric's F6 allows a technical property that is "described as visible tissue appearance", which leaves room for both readings.

### 6.4 What the cheatsheets contain, and what the predictors did with them

Tags by script are in `R/C7_report/tags.csv`, with the keyword counts behind each. Every final cheatsheet was then read in full, and the tags as read are in `R/C7_report/tags_read.csv`, with a note where they differ from the script's.

| allowance, bytes | A1 classes | A2 class values | A3 gradients by eye | A4 gene modules | A5 patient-level variation | A6 cautions | A7 levels and spread | metric |
|---|---|---|---|---|---|---|---|---|
| 256 | yes | yes | yes | no | no | yes | no | 0.105 |
| 512 | yes | yes | yes | no | no | yes | yes | 0.110 |
| 1,024 | yes | yes | yes | yes | yes | yes | yes | 0.119 |
| 2,048 | yes | yes | yes | yes | yes | yes | yes | 0.136 |
| 4,096 | yes | yes | yes | yes | yes | yes | yes | 0.041 |
| 8,192 | yes | yes | yes | yes | yes | yes | yes | 0.158 |
| 16,384 | yes | yes | yes | yes | yes | yes | yes | 0.106 |
| 32,768 | yes | yes | yes | yes | yes | yes | yes | 0.123 |
| 65,536 | yes | yes | yes | yes | yes | yes | yes | 0.049 |

The script's keyword tags missed the gradient and the caution in the shorter files, where they are single clauses such as "Expression tracks cellularity" and "Stain hue varies; ignore it". The table above is the reading. From 1,024 bytes up every cheatsheet holds all seven kinds of content, so the tags do not separate the sizes, and the metric does not follow them.

What the reading shows beyond the tags.

- **One message at every size.** Every cheatsheet says that all 50 genes rise and fall together with how much cellular tissue is in the spot, and that stain colour should be ignored. The 248-byte cheatsheet says little else.
- **Section types that are the training patients.** From 1,024 bytes up, the cheatsheets describe five to seven "section types" or "phenotypes" by their histology, each with its gene levels. The 32,768-byte file says seven phenotypes were seen, and the 65,536-byte file says every training section had a distinct character and gives a "section-average table for the seven types". These are the seven training patients, described by appearance and never by label. The rubric's A5 allows this, and every checker passed it. It means that most of the added bytes carry per-patient mean levels, which describe differences between patients.
- **What the larger sizes add.** 8,192 bytes adds a full table of 50 genes by pattern. 32,768 bytes adds quantiles within each phenotype. 65,536 bytes adds two tables of 50 genes by tissue compartment, one line of summary per gene and seven worked examples.
- **No forbidden content in the final versions by keyword.** The script that counts keywords for code, model recipes, computed image measurements, spot or patient labels and metric advice finds none, apart from one word at 32,768 bytes that the reading shows to be a caution about stain batches (`R/C7_report/forbidden.csv`).

What the predictors did, from their transcripts and their own summaries.

- **A level per patient, then a scaling per patch.** Seven of the nine predictors, those from 1,024 bytes up, looked at three to nine montages, assigned each test patient one of the cheatsheet's section types or a blend, and started every spot of that patient from that type's gene levels. They then adjusted each spot with measurements they computed from the image, in most cases a measure of cellularity. The patient's level is the same for all 500 of its spots, so it does not enter a within-slide correlation. Only the per-patch scaling does.
- **The two smallest sizes.** The predictors at 256 and 512 bytes viewed no image at all (`R/C7_report/sessions.csv`). They computed a cellularity score for every patch and mapped it to genes with the cheatsheet's few numbers.
- **None read patches one by one.** The most images any predictor viewed is 9.

This gives a reading of the flat curve, offered as a reading and not as a tested cause. What a predictor can turn into within-slide ranking is the cellularity rule, which fits in 248 bytes. Most of what larger cheatsheets add is between-patient level, which the metric removes. The variables that differ between a low cell and its neighbours are listed in section 4, and the transcripts do not single out one of them for the two low sizes.

### 6.5 The combined session

`R/C7_report/combined.json`, `R/C7_report/grid.csv` and `R/C7_report/comparators.csv`, and transcript `bab3f51f_combined.stream.jsonl`.

- **Score.** 0.194 on the metric, against 0.158 for the best cheatsheet predictor and 0.184 for the `uni_v2` head on the same 3,500 spots. It is 0.036 above the best cheatsheet and 0.010 above that head, and both differences are within what one trial can show. It is below the `uni_v2` head fitted on all 31,075 patched spots, at 0.221.
- **Per slide.** It is above the `uni_v2` head on the writer spots on `INT13`, at 0.248 against 0.151, and below it on `INT15` and `INT24`.
- **What it did.** In 19 turns it viewed one montage, computed hand-made features for every labelled and target patch (colour, stain separation, nucleus counts and texture), and fitted regressions on the 3,500 labelled spots with each labelled patient held out in turn. It reported a held-out correlation of about 0.12 per gene. It gave every target patient the same baseline level and took only the spot-to-spot variation from the images, because, in its words, estimating a patient's level from the images did worse than the average across patients.
- **Reading.** A session with the labelled data and no pretrained model matched the frozen pathology encoder's head on this metric, within noise, and did so by fitting a model, which the rubric forbids a cheatsheet to carry.

### 6.6 Cost, tokens and wall time

`R/C7_report/cost_by_role.csv`, over both stages. Cost is Claude Code's own estimate at list prices. A resumed revision reports its session's running total, so each revision's cost is that total less the total before it.

| role | sessions | cost, USD | mean cost, USD | output tokens | cache read | cache write | turns | wall, s | mean wall, s | largest peak context | images viewed |
|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline | 1 | 0.18 | 0.18 | 4,666 | 65,345 | 9,644 | 8 | 80.7 | 80.7 | 14,422 | 1 |
| writer | 9 | 10.55 | 1.17 | 161,068 | 12,273,246 | 608,607 | 368 | 2,050.3 | 227.8 | 153,070 | 196 |
| writer revision | 3 | 0.49 | 0.16 | 4,084 | 1,633,108 | 10,239 | 14 | 55.6 | 18.5 | 155,223 | 0 |
| checker | 12 | 1.93 | 0.16 | 26,802 | 312,372 | 166,439 | 62 | 319.2 | 26.6 | 42,695 | 0 |
| predictor | 9 | 2.30 | 0.26 | 39,550 | 1,237,087 | 157,485 | 94 | 567.1 | 63.0 | 58,423 | 32 |
| combined | 1 | 0.54 | 0.54 | 15,033 | 255,065 | 23,753 | 19 | 269.6 | 269.6 | 29,369 | 1 |
| all | 35 | 15.99 | | 251,203 | 15,776,223 | 976,167 | 565 | 3,342.5 | | | 230 |

Input tokens outside the cache are 730 in all. A writer's cost grows with its allowance, from 0.15 dollars at 256 bytes to 2.90 at 65,536 bytes, and no session reached its turn cap (`R/C7_report/sessions.csv`). The C5 report projected 15 to 40 dollars for the remaining grid, and C6 cost 14.40.

### 6.7 Comparison with round 6's arm C

Round 6's values are from `results/round6/cheatsheet/C3_report/grid.csv`, and this extension's from `R/C7_report/grid.csv` and `R/C7_report/comparators.csv`. The variables that differ are listed in section 4.

| | round 6, arm C | this extension |
|---|---|---|
| baseline, 0 bytes | 0.345 | -0.009 |
| cheatsheet at 4,096 bytes | 0.647 | 0.041 |
| best cheatsheet | | 0.158, at 8,192 bytes |
| `uni_v2` head on the writer's spots | 0.683 | 0.184 |

The two are not on one scale. Round 6's task was one where the head itself reached 0.683, and this one's head reaches 0.184. As a share of its own head, the best cheatsheet here is at 86% and round 6's 4,096-byte cheatsheet was at 95%. The baseline differs in kind. Round 6's zero-shot predictor carried 0.345 with no cheatsheet, and here it carries nothing.

## 7. Discrepancies, open questions and escalations

**Escalations.** None is new in this interval. No session failed, none was excluded, no writer exceeded its size, and no cheatsheet failed after two revisions. E2 of the C5 report stands, and `INT24`'s column is marked in section 6.1. E3, the billing check, is with Nicolas.

**Discrepancies.**

- **The 4,096-byte cell is from the pilot.** It ran a day earlier and alone. It is one of the two low values. Nothing in its setup differs from the grid's cells, and the C5 memo counts it. A reader who wants to rule the day out would need a second trial at that size.
- **Two audits read the same kind of phrase differently** (section 6.3).
- **The script's tags and the reading differ** for five of the nine cheatsheets (section 6.4). The report uses the reading.

**Open questions for the oversight chat.**

- **Q1.** The cheatsheets' section types are the seven training patients, described by appearance. Is that within what the extension meant by "transferable"? The rubric allows it and the checkers passed it.
- **Q2.** The curve's shape rests on one trial per size, and the two low sizes cannot be told from noise in the predictor session. Whether to replicate is a scope decision and not the session's.
- **Q3.** The within-slide metric removes the between-patient levels that most of the larger cheatsheets' bytes describe. The pooled value is reported beside it at every size, as section 6.7 of the instruction asks.

## 8. What was not checked

- Whether any difference between sizes would survive a second trial. Every cell is one writer and one predictor.
- Whether a different predictor session given the same cheatsheet would score the same. The writer and the predictor are confounded in every cell.
- Whether the checker's verdicts are stable. Each version was audited once, and section 6.3 shows one case where two audits disagree in kind.
- Whether the cheatsheets' gene values are correct. The checker judged the rules only, and this report did not compare the quoted means with the package.
- The cause of the two low cells.
- Billing on Nicolas's account, and the effort level beyond its being accepted, as in the C5 report.

## 9. Proposed next step

The track ends here. The oversight chat reviews this report and writes the closing memo. Nothing further is set up.

---

## What the extension established

Each sentence names the file it rests on. Every agent value is one trial.

1. On three held-out clear cell renal cell carcinoma patients, a zero-shot Opus 5.5 predictor with no cheatsheet scored -0.009 on the mean within-slide Pearson over 50 genes (`R/C7_report/grid.csv`).
2. Every one of nine rubric-bound cheatsheets, from 256 to 65,536 bytes, lifted the predictor above that baseline, to between 0.041 and 0.158 (`R/C7_report/grid.csv`).
3. Prediction did not grow with the size of the text, with a rank correlation of -0.017 between the metric and the allowance, and a 248-byte cheatsheet scored 0.105 (`R/C7_report/spread.json`, `R/C7_report/grid.csv`).
4. No cheatsheet reached the `uni_v2` benchmark head fitted on the same 3,500 labelled spots, at 0.184, and the best, at 8,192 bytes, was 0.026 below it (`R/C7_report/comparators.csv`, `R/C7_report/bstar.csv`).
5. Seven of the nine sizes lie within a span of 0.052, which is about what a size-matched codebook with no agent moves by itself from 512 bytes up, 0.059, and the two low sizes, 4,096 and 65,536 bytes, cannot be told from session noise with one trial each (`R/C7_report/spread.json`, `R/C7_report/grid.csv`).
6. The rubric and its audit held, with no code, model recipe or computed image measurement found in any version, five violations at the three largest sizes, each fixed in one revision, and all nine final versions passed (`R/C7_report/audits.csv`).
7. From 1,024 bytes up the cheatsheets describe section types that correspond to the seven training patients, each with its gene levels, so most added bytes carry differences between patients, which a within-slide metric does not reward (`R/C7_report/tags_read.csv`, `R/C6_grid/cheatsheets/c2adaa46_v2.txt`).
8. The predictors did not read patches one by one, viewing at most 9 images each, and seven of nine set one level per test patient and adjusted it per patch with measurements they computed (`R/C7_report/sessions.csv`).
9. A single session given the labelled spots directly, with no pretrained model and no rubric, scored 0.194 by fitting a model on hand-made image features, level with the `uni_v2` head on the same spots within noise and above every cheatsheet (`R/C7_report/combined.json`, `R/C7_report/comparators.csv`).
10. The slides differed more than the sizes, with no cheatsheet predictor above 0.089 on `INT15`, and the test slide `INT24` failed the representativeness check on 9 of 50 genes (`R/C7_report/grid.csv`, `R/C4_package/representativeness.csv`).
11. The 35 sessions of the pilot and the grid cost 15.99 dollars at list prices and 56 minutes of session time in all (`R/C7_report/cost_by_role.csv`).
12. Five of the eight predictions written before the run were refuted, among them that the metric would rise from 256 to 4,096 bytes and that the combined session would score below the best cheatsheet (section 5 of this report, `R/C7_report/grid.csv`).
