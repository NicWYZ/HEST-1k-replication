"""Round 6 extension, cheatsheet track: validate and score predictions.

The metric of instruction section 6.7. For test slide s and gene g, over that
slide's 500 scored spots,

    rbar = (1/3) * sum_s (1/|G_s|) * sum_{g in G_s} corr(yhat_sg, y_sg)

where G_s is the set of genes whose measured values are not constant over the
slide's scored spots. A gene whose predictions are constant on a slide counts
as 0 there and is flagged. A gene whose measured values are constant on a
slide is left out of that slide's mean and flagged, for every predictor and
comparator alike, since G_s depends on the measurements only. The pooled value
over all scored spots, the mean over the 50 genes of the correlation across
slides, is returned beside it and is never the headline.

Validation is round 6's (round6_cheatsheet_score.validate), unchanged. A file
that misses a spot or a gene, has an extra or duplicated row, or holds a
non-numeric or non-finite value fails, and nothing is filled in.

Library use: `validate(df, ids, genes)` and `score(pred, truth, slide)`.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from round6_cheatsheet_score import InvalidPredictions, validate  # noqa: E402,F401


def _corr(p, y):
    cp, cy = bool(np.ptp(p) == 0), bool(np.ptp(y) == 0)
    if cy:
        return np.nan, cp, cy
    if cp:
        return 0.0, cp, cy
    return float(np.corrcoef(p, y)[0, 1]), cp, cy


def score(pred, truth, slide):
    """pred, truth: frames with the same index (spots) and gene columns.
    slide: the slide of each spot, in the same order.

    Returns a dict with rbar, per_slide (slide -> within-slide mean), pooled,
    and cells, a frame with one row per slide and gene (r, constant_pred,
    constant_truth) followed by one row per gene with slide == "pooled".
    """
    assert list(pred.index) == list(truth.index)
    assert list(pred.columns) == list(truth.columns)
    slide = np.asarray(slide)
    assert len(slide) == len(pred)
    rows = []
    for s in sorted(set(slide.tolist())):
        m = slide == s
        for g in truth.columns:
            r, cp, cy = _corr(pred[g].to_numpy(dtype=float)[m], truth[g].to_numpy(dtype=float)[m])
            rows.append((s, g, r, cp, cy, int(m.sum())))
    for g in truth.columns:
        r, cp, cy = _corr(pred[g].to_numpy(dtype=float), truth[g].to_numpy(dtype=float))
        rows.append(("pooled", g, r, cp, cy, len(pred)))
    cells = pd.DataFrame(rows, columns=["slide", "gene", "r", "constant_pred", "constant_truth", "n_spots"])
    within = cells[cells["slide"] != "pooled"]
    per_slide = within.groupby("slide")["r"].mean()  # NaN cells, constant truth, are skipped
    pooled = cells.loc[cells["slide"] == "pooled", "r"].mean()
    return {"rbar": float(per_slide.mean()), "per_slide": {k: float(v) for k, v in per_slide.items()},
            "pooled": float(pooled) if np.isfinite(pooled) else float("nan"),
            "n_constant_pred_cells": int(within["constant_pred"].sum()),
            "n_constant_truth_cells": int(within["constant_truth"].sum()),
            "cells": cells}
