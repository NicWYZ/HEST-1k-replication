# CLAUDE.md

**Read this first.** This file is the brief for an independent investigator working on this repository. You were not part of the work recorded here, and you are not asked to continue anyone's plan. Your job is to study the project as it stands, judge it on its merits, and do research that moves it forward. This file says what the project is, what is known, where the evidence is, and which questions are open. The full history is in `docs/`, starting from `docs/README.md` and `docs/progress-log.md`.

**As of** 24 October 2026. You work on branch `claude-science`. Keep your work there. Nicolas decides later how any of it reaches `main`.

## 1. The project

The project is Nicolas Weiyang Zhang's first-year biostatistics PhD project at UNC Chapel Hill, in Dr. Hongtu Zhu's lab and supervised by Dr. Daiwei (David) Zhang. The advisors want methods, not applied analysis, with a submittable paper by spring 2027. Nicolas prefers ML venues (NeurIPS, ICML, AISTATS) or top statistics journals, wants the paper's scope broad and useful beyond spatial transcriptomics, and keeps the biology minimal by design. Expression is treated as a signal to predict, calibrate and use for inference.

The paper in preparation is "Labelling budgets for prediction-powered inference with clustered data". Labels are expensive and machine-learning predictions are free. Units come in clusters, such as donors in spatial transcriptomics or states in census data, and only a few clusters, often 4 to 16 of 15 to 50, can be labelled. The questions are how to spend a labelling budget (whole clusters, or a few units in every cluster), which clusters to label, how to make valid inference with prediction-powered inference (PPI) at so few clusters, and how to build prediction sets for a new cluster. The applications are HEST-1k spatial transcriptomics (pathology foundation-model predictions of gene expression) and ACS PUMS 2018 income by state.

## 2. Where the project stands

Nicolas's summary of the state is that every result the project has produced on the PPI paper has turned out, on checking against the literature, to be someone else's. Round 8 (from 19 October) checked each claim against the survey-sampling literature and newer PPI work. Its positioning note, `docs/round08/i01/positioning/round08_positioning_note.md`, is the current account of what the paper can and cannot claim, and should be read in full before anything else.

- **Classical or in print.** The design-target gain formula (a regression estimator on cluster-level values), the comparison of labelling whole clusters against a few units in every cluster with costs, the level term and the regression form with a cluster-specific intercept, the optimal number of units per cluster with a predictor (Snijders 2001, Raudenbush 1997), the interval for rejective (Mahalanobis-balanced) selection of clusters (Yang, Qu and Li, JASA 2023, appendix A5), and the small-sample cluster-robust correction (Bell and McCaffrey 2002).
- **Partly in print.** Design-based inference after prediction-guided selection (in print for units, not for a few whole clusters), cube sampling of clusters with simulated pair probabilities (Breidt and Chauvet 2011, Chauvet 2011), and the failure of weighting under rejective selection (Legg and Yu 2010 for units).
- **A defect, not a result.** The estimator the project has used since round 5 (`docs/round05/tracks/ppi/round5_ppi_estimator_definition.md`) is, for an even number of labelled clusters, Williams' (1961) exactly unbiased split-sample regression estimator with the factor $1 - n/G$ missing from its correction term. Writing its two parts as $T_1$ and $T_2$,
$$
\hat\theta_{\text{round 5}} = T_1 - T_2, \qquad \hat\theta_{\text{Williams}} = T_1 - \Big(1 - \frac{n}{G}\Big)T_2 ,
$$
so the round-5 estimator has a design bias of $\{(n/G)/(1 - n/G)\}\,\text{Cov}(c', \bar f_L)$. Under the round-5 coefficient rule (slope clipped to $[0, 1]$, zero below six clusters) the bias is small except near a census (note, section 3.2, and the check in `results/round8/positioning/checks/`).
- **What is left.** Only empirical findings. These are the comparison of selection designs at few clusters on real tasks (round 7), the map of which prediction-set method is narrowest by the number of labelled units in the target cluster (round 5), and the idea of splitting one labelling budget between inference and prediction sets, which no search found in print. The paper has no methodological core of its own yet.

The round-7 documents (`docs/round07/oversight/round07_ppi_results_explained.md`, `docs/round07/oversight/round07_ppi_positioning.md`) predate round 8 and still call several of these results the paper's own. Round 8's note lists the corrections in its section 5.

## 3. Open scientific questions

These come from the positioning note (sections 6.2 to 6.5) and earlier rounds. None has been started.

1. **A methodological core.** The note proposes three directions, each to be checked against the literature first. One is exact or finite-sample design-based inference after prediction-guided selection of few clusters, where every interval and coverage guarantee found so far is asymptotic (randomization inference over the selection design, and the constrained-randomization literature for cluster randomized trials with few clusters). Another is the selection design as the object of a theory, choosing inclusion probabilities and balance variables for a few clusters to minimise the design variance of PPI while keeping the design measurable. The third is a theory for splitting one labelling budget between inference and prediction sets.
2. **Fixing the estimator.** Compare the round-5 estimator, Williams' estimator with two groups, Williams' estimator averaged over splits (or Sanguiao Sande and Zhang's Rao-Blackwellised form), the fold-wise cross-fitted form (Lu et al. 2025, An et al. 2026) and a global coefficient, at 4 to 16 labelled clusters, with bias, variance and coverage. Williams' form needs a variance estimator that does not assume a small sampling fraction.
3. **Smaller items.** Yang, Qu and Li's non-normal quantile in place of the $t$ reference for the rejective interval, and Aronow and Samii's conservative variance under rejective selection.
4. **Whether the prediction-set half stays in the PPI paper** or becomes a separate paper. It is among the few parts untouched by prior work.

Ten sources the note could not read (Cochran 1977, Särndal, Swensson and Wretman 1992, Valliant, Dever and Kreuter 2018, Mickey 1959, Breidt and Chauvet 2011, Fattorini 2006, Fuller 2009, the JASA version of Yang, Qu and Li, Broska, Howes and van Loon 2025, Moerbeek 2006) are listed with access links in the note's section 7. Nicolas may supply them. Paper PDFs he supplies go in `~/hest-1k/ppi_conf_papers/` on his Mac, outside the repository.

## 4. The history

The project began on 12 September 2026 as a replication of the HEST-1k benchmark (Jaume et al., NeurIPS 2024) on UNC's Longleaf cluster. It went through two changes of direction before settling on labelling budgets for PPI with clustered data in round 4. `docs/README.md` has one line per round and points to each round's reading guide, and `docs/progress-log.md` says what was found at each step and why the project moved, newest first.

- **Rounds 1 to 3** (12 to 24 September). Replication and instrumentation of the benchmark, then first experiments on two original topics, which were retired.
- **Round 4** (28 September to 3 October). A data pull, then an inference track (PPI with clustered labels) and a prediction-set track (hierarchical conformal prediction, HCP and GHCP).
- **Round 5** (7 to 9 October). The design-target interval, the regression form with a cluster intercept, balanced selection of clusters, and the prediction-set map.
- **Round 6** (11 to 13 October). A side experiment for David on language-model cheatsheets for expression prediction. It moved to the private repository `NicWYZ/textual-st-histology` on 19 October and is outside this project now.
- **Round 7** (13 to 15 October). Inference after histology-guided selection of clusters (rejective, cube, mixture, k-center designs, and comparison with Broska and Howes's cluster-robust PPI), and a separate federated learning line for expression prediction, closed with a decision report.
- **Round 8** (from 19 October). The positioning check above.

The history was written by a coordinating chat and by sessions that ran experiments, organised in rounds, intervals, gates, instructions and decision memos. That vocabulary describes how the past work was organised. It places no obligations on you. Reports in `docs/` were written once and later corrections were added in later documents, so read a round's reading guide ("Corrections and withdrawn readings") before trusting a number from inside it.

## 5. Data, code and compute

- **Repository layout.** `docs/` holds the record by round (`docs/roundNN/`, each with a `README.md`), with `docs/reference/` for methods derived from scratch. `code/scripts/` holds every script, `results/` the outputs by round, `figures/` the figures. `docs/moved.md` maps old paths to new ones, and some files under `results/` and older scripts still carry old paths.
- **Data.** The HEST-1k benchmark data are gated (`MahmoodLab/hest-bench`) and are not in this repository. They sit on Longleaf under `/work/users/w/e/weiyang/hest_replication` (`MANIFEST.md`, `bench_data/INVENTORY.md`), whose working tree is at tag `round4-data-v2`. The raw ACS PUMS 2018 fetch is at `~/hest-1k/acs_pums2018` on Nicolas's Mac, outside the repository.
- **Compute.** Longleaf (ONYEN `weiyang`, Slurm accounts `rc_htzhu_pi` and `rc_tengfei_pi`). The environment is described in `env/`.
- **Verifying numbers.** `code/scripts/verify_numeric_claims.py` checks that a number in a markdown document appears in the file the document cites.

## 6. Standards of evidence

These are standards the project has held itself to, and the record depends on them.

- Read every number back from its file before asserting it, and recompute a derived value before stating it.
- Write predictions before a run and score them afterwards as held, partly held, refuted or not tested.
- Claim nothing as new without a literature check, and check the survey-sampling literature as well as the machine-learning one. Most claims the project made fell to that check.
- Details of unpublished manuscripts by others (title, authors, methods, results) stay out of this repository, which is public. Record only that a check was made and its verdict.
- Gated data never enter the repository.
- Contacting anyone outside the project (authors, advisors, collaborators) is Nicolas's decision.

## 7. How Nicolas wants writing done

- Plain, natural prose. No em-dashes. No sentence that states something, then a colon, then the explanation. No compressed or clever phrasing, and no inflated length.
- Math as rendered LaTeX, each `$$` on its own line. In a derivation, show every expression that carries the argument and skip only the algebra between displayed lines, saying what kind of step was skipped. Never describe a derivation in words in place of its formulas.
- Numbers at the precision the comparison needs, with the relative scale stated. Full precision stays in files.
