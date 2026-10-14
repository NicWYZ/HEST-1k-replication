# Round 7, the federated learning track, F2 gate report

13 October 2026. Execution session of the federated learning track, for the oversight chat. Branch `round7-fedlearn` from the starting commit `3c328ccc4d68b44d0795cfb9c91ff332c3b399d3`. The instruction is `docs/round07/i01/fedlearn/round07_fedlearn_track.md` and the operating plan is `docs/round07/tracks/fedlearn/round07_fedlearn_plan.md`. The literature review is `docs/round07/tracks/fedlearn/round07_fedlearn_literature_review.md`.

## 1. Stage and status

Interval i01 is complete up to this gate. F0, F1 and F2 are done. One of three reader sub-agents of F1 step 4 parked on an approval card and was stopped, so seven core papers it was to read in full remain at the level the evidence table records (section 7 of this report). Nothing of interval 2 has been set up, staged or piloted. The gate is the tag `round7-fedlearn-F2` and pull request #28 into `main`, the number GitHub was due to assign when this report was written, confirmed on GitHub after opening. The session stops here and waits for the F2 decision memo.

## 2. What was run

**Sub-agents.** Seven theme sub-agents, T1 to T7, searched and screened as section 6 of the instruction sets out, with the briefs built from sections 2.2 to 2.4 and 4 of the instruction and the protocol of the plan. Their frame ids are in the plan's sub-agent table. Every theme ran its protocol queries on PubMed or Europe PMC, on arXiv and on the web search, and T2 was asked for a second pass to close gaps it declared. Three reader sub-agents then read in full the core papers left at the abstract level (plan, "Readers of F1 step 4"). A fresh sub-agent at the session's own tier ran the citation audit of F2 step 6. The searching and reading sub-agents ran at the session's default sub-agent tier. The synthesis, the verdicts and the text of the review are the session's own.

**Sources reached.** PubMed, PubMed Central, Europe PMC, arXiv, bioRxiv and medRxiv, Crossref, Unpaywall, the NeurIPS proceedings, PMLR, OpenReview pages, the MICCAI papers site and nature.com, after Nicolas approved access to the last seven on 13 October. AAAI's server refuses direct connections, so AAAI pages were seen through the web search. The table of sources and what each allows is in the plan, "Literature sources reached".

**Computation.** Three Slurm jobs, as section 2.5 of the instruction allows. Times and memory are from `sacct`, recorded in `results/round7/fedlearn/job_accounting.csv`.

| job | Slurm id | account, partition, node | what ran | wall time | peak memory | record |
|---|---|---|---|---|---|---|
| 1, code clone | 4803248 | `rc_tengfei_pi` (moved from `rc_htzhu_pi` while pending), `spill`, c130502 | `git clone` over the Longleaf SSH key, `git checkout -b round7-fedlearn 3c328ccc` | 1 min 46 s, after 1 h 42 min pending | 2091724K | the plan's job ledger |
| 2, delivery 1 | 4806950 | `rc_tengfei_pi`, `spill`, c0413 | bundle `3c328ccc..f1f11c90` (md5 `446dfd08db2e56d6e904aafea91d76be`), `git merge --ff-only`, snapshot by `git archive` | 11 s | 64580K | `results/round7/fedlearn/deliveries/delivery_01_job4806950.log`, `results/round7/fedlearn/code_deliveries.csv` |
| 3, inventory | 4806992 | `rc_tengfei_pi`, `spill`, c151418 | `code/scripts/round7_fedlearn_f2_inventory.py` (md5 `e5b12550229ca4187fcdcee7f19bd286`) and `code/scripts/round7_fedlearn_common.py` (md5 `69a4cdb299564fc079b683f0a3219dbc`) from the snapshot of commit `f1f11c901e440023cadb7f992e4c8c12be3ccbad` | 33 s | 315760K | `results/round7/fedlearn/F2_inventory/PROVENANCE.txt` |

The provenance index and its two checks were made in the Mac clone with `code/scripts/round7_fedlearn_provenance_index.py`, which reads only git objects and the provenance files. The numeric-claim sweep ran in the Mac clone. Both are the bookkeeping section 4 of the instruction counts as the session's own work. If the oversight chat reads the provenance script as a local run, it can be redone on Longleaf.

**Commits on the branch.** `f1f11c90` (plan, protocol, inventory script), `ab51cac2` (F1 outputs), `9a977457` (delivery record and ledger), and the commits of this gate. Only `f1f11c90` was delivered to Longleaf, since the later ones change only documents and results.

## 3. Acceptance checks and exit items

**Exit item 1, the search log.** `results/round7/fedlearn/F1_search/search_log.csv` has 695 rows and 219 query identifiers over the seven themes. The number of query identifiers each theme ran on each kind of source is in `results/round7/fedlearn/F1_search/search_coverage_by_theme_and_source.csv`. Every theme ran at least its protocol queries on PubMed or Europe PMC, on arXiv and on the web search. T3 and T6 reached the proceedings sites only through the web search, and other shortfalls the sub-agents declared are in section 7. Met, with those limits.

**Exit item 2, identifiers and read levels.** `results/round7/fedlearn/F1_search/evidence_table.csv` has 406 papers, merged from 488 fragment rows, with 55 merge collisions listed in `results/round7/fedlearn/F1_search/merge_collisions.csv`. The review cites 91 of them, and each carries `cited_in_review = yes`. The lead re-verified each of the 91 against Crossref, PubMed, Europe PMC, arXiv or a proceedings page (columns `lead_verified_from` and `lead_check`). Of the 91, 72 are read at full text and 19 at the abstract level. The review cites nothing outside the table. Met.

**Exit item 3, the citation audit.** `results/round7/fedlearn/F2_audit/citation_audit.csv`. The audit's findings and the fixes are in section 6 of this report.

**Exit item 4, paper requests.** `results/round7/fedlearn/F1_search/paper_requests.md` holds the 5 papers sent to Nicolas on 13 October and what arrived. Section 14 of the review lists the claims that still rest on abstracts.

**Exit item 5, the documents and the sweep.** The review, the verdicts (its section 11), the inventory (section 6 of this report) and the proposal (section 9 of this report) are written. The numeric-claim sweep over the plan, the review and this report is clean, with every claim verified and none uncited (`results/round7/fedlearn/F2_audit/numeric_sweep_F2.txt`). Its exceptions are in `.verify-exceptions-round7-fedlearn`. Three are HTTP status codes and a page number. Eleven are comma-grouped integers that sit inside the free-text summary cells of the cited tables, which the checker does not match, and each was confirmed by string search. That is a checker limitation, which section 7 proposes to fix in the checker.

**Exit item 6, provenance.** `results/round7/fedlearn/provenance_index.csv` has a row for each script of the inventory job. Both rows pass check 1 (the recorded commit is an ancestor of the gate tag) and check 2 (the recorded md5 equals the md5 of the script at that commit). The clone and delivery jobs ran shell commands and no repository script, so their record is the delivery log and the ledger, as in round 5.

**The inventory job's own checks**, from `results/round7/fedlearn/F2_inventory/inventory_summary.json`. The walk listed 26592 files and completed. Every one of the 205 samples on disk is in the committed inventory table, all 72 benchmark samples are on disk, and no header failed to read. All 237 task-definition rows in 17 files name a sample on disk.

## 4. The variables that differ between the arms of each comparison

This gate makes no experimental comparison. The comparisons quoted from the literature in the review are each paper's own. For the comparisons the proposal of section 9 would make, the differing variables are listed with each experiment.

## 5. Predictions against outcomes

The oversight chat's predictions for this gate, scored from the review and the inventory.

| prediction | outcome | score |
|---|---|---|
| F.1 At most three papers federate prediction of expression from histology, and none fits a head on a frozen foundation model from per-center summary statistics. | One paper, PPML-Omics (P001), within the sources searched. privateST (P002) is encrypted inference, not federated learning. No summary-statistic head was found (review, sections 7 and 12). | held |
| F.2 No paper reports a learning curve of spot-level accuracy against training patients or centers for heads on frozen foundation-model embeddings. | None found. The nearest are VOICE (P378), a two-point comparison of 24 against 75 training slides for an end-to-end model on Xenium cells, and SEQUOIA (P130), a downsampling curve for bulk prediction (review, section 2). | held |
| F.3 At least two federated pathology studies report federated performance within 0.02 of pooled training for classification. | Saldanha et al. (P014), swarm 0.763 against merged 0.757 AUROC. Adnan et al. (P018), 0.823 against 0.839 accuracy. Lu et al. (P015), kidney subtyping about 0.976 against 0.985 AUC, while breast subtyping was about 0.86 against 0.92 (review, section 4). | held |
| F.4 No federated method handles centers measuring different gene panels in expression prediction. | None found (T5 queries q03, q04, q09, T1 query q10, T6 query q10). The nearest are fedRBE (P006), batch correction with non-identical features, and Ayme et al. (P287), covariates missing by center (review, section 5). | held |
| F.5 The inventory finds two or three organ and technology groups on disk with slides from two or more labs, enough for leave-one-lab-out without a download. | The table's own flag counts 6 groups with two or more labs holding expression and 4 holding expression and embeddings. Read row by row, the lab field splits one vendor across two spellings and counts unresolved studies as labs, and the groups with two or more distinct sources holding embeddings are kidney Visium, breast Xenium and lung Xenium, where lung's second source is 2 vendor samples (section 6). In every one, lab is mixed with disease or study. | partly held |

The session's own predictions for the inventory, written in the plan before the job ran, were about 200 to 260 samples on disk (205, held), one to three groups with two or more labs holding expression and embeddings (raw flag 4, reading 2 or 3, partly held), and no header errors (none, held).

## 6. Results

**The review.** The answers, grades and verdicts are in `docs/round07/tracks/fedlearn/round07_fedlearn_literature_review.md`. In brief, by its own grades, Q1 (is accuracy limited by data) is weak and not established, Q2 moderate, Q3 strong for the algebra of a summary-statistic head and for iterative heads in pathology classification but none found for expression, Q4 moderate with none found for differing gene panels, Q5 moderate, Q6 strong as a search result, Q7 strong for exact one-round linear and mixed-model fits, Q8 weak, and Q9 moderate for leave-one-site-out evaluation. The verdicts on the routes and concepts are conditional for route 1, route 2, C1, C2 and C3, not supported for a first paper for routes 3 and 4, and not supported as privacy-preserving for C4.

**The citation audit.** A fresh sub-agent at the session's own tier (frame `e9fb6ffa-9020-4899-a46c-b5387c5de284`), which had not seen the drafting, opened the record of every one of the 91 cited papers and checked every citing sentence (`results/round7/fedlearn/F2_audit/citation_audit.csv`, totals in `results/round7/fedlearn/F2_audit/audit_notes.md`). Every identifier resolved to the paper named and every title matched. Of the claims, 69 were fully supported, 20 partly and 2 not supported, so 22 papers had a claim-level mismatch, and 33 papers had some mismatch once record-level issues are counted. The two unsupported claims were that SEAL's 1.33% belonged to the best encoder (it belongs to the encoder that improved most, and the best baseline rose from 0.4142 to 0.4186) and that Ziegler et al.'s private model was 0.03 below the non-private one (it matched it, and the 0.03 drop was on some clients). Every claim-level finding was fixed in the review, and the venue and year findings were fixed in the evidence table. Each change is a row of `results/round7/fedlearn/F2_audit/audit_fixes.csv`. Two things were not fixed. Author lists truncated at 15 names plus "et al." were left as the fragment format asked. The number of hospitals in the published version of Ogier du Terrail et al. was not verified, since only the preprint could be read, and the review now names the preprint. The audit itself checked P188 from its abstract only, and relied on arXiv comments for several published venues.

**The novelty statement** is section 12 of the review. Within the sources and queries in the search log, no paper fits a head for spatial expression on frozen pathology foundation-model embeddings from per-center summary statistics, or handles differing gene panels. The estimator itself is established for linear and mixed models and for classification heads on frozen features, so novelty could rest only on its application and what it shows.

**The inventory.** From `results/round7/fedlearn/F2_inventory/inventory_summary.json` and `results/round7/fedlearn/F2_inventory/centers_by_group.csv`. There are 205 samples on disk in 18 organ and technology groups, all with expression and 142 with embeddings. The four groups the table flags as having two or more labs with expression and embeddings are these, read from `inventory.csv`.

| group | sources on disk with embeddings | samples | what differs besides lab |
|---|---|---|---|
| Kidney Visium | Sorbonne Université (the CCRCC cohort, 24 samples, 24 donors), Washington University (23 samples) and Indiana University (7 samples), both in the committed task `INDIANA_KIDNEY`, KTH (3 samples) and a 10x vendor sample | 58 | cancer against non-tumour kidney, study, protocol. The committed task definition gives one Indiana laboratory as the lab of all 26 `INDIANA_KIDNEY` samples, so the Washington and Indiana split in `lab_provisional` may name the paper's last author rather than where the tissue was processed |
| Breast Xenium | 10x Genomics under two spellings (7 samples with embeddings) and one study recorded as unresolved, a 2025 bioRxiv preprint (11 samples with embeddings) | 21 | study, and healthy tissue in the second source only |
| Lung Xenium | the Translational Genomics Research Institute under two spellings (22 samples) and a 10x vendor source (2 samples) | 24 | fibrosis against cancer, study, panel design |
| Bowel Xenium | 10x Genomics under two spellings (4 samples) | 4 | none, since it is one source |

So the honest count is two groups with a usable second source (kidney Visium and breast Xenium), and a third (lung Xenium) whose second source has 2 samples. Every expression file of a Xenium sample on disk has 541 genes, so the headers cannot show whether centers measured different panels. Whether HEST stores absent genes as zero columns was not checked. The tasks with at least 8 donors on disk and embeddings for `hoptimus0`, `resnet50` and `uni_v2` are `CCRCC`, `INDIANA_KIDNEY` and `LUNG_XENIUM`, so the default V1 can run on the data on disk.

## 7. Discrepancies, open questions and escalations

**Escalations, recorded and continued.**

1. *The inventory's lab field overcounts labs.* `lab_provisional` in the committed inventory table records one vendor under two spellings and records unresolved studies as strings beginning "unresolved:", and the inventory script counted each distinct string as a lab. So the `two_plus_labs` flags of `centers_by_group.csv` overcount, as section 6 shows. The tables were read row by row for this report and not recomputed, since any further Slurm job in interval 1 is not the session's decision. A corrected grouping is proposed as the first job of interval 2.
2. *PPML-Omics' preprint and published numbers differ.* The fragment summaries of T1 and T6 quoted the preprint, where every arm of the spatial task had an MSE near 0.91. The published Table 2 has 0.93120 for federated training against 0.90904 centrally, and higher values under differential privacy. The review quotes the published table (reading notes, `results/round7/fedlearn/F1_search/reading/R2/reading_notes.csv`).
3. *Items of section 2.4 that differ from their description.* fedRBE (arXiv:2412.05894) now carries the title "Batch effects can impair federated learning in multi-center omics studies" and introduces fedRBE inside it. Grammenos et al. is a streaming, differentially private PCA, not an exact PCA from summed covariances. Hosseini et al. (IEEE TMI 2023) is about fairness across hospitals, not accuracy or scale. scFed's Crossref year is 2023, published online in January 2024. The published Kairouz et al. record on Crossref lists two authors, while the arXiv version lists the full group. The statement that none of the accuracy-and-scale papers reports a learning curve holds for the spatial papers, while SEQUOIA reports a downsampling curve for bulk prediction and VOICE a two-point comparison in slides.
4. *Sources that could not be reached.* AAAI's own server, the OpenReview API and PDFs, and the publisher sites listed in the plan. Records came from Crossref, PubMed or Europe PMC and texts from PubMed Central or preprints.
5. *A reader sub-agent was stopped.* Reader R1 (frame `15c936b1-0606-43e5-9b70-011349229b58`) asked for network access to `europepmc.org` during F1 step 4, against its brief, and parked on that approval card. The session stopped it before the gate, since a push after the gate would add commits to the open pull request, and it wrote no notes. Its papers, P006, P183, P267, P287, P293, P321 and P401, stay at the read level the evidence table records, and section 14 of the review lists those cited at the abstract level. Reading them in full is proposed for interval 2.
6. *Screening shortfalls the theme sub-agents declared.* Titles beyond the first 100 by relevance were not screened for broad queries, several themes screened titles through a keyword filter before reading, the arXiv API returned HTTP 429 during the parallel searches and some rows used the arXiv website search, and web-search rows have no hit totals. The sub-agents' own lists are in their results and in each theme's `notes.md`.
7. *Read level.* In this track "full text" means the methods, results and discussion were read where they bear on the questions. Several sub-agents read by targeted passages within that definition, and the plan records it.

8. *A checker limitation.* `code/scripts/verify_numeric_claims.py` does not match comma-grouped integers inside free-text cells of a cited CSV, so 11 values quoted from paper summaries were declared as exceptions with the cell named. The fix belongs in the checker, which this track may not edit.

**Open questions for the oversight chat.** Whether the provenance index script counts as bookkeeping or as a local run. Whether a center in V2 may be a study rather than a lab, given escalation 1.

## 8. What was not checked

Whether the Xenium expression files on disk hold zero columns for genes a center did not measure. Whether the Washington University and Indiana University samples of the kidney atlas were processed at different sites. The OpenReview and AAAI full texts. Proofs and appendices of the statistical papers. Every number in the theme fragments' summaries that the review does not quote.

## 9. Proposed next step, the proposal for interval 2

Everything below is a proposal for the F2 memo to fix or change. No download is needed for any of it. Every job would run on Longleaf from a delivered snapshot, with the exact head of section 2.3 of the instruction unless stated. Compute estimates assume the round-1 measurement of about 17 GB peak for heads over the largest benchmark task (`docs/WAYS_OF_WORKING.md`, "Size memory from sacct").

**F3.00, a corrected center grouping (new).** Rerun the inventory grouping with vendor spellings merged and unresolved studies kept as their own study label, and add a study column from the committed task definitions, so that V2 can say whether a center is a lab or a study. One job of under a minute.

**F3.0, the anchors (as in the instruction).** Refit the faithful `pca_ridge` head for `uni_v2` on `CCRCC` on round 1's split and match round 1's 0.264 within 0.001 (`results/summary/discrepancy_table.csv`). Then fit the exact head once on the pooled data and once from per-center sums with the centers of V2, and match the predictions to a relative difference below $10^{-8}$. One job, 4 CPUs, 32 GB, under an hour.

**V1, is accuracy limited by data within what the project holds (as in the instruction).** Tasks `CCRCC` (with `INT4` and `INT24` merged), `INDIANA_KIDNEY` and `LUNG_XENIUM`, encoders `hoptimus0`, `resnet50` and `uni_v2`, a fixed quarter of donors held out, at least three, training donors on a doubling grid from 1 to the maximum with 20 draws each. The within-slide Pearson and the pooled Pearson on test spots, with the spread over draws. The arms of one curve differ only in which and how many donors train the head. Nine jobs of about 30 minutes each.

**V2, a simulated federation (revised).** Centers are formed in three ways. (a) By source, wherever section 6 found two or more, which is kidney Visium (the Sorbonne CCRCC cohort against the kidney atlas, using the committed task `KIDNEY_POP54`, whose populations are exactly these two) and breast Xenium (10x against the second study, task `BREAST_XENIUM`). Lung Xenium is reported but not scored, since its second source has 2 samples. Between these centers, lab, study, disease and often protocol all differ. (b) Random partitions of one source's donors into $K = 3$ pseudo-centers, in `CCRCC`, `INDIANA_KIDNEY` and `LUNG_XENIUM`, where only the donors differ. (c) New, from Q4 of the review. The same partitions as (a), with each center's embeddings centred on that center's own mean before the head is fitted and before prediction, which is a one-round, summary-statistic analogue of keeping normalisation local [P268]. This arm tests whether the scanner and site signatures the review found in frozen embeddings [P289, P355] are what limits leave-one-center-out accuracy.

The arms are a local head on one center, the federated head (equal to the pooled head), the federated head with a center-specific intercept, and in (c) the federated head with center-centred embeddings. With centers $k = 1, \dots, K$ and spots $i$, the intercept arm fits

$$
y_{ik} = \alpha_k + B^\top V^\top (x_{ik} - \bar x) + \varepsilon_{ik},
$$

from the same sums, plus each center's spot count and expression sum. A center left out gets the spot-weighted mean of the other centers' $\alpha_k$. Scoring is leave one center out and held-out donors within each center, with the within-slide Pearson and the pooled Pearson. Between the local and federated arms, the training donors and their centers differ. Between the federated and intercept arms, only the intercept term differs. Between the federated and centred arms, only the centring of the embeddings differs. About 20 jobs of under 30 minutes.

**V3, the cost of differential privacy (offered, for the memo to add or not).** Gaussian noise added once to each center's sums, calibrated as in AdaSSP [P339], at several budgets, with the accuracy cost read against the federated head. The review found no measurement of this cost for embeddings of a thousand or more dimensions. Cheap, since it reuses V2's sums.

**V4, partial gene overlap (offered, new).** Mask a random part of the target genes at each center of V2(b), fit each gene from the centers that measure it (its cross-products then come only from those centers), and compare with the full-overlap fit. This is the gap F.4 confirmed. Cheap.

**Predictions for interval 2.** The oversight chat's F.6 to F.10 stand as written. The session's own, beside them, are these.

| prediction | oversight chat | session |
|---|---|---|
| F.6, the rise from 1 to 4 donors exceeds the rise from 4 to the largest size | in every task and encoder | in at least 7 of the 9 task and encoder cells |
| F.7, `CCRCC` with `uni_v2` at the largest size within 0.02 of half that size | within 0.02 | within 0.02 |
| F.8, leave-one-lab-out below held-out donors within the lab | in every group and encoder | held in kidney, not predicted for breast |
| F.9, adding another lab's slides changes a lab's held-out accuracy by less than 0.02 | less than 0.02 | less than 0.02 in breast, more than 0.02 in kidney |
| F.10, the intercept changes the within-slide metric by less than 0.005 and raises the pooled Pearson | as stated | as stated |
| new, V2(c), centring each center's embeddings raises the leave-one-center-out pooled Pearson | none | raises it in kidney, and changes the within-slide metric by less than 0.01 |
| new, F3.0, the federated and pooled exact heads agree | below $10^{-8}$ | below $10^{-10}$ in float64 |

The review's Q1 grade is weak, so V1 is the experiment that bears most on whether the paper's premise holds, and V2(a) is the one that bears most on what a federation adds across real sources.
