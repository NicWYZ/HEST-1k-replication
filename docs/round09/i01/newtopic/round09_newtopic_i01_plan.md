# Round 9, track newtopic, the plan for interval 1

*26 October 2026. Written by the newtopic session at the start of its work, on Nicolas's Mac. Living while interval 1 runs. Changes are appended at the end with their date, and the text above them is not rewritten.*

## 1. What interval 1 is for

The track looks for a fresh direction for a statistics-forward methods paper, outside clustered prediction-powered inference (PPI) and hierarchical conformal prediction, built on the data the project already has (the brief, `docs/round09/i01/newtopic/round09_newtopic_brief.md`). Interval 1 ends in one of two ways. Either a candidate direction survives independent novelty checkers and a first test on the data, and the session reports it to Nicolas with the decisions he needs to make, or no candidate survives, and the session reports that as a roadblock with what it tried.

A note on lettering. The direction scan's section 4 (`docs/round09/00_prep/round09_direction_scan.md`) calls the prediction-set half "option C" and a new brainstorm "option D". The masterplan, the brief and this branch's `CLAUDE.md`, all written after Nicolas's decision of 26 October, call this track's direction "option C" and define it as a fresh direction outside clustered PPI and hierarchical conformal prediction. This track follows the brief's definition.

## 2. Criteria for a direction, fixed before the search

A candidate is kept only if all six hold. They are written now so that they cannot be bent to fit whatever turns up.

1. **A formal result of its own.** A theorem, an identity, a lower bound or a procedure with a stated guarantee. Applying known machinery to spatial transcriptomics does not count.
2. **Outside the excluded ground.** Outside clustered PPI, hierarchical and group conformal prediction, the other track's topic (valid inference with few labelled clusters under skew), every entry of `results/round9/scan/scan_structured_results.json` and the proposers' rejected candidates in `results/round9/scan/propose_<lens>_queries.csv`, everything in round 8's positioning note, round 3's retired topics (conformal prediction under donor shift, inference with donor-clustered variance), round 6's cheatsheets and round 7's federated learning.
3. **A test on the project's data.** It can be checked on HEST-1k tasks already on Longleaf, or on ACS PUMS 2018, with no new data pull.
4. **Broad scope.** The statement is not specific to spatial transcriptomics. A second application outside it, such as ACS or a finance-style panel, is at least plausible.
5. **Transferable skills.** Nicolas's career goal is quantitative research in finance, so directions whose machinery is used there (forecast evaluation, high-dimensional regression, factor models, model selection under multiplicity, shift and robustness) weigh more.
6. **Feasible by spring 2027,** for a venue Nicolas prefers (NeurIPS, ICML, AISTATS or a top statistics journal).

## 3. Steps

The IDs are the ones in `CLAUDE.md`, section 3.

- **N1 Orientation and plan.** Read the start files and write this plan.
- **N2 Proposer wave.** Five subagents, each with a distinct lens and none with the session's own reasoning, are given the data facts (section 4), the exclusions and the criteria. Each writes at least six raw ideas, searches each adversarially before keeping it, and keeps at most two. Every query is logged. The lenses are chosen to differ from round 9's four (factor, spatial, predictor, decision), which all looked at PPI.
  - `FORECAST`. Forecast evaluation, forecast combination and financial econometrics. The ten encoders are forecasters, genes are like assets, and donors are like independent periods or markets.
  - `REPR`. The statistics of frozen foundation-model representations. Linear probes, high-dimensional ridge theory, comparing representations, and risk estimation when samples come in groups.
  - `MEASURE`. Measurement. Count noise, a shared technical factor, single cells on Xenium against spots on Visium, change of support and resolution, deconvolution and errors in variables.
  - `SHIFT`. Shift between donors outside conformal prediction. Risk under shift, worst-group and quantile-of-groups risk, invariance, transfer with few groups, and estimating performance on a new donor without its labels.
  - `MULTI`. Inference over many outcomes at once, excluding PPI, false-coverage proportions and moderated variances. The rank or dimension of what is predictable, simultaneous statements about gene-wise performance, and selection among many targets.
- **N3 Data-first diagnostics.** The one new finding of round 9's preparation came from the data, so the session looks at structure no earlier round examined, in parallel with N2. Candidates are the error structure across encoders, the spatial structure of residuals within a slide, how predictability changes with the size of the aggregation unit on Xenium, and the factor structure of residuals across genes. Each run has predictions written before it and scored after it. These runs need Longleaf.
- **N4 Checker wave.** The best three to five candidates from N2 and N3 each go to a fresh checker whose only job is to find the paper that already did it, under the vocabulary of other fields as well as machine learning, as in round 9's scan.
- **N5 First test.** For a candidate that survives N4, a first formal statement and a first test on the data, with predictions before the run. A fresh checker reruns the novelty check on the sharpened claim.
- **N6 Report to Nicolas.** A one-paragraph brief and the decisions he needs to make, in this session's chat, and a report in this folder.

## 4. The data facts given to proposers

From the brief's section 4 and round 9's preparation, with numbers read from the files cited.

- Ten HEST-Bench tasks with H&E patches, expression and patient splits. Patch embeddings from ten encoders (conch_v1, conch_v15, ctranspath, gigapath, hoptimus0, hoptimus1, phikon, resnet50, uni_v1, uni_v2). Extension sets INDIANA_KIDNEY (Visium, 25 donors) and LUNG_XENIUM (Xenium, 15 donors, 343 genes).
- Per-spot leave-donor-out predictions with labels for CCRCC, IDC, LYMPH_IDC, PRAD, INDIANA_KIDNEY and LUNG_XENIUM from three encoders (hoptimus0, resnet50, uni_v2), with nuclear morphology and a neoplastic fraction per spot. Raw counts are in each sample's h5ad. Spatial coordinates are available.
- On CCRCC (24 donors), the first principal component of donor-mean expression carries 0.650 of between-donor variance and correlates 0.998 with the donor's average expression, a depth or detection factor (`results/round9/diagnostics/c0_shared_donor_factor.csv`). Its share is 0.313 on INDIANA_KIDNEY and 0.343 on LUNG_XENIUM.
- Out of sample, donor-level prediction from histology does not beat a constant for the median gene on Visium, while composition-marker genes on lung reach a leave-one-donor-out R^2 near 0.9 (`docs/round09/00_prep/round09_direction_scan.md`, section 3).
- The within-donor correlation of predictions with labels, averaged over donors and then the median over genes, is 0.114 to 0.198 on CCRCC and INDIANA_KIDNEY and 0.523 to 0.625 on LUNG_XENIUM across the three encoders (`results/round9/diagnostics/c0_task_medians.csv`, column `r_within`).
- ACS PUMS 2018, all columns, is on Nicolas's Mac and is not gated.

## 5. Predictions for the search, written before it

Round 9's scan found 9 of 14 directions mostly taken and the other 5 partly open with a thin remainder. Its proposers graded every one of their own proposals uncertain or likely taken.

- **W1.** At least 0.7 of the raw ideas the five proposers write will be found in print by the proposers themselves.
- **W2.** At most two kept candidates will be graded partly open with a remainder the checker calls substantive.
- **W3.** The kept candidates most likely to survive will be those tied to a data fact rather than to a lens alone.

They are scored in the interval's report.

## 6. Rules followed here

Subagents do not commit and do not use OpenAlex unless Nicolas approves its credential. They use web search, the arXiv API, Crossref and Semantic Scholar, spaced out. Full-text copies of papers stay out of the repository. Details of unpublished manuscripts by others stay out of it too. Logs go to `results/round9/newtopic/`, with one queries CSV and one candidates CSV per subagent and a structured JSON of verdicts, in the format of `results/round9/scan/`.

## Amendments

**26 October, after the first proposer and checker waves.** The five proposers kept ten candidates, none graded better than uncertain. The checkers graded NESTED, HIDDEN, PRANK and SCALE mostly taken, each with a remainder of proposition size. LOADING was parked on an approval card. Longleaf did not answer all day, so step N3 has not run. Before reporting a roadblock, the session adds step N2b, a second wave of a different kind. Three open-problem miners each read the limitations and future-work sections of recent papers in one area, list the open problems stated there, check each for a scoop, and rank them against the criteria of section 2. The areas are statistical methods for spatial omics (`STSTAT`), the statistics of evaluating and using foundation models (`FMEVAL`), and high-dimensional financial econometrics whose structure the project's data share (`FINECON`). The exclusion digest given to them adds wave 1's 45 raw ideas and the checkers' verdicts. Prediction W4, written before the wave, is that at most one mined problem will pass a checker as partly open with a remainder the checker calls able to carry a methods paper.
