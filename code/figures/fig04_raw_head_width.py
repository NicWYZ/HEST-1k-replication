"""fig04_raw_head_width -- slide 6. The raw-head ranking tracks embedding width.

Stage: deck rendering (deck_figures_and_repo_update.md section 1.2, fig04).
Inputs:
  results/round2/R8_raw_heads/r8_raw_head_leaderboard.csv  ranks and widths
  results/round2/R8_raw_heads/r8_width_correlations.csv     the Spearmans
Outputs: figures/deck/fig04_raw_head_width.{png,pdf}

Table A13 of the paper ranks encoders on a ridge head fitted to the raw
embedding. R8 tested whether that ranking measures representation quality or
embedding width, using H-optimus-1 -- the strongest encoder in the set on the
PCA head and one of the widest -- as the sharpest available case. It lands 7th
of 12 on the raw head.

Each point is one encoder: its PCA-head rank against its raw-head rank. Colour
is embedding width, which is what the ordering follows. A second panel plotting
score against width directly was drafted and dropped -- the instruction asks for
the scatter with the two Spearmans annotated, and the extra panel changed no
conclusion while costing the labels their room.

The correlation file carries two cohorts, an 11-encoder one from round 1 (before
H-optimus-1 had raw-head cells) and the 12-encoder one R8 completed. This figure
uses the 12-encoder rows and says so, because quoting a correlation without its
cohort is how the two documents came to disagree about this number.
"""
import matplotlib.pyplot as plt
import numpy as np

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from _deckstyle import (ACCENT, FULL, GREY, PRETTY, apply_deck_style, footnote,
                        read, save)

apply_deck_style()

d = read("results/round2/R8_raw_heads/r8_raw_head_leaderboard.csv")
w = read("results/round2/R8_raw_heads/r8_width_correlations.csv")

N = int(d.encoder.nunique())
w12 = w[w.n_encoders == N]
assert len(w12), f"no correlation rows for the {N}-encoder cohort"


def spear(relation):
    r = w12[w12.relation == relation]
    assert len(r) == 1, f"expected one row for {relation!r}, found {len(r)}"
    return float(r.spearman.iloc[0]), float(r.p.iloc[0]), str(r.cohort.iloc[0])


rho_raw, p_raw, cohort = spear("embedding width vs raw_ridge mean Pearson")
rho_pca, p_pca, _ = spear("embedding width vs pca_ridge mean Pearson")
rho_rank, p_rank, _ = spear("raw_ridge rank vs pca_ridge rank")

fig, ax = plt.subplots(figsize=FULL)

lim = (0.3, N + 0.7)
ax.plot(lim, lim, color="0.82", lw=1.0, ls="--", zorder=1)
# Diagonal label at the LOWER-left end: the upper-right end is where the
# correlation block goes, that being the only empty quadrant.
# The diagonal carries no text label. Three placements were tried -- both ends
# and the middle -- and each collided with something: the lower-left with the
# H-Optimus-1 callout, the upper-right with the correlation block, the middle
# with UNI. What the diagonal means is stated in the footnote instead, which
# costs nothing and keeps the busiest band of the panel clear.

widths = sorted(d.width.unique())
sc = ax.scatter(d.rank_pca, d.rank_raw, c=d.width, cmap="viridis", s=150,
                edgecolor="white", lw=1.1, zorder=3,
                norm=plt.Normalize(min(widths), max(widths)))

# Label placement is explicit per encoder rather than rule-based: with twelve
# points on a 12x12 grid every uniform offset put at least two labels on top of
# each other or on a tick. (dx, dy) in points, then ha/va.
PLACE = {
    "hoptimus1": (14, 0, "left", "center"),      # at x=1, a label above hits the y ticks
    "hoptimus0": (0, -15, "center", "top"),
    "uni_v2": (13, -2, "left", "top"),   # H-Optimus-1 labels right into this slot
    "virchow": (0, -15, "center", "top"),
    "virchow2": (0, 13, "center", "bottom"),
    "gigapath": (0, -15, "center", "top"),
    "uni_v1": (0, -15, "center", "top"),
    "conch_v15": (-11, -6, "right", "top"),
    "conch_v1": (-11, 2, "right", "center"),       # its neighbour Phikon labels right
    "phikon": (11, -4, "left", "top"),
    "ctranspath": (11, -4, "left", "top"),
    "resnet50": (0, 13, "center", "bottom"),
}
for _, r in d.iterrows():
    hl = r.encoder == "hoptimus1"
    dx, dy, ha, va = PLACE[r.encoder]
    ax.annotate(PRETTY.get(r.encoder, r.encoder),
                xy=(r.rank_pca, r.rank_raw), xytext=(dx, dy),
                textcoords="offset points", ha=ha, va=va, fontsize=11.5,
                color=ACCENT if hl else "0.25",
                fontweight="bold" if hl else "normal")

h1 = d[d.encoder == "hoptimus1"].iloc[0]
ax.annotate("", xy=(h1.rank_pca, h1.rank_raw), xytext=(h1.rank_pca, h1.rank_pca),
            arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=1.5, shrinkA=4, shrinkB=8))
ax.annotate(f"H-Optimus-1: rank {int(h1.rank_pca)} on the PCA head,\n"
            f"rank {int(h1.rank_raw)} on the raw head",
            xy=(h1.rank_pca, (h1.rank_pca + h1.rank_raw) / 2), xytext=(12, -6),
            textcoords="offset points", ha="left", va="center", fontsize=12,
            color=ACCENT, fontweight="bold")

ax.annotate(f"Spearman(embedding width, score)\n"
            f"raw head   {rho_raw:+.2f}   (p = {p_raw:.1e})\n"
            f"PCA head  {rho_pca:+.2f}   (p = {p_pca:.3f})\n"
            f"n = {N} encoders",
            # Upper right. The lower-right block, tried first, sits exactly on the
            # narrow encoders -- the points the annotation is about.
            xy=(0.86, 0.965), xycoords="axes fraction", ha="right", va="top",
            fontsize=12, color="0.2", linespacing=1.5)

ax.set_xlabel("Rank on the PCA-256 head   (1 = best)")
ax.set_ylabel("Rank on the raw-embedding head   (1 = best)")
ax.set_xlim(*lim)
ax.set_ylim(*lim)
ax.set_xticks(range(1, N + 1))
ax.set_yticks(range(1, N + 1))
cb = fig.colorbar(sc, ax=ax, pad=0.015, fraction=0.04)
cb.set_label("width (dimensions)", fontsize=11)
cb.ax.tick_params(labelsize=11)
cb.set_ticks(widths)

footnote(fig, f"{N} encoders, cohort: {cohort}. The dashed line is equal rank on both heads; "
              f"points below it rank better on the raw head. On raw embeddings the Gram matrix is "
              f"effectively singular at the benchmark's fixed alpha; the PCA head projects every "
              f"encoder to {int(w12.pca_latent_dim.iloc[0])} dimensions first and the width effect "
              f"reverses sign. Rank-versus-rank Spearman {rho_rank:+.3f} (p = {p_rank:.3f}).")
fig.subplots_adjust(left=0.072, right=0.955, top=0.985, bottom=0.125)
save(fig, "fig04_raw_head_width")

print(d[["encoder", "width", "rank_pca", "rank_raw", "rank_shift"]]
      .sort_values("rank_raw").to_string(index=False))
print(f"[fig04] width vs raw {rho_raw:+.3f} (p={p_raw:.2e}) | width vs pca {rho_pca:+.3f} "
      f"(p={p_pca:.4f}) | rank vs rank {rho_rank:+.3f} (p={p_rank:.4f}) | cohort: {cohort}")
