#!/usr/bin/env python
"""Round 5, prediction-set track, W3 report numbers, prediction scores and figures.

Reads MERGED/w3_map_by_task.csv (round5_conf_w3_merge.py) and writes into OUT:

  w3_report_numbers.csv   one row per number quoted in the W3 section of the report
  w3_prediction_scores.csv  one row per prediction clause and task, then one per prediction
  fig_w3_map.png          part 1 (K = 10): width relative to HCP against o, per task
  fig_w3_fixed_head.png   part 3: width against K at o = 5, 15, 25, per task

SCORING RULES, written before the production merge was read (alpha = 0.1 throughout; widths
are the map's width_mean; "valid" is the map's valid column; a method infinite in any row has
width inf and is never narrowest):

W3.1 (part 1, K = 10, every task)
  a  ghcp / hcp width is in [1.2, 1.5] at o = 3 and at o = 5
  b  original: within_full is narrowest_valid at every o >= 9 of the grid
     amended (W2 memo section 5 item 3): the same, except o = 17
  c  within_full / hcp width is in [0.45, 0.65] at o = 9, 10, 12, 15
  The original wording is a and b-original and c; the amended wording a and b-amended and c.
W3.2 (part 1, K = 10, every task)
  a  1 - within_full / within_plain is in [0.05, 0.15] at every o >= 9
  b  1 - within_full / within is in [0.05, 0.12] at every o >= 20
W3.3 (part 2, both kidney cancer label sets CCRCC and CCRCC_23merged)
  a  |ghcp / hcp - 1| <= 0.08 at o = 5 for every K in 12..20
  b  at o < 9 (part 1 o = 3, 5 at K = 10; part 2 o = 5 at every K) ghcp is never narrower than
     every other valid finite method by more than 5% (ghcp < 0.95 x the narrowest other)
W3.4 (part 3, each task present)
  a  within, within_plain and within_full: (max - min) / min of width over K is <= 1e-8 at every o
  b  ghcp width is non-increasing in K at every o > 0 (relative tolerance 1e-8)
  c  at o = 10, 15, 17, 25 and every K, ghcp is not narrower than every other valid finite
     method by more than 5%
W3.5  INDIANA_KIDNEY's truth value of each clause of W3.3 a, b (part 2) and W3.4 a, b, c
  (part 3) equals CCRCC's (CCRCC:24, out_task CCRCC).
A prediction is held when every clause holds on every task it names, refuted when no clause
holds on any task, and partly held otherwise. W3.5 is held when every clause agrees, refuted
when none does.
"""
import argparse
import os

import numpy as np
import pandas as pd

A = 0.1
KIDNEY = ["CCRCC", "CCRCC_23merged"]
WITHINS = ["within", "within_plain", "within_full"]


def w(M, task, part, K, o, method):
    r = M[(M.task == task) & (M.part == part) & (M.alpha == A) & (M.K == K) & (M.o == o) &
          (M.method == method)]
    return float(r.width_mean.iloc[0]) if len(r) else np.nan


def margin(M, task, part, K, o, m="ghcp"):
    """ghcp width / narrowest other valid finite method (one_per excluded, as the map)."""
    g = M[(M.task == task) & (M.part == part) & (M.alpha == A) & (M.K == K) & (M.o == o) &
          M.valid & (M.method != "one_per") & np.isfinite(M.width_mean)]
    if m not in set(g.method) or len(g) < 2:
        return np.nan
    return float(g[g.method == m].width_mean.iloc[0] / g[g.method != m].width_mean.min())


def score(M):
    N, S = [], []

    def num(pred, clause, task, part, K, o, quantity, value, lo=np.nan, hi=np.nan, ok=None):
        N.append(dict(prediction=pred, clause=clause, task=task, part=part, K=K, o=o,
                      quantity=quantity, value=value, lo=lo, hi=hi, holds=ok))
        return ok

    tasks1 = sorted(M[M.part == 1].task.unique())
    o1 = sorted(M[(M.part == 1)].o.unique())
    for t in tasks1:
        a = [num("W3.1", "a", t, 1, 10, o, "ghcp/hcp", r, 1.2, 1.5, bool(1.2 <= r <= 1.5))
             for o in (3, 5) for r in [w(M, t, 1, 10, o, "ghcp") / w(M, t, 1, 10, o, "hcp")]]
        b = []
        for o in [x for x in o1 if x >= 9]:
            nv = M[(M.task == t) & (M.part == 1) & (M.alpha == A) & (M.K == 10) & (M.o == o) & M.narrowest_valid]
            name = nv.method.iloc[0] if len(nv) else "none"
            N.append(dict(prediction="W3.1", clause="b", task=t, part=1, K=10, o=o,
                          quantity=f"narrowest_valid={name}",
                          value=w(M, t, 1, 10, o, name) / w(M, t, 1, 10, o, "hcp") if len(nv) else np.nan,
                          lo=np.nan, hi=np.nan, holds=name == "within_full"))
            b.append((o, name == "within_full"))
        c = [num("W3.1", "c", t, 1, 10, o, "within_full/hcp", r, 0.45, 0.65, bool(0.45 <= r <= 0.65))
             for o in (9, 10, 12, 15) for r in [w(M, t, 1, 10, o, "within_full") / w(M, t, 1, 10, o, "hcp")]]
        S += [dict(prediction="W3.1", clause="a", task=t, holds=all(a)),
              dict(prediction="W3.1", clause="b_original", task=t, holds=all(x for _, x in b)),
              dict(prediction="W3.1", clause="b_amended", task=t, holds=all(x for o, x in b if o != 17)),
              dict(prediction="W3.1", clause="c", task=t, holds=all(c))]
        a2 = [num("W3.2", "a", t, 1, 10, o, "1-within_full/within_plain", r, 0.05, 0.15, bool(0.05 <= r <= 0.15))
              for o in o1 if o >= 9 for r in [1 - w(M, t, 1, 10, o, "within_full") / w(M, t, 1, 10, o, "within_plain")]]
        b2 = [num("W3.2", "b", t, 1, 10, o, "1-within_full/within", r, 0.05, 0.12, bool(0.05 <= r <= 0.12))
              for o in o1 if o >= 20 for r in [1 - w(M, t, 1, 10, o, "within_full") / w(M, t, 1, 10, o, "within")]]
        S += [dict(prediction="W3.2", clause="a", task=t, holds=all(a2)),
              dict(prediction="W3.2", clause="b", task=t, holds=all(b2))]

    def w33(t):
        Ks = sorted(k for k in M[(M.part == 2) & (M.task == t)].K.unique() if 12 <= k <= 20)
        a = [num("W3.3", "a", t, 2, K, 5, "ghcp/hcp-1", r - 1, -0.08, 0.08, bool(abs(r - 1) <= 0.08))
             for K in Ks for r in [w(M, t, 2, K, 5, "ghcp") / w(M, t, 2, K, 5, "hcp")]]
        cells = [(1, 10, o) for o in (3, 5)] + [(2, K, 5) for K in sorted(M[(M.part == 2) & (M.task == t)].K.unique())]
        b = [num("W3.3", "b", t, p, K, o, "ghcp/narrowest_other", r, 0.95, np.nan, not (r < 0.95))
             for p, K, o in cells for r in [margin(M, t, p, K, o)] if not np.isnan(r)]
        return dict(a=all(a) if a else None, b=all(b) if b else None)

    def w34(t):
        P = M[(M.part == 3) & (M.task == t) & (M.alpha == A)]
        if not len(P):
            return dict(a=None, b=None, c=None)
        Ks = sorted(P.K.unique())
        a = []
        for m in WITHINS:
            for o in sorted(P.o.unique()):
                if o == 0:
                    continue
                v = np.array([w(M, t, 3, K, o, m) for K in Ks])
                if np.all(np.isfinite(v)):
                    r = (v.max() - v.min()) / v.min()
                    a.append(num("W3.4", "a", t, 3, -1, o, f"{m} rel range over K", r, np.nan, 1e-8, bool(r <= 1e-8)))
        b = []
        for o in sorted(P.o.unique()):
            if o == 0:
                continue
            v = np.array([w(M, t, 3, K, o, "ghcp") for K in Ks])
            inc = np.diff(v) / v[:-1]
            b.append(num("W3.4", "b", t, 3, -1, o, "ghcp max relative increase between successive K",
                         float(np.nanmax(inc)), np.nan, 1e-8, bool(np.nanmax(inc) <= 1e-8)))
        c = [num("W3.4", "c", t, 3, K, o, "ghcp/narrowest_other", r, 0.95, np.nan, not (r < 0.95))
             for K in Ks for o in (10, 15, 17, 25) for r in [margin(M, t, 3, K, o)] if not np.isnan(r)]
        return dict(a=all(a) if a else None, b=all(b) if b else None, c=all(c) if c else None)

    r33 = {t: w33(t) for t in sorted(M[M.part == 2].task.unique())}
    r34 = {t: w34(t) for t in sorted(M[M.part == 3].task.unique())}
    for t, d in r33.items():
        if t in KIDNEY:
            S += [dict(prediction="W3.3", clause=k, task=t, holds=v) for k, v in d.items()]
    for t, d in r34.items():
        S += [dict(prediction="W3.4", clause=k, task=t, holds=v) for k, v in d.items()]
    if "INDIANA_KIDNEY" in r33 and "CCRCC" in r33:
        for src, R in (("W3.3", r33), ("W3.4", r34)):
            for k in ("a", "b", "c"):
                if k in R.get("CCRCC", {}) and k in R.get("INDIANA_KIDNEY", {}):
                    ci, ii = R["CCRCC"][k], R["INDIANA_KIDNEY"][k]
                    S.append(dict(prediction="W3.5", clause=f"{src}{k} agrees", task="INDIANA_KIDNEY",
                                  holds=None if ci is None or ii is None else ci == ii,
                                  note=f"CCRCC {ci}, INDIANA {ii}"))
    S = pd.DataFrame(S)
    overall = []
    for p, g in S.groupby("prediction"):
        if p == "W3.1":
            for wd, bcl in (("original", "b_original"), ("amended", "b_amended")):
                h = g[g.clause.isin(["a", bcl, "c"])].holds.dropna()
                overall.append(dict(prediction=f"W3.1 ({wd})", clause="ALL", task="all", holds=None,
                                    score=verdict(h)))
        else:
            overall.append(dict(prediction=p, clause="ALL", task="all", holds=None,
                                score=verdict(g.holds.dropna())))
    return pd.DataFrame(N), pd.concat([S, pd.DataFrame(overall)], ignore_index=True)


def verdict(h):
    h = list(h.astype(bool))
    if not h:
        return "not tested"
    return "held" if all(h) else ("refuted" if not any(h) else "partly held")


LABEL = {"hcp": "HCP (hcp)", "ghcp": "GHCP (ghcp)", "ghcp_noad": "GHCP, no size adjustment (ghcp_noad)",
         "within": "within donor, half split (within)", "within_plain": "within donor, split (within_plain)",
         "within_full": "within donor, full conformal (within_full)", "one_per": "one spot per donor (one_per)"}
SHORT = {"CCRCC": "CCRCC, 24 donors", "CCRCC_23merged": "CCRCC, 23 merged", "INDIANA_KIDNEY": "Indiana kidney",
         "LUNG_XENIUM": "Lung (Xenium)"}
COL = {"hcp": "#000000", "ghcp": "#1b6ca8", "ghcp_noad": "#8fbbd9", "within": "#c98a1b",
       "within_plain": "#e8a87c", "within_full": "#8e2c1f", "one_per": "#8c8c8c"}


def _style():
    import matplotlib as mpl
    mpl.rcParams.update({"font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8, "legend.fontsize": 7,
                         "xtick.labelsize": 6, "ytick.labelsize": 6, "axes.spines.top": False,
                         "axes.spines.right": False, "axes.titlelocation": "left", "savefig.dpi": 300})


def fig_map(M, path):
    from matplotlib import pyplot as plt
    _style()
    T = sorted(M[M.part == 1].task.unique())
    meths = ["ghcp", "ghcp_noad", "within", "within_plain", "within_full", "one_per"]
    fig, axes = plt.subplots(1, len(T), figsize=(7.2, 2.6), sharey=True, squeeze=False,
                             gridspec_kw=dict(wspace=0.06))
    for ax, t in zip(axes[0], T):
        P = M[(M.task == t) & (M.part == 1) & (M.alpha == A) & (M.K == 10)]
        h = P[P.method == "hcp"].set_index("o").width_mean
        for m in meths:
            q = P[(P.method == m) & (P.o > 0)].set_index("o").width_mean
            r = (q / h.reindex(q.index)).replace([np.inf], np.nan)
            ax.plot(r.index, r.values, marker="o", ms=2.5, lw=1.4 if m in ("ghcp", "within_full") else 0.9,
                    color=COL[m], label=LABEL[m], zorder=2)
            nv = P[(P.method == m) & P.narrowest_valid & (P.o > 0)]
            ax.scatter(nv.o, (nv.set_index("o").width_mean / h.reindex(nv.o)).values, s=34,
                       facecolors="none", edgecolors="k", lw=0.7, zorder=3)
        ax.axhline(1, color="k", lw=0.7, ls="--", zorder=1)
        ax.set_xscale("log")
        ax.set_xticks([3, 5, 10, 20, 50, 100]); ax.set_xticklabels(["3", "5", "10", "20", "50", "100"])
        ax.minorticks_off()
        ax.set_title(f"{SHORT.get(t, t)}\nhead fitted on {P.n_T_donors.median():.0f} donors")
        ax.margins(0.04)
    axes[0][0].set_ylabel("90% width relative to HCP")
    axes[0][0].text(3.2, 1.02, "HCP", fontsize=7, va="bottom")
    h, l = axes[0][0].get_legend_handles_labels()
    h.append(plt.Line2D([], [], ls="", marker="o", ms=6, mfc="none", mec="k", mew=0.7)); l.append("narrowest valid method")
    fig.supxlabel("labelled spots in the target donor, o (log scale)", y=0.23, fontsize=8)
    fig.legend(h, l, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 0.0))
    fig.subplots_adjust(left=0.08, right=0.99, top=0.86, bottom=0.36)
    fig.savefig(path)
    return fig


def fig_fixed(M, path):
    from matplotlib import pyplot as plt
    _style()
    T = sorted(M[M.part == 3].task.unique())
    if not T:
        return None
    O = [5, 15, 25]
    meths = ["hcp", "ghcp", "within_plain", "within_full"]
    fig, axes = plt.subplots(len(T), len(O), figsize=(7.2, 2.3 * len(T) + 0.5), squeeze=False)
    for i, t in enumerate(T):
        for j, o in enumerate(O):
            ax = axes[i][j]
            P = M[(M.task == t) & (M.part == 3) & (M.alpha == A) & (M.o == o)]
            for m in meths:
                q = P[P.method == m].sort_values("K")
                q = q[np.isfinite(q.width_mean)]
                ax.plot(q.K, q.width_mean, marker="o", ms=2.5, lw=1.4 if m in ("ghcp", "within_full") else 0.9,
                        color=COL[m], label=LABEL[m])
            ax.set_xticks(sorted(P.K.unique()))
            ax.set_title(f"{SHORT.get(t, t)}, o = {o}")
            if j == 0:
                ax.set_ylabel("mean 90% width")
            ax.margins(0.04)
    h, l = axes[0][0].get_legend_handles_labels()
    fig.supxlabel("reference donors K (prediction head fitted once, at K = 20)", y=0.075, fontsize=8)
    fig.legend(h, l, loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(0.5, 0.0))
    fig.subplots_adjust(left=0.08, right=0.99, top=0.95, bottom=0.17, hspace=0.45, wspace=0.22)
    fig.savefig(path)
    return fig


def main(a):
    os.makedirs(a.out, exist_ok=True)
    M = pd.read_csv(a.map)
    M["valid"] = M.valid.astype(str) == "True"
    M["narrowest_valid"] = M.narrowest_valid.astype(str) == "True"
    N, S = score(M)
    N.to_csv(os.path.join(a.out, "w3_report_numbers.csv"), index=False)
    S.to_csv(os.path.join(a.out, "w3_prediction_scores.csv"), index=False)
    if not a.no_figs:
        fig_map(M, os.path.join(a.out, "fig_w3_map.png"))
        fig_fixed(M, os.path.join(a.out, "fig_w3_fixed_head.png"))
    print(S[S.clause == "ALL"][["prediction", "score"]].to_string(index=False))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--map", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--no-figs", action="store_true")
    main(p.parse_args())
