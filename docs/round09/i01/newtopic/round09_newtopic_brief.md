# Round 9, track newtopic, the brief

*Written on 26 October 2026 by the claude-science session, which hands this track to an independent session and takes no further part in it. It is a starting point, not an instruction. The session working on branch `claude-science-newtopic` plans its own work.*

## 1. The direction

Nicolas chose this direction on 26 October (option C of `docs/round09/00_prep/round09_direction_scan.md`, section 4). The aim is a fresh direction for a statistics-forward methodological paper in spatial transcriptomics, outside clustered prediction-powered inference and hierarchical conformal prediction, built on the data the project already has. It should have a formal result, a test on real data and a novelty check it survives. Nicolas's preferences (in `CLAUDE.md`, section 4) weigh in the choice. He wants minimal biology, with expression as a signal to predict, calibrate and use for inference. He wants a scope broad and useful beyond spatial transcriptomics, skills that transfer to quantitative finance, ML venues (NeurIPS, ICML, AISTATS) or top statistics journals, and a submittable paper by spring 2027.

## 2. What not to re-propose

The project's earlier work and round 9's scan have graded many directions. Read their verdicts before proposing anything, and do not re-propose one unless the new claim differs in a way you can state.

- Every entry of `results/round9/scan/scan_structured_results.json`. It covers capture-window placement, few-donor benchmark inference, moderated PPI variances across genes, PPI for pairwise spatial statistics, noise-ceiling evaluation by count thinning, sensitivity analysis for convenience-sampled clusters, conformal selection with clustered calibration, a between-donor prediction head, false-coverage proportions under a donor factor, design-calibrated reference distributions, few-cluster sign-flip inference, a joint PPI and prediction-set budget, multiple predictors, design-based PPI over genes, hierarchical conformal width laws, studentized hierarchical conformal sets, and probe-then-label designs. The proposer subagents' rejected candidates are in their query logs, `results/round9/scan/propose_<lens>_queries.csv`.
- Everything in round 8's positioning note (`docs/round08/i01/positioning/round08_positioning_note.md`).
- The other track's topic, valid inference with few labelled clusters under skew.
- Topics outside this project. The textual knowledge base of round 6 lives in `NicWYZ/textual-st-histology`, and round 7's federated learning line closed with a decision report (`docs/round07/oversight/round07_fedlearn_decision_report.md`).

## 3. Lessons from the scan

The space next to clustered PPI and group conformal prediction is crowded. Most candidates the session wrote down from its own knowledge were already in print, often in survey sampling, stereology, econometrics or psychometrics rather than in machine learning. The one finding that was new to the project came from looking at the data first. That was the shared technical donor factor and its single outlier donor (`docs/round09/00_prep/round09_stud_and_depth.md`). Proposer subagents given the data facts and a distinct lens each (`round09_direction_scan.md`, section 1) widened the search, and independent checkers caught what the proposers missed.

## 4. The data in hand

All HEST-1k data are gated and stay on Longleaf under `/work/users/w/e/weiyang/hest_replication` (`MANIFEST.md`, `bench_data/INVENTORY.md`). Only aggregates enter the repository.

- **HEST-Bench snapshot,** `bench_data/`, ten tasks (CCRCC, COAD, HCC, IDC, LUNG, LYMPH_IDC, PAAD, PRAD, READ, SKCM) with H&E patches, expression and the benchmark's patient splits.
- **Patch embeddings** from ten encoders (conch_v1, conch_v15, ctranspath, gigapath, hoptimus0, hoptimus1, phikon, resnet50, uni_v1, uni_v2) under `embeddings/<TASK>/<encoder>/<sample>.h5`, and for the extension sets under `embeddings_ext/` (kidney_visium_cell, lung_xenium, institution_breast_xenium).
- **Extension sets** under `hest_ext/`, with Visium kidney (INDIANA_KIDNEY, 25 donors) and Xenium lung (LUNG_XENIUM, 15 donors, 343 genes) as tasks defined in rounds 3 and 4.
- **Per-spot leave-donor-out predictions** with labels, for CCRCC, IDC, LYMPH_IDC, PRAD, INDIANA_KIDNEY and LUNG_XENIUM from three encoders. These are `b1_predictions__<TASK>__<encoder>.parquet` under `results/round3/B1_ppi/` and `results/round4/ppi/Q2_theory/predictions*/`. They also carry nuclear morphology (`area_mean`, `m_std`) and a neoplastic fraction per spot.
- **Morphology tables** under `instrumentation/`, and the HEST-1k release metadata. The project's on-disk table is v1_1_0, which the round 3 inventory (`results/round3/D0_inventory/hest_inventory.csv`) covers.
- **Raw counts** in each sample's `h5ad` (paths in the task definitions, for example `results/round4/data/P5_task/LUNG_XENIUM.json`).
- **ACS PUMS 2018,** all columns, at `~/hest-1k/acs_pums2018` on Nicolas's Mac. It is not gated.
- **Round 9's donor-level aggregates** under `results/round9/claude_science/` on Longleaf. These are donor by gene means, variances and covariances of labels and predictions, donor-mean embeddings, and normalized summaries.

Compute is Longleaf through the session's compute connector, in batch jobs, never on the login node. The project Python is `env/miniforge3/envs/hest/bin/python`.

## 5. Rules that matter most here

The full set is in the branch's `CLAUDE.md`. Three bear most on this direction.

- A literature check for novelty before any claim, run continually by independent subagents, under the vocabulary of other fields as well as machine learning. The model is prone to rediscovering results it absorbed in training.
- Subagents cannot use OpenAlex unless Nicolas approves its credential card. Tell them to use arXiv, Crossref, Semantic Scholar and web search, and to space their calls. Full-text copies of papers stay out of the repository.
- Predictions are written before every run and scored after it.

## 6. The other track

Track `fewcluster` runs at the same time on branch `claude-science-fewcluster`, on valid inference with few labelled clusters under skew. The two tracks are independent. Do not edit its files.
