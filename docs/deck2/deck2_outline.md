# Presentation 2, outline (revision 3)

4 October 2026. This replaces revision 2. The audience is Dr. Zhu and Dr. Zhang. They know spatial transcriptomics, conformal prediction and PPI. What they have not seen is our own methodology work since the first half of the previous deck, and why each step was taken. So there are no background slides. The two that revision 2 had (the problem in one picture, and the two tools) are cut. In their place, every slide says in its first line why we did what it shows, and the formulas sit on the slides where they are used.

The structure is the one in `ST_presentation2.pdf`. Part 1 is from last time, part 2 is since last time. The pivot and the revised direction are one slide and come after the originality check. A slide on the data sets comes before the results.

There are 16 slides. The per-slide allowances sum to 23.5 minutes, down from 26. A cut list to about 20 is at the end.

Figures are named F1 to F13 and are built. Numbers are in a numbers file built by script. Both are listed in the last section. Nothing on the slides refers to them by file.

---

## Part 1. From last time

### Slide 1. Title and roadmap (30 seconds)

- Title. "Labelling budgets for prediction-powered inference with clustered data. Spatial transcriptomics update."
- Roadmap in two lines. Where we were last time. What happened since, in order, ending with new results and what comes next.

### Slide 2. 1a. Our read on the literature (45 seconds)

Slide 7 of the previous deck, with three facts refreshed from the new search.

- Accuracy has a low ceiling. On HEST-1k the best average correlation moved from 0.41 to 0.42 in two years and 25 models.
- Embeddings carry the site. The medical centre is recoverable from a patch with 88 to 98% accuracy across 20 foundation models.
- Predicted expression is used downstream as if measured. One model trained on 14 patients was applied to 1,096 archive samples to derive prognostic signatures.
- Few ask how wrong a prediction is, or how to do valid inference with it. That gap is where we chose to work, and not on predicting better.

### Slide 3. 1b. The two original topics (45 seconds)

Slide 8 of the previous deck.

- Topic A. Calibrated uncertainty for a predicted spot. A conformal interval around each prediction that keeps its coverage when the slide or donor is new.
- Topic B. Valid inference for a population quantity. A PPI confidence interval for, say, the relationship between morphology and expression across a cohort, using predictions plus a small measured set.
- What made both non-trivial. Conformal prediction and PPI both assume independent units. Spots are nested in slides and slides in donors.

### Slide 4. 1c. Efforts toward the two topics (1.5 minutes)

Left. The three-panel strip from the previous deck's slides 9 to 11.

Right.

- Before building on the predictor we checked what it gives us. Three findings.
  - The benchmark's prediction head has no intercept and spreads its predictions 1.84 times too widely.
  - A slide-and-session signature lives in the image features and not in the expression.
  - The unit of inference is the donor. Between-donor differences are 30 to 40% of expression variance, so thousands of spots per donor are worth far fewer independent observations.
- We then ran a first experiment for each topic. Conformal intervals under four ways of holding out calibration data. PPI with three ways of computing the variance. And a search for more data with several institutions, since Topic A was about shift between cohorts.
- A correction to last time. Two breast-cancer samples we presented as one donor are two donors from one laboratory.

---

## Part 2. Since last time

### Slide 5. 2a. Roadblocks (1.5 minutes)

Left. Figure F1 (coverage by calibration design, and the same model calibrated on other donors against blocks of its own training slides).

Right. Three measured facts, each of which closed part of Topic A as first stated.

- Coverage is a property of how calibration data are held out, not of the predictor. At a nominal 0.90 it is 0.89 with random spots, 0.86 with a held-out slide, 0.80 with a held-out donor. The order is the same for all twelve image models.
- Reweighting cannot repair the shift. Calibration and test slides can be told apart almost perfectly from their features (AUC 0.97), so importance weights leave about 2% of the calibration sample effective.
- The public data have no institution axis. No tissue-and-technology combination has three laboratories with three donors each.

Bottom line. "Calibrated uncertainty under cohort shift" is not answerable on these data. The shift that exists and can be measured is a new donor.

### Slide 6. What the first experiments did establish (1.5 minutes)

Left. Figure F2 (coverage of three intervals for a population quantity).

Right.

- Treating spots as independent is wrong by more than an order of magnitude. A nominal 90% interval covers 0.04. A donor-clustered variance with a $t$ reference covers 0.91.
- For a spot of a new donor, hierarchical conformal prediction (HCP) is valid, because it treats the $K$ calibration donors as the exchangeable units. Its set is finite only if

$$
K + 1 \ge \frac{1}{\alpha},
$$

  so a 90% set needs at least 9 calibration donors. With 10 donors it covers 0.97 and is 1.95 times as wide as the naive interval, which covers 0.86.
- Both topics ran into the same thing. The donor is the unit, there are few donors, and any method has to be stated in donors. This is what the rest of the work is built on.

### Slide 7. 2c. The originality check (2 minutes)

No figure. Two columns, and a line at the bottom.

Why we did it. Clustered versions of PPI and conformal prediction looked like the natural next step, and we wanted to know whether they were already done before building them.

On the inference side.

- PPI is the survey-sampling difference estimator, and PPI++ is the regression estimator (Mozer 2026). With clusters it is model-assisted estimation under two-stage sampling. So a "cluster-robust PPI" is not a new estimator.
- The cost of tuning $\lambda$ with few labels is known for independent data (Mani, Xu, Lipton and Oberst 2025).
- How much a covariate helps in a clustered design is known in the cluster-randomised-trial literature (Raudenbush 1997; Bloom and colleagues 2007).
- Not found anywhere. PPI with few labelled clusters, and the comparison of where to put the labels.

On the prediction-set side.

- Generalized hierarchical conformal prediction (GHCP; Mallick, Tchetgen Tchetgen, Dobriban and Lee, August 2026) starts from our observation that HCP is conservative with few groups, and uses a few labelled observations from the test group. Our idea of labelling a few spots on the test slide was their setting, six weeks before us.
- Not treated by them. Fewer than 20 groups, and what the labelled observations are worth against a plain split inside the test group.

Bottom line. The methods exist. What is missing is what they buy with few clusters, and how to spend a labelling budget.

### Slide 8. 2b and 2d. The pivot and the revised direction (2 minutes)

Left. Figure F3 (the two labelling regimes).

Right.

- After the roadblocks we considered four directions and kept two. Inference with predictions under clustering, and prediction sets for a new cluster. The originality check then moved the question from "which estimator" to "what does a labelling budget buy".
- One paper. Units nested in clusters, a black-box predictor, and a budget of labels to spend.
- Two ways to spend it. Regime A labels a few clusters fully. Regime B labels a few units in every cluster.
- Two targets. A confidence interval for a population quantity, and a prediction set for units of a new cluster.
- Three questions.
  1. How much do predictions buy?
  2. How many labelled clusters before they buy anything?
  3. Where should the labels go?
- The framing is general. Spatial transcriptomics is the main application and census income is a second one.

### Slide 9. The data sets and why they were chosen (1.5 minutes)

A table, no figure.

| data set | clusters | units | why it is here |
|---|---|---|---|
| Kidney cancer, Visium | 24 donors | 74,220 spots, median 2,893 per donor | the benchmark task with the most donors |
| Kidney, Visium, one laboratory | 25 donors | 31,425 spots, median 673 per donor | every technical factor held fixed, so differences between donors are biological |
| Lung, Xenium | 15 donors | 19,083 patches, median 1,124 per donor | a different technology and a predictor that is far more accurate at the donor level |
| Census income (ACS 2018) | 51 states, or 265 areas of California | 1,659,616 people | not biology, and the data set both the PPI software and the GHCP paper use, so numbers are comparable |

Below the table.

- Donor labels were audited against source records. On two benchmark tasks the shipped patient labels were wrong.
- Three image models are used as predictors, plus a permuted predictor that carries no information, as a control.
- The quantity estimated in most results is a within-donor slope of expression on a morphology feature, averaged over donors.

### Slide 10. Result 1. A valid interval with few labelled clusters (1.5 minutes)

Left. Figure F4 (coverage against number of labelled clusters, two panels).

Right.

- Why. Before asking what predictions buy, we needed an interval that holds its coverage with 4 to 12 labelled donors. The standard PPI interval is built for many independent units.
- The estimator averages over labelled clusters $L$, with $z_g$ a cluster's contribution and $f_g$ its predicted contribution, and $\bar F$ the mean of $f_g$ over all clusters,

$$
\hat\theta = \lambda\,\bar F + \frac{1}{n_L}\sum_{g \in L}\big(z_g - \lambda f_g\big), \qquad \widehat{\text{Var}} = \Big(1 - \frac{n_L}{G}\Big)\frac{s^2}{n_L}, \quad t_{n_L - 1}.
$$

- $\lambda = 0$ is the classical estimator and $\lambda = 1$ is PPI. PPI++ tunes it, here at the cluster level,

$$
\hat\lambda \approx \frac{\widehat{\text{Cov}}(z_g, f_g)}{\widehat{\text{Var}}(f_g)} .
$$

- Tuning $\lambda$ on the same clusters it is applied to under-covers with four clusters (0.86 to 0.87) and looks narrowest. Cross-fitting, where each half of the clusters uses the other half's $\lambda$, restores 0.90.
- When the clusters at hand are the population, the factor $(1 - n_L/G)$ is needed. Without it the interval covers 0.98 with 12 of 24 clusters labelled.
- Cross-fitting needs one more variance term, because the two halves carry different $\lambda$. On census income the estimated variance was 200 to 1,070 times too large without it and 0.89 to 1.04 times with it.

### Slide 11. Result 2. What predictions buy (2 minutes)

Left. Figure F5 (observed variance ratio against $1 - R^2_{\text{cluster}}$, every task and predictor). Figure F6 (one point per gene) as a second panel or a backup.

Right.

- Why. Image models are compared by spot-level correlation. With the donor as the unit, we wanted to know which property of a predictor decides whether it helps inference.
- Split outcome and prediction into a cluster part and a unit part,

$$
y_{gi} = \mu + u_g + e_{gi}, \qquad \hat y_{gi} = \nu + p_g + d_{gi}.
$$

- With many units per cluster the unit parts average away. At the best $\lambda$,

$$
\frac{\text{Var}(\hat\theta_{\text{PPI}})}{\text{Var}(\hat\theta_{\text{classical}})} \;\longrightarrow\; 1 - R^2_{\text{cluster}}, \qquad R^2_{\text{cluster}} = \text{Corr}(u_g, p_g)^2 .
$$

- This is the cluster-randomised-trial formula for a covariate, carried over to a black-box predictor.
- On data the observed ratio follows this floor. Lung 0.43 against a floor of 0.27. Census income 0.43 against 0.30. Kidney cancer 0.84 to 1.00 against 0.56 to 0.80.
- Across 459 genes the gain tracks cluster-level $R^2$ (rank correlation $-0.86$ to $-0.90$) far better than ordinary unit-level correlation ($-0.36$ to $-0.51$).
- The permuted predictor gains nothing, as it should.

### Slide 12. Result 3. The price of tuning (1.5 minutes)

Left. Figure F7 (observed ratio by number of labelled clusters, four data sets, each predictor's floor marked). Figure F8 (simulation, observed against predicted cost) as an inset or backup.

Right.

- Why. On the kidney data the observed gain was well short of the floor in result 2, and sometimes PPI was no better than the classical estimator. We needed to account for the gap.
- The gap is the cost of estimating $\lambda$ from a handful of clusters,

$$
\text{ratio} = 1 - R^2_{\text{cluster}} + \text{MSE}(\hat\lambda)\,\frac{\sigma_p^2}{\sigma_u^2}.
$$

- In simulation this matches the observed cost to within 0.04 in all 24 settings.
- Predictions pay for their own tuning only when

$$
n_L > 4 + \frac{2}{R^2_{\text{cluster}}}.
$$

- This is the rule of Mani and colleagues for independent data, with clusters in place of units. The consequence is new. What counts is the number of labelled clusters and the cluster-level $R^2$, not the number of labelled units.
- About 7 clusters on lung and census income, 9 for the best model on kidney cancer, 11 or more for the rest. That is why lung gains and most kidney cases do not.

### Slide 13. Result 4. Where to put the labels (2 minutes)

Left. Figure F9 (variance against budget, regime A and regime B, three tissues). Figure F10 (regime B, predicted against observed) as a second panel or backup.

Right.

- Why. Results 2 and 3 say that with few labelled donors, predictions buy little. The same labels could instead be spread thinly over every donor, and the originality check found no comparison of the two.
- In regime B every cluster is observed, so the clusters act as strata and cluster-level error drops out. For a fixed set of $G$ clusters, with $m$ labelled units out of $M_g$ in cluster $g$ and $S^2_{r,g}$ the within-cluster variance of $y - \lambda\hat y$,

$$
\text{Var}_B = \frac{1}{G^2}\sum_{g=1}^{G}\Big(1 - \frac{m}{M_g}\Big)\frac{S^2_{r,g}}{m}, \qquad \frac{\text{Var}_B(\text{PPI})}{\text{Var}_B(\text{classical})} = 1 - R^2_{\text{within}} .
$$

- So the two regimes are governed by different properties of the predictor. Cluster-level accuracy in A, within-cluster accuracy in B.
- At the same number of labelled spots, regime B gives the narrower interval on every tissue when regime A has 8 or fewer donors. With a donor costing as much as 10 spots it is narrower in 216 of 232 comparisons.
- It reverses when touching a cluster is expensive. The best number of units per cluster is

$$
m^\star = \sqrt{\frac{c_{\text{cluster}}}{c_{\text{unit}}}\cdot\frac{\sigma^2_{\text{within}}}{\sigma^2_{\text{between}}}},
$$

  with the variances of the outcome for the classical estimator and of $y - \lambda\hat y$ for PPI.
- This comparison was not found in the literature. It is the result we would lead with.

*One bullet on this slide is held back until the two open points are settled. See the note at the end.*

### Slide 14. Result 5. Prediction sets for a new donor (2 minutes)

Left. Figure F12 (width of a valid set against labelled units in the new cluster, four data sets). Figure F11 (coverage and width against number of calibration donors) as a second panel.

Right.

- Why. Topic A survived as prediction sets for a new donor. HCP is valid there but wide with 10 to 25 donors, and GHCP proposes labelling a few spots on the new donor. We asked what those spots are worth at our numbers of donors.
- We reproduced GHCP from its released code and then mapped what a valid 90% set costs, over the number of calibration donors $K$ and the number $o$ of labelled spots on the new donor.
- No labelled spots. HCP is the method. Its width over the naive interval falls from 1.95 at $K = 10$ to 1.36 at $K = 20$.
- With 10 donors, a few labelled spots do not help. GHCP with 5 or 10 spots is 1.2 to 1.5 times wider than HCP with none.
- From about 10 labelled spots, an ordinary split inside the new donor is valid, covers 0.91, and is about half GHCP's width. It needs $\lceil 0.9\,(o+1) \rceil \le o$, that is $o \ge 9$.
- A short proposition of our own for very few donors. If $K + 1 < 1/\alpha$, every valid method must return an infinite set with probability at least

$$
1 - \alpha\,(K + 1),
$$

  and a finite set must over-cover.

### Slide 15. Result 6. One design for both targets (1 minute)

A table, no figure.

Why. Both targets spend labelled spots, so we asked whether one labelling design can serve the confidence interval and the prediction set together.

| data set | labelled spots per donor | confidence interval, width against classical | its coverage | cheapest valid prediction set | its coverage |
|---|---|---|---|---|---|
| Kidney cancer | 14 | 0.83 | 0.89 | split inside the donor | 0.91 |
| Kidney cancer | 84 | 0.81 | 0.89 | split inside the donor | 0.92 |
| Kidney, one laboratory | 51 | 0.84 | 0.90 | split inside the donor | 0.92 |
| Lung | 36 | 0.43 | 0.90 | split inside the donor | 0.93 |

- Tens of labelled spots on every donor serve the confidence interval and the prediction set at once.
- A few fully labelled donors serve neither as well.
- Not yet tested. Fewer than 6 labelled spots per donor.

### Slide 16. Summary, next steps, and questions for you (1.5 minutes)

What we can now say.

- Under cluster sampling, predictions buy at most $1 - R^2_{\text{cluster}}$, and nothing until about $4 + 2/R^2_{\text{cluster}}$ clusters are labelled.
- Spreading labels over every cluster beats concentrating them, unless touching a cluster is expensive.
- For a new cluster, the price of a valid prediction set is mapped, and for very few clusters it is characterised.

Next steps.

- Which clusters to label, not only how many.
- An estimand for unit-weighted quantities under which the gain is real.
- A direct comparison with GHCP in its own setting of 20 groups.
- Writing.

Questions for Dr. Zhu and Dr. Zhang.

- Does this direction sound right to you, and is the scope right for a first paper?
- Which of the three results would you lead with?
- Are there directions you think are worth exploring from here, in spatial transcriptomics or beyond it?

---

## Backup slides

- B1. The permuted-predictor check on unit-weighted estimands.
- B2. Optimal units per cluster, with and without a predictor, on each data set.
- B3. The lower bound for very few clusters (figure F13).
- B4. Methods tried for prediction sets with no labelled test units, and why none improved on HCP.
- B5. The previous deck's backup slides.

---

## Timing

| slides | content | minutes |
|---|---|---|
| 1 to 4 | from last time | 3.5 |
| 5 to 6 | roadblocks, what the first experiments established | 3 |
| 7 to 9 | originality check, revised direction, data sets | 5.5 |
| 10 to 15 | new results | 10 |
| 16 | summary and questions | 1.5 |

That sums to 23.5 minutes. Cutting the two background slides saved 2.5.

**To reach about 20.** Each line gives the saving.

- Fold slide 15 into the last bullet of slide 13. One minute.
- Show one figure and three or four bullets on each of slides 11, 13 and 14. One and a half minutes.
- Merge slides 2 and 3 into one. Half a minute.
- Take slide 4 down to the donor-as-unit bullet and the correction. Three quarters of a minute.

That removes just under four minutes and lands at about 20. To go lower, move result 1 (slide 10) to backup and keep only its estimator and $\hat\lambda$ formulas, placed at the top of slide 11.

---

## Held back, as you asked

Two points are not resolved in this revision. Both wait until you have read the explainer.

1. A footnote on slide 11 about the floor and the observed ratio coming from two different computations.
2. On slide 13, how much of regime B's gain on the kidney tasks comes from the image model. Figure F10 already shows the permuted predictor on the same line as the real ones, so it can carry either wording.

---

## Preparation, built and checked

**Numbers.** `results/summary/deck2_numbers.csv`, 464 rows, written by `code/scripts/deck2_numbers.py`. Every row has the value, the form shown on the slide, the source file and how it was read. Nothing is typed in.

**Figures.** `figures/deck2/`, written by `code/scripts/deck2_figures.py` from the same result files. Labels use plain names only.

| id | file | slide | shows |
|---|---|---|---|
| F1 | `f01_coverage_by_design.png` | 5 | coverage by calibration design, and donors against blocks |
| F2 | `f02_spot_vs_donor_interval.png` | 6 | coverage of three intervals for a population quantity |
| F3 | `f03_two_regimes_schematic.png` | 8 | the two labelling regimes |
| F4 | `f04_interval_coverage_simulation.png` | 10 | coverage against labelled clusters, by tuning rule and by correction |
| F5 | `f05_gain_floor_vs_observed.png` | 11 | observed ratio against $1 - R^2_{\text{cluster}}$ |
| F6 | `f06_gain_across_genes.png` | 11 | one point per gene, two measures of accuracy |
| F7 | `f07_ratio_by_labelled_clusters.png` | 12 | observed ratio by labelled clusters, with floors |
| F8 | `f08_tuning_cost_simulation.png` | 12 | observed against predicted tuning cost |
| F9 | `f09_regime_A_vs_B.png` | 13 | variance against budget in the two regimes |
| F10 | `f10_regimeB_predicted_vs_observed.png` | 13 | regime B width ratio, predicted against observed |
| F11 | `f11_prediction_sets_by_K.png` | 14 | coverage and width against calibration donors |
| F12 | `f12_prediction_sets_by_labelled_units.png` | 14 | width of valid sets against labelled test units |
| F13 | `f13_lower_bound_small_K.png` | backup | forced infinite sets and the coverage floor |

**Still to draw.** The three-panel strip for slide 4, from the previous deck's figures. The schematic that revision 2 planned for the cut slide is no longer needed.

**Not built.** The slides.
