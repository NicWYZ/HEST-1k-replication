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

### B.1 The optimality theorem for ordinary data, and three senses of "beaten" (transcribed and derived)

Tibshirani, Barber and Ramdas, Theorem 7 (arXiv:2608.27310, p. 12). Fix an i.i.d. law $P = P_{X,Y}^{n+1}$ whose conditional density $p_{Y \mid X}$ is positive. Among all mappings from $X_{n+1}, Z_1, \dots, Z_n$ to a set with coverage $1 - \alpha$ over every exchangeable law, expected Lebesgue measure under $P$ is minimised by the randomised conformal predictor with score $1/p_{Y \mid X = x_{n+1}}(y_{n+1})$. The proof is Neyman and Pearson with a least favourable law, the uniform law over permutations of the observed bag.

Three senses of "beaten" for grouped data, with the method set $\mathcal{V}$ of all methods valid over every law $\Pi$ on group laws.

1. Dominated. Method $A \in \mathcal{V}$ is dominated if some $B \in \mathcal{V}$ has $E_\Pi[\mathrm{width}(B)] \le E_\Pi[\mathrm{width}(A)]$ for every $\Pi$, with strict inequality for some $\Pi$.
2. Beaten at a law. $A$ is beaten at $\Pi_0$ if some $B \in \mathcal{V}$ has $E_{\Pi_0}[\mathrm{width}(B)] < E_{\Pi_0}[\mathrm{width}(A)]$.
3. Beaten in the minimax sense over a named class $\mathcal{C}$. Some $B \in \mathcal{V}$ has $\sup_{\Pi \in \mathcal{C}} E_\Pi[\mathrm{width}(B)]/q^\star(\Pi) < \sup_{\Pi \in \mathcal{C}} E_\Pi[\mathrm{width}(A)]/q^\star(\Pi)$.

Theorem 7 answers sense 2, for ordinary data. At each law it names the best valid method, so any method that differs from it on a set of positive probability is beaten at that law. It does not by itself settle sense 1. A dominating method must tie with the pointwise optimum wherever the dominated method is that optimum. Theorem 7 says nothing about whether a fixed-score method can be improved everywhere at once. Sense 3 is not addressed. Round 4's attempt at sense 3 failed (`docs/round4_conf_lower_bound.md` section 6, step 1), because the ratio is unbounded on heavy-tailed degenerate laws for every valid method.

### B.2 The baseline is randomised HCP (definition)

HCP's threshold is $Q_{1-\alpha}(\nu)$, with

$$
\nu = \frac{1}{K+1} \sum_{k=1}^{K} \frac{1}{N_k} \sum_{i=1}^{N_k} \delta_{s_{ki}} + \frac{1}{K+1} \delta_{+\infty}.
$$

At the atom where the cumulative mass first reaches $1 - \alpha$, it rounds up. Randomised HCP returns the next lower atom with the probability that makes coverage under the permutation form exactly $1 - \alpha$, in the way the randomised conformal p-value of Theorem 7's form (37) does. Deterministic HCP is beaten at every law by its own randomisation whenever the rounding binds. That is not the question, so randomised HCP is the baseline.

### B.3 The revealed-law model: validity is the permutation form and nothing more (derived)

In the model where each calibration group's law is seen exactly, the data are $F_1, \dots, F_K$ drawn i.i.d. from $\Pi$, and the target is one draw $S \sim F_{K+1}$ with $F_{K+1} \sim \Pi$ unseen. Write $D_{-j}$ for the $K$ laws other than $F_j$.

Claim. A method $\hat q$ that is symmetric in the calibration groups is valid for every $\Pi$ if and only if, for every configuration $\{F_1, \dots, F_{K+1}\}$ of distinct laws,

$$
\frac{1}{K+1} \sum_{j=1}^{K+1} F_j\bigl(\hat q(D_{-j})\bigr) \ge 1 - \alpha .
$$

Argument. Sufficiency: condition on the bag of the $K + 1$ laws. Under i.i.d. sampling from $\Pi$, the unseen law is equally likely to be any one of them, so coverage is the average of the left side over bags. Necessity is round 4's section 2. Take $\Pi$ uniform on a large finite set of distinct laws, so that draws are distinct with probability tending to one, and validity at every such $\Pi$ forces the inequality at each configuration. In Tibshirani, Barber and Ramdas' language, this is Neyman structure with respect to the bag of laws. Their completeness step uses the uniform law over permutations of one bag, which is exchangeable but not i.i.d. Round 4's limiting argument is what replaces it for the i.i.d. class. So within the revealed-law model, universality lifts. Every valid symmetric method is characterised by the displayed inequality and by nothing more.

Is HCP a conformal method on this model? HCP keeps $s$ exactly when

$$
\frac{1}{K+1}\Bigl(1 + \sum_{k=1}^{K} P_{F_k}(S' \ge s)\Bigr) > \alpha ,
$$

up to the tie convention at the boundary. The left side is the expectation of the single-draw conformal p-value of Dunn, Wasserman and Ramdas' "subsampling once" (their Theorem 5), over the draw of one score per group. So, in the revealed-law limit, HCP is the limit as $B \to \infty$ of their repeated-subsampling p-value, an average of conformal p-values. It is not a conformal set of form (15) for a single draw. That an average of p-values is valid here, where Dunn, Wasserman and Ramdas guarantee only $1 - 2\alpha$ for averages in general, is Lee, Barber and Willett's result. The derivation above shows why. The average is taken over the within-group draw and not over the permutations, so the permutation form still holds exactly. Round 4's section 6 item 2 is a second reading of the same fact: group-level full conformal with the test law replaced by a point mass at the candidate returns HCP's set.

### B.4 What round 4 already settles, stated as a result (derived in round 4, restated)

Result. Let $K + 1 > 1/\alpha$, and let the laws be revealed exactly. The repaired switching rule of `docs/round4_conf_lower_bound.md` section 8.3 is valid for every $\Pi$. Its HCP branch runs at level

$$
1 - \alpha' = \frac{(K-1)\bigl[(1-\alpha)(K+1)/K + d\bigr] + 1}{K+1},
$$

and its pooled branch at $1 - \alpha + 2d$, with $d$ the Kolmogorov homogeneity tolerance. On configurations whose laws are all within $d$ of each other, its threshold is the pooled quantile at level $1 - \alpha + 2d$. That is narrower than HCP's, whose level is about $(1-\alpha)(K+1)/K$. So HCP is beaten at the homogeneous law, sense 2. On configurations that fail the check, the rule uses HCP at the stricter level $1 - \alpha' > 1 - \alpha$, so it is wider than HCP there and does not dominate HCP (sense 1). At $K = 10$ and $\alpha = 0.1$, $1 - \alpha'$ is 0.900909 at $d = 0$ and 0.941818 at $d = 0.05$ (`results/round4/conformal/C2_candidates/lower_bound/c2_lb_case3.csv`).

Conditions. The result holds with laws revealed exactly. With finite group sizes the check uses empirical CDFs, and round 4's section 8.4 shows a possible coverage loss of $K\gamma$ for a per-group DKW level $\gamma$. Exact validity then needs $\gamma$ of order $\alpha/K$, charged to the level, and the band widens $d$ by $2\epsilon_{N}$. That is 0.3255, 0.1456 and 0.0728 in Kolmogorov distance at $N_k = 100$, 500 and 2000 with $\gamma = 0.01$ (same file). So at the group sizes of this project the homogeneous-law gain is small or absent.

Step 5 of the instruction's order, the question of dominance, is not started. It belongs to the W3 interval, under the part B cap.
