# Between-donor head test, predictions written before the run

Written 25 October 2026 by the claude-science session, before the donor-mean embeddings (job 486ce179) were read.

Setting. For each task (CCRCC, INDIANA_KIDNEY, LUNG_XENIUM), encoder (uni_v2, hoptimus0, resnet50) and gene, the donor-level target is the donor mean of log1p expression over joined spots. Three cluster-level predictors are compared by leave-one-donor-out (LODO) out-of-sample R^2 of the donor mean, R2c_oos = 1 - SS_res / SS_tot. (a) Pooled head: the donor mean of the existing leave-donor-out spot predictions, recalibrated by a LODO linear fit. (b) Between head: ridge of donor-mean label on the leading principal components of donor-mean embeddings (PCA fitted on all donors, label-free), penalty by inner LODO. (c) Shrink-to-within head: (a) plus a ridge correction on the same components, so the between block is shrunk toward the pooled (within) head.

Predictions.
- P1. The median over genes of R2c_oos for (a) is at most 0.10 on CCRCC and on INDIANA_KIDNEY for every encoder.
- P2. On CCRCC, (c) raises the median R2c_oos over (a) by at least 0.05 for at least one encoder, because part of the shared donor factor is visible in mean embeddings.
- P3. On LUNG_XENIUM, (c) changes the median R2c_oos by less than 0.05 for every encoder.
- P4. When the between block is fitted on 8 randomly chosen training donors instead of G - 1, the gain of (c) over (a) on CCRCC falls below 0.02.
