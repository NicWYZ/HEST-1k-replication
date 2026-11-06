# Library-size normalization check, predictions written before the run

Written 26 October 2026 by the claude-science session, before the output of Longleaf job b4d4780e was read. Script `code/scripts/round9_c2_normalized_summaries.py`; analysis in this folder.

- N1. The donor mean of log total counts correlates above 0.9 in absolute value with the shared first factor of donor-mean log1p expression on CCRCC.
- N2. After normalization (log1p of counts per 10,000), the share of between-donor variance carried by the first factor on CCRCC falls below 0.35 (from 0.650 before).
- N3. After normalization, the median skewness of donor means on CCRCC falls below 1.0 (from 2.05 before).
- N4. After normalization, the median over genes of the leave-one-donor-out R^2 of the donor mean on the (unnormalized-trained) prediction's donor mean rises above 0 on CCRCC and on LUNG_XENIUM.
