# Round 7, federated learning for expression prediction, and the PPI paper's positioning (from 13 October 2026)

The advisor meeting of 12 October added a second line of work. David argued that predicting expression from foundation-model embeddings of H&E has reached a bottleneck, and proposed a textual knowledge base written by agents. Dr. Zhu proposed federated learning instead. Nicolas's assignment is a literature review of the viability of federated learning for this problem, toward a proof-of-concept methods paper. Before the PPI paper resumes, an overlap check against a lab manuscript and the newer literature found that the paper's direction stands but its claims of novelty must be repositioned. The plan is `masterplan.md`.

**Tracks.** fedlearn (branch `round7-fedlearn`, stages F0 to F4, run by a Claude Science session with sub-agents, computation on Longleaf). ppi (branch `round7-ppi`, stages S0 to S5, opened on 13 October after Nicolas accepted the reframed question, run by a Claude Science session, computation on Longleaf). **Starts from** `main` at the commit that carries the masterplan and the fedlearn instruction.

## Gates

| Date | Track | Gate | Report | Answered by | Tag | Pull request |
|---|---|---|---|---|---|---|
| 13 Oct | fedlearn | F2 | `i01/fedlearn/round07_fedlearn_F2_report.md` | `i02/fedlearn/round07_fedlearn_F2_decisions.md` | `round7-fedlearn-F2` | #28 |
| 14 Oct | fedlearn | F4, end of track | `i02/fedlearn/round07_fedlearn_final_report.md` | `i03/fedlearn/round07_fedlearn_final_decisions.md` | `round7-fedlearn-final` | #30 |
| 14 Oct | ppi | S2 | `i01/ppi/round07_ppi_S2_report.md` | `i02/ppi/round07_ppi_S2_decisions.md` | `round7-ppi-S2` | #29 |

## Documents

| Document | Date | Role |
|---|---|---|
| `00_prep/round07_advisor_directions.md` | 13 Oct | record of the advisor meeting of 12 October, with David's textual knowledge base, Dr. Zhu's federated learning, Nicolas's assignment, and what the project already holds that bears on both |
| `00_prep/round07_overlap_check.md` | 13 Oct | public version of the overlap check of the PPI paper against an unpublished lab manuscript on slide selection and the newer PPI literature. The full check is in the private claude.ai project docs at `claude/round07_overlap_check_full.md` |
| `masterplan.md` | 13 Oct, living | the round's plan, with the tracks, the schedule, the open questions and amendments |
| `i01/fedlearn/round07_fedlearn_track.md` | 13 Oct, living | instruction for the fedlearn track, with the review's nine questions, the starting points, the sub-agent themes, stages F0 to F4, the rule for papers that cannot be retrieved, and predictions F.1 to F.10 |
| `oversight/round07_ppi_positioning.md` | 13 Oct | the PPI paper's positioning after a full reading of Broska and Howes, Chen et al. and the cluster parts of Kluger et al., with what the paper can claim and a recommendation on O2 |
| `i01/ppi/round07_ppi_track.md` | 13 Oct, living | instruction for the inference track, with inclusion-probability weighting under rejective selection, Broska and Howes's and Kluger et al.'s comparators, a cluster-level balanced adaptive design, the k-center check, stages S0 to S5 and predictions S1.1 to S4.2 |
| `i01/fedlearn/round07_fedlearn_F2_report.md` | 13 Oct | report at the F2 gate (F0 to F2), with the search, the citation audit, the inventory and the proposal for interval 2 |
| `i02/fedlearn/round07_fedlearn_F2_decisions.md` | 13 Oct | decision at F2. Accepted, the shared-queue revision carried in full, a center may be a study, V1 and V2 as proposed, V3 (privacy cost) and V4 (partial gene overlap) added, predictions F.11 and F.12 |
| `tracks/fedlearn/round07_fedlearn_plan.md` | 13 to 14 Oct | the fedlearn session's operating plan |
| `tracks/fedlearn/round07_fedlearn_literature_review.md` | 13 to 14 Oct | the literature review, with the nine questions, graded evidence, verdicts on the routes and concepts, and the novelty statement |
| `i02/fedlearn/round07_fedlearn_final_report.md` | 14 Oct | closing report of the fedlearn track (F3 and F4), with the exact federated head, the learning curve, the simulated and real federations, the cost of spot-level differential privacy and of partial gene overlap, revised verdicts and the closing page |
| `i03/fedlearn/round07_fedlearn_final_decisions.md` | 14 Oct | decision at F4. Accepted and the track closed, six readings for the record, the reuse rule for named inputs, and the paper's direction left to Nicolas and his advisors as R7-4 |
| `tracks/ppi/round07_ppi_plan.md` | 13 Oct, living | the inference session's operating plan |
| `tracks/ppi/round07_ppi_theory.md` | 13 Oct, living | the inference track's theory, with the weighted estimators under D2, why zero pair probabilities break the Sen-Yates-Grundy form, and Broska and Howes's and Kluger et al.'s intervals for whole labelled clusters |
| `i01/ppi/round07_ppi_S2_report.md` | 14 Oct | report at the S2 gate (S0 to S2), with the anchors, weighting under rejective selection, the comparators from the literature, and the disagreement with round 5 on $\theta_2$ |
| `i02/ppi/round07_ppi_S2_decisions.md` | 14 Oct | decision at S2. Accepted, weighting under D2 recorded as a negative result with its mechanism, the fallback explanation of the $\theta_2$ disagreement refuted from round 5's files, and interval i02 fixed as S2b (a $\theta_2$ replay, the simulation bias by population, Broska and Howes with small-sample corrections), S3 and S4 |

## Corrections recorded this round

- The originality check of 28 September (`docs/round04/00_prep/round4_originality_check.md`, section 1) said that nobody had treated PPI under cluster sampling. Kluger, Lu, Zrnic, Wang and Bates (arXiv:2501.18577, January 2025) had already given bootstrap intervals for PPI under clustered designs, and the deck-2 literature check of 4 October recorded them (`docs/round05/00_prep/deck2/deck2_literature_check.md`). Broska and Howes (arXiv:2610.09601, 7 October 2026) now give cluster-robust PPI++. The originality check is frozen, so this is recorded here and in `00_prep/round07_overlap_check.md`, section 3.
- The overlap check (`00_prep/round07_overlap_check.md`, section 3) listed the gain theorem among what remains the paper's own. Its endpoint and the shrunken coefficient follow from Broska and Howes's appendix C at whole-cluster labelling, as from the classical survey-sampling variance. Round 4's condition for regime B to win on the between-cluster term (`docs/round04/tracks/ppi/round4_ppi_theory.md`, section 4.3) leaves out the unlabelled clusters' term, and with it regime B never loses on that term. Both are recorded in `oversight/round07_ppi_positioning.md`, sections 2.2 and 2.3.
- Round 5's closing memo (`docs/round05/i04/ppi/round5_ppi_E5_decisions.md`, section 3 item 3) says the rejective design failed with two balance variables at few residual degrees of freedom, from eight Indiana $\theta_2$ cells at $n_L = 6$. The statement stands, and round 7 adds its mechanism. For $\theta_2$, `rej_t` forms no interval when the valid labelled clusters leave fewer than 2 residual degrees of freedom, which happens in about a quarter of those cells' draws, and round 5 counted such draws as misses. The intervals that are formed cover 0.86 to 0.89 (`i02/ppi/round07_ppi_S2_decisions.md`, section 3). Every $\theta_2$ coverage is now reported with the share of draws that formed an interval.

## Carried from the fedlearn track

If the federated learning paper goes ahead (R7-4), the first interval of its track runs three cheap checks from the closing report, section 8. They are the split of the privacy cost between the noise and the added penalty, the cost of partial gene overlap gene by gene against the number of centers that measure each gene, and the pseudo-center intercept loss against center size. It also adds a metric that pools test centers, or mean squared error, before any claim about intercepts or centring.
