# Round 7, federated learning for expression prediction, and the PPI paper's positioning (from 13 October 2026)

The advisor meeting of 12 October added a second line of work. David argued that predicting expression from foundation-model embeddings of H&E has reached a bottleneck, and proposed a textual knowledge base written by agents. Dr. Zhu proposed federated learning instead. Nicolas's assignment is a literature review of the viability of federated learning for this problem, toward a proof-of-concept methods paper. Before the PPI paper resumes, an overlap check against a lab manuscript and the newer literature found that the paper's direction stands but its claims of novelty must be repositioned. The plan is `masterplan.md`.

**Tracks.** fedlearn (branch `round7-fedlearn`, stages F0 to F4, run by a Claude Science session with sub-agents, computation on Longleaf). ppi, to be opened by an amendment after the positioning note if Nicolas accepts the reframed question. **Starts from** `main` at the commit that carries the masterplan and the fedlearn instruction.

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

## Corrections recorded this round

- The originality check of 28 September (`docs/round04/00_prep/round4_originality_check.md`, section 1) said that nobody had treated PPI under cluster sampling. Kluger, Lu, Zrnic, Wang and Bates (arXiv:2501.18577, January 2025) had already given bootstrap intervals for PPI under clustered designs, and the deck-2 literature check of 4 October recorded them (`docs/round05/00_prep/deck2/deck2_literature_check.md`). Broska and Howes (arXiv:2610.09601, 7 October 2026) now give cluster-robust PPI++. The originality check is frozen, so this is recorded here and in `00_prep/round07_overlap_check.md`, section 3.
