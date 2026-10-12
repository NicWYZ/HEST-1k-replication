"""Round 6 cheatsheet track: build trial directories from the staged package.

The package (C0.3) is staged unblinded at PRIVATE/package. `stage()` unpacks
its patch shards and writes the truth tables of S1* and S2*. `build()` makes
one trial directory under TRIALS/<trial_id> from a manifest row, as
instruction 6.2 lays it out, and keeps the ID mappings under PRIVATE/maps.

Layout of a trial directory
  writer      patches/<sid>.png, spots.csv (spot_id,x,y), expression.csv
              (spot_id + 50 genes), overview.png
  predictor   patches/<pid>.png for the scored spots, genes.txt, cheatsheet.txt
  baseline    patches/<pid>.png, genes.txt
  combined    labelled/ as a writer's directory, target/patches/<pid>.png,
              target/genes.txt

Writers' positions are in pixels of the patches' own scale (0.5 um per pixel),
with the origin at the overview's top-left corner, so that position / f lands
on overview.png for f = overview um_per_px / 0.5 (flag F10). In arm B the
writer sees training-block spots only and the held-out blocks of the overview
are filled with white.
"""
import io
import json
import os
import shutil
import tarfile
import zlib

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw

PRIVATE = os.environ.get("R6_PRIVATE", "/srv/r6_private")  # overridden only for smoke tests
TRIALS = "/srv/r6"
PATCH_PX_UM = 0.5


def seed_of(key):
    return zlib.crc32(key.encode())


class Package:
    def __init__(self, private=PRIVATE):
        self.private = private
        self.pkg = os.path.join(private, "package")
        self.genes = json.load(open(os.path.join(self.pkg, "genes.json")))["genes"]
        self.s1 = pd.read_parquet(os.path.join(self.pkg, "S1_spots.parquet"))
        self.s2 = pd.read_parquet(os.path.join(self.pkg, "S2_spots.parquet"))
        self.t1 = pd.read_parquet(os.path.join(self.pkg, "S1_target.parquet")).set_index("barcode")
        self.t2 = pd.read_parquet(os.path.join(self.pkg, "S2_target.parquet")).set_index("barcode")
        self.frame = json.load(open(os.path.join(self.pkg, "overview.json")))
        self.summary = json.load(open(os.path.join(self.pkg, "package_summary.json")))
        self.patch_dir = {"S1": os.path.join(private, "patches", "S1"), "S2": os.path.join(private, "patches", "S2star")}
        self.star1 = self.s1.loc[self.s1["in_S1star"], "barcode"].tolist()
        self.star2 = self.s2.loc[self.s2["in_S2star"], "barcode"].tolist()

    def writer_spots(self, arm):
        if arm in ("A", "C", "AC"):
            return self.s1
        if arm == "B":
            return self.s1[~self.s1["heldout"]]
        raise ValueError(arm)

    def scored(self, arm):
        if arm in ("A", "B", "AB"):
            return ("S1", self.star1, self.t1)
        if arm == "C":
            return ("S2", self.star2, self.t2)
        raise ValueError(arm)


def stage(private=PRIVATE):
    """Unpack the patch shards and write the S1*/S2* truth tables."""
    pkg = os.path.join(private, "package")
    for prefix, sub in (("S1_patches", "S1"), ("S2star_patches", "S2star")):
        d = os.path.join(private, "patches", sub)
        os.makedirs(d, exist_ok=True)
        for f in sorted(os.listdir(pkg)):
            if f.startswith(prefix) and f.endswith(".tar"):
                with tarfile.open(os.path.join(pkg, f)) as tf:
                    for m in tf.getmembers():
                        assert "/" not in m.name and m.name.endswith(".png"), m.name
                        with open(os.path.join(d, m.name), "wb") as fh:
                            fh.write(tf.extractfile(m).read())
    P = Package(private)
    os.makedirs(os.path.join(private, "truth"), exist_ok=True)
    for name, star, t in (("S1star", P.star1, P.t1), ("S2star", P.star2, P.t2)):
        df = t.loc[star, P.genes].reset_index().rename(columns={"barcode": "spot"})
        df.to_parquet(os.path.join(private, "truth", f"{name}.parquet"), index=False)
    return P


def clean_png(src, dst):
    """Re-encode so that no metadata chunk of the source survives."""
    im = Image.open(src)
    im.load()
    Image.fromarray(np.asarray(im.convert("RGB"))).save(dst, format="PNG")


def overview_for(P, arm, dst):
    im = Image.open(os.path.join(P.pkg, "S1_overview.png")).convert("RGB")
    if arm == "B":  # arm B writers and arm B combined sessions only
        f = P.frame
        x0, y0, x1, y1 = P.summary["S1_bbox_um_xmin_ymin_xmax_ymax"]
        bw, bh = P.summary["S1_block_w_um"], P.summary["S1_block_h_um"]
        draw = ImageDraw.Draw(im)
        for i in range(4):
            for j in range(4):
                if (i + j) % 2 == 1:
                    # the outer blocks are extended to the image border, which the patch
                    # half-width beyond the bounding box would otherwise leave visible
                    lx = 0 if j == 0 else (x0 + j * bw - f["origin_x_um"]) / f["um_per_px"]
                    rx = f["width_px"] if j == 3 else (x0 + (j + 1) * bw - f["origin_x_um"]) / f["um_per_px"]
                    ty = 0 if i == 0 else (y0 + i * bh - f["origin_y_um"]) / f["um_per_px"]
                    by = f["height_px"] if i == 3 else (y0 + (i + 1) * bh - f["origin_y_um"]) / f["um_per_px"]
                    draw.rectangle([int(np.floor(lx)), int(np.floor(ty)), int(np.ceil(rx)), int(np.ceil(by))],
                                   fill=(255, 255, 255))
    Image.fromarray(np.asarray(im)).save(dst, format="PNG")


def build_writer_dir(P, d, arm, trial_id, maps):
    os.makedirs(os.path.join(d, "patches"))
    spots = P.writer_spots(arm)
    order = np.random.default_rng(seed_of(f"round6-writer-order-{trial_id}")).permutation(len(spots))
    sp = spots.iloc[order].reset_index(drop=True)
    sids = [f"s{k + 1:04d}" for k in range(len(sp))]
    f = P.frame
    x = (sp["x_um"].to_numpy() - f["origin_x_um"]) / PATCH_PX_UM
    y = (sp["y_um"].to_numpy() - f["origin_y_um"]) / PATCH_PX_UM
    pd.DataFrame({"spot_id": sids, "x": np.round(x, 1), "y": np.round(y, 1)}).to_csv(
        os.path.join(d, "spots.csv"), index=False)
    ex = P.t1.loc[sp["barcode"], P.genes].copy()
    ex.insert(0, "spot_id", sids)
    ex.to_csv(os.path.join(d, "expression.csv"), index=False, float_format="%.6g")
    for sid, bc in zip(sids, sp["barcode"]):
        clean_png(os.path.join(P.patch_dir["S1"], f"{bc}.png"), os.path.join(d, "patches", f"{sid}.png"))
    overview_for(P, arm, os.path.join(d, "overview.png"))
    maps.append(pd.DataFrame({"trial_id": trial_id, "kind": "writer", "local_id": sids, "slide": "S1",
                              "spot": sp["barcode"].tolist()}))


def build_target_dir(P, d, arm, trial_id, maps, cheatsheet=None):
    os.makedirs(os.path.join(d, "patches"))
    slide, star, _ = P.scored(arm)
    order = np.random.default_rng(seed_of(f"round6-pred-order-{trial_id}")).permutation(len(star))
    spots = [star[k] for k in order]
    pids = [f"p{k + 1:04d}" for k in range(len(spots))]
    for pid, bc in zip(pids, spots):
        clean_png(os.path.join(P.patch_dir[slide], f"{bc}.png"), os.path.join(d, "patches", f"{pid}.png"))
    with open(os.path.join(d, "genes.txt"), "w") as fh:
        fh.write("\n".join(P.genes) + "\n")
    if cheatsheet is not None:
        shutil.copy(cheatsheet, os.path.join(d, "cheatsheet.txt"))
    maps.append(pd.DataFrame({"trial_id": trial_id, "kind": "target", "local_id": pids, "slide": slide,
                              "spot": spots}))


def build(P, row, cheatsheet=None, trials=TRIALS):
    """row: dict with trial_id, role (writer, predictor, baseline, combined), arm."""
    tid, role, arm = row["trial_id"], row["role"], row["arm"]
    d = os.path.join(trials, tid)
    os.makedirs(d)
    maps = []
    if role == "writer":
        build_writer_dir(P, d, arm, tid, maps)
    elif role in ("predictor", "baseline"):
        if role == "predictor":
            assert cheatsheet is not None and os.path.exists(cheatsheet), "predictor needs a cheatsheet"
        build_target_dir(P, d, arm, tid, maps, cheatsheet if role == "predictor" else None)
    elif role == "combined":
        build_writer_dir(P, os.path.join(d, "labelled"), arm, tid, maps)
        build_target_dir(P, os.path.join(d, "target"), arm, tid, maps)
    else:
        raise ValueError(role)
    os.makedirs(os.path.join(P.private, "maps"), exist_ok=True)
    m = pd.concat(maps)
    m.to_csv(os.path.join(P.private, "maps", f"{tid}.csv"), index=False)
    return d, m
