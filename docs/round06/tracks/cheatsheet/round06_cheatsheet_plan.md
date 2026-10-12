# Round 6, the cheatsheet track, operating plan

Living document of the execution session. Started 12 October 2026.

## 0. Where this plan comes from

- Instruction: `docs/round06/i01/cheatsheet/round06_cheatsheet_track.md` on `main`, including its revision of 11 October, 22:50 (package and transcripts through the private repository `NicWYZ/hest-r6-data`).
- Masterplan: `docs/round06/masterplan.md`, including its two amendments of 11 October.
- Starting commit: `23cbb0d8e88a5ae185600ca78b56a74b517a08e1` on `main` (clean tree). Branch `round6-cheatsheet` created from it on 12 October.
- Sections 1 to 3 below are this session's own. Section 4 onward transcribes the instruction's sections 6, 7 and 8 unchanged, so the predictions are on record before any trial runs.

## 1. Facts of this container, recorded at the start

- Container ID `container_01X2Wndmgtf3F8ecgnayq6C3`.
- Claude Code 2.1.296, binary `/opt/claude-code/bin/claude` (linked from `/opt/node22/bin/claude`).
- `bubblewrap` 0.9.0 and `socat` 1.8.0.0, installed with `apt-get` on 12 October.
- Python 3.13.16 at `/usr/bin/python3`.
- `nproc` reports 4 CPUs and `free` reports 15 GB of memory, not the 2 CPUs and 7 GB the instruction expects (flag F1).
- An unconfined child `claude --safe-mode -p` with `env -i` and the thirteen variables of instruction section 6.4 authenticated and answered on `claude-haiku-5-5`. Its `system/init` event reported model `claude-haiku-5-5`, Claude Code 2.1.296 and no MCP servers.

## 2. Flags, recorded without changing the instruction

- **F1.** The container has 4 CPUs and about 15 GB, more than the instruction's 2 and 7. The default of two trials at once stands until C1 measures what fits.
- **F2.** This session has no link to Nicolas's Mac. The instruction's revision of 11 October, 22:50 already moves the package and transcripts to `NicWYZ/hest-r6-data`.
- **F3.** The variables copied to the child include `CLAUDE_CODE_SESSION_ID` and `CLAUDE_CODE_REMOTE_SESSION_ID` of this parent session. If the child does not need them, they should be dropped so that child sessions cannot write into the parent's session record. C0.1's leave-one-out test settles this.
- **F4 (resolved for confined children, 12 October).** This session runs under Claude Code's auto-mode permission classifier. It refused, on 12 October, a batch of child sessions started with `--permission-mode dontAsk` and the session's credentials ("Create Unsafe Agents"), and a read of the container proxy's README ("Credential Exploration"). Every trial of this track is such a child. Nicolas has to authorise it, by a permission rule or in chat, before C0.1 can finish. Nicolas wrote on 12 October: "You may start confined child Claude Code sessions with this session's credentials, as section 6.4 of the instruction describes." After that the classifier still refused unconfined children and a test of a child with the credential folder unbound ("Credential Exploration"), and allowed confined children as 6.4 describes. Every child of this track is therefore confined, the credential folder stays bound read-only as 6.4 says, and the question whether a child needs that folder at all was not tested.
- **F11.** `--safe-mode` still lists Claude Code's bundled skills (deep-research, dataviz, claude-api and others) and three built-in plugins (`cc-plugin-agents-md`, `cc-plugin-telemetry`, `cc-plugin-plugin-authoring`) in the child's `system/init` event. `--disable-slash-commands` is added, and the skills list is then empty. The three built-in plugins remain and no flag removes them. None comes from the repository or from Nicolas's settings. I1's criterion of "no plugins" in the init event is therefore not met to the letter, and the C1 report says so.
- **F12.** C0.2's I2 probe found that the child's stdout and stderr were open file descriptors on its own log files in `/srv/r6_private/logs`, readable through `/proc/1/fd/1`. It could read only its own transcript, and no canary. The runner now passes stdout and stderr through pipes, and a check afterwards found no host file among the child's open descriptors. The I2 and I3 probes are rerun on the final harness before C1.
- **F13.** The child's `HOME` is `/work` as 6.4 says, so Claude Code writes `.claude/` and `.claude.json` into the trial directory, and the agent can see them there.
- **F5.** The container did not have scipy, scikit-image, scikit-learn, pyarrow or h5py, although the instruction lists the first three. They were installed with `pip` on 12 October (scipy 1.18.1, scikit-image 0.26.0, scikit-learn 1.9.1, pyarrow 26.0.0, h5py 3.16.0, with anndata for the packaging smoke test). A reclaimed container must install them again.
- **F6.** In the bubblewrap command of instruction 6.4, `--ro-bind "$CA_BUNDLE" "$CA_BUNDLE"` comes before `--tmpfs /root`, and the bundle lives under `/root`, so the later tmpfs hides it and TLS fails inside the confinement (curl exit 77). The working order puts the bundle's bind after `--tmpfs /root`. This is a flag replaced by its working equivalent, which section 10 lets the session decide, and it is recorded here.
- **F7.** The round-1 benchmark patches cover only some of each slide's spots. The subagent's reading of `bench_data/INVENTORY.md` and the patch files gives 1,741 patched spots of TENX115's 3,886 and 1,293 of TENX117's 1,830. Every arm, comparator and writer therefore works on the patched spots only, since a spot without a patch cannot be shown to a predictor and has no embedding. This is an escalation (a spot count that differs from the inventory). The package job records the counts it finds. One consequence is that the S1 expression matrix at one byte per value is about 87 kB rather than the masterplan's 194,300 bytes, so 262,144 bytes is still above it.
- **F8.** No whole-slide image or thumbnail of these two samples is on Longleaf, because round 3 and round 4 downloaded "never wsis/". The writer's `overview.png` is therefore built as a mosaic of the S1 patches at their positions, scaled to 1,500 pixels on the long side, with white where there is no patch. This is a new property of the data and is recorded as an escalation. No download is made.
- **F9.** The buffer rule of 6.1 reads "within 165 µm of a held-out block's edge". The package applies it to all four edges of the spot's own block, including edges on the bounding box that border no training block, which is the literal reading and the stricter one. It also records the count under the internal-edges-only reading. If fewer than 500 spots are eligible, S1* becomes every eligible spot and the report escalates it.
- **F10.** Writers' `spots.csv` positions are given in the 0.5 µm per pixel frame of the patches (the full-resolution coordinates times the pixel size divided by 0.5), so that a writer's positions and patches share one scale. The patch files store the coordinates in full-resolution pixels. The package job checks which stored column is the image's x axis by matching the pixels where neighbouring patches overlap, and records the result.

## 3. Status

| step | status |
|---|---|
| C0.1 child sessions | done. Confined children authenticate with none of the thirteen variables (leave-one-out, and all dropped), so none is passed (F3). `claude-haiku-5-5`, `claude-sonnet-5-5` and `claude-opus-5-5` each answered at `--effort high` and were served under the same IDs. Flags as 6.4 plus `--disable-slash-commands` (F11), CA bind order (F6), pipes for output (F12) |
| C0.2 isolation with child probes | first run done on Opus: no canary string in any output (`results/round6/cheatsheet/C0_isolation/canary_hits.csv` is empty). I1 found no project context, I2 failed on all four canaries by every route, I3 was refused everywhere. Rerun of I2 and I3 on the final harness pending, then canaries removed |
| C0.3 package and builder | `round6_cheatsheet_package.py` and its Slurm script written and smoke-tested on a synthetic project tree (targets, patch PNGs and embedding alignment matched the inputs exactly, and the axis check found a planted swap). Waits on Nicolas to run it on Longleaf and push the package to `NicWYZ/hest-r6-data`. The builder is not written yet |
| C0.2 confinement without a child | the filtering proxy `round6_cheatsheet_filter_proxy.py` and the bubblewrap confinement were tested with curl. Inside, only `lo` exists, `/proc` shows only the confined processes, and `/home`, `/root` and `/srv` are empty. The proxy allowed `CONNECT api.anthropic.com:443` (the API answered 401 without a key) and refused huggingface.co, github.com and pypi.org, and nothing reached the network with the proxy bypassed |
| C0.4 comparators | waits on the package |
| C0.5 harness and scorer | scorer and its four tests written. All four pass on synthetic data and must be rerun on S1*'s real targets. Runner, manifest and scanner not written |
| C1 pilot | not started |

---

## Transcribed from the instruction, sections 6 to 8

### 6. The trial design, fixed

Everything in this section is fixed before any trial runs, because the result depends on it. Changing a prompt, an input or a flag after a trial has run is not yours to decide (section 10), with the single exception named in 6.3.

#### 6.1 Data, blocks and scored spots

- Slide S1 is `TENX115` and slide S2 is `TENX117`. The 50 genes are `bench_data/SKCM/var_50genes.json`. The target is what the round-1 faithful pipeline computes for these genes, read through its own loading code. Record the transform in the plan.
- S1's tissue bounding box is cut into a 4 by 4 grid. Blocks $(i, j)$ with $i + j$ odd are held out and the rest are training blocks. Spots within 165 µm of a held-out block's edge (three spot spacings of 55 µm, more than one patch width of 112 µm) are excluded from the scored set, so no scored patch shares pixels with a training patch. If either half holds under 35% of S1's spots, record it as an escalation and keep the split.
- S1* is 500 spots drawn uniformly without replacement from the eligible held-out spots, with seed `crc32("round6-S1star")`. S2* is 500 spots from S2 with seed `crc32("round6-S2star")`.
- Patches are HEST-bench's own 224 by 224 patches at 0.5 µm per pixel, written as PNG. Predictors see them under new IDs, a random permutation of `p0001` onward per trial, drawn with a seed keyed on the trial ID. The harness keeps the mapping outside the trial directory.
- Nothing in a trial directory or its path names the sample, the dataset, the patient or HEST. Writers' spots are renamed `s0001` onward in a random order drawn with a seed keyed on the trial ID, kept outside the trial directory like the predictors' mapping.

#### 6.2 Trial directories

| session | files in its directory |
|---|---|
| writer | `patches/<sid>.png` and `spots.csv` (spot ID, x and y in pixels) for its labelled spots, `expression.csv` (spot ID and the 50 genes), `overview.png` (the slide at about 1,500 pixels on its long side, with the held-out blocks filled with white for an arm B writer) |
| predictor and baseline | `patches/<pid>.png` for the 500 scored spots, `genes.txt`, and `cheatsheet.txt` unless baseline |
| combined | `labelled/` laid out as a writer's directory, and `target/patches/<pid>.png` with `genes.txt` |

A writer for arms A and C has all of S1's spots. A writer for arm B has the training-block spots only, and its overview shows the training blocks only, so it cannot describe the held-out region or give a predictor anything to match its patches against. The combined session's `labelled/` follows the same rule for its arm, and its `target/` holds S1* (arms A and B) or S2* (arm C).

#### 6.3 The prompts, verbatim

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

#### 6.4 How a trial runs

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
      CLAUDE_CODE_EFFORT_LEVEL=high $AUTH_ENV \
  claude --safe-mode -p "$PROMPT" \
    --session-id "$UUID" --model "$MODEL" --effort high \
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
- Two trials run at once by default, since the container has 2 CPUs. C1 measures whether more fit, and the C1 report proposes the number. The harness keeps a manifest with a status per trial, so a stop at a usage limit or a reclaimed container resumes where it stopped.
- A writer's file is measured in UTF-8 bytes. If it exceeds $b$, the harness keeps the first $b$ bytes, cutting at the last whole character, and records both sizes. The writer is not asked again.
- A trial that ends without a valid output file (missing, unreadable, missing spots or genes, non-numeric values) is run once more as a new session with a new ID. If the second also fails, it is recorded as failed and the report counts it. A missing gene or spot is never filled in.
- Every trial records in the manifest its ID, arm, size, model, replicate, role, the writer it depends on, session ID, status, bytes written and kept, input and output tokens with cache reads and writes, estimated cost, turns, wall time, Claude Code version and served model.

#### 6.5 Isolation, the properties every trial must have

| # | property | how C0.2 tests it |
|---|---|---|
| I1 | No project context. The session's context holds the prompt and Claude Code's own system prompt, and nothing from this repository, the user's settings, memory, skills or MCP servers | the `system/init` event lists only the six tools and no MCP servers or plugins, and a probe session asked to quote every instruction it has received beyond the prompt quotes nothing from the project |
| I2 | File confinement. The session cannot read or list any file outside its trial directory, through any tool | an adversarial probe session told to read canary files at given absolute paths, one in your clone, one in `/srv/r6_private/`, one in the home directory and one in another trial directory running at the same time, fails on all four, with Read, Glob, Grep and Bash each tried, and also through `/proc/*/root`, `/proc/*/cwd` and `/proc/*/environ` |
| I3 | No network except the Anthropic API | an adversarial probe told to fetch `https://huggingface.co`, `https://github.com` and `https://pypi.org` with Bash, curl and Python, with the proxy variables set and unset, and to open sockets to every localhost port it can find, fails on all of them |
| I4 | Blinding | a script finds no sample ID, patient label, dataset title, oncotree code or HEST file name in any trial file or path |

Run the I2 and I3 probes on Opus, the most capable model. After every batch, a script scans every transcript for the canary strings, the sample IDs, any URL other than the API's, any absolute path outside the trial directory, the nested-session signs of 6.4 and the credentials. Any hit excludes that trial, which is rerun, and is reported. Before anything is committed or pushed to either repository, every cheatsheet, prediction file and manifest is scanned for the credentials too. Transcripts go only to the private repository.

#### 6.6 Scoring and comparators

- The scorer reads `predictions.csv`, maps the predictor's IDs back to spots outside the trial directory, and computes $\bar r$ of the masterplan's metric section over the 500 scored spots, with a constant gene counted as $0$ and flagged. It writes per-gene correlations too.
- The comparators are those of the masterplan's "Comparators" list, computed in C0.4. The benchmark head is the round-1 faithful head with its configuration from `results/faithful/pca_ridge/<encoder>/SKCM/split<k>/config.json`, on `uni_v2` and `hoptimus1`, fitted on the spots each arm's writer saw and scored on S1* or S2*. The codebook uses `uni_v2`, k-means with $k = \min(\lfloor b/50 \rfloor, n)$ for $n$ writer spots, which is $81$, $655$ and $n$ at the three finite sizes, fitted on the writer's spots with seed `crc32("round6-codebook")`, cluster means quantised to one byte per gene over each gene's range in the writer's spots, and nearest-centroid assignment for scored spots.

---

### 7. The plan

Four stages. Gates at C1 and C3.

#### Interval 1

##### C0. Setup (two days, capped at three)

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

##### C1. Pilot (one day; gate)

For each model, run four trials in this order. One baseline predictor on S1* (replicate 1). One arm B writer at 32,768 bytes (replicate 1). The predictor that uses its cheatsheet, on S1*. One arm B combined session (replicate 1). These are grid trials. They keep their IDs and count towards the grid if the C1 memo accepts the harness unchanged.

The C1 report, in the format of section 9, also carries these items.
1. The twelve trials' scores beside the comparators on S1*, with the cheatsheets' sizes and a one-paragraph description of what each cheatsheet contains.
2. Per model and role, the measured tokens, estimated cost, turns and wall time, and failures with their causes.
3. A projection of the full grid's tokens, cost and wall time per model and in total, from those measurements, with the rate the usage limits allowed.
4. The proposed i02 grid. The masterplan's grid if it fits what Nicolas has said about budget, and otherwise the masterplan's cut order taken as far as needed, with the cost of each cut.
5. Every prediction of section 8 that C1 can score.

Tag `round6-cheatsheet-C1`, open the pull request, and stop.

#### Interval 2, opened by the C1 decision memo

##### C2. The grid

Every trial of the grid the C1 memo sets, writers before their predictors, with the scanner run after each batch. Arms A and C use the same writers.

**Parallel sessions** `[proposed]`. To finish sooner, the grid can be split by model across up to three cloud sessions, each with its own container, run at the same time. You run the Opus grid. Nicolas starts two worker sessions from the desktop app, with both repositories attached, for Haiku and Sonnet, with the prompt the C1 memo gives, which tells each to read this instruction and the memo and to run C2 for its model only. Each worker starts from tag `round6-cheatsheet-C1`, builds the same harness, clones the package from `NicWYZ/hest-r6-data`, checks its md5s, sets up the confinement and reruns the I2 and I3 probes. It skips its model's trials that the C1 manifest marks done. It works on its own branch (`round6-cheatsheet-haiku`, `round6-cheatsheet-sonnet`), writes only under `results/round6/cheatsheet/C2_grid/<model>/` with one parquet per kind of file, pushes after every batch, and pushes its transcripts to `NicWYZ/hest-r6-data` under `transcripts/C2/<model>/`. It opens no pull request. When all three have finished, you merge the workers' branches into yours with merge commits, check that every manifest row and file arrived, combine the per-model files into one per kind for C3, and write C3. The split is by model because a model's trials depend on nothing outside it, while arms A and C share writers. The sessions draw on the same usage limits of Nicolas's account, so the speed-up stops where those limits bind. The C1 memo decides whether to split.

##### C3. Analysis and the closing report (gate, end of track)

- For each arm and model, $\bar r$ against $b$ with both replicates and their mean, beside the comparators.
- $b^*(0.8)$ and $b^*$ at the `uni_v2` benchmark head's $\bar r$, the primary comparator, as brackets on the grid, with the `hoptimus1` head and the codebook reported beside it. Say in the text that the codebook's centroids are not counted in its bytes.
- The arm differences at each size, with the variables that differ between arms listed.
- What the cheatsheets contain. Tag each by script as holding prose, numbers keyed to visual features, per-cluster values, code or coefficients, or values keyed to individual patches (for example image fingerprints), and read a sample of each model's cheatsheets to check the tags. Report $\bar r$ by tag where the counts allow.
- Cost and tokens per model and role.

`docs/round06/i02/cheatsheet/round06_cheatsheet_final_report.md` in the format of section 9, with the full predictions-against-outcomes table, an "Escalations" section, and a closing page titled "What the cheatsheet experiment established", at most one page, every sentence naming its file. Run the numeric-claim sweep. Tag `round6-cheatsheet-final`, open the pull request, and stop.

---

### 8. Predictions for the track

The oversight chat's, from the masterplan, numbered for scoring. Copy them into the plan before running and score each as held, partly held, refuted or not tested.

- **C.1** At $b = 0$, Opus's $\bar r$ on S1* is between 0.05 and 0.35, and Haiku's is below Opus's.
- **C.2** In arm C no model reaches the `uni_v2` comparator's $\bar r$ on S2* at any finite size.
- **C.3** In arm C Opus's combined session is above its own 262,144-byte value and below the `uni_v2` comparator.
- **C.4** In arm A no model reaches $\bar r = 0.8$ at 32,768 bytes, and at least one model reaches it at 262,144 bytes.
- **C.5** In arm B, each model's $\bar r$ at 262,144 bytes is within 0.05 of its value at 32,768 bytes, and below its arm A value at 262,144 bytes.
- **C.6** Replicate means are ordered Opus, then Sonnet, then Haiku, in at least two thirds of the pairs of arm and finite size that are run.

Most of the project's magnitude predictions in earlier rounds were refuted, so a refuted prediction is reported as plainly as a held one.

---

