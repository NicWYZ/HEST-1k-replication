# Round 6, the cheatsheet track, C1 gate report

12 October 2026. Execution session (Claude Code cloud session, container `container_01X2Wndmgtf3F8ecgnayq6C3`), branch `round6-cheatsheet`. The instruction is `docs/round06/i01/cheatsheet/round06_cheatsheet_track.md` at revision 11 October, 22:50. The operating plan with flags F1 to F16 is `docs/round06/tracks/cheatsheet/round06_cheatsheet_plan.md`.

The gate rule. Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. Contact with anyone outside the project is never the session's decision.

## 1. Stage and status

C0 and C1 are done and the session has stopped at the C1 gate. Eleven of the twelve pilot slots have a counted trial. The twelfth, Haiku's arm B combined session, failed after four attempts, each excluded by the transcript scanner because the agent tried to download pretrained models or looked outside its directory (section 7, E4). No C2 trial has been set up or run.

## 2. What was run

- Starting commit `23cbb0d8e88a5ae185600ca78b56a74b517a08e1` on `main`. The pilot ran from commit `55913b0719ca9bcfabbe62f3cca9c9322f7285c3` (`results/round6/cheatsheet/C1_pilot/PROVENANCE.txt`), with Claude Code 2.1.296. The md5 of every script is in `results/round6/cheatsheet/C1_pilot/scripts_md5.csv`.
- The packaging job ran on Longleaf as job 4612750 on partition `spill`, node `c151412.ll.unc.edu`, from commit `b1130651d76f1bbc0e4a636690df2a93861e2723`, in 36 seconds, with exit code 0 (`results/round6/cheatsheet/C0_package/PROVENANCE.txt`). Nicolas pushed its output to the private repository `NicWYZ/hest-r6-data`.
- Trials run as confined child processes in the container, two at a time. The pilot's first trial started at 03:54:35 UTC and its last finished at 05:40:51 UTC on 12 October (`results/round6/cheatsheet/C1_pilot/manifest.csv`).
- Trial counts by status over the pilot's 19 attempts are 11 done and 8 excluded, with no failure from an invalid output (`results/round6/cheatsheet/C1_pilot/manifest.csv`).
- C0's own child sessions (the authentication tests, the model checks and the isolation probes) are not grid trials and are listed in the plan, section 3.
- The numeric-claim sweep over this report and the plan, with exceptions in `.verify-exceptions-cheatsheet`, verifies all 159 claims in this report. The plan has no unresolved claim and 36 uncited ones, most in its copy of the instruction's sections 6 to 8.
- Transcripts are in `NicWYZ/hest-r6-data` under `transcripts/C0_isolation/` and `transcripts/C1_pilot/`, with their md5s in `results/round6/cheatsheet/C0_isolation/transcripts_md5.csv`, `results/round6/cheatsheet/C0_isolation/rerun/transcripts_md5.csv` and `results/round6/cheatsheet/C1_pilot/transcripts_md5.csv`. All 19 pilot transcripts were checked against their md5 after the push.

## 3. Acceptance checks

**Exit item 1, flags and model IDs.** A confined child authenticates. A leave-one-out test over the thirteen variables of instruction 6.4, and a run with all thirteen dropped, all authenticated, so the children get none of them (plan F3). Without the credential folder bound, the child is not logged in, so the folder stays bound as 6.4 says (plan F14, a test Nicolas approved in chat). Each model ID answered a one-line prompt at `--effort high` and was served under the same ID, `claude-haiku-5-5`, `claude-sonnet-5-5` and `claude-opus-5-5`. Every pilot trial's `system/init` event shows the same three served IDs and Claude Code 2.1.296 (`results/round6/cheatsheet/C1_pilot/manifest.csv`). Three changes to the command of 6.4 were made, each a working equivalent the instruction lets the session choose.
- The CA bundle is bound after `--tmpfs /root`, because the bundle lives under `/root` and the earlier bind is hidden by the tmpfs (plan F6).
- `--disable-slash-commands` is added, because `--safe-mode` still lists Claude Code's bundled skills (plan F11).
- The child's output goes through pipes rather than file descriptors on the log files, after the I2 probe found it could read its own log through `/proc/1/fd/1` (plan F12).

**Exit item 2, isolation.** Both probe runs were on Opus. The second ran on the final harness. In both, no canary string appears in any probe output or transcript (`results/round6/cheatsheet/C0_isolation/canary_hits.csv` and `results/round6/cheatsheet/C0_isolation/rerun/canary_hits.csv` are empty). The probes' sessions and costs are in `results/round6/cheatsheet/C0_isolation/probes.csv` and `results/round6/cheatsheet/C0_isolation/rerun/probes.csv`.
- I1. The probe listed what it received as Claude Code's system prompt, the six tool descriptions and Claude Code's own reminders, and named no file, repository, person or dataset (`results/round6/cheatsheet/C0_isolation/probe_reports/I1_4835676c_report.txt`). Its verbatim dump was stopped by the child's own safety classifier, and the rerun's I1 session was stopped by the API's prompt-extraction safeguard. Every init event lists the six tools and no MCP server. It still lists three built-in plugins of Claude Code that no flag removes (plan F11), so I1's "no plugins" criterion is not met to the letter.
- I2. In both runs the probe failed to read all four canaries (in the clone, in `/srv/r6_private`, in the home directory and in a trial running at the same time) through Read, Glob, Grep, Bash and `/proc/*/root`, `/proc/*/cwd`, `/proc/*/environ` and `/proc/*/fd`. Its reports name the credential files, so they are kept private and not committed.
- I3. In both runs, fetches of huggingface.co, github.com and pypi.org with curl, urllib and raw sockets were refused with the proxy variables set, failed to resolve with them unset, and a scan of every localhost port found only the filter's port, which refused the three hosts (`results/round6/cheatsheet/C0_isolation/probe_reports/I3_8670bd6d_report.txt`, `results/round6/cheatsheet/C0_isolation/rerun/probe_reports/I3_8bdce2fc_report.txt`).
- I4. The builder's blinding scan runs on every trial directory before its child starts, and no pilot trial was stopped by it. A planted sample ID was caught in a test.
- The canaries were removed after the rerun.

**Exit item 3, the comparator anchor.** The benchmark head fitted on all spots of one slide and scored on all spots of the other reproduces round 1 in all four cells (`results/round6/cheatsheet/C0_comparators/anchor.csv`).

| encoder | direction | $\bar r$ now | round 1 | absolute difference |
|---|---|---|---|---|
| `uni_v2` | split0, S1 to S2 | 0.676296 | 0.6763 | 0.000004 |
| `uni_v2` | split1, S2 to S1 | 0.646207 | 0.6462 | 0.000007 |
| `hoptimus1` | split0, S1 to S2 | 0.706857 | 0.7069 | 0.000043 |
| `hoptimus1` | split1, S2 to S1 | 0.610832 | 0.6109 | 0.000068 |

**Exit item 4, the scorer.** On S1*'s real targets, true values score exactly 1, values permuted across spots score 0.004404 on average over 20 permutations, a constant gene scores 0 and is flagged, and a file missing a spot fails validation (`results/round6/cheatsheet/C0_comparators/scorer_tests.csv`).

**The package.** All 20 files match the job's manifest md5s after staging. The counts it records, from `results/round6/cheatsheet/C0_package/package_summary.json`, are these.
- S1 has 3,886 spots in its AnnData and 1,741 with a benchmark patch. S2 has 1,830 and 1,293.
- The training blocks hold 814 of S1's patched spots and the held-out blocks 927, shares of 0.468 and 0.532, both above 35%.
- 579 held-out spots are eligible under the buffer applied to all four edges of a block (597 if only internal edges counted), so S1* has its full 500. S2* has 500.
- The target is log1p of the raw count, with a maximum difference of 0.0 from scanpy's `log1p` on both slides, so the prompts' phrase "as log(1 + count)" stands and 6.3's one exception is not used.

## 4. What differs between the arms of each comparison

Spot counts here are from `results/round6/cheatsheet/C0_package/package_summary.json` and cheatsheet sizes from `results/round6/cheatsheet/C1_pilot/manifest.csv`.

- **Baseline against predictor, same model.** The predictor has `cheatsheet.txt` and the prompt's second paragraph. Each is a separate session with its own random patch IDs. The predictor's input also depends on one writer session, which is itself a single draw. Both are scored on the same 500 S1* spots.
- **Predictor against combined session, same model.** The combined session sees the 814 training-block spots' expression, positions, patches and the masked overview directly, where the predictor sees the writer's text of 6,892 to 17,688 bytes. The prompts and directory layouts differ, and the combined session decides itself what to compute from the labels.
- **One model against another.** The model differs, along with every choice its sessions made. There is one replicate per cell, so a model's difference is confounded with the draw of that session and, for predictors, of its writer.
- **A language-model session against a comparator.** The comparators are fitted on the same 814 training-block spots and scored on the same S1* spots. They see the `uni_v2` or `hoptimus1` embedding of each patch rather than the image. The codebook's centroids, which it needs to assign a patch, are not counted in its bytes.
- **A counted trial against an excluded attempt of the same slot.** Same inputs and prompt. The attempts differ in what the agent chose to do, and the scanner keeps only attempts that did not look outside their directory or try the network. So the counted trial is selected on behaviour (E4).

## 5. Predictions against outcomes

The predictions are those of instruction section 8, written before any run.

| # | prediction | C1 outcome | verdict |
|---|---|---|---|
| C.1 | At $b = 0$, Opus's $\bar r$ on S1* is between 0.05 and 0.35, and Haiku's is below Opus's | Opus 0.502, Haiku 0.260 | refuted, since Opus is above the range. Haiku is below Opus |
| C.2 | In arm C no model reaches the `uni_v2` comparator's $\bar r$ on S2* at any finite size | arm C not run | not tested |
| C.3 | In arm C Opus's combined session is above its 262,144-byte value and below the `uni_v2` comparator | arm C not run | not tested |
| C.4 | In arm A no model reaches 0.8 at 32,768 bytes, and at least one reaches it at 262,144 | arm A not run | not tested |
| C.5 | In arm B, each model's value at 262,144 bytes is within 0.05 of its value at 32,768, and below its arm A value at 262,144 | one size of arm B only | not tested |
| C.6 | Replicate means are ordered Opus, Sonnet, Haiku in at least two thirds of the pairs of arm and finite size | one replicate of one pair. Opus 0.600, Haiku 0.545, Sonnet 0.400 | not tested |

Scores are from `results/round6/cheatsheet/C1_pilot/c1_trials.csv`.

## 6. Results

**C1 item 1, the twelve slots beside the comparators on S1*.** All on S1*, one replicate (`results/round6/cheatsheet/C1_pilot/c1_trials.csv`, `results/round6/cheatsheet/C0_comparators/comparators.csv`).

| model | baseline, $b = 0$ | arm B predictor, 32,768 bytes | arm B combined, $b = \infty$ | writer's cheatsheet, bytes kept |
|---|---|---|---|---|
| Haiku | 0.260 | 0.545 | failed after 4 excluded attempts | 6,990 |
| Sonnet | 0.339 | 0.400 | 0.669 | 6,892 |
| Opus | 0.502 | 0.600 | 0.705 | 17,688 |

| comparator on S1* | arm A, fitted on all S1 | arm B, fitted on the training blocks |
|---|---|---|
| benchmark head, `uni_v2` | 0.872 | 0.757 |
| benchmark head, `hoptimus1` | 0.873 | 0.754 |
| codebook, 4,096 bytes ($k = 81$) | 0.794 | 0.720 |
| codebook, 32,768 bytes ($k = 655$) | 0.909 | 0.684 |
| codebook, 262,144 bytes (every writer spot) | 1.000 | 0.669 |

No writer exceeded its size and none was truncated. Each wrote well under 32,768 bytes (`results/round6/cheatsheet/C1_pilot/manifest.csv`, columns `bytes_written` and `bytes_kept`). In this one replicate, every arm B session at 32,768 bytes and every combined session scored below the `uni_v2` benchmark head's 0.757 on the same spots, and each model's predictor scored above its own baseline. The excluded attempts scored 0.186, 0.316 and 0.290 for Haiku's baseline, 0.675, 0.695, 0.681 and 0.639 for Haiku's combined session, and 0.698 for Opus's combined session (`results/round6/cheatsheet/C1_pilot/manifest.csv`). They do not count.

What each cheatsheet contains (`results/round6/cheatsheet/C1_pilot/cheatsheets/`).
- **Haiku's** (`443f584b.txt`) sorts patches into six visual archetypes (tumour nests, sparse or blank, immune-rich, cornified epithelium, basal-squamous with stroma, non-cornified epithelium), each with its share of spots and a description of its look. A table gives every gene's overall mean, SD, fraction of zeros and mean in each archetype. Short sections on gene programs, visual cues within an archetype and prediction rules follow.
- **Sonnet's** (`d96d2f78.txt`) names two gene axes (tumour and stroma against keratinocyte), describes the section's appearance, gives rules for five patch classes from empty to tumour, and tabulates each gene's mean per class, with advice to stay near class means.
- **Opus's** (`50e31fff.txt`) defines three gene-program scores (keratinocyte, melanoma and stroma, immune and vascular) and six visual classes with frequencies and descriptions. A table gives each gene's class means and linear coefficients on the three scores. An optional Python recipe computes nine hand-built image features and maps them through 80 feature prototypes to the three scores.

None holds values keyed to individual patches. All three are per-class values keyed to visual descriptions, and Opus's adds coefficients and code.

**C1 item 2, tokens, cost, turns and wall time per model and role.** Cost is Claude Code's own `total_cost_usd`, an estimate at API prices, not what Nicolas's subscription is charged (E10). From `results/round6/cheatsheet/C1_pilot/c1_by_model_role.csv`, counted trials only.

| model | role | output tokens | cache reads | cost, US$ | turns | wall, s |
|---|---|---|---|---|---|---|
| Haiku | baseline | 12,602 | 147,464 | 0.011 | 12 | 79.9 |
| Haiku | writer | 22,400 | 484,006 | 0.026 | 28 | 259.0 |
| Haiku | predictor | 14,009 | 288,364 | 0.015 | 15 | 94.6 |
| Sonnet | baseline | 4,166 | 47,901 | 0.085 | 7 | 56.5 |
| Sonnet | writer | 6,248 | 139,185 | 0.167 | 13 | 81.5 |
| Sonnet | predictor | 2,327 | 45,827 | 0.057 | 5 | 30.5 |
| Sonnet | combined | 3,634 | 72,386 | 0.084 | 8 | 63.8 |
| Opus | baseline | 21,487 | 788,063 | 1.023 | 38 | 310.8 |
| Opus | writer | 30,753 | 1,471,327 | 1.446 | 45 | 504.6 |
| Opus | predictor | 16,113 | 716,617 | 0.855 | 32 | 174.1 |
| Opus | combined | 23,597 | 903,072 | 0.997 | 34 | 1928.8 |

Over all 19 attempts the pilot cost 5.1957 US dollars at API prices, of which 4.767 was for counted trials. Input tokens outside the cache were under 100 per session and cache writes are in the file. Haiku's four combined attempts cost 0.081 together and took 5,523 seconds. Failures were only exclusions, with causes in E4.

**C1 item 3, the projection.** The masterplan's grid per model and role, at the pilot's cost and wall time per counted trial with every attempt it took included (`results/round6/cheatsheet/C1_pilot/c1_projection.csv`, totals in `results/round6/cheatsheet/C1_pilot/c1_projection_totals.csv`).

| model | projected cost, US$ | projected wall, hours, serial | at two at once |
|---|---|---|---|
| Haiku | 0.86 | 3.63 | 1.82 |
| Sonnet | 3.80 | 0.58 | 0.29 |
| Opus | 43.39 | 6.12 | 3.06 |
| total | 48.05 | 10.33 | 5.16 |

The projection rests on assumptions the pilot could not check. A writer's cost is taken as the same at every size, and each role's cost as the same in every arm, because the pilot ran one size and one arm per role. Haiku's combined row is a lower bound, since no attempt counted. The 117 sessions include the 11 counted pilot trials. No usage limit was hit during the pilot, so the rate the limits allow was not measured. Two trials at once ran without a resource failure. CPU and memory per trial were not recorded, so whether more fit was not measured (E8).

**C1 item 4, the proposed i02 grid.** Nicolas has not said anything about budget in this session. The full grid projects to 48.05 US dollars at API prices. The masterplan's cut order saves little, because Opus is 43.39 of it and the cuts touch Haiku and Sonnet (`results/round6/cheatsheet/C1_pilot/c1_cuts.csv`).

| step | projected cost after the step, US$ | saving, US$ |
|---|---|---|
| full grid | 48.05 | 0 |
| cut 1, arm A combined on Haiku only | 46.66 | 1.39 |
| cut 2, Haiku one replicate | 46.24 | 0.42 |
| cut 3, no 4,096 bytes for Sonnet | 45.23 | 1.01 |

The proposal is the masterplan's full grid, in one session at two trials at once, once the exclusion question of E4 is decided. Whether to split it across three sessions is the memo's decision. A split by model would put most of the wall time in the Opus session. If cost must come down, a cut that touches Opus would be needed to move the total.

**C1 item 5.** The predictions C1 can score are in section 5.

## 7. Discrepancies, open questions and escalations

### Escalations

- **E1. Spot counts differ from the inventory.** The benchmark patches cover 1,741 of TENX115's 3,886 spots and 1,293 of TENX117's 1,830 (`results/round6/cheatsheet/C0_package/package_summary.json`). Every arm, writer and comparator uses the patched spots, since a spot without a patch has no image and no embedding. The masterplan's scale note changes accordingly. The S1 matrix at one byte per value is 1,741 × 50, or 87,050 bytes, rather than 194,300, so 262,144 bytes still holds all of it.
- **E2. No image of the whole section exists on Longleaf.** Rounds 3 and 4 never downloaded whole-slide images. The writers' `overview.png` is a mosaic of the S1 patches at their positions, 1,353 by 1,500 pixels, white where there is no patch (`results/round6/cheatsheet/C0_package/overview.json`). No download was made.
- **E3. The stored coordinates are transposed relative to the images.** The packaging job's axis check found no overlapping pairs, because its cut-off excluded neighbours exactly 100 µm apart, which is the grid spacing. Rerun in the container over 300 pairs, overlapping pixels differ by 38.1 grey levels when stored column 0 is read as x and by 2.7 when column 1 is (`results/round6/cheatsheet/C0_package/axes.json`). The overview and the writers' positions are rebuilt in the image frame by `code/scripts/round6_cheatsheet_derive.py`, and the package's own overview is not used. The blocks, held-out set and S1* do not change under transposition (plan F16).
- **E4. Exclusions select on behaviour, and Haiku's combined slot failed.** Eight of 19 pilot attempts were excluded. Haiku's baseline listed `/data`, `/home` and `/mnt` looking for labelled data in three attempts and passed on the fourth. Haiku's combined session looked for a HuggingFace cache or tried to download from `download.pytorch.org` or `huggingface.co` in all four attempts. Opus's combined session ran `curl https://pypi.org` once. Every such attempt failed at the network or found nothing. The filter's log shows CONNECT requests allowed only to `api.anthropic.com` over the whole session, and refused ones to `download.pytorch.org`, `github.com`, `huggingface.co`, `pypi.org` and a telemetry host. The log is kept in the container and not committed. The scanner applies 6.5 as written, so each was excluded. There are two consequences. Counted trials are selected for not exploring, which may bias scores, and the excluded attempts' scores (section 6) are similar to the counted ones but not identical. And a Haiku combined trial may never pass, so arm B's and arm C's Haiku combined cells could stay empty in the grid. Changing the rule is not the session's decision. Two options, for the memo.
  - (a) Keep the rule, cap attempts at four as the pilot did, and report empty cells.
  - (b) Exclude for a canary string, a sample ID, credential contents, a nested session, or any reply that came back from a host other than the API. Record but do not exclude listings of empty directories and network attempts the filter refused. The scanner already separates these kinds (`results/round6/cheatsheet/C1_pilot/scan_hits.csv`).
- **E5. The credential folder is visible inside the confinement.** A child cannot log in without it (plan F14), so it stays bound read-only as 6.4 says. One C0 smoke-test agent listed it while looking for data, and the scanner excluded it. No pilot transcript contains the credential contents, and every committed file was scanned for credential patterns before commit.
- **E6. I1 is not met to the letter.** Three built-in Claude Code plugins appear in every init event and no flag removes them (plan F11). The I1 probe's verbatim quote was blocked by safeguards twice, so I1 rests on its summary and on the init events.
- **E7. Two pilot trials were interrupted by the session's own restart before any child started.** IDs `5f939f77` and `156bff98` were being built at 03:54 UTC when the runner was stopped to relaunch it detached from the tool's two-hour limit. No child ran and no manifest row exists for them, and their directories were removed.
- **E8. The container differs from the instruction.** It has 4 CPUs and about 15 GB. scipy, scikit-image, scikit-learn, pyarrow and h5py were missing and were installed with `pip` (plan F1, F5). Trials see the versions in `results/round6/cheatsheet/C1_pilot/PROVENANCE.txt`.
- **E9. Cost figures are Claude Code's estimates at API prices.** How they map to Nicolas's usage limits is not known to the session.

### Open questions for the memo

1. E4, which exclusion rule C2 uses.
2. The i02 grid and budget (R6-2), and whether to split by model.
3. Whether the eleven counted pilot trials count towards the grid. The harness did not change after the first pilot trial, so they qualify under C1's rule. If the memo changes the exclusion rule, the excluded attempts' status would be re-read under it.

## 8. What was not checked

- Whether a writer's cost depends on its size, and whether a role's cost differs by arm. The projection assumes neither.
- CPU and memory per trial, and so how many trials fit at once.
- Whether the three built-in plugins add anything to a child's context beyond their names.
- The I1 verbatim quote, which safeguards blocked twice.
- Whether excluded and counted attempts differ systematically in score. With one counted trial per slot this cannot be estimated.
- The cheatsheets' contents were read by the session, not tagged by script. The C3 tagging script is not written.

## 9. Proposed next step

The C1 decision memo sets the exclusion rule (E4), the i02 grid and budget, and whether to split. Then C2 runs that grid with the pilot's harness, writers before their predictors, with transcripts pushed and the scanner run after every batch.
