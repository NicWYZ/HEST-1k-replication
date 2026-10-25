# Cross-gene studentized prediction sets, predictions scored

Scored 26 October 2026 from `stud_summary.csv`, `stud_per_donor_coverage.csv`, `stud_per_donor_coverage_sd.csv` and `stud_factor_log_resid_sd.csv` (Longleaf job 741e07ed, 40 replicates per target donor and o, uni_v2, alpha 0.1).

- Q1 held. The lowest average coverage of methods A to D over tasks and o is 0.899 (the target's own set at o = 9, which is exact by construction).
- Q2 refuted. At o = 2 the mean finite half-width of D against A is 1.300 against 1.273 on CCRCC and 0.968 against 0.933 on INDIANA_KIDNEY, so D is not narrower.
- Q3 held. At o = 5 the per-gene studentized set is wider than HCP on every task (1.331 against 1.269 on CCRCC).
- Q4 held. At o = 3 on CCRCC the standard deviation over target donors of per-donor coverage is 0.0213 for D against 0.1333 for A.
- Q5 refuted. The first principal component of log within-donor residual SD explains 0.468 on CCRCC, below 0.50.

Reading. Width: the oracle that knows each target donor's true per-gene scale is only 0.130 narrower than HCP on CCRCC, 0.064 on INDIANA_KIDNEY and 0.067 on LUNG_XENIUM at o = 3, so scale adaptation cannot buy much width. Donor-level coverage: HCP's lowest per-donor coverage is 0.310 on CCRCC (one donor of 24), 0.839 on INDIANA_KIDNEY and 0.847 on LUNG_XENIUM, against 0.878, 0.877 and 0.916 for the cross-gene studentized set at o = 3. The value of studentizing is robustness of coverage for atypical donors at no width cost, not width. Whether that is new is for the STUD novelty check.
