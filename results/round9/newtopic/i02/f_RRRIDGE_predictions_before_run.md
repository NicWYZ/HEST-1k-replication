# F1 RRRIDGE, predictions for the data check, written before any data run (26 Oct 2026)

The data check was planned as: take the patch embeddings of one task (CCRCC, hoptimus0), standardise and whiten them within the training donors so that the isotropic theory is the nearest available approximation, take the 50 gene columns of the leave-donor-out labels, and ask whether the leading gene programme (top singular vector of the donor-centred response) sits above or below the ridge-RRR threshold and the PCA threshold computed from the observed (gamma, c) and a plug-in signal-to-noise ratio.

Predictions.

1. Whitened embeddings give an effective gamma = p/n above 1 in every task, so the ridge-RRR threshold is within 10 percent of the PCA threshold (ratio above 0.9 for gamma >= 2 in the isotropic grid).
2. The first gene programme is above both thresholds, and the second and later ones are below both.
3. The spectrum of the raw, unwhitened embeddings is far from Marchenko-Pastur (top eigenvalue shares above 20 percent), so the isotropic formulas are not expected to predict the observed alignment of any programme to better than a factor of two.

Status at the time of writing the note: the check was not run (see the note, deviations). All three predictions are scored not tested.
