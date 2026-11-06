# Round 9, track fewcluster, position note (step I2-5)

*27 October 2026, early morning. Written by the fewcluster session for Nicolas's decision D1, after the last novelty pass (NOV8) and the exact computations of I2-6. It gathers what the track has established, what of it is new on the evidence, and what it would contribute to the PPI paper. It replaces nothing. The theorem notes stay the record of the statements and proofs. Recommendations are `[proposed]`.*

## 1. The results

All statements are under simple random sampling of $n$ of $G$ clusters from a finite population, with predictions $f$ known for every cluster, for intervals that rescale with the data (location and scale equivariant). That class includes every PPI, $t$, CR2, sign-change and wild-bootstrap interval. The class of populations is bounded by the residual max-share $\kappa$, the largest share of the residual sum of squares carried by one cluster (Hájek's condition, in finite-sample form).

1. **The fixed-coefficient frontier** (`docs/round09/i01/fewcluster/round09_fewcluster_frontier.md`). Let $\pi(k)$ be the probability that the sample falls inside one group of a two-point population with $k$ and $G - k$ clusters, and $k^\ast$ the smallest $k \le G/2$ with $\pi(k) \le \alpha$. A valid interval of finite length exists over $\{\kappa \le \kappa_0\}$ when $\kappa_0 < \kappa_2(k^\ast - 1) = (1 - (k^\ast - 1)/G)/(k^\ast - 1)$, and above it every valid interval is unbounded with probability at least $\pi(k^\ast - 1) - \alpha$ under every population. The two-point population is extremal, and no fixed-size design that does not see the outcomes does better than simple random sampling.
2. **The tuned-coefficient frontier** (`docs/round09/i02/fewcluster/round09_fewcluster_tuned.md`). With the coefficient fitted by least squares on the sample, the defeating samples are those on which the population residual is exactly affine in the predictions. Impossibility and possibility meet at a frontier $\kappa^\dagger(f, G, n, \alpha)$ that depends on the prediction vector. An outcome spike at cluster $g$ has residual max-share $\max\{(1 - h_{gg})^2, \max_{j \ne g} h_{gj}^2\}/(1 - h_{gg})$.
3. **An exact algorithm for the tuned frontier** (`code/scripts/round9_fewcluster_exact_tuned.py`, I2-6). At the project's sizes, only a single line of $m_{\min}$ collinear clusters can defeat the interval. The frontier is the minimum over such lines of the reciprocal of a convex maximisation, solved exactly by enumerating the vertices of a small polytope. It matched the verifier's independent flat-lattice computation in 15 of 15 cases to $2 \times 10^{-16}$ (`results/round9/fewcluster/exact/i26_benchmark.csv`).

Each statement was proved by the session and again by a fresh agent from the statements alone, with exact enumeration at small sizes (`results/round9/fewcluster/verify/`, `results/round9/fewcluster/verify_tuned/`). The verifiers' corrections (the off-by-one in the fixed frontier, the possibility half for a fixed coefficient only, the floor on the spike's share) are in the notes.

## 2. The numbers

From the files cited, at $\alpha = 0.10$.

| Quantity | Value | File |
|---|---|---|
| fixed frontier, 8 of 24 | 0.158 (every residual within 1.91 SD) | `results/round9/fewcluster/feasibility/s3_frontier_exact.csv` |
| fixed frontier, 8 of 51 | 0.071 (1.89 SD) | same |
| Gaussian populations inside it, 8 of 24 and 8 of 51 | 0.167 and 0.009 | same |
| clusters to label for a guarantee if residuals beyond 3 or 4 SD cannot be ruled out, $G = 24$ | 13 or 17 | `results/round9/fewcluster/feasibility/s3_required_n.csv` |
| exact tuned frontier, 8 of 24, normal predictions (mean of 10 draws) | 0.0853 | `results/round9/fewcluster/exact/i26_synth_exact.csv` |
| tuned over fixed frontier, cell means | 0.51 to 0.56 | same |
| exact tuned frontier, median over genes: CCRCC, INDIANA_KIDNEY (8 labelled), LUNG_XENIUM (6) | 0.091, 0.086, 0.148 | `results/round9/fewcluster/exact/i26_real_exact_summary.csv` |
| median residual max-share on the same tasks | 0.533, 0.336, 0.312 | same |
| genes beyond the exact tuned frontier | 1.00, 1.00, 0.997 | same |
| CCRCC with INT5 as a take-all donor: median max-share of the other 23, frontier for 7 of 23 | 0.293, 0.157 (0.06 of genes inside) | `results/round9/fewcluster/design/i23_takeall_summary.csv` |
| ACS by state with predictions: residual max-share, fixed frontier | 0.147, 0.071 | `results/round9/fewcluster/hest/i24_task_summary.csv` |

At the design sizes the project has used, no scale-free method could carry a finite-sample guarantee on any task. This holds with either coefficient, and on CCRCC it still holds after the most atypical donor is labelled with certainty.

## 3. Novelty, on the evidence

Eight checkers searched over two sessions: five broad ones, then NOV6, NOV7 and NOV8, which read the closest papers in full where an open version existed. Their logs hold 424 query rows (the checkers' own counts differ slightly), the session ran 13 more on OpenAlex, and together they screened 275 forward citations through OpenAlex and 932 through Semantic Scholar (`results/round9/fewcluster/novelty/`).

| Statement | Status | Where the nearest work stands |
|---|---|---|
| Unrestricted impossibility, constant $(1 - \alpha - n/G)/(1 - n/G)$ | folklore | the total-variation form of Bahadur and Savage (1956), Gleser and Hwang (1987), Dufour (1997), Bertanha and Moreira (2020). Cited, not claimed |
| Fixed-coefficient frontier, both halves, extremality and design minimaxity | not found in print | Pötscher and Preinerstorfer (arXiv:2412.17470) give a yes-or-no leverage condition in a Gaussian model. Dufour and Hansen (2026) were read in full and do not contain it |
| Its large-$G$ limit, $n < 1 + \log_2(1/\alpha)$ | known as a number | Lanke (1974) claimed it for the median (as discussed by Paul and Kuchibhotla, arXiv:2403.06357), Hendriks et al. (2006) remark it for the $t$-interval, and Székely (2006, Theorem 2.1) implies it for $t$ critical values. What may be new is its derivation for every equivariant interval as a limit of the finite-population result |
| Tuned-coefficient frontier, spike formula, exact algorithm | not found in print | Mani et al. (arXiv:2505.20178) give the tuned estimator's finite-sample mean squared error under independent sampling. Hansen (2026) shows leverage can destroy any finite critical value for conventional intervals under Gaussian errors. Neither has the affine-sample characterisation or a frontier |
| Proof technique (limiting sequences, pigeonhole, compactness) | classical | Gleser and Hwang, Dufour |

What a paper could claim is the finite-population, graded form of the frontier with its matching possibility half, the tuned-coefficient frontier and its exact computation, and the consequences for few-cluster PPI. It could not claim the technique, the unrestricted impossibility or the iid limit. Four primary sources could not be read legally (section 5), and several checkers read some papers only from abstracts, so "not found" is the strongest verdict the evidence supports, not proof that no such paper exists.

## 4. What it would contribute to the paper `[proposed]`

A theory section of the PPI paper, "What few labelled clusters can and cannot guarantee", would run as follows. It would open with the frontier for the fixed coefficient as the main theorem, with the two-point extremal lemma and design minimaxity, and the table of required labelled clusters as its practical form. It would then give the tuned-coefficient frontier as the second theorem, the place where the predictions enter the theory, with the exact algorithm and the spike formula. It would close with the application, where every task lies beyond both frontiers at the sizes used. That explains, as a theorem rather than an observation, why every interval since round 5 under-covered, and it motivates the paper's empirical design comparison, the bounded-residual interval of the PPI paper's appendix, and the probe design as the three ways out. In the session's view this is a sharp and apparently new theory section, but a modest one. The proofs are short and the technique is classical. It strengthens a methods paper on labelling budgets for clustered PPI, and on its own it would be a short note rather than a paper for the venues Nicolas prefers.

## 5. For Nicolas

- **D1.** Whether this becomes the theory section of the PPI paper, as section 4 proposes. It may need David's view, since it makes the paper's theoretical content a sharp negative result with a design consequence.
- **Sources to obtain** (UNC library proxy), so the four provisional verdicts can be closed.
  1. Gleser and Hwang (1987), Annals of Statistics 15(4), 1351 to 1362. https://login.libproxy.lib.unc.edu/login?url=https://doi.org/10.1214/aos/1176350597
  2. Lanke (1974), "Interval estimation of a median", Scandinavian Journal of Statistics, 28 to 32 (venue as cited by Paul and Kuchibhotla; the DOI the session had was wrong). https://login.libproxy.lib.unc.edu/login?url=https://www.jstor.org/action/doBasicSearch?Query=Lanke+%22Interval+estimation+of+a+median%22
  3. Bakirov and Székely (2006), Journal of Mathematical Sciences 139(3), 6497 to 6505. https://login.libproxy.lib.unc.edu/login?url=https://doi.org/10.1007/s10958-006-0366-5
  4. Basu and DasGupta (1995), Annals of Statistics 23(4), 1433 to 1442. https://login.libproxy.lib.unc.edu/login?url=https://doi.org/10.1214/aos/1176324716
- **Open technical items,** not needed for the decision. They are an exact critical value below the frontier (claim K), an exact tuned frontier for ACS ($G = 51$, which needs a smarter search), and the boundary points.
