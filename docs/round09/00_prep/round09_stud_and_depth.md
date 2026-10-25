# Round 9 preparation, studentized prediction sets and the donor depth factor

*26 October 2026. The claude-science session, on Nicolas's Mac and Longleaf. Steps S3 and S4 of CLAUDE.md section 3. Recommendations are `[proposed]`.*

## 1. What was tried

Nicolas left the choice of direction to the session (CLAUDE.md section 4). The session took option C of the direction scan, prediction sets for a new donor, with one idea. Each donor's residual scores are divided by a scale estimated from its own o labelled spots, and the studentized scores are calibrated across reference donors with one held-out spot per donor. A variant pools the donor's scale over all genes of its o spots, since a labelled spot measures every gene at once. Predictions were written before the run (`results/round9/stud/predictions_before_run.md`) and scored after it (`results/round9/stud/predictions_scored.md`). The script is `code/scripts/round9_stud_feasibility.py` (Longleaf job 741e07ed, uni_v2, alpha 0.1, every donor in turn the target, 40 replicates per target and o).

## 2. Novelty

An independent checker (`results/round9/scan/scan_STUD_queries.csv`, `results/round9/scan/scan_STUD_candidates.csv`, entry STUD of `results/round9/scan/scan_structured_results.json`) graded the idea mostly taken. Its validity is a remark in GHCP's appendix B.1 (arXiv:2608.15500), which allows a studentized score with a scale built by the same rule from each group's own block. Duchi, Gupta, Jiang and Sur (arXiv:2403.16336, section 5) already resize sets by a group scale estimated from the same number of labelled points in every environment, under a different guarantee. Round 4 of this project had tested the per-gene version inside GHCP as candidate K5 (`docs/round04/i01/conformal/round4_conf_C2_report.md`, section 5), which kept coverage and widened the set. What the checker found open (an empirical-Bayes pooled scale, a width law and crossover, and the cross-gene factor) it judged a secondary component at most.

## 3. What the run showed

All methods kept average coverage (Q1 held). Width gains are small because there is little to gain. At o = 3, an oracle that knows each target donor's true per-gene scale is only 0.130 narrower than HCP on CCRCC, 0.064 on INDIANA_KIDNEY and 0.067 on LUNG_XENIUM (`results/round9/stud/stud_summary.csv`). The cross-gene set was not narrower than HCP at o = 2 (Q2 refuted), and the per-gene set was wider at o = 5 (Q3 held).

The run showed something else. HCP's coverage for one target donor of CCRCC, INT5, is 0.310 at o = 3, while every other donor is near or above nominal, and the cross-gene studentized set raises it to 0.878 at about the same average width (`results/round9/stud/stud_per_donor_coverage.csv`; Q4 held). INT5 is the donor with the largest average expression of the 24 (z = 3.98) and the largest residual scale, and it is not atypical in label-free terms. Its prediction outlyingness ranks 15th and its embedding outlyingness 22nd (`results/round9/stud/atypical_donor_diagnostics.csv`, computed in the session from the same C0 and C1 aggregates). The donor that breaks hierarchical conformal coverage is a technical outlier that histology cannot see and that any labelled spot reveals.

## 4. The depth factor as an auxiliary

The same factor explains the failures of few-cluster PPI. With a depth proxy for each donor (its average over the other genes, from the donor's full data, so an upper bound for what a few probe spots would give), the leave-one-donor-out R^2 of the donor mean, median over genes, is 0.523 on CCRCC against -0.066 for the predictions, and the skewness of donor means falls from 2.053 to 0.906 once depth and predictions are both regressed out. On LUNG_XENIUM neither works alone (-0.025 for predictions, 0.051 for depth) but together they reach 0.351. The histology signal there is masked by the technical factor (`results/round9/stud/probe_depth_auxiliary_medians.csv`, script `code/scripts/round9_depth_probe_diagnostics.py`).

## 5. What follows `[proposed]`

Two things. First, the empirical account of the project's failures is now specific. Between-donor variation on Visium is dominated by a depth factor invisible to histology, a single depth-outlier donor drives the skew of donor means on CCRCC and the collapse of HCP coverage for that donor, and histology predictions carry between-donor information only once the factor is controlled. Second, this suggests a probe-then-label design (a few labelled spots in every donor to measure the factor, then whole donors), which is two-phase sampling with an estimated auxiliary and is now with a novelty checker (PROBE). The estimands of earlier rounds are on log1p of unnormalized counts, so part of what they measure is depth. Whether they should be redefined on depth-normalized expression is a question for the paper.
