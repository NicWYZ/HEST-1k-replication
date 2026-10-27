# Round 9, track fewcluster. How the paper could be built `[proposed]`

27 October 2026. Written by the fewcluster session at Nicolas's request ("based on everything done so far since the very beginning, how would we construct a paper"). It draws on the round 7 closing decisions (`docs/round07/i04/ppi/round07_ppi_final_decisions.md`), the round 8 positioning note (`docs/round08/i01/positioning/round08_positioning_note.md`) and this track's notes (`round09_fewcluster_position.md`, `round09_fewcluster_sources_and_median.md`). Every part of it is a proposal for Nicolas, and D1 and R8-1 are his.

## 1. The problem the record leaves

The round 8 note found that every formula the paper would have displayed up to round 7 is classical or in print. What was left as the paper's own was empirical: the few-cluster design comparison, the prediction-set map and the joint design. Its view was that the paper needs a methodological core of its own. Round 9 supplies one candidate core, the two frontiers. They also explain a fact the empirical rounds kept running into. On tissue, every interval covered below nominal at few clusters (`rej_t` 0.852 to 0.866, D0 classical 0.875 to 0.878, Broska and Howes 0.704 at 4 labelled), and the real tasks lie beyond both frontiers for practically every gene.

## 2. The paper's thesis

With predictions free for every cluster and only a few clusters labelled, a finite-sample guarantee is possible exactly when residual concentration lies below a frontier that depends on $G$, $n$, $\alpha$ and, for tuned PPI, the prediction vector. The paper computes that frontier and shows that real tasks lie beyond it at the sizes practitioners use. It then shows what a labelling budget can do about this. The budget can label more clusters, label the atypical cluster with certainty, label a few units in every cluster, or buy a stated bound on the residuals. Finally it compares the designs that do best in practice when no guarantee is available.

Working title: "How few labelled clusters are enough? Limits and labelling budgets for prediction-powered inference with clustered data."

## 3. Sections

1. **Introduction.** The setting (spatial transcriptomics donors, states in census data), why PPI at few clusters is fragile, and the contributions in the order of section 4 below.
2. **Setting.** A finite population of $G$ clusters, predictions $f$ for all of them, a design-based target, and fixed-size designs. The class of intervals is all location and scale equivariant intervals, which includes PPI, PPI++, $t$, CR2, wild cluster bootstrap and Broska and Howes's interval. Residual concentration is measured by the max-share $\kappa$. Mozer (arXiv:2603.19160), Cochran and Williams (1961) are cited for the estimators.
3. **What few labelled clusters can and cannot guarantee.**
   1. Lemma 0, the unconditional impossibility (folklore, cited to Bahadur and Savage, Gleser and Hwang, Dufour).
   2. Theorem 1, the fixed-coefficient frontier, with both halves, the two-point extremal lemma and simple random sampling as minimax among fixed-size designs. Corollary: the number of labelled clusters needed for a stated bound $\Lambda$ (13 of 24 at $\Lambda = 3$, 17 of 24 at $\Lambda = 4$).
   3. The large-$G$ limit, which is known (Lanke 1974; Székely 2006), with the median result of `round09_fewcluster_sources_and_median.md` as a remark.
   4. Theorem 2, the tuned-coefficient frontier $\kappa^\dagger(f)$, the spike formula and the exact algorithm. Because $\kappa^\dagger$ depends only on $f$, $G$, $n$ and $\alpha$, it can be computed before any label is bought, which makes it a design-stage diagnostic.
   5. Theorem 3, not yet written. The product form over strata, covering a take-all stratum and regime B, where a few units are labelled in every cluster so the clusters act as strata. This would turn the round 4 to 8 regime comparison from a classical variance comparison into a statement about which budgets can carry a guarantee at all.
4. **A valid interval below the frontier.** The possibility half of Theorem 1 says a finite critical value exists over $\{\kappa \le \kappa_0\}$. The exact critical value $c(\kappa_0)$ (claim K, deferred in interval 1) would make it a usable method, an interval valid in finite samples for any analyst-stated $\kappa_0$ or $\Lambda$. This is the paper's positive method if it can be computed and is not in print.
5. **Designs when no guarantee is available.** The round 7 comparison at 4 to 16 labelled clusters. Rejective selection with `rej_t` is narrowest on census (0.449 to 0.467 of D0's width). The cube design with bounded probabilities is valid at $n_L \ge 6$ on both domains. Weighting fails under rejective selection, and greedy k-center covers 0.326 to 0.458. The corrected Broska and Howes interval (`bh_t`) covers at $n_L = 4$. These are presented as the paper's empirical evidence with their prior art cited (Yang, Qu and Li; Deville and Tillé; Legg and Yu; Neyman), and read against the frontiers.
6. **Applications.** CCRCC, INDIANA_KIDNEY and LUNG_XENIUM on HEST-1k, and ACS PUMS 2018 by state. For each task the paper reports $\kappa$ and $\kappa^\dagger$ per gene, the labelled clusters a guarantee would need, the effect of labelling INT5 with certainty, and the design comparison's coverage and width.
7. **Prediction sets for a new cluster** (R8-1). This would be the round 5 map, where the narrowest method switches from HCP to the target donor's own full conformal set at 9 labelled spots, plus the joint design. The session's view is that it belongs in a separate paper, because it answers a different question and would dilute the thesis. Keeping it is the one choice that leaves an untouched part in this paper.
8. **Discussion.**

## 4. Claims, by status

| Claim | Status | Source |
|---|---|---|
| Theorem 1 in its finite-population, graded form, with its possibility half and design minimaxity | not found in print (nine checkers) | `round09_fewcluster_position.md` |
| Theorem 2, spike formula, exact algorithm | not found in print | same |
| Median conjecture remark | not found in print, provisional | `round09_fewcluster_sources_and_median.md` |
| Lemma 0, technique, iid limit | classical or known, cited | same |
| Estimators, finite-population factor, regime comparison, allocation | classical, cited | round 8 note, section 2 |
| `rej_t`, cube design, weighting mechanism, k-center | prior art for the components, the few-cluster comparison the paper's own | round 8 note, C5 to C8 |
| Theorem 3 and the exact critical value | not yet done | to do |

## 5. Work before drafting

1. Theorem 3 (product form, take-all, regime B), with a fresh-agent proof check and a novelty check.
2. The exact critical value of section 3, item 4, with a novelty check. NOV1 found claim K partly open.
3. The estimator fix of the round 8 note (run 6.4.1, Williams' 1961 form against round 5's), which this branch does not record as run. The paper cannot display round 5's estimator once Williams is known.
4. Re-run the design comparison with the fixed estimator, if item 3 changes it.
5. Decisions D1 (theory section) and R8-1 (prediction sets), and the venue.

## 6. Venue

With Theorems 1 to 3 and a usable interval, the paper is a theory-and-methods paper with real applications, and fits a statistics journal better than an ML conference. The theory is sharp but its technique is classical, and the ML venues weigh new methods more than limits. AISTATS is the most plausible ML venue. Without item 2 of section 5 the paper's new content is a negative result with design consequences, which is the weaker position the round 8 note warned about.
