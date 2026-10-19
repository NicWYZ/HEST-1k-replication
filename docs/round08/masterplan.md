# Round 8, masterplan

*Living while the round runs. The oversight chat revises it by appending dated amendments at the end, and the text above them is not rewritten. It is frozen at the round's close.*

Written on 19 October 2026 by the oversight chat, through the `project-state-keeping` skill, after Nicolas chose the round's direction in chat the same day. The scope of the one track opened now is `i01/positioning/round08_positioning_scope.md`. A fresh agent checked this masterplan and the scope before the first commit, and its findings are worked in.

## Why this round

Round 7 closed on 15 October (`docs/round07/README.md`). Its PPI track finished the design questions round 5 had left open, and its reading of Broska and Howes, Kluger et al. and Chen et al. narrowed what the paper "Labelling budgets for prediction-powered inference with clustered data" can claim as its own. The gain theorem and the superpopulation comparison of the two labelling regimes are held by published work. The paper also cannot claim the few-cluster regime in general, because a simple small-sample correction of Broska and Howes's interval, made by the project, covers at four labelled clusters. What remains the paper's own is listed in `docs/round07/oversight/round07_ppi_results_explained.md`, Part C, with allocation in Part B. It is the finite-population factor and the cross-fitting term of the design-target interval, the cluster-level reading and design-target version of the gain formula, the design-target regime comparison with costs and the level term, the allocation between clusters and units per cluster, the few-cluster comparison of balanced designs with its two negative results, and the prediction-set map.

Round 7's searches were on the PPI side of the literature. On 19 October, before this round opened, the oversight chat ran a few searches toward the survey-sampling side and found four papers bearing, by their abstracts, on the claims above. Three are new to the project. The fourth, Shirota's, was found in round 3 and checked from its abstract in the deck-2 literature check of 4 October (`docs/round05/00_prep/deck2/deck2_literature_check.md`, sections 2 and 6), which said it needed a full read.

- Shirota, "Design-Based Prediction-Powered Inference for Spatial Data", arXiv:2608.10356, August 2026. Design-based PPI for a fixed spatial population, exact design variances under simple and stratified sampling, a condition for when spatially balanced sampling improves precision, an optimal spatial allocation of labels, and inference with estimated selection propensities when selection depends on the prediction map. It bears on the design-target framing, on allocation and on inference after prediction-guided selection.
- An, Dagdoug, Haziza and Tillé, "Agnostic Model-Assisted Estimation with Machine Learning for Survey Data", arXiv:2609.10904, September 2026. Cross-fitting in model-assisted survey estimation, the sampling designs under which the folds are independent, and variance estimators from cross-fitted residuals. It bears on the cross-fitting term of the design-target interval.
- Riaño, "Model-assisted estimation with a training subsample: a two-phase sampling approach with design-based variance estimation", arXiv:2609.04082, September 2026. It treats the training split as a second phase of sampling and estimates the variance that split adds. It bears on the same term.
- Ma and Candès, "Optimized Labeling Resource Allocation for Prediction-Assisted Inference via OPAL", arXiv:2606.03211, June 2026. Labelling-budget allocation for prediction-assisted inference, from the active-inference side. It bears on the allocation result and on the paper's title.

Hard rule 8 forbids a claim of novelty without a literature check, and the paper should not be planned on claims that may already be published. So Nicolas decided on 19 October that the round starts with a positioning check, and that the paper plan, any execution track and the advisor deck follow from what survives. He said that thoroughness always comes first. He also said that his next advisor meeting will be about the other lines of work (federated learning and the textual knowledge base).

## Goal

A verdict for every remaining claim of the PPI paper against the survey-sampling literature and the PPI literature up to the date of the check, with derivations wherever two formulas are compared. Then a plan for the paper built only on what survives, and a short execution track for the gaps that plan needs. The round gives Nicolas a settled positioning to take to David (the groundwork for O5 and R7-5), the evidence he needs to choose the paper's main result with his advisors (Q3), and a list of the runs still missing.

## Tracks

**positioning,** opened now. An oversight track, done by the oversight chat itself in this claude.ai project, with Nicolas's review as its gate. Its documents go on `main` under the documentation rule. Its search logs and any `.verify-exceptions-positioning` lines are results, so they go to Nicolas as one oversight pull request at the P3 gate (`CLAUDE.md` section 1). Searches go to subagents one model tier below the oversight chat's model. Because Nicolas put thoroughness first, a second, independent search pass at high effort follows the first, seeded with every reference the earlier checks recorded and with the backward citations of the papers read in full. The full reading and every verdict stay with the oversight chat, and a fresh agent at the oversight chat's own tier checks the note before it is committed.

| Interval | Stages | Gate | What it delivers |
|---|---|---|---|
| i01 | P0 the scope and search protocol, P1 a systematic search in two passes with logged queries, P2 full reading of the closest papers and of the classical results, P3 the positioning note | P3, Nicolas's review | `i01/positioning/round08_positioning_note.md`, with a verdict per claim, the search logs for `results/round8/positioning/P1_search/` in the gate's pull request, and any papers Nicolas must supply |

Papers the oversight chat cannot read in full go to Nicolas as one list of at most 10, each with a link through UNC Chapel Hill's library proxy or to a free version, as in round 7. The tag proposed for the gate is `round8-positioning-P3` `[proposed]`.

**Later tracks, not opened now.** After the P3 review the oversight chat proposes, as amendments to this masterplan, an oversight track for the paper plan and an execution track on Longleaf for the runs the plan needs. Candidates for that track already known are R7-6 (a global coefficient below six labelled clusters, where the finite-population version of the corrected Broska and Howes interval, `bh_t_fpc`, is already known to under-cover), the superpopulation target for the cube designs, and the cube design's sensitivity to its score and to $\tau$ (`docs/round07/i03/ppi/round07_ppi_final_report.md`, sections 8 and 10). None of them is set up before the review.

**Outside this round.** Federated learning (R7-4) and David's textual knowledge base. The advisor deck is carried and is built after the positioning settles.

## Schedule

No date was set. The target is a submittable paper by spring 2027. The next advisor meeting will be about federated learning and the textual knowledge base, so no gate of this round is tied to it.

| When | What |
|---|---|
| Monday 19 October | this masterplan, the scope document and the round's reading guide on `main`. P1's first pass starts |
| after the first pass | the second search pass, then P2 |
| when P2 and P3 are done | the positioning note, checked by a fresh agent, then Nicolas's review and the gate's pull request |
| after the review | amendments that open the paper plan and the execution track |

## Predictions

Written on 19 October before any of the four papers was read beyond its abstract, and scored in the positioning note.

- **P.1** An, Dagdoug, Haziza and Tillé give a design-based variance for a cross-fitted model-assisted estimator that accounts for the dependence between folds drawn without replacement. So the substance of round 5's cross-fitting term is in print at the unit level. They do not treat clusters as the sampling units with 4 to 16 of them, nor a $t$ reference.
- **P.2** Shirota works with units (spatial cells) and with stratified or blocked designs, not with a few whole clusters, and has no small-sample correction. The paper's inference after map-dependent selection uses estimated propensities with a sandwich variance, not fixed-size rejective or cube selection with simulated inclusion probabilities.
- **P.3** OPAL allocates labels across strata or tasks to minimise variance, and does not split a budget between clusters and units within clusters with a cost per cluster and a cost per unit.
- **P.4** The optimal number of units per cluster for a regression estimator under two-stage sampling with costs is in the classical survey-sampling literature, so the form of round 5's allocation, $m^\star\sqrt{(1 - R^2_w)/\rho_c}$, is classical and what is the paper's own is its reading with a machine-learned predictor and the measured between ratio.
- **P.5** The systematic search finds at least one further paper from 2025 or 2026, not yet recorded in the repository, that bears on balanced or prediction-guided selection of clusters with design-based inference.

**How they are scored,** fixed on 19 October after the independent check and before any scoring. The text above is kept as written, since predictions are not rewritten after the reading has begun. P.1 is scored in three parts, (a) a design-based variance that accounts for the dependence between folds, (b) no clusters as sampling units with 4 to 16 of them, (c) no $t$ reference, and its "So" sentence is scored as a fourth part. The parts of P.2 about units and the absence of a small-sample correction repeat what the deck-2 check already recorded from Shirota's abstract, so only the part about estimated propensities against fixed-size rejective or cube selection counts as a prediction. P.3 counts as held only if OPAL has no two-level cost model with a cost per cluster and a cost per unit. P.4 named the wrong formula. The classical candidate is $m^\star\sqrt{(1 - R^2_w)/(1 - R^2_c)}$ (`docs/round05/tracks/ppi/round5_ppi_estimator_definition.md`, "Allocation"), and the replacement of $1 - R^2_c$ by the measured $\rho_c$ is the project's own, so P.4 is scored on whether the $(1 - R^2_c)$ form is classical. P.5 counts as held if at least one paper dated 2025 or 2026 is graded close for one of C0 or C5 to C8 and is not found by a search of the repository at the opening commit. Each prediction is scored as held, partly held, refuted or not tested.

## Open questions

| # | Question | Who decides | Default |
|---|---|---|---|
| R7-5 | The PPI paper's positioning against the corrected Broska and Howes interval | Nicolas, with David | the positioning note of round 7 with its banner |
| R7-6 | Whether the tuned estimator uses a global coefficient below six labelled clusters | Nicolas, after round 8's positioning note (said on 19 October) | round 5's estimator as defined |
| R7-7 | Which balanced design the paper recommends | Nicolas, with David | `[proposed]` `rej_t` where its support and one balance variable allow, the cube design with the constant balanced as the design-based alternative |
| Q3 | Which venue, and which result the paper leads with | Nicolas, with his advisors, after round 8's positioning note | open |
| O5 | The PPI paper's positioning, as in `docs/round07/oversight/round07_ppi_positioning.md`, section 5 | Nicolas, with David | the paper claims nothing that note marks as prior art, classical or implied, nor the few-cluster regime in general (its banner of 15 October) |
| R8-1 | Whether the prediction-set half stays in the PPI paper or becomes a separate paper | Nicolas, after round 8's positioning note (said on 19 October) | the decision waits |

## What closes the round

The positioning track's P3 review is done and its decisions recorded, and every track opened by amendment has its closing memo written and merged. Then the close check of the `project-state-keeping` skill runs.

## Amendments
