# Round 5, prediction-set track: the two theory questions (W4)

Written by the lead as W4 runs beside W1 to W3 (`docs/round5_conf_plan.md` section 2, W4). Each step is marked derived, conjectured or failed. `docs/round4_conf_lower_bound.md` is the record of round 4 and is not edited. Part A is capped at one and a half days and part B at three and a half. This document is a working record until the W2 gate.

## Reading log

Full texts were downloaded from arXiv on 7 October 2026 into the session workspace and read from text extracted with pypdfium2. "Searched" means the whole text was searched for the small-sample conditions $n + 1 < 1/\alpha$, $(1-\alpha)(n+1) > n$, $(K+1)\alpha < 1$ and their variants, and for statements about infinite or trivial sets, and every hit was read in context.

| paper | identifier | opened | sections read | date |
|---|---|---|---|---|
| Tibshirani, Barber and Ramdas, "Conformal Prediction Through the Lens of Hypothesis Testing: Universality, Impossibility, and Optimality" | arXiv:2608.27310 v2 | full text | sections 1 to 6 in full (pp. 1 to 13); section 7 and appendices A.1 to A.6 searched | 7 Oct 2026 |
| Mallick, Tchetgen Tchetgen, Dobriban and Lee, "Generalized Hierarchical Conformal Prediction" | arXiv:2608.15500 | full text | searched; hits on pp. 6, 9, 11, 33 read | 7 Oct 2026 |
| Lee, Barber and Willett, "Distribution-free inference with hierarchical data" | arXiv:2306.06342 | full text | searched; no hit | 7 Oct 2026 |
| Dunn, Wasserman and Ramdas, "Distribution-Free Prediction Sets for Two-Layer Hierarchical Models" | arXiv:1809.07441 | full text | section 2 (Theorems 1 and 2) and the nontriviality conditions of sections 3 to 5 | 7 Oct 2026 |
| Angelopoulos, Barber and Bates, "Theoretical Foundations of Conformal Prediction" | arXiv:2411.11824 | full text | section 3 around Algorithm 3.3 (p. 34) and Lemma 3.4; section 4.3, Theorem 4.5 and Corollary 4.6 (pp. 58 to 61); rest searched | 7 Oct 2026 |
| Vovk, "Conditional validity of inductive conformal predictors" | arXiv:1209.2673 | full text | searched; one hit (p. 9) read | 7 Oct 2026 |
| Lei and Wasserman, JRSS B 2014 | arXiv:1203.5422, titled "Distribution Free Prediction Bands" on arXiv; taken to be the same paper, not yet confirmed against the journal version | full text | not yet read | 7 Oct 2026 |
| Barber, Candès, Ramdas and Tibshirani, "The limits of distribution-free conditional predictive inference" | arXiv:1903.04684 | full text | searched; one hit (p. 18) read | 7 Oct 2026 |
| Lei, G'Sell, Rinaldo, Tibshirani and Wasserman, JRSS B 2018 | arXiv:1604.04173 | full text | searched; no hit | 7 Oct 2026 |
| Vovk, Gammerman and Shafer, *Algorithmic Learning in a Random World*, 2005 | book | nothing | not opened. Cited here only through Tibshirani, Barber and Ramdas, who cite its Proposition 2.9 (2022 edition) for universality | 7 Oct 2026 |
| Dobriban and Yu 2025; Duchi and colleagues 2025 | as cited by the GHCP paper | nothing yet | not yet identified | |

## Part A. Whether the two propositions are in print

The two statements are those of `docs/round4_conf_lower_bound.md`. Proposition 1 is the coverage floor $1 - \beta^\star(K, \alpha)$ for a valid method that is finite almost surely under some law when $K + 1 < 1/\alpha$. Proposition 2 says that every valid method returns an infinite set with probability at least $1 - \alpha(K+1)$ under some law.

### A.1 What Tibshirani, Barber and Ramdas prove (transcribed)

- Theorem 3 (universality). If a mapping from $X_{n+1}$ and $Z_1, \dots, Z_n$ to a set covers at level $1 - \alpha$ for every exchangeable law, the set is of conformal type, their form (16), for some score function. If the set is also invariant to the order of $Z_1, \dots, Z_n$, it is of their form (15) with a symmetric score. The paper's own Theorem 3 is stated for deterministic mappings. Its proof writes the set as the acceptance region of a test $\varphi$ and uses Theorem 2, a version of Lehmann and Romano's Theorem 4.3.2, with the bag $U = *Z+$ as a boundedly complete sufficient statistic.
- Theorem 5 and Corollary 1 (conditional hardness). These concern coverage conditional on $X_{n+1}$ and are not about small $n$.
- Theorem 7 (optimality). This is optimality in the sense of minimum expected Lebesgue measure under one fixed i.i.d. law $P$, among all mappings valid over every exchangeable law. The optimum is the randomised conformal predictor with score $1/p_{Y \mid X}$. This is "beaten at a law" in the language of part B: a pointwise optimum at each $P$, not dominance and not minimax.

### A.2 Proposition 2 for ordinary data: a corollary for order-invariant deterministic methods (derived)

Take the degenerate hierarchical model of `docs/round4_conf_lower_bound.md` section 4, step 1, in which every group's law is a point mass. Then the data are $K$ exchangeable values and the problem is ordinary prediction with $n = K$. Let the method be deterministic and invariant to the order of the calibration groups. Then by Theorem 3, second claim, the set is

$$
C = \Bigl\{ y : \frac{1}{n+1} \sum_{i=1}^{n+1} 1\{s^y_i \ge s^y_{n+1}\} > \alpha \Bigr\}.
$$

The term $i = n + 1$ is always one, so the left side is at least $1/(n+1)$. When $n + 1 < 1/\alpha$ this exceeds $\alpha$ for every $y$, so $C$ is the whole line with probability one. This is stronger than Proposition 2's $1 - \alpha(K+1)$, and it holds under every law in the degenerate family. Two limits must be stated. First, it covers only deterministic, order-invariant methods. Randomised HCP is excluded, and it is the method that attains Proposition 2's bound. Second, the same observation, that the conformal p-value is at least $1/(n+1)$, is printed by Dunn, Wasserman and Ramdas (arXiv:1809.07441, after Theorem 2, p. 6) and by Angelopoulos, Barber and Bates (arXiv:2411.11824, p. 34). Both state it as a property of the conformal construction, not of every valid method. What turns it into a statement about every valid method is universality.

Not yet done. The randomised case, which needs a universality statement for mappings that use auxiliary randomness, and the lift of the ordinary-data statement back to the hierarchical model at the level of Proposition 2's bound.

### A.3 Proposition 1

Not found in any paper searched so far. The device in Angelopoulos, Barber and Bates' proof of Theorem 4.5, a point-mass contamination $(1 - \epsilon) P + \epsilon \delta_{(x,y)}$, is the same device as Proposition 1's proof, used there for conditional coverage.

## Part B. Whether HCP can be beaten when $K + 1 \ge 1/\alpha$

Not started.
