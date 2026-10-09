#!/usr/bin/env python
"""Round 5 prediction-set track, W5: numbers quoted on the closing page and in the section on
round-4 statements changed, read from the W3 map. Writes results/round5/conformal/W5_map/w5_report_numbers.csv
(quantity, task, part, K, o, alpha, value). Run from the repository root."""
import numpy as np
import pandas as pd

M = pd.read_csv("results/round5/conformal/W3_real/merged/w3_map_by_task.csv")
A = 0.1
rows = []


def w(t, p, K, o, m, col="width_mean"):
    r = M[(M.task == t) & (M.part == p) & (M.alpha == A) & (M.K == K) & (M.o == o) & (M.method == m)]
    return float(r[col].iloc[0]) if len(r) else np.nan


def add(q, t, p, K, o, v):
    rows.append(dict(quantity=q, task=t, part=p, K=K, o=o, alpha=A, value=v))


T1 = sorted(M[M.part == 1].task.unique())
for t in T1:
    for o in (3, 5, 9, 10):
        add("ghcp/hcp width", t, 1, 10, o, w(t, 1, 10, o, "ghcp") / w(t, 1, 10, o, "hcp"))
    for o in (9, 10, 12, 15, 20, 25, 50, 100):
        add("within_full/hcp width", t, 1, 10, o, w(t, 1, 10, o, "within_full") / w(t, 1, 10, o, "hcp"))
    for o in (10, 25, 100):
        for m in ("within_plain", "within", "within_full", "ghcp"):
            add(f"{m} width", t, 1, 10, o, w(t, 1, 10, o, m))
            add(f"{m} coverage", t, 1, 10, o, w(t, 1, 10, o, m, "coverage"))
    g = M[(M.task == t) & (M.part == 1) & (M.alpha == A) & (M.method == "ghcp") & (M.o > 0)]
    add("ghcp coverage min over o", t, 1, 10, -1, float(g.coverage.min()))
    add("ghcp coverage max over o", t, 1, 10, -1, float(g.coverage.max()))
    add("hcp width", t, 1, 10, 0, w(t, 1, 10, 0, "hcp"))
for t in sorted(M[M.part == 2].task.unique()):
    for K in sorted(M[(M.part == 2) & (M.task == t)].K.unique()):
        add("ghcp/hcp width", t, 2, int(K), 5, w(t, 2, K, 5, "ghcp") / w(t, 2, K, 5, "hcp"))
        add("ghcp width", t, 2, int(K), 5, w(t, 2, K, 5, "ghcp"))
        add("hcp width", t, 2, int(K), 5, w(t, 2, K, 5, "hcp"))
for t in sorted(M[M.part == 3].task.unique()):
    for K in sorted(M[(M.part == 3) & (M.task == t)].K.unique()):
        for o in (5, 15, 25):
            for m in ("ghcp", "hcp", "within_full"):
                add(f"{m} width", t, 3, int(K), o, w(t, 3, K, o, m))
pd.DataFrame(rows).to_csv("results/round5/conformal/W5_map/w5_report_numbers.csv", index=False)
