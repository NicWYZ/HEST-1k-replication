# Round 7, the federated learning track, operating plan

Living document of the execution session. Started 13 October 2026. The instruction is `docs/round07/i01/fedlearn/round07_fedlearn_track.md` on `main`.

## Current state

- **Stage.** F0, setup and the search protocol, in progress.
- **Branch.** `round7-fedlearn` in `~/hest-1k/HEST-1k-replication-fedlearn`, created from the starting commit. Not pushed.
- **Starting commit.** `3c328ccc4d68b44d0795cfb9c91ff332c3b399d3`. It is the only commit on `main` that touches the instruction, so it carries both revision lines of 13 October. `main` was at `b84187b65b61365e1348ba2d5c98b43c606f27e1` when the branch was made, one commit later, and that commit changes only `CLAUDE.md`.
- **Longleaf.** Reached on 13 October from `longleaf-login4`. The project tree is on `main` at `9d7277dc8c4bfade08d5895051666ee134b8396a` (tag `round4-data-v2`), read with `git --no-optional-locks`. `results/round7/` does not exist there yet. The project's environment has `h5py`, `anndata`, `pyarrow` and `zarr`.
- **Code clone on Longleaf.** Job 1 submitted 13 October as Slurm 4803248, pending at the time of writing.
- **Jobs.** See the job ledger. Job 1 was moved while pending from `rc_htzhu_pi` to `rc_tengfei_pi` with `scontrol update`, as section 4 allows.
- **F1.** The seven theme sub-agents T1 to T7 were dispatched on 13 October while the F0 jobs queue, since the instruction has the inventory job run while F1 proceeds and there is no gate between F0 and F1. Their frame ids are in the sub-agent table below.
- **Last delivered commit.** None.
- **Papers folder.** `~/hest-1k/fedlearn_papers/` exists and is empty. The session has read and write access to it.
- **F1 progress.** All seven theme fragments returned (488 rows, merged into 404 papers in `results/round7/fedlearn/F1_search/evidence_table.csv`, 695 search-log rows). The lead chose 84 core papers and re-verified each record against Crossref, PubMed, Europe PMC, arXiv or a proceedings page. Five core papers without an open full text were sent to Nicolas on 13 October (`paper_requests.md`). Three reader sub-agents are reading the 22 core papers that were at abstract level and have open copies.
- **Read level.** In this track "full text" means the full text was opened and its methods, results and discussion were read where they bear on the questions, not every line. Several fragments used the same definition. Where only a preprint version was read, the row says so.
- **Next action.** Submit job 2 when job 1 has finished and been checked, then job 3. Fold the readers' notes into the evidence table and commit F1.

## Extensions

None. A local run that Nicolas asks for in chat is written here as a numbered extension before it runs.

## Escalations recorded so far

None yet beyond the source notes of the next section, which are recorded under decision boundaries as sources that cannot be reached.

## Literature sources reached (F0 step 3, 13 October 2026)

Checked from the session's sandbox with one request to each source. "Landing pages" means the record page or an API record with title, authors, year and venue. "Full texts" means an open full text could be fetched.

| source | landing pages | full texts | how checked, and notes |
|---|---|---|---|
| General web search | yes | not applicable | the session's web search tool returned AAAI, arXiv and institutional pages for a test query |
| PubMed | yes | not applicable | E-utilities `esearch` returned JSON, and a PubMed record page opened |
| PubMed Central | yes | yes | an open-access article page opened in full |
| Europe PMC | yes | yes, for its open-access set | REST search returned JSON |
| arXiv | yes | yes | the API, an abstract page and a PDF opened |
| bioRxiv | yes | yes | the API and an article page opened |
| medRxiv | yes | yes | the API opened (same service as bioRxiv) |
| Crossref | yes | not applicable | a DOI record opened. Used to read title, authors, year and venue where a publisher page is blocked |
| Unpaywall, through the session's DOI full-text fetcher | yes | yes, where an open copy exists | the fetcher found a legal free copy of PPML-Omics (a bioRxiv PDF) |
| NeurIPS proceedings | yes | yes | network access granted by Nicolas on 13 October, index page opened |
| PMLR (ICML, AISTATS, MIDL from 2023) | yes | yes | access granted 13 October, the FedAvg page and its PDF opened |
| OpenReview (ICLR, MIDL) | yes | no | access granted 13 October, a forum page opened, the PDF link returned 403 |
| MICCAI open-access papers site | yes | not tested | access granted 13 October, the 2024 index opened |
| AAAI proceedings (ojs.aaai.org) | through web search only | through web search and arXiv | access granted 13 October, but the server closes direct connections from the sandbox. AAAI pages and PDFs are seen through the web search tool, and arXiv versions are used where they exist |
| nature.com (Nature journals, npj, Scientific Reports) | yes | yes, for open-access articles | access to `www.nature.com` and its sign-in redirect `idp.nature.com` granted 13 October |
| Other publisher sites (science.org, ScienceDirect, Oxford Academic, PLOS, IEEE Xplore, Taylor and Francis, Project Euclid, Springer) | no | no | blocked by the sandbox's allowlist. Not requested, because Crossref, PubMed and Europe PMC give the bibliographic record and PMC or a preprint server usually gives an open copy. A paper whose full text exists only behind one of these sites goes to the list of section 8 of the instruction |
| Semantic Scholar API | rate limited | not applicable | returned 429 without a key. Not relied on |

So at least one source of every kind the instruction names was reached, and no stop condition applies. The verification rule that follows from the table is this. An evidence row's identifier is opened at the publisher's page where that page is reachable, and otherwise at its PubMed, Europe PMC, Crossref, arXiv or bioRxiv record, and the row says which.

## Search protocol (F0 step 4)

### Common to every theme

**Sources.** PubMed through E-utilities, Europe PMC (which also indexes bioRxiv and medRxiv), arXiv through its API, the general web search, and for each theme the proceedings sites named below. Crossref is used to confirm bibliographic records, not to search. Each query is run on at least PubMed or Europe PMC, on arXiv, and on the web search, and each source is a row of the search log.

**Date range.** 1 January 2016 to the date of the search for federated learning and for prediction from histology. FedAvg's preprint is from 2016 and ST-Net from 2020, so this covers the field. Theme T4 goes back to 2000 for the statistical foundations (distributed and one-shot estimation, meta-analysis of sufficient statistics), and theme T6 to 2006 for differential privacy itself. A paper earlier than its theme's range is included only when a later included paper builds on it directly, and the row says so.

**Inclusion.** Peer-reviewed papers, conference proceedings and preprints (arXiv, bioRxiv, medRxiv) that report a method, a study, a benchmark, a survey or a consortium's practice relevant to the theme's questions. A preprint is marked as a preprint in the venue column. English language.

**Exclusion.** Papers the sub-agent cannot open at least at the abstract level. Editorials and news items without data. Theses, patents and slides. Duplicates, where the published version replaces its preprint and the row records both identifiers. Federated learning papers whose only data are natural images or text, unless the theme is T4, T5 or T6 and the paper is a standard reference for a method the review names (FedAvg, FedProx, SCAFFOLD, FedBN and the like).

**Screening.** Each sub-agent screens titles and abstracts for every query, records the number of hits and the number screened, and includes papers by the criteria above. Where a query returns more than 200 hits, the sub-agent screens the first 100 by relevance and records that.

**Core papers.** A paper is core if an answer to one of Q1 to Q9, or a verdict on a route of Q3 or a concept C1 to C4, would rest on it. That is, removing it would change the answer, its grade, or the verdict. In practice the core set is, at least, every paper on federated or privacy-preserving prediction of expression from histology, every paper that reports a learning curve or scaling result for histology-to-expression prediction, every multi-site federation in computational pathology that compares federated and pooled training, and the primary reference for each statistical method of Q7 that the review proposes. Sub-agents mark candidates with `core_candidate = yes`, and the lead decides.

**Fragment format.** `search_log.csv` has the columns `theme, query_id, date, source, query, hits, screened, included, note`. `evidence.csv` has the columns `theme, identifier, id_type, title, first_author, authors, year, venue, is_preprint, read_level, questions, summary, core_candidate, free_full_text, full_text_url, verified_from, note`. `read_level` is one of `full text`, `abstract only`, `secondary`. `summary` is two sentences in the sub-agent's own words. `verified_from` names the page the record was read from. A one-page `notes.md` beside them records what the sub-agent found and did not find, by question, with identifiers.

### T1. Prior art (Q6)

Sources as above, plus the MICCAI open-access site, NeurIPS proceedings and PMLR.

1. `federated learning spatial transcriptomics`
2. `federated learning gene expression prediction histology`
3. `privacy-preserving spatial transcriptomics prediction H&E`
4. `federated learning single-cell RNA-seq`
5. `federated learning cell type annotation`
6. `differential privacy omics deep learning federated`
7. `decentralized training whole slide image gene expression`
8. `federated batch effect correction omics`
9. `secure multi-party computation transcriptomics`
10. `swarm learning transcriptomics`

Seeds from section 2.4 of the instruction: PPML-Omics, privateST, scFed, Federated Harmony, SwarmMAP, fedRBE. Each is re-verified, and its citing papers are screened by a forward search on Europe PMC or the web search.

### T2. Federated computational pathology and medical imaging (Q3, Q5)

Sources as above, plus the MICCAI site, NeurIPS, PMLR, OpenReview, and AAAI through the web search.

1. `federated learning computational pathology`
2. `federated learning whole slide image multiple instance learning`
3. `swarm learning histopathology`
4. `federated learning medical imaging multi-institutional`
5. `federated fine-tuning foundation model pathology`
6. `parameter-efficient federated learning medical imaging`
7. `federated self-supervised pretraining histopathology`
8. `federated learning versus centralized training pathology performance`
9. `federated prompt learning frozen features`

Seeds: Lu et al. 2022, Saldanha et al. 2022, Adnan et al. 2022, Hosseini et al. 2023, Cong et al. 2026, Tsai et al. 2026, Rieke et al. 2020, Pati et al. 2022, Dayan et al. 2021.

### T3. Data scale and the data centers hold (Q1, Q2)

Sources as above, plus NeurIPS (Datasets and Benchmarks), PMLR and OpenReview.

1. `gene expression prediction histology learning curve training size`
2. `spatial transcriptomics prediction H&E benchmark`
3. `pathology foundation model scaling data`
4. `bulk RNA-seq prediction from whole slide images`
5. `cross-cohort generalization gene expression prediction histology`
6. `HEST-1k`
7. `spatial transcriptomics atlas paired histology dataset`
8. `weakly supervised spatial gene expression from bulk`
9. `TCGA H&E transcriptome prediction external validation`

Seeds: Jaume et al. 2024, Wang et al. 2025, STPath, STFlow, HESCAPE, ST-Net, HE2RNA, BLEEP.

### T4. Distributed and federated statistical estimation (Q7)

Sources as above, plus PMLR, NeurIPS and the web search for Annals of Statistics, JASA and JRSS-B records.

1. `communication-efficient distributed statistical inference`
2. `one-shot distributed estimation`
3. `distributed ridge regression sufficient statistics`
4. `federated principal component analysis`
5. `distributed linear mixed model summary statistics`
6. `federated transfer learning statistics`
7. `distributed algorithms multi-site electronic health records`
8. `DataSHIELD federated analysis`
9. `meta-analysis individual participant data equivalence summary statistics`
10. `federated inference confidence intervals heterogeneity`

Seeds: Jordan, Lee and Yang 2019; Battey et al. 2018; Dobriban and Sheng 2021; Fan, Guo and Wang 2023; Gaye et al. 2014; Grammenos et al. 2020; Duan and colleagues 2020; Li, Cai and Duan 2023.

### T5. Heterogeneity across centers (Q4)

Sources as above, plus NeurIPS, PMLR, OpenReview and the MICCAI site.

1. `federated learning non-IID data`
2. `personalized federated learning`
3. `federated learning partial label overlap` and `federated learning heterogeneous label space`
4. `federated learning missing features different feature sets`
5. `stain normalization federated learning`
6. `scanner domain shift federated pathology`
7. `federated batch normalization feature shift`
8. `federated learning site effects random effects`
9. `spatial transcriptomics gene panel harmonization Xenium Visium`

Seeds: FedProx, SCAFFOLD, FedBN, FedSDA, fedRBE, Federated Harmony.

### T6. Privacy and governance (Q5)

Sources as above, plus NeurIPS, PMLR and the web search.

1. `membership inference attack summary statistics genomics`
2. `gradient inversion attack federated learning medical images`
3. `differential privacy federated learning accuracy cost medical`
4. `re-identification histopathology images`
5. `re-identification gene expression profiles`
6. `differentially private linear regression sufficient statistics`
7. `federated learning governance data use agreement consortium`
8. `secure aggregation federated learning`

Seeds: the attacks and defences cited by PPML-Omics and by Lu et al. 2022, Kairouz et al. 2021.

### T7. Alternatives and public stand-ins for a federation (Q8, Q9)

Sources as above, plus NeurIPS, PMLR, OpenReview and arXiv.

1. `retrieval-augmented gene expression prediction histology`
2. `contrastive image expression embedding retrieval spatial transcriptomics`
3. `language model knowledge base pathology prediction`
4. `agent-written knowledge base few-shot prediction`
5. `fine-tuning pathology foundation model gene expression prediction`
6. `leave-one-site-out evaluation pathology`
7. `TCGA tissue source site batch effect`
8. `multi-center spatial transcriptomics benchmark`

Seeds: BLEEP, HESCAPE, STPath, and round 6's results (`docs/round06/README.md`).

### Searches that find nothing

A query with no relevant hits is a row of the search log with `included = 0`, and its theme's `notes.md` says what was looked for. The novelty statement of F2 cites the T1 queries and dates.

## The inventory job (F2 step 4, submitted in F0)

**Script.** `code/scripts/round7_fedlearn_f2_inventory.py`, with the helpers in `code/scripts/round7_fedlearn_common.py`. It walks the project tree, skipping only `env/`, `.git/` and `code/` at the top, and records every file's name and size. For expression files (`.h5ad`) it reads the lengths of the `obs` and `var` indexes, and for embedding and patch files (`.h5`) the shape of the `embeddings`, `barcodes` or `img` dataset. No array is loaded. It joins the listing to `results/round3/D0_inventory/hest_inventory.csv` and to the committed task definitions (`results/round3/task_defs/`, `results/round3/D4_expansion/task_defs/`, `results/round4/data/P5_task/`), all read from the code clone. The walk is capped at 45 minutes and the summary says whether it completed.

**Outputs**, in `results/round7/fedlearn/F2_inventory/`, summaries first. `inventory_summary.json`, then `centers_by_group.csv`, `inventory.csv`, and a file-level `file_listing.csv`. The lab of a sample is `lab_provisional` from the committed inventory. A group is marked as able to support a design with two or more centers when at least two resolved labs each hold a sample with expression and embeddings, and the encoders common to those labs are listed. The task definitions' own `lab` field is carried beside it, because it is more specific for the expansion sets.

**What I expect before it runs**, my own predictions beside F.5.
- About 200 to 260 samples on disk. The sets on disk are the benchmark (72 samples), `kidney_visium_cell` (58), `donor_labelled_v` (39), `lung_xenium` (24), `institution_breast_xenium` and `platform_pair_multitech`, which overlap in part.
- One to three organ and technology groups with two or more labs holding expression and embeddings. Kidney Visium will be one, with the Sorbonne ccRCC cohort and the Indiana atlas, so lab is fully mixed with disease there. The committed task definition `BREAST_XENIUM.json` gives 10x Genomics as the lab of all 18 breast Xenium samples under two spellings, so breast Xenium is a candidate only if `lab_provisional` separates them, and then the two "labs" are one vendor.
- No header errors on the benchmark and expansion files, since every one was read by an earlier round.

## Job ledger

| # | stage | purpose | Slurm id | account, partition | state | output |
|---|---|---|---|---|---|---|
| 1 | F0 | make the Longleaf code clone | 4803248 | submitted on `rc_htzhu_pi`, moved while pending to `rc_tengfei_pi`; `spill` | pending | |
| 2 | F0 | deliver the first bundle and write the snapshot | | | not submitted | |
| 3 | F0 | the inventory of F2 step 4 | | | not submitted | `results/round7/fedlearn/F2_inventory/` |

Job names carry the prefix `r7fl_` and the stage in `PROVENANCE.txt`, because the submission route replaces `--job-name`.

## How the F0 jobs are built

- **Job 1** clones `git@github.com:NicWYZ/HEST-1k-replication.git` over the SSH key on Longleaf into `/work/users/w/e/weiyang/hest_code/round7-fedlearn/`, then runs `git checkout -b round7-fedlearn 3c328ccc4d68b44d0795cfb9c91ff332c3b399d3`, since the branch is not on GitHub before the F2 push. It prints HEAD and confirms it equals the starting commit. From then on the clone never fetches from GitHub.
- **Job 2** applies `git bundle create r7fl_delivery_01.bundle 3c328ccc4d68b44d0795cfb9c91ff332c3b399d3..round7-fedlearn`, copied to Longleaf, with `git bundle verify`, `git fetch <bundle> round7-fedlearn` and `git merge --ff-only FETCH_HEAD`. It then writes `/work/users/w/e/weiyang/hest_code/round7-fedlearn_snapshots/<full hash>/` with `git archive <hash> code | tar -x` and removes write permission. Its log comes back as `results/round7/fedlearn/deliveries/delivery_01_job<id>.log`, and it is row 1 of `results/round7/fedlearn/code_deliveries.csv`, in the columns of round 5's file.
- **Job 3** runs `code/scripts/round7_fedlearn_f2_inventory.py` from that snapshot, with the snapshot's `code/scripts` on `PYTHONPATH`, from its own output directory `results/round7/fedlearn/F2_inventory/` in the project tree, with the project's Python by absolute path, 4 CPUs and an explicit memory request.

## Sub-agents of F1

| theme | questions | frame id | fragment directory |
|---|---|---|---|
| T1 | Q6 | `9ef88f09-c873-4961-9afd-06411f9bd293` | `results/round7/fedlearn/F1_search/fragments/T1/` |
| T2 | Q3;Q5 | `2cf11025-bf4b-4547-900c-6b9c4434b588` | `results/round7/fedlearn/F1_search/fragments/T2/` |
| T3 | Q1;Q2 | `7ed66b13-b09f-4181-a1e3-213a2cc78a1c` | `results/round7/fedlearn/F1_search/fragments/T3/` |
| T4 | Q7 | `3ce4ad9b-dd8e-4531-baf4-4dd3de2ac9e1` | `results/round7/fedlearn/F1_search/fragments/T4/` |
| T5 | Q4 | `54a93196-a4cd-4da2-a1cb-d4c8212f1a14` | `results/round7/fedlearn/F1_search/fragments/T5/` |
| T6 | Q5 | `50761697-26e9-4ab1-8b77-399ef856c709` | `results/round7/fedlearn/F1_search/fragments/T6/` |
| T7 | Q8;Q9 | `5dc14bbb-9e27-4a40-9cc1-5ff30d21aa49` | `results/round7/fedlearn/F1_search/fragments/T7/` |

Each brief carries the theme's questions, section 2.3 and section 2.4 of the instruction, the theme's query set, the literature rules of section 4, the fragment format and the sentence "Write only into your fragment directory, run no git command, and cite nothing you have not opened." Full texts go to `~/hest-1k/fedlearn_papers/<theme>/`. The searching sub-agents run at the session's default sub-agent tier.

### Readers of F1 step 4

| reader | frame id | papers |
|---|---|---|
| Reader 1 | `15c936b1-0606-43e5-9b70-011349229b58` | P001, P006, P183, P267, P287, P293, P321, P401 |
| Reader 2 | `9cb95535-96d1-4676-8bf2-00ae8b6035a2` | P003, P042, P205, P268, P289, P294, P329 |
| Reader 3 | `723116ff-235c-4bc8-9760-7dacadead704` | P005, P131, P266, P273, P292, P315, P339 |

Readers write `results/round7/fedlearn/F1_search/reading/R<k>/reading_notes.csv` and save full texts to `~/hest-1k/fedlearn_papers/reading/`.

## Section 7 of the instruction, transcribed

Four stages and a closing stage. Gates at F2 and F4. Transcribe this section into the plan before running anything, and keep the plan's current-state block at its top so that a compacted or restarted session can resume from the plan alone.

#### Interval i01

##### F0. Setup and the search protocol (two hours, capped at half a day)

**Entry gate for interval i01.** This document is on `main`, Nicolas has made the clone and the papers folder of section 12, and the session can reach Longleaf and at least one literature source.

1. Read this document, `docs/WAYS_OF_WORKING.md`, section 4 of `docs/round05/i02/ppi/round5_ppi_E2_decisions.md`, `docs/round07/00_prep/round07_advisor_directions.md`, `docs/round06/README.md` and sections 21 to 24 of `docs/reference/methods_and_state_of_play.md`.
2. Set up the clone and the branch (section 5), and transcribe section 7 into the plan with the starting commit's hash.
3. Check which literature sources you can reach and record the result in the plan. At least a general web search, PubMed, arXiv, bioRxiv and medRxiv, PubMed Central, and the proceedings pages of NeurIPS, ICML, ICLR, AISTATS, MICCAI, MIDL and AAAI. Record for each whether you can open landing pages and whether you can fetch full texts.
4. Write the search protocol into the plan. For each theme, the sources, the date range (2016 to the present for federated learning, earlier where a statistical foundation needs it), at least five query strings, the inclusion and exclusion criteria, and which papers count as core (those an answer to a question would rest on).
5. Make the Longleaf code clone (section 5), write `code/scripts/round7_fedlearn_f2_inventory.py` (F2 step 4), commit it, deliver it by bundle with a snapshot, and submit the inventory job, so that it queues and runs while F1 proceeds.

**Exit.** The plan with the protocol, committed on the branch and not pushed, the first row of `code_deliveries.csv`, and the inventory job submitted.

##### F1. Search, screening and extraction (one day, capped at a day and a half)

1. Dispatch the theme sub-agents of section 6.
2. As soon as the core papers are known, and no later than the middle of F1, list the core papers whose full text you cannot retrieve, choose at most 10 of them, and send the list to Nicolas as section 8 says. Continue with abstracts while you wait, and mark every claim that rests on an abstract.
3. Merge the fragments, remove duplicates, and re-verify the identifier, title, authors, year and venue of every core paper yourself.
4. Read the full text of every core paper you can retrieve, including those Nicolas uploads, and record the read level.

**Exit.** `results/round7/fedlearn/F1_search/search_log.csv`, `evidence_table.csv`, `paper_requests.md` (the list as sent, and what arrived), and the fragments, all committed.

##### F2. The review, the inventory and the proposal (one day, capped at a day and a half; gate)

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

#### Interval i02, opened by the F2 decision memo

What follows is the default. The F2 memo fixes the design, and nothing of it is set up, staged or piloted before the memo.

##### F3. Scoping experiments (two days)

**F3.0 Anchor** (outputs in `results/round7/fedlearn/F3_anchor/`). First, refit the faithful HEST-bench head (`pca_ridge`, as round 1 replicated it) for one encoder and one task on round 1's split, and match round 1's value within 0.001. Second, fit the exact head of section 2.3 (float64 eigendecomposition and Cholesky solve) once on the pooled data and once from the per-center sums, with the data split into the experiment's centers, and match the two sets of predictions to a relative difference below $10^{-8}$. Compare predictions rather than coefficients, since principal components are defined only up to sign. All later fits in F3 use the exact head. Both checks are acceptance checks, and a failure of either after one fix is a stop (section 11).

**V1. Is accuracy limited by data within what the project holds?** Outputs in `results/round7/fedlearn/F3_V1/`. On each task with at least 8 donors on disk (candidates are `CCRCC`, `INDIANA_KIDNEY` and `LUNG_XENIUM`) and each of the encoders with embeddings, hold out a fixed quarter of the donors, at least three, as the test set. Train the head on $n$ donors drawn from the rest, with $n$ on a doubling grid from 1 to the maximum, and 20 draws for each $n$. Donors `INT4` and `INT24` of `CCRCC` are treated as one donor, as in the task `CCRCC_merged`, since the two may be one person. Report the project's metric on the test donors, and the pooled Pearson correlation over all test spots beside it, with the spread over draws.

**V2. A simulated federation.** Outputs in `results/round7/fedlearn/F3_V2/`. Centers are formed in two ways. (a) By lab, wherever an organ and technology has two or more labs on disk, with the caveat of section 2.3 that lab is mixed with study and disease. (b) As a control without lab differences, random partitions of one lab's donors into $K = 3$ pseudo-centers. The arms are a local head trained on one center alone, the federated head from summary statistics (equal to the pooled head), and the federated head with a center-specific intercept. Scoring is leave one center out, and held-out donors within each center. A center left out has no intercept of its own and gets the mean of the other centers' intercepts, weighted by their numbers of spots.

**V3, only if the F2 memo adds it.** The accuracy cost of noise for differential privacy added to each center's sums, with outputs in `results/round7/fedlearn/F3_V3/`.

##### F4. The closing report (half a day; gate, end of track)

`docs/round07/i02/fedlearn/round07_fedlearn_final_report.md`, with the predictions F.6 to F.10 scored, the viability verdict of F2 revised in light of the experiments, a recommendation for the proof-of-concept paper's method and data, and what is not established. It ends with a closing page "What the federated learning track established". Update the literature review with anything read since F2, then commit, tag `round7-fedlearn-final`, push, open the pull request, and stop.

**Exit items, each with its evidence.**
1. Both F3.0 anchors pass (`F3_anchor/`).
2. Every experiment the F2 memo fixed has run in full, or the report says which cells did not and why (each experiment's results directory).
3. Every prediction of the memo is scored in a table beside its outcome (the report, section 5).
4. Every number in the report is read back from a file named beside it, and the sweep is clean or its exceptions are listed.
5. The provenance index passes both checks of section 5 for every job of the track (`provenance_index.csv`).

## Predictions, section 9 of the instruction, transcribed

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
