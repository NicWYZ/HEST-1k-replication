# Why spatial-transcriptomics prediction needs site-aware uncertainty, not a global interval

*Draft motivation for Topic A. Generated 2026-09-14 13:35 from the replication's own result tables; every figure below traces to a saved CSV.*

## The claim

Histology-to-expression models are evaluated, and increasingly deployed, as if a single held-out
score characterised their reliability. It does not. In a faithful replication of the HEST-1k
benchmark — eleven encoders across ten tasks, reproducing the published leaderboard to a mean
absolute difference of 0.0002 over 99 encoder-task cells — the dominant determinant of measured
performance is not which foundation model supplies the features. It is which slides the test set
is allowed to contain.

The entire spread between the best and worst of eleven encoders is **0.090** Pearson
(0.325 for ResNet50 to 0.415 for H-optimus-0). Against that reference:

- Ignoring slide boundaries inflates the score by **0.158** — 1.75x the encoder spread.
- Of that, **0.124** is slide identity and **0.033** is spatial adjacency between
  neighbouring patches; the terms are additive by construction and positive in
  30/30 and 30/30
  encoder-task cells respectively.
- Holding out the *source institution* rather than the slide costs a further **0.042**, with
  both arms evaluated on a single slide so no aggregation artefact can contribute.

A model selected on a random spot-level split is therefore optimising a quantity that differs from
deployment performance by more than the entire architecture choice — and the gap is structured, not
noise: it decomposes into a local-texture term and a slide-signature term that behave differently.

## Why this is non-exchangeability, not just a harder split

Slides are almost perfectly identifiable from their embeddings. A logistic probe recovers slide
identity at **0.990** balanced accuracy under random spot splitting and **0.980** under
spatial block cross-validation, where whole contiguous grid blocks are held out so a test patch's
neighbours are also held out. The block design widened the median distance from a test spot to its
nearest training spot by 2.83x, verified before any accuracy was read,
so the near-ceiling separability is a genuine slide-level signature rather than nearest-neighbour
lookup on adjacent tissue.

That is the operational definition of non-exchangeability: the calibration and test distributions
are distinguishable by a learned function, so any procedure assuming exchangeable residuals — split
conformal with a single global quantile included — has no coverage guarantee across a slide boundary.

**One caveat stated plainly, because it bounds the mechanism claim.** Whether the embeddings encode
*institution* specifically is unresolved on this data. Probes for assay technology and cohort source
reach 0.994 and 0.938 (chance 0.50 and 0.20), but both are confounded: the
five imaging-based tasks are different organs from the five sequencing-based ones, tissue preservation
method is perfectly collinear with assay, and most cohort sources appear in exactly one task. The one
confound-free contrast — two sources of the same breast tissue on the same 541-gene panel within IDC —
gives 0.682 balanced accuracy, and with four folds only
2 of 11 encoders are distinguishable from chance at 95%. So the
*consequence* (performance degrades across sites) is measured and large; the *mechanism* (embeddings
carry site identity) is supported for slides and unresolved for institutions.

## What the observation model should be

Per-gene maximum-likelihood fits on the benchmark's own target panel (500 gene-task pairs)
settle the noise model without requiring a modelling assumption:

- Poisson is decisively rejected: negative binomial is preferred for **478/488** converged
  genes, median dAIC 57,812, and **all 500/500**
  genes are overdispersed relative to Poisson.
- Zero inflation buys nothing: ZINB is preferred for only **14/474** genes, with median
  dAIC **-2.002** against the **-2.000** predicted if the extra parameter contributes zero
  likelihood (455/474 genes within 0.5 of that value).

So a heteroscedastic negative-binomial head is the right conditional model, and the apparent excess
of zeros is an assay property rather than a separate biological process: median zero fraction is
0.29 for imaging-based tasks against
0.61 for sequencing-based ones, a split that follows
the technology and not the tissue.

## What is now available to condition on

The instrumentation layer joins 236,495 predicted spots — all of them, with
zero duplicate keys — to per-spot covariates: tissue position, sequencing depth, expression level,
slide and patient and cohort-source metadata, and CellViT morphology derived from
13,530,431 segmented nuclei (count, nuclear area, and the fraction of nuclei in each of five
classes, measured over exactly the patch the encoder embedded). Morphology coverage is
0.960 of predicted spots; the remainder carry
missing values rather than imputed zeros, so empty stroma cannot be read as unusually small nuclei.

This is what a site-aware calibration method needs in order to be *tested* rather than asserted:
a held-out slide is a genuine distribution shift of measured size, the conditional model is
identified, and the covariates that might carry the shift are on the same rows as the residuals.

## The gap this leaves open

Two quantities the replication could not identify, recorded so the calibration work does not
inherit them as assumptions:

1. **Across-task shift is not a scalar.** Holding training-set size fixed, the cost of training on
   other organs varies monotonically with how much in-domain data exists — **+0.145** on
   IDC with 26,652 in-domain spots, and slightly negative on the smallest task, where a size-matched
   mix of four other organs does marginally better. Task diversity substitutes for task specificity
   at small sample size, so any single across-domain number is a function of the reference task.
2. **The target genes were selected using the test folds.** The 50 genes per task were ranked by
   variance over every spot, test folds included. This is a property of the shipped benchmark data
   and no refit detects it; a leakage-free evaluation would recompute the ranking within each fold.

## Method note on the headline number

An earlier version of this analysis reported the leakage gap as +0.314.
That figure was inflated by **+0.177** because Pearson was computed on whatever spots the test
set contained: a pooled test set spanning many patients carries between-patient variance in the
correlation denominator, so the same model scores higher on a heterogeneous test set. All numbers
above use within-patient Pearson for every design, with the pooled value retained alongside so the
size of the artefact is measured rather than assumed — it is exactly zero for the single-slide arms
and +0.192 for the random split.
