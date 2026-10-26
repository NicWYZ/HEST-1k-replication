# Library-size normalization check, predictions scored

Scored 26 October 2026 from `norm_summary.csv` and `c2_checks.csv` (Longleaf job b4d4780e; raw counts recovered exactly, `frac_integer_counts` 1.0 on every task; every spot matched to its library size).

- N1 refuted. The donor mean of log total counts correlates with the shared first factor at 0.802 on CCRCC (below 0.9), 0.929 on INDIANA_KIDNEY and 0.942 on LUNG_XENIUM.
- N2 held. On CCRCC the first factor's share falls from 0.650 to 0.338 after normalization.
- N3 refuted. On CCRCC the median skewness of donor means falls from 2.053 to 1.416, not below 1.0.
- N4 refuted. After normalization the median leave-one-donor-out R^2 of the prediction is -0.073 on CCRCC and -0.035 on LUNG_XENIUM, still below 0.

Reading. Library-size normalization removes about half of the shared factor on CCRCC and little elsewhere, and leaves the donor means skewed. Log library size alone explains a median 0.216 of raw between-donor variance on CCRCC out of sample, less than the cross-gene average (0.523, `results/round9/stud/probe_depth_auxiliary_medians.csv`), so the shared factor is broader than total counts (detection efficiency or RNA quality are candidates). The predictions carry no between-donor information for the median gene with or without normalization, so the null result of the earlier rounds is not an artifact of the unnormalized estimand.
