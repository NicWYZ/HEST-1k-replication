"""Shared style and helpers for the deck figures.

Stage: deck rendering (deck_figures_and_repo_update.md Part 1).
Inputs: none -- this module only configures matplotlib and resolves paths.
Outputs: none directly; `save()` writes PNG + PDF into figures/deck/.

The deck rules this module enforces, from the instruction's section 1.1:

  * width 10 in; height 5.6 in, or 4.2 in for half-height panels
  * 300 dpi PNG *and* PDF
  * no font below 11 pt at that size
  * no title baked into the figure -- the slide carries the title
  * one accent colour for the quantity of interest, grey for reference
  * one fixed colour per encoder, identical across every figure

Every script that imports this reads only CSVs already committed in the
repository. Nothing here reads a session artifact, and no annotated number is
typed into a script: each is pulled from the source table at render time, so a
figure cannot drift from the file it claims to plot.

HEST_ROOT lets the same script run against a local checkout during development
and against the repository on Longleaf for the committed output.
"""
from __future__ import annotations

import os
import pathlib

import matplotlib as mpl
import pandas as pd

ROOT = pathlib.Path(os.environ.get("HEST_ROOT", "/work/users/w/e/weiyang/hest_replication"))
OUTDIR = ROOT / "figures" / "deck"

# Geometry. 16:9-friendly: a 10 x 5.6 in figure dropped on a 13.33 x 7.5 in slide
# leaves a title band and even side margins.
FULL = (10.0, 5.6)
HALF = (10.0, 4.2)
DPI = 300

# Colour. ACCENT carries the quantity the slide is about; GREY is always
# reference (a paper value, a chance line, a comparator). Deliberately not a
# red/green pair anywhere -- those are indistinguishable under deuteranopia.
ACCENT = "#C1272D"
GREY = "#7A7A7A"
GREY_LIGHT = "#BDBDBD"
BLUE = "#2E6E8E"
AMBER = "#E8A33D"

# One colour per encoder, used in this order wherever encoders are shown. Fixed
# here rather than per script so fig02, fig05, fig06 and fig07 cannot disagree.
ENCODERS = ["hoptimus0", "uni_v2", "resnet50"]
ENCODER_COLOUR = {"hoptimus0": BLUE, "uni_v2": AMBER, "resnet50": "#6B4C9A"}

# Display names. Axis and legend text uses these, never the codebase key.
PRETTY = {
    "hoptimus0": "H-Optimus-0", "hoptimus1": "H-Optimus-1", "uni_v1": "UNI",
    "uni_v2": "UNI2-h", "virchow": "Virchow", "virchow2": "Virchow2",
    "gigapath": "GigaPath", "conch_v1": "CONCH v1", "conch_v15": "CONCH v1.5",
    "phikon": "Phikon", "ctranspath": "CTransPath", "resnet50": "ResNet50",
}


def apply_deck_style():
    """Three font sizes mapped to role, floor 11 pt. Called by every script."""
    mpl.rcParams.update({
        "figure.dpi": 110,
        "savefig.dpi": DPI,
        "savefig.bbox": "tight",
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial"],
        "font.size": 13,          # axis labels, series identity
        "axes.labelsize": 13,
        # Axis labels sit clear of the tick labels. At the matplotlib default of
        # 4 pt the label's box touched every x tick label's box at 13/11 pt --
        # visually a hairline, but it is the kind of touch that becomes a real
        # collision as soon as a tick label gains a digit.
        "axes.labelpad": 9,
        "axes.titlesize": 13,
        "legend.fontsize": 12,    # legend and annotation
        "xtick.labelsize": 11,    # ticks -- the floor
        "ytick.labelsize": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.edgecolor": "#444444",
        "axes.linewidth": 0.9,
        "axes.grid": False,
        "legend.frameon": False,
        "lines.solid_capstyle": "round",
        "pdf.fonttype": 42,       # embed as TrueType so the PDF text stays editable
        "ps.fonttype": 42,
    })


def read(relpath: str) -> pd.DataFrame:
    """Read a repository CSV by its repo-relative path, failing loudly."""
    p = ROOT / relpath
    if not p.exists():
        raise FileNotFoundError(f"{p} -- deck figures read only committed results")
    return pd.read_csv(p)


def save(fig, name: str) -> dict:
    """Write PNG and PDF, then run the geometric text check and report it."""
    OUTDIR.mkdir(parents=True, exist_ok=True)
    png, pdf = OUTDIR / f"{name}.png", OUTDIR / f"{name}.pdf"
    fig.savefig(png)
    fig.savefig(pdf)
    r = fig.canvas.get_renderer()

    # Tick labels for ticks outside the current axis limits still exist as Text
    # objects with real extents but are never drawn. Counting them produced a
    # phantom "0.8 outside canvas" on a panel whose axis stops at 0.71, so they
    # are excluded here rather than worked around in each script.
    phantom = set()
    for ax in fig.axes:
        for axis, lim in ((ax.xaxis, ax.get_xlim()), (ax.yaxis, ax.get_ylim())):
            lo, hi = sorted(lim)
            # Major and minor are paired separately: zipping labels(which="both")
            # against a concatenated loc list mis-pairs them and mislabels a
            # live tick as phantom (or vice versa).
            for minor in (False, True):
                labels = axis.get_ticklabels(minor=minor)
                locs = axis.get_ticklocs(minor=minor)
                for tick, loc in zip(labels, locs):
                    if not (lo - 1e-9 <= loc <= hi + 1e-9):
                        phantom.add(id(tick))

    # An axes with axison=False (a text-only panel) still carries its tick label
    # Text objects, with real extents, though none of them is drawn. Collected by
    # walking the AXES: a tick label's `.axes` attribute is None in this
    # matplotlib, so the earlier per-text version of this test never fired and
    # the notes panel's default 0.0-1.0 ticks were still being counted.
    hidden = set()
    for ax in fig.axes:
        if not ax.axison:
            for t in (ax.get_xticklabels(which="both")
                      + ax.get_yticklabels(which="both")
                      + [ax.xaxis.label, ax.yaxis.label, ax.title]):
                hidden.add(id(t))

    def drawn(t):
        return (bool(t.get_text().strip()) and t.get_visible()
                and id(t) not in phantom and id(t) not in hidden)

    texts = [(t, t.get_window_extent(r)) for t in fig.findobj(mpl.text.Text) if drawn(t)]
    overlaps = [(a.get_text()[:18], b.get_text()[:18])
                for i, (a, ba) in enumerate(texts) for b, bb in texts[i + 1:]
                if ba.overlaps(bb)]
    # Overflow past fig.bbox is measured but is NOT a defect here: savefig runs
    # with bbox_inches="tight", which expands the written canvas to enclose any
    # text hanging outside the figure rectangle, so these are present in the
    # saved PNG and PDF. Reported as "absorbed" for visibility rather than
    # flagged, because chasing it would mean padding margins to fix nothing.
    absorbed = []
    for t, b in texts:
        over = max(0.0, fig.bbox.x0 - b.x0, fig.bbox.y0 - b.y0,
                   b.x1 - fig.bbox.x1, b.y1 - fig.bbox.y1)
        if over > 1.0:
            absorbed.append((t.get_text()[:18], round(over, 1)))
    smallest = min((t.get_fontsize() for t, _ in texts), default=None)
    print(f"[{name}] wrote {png.name} + {pdf.name} | smallest font {smallest} pt "
          f"| text overlaps {len(overlaps)} | tight-bbox absorbed {len(absorbed)}")
    if overlaps:
        print(f"[{name}]   OVERLAPS: {overlaps[:6]}")
    if absorbed:
        print(f"[{name}]   absorbed (in the saved file, not a defect): {absorbed[:4]}")
    assert smallest is None or smallest >= 11, f"{name}: {smallest} pt is below the 11 pt floor"
    return {"png": str(png), "pdf": str(pdf), "overlaps": overlaps,
            "absorbed": absorbed}


def footnote(fig, text: str, y: float = -0.018):
    """A line recording what the panel averages over.

    Anchored just BELOW the figure rectangle on purpose. savefig runs with
    bbox_inches="tight", so the written canvas expands to enclose it and the
    note is in the saved PNG and PDF. Anchoring it inside the rectangle instead
    made its height depend on the line count, and it collided with the x-axis
    label on three of the seven figures at slightly different margins each time
    -- a collision that has to be re-tuned per figure is the wrong fix.
    """
    # va="top" so the block grows DOWNWARD, away from the axes. With va="bottom"
    # its height depended on the line count and a four-line note reached back up
    # into the x-axis label.
    fig.text(0.008, y, text, fontsize=11, color="#555555", va="top", ha="left",
             wrap=True)
