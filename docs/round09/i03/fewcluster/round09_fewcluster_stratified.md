# Round 9, track fewcluster, the frontier for stratified designs (Theorem 3)

*27 October 2026. Written by the fewcluster session for steps I3-1 and I3-2. These are the first of the three pieces of work the paper outline (`docs/round09/i02/fewcluster/round09_fewcluster_paper_outline.md`) lists before drafting. The statements were proved by the session and again by a fresh agent from the statements alone, with exact enumeration at small sizes (`results/round9/fewcluster/verify_strat/verify_strat_report.md`). The verifier's corrections are folded in below and listed in section 6. Predictions were written before each run (`results/round9/fewcluster/strat/predictions_before_run.md`) and are scored in `predictions_scored.md` beside it. The literature position (section 7) is provisional. Recommendations are `[proposed]`.*

## 1. Why this theorem

Theorem 1 (`docs/round09/i01/fewcluster/round09_fewcluster_frontier.md`) covers simple random sampling of whole clusters. Two designs the paper needs are outside it. One labels an atypical cluster with certainty and samples the rest, which is a stratified design with a take-all stratum. The other labels a few units in every cluster, which is regime B of rounds 4 to 8, a stratified design with the clusters as strata. Theorem 3 gives the frontier for every stratified design. With it the comparison of regimes A and B becomes a statement about which designs can carry a finite-sample guarantee at all.

## 2. Setting

There are strata $h = 1, \dots, H$, stratum $h$ with $N_h$ units and fixed-coefficient residuals $e_{h1}, \dots, e_{hN_h}$. From stratum $h$ a sample $S_h$ of $n_h$ units is drawn by simple random sampling without replacement, independently across strata, with $2 \le n_h \le N_h$. A stratum with $n_h = N_h$ is take-all, and $P$ denotes the strata with $n_h < N_h$. With known weights $W_h > 0$ the target, the estimator and its standard error are

$$
\theta = \sum_h W_h \bar e_h, \qquad T = \sum_h W_h \bar e_{S_h}, \qquad \mathrm{SE}^2 = \sum_h W_h^2 \Big(1 - \frac{n_h}{N_h}\Big) \frac{s_h^2}{n_h},
$$

and the design variance of $T$ is

$$
V = \sum_h V_h, \qquad V_h = W_h^2 \Big(1 - \frac{n_h}{N_h}\Big) \frac{S_h^2}{n_h}, \qquad S_h^2 = \frac{1}{N_h - 1} \sum_i (e_{hi} - \bar e_h)^2 .
$$

A procedure is equivariant if it moves with the group that shifts each stratum separately and rescales all strata together,

$$
e_h \mapsto b\, e_h + a_h \ (b > 0), \qquad \theta \mapsto b\,\theta + \sum_h W_h a_h ,
$$

which the stratified interval $T \pm c\,\mathrm{SE}$ does. Write $v_h = V_h / V$ for stratum $h$'s share of the design variance and

$$
\kappa_h = \frac{\max_i (e_{hi} - \bar e_h)^2}{\sum_i (e_{hi} - \bar e_h)^2}
$$

for its own max-share, with $\kappa_h = 0$ when $S_h = 0$. The share of unit $(h, i)$ in $V$ is then $v_h (e_{hi} - \bar e_h)^2 / \sum_j (e_{hj} - \bar e_h)^2$, so the largest share of one unit is

$$
\kappa_{\mathrm{st}} = \max_h v_h \kappa_h .
$$

For a stratum in $P$ and $1 \le k \le N_h/2$ the two quantities of Theorem 1 become

$$
\pi_h(k) = \frac{\binom{N_h - k}{n_h} + \binom{k}{n_h}}{\binom{N_h}{n_h}}, \qquad \kappa_{2,h}(k) = \frac{1 - k/N_h}{k},
$$

and $R_h$ is Proposition 3's bound for populations without a level set of half the stratum.

## 3. Theorem 3

A class is any set of the form $\mathcal{K}(A) = \{e : V > 0,\ (v_h, \kappa_h)_{h \in P} \in A\}$ with $A$ closed and monotone in $\kappa$, so that lowering any $\kappa_h$ keeps a point in $A$. A configuration is a nonempty set $S \subseteq P$, minority sizes $1 \le k_h \le N_h/2$ for $h \in S$, and shares $v$ supported on $S$. It lies in $A$ if $(v, (\kappa_{2,h}(k_h))_{h \in S}) \in A$, and its value is $\prod_{h \in S} \pi_h(k_h)$.

**Theorem 3a (impossibility).** *If a configuration in the interior of $A$ in the $\kappa$ direction has value above $\alpha$, then every equivariant procedure with coverage at least $1 - \alpha$ over $\mathcal{K}(A)$ is unbounded with probability at least the value minus $\alpha$ under every population. If the configuration lies in $A$ only on its boundary, the conclusion holds at the two-point population itself.*

Take the population that is two-point in each stratum of $S$, with values $a_h$ on $k_h$ units and $0$ on the rest, and constant elsewhere. Let $E$ be the event that every sampled stratum of $S$ falls inside one of its two groups. The strata are independent, so

$$
P(E) = \prod_{h \in S} \pi_h(k_h).
$$

On $E$ each stratum's sample is constant at some $\sigma_h a_h$, $\sigma_h \in \{0, 1\}$. The per-stratum shifts carry the data to the all-zero data, which the rescaling leaves fixed, so a bounded equivariant procedure there returns at most the single point

$$
t_\sigma = \sum_{h \in S} W_h \sigma_h a_h, \qquad \text{while} \qquad \theta = \sum_{h \in S} W_h a_h \frac{k_h}{N_h}.
$$

Since $0 < k_h/N_h \le 1/2$, choosing the $a_h$ off finitely many hyperplanes makes $t_\sigma \ne \theta$ for every pattern $\sigma$. The $a_h$ can also be chosen so that the shares $v_h$ are any point of the open simplex over $S$. So the procedure misses or is unbounded on $E$. The verifier added the perturbation that carries this to every population, as in Theorem 1, which needs the configuration to stay in $A$ when the population is jittered. That is where the interior is used. $\square$

**Theorem 3b (possibility).** *Let $\beta(A)$ be the largest, over $\mathcal{K}(A)$, of the probability that every stratum in $P$ draws a constant sample. If $\beta(A) \le \alpha$, there is a finite $c$ such that $T \pm c\,\mathrm{SE}$ (a point when $\mathrm{SE} = 0$) covers $\theta$ with probability at least $1 - \alpha$ at every population in $\mathcal{K}(A)$. Moreover,*

$$
\beta(A) \le \max \Big\{ \prod_{h \in S} \ell_h \Big\},
$$

*where the maximum is over $S$, shares $v$ on $S$ and per-stratum levels $(\ell_h, \kappa_h)$ equal to $(\pi_h(k), \kappa_{2,h}(k))$ for some $k \le N_h/2$ or to $(R_h, 1/N_h)$, with $(v, \kappa) \in A$.*

The first part is Theorem 2's compactness argument with every stratum centred and $V = 1$. That set is compact because take-all strata enter neither $T - \theta$ nor $\mathrm{SE}$, and $\mathcal{K}(A)$ is closed in it because $A$ is closed. If no finite $c$ works, a fixed set $W$ of more than $\alpha$ of the samples is missed along a sequence $c_j \to \infty$, with populations converging in the class. A missed sample has

$$
\mathrm{SE}(e_j) < \frac{|T - \theta|(e_j)}{c_j} \to 0 ,
$$

so every stratum in $P$ is constant on the samples of $W$ under the limit, contradicting $\beta(A) \le \alpha$. For the bound, a population in the class has

$$
P(\mathrm{SE} = 0) = \prod_{h : V_h > 0} P_h(\text{constant}).
$$

Lemma 1 and Proposition 3 of the frontier note give each factor a level with $\ell_h \ge P_h(\text{constant})$ and level $\kappa$ at most $\kappa_h$, and monotonicity keeps the configuration in $A$. $\square$

## 4. Two classes

**The pooled class** caps every unit's share, $A = \{\max_h v_h \kappa_h \le \kappa_0\}$. A configuration lies in it when shares with $v_h \kappa_{2,h}(k_h) \le \kappa_0$ can be chosen to sum to one, that is when

$$
\sum_{h \in S} \frac{1}{\kappa_{2,h}(k_h)} = \sum_{h \in S} \frac{k_h N_h}{N_h - k_h} \ge \frac{1}{\kappa_0}.
$$

So the frontier is a multiple-choice knapsack. Each stratum offers levels with a cost $-\log \pi_h(k)$ and a capacity $k N_h/(N_h - k)$. The frontier is $1/\mathrm{Cap}^\ast$, where $\mathrm{Cap}^\ast$ is the largest total capacity at total cost below $\log(1/\alpha)$ (`code/scripts/round9_fewcluster_strat_frontier.py`, which brackets it between two rounded dynamic programmes). With one stratum it is Theorem 1's $\kappa_2(k^\ast - 1)$, exactly whenever $k^\ast$ exists (22 of 22 grid cells here, 2216 cases for the verifier). Two strata of 12 with 4 drawn in each give 0.156, against 0.158 for 8 of 24 unstratified (`results/round9/fewcluster/strat/i31_checks.txt`).

**The box class** bounds every residual by $\Lambda_0$ standard deviations of its own stratum and every stratum's share of the variance by $v_0$,

$$
A = \big\{ \kappa_h (N_h - 1) \le \Lambda_0^2 \ \text{and}\ v_h \le v_0 \ \text{for all } h \big\}.
$$

The shares must sum to one with none above $v_0$, so a configuration needs at least $\lceil 1/v_0 \rceil$ strata, and in each the smallest admissible minority is

$$
k_{\min,h} = \Big\lceil \frac{N_h (N_h - 1)}{N_h \Lambda_0^2 + N_h - 1} \Big\rceil .
$$

Since $\pi_h$ falls as $k$ grows, the worst value is the product of the $\lceil 1/v_0 \rceil$ largest $\pi_h(k_{\min,h})$ (`code/scripts/round9_fewcluster_box.py`). The verifier proved that this equals $\beta$ exactly when two-point levels are admissible ($\Lambda_0 \ge 2$ is enough), and matched it by brute force in 360 of 360 cases. It also found the $R_h$ level necessary for smaller $\Lambda_0$ in odd strata. The class is empty when fewer than $\lceil 1/v_0 \rceil$ strata are sampled.

The pooled class is the direct analogue of Theorem 1, and it is the wrong class when strata differ in size. It compares a person in Wyoming with a person in California on one scale. The adversary then puts all the variance in the largest stratum, where two-point populations have shares near $1/N_h$. The box class bounds each stratum on its own scale and adds the one assumption pooling needs, that no stratum dominates the variance.

## 5. What it shows

**Pooling beats the per-stratum limit.** One stratum alone is impossible for every class as soon as $\pi(\lfloor N/2 \rfloor) > \alpha$, which for large $N$ is the iid threshold $m < \log_2(2/\alpha) = 4.32$ at $\alpha = 0.10$. With many strata a degenerate sample must occur in several strata at once, and the probabilities multiply. For 24 clusters of 2000 units drawn 4 per cluster, the pooled frontier is $4.73 \times 10^{-4}$. Over 200 populations of independent standard normal units, 0.875 lie inside it at $m = 4$ and all at $m = 5$, against 0.26 at $m = 3$.

**Regime A against regime B on the real tasks.** At $\alpha = 0.10$ and with predictions ($\lambda = 1$), each population is judged at its own $(\Lambda_0, v_0)$ for regime B and by Theorem 1 on the cluster means for regime A (`results/round9/fewcluster/strat/i32_acs_box.csv`, `i32_hest_box_summary.csv`, `i32_hest_box_genes.csv`).

| Task | Regime A, clusters needed (median over genes) | Regime B, units per cluster needed (median, 90th percentile) | Largest residual within a cluster (median, within-cluster SDs) | Clusters that must degenerate at once ($\lceil 1/v_0 \rceil$ at $m = 10$, median) |
|---|---|---|---|---|
| ACS by state, 51 states | 11 | 5 | 8.9 | 40 |
| CCRCC, 24 donors | 17 | 6, 10 | 5.3 | 13 |
| INDIANA_KIDNEY, 25 donors | 13 | 8, 12 | 6.3 | 13 |
| LUNG_XENIUM, 15 donors | 8 | 8, 25 | 5.3 | 9 |

On ACS, regime A needs at least 11 of 51 whole states, between 54,539 and 931,765 persons depending on which states, while regime B needs 5 persons in each, 255 in all. On CCRCC, regime A needs 17 of 24 whole donors, while regime B needs about 6 spots in each donor. Under the pooled class, ACS regime B lies beyond the frontier at every $m$ up to 30 (largest share $3.1 \times 10^{-4}$ against $6.4 \times 10^{-5}$ at $m = 30$), for the reason given in section 4.

**The requirement as a design table.** For large clusters ($N_h = 2000$), the units per cluster that regime B needs are these. With $N_h = 20{,}000$ no entry of this table changes by more than 5 (`i32_required_m_B.csv`).

| $\Lambda_0$ | $v_0 = 0.025$ | $0.05$ | $0.1$ | $0.2$ | $0.5$ | $1$ |
|---|---|---|---|---|---|---|
| 3 | 2 | 2 | 3 | 5 | 11 | 22 |
| 4 | 2 | 2 | 4 | 8 | 19 | 38 |
| 6 | 3 | 5 | 9 | 17 | 41 | 81 |
| 8 | 4 | 8 | 15 | 30 | 73 | 143 |

For regime A with the same $\Lambda_0$ on the cluster means (`i32_required_n_A.csv`), 24 clusters need 13 labelled at $\Lambda_0 = 3$ and 17 at $\Lambda_0 = 4$, and 51 clusters need 16 and 27. With $G$ clusters no standardized residual can exceed $(G - 1)/\sqrt{G}$, which is 4.69 at $G = 24$, so larger $\Lambda_0$ are vacuous there. The $v_0 = 1$ column is a design with no assumption across clusters, and there regime B needs 22 to 143 units per cluster. The gain of regime B rests on the assumption that no cluster carries a large share of the variance, and the paper has to state it as an assumption.

**Take-all.** A take-all stratum has $v_h = 0$ and never enters the frontier, so labelling a cluster with certainty removes it from the class. The I2-3 computation (CCRCC with INT5 taken, 0.94 of genes still beyond) is now covered by the theorem.

## 6. What the verifier changed

1. The impossibility half needs the strict form. At equality only the weak version survives, and the verifier gives a counterexample at $N = 8$, $\kappa_0 = 1/N$. The defeating population must be generic, so that the collapsed point differs from $\theta$, and this is part of the proof.
2. The reduction to Theorem 1 is exact when $k^\ast$ exists. When it does not and $N$ is odd, the $R$ level separates the two bounds.
3. The pooled frontier at 24 clusters of 2000 with 4 per cluster is $4.7325 \times 10^{-4}$, inside the session's bracket of 4.7228 to $4.7349 \times 10^{-4}$. "Each stratum alone is impossible" holds for $\kappa_0 > 1/N$, and its condition is $\pi(N/2) > \alpha$ (0.1246 here), with $m < \log_2(2/\alpha)$ the large-$N$ form. The verifier's 20 normal populations had largest shares from $3.0 \times 10^{-4}$ to $6.7 \times 10^{-4}$, so single populations can lie beyond. The session's first run of 21 populations had put all of them inside at $m = 4$, and the rerun over 200 gives 0.875 (section 5).
4. The general form has a weak and a strong version (section 3), and the box class needs the $R$ level for $\Lambda_0 < 2$ in odd strata.
5. An adversarial search at $\kappa_0 = 0.99/\mathrm{Cap}_{\mathrm{up}}$ in five small designs ($N_h \le 8$) needed critical values of 9.6 to 13.6. That is a lower bound on the true worst case and bears on step I3-3.

## 7. Literature, provisional

NOV10 found none of the three results (46 queries, six neighbours read in full text, `results/round9/fewcluster/novelty/novelty_NOV10_structured.json` and the CSVs beside it).

1. The stratified frontier and its knapsack and box forms were not found. The ingredients are in print separately. These are the single-sample threshold (Lanke 1974; Paul and Kuchibhotla, arXiv:2403.06357), the extremal shape of $k$ equal nonzero variances (Bakirov and Székely 2006), the finite-sample leverage condition in Gaussian regression (Pötscher and Preinerstorfer, arXiv:2412.17470), and asymptotic Lindeberg conditions for stratified sampling (Bickel and Freedman 1984; Hájek 1960).
2. That pooling restores inference is in print qualitatively. Ibragimov and Müller (2010, 2016) show that the $t$-test on a few heterogeneous group estimates is valid at small $\alpha$, and Canay, Romano and Shaikh (2017) give sign-change tests with few clusters. Both rest on asymptotically Gaussian or symmetric group statistics from large groups, not on a few draws per stratum from a finite population.
3. The finite-sample comparison of whole-cluster and within-cluster labelling was not found. Broska and Howes (arXiv:2610.09601) compare the same labelling designs through asymptotic variance only and defer small-sample questions.

The session then screened OpenAlex forward citations of Ibragimov and Müller (2010, 2016), Bakirov and Székely, Canay, Romano and Shaikh, and Bickel and Freedman (`openalex_forward_NOV10.csv`, `openalex_queries_NOV10.csv`). Of 755 citing works, 80 match finite-population or design keywords, and none states the result by title or abstract. Four of them need a full read and are with a second checker (NOV10b), which is waiting on an approval card. They are Kojevnikov and Song on impossibility with few large clusters, Müller's "A More Robust t-Test", Hagemann's permutation inference with a finite number of heterogeneous clusters, and Pötscher and Preinerstorfer's "Valid Heteroskedasticity Robust Testing". NOV10 read Ibragimov and Müller, Bakirov and Székely, and Canay, Romano and Shaikh only from abstracts, so the verdicts stay provisional until NOV10b reports. The proof technique is Theorem 1's and is not claimed. What may be new is the product form over strata, the two classes and the regime comparison they give.

## 8. For the paper `[proposed]`

Theorem 3 is the product-form theorem the outline planned, and it fills item 5 of the outline's section 3. The regime comparison it gives is the paper's clearest labelling-budget result. On the tasks here, labelling whole clusters needs between 11 of 51 and 17 of 24 of them before any scale-free guarantee is possible. Labelling a few units in every cluster can carry one with single-digit units per cluster, provided no cluster carries more than a small share of the design variance. The design table of section 5 is its practical form. The assumption across clusters is the price, and the paper should present the $v_0 = 1$ column beside it.
