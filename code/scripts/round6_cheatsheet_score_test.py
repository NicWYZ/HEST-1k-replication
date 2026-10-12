"""Round 6 cheatsheet track: the scorer tests of instruction C0.5.

1. True values score exactly 1.
2. Values permuted across spots score near 0, within +-0.05 on average over
   20 permutations.
3. A file with one constant gene scores that gene 0 and flags it.
4. A file missing a spot fails validation.

Run with a truth parquet (column `spot` plus one column per gene) to test on
real targets, or with no argument to test on synthetic correlated data.
Writes a one-row-per-test CSV to the path given by --out.
"""
import argparse
import io
import zlib

import numpy as np
import pandas as pd

from round6_cheatsheet_score import InvalidPredictions, score, validate


def as_csv(frame):
    buf = io.StringIO()
    frame.to_csv(buf, index=False)
    buf.seek(0)
    return pd.read_csv(buf)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--truth", default=None)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rng = np.random.default_rng(zlib.crc32(b"round6-scorer-test"))
    if a.truth:
        truth = pd.read_parquet(a.truth)
        truth["spot"] = truth["spot"].astype(str)
        truth = truth.set_index("spot")
        source = a.truth
    else:
        n, g = 500, 50
        z = rng.normal(size=(n, 5))
        y = np.log1p(np.exp(z @ rng.normal(size=(5, g)) + rng.normal(size=(n, g))))
        truth = pd.DataFrame(y, index=[f"x{i:04d}" for i in range(n)],
                             columns=[f"G{j:02d}" for j in range(g)])
        source = "synthetic"
    genes = list(truth.columns)
    spots = list(truth.index)
    pids = [f"p{i + 1:04d}" for i in range(len(spots))]
    to_spot = dict(zip(pids, spots))

    def run(frame):
        pred = validate(as_csv(frame), pids, genes)
        pred.index = [to_spot[p] for p in pred.index]
        return score(pred, truth.loc[pred.index, genes])

    def frame_of(values):
        f = pd.DataFrame(values, columns=genes)
        f.insert(0, "spot_id", pids)
        return f

    rows = []
    rbar, _ = run(frame_of(truth.to_numpy()))
    rows.append(("true_values", rbar, abs(rbar - 1) < 1e-12, "rbar == 1"))

    perm_scores = []
    for k in range(20):
        perm = rng.permutation(len(spots))
        r, _ = run(frame_of(truth.to_numpy()[perm]))
        perm_scores.append(r)
    m = float(np.mean(perm_scores))
    rows.append(("permuted_mean_of_20", m, abs(m) <= 0.05, "|mean rbar| <= 0.05"))

    v = truth.to_numpy().copy()
    v[:, 0] = 1.5
    r, pg = run(frame_of(v))
    ok = pg.loc[0, "r"] == 0.0 and bool(pg.loc[0, "constant_pred"]) and int(pg["constant_pred"].sum()) == 1
    rows.append(("one_constant_gene", float(pg.loc[0, "r"]), ok, "gene r == 0 and flagged"))

    f = frame_of(truth.to_numpy()).iloc[1:]
    try:
        run(f)
        rows.append(("missing_spot_fails", np.nan, False, "raises InvalidPredictions"))
    except InvalidPredictions as e:
        rows.append(("missing_spot_fails", np.nan, True, f"raised: {e}"))

    out = pd.DataFrame(rows, columns=["test", "value", "passed", "criterion"])
    out["truth_source"] = source
    out.to_csv(a.out, index=False)
    print(out.to_string(index=False))
    print("permutation scores:", np.round(perm_scores, 4).tolist())
    if not out["passed"].all():
        raise SystemExit(1)


if __name__ == "__main__":
    main()
