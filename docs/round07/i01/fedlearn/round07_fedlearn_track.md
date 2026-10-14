# Round 7, the federated learning track, instruction

13 October 2026. Prepared by the oversight chat for a fresh Claude Science session. This document is self-contained. The track starts from `main` of `NicWYZ/HEST-1k-replication` at the commit that carries the first version of this document, on its own branch `round7-fedlearn`. Record that commit's hash in your plan. Read this document fully, then transcribe section 7 into `docs/round07/tracks/fedlearn/round07_fedlearn_plan.md` before running anything.

This instruction stays living on `main` while the track runs. The oversight chat revises it in place and adds a dated line below. When Nicolas tells you to check for updates, fetch `main`, read the revisions, and transcribe any change into your plan.

**Revisions**
- 13 October 2026. First version.
- 13 October 2026, before handover. Revised after an independent check. The federated and pooled fits are compared with an exact head, the inventory job uses delivered code, full texts have a folder outside the clone, there is one list of papers, and the entry gate, the needs, the exit items of F4 and several paths were added.
- 13 October 2026, evening. Round 7's inference track now runs at the same time on branch `round7-ppi`, with its own areas, and both tracks use the same Slurm accounts. Section 4 gains the rule that only the lead cancels a job, after checking that it is this track's own.
- 13 October 2026, F2 gate. The session had not fetched the evening revision, so the F2 decision memo carries it in full (section 2 of `docs/round07/i02/fedlearn/round07_fedlearn_F2_decisions.md`). Interval i02 is fixed by that memo, which adds V3 and V4.

---

## 1. Your role and the people

You are the execution agent. A separate chat session, the oversight chat, reviews your reports, makes scope decisions and writes decision memos, which Nicolas hands to you or tells you to fetch from `main`. Nicolas Weiyang Zhang (Longleaf ONYEN `weiyang`, Slurm accounts `rc_htzhu_pi` and `rc_tengfei_pi`) is the first-year biostatistics PhD student whose project this is. He reads every command before it runs and will ask why. His advisors are Dr. Hongtu Zhu and Dr. Daiwei (David) Zhang at UNC.

Your responsibilities are a literature review of the viability of federated learning for predicting gene expression from histology, carried out with sub-agents, a read-only inventory of the data the project already holds, a proposal for quick scoping experiments, and, after the first gate, those experiments on Longleaf. You verify every output before moving on, write reports in the format of section 10, commit on your branch, and stop at each gate. You do not make scope decisions. Anything this document does not cover is reported as a proposal, not done.

**The gate rule, in the wording Nicolas approved.** Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. Contact with anyone outside the project is never the session's decision.

This track's gates are F2 and F4. Inside an interval you message Nicolas for three things only. You send the list of papers you could not retrieve (section 8), which is a request for inputs and does not pause the work. You send the standing four-hour queue notice of section 4. And you tell him of a setup problem in F0 that only he can clear, such as a clone that is not clean. The stop conditions of section 11 are the only exceptions to "no interim stop conditions", as they were in round 5, and a stop produces a report in the format of section 10.

**How Nicolas wants things written.** Plain, natural prose. No em-dashes. No colon-then-explanation constructions. No compressed or clever phrasing. Math as LaTeX, with each `$$` on a line of its own. Numbers quoted at the precision the comparison needs, with the relative scale stated. Full precision stays in the files. Every number in a report is read back from the file named beside it. A derivation shows every expression and skips only algebra, and says where a step of algebra is skipped. Do not inflate length.

---

## 2. What this track is for

### 2.1 Where it comes from

At the advisor meeting of 12 October (`docs/round07/00_prep/round07_advisor_directions.md`), David explained that the current way of predicting expression from H&E, in which a pathology foundation model turns image patches into embeddings and a prediction head is fitted on them, has reached a bottleneck in accuracy. He proposed that writer agents record relationships between histology and expression over many training pairs, building a textual knowledge base that predictor agents draw on, as a scaled-up version of round 6's cheatsheets. Dr. Zhu objected that text loses information, and proposed federated learning instead, gathering training information as summary statistics at scale from centers around the world, so that models improve without collecting more explicit training data such as HEST-1k.

Nicolas's assignment is a literature review of the viability of federated learning for this problem. The end goal is a methods paper that proposes a federated method and argues for adopting it and for further research in this direction. The paper is meant to be preliminary and a proof of concept, not a technically complex methodology paper. This track is its first round, a literature review with quick validation and scoping experiments. It is separate from the project's PPI paper and uses none of its tracks' areas.

### 2.2 The questions the review answers

Each question gets an answer, the evidence behind it, and a grade for that evidence. The grades are **strong** (several independent studies on this problem or one very close to it), **moderate** (one study on this problem, or several on a close neighbour), **weak** (only adjacent problems, or one small study) and **none found** (with the search that found nothing named).

- **Q1. Is accuracy limited by data?** Is the accuracy of predicting expression from histology limited by the amount and diversity of paired training data, so that more data from more centers would raise it, or by the representation, the platform and the biology, so that it would not? Look for learning curves in training patients, slides or sites, scaling studies of foundation models and of heads, and cross-cohort transfer.
- **Q2. What data do centers hold?** Paired H&E and spatial transcriptomics is rare everywhere. H&E with bulk RNA-seq from clinical or research sequencing is far more common, and H&E alone is abundant. Which of these could a federation use, how much exists, and how would each enter a model (a supervised head, weak supervision from bulk, self-supervised pretraining)?
- **Q3. What would be federated?** There are at least four routes. One is a prediction head on frozen embeddings, fitted from summary statistics in one round of communication. Another is a nonlinear head trained iteratively. A third is parameter-efficient fine-tuning of the encoder, and a fourth is federated pretraining of the encoder on unlabelled slides. For each, the review says what leaves a site, the compute a site needs, the rounds of communication, and the evidence that it works.
- **Q4. Heterogeneity across centers.** Sites differ in platform and gene panel (Visium, Visium HD, Xenium and others), in stain and scanner, in their mix of organ and disease, and by offsets at the level of the center or the slide. Which federated methods handle non-identical data, personalisation, partial overlap of the measured genes, and batch effects, and how well?
- **Q5. Privacy and governance.** What in H&E images, expression profiles and their summary statistics is identifying, which attacks on shared statistics or gradients are documented, what differential privacy costs in accuracy, and what consortia have done in practice (data-use agreements, multi-site federations in medical imaging, analysis that runs at the data's home site).
- **Q6. Prior art.** What has already been done on federated prediction of expression from histology, and on federated learning in single-cell and spatial omics. This answer is the novelty check that hard rule 8 requires before the paper claims anything is new.
- **Q7. Statistical methods that suit a biostatistics methods paper.** The candidates are one-shot and communication-efficient distributed estimation, distributed regression from sufficient statistics, federated principal components, federated mixed and random-effects models, federated transfer learning, and inference with valid uncertainty in a federation.
- **Q8. The alternatives a paper advocating federated learning has to argue against.** This is a short section, as Nicolas decided on 13 October. It covers David's textual knowledge base and its relatives (agent-written knowledge bases, retrieval-augmented prediction), retrieval of reference spots in a joint image and expression embedding space, scaling public data centrally, and better or fine-tuned encoders. For each, the section gives what the route predicts and the evidence, with round 6's results as the project's own evidence on the textual route (`docs/round06/README.md`, "What the round established"). The review compares the routes on evidence. It does not take a side between the advisors.
- **Q9. How to show viability with public data.** Which public data can stand in for a federation (centers simulated from labs or studies in HEST-1k, tissue source sites in other public cohorts), how to evaluate (leave one center out, held-out donors within a center), and which metric, given that the project's metric removes slide-level offsets.

### 2.3 What the project already holds

- **The pipeline being federated.** HEST-bench's head is principal components of the patch embeddings followed by ridge regression, and round 1 reproduced it to a mean absolute difference of 0.0002 against the live leaderboard over 108 encoder and task cells (`README.md`, `results/summary/discrepancy_table.csv`). The project's metric since round 2 is the within-slide Pearson correlation, averaged over genes and test slides (`docs/round02/README.md`).
- **Summary statistics are exact for a ridge head fitted exactly.** Center $k$ holds $n_k$ spots with embeddings $X_k$ and expression $Y_k$. The pooled means $\bar x$ and $\bar y$, the pooled covariance of the embeddings and so its principal-component basis $V$ follow from $\sum_k n_k$, $\sum_k X_k^\top \mathbf{1}$, $\sum_k Y_k^\top \mathbf{1}$ and $\sum_k X_k^\top X_k$. With $N = \sum_k n_k$, the ridge fit on the centred scores is

$$
\hat B = \Big(V^\top \big(\textstyle\sum_k X_k^\top X_k - N\bar x \bar x^\top\big) V + \lambda I\Big)^{-1} V^\top \Big(\textstyle\sum_k X_k^\top Y_k - N \bar x \bar y^\top\Big),
$$

  which uses only those sums and $\sum_k X_k^\top Y_k$. Any standardisation the head applies comes from the same sums. So for this head, federating summary statistics loses nothing, provided the basis and the fit are computed exactly. The head as round 1 replicated it is not exact in this sense. It uses an iterative `lsqr` ridge solver that is not the ridge solution to any tight tolerance (`README.md`, known limitation 9), and its principal-component step may use a randomised solver. So the exact comparison uses a float64 eigendecomposition and a Cholesky solve, and the faithful head is anchored separately (F3.0). Whether more data from more centers raises accuracy at all is Q1.
- **Slide-level error is large.** Round 3 measured slide offsets of about half a standard deviation (`docs/round04/00_prep/round4_originality_check.md`, section 2). Rounds 4 and 5 showed that what predictions buy under cluster sampling is governed by their accuracy at the cluster level (`docs/round04/tracks/ppi/round4_ppi_theory.md`, section 2, and `docs/round05/i04/ppi/round5_ppi_E5_decisions.md`, section 3). In a federation, centers play the role of clusters.
- **HEST-1k has no laboratory contrast with disease held fixed.** Checked across all 46 organ and technology cells in round 3 (`docs/reference/methods_and_state_of_play.md`, sections 23 and 24). Any center simulated from HEST-1k labs mixes lab with study, disease and often protocol. Q9 and the proposal of F2 have to deal with this.
- **Round 6 tested a small textual route.** No cheatsheet let Opus 5.5 beat the `uni_v2` head fitted on the same spots. On one unseen patient the best result was within one trial's noise of the head, and on three held-out kidney cancer patients every cheatsheet stayed below it (`docs/round06/README.md`, "What the round established").

### 2.4 Starting points from the oversight chat's scan

Two search agents of the oversight chat scanned the field on 13 October. This list is a starting point, not a result. Re-verify every item before it enters the evidence table, and do not stop searching where the scan stopped.

Seen on a fetched page or a PubMed record on 13 October.
- Federated prediction of expression from histology. Only one paper was found, PPML-Omics (Zhou et al., Science Advances 2024, 10(5):eadh8601), which trains ST-Net on breast spatial transcriptomics across simulated hospitals with differential privacy. privateST (Kim et al., Scientific Reports 2026) encrypts inference and is not federated learning. No paper was found that fits a head on a frozen pathology foundation model from per-center summary statistics, and none that handles differing gene panels across sites.
- Federated computational pathology. Lu et al., Medical Image Analysis 2022, 76:102298 (federated attention-based multiple-instance learning with differential privacy). Saldanha et al., Nature Medicine 2022, 28:1232-1239 (swarm learning across three sites). Adnan et al., Scientific Reports 2022, 12:1953. Hosseini et al., IEEE Transactions on Medical Imaging 2023, 42(7):1982-1995. Cong et al., npj Digital Medicine 2026, 9:578 (federated prompts on frozen features). Tsai et al., FedSDA, AAAI 2026 (stain alignment).
- Single-cell and omics. scFed (Wang et al., Briefings in Bioinformatics 2024, 25(1):bbad507), Federated Harmony (Yuan et al., PLoS Computational Biology 2025), SwarmMAP (Saldanha et al., npj Systems Biology and Applications 2026), fedRBE (Burankova et al., arXiv:2412.05894).
- Distributed statistics. Jordan, Lee and Yang, JASA 2019. Battey, Fan, Liu, Lu and Zhu, Annals of Statistics 2018. Dobriban and Sheng, Annals of Statistics 2021. Fan, Guo and Wang, JASA 2023. Gaye et al., DataSHIELD, International Journal of Epidemiology 2014. Grammenos et al., federated principal components, NeurIPS 2020.
- Accuracy and scale. Jaume et al., HEST-1k, NeurIPS 2024 Datasets and Benchmarks. Wang et al., Nature Communications 2025, 16:1544 (benchmark of expression prediction, weak transfer across studies). STPath (Huang et al., npj Digital Medicine 2025). STFlow (Huang et al., arXiv:2506.05361). HESCAPE (Gindra et al., arXiv:2508.01490). None of these was found to report a learning curve in training patients or sites.

From the oversight chat's memory, marked `[verify]`. FedAvg (McMahan et al., AISTATS 2017). The survey of open problems by Kairouz et al. (2021). FedProx (Li et al., MLSys 2020). SCAFFOLD (Karimireddy et al., ICML 2020). FedBN (Li et al., ICLR 2021). Swarm learning (Warnat-Herresthal et al., Nature 2021). Rieke et al. on federated learning in digital health (npj Digital Medicine 2020). The FeTS federation (Pati et al., Nature Communications 2022) and EXAM (Dayan et al., Nature Medicine 2021). One-shot distributed algorithms for multi-site health records (Duan and colleagues, JAMIA 2020) and federated transfer learning (Li, Cai and Duan, Annals of Applied Statistics 2023). ST-Net (He et al., Nature Biomedical Engineering 2020), HE2RNA (Schmauch et al., Nature Communications 2020) and BLEEP (Xie et al., NeurIPS 2023).

**Candidate method concepts, the oversight chat's starting points.** The review assesses each on evidence and may add or drop any.
- **C1. A one-shot federated head.** Centers send the sums of section 2.3, a shared principal component basis is formed from them, and the ridge head is fitted centrally, with center-specific intercepts and optional noise for differential privacy. The barrier for a center is low, with no GPU training and one message.
- **C2. Iterative federation of a nonlinear head or of adapters on the encoder.** It needs more compute at each center and many rounds of communication, and it is the form most of the federated learning literature studies.
- **C3. Weak supervision from H&E and bulk RNA-seq.** Uses the data centers actually hold in quantity, with spatial prediction learned from slide-level targets.
- **C4. A federated reference database.** Centers keep pairs of embedding and expression locally and answer nearest-neighbour queries in embedding space. It is a database, as David proposed, but not a textual one, so it relates directly to both advisors' views. Its privacy cost is the first question about it.

### 2.5 Scope

**In.** The literature, the read-only inventory and the proposal in interval 1. The scoping experiments that the F2 memo fixes, in interval 2. **Out.** Any experiment or pilot in interval 1, and any Slurm job there other than the three of F0 (making the code clone, delivering the first bundle, and the inventory job). Downloads of data, unless the F2 memo approves one that Nicolas has decided. Writing the paper. Choosing the paper's framing, venue or authorship. Anything in the PPI paper's areas.

---

## 3. Machines, data and assets

**Repository** at the starting commit. Everything under `results/` that exists at the starting commit is read only for you, and so is every existing script and document. `docs/WAYS_OF_WORKING.md` is the accumulated procedure. Read it before your first job.

**Longleaf** project tree `/work/users/w/e/weiyang/hest_replication`, on `main` at tag `round4-data-v2`. Read it with `git --no-optional-locks` and never check out, fetch or pull there. Never compute on the login node. The project's Python is `/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python` (Python 3.11.16, numpy 2.4.6, pandas 2.3.3, scipy 1.17.1), called by absolute path in every job script.

| asset | path | what it gives you |
|---|---|---|
| HEST-1k inventory | `results/round3/D0_inventory/hest_inventory.csv` (1,276 rows) | per sample, organ, technology, disease state, study, provisional lab (`lab_provisional`) and donor key, and whether it is in the benchmark |
| organ and technology table | `results/round3/D0_inventory/organ_technology_ranking.csv` | samples, labs and donors per organ and technology |
| round 4's download | `results/round4/data/P1_download/` | which samples were pulled to Longleaf in round 4 (sets `donor_labelled_v` and `lung_xenium`) |
| round 4's embeddings and tasks | `results/round4/data/P2_embeddings/`, `results/round4/data/P5_task/` | the lung task and its embeddings for `uni_v2`, `hoptimus0` and `resnet50` |
| round 3's extra embeddings | `results/round3/D2_embeddings/`, `results/round3/D4_expansion/` | embeddings for two sets beyond the benchmark, `institution_breast_xenium` (breast Xenium from several institutions, with different gene panels) and `kidney_visium_cell`, for the same three encoders |
| round 1's heads | `results/faithful/`, `results/tailored/` | the replicated HEST-bench heads, the anchor for any refit |
| round 4's prediction tables, Longleaf only | the parquets listed in `docs/round05/i01/ppi/round5_ppi_track.md`, section 3 | per spot outcome, prediction and donor for `CCRCC`, `INDIANA_KIDNEY` and `LUNG_XENIUM` |
| what the archive holds | `docs/reference/methods_and_state_of_play.md`, sections 21 to 24 | what has been used and what the rest of HEST-1k holds |

Where the embeddings of the `CCRCC` and `INDIANA_KIDNEY` tasks live on Longleaf is not recorded in this document. The inventory of F2 establishes which assets are on disk, for which samples and encoders. Do not assume any of them from this table.

---

## 4. Standing rules and conventions

**For the literature.**
- Never cite a paper you have not seen. Every entry in the evidence table carries an identifier you opened (DOI, PubMed ID, arXiv or bioRxiv ID, or a proceedings page), and its title, authors, year and venue are read from that page.
- Record the read level of every paper, **full text**, **abstract only** or **secondary** (known only from another paper's description). A claim in the review that rests on a paper read at abstract level says so.
- Quote at most a short phrase from any paper. Summaries are in your own words.
- Full texts and PDFs are never committed to the repository, which is public. The same holds for any figure taken from a paper.
- A search that finds nothing is a result. Record the query, the source and the date.
- No claim of novelty beyond what the search log supports. A novelty statement says "within the sources and queries in the search log".

**What counts as computation.** Searching, reading, writing documents, merging and checking the sub-agents' citation tables, and the numeric-claim sweep of your own documents before a handover are the session's own work, done in its clone as every earlier track did. Anything that reads data, including the inventory, is computation and runs on Longleaf.

**For computation.**
- Silent failure is the main risk. Verify each stage's output against an expected value before moving on. Every new computation has one arm anchored to a prior result.
- Never assert a number you have not read back from a file. Cite the path.
- Read the whole grid before writing a headline. Tabulate the quantity over every axis the experiment varied and check that the sentence holds in each cell it claims.
- When you explain a number, state the mechanism and name what in the files would contradict it, then check that.
- Before naming the effect of a comparison, list in writing every variable that differs between its arms.
- Write predictions down before running, and report them beside the outcomes. Do not quote a ratio whose denominator is within noise of zero.
- Longleaf is where work runs. Nothing runs on Nicolas's Mac unless he asks for that specific task in chat. Such a request is written into the plan as a numbered extension before the task runs, covers the work it names, and does not carry across a gate. A local run records the host, the library versions, the md5 of every script and input, and the command line in place of the Slurm fields.
- A job that has waited four hours is reported to Nicolas in chat with what it needs, and it keeps waiting. A pending job of this track's own may be switched between `rc_htzhu_pi` and `rc_tengfei_pi`. Only the lead cancels a Slurm job, and only after confirming with `squeue -u weiyang` and the track's job ledger, `results/round7/fedlearn/r7fl_slurm_jobs.csv`, that the job is this track's own. Round 7's inference track (branch `round7-ppi`, areas `results/round7/ppi/`, `code/scripts/round7_ppi_*.py`, `docs/round07/**/round07_ppi_*.md` and `.verify-exceptions-round7-ppi`) runs at the same time on the same accounts. A sub-agent never runs `scancel`, and you never write in the inference track's areas.
- Every output directory gets `PROVENANCE.txt` (job id, partition actually used, node, date, the commit of the snapshot the job ran from, command line, config hash with its config, `PYTHONHASHSEED`, md5 of every script that ran) and is stamped with `stamp_dir()` from the `longleaf-provenance` skill, written by the job on the node. Before reusing any output you did not create, run `whose()` on it, and if the verdict is `sibling` or `unstamped`, ask the oversight chat through the report.
- The submission route replaces `--job-name`, so jobs are identified by Slurm id. Record the intended prefix `r7fl_` and the stage in `PROVENANCE.txt`.
- Give every parquet an explicit `pa.schema`, write summaries before bulk tables, and take seeds from `zlib.crc32`, never from `hash()`.
- Take memory and time from a sibling job's `sacct`, and set Slurm time limits at about three times the expected runtime.
- Put a time cap on anything that is not analysis, and stop at the cap.

**For git and files.**
- Write commit messages through a file. Sub-agents run no git command. The lead is the only committer and checks every hand-back against its sources before commit. Each file has one writer, and parallel work writes fragments that a merge step joins, reporting any collisions.
- Before every commit, list the staged files and confirm that none is a paper's text, a PDF or a figure taken from a paper.
- Do not edit `README.md`, `CLAUDE.md`, `docs/README.md`, `docs/progress-log.md`, `docs/WAYS_OF_WORKING.md`, any earlier round's files, or anything outside the areas of section 5. Proposed edits go in the report.
- Run `code/scripts/verify_numeric_claims.py` over your documents before every handover, with your exceptions in `.verify-exceptions-round7-fedlearn`.
- After opening a pull request, confirm on GitHub that it exists and put its number in the report.

---

## 5. Working copies, code delivery and where to write

**Your areas.** Branch `round7-fedlearn`, from the starting commit, never rebased, never merged into `main` by you, and with nothing merged into it. Record the starting commit's hash in the plan. Scripts `code/scripts/round7_fedlearn_*.py`. Results `results/round7/fedlearn/<STAGE>/`. The numeric-claim exceptions file `.verify-exceptions-round7-fedlearn` at the repository root. Documents, with these exact names:

| document | path | kind |
|---|---|---|
| operating plan | `docs/round07/tracks/fedlearn/round07_fedlearn_plan.md` | living |
| the literature review | `docs/round07/tracks/fedlearn/round07_fedlearn_literature_review.md` | living, frozen at the round's close |
| F2 gate report | `docs/round07/i01/fedlearn/round07_fedlearn_F2_report.md` | frozen once handed over |
| F4 closing report | `docs/round07/i02/fedlearn/round07_fedlearn_final_report.md` | frozen once handed over |

Tags `round7-fedlearn-F2` and `round7-fedlearn-final`. Longleaf outputs under `results/round7/fedlearn/` in the project tree, stamped. When Nicolas hands you a decision memo, commit it unchanged at the path it names on your branch, so that it merges cleanly with the copy the oversight chat has put on `main`.

**Papers and full texts** live in `~/hest-1k/fedlearn_papers/` on the Mac, outside every clone, never in the repository. That holds for papers Nicolas uploads (save any he gives you in chat there) and for full texts you or a sub-agent fetch. Sub-agents' fragments hold citations and summaries only.

**Working copies.** Your clone on Nicolas's Mac is `~/hest-1k/HEST-1k-replication-fedlearn`, a new clone for this new track (section 12). Confirm the working tree is clean, fetch, and create `round7-fedlearn` from `origin/main` at the starting commit. If the tree is not clean or a `.git/index.lock` is present, tell Nicolas and wait. The other clones under `~/hest-1k` belong to other sessions. Do not run git in them. On Longleaf, the track's code clone is `/work/users/w/e/weiyang/hest_code/round7-fedlearn/`, made in F0 by a Slurm job that clones the repository over the SSH key on Longleaf and checks out `round7-fedlearn` at the starting commit, as round 5's tracks did. The project tree is never used as a code clone.

**Code delivery.** As the round-5 tracks did from their second interval (`docs/round05/i02/ppi/round5_ppi_E2_decisions.md`, section 4), for every job including the inventory job of F2. Commits reach the Longleaf clone as a git bundle applied by a short Slurm job with `git merge --ff-only`. The same job writes a read-only snapshot of the delivered commit's `code/` directory to `/work/users/w/e/weiyang/hest_code/round7-fedlearn_snapshots/<full commit hash>/`, and every job runs from its own output directory with that snapshot on `PYTHONPATH`. Each delivery is a row of `results/round7/fedlearn/code_deliveries.csv`. Bundles reach Longleaf, and results come back to the Mac clone, by copying over your Longleaf access (`scp` or `rsync`). Results are committed in the Mac clone. Before each gate push, run the two checks of that memo's item 6 (every recorded commit is an ancestor of the gate tag, and every recorded script md5 matches that commit) and keep `results/round7/fedlearn/provenance_index.csv`.

**Pull requests.** GitHub sees one push per gate. At each gate you commit, tag and push the branch and the tag together, open one pull request into `main`, and stop. You never merge. Nicolas merges with a merge commit after the oversight chat accepts the report. Do not push again while that pull request is open. Branches are never rebased, squashed, amended after a push or force-pushed. A rejected gate is fixed with new commits on the same open pull request.

---

## 6. Sub-agents

The review is done by you and your sub-agents. Dispatch one sub-agent per theme with a written brief, at most eight at once, so that the work stays within Nicolas's usage. Searching and screening sub-agents may run one model tier below yours. The citation audit of F2 runs at your own tier, by a fresh sub-agent that has not seen the drafting. The synthesis, the verdicts and every sentence of the review stay with you.

| theme | questions | what it covers |
|---|---|---|
| T1 | Q6 | federated or privacy-preserving prediction of expression from histology, federated learning in single-cell and spatial omics |
| T2 | Q3, Q5 | federated learning in computational pathology and medical imaging, large multi-site federations, federated fine-tuning and pretraining of foundation models |
| T3 | Q1, Q2 | evidence on data scale for histology-to-expression prediction, learning curves, scaling studies, cross-cohort transfer, what paired data exist and where |
| T4 | Q7 | distributed and federated statistical estimation from summary statistics, federated principal components, mixed models, transfer learning, inference |
| T5 | Q4 | non-identical data, personalisation, partial label or gene-panel overlap, stain and scanner shift, batch effects in federated settings |
| T6 | Q5 | attacks on shared statistics and gradients, differential privacy and its cost, governance in practice |
| T7 | Q8, Q9 | the alternatives (textual and agent-written knowledge bases, retrieval in joint embedding spaces, central scaling, encoder adaptation), and public data that can stand in for a federation |

Each brief carries the theme's questions, the relevant part of section 2.4, the query set from the plan, the rules of section 4 for the literature, the fragment format, and the sentence "Write only into your fragment directory, run no git command, and cite nothing you have not opened." Each sub-agent writes `results/round7/fedlearn/F1_search/fragments/<theme>/search_log.csv` (one row per query, with the date, the source, the query string, the number of hits and the number screened) and `evidence.csv` (one row per included paper, with the identifier, title, first author, year, venue, read level, the questions it serves, a two-sentence summary in its own words, and whether a free full text exists, with its URL). The lead merges the fragments into `search_log.csv` and `evidence_table.csv` in `F1_search/`, removes duplicates, and reports collisions.

---

## 7. The plan

Four stages and a closing stage. Gates at F2 and F4. Transcribe this section into the plan before running anything, and keep the plan's current-state block at its top so that a compacted or restarted session can resume from the plan alone.

### Interval i01

#### F0. Setup and the search protocol (two hours, capped at half a day)

**Entry gate for interval i01.** This document is on `main`, Nicolas has made the clone and the papers folder of section 12, and the session can reach Longleaf and at least one literature source.

1. Read this document, `docs/WAYS_OF_WORKING.md`, section 4 of `docs/round05/i02/ppi/round5_ppi_E2_decisions.md`, `docs/round07/00_prep/round07_advisor_directions.md`, `docs/round06/README.md` and sections 21 to 24 of `docs/reference/methods_and_state_of_play.md`.
2. Set up the clone and the branch (section 5), and transcribe section 7 into the plan with the starting commit's hash.
3. Check which literature sources you can reach and record the result in the plan. At least a general web search, PubMed, arXiv, bioRxiv and medRxiv, PubMed Central, and the proceedings pages of NeurIPS, ICML, ICLR, AISTATS, MICCAI, MIDL and AAAI. Record for each whether you can open landing pages and whether you can fetch full texts.
4. Write the search protocol into the plan. For each theme, the sources, the date range (2016 to the present for federated learning, earlier where a statistical foundation needs it), at least five query strings, the inclusion and exclusion criteria, and which papers count as core (those an answer to a question would rest on).
5. Make the Longleaf code clone (section 5), write `code/scripts/round7_fedlearn_f2_inventory.py` (F2 step 4), commit it, deliver it by bundle with a snapshot, and submit the inventory job, so that it queues and runs while F1 proceeds.

**Exit.** The plan with the protocol, committed on the branch and not pushed, the first row of `code_deliveries.csv`, and the inventory job submitted.

#### F1. Search, screening and extraction (one day, capped at a day and a half)

1. Dispatch the theme sub-agents of section 6.
2. As soon as the core papers are known, and no later than the middle of F1, list the core papers whose full text you cannot retrieve, choose at most 10 of them, and send the list to Nicolas as section 8 says. Continue with abstracts while you wait, and mark every claim that rests on an abstract.
3. Merge the fragments, remove duplicates, and re-verify the identifier, title, authors, year and venue of every core paper yourself.
4. Read the full text of every core paper you can retrieve, including those Nicolas uploads, and record the read level.

**Exit.** `results/round7/fedlearn/F1_search/search_log.csv`, `evidence_table.csv`, `paper_requests.md` (the list as sent, and what arrived), and the fragments, all committed.

#### F2. The review, the inventory and the proposal (one day, capped at a day and a half; gate)

1. **The literature review** in `docs/round07/tracks/fedlearn/round07_fedlearn_literature_review.md`. One section per question of section 2.2, each with its answer, its evidence and its grade, then a section on the candidate method concepts. Every citation has its identifier, and every claim resting on an abstract says so.
2. **The viability verdict.** For each route of Q3 and each candidate concept of section 2.4, one of **supported**, **conditional** (with the condition) or **not supported**, each with its reasons and the papers behind it.
3. **The novelty statement** for federated prediction of expression from histology, bounded by the search log.
4. **The inventory.** The job submitted in F0 runs `code/scripts/round7_fedlearn_f2_inventory.py` from the delivered snapshot. It lists the project tree, reads nothing but file names, sizes and the headers of expression and embedding files, joins the listing to the committed inventory table, and writes into its stamped output directory `results/round7/fedlearn/F2_inventory/` two tables. `inventory.csv` has one row per sample on disk, with organ, technology, lab, donor, task, the encoders with embeddings, and the number of spots and genes. `centers_by_group.csv` has one row per organ and technology, with the labs and donors on disk, and marks which could support a design with two or more centers.
5. **The proposal for interval 2,** as a section of the F2 report. Start from the defaults in F3, and revise them in light of the review and the inventory. For each experiment give the data, the design, the arms, the metric, your own predictions beside the oversight chat's, the compute estimate, and whether a download would be needed. A download is Nicolas's decision, so a design that needs one also comes with a version that does not.
6. **The citation audit.** A fresh sub-agent at your tier checks every paper cited in the review against its landing page (identifier, title, authors, year, venue) and checks that the claim attributed to it matches its abstract or full text. Fix what it finds and list it in the report.
7. **The F2 report** in `docs/round07/i01/fedlearn/round07_fedlearn_F2_report.md`, in the format of section 10, with the predictions F.1 to F.5 scored. Run the numeric-claim sweep, then commit, tag `round7-fedlearn-F2`, push, open the pull request, and stop.

**Exit items, each with its evidence.**
1. The search log covers every theme with at least the queries the protocol names, with counts per source (`search_log.csv`).
2. Every paper cited in the review has a verified identifier and a read level in `evidence_table.csv`, and the review cites nothing outside it.
3. The citation audit's table, with every mismatch fixed or listed (`results/round7/fedlearn/F2_audit/citation_audit.csv`).
4. The paper requests, what arrived, and which claims still rest on abstracts (`paper_requests.md`, and the report).
5. The review, the verdicts, the inventory and the proposal are written, and the sweep is clean or its exceptions are listed.
6. The inventory job's provenance passes both checks of section 5 (`provenance_index.csv`).

### Interval i02, opened by the F2 decision memo

What follows is the default. The F2 memo fixes the design, and nothing of it is set up, staged or piloted before the memo.

#### F3. Scoping experiments (two days)

**F3.0 Anchor** (outputs in `results/round7/fedlearn/F3_anchor/`). First, refit the faithful HEST-bench head (`pca_ridge`, as round 1 replicated it) for one encoder and one task on round 1's split, and match round 1's value within 0.001. Second, fit the exact head of section 2.3 (float64 eigendecomposition and Cholesky solve) once on the pooled data and once from the per-center sums, with the data split into the experiment's centers, and match the two sets of predictions to a relative difference below $10^{-8}$. Compare predictions rather than coefficients, since principal components are defined only up to sign. All later fits in F3 use the exact head. Both checks are acceptance checks, and a failure of either after one fix is a stop (section 11).

**V1. Is accuracy limited by data within what the project holds?** Outputs in `results/round7/fedlearn/F3_V1/`. On each task with at least 8 donors on disk (candidates are `CCRCC`, `INDIANA_KIDNEY` and `LUNG_XENIUM`) and each of the encoders with embeddings, hold out a fixed quarter of the donors, at least three, as the test set. Train the head on $n$ donors drawn from the rest, with $n$ on a doubling grid from 1 to the maximum, and 20 draws for each $n$. Donors `INT4` and `INT24` of `CCRCC` are treated as one donor, as in the task `CCRCC_merged`, since the two may be one person. Report the project's metric on the test donors, and the pooled Pearson correlation over all test spots beside it, with the spread over draws.

**V2. A simulated federation.** Outputs in `results/round7/fedlearn/F3_V2/`. Centers are formed in two ways. (a) By lab, wherever an organ and technology has two or more labs on disk, with the caveat of section 2.3 that lab is mixed with study and disease. (b) As a control without lab differences, random partitions of one lab's donors into $K = 3$ pseudo-centers. The arms are a local head trained on one center alone, the federated head from summary statistics (equal to the pooled head), and the federated head with a center-specific intercept. Scoring is leave one center out, and held-out donors within each center. A center left out has no intercept of its own and gets the mean of the other centers' intercepts, weighted by their numbers of spots.

**V3, only if the F2 memo adds it.** The accuracy cost of noise for differential privacy added to each center's sums, with outputs in `results/round7/fedlearn/F3_V3/`.

#### F4. The closing report (half a day; gate, end of track)

`docs/round07/i02/fedlearn/round07_fedlearn_final_report.md`, with the predictions F.6 to F.10 scored, the viability verdict of F2 revised in light of the experiments, a recommendation for the proof-of-concept paper's method and data, and what is not established. It ends with a closing page "What the federated learning track established". Update the literature review with anything read since F2, then commit, tag `round7-fedlearn-final`, push, open the pull request, and stop.

**Exit items, each with its evidence.**
1. Both F3.0 anchors pass (`F3_anchor/`).
2. Every experiment the F2 memo fixed has run in full, or the report says which cells did not and why (each experiment's results directory).
3. Every prediction of the memo is scored in a table beside its outcome (the report, section 5).
4. Every number in the report is read back from a file named beside it, and the sweep is clean or its exceptions are listed.
5. The provenance index passes both checks of section 5 for every job of the track (`provenance_index.csv`).

---

## 8. Papers you cannot retrieve

Nicolas asked for this on 13 October. When you cannot retrieve a core paper's full text, add it to a list for him. The list has at most 10 papers, chosen by how much of the review rests on them, and goes to him once, in chat, during F1. It is recorded in `paper_requests.md`.

For each paper give its number, the citation (authors, year, title, venue), one line on which question it serves and why the abstract is not enough, and its access link by the following rule.
- When the paper has a DOI at a subscription publisher, give the link through UNC Chapel Hill's library proxy, `https://login.libproxy.lib.unc.edu/login?url=https://doi.org/<DOI>`.
- When UNC's institutional access is not available for it (no DOI, a publisher UNC does not subscribe to, or a proceedings page without a subscription route), give the link to a free version instead, such as PubMed Central, arXiv, bioRxiv, medRxiv, the authors' own copy or an institutional repository.
- When you are not sure which applies, give both, the UNC link first.

Nicolas uploads the papers into your chat or puts them in `~/hest-1k/fedlearn_papers/`, outside every clone. Save any he gives you in chat into that folder. Never commit them. If a paper does not arrive, the review says which claims rest on its abstract.

---

## 9. Predictions

These are the oversight chat's, written before any search or run. Copy them into the plan and score each as held, partly held, refuted or not tested in the report of its gate. In earlier rounds most of the oversight chat's magnitude predictions were refuted, so a refuted prediction is an ordinary outcome and is reported as plainly as a held one.

Scored at F2.
- **F.1** Within the sources searched, at most three papers federate the prediction of expression, spatial or bulk, from histology, and none fits a prediction head on a frozen pathology foundation model from per-center summary statistics.
- **F.2** No paper reports a learning curve of spot-level expression-prediction accuracy against the number of training patients or centers for heads on frozen foundation-model embeddings.
- **F.3** At least two federated computational pathology studies report federated performance within 0.02 of pooled training on their own metric (for example AUC) for classification tasks.
- **F.4** No federated method is found that handles centers measuring different gene panels in expression prediction.
- **F.5** The inventory finds at least two and at most three organ and technology groups on disk with slides from two or more labs, enough for a leave-one-lab-out design without a download.

Scored at F4, for the default design. The F2 memo may restate them for the design it fixes.
- **F.6** On every V1 task and encoder, the project's metric rises more from 1 to 4 training donors than from 4 donors to the largest training size.
- **F.7** On `CCRCC` with `uni_v2`, the project's metric at the largest training size is within 0.02 of its value at half that size.
- **F.8** Leave-one-lab-out accuracy is below the accuracy on held-out donors within the lab, in every organ and technology group and for every encoder where V2(a) runs.
- **F.9** Adding another lab's slides to a lab's own training data changes that lab's accuracy on its held-out donors by less than 0.02 in either direction.
- **F.10** On held-out donors within centers, the center-specific intercept changes the project's metric by less than 0.005, since the intercepts cancel in a within-slide correlation and only their effect on the fitted slopes remains, and it raises the pooled Pearson correlation over those donors' spots.

---

## 10. Reporting format

After each gate, in this order. 1. Stage and status. 2. What was run, with the sub-agents and their briefs, the sources reached, and for computation the scripts with md5s, commits, job ids, partitions, wall times and peak memory from `sacct`. 3. Acceptance checks and exit items with the actual numbers and file paths. 4. For every comparison, the variables that differ between its arms, written out. 5. Predictions against outcomes, as a table. 6. Results, numbers from files with paths, dispersion beside every mean, and paths in place of pasted tables over 20 rows. 7. Discrepancies, open questions and escalations. 8. What was not checked. 9. Proposed next step.

Keep prose plain, as section 1 asks.

---

## 11. Decision boundaries

**You decide alone.** The sub-agent structure within section 6, extra query strings and sources, which papers count as core, which papers to read in full, the structure of the review within section 7, and seeds and job sizing in interval 2.

**Record as an escalation and continue.** A core paper you cannot retrieve that is not on the list. A theme with no relevant literature. An item of section 2.4 that does not exist or differs from its description. A source that cannot be reached. The inventory showing that a default experiment cannot run on the data on disk (propose the nearest design that can). Any acceptance check of interval 2 failing at a tolerance the dtype supports (fix, rerun, say so). Any new property of the data.

**Stop and report.** No literature source reachable at all. The F3.0 anchor or the equality of the federated and pooled fits failing after one fix.

**Never the session's decision.** Contact with anyone outside the project, including authors, to ask for papers, code or data. Any download of data. Any Slurm job in interval 1 other than the three of F0. Committing a paper, a PDF or a figure taken from one. A claim of novelty beyond the search log. The paper's framing, venue or authorship, and any choice between the advisors' views. Changes to `main` or to any area outside section 5. Any local run that Nicolas has not asked for in chat.

---

## 12. Needs, and what Nicolas does before starting

**The session needs** web search and page fetching, PubMed, access to the Mac clone and to `~/hest-1k/fedlearn_papers/`, Longleaf by the route the round-5 tracks used (with the SSH key on Longleaf for GitHub), the project's Python environment, and the `longleaf-provenance` skill.

**Nicolas does**

1. Merges nothing new. The track starts from `main` at the commit that carries the first version of this document.
2. Makes the track's clone on the Mac, `git clone https://github.com/NicWYZ/HEST-1k-replication.git ~/hest-1k/HEST-1k-replication-fedlearn`, and creates `~/hest-1k/fedlearn_papers/` for uploaded papers.
3. Starts a fresh Claude Science session with access to that clone and to Longleaf by the route the round-5 tracks used, and gives it this message. "You are the execution session of round 7's federated learning track. Read `docs/round07/i01/fedlearn/round07_fedlearn_track.md` on `main` of `NicWYZ/HEST-1k-replication` in full and follow it. Your clone is `~/hest-1k/HEST-1k-replication-fedlearn`. Start with F0."
4. Watches for the list of papers during F1 and uploads what he can.
