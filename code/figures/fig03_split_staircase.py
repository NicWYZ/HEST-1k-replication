"""fig03_split_staircase -- slide 5. Split design costs more than encoder choice.

Stage: deck rendering (deck_figures_and_repo_update.md section 1.2, fig03).
Inputs:
  results/round2/R3_splits/r3_decomposition_terms.csv   pooled term means
  results/round2/R3_splits/r3_per_task_terms.csv        per-task terms
  results/round2/R3_splits/split_v4__*.csv              the grid sweep
  results/summary/results_encoder.csv                   the between-encoder spread
Outputs: figures/deck/fig03_split_staircase.{png,pdf}

The instruction offers two constructions and this script takes the second: two
waterfalls side by side rather than one that mixes averaging populations. The
reason is that the last two steps are only DEFINED on the three tasks where a
patient contributes more than one slide (PRAD, COAD, READ) -- on the other seven
each patient has exactly one slide, so "novel slide" and "same patient, other
slide" are the same contrast and cannot be separated. Splicing a ten-task mean
onto a three-task mean inside one bar stack would put two populations in one
column; drawing both and labelling each keeps that visible.

The axis is Pearson LOST relative to a random split, which is what the term
files contain (differences, not levels). That also makes the between-encoder
spread directly comparable on the same axis: it too is a Pearson difference.
Both waterfalls are checked to close on the TOTAL in the file before drawing.
"""
import matplotlib.pyplot as plt
import numpy as np

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from _deckstyle import (ACCENT, FULL, GREY, GREY_LIGHT, apply_deck_style,
                        footnote, read, save)

apply_deck_style()

dec = read("results/round2/R3_splits/r3_decomposition_terms.csv").set_index("term")
pt = read("results/round2/R3_splits/r3_per_task_terms.csv")
enc = read("results/summary/results_encoder.csv")

FIRST3 = ["training-set size", "spatial adjacency, size matched", "residual adjacency (buffer)"]
# Short two-line tick labels. Rotated labels were tried first and overflowed the
# bottom margin into the footnote; unrotated short ones fit and read faster.
SHORT = {"training-set size": "training\nset size",
         "spatial adjacency, size matched": "spatial\nadjacency",
         "residual adjacency (buffer)": "residual\nadjacency",
         "patient identity": "patient\nidentity",
         "novel slide": "novel\nslide",
         "same patient,\nother slide": "same patient,\nother slide"}
TOTAL = "TOTAL random - patient"
MULTI = ["COAD", "PRAD", "READ"]

# Ten-task version: the three measurable steps, then everything left over, which
# is patient identity (slide identity is not separable here -- see the docstring).
ten = [(s, float(dec.loc[s, "mean"])) for s in FIRST3]
ten_total = float(dec.loc[TOTAL, "mean"])
ten.append(("patient identity", ten_total - sum(v for _, v in ten)))
assert abs(sum(v for _, v in ten) - ten_total) < 1e-9

# Three-task version: same three steps averaged over the three multi-slide tasks
# only, then the two steps that exist there.
m = pt[pt.task.isin(MULTI)]
assert len(m) == 3, f"expected 3 multi-slide tasks, found {sorted(m.task)}"
three = [(s, float(m[s].mean())) for s in FIRST3]
three += [("novel slide", float(m["novel slide"].mean())),
          ("same patient,\nother slide", float(m["same patient, other slide"].mean()))]
three_total = float(m[TOTAL].mean())
assert abs(sum(v for _, v in three) - three_total) < 5e-4, \
    f"three-task waterfall does not close: {sum(v for _, v in three):.5f} vs {three_total:.5f}"

ours = enc[enc["head"] == "pca_ridge"].dropna(subset=["avg_paper9"])
spread = float(ours.avg_paper9.max() - ours.avg_paper9.min())

sv = []
for e in ("hoptimus0", "uni_v2", "resnet50"):
    sv.append(read(f"results/round2/R3_splits/split_v4__{e}.csv"))
sv = __import__("pandas").concat(sv, ignore_index=True)
gr = (sv[sv.design.isin(["blocked", "blocked_buffered"])]
      .groupby(["design", "grid"]).pearson_within.mean().unstack("design"))
gr.index = gr.index.astype(int)

# Two rows rather than one. A single row of three panels -- and a variant with the
# grid sweep as an inset -- both failed the same way: four or five step labels
# cannot be read in a 3-inch-wide panel even shortened to two lines, and the
# aspect ratio was fighting the label count rather than the data. Two rows give
# each waterfall most of the figure width, which is what the labels need.
fig = plt.figure(figsize=FULL)
gs = fig.add_gridspec(2, 2, width_ratios=[1.0, 1.14], height_ratios=[1.0, 0.82],
                      wspace=0.16, hspace=0.62)
axes = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])]


def waterfall(ax, steps, total, header):
    cum = 0.0
    for i, (lab, v) in enumerate(steps):
        dominant = v == max(x for _, x in steps)
        ax.bar(i, v, bottom=cum, width=0.66, color=ACCENT if dominant else GREY_LIGHT,
               edgecolor="white", lw=0.8, zorder=3)
        ax.annotate(f"{v:.3f}", xy=(i, cum + v), xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=11,
                    color=ACCENT if dominant else "0.3",
                    fontweight="bold" if dominant else "normal")
        cum += v
        if i < len(steps) - 1:
            ax.plot([i + 0.33, i + 0.67], [cum, cum], color="0.65", lw=0.9, ls=":", zorder=2)
    ax.axhline(total, color="0.35", lw=1.0, zorder=4)
    # Total sits at the LEFT end of its own rule, where no bar reaches, so it
    # cannot collide with the final step's value label.
    ax.annotate(f"total {total:.3f}", xy=(-0.6, total), xytext=(2, 4),
                textcoords="offset points", ha="left", va="bottom", fontsize=11, color="0.25")
    ax.set_xticks(range(len(steps)))
    ax.set_xticklabels([SHORT.get(s, s) for s, _ in steps])
    ax.set_xlim(-0.65, len(steps) - 0.35)
    ax.text(0.5, 1.02, header, transform=ax.transAxes, ha="center", va="bottom",
            fontsize=12, fontweight="bold", color="0.2")
    return cum


waterfall(axes[0], ten, ten_total, f"all {int(dec.loc[TOTAL, 'n_tasks'])} tasks")
waterfall(axes[1], three, three_total, f"{len(MULTI)} multi-slide tasks\n({', '.join(MULTI)})")
hi = max(ten_total, three_total) * 1.20
for a in axes[:2]:
    a.set_ylim(0, hi)
    a.axhline(spread, color=ACCENT, lw=1.2, ls="--", zorder=5)
axes[0].set_ylabel("Within-slide Pearson lost\nrelative to a random split")
axes[1].set_yticklabels([])
# The reference line is annotated once, on the left panel, in the empty region
# above the first two (small) bars.
# Annotated once, ABOVE its own line in the right panel, where the band between
# the reference line and the total rule is empty. The left panel has no clear
# band: its 0.033 and 0.011 labels sit exactly where this text would go.
axes[1].annotate(f"between-encoder spread {spread:.3f}\n(best minus worst of 12 encoders)",
                 xy=(-0.58, spread), xytext=(2, 5), textcoords="offset points",
                 ha="left", va="bottom", fontsize=11, color=ACCENT)

ax = fig.add_subplot(gs[1, 0])
for design, col, mk, lab in [("blocked", GREY, "o", "blocked"),
                             ("blocked_buffered", ACCENT, "s", "blocked + buffer")]:
    ax.plot(gr.index, gr[design], marker=mk, ms=6, color=col, lw=1.6, label=lab, zorder=3)
    sp = float(gr[design].max() - gr[design].min())
    ax.annotate(f"spread {sp:.3f}", xy=(gr.index[0], gr[design].iloc[0]),
                xytext=(6, 9 if design == "blocked" else -18), textcoords="offset points",
                ha="left", fontsize=11, color=col,
                fontweight="bold" if design != "blocked" else "normal")
ax.set_xticks(list(gr.index))
ax.set_xlabel("Block grid (cells per side)")
ax.set_ylabel("Within-slide Pearson")
ax.margins(y=0.34)
# Direct end-of-line labels rather than a legend box: two series, and the legend
# competed with the spread annotations for the same corner.
for design, col, va in [("blocked", GREY, "bottom"), ("blocked_buffered", ACCENT, "top")]:
    lab = "blocked" if design == "blocked" else "blocked\n+ buffer"
    ax.annotate(lab, xy=(gr.index[-1], gr[design].iloc[-1]), xytext=(5, 0),
                textcoords="offset points", ha="left", va="center", fontsize=11,
                color=col, annotation_clip=False)
ax.set_xlim(gr.index.min() - 0.6, gr.index.max() + 2.6)
ax.text(0.5, 1.02, "buffer removes the\ngrid dependence", transform=ax.transAxes,
        ha="center", va="bottom", fontsize=12, fontweight="bold", color="0.2")

# The notes live in the fourth grid cell rather than as a banner under the
# figure, so they sit inside the canvas and beside what they describe.
axn = fig.add_subplot(gs[1, 1])
axn.axis("off")
axn.set_xticks([])
axn.set_yticks([])
notes = [
    f"Means over three encoders throughout.",
    f"Top left: all {int(dec.loc[TOTAL, 'n_tasks'])} tasks, {int(dec.loc[TOTAL, 'n_cells'])} encoder-task cells.",
    f"Top right: {', '.join(MULTI)} only -- the tasks where a",
    f"patient contributes more than one slide, so the last",
    f"two steps are separable. On the other seven each",
    f"patient has one slide and they are the same contrast.",
    f"Bottom: mean over tasks, folds and repeats per grid.",
]
for i, line in enumerate(notes):
    axn.text(0.0, 0.94 - 0.125 * i, line, fontsize=11, color="0.35",
             transform=axn.transAxes, va="top", ha="left")
fig.subplots_adjust(left=0.112, right=0.985, top=0.885, bottom=0.10)
save(fig, "fig03_split_staircase")

print("[fig03] ten-task steps:", [(s, round(v, 4)) for s, v in ten], "total", round(ten_total, 4))
print("[fig03] three-task steps:", [(s.replace(chr(10), ' '), round(v, 4)) for s, v in three],
      "total", round(three_total, 4))
print(f"[fig03] encoder spread {spread:.4f} | grid spreads "
      f"{ {c: round(float(gr[c].max() - gr[c].min()), 4) for c in gr.columns} }")
