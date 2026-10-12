# Round 6, the cheatsheet track, on how large a cheatsheet a language model needs to predict expression from histology

11 October 2026, revised the same evening. Prepared by the oversight chat for a fresh Claude Code cloud session, started by Nicolas from the Claude desktop app with this repository attached. This document is self-contained. It is kept current on `main`. When Nicolas tells you to check for updates, fetch `main`, read the "Revisions" list below and the masterplan's amendments, and transcribe what changed into your plan.

**Revisions.**
- 11 October, 22:50. A cloud session cannot link to Nicolas's Mac, so the data package and the transcripts move through a private GitHub repository, `NicWYZ/hest-r6-data`, instead (sections 3, 5, 6.5, 7 and 11). Work that needs neither, such as child sessions, the confinement, the probes, the harness and the packaging script, goes ahead as before.
- 12 October, at the C1 gate (`docs/round06/i02/cheatsheet/round06_cheatsheet_C1_decisions.md`). Reasoning effort is medium for every C2 trial (6.4), by Nicolas's decision, so the pilot's trials become a high-effort reference and every grid slot is run afresh. One sentence is added to each prompt (6.3). Trials are excluded only for the leak signs of the memo's section 3.2 (6.5). Up to four trials run at once (6.4). Replicate 1 of every cell runs before any replicate 2 (7, C2).
- 12 October, 02:20. The writer prompt (6.3) asks the writer to use as much of the allowed size as helps, because no pilot writer came near its allowance (6,890 to 17,690 of 32,768 bytes). C3 reports each cheatsheet's bytes written beside its allowance and plots accuracy against both.
- 12 October, 02:10. C2 runs Opus only, at medium effort, one replicate per cell, 20 sessions (C1 memo, section 3.4). Haiku's and Sonnet's pilot trials are kept as high-effort reference values. The track starts from `main` of `NicWYZ/HEST-1k-replication` at the commit that carries this document, on its own branch `round6-cheatsheet`. Read this document fully, then transcribe sections 6 and 7 into `docs/round06/tracks/cheatsheet/round06_cheatsheet_plan.md` before running anything. The round's plan is `docs/round06/masterplan.md`.

---

## 1. Your role and the people

You are the execution agent. A separate chat session, the oversight chat, reviews your reports, makes scope decisions and writes decision memos, which Nicolas hands to you in full. Nicolas Weiyang Zhang (Longleaf ONYEN `weiyang`, Slurm accounts `rc_htzhu_pi` and `rc_tengfei_pi`) is the first-year biostatistics PhD student whose project this is. He reads every command before it runs and will ask why. His advisors are Dr. Hongtu Zhu and Dr. Daiwei (David) Zhang at UNC. David proposed this experiment.

If the repository's `CLAUDE.md` is in your context, it belongs to the oversight chat. Do not edit it and do not act on its plan. Its section 7 rules apply to you, with two exceptions for this track that Nicolas decided on 11 October. The trials and the analysis run in your cloud container rather than on Longleaf (rule 7), and code reaches Longleaf by Nicolas pulling your pushed branch rather than as bundles (rule 5).

Your responsibilities are to build the trial harness, run the trials as child processes in your container, verify every stage's output against an expected value before moving on, write reports in the format of section 9, commit and push on your branch, and stop at each gate. You do not make scope decisions. Anything this document does not cover is reported as a proposal, not done.

**The gate rule, in the wording Nicolas approved.** Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. Contact with anyone outside the project is never the session's decision.

This track's gates are C1 and C3.

**How Nicolas wants things written.** Plain, natural prose. No em-dashes. No colon-then-explanation constructions. No compressed or clever phrasing. Math as LaTeX, with each `$$` on a line of its own. Numbers quoted at the precision the comparison needs, with the relative scale stated. Full precision stays in the files. Every number in a report is read back from the file named beside it. Do not inflate length.

---

## 2. What this track is for

David's question. An agent predicts the expression of 50 genes from H&E patches. A second agent, which saw the measured expression, writes a text cheatsheet of limited size, and the predicting agent may use it. How large must the cheatsheet be for the predictions to reach a given accuracy? Nicolas's purpose, set on 11 October, is to learn whether one-shot or few-shot prediction with a general-purpose language model can beat pathology foundation models. So nothing restricts what a cheatsheet contains, and every result is set beside the benchmark's encoders given the same labelled spots.

The design is in `docs/round06/masterplan.md`, sections "Design" and "Trial count". In short, the writer and the predictor are always separate fresh sessions. Three arms separate copying from learning. Arm A scores the predictor on spots the writer saw, arm B on a held-out region of the same section, and arm C on a second patient's slide. Sizes run over $0$, $4{,}096$, $32{,}768$ and $262{,}144$ bytes, and a combined session that sees the labelled spots and the targets together gives $b = \infty$. The pilot ran three models at high reasoning effort. From C2 on only Opus runs, at medium effort, with one replicate per cell.

What is not claimed. This track builds no method for the paper and makes no claim of novelty in any document. It measures and reports.

---

## 3. Data and assets

**Repository** at the starting commit. Everything under `results/` from rounds 1 to 5 is read-only for you, and so is every earlier script and document. `docs/WAYS_OF_WORKING.md` is the accumulated procedure. Read it before your first job.

**Your container** has no Longleaf and no HEST data. It has Python 3 with numpy, pandas, scipy, Pillow, scikit-image and scikit-learn, Claude Code itself, and `apt-get` and `pip` through the container's network allowlist. Its egress allowlist already refuses HuggingFace and 10x Genomics (checked by the oversight chat on 11 October), but it reaches GitHub and the package registries. It has 2 CPUs and about 7 GB of memory. It is reclaimed after a period of inactivity, so anything not pushed can be lost (section 5).

**The data package** is built on Longleaf by one job you write (C0.3), because the data is there. On Longleaf the project tree `/work/users/w/e/weiyang/hest_replication` is on `main` at tag `round4-data-v2`, its checkout is never changed, nothing runs on the login node, and the project's Python is `/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python`, called by absolute path.

| asset on Longleaf | path in the project tree | what the package takes from it |
|---|---|---|
| benchmark data | `bench_data/SKCM/` (`adata/*.h5ad`, the patches, the splits, `var_50genes.json`) | the two slides' spots, positions, patches, the 50 genes and the target, computed with the round-1 pipeline's own loading code |
| embeddings | `embeddings/SKCM/<encoder>/<sample>.h5` | `uni_v2` and `hoptimus1` embeddings for every spot of both slides |

| asset in the repository | path | what it gives you |
|---|---|---|
| round-1 faithful runs | `results/faithful/pca_ridge/<encoder>/SKCM/split0/` and `split1/` (`config.json`, `results.json`) | the benchmark head's configuration and its per-direction Pearson, the anchor of C0.4 |
| the round-1 pipeline | `code/scripts/`, the faithful HEST-bench harness of round 1 | how the target is computed from counts, reused unmodified by the packaging job |
| inventory | `results/round3/D0_inventory/hest_inventory.csv` | `TENX115`, patient 2, 3,886 spots under tissue. `TENX117`, patient 1, 1,830 spots. Both Xenium |

**Known values for anchoring.** The benchmark head's mean Pearson on SKCM per direction is 0.6763 and 0.6462 for `uni_v2`, and 0.7069 and 0.6109 for `hoptimus1` (`results/faithful/pca_ridge/<encoder>/SKCM/split<k>/results.json`). Which split tests which slide is in the task's splits files, which the packaging job reads and records.

**Contamination.** Both slides are public 10x datasets from 2023 and are certainly in the models' training data as datasets. Memorised per-spot values are implausible, but download during a trial is possible, which is why section 6.5 blocks the network. The reports say plainly that the slides are public.

---

## 4. Standing rules and conventions

- Silent failure is the main risk. Verify each stage's output against an expected value before moving on.
- Never assert a number you have not read back from a file. Cite the path.
- Read the whole grid before writing a headline. Before a summary sentence goes into a report, tabulate the quantity over every axis the experiment varied, which here are arm, size, model and replicate, and check that the sentence holds in each cell it claims.
- Before naming the cause of a difference, list in writing every variable that differs between its arms.
- Write predictions down before running, and report them beside the outcomes.
- Trials, comparators and analysis run in your container, by Nicolas's decision of 11 October. The packaging job runs on Longleaf through Slurm. Nothing runs on Nicolas's Mac.
- The packaging job's output directory gets `PROVENANCE.txt` (job id, partition, node, date, the code commit, command line, md5 of every script) and a provenance stamp (section 5). Only Nicolas can see the queue, so ask him for its state when you check on the job. Every output directory in your container gets `PROVENANCE.txt` with the container's ID (`CLAUDE_CODE_CONTAINER_ID`), the date, the code commit, the command line, `PYTHONHASHSEED`, the md5 of every script and of the data package, and for trials the Claude Code version and the served model ID.
- Seeds from `zlib.crc32` of a written key, never `hash()`. Explicit `pa.schema` on every parquet.
- Commit messages through a file. Sub-agents run no git command. You are the only committer and check every hand-back against its primary tables before commit.
- Do not edit `CLAUDE.md`, `README.md`, `docs/README.md`, `docs/WAYS_OF_WORKING.md`, `docs/round06/README.md`, the masterplan or any earlier round's files. Proposed edits go in the report.
- Run `code/scripts/verify_numeric_claims.py` over `docs/round06/**/round06_cheatsheet_*.md` before every handover, in the form `docs/WAYS_OF_WORKING.md` gives for the layout by round, with your exceptions in `.verify-exceptions-cheatsheet`.
- After opening a pull request, confirm on GitHub that it exists and put its number in the report.

**Your own sub-agents.** You may use your session's sub-agent tool for building, checking and analysis. A trial is never run through that tool, because a sub-agent shares your files and context. Every trial is a separate headless Claude Code process started by the harness inside its own confinement (section 6.4).

---

## 5. Working copies, code delivery and where to write

**Your session** works in its own clone of the repository in the cloud container. Confirm it is on `main` at the starting commit with a clean tree, then create branch `round6-cheatsheet`. Record the starting commit's hash in the plan.

**The packaging job on Longleaf.** Commit and push the packaging script and its Slurm script, then give Nicolas the exact commands. He pulls your branch into a clone on Longleaf that only he uses (his existing clone under `/work/users/w/e/weiyang/hest_code/`, which already pushes and pulls over SSH), checks out the commit you name, and submits the job. The job script copies that commit with `git archive` into its output directory and runs from the copy, not from the clone. Longleaf may not have the `longleaf-provenance` skill's code on your side, so the packaging script carries its own stamping code, copied from that skill if you have it and written to the same fields if you do not. The job writes the package to its own stamped output directory under `results/round6/cheatsheet/C0_package/` in the project tree, as files of at most 95 MB each (split archives if needed), because GitHub refuses files over 100 MB. Give Nicolas the commands that commit the package from that directory into a clone of the private repository `NicWYZ/hest-r6-data` on Longleaf, under `package/`, and push it over SSH. You attach that repository to your session with push access, clone it outside your repository clone, copy `package/` into `/srv/r6_private/`, and check every md5 against the job's manifest.

**Why a separate private repository.** `NicWYZ/HEST-1k-replication` is public. Pushing the package there would republish HEST data, which is under a non-commercial share-alike licence, and the transcripts can contain credentials. Large files in its history could not be removed without a force-push, which the project's git rules forbid. So nothing from the package and no transcript ever goes into `NicWYZ/HEST-1k-replication`.

**What the package holds.** For S1, every spot's patch as PNG, position, target values and embeddings, the pixel size in micrometres, the coordinate frame of the positions, the tissue bounding box, and a low-resolution image of the whole section in the same frame for `overview.png`. For S2, every spot's target values and embeddings, and the patches of S2*. The blocks, S1* and S2*. The 50 genes. A manifest with md5s. Nothing in it is blinded yet. Blinding happens when trial directories are built in your container.

**Trial directories** live under `/srv/r6/` in your container, outside your clone, one directory per trial. A trial's directory and its ID are an opaque random string of eight hexadecimal characters, so the path tells the agent nothing about its arm, size, role or model. The manifest holds the meaning of each ID. The data package, the ground truth and the ID mappings live under `/srv/r6_private/`, which no trial can see (section 6.4).

**Your areas.** Scripts `code/scripts/round6_cheatsheet_*.py`. Results `results/round6/cheatsheet/<STAGE>/`. Documents:

| file | role |
|---|---|
| `docs/round06/tracks/cheatsheet/round06_cheatsheet_plan.md` | your operating plan, living |
| `docs/round06/i01/cheatsheet/round06_cheatsheet_C1_report.md` | report at the C1 gate |
| `docs/round06/i02/cheatsheet/round06_cheatsheet_final_report.md` | report at the C3 gate, end of track |

What is committed. Every trial's manifest row, every cheatsheet (`results/round6/cheatsheet/<STAGE>/cheatsheets/<trial_id>.txt`), every prediction file as one parquet per stage, every score and every comparator table. No patch, expression value or embedding from the package is committed. Transcripts are compressed and pushed to `NicWYZ/hest-r6-data` under `transcripts/<STAGE>/`, with their md5s committed in `results/round6/cheatsheet/<STAGE>/transcripts_md5.csv`. They are kept out of this repository because they are large and can contain credentials (section 6.4).

**Because the container can be reclaimed,** commit and push the manifest, cheatsheets, predictions and scores to your branch after every batch of trials, and push that batch's transcripts to `NicWYZ/hest-r6-data`, compressed into files of at most 95 MB. The pull request still comes once per gate. Run trials in the background and keep the session active by checking on them with a Bash call at least every ten minutes. If the container is reclaimed, a new session on your branch reinstalls `bubblewrap` and `socat`, restarts the filtering proxy, clones `NicWYZ/hest-r6-data` again, copies the package into `/srv/r6_private/`, checks its md5s, reruns the I2 and I3 probes, and resumes from the pushed manifest. A trial interrupted by a reclaim is rerun from scratch under a new ID and does not count as a failure. A trial whose transcript was never pushed is rerun, because the scanner cannot clear it.

**Pull requests and tags.** At each gate you commit, tag and push your branch, open a pull request into `main` or ask Nicolas to open it if your session cannot, and stop. Tags `round6-cheatsheet-C1` and `round6-cheatsheet-final`. You never merge. Nicolas merges with a merge commit after the oversight chat accepts the report. Branches are never rebased, squashed, amended after a push or force-pushed. A rejected gate is fixed with new commits on the same open pull request.

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
> Write that file as `cheatsheet.txt` in this directory. It may contain anything that you think will help the other agent predict accurately. It must be at most {B} bytes in UTF-8. Anything beyond {B} bytes will be cut off. Use as much of the allowed size as helps; more detail is generally better. You may use the tools available to you, including Python, to study the data. There is no internet access, and no pretrained models or files other than those in this directory are available. When the file is written, stop.

**Predictor.** For a baseline, the second paragraph is left out.

> You are working in a directory that holds H&E images from a tissue section of human skin melanoma that was profiled by spatial transcriptomics (10x Xenium, aggregated to spots). `patches/` holds one H&E image per spot, 224 by 224 pixels at 0.5 micrometres per pixel, named by spot ID. `genes.txt` lists 50 genes.
>
> `cheatsheet.txt` was written by someone who had measured the expression of these genes in tissue of this kind. Use it as a reference to help you make your predictions.
>
> Predict the expression of each of the 50 genes at every spot, as log(1 + count). Write `predictions.csv` with one row per spot, a column `spot_id` followed by one column per gene, named as in `genes.txt`. Every spot and every gene must have a number. You may use the tools available to you, including Python. There is no internet access, and no pretrained models or files other than those in this directory are available. When the file is written, stop.

**Combined session** ($b = \infty$).

> You are working in a directory with two folders from spatial transcriptomics of human skin melanoma (10x Xenium, aggregated to spots). In `labelled/`, `patches/` holds one H&E image per spot, 224 by 224 pixels at 0.5 micrometres per pixel, named by spot ID, `spots.csv` gives each spot's position in pixels, `expression.csv` gives each spot's expression of 50 genes, as log(1 + count), and `overview.png` is a low-resolution image of the whole section those spots come from. In `target/`, `patches/` holds H&E images of the spots whose expression you are to predict, with no measurements, and `genes.txt` lists the 50 genes.
>
> Predict the expression of each of the 50 genes at every spot in `target/patches/`, as log(1 + count). Write `predictions.csv` in this directory with one row per target spot, a column `spot_id` followed by one column per gene, named as in `target/genes.txt`. Every spot and every gene must have a number. You may use the tools available to you, including Python. There is no internet access, and no pretrained models or files other than those in this directory are available. When the file is written, stop.

### 6.4 How a trial runs

Each trial is one headless Claude Code process started by the harness in your container, inside a bubblewrap confinement that shows it only its own trial directory. The oversight chat tested this route in a cloud container on 11 October. `bwrap` and `socat` installed with `apt-get` after `apt-get update`. A child `claude -p` started with the recipe below authenticated on Nicolas's account and answered with Haiku. It could not see a file planted in `/home/claude`. Its request to GitHub was refused by the filter, it had no route out with the proxy variables unset, and `/proc` showed only its own processes. The filter's log showed requests to the API host and refused ones to GitHub and to a telemetry host, which the child does without. Each flag stays `[verify]` until C0.1 confirms it in your container.

```
bwrap --unshare-all --new-session --die-with-parent \
      --ro-bind /usr /usr --ro-bind /lib /lib --ro-bind /lib64 /lib64 \
      --ro-bind /bin /bin --ro-bind /sbin /sbin --ro-bind /etc /etc \
      --ro-bind /opt /opt --ro-bind "$CA_BUNDLE" "$CA_BUNDLE" \
      --proc /proc --dev /dev --tmpfs /tmp --tmpfs /home --tmpfs /srv --tmpfs /root \
      --ro-bind "$AUTH_DIR" "$AUTH_DIR" \
      --bind "$PROXY_SOCKET_DIR" /run/proxy \
      --bind "/srv/r6/$TRIAL_ID" /work --chdir /work \
  /run/proxy/start.sh \
  env -i PATH=/usr/bin:/bin:/opt/node22/bin HOME=/work \
      HTTPS_PROXY=http://127.0.0.1:3128 https_proxy=http://127.0.0.1:3128 \
      SSL_CERT_FILE="$CA_BUNDLE" NODE_EXTRA_CA_CERTS="$CA_BUNDLE" \
      CLAUDE_CODE_EFFORT_LEVEL=medium $AUTH_ENV \
  claude --safe-mode -p "$PROMPT" \
    --session-id "$UUID" --model "$MODEL" --effort medium \
    --tools "Bash,Read,Write,Edit,Glob,Grep" \
    --disallowedTools "WebFetch" "WebSearch" "Agent" \
    --allowedTools "Read" "Write" "Edit" "Glob" "Grep" "Bash" \
    --permission-mode dontAsk \
    --max-turns 80 \
    --output-format stream-json --verbose
```

- `--unshare-all` gives the trial its own process, network, IPC and user namespaces. With its own process namespace, `/proc` shows only the trial's processes, so it cannot reach other processes' files, environments or command lines. With its own network namespace, it has no route out at all except the one below.
- The only route out is a Unix socket. Outside the confinement, a small filtering proxy you write listens on `$PROXY_SOCKET_DIR/filter.sock`, accepts `CONNECT` only to the Anthropic API host, and forwards it through the container's own proxy (`$HTTPS_PROXY` of your session). Inside, `start.sh`, a short script in `$PROXY_SOCKET_DIR`, runs `socat TCP-LISTEN:3128,bind=127.0.0.1,fork,reuseaddr UNIX-CONNECT:/run/proxy/filter.sock &` and then executes its arguments, so `socat` turns that socket into `127.0.0.1:3128`. A script file is used rather than `sh -c`, which Claude Code's own safety check refused in the oversight chat's test. Unsetting the proxy variables or trying other ports reaches nothing, because the namespace has no other interface. This gives property I3 of 6.5. Log every `CONNECT` the filter receives.
- `$AUTH_DIR` is the folder holding the session's own credentials, `/home/claude/.claude/remote` in the oversight chat's container, and `$AUTH_ENV` the environment variables the child needs to authenticate, found by test in C0.1. In the oversight chat's test these were `ANTHROPIC_BASE_URL`, `CLAUDE_CODE_REMOTE`, `CLAUDE_CODE_REMOTE_ENVIRONMENT_TYPE`, `CLAUDE_SESSION_INGRESS_TOKEN_FILE`, `CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST`, `CLAUDE_CODE_ACCOUNT_UUID`, `CLAUDE_CODE_ORGANIZATION_UUID`, `CLAUDE_CODE_USE_CCR_V2`, `CLAUDE_CODE_PROXY_RESOLVES_HOSTS`, `CLAUDE_CODE_ENTRYPOINT`, `SESSION_INGRESS_URL`, `CLAUDE_CODE_REMOTE_SESSION_ID` and `CLAUDE_CODE_SESSION_ID`, copied from the parent session. Whether all are needed was not tested. Binding the folder lets the child authenticate, which also means the agent could read the credentials. So every file is scanned for them before it is committed or copied (6.5), and transcripts are never committed. C0.1 also checks that a child running longer than an hour keeps authenticating with the folder bound read-only.
- `$CA_BUNDLE` is the container proxy's certificate bundle (`/root/.ccr/ca-bundle.crt` in the oversight chat's container). Only that file is bound, not its folder, whose README describes the container's proxy.
- The agent can see the `claude` binary, so it could start a nested session or call the API directly and get round `--tools`, the turn cap and the cost record. The scanner flags any Bash command in a transcript that runs `claude`, calls the API host or reads `$AUTH_DIR`, and such a trial is excluded and rerun. Report how many there were.
- `$MODEL` is `claude-haiku-5-5`, `claude-sonnet-5-5` or `claude-opus-5-5`. The Haiku ID was served in the oversight chat's test. If a full ID is refused, use the alias `haiku`, `sonnet` or `opus`. Record the served model ID from the stream's `system/init` event for every trial.
- `--safe-mode` keeps out `CLAUDE.md`, skills, plugins, hooks, MCP servers and memory while keeping the session's login. `env -i` starts the child with only the variables listed, rather than your session's whole environment.
- Inside the confinement the agent has the container's Python 3 with numpy, pandas, scipy, Pillow, scikit-image and scikit-learn, and no pretrained model weights of any kind. Record the versions.
- Usage is billed to Nicolas's account through the session's own login, which is what he chose (masterplan open question R6-1).
- Up to four trials run at once from C2 on, since the container has 4 CPUs and about 15 GB. Measure memory per trial in the first batch, and drop to three if peak memory across the running trials passes 12 GB. The pilot ran at C1 with high effort (`--effort high`, `CLAUDE_CODE_EFFORT_LEVEL=high`) and two at once. The harness keeps a manifest with a status per trial, so a stop at a usage limit or a reclaimed container resumes where it stopped.
- A writer's file is measured in UTF-8 bytes. If it exceeds $b$, the harness keeps the first $b$ bytes, cutting at the last whole character, and records both sizes. The writer is not asked again.
- A trial that ends without a valid output file (missing, unreadable, missing spots or genes, non-numeric values) is run once more as a new session with a new ID. If the second also fails, it is recorded as failed and the report counts it. A missing gene or spot is never filled in.
- Every trial records in the manifest its ID, arm, size, model, replicate, role, the writer it depends on, session ID, status, bytes written and kept, input and output tokens with cache reads and writes, estimated cost, turns, wall time, Claude Code version and served model.

### 6.5 Isolation, the properties every trial must have

| # | property | how C0.2 tests it |
|---|---|---|
| I1 | No project context. The session's context holds the prompt and Claude Code's own system prompt, and nothing from this repository, the user's settings, memory, skills or MCP servers | the `system/init` event lists only the six tools and no MCP servers or plugins, and a probe session asked to quote every instruction it has received beyond the prompt quotes nothing from the project |
| I2 | File confinement. The session cannot read or list any file outside its trial directory, through any tool | an adversarial probe session told to read canary files at given absolute paths, one in your clone, one in `/srv/r6_private/`, one in the home directory and one in another trial directory running at the same time, fails on all four, with Read, Glob, Grep and Bash each tried, and also through `/proc/*/root`, `/proc/*/cwd` and `/proc/*/environ` |
| I3 | No network except the Anthropic API | an adversarial probe told to fetch `https://huggingface.co`, `https://github.com` and `https://pypi.org` with Bash, curl and Python, with the proxy variables set and unset, and to open sockets to every localhost port it can find, fails on all of them |
| I4 | Blinding | a script finds no sample ID, patient label, dataset title, oncotree code or HEST file name in any trial file or path |

Run the I2 and I3 probes on Opus, the most capable model. After every batch, a script scans every transcript for the canary strings, the sample IDs, any URL other than the API's, any absolute path outside the trial directory, the nested-session signs of 6.4 and the credentials. From C2 on, a trial is excluded only for a canary string, a sample ID or other blinded name, credential contents, a nested `claude` session or a direct API call, or any content that came back from a host other than the API. Listings of empty or absent directories and network attempts the filter refused are recorded per trial and reported, but do not exclude (C1 memo, section 3.2). An excluded trial is rerun and reported. Before anything is committed or pushed to either repository, every cheatsheet, prediction file and manifest is scanned for the credentials too. Transcripts go only to the private repository.

### 6.6 Scoring and comparators

- The scorer reads `predictions.csv`, maps the predictor's IDs back to spots outside the trial directory, and computes $\bar r$ of the masterplan's metric section over the 500 scored spots, with a constant gene counted as $0$ and flagged. It writes per-gene correlations too.
- The comparators are those of the masterplan's "Comparators" list, computed in C0.4. The benchmark head is the round-1 faithful head with its configuration from `results/faithful/pca_ridge/<encoder>/SKCM/split<k>/config.json`, on `uni_v2` and `hoptimus1`, fitted on the spots each arm's writer saw and scored on S1* or S2*. The codebook uses `uni_v2`, k-means with $k = \min(\lfloor b/50 \rfloor, n)$ for $n$ writer spots, which is $81$, $655$ and $n$ at the three finite sizes, fitted on the writer's spots with seed `crc32("round6-codebook")`, cluster means quantised to one byte per gene over each gene's range in the writer's spots, and nearest-centroid assignment for scored spots.

---

## 7. The plan

Four stages. Gates at C1 and C3.

### Interval 1

#### C0. Setup (two days, capped at three)

**C0.1 Child sessions in the container.** Record the Claude Code version. Install `bubblewrap` and `socat`. Confirm that a child session started as in 6.4 authenticates, that each model ID answers a one-line prompt at `--effort high`, and which environment variables it needs. Confirm each flag of 6.4, and record any that differs from the documentation with what you used instead.

**C0.2 Isolation.** Write the filtering proxy, build the confinement of 6.4 and run the probes of 6.5. Write the canary files with a unique random string each, and remove them only after C0.2 passes.

**C0.3 The data package and trial inputs.** Write the packaging job of section 5 and hand Nicolas the commands. While it runs, write the builder that makes every trial directory of 6.2 from a trial's manifest row. When the package arrives, check its md5s, build S1*, S2* and the blocks from it as 6.1 defines them (the job computes them, and the builder checks them), and record the spot counts actually used, each half's share of S1 and the md5 of every input file.

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

Every trial of the grid the C1 memo sets, writers before their predictors, with the scanner run after each batch. Arms A and C use the same writers. C2 runs Opus only, with one replicate per cell, 20 sessions in all (C1 memo, section 3.4).

**Parallel sessions** `[proposed]`. To finish sooner, the grid can be split by model across up to three cloud sessions, each with its own container, run at the same time. You run the Opus grid. Nicolas starts two worker sessions from the desktop app, with both repositories attached, for Haiku and Sonnet, with the prompt the C1 memo gives, which tells each to read this instruction and the memo and to run C2 for its model only. Each worker starts from tag `round6-cheatsheet-C1`, builds the same harness, clones the package from `NicWYZ/hest-r6-data`, checks its md5s, sets up the confinement and reruns the I2 and I3 probes. It skips its model's trials that the C1 manifest marks done. It works on its own branch (`round6-cheatsheet-haiku`, `round6-cheatsheet-sonnet`), writes only under `results/round6/cheatsheet/C2_grid/<model>/` with one parquet per kind of file, pushes after every batch, and pushes its transcripts to `NicWYZ/hest-r6-data` under `transcripts/C2/<model>/`. It opens no pull request. When all three have finished, you merge the workers' branches into yours with merge commits, check that every manifest row and file arrived, combine the per-model files into one per kind for C3, and write C3. The split is by model because a model's trials depend on nothing outside it, while arms A and C share writers. The sessions draw on the same usage limits of Nicolas's account, so the speed-up stops where those limits bind. The C1 memo decides whether to split.

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

**You decide alone.** Your own sub-agents. The details of the confinement and the filtering proxy, provided I1 to I4 pass. Job sizing and the order of trials within a stage. Replacing a flag the documentation names with its working equivalent, recorded. The exact target wording of 6.3's one exception.

**Record as an escalation and continue.** A spot count that differs from the inventory. A half of S1 under 35% of its spots. A trial that fails twice. A writer that exceeds its size, which is truncated as 6.4 says. A comparator anchor off by more than 0.01 in one cell when the others pass (investigate, say what you found). Any new property of the data. A usage limit that stops the harness for more than a day. A container reclaimed mid-batch.

**Stop and report.** Any of I1 to I3 that no confinement you can build satisfies. A child session that cannot authenticate inside the confinement. A model ID that cannot be served by any name, or a model that refuses `--effort high`. The comparator anchor failing in more than one cell. Any sign that a trial saw expression it should not have.

**Never yours.** Contact with anyone outside the project, David included. Changing a prompt, an input layout, a size, a model or the effort level after the first C2 trial has run. Any download of data. Running a trial through your own sub-agent tool. Putting any package file or transcript into `NicWYZ/HEST-1k-replication`. Changes to `main`, to earlier rounds' files or to the project tree's checkout. Any claim of novelty.

---

## 11. Before starting, Nicolas does

1. Starts a new cloud session from the Claude desktop app, outside the claude.ai project (whose instructions are for the oversight chat), with `NicWYZ/HEST-1k-replication` attached with push access, and pastes the line "Read docs/round06/i01/cheatsheet/round06_cheatsheet_track.md in full and follow it." Later changes reach the session through `main`, and he tells it to check for updates.
2. Creates the empty private repository `NicWYZ/hest-r6-data` on GitHub, which the session attaches with push access.
3. When the session hands him the packaging commands, runs the job on Longleaf and pushes the package to `NicWYZ/hest-r6-data` from Longleaf as the commands say.
4. After the C1 gate, if the memo splits the grid, starts the two worker sessions the same way, each with the worker prompt the memo gives.
