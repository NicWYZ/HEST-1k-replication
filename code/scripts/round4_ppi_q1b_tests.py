#!/usr/bin/env python
"""Round 4, PPI track, interval 2: checks of rule (d) and the Q1b additions before Q1b runs
(plan section 13, step 'Implement rule (d) and Q1b additions in the estimator').

  T1  rules none, a_b1, b_cluster, c_crossfit give bit-identical output to the Q1 module
      (round4_ppi_estimator.py at a given commit, passed as --ref-module) on random data.
  T2  rule d equals rule c in every column where both halves pass the pre-test.
  T3  at G_L = 4 and 5 rules d1 and d2 are the classical estimator (theta, CR1 and CR2 intervals).
  T4  on an independent predictor (r = 0) the fraction of columns with lambda 0 under d2 is
      reported, and every such column equals the classical estimator.
  T5  the masked statistics with a full mask equal round4_ppi_q1_sim.donor_stats / build_stats.
  T6  the wild cluster bootstrap-t runs, is finite, and at G_L = 40 its interval width is within
      10% of the CR1 t interval's on average.
  T7  a reduced Q1b run (50 replicates, one m, one rho) completes for G_L = 4 and 8 with no
      non-finite intervals.
Writes q1b_tests.csv (test, detail, value, pass) to --out-dir and exits non-zero on any failure.
"""
import argparse
import importlib.util
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import round4_ppi_estimator as E  # noqa: E402
import round4_ppi_q1_sim as Q1  # noqa: E402
import round4_ppi_q1b_sim as B  # noqa: E402


def load_ref(path):
    spec = importlib.util.spec_from_file_location("ref_est", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sim_stats(G, m, R, rho, r, seed):
    rng = E.seed_rng(seed)
    mm, y, a0, eps0 = Q1.gen_block(rng, G, m, R, rho)
    yh = Q1.yhat_at(y, a0, eps0, r, rho)
    return Q1.build_stats(mm, y, yh, (0.0, 1.0)), (mm, y, yh)


def cmp_iv(a, b, cols=None):
    d = 0.0
    for k in a:
        if k not in b:
            continue
        for kk in ("lo", "hi"):
            x, y = a[k][kk], b[k][kk]
            if cols is not None:
                x, y = x[cols], y[cols]
            d = max(d, float(np.nanmax(np.abs(x - y))) if x.size else 0.0)
    return d


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ref-module", required=True)
    p.add_argument("--out-dir", required=True)
    a = p.parse_args()
    np.seterr(all="ignore")
    os.makedirs(a.out_dir, exist_ok=True)
    ref = load_ref(a.ref_module)
    rows = []

    def rec(test, detail, value, ok):
        rows.append(dict(test=test, detail=detail, value=value, passed=bool(ok)))
        print(test, detail, value, ok, flush=True)

    # T1
    for GL in (4, 8):
        G = GL + 20
        st, _ = sim_stats(G, 50, 200, 0.3, 0.5, f"t1|{GL}")
        Lm = np.zeros((G, 200), bool); Lm[:GL] = True; Um = ~Lm
        for (est, pop), D0 in st.items():
            D = Q1._n_for_iid(D0, 50) if pop == "donor" else D0
            for rule in ("none", "a_b1", "b_cluster", "c_crossfit"):
                _, r1, i1 = E.all_intervals(pop, D, Lm, Um, rule, 0.0, G_pop=G, seed="t1",
                                            do_boot=True, n_boot=50)
                _, r0, i0 = ref.all_intervals(pop, D, Lm, Um, rule, 0.0, G_pop=G, seed="t1",
                                              do_boot=True, n_boot=50)
                d = max(cmp_iv(i1, i0), float(np.nanmax(np.abs(r1["theta"] - r0["theta"]))))
                rec("T1", f"GL{GL}|{est}|{pop}|{rule}", d, d == 0.0)
    # T2 and T3 and T4
    for GL, r in ((4, 0.8), (5, 0.8), (8, 0.8), (12, 0.8), (8, 0.0), (12, 0.0)):
        G = GL + 20
        st, _ = sim_stats(G, 200, 300, 0.5, r, f"t2|{GL}|{r}")
        Lm = np.zeros((G, 300), bool); Lm[:GL] = True; Um = ~Lm
        for (est, pop), D0 in st.items():
            D = Q1._n_for_iid(D0, 200) if pop == "donor" else D0
            lc, rc, ic = E.all_intervals(pop, D, Lm, Um, "c_crossfit", 0.0, G_pop=G, seed="t2",
                                         do_boot=False)
            l0, r0, i0 = E.all_intervals(pop, D, Lm, Um, "none", 0.0, G_pop=G, seed="t2",
                                         do_boot=False)
            for rule in ("d1_pretest", "d2_pretest"):
                ld, rd, idd = E.all_intervals(pop, D, Lm, Um, rule, 0.0, G_pop=G, seed="t2",
                                              do_boot=False)
                cc = ld["classical_cols"]
                both = (ld["lamA"] == lc["lamA"]) & (ld["lamB"] == lc["lamB"]) & ~cc
                tag = f"GL{GL}|r{r}|{est}|{pop}|{rule}"
                if GL < 6:
                    d = max(cmp_iv(idd, i0), float(np.nanmax(np.abs(rd["theta"] - r0["theta"]))))
                    rec("T3", tag, d, (d == 0.0) and cc.all())
                    continue
                if both.any():
                    d = max(cmp_iv(idd, ic, both),
                            float(np.nanmax(np.abs(rd["theta"][both] - rc["theta"][both]))))
                    rec("T2", tag + f"|ncols{int(both.sum())}", d, d == 0.0)
                if cc.any():
                    d = max(cmp_iv(idd, i0, cc),
                            float(np.nanmax(np.abs(rd["theta"][cc] - r0["theta"][cc]))))
                    rec("T4" if r == 0.0 else "T2c", tag + f"|classical_cols{int(cc.sum())}",
                        d, d == 0.0)
                if r == 0.0:
                    rec("T4", tag + "|frac_lambda0", float(np.mean(ld["lam"] == 0.0)), True)
    # T5
    rng = E.seed_rng("t5")
    mm, y, a0, eps0 = Q1.gen_block(rng, 10, 30, 5, 0.3)
    yh = Q1.yhat_at(y, a0, eps0, 0.5, 0.3)
    M = np.ones((10, 30), bool)
    s1, s0 = B.build_stats(mm, y, yh, (0.0, 1.0), M), Q1.build_stats(mm, y, yh, (0.0, 1.0))
    d = max(float(np.max(np.abs(s1[k][kk] - s0[k][kk]))) for k in s0 for kk in E.STAT_KEYS)
    rec("T5", "full mask equals Q1 stats", d, d < 1e-10)
    # T6
    G = 60
    st, _ = sim_stats(G, 100, 100, 0.3, 0.5, "t6")
    Lm = np.zeros((G, 100), bool); Lm[:40] = True; Um = ~Lm
    for rule in ("none", "c_crossfit"):
        lam, res, iv = E.all_intervals("spot", st[("theta3", "spot")], Lm, Um, rule, 0.3,
                                       G_pop=G, seed="t6", do_boot=False)
        wb = B.wild_t(res, res["theta"], 200, "t6", E.ALPHA)
        w1 = float(np.mean(iv["CR1_t"]["hi"] - iv["CR1_t"]["lo"]))
        for kind, (lo, hi) in wb.items():
            ratio = float(np.mean(hi - lo)) / w1
            rec("T6", f"{rule}|{kind}|width_ratio_to_CR1",
                ratio, np.isfinite(lo).all() and np.isfinite(hi).all() and abs(ratio - 1) < 0.10)
    # T7
    for GL in (4, 8):
        out = os.path.join(a.out_dir, f"t7_GL{GL}")
        rc = B.main(["--G-L", str(GL), "--reps", "50", "--chunk", "50", "--m-grid", "200",
                     "--rho-grid", "0.1", "--out-dir", out])
        df = pd.read_csv(os.path.join(out, f"q1b_sim__GL{GL}.csv"))
        rec("T7", f"GL{GL}|rows{len(df)}|nonfinite", int(df.n_nonfinite.sum()),
            rc == 0 and int(df.n_nonfinite.sum()) == 0)
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(a.out_dir, "q1b_tests.csv"), index=False)
    print("failed", int((~df.passed).sum()), "of", len(df), flush=True)
    return 0 if df.passed.all() else 1


if __name__ == "__main__":
    sys.exit(main())
