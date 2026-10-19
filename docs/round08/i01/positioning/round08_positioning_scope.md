# Round 8, the positioning track, scope and search protocol

19 October 2026. Written by the oversight chat as stage P0 of the positioning track (`docs/round08/masterplan.md`). This is an oversight track, so the document is the oversight chat's own plan rather than an instruction to an execution session. A fresh agent checked it before the first commit, and its findings are worked in. It is frozen once committed, and anything that changes it afterwards is recorded in the positioning note.

## 1. The question

Which of the PPI paper's remaining claims are already in print, on the survey-sampling side or in PPI work newer than round 7's check, and in what form. The answer is a verdict per claim, with the formulas compared wherever a verdict rests on a formula. The paper plan of this round is built on the claims that survive.

## 2. The claims to check

Taken from `docs/round07/oversight/round07_ppi_results_explained.md` (Parts A to C) and `docs/round07/oversight/round07_ppi_positioning.md` (sections 2.2 and 5), in the terms round 7 left them. Each claim keeps its ID through the round.

| ID | Claim the paper would make | Where it was established |
|---|---|---|
| C0 | The framing, valid inference after histology-guided (prediction-guided) selection of the clusters to label | round 7, open question O2 |
| C1 | For the design target with whole labelled clusters, the finite-population factor and the cross-fitting term that the factor does not shrink, which together keep the tuned interval valid at moderate and large $n_L/G$. The coefficient is cross-fitted from $n_L = 6$, so the term exists only there. The general few-cluster claim is already settled against the paper (round 7) | round 5, `docs/round05/tracks/ppi/round5_ppi_estimator_definition.md`, explainer A2 and A5 item 4 |
| C2 | The comparison of labelling whole clusters (regime A) with labelling a few units in every cluster (regime B) for the design target, where regime B has no between-cluster term, with costs per cluster and per unit and a crossover cost ratio | rounds 4 and 5, explainer A1 and Part C |
| C3 | The level term in regime B, and form C (a cluster-specific intercept) as the estimator that removes it, with the constant predictor as the control | round 5, explainer A1 |
| C4 | The optimal number of labelled units per cluster with a predictor. With fixed coefficients it is $m^\star\sqrt{(1 - R^2_w)/(1 - R^2_c)}$, and round 5 replaces $1 - R^2_c$ by the measured between ratio $\rho_c(n_L)$ for cross-fitted coefficients | round 5, estimator definition "Allocation", explainer Part B |
| C5 | Rejective selection of a few clusters balanced on their mean predictions, accepting a draw when its Mahalanobis distance is small, with the classical mean and the interval `rej_t`, and its matched comparison with simple random selection and the tuned estimator | rounds 5 and 7, explainer A4 |
| C6 | A cluster-level cube design with inclusion probabilities bounded below, balanced on $\pi_g$, the constant and $\bar f_g$, with the Hájek mean and the Sen-Yates-Grundy variance from simulated pair probabilities | round 7, explainer A5 item 2 |
| C7 | The negative result that inclusion-probability weighting fails under rejective selection, through near-zero $\pi_g$ and zero $\pi_{gh}$ | round 7, explainer A5 item 1 |
| C8 | The negative result that greedy k-center selection of clusters admits no design-based variance and that the classical interval then under-covers badly | round 7, explainer A5 item 3 |
| C9 | Not a claim. A comparator check for R7-5, whether anyone has published a small-sample cluster-robust PPI interval. The correction itself ($t_{n_L - 1}$ and the divisor $n_L - 1$) is graded classical in advance, since round 3 already used $G/(G-1)$ and $t_{G-1}$ following Cameron and Miller and MacKinnon, Nielsen and Webb (`docs/round03/i03/exec/round3_final_report.md`, section 6.4) | round 7, explainer A5 item 4 |
| C10 | For prediction sets for a new donor, HCP (Lee, Barber and Willett, arXiv:2306.06342, as the round-5 conformal instruction defines it) up to 5 labelled target spots and the full conformal set inside the target donor from 9, with GHCP's dependence on the number of calibration donors | rounds 4 and 5, explainer A3 and Part B |
| C11 | The joint design, inference and prediction sets under one labelling budget | rounds 4 and 5, explainer Part C |
| C12 | The cluster-level reading of the gain formula, its no-gain corollary at large cluster size, and its design-target version, the tuned ratio $1 - R^2_{\text{cluster}}$ with the unshrunk coefficient $\lambda_c$ | round 7, positioning note section 2.2 last paragraph and section 5 row 3, explainer Part C row 3 |

## 3. Search protocol (P1)

**First pass.** One subagent per theme, run in parallel, each one model tier below the oversight chat's model at medium effort.

| Theme | Claims | What it searches |
|---|---|---|
| T1 | C1, C3, C12 | model-assisted and difference estimation with machine-learned predictions, cross-fitting and sample splitting under design-based inference, finite-population corrections, two-stage and cluster sampling |
| T2 | C0, C1, C2, C9 | design-based PPI, PPI under survey, cluster or few-cluster designs, small-sample or cluster-robust corrections for PPI, from 2023 |
| T3 | C2, C4, C11 | optimal allocation in two-stage sampling with auxiliary information or regression estimators and costs, and labelling-budget allocation for PPI and active inference |
| T4 | C0, C5 to C8 | rejective, balanced and cube sampling of clusters or primary units and its variance estimation, balancing on predictions, adaptive or active selection of clusters with design-based inference, and inference after deterministic or coreset selection |
| T5 | C10, C11 | conformal prediction for a new group with few labelled target points, hierarchical and clustered conformal prediction, and work citing GHCP |

**Second pass.** Because Nicolas put thoroughness first (19 October), a second, independent pass follows at high effort, one tier below the oversight chat's model. It is seeded with every reference the earlier checks recorded (round 4's originality check, the deck-2 literature check, round 7's overlap check and positioning note) and with the backward citations of every paper the oversight chat reads in full. It also searches by name the classical sources the independent check listed for each claim (the separate and combined regression estimators, stratified against cluster sampling with costs, the optimum cluster size in two-stage sampling, degrees of freedom with few primary units, rejective sampling in Hájek's sense and in the Mahalanobis sense, inclusion probabilities estimated by simulation, measurability and the Sen-Yates-Grundy form, purposive selection, design-based supervised learning, few-shot conformal prediction). Each of those names is marked `[verify]` until a source is read.

**Recall test and stopping rule.** Every seed reference must be retrieved by the logged queries of one pass or the other, and a seed that is not is logged as a recall failure. A theme stops after two rounds of queries in a row with no new close paper.

**Sources.** Web search, arXiv listings (stat.ME, stat.ML, math.ST, stat.CO), the survey journals (Survey Methodology, Journal of Survey Statistics and Methodology, International Statistical Review, Journal of Official Statistics), the general statistics journals (Biometrika, JASA, JRSS A and B, Annals of Statistics, Statistical Science), the Joint Statistical Meetings' survey research methods proceedings, the Journal of Econometrics for few-cluster inference, and the ML venues. Where a citation service is reachable, the forward citations of the anchor papers, which are Angelopoulos et al. 2023 (PPI), Angelopoulos, Duchi and Zrnic (PPI++), Broska and Howes, Kluger et al., Chen et al. (Balanced Active Inference), Breidt and Opsomer 2017, Mozer 2026, Fuller 2009 on rejective sampling, Deville and Tillé 2004 on the cube method, Lee, Barber and Willett, and the GHCP paper. When no citation service is reachable from the cloud session, the fallback is the arXiv HTML reference lists of the papers read in full, read through the browser on Nicolas's Mac.

**Window.** PPI-side work from 2023, and semi-supervised and surrogate inference from 2000. Anything after round 7's check of 13 October is flagged. Survey-side work at any date, since a classical result decides a claim as surely as a new one.

**Logging.** Each pass writes `search_log.csv` (theme, query, source, date, number of hits kept) and `candidates.csv` (theme, claims, authors, title, venue or arXiv number, date, link, whether full text is open, closeness, what it holds). Closeness is graded close (may hold a claim or part of one), related (same problem, different setting), or background, and a grade from an abstract alone is provisional. The oversight chat merges both passes and regrades every close paper itself. The merged files go to `results/round8/positioning/P1_search/` through the gate's pull request.

**Papers not readable in full.** Those graded close that the oversight chat cannot read go to Nicolas as one list of at most 10, each with a link through UNC Chapel Hill's library proxy, or to a free version where UNC's access is not available. If more than 10 are unreadable, the list is ranked by how directly each bears on a claim, and the rest are graded from their abstracts with that limit stated in the note.

## 4. Full reading (P2)

The oversight chat reads in full every paper graded close, starting with the four named in the masterplan, and the classical sources each verdict rests on. Subagents do not read for verdicts. For each close paper the note records its setting, estimator, variance, design, sample sizes, and exactly which claim it touches and how.

## 5. Verdicts (P3)

Each claim receives one of these.

- **Prior art.** The claim is in print in the same setting. The paper cites it and does not claim it.
- **Classical.** The claim follows from a standard survey-sampling or conformal result. The paper states it as that result read in its setting.
- **Partly held.** Part of the claim is in print. The note says which part remains, and in what setting.
- **The paper's own.** Nothing found holds it, within the search logs. The note says how far the search went, so the verdict is bounded by the logs.

Every verdict that compares formulas shows both formulas and the step between them, in the form of `docs/round07/oversight/round07_ppi_positioning.md`, section 2.2. The predictions P.1 to P.5 of the masterplan are scored as its "How they are scored" paragraph fixes, each as held, partly held, refuted or not tested.

## 6. Output

- The note, `docs/round08/i01/positioning/round08_positioning_note.md`, with what was read, a section per close paper, a verdict table over C0 to C12, the predictions scored, what this means for Q3, R7-5, R7-6, R7-7 and R8-1, and a recommendation marked `[proposed]`.
- The merged search outputs and any `.verify-exceptions-positioning` lines, in one oversight pull request at the gate.
- A fresh agent at the oversight chat's tier checks the note against the papers and the repository before it is committed. Its findings are worked in before commit, as the row "An independent checker agent on high-stakes memos" of the guardrails register in `docs/WAYS_OF_WORKING.md` requires.
- Nicolas's decisions after his review go in `docs/round08/i02/positioning/round08_positioning_P3_decisions.md`.
