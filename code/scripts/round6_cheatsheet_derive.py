"""Round 6 cheatsheet track, C0.3: derived inputs computed in the container.

The packaging job's axis check found no overlapping neighbour pairs, because
its cut-off excluded neighbours exactly 200 patch pixels (100 um) apart, which
is the grid spacing, and so it kept the stored order of the coordinate
columns. Rerun here with the cut-off at the patch width, the check shows that
the stored column 1 is the image's x axis (flag F16). This script records the
check and rebuilds, in the image frame, what depends on it:

  PRIVATE/derived/axes.json        which stored column is image x and image y,
                                   with the check's numbers
  PRIVATE/derived/S1_overview.png  the patch mosaic in the image frame
  PRIVATE/derived/overview.json    its origin and scale, in image-frame um

The blocks, held-out flags, eligibility and S1* of the package are unchanged:
the 4 by 4 grid over the bounding box is the same set of rectangles whichever
axis is called x, and the checkerboard parity i + j does not change when i and
j swap. The package's own S1_overview.png is not used.

    python round6_cheatsheet_derive.py [--private /srv/r6_private] --out DIR
"""
import argparse
import json
import os

import numpy as np
import pandas as pd
from PIL import Image

PATCH_UM = 112.0
LONG_SIDE = 1500


def overlap_check(xy, barcodes, patch_dir, n=300, seed=1):
    rng = np.random.default_rng(seed)
    res = {}
    for name, (cx, cy) in (("stored_col0_is_x", (0, 1)), ("stored_col1_is_x", (1, 0))):
        diffs = []
        for a in rng.permutation(len(xy))[:n]:
            d = np.hypot(*(xy - xy[a]).T)
            d[a] = np.inf
            b = int(np.argmin(d))
            dx = int(round((xy[b, cx] - xy[a, cx]) / 0.5))
            dy = int(round((xy[b, cy] - xy[a, cy]) / 0.5))
            if abs(dx) >= 224 or abs(dy) >= 224:
                continue
            A = np.asarray(Image.open(os.path.join(patch_dir, f"{barcodes[a]}.png"))).astype(np.int16)
            B = np.asarray(Image.open(os.path.join(patch_dir, f"{barcodes[b]}.png"))).astype(np.int16)
            ya, xa, yb, xb = max(0, dy), max(0, dx), max(0, -dy), max(0, -dx)
            h, w = 224 - abs(dy), 224 - abs(dx)
            diffs.append(float(np.abs(A[ya:ya + h, xa:xa + w] - B[yb:yb + h, xb:xb + w]).mean()))
        res[name] = {"mean_abs_diff": float(np.mean(diffs)) if diffs else None, "pairs": len(diffs)}
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--private", default="/srv/r6_private")
    ap.add_argument("--out", required=True, help="committed copy of axes.json and overview.json")
    a = ap.parse_args()
    pkg = os.path.join(a.private, "package")
    der = os.path.join(a.private, "derived")
    os.makedirs(der, exist_ok=True)
    os.makedirs(a.out, exist_ok=True)
    s1 = pd.read_parquet(os.path.join(pkg, "S1_spots.parquet"))
    patch_dir = os.path.join(a.private, "patches", "S1")
    xy = s1[["x_um", "y_um"]].to_numpy()
    chk = overlap_check(xy, s1["barcode"].tolist(), patch_dir)
    swap = chk["stored_col1_is_x"]["mean_abs_diff"] < chk["stored_col0_is_x"]["mean_abs_diff"]
    xcol, ycol = ("y_um", "x_um") if swap else ("x_um", "y_um")
    xi, yi = s1[xcol].to_numpy(), s1[ycol].to_numpy()
    nn = []
    for k in range(len(xi)):
        d = np.hypot(xi - xi[k], yi - yi[k])
        d[k] = np.inf
        nn.append(d.min())
    axes = {"image_x_column": xcol, "image_y_column": ycol, "swapped_relative_to_package": bool(swap),
            "check": chk, "nn_spacing_um_min": float(np.min(nn)), "nn_spacing_um_median": float(np.median(nn))}
    # the mosaic in the image frame
    x0, y0, x1, y1 = xi.min(), yi.min(), xi.max(), yi.max()
    half = PATCH_UM / 2
    ox, oy = x0 - half, y0 - half
    w_um, h_um = x1 - x0 + PATCH_UM, y1 - y0 + PATCH_UM
    um_per_px = max(w_um, h_um) / LONG_SIDE
    W, H = int(np.ceil(w_um / um_per_px)), int(np.ceil(h_um / um_per_px))
    side = max(1, int(round(PATCH_UM / um_per_px)))
    canvas = Image.new("RGB", (W, H), (255, 255, 255))
    for bc, x, y in zip(s1["barcode"], xi, yi):
        tile = Image.open(os.path.join(patch_dir, f"{bc}.png")).convert("RGB").resize((side, side), Image.BILINEAR)
        canvas.paste(tile, (int(round((x - half - ox) / um_per_px)), int(round((y - half - oy) / um_per_px))))
    canvas.save(os.path.join(der, "S1_overview.png"))
    frame = {"origin_x_um": float(ox), "origin_y_um": float(oy), "um_per_px": float(um_per_px), "width_px": W,
             "height_px": H, "patch_side_px": side, "bbox_image_um": [float(x0), float(y0), float(x1), float(y1)],
             "built_from": "mosaic of S1 benchmark patches, image frame, built in the container"}
    for name, obj in (("axes.json", axes), ("overview.json", frame)):
        json.dump(obj, open(os.path.join(der, name), "w"), indent=1)
        json.dump(obj, open(os.path.join(a.out, name), "w"), indent=1)
    print(json.dumps(axes, indent=1))
    print(json.dumps(frame, indent=1))


if __name__ == "__main__":
    main()
