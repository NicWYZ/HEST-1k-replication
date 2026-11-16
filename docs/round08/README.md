# Round 8, the PPI paper's positioning against the survey-sampling literature (19 October to 6 November 2026, closed)

Round 8 ran one oversight track, `positioning` (stages P0 to P3, no branch), which checked every claim the PPI paper "Labelling budgets for prediction-powered inference with clustered data" still held as its own after round 7 against the survey-sampling literature and PPI work newer than round 7's check. Its scope and protocol are `i01/positioning/round08_positioning_scope.md`, and its report is `i01/positioning/round08_positioning_note.md`. The gate's search logs and the Williams check went to `main` through pull request #35, merged on 22 October. The proposed gate tag `round8-positioning-P3` was never created, and no decision file was written for the gate. Nicolas did not rule on the note's recommendation separately and closed the round on 6 November, after round 9 had carried the recommendation out. No later track of round 8 was opened. `docs/round10/00_prep/round10_findings_survey.md` gives the status of every finding by question (rows B4, B9, E2, E3 and section 3.1).

## What the round established, as it now stands

1. **No formula the paper would display is its own.** Each claim C0 to C12 of the scope got a verdict (note, section 2). The design-target finite-population factor (C1) is classical. The comparison of labelling whole clusters against a few units in every cluster for the design target with costs (C2) and the level term with form C (C3) are classical. The optimal number of units per cluster with a predictor, $m^\star\sqrt{(1 - R^2_w)/(1 - R^2_c)}$ (C4), is Snijders (2001) eq. (12) and (13) and Raudenbush (1997), with only the measured between ratio $\rho_c(n_L)$ in place of $1 - R^2_c$ left as the project's. `rej_t` (C5) is Yang, Qu and Li's (JASA 2023) Corollary A5 at the cluster level with a $t$ reference. The gain formula's cluster-level and design-target reading (C12) is Cochran's regression estimator on cluster values, with Hagesæther and Zhang (2009) for the design effect. Greedy k-center's lack of a design-based variance (C8) goes back to Neyman (1934). The framing (C0), the cube design of clusters (C6) and the failure of weighting under rejective selection (C7) are partly held: the components are in print for units or in part, and what remains is the few-cluster comparison. Caveat: C2, C3 and C12 rested on textbook sections the round could not read and were marked `[verify]`. Round 10's ledger read Cochran and Särndal, Swensson and Wretman by chapter and places C2 at Cochran's Theorems 10.1 and 10.2 (`docs/round10/i01/ledger/round10_ledger.md`, rows E1 and E2 and its sources table).

2. **Round 5's cross-fitted estimator is Williams' estimator without one factor.** For an even number of labelled clusters, round 5's estimator (`docs/round05/tracks/ppi/round5_ppi_estimator_definition.md`) is Williams' (1961) exactly unbiased split-sample regression estimator with two groups, except that the factor $1 - n/G$ on his covariance correction is missing. For $n < G$ it therefore has a design bias of $\{(n/G)/(1 - n/G)\}\,\text{Cov}(c', \bar f_L)$, which round 5's theory had called zero up to finite-population terms. The cross-fitting term that round 7 counted as the paper's last technical result is that omission (note, section 3.2). Exact enumeration on a toy population confirmed the identity, and under round 5's clipped coefficient, set to 0 below six clusters, the bias is $+0.01092$ at $n = 6$ and $+0.01197$ at $n = 8$, against $+0.05764$ and $+0.15858$ unclipped (`results/round8/positioning/checks/williams_vs_r5_output.txt`). Round 5's theory and round 7's positioning did not cite Mickey (1959) or Williams (1961). **Changed since.** Round 9 measured the effect on the real tasks (`docs/round09/i03/fewcluster/round09_fewcluster_williams.md`), and round 10 adopted the two-fold cross-fitted estimator in Mickey's form, which is Williams' form for even $n$, beside a primary estimator with the coefficient fixed at 1 (`docs/round10/round10_methods_note.md`, item 3).

3. **What remained the paper's own was empirical** (note, section 6.1): the few-cluster comparison of prediction-guided selection designs on matched cells of real tasks (round 7's summary, `docs/round07/README.md`, findings 1 to 5), the prediction-set map with its switch from HCP to the target donor's own full conformal set at 9 labelled spots (C10), and the joint design (C11), all bounded by the search logs. The small-sample correction of Broska and Howes's interval stays classical (C9; the CR2 form's survey origin is Bell and McCaffrey 2002), and nobody was found to have published it for PPI. Since Nicolas's reframing of 6 November, applying existing or classical methods is acceptable for a first paper, and new theory arises only where a literature search finds a genuine gap (`docs/round10/00_prep/round10_reframing.md`, section 1), so the absence of a technical result of its own no longer blocks the paper.

4. **The searches** (note, section 1; `results/round8/positioning/P1_search/`). The first pass logged 205 queries and kept 129 candidate rows, 27 graded close. The second pass screened the reference lists of the earlier checks and of the papers read in full (200 rows, 134 candidate rows, 77 seed lookups) but ran only 22 of its web searches, and pass 2b ran the rest under per-theme caps (48, 45 and 45 searches), keeping 126 candidate rows, 25 graded close, with 2 of 33 seeds unconfirmed. Caveats that bound every verdict: forward citations of the anchor papers were not retrieved, the caps were hit while C7, C8 and C11 were still turning up related items, and several sources were graded from abstracts (note, section 1.3). Verdicts that rest on abstracts stay provisional.

5. **Corrections the round made to earlier documents.** Round 7's positioning note (section 5) and its results explainer called the regime comparison, the allocation formula, `rej_t` and the cross-fitting term the paper's own, which this round withdrew (round 7's summary says what stands). Round 7's simulated inclusion probabilities, its zero pair probabilities and its comparison of rejective and cube selection have antecedents it did not cite, Fattorini (2006), Aronow and Samii (2013) and Legg and Yu (2010). The round's masterplan first presented Shirota's paper (arXiv:2608.10356) as new, though round 3 had found it, which was corrected before the masterplan was committed.

## Expectations and their scores

The masterplan's predictions P.1 to P.5 were written before any of the four opening papers was read beyond its abstract, and its "How they are scored" paragraph fixed the scoring before any score. The note scores them in section 4.

| Prediction | Score |
|---|---|
| P.1 An, Dagdoug, Haziza and Tillé give a design-based variance for cross-fitting that accounts for dependence between folds, without clusters or a $t$ reference, so round 5's term is in print at the unit level | partly held: (a) refuted, they condition on the split; (b) and (c) held; the "So" part refuted as written, though its conclusion turned out true through Williams (1961) |
| P.2 Shirota's inference after map-dependent selection uses estimated propensities, not fixed-size rejective or cube selection | held |
| P.3 OPAL has no cost per cluster and per unit | held |
| P.4 the $(1 - R^2_c)$ allocation form is classical | held |
| P.5 at least one further 2025 or 2026 paper close for C0 or C5 to C8 | held (Datta and Polson, arXiv:2508.10149) |

The note was checked before its commit by an independent agent, which redid the algebra and enumeration of section 3.2 with its own script, and no score was changed afterwards.

## What was tried and did not work

- Finding a technical result for the paper in the survey-sampling literature. Every candidate that round 7 had left, the cross-fitting term last, was found classical or in print. Round 9 then searched three directions for a methodological core (note, section 6.2) and found none outside its provisional few-cluster frontier (`docs/round10/00_prep/round10_findings_survey.md`, sections 1 and 4.1).
- Checking claims on the machine-learning side of the literature only. Rounds 4 to 7 did so, and most of the prior art this round found was in survey sampling, which is why hard rule 5 now requires both.

## What was presented outside the project

Nothing, as far as the record shows. The masterplan recorded on 19 October that Nicolas's next advisor meeting would be about federated learning and the textual knowledge base, and the note was meant as the groundwork for O5 and R7-5 with David. The record does not show that it was taken to him.

## Open threads

- **Decided since.** The note's recommendation (section 6.5) was carried out by round 9: its run 6.4.1 is `docs/round09/i03/fewcluster/round09_fewcluster_williams.md`, and the search for a core was round 9's preparation and tracks. R7-5, R7-6, R7-7 and O5 were decided in round 10 (`docs/round10/round10_methods_note.md`), and R8-1 was decided for keeping prediction sets in the paper, with the joint design settled at round 10's F3 as E8 (`docs/round10/README.md`).
- **Open.** Q3, which result the paper leads with, in the state block.
- **Candidate runs not made** (note, section 6.4): `rej_t` with Yang, Qu and Li's quantile in place of $t_{n_L - k - 1}$, and Aronow and Samii's conservative variance under rejective selection.
- **Sources** (note, section 7). Of the ten, round 10's ledger read Cochran, Särndal et al., Mickey and Fuller. Breidt and Chauvet (2011) and the JASA text of Yang, Qu and Li remain unread, Fattorini is read from the abstract, and Valliant, Dever and Kreuter, Broska, Howes and van Loon, and Moerbeek (2006) are not in the ledger's sources.

## Documents kept

- `masterplan.md`, the round's plan, with predictions P.1 to P.5 and how they are scored.
- `i01/positioning/round08_positioning_scope.md`, the claims C0 to C12, the search themes T1 to T5, the protocol and the verdict scale, which `results/round8/positioning/P1_search/README.md` cites.
- `i01/positioning/round08_positioning_note.md`, the verdict per claim, the readings and derivations behind them (section 3), the scored predictions and the sources to obtain.

The record as it stood before this summary is at the tag `record-full-2026-11`.
