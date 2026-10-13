# Round 6 extension, the cheatsheet track on held-out patients, operating plan

Living document of the execution session. Started 12 October 2026.

## 0. Where this plan comes from

- Instruction `docs/round06/i04/cheatsheet/round06_cheatsheet_ext_track.md` on `main`, including its revisions of 12 October, before handover and 15:30. The second, read at commit `1cb6b08f`, changes only how Longleaf is reached (its sections 5 and 11) and nothing in the sections transcribed below. The branch, which had no commit of its own yet, was fast-forwarded to `1cb6b08f`.
- Masterplan `docs/round06/masterplan.md`, section "Extension".
- Starting commit `4230b713d02c2cb7b033e714497257f80f170752` on `main`, clean tree. Branch `round6-cheatsheet-ext` created from it on 12 October in the clone `~/hest-1k/HEST-1k-replication-cheatsheet`.
- Sections 1 to 4 below are this session's own. After them come the instruction's sections 6, 7 and 8, copied unchanged under their own numbers, so the design and the predictions are on record before any trial runs.

## 1. Facts of the Mac, recorded at the start

- Apple silicon (`arm64`), 10 CPUs and 16 GB of memory (`sysctl hw.memsize` gives 17,179,869,184 bytes).
- Claude Code 2.1.295 at `~/.local/bin/claude`.
- Docker's command-line client is at `/usr/local/bin/docker`. Its daemon was not running at the start. OrbStack and colima are not installed.
- `gh` is logged in as `NicWYZ`, and `NicWYZ/hest-r6-data` is private with push access.
- `~/hest-1k/r6ext_private/` (mode 700), `~/hest-1k/r6ext_trials/` and `~/hest-1k/r6ext_results/` were created empty by this session.
- The home volume had 26 GB free of 460 GB at the start.
- macOS 26.6.2, system Python 3.12.9 with numpy 2.4.4.

## 2. Flags, recorded without changing the instruction

- **G1 (resolved, 12 October).** `~/.ssh/config` has a host entry named `longleaf` and no shared-connection options, and the instruction first said `ssh longleaf.unc.edu`. The instruction's revision of 12 October, 15:30 makes `ssh longleaf` the route. `ssh -o BatchMode=yes longleaf` logged in as `weiyang` with the key and no Duo prompt, and showed the project tree at tag `round4-data-v2`.
- **G2 (resolved, 12 October).** The Docker daemon was not running at the start. Nicolas started Docker Desktop, server 29.7.2 on `aarch64`, with 10 CPUs and 8.3 GB of memory given to containers.
- **G3 (resolved, 12 October).** The token is at `~/hest-1k/r6ext_private/oauth_token`, mode 600, 108 bytes. Its contents are never printed.
- **G4.** 26 GB free on the home volume is tight for the container image, the package and the trial directories. Ten sessions hold a copy of the 3,500 writer patches (nine writers and the combined session) and eleven hold the 1,500 scored patches. The package's size is measured in C4.3 and the trial directories' total is estimated from it before any are built.
- **G5.** The Mac has 16 GB, and Docker Desktop gives containers 8.3 GB of it. The rule of 6.5 on concurrency (drop to three trials past 75% of the container's memory) applies from the first batch.
- **G6.** The instruction gives the seeds of the two slide draws and not the call. Section 3 records the call used.
- **G7.** The oversight clone's `main` was two commits behind `origin/main` at the start and did not hold the instruction. This session fast-forwarded it with `git pull --ff-only` to read the instruction there, as Nicolas asked. It writes nothing else in that clone.

## 3. The two slide draws, recorded before building anything

The 12 FFPE slides are `INT13` to `INT24`, by the `subseries` column of `results/round3/D0_inventory/hest_inventory.csv` (every one reads `ccRCC tumor ffpe_*`, with 3,206 to 4,975 spots under tissue). The same reading from the HEST metadata on Longleaf is still to be confirmed in C4.3, and is recorded here when it is.

Each draw is `numpy.random.default_rng(seed).choice(sorted_list, size, replace=False)`, with numpy 2.4.4 on the Mac and the list sorted by the number after `INT`. The packaging job on Longleaf repeats both draws and must give the same sets.

| draw | key | seed | result |
|---|---|---|---|
| 10 slides of the 12 | `round6ext-slides` | 543059522 | `INT13`, `INT14`, `INT15`, `INT16`, `INT18`, `INT19`, `INT20`, `INT22`, `INT23`, `INT24` (left out, `INT17` and `INT21`) |
| 3 test slides of the 10 | `round6ext-split` | 4254856531 | `INT13`, `INT15`, `INT24` |

The 7 training slides are `INT14`, `INT16`, `INT18`, `INT19`, `INT20`, `INT22` and `INT23`.

## 4. What runs on the Mac, and why

By Nicolas's decision of 12 October (hard rule 7 in `CLAUDE.md`), the agent trials and the analysis run on the Mac, and the data preparation and the comparators run on Longleaf through Slurm.

| what runs locally | why |
|---|---|
| the two slide draws of section 3, a few lines of numpy | they must be in this plan before anything is built, and the packaging job repeats them |
| the container image build, the filtering proxy, the probes of C4.1 and C4.2 | the trials' confinement lives on the Mac |
| the trial-directory builder, the harness, the scorer, the scanner and their tests (C4.5) | they serve the trials |
| every trial, writer revision and checker audit (C5, C6), each a separate headless Claude Code process in its own confinement | Nicolas's decision |
| scoring and analysis (C5, C7) | Nicolas's decision |

## 4-bis. Change of 12 October, evening. Data preparation and comparators move to the Mac

Job 4674826 waited in the Longleaf queue for about four hours behind 824 jobs of higher priority, with the account's fair share at 0.013. Nicolas then wrote in chat, "just rsync the data to my disk what are we even waiting for longleaf for". By that decision C4.3 and C4.4 run on the Mac, which changes hard rule 7's split for this track. The job was cancelled before it started.

| what now runs locally | why |
|---|---|
| a copy by `rsync` from the project tree on Longleaf to `~/hest-1k/r6ext_private/tree/`, about 10 GB. The patch files of the 10 slides, the count files and both encoders' embeddings of all 24 slides, the splits, the gene list and HEST's metadata table | Nicolas's decision. The 24 slides are needed for the anchor, whose split uses slides outside the 10 |
| the packaging script, unchanged, in the container | Nicolas's decision |
| the anchor and the comparators, unchanged, in the container | Nicolas's decision |

The copy sits in the private folder, which no trial can see and which never enters either repository. Nothing on Longleaf is changed. The container's harness environment gains `h5py`, `anndata` and `scanpy` for these two steps, in `/opt/harness`, which no trial's confinement binds, so a trial's Python is unchanged. scikit-learn is 1.9.1 on both machines. The raw patch files are deleted from the Mac once the package's md5s are recorded, since the disk has under 20 GB free and they remain on Longleaf.

## 4a. Progress

- [x] Clone, branch and this plan (12 October).
- [x] Section 11 of the instruction, Nicolas's part, checked on 12 October (G1 to G3).
- [x] C4.1 child sessions (12 October, section 4b).
- [x] C4.2 isolation, I1 to I4 (12 October, section 4c). The canaries were removed after I4 passed.
- [x] C4.3 the data package, on the Mac (12 October, sections 4-bis and 4e). Jobs 4674823 (mistyped commit hash) and 4674826 (four hours in the queue) were both cancelled before they started.
- [x] C4.4 the anchor and the comparators, on the Mac (12 October, section 4e).
- [x] C4.5 harness and scorer tests (12 October, section 4e).
- [x] C5 pilot and report (13 October). The baseline, the writer at 4,096 bytes with one audit and no revision, and its predictor ran without a failure. The report is `docs/round06/i04/cheatsheet/round06_cheatsheet_C5_report.md`. Tag `round6-cheatsheet-C5`. The session stops here until the C5 decision memo arrives.
- [ ] C6 and C7, after the memo.

## 4b. C4.1, child sessions on the Mac

Evidence in `results/round6/cheatsheet_ext/C4_children/children.json`.

- **Image.** `r6ext:1`, built from `code/scripts/round6_cheatsheet_ext.Dockerfile` on `node:22-trixie-slim`. Claude Code 2.1.295 in the image and on the Mac, bubblewrap 0.12.0, socat 1.8.0.3, Python 3.13.5 with numpy 2.5.3, pandas 3.0.5, scipy 1.18.1, Pillow 12.3.0, scikit-image 0.26.0 and scikit-learn 1.9.1, the versions round 6's trials saw. The harness's own pyarrow sits in `/opt/harness`, which no trial's confinement binds. `curl` is not in the image.
- **Container.** Started by `code/scripts/round6_cheatsheet_ext_container.sh`. It runs as the unprivileged user `node` with every capability dropped. It needs `seccomp=unconfined` and `apparmor=unconfined` for bubblewrap's user namespaces, and `systempaths=unconfined` so that bubblewrap can mount a fresh `/proc`. Neither `--privileged` nor `SYS_ADMIN` is needed, which is narrower than either form the instruction names.
- **Authentication.** A confined child given only `CLAUDE_CODE_OAUTH_TOKEN` from the token file authenticated. Its `system/init` event reports `apiKeySource` as `none`, so no API key is in play and usage goes to the account that made the token. Whether the usage shows on Nicolas's account can only be seen from his side, and the C5 report asks him to confirm it.
- **Model and effort.** `--model claude-opus-5-5` was accepted and served as `claude-opus-5-5`. `--effort medium` and `CLAUDE_CODE_EFFORT_LEVEL=medium` were accepted. The stream does not echo the effort level, so it is confirmed only as accepted.
- **Flags.** Every flag of 6.5 was accepted as written. `--disable-slash-commands` is added, as in round 6 (its flag F11), and the skills list is then empty. The three built-in plugins `cc-plugin-agents-md`, `cc-plugin-telemetry` and `cc-plugin-plugin-authoring` remain listed, as in round 6.
- **`env -i`.** The child gets exactly six variables (`PATH`, `HOME`, `HTTPS_PROXY`, `https_proxy`, `CLAUDE_CODE_EFFORT_LEVEL`, `CLAUDE_CODE_OAUTH_TOKEN`). They are given as the process environment of `bwrap` and not on an `env -i` command line, so the token does not appear in a process listing in the container. The effect is that of `env -i`.
- **What is not bound.** `/opt`, `/lib64`, a certificate bundle and a credential folder are not bound. Node, Claude Code and Python sit under `/usr`. The filter tunnels TLS unchanged and the API's certificate verifies against Node's own store, so no certificate variable is set.
- **The filter.** `code/scripts/round6_cheatsheet_ext_filter_proxy.py` is round 6's proxy with a `--direct` mode that opens the connection to the allowed host itself. The allow list is `api.anthropic.com:443` only. Its Unix socket lives in the container's own `/srv/r6_proxy`, not on a folder mounted from the Mac.
- **Resume.** A session told to remember a word was resumed with `--resume` in the same trial directory under the same confinement, kept its session ID, and gave the word back.

## 4c. C4.2, isolation

Evidence in `results/round6/cheatsheet_ext/C4_isolation/`. The probes ran on Opus 5.5 at medium effort, beside a holder session in another trial directory.

- **I1.** The `system/init` events list the six allowed tools, no MCP servers, no skills and no slash commands (`probes.csv`). The probe quoted Claude Code's own system prompt, an attribution reminder and an environment block, and nothing from the repository, Nicolas's settings, memory or skills (`probe_reports/I1_93cfea05_report.txt`).
- **I2.** Five canaries were planted. They sit in the clone, in the private folder, in Nicolas's home directory on the Mac, in the container user's home and in the holder's trial directory. The probe was given each path as the container sees it and as the Mac sees it, tried Read, Glob, Grep and Bash, and went through `/proc/<pid>/root`, `cwd`, `environ`, `cmdline` and `fd`. It read none of them, and no canary string is in any report or transcript (`canary_hits.csv` is empty).
- **I3.** Requests to `huggingface.co`, `github.com` and `pypi.org` through the proxy were refused with 403, and without the proxy there is no name resolution and no route. A scan of every localhost port found only the proxy's own port (`probe_reports/I3_a947fba6_report.txt`). The filter's log for the probes shows three refused requests to each of the three hosts, twelve to a telemetry host, and allowed requests to the API host only (`filter_log_summary.csv`).
- **The scanner on the probes.** `transcript_scan_hits.csv` shows that the scanner finds the token's value in the I2 transcript, which the probe read from its own environment as instructed, and the Mac paths the probe's prompt named. Both are what a real leak would look like, so the scanner is shown to detect them.

Two things the probes showed that are recorded and not fixed.

- A trial can read `bwrap`'s own command line in `/proc/1/cmdline`. It holds the trial's own path under `/trials` and the proxy folder's name, and nothing about the task or the data.
- The I3 probe's instruction names `curl`, which the image does not have, so the fetches were made with Python only.

## 4e. C4.3 to C4.5, what the files show

- **Package** (`results/round6/cheatsheet_ext/C4_package/`). 78 files, every md5 equal to its manifest entry. The two draws are those of section 3 (`draws.json`). Every one of the 10 slides has as many patched spots as the inventory's spots under tissue (`package_summary.json`).
- **FFPE.** The inventory and HEST's own table give the same `subseries` strings, 12 of them `ccRCC tumor ffpe_*`, from 12 distinct patients (`ffpe_check.csv`). HEST's `preservation_method` column is empty for all 24 slides, so the subseries string is the only evidence of preservation in either table.
- **Target.** Counts are integers, and the target equals scanpy's `log1p` to within 3e-7 on every slide, so it is the natural log of one plus the count and the prompts' phrase stands.
- **Pixels and frame.** The patch files' `patch_size` is 245 full-resolution pixels for 112 micrometres (244 on `INT18`), so a 224-pixel patch is at 0.5 micrometres per pixel. The stored coordinates were transposed on all 10 slides, as round 6's flag F16 found on its slides, and are corrected in the package. On `INT18` the overlap check had only 3 and 4 usable pairs, so its mosaic was also looked at, and it shows continuous tissue.
- **Representativeness** (`representativeness.csv`). Nine slides fail on 0 to 3 of 50 genes. `INT24`, a test slide, fails on 9, which is over the limit of 5. Its sample is kept and this is an escalation for the C5 report.
- **I4** (`C4_blinding/i4_tree_scan.csv`). One trial directory of each of the five kinds, built from the real package, has no blinded name in any path, text file or PNG metadata.
- **Anchor** (`C4_comparators/tables/anchor.csv`). The head on round 1's split 0 gives 0.2205 for `uni_v2` and 0.2377 for `virchow2`, against round 1's 0.2205 and 0.2378. Both are within 0.01.
- **Comparators** (`C4_comparators/tables/comparators.csv`). On the 1,500 scored spots the `uni_v2` head fitted on the 3,500 writer spots has mean within-slide Pearson 0.184, and 0.221 when fitted on all 31,075 patched spots of the training slides. The `virchow2` head has 0.126 and 0.180. The codebook runs from -0.041 at 256 bytes to 0.151 at 16,384 bytes. No gene is constant in the measurements on any test slide.
- **Scorer tests** (`C4_tests/score_test_real.json`). All five pass on the real test-slide values.
- **Mechanical check on round 6's nine cheatsheets** (`C4_tests/check_cheatsheet_on_round6.csv`). Seven are flagged, among them every one with a code or table flag. The two not flagged are 3,816 and 6,990 bytes.

## 4d. Readings of the instruction made while building, for the C5 report

- **R1.** 6.4 says a mechanical flag is "an input to the checker". 6.2 gives the checker three files and 6.3 fixes its prompt, and neither carries the mechanical report. The harness keeps the mechanical report beside the verdict and does not show it to the checker.
- **R2.** A verdict passes if and only if its list of violations is empty, as the checker's prompt says. A `pass` key that disagrees is recorded in the manifest.
- **R3.** A session that stops at its turn cap with a valid output file is used, and its stop reason is recorded. Only a missing or invalid file makes a session fail.
- **R4.** If a resumed revision fails, the previous version is put back and the last verdict's violations are sent again in the second revision, without a new audit of an unchanged file.
- **R5.** Positions in `spots.csv` are the spot's centre in pixels at 0.5 micrometres per pixel, measured from the top-left corner of that patient's overview image. Expression is written to 4 decimals.
- **R6.** Scored patches are numbered `p0001` to `p1500` across the three folders, so a spot ID in `predictions.csv` is unambiguous.
- **R7.** Test patients' folders and patches are ordered with the keys `round6ext-patientorder-<trial_id>-test` and `round6ext-spotorder-<trial_id>-test`, so that a combined session's two halves use different draws.
- **R8.** Strata. k-means is scikit-learn's `KMeans` with 8 clusters and `n_init=10`, on rows sorted by barcode. Clusters are numbered by their smallest barcode. A cluster's floor is 10, or its size if smaller. Ties in the largest remainder go to the cluster numbered first. One generator per slide draws from the clusters in order.
- **R10.** In the transcript scan a sample ID or barcode must stand apart from letters, digits and the base64 characters, because viewed images sit in a transcript as base64 and matched by chance in the pilot.
- **R9.** The transcript scan does not treat the uppercase task code or "patient" followed by a number as blinded names, since an agent told the tissue type may write either by itself. The scan of trial directories before a session starts does refuse both.

---

*What follows is the instruction's sections 6, 7 and 8, copied unchanged and under their own numbers.*

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
