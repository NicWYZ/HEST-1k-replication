"""fig01_fidelity -- slide 3. Replication fidelity, per encoder.

Stage: deck rendering (deck_figures_and_repo_update.md section 1.2, fig01).
Inputs:
  results/summary/results_encoder.csv        our avg Pearson on the 9 paper tasks
  results/summary/scaling_law_inputs.csv     the paper's Table 1 printed values
  results/summary/hest_leaderboard_030426.csv  the live leaderboard, 3 Apr 2026
Outputs: figures/deck/fig01_fidelity.{png,pdf}

Three values per encoder on one axis: ours, the paper's printed Table 1 average,
and the live leaderboard. Sorted by ours.

Three things the data forces and the figure must not hide.

The paper's Table 1 covers ten encoders -- H-Optimus-1 and CONCH v1.5 have no
paper value at all, so those slots are marked `n.d.` rather than left blank,
because an empty slot on a dot plot reads as a low value.

"Exact" means "agrees to the four decimals the leaderboard publishes", and this
script computes the set rather than asserting it. That matters: the instruction
asks for "the two exact hits (ResNet50, H-Optimus-1)", but avg_paper9 is stored
rounded to 4 dp and at that precision SEVEN of twelve encoders agree, while at
full precision (recomputed from results_task.csv) NONE agree exactly -- the
closest are H-Optimus-1, GigaPath and CONCH v1 at 1.1e-05. ResNet50 and
H-Optimus-1 are both in the agreeing set and are annotated as the deck's two
callouts, but the figure states the count so the slide cannot imply they are
uniquely exact. ResNet50 is the informative case for the reason the README
gives -- no gated weights, no version ambiguity, no transform drift -- not
because it is the only match.

Note that ours and the leaderboard agree far more closely than ours and the
paper's printed Table 1 (mean |diff| 0.0002 against 0.0027): the leaderboard is
the live recomputation, Table 1 is the frozen printed value.
"""
import matplotlib.pyplot as plt
import numpy as np

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from _deckstyle import (ACCENT, ENCODERS, FULL, GREY, GREY_LIGHT, PRETTY,
                        apply_deck_style, footnote, read, save)

apply_deck_style()

ours = read("results/summary/results_encoder.csv")
ours = ours[ours["head"] == "pca_ridge"][["encoder", "avg_paper9", "n_tasks_paper9"]]
ours = ours.dropna(subset=["avg_paper9"]).sort_values("avg_paper9", ascending=False)

paper = read("results/summary/scaling_law_inputs.csv")[["encoder", "paper_printed"]]
board = read("results/summary/hest_leaderboard_030426.csv")[["encoder", "Average"]]
board = board.dropna(subset=["encoder"]).rename(columns={"Average": "leaderboard"})

d = ours.merge(paper, on="encoder", how="left").merge(board, on="encoder", how="left")
assert (d.n_tasks_paper9 == 9).all(), "every encoder must average the same nine tasks"

# Agreement with the leaderboard at the precision both are published to (4 dp).
d["agrees_4dp"] = d.avg_paper9.round(4) == d.leaderboard.round(4)
n_agree = int(d.agrees_4dp.sum())
# The two the deck calls out. Asserted to be inside the agreeing set, so the
# annotation cannot outlive a change in the underlying numbers.
CALLOUTS = ["resnet50", "hoptimus1"]
assert set(CALLOUTS) <= set(d[d.agrees_4dp].encoder), \
    "a deck callout no longer agrees with the leaderboard at 4 dp -- re-check the slide text"

fig, ax = plt.subplots(figsize=FULL)
y = np.arange(len(d))[::-1]

for yi, (_, r) in zip(y, d.iterrows()):
    if np.isfinite(r.paper_printed):
        ax.plot([r.paper_printed, r.avg_paper9], [yi, yi], color=GREY_LIGHT, lw=1.6,
                zorder=1, solid_capstyle="butt")

ax.scatter(d.paper_printed, y, s=58, facecolor="white", edgecolor=GREY, lw=1.4,
           zorder=3, label="paper Table 1 (printed)")
ax.scatter(d.leaderboard, y, s=150, marker="|", color=GREY, lw=1.8, zorder=2,
           label="live leaderboard, 3 Apr 2026")
ax.scatter(d.avg_paper9, y, s=64, color=ACCENT, zorder=4, label="ours")

for yi, (_, r) in zip(y, d.iterrows()):
    if not np.isfinite(r.paper_printed):
        ax.annotate("n.d. in Table 1", xy=(r.avg_paper9 - 0.0035, yi), ha="right",
                    va="center", fontsize=11, color=GREY, style="italic")

ax.set_yticks(y)
ax.set_yticklabels([PRETTY.get(e, e) for e in d.encoder])
ax.set_xlabel("Average Pearson over the nine paper tasks   (higher = better)")
# Placed explicitly. Automatic placement put the label's box 20 pt higher than
# its labelpad implies -- overlapping every x tick label -- and raising labelpad
# did not move it, so the position is set in axes coordinates instead.
ax.xaxis.set_label_coords(0.5, -0.105)
ax.margins(y=0.035)
lo = float(np.nanmin([d.avg_paper9.min(), d.paper_printed.min(), d.leaderboard.min()]))
hi = float(np.nanmax([d.avg_paper9.max(), d.paper_printed.max(), d.leaderboard.max()]))
ax.set_xlim(lo - 0.030, hi + 0.020)
ax.set_xticks(np.arange(0.30, 0.441, 0.02))

# Value labels on the two the deck calls out. A per-row agreement marker was
# tried and dropped: twelve cryptic glyphs in a right-hand column cost more
# reading than they carry, and the count belongs in one legend line instead.
order = d.encoder.tolist()
for e in CALLOUTS:
    r = d[d.encoder == e].iloc[0]
    yi = int(y[order.index(e)])
    ax.annotate(f"{r.avg_paper9:.4f}", xy=(r.avg_paper9, yi),
                xytext=(r.avg_paper9 + 0.0048, yi), va="center", fontsize=12,
                color=ACCENT, fontweight="bold",
                arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.9, shrinkA=2, shrinkB=3))

# Legend inside the axes, in the empty lower-right block (no encoder plots above
# x=0.39 below the CONCH v1 row). Two placements were tried and rejected: at the
# default lower right it sat on the 0.36/0.38 tick labels, and below the axes it
# collided with the x-axis label and the footnote. labelspacing is widened
# because at the default the three entry boxes touch each other.
h, lab = ax.get_legend_handles_labels()
ax.legend(h, lab, loc="lower right", bbox_to_anchor=(0.995, 0.155),
          handletextpad=0.6, labelspacing=0.85, borderpad=0.4)
mad_board = (d.avg_paper9 - d.leaderboard).abs().mean()
mad_paper = (d.avg_paper9 - d.paper_printed).abs().mean()
footnote(fig,
    f"pca_ridge head, nine paper tasks (HCC excluded, the paper's convention). {n_agree} of "
    f"{len(d)} encoders agree with the leaderboard at the 4 dp both are published to; mean "
    f"|ours - leaderboard| {mad_board:.4f}, against {mad_paper:.4f} versus the paper's printed "
    f"Table 1. Labelled: {' and '.join(PRETTY.get(e, e) for e in CALLOUTS)} - both inside that "
    f"agreeing set, not uniquely exact.")
fig.subplots_adjust(left=0.135, right=0.985, top=0.985, bottom=0.215)
res = save(fig, "fig01_fidelity")

print(f"[fig01] agree with leaderboard at 4 dp: {n_agree}/{len(d)} -> "
      f"{d[d.agrees_4dp].encoder.tolist()}")
print(f"[fig01] mean |ours - leaderboard| = {mad_board:.5f} | "
      f"mean |ours - paper_printed| = {mad_paper:.5f}")
print(d.round(4).to_string(index=False))
