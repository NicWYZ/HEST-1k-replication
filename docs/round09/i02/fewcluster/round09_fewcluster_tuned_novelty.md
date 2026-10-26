# Round 9, track fewcluster, novelty verdict on the tuned-coefficient frontier

*26 October 2026. Written by the fewcluster session after the novelty check NOV7 returned. It records the verdict that `round09_fewcluster_tuned.md` left pending, and is not an edit of that note. The logs are in `results/round9/fewcluster/novelty/` (`novelty_NOV7_TUNED_queries.csv`, `novelty_NOV7_TUNED_candidates.csv`, `novelty_NOV7_structured.json`, 32 queries).*

## Verdict

The checker found none of T1′ (impossibility), T2′ (possibility) or T3 (the spike formula and its use) in print. It graded T0, the reduction of coverage to the population residual, an immediate special case of the affine equivariance of least squares and of the residual form of the regression estimator (Mozer, arXiv:2603.19160, shows that PPI with a tuned coefficient is that estimator). The closest papers are these.

- Gleser and Hwang (1987) and Dufour (1997) give the general form of T1′, that a valid confidence set must be unbounded with positive probability, with the same scaling argument. Read from abstracts.
- Pötscher and Preinerstorfer (arXiv:2412.17470) give a condition on the design's leverage for size control of regression-based tests in a Gaussian model, without sampling from a finite population and without the affine-sample characterisation.
- Mani, Xu, Lipton and Oberst (arXiv:2505.20178) give the exact finite-sample mean squared error of PPI with a tuned coefficient under independent sampling, with nothing on coverage, leverage or impossibility.
- Hansen (Review of Economic Studies, 2026) gives worst-case coverage driven by leverage for cluster-robust intervals under normal errors. Closed access, abstract only.
- Lee and Kim (arXiv:2606.08730) and Shirota (arXiv:2608.10356) treat PPI under sampling without replacement asymptotically.

What the checker judged new is the finite-population statement for the tuned estimator. The defeating samples are those on which the population is exactly affine in the predictions, the frontier depends on the prediction vector through which sample lines can occur, and impossibility and possibility meet through $\beta_{\text{OLS}}$. The proof technique is the classical one, so a paper would claim the results, not the method.

## Checks it ran, and limits

It recomputed the example at $G = 24$, $n = 8$ with its own predictions. It found a two-piece population with five clusters in the second piece and $\kappa(\hat e) = 0.0905$, and exact coverage 0.8972332, which is $1 - \pi(5)$. It confirmed the spike formula to $10^{-10}$. It added that for its prediction vectors at $G = 24$ the smallest max-share of any spike is 0.52 to 0.76, so no spike lies in the class at $\kappa_0 = 0.10$. At these sizes the tuned frontier is therefore set by two-piece populations, and the leverage mechanism of section 4 of the tuned note matters only for smaller $G$ or more extreme predictions. It did not recheck the ratio of 0.37 to 0.74 between the two frontiers. Several sources were read only from abstracts or snippets (Gleser and Hwang, Dufour, Lanke, Hansen), and its Semantic Scholar queries failed, so the absence findings are provisional.
