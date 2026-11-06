# F3 SCALE, interval 2 note (26 October 2026)

## Outcome in one paragraph

The track stops. The covariance side of the claim is a plain sample covariance and needs no second scale. The ceiling side is identified by the Poisson assumption alone, and without it only by a shape assumption on the latent covariance, which is the geostatistical nugget problem. The spatial CLT is a delta-method corollary of published mixing-field results. What remains is a short, correct statement about what two scales can and cannot identify, which is a remark rather than a paper.

## What was checked in print

About 13 queries were logged in f_SCALE_novelty_queries.csv (five web searches, five arXiv API calls of which three returned an error body and two returned nothing, three Crossref calls). Candidates are in f_SCALE_novelty_candidates.csv. Two-scale realized covariance (Zhang 2011, Mykland, Zhang and Chen 2019) is the same moment algebra for additive noise on a price path, with no predictor and no counts. Pospisil and Bair (2021) give the noise-corrected variance explained but need repeats or a known trial variance. A geostatistics report by Camana and Deutsch infers the nugget from the variance of composites at several supports given a variogram shape. Lahiri (2003), Nordman and Lahiri (2004) and Biscio and Waagepetersen supply the spatial CLT and subsampling variance estimation. I did not find a paper that states the ceiling identification for a predictor under count noise, but I read these papers only through excerpts and abstracts, so this is absence in a thin search and not a proof of absence. Semantic Scholar and forward citations were not used.

## Derivation in the simplest case

Take units $i$ with latent intensity $\Lambda_i$, counts $Y_i \mid \Lambda \sim \mathrm{Poisson}(\Lambda_i)$, a predictor $P_i$ built without looking at $Y$, and a stationary field with $E\Lambda_i=\mu$, $\mathrm{Var}\,\Lambda_i=\sigma^2$. The law of total variance gives

$$\mathrm{Var}(Y_i)=\mu+\sigma^2 ,$$

so the unit-level ceiling, the largest squared correlation any predictor can have with $Y_i$, is

$$R^2_{\max}=\frac{\sigma^2}{\mu+\sigma^2}=1-\frac{\mu}{\mathrm{Var}(Y_i)} .$$

This is one-scale. The plug-in $1-\bar Y/s_Y^2$ needs no pooling, and it holds when the mean varies across units, since the identity applies to the mixture over units. For the covariance side, independence of the counting noise and $P$ gives

$$\mathrm{Cov}(P_i,Y_i)=\mathrm{Cov}(P_i,\Lambda_i)=c_0 ,$$

so the sample covariance is unbiased for the unit-level predictive covariance. The noise-free skill is then $\rho(P,\Lambda)=c_0/\sqrt{\mathrm{Var}(P)\,\sigma^2}$, with the denominator from the display above. In the claim's notation, $c_0$ and the $m\mu$ term are both identified at $m=1$, and the second block size adds nothing in the Poisson case.

Now let the counts carry extra noise, $\mathrm{Var}(Y_i\mid\Lambda)=\mu+\tau^2$ in the claim's notation, independent across units. A block of $m$ units has

$$\mathrm{Var}\Big(\sum_{i\in B}Y_i\Big)=m(\mu+\tau^2+\sigma^2)+\sum_{i\ne j\in B}\mathrm{Cov}(\Lambda_i,\Lambda_j).$$

Subtracting $m$ times the unit variance leaves only the cross-unit latent covariance. Write $\mathrm{Cov}(\Lambda_i,\Lambda_j)=\sigma^2\rho(d_{ij})$ with a known shape $\rho$. For the hex pool of seven spots the estimator is

$$\hat\sigma^2=\frac{\widehat{\mathrm{Var}}(Y^{(7)})-7\,\widehat{\mathrm{Var}}(Y)}{\sum_{i\ne j\in B}\rho(d_{ij})},\qquad \hat R^2_{\max}=\hat\sigma^2/\widehat{\mathrm{Var}}(Y).$$

The numerator is a sum of neighbour covariances, so this two-scale estimator is the neighbour covariogram divided by an assumed $\rho$. Two consequences follow, and I derived them by algebra without a separate simulation. First, if $\rho$ is misspecified, $\hat\sigma^2$ is off by the factor $\rho_{\text{true}}/\rho_{\text{assumed}}$ in the pooled sum, so the relative bias of the ceiling is first order in the shape error. Second, without a shape, the split of the variance into $\sigma^2$ and $\tau^2$ is not identified. A pure nugget of size $\tau^2$ and a latent field with $\rho(d)=0$ for $d>0$ give the same moments at every block size. This is the nugget in geostatistics, and it is the reason the Poisson restriction carries the identification.

Two shape-free bounds follow from $0\le\rho\le 1$ and $\tau^2\ge 0$. The covariance of neighbouring units divided by $\mathrm{Var}(Y)$ is a lower bound on $\sigma^2/\mathrm{Var}(Y)$, and the Poisson plug-in is an upper bound on the ceiling of the latent part when extra noise is present. I call this the sandwich. The skill interval is the corresponding pair after dividing by the square roots of the two bounds.

For inference, the ceiling estimators are smooth functions of sample moments of a stationary mixing field. A delta method on the moment vector, with the long-run variance estimated by spatial subsampling, gives the CLT. I did not derive a block-size optimum for the pair of scales. The trade-off between the bias from a larger block and the loss of effective blocks has the form handled by Nordman and Lahiri, and I did not go beyond that observation.

## Simulation

The script is f_SCALE_sim.py with seed 20261026. The field is log-Gaussian on a 50 by 50 hex lattice with exponential log-covariance (range 1 or 2.5 spot spacings, log-variance 0.5), mean 0.5 or 3, and either Poisson noise or a gamma-Poisson with extra variance 0.5. The predictor has correlation 0.6 with $\Lambda$. Each cell uses 300 replicates, and Monte Carlo standard errors of the mean are at most 0.005 for the ceiling estimators.

With Poisson noise the one-scale plug-in has relative bias between $-2.1\%$ and $-0.3\%$. With extra noise it overstates the ceiling by 125 to 126 percent, and the skill computed from it is understated by about 33 percent. The two-scale estimator with the correct shape has relative bias between $-4.5\%$ and $+0.4\%$ in all eight cells, so the ten percent target holds. The correct shape here is that of $\Lambda$, not of $\log\Lambda$. My first run used the exponential shape for the lognormal field and gave biases of $-13\%$ to $-19\%$. A mislocated range gave $-28\%$ to $-17\%$ for a range 1.3 times too large and $+19\%$ to $+70\%$ for 0.7 times. The cost of the two-scale estimator is variance. Its standard deviation across replicates is 0.04 to 0.09 against 0.02 to 0.05 for the plug-in. The skill ratio is unstable when $\hat\sigma^2$ is near zero, and one replicate in 300 gave a value above 600 in one cell, so a ratio of this kind needs truncation or a ratio-aware interval.

For the variance formula I used a delete-one-tile jackknife over 25 tiles of ten lattice units. Its standard error is 0.74 to 0.94 of the empirical standard deviation of the two-scale estimator (median 0.83), so the spatial subsampling variance estimate is somewhat anticonservative at these tile sizes. This checks the form of the CLT, not an analytic first-order variance, which I did not derive.

## Data check

Predictions were written before the run and published as f_SCALE_predictions_before_run.md. The job used uni_v2 predictions on CCRCC (24 donors), INDIANA_KIDNEY (25) and LUNG_XENIUM (15), counts recovered as $\mathrm{expm1}$ of the stored log1p labels, a pool of the spot and its six nearest neighbours, and donor means over slides. Aggregates are in f_SCALE_task_summary.csv and f_SCALE_gene_summary.csv.gz. Predictions on the count scale are $\mathrm{expm1}$ of the stored log-scale predictions, which is a scale mismatch, so every skill and covariance value below is provisional.

| Prediction | Result | Score |
|---|---|---|
| 1. $L\le U$ in at least 95 percent of donor-gene cells | 98.2, 99.1, 99.4 percent | held |
| 2. median width $U-L\ge0.15$ in each task | 0.11 (CCRCC), 0.25, 0.50 | partly held |
| 3. thinning and plug-in ceilings agree within 0.02 | median gap 0.013, 0.025, 0.004 | partly held |
| 4. top 20 lung genes have SE below half the covariance in at least 15 | 20 of 20, median ratio 0.22 | held |
| 5. upper skill end at most 1 in 90 percent of cells | 99.7, 81.2, 41.2 percent | refuted for two of three tasks |

The Poisson plug-in ceiling has a task median of 0.34 on both Visium tasks and 0.89 on LUNG_XENIUM, against shape-free lower bounds of 0.21, 0.09 and 0.31. The thinning ceiling matches the plug-in by construction and carries the same overdispersion bias, so it is a check on code and not on the bias. The upper skill end exceeds 1 in most Xenium cells. That means either the neighbour covariance is too small a lower bound for pseudo-spots, where adjacent bins are weakly correlated, or the count-scale predictions do not estimate $\Lambda$ on the right scale. I did not separate the two.

## Stop rule and plan prediction

The stop rule says to stop if the CLT is a direct corollary of known results. It is, through the delta method and the spatial CLT and subsampling literature above. The estimator was computable on the data, so the second clause did not fire. Verdict: stop.

The plan's prediction for this track held in both parts. The estimator recovered the ceiling within ten percent in simulation once the shape was right, and the donor-level standard error was under half the estimate for all 20 best lung genes. Both parts are weak confirmations, since the second concerns a plain sample covariance, and the first holds only with the right shape.

## What a paper would need

A paper would need an identification theorem stating when the two-scale moment system separates the latent and noise variance, and the result above says the Poisson case needs no second scale and the extra-noise case needs a shape. It would need a data design with true multi-scale supports, such as single-cell transcripts aggregated to chosen windows, which the pseudo-spot binnings here cannot provide. It would need a ratio-aware interval for skill, a derived variance with an optimal pair of scales, and an over-identification test built from at least four scales. Even then, the closest published pieces are the nugget-from-compositing method and the noise-corrected variance explained, so the contribution would be a combination and not a new principle.

## Deviations

No analytic first-order variance or optimal block-size pair was derived. The over-identification test was not built. Only uni_v2 was used and LUNG_XENIUM binnings are pseudo-spots coarsened only. The sandwich bounds were checked on data but not in the simulation. Papers were read through excerpts only, forward citations were not checked, and three arXiv queries failed.
