# Round 7, masterplan

*Living while the round runs. The oversight chat revises it by appending dated amendments at the end, and the text above them is not rewritten. It is frozen at the round's close.*

Written on 13 October 2026 by the oversight chat, after Nicolas confirmed the skeleton in chat the same day. The full instruction to the execution session of the one track opened now is `i01/fedlearn/round07_fedlearn_track.md`.

## Why this round

Round 6 closed on 13 October with David's cheatsheet experiment and its extension done and nothing carried forward (`docs/round06/README.md`). Round 7 was to return to the PPI paper, starting from the question round 5 left, which is weighting the labelled clusters by their inclusion probabilities under rejective selection (`docs/round05/i04/ppi/round5_ppi_E5_decisions.md`, section 5).

Two things changed before the round opened.

**A new line of work from the advisor meeting of 12 October** (`00_prep/round07_advisor_directions.md`). David argued that predicting expression from foundation-model embeddings of H&E has reached a bottleneck in accuracy, and proposed a textual knowledge base written by agents over many training pairs. Dr. Zhu objected that text loses information, and proposed federated learning, gathering training information as summary statistics from centers around the world. Nicolas's assignment for the week is a literature review of the viability of federated learning for this problem, toward a methods paper that proposes a federated method and argues for the direction. It is preliminary and a proof of concept. It is a second paper, alongside the PPI paper.

**An overlap check of the PPI paper** (`00_prep/round07_overlap_check.md`). Nicolas asked whether a group member's unpublished manuscript on choosing which slides receive a spatial transcriptomics assay changes the paper's direction. It does not, since it makes no inferential claim. In writing the check, the oversight chat noted that a cohort chosen by a deterministic or outcome-dependent selection rule cannot be analysed with design-based PPI, which is what round 5's open question addresses. The check also found public work that changes what the paper can claim as new, above all Broska and Howes, "Cluster-Robust Prediction-Powered Inference" (arXiv:2610.09601, 7 October 2026), which gives large-sample cluster-robust PPI++ with partly labelled clusters. The details of the manuscript are kept out of this public repository by Nicolas's decision.

## Goal

For the federated learning line, a literature-based assessment of whether federated learning can raise the accuracy of predicting expression from histology, with quick scoping experiments on the data the project holds. The round hands Nicolas a viability verdict for each route, two or three candidate method concepts for a proof-of-concept paper, and a first reading on whether accuracy is limited by data at all.

For the PPI line, a positioning of the paper against the newer literature, and then, if Nicolas accepts it, a track on the reframed first methods question, valid inference after histology-guided assay allocation.

## Tracks

**fedlearn,** opened now. Branch `round7-fedlearn`, run by a Claude Science session with sub-agents, which Nicolas decided on 13 October, from a new clone on the Mac at `~/hest-1k/HEST-1k-replication-fedlearn`, with computation on Longleaf. The oversight chat sets the scope and writes the instruction and memos.

| Interval | Stages | Gate | What it delivers |
|---|---|---|---|
| i01 | F0 setup and the search protocol, F1 search, screening and extraction with seven theme sub-agents, F2 the review, the viability verdict, a read-only inventory and the proposal for experiments | F2 | the literature review, the verdicts, the novelty statement bounded by the search log, the inventory, the proposal |
| i02, opened by the F2 memo | F3 scoping experiments, F4 the closing report | F4, end of track | a learning curve in training donors (V1), a simulated federation by lab and by pseudo-center (V2), and the privacy experiment V3 if the memo adds it |

Papers the session cannot retrieve go to Nicolas as one list of at most 10 during F1, each with a link through UNC Chapel Hill's library proxy or, where UNC's access is not available, to a free version (instruction section 8). Nothing of interval 2 is set up before the F2 memo.

**ppi,** not opened now. Nicolas decided on 13 October that the positioning comes first. The oversight chat reads Broska and Howes and "Balanced Active Inference" (Chen, Zhou, Peng and Wang, NeurIPS 2025) in full and writes a positioning note in `oversight/`. If Nicolas then accepts the reframed question (open question O2), the oversight chat writes the PPI instruction into `i01/ppi/`, the track's own first interval, as an amendment to this masterplan, with stages for the Horvitz-Thompson and Hájek weighting under rejective selection balanced on embedding components, a randomised counterpart of an adaptive selection policy, and the coverage of a deterministic rule. Its compute would be Longleaf, as in round 5.

**conformal.** No work is planned. Its readings stand (`docs/round05/i03/conformal/round5_conformal_W5_decisions.md`, section 3), and nothing in the overlap check touches it.

## Schedule

| When | What |
|---|---|
| Tuesday 13 October | masterplan, the fedlearn instruction, the overlap check and the meeting record on `main` |
| Wednesday 14 to Friday 16 October | F0 to F2. The inventory job is submitted in F0 and the list of papers reaches Nicolas during F1 |
| about Friday 16 October | gate F2, then the F2 memo |
| this week | the PPI positioning note |
| about Wednesday 21 October | gate F4 |

Nicolas called the review his task for the week. The date of the next advisor meeting was not given.

## Predictions

The fedlearn predictions F.1 to F.10 are in the instruction's section 9, written before any search or run. The two that matter most for the paper are F.1, that at most three papers federate expression prediction from histology and none fits a head on a frozen foundation model from summary statistics, and F.6 and F.7, that accuracy rises with the first few training donors and then flattens within the data the project holds. If F.7 holds, then for one task, one encoder and a linear head trained on at most about 17 donors, more data of the same kind would not by itself raise accuracy. The case for federation would then have to rest on the diversity of centers, or on heads and data that the experiment does not cover, rather than on volume alone.

## Open questions

| # | Question | Who decides | Default |
|---|---|---|---|
| R7-1 | Any download of further HEST-1k slides, or other public data, for the scoping experiments | Nicolas, at the F2 gate | none, the experiments use what is on Longleaf |
| R7-2 | How the federated learning paper is framed relative to David's textual knowledge base | Nicolas, with David and Dr. Zhu | the review compares the routes on evidence and takes no side |
| R7-3 | Venue and authorship of the federated learning paper | Nicolas, with his advisors | open |
| O2 | Round 7's PPI question reframed as inference after histology-guided allocation (overlap check, section 2) | Nicolas, after the positioning note | the E5 memo's question as written |
| O3 | How the PPI paper and the lab's manuscript refer to each other | Nicolas, with David and Dr. Zhu | neither refers to the other |
| O5 | The PPI paper's positioning against Broska and Howes, Kluger et al. and Chen et al. | Nicolas, with David | the paper claims nothing about large-sample cluster-robust PPI as new |

O1 (the PPI paper's direction stands) and O4 (no contact with the manuscript's authors) are in the overlap check, section 5, with their defaults.

## What closes the round

The fedlearn track's closing memo is written after its F4 report is reviewed and its pull request merged. If a PPI track was opened by amendment, its closing memo is written and merged too. If none was opened, the positioning note is done and the PPI question is carried to round 8. Then the close check of the `project-state-keeping` skill runs.

## Amendments

- 13 October 2026. The PPI positioning note is written (`oversight/round07_ppi_positioning.md`). It recommends accepting O2 with three changes. The core question becomes inclusion-probability weighting for fixed-size rejective selection at few clusters, beside Kluger et al.'s independent Bernoulli selection. Broska and Howes's interval becomes a comparator in every design. And the adaptive arm becomes a cluster-level version of Chen et al.'s balanced design. The PPI track is still not opened, and waits for Nicolas's decision on O2.
- 13 October 2026, evening. Nicolas accepted O2 with the positioning note's three changes. The `ppi` track opens with its instruction `i01/ppi/round07_ppi_track.md`, branch `round7-ppi`, a Claude Science session from the reused PPI clone `~/hest-1k/HEST-1k-replication-PPI`, computation on Longleaf, stages S0 to S5 with gates at S2, S4 and S5. It runs at the same time as `fedlearn`, with disjoint areas. An independent agent checked the instruction before commit and its findings were worked in. The round now closes when both tracks' closing memos are written and merged.
