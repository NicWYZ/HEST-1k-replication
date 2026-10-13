# Round 7, federated learning for expression prediction, and the PPI paper's positioning (from 13 October 2026)

The advisor meeting of 12 October added a second line of work. David argued that predicting expression from foundation-model embeddings of H&E has reached a bottleneck, and proposed a textual knowledge base written by agents. Dr. Zhu proposed federated learning instead. Nicolas's assignment is a literature review of the viability of federated learning for this problem, toward a proof-of-concept methods paper. Before the PPI paper resumes, an overlap check against a lab manuscript and the newer literature found that the paper's direction stands but its claims of novelty must be repositioned. The plan is `masterplan.md`.

**Tracks.** fedlearn (branch `round7-fedlearn`, stages F0 to F4, run by a Claude Science session with sub-agents, computation on Longleaf). ppi (branch `round7-ppi`, stages S0 to S5, opened on 13 October after Nicolas accepted the reframed question, run by a Claude Science session, computation on Longleaf). **Starts from** `main` at the commit that carries the masterplan and the fedlearn instruction.

## Gates

| Date | Track | Gate | Report | Answered by | Tag | Pull request |
|---|---|---|---|---|---|---|

## Documents

| Document | Date | Role |
|---|---|---|
| `00_prep/round07_advisor_directions.md` | 13 Oct | record of the advisor meeting of 12 October, with David's textual knowledge base, Dr. Zhu's federated learning, Nicolas's assignment, and what the project already holds that bears on both |
| `00_prep/round07_overlap_check.md` | 13 Oct | public version of the overlap check of the PPI paper against an unpublished lab manuscript on slide selection and the newer PPI literature. The full check is in the private claude.ai project docs at `claude/round07_overlap_check_full.md` |
| `masterplan.md` | 13 Oct, living | the round's plan, with the tracks, the schedule, the open questions and amendments |
| `i01/fedlearn/round07_fedlearn_track.md` | 13 Oct, living | instruction for the fedlearn track, with the review's nine questions, the starting points, the sub-agent themes, stages F0 to F4, the rule for papers that cannot be retrieved, and predictions F.1 to F.10 |
| `oversight/round07_ppi_positioning.md` | 13 Oct | the PPI paper's positioning after a full reading of Broska and Howes, Chen et al. and the cluster parts of Kluger et al., with what the paper can claim and a recommendation on O2 |
| `i01/ppi/round07_ppi_track.md` | 13 Oct, living | instruction for the inference track, with inclusion-probability weighting under rejective selection, Broska and Howes's and Kluger et al.'s comparators, a cluster-level balanced adaptive design, the k-center check, stages S0 to S5 and predictions S1.1 to S4.2 |

## Corrections recorded this round

- The originality check of 28 September (`docs/round04/00_prep/round4_originality_check.md`, section 1) said that nobody had treated PPI under cluster sampling. Kluger, Lu, Zrnic, Wang and Bates (arXiv:2501.18577, January 2025) had already given bootstrap intervals for PPI under clustered designs, and the deck-2 literature check of 4 October recorded them (`docs/round05/00_prep/deck2/deck2_literature_check.md`). Broska and Howes (arXiv:2610.09601, 7 October 2026) now give cluster-robust PPI++. The originality check is frozen, so this is recorded here and in `00_prep/round07_overlap_check.md`, section 3.
- The overlap check (`00_prep/round07_overlap_check.md`, section 3) listed the gain theorem among what remains the paper's own. Its endpoint and the shrunken coefficient follow from Broska and Howes's appendix C at whole-cluster labelling, as from the classical survey-sampling variance. Round 4's condition for regime B to win on the between-cluster term (`docs/round04/tracks/ppi/round4_ppi_theory.md`, section 4.3) leaves out the unlabelled clusters' term, and with it regime B never loses on that term. Both are recorded in `oversight/round07_ppi_positioning.md`, sections 2.2 and 2.3.
