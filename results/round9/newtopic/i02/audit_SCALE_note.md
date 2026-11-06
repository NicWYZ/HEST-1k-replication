# Audit of the SCALE stop (fresh read)

Verdict: stop_confirmed, moderate confidence. The audit was shallower than the brief asked; see the last section.

## Is the Poisson one-scale point standard?
Yes, as folklore. Under conditionally Poisson counts, Var(Y) = E[Lambda] + Var(Lambda) is the law of total variance, and 1 - mean/Var(Y) is the Fano-factor identity restated as a variance fraction. Neuroscience uses the Fano factor to separate Poisson from super-Poisson variability, and noise ceilings for counts are normally built from repeats with Spearman-Brown correction, or from Pospisil and Bair's estimator that needs repeats or a known noise variance. I found no paper writing the one-scale ceiling for a predictor in this form, but it is a two-line identity and carries no theorem. Class (b): corollary of the law of total variance.

## Is identification with a shape covered?
Mostly. Block-sum variance minus m times unit variance leaves only cross-unit latent covariance. That is the change-of-support and nugget algebra of geostatistics (Camana-Deutsch compositing) and the moment algebra of two-scale realized covariance (Zhang 2011). Non-identification of nugget versus short-range latent variance without a shape is textbook: variation below the sampling interval is absorbed into the nugget. Class (a): in print for the algebra and the non-identification statement; the predictor-ceiling-under-counts instance is small.

One point where the stop note is too quick: a shape is not the only route. If the latent field is mean-square continuous, sigma^2 is the limit of the latent covariance at zero lag, so it is identified by extrapolation when supports shrink continuously (finely binned Xenium transcripts). On a fixed lattice it is only partially identified. That is a legitimate partial-identification problem, not a corollary of the cited work.

## Is the CLT a corollary?
Yes. The estimators are smooth functions of fixed-m local moments of a stationary alpha-mixing field. A CLT for such sums (Bolthausen 1982, Guyon 1995, Lahiri 2003) plus the delta method gives normality; Nordman and Lahiri 2004 or a tile jackknife gives the variance. Across donors the units are independent clusters, so a cluster CLT already suffices. Zhang-type CLTs with growing block size are not needed. Class (b).

## What would be a genuine new step
1. A sharp identified set for sigma^2 from block-sum variances at k scales when the latent correlation is only assumed non-negative, decreasing and positive definite in the plane (Schoenberg mixtures). The note's sandwich uses only Cauchy-Schwarz and tau^2 >= 0 and is wide (0.21 to 0.34 on CCRCC). Positive-definiteness and monotonicity give a finite-dimensional moment problem with provably sharp bounds. Real but modest: one theorem and one lemma. Not checked against the geostatistics literature.
2. Ratio-aware inference for the skill c0 / sqrt(Var(P) sigma^2) with a partially identified denominator (Imbens-Manski or Fieller type). Standard, small.
3. An over-identification test from four or more scales. Routine GMM.

## Strongest surviving claim
A partial-identification result: with count noise of unknown extra variance and a latent field known only to be non-negatively and monotonically correlated, the predictor ceiling and noise-free skill lie in explicit sharp sets computable from block-sum variances, with ratio-aware intervals and simulation. This is a methods contribution, not a deep theorem, and the data show the bounds can be uninformative (the note reports the upper skill end above 1 in about 59 percent of LUNG_XENIUM cells).

## Venue
Biostatistics or an applied-statistics or bioinformatics journal, or a workshop. Not NeurIPS, ICML or a top theory journal. The two-scale algebra is already finance (Zhang 2011), so it adds no finance skill transfer.

## Limits of this audit
I read no paper in full. The verdict rests on search excerpts, the note, my own algebra, and standard theorems cited from memory. I ran no data or simulation. Claim 1 above is unchecked against the literature and should go to a novelty checker before any investment.
