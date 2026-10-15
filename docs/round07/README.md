# Round 7, federated learning for expression prediction, and the PPI paper's positioning (13 to 15 October 2026, closed)

The advisor meeting of 12 October added a second line of work. David argued that predicting expression from foundation-model embeddings of H&E has reached a bottleneck, and proposed a textual knowledge base written by agents. Dr. Zhu proposed federated learning instead. Nicolas's assignment is a literature review of the viability of federated learning for this problem, toward a proof-of-concept methods paper. Before the PPI paper resumes, an overlap check against a lab manuscript and the newer literature found that the paper's direction stands but its claims of novelty must be repositioned. The plan is `masterplan.md`.

**Tracks.** fedlearn (branch `round7-fedlearn`, stages F0 to F4, run by a Claude Science session with sub-agents, computation on Longleaf). ppi (branch `round7-ppi`, stages S0 to S5, opened on 13 October after Nicolas accepted the reframed question, run by a Claude Science session, computation on Longleaf). **Starts from** `main` at the commit that carries the masterplan and the fedlearn instruction.

## Gates

| Date | Track | Gate | Report | Answered by | Tag | Pull request |
|---|---|---|---|---|---|---|
| 13 Oct | fedlearn | F2 | `i01/fedlearn/round07_fedlearn_F2_report.md` | `i02/fedlearn/round07_fedlearn_F2_decisions.md` | `round7-fedlearn-F2` | #28 |
| 14 Oct | fedlearn | F4, end of track | `i02/fedlearn/round07_fedlearn_final_report.md` | `i03/fedlearn/round07_fedlearn_final_decisions.md` | `round7-fedlearn-final` | #30 |
| 14 Oct | ppi | S2 | `i01/ppi/round07_ppi_S2_report.md` | `i02/ppi/round07_ppi_S2_decisions.md` | `round7-ppi-S2` | #29 |
| 14 Oct | ppi | S4 | `i02/ppi/round07_ppi_S4_report.md` | `i03/ppi/round07_ppi_S4_decisions.md` | `round7-ppi-S4` | #31 |
| 15 Oct | ppi | S5, end of track | `i03/ppi/round07_ppi_final_report.md` | `i04/ppi/round07_ppi_final_decisions.md` | `round7-ppi-final` | #32 |


## Documents

In folder order. Living documents were frozen at the round's close on 15 October.

| Document | Date | Role |
|---|---|---|
| `00_prep/round07_advisor_directions.md` | 13 Oct | record of the advisor meeting of 12 October, with David's textual knowledge base, Dr. Zhu's federated learning, Nicolas's assignment, and what the project already holds that bears on both |
| `00_prep/round07_overlap_check.md` | 13 Oct | public version of the overlap check of the PPI paper against an unpublished lab manuscript on slide selection and the newer PPI literature. The full check is in the private claude.ai project docs at `claude/round07_overlap_check_full.md` |
| `masterplan.md` | 13 Oct, frozen at close | the round's plan, with the tracks, the schedule, the open questions and amendments |
| `i01/fedlearn/round07_fedlearn_F2_report.md` | 13 Oct | report at the F2 gate (F0 to F2), with the search, the citation audit, the inventory and the proposal for interval 2 |
| `i01/fedlearn/round07_fedlearn_track.md` | 13 Oct, frozen at close | instruction for the fedlearn track, with the review's nine questions, the starting points, the sub-agent themes, stages F0 to F4, the rule for papers that cannot be retrieved, and predictions F.1 to F.10 |
| `i01/ppi/round07_ppi_S2_report.md` | 14 Oct | report at the S2 gate (S0 to S2), with the anchors, weighting under rejective selection, the comparators from the literature, and the disagreement with round 5 on $\theta_2$ |
| `i01/ppi/round07_ppi_track.md` | 13 Oct, frozen at close | instruction for the inference track, with inclusion-probability weighting under rejective selection, Broska and Howes's and Kluger et al.'s comparators, a cluster-level balanced adaptive design, the k-center check, stages S0 to S5 and predictions S1.1 to S4.2 |
| `i02/fedlearn/round07_fedlearn_F2_decisions.md` | 13 Oct | decision at F2. Accepted, the shared-queue revision carried in full, a center may be a study, V1 and V2 as proposed, V3 (privacy cost) and V4 (partial gene overlap) added, predictions F.11 and F.12 |
| `i02/fedlearn/round07_fedlearn_final_report.md` | 14 Oct | closing report of the fedlearn track (F3 and F4), with the exact federated head, the learning curve, the simulated and real federations, the cost of spot-level differential privacy and of partial gene overlap, revised verdicts and the closing page |
| `i02/ppi/round07_ppi_S2_decisions.md` | 14 Oct | decision at S2. Accepted, weighting under D2 recorded as a negative result with its mechanism, the fallback explanation of the $\theta_2$ disagreement refuted from round 5's files, and interval i02 fixed as S2b (a $\theta_2$ replay, the simulation bias by population, Broska and Howes with small-sample corrections), S3 and S4 |
| `i02/ppi/round07_ppi_S4_report.md` | 14 Oct | report at the S4 gate (S2b, S3, S4), with the $\theta_2$ recount, Broska and Howes with small-sample corrections, the cube design and the mixture of D2 and D0, and greedy k-center |
| `i03/fedlearn/round07_fedlearn_final_decisions.md` | 14 Oct | decision at F4. Accepted and the track closed, six readings for the record, the reuse rule for named inputs, and the paper's direction left to Nicolas and his advisors as R7-4 |
| `i03/ppi/round07_ppi_S4_decisions.md` | 14 Oct | decision at S4. Accepted. On matched, supported cells the cube design matches or beats `rej_t` on tissue and loses on census, the mixture is a control rather than a candidate, k-center is a negative result, and the project's correction of Broska and Howes's interval is a strong comparator at four labelled clusters. Interval i03 adds S4b, the cube design with the constant balanced to test why it loses on census, then S5 |
| `i03/ppi/round07_ppi_final_report.md` | 15 Oct | closing report of the inference track (S4b and S5), with the cube design balanced also on the constant, every design and comparator on matched supported cells, and the closing page |
| `i04/ppi/round07_ppi_final_decisions.md` | 15 Oct | decision at the closing gate. Accepted and the track closed, nine readings for the record, and three decisions for Nicolas (R7-5, R7-6, R7-7) |
| `oversight/round07_fedlearn_decision_report.md` | 14 Oct | report for Nicolas on how to proceed with federated learning, with the concepts (federated learning, the one-round head, differential privacy), what the review established, the results and the decisions to make |
| `oversight/round07_ppi_positioning.md` | 13 Oct | the PPI paper's positioning after a full reading of Broska and Howes, Chen et al. and the cluster parts of Kluger et al., with what the paper can claim and a recommendation on O2 |
| `oversight/round07_ppi_results_explained.md` | 15 Oct | the PPI paper's results explained after round 7, replacing the round-5 explainer, with the status of each round-5 result, what round 7 added, what published work now holds, and the open decisions |
| `tracks/fedlearn/round07_fedlearn_literature_review.md` | 13 to 14 Oct, frozen at close | the literature review, with the nine questions, graded evidence, verdicts on the routes and concepts, and the novelty statement |
| `tracks/fedlearn/round07_fedlearn_plan.md` | 13 to 14 Oct, frozen at close | the fedlearn session's operating plan |
| `tracks/ppi/round07_ppi_plan.md` | 14 to 15 Oct, frozen at close | the inference session's operating plan |
| `tracks/ppi/round07_ppi_theory.md` | 14 to 15 Oct, frozen at close | the inference track's theory, with the weighted estimators under D2, why zero pair probabilities break the Sen-Yates-Grundy form, and Broska and Howes's and Kluger et al.'s intervals for whole labelled clusters |

## What the round established

**The PPI paper (track ppi, `i04/ppi/round07_ppi_final_decisions.md`, section 2, explained in `oversight/round07_ppi_results_explained.md`).**

- Weighting the labelled clusters by simulated inclusion probabilities under rejective selection fails. Some clusters are almost never accepted ($\hat\pi_g = 0$ from 100,000 draws in 225 of 1336 real-task cells) and many pairs never appear together, so the Horvitz-Thompson and Hájek means are biased or unstable and the Sen-Yates-Grundy variance loses terms (`i02/ppi/round07_ppi_S2_decisions.md`, section 2).
- On cells matched across designs with enough support, rejective selection with `rej_t` is the narrowest valid interval on census, at 0.456 of simple random selection's width at $n_L = 8$. On tissue it covers 0.861 against 0.875 for simple random selection, and a cube design is as narrow and covers better (`i04/ppi/round07_ppi_final_decisions.md`, section 2 items 2 and 3).
- A cube design with inclusion probabilities bounded below by half of $n_L/G$, balanced on $\pi_g$, the constant and $\bar f_g$, with the Hájek mean and the Sen-Yates-Grundy variance, covers like simple random selection on both domains at $n_L \ge 6$. Balancing the constant halved its census width, from 0.912 to 0.568 (same memo, item 3).
- The mixture of rejective and simple random selection is a valid control that keeps none of balance's width gain on tissue, and greedy k-center is a negative result, with exact coverage of the classical interval down to 0.326 on kidney cancer (same memo, items 4 and 5).
- Broska and Howes's published interval under-covers at four labelled clusters (0.704 on tissue), and Kluger et al.'s cluster bootstrap under-covers at these cluster counts. With the project's small-sample correction, Broska and Howes's interval covers 0.884 at four labelled clusters and is narrower there than the paper's tuned interval (same memo, items 6 and 7).
- Round 5's worst `rej_t` cells were draws with no interval, which round 5 counted as misses (same memo, item 9).
- The paper's own ground, after the full reading of Broska and Howes, Kluger et al. and Chen et al., is the design target with the finite-population factor and cross-fitting term, the design questions (regime comparison for the design target, costs, which clusters to label) and the prediction-set map. The gain formula and the superpopulation regime comparison are held by published work (`oversight/round07_ppi_positioning.md`, section 5, updated in `oversight/round07_ppi_results_explained.md`, Part C).

**Federated learning (track fedlearn, `i03/fedlearn/round07_fedlearn_final_decisions.md`, section 2, and `oversight/round07_fedlearn_decision_report.md`).**

- The literature has one federated study of expression from histology and no method that fits a head on frozen pathology embeddings from per-center sums. The algebra of such a head is established elsewhere, so novelty could rest only on the application (`tracks/fedlearn/round07_fedlearn_literature_review.md`, section 12).
- The one-round head from per-center sums equals the pooled fit to $7.6 \times 10^{-15}$ and reproduces round 1's benchmark.
- Accuracy rises steeply to 4 to 8 training donors and slowly after. Pooling helps by 0.016 to 0.038 when centers differ only in donors, and not clearly across real sources.
- Spot-level differential privacy costs 0.0225 at $\varepsilon = 10$ and 0.107 at $\varepsilon = 1$ against 0.219. Fitting each gene only from the centers that measure it costs 0.010 to 0.023, and the literature has no method for it.

## Corrections and withdrawn readings

- The originality check of 28 September (`docs/round04/00_prep/round4_originality_check.md`, section 1) said that nobody had treated PPI under cluster sampling. Kluger, Lu, Zrnic, Wang and Bates (arXiv:2501.18577, January 2025) had already given bootstrap intervals for PPI under clustered designs, and the deck-2 literature check of 4 October recorded them (`docs/round05/00_prep/deck2/deck2_literature_check.md`). Broska and Howes (arXiv:2610.09601, 7 October 2026) now give cluster-robust PPI++. The originality check is frozen, so this is recorded here and in `00_prep/round07_overlap_check.md`, section 3.
- The overlap check (`00_prep/round07_overlap_check.md`, section 3) listed the gain theorem among what remains the paper's own. Its endpoint and the shrunken coefficient follow from Broska and Howes's appendix C at whole-cluster labelling, as from the classical survey-sampling variance. Round 4's condition for regime B to win on the between-cluster term (`docs/round04/tracks/ppi/round4_ppi_theory.md`, section 4.3) leaves out the unlabelled clusters' term, and with it regime B never loses on that term. Both are recorded in `oversight/round07_ppi_positioning.md`, sections 2.2 and 2.3.
- Round 5's closing memo (`docs/round05/i04/ppi/round5_ppi_E5_decisions.md`, section 3 item 3) says the rejective design failed with two balance variables at few residual degrees of freedom, from eight Indiana $\theta_2$ cells at $n_L = 6$. The statement stands, and round 7 adds its mechanism. For $\theta_2$, `rej_t` forms no interval when the valid labelled clusters leave fewer than 2 residual degrees of freedom, which happens in about a quarter of those cells' draws, and round 5 counted such draws as misses. The intervals that are formed cover 0.86 to 0.89 (`i02/ppi/round07_ppi_S2_decisions.md`, section 3). Every $\theta_2$ coverage is now reported with the share of draws that formed an interval.
- The S4 memo (`i03/ppi/round07_ppi_S4_decisions.md`, section 2) gave D0 classical a coverage of 0.903 on the 12 supported tissue cells at $n_L = 4$ and $p_a = 0.1$. Counting draws without an interval as misses, as that memo required of every row, it is 0.874. The 0.903 was the coverage over formed draws (`i04/ppi/round07_ppi_final_decisions.md`, section 3).
- The S2 memo's first version (`i02/ppi/round07_ppi_S2_decisions.md`, revision of 14 October) explained the disagreement with round 5 as a fallback in round 5's selection. Round 5's own diagnostics show no fallback, and an independent check found the counting difference before the memo was handed over.
- The S4 memo's first version (`i03/ppi/round07_ppi_S4_decisions.md`, revision of 14 October) compared designs on unmatched cells and kept `rej_t` as narrowest on tissue, and explained the cube design's census loss by its landing phase. Both were reversed before handover, on matched supported cells and on the balance residuals.
- The S4 report's proposal of the mixture as the paper's candidate was not accepted. The mixture is a control (`i03/ppi/round07_ppi_S4_decisions.md`, section 2).
- Predictions refuted this round include F.9, F.11 (partly) and F.12 on federated learning, S2.2, S3.2, S3.4, S3.5 and S4b.3 on inference, all scored in their reports.

## Carried forward

- **Decisions that are Nicolas's,** in `CLAUDE.md`. R7-4, whether federated learning becomes a paper and its first method (with Dr. Zhu and David). R7-5, the PPI paper's positioning against the corrected Broska and Howes interval (with David). R7-6, whether the tuned estimator uses a global coefficient below six labelled clusters. R7-7, which balanced design the paper recommends. Q3, which result the paper leads with.
- **The positioning note** (`oversight/round07_ppi_positioning.md`) is revised once R7-5 is decided.
- **If the federated learning paper goes ahead,** its first interval runs three cheap checks from the closing report, section 8 (the split of the privacy cost between noise and penalty, partial overlap gene by gene, the intercept loss against center size), and adds a metric that pools test centers or mean squared error.
- **Unfinished from the ppi track,** listed in its final report, section 10: the superpopulation target for the cube designs, every result that took one score, $\tau$, $\epsilon$ or skewed law, why $\hat N$ misses $G$, and the lung $\theta_2$ ties.
- **Oversight housekeeping.** Branch `oversight-round7-positioning-exceptions` holds three `.verify-exceptions` lines for the positioning note and needs a pull request. The numeric checker misses comma-grouped integers in free-text CSV cells (step R7.6 in `CLAUDE.md`).
- **The first question for round 8** is Nicolas's choice between writing the PPI paper on what rounds 4 to 7 established, after deciding R7-5 to R7-7, and opening federated learning work if R7-4 says so.

## Read first next round

- `oversight/round07_ppi_results_explained.md`, the current account of the PPI paper's results.
- `i04/ppi/round07_ppi_final_decisions.md` and `oversight/round07_ppi_positioning.md`, for what the paper can claim.
- `oversight/round07_fedlearn_decision_report.md`, if federated learning goes ahead.
- `docs/round05/tracks/ppi/round5_ppi_estimator_definition.md`, the paper's estimator.
