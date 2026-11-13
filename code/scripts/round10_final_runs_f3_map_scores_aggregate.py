"""Round 10, track final-runs, F3.1 item 7: summary of the adaptive-score units (plan section 5d.1 items 7 and 8).

Usage: round10_final_runs_f3_map_scores_aggregate.py <out_dir> <scores_full__*.csv.gz ...>

Reads the spec-level rows that round10_final_runs_f3_map.py's scores mode writes (one file per shard; the
i7_lung_part units write only CQR parts and no scores_full, so only i7_ccrcc, i7_indiana and i7_lung_merge
files are passed). Writes
  scores_by_task.csv      per (task, encoder, method, score, alpha, o, K): folds, coverage and widths, where the
                          median width is the median over target donors (folds) of the fold's width_median averaged
                          over draws, as P10.3 defines it; nb_model carries conformal_guarantee False;
  scores_margins.csv      for every score against abs in the same (task, method, o): the difference and ratio of
                          median widths with a bootstrap standard error (item 8: (cal_draw, label_draw) pairs
                          resampled within each fold, the same resample for both scores, B = 1000);
  scores_checks.json      fold means recomputed here against each shard's scores_by_fold file, duplicate rows,
                          folds per task.
Seeds come from zlib.crc32.
"""
import glob, json, os, sys, zlib
import numpy as np, pandas as pd

B = 1000
KEYS = ["task", "encoder", "method", "score", "alpha", "o", "K"]


def load(paths):
    parts = []
    for p in paths:
        x = pd.read_csv(p)
        if "score.1" in x.columns:  # the driver writes the score column twice
            assert (x["score"].astype(str) == x["score.1"].astype(str)).all(), p
            x = x.drop(columns="score.1")
        parts.append(x.assign(src=p))
    return pd.concat(parts, ignore_index=True)


def fold_level(d):
    return d.groupby(KEYS + ["fold"]).agg(coverage=("coverage", "mean"), width_mean=("width_mean", "mean"),
                                          width_median=("width_median", "mean"), finite=("finite", "mean"),
                                          n_genes=("n_genes", "first"), n_draws=("draw", "nunique")).reset_index()


def by_task(f):
    t = f.groupby(KEYS).agg(n_folds=("fold", "nunique"), n_genes=("n_genes", "max"), coverage_mean=("coverage", "mean"),
                            coverage_median=("coverage", "median"), coverage_min=("coverage", "min"),
                            width_median_median=("width_median", "median"), width_mean_mean=("width_mean", "mean"),
                            finite_mean=("finite", "mean")).reset_index()
    t["conformal_guarantee"] = t["method"] != "nb_model"
    return t


def margins(d):
    rows = []
    for (task, enc, method, alpha, o, K), g in d.groupby(["task", "encoder", "method", "alpha", "o", "K"]):
        if method == "nb_model":
            continue
        scores = sorted(g["score"].unique())
        if "abs" not in scores:
            continue
        piv = g.pivot_table(index=["fold", "cal_draw", "label_draw"], columns="score", values="width_median")
        for sc in scores:
            if sc == "abs":
                continue
            q = piv[["abs", sc]].dropna()
            folds = [q.xs(fd, level="fold").to_numpy() for fd in q.index.get_level_values("fold").unique()]
            a0 = np.median([x[:, 0].mean() for x in folds]); b0 = np.median([x[:, 1].mean() for x in folds])
            rng = np.random.default_rng(zlib.crc32(f"f3map|i7|{task}|{method}|{o}|{sc}".encode()))
            dif, rat = np.empty(B), np.empty(B)
            for b in range(B):
                ma, mb = [], []
                for x in folds:
                    i = rng.integers(0, len(x), len(x))
                    ma.append(x[i, 0].mean()); mb.append(x[i, 1].mean())
                A, Bm = np.median(ma), np.median(mb)
                dif[b], rat[b] = Bm - A, Bm / A
            rows.append(dict(task=task, encoder=enc, method=method, alpha=alpha, o=o, K=K, score=sc, vs="abs",
                             n_folds=len(folds), n_pairs_min=min(len(x) for x in folds),
                             width_median_abs=a0, width_median_score=b0, diff=b0 - a0, diff_se=dif.std(ddof=1),
                             ratio=b0 / a0, ratio_se=rat.std(ddof=1), B=B))
    return pd.DataFrame(rows)


def check_by_fold(d, f):
    out = []
    for p in sorted(d["src"].unique()):
        q = p.replace("scores_full__", "scores_by_fold__").replace(".csv.gz", ".csv")
        if not os.path.exists(q):
            out.append(dict(file=p, by_fold="missing")); continue
        r = pd.read_csv(q)
        mine = fold_level(d[d["src"] == p])
        m = r.merge(mine, on=KEYS + ["fold"], suffixes=("_drv", "_agg"))
        diff = max(float(np.abs(m[f"{c}_drv"] - m[f"{c}_agg"]).max()) for c in ("coverage", "width_mean", "width_median"))
        out.append(dict(file=p, rows_driver=len(r), rows_matched=len(m), max_abs_diff=diff))
    return out


def main(out_dir, paths):
    os.makedirs(out_dir, exist_ok=True)
    d = load(paths)
    key = ["task", "encoder", "method", "score", "alpha", "o", "K", "fold", "cal_draw", "label_draw"]
    dup = int(d.duplicated(key).sum())
    f = fold_level(d)
    t = by_task(f); t.to_csv(os.path.join(out_dir, "scores_by_task.csv"), index=False)
    m = margins(d); m.to_csv(os.path.join(out_dir, "scores_margins.csv"), index=False)
    cb = check_by_fold(d, f)
    ok = all(x.get("rows_driver") == x.get("rows_matched") and x.get("max_abs_diff", 1) <= 1e-12 for x in cb)
    chk = dict(n_files=len(paths), n_rows=len(d), duplicate_rows=dup,
               folds_per_task={k: int(v) for k, v in d.groupby("task")["fold"].nunique().items()},
               scores=sorted(d["score"].astype(str).unique()), methods=sorted(d["method"].unique()),
               by_fold_check_passed=bool(ok), by_fold_check_max_abs_diff=max(x.get("max_abs_diff", np.nan) for x in cb),
               by_fold_check=cb)
    json.dump(chk, open(os.path.join(out_dir, "scores_checks.json"), "w"), indent=1, default=float)
    print(t.to_string(), flush=True)
    print(json.dumps({k: v for k, v in chk.items() if k != "by_fold_check"}, default=float), flush=True)
    return 0 if (ok and dup == 0) else 5


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2:]))
