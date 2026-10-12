# Round 6 extension, the cheatsheet track on held-out patients, instruction

12 October 2026. Prepared by the oversight chat for a fresh local Claude Code session on Nicolas's Mac, which reaches Longleaf over SSH. This document is self-contained. It is kept current on `main`. When Nicolas tells you to check for updates, fetch `main`, read the "Revisions" list below and the masterplan's amendments, and transcribe what changed into your plan.

**Revisions.**
- 12 October, 15:30. Longleaf is reached through Nicolas's existing `Host longleaf` alias and SSH key, and a shared connection is needed only if Duo prompts (5, 11). Section 11 says why the trials need their own token.
- 12 October, before handover. An independent check found eleven problems, all fixed in place. The container mounts and the Mac-specific parts of the confinement (6.5), patient labels `P1` to `P7` and a mechanical check that no longer flags class letters or gene lists (6.1, 6.4), the mechanics of the audit loop (6.4), rubric clarifications with examples (6.4), `virchow2` as the second encoder (3, 6.7), the anchor's inputs (C4.4), the seeds and the sampling rule (6.1), and three gaps in the metric (6.7).

The track starts from `main` of `NicWYZ/HEST-1k-replication` at the commit that carries this document. Read this document fully, then transcribe sections 6 and 7 into `docs/round06/tracks/cheatsheet/round06_cheatsheet_ext_plan.md` before running anything. The round's plan is `docs/round06/masterplan.md`, whose section "Extension" covers this work. Round 6's first three intervals are closed and their files are history for you, not instructions.

---

## 1. Your role and the people

You are the execution agent. A separate chat session, the oversight chat, reviews your reports, makes scope decisions and writes decision memos, which Nicolas hands to you. Nicolas Weiyang Zhang (Longleaf ONYEN `weiyang`, Slurm accounts `rc_htzhu_pi` and `rc_tengfei_pi`) is the first-year biostatistics PhD student whose project this is. He reads every command before it runs and will ask why. His advisors are Dr. Hongtu Zhu and Dr. Daiwei (David) Zhang at UNC. David proposed the original experiment.

If the repository's `CLAUDE.md` is in your context, it belongs to the oversight chat. Do not edit it and do not act on its plan. Its section 7 rules apply to you. Rule 7 records Nicolas's decision of 12 October for this track, that the agent trials and the analysis run on his Mac while the data preparation and the comparators run on Longleaf.

Your responsibilities are to prepare the data on Longleaf, build the trial harness on the Mac, run the trials, verify every stage's output against an expected value before moving on, write reports in the format of section 9, commit and push at each gate, and stop. You do not make scope decisions. Anything this document does not cover is reported as a proposal, not done.

**The gate rule, in the wording Nicolas approved.** Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. Contact with anyone outside the project is never the session's decision.

This track's gates are C5 and C7.

**How Nicolas wants things written.** Plain, natural prose. No em-dashes. No colon-then-explanation constructions. No compressed or clever phrasing. Math as LaTeX, with each `$$` on a line of its own. Numbers quoted at the precision the comparison needs, with the relative scale stated. Full precision stays in the files. Every number in a report is read back from the file named beside it. Do not inflate length.

---

## 2. What this track is for

Round 6 ran David's cheatsheet experiment on two melanoma slides. On the second patient, a 4,096-byte cheatsheet lifted Opus 5.5 from 0.345 to 0.647 mean Pearson, and larger cheatsheets added little. Large cheatsheets turned into training tables and feature-extraction code, so at those sizes the predictor ran a small hand-built image model rather than reading text (`docs/round06/i03/cheatsheet/round06_cheatsheet_final_decisions.md`, section 2).

This extension asks a narrower question with more data. How much of the relation between tissue appearance and expression can be passed on as text that is biological and transferable, and how does prediction on unseen patients grow with the size of that text? Every cheatsheet must follow a rubric that allows descriptions of tissue and expression and forbids code, model recipes, computed image measurements and anything keyed to a training spot or patient (section 6.4). A separate checker agent audits each cheatsheet, and violations go back to the writer for revision. Writers learn from 7 patients and predictors are scored on 3 others, which is round 6's arm C only.

What is not claimed. This track builds no method for the paper and makes no claim of novelty in any document. It measures and reports.

---

## 3. Data and assets

**The task.** HEST-bench `CCRCC`, clear cell renal cell carcinoma, 10x Visium, 24 slides from 24 patients (`results/round3/D0_inventory/hest_inventory.csv`). It is the only HEST-bench task with at least 10 slides from different patients. Its 24 slides are 12 frozen sections (`INT1` to `INT12`, subseries `ccRCC tumor frozen_*`) and 12 FFPE sections (`INT13` to `INT24`, subseries `ccRCC tumor ffpe_*`). Freezing and paraffin embedding change how H&E looks, so this track uses the FFPE slides only. The FFPE slides have 3,206 to 4,975 spots under tissue. Round 3 flagged `INT4` and `INT24` as possibly one donor, and `INT4` is frozen, so the FFPE set has no such pair. Confirm the preservation of all 12 from the inventory's `subseries` column and from the HEST metadata on Longleaf, and record both.

**On Longleaf.** The project tree `/work/users/w/e/weiyang/hest_replication` is on `main` at tag `round4-data-v2`. Its checkout is never changed. Nothing heavy runs on a login node. The project's Python is `/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python`, called by absolute path.

| asset on Longleaf | path in the project tree | what the package takes from it |
|---|---|---|
| benchmark data | `bench_data/CCRCC/` (`adata/*.h5ad`, the patches, the splits, `var_50genes.json`) | the 10 slides' spots, positions, patches, the 50 genes and the target, through the round-1 pipeline's own loading code |
| embeddings | `embeddings/CCRCC/<encoder>/<sample>.h5` | `uni_v2` and `virchow2` embeddings for every spot of the 10 slides |

| asset in the repository | path | what it gives you |
|---|---|---|
| round-1 faithful runs | `results/faithful/pca_ridge/<encoder>/CCRCC/split0/` to `split5/` (`config.json`, `results.json`) | the benchmark head's configuration and its per-split Pearson, the anchor of C4.4 |
| the round-1 pipeline | `code/scripts/`, the faithful HEST-bench harness of round 1 | how the target is computed, reused unmodified |
| round 6's harness | `code/scripts/round6_cheatsheet_*.py`, `docs/round06/tracks/cheatsheet/round06_cheatsheet_plan.md` | the confinement, filtering proxy, runner, scanner and scorer that passed I1 to I4 in round 6, to adapt rather than rewrite |

`uni_v2` is the primary comparator, as in round 6. `virchow2` is the best encoder on CCRCC in round 1, at 0.2719 mean Pearson against 0.264 for `uni_v2` (`results/summary/discrepancy_table.csv`), so it is the second comparator. Both values are means over 6 folds whose test sets mix frozen and FFPE slides and pool spots across patients, so neither is a target for this track. They serve only as the anchor.

**Contamination.** The CCRCC slides are from a 2022 study (Meylan et al., PMID 35231421) and may be in the models' training data as a dataset. Download during a trial is blocked by section 6.6.

---

## 4. Standing rules and conventions

- Silent failure is the main risk. Verify each stage's output against an expected value before moving on.
- Never assert a number you have not read back from a file. Cite the path.
- Read the whole grid before writing a headline. Tabulate the quantity over every axis the experiment varied, which here are size, test slide and gene, and check that each summary sentence holds in each cell it claims.
- Before naming the cause of a difference, list in writing every variable that differs between its arms.
- Write predictions down before running, and report them beside the outcomes.
- Data preparation and comparators run on Longleaf through Slurm. Trials and analysis run on Nicolas's Mac, by his decision of 12 October. Before anything runs locally, record in the plan what runs and why.
- Every Longleaf output directory gets `PROVENANCE.txt` (job id, partition, node, date, the code commit, command line, md5 of every script) and the stamp of the `longleaf-provenance` skill if you have it, or the same fields if you do not. Every local output directory gets `PROVENANCE.txt` with the machine, the date, the code commit, the command line, `PYTHONHASHSEED`, the md5 of every script and of the data package, and for trials the Claude Code version and the served model ID.
- Seeds from `zlib.crc32` of a written key, never `hash()`. Explicit `pa.schema` on every parquet.
- Commit messages through a file. Sub-agents run no git command. You are the only committer.
- Do not edit `CLAUDE.md`, `README.md`, `docs/README.md`, `docs/WAYS_OF_WORKING.md`, `docs/round06/README.md`, the masterplan, round 6's earlier files or any earlier round's files. Proposed edits go in the report.
- Run `code/scripts/verify_numeric_claims.py` over `docs/round06/**/round06_cheatsheet_ext_*.md` and your gate reports before every handover, in the form `docs/WAYS_OF_WORKING.md` gives, with your exceptions in `.verify-exceptions-cheatsheet-ext`.
- After opening a pull request, confirm on GitHub that it exists and put its number in the report.

**Your own sub-agents.** You may use your session's sub-agent tool for building, checking and analysis. A trial, a writer revision or a checker audit is never run through that tool, because a sub-agent shares your files and context. Every one is a separate headless Claude Code process started by the harness inside its own confinement (section 6.5).

---

## 5. Machines, working copies, code delivery and where to write

**Your clone** is a new clone at `~/hest-1k/HEST-1k-replication-cheatsheet` on the Mac. The other clones under `~/hest-1k` belong to other sessions and are read only, with `git --no-optional-locks`. Confirm your clone is on `main` at the starting commit with a clean tree, then create branch `round6-cheatsheet-ext`. Record the starting commit's hash in the plan.

**Longleaf.** You reach Longleaf with `ssh longleaf`, the host alias in Nicolas's `~/.ssh/config`, which logs in as `weiyang` with his key. If a command asks for a password or a Duo prompt, stop and ask him to reopen the connection. Your code clone on Longleaf is `/work/users/w/e/weiyang/hest_code/HEST-1k-replication-cheatsheet`. Commits reach it as git bundles you copy over with `scp`, as hard rule 5 says, and every job copies its commit with `git archive` into its output directory and runs from that copy. Slurm jobs use `rc_htzhu_pi` unless the queue says otherwise. On a login node you run only `git`, `sbatch`, `squeue`, `sacct`, `scp`, `rsync` and light file inspection.

**The data package** is built on Longleaf by one job (C4.3) and lands under `results/round6/cheatsheet_ext/C4_package/` in the project tree on Longleaf. You copy it with `rsync` over SSH to `~/hest-1k/r6ext_private/package/` on the Mac and check every md5 against its manifest. `~/hest-1k/r6ext_private/` holds the package, the ground truth and the ID mappings, and no trial can see it.

**Why the package never enters the public repository.** `NicWYZ/HEST-1k-replication` is public. Pushing the package there would republish HEST data, which is under a non-commercial share-alike licence, and transcripts can contain credentials. Nothing from the package and no transcript goes into it. Transcripts go to the private repository `NicWYZ/hest-r6-data` under `transcripts/ext/<STAGE>/`, compressed, in files of at most 95 MB, pushed at each gate.

**Trial directories** live under `~/hest-1k/r6ext_trials/`, one per trial, named by an opaque random string of eight hexadecimal characters. The manifest holds the meaning of each ID.

**Your areas.** Scripts `code/scripts/round6_cheatsheet_ext_*.py` and `*.sh`. Results `results/round6/cheatsheet_ext/<STAGE>/`. Documents:

| file | role |
|---|---|
| `docs/round06/tracks/cheatsheet/round06_cheatsheet_ext_plan.md` | your operating plan, living |
| `docs/round06/i04/cheatsheet/round06_cheatsheet_C5_report.md` | report at the C5 gate |
| `docs/round06/i05/cheatsheet/round06_cheatsheet_C7_report.md` | report at the C7 gate, end of track |

What is committed. Every trial's manifest row, every cheatsheet version with its checker verdicts (`results/round6/cheatsheet_ext/<STAGE>/cheatsheets/<trial_id>_v<k>.txt` and `verdicts/<audit_id>.json`), every prediction file as one parquet per stage, every score and every comparator table. No patch, expression value or embedding from the package is committed. The confinement's scripts, including the filtering proxy and its start script, are committed in interval i04 (closing memo of round 6, section 3).

**Pull requests and tags.** At each gate you commit, tag and push your branch, push the stage's transcripts to `NicWYZ/hest-r6-data`, open a pull request into `main` with `gh` or ask Nicolas to open it, and stop. Tags `round6-cheatsheet-C5` and `round6-cheatsheet-C7`. You never merge. Nicolas merges with a merge commit after the oversight chat accepts the report. Branches are never rebased, squashed, amended after a push or force-pushed. A rejected gate is fixed with new commits on the same open pull request.

---

## 6. The trial design, fixed

Everything in this section is fixed before any trial runs. Changing a prompt, an input, the rubric or a flag after the first C6 trial has run is not yours to decide (section 10), with the one exception named in 6.3.

### 6.1 Slides, samples and the split

- **Random numbers.** Every draw uses `numpy.random.default_rng(seed)` with the seed given, and any list it draws from is sorted first by the number after `INT` for sample IDs, or by the existing ID for spots. Seeds keyed on a trial use `crc32("round6ext-<purpose>-<trial_id>")`, where `<purpose>` names the draw (for example `spotorder` or `patientorder`).
- **Slides.** From the 12 FFPE slides, draw 10 without replacement with seed `crc32("round6ext-slides")`. Of those, draw 3 test slides with seed `crc32("round6ext-split")`. The other 7 are training slides. Record both draws in the plan before building anything.
- **Spots.** Only spots with a HEST-bench patch are used. From each of the 10 slides take a fixed sample of 500 spots, stratified by expression. Cluster all of the slide's patched spots by k-means with $k = 8$ on the standardised 50-gene target, seed `crc32("round6ext-strata-<sample_id>")`. Give each cluster with at least 2% of the slide's spots a floor of 10 spots. Allocate the rest of the 500 over all clusters, including those under 2%, in proportion to the spots each has beyond its floor, by largest remainder. Draw within each cluster with seed `crc32("round6ext-sample-<sample_id>")`.
- **Representativeness.** For each slide and gene, with $\bar y$ and $\sigma$ the mean and standard deviation over all of the slide's patched spots and $\bar y_{\text{sample}}$ and $\sigma_{\text{sample}}$ the same over the 500, the sample must satisfy $|\bar y_{\text{sample}} - \bar y| \le 0.1\,\sigma$ and $0.9 \le \sigma_{\text{sample}}/\sigma \le 1.1$. Record every value. A slide that fails on more than 5 of its 50 genes is an escalation, and its sample is kept.
- **Sizes.** Writers get $7 \times 500 = 3{,}500$ labelled spots. Predictors are scored on $3 \times 500 = 1{,}500$ spots.
- **Patches.** HEST-bench's own 224 by 224 patches at 0.5 µm per pixel, written as PNG. Confirm the pixel size from the patch files' attributes as round 6 did, and confirm that the stored coordinates are in the same frame as the images (round 6 found them transposed, plan flag F16).
- **The target** is what the round-1 faithful pipeline computes for the 50 genes in `bench_data/CCRCC/var_50genes.json`, read through its own loading code. Record the transform in the plan.
- **Blinding.** Nothing in a trial directory or its path names a sample, dataset, patient, study or HEST. Writers' training patients get labels `P1` to `P7` in a random order per trial, and their spots get IDs `s0001` onward in a random order per trial. Predictors' test patients get folders `a`, `b` and `c` in a random order per trial, and their patches IDs `p0001` onward. All orders are drawn with seeds keyed on the trial ID and kept outside the trial directory.

### 6.2 Trial directories

| session | files in its directory |
|---|---|
| writer | `patches/<sid>.png` for its 3,500 spots, `spots.csv` (spot ID, patient label, x and y in pixels), `expression.csv` (spot ID and the 50 genes), `overviews/<label>.png` (a mosaic of all of that patient's patched spots at their positions, about 1,500 pixels on its long side), `RULES.md` (6.4), `check_cheatsheet.py` (6.4) and `genes.txt` |
| checker | `cheatsheet.txt`, `RULES.md` and `genes.txt` only |
| predictor and baseline | `patches/a/`, `patches/b/` and `patches/c/` holding `<pid>.png` for the 1,500 scored spots, `genes.txt`, and `cheatsheet.txt` unless baseline |
| combined | `labelled/` laid out as a writer's directory without `RULES.md` and `check_cheatsheet.py`, and `target/` laid out as a predictor's directory without `cheatsheet.txt` |

A writer revision runs in the writer's own directory, resuming the writer's session.

### 6.3 The prompts, verbatim

`{B}` is replaced by the size in bytes, written with digits only. The phrase "as log(1 + count)" is the one exception to the fixing rule. If C4 finds that the target is not the natural log of one plus the count, replace that phrase in every prompt with an exact description of the target before any trial runs, and record the change.

**Writer.**

> You are working in a directory that holds measurements from tissue sections of human clear cell renal cell carcinoma from seven patients, profiled by spatial transcriptomics (10x Visium, spots 55 micrometres across). `patches/` holds one H&E image per spot, 224 by 224 pixels at 0.5 micrometres per pixel, centred on the spot and named by spot ID. `spots.csv` gives each spot's patient, as a label from P1 to P7, and its position in pixels on that patient's section. `expression.csv` gives each spot's expression of 50 genes, as log(1 + count). The spots of each patient are a sample of 500 from that section. `overviews/` holds a low-resolution image of each patient's section.
>
> Later, a different agent will predict the expression of the same 50 genes from H&E patches of this kind of tissue taken from other patients. That agent will see only the patch images and one text file written by you. It will not see these measurements or these patients.
>
> Write that file as `cheatsheet.txt` in this directory. It should pass on, in words and numbers, what this tissue looks like and how its appearance relates to the expression of these genes, in a form that will hold for new patients. It must follow the rules in `RULES.md`, and it must be at most {B} bytes in UTF-8. Anything beyond {B} bytes will be cut off. Use as much of the allowed size as helps; more detail is generally better. Look at patches from every patient. Before you finish, run `python3 check_cheatsheet.py`, which reports the size and possible problems, and fix those that break the rules. You may use the tools available to you, including Python, to study the data. There is no internet access, and no pretrained models or files other than those in this directory are available. When the file is written and the check passes, stop.

**Writer revision**, sent by resuming the writer's session. `{VIOLATIONS}` is the checker's list, one violation per line, as line numbers, rule and reason.

> An independent reviewer checked `cheatsheet.txt` against `RULES.md` and found the problems listed below. Revise `cheatsheet.txt` so that it follows every rule and stays within {B} bytes. Run `python3 check_cheatsheet.py` again before you finish, and fix what it reports that breaks the rules. When the revised file is written and the check passes, stop.
>
> {VIOLATIONS}

**Checker.**

> You are reviewing a text file, `cheatsheet.txt`, against the rules in `RULES.md`. `genes.txt` lists the 50 genes the file is about. Read both files in full. For every passage that breaks a rule, give its line numbers, the number of the rule it breaks, and one sentence saying why. Judge only whether the file follows the rules, not whether its content is correct or useful. Write `verdict.json` in this directory as a JSON object with a key `pass`, true or false, and a key `violations`, a list of objects with keys `lines`, `rule` and `reason`. The file passes only if the list is empty. When `verdict.json` is written, stop.

**Predictor.** For the baseline, the second paragraph is left out.

> You are working in a directory that holds H&E images from tissue sections of human clear cell renal cell carcinoma from three patients, profiled by spatial transcriptomics (10x Visium, spots 55 micrometres across). `patches/a/`, `patches/b/` and `patches/c/` each hold the patches of one patient, one H&E image per spot, 224 by 224 pixels at 0.5 micrometres per pixel, centred on the spot and named by spot ID. `genes.txt` lists 50 genes.
>
> `cheatsheet.txt` was written by someone who had measured the expression of these genes in this kind of tissue from other patients. Use it as a reference to help you make your predictions.
>
> Predict the expression of each of the 50 genes at every spot, as log(1 + count). Write `predictions.csv` with one row per spot, a column `spot_id` followed by one column per gene, named as in `genes.txt`. Every spot and every gene must have a number. You may use the tools available to you, including Python. There is no internet access, and no pretrained models or files other than those in this directory are available. When the file is written, stop.

**Combined session.**

> You are working in a directory with two folders from spatial transcriptomics of human clear cell renal cell carcinoma (10x Visium, spots 55 micrometres across). In `labelled/`, from seven patients, `patches/` holds one H&E image per spot, 224 by 224 pixels at 0.5 micrometres per pixel, centred on the spot and named by spot ID, `spots.csv` gives each spot's patient, as a label from P1 to P7, and its position in pixels on that patient's section, `expression.csv` gives each spot's expression of 50 genes, as log(1 + count), and `overviews/` holds a low-resolution image of each patient's section. In `target/`, from three other patients, `patches/a/`, `patches/b/` and `patches/c/` hold the H&E images of the spots whose expression you are to predict, one folder per patient, and `genes.txt` lists the 50 genes.
>
> Predict the expression of each of the 50 genes at every spot in `target/patches/`, as log(1 + count). Write `predictions.csv` in this directory with one row per target spot, a column `spot_id` followed by one column per gene, named as in `target/genes.txt`. Every spot and every gene must have a number. You may use the tools available to you, including Python. There is no internet access, and no pretrained models or files other than those in this directory are available. When the file is written, stop.

### 6.4 The rubric, `RULES.md` verbatim, and the mechanical check

The writer's and the checker's `RULES.md` is the quoted text between the two horizontal rules below, with the quote markers removed and nothing else changed.

---

> # Rules for `cheatsheet.txt`
>
> The file is for an agent that will look at H&E patches from patients you have not seen and predict the expression of the 50 genes. Everything in it must be something a pathologist could apply while looking at one patch from a new patient, without a computer. That is the test for every sentence.
>
> ## Allowed
>
> - **A1.** Tissue and cell types, structures and states, described in histological terms. For example, clear-cell tumour nests with a fine capillary network, eosinophilic or granular tumour cells, lymphoid aggregates, fibrous stroma, necrosis, haemorrhage, normal tubules or glomeruli.
> - **A2.** The expression of any of the 50 genes in each described class, in numbers (means, typical ranges, quantiles) or in words.
> - **A3.** How expression changes with something visible, such as the density of lymphocytes, the share of the patch that is stroma, or the presence of vessels, described so that it can be judged by eye.
> - **A4.** Groups of genes that rise and fall together, and the biology behind them.
> - **A5.** How patients differ, described by what their tissue looks like and without saying which patient. "In some patients the tumour cells are granular and eosinophilic, and there CA9 is lower" is allowed. "Patient P3 had granular cells" is not (F3).
> - **A6.** Cautions about appearance, such as staining that varies between sections, and what to look at instead.
> - **A7.** The overall level and spread of each gene across tissue of this kind.
>
> Estimates by eye are allowed, such as "about half of the patch is empty space". So are rules a person applies by eye, such as "decide which of these classes the patch looks most like, then use that class's values" or "if the patch is mostly stroma, expect COL1A1 to be high".
>
> ## Forbidden
>
> - **F1.** Code, pseudocode, formulas over pixel values, and instructions for fitting, training or running any model or algorithm on computed data (for example regression, nearest neighbours, clustering, or thresholds on computed features). Rules applied by eye, as above, are not covered by this rule.
> - **F2.** Image measurements that need a computer, such as mean colour values, pixel counts or fractions computed from pixels, texture or frequency statistics, or colour-space conversions.
> - **F3.** Anything keyed to an individual training spot, section or patient, including spot IDs, patient labels, positions, image fingerprints, or tables with one row per spot.
> - **F4.** Encoded, compressed or otherwise unreadable data.
> - **F5.** Advice about the scoring metric, or about transforming or rescaling predictions in order to score well. Typical levels and spreads of genes are A7 and are allowed.
> - **F6.** Technical properties used as predictors, such as file properties, image size, scanner, batch or section quality, unless described as visible tissue appearance.

---

`check_cheatsheet.py` sits in the writer's directory, with the size $b$ written into it, and reports each of these with line numbers. The harness runs the same checks after each version and records them.

1. The file is at most $b$ bytes in UTF-8.
2. No code fence (a line starting with three backticks) and no line that looks like code. Matching is case-sensitive, so prose that starts with a capital letter is never flagged. A line is flagged if, after leading spaces, it starts with `import `, `from ` followed by `import` later on the line, `def `, `class ` followed by a name and `(` or `:`, `return `, `print(` or `lambda`, or if it starts with lowercase `for ` or `while ` or `if ` and ends with `:`. Lines naming common code libraries followed by a dot (`np.`, `pd.`, `cv2.`, `skimage.`, `sklearn.`) are flagged too.
3. No token of the form of a training spot ID (`s` and four digits) and no patient label (`P1` to `P7` as a standalone token).
4. No unbroken run of 40 or more characters without a space, except a list of names from `genes.txt` joined by commas, slashes or hyphens.
5. No table with more than 64 data rows, where a table is a run of lines that each hold at least 5 numbers.

A mechanical flag is a warning to the writer and an input to the checker, not a verdict. The checker's verdict decides. The script's output says so in its first line.

**The audit loop.** After the writer stops, the harness first cuts the file to $b$ bytes if it is longer (6.5) and overwrites `cheatsheet.txt` in the writer's directory with the cut version. It then runs the mechanical checks, copies that version into a fresh checker directory and runs the checker. If the verdict fails, the harness resumes the writer's session in the writer's directory with the revision prompt and `--max-turns 60`. After the revision it cuts, overwrites, checks and audits again in the same way, with a fresh checker each time. There are at most two revisions. A cheatsheet that still fails after the second revision is used as it stands, flagged, and reported separately (Nicolas's decision of 12 October). If a resumed revision ends with no readable file or a session error, the previous version is kept, the attempt counts as one of the two revisions, and the manifest records it. Every version, every verdict and every mechanical report is kept. The predictor gets the last version.

### 6.5 How a trial runs

The trials need confinement with the properties of 6.6. On the Mac, the default route `[proposed]` is round 6's confinement unchanged, inside a Linux container. Run Docker Desktop, OrbStack or colima (whichever Nicolas has or installs, section 11), build one image with Debian, `bubblewrap`, `socat`, Node, Claude Code at a recorded version and Python 3 with numpy, pandas, scipy, Pillow, scikit-image and scikit-learn, and run the harness inside it. Mount three things into the container and nothing else. Your clone read-only at `/repo`, for the scripts. `~/hest-1k/r6ext_trials/` and `~/hest-1k/r6ext_private/`. A writable `~/hest-1k/r6ext_results/` for the harness's outputs, which you copy into your clone's `results/round6/cheatsheet_ext/` from outside the container. Each trial's `bwrap` binds only its own trial directory, so the clone, the private folder and the results folder stay outside every trial, and the I2 canaries in the clone and in the private folder test that. Inside it, each trial runs under the `bwrap` command of round 6's instruction, section 6.4 (`docs/round06/i01/cheatsheet/round06_cheatsheet_track.md`), with its own process, network and IPC namespaces, its trial directory as `/work`, and the filtering proxy reached through a Unix socket as its only route out. The filter forwards `CONNECT` to the Anthropic API host only. Round 6 committed the runner, the scanner and the filtering proxy (`code/scripts/round6_cheatsheet_filter_proxy.py`) but not the proxy's `start.sh`, so you rewrite that from the instruction's description. Three parts need changing for a container on a Mac, each `[verify]` until C4.2 passes.
- Round 6's filter forwards to an upstream proxy taken from `$HTTPS_PROXY`, which a container on the Mac does not have. Give it a mode that connects directly to the API host and still accepts `CONNECT` to that host only.
- `$CA_BUNDLE` was the cloud container's certificate bundle. Use the image's system bundle instead, or leave the proxy variables for certificates unset if the API's certificate verifies against the system store.
- `bwrap --unshare-all` inside Docker normally needs the container started with `--privileged`, or with `--security-opt seccomp=unconfined --security-opt apparmor=unconfined --cap-add SYS_ADMIN`. Use the narrower form if it works, and record which you used.

You may use another route if it gives the same properties, such as Claude Code's own sandbox on macOS. Whatever route you use, I1 to I4 decide.

- **Authentication.** Round 6's children authenticated through the cloud session's own credentials. Here, Nicolas creates a long-lived token for his account with `claude setup-token` and stores it in a file under `~/hest-1k/r6ext_private/` readable only by him, and the harness passes it to each child as `CLAUDE_CODE_OAUTH_TOKEN` `[verify]`. Confirm in C4.1 that a child authenticates this way and that usage is billed to his account. The token is visible to the agent through its environment, so the scanner searches every file for it before anything is committed or pushed (6.6).
- **The command.** As round 6's, with `--model claude-opus-5-5` (alias `opus` if the full ID is refused), `--effort medium` and `CLAUDE_CODE_EFFORT_LEVEL=medium`, `--safe-mode`, `env -i`, `--tools "Bash,Read,Write,Edit,Glob,Grep"`, `--disallowedTools "WebFetch" "WebSearch" "Agent"`, `--permission-mode dontAsk` and `--output-format stream-json --verbose`. Writers get `--max-turns 120` and every other role `--max-turns 80`. The checker gets `--tools "Read,Write,Glob"` only. A writer revision is started with `--resume <writer session ID>` in the writer's directory under the same confinement.
- **Concurrency.** Up to four trials at once. Measure memory in the first batch and drop to three if the container passes 75% of the memory it was given.
- **Size.** A writer's file is measured in UTF-8 bytes. If it exceeds $b$, the harness keeps the first $b$ bytes, cut at the last whole character, and records both sizes.
- **Failure.** A trial that ends without a valid output file (missing, unreadable, missing spots or genes, non-numeric values, or for a checker an unreadable verdict) is run once more as a new session with a new ID. If the second also fails, it is recorded as failed and the report counts it. A missing gene or spot is never filled in.
- **The manifest** records per session its ID, role, size, the writer it depends on, the version and audit number for writers and checkers, session ID, status, bytes written and kept, input and output tokens with cache reads and writes, estimated cost, turns, wall time, Claude Code version and served model.

### 6.6 Isolation, the properties every session must have

| # | property | how C4.2 tests it |
|---|---|---|
| I1 | No project context. The session's context holds the prompt and Claude Code's own system prompt, and nothing from this repository, Nicolas's settings, memory, skills or MCP servers | the `system/init` event lists only the allowed tools and no MCP servers or plugins, and a probe session asked to quote every instruction it has received beyond the prompt quotes nothing from the project |
| I2 | File confinement. The session cannot read or list any file outside its trial directory, through any tool | an adversarial probe told to read canary files at given absolute paths, one in your clone, one in `~/hest-1k/r6ext_private/`, one in Nicolas's home directory and one in another trial directory running at the same time, fails on all four, with Read, Glob, Grep and Bash each tried, and also through `/proc/*/root`, `/proc/*/cwd` and `/proc/*/environ` |
| I3 | No network except the Anthropic API | an adversarial probe told to fetch `https://huggingface.co`, `https://github.com` and `https://pypi.org` with Bash, curl and Python, with the proxy variables set and unset, and to open sockets to every localhost port it can find, fails on all of them |
| I4 | Blinding | a script finds no sample ID, patient label, dataset title, study name, oncotree code or HEST file name in any trial file or path |

Run the I2 and I3 probes on Opus 5.5 at medium effort. After every batch, a script scans every transcript for the canary strings, the sample IDs, any URL other than the API's, any absolute path outside the trial directory, a nested `claude` session, a direct API call, and the token. A session is excluded and rerun only for a canary string, a sample ID or other blinded name, the token's contents, a nested `claude` session or direct API call, or content that came back from a host other than the API. Listings of empty or absent directories and refused network attempts are recorded and reported, and do not exclude. Before anything is committed or pushed to either repository, every cheatsheet, verdict, prediction file and manifest is scanned for the token too.

### 6.7 Scoring and comparators

**The metric.** For test slide $s$ and gene $g$, $y_{sg}$ is the measured target over that slide's 500 scored spots and $\hat y_{sg}$ the predictions. The primary metric is the mean over the three test slides of the within-slide mean Pearson,

$$
\bar r = \frac{1}{3}\sum_{s=1}^{3} \frac{1}{50}\sum_{g=1}^{50} \operatorname{corr}\big(\hat y_{sg},\, y_{sg}\big),
$$

with a gene whose predictions are constant on a slide counted as $0$ there and flagged. A gene whose measured values are constant over a slide's 500 spots has no defined correlation there. It is left out of that slide's mean and flagged, and the same genes are left out for every predictor and comparator. Round 1 showed that a correlation pooled across patients is inflated by the differences between them (`docs/round01/README.md`), so the pooled value over all 1,500 spots is reported beside it and never as the headline. Per-slide values are reported too.

**The size needed.** Over the size grid $\mathcal{B}$ and a threshold $\tau$,

$$
b^*(\tau) = \min\{\, b \in \mathcal{B} : \bar r(b) \ge \tau \,\},
$$

reported as a bracket between adjacent grid sizes, or as not reached, for $\tau$ equal to the `uni_v2` head's $\bar r$ and to the `virchow2` head's.

**Comparators,** computed in C4.4 on Longleaf, scored with the same metric on the same 1,500 spots.

- The benchmark head (PCA to 256 components and ridge, with the round-1 faithful configuration from `results/faithful/pca_ridge/<encoder>/CCRCC/split0/config.json`) on `uni_v2` and `virchow2`, fitted on the 3,500 writer spots. The `uni_v2` head is the primary comparator.
- The same head fitted on every patched spot of the 7 training slides, to show what the 500-spot sample costs.
- A size-matched codebook on `uni_v2`. k-means on the 3,500 writer spots with $k = \min(\lfloor b/50 \rfloor, 3{,}500)$, which is 5, 10, 20, 40, 81, 163, 327, 655 and 1,310 at the nine sizes, seed `crc32("round6ext-codebook")`, cluster means quantised to one byte per gene over each gene's range in the writer spots, and nearest-centroid assignment for scored spots. Its quantised gene means take $50k \le b$ bytes, and its embedding centroids are not counted in $b$.
- A mean predictor, which predicts each gene's mean over the writer spots at every scored spot. Its within-slide correlation is undefined, so it is reported only as the pooled value, as a floor for the pooled numbers.

**The anchor.** It is computed from the project tree's `bench_data/CCRCC/` and `embeddings/CCRCC/`, not from the package, since round 1's split 0 uses slides outside the 10. The benchmark head fitted on round 1's CCRCC split 0 training slides and scored on its test slides must reproduce round 1's `pearson_mean` in `results/faithful/pca_ridge/<encoder>/CCRCC/split0/results.json` within 0.01, for both encoders.

---

## 7. The plan

Four stages. Gates at C5 and C7.

### Interval i04

#### C4. Setup (two days, capped at three)

**C4.1 Child sessions on the Mac.** Record the Claude Code version on the Mac and in the container image. Confirm that a child session started as in 6.5 authenticates with the token, is billed to Nicolas's account, and answers a one-line prompt as `claude-opus-5-5` at medium effort. Confirm each flag, and record any that differs from the documentation with what you used instead. Confirm that `--resume` continues a writer's session inside the confinement with its earlier context.

**C4.2 Isolation.** Build the confinement and the filtering proxy, and run the probes of 6.6. Write each canary file with a unique random string, and remove them only after C4.2 passes.

**C4.3 The data package.** Write the packaging job and run it on Longleaf. It confirms the FFPE set, makes the two draws of 6.1, computes the strata and samples, runs the representativeness check, writes every patch as PNG with its position, the targets, the overview mosaics, the embeddings of every patched spot of the 10 slides, the 50 genes and a manifest with md5s. Copy the package to the Mac and check every md5. While it runs, write the builder that makes every trial directory of 6.2 from a manifest row.

**C4.4 Comparators,** on Longleaf. The anchor first, from the project tree as 6.7 says, then every other comparator of 6.7 from the package.

**C4.5 Harness and scorer.** Write the runner, the audit loop, the manifest, the scorer and the transcript scanner, and write `check_cheatsheet.py`. Test the scorer. True values score exactly 1. Values permuted across spots within each slide score near 0, within $\pm 0.05$ on average over 20 permutations. A file with one constant gene on one slide scores that gene $0$ there and flags it. A file missing a spot fails validation. Test `check_cheatsheet.py` on round 6's nine cheatsheets (`results/round6/cheatsheet/C1_pilot/cheatsheets/`, `results/round6/cheatsheet/C2_grid/cheatsheets/`). Those with code or per-spot tables must be flagged. Report what else the script flags in them, since the script cannot detect computed image measurements (F2) and the checker judges those.

Exit items for C4, each with its evidence in the C5 report.
1. Every flag confirmed or replaced, with the served model ID, the authentication route and the billing check.
2. I1 to I4 pass, with the probe transcripts' md5s and the scanner's output.
3. The draws, the samples and the representativeness table.
4. The anchor passes for both encoders, and every comparator is computed.
5. The scorer's and the mechanical check's tests pass.

#### C5. Pilot (one day; gate)

Run in this order. The baseline predictor. The writer at 4,096 bytes with its full audit loop. The predictor that uses its final cheatsheet. These are grid sessions and count towards the grid if the C5 memo accepts the harness unchanged.

The C5 report, in the format of section 9, also carries these items.
1. The pilot's scores beside every comparator, the cheatsheet's bytes written, every checker verdict with the writer's revisions, and a one-paragraph description of what the cheatsheet contains.
2. Per role, the measured tokens, estimated cost, turns, wall time and peak context, and how many patches the writer and the predictor actually viewed, counted from their transcripts as images returned to the agent and the patches each image held.
3. A projection of C6's tokens, cost and wall time.
4. Every prediction of section 8 that C5 can score.

Tag `round6-cheatsheet-C5`, push the transcripts, open the pull request, and stop.

### Interval i05, opened by the C5 decision memo

#### C6. The grid

The size grid is

$$
\mathcal{B} = \{0\} \cup \{2^{8}, 2^{9}, \ldots, 2^{16}\} = \{0,\ 256,\ 512,\ 1{,}024,\ 2{,}048,\ 4{,}096,\ 8{,}192,\ 16{,}384,\ 32{,}768,\ 65{,}536\} \text{ bytes},
$$

with one writer and one predictor per nonzero size, the baseline at $b = 0$, and one combined session, 20 sessions besides the checkers. Opus 5.5 at medium effort throughout, one run per cell. Writers run before their predictors, and each writer's audit loop finishes before its predictor starts. The scanner runs after each batch.

For scale, the 3,500 writer spots at one byte per value take $3{,}500 \times 50 = 175{,}000$ bytes, so the largest size is 37% of that.

#### C7. Analysis and the closing report (gate, end of track)

- $\bar r$ against the allowance and against the bytes written, beside every comparator, with per-slide values.
- $b^*$ at the `uni_v2` head and at the `virchow2` head, as brackets.
- The audit record. Per size, the number of revisions, the rules broken at each audit, whether the final version passed, and the bytes written before and after revision. Flagged cheatsheets are reported in a separate row.
- What the cheatsheets contain. Tag each by script as holding class descriptions, per-class gene values, gradients by eye, gene modules, patient-level variation or cautions (the rubric's A1 to A7), and read every cheatsheet to check the tags. Report $\bar r$ beside the tags.
- The combined session against the best cheatsheet and against the heads, with what it did, from its transcript.
- Cost, tokens and wall time per role.
- Comparison with round 6's arm C, with every variable that differs listed (task, platform, number of training patients and spots, number of test patients, the rubric, the metric).

`docs/round06/i05/cheatsheet/round06_cheatsheet_C7_report.md` in the format of section 9, with the full predictions-against-outcomes table, an "Escalations" section, and a closing page titled "What the extension established", at most one page, every sentence naming its file. Run the numeric-claim sweep. Tag `round6-cheatsheet-C7`, push the transcripts, open the pull request, and stop.

---

## 8. Predictions for the track

The oversight chat's, written before any run and numbered for scoring. Copy them into the plan before running and score each as held, partly held, refuted or not tested. Every value is one trial, so a difference under about 0.05 cannot be told from chance.

- **X.1** At $b = 0$, $\bar r$ lies between 0.03 and 0.20.
- **X.2** $\bar r$ at 4,096 bytes is above $\bar r$ at 256 bytes, and the five values from 4,096 to 65,536 bytes span less than 0.05.
- **X.3** No cheatsheet reaches the `uni_v2` head fitted on the 3,500 writer spots.
- **X.4** The best cheatsheet is within 0.05 of that head.
- **X.5** The writers at 32,768 and 65,536 bytes each write less than 70% of their allowance in their final version.
- **X.6** At least three of the nine writers need at least one revision after the first audit, and every final version passes.
- **X.7** The combined session scores below the best cheatsheet predictor.
- **X.8** The head fitted on every patched spot of the 7 training slides beats the head fitted on the 3,500 sampled spots by less than 0.02.

Most of the project's magnitude predictions in earlier rounds were refuted, so a refuted prediction is reported as plainly as a held one.

---

## 9. Reporting format

After each gate, in this order. 1. Stage and status. 2. What was run (scripts with md5s, commits, job ids, partitions, wall times, the Claude Code version, session counts by role and status). 3. Acceptance checks with the actual numbers and file paths. 4. For every comparison, the list of variables that differ between its arms, written out. 5. Predictions against outcomes, as a table. 6. Results, numbers from files with paths, and paths in place of pasted tables over 20 rows. 7. Discrepancies, open questions and escalations. 8. What was not checked. 9. Proposed next step.

---

## 10. Decision boundaries

**You decide alone.** Your own sub-agents. The confinement's route and details, provided I1 to I4 pass. Job sizing and the order of sessions within a stage. Replacing a flag the documentation names with its working equivalent, recorded. The exact target wording of 6.3's one exception. The exact patterns of the mechanical check, within the five checks of 6.4, decided before C5.

**Record as an escalation and continue.** A spot count that differs from the inventory. A slide that fails the representativeness check. A session that fails twice. A writer that exceeds its size. A cheatsheet still failing after two revisions. An anchor off by more than 0.01 for one encoder when the other passes (investigate, say what you found). Any new property of the data. A usage limit that stops the harness for more than a day.

**Stop and report.** Any of I1 to I3 that no confinement you can build on the Mac satisfies. A child session that cannot authenticate inside the confinement. The model refused by every name. The anchor failing for both encoders. Any sign that a session saw expression it should not have.

**Never yours.** Contact with anyone outside the project, David included. Changing a prompt, the rubric, an input layout, a size, the model or the effort level after the first C6 session has run. Any download of data. Running a session through your own sub-agent tool. Putting any package file, token or transcript into `NicWYZ/HEST-1k-replication`. Changes to `main`, to earlier files or to the project tree's checkout on Longleaf. Any claim of novelty.

---

## 11. Before starting, Nicolas does

1. Clones `NicWYZ/HEST-1k-replication` to `~/hest-1k/HEST-1k-replication-cheatsheet` and starts Claude Code there, outside the claude.ai project, then pastes the line "Read docs/round06/i04/cheatsheet/round06_cheatsheet_ext_track.md in full and follow it."
2. Checks that `ssh longleaf hostname` in a terminal logs in with his key and no Duo prompt. If it does, nothing more is needed. If it asks for Duo, he adds `ControlMaster auto`, `ControlPath ~/.ssh/cm-%r@%h:%p` and `ControlPersist 12h` under `Host longleaf` in `~/.ssh/config` and logs in once in a terminal, so the session's commands reuse that connection.
3. Installs Docker Desktop, OrbStack or colima if none is on the Mac, so the session can build the Linux container of 6.5.
4. Runs `claude setup-token` in a terminal and saves the token it prints to `~/hest-1k/r6ext_private/oauth_token` with permissions `600`. The trials run as separate `claude` processes inside the Linux container, where his Mac's own Claude login is not visible, and this token is how they sign in on his plan. It is never pasted into a chat.
5. Gives the session push access to `NicWYZ/hest-r6-data` for transcripts, which his GitHub login on the Mac should already have.
