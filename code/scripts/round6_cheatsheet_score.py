"""Round 6 cheatsheet track: validate and score a trial's predictions.csv.

The scorer reads a predictor's or combined session's `predictions.csv`, maps
the trial's patch IDs back to spots with the mapping kept outside the trial
directory, and computes the masterplan's metric

    rbar = (1/50) * sum_g corr(yhat_g, y_g)

over the scored spots. A gene whose predictions are constant is counted as 0
and flagged. A file that misses a spot or a gene, has an extra or duplicated
row, or holds a non-numeric or non-finite value fails validation, and nothing
is filled in (instruction section 6.4).

Usage as a library: `validate(df, pids, genes)` and `score(pred, truth)`.
Usage from the command line:

    python round6_cheatsheet_score.py PRED_CSV MAPPING_CSV TRUTH_PARQUET GENES_TXT

where MAPPING_CSV has columns `pid,spot` and TRUTH_PARQUET has a `spot`
column plus one column per gene.
"""
import json
import sys

import numpy as np
import pandas as pd


class InvalidPredictions(ValueError):
    pass


def validate(df, pids, genes):
    """Check a predictions frame and return it indexed by pid, columns = genes.

    Raises InvalidPredictions with the reason on any defect.
    """
    if df.columns.size == 0 or df.columns[0] != "spot_id":
        raise InvalidPredictions("first column is not spot_id")
    cols = list(df.columns[1:])
    missing_genes = [g for g in genes if g not in cols]
    if missing_genes:
        raise InvalidPredictions(f"missing genes: {missing_genes[:5]} ({len(missing_genes)})")
    extra = [c for c in cols if c not in genes]
    if extra:
        raise InvalidPredictions(f"unexpected columns: {extra[:5]} ({len(extra)})")
    if len(set(cols)) != len(cols):
        raise InvalidPredictions("duplicated gene columns")
    ids = df["spot_id"].astype(str).str.strip()
    if ids.duplicated().any():
        raise InvalidPredictions(f"duplicated spot ids: {int(ids.duplicated().sum())}")
    want = set(pids)
    got = set(ids)
    if want - got:
        raise InvalidPredictions(f"missing spots: {len(want - got)}")
    if got - want:
        raise InvalidPredictions(f"unknown spots: {len(got - want)}")
    vals = df[genes].apply(pd.to_numeric, errors="coerce")
    bad = vals.isna() | ~np.isfinite(vals.to_numpy(dtype=float))
    if bad.to_numpy().any():
        raise InvalidPredictions(f"non-numeric or non-finite values: {int(bad.to_numpy().sum())}")
    vals.index = ids.to_numpy()
    return vals.loc[list(pids), genes].astype(float)


def score(pred, truth):
    """pred, truth: frames with the same index (spots) and the same gene columns.

    Returns (rbar, per_gene) where per_gene is a frame with columns
    gene, r, constant_pred, constant_truth.
    """
    assert list(pred.index) == list(truth.index)
    assert list(pred.columns) == list(truth.columns)
    rows = []
    for g in truth.columns:
        p = pred[g].to_numpy(dtype=float)
        y = truth[g].to_numpy(dtype=float)
        cp = bool(np.ptp(p) == 0)
        cy = bool(np.ptp(y) == 0)
        if cp or cy:
            r = 0.0
        else:
            r = float(np.corrcoef(p, y)[0, 1])
        rows.append((g, r, cp, cy))
    per_gene = pd.DataFrame(rows, columns=["gene", "r", "constant_pred", "constant_truth"])
    return float(per_gene["r"].mean()), per_gene


def score_file(pred_csv, mapping_csv, truth_parquet, genes_txt):
    genes = [l.strip() for l in open(genes_txt) if l.strip()]
    mapping = pd.read_csv(mapping_csv, dtype=str)
    truth = pd.read_parquet(truth_parquet)
    truth["spot"] = truth["spot"].astype(str)
    truth = truth.set_index("spot")
    df = pd.read_csv(pred_csv)
    pred = validate(df, list(mapping["pid"]), genes)
    pred.index = mapping.set_index("pid").loc[pred.index, "spot"].to_numpy()
    return score(pred, truth.loc[pred.index, genes])


if __name__ == "__main__":
    try:
        rbar, per_gene = score_file(*sys.argv[1:5])
    except InvalidPredictions as e:
        print(json.dumps({"valid": False, "reason": str(e)}))
        sys.exit(2)
    print(json.dumps({"valid": True, "rbar": rbar,
                      "n_constant_pred": int(per_gene["constant_pred"].sum())}))
