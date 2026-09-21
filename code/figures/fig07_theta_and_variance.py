"""fig07_theta_and_variance -- slide 11. The estimand is slide-level; the unit is the donor.

Stage: deck rendering (deck_figures_and_repo_update.md section 1.2, fig07).
Inputs:
  results/round2/R6_theta/r6_theta_bootstrap_ci.csv        theta1 + 95% intervals
  results/round2/R6_variance/r6_theta_build_comparison.csv the two morphology builds
  results/round2/R6_variance/r6_variance_by_task.csv       nested components
  results/round2/R6_variance/r6_pooled_between_donor.csv   the pooled figure
Outputs: figures/deck/fig07_theta_and_variance.{png,pdf}

Left: HEST's own biomarker example -- Pearson of mean neoplastic nuclear area
against raw GATA3 counts -- on each of the four IDC slides, with spot-bootstrap
95% percentile intervals (200 resamples, seed 1, the same resampling that
produced the stored standard errors). The point is the spread BETWEEN slides
against the width WITHIN each: the intervals do not overlap, so the estimand is
a slide-level quantity and a single slide's value is not a property of the
tissue type.

One discrepancy against the outline, annotated rather than smoothed. The outline
says the example "reproduces at 0.46". That is the ROUND-1 morphology build
(0.4578). The current build -- which the instruction asks this panel to use --
gives 0.4209 on the same slide. Both are plotted, so the difference is visible
rather than hidden behind whichever number is quoted.

Right: where the variance in expression sits, on the audited donor labels rather
than HEST's patient field. Tasks are sorted by the between-donor share, with the
donor degrees of freedom under each bar, because five of the ten tasks rest on
df_donor = 1 and their between-donor share is not a measurement so much as a
single contrast. The label-status flag is marked for the same reason.
"""
import matplotlib.pyplot as plt
import numpy as np

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from _deckstyle import (ACCENT, FULL, GREY, apply_deck_style, footnote, read,
                        save)

apply_deck_style()

BS = read("results/round2/R6_theta/r6_theta_bootstrap_ci.csv")
TB = read("results/round2/R6_variance/r6_theta_build_comparison.csv")
VT = read("results/round2/R6_variance/r6_variance_by_task.csv")
PB = read("results/round2/R6_variance/r6_pooled_between_donor.csv")

d = BS.merge(TB[["sample_id", "v1_theta1_raw", "round1_reported"]], on="sample_id",
             how="left").sort_values("theta1_raw", ascending=False).reset_index(drop=True)
assert len(d) == 4, f"expected the four IDC slides, got {len(d)}"

# The claim the panel makes: between-slide spread exceeds within-slide width.
# Checked here so the annotation cannot outlive the numbers.
widest = float((d.ci_hi_percentile - d.ci_lo_percentile).max())
spread = float(d.theta1_raw.max() - d.theta1_raw.min())
assert spread > widest, f"spread {spread:.4f} is not wider than the widest interval {widest:.4f}"
gaps = [float(d.ci_lo_percentile.iloc[i] - d.ci_hi_percentile.iloc[i + 1])
        for i in range(len(d) - 1)]
n_disjoint = sum(g > 0 for g in gaps)

fig = plt.figure(figsize=FULL)
gs = fig.add_gridspec(1, 2, width_ratios=[0.86, 1.14], wspace=0.30)

# ------------------------------------------------------------------ left: theta1
ax = fig.add_subplot(gs[0, 0])
y = np.arange(len(d))[::-1]
ax.axvline(0, color="0.72", lw=1.0, ls=":", zorder=1)
for yi, (_, r) in zip(y, d.iterrows()):
    ax.plot([r.ci_lo_percentile, r.ci_hi_percentile], [yi, yi], color=ACCENT,
            lw=2.2, solid_capstyle="butt", zorder=3)
    ax.plot(r.theta1_raw, yi, "o", ms=8, color=ACCENT, zorder=4)
    ax.plot(r.v1_theta1_raw, yi, "s", ms=5.5, mfc="white", mec=GREY, mew=1.4, zorder=4)
    # Above the point, not to the right of the interval: right of the widest
    # interval the label crossed the panel edge into the next column's tick
    # labels, and the four rows are far enough apart to stack vertically.
    ax.annotate(f"{r.theta1_raw:+.3f}", xy=(r.theta1_raw, yi), xytext=(0, 11),
                textcoords="offset points", ha="center", va="bottom", fontsize=12,
                color=ACCENT, fontweight="bold")
ax.set_yticks(y)
ax.set_yticklabels([f"{r.sample_id}\n{int(r.n_spots):,} spots" for _, r in d.iterrows()])
ax.set_xlabel(r"$\theta_1$: nuclear area vs GATA3 (raw counts)")
ax.xaxis.set_label_coords(0.5, -0.115)
ax.set_ylim(-0.75, len(d) - 0.25)
ax.set_xlim(-0.16, 0.60)
# A marker legend in the panel's empty lower-right rather than a leader line to
# the top slide's square: the leader's text landed on the next row's value label
# wherever it was placed, and the distinction applies to all four rows anyway.
top = d.iloc[0]
ax.legend(handles=[
    plt.Line2D([], [], marker="o", ls="", ms=8, color=ACCENT,
               label="current build"),
    plt.Line2D([], [], marker="s", ls="", ms=5.5, mfc="white", mec=GREY, mew=1.4,
               label=f"round-1 build")],
    loc="lower right", bbox_to_anchor=(0.94, 0.02), frameon=False, fontsize=11,
    handletextpad=0.7, labelspacing=1.1)
ax.text(0.5, 1.02, "four slides, one tissue type",
        transform=ax.transAxes, ha="center", va="bottom", fontsize=12,
        fontweight="bold", color="0.2")

# --------------------------------------------------------- right: variance shares
ax = fig.add_subplot(gs[0, 1])
V = VT.copy()
for c in ("frac_donor", "frac_slide", "frac_spot"):
    V[c] = V[c].fillna(0.0)      # NaN where df_slide = 0, i.e. one slide per donor
V = V.sort_values("frac_donor", ascending=True).reset_index(drop=True)
yv = np.arange(len(V))
SEG = [("frac_donor", "between donors", ACCENT),
       ("frac_slide", "between slides,\nsame donor", "#7A7A7A"),
       ("frac_spot", "within slide", "#CFCFCF")]
left = np.zeros(len(V))
for c, lab, col in SEG:
    ax.barh(yv, V[c], left=left, height=0.66, color=col, edgecolor="white",
            lw=0.7, zorder=3, label=lab)
    left = left + V[c].to_numpy()
for i, r in V.iterrows():
    ax.annotate(f"{r.frac_donor:.2f}", xy=(r.frac_donor, i), xytext=(4, 0),
                textcoords="offset points", ha="left", va="center", fontsize=11,
                color="white" if r.frac_donor > 0.12 else ACCENT,
                fontweight="bold" if r.frac_donor > 0.12 else "normal")
# df_donor = 1 is the caveat that decides how the left-hand segment reads.
low = V.df_donor <= 1
ax.set_yticks(yv)
ax.set_yticklabels([f"{r.task}   df {int(r.df_donor)}"
                    + ("  \u25b2" if r.df_donor <= 1 else "")
                    + ("" if "verified" in str(r.status) and "contradicted" not in str(r.status)
                       else "  \u2022")
                    for _, r in V.iterrows()])
ax.set_xlabel("Share of expression variance")
ax.xaxis.set_label_coords(0.5, -0.088)
# The axis runs past 1.0 to open a strip of empty space at the right for the
# segment legend. Every row's bar fills 0 to 1, so any in-axes legend inside
# that range covers data, and below the panel it landed in the same horizontal
# band as both x-axis labels.
ax.set_xlim(0, 1.34)
ax.set_xticks(np.arange(0, 1.01, 0.2))
ax.set_ylim(-0.7, len(V) - 0.3)
pooled = float(PB.loc[PB.definition.str.startswith("well-powered"), "value"].iloc[0])
ax.axvline(pooled, color=ACCENT, lw=1.4, ls="--", zorder=5)
# On the IDC row, where the line crosses plain grey well clear of that row's own
# value label. Below the axis it landed on the x tick labels; the two rows above
# have their own labels within a few hundredths of the pooled value.
row_idc = int(V.index[V.task == "IDC"][0])
ax.annotate(f"pooled {pooled:.2f}", xy=(pooled, row_idc), xytext=(6, 0),
            textcoords="offset points", ha="left", va="center", fontsize=11,
            color=ACCENT, fontweight="bold")
# labelspacing is generous because the middle entry is two lines; at the
# default its box touched the entry above.
ax.legend(loc="center left", bbox_to_anchor=(1.005, 0.5), frameon=False,
          fontsize=11, handletextpad=0.6, labelspacing=1.7)
ax.text(0.5, 1.02, "variance in expression, on audited donor labels",
        transform=ax.transAxes, ha="center", va="bottom", fontsize=12,
        fontweight="bold", color="0.2")

footnote(fig, f"Left: spot bootstrap, 200 resamples, seed 1 -- the same resampling that produced "
              f"the stored standard errors, verified to reproduce them exactly. Between-slide "
              f"spread is {spread:.3f} against a widest interval of {widest:.3f}, and "
              f"{n_disjoint} of {len(d) - 1} adjacent pairs are disjoint. Squares are the "
              f"superseded round-1 morphology build, which reads {top.v1_theta1_raw:.3f} on the "
              f"top slide where the outline quotes 0.46. Right: method-of-moments components on the "
              f"R5b audited donor labels, with the pooled between-donor share over the two tasks "
              f"having df_donor $\\geq$ 3 marked; "
              f"\u25b2 marks df_donor $\\leq$ 1, where the between-donor "
              f"share is one contrast rather than an estimate, and \u2022 marks a task whose donor "
              f"labels are not fully verified.")
fig.subplots_adjust(left=0.098, right=0.988, top=0.905, bottom=0.155)
save(fig, "fig07_theta_and_variance")

print(d[["sample_id", "n_spots", "theta1_raw", "ci_lo_percentile", "ci_hi_percentile",
         "v1_theta1_raw"]].round(4).to_string(index=False))
print(f"between-slide spread {spread:.4f} | widest interval {widest:.4f} | "
      f"disjoint adjacent pairs {n_disjoint}/{len(d) - 1}")
print(V[["task", "donors", "slides", "df_donor", "frac_donor", "frac_slide", "frac_spot",
         "status"]].round(4).to_string(index=False))
print(f"pooled between-donor (well-powered) {pooled:.4f}")
