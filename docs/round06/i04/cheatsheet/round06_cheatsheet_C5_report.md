# Round 6 extension, the cheatsheet track on held-out patients, report at the C5 gate

13 October 2026. Written by the execution session on Nicolas's Mac. Every number here is read back from the file named beside it. Paths are relative to the repository root, and `R` stands for `results/round6/cheatsheet_ext`.

## 1. Stage and status

C4 (setup) and C5 (pilot) are complete. All five exit items of C4 are met. The pilot ran its three sessions and one audit without a failure, an exclusion or a revision. Nothing after C5 has been set up, staged or piloted. The session now stops and waits for the oversight chat's reply.

One thing changed from the instruction during the interval, by Nicolas's decision in chat on 12 October. Data preparation and the comparators ran on his Mac and not on Longleaf (section 7, escalation E1).

## 2. What was run

**Commits.** The branch `round6-cheatsheet-ext` started from `4230b713` and was fast-forwarded to `1cb6b08f` when the instruction's revision of 12 October, 15:30 arrived, before it had a commit of its own. Its commits are listed by `git log 1cb6b08f..round6-cheatsheet-C5`.

**Scripts.** All are `code/scripts/round6_cheatsheet_ext_*`, with md5s in each stage's `PROVENANCE.txt` under `R`. They are the Dockerfile and the container's start script, the filtering proxy with its direct mode and its `start.sh` (committed, as the closing memo of round 6 asked), the child runner, the probes, the scanner, the packaging script, the comparators, the prompts, the mechanical check, the builder, the harness, the scorer with its tests, and the pilot's summary script.

**Longleaf.** Two packaging jobs were submitted and both were cancelled before they started. Job 4674823 carried a mistyped commit hash and was cancelled within a minute. Job 4674826 waited about four hours in the queue, and was cancelled when Nicolas moved the work to the Mac. No job ran. The code clone `/work/users/w/e/weiyang/hest_code/HEST-1k-replication-cheatsheet` was created from a bundle and holds commit `a3e2d388`. The project tree was read and not changed, apart from an empty folder `results/round6/cheatsheet_ext/C4_package/` made for the job's log.

**On the Mac.** Claude Code 2.1.295 on the Mac and in the image. Docker Desktop 29.7.2, image `r6ext:1`, container `r6ext` (`R/C4_children/PROVENANCE.txt`). Packaging took under a minute per slide and the comparators a few minutes.

**Sessions.** Counts by role and status, from `R/C4_children/children.json`, `R/C4_isolation/probes.csv` and `R/C5_pilot/manifest.csv`.

| stage | role | sessions | status |
|---|---|---|---|
| C4.1 | one-line and resume tests, Opus 5.5 | 3 | all answered |
| C4.2 | probes I1, I2 and I3, Opus 5.5 | 3 | all completed |
| C4.2 | holder beside the probes, Haiku 5.5 | 1 | completed |
| C5 | baseline | 1 | ok |
| C5 | writer at 4,096 bytes | 1 | ok |
| C5 | checker | 1 | ok |
| C5 | predictor | 1 | ok |

## 3. Acceptance checks, C4's exit items

**Exit item 1, flags, model, authentication and billing** (`R/C4_children/children.json`).

- A confined child given only `CLAUDE_CODE_OAUTH_TOKEN` from the token file authenticated and was served `claude-opus-5-5`. Its `apiKeySource` is `none`.
- Every flag of the instruction's section 6.5 was accepted as written. `--disable-slash-commands` is added, as in round 6. The three built-in plugins remain listed, as in round 6.
- `--resume` continued a session inside the confinement with its earlier context. The resumed session kept its session ID and gave back the word it had been told to remember.
- The billing check is not complete. The session cannot see Nicolas's usage page. What it can show is that no API key was in play. Nicolas is asked to confirm that the usage of 12 and 13 October appears on his account.
- The effort level was accepted on the command line and in the environment. The stream does not echo it, so it is confirmed only as accepted.

**Exit item 2, isolation** (`R/C4_isolation/`, `R/C4_blinding/i4_tree_scan.csv`).

| property | result | evidence |
|---|---|---|
| I1 | pass | the `system/init` events list six tools, no MCP servers, no skills and no slash commands, and the probe quoted nothing from the project (`probe_reports/I1_93cfea05_report.txt`) |
| I2 | pass | five canaries, each tried by Read, Glob, Grep, Bash and through `/proc`, none read, and `canary_hits.csv` is empty |
| I3 | pass | the three hosts were refused through the proxy and unreachable without it, and the filter allowed the API host only (`filter_log_summary.csv`) |
| I4 | pass | one real trial directory of each of the five kinds has no blinded name in any path, text file or PNG metadata |

The probes ran on Opus 5.5 at medium effort. Their transcripts' md5s are in `R/C4_isolation/transcripts_md5.csv`. The confinement is round 6's `bwrap` recipe inside a Docker container that runs as an unprivileged user with every capability dropped. It needs `seccomp`, `apparmor` and `systempaths` unconfined, and neither `--privileged` nor `SYS_ADMIN`. The canaries were removed after I4 passed.

**Exit item 3, draws, samples and representativeness** (`R/C4_package/`).

- The 10 slides are `INT13`, `INT14`, `INT15`, `INT16`, `INT18`, `INT19`, `INT20`, `INT22`, `INT23` and `INT24`. The test slides are `INT13`, `INT15` and `INT24` (`draws.json`). They equal the draws recorded in the plan before anything was built.
- All 12 FFPE slides are confirmed by their `subseries` strings in both metadata tables, from 12 distinct patients (`ffpe_check.csv`). HEST's `preservation_method` column is empty for these slides, so it confirms nothing.
- Every slide has as many patched spots as the inventory's spots under tissue (`package_summary.json`).
- The target is the natural log of one plus the count, so the prompts' phrase is unchanged. Patches are at 0.5 micrometres per pixel. Stored coordinates were transposed on all 10 slides and are corrected.
- Nine slides fail the representativeness check on 0 to 3 genes of 50. `INT24` fails on 9 (`representativeness.csv`, escalation E2).

**Exit item 4, anchor and comparators** (`R/C4_comparators/tables/`).

| encoder | this run | round 1 | difference |
|---|---|---|---|
| `uni_v2` | 0.2205 | 0.2205 | under 0.0001 |
| `virchow2` | 0.2377 | 0.2378 | 0.0001 |

Both are within 0.01 (`anchor.csv`). Every comparator of section 6.7 is computed (`comparators.csv`), and section 6 below gives them.

**Exit item 5, tests** (`R/C4_tests/`).

- The scorer's five tests pass on the real test-slide values (`score_test_real.json`). True values score 1.0. Values permuted within each slide average 0.0002 over 20 permutations. A constant gene on one slide scores 0 there and is flagged. A file missing a spot fails validation. A gene made constant in the measurements on one slide is left out of that slide's mean.
- The mechanical check flags 7 of round 6's 9 cheatsheets (`check_cheatsheet_on_round6.csv`). Every cheatsheet with a code flag or a table flag is among the seven. Five of the seven are flagged for code-like lines, library names or a long table. Two, `d96d2f78.txt` and `54ff6aa7.txt`, are flagged only for long unbroken runs of characters. The two not flagged are 6,990 and 3,816 bytes long. The script cannot see computed image measurements, which the checker judges.

## 4. Variables that differ between the arms of each comparison

**The pilot's predictor against the baseline.** The predictor has `cheatsheet.txt` and the prompt's second paragraph. Beyond that, the two are separate sessions with different trial IDs, so their patients' folder letters and their patches' numbers are in different random orders. Each is one run.

**The pilot's predictor against the benchmark heads.** The predictor is a language model that sees image patches and 4,096 bytes of text, and decides for itself what to compute. A head is a ridge regression on a frozen encoder's embeddings. The head sees 3,500 or 31,075 labelled spots directly. The predictor sees none, and what it knows of them reached it through the writer's text. The head uses an encoder trained on a large pathology collection. The predictor was told no pretrained model is available and had none.

**The head on the 3,500 writer spots against the head on all patched spots.** The number of labelled spots, 3,500 against 31,075, and how they were chosen, a stratified sample against every spot. The seven slides are the same.

**The codebook against the head.** The codebook stores per-cluster gene means at one byte each and assigns by nearest centroid. The head fits a linear map. Both use `uni_v2` embeddings of the same 3,500 spots.

**This extension against round 6's arm C.** The task (clear cell renal cell carcinoma against melanoma), the number of training patients (7 against 1) and labelled spots, the number of test patients (3 against 1), the rubric and its audit, the effort level and the metric (mean of within-slide values against one slide's value).

## 5. Predictions against outcomes

| # | prediction | outcome at C5 | score |
|---|---|---|---|
| X.1 | at 0 bytes the metric lies between 0.03 and 0.20 | -0.009 (`R/C5_pilot/scores.csv`) | refuted |
| X.2 | the value at 4,096 bytes is above the value at 256 bytes, and the five largest sizes span under 0.05 | only 4,096 bytes has run | not tested |
| X.3 | no cheatsheet reaches the `uni_v2` head on the 3,500 writer spots | the one cheatsheet so far scores 0.041 against 0.184 | not tested, consistent so far |
| X.4 | the best cheatsheet is within 0.05 of that head | the one so far is 0.143 below it | not tested |
| X.5 | the two largest writers write under 70% of their allowance | not run | not tested |
| X.6 | at least three of nine writers need a revision, and every final version passes | the one writer so far passed its first audit | not tested |
| X.7 | the combined session scores below the best cheatsheet predictor | not run | not tested |
| X.8 | the head on all patched spots beats the head on the sample by under 0.02 | 0.221 against 0.184, a gap of 0.037 (`R/C4_comparators/tables/comparators.csv`) | refuted |

## 6. Results

**The pilot beside the comparators.** The metric is the mean over the three test slides of the within-slide mean Pearson over 50 genes. Agent rows are from `R/C5_pilot/scores.csv` and the others from `R/C4_comparators/tables/comparators.csv`. Each agent value is one trial, so a difference under about 0.05 cannot be told from chance.

| predictor | fitted on or given | metric | `INT13` | `INT15` | `INT24` | pooled |
|---|---|---|---|---|---|---|
| baseline, 0 bytes | nothing | -0.009 | -0.011 | -0.073 | 0.056 | -0.005 |
| cheatsheet, 4,096 bytes | the writer's text | 0.041 | 0.103 | -0.022 | 0.041 | 0.080 |
| `uni_v2` head | 3,500 writer spots | 0.184 | 0.151 | 0.119 | 0.281 | 0.182 |
| `uni_v2` head | 31,075 patched spots | 0.221 | 0.187 | 0.154 | 0.321 | 0.219 |
| `virchow2` head | 3,500 writer spots | 0.126 | 0.082 | 0.042 | 0.253 | 0.125 |
| `virchow2` head | 31,075 patched spots | 0.180 | 0.126 | 0.099 | 0.315 | 0.196 |
| codebook at 4,096 bytes | 3,500 writer spots | 0.115 | 0.090 | 0.106 | 0.149 | 0.106 |

The codebook at the nine sizes runs from -0.041 at 256 bytes to 0.151 at 16,384 bytes, and the full row for each size is in `comparators.csv`. The mean predictor is constant on every slide, so it scores 0 by the scorer's rule, within slides and pooled. No gene is constant in the measurements on any test slide (`constant_truth_genes.csv`).

Three readings of this table, each checked against every cell it covers.

- The cheatsheet predictor is above the baseline on the metric by 0.050, which is at the edge of what one trial can show. It is above on `INT13` and `INT15` and below on `INT24`.
- Both agent predictors are below both `uni_v2` heads on the metric and on every slide.
- `virchow2` is below `uni_v2` on the metric at both training sizes, although round 1 found it the better encoder on this task. On `INT24` alone the two are close.

**The writer and its audit** (`R/C5_pilot/writers/d35a522f.json`, `R/C5_pilot/verdicts/727d88f6.json`, `R/C5_pilot/mechanical/d35a522f_v1.json`). The writer wrote 4,096 bytes, exactly its allowance, and nothing was cut. The mechanical check raised no flag. The checker found no violation, so there was no revision and version 1 is final.

**What the cheatsheet contains** (`R/C5_pilot/cheatsheets/d35a522f_v1.txt`). It opens with each gene's overall mean and, for the main ones, a high quantile. Its main rule is that all 50 genes rise and fall together with how much cellular tissue is in the spot, with typical values for dense tumour, for hypocellular or necrotic tissue, for lymphoid aggregates and for vessels and haemorrhage. It then describes seven kinds of section by their histology, from high-grade solid tumour to mostly fibrotic tissue, with gene values for each, without naming a patient. It closes with five gene groups and their biology, and a rule for scaling a section's level by a patch's cellularity. In the rubric's terms it holds A1, A2, A3, A4, A5, A6 and A7.

**What the sessions did**, from their transcripts. The writer computed image features with scikit-image while it studied the data, and wrote none of them into the cheatsheet. Both predictors looked at one to four montages, then wrote a script that computes colour and texture features for every patch and maps them to genes by rules of their own. Neither read patches one by one. The predictor with the cheatsheet typed the cheatsheet's gene levels and section types into its script and assigned each folder a mixture of section types by eye.

**Cost and size per role** (`R/C5_pilot/sessions.csv`, `R/C5_pilot/patches_viewed.csv`). Cost is Claude Code's own estimate at list prices.

| role | input tokens | output tokens | cache read | cache write | cost, USD | turns | wall, s | peak context | images viewed | patches in them |
|---|---|---|---|---|---|---|---|---|---|---|
| baseline | 16 | 4,666 | 65,345 | 9,644 | 0.18 | 8 | 80.7 | 14,422 | 1 | 24 |
| writer | 56 | 16,093 | 1,096,831 | 67,658 | 1.08 | 49 | 200.5 | 73,274 | 26 | 602 |
| checker | 6 | 1,705 | 12,807 | 6,542 | 0.09 | 5 | 21.2 | 8,509 | 0 | 0 |
| predictor | 16 | 4,681 | 101,815 | 15,130 | 0.24 | 11 | 61.5 | 20,746 | 4 | 107 |

The writer's 602 patches are not all different, since the montages of extreme spots can repeat patches from the random ones. Peak memory of the container during the pilot was 0.82 GiB of 7.75 GiB, with one session at a time (`R/C5_pilot/memory_samples.csv`).

**Scanner** (`R/C5_pilot/transcript_scan_hits.csv`, `R/C5_pilot/file_scan_hits.csv`). No session is excluded. The transcript scan's only hits are 65 recorded uses of system paths such as `/tmp`. The filter allowed the API host only and refused 19 requests to a telemetry host. No committed file holds the token.

**Projection for C6.** The grid still needs 8 writers with their audits, 8 predictors and the combined session, if the pilot's three sessions are accepted as grid sessions. From one trial per role, a writer costs about 1 dollar, an audit about 0.1 and a predictor about 0.25. Larger allowances and revisions will cost more, and the combined session reads both folders. A range of 15 to 40 dollars at list prices, 10 to 30 million tokens (almost all of it cache reads) and under one hour of wall time at four sessions at once is this session's estimate, and it rests on one trial per role. Four at once fits the container's memory by a wide margin.

## 7. Discrepancies, open questions and escalations

**Escalations.**

- **E1. Data preparation and comparators ran on the Mac.** The instruction places them on Longleaf. After job 4674826 had waited about four hours, Nicolas wrote in chat, "just rsync the data to my disk what are we even waiting for longleaf for". The session copied 96 files, about 10 GB, from the project tree to `~/hest-1k/r6ext_private/tree/`, checked every md5 against Longleaf's (`R/C4_package/inputs_md5_longleaf.txt`), and ran the unchanged packaging and comparator scripts in the container. The raw patch files were deleted from the Mac after packaging. scikit-learn is 1.9.1 on both machines. The package does not exist on Longleaf.
- **E2. `INT24` fails the representativeness check on 9 genes of 50**, over the limit of 5. Its sample's standard deviation is up to 1.145 times the slide's (`R/C4_package/representativeness.csv`). The sample is kept, as section 6.1 says. `INT24` is a test slide, and it is also the slide on which every head scores highest.
- **E3. The billing check is not complete** (section 3, exit item 1).

**Readings of the instruction made while building.** They are in the plan's section 4d, R1 to R9. Three matter most.

- 6.4 calls a mechanical flag "an input to the checker", while 6.2 and 6.3 fix the checker's files and prompt without it. The harness does not show the mechanical report to the checker.
- A session that stops at its turn cap with a valid output file is used, with its stop reason recorded.
- The transcript scan does not treat the uppercase task code or "patient" with a number as blinded names. The scan of trial directories does.

**Findings about the harness.**

- The scanner's sample-ID pattern first matched by chance inside the base64 image data of three transcripts. The pattern now requires the ID to stand apart from base64 characters. This was fixed before the pilot's scan was recorded.
- A trial can read `bwrap`'s command line in `/proc/1/cmdline`, which holds its own path under `/trials` and the proxy folder's name. Nothing about the task or data is in it.
- The image has no `curl`, so the I3 probe's fetches were made with Python only.
- The I2 probe's transcript holds the token, which the probe read from its own environment as instructed. The copy pushed to the private repository has the token replaced by a marker, and its md5 therefore differs from the one in `R/C4_isolation/transcripts_md5.csv`. Both md5s are in `R/C5_pilot/transcripts_pushed_md5.csv`.

**Open questions for the oversight chat.**

- **Q1.** Both predictors scored far below round 6's, and both wrote a feature script after viewing at most four montages. Is that the behaviour the extension wants to measure, given that the prompts are fixed? Changing a prompt is not the session's to decide, and nothing was changed.
- **Q2.** Should the pilot's three sessions count towards the grid?
- **Q3.** Should `curl` be added to the image and the I3 probe rerun, or is the Python-only probe enough?

## 8. What was not checked

- Whether usage is billed to Nicolas's account.
- Whether the effort level is applied, beyond its being accepted.
- Whether the confinement holds against a probe at higher effort or with more turns. The I2 probe used 14 turns and the I3 probe 8.
- Whether the audit loop's revision path works with a real writer. The pilot's cheatsheet passed at once, so the resume with the revision prompt, the handling of a failed revision and the flagging after two revisions have run only as far as the C4.1 resume test.
- Whether a second checker would agree with the first. The cheatsheet was audited once.
- The packaging on Longleaf's own environment. It ran in the container, with the same scikit-learn version and a newer numpy.
- Patches per viewed image were counted from the commands that built the montages, not from the images.

## 9. Proposed next step

Wait for the C5 decision memo. If it accepts the harness unchanged, C6 runs the remaining eight sizes and the combined session, four at a time, with the scanner after each batch.
