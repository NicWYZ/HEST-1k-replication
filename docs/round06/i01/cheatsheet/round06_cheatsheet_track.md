# Round 6, the cheatsheet track, on how large a cheatsheet a language model needs to predict expression from histology

11 October 2026. Prepared by the oversight chat for a fresh Claude Code session on Longleaf. This document is self-contained. The track starts from `main` of `NicWYZ/HEST-1k-replication` at the commit that carries this document, on its own branch `round6-cheatsheet`. Read this document fully, then transcribe sections 6 and 7 into `docs/round06/tracks/cheatsheet/round06_cheatsheet_plan.md` before running anything. The round's plan is `docs/round06/masterplan.md`.

---

## 1. Your role and the people

You are the execution agent. A separate chat session, the oversight chat, reviews your reports, makes scope decisions and writes decision memos, which Nicolas hands to you in full. Nicolas Weiyang Zhang (Longleaf ONYEN `weiyang`, Slurm accounts `rc_htzhu_pi` and `rc_tengfei_pi`) is the first-year biostatistics PhD student whose project this is. He reads every command before it runs and will ask why. His advisors are Dr. Hongtu Zhu and Dr. Daiwei (David) Zhang at UNC. David proposed this experiment.

The repository's `CLAUDE.md` loads into your session because you run inside the clone. It belongs to the oversight chat. Do not edit it and do not act on its plan. Its section 7 rules apply to you, except that rule 5's route of bundles is replaced for this track by section 5 here, because you work on Longleaf directly.

Your responsibilities are to build the trial harness, run the trials on Longleaf through Slurm, verify every stage's output against an expected value before moving on, write reports in the format of section 9, commit and push on your branch, and stop at each gate. You do not make scope decisions. Anything this document does not cover is reported as a proposal, not done.

**The gate rule, in the wording Nicolas approved.** Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. Contact with anyone outside the project is never the session's decision.

This track's gates are C1 and C3.

**How Nicolas wants things written.** Plain, natural prose. No em-dashes. No colon-then-explanation constructions. No compressed or clever phrasing. Math as LaTeX, with each `$$` on a line of its own. Numbers quoted at the precision the comparison needs, with the relative scale stated. Full precision stays in the files. Every number in a report is read back from the file named beside it. Do not inflate length.

---

## 2. What this track is for

David's question. An agent predicts the expression of 50 genes from H&E patches. A second agent, which saw the measured expression, writes a text cheatsheet of limited size, and the predicting agent may use it. How large must the cheatsheet be for the predictions to reach a given accuracy? Nicolas's purpose, set on 11 October, is to learn whether one-shot or few-shot prediction with a general-purpose language model can beat pathology foundation models. So nothing restricts what a cheatsheet contains, and every result is set beside the benchmark's encoders given the same labelled spots.

The design is in `docs/round06/masterplan.md`, sections "Design" and "Trial count". In short, the writer and the predictor are always separate fresh sessions. Three arms separate copying from learning. Arm A scores the predictor on spots the writer saw, arm B on a held-out region of the same section, and arm C on a second patient's slide. Sizes run over $0$, $4{,}096$, $32{,}768$ and $262{,}144$ bytes, and a combined session that sees the labelled spots and the targets together gives $b = \infty$. Three models run at high reasoning effort.

What is not claimed. This track builds no method for the paper and makes no claim of novelty in any document. It measures and reports.

---

## 3. Data and assets

**Repository** at the starting commit. Everything under `results/` from rounds 1 to 5 is read-only for you, and so is every earlier script and document. `docs/WAYS_OF_WORKING.md` is the accumulated procedure. Read it before your first job.

**Longleaf project tree** `/work/users/w/e/weiyang/hest_replication`, on `main` at tag `round4-data-v2`. Keep its checkout as it is. Never compute on the login node. The project's Python is `/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python`, called by absolute path in every job script.

| asset | path | what it gives you |
|---|---|---|
| benchmark data | `bench_data/SKCM/` in the project tree, with `adata/*.h5ad`, the patches, the splits and `var_50genes.json` | the two slides, their spots, the 50 genes and the target |
| embeddings | `embeddings/SKCM/<encoder>/<sample>.h5` in the project tree | `uni_v2` and `hoptimus1` embeddings for every spot |
| round-1 faithful runs | `results/faithful/pca_ridge/<encoder>/SKCM/split0/` and `split1/` (`config.json`, `results.json`) | the benchmark head's configuration and its per-direction Pearson, the anchor of C0.4 |
| the round-1 pipeline | `code/scripts/` of the repository, the faithful HEST-bench harness of round 1 | how the target is computed from counts. Reuse it unmodified for the target and the comparator head |
| inventory | `results/round3/D0_inventory/hest_inventory.csv` | `TENX115`, patient 2, 3,886 spots under tissue. `TENX117`, patient 1, 1,830 spots. Both Xenium |

**Known values for anchoring.** The benchmark head's mean Pearson on SKCM per direction is 0.6763 and 0.6462 for `uni_v2`, and 0.7069 and 0.6109 for `hoptimus1` (`results/faithful/pca_ridge/<encoder>/SKCM/split<k>/results.json`). Which split tests which slide is in the task's splits files, which you read and record.

**Contamination.** Both slides are public 10x datasets from 2023 and are certainly in the models' training data as datasets. Memorised per-spot values are implausible, but download during a trial is possible, which is why section 6.4 blocks the network. The reports say plainly that the slides are public.

---

## 4. Standing rules and conventions

- Silent failure is the main risk. Verify each stage's output against an expected value before moving on.
- Never assert a number you have not read back from a file. Cite the path.
- Read the whole grid before writing a headline. Before a summary sentence goes into a report, tabulate the quantity over every axis the experiment varied, which here are arm, size, model and replicate, and check that the sentence holds in each cell it claims.
- Before naming the cause of a difference, list in writing every variable that differs between its arms.
- Write predictions down before running, and report them beside the outcomes.
- Longleaf is where work runs. Nothing runs on Nicolas's Mac unless he asks for that specific task in chat. Such a request is written into the plan as a numbered extension before the task runs.
- A job that has waited four hours is reported to Nicolas in chat with what it needs, and it keeps waiting. A pending job may be switched between `rc_htzhu_pi` and `rc_tengfei_pi`.
- Every output directory gets `PROVENANCE.txt` (job id, partition, node, date, the code commit, command line, `PYTHONHASHSEED`, md5 of every script that ran, and for trials the Claude Code version and the served model ID) and is stamped with `stamp_dir()` from the `longleaf-provenance` skill, written by the job on the node. Before reusing or rebuilding any output you did not create, run `whose()` on it. If the verdict is `sibling` or `unstamped`, ask the oversight chat.
- Seeds from `zlib.crc32` of a written key, never `hash()`. Explicit `pa.schema` on every parquet.
- Commit messages through a file. Sub-agents run no git command. You are the only committer and check every hand-back against its primary tables before commit.
- Do not edit `CLAUDE.md`, `README.md`, `docs/README.md`, `docs/WAYS_OF_WORKING.md`, `docs/round06/README.md`, the masterplan or any earlier round's files. Proposed edits go in the report.
- Run `code/scripts/verify_numeric_claims.py` over `docs/round06/**/round06_cheatsheet_*.md` before every handover, in the form `docs/WAYS_OF_WORKING.md` gives for the layout by round, with your exceptions in `.verify-exceptions-cheatsheet`.
- After opening a pull request, confirm on GitHub that it exists and put its number in the report.

**Your own sub-agents.** You may use your session's sub-agent tool for building, checking and analysis. A trial is never run through that tool, because a sub-agent shares your files and context. Every trial is a separate headless Claude Code process started by the harness (section 6).

---

## 5. Working copies, code delivery and where to write

**Your session** runs in a clone at `/work/users/w/e/weiyang/hest_code/round6-cheatsheet/`, which Nicolas clones before starting you (section 11). Confirm it is on `main` at the starting commit with a clean tree, then create branch `round6-cheatsheet` there. Record the starting commit's hash in the plan. The clone is yours alone. The project tree is not a working copy for you.

**Jobs** run from a read-only snapshot of a committed state (`git archive` of the commit into the job's output directory), never from inside the clone, and record that commit. This replaces round 5's bundle route, since you work on Longleaf directly.

**Trial directories** live under `/work/users/w/e/weiyang/agent_trials/r6/`, outside the repository and the project tree, one directory per trial. A trial's directory and its ID are an opaque random string of eight hexadecimal characters, so the path tells the agent nothing about its arm, size, role or model. The manifest holds the meaning of each ID. Confirm in C0 that no `CLAUDE.md` exists in any parent of that path.

**Your areas.** Scripts `code/scripts/round6_cheatsheet_*.py`. Results `results/round6/cheatsheet/<STAGE>/`. Documents:

| file | role |
|---|---|
| `docs/round06/tracks/cheatsheet/round06_cheatsheet_plan.md` | your operating plan, living |
| `docs/round06/i01/cheatsheet/round06_cheatsheet_C1_report.md` | report at the C1 gate |
| `docs/round06/i02/cheatsheet/round06_cheatsheet_final_report.md` | report at the C3 gate, end of track |

What is committed. Every trial's manifest row, every cheatsheet (`results/round6/cheatsheet/<STAGE>/cheatsheets/<trial_id>.txt`), every prediction file as one parquet per stage, every score and every comparator table. Transcripts stay on Longleaf under the trial directories, compressed, with their md5s committed in `results/round6/cheatsheet/<STAGE>/transcripts_md5.csv`, because they may contain credentials in environment output and are large.

**Pull requests and tags.** At each gate you commit, tag and push your branch, open a pull request into `main`, and stop. Tags `round6-cheatsheet-C1` and `round6-cheatsheet-final`. You never merge. Nicolas merges with a merge commit after the oversight chat accepts the report. Branches are never rebased, squashed, amended after a push or force-pushed. A rejected gate is fixed with new commits on the same open pull request.

---

## 6. The trial design, fixed

Everything in this section is fixed before any trial runs, because the result depends on it. Changing a prompt, an input or a flag after a trial has run is not yours to decide (section 10), with the single exception named in 6.3.

### 6.1 Data, blocks and scored spots

- Slide S1 is `TENX115` and slide S2 is `TENX117`. The 50 genes are `bench_data/SKCM/var_50genes.json`. The target is what the round-1 faithful pipeline computes for these genes, read through its own loading code. Record the transform in the plan.
- S1's tissue bounding box is cut into a 4 by 4 grid. Blocks $(i, j)$ with $i + j$ odd are held out and the rest are training blocks. Spots within 165 µm of a held-out block's edge (three spot spacings of 55 µm, more than one patch width of 112 µm) are excluded from the scored set, so no scored patch shares pixels with a training patch. If either half holds under 35% of S1's spots, record it as an escalation and keep the split.
- S1* is 500 spots drawn uniformly without replacement from the eligible held-out spots, with seed `crc32("round6-S1star")`. S2* is 500 spots from S2 with seed `crc32("round6-S2star")`.
- Patches are HEST-bench's own 224 by 224 patches at 0.5 µm per pixel, written as PNG. Predictors see them under new IDs, a random permutation of `p0001` onward per trial, drawn with a seed keyed on the trial ID. The harness keeps the mapping outside the trial directory.
- Nothing in a trial directory or its path names the sample, the dataset, the patient or HEST. Writers' spots are renamed `s0001` onward in a random order drawn with a seed keyed on the trial ID, kept outside the trial directory like the predictors' mapping.

### 6.2 Trial directories

| session | files in its directory |
|---|---|
| writer | `patches/<sid>.png` and `spots.csv` (spot ID, x and y in pixels) for its labelled spots, `expression.csv` (spot ID and the 50 genes), `overview.png` (the slide at about 1,500 pixels on its long side, with the held-out blocks filled with white for an arm B writer) |
| predictor and baseline | `patches/<pid>.png` for the 500 scored spots, `genes.txt`, and `cheatsheet.txt` unless baseline |
| combined | `labelled/` laid out as a writer's directory, and `target/patches/<pid>.png` with `genes.txt` |

A writer for arms A and C has all of S1's spots. A writer for arm B has the training-block spots only, and its overview shows the training blocks only, so it cannot describe the held-out region or give a predictor anything to match its patches against. The combined session's `labelled/` follows the same rule for its arm, and its `target/` holds S1* (arms A and B) or S2* (arm C).

### 6.3 The prompts, verbatim

`{B}` is replaced by the size in bytes, written with digits only. The phrase "as log(1 + count)" is the one exception to the fixing rule. If C0 finds that the target is not the natural log of one plus the count, replace that phrase in all three prompts with an exact description of the target before any trial runs, and record the change.

**Writer.**

> You are working in a directory that holds measurements from one tissue section of human skin melanoma, profiled by spatial transcriptomics (10x Xenium, aggregated to spots). `patches/` holds one H&E image per spot, 224 by 224 pixels at 0.5 micrometres per pixel, named by spot ID. `spots.csv` gives each spot's position in pixels. `expression.csv` gives each spot's expression of 50 genes, as log(1 + count). `overview.png` is a low-resolution image of the whole section.
>
> Later, a different agent will predict the expression of the same 50 genes from H&E patches of this kind of tissue. That agent will see only the patch images, under new IDs and without positions, and one text file written by you. It will not see these measurements.
>
> Write that file as `cheatsheet.txt` in this directory. It may contain anything that you think will help the other agent predict accurately. It must be at most {B} bytes in UTF-8. Anything beyond {B} bytes will be cut off. You may use the tools available to you, including Python, to study the data. When the file is written, stop.

**Predictor.** For a baseline, the second paragraph is left out.

> You are working in a directory that holds H&E images from a tissue section of human skin melanoma that was profiled by spatial transcriptomics (10x Xenium, aggregated to spots). `patches/` holds one H&E image per spot, 224 by 224 pixels at 0.5 micrometres per pixel, named by spot ID. `genes.txt` lists 50 genes.
>
> `cheatsheet.txt` was written by someone who had measured the expression of these genes in tissue of this kind. Use it as a reference to help you make your predictions.
>
> Predict the expression of each of the 50 genes at every spot, as log(1 + count). Write `predictions.csv` with one row per spot, a column `spot_id` followed by one column per gene, named as in `genes.txt`. Every spot and every gene must have a number. You may use the tools available to you, including Python. When the file is written, stop.

**Combined session** ($b = \infty$).

> You are working in a directory with two folders from spatial transcriptomics of human skin melanoma (10x Xenium, aggregated to spots). In `labelled/`, `patches/` holds one H&E image per spot, 224 by 224 pixels at 0.5 micrometres per pixel, named by spot ID, `spots.csv` gives each spot's position in pixels, `expression.csv` gives each spot's expression of 50 genes, as log(1 + count), and `overview.png` is a low-resolution image of the whole section those spots come from. In `target/`, `patches/` holds H&E images of the spots whose expression you are to predict, with no measurements, and `genes.txt` lists the 50 genes.
>
> Predict the expression of each of the 50 genes at every spot in `target/patches/`, as log(1 + count). Write `predictions.csv` in this directory with one row per target spot, a column `spot_id` followed by one column per gene, named as in `target/genes.txt`. Every spot and every gene must have a number. You may use the tools available to you, including Python. When the file is written, stop.

### 6.4 How a trial runs

Each trial is one headless Claude Code process, started by the harness inside a Slurm job, in its own trial directory. The starting point, from the Claude Code documentation as read on 11 October, is below. Each flag is `[verify]` until C0.1 confirms it on Longleaf.

```
env -u ANTHROPIC_API_KEY CLAUDE_CODE_EFFORT_LEVEL=high \
  claude --safe-mode -p "$PROMPT" \
    --session-id "$UUID" --model "$MODEL" --effort high \
    --tools "Bash,Read,Write,Edit,Glob,Grep" \
    --disallowedTools "WebFetch" "WebSearch" "Agent" \
    --allowedTools "Read" "Write" "Edit" "Glob" "Grep" "Bash" \
    --permission-mode dontAsk \
    --max-turns 80 \
    --output-format stream-json --verbose
```

- `$MODEL` is `claude-haiku-5-5`, `claude-sonnet-5-5` or `claude-opus-5-5`. If a full ID is refused, use the alias `haiku`, `sonnet` or `opus`. Record the served model ID from the stream's `system/init` event for every trial.
- `--safe-mode` keeps out `CLAUDE.md`, skills, plugins, hooks, MCP servers and memory while keeping subscription login. `--bare` would also do this but cannot use a subscription token.
- The Bash sandbox of Claude Code does not cover the Read tool, so it cannot give the file confinement of 6.5 on its own. Candidate mechanisms for 6.5 are an Apptainer container that binds only the trial directory and a read-only Python environment, and the Anthropic sandbox runtime (`@anthropic-ai/sandbox-runtime`), which wraps the whole process and allows named hosts. You choose the mechanism and record it.
- Inside the confinement the agent has Python 3 with numpy, pandas, scipy, Pillow, scikit-image and scikit-learn, and no pretrained model weights of any kind. Record the versions.
- Authentication is by `CLAUDE_CODE_OAUTH_TOKEN` for a subscription, or by `ANTHROPIC_API_KEY` if Nicolas chooses that (open question R6-1 in the masterplan). The token is passed in the environment and never written to a trial directory or a committed file.
- At most two trials run at once unless Nicolas says otherwise. The harness keeps a manifest with a status per trial, so a stop at a usage limit resumes where it stopped.
- A writer's file is measured in UTF-8 bytes. If it exceeds $b$, the harness keeps the first $b$ bytes, cutting at the last whole character, and records both sizes. The writer is not asked again.
- A trial that ends without a valid output file (missing, unreadable, missing spots or genes, non-numeric values) is run once more as a new session with a new ID. If the second also fails, it is recorded as failed and the report counts it. A missing gene or spot is never filled in.
- Every trial records in the manifest its ID, arm, size, model, replicate, role, the writer it depends on, session ID, status, bytes written and kept, input and output tokens with cache reads and writes, estimated cost, turns, wall time, Claude Code version and served model.

### 6.5 Isolation, the properties every trial must have

| # | property | how C0.2 tests it |
|---|---|---|
| I1 | No project context. The session's context holds the prompt and Claude Code's own system prompt, and nothing from this repository, the user's settings, memory, skills or MCP servers | the `system/init` event lists only the six tools and no MCP servers or plugins, and a probe session asked to quote every instruction it has received beyond the prompt quotes nothing from the project |
| I2 | File confinement. The session cannot read or list any file outside its trial directory, through any tool | an adversarial probe session told to read canary files at given absolute paths, one in the project tree, one in your clone, one in the home directory and one in another trial directory, fails on all four, with Read, Glob, Grep and Bash each tried |
| I3 | No network except the Anthropic API | an adversarial probe told to fetch `https://huggingface.co` and `https://www.10xgenomics.com` with Bash, curl and Python fails |
| I4 | Blinding | a script finds no sample ID, patient label, dataset title, oncotree code or HEST file name in any trial file or path |

Run the I2 and I3 probes on Opus, the most capable model. After every stage, a script scans every transcript for the canary strings, the sample IDs, any URL other than the API's, any absolute path outside the trial directory, and the authentication token. Any hit excludes that trial, which is rerun, and is reported.

### 6.6 Scoring and comparators

- The scorer reads `predictions.csv`, maps the predictor's IDs back to spots outside the trial directory, and computes $\bar r$ of the masterplan's metric section over the 500 scored spots, with a constant gene counted as $0$ and flagged. It writes per-gene correlations too.
- The comparators are those of the masterplan's "Comparators" list, computed in C0.4. The benchmark head is the round-1 faithful head with its configuration from `results/faithful/pca_ridge/<encoder>/SKCM/split<k>/config.json`, on `uni_v2` and `hoptimus1`, fitted on the spots each arm's writer saw and scored on S1* or S2*. The codebook uses `uni_v2`, k-means with $k = \min(\lfloor b/50 \rfloor, n)$ for $n$ writer spots, which is $81$, $655$ and $n$ at the three finite sizes, fitted on the writer's spots with seed `crc32("round6-codebook")`, cluster means quantised to one byte per gene over each gene's range in the writer's spots, and nearest-centroid assignment for scored spots.

---

## 7. The plan

Four stages. Gates at C1 and C3.

### Interval 1

#### C0. Setup (two days, capped at three)

**C0.1 Claude Code on Longleaf.** Install Claude Code in Nicolas's user space if it is not there, record its version, and confirm `claude auth status` with the method Nicolas chose. On a compute node, confirm that the API is reachable and that each model ID answers a one-line prompt at `--effort high`. Confirm each flag of 6.4, and record any that differs from the documentation with what you used instead.

**C0.2 Isolation.** Build the confinement of 6.4 and run the probes of 6.5. Write the canary files with a unique random string each, and remove them only after C0.2 passes.

**C0.3 Data and trial inputs.** Build S1, S2, the blocks, S1*, S2* and the target, and write a builder that makes every trial directory of 6.2 from a trial's manifest row. Record the spot counts actually used, each half's share of S1 and the md5 of every input file.

**C0.4 Comparators.** Compute every comparator on S1* and S2*. As the anchor, the benchmark head fitted on one slide and scored on all spots of the other must reproduce the round-1 value of that direction within 0.01, for both encoders and both directions.

**C0.5 Harness and scorer.** Write the runner, the manifest, the scorer and the transcript scanner. Test the scorer. True values score exactly 1. Values permuted across spots score near 0, within $\pm 0.05$ on average over 20 permutations. A file with one constant gene scores that gene $0$ and flags it. A file missing a spot fails validation.

Exit items for C0, each with its evidence in the C1 report.
1. Every flag and model ID confirmed or replaced, with the served model IDs.
2. I1 to I4 pass, with the probe transcripts' md5s and the scanner's output.
3. The comparator anchor passes in all four cells.
4. The scorer tests pass.

#### C1. Pilot (one day; gate)

For each model, run four trials in this order. One baseline predictor on S1* (replicate 1). One arm B writer at 32,768 bytes (replicate 1). The predictor that uses its cheatsheet, on S1*. One arm B combined session (replicate 1). These are grid trials. They keep their IDs and count towards the grid if the C1 memo accepts the harness unchanged.

The C1 report, in the format of section 9, also carries these items.
1. The twelve trials' scores beside the comparators on S1*, with the cheatsheets' sizes and a one-paragraph description of what each cheatsheet contains.
2. Per model and role, the measured tokens, estimated cost, turns and wall time, and failures with their causes.
3. A projection of the full grid's tokens, cost and wall time per model and in total, from those measurements, with the rate the usage limits allowed.
4. The proposed i02 grid. The masterplan's grid if it fits what Nicolas has said about budget, and otherwise the masterplan's cut order taken as far as needed, with the cost of each cut.
5. Every prediction of section 8 that C1 can score.

Tag `round6-cheatsheet-C1`, open the pull request, and stop.

### Interval 2, opened by the C1 decision memo

#### C2. The grid

Every trial of the grid the C1 memo sets, writers before their predictors, with the scanner run after each batch. Arms A and C use the same writers.

#### C3. Analysis and the closing report (gate, end of track)

- For each arm and model, $\bar r$ against $b$ with both replicates and their mean, beside the comparators.
- $b^*(0.8)$ and $b^*$ at the `uni_v2` benchmark head's $\bar r$, the primary comparator, as brackets on the grid, with the `hoptimus1` head and the codebook reported beside it. Say in the text that the codebook's centroids are not counted in its bytes.
- The arm differences at each size, with the variables that differ between arms listed.
- What the cheatsheets contain. Tag each by script as holding prose, numbers keyed to visual features, per-cluster values, code or coefficients, or values keyed to individual patches (for example image fingerprints), and read a sample of each model's cheatsheets to check the tags. Report $\bar r$ by tag where the counts allow.
- Cost and tokens per model and role.

`docs/round06/i02/cheatsheet/round06_cheatsheet_final_report.md` in the format of section 9, with the full predictions-against-outcomes table, an "Escalations" section, and a closing page titled "What the cheatsheet experiment established", at most one page, every sentence naming its file. Run the numeric-claim sweep. Tag `round6-cheatsheet-final`, open the pull request, and stop.

---

## 8. Predictions for the track

The oversight chat's, from the masterplan, numbered for scoring. Copy them into the plan before running and score each as held, partly held, refuted or not tested.

- **C.1** At $b = 0$, Opus's $\bar r$ on S1* is between 0.05 and 0.35, and Haiku's is below Opus's.
- **C.2** In arm C no model reaches the `uni_v2` comparator's $\bar r$ on S2* at any finite size.
- **C.3** In arm C Opus's combined session is above its own 262,144-byte value and below the `uni_v2` comparator.
- **C.4** In arm A no model reaches $\bar r = 0.8$ at 32,768 bytes, and at least one model reaches it at 262,144 bytes.
- **C.5** In arm B, each model's $\bar r$ at 262,144 bytes is within 0.05 of its value at 32,768 bytes, and below its arm A value at 262,144 bytes.
- **C.6** Replicate means are ordered Opus, then Sonnet, then Haiku, in at least two thirds of the pairs of arm and finite size that are run.

Most of the project's magnitude predictions in earlier rounds were refuted, so a refuted prediction is reported as plainly as a held one.

---

## 9. Reporting format

After each gate, in this order. 1. Stage and status. 2. What was run (scripts with md5s, commits, job ids, partitions, wall times, the Claude Code version, trial counts by status). 3. Acceptance checks with the actual numbers and file paths. 4. For every comparison, the list of variables that differ between its arms, written out. 5. Predictions against outcomes, as a table. 6. Results, numbers from files with paths, both replicates beside every mean, and paths in place of pasted tables over 20 rows. 7. Discrepancies, open questions and escalations. 8. What was not checked. 9. Proposed next step.

---

## 10. Decision boundaries

**You decide alone.** Your own sub-agents. The confinement mechanism, provided I1 to I4 pass. Job sizing and the order of trials within a stage. Replacing a flag the documentation names with its working equivalent, recorded. The exact target wording of 6.3's one exception.

**Record as an escalation and continue.** A spot count that differs from the inventory. A half of S1 under 35% of its spots. A trial that fails twice. A writer that exceeds its size, which is truncated as 6.4 says. A comparator anchor off by more than 0.01 in one cell when the others pass (investigate, say what you found). Any new property of the data. A usage limit that stops the harness for more than a day.

**Stop and report.** Any of I1 to I3 that no mechanism you can build satisfies. The API unreachable from compute nodes. A model ID that cannot be served by any name, or a model that refuses `--effort high`. The comparator anchor failing in more than one cell. Any sign that a trial saw expression it should not have.

**Never yours.** Contact with anyone outside the project, David included. Changing a prompt, an input layout, a size, a model or the effort level after the first trial has run. Any download of data. Running a trial through your own sub-agent tool. Any local run that Nicolas has not asked for in chat. Changes to `main`, to earlier rounds' files or to the project tree's checkout. Any claim of novelty.

---

## 11. Before starting, Nicolas does

1. Decides open question R6-1, subscription or API key, and makes the credential available on Longleaf (`claude setup-token` on a machine with a browser gives a long-lived token for `CLAUDE_CODE_OAUTH_TOKEN`).
2. Gives the clone on Longleaf a way to push to GitHub (a credential for `gh` or an SSH key), or tells the session to deliver commits another way.
3. Clones the repository to `/work/users/w/e/weiyang/hest_code/round6-cheatsheet/` (`git clone https://github.com/NicWYZ/HEST-1k-replication.git round6-cheatsheet` inside `hest_code/`), starts Claude Code there on a login node inside `tmux`, and pastes the line "Read docs/round06/i01/cheatsheet/round06_cheatsheet_track.md in full and follow it."
