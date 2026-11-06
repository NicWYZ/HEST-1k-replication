# Track newtopic, step N3, predictions written before the run

*26 October 2026, written before `code/scripts/round9_newtopic_n3_diagnostics.py` was run. Scored afterwards in `n3_predictions_scored.md`.*

Inputs are the per-spot leave-donor-out prediction files of rounds 3 and 4 (`b1_predictions__<TASK>__<encoder>.parquet`) for CCRCC, IDC, LYMPH_IDC, PRAD, INDIANA_KIDNEY and LUNG_XENIUM and the encoders hoptimus0, resnet50 and uni_v2, with spot coordinates from each sample's h5ad. All statistics are computed within a sample (slide), then summarised by the median over genes and slides. The labels are log1p counts. "Panel depth" is the log of the sum over the panel genes of expm1 of the label.

- **D1, encoders agree with each other more than with the label.** The within-slide correlation between two encoders' predictions of the same gene, median over genes and slides, is at least 0.6 on every Visium task, while the within-slide correlation of a prediction with its label is below 0.3 there. On LUNG_XENIUM the two are closer (prediction-prediction minus prediction-label below 0.3).
- **D2, residuals are spatially autocorrelated, and predictions are smoother than labels.** Moran's I on a six-nearest-neighbour graph, median over genes and slides, is at least 0.15 for the residual label minus prediction on the Visium tasks, and Moran's I of the prediction exceeds Moran's I of the label for at least 0.7 of gene-slide pairs.
- **D3, a spot-level depth factor sits in the residuals.** Within each slide, the first principal component of the gene-by-gene correlation matrix of residuals carries at least 0.25 of their variance on the Visium tasks, and its score correlates with panel depth at absolute value at least 0.8.

Scoring is held, partly held, refuted or not tested, per task.
