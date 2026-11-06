# Round 9, track newtopic, the plan for interval 2

*26 October 2026, evening. Written by the newtopic session before any run of the interval. Living while interval 2 runs. Changes are appended at the end with their date, and the text above them is not rewritten.*

## 1. The decision that opens it

Interval 1's report (`docs/round09/i01/newtopic/round09_newtopic_i01_report.md`, section 5) offered C1 (a feasibility interval on RRRIDGE), C2 (the same for BOUNDARY) and C3 (close the track). On 26 October Nicolas answered "continue with a breadth first experimentation, exploring the various directions you see feasibility in". The session reads this as running feasibility tests on every direction with a plausible remainder at once, each small and each with a stop rule, rather than committing to one.

## 2. Tracks

Each track is run by its own subagent, independent of the others, and none commits to git. Each does four things in order. First, a focused novelty check on the sharpened claim, aimed at the suspects named below. Second, a derivation in the simplest case, with every expression that carries the argument displayed. Third, a simulation that checks the derivation. Fourth, where the data allow, a check on the project's data, with predictions written to a file before the run. Each ends by applying its stop rule.

| Track | Claim, sharpened by interval 1's checkers | Suspects to check first | Stop rule |
|---|---|---|---|
| F1 RRRIDGE | Proportional-regime limits of ridge reduced-rank regression (risk, subspace alignment, a threshold against PCA of the outcomes), with a group-level nuisance factor in the errors | spiked separable-covariance and eigenvector-overlap results (Ding and Yang; Bai and Yao; Romanov et al.; Benaych-Georges and Nadakuditi), and PRANK's ground (Bing, Ning and Xu; Wu and co-authors) | stop if the limits follow directly from published results, or if the rank-one isotropic case gives no threshold that differs from the one for PCA of the outcomes |
| F2 BOUNDARY | Size of a local-linear discontinuity test at a boundary selected on a thinned copy of counts driven by a continuous latent field, a bandwidth rule restoring size, and an optimal thinning fraction | regression-discontinuity smoothing bias (Cattaneo, Titiunik and Yu; Porter and Yu), data thinning (Neufeld, Dharamshi, Gao and Witten), wombling (Banerjee and Gelfand) | stop if simulation shows no size inflation beyond Monte Carlo error at realistic settings, or the inflation is the textbook smoothing bias with no selection effect |
| F3 SCALE | A two-scale estimator of fine-scale predictive covariance under count noise, with a CLT when the latent field is spatially correlated | two-scale realized covariance (Zhang 2011), variance components with unbalanced clusters, noise ceilings (Pospisil and Bair) | stop if the CLT is a direct corollary of known results, or the estimator cannot be computed on the project's data, where pseudo-spots can only be coarsened |
| F4 LLGCLUSTER | Chen, Kelly and Malamud's lower bound on population R^2 under group-level shifts, with unequal group sizes | the February 2026 version of the anchor, mixed-model R^2, Rabinowicz and Rosset | stop if the iid bound stays valid under group shifts in simulation, or the group version is the iid bound on demeaned data and group means with no new term |
| F5 Checkers | Fresh novelty checks of the four mined problems interval 1 left unchecked but its miners graded partly open. They are donor-aware CKA similarity between encoders, a ridge SNR frontier with random group SNR, neighbour effects under transcript spillover, and deconvolved composition as a generated regressor | as each checker finds | a candidate goes forward only if graded partly open or open with a remainder its checker says could carry a methods paper |

## 3. Predictions, written before any run

- **F1.** In the rank-one isotropic case the ridge reduced-rank estimator has a detection threshold in signal strength that depends on the aspect ratio and the penalty, and lies strictly below the threshold for PCA of the outcomes whenever the features carry the factor, so a threshold result exists. The focused novelty check finds the unregularised version in print and the ridge version not.
- **F2.** Under a continuous latent field, the naive local-linear discontinuity test on the held-out thinned counts at a boundary selected on the other part over-rejects at nominal 0.05 by at least 0.03 for bandwidths of a few spot spacings, and the over-rejection grows with the field's smoothness range.
- **F3.** On simulated data the two-scale estimator recovers fine-scale covariance within ten percent, and on the project's data its donor-level standard error is less than half the estimate for the most predictable lung genes.
- **F4.** The iid lower bound, applied to predictions fitted without demeaning, over-claims within-donor population R^2 in simulation when the donor-shift share of variance is at least 0.3, which is about the CCRCC level.
- **F5.** At most one of the four mined problems passes its checker as partly open with a remainder able to carry a methods paper.

## 4. Rules

Longleaf runs go through batch jobs, never the login node, and write under `/work/users/w/e/weiyang/hest_replication/results/round9/newtopic/` with small copies in the scratch root for download. Only aggregates enter the repository. Subagents do not use OpenAlex. Each track returns a short note in plain prose, its scripts and its aggregates as artifacts, and declares what it did not do. A fresh agent checks any track that passes its stop rule before the session builds on it.

## Amendments

**27 October, early.** All four feasibility tracks stopped on their own judgement. A fresh agent then read the papers F1's stop rested on and overturned it (the result needs a short genuine step and is not in print as far as it found). A fresh review of the draft report pointed out that the stops of F2, F3 and F4 were untested self-judgements, and F2's subagent had itself asked for a check. The session therefore adds step F7, three fresh auditors, one per stop, each reading the papers the stop rests on in full and returning stop confirmed, overturned or unclear, before the report is committed.
