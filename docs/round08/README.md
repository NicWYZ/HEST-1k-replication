# Round 8, the PPI paper's positioning against the survey-sampling literature, then its plan (19 October to 6 November 2026, closed)

Round 7 left the PPI paper with a narrower set of claims of its own. A first look toward the survey-sampling literature on 19 October found four papers from June to September 2026 that bear on the claims that remained, three of them new to the project, so the round starts with a positioning check by the oversight chat, and the paper plan and any execution track follow from what survives. The plan is `masterplan.md`.

**Tracks.** positioning (an oversight track, no branch, stages P0 to P3, gate P3 at Nicolas's review, with one oversight pull request for its search logs). Later tracks are opened by amendments to the masterplan. **Starts from** `main` at the commit that carries the masterplan.

## Gates

| Date | Track | Gate | Report | Answered by | Tag | Pull request |
|---|---|---|---|---|---|---|
| 19 Oct | positioning | P3 | `i01/positioning/round08_positioning_note.md` | pull request merged by Nicolas on 22 October. He did not rule on the note's recommendation separately, and closed the round on 6 November after round 9 had carried the recommendation out in effect | `round8-positioning-P3` `[proposed]`, not created | #35, from `oversight-round8-positioning-search` |

## Documents

In folder order. Living documents are frozen at the round's close.

| Document | Date | Role |
|---|---|---|
| `masterplan.md` | 19 Oct, living | the round's plan, with why the round starts with positioning, the tracks, the predictions P.1 to P.5, the open questions and amendments |
| `i01/positioning/round08_positioning_scope.md` | 19 Oct | stage P0 of the positioning track, with the claims C0 to C12, the search themes T1 to T5 and the second pass, the protocol and how verdicts are graded |
| `i01/positioning/round08_positioning_note.md` | 19 Oct | stage P3 and the gate's report, with what was read, a verdict per claim C0 to C12, the regrade of every close row, the predictions scored, corrections to the record, what follows for Q3, R7-5, R7-6, R7-7 and R8-1, and the sources Nicolas is asked to obtain. Its main finding is that round 5's cross-fitted estimator is Williams' (1961) estimator without one factor |

## What the round established

The positioning note (`i01/positioning/round08_positioning_note.md`, sections 2 and 6.1) checked every claim C0 to C12 of the PPI paper against the survey-sampling literature and PPI work newer than round 7's check.

- No technical result of the paper survived as its own. The design-target gain formula, the comparison of labelling whole clusters against a few units in every cluster with costs, the level term, the optimal number of units per cluster with a predictor (Snijders 2001, Raudenbush 1997), the interval `rej_t` (Yang, Qu and Li, JASA 2023) and the small-sample cluster-robust correction are classical or in print. Design-based inference after prediction-guided selection, cube selection of clusters and the failure of weighting under rejective selection are in print for units or in part.
- Round 5's cross-fitted estimator is, for an even number of labelled clusters, Williams' (1961) exactly unbiased split-sample regression estimator without the factor $1 - n/G$ on its correction term. Its cross-fitting term is that omission, a defect with a one-line fix, and its design bias is small under round 5's clipped coefficient (note, section 3.2, checked by exact enumeration).
- What remained was empirical, the few-cluster comparison of selection designs on real tasks, the prediction-set map and the joint design. Predictions P.2 to P.5 held and P.1 partly held (note, section 4).

## Corrections and withdrawn readings

The note's section 5 lists the corrections to the record. They take effect with the round's close. Round 7's positioning note (section 5) and explainer (Parts B and C) are frozen and still call the regime comparison, the allocation formula, `rej_t` and the cross-fitting term the paper's own, which this round withdraws. Round 7's simulated inclusion probabilities, its zero pair probabilities and its rejective-against-cube comparison have uncited antecedents (Fattorini 2006, Aronow and Samii 2013, Legg and Yu 2010).

## Carried forward

- **The recommendation** of the note's section 6.5 (fix the estimator, check three directions for a methodological core, then choose the lead) was carried out in effect by round 9. Run 6.4.1 is round 9's `docs/round09/i03/fewcluster/round09_fewcluster_williams.md`, and the search for a core is round 9's preparation and its two tracks. No later track of round 8 was opened.
- **Sources.** The ten sources of the note's section 7 were not obtained. On 6 November Nicolas decided that no new paper reads are made for now, so the verdicts that rest on abstracts or on unread textbooks (C2, C3, C12 among them) stay provisional.
- **Decisions** Q3, R7-5, R7-6, R7-7, R8-1 and O5 carry into `CLAUDE.md`, section 2, unchanged by the close.

## Read first next round

The positioning note, sections 2, 3.2 and 6, then round 9's guide (`docs/round09/README.md`), which builds on it.
