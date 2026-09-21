"""fig05_r2_ladder -- slide 9. Where the R^2 deficit goes.

Stage: deck rendering (deck_figures_and_repo_update.md section 1.2, fig05).
Inputs:
  results/round2/R1b_heads/r1b_ladder_pooled.csv      pooled rungs and gains
  results/round2/R1b_heads/r1b_ladder_by_task.csv     the same rungs per task
  results/round2/R1b_heads/r1b_ladder_by_encoder.csv  rho/r per encoder
Outputs: figures/deck/fig05_r2_ladder.{png,pdf}

The benchmark head is Ridge(fit_intercept=False) on PCA features that are
centred by construction, so its predictions have training mean zero while
log1p(y) has a positive mean. Pearson is shift-invariant and never saw it; R^2
is not. Using the identity R^2 = 2*r*rho - rho^2 - b^2/s_y^2 on the stored
columns, each rung fixes one more term without refitting anything.

Two readings the figure has to keep straight. The third rung uses the TEST
fold's own mean, so it is diagnostic, not achievable -- it measures a
slide-level mean shift that no training-mean intercept can track. The fourth
equals r^2 in every individual cell, and r^2 is the ceiling any level-and-scale
recalibration of that cell can reach, so the gap from there to 1 is the
encoder's pattern limit and not something calibration can recover. The plotted
pooled value is the median of those per-cell r^2, which is not the square of the
pooled median r (0.0997 against 0.0992).

The pooled rungs are NOT the mean of the per-task columns: averaging ten task
medians is not the median over all cells, and the two differ materially
(-1.064 against -0.953 on the first rung). Both files are read separately and
the pooled one is used for the pooled panel.
"""
import matplotlib.pyplot as plt
import numpy as np

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from _deckstyle import (ACCENT, ENCODER_COLOUR, FULL, GREY, GREY_LIGHT,
                        PRETTY, apply_deck_style, read, save)

apply_deck_style()

RUNGS = ["faithful", "train-mean intercept", "oracle level",
         "oracle level and optimal scale"]
# Short names for the per-task panel only; the pooled panel names the rungs in
# full on its y axis, so this one does not need to repeat them and at this panel
# width the two-line names ran together.
SHORT = ["shipped", "intercept", "oracle\nlevel", "oracle\n+ scale"]

pooled = read("results/round2/R1b_heads/r1b_ladder_pooled.csv").iloc[0]
by_task = read("results/round2/R1b_heads/r1b_ladder_by_task.csv")
by_enc = read("results/round2/R1b_heads/r1b_ladder_by_encoder.csv")

vals = np.array([float(pooled[r]) for r in RUNGS])
gains = np.diff(vals)
# The fourth rung is r^2 PER CELL by construction, and the pooled value is the
# median of those r^2 -- which is not the square of the pooled median r. Here
# they are 0.0997 against 0.0992, a 5e-04 gap purely from median(x^2) !=
# median(x)^2. Worth stating rather than smoothing: the ceiling reading is a
# per-cell statement, and the panel reports the median of it. The check below is
# a sanity band on that gap, not an equality.
r2_of_median = float(pooled.median_r) ** 2
assert abs(vals[3] - r2_of_median) < 0.02, \
    f"rung 4 ({vals[3]:.6f}) is implausibly far from r^2 of the median r ({r2_of_median:.6f})"
# The gain columns and the rung differences are independently rounded to 6
# decimals in the CSV, so they can disagree in the last digit; 2e-06 is the
# tolerance that precision allows, not a loosened check.
for i, g in enumerate(gains):
    stored = float(pooled[f"gain_{i + 1}"])
    assert abs(g - stored) < 2e-6, f"gain {i + 1}: {g:.8f} vs stored {stored:.8f}"

# Two rows. The rho/r panel was first an inset inside the per-task panel and
# covered the task lines it sat on, with its own y labels running into the host
# axis; a 1x3 row left the four two-line rung labels too narrow to read.
fig = plt.figure(figsize=FULL)
gs = fig.add_gridspec(2, 2, width_ratios=[1.0, 1.0], height_ratios=[1.0, 1.28],
                      wspace=0.30, hspace=0.62)
axes = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])]

ax = axes[0]
x = np.arange(4)

# The pooled ladder runs HORIZONTALLY: one row per rung. Vertically, this panel
# had to carry four two-line tick labels plus a value label and a gain label per
# step in about three inches, and no arrangement of offsets kept them apart --
# the aspect ratio was fighting the annotation count. As rows, each rung gets a
# single-line name on the y axis and its own clear band for both numbers.
y = np.arange(4)[::-1]
ax.axvline(0, color="0.72", lw=1.0, ls=":", zorder=1)
ax.plot(vals, y, "-", color=ACCENT, lw=2.0, zorder=3)
ax.plot(vals, y, "o", ms=9, color=ACCENT, zorder=4)
for yi, v in zip(y, vals):
    ax.annotate(f"{v:+.3f}", xy=(v, yi), xytext=(12, 0), textcoords="offset points",
                ha="left", va="center", fontsize=12.5, color=ACCENT, fontweight="bold")
for i, g in enumerate(gains):
    ax.annotate(f"+{g:.3f}", xy=((vals[i] + vals[i + 1]) / 2, (y[i] + y[i + 1]) / 2),
                xytext=(0, 0), textcoords="offset points", ha="center", va="center",
                fontsize=12, color="0.25",
                bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none"))
ax.set_yticks(y)
ax.set_yticklabels(["as shipped (no intercept)", "training-mean intercept",
                    "oracle level (test-fold mean)", "oracle level + optimal scale"])
ax.set_xlabel("Fold-median $R^2$")
# Explicit, like fig01's: automatic placement puts this label higher than its
# padding implies and it reaches the lowest rung's value label.
ax.xaxis.set_label_coords(0.5, -0.24)
ax.set_ylim(-0.6, 3.6)
# Right limit set by the widest value LABEL, not by the widest value: the labels
# sit to the right of their points and at 0.30 the rung-4 label crossed the panel
# edge into the next column's y-axis label.
ax.set_xlim(vals.min() - 0.16, 0.72)
ax.text(0.5, 1.02, "pooled over 12 encoders, 10 tasks, 29 folds",
        transform=ax.transAxes, ha="center", va="bottom", fontsize=12,
        fontweight="bold", color="0.2")

ax = axes[1]
for _, r in by_task.iterrows():
    ax.plot(x, [float(r[c]) for c in RUNGS], "-", color=GREY_LIGHT, lw=1.1, zorder=2)
ax.plot(x, vals, "-", color=ACCENT, lw=2.0, zorder=4, label="pooled")
ax.plot(x, vals, "o", ms=6, color=ACCENT, zorder=5)
ax.axhline(0, color="0.72", lw=1.0, ls=":", zorder=1)
# Name the two extremes rather than all ten: the message is the spread.
ext = [by_task.loc[by_task[RUNGS[0]].idxmin()], by_task.loc[by_task[RUNGS[0]].idxmax()]]
for r in ext:
    ax.annotate(r.task, xy=(0, float(r[RUNGS[0]])), xytext=(6, 0),
                textcoords="offset points", ha="left", va="center",
                fontsize=11, color="0.35")
ax.set_xticks(x)
ax.set_xticklabels(SHORT)
ax.set_ylabel("Fold-median $R^2$")
ax.set_xlim(-0.45, 3.45)
ax.legend(loc="lower right", borderpad=0.4)
ax.text(0.5, 1.02, f"one line per task ({len(by_task)} tasks)",
        transform=ax.transAxes, ha="center", va="bottom", fontsize=12,
        fontweight="bold", color="0.2")

# The scale term, per encoder, as its own panel.
ins = fig.add_subplot(gs[1, 0])
be = by_enc.sort_values("rho_over_r")
cols = [ENCODER_COLOUR.get(e, GREY) for e in be.encoder]
ins.barh(np.arange(len(be)), be.rho_over_r, color=cols, height=0.72,
         edgecolor="white", lw=0.5, zorder=3)
ins.axvline(float(pooled.rho_over_r), color=ACCENT, lw=1.3, ls="--", zorder=4)
ins.annotate(f"pooled {float(pooled.rho_over_r):.2f}",
             xy=(float(pooled.rho_over_r), -0.55), xytext=(4, 0),
             textcoords="offset points", ha="left", va="bottom", fontsize=11,
             color=ACCENT, fontweight="bold")
ins.set_yticks(np.arange(len(be)))
ins.set_yticklabels([PRETTY.get(e, e) for e in be.encoder], fontsize=11)
ins.set_xlim(1.0, float(be.rho_over_r.max()) * 1.10)
ins.set_xlabel(r"$\rho / r$  (1 = optimally scaled)", fontsize=11)
# Set explicitly: automatic placement put this label on the tick labels, the
# same failure fig01's x-axis label had.
ins.xaxis.set_label_coords(0.5, -0.20)
ins.tick_params(labelsize=11)
ins.set_title("predictions spread more than their correlation warrants",
              fontsize=12, fontweight="bold", color="0.2", pad=6)

axn = fig.add_subplot(gs[1, 1])
axn.axis("off")
axn.set_xticks([])
axn.set_yticks([])
# The explanatory text lives here rather than as annotations inside the ladder
# panel, which had four kinds of label competing for the same band.
notes = [
    f"Medians over {int(pooled.n_rows):,} encoder-task-fold-gene cells,",
    r"from the stored columns by the identity",
    r"$R^2 = 2r\rho - \rho^2 - b^2/s_y^2$, nothing refitted.",
    r"$R^2 = 0$ is predicting the test fold's own gene mean.",
    "",
    "Rung 3 uses the test fold's mean, so it is diagnostic",
    "rather than achievable: it measures a slide-level",
    "shift no training-mean intercept can track.",
    "",
    rf"Rung 4 is median$(r^2) = {vals[3]:.4f}$; per cell, $r^2$ is the",
    "ceiling for any level-and-scale recalibration.",
]
for i, line in enumerate(notes):
    axn.text(0.0, 0.97 - 0.112 * i, line, fontsize=11, color="0.35",
             transform=axn.transAxes, va="top", ha="left")

fig.subplots_adjust(left=0.082, right=0.988, top=0.925, bottom=0.075)
save(fig, "fig05_r2_ladder")

print("pooled rungs: " + "  ".join(f"{r}={v:+.4f}" for r, v in zip(RUNGS, vals)))
print("gains: " + "  ".join(f"+{g:.4f}" for g in gains))
print(f"rho/r pooled {float(pooled.rho_over_r):.4f} | "
      f"best {be.iloc[0].encoder} {be.iloc[0].rho_over_r:.3f} | "
      f"worst {be.iloc[-1].encoder} {be.iloc[-1].rho_over_r:.3f}")
