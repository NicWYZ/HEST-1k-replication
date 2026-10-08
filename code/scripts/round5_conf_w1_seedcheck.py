#!/usr/bin/env python
"""Round 5, W1: is the over-coverage in t3|K16|N100|share0.9|tau0.0 Monte Carlo fluctuation?

In the merged W1 grid every within-cluster method over-covers in this one cell, by up to 5.3
MC standard errors (results/round5/conformal/W1_sim/w1_coverage_z.csv). The three methods are
exact by within-cluster exchangeability whatever the tails. The hypothesis is that the cell's
5,000 shared replicates are an unusual draw. Two runs test it.
  (a) The same cell with seed tag "C1", which must reproduce the W1 rows exactly (determinism).
  (b) The same cell with an independent seed tag, "W1seedcheck", which under the hypothesis gives
      |z| below about 3. If the excess reappears, the hypothesis is refuted and the cause is a
      defect, to be found before W1 is reported.
Diagnostic only; nothing here enters the W1 tables.
"""
import math
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import round4_conf_sim as SIM  # noqa: E402
import round5_conf_io as IO5  # noqa: E402
import round5_conf_w1_sim as W1  # noqa: E402

CELL = "t3|K16|N100|share0.9|tau0.0"


def main(out, reps=5000):
    os.makedirs(out, exist_ok=True)
    IO5.stamp(out, track="conformal-W1", note="W1 seed check of one outlier cell")
    cell = [c for c in W1.build_cells(16, semireal=False) if c["cell_id"] == CELL][0]
    rows = []
    for tag in ("C1", "W1seedcheck"):
        W1._WF_LOG.clear()
        rr = SIM.run_cell(cell, list(W1.ALPHAS), reps, W1.O_GRID, None,
                          methods=["within", "within_plain", "within_full"], seed_tag=tag)
        wf = pd.DataFrame(W1._WF_LOG, columns=["o", "alpha", "exact_coverage", "is_interval"])
        for (a, m, o), d in rr.groupby(["alpha", "method", "o"]):
            if not np.isfinite(d.q).all():
                continue
            n = o - o // 2 if m == "within" else o
            exp = math.ceil((n + 1) * (1 - a) - 1e-9) / (n + 1)
            cov = d.coverage.values
            if m == "within_full":
                cov = wf[(wf.alpha == a) & (wf.o == o)].exact_coverage.values
            se = cov.std(ddof=1) / math.sqrt(len(cov))
            rows.append(dict(seed_tag=tag, alpha=a, method=m, o=o, coverage=float(cov.mean()),
                             coverage_hull=float(d.coverage.mean()), mcse=se, expected=exp,
                             z=(cov.mean() - exp) / se))
    R = pd.DataFrame(rows)
    R.to_csv(os.path.join(out, "w1_seedcheck.csv"), index=False)
    IO5.write_provenance(out, "W1_seedcheck", __file__, dict(stage="W1 seed check", cell=CELL, reps=reps,
                         tags=["C1", "W1seedcheck"]))
    print(R.groupby("seed_tag").z.agg(lambda x: x.abs().max()))


if __name__ == "__main__":
    main(sys.argv[1])
