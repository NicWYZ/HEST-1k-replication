"""fig02_replicate_leak -- slide 4. What a same-specimen replicate is worth.

Stage: deck rendering (deck_figures_and_repo_update.md section 1.2, fig02).
Inputs:
  results/round2/R5c_leak/r5c_replicate_leak.csv   one row per task x encoder x held-out slide
  results/round2/R5c_leak/r5c_leak_summary.csv     per-task mean, count, share of gap
Outputs: figures/deck/fig02_replicate_leak.{png,pdf}

Design: hold out one slide, draw two training sets of IDENTICAL size -- one from
a pool containing the slide's same-donor partner, one from a pool without it --
and score the same test spots. The pair of points is that contrast; the line
between them is the leak.

The distinction the figure has to carry is the one my first pass got wrong.
IDC's shipped folds put TENX95 and TENX99 in DIFFERENT folds, so each is in the
other's training set and the leak is realised in the benchmark as published.
READ's folds hold each pair out TOGETHER, so no replicate is ever in its
partner's training set: READ's number is a counterfactual -- what a replicate
would be worth if the split did not group it -- and a second independent
estimate of the same quantity, not a defect. Expressing READ as a share of its
task gap would be wrong, so that column is printed only where the flag in
r5c_leak_summary.csv says the leak is realised.
"""
import matplotlib.pyplot as plt
import numpy as np

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from _deckstyle import (ACCENT, BLUE, ENCODERS, ENCODER_COLOUR, GREY, HALF,
                        PRETTY, apply_deck_style, footnote, read, save)

apply_deck_style()

d = read("results/round2/R5c_leak/r5c_replicate_leak.csv")
s = read("results/round2/R5c_leak/r5c_leak_summary.csv").set_index("task")

assert set(d.encoder) == set(ENCODERS), f"expected {ENCODERS}, found {sorted(set(d.encoder))}"
# The controlled design is the whole point: if the two arms ever differ in
# training size the contrast is confounded, so check rather than trust.
sz = d.groupby(["task", "fold"]).size()
assert (sz == len(ENCODERS)).all(), "expected one row per encoder per held-out slide"

TASKS = ["IDC", "READ"]
slides = [(t, f) for t in TASKS for f in sorted(d[d.task == t].fold.unique())]
OFF = {e: o for e, o in zip(ENCODERS, (-0.22, 0.0, 0.22))}

fig, (ax, axr) = plt.subplots(1, 2, figsize=HALF,
                              gridspec_kw=dict(width_ratios=[2.9, 1.0], wspace=0.06))

for xi, (t, f) in enumerate(slides):
    for e in ENCODERS:
        r = d[(d.task == t) & (d.fold == f) & (d.encoder == e)].iloc[0]
        x = xi + OFF[e]
        ax.plot([x, x], [r.without_replicate, r.with_replicate], color="0.62", lw=1.0, zorder=2)
        ax.plot(x, r.without_replicate, "o", ms=5.2, mfc="white", mec=ENCODER_COLOUR[e],
                mew=1.6, zorder=3)
        ax.plot(x, r.with_replicate, "o", ms=5.2, color=ENCODER_COLOUR[e], zorder=3)

ax.axhline(0, color="0.78", lw=0.8, ls=":", zorder=1)
nb = len(d[d.task == "IDC"].fold.unique())
ax.axvline(nb - 0.5, color="0.86", lw=1.0, zorder=1)
ax.set_xticks(range(len(slides)))
ax.set_xticklabels([f for _, f in slides])
ax.set_ylabel("Within-slide Pearson")
ax.set_xlim(-0.6, len(slides) - 0.4)
# Explicit y limits rather than margins: the automatic upper tick ran to 0.8,
# past the axis and off the canvas, and left the group headers sitting on it.
lo = min(d.without_replicate.min(), 0.0)
hi = d.with_replicate.max()
ax.set_ylim(lo - 0.045, hi + 0.075)

# Group headers sit ABOVE the axes, so they cannot collide with a y tick or
# with the topmost data point.
for t, lo, hi in [("IDC", -0.5, nb - 0.5), ("READ", nb - 0.5, len(slides) - 0.5)]:
    realised = bool(s.loc[t, "leak_realised_in_shipped_split"])
    ax.text((lo + hi) / 2, 1.015, f"{t} — pair {'split across folds' if realised else 'held out together'}",
            transform=ax.get_xaxis_transform(), ha="center", va="bottom", fontsize=12,
            color=ACCENT if realised else GREY, fontweight="bold")

hs = [plt.Line2D([], [], marker="o", ls="", ms=5.2, color=ENCODER_COLOUR[e],
                 label=PRETTY[e]) for e in ENCODERS]
hs += [plt.Line2D([], [], marker="o", ls="", ms=5.2, mfc="white", mec="0.35", mew=1.6,
                  label="partner absent"),
       plt.Line2D([], [], marker="o", ls="", ms=5.2, color="0.35",
                  label="partner present")]
# Upper right, inside the axes: that block is empty (no slide reaches 0.55 right
# of TENX99). At lower left the legend sat on the TENX95/TENX99 tick labels.
ax.legend(handles=hs, loc="upper right", ncol=2, handletextpad=0.5,
          columnspacing=1.4, labelspacing=0.7, borderpad=0.4)

# Right panel: the per-task summary, every figure read from the summary CSV.
axr.axis("off")
lines, ypos = [], 0.93
for t in TASKS:
    r = s.loc[t]
    realised = bool(r.leak_realised_in_shipped_split)
    axr.text(0.0, ypos, t, fontsize=13, fontweight="bold",
             color=ACCENT if realised else GREY, transform=axr.transAxes)
    ypos -= 0.085
    body = [f"mean {r['mean']:+.3f}",
            f"{int(r.n_positive)}/{int(r['count'])} positive",
            f"range {r['min']:+.3f} to {r['max']:+.3f}"]
    if realised:
        body.append(f"{r.share_of_gap:.0%} of the {r.random_minus_patient:.3f} gap")
    else:
        body.append("counterfactual: folds")
        body.append("group the pairs, so no")
        body.append("leak in the shipped split")
    for b in body:
        axr.text(0.0, ypos, b, fontsize=11.5, color="0.25", transform=axr.transAxes)
        ypos -= 0.075
    ypos -= 0.045

pooled = d.leak.mean()
footnote(fig, f"Test spots and training-set size held fixed within every pair; only the partner's "
              f"availability varies. Positive in {int((d.leak > 0).sum())} of {len(d)} encoder-slide "
              f"cells, pooled mean {pooled:+.4f}. Same-donor pairs established in "
              f"results/round2/R5b_audit/ (IDC probable, unresolved; READ confirmed same specimen).")
# Explicit margins rather than tight_layout: the right-hand panel is a text
# block with its axes switched off, which tight_layout cannot measure.
fig.subplots_adjust(left=0.078, right=0.995, top=0.915, bottom=0.255)
save(fig, "fig02_replicate_leak")

print(s[["mean", "count", "n_positive", "share_of_gap",
         "leak_realised_in_shipped_split"]].to_string())
print(f"[fig02] pooled leak {pooled:+.4f}; positive {int((d.leak > 0).sum())}/{len(d)}")
