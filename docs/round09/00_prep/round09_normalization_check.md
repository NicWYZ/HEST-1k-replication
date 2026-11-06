# Round 9 preparation, the normalization check

*26 October 2026. The claude-science session. It follows `round09_stud_and_depth.md`, which is not edited.*

That document noted that the estimands of earlier rounds are on log1p of unnormalized counts. This check recomputes the donor-level diagnostics on library-size-normalized expression (log1p of counts per 10,000), with the predictions as before. Script `code/scripts/round9_c2_normalized_summaries.py` (Longleaf job b4d4780e), predictions written before the run in `results/round9/norm/predictions_before_run.md` and scored in `results/round9/norm/predictions_scored.md`, numbers in `results/round9/norm/norm_summary.csv`.

Normalization removes about half of the shared donor factor on CCRCC (its share falls from 0.650 to 0.338) and little on the other tasks, and the donor means stay skewed (median skewness 1.416 on CCRCC). The predictions still explain nothing of between-donor variation for the median gene (leave-one-donor-out R^2 of -0.073 on CCRCC). Log library size is a weaker donor auxiliary than the cross-gene average (0.216 against 0.523 on CCRCC), so the shared factor is broader than total counts. The earlier rounds' null result for donor-level estimands on Visium is not an artifact of the unnormalized estimand. Of the four predictions, N2 held and N1, N3 and N4 were refuted.
