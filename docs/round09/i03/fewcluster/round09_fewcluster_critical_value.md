# Round 9, track fewcluster, critical values below the frontier (step I3-3), and the novelty checks of interval 3

*27 October 2026. Written by the fewcluster session. Section 1 reports a dedicated research agent's work on claim K (`results/round9/fewcluster/crit/crit_value_report.md` and the scripts and tables beside it) and a fresh agent's check of it (`results/round9/fewcluster/verify_crit/verify_crit_report.md`). Section 2 records the novelty checks that returned after the Theorem 3 note was committed, which section 7 of that note left open. Recommendations are `[proposed]`.*

## 1. Critical values

**The question.** Theorems 2 and 3b say a finite critical value exists below the frontier but not how large it is. For the fixed-coefficient interval over $\mathcal{K}(\kappa_0)$, let $c(\kappa_0)$ be the smallest $c$ with coverage at least $1 - \alpha$ at every population in the class.

**The reduction.** With $x$ the residuals centred at the population mean, $A = \sum_{i \in S} x_i$ and $Q = \sum_{i \in S} x_i^2$, the interval misses on sample $S$ exactly when

$$
A^2 > \rho\, n\, Q, \qquad \rho = \frac{g}{1 + g}, \qquad g = \frac{c^2 (1 - f)}{n - 1}.
$$

**Certified upper bounds.** The miss region is a wedge in $(A^2, Q)$. For coefficients with $a_1 + a_2/n \ge 0$ and $a_1 + a_2/(\rho n) \ge 0$, the line $L = 1 + a_1 A^2 + a_2 Q$ is at least 1 on the wedge, so

$$
P(\text{miss}) \le E\,L^2 .
$$

Under sampling without replacement, with $\sum x = 0$ and $\sum x^2 = 1$, the moments $E A^2$, $E Q$, $E A^4$, $E A^2 Q$ and $E Q^2$ depend on the population only through $p_4 = \sum x^4$, linearly. For example,

$$
E Q^2 = \frac{n\{(G - n)\,p_4 + n - 1\}}{G(G - 1)}.
$$

Since $1/G \le p_4 \le \kappa_0$ on the class, the bound is the larger of its values at the two ends, and it can be minimised over $(a_1, a_2)$ and checked in exact rational arithmetic. The fresh agent re-derived every moment, proved the certificate (the condition $a_1 \ge 0$ in the agent's statement is not needed), and recomputed four cells exactly.

| Design | $\kappa_0$ (fraction of the frontier) | Certified $c_U$ | Exact bound at $c_U$ | Lower bound $c_L$ |
|---|---|---|---|---|
| 8 of 24 | 19/300 (0.4) | 3.775 | 0.09998 | 2.086 |
| 12 of 24 | 7/96 (0.25) | 2.892 | 0.09995 | 1.913 |
| 8 of 51 | 16/561 (0.4) | 4.403 | 0.09999 | 2.358 |
| 16 of 51 | 23/510 (0.25) | 3.234 | 0.09998 | 1.981 |

The lower bounds are the critical values needed by explicit populations, found by stochastic search over populations with two to six distinct values and checked by full enumeration of every sample. The fresh agent confirmed four of them to three decimals by its own enumeration, among them the two-point population with 9 and 15 clusters at 8 of 24, which needs $\sqrt 6 = 2.449$. The normal quantile is 1.645.

**Where it stops.** The quadratic certificate does not tend to the $c \to \infty$ limit $\beta(\kappa_0)$, so it gives nothing once $\kappa_0$ passes about half the frontier. A second certificate built on a band lemma (a missed sample at large $c$ is one-signed with $\max/\min < (1 + \delta)/(1 - \delta)$, $\delta = (n - 1)/(c\sqrt{1 - f})$) and a generalised Lemma 1 is valid but gives $c$ between 33 and 270. The lower bounds stay between 1.9 and 3.0 up to three quarters of the frontier and rise to between 4.4 and 5.0 at nine tenths. The worst populations found have two or three distinct values at $G = 24$ and four to six at $G = 51$. For the box class of Theorem 3 at the ACS and HEST settings no certified value was found. Its lower bounds are 2.1 to 2.8. The obstruction is that the probability of every stratum degenerating at once is already close to $\alpha$ (0.0858 at 51 strata, 5 per stratum, $\Lambda_0 = 9$, $v_0 = 0.025$). The verifier also notes that the quadratic certificate is loose even where it works, since random members of the class miss about 0.01 at $c_U$.

**What this means.** The real tasks' median residual max-shares are 0.31 to 0.53 (section 6 of the paper draft), and the certified range at 8 of 24 reaches only half the frontier, about 0.08 (where the certificate gives $c = 7.405$). So a certified critical value for the classes that real tasks satisfy is not in hand. The lower bounds do say that the price of a finite-sample guarantee, where one exists, is a critical value 1.2 to 1.8 times the normal one over most of the region, rising steeply near the frontier. `[proposed]` The paper should state the certified values as a proposition, give the lower bounds as the cost of validity, and leave a sharp computable critical value as an open problem. It should not present a positive method it does not have.

## 2. Novelty checks of interval 3

**NOV10b (Theorem 3 and claim K).** A second checker read in full text Kojevnikov and Song (2023), Müller's "A More Robust t-Test", Hagemann (2023), Pötscher and Preinerstorfer (2023), Ibragimov and Müller (2010, 2016) and Canay, Romano and Shaikh (2017), and Székely (arXiv:math/0610838) in place of Bakirov and Székely (`results/round9/fewcluster/novelty/novelty_NOV10b_structured.json`, `novelty_NOV10b_fulltext_verdicts.csv`). None contains the stratified frontier, the pooling result, the regime comparison or claim K.

1. The nearest structural analogue of Theorem 3 is Pötscher and Preinerstorfer's Theorem 5.1 and Theorem A.5. A size-controlling critical value exists if and only if no extreme-leverage configuration exists, over Gaussian covariance classes that include clustered ones.
2. The nearest to the pooling result are baselines for it. Hagemann's Theorem 2.1 gives exact size $2^{-\min(q_1, q_2)}$ for symmetric heterogeneous variables, and Canay, Romano and Shaikh's sign-change group needs $2^q$ large. Both count clusters under symmetry.
3. Kojevnikov and Song show asymptotically that one large cluster makes the mean impossible to learn and that two suffice. That result is asymptotic and set in dependency-graph models.
4. Nearest to claim K is Székely's certified $t$ critical values over symmetric scale mixtures. That class is not a bound on the largest standardized deviation and does not involve a finite population.

The checker could not obtain Bakirov and Székely's original. NOV9 had read it in full from `refs/` and found its extremal case model-based, with no threshold. The full texts were read through extraction and keyword scans, with theorem statements read and proofs not, so the verdicts stay provisional.

**NOV11 (claim K).** Claim K was not found in print, provisionally, with one paper read in full (Pinelis, arXiv:math/0606160) and the rest from abstracts (`novelty_NOV11_structured.json`). The nearest are Lehmann and Loh (1990) and Romano (2004), with asymptotic uniform validity of the $t$-test over classes of the same kind but no finite-sample critical values.

**NOV12 (the certificate, claim K, the band lemma).** This check is dispatched (frame e91483e5-3117-49ac-a886-549c2f0f16b3) and is waiting on an approval card. It covers Eaton (1974), Dufour and Hallin (1993), Edelman (1990), Pinelis (1994), Efron (1969), Eaton and Efron (1970) and Romano and Wolf (2000), which NOV10b named as closer to claim K than anything it read. Until it reports, the quadratic certificate is not claimed as new. A Chebyshev-type majorant of an indicator is a classical device.

**Theorem 3, status after NOV10 and NOV10b.** Not found in print. The technique is Theorem 1's, and pooling across groups is known qualitatively under symmetry or Gaussianity, which the paper cites. What may be new is the product frontier for stratified sampling from a finite population, its two classes, and the finite-sample comparison of regimes A and B.

## 3. Files the checkers saved outside the repository

The checkers were told not to save paper full texts as artifacts. NOV10 saved two PDFs and NOV10b saved thirteen PDF and text files to the project's private artifact store. They are not in this repository, which is public. Whether to delete them is Nicolas's decision.
