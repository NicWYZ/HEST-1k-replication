"""fig06_session_signature -- slide 10. The signature is in the features, not the expression.

Stage: deck rendering (deck_figures_and_repo_update.md section 1.2, fig06).
Inputs:
  results/round2/R4_probes/r4_probes_v2.csv            the three PRAD probes
  results/round2/R6_variance/r6_prad_session_variance.csv  per-gene components
Outputs: figures/deck/fig06_session_signature.{png,pdf}

Left: what a linear probe on frozen PCA-256 features can decode inside ONE
patient, where tissue and donor are fixed. Middle: how much of that is tissue
composition, measured by regressing nuclear-morphology covariates out of the
features first. Right: how much of the measured expression the same session
axis explains.

Two things the data forces against the outline's wording, both annotated rather
than smoothed:

1. The outline says morphology adjustment removes "17-27% on cross-patient
   tasks". IDC is a cross-patient task and sits at 3.0%, so the range over the
   four is 3-27%. IDC is the one task here whose slides include a same-donor
   replicate pair, which is the obvious candidate explanation, so the figure
   marks IDC rather than dropping it or widening the claim silently.

2. The outline says within-slide variance is "0.6-0.9 everywhere"; the actual
   range over the ten tasks is 0.61-0.99. That belongs to fig07, but the same
   caution applies here: this panel reports the PRAD patient-2 decomposition
   only, and says so.

The resolution probe is the rescored one. Its first version reported 0.71 by
taking per-fold balanced accuracy on folds whose held-out labels are
single-class; with 5 slides in one class and 2 in the other, a constant
predictor scores 5/7 = 0.714. The majority-class baseline is drawn so that the
rescored value cannot be read as a low number without its reference.
"""
import matplotlib.pyplot as plt
import numpy as np

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from _deckstyle import (ACCENT, ENCODER_COLOUR, FULL, GREY, PRETTY,
                        apply_deck_style, footnote, read, save)

apply_deck_style()

ENC = ["hoptimus0", "uni_v2", "resnet50"]
P4 = read("results/round2/R4_probes/r4_probes_v2.csv")
PV = read("results/round2/R6_variance/r6_prad_session_variance.csv")

# (probe, accuracy column, short label, unit) -- the accuracy column differs by
# probe on purpose: the two-class probes are scored by pooling predictions over
# folds, because per-fold balanced accuracy is degenerate when a fold's held-out
# labels are all one class.
PROBES = [("probe1_slide_within_patient", "acc_blocked", "slide identity", "patient 2"),
          ("probe1b_scan_subcluster", "acc_blocked", "scan session", "patient 2"),
          ("probe2_2class", "acc_pooled_balanced", "resolution class", "patient 1")]
chance_by_probe = {}
TASKS = ["PRAD", "IDC", "LUNG", "PAAD", "SKCM"]
COMPS = [("within_slide", "within slide", "#BFBFBF"),
         ("between_slide_within_session", "between slides,\nsame session", "#7A7A7A"),
         ("between_session", "between sessions", ACCENT)]

# Two rows. A single row of three panels put the probe panel's grouped bars,
# its three chance lines and their labels into about four inches, where the
# tick labels ran together and the chance annotations collided; the variance
# bar meanwhile had a panel to itself and used a tenth of it. As two rows the
# stacked bar spans the full width, which is what its segment labels need.
fig = plt.figure(figsize=FULL)
gs = fig.add_gridspec(2, 2, width_ratios=[1.0, 1.05], height_ratios=[1.0, 0.62],
                      wspace=0.30, hspace=0.72)
axes = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, 0])]

# ----------------------------------------------------------------- left: probes
ax = axes[0]
w = 0.26
for k, (probe, col, lab, unit) in enumerate(PROBES):
    sub = P4[P4.probe == probe].set_index("encoder")
    for j, e in enumerate(ENC):
        ax.bar(k + (j - 1) * w, float(sub.loc[e, col]), width=w * 0.92,
               color=ENCODER_COLOUR[e], edgecolor="white", lw=0.6, zorder=3)
    ch = float(sub[["chance"]].iloc[0, 0])
    ax.plot([k - 1.55 * w, k + 1.55 * w], [ch, ch], color="0.25", lw=1.3, ls="--", zorder=4)
    # The chance VALUE goes in the tick label, with the class count it follows
    # from; the line is left as an unlabelled reference. Labelling each line in
    # place put the text either on the bars (the session group reaches 0.97) or
    # on the next group, and the gaps between groups are too narrow for it.
    chance_by_probe[probe] = ch
    if probe == "probe2_2class":
        mb = float(sub.majority_class_baseline.iloc[0])
        ax.plot([k - 1.55 * w, k + 1.55 * w], [mb, mb], color=ACCENT, lw=1.3, ls=":", zorder=4)
        # To the LEFT of its group: the band right of it runs into the next
        # column's y-axis label.
        # Just the value. Spelled out ("majority class 0.71") the text was wide
        # enough to cross the panel edge into the next column; what it means is
        # in the notes panel, which has room for the sentence.
        ax.annotate(f"{mb:.2f}", xy=(k, mb), xytext=(0, 4),
                    textcoords="offset points", ha="center", va="bottom",
                    fontsize=11.5, color=ACCENT, fontweight="bold")
ax.set_xticks(range(len(PROBES)))
# Three short lines rather than two long ones: the two-line form ran the
# neighbouring groups' labels together.
ax.set_xticklabels([f"{lab}\n{int(P4[P4.probe == pr].n_classes.iloc[0])} classes\n"
                    f"chance {chance_by_probe[pr]:.2f}"
                    for pr, _, lab, _ in PROBES])
# Widened so the group-2 annotations, which are wider than their group, stay
# inside the panel instead of reaching the next column's y-axis label.
ax.set_xlim(-0.62, 2.62)
ax.set_ylabel("Balanced accuracy")
ax.set_ylim(0, 1.32)
ax.set_yticks(np.arange(0, 1.01, 0.2))
ax.text(0.5, 1.02, "decodable from frozen features,\nwithin one PRAD patient",
        transform=ax.transAxes, ha="center", va="bottom", fontsize=12,
        fontweight="bold", color="0.2")

# ------------------------------------------------- middle: morphology adjustment
ax = axes[1]
p3 = P4[P4.probe == "probe3_composition_adjusted"].set_index(["task", "encoder"])
for k, t in enumerate(TASKS):
    for j, e in enumerate(ENC):
        ax.bar(k + (j - 1) * w, float(p3.loc[(t, e), "acc_drop"]), width=w * 0.92,
               color=ENCODER_COLOUR[e], edgecolor="white", lw=0.6, zorder=3)
means = {t: float(p3.loc[t, "acc_drop"].mean()) for t in TASKS}
for k, t in enumerate(TASKS):
    ax.annotate(f"{means[t] * 100:.1f}%", xy=(k, max(float(p3.loc[t, "acc_drop"].max()), 0.0)),
                xytext=(0, 5), textcoords="offset points", ha="center", va="bottom",
                fontsize=11.5, color=ACCENT if t == "PRAD" else "0.3",
                fontweight="bold" if t == "PRAD" else "normal")
# The IDC caveat lives in the notes panel; here it would sit on the PRAD label.
ax.set_xticks(range(len(TASKS)))
ax.set_xticklabels(TASKS)
ax.set_ylabel("Accuracy removed")
ax.set_ylim(0, 0.42)
ax.text(0.5, 1.02, "how much of the signature is\ntissue composition",
        transform=ax.transAxes, ha="center", va="bottom", fontsize=12,
        fontweight="bold", color="0.2")

# ------------------------------------------------------ right: variance in y
ax = axes[2]
tot = PV[[c for c, _, _ in COMPS]].sum().sum()
fr = {c: float(PV[c].sum() / tot) for c, _, _ in COMPS}
left = 0.0
for c, lab, col in COMPS:
    ax.barh(0, fr[c], left=left, height=0.55, color=col, edgecolor="white", lw=0.8, zorder=3)
    # Only the widest segment can hold its label inside; the other two are
    # labelled below the bar with a leader, because white text on a 0.24-wide
    # segment was clipped.
    if fr[c] > 0.5:
        ax.annotate(f"{lab}  {fr[c] * 100:.1f}%", xy=(left + fr[c] / 2, 0),
                    xytext=(0, 0), textcoords="offset points", ha="center", va="center",
                    fontsize=11.5, color="0.15")
    else:
        # Staggered depths: both labels centred at the same depth overlapped,
        # since the two segments are adjacent and the labels are wider than them.
        depth = -0.30 if c == "between_slide_within_session" else -1.00
        # Right-anchored: centred under a segment at x>0.95 the text ran past the
        # panel into the notes column.
        ax.annotate(f"{lab.replace(chr(10), ' ')}  {fr[c] * 100:.1f}%",
                    xy=(min(left + fr[c] / 2, 0.99), depth), xytext=(0, -6),
                    textcoords="offset points", ha="right", va="top", fontsize=11,
                    color=ACCENT if c == "between_session" else "0.3",
                    fontweight="bold" if c == "between_session" else "normal",
                    arrowprops=dict(arrowstyle="-", color="0.6", lw=0.8,
                                    shrinkA=0, shrinkB=2))
    left += fr[c]
n_le0 = int((PV.between_session_raw <= 0).sum())
ax.set_xlim(0, 1)
ax.set_ylim(-1.55, 0.55)
ax.set_yticks([])
ax.set_xlabel("Share of expression variance")
ax.xaxis.set_label_coords(0.5, -0.24)
ax.spines["left"].set_visible(False)
ax.text(0.5, 1.02, "the same session axis, in the\nexpression it is meant to predict",
        transform=ax.transAxes, ha="center", va="bottom", fontsize=12,
        fontweight="bold", color="0.2")

axn = fig.add_subplot(gs[1, 1])
axn.axis("off")
axn.set_xticks([])
axn.set_yticks([])
notes = [
    f"IDC drops {means['IDC'] * 100:.1f}%, not the 17-27% the other three",
    "cross-patient tasks give -- it is also the only",
    "task here with a same-donor replicate pair.",
    "",
    "The dotted 0.71 is the majority-class baseline",
    "for the resolution probe: 5 slides in one class,",
    "2 in the other. Its withdrawn first version",
    "scored exactly that.",
]  # the between-session gene count is in the footnote; two more lines here
   # pushed the block past the bottom of its panel
# One multi-line text rather than a line-per-text loop: matplotlib spaces the
# lines from the font metrics, so the spacing does not have to be re-tuned to
# the panel height every time a line is added or the layout changes.
axn.text(0.0, 0.99, "\n".join(notes), fontsize=11, color="0.35",
         transform=axn.transAxes, va="top", ha="left", linespacing=1.32)

handles = [plt.Rectangle((0, 0), 1, 1, fc=ENCODER_COLOUR[e], ec="white")
           for e in ENC]
# In the morphology panel's upper left, which is empty -- PRAD and IDC barely
# rise off the axis. Inside the probe panel it sat on bars reaching 0.95, and in
# the band between the rows it sat on the probe panel's tick labels.
axes[1].legend(handles, [PRETTY.get(e, e) for e in ENC], loc="upper left",
               bbox_to_anchor=(0.0, 1.0), ncol=1, frameon=False, fontsize=11.5,
               handletextpad=0.6, labelspacing=0.85)

footnote(fig, f"Left and middle: spatial-block cross-validation on PCA-256 features, so a "
              f"held-out patch's neighbours are not in training. Middle regresses eight "
              f"nuclear-morphology covariates out of each feature, fitted on training spots only; "
              f"bars are per encoder, the annotated figures are means over the three. Right: PRAD "
              f"patient 2 only, variance summed over the 50 target genes, method-of-moments "
              f"components -- the raw between-session estimate is at or below zero for {n_le0} of "
              f"{len(PV)} genes.")
fig.subplots_adjust(left=0.068, right=0.992, top=0.865, bottom=0.095)
save(fig, "fig06_session_signature")

sl = P4[P4.probe == "probe1_slide_within_patient"]
print(f"slide identity {sl.acc_blocked.min():.3f}-{sl.acc_blocked.max():.3f} "
      f"(chance {sl.chance.iloc[0]:.4f})")
ss = P4[P4.probe == "probe1b_scan_subcluster"]
print(f"session {ss.acc_blocked.min():.3f}-{ss.acc_blocked.max():.3f}")
r2_ = P4[P4.probe == "probe2_2class"]
print(f"resolution class {r2_.acc_pooled_balanced.min():.3f}-{r2_.acc_pooled_balanced.max():.3f} "
      f"(majority-class baseline {r2_.majority_class_baseline.iloc[0]:.4f})")
print(f"within-session share of slide-probe errors: "
      f"{sl.confusion_within_subcluster_frac.min():.3f}-"
      f"{sl.confusion_within_subcluster_frac.max():.3f} "
      f"against {sl.confusion_within_subcluster_chance.iloc[0]:.3f} at chance")
print("morphology drop, task means: " + "  ".join(f"{t} {means[t] * 100:.1f}%" for t in TASKS))
print("variance shares: " + "  ".join(f"{c} {fr[c] * 100:.1f}%" for c, _, _ in COMPS))
