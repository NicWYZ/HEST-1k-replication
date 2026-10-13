"""Round 6 extension, cheatsheet track: build one trial directory (instruction 6.1, 6.2).

Runs in the container, from the package in /private/package. Every directory
is blinded. Nothing in it or in its path names a sample, dataset, patient,
study or the source collection. The orders that give patients and spots
their labels are drawn with seeds keyed on the trial ID, and the mapping back
is written to /private/maps/<trial_id>.json, outside every trial directory.

  writer      patches/<sid>.png (3,500), spots.csv, expression.csv,
              overviews/<label>.png, RULES.md, check_cheatsheet.py, genes.txt
  checker     cheatsheet.txt, RULES.md, genes.txt
  predictor   patches/{a,b,c}/<pid>.png (1,500), genes.txt, cheatsheet.txt
  baseline    as predictor, without cheatsheet.txt
  combined    labelled/ as a writer's directory without RULES.md and
              check_cheatsheet.py, target/ as a baseline's directory

Positions in spots.csv are the spot's centre in pixels at 0.5 micrometres per
pixel, the scale of the patches, measured from the top-left corner of that
patient's overview image. Expression is written to 4 decimals.

    python round6_cheatsheet_ext_build.py ROLE [--size B] [--cheatsheet FILE] [--trial-id ID]
"""
import argparse
import csv
import json
import os
import secrets
import shutil
import sys
import tarfile
import zlib

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import round6_cheatsheet_ext_prompts as PR  # noqa: E402

PRIVATE = "/private"
PACKAGE = os.path.join(PRIVATE, "package")
PATCHES = os.path.join(PRIVATE, "patches")   # the package's tars, unpacked once
MAPS = os.path.join(PRIVATE, "maps")
TRIALS = "/trials"
PATCH_UM_PER_PX = 0.5
WRITER_DOC = '''"""Mechanical check of cheatsheet.txt.

    python3 check_cheatsheet.py

Reads cheatsheet.txt and genes.txt in the current directory and reports the
size and possible problems, with line numbers. A flag from this script is a
warning, not a verdict. An independent reviewer decides whether the file
follows RULES.md.
"""'''


def seed_of(key):
    return zlib.crc32(key.encode())


def int_key(sid):
    return int(sid[3:])


def new_trial_id():
    while True:
        tid = secrets.token_hex(4)
        if not os.path.exists(os.path.join(TRIALS, tid)):
            return tid


def package():
    genes = json.load(open(os.path.join(PACKAGE, "genes.json")))["genes"]
    draws = json.load(open(os.path.join(PACKAGE, "draws.json")))
    frames = json.load(open(os.path.join(PACKAGE, "overview.json")))
    return genes, draws, frames


def unpack_patches():
    """Unpack each slide's tar of sampled patches into /private/patches/<sample>/, once."""
    _, draws, _ = package()
    for sid in draws["slides"]:
        d = os.path.join(PATCHES, sid)
        if os.path.isdir(d) and len(os.listdir(d)) == 500:
            continue
        os.makedirs(d, exist_ok=True)
        with tarfile.open(os.path.join(PACKAGE, f"{sid}_patches.tar")) as tf:
            for m in tf.getmembers():
                assert m.isfile() and "/" not in m.name and m.name.endswith(".png"), m.name
                with open(os.path.join(d, m.name), "wb") as fh:
                    fh.write(tf.extractfile(m).read())
        assert len(os.listdir(d)) == 500, sid


def sampled(sid, genes):
    spots = pd.read_parquet(os.path.join(PACKAGE, f"{sid}_spots.parquet"))
    target = pd.read_parquet(os.path.join(PACKAGE, f"{sid}_target.parquet"))
    assert list(spots["barcode"]) == list(target["barcode"])
    m = spots["sampled"].to_numpy(dtype=bool)
    s = spots[m].merge(target[m], on="barcode").sort_values("barcode").reset_index(drop=True)
    assert len(s) == 500
    return s


def labelled(root, tid, genes, draws, frames):
    """The writer's data files under root. Returns the mapping."""
    train = sorted(draws["train"], key=int_key)
    order = np.random.default_rng(seed_of(f"round6ext-patientorder-{tid}")).permutation(len(train))
    label = {train[j]: f"P{k + 1}" for k, j in enumerate(order)}
    rows = [(sid, r) for sid in train for _, r in sampled(sid, genes).iterrows()]
    perm = np.random.default_rng(seed_of(f"round6ext-spotorder-{tid}")).permutation(len(rows))
    os.makedirs(os.path.join(root, "patches"))
    os.makedirs(os.path.join(root, "overviews"))
    spot_map, srows, erows = {}, [], []
    for k, j in enumerate(perm):
        sid, r = rows[j]
        spot = f"s{k + 1:04d}"
        f = frames[sid]
        x = (r["x_um"] - f["origin_x_um"]) / PATCH_UM_PER_PX
        y = (r["y_um"] - f["origin_y_um"]) / PATCH_UM_PER_PX
        shutil.copyfile(os.path.join(PATCHES, sid, f"{r['barcode']}.png"), os.path.join(root, "patches", f"{spot}.png"))
        srows.append([spot, label[sid], int(round(x)), int(round(y))])
        erows.append([spot] + [f"{float(r[g]):.4f}" for g in genes])
        spot_map[spot] = [sid, r["barcode"]]
    with open(os.path.join(root, "spots.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["spot_id", "patient", "x", "y"])
        w.writerows(srows)
    with open(os.path.join(root, "expression.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["spot_id"] + genes)
        w.writerows(erows)
    for sid, lab in label.items():
        shutil.copyfile(os.path.join(PACKAGE, f"{sid}_overview.png"), os.path.join(root, "overviews", f"{lab}.png"))
    return {"patients": {v: k for k, v in label.items()}, "spots": spot_map}


def target(root, tid, genes, draws):
    """The predictor's data files under root. Returns the mapping."""
    test = sorted(draws["test"], key=int_key)
    order = np.random.default_rng(seed_of(f"round6ext-patientorder-{tid}-test")).permutation(len(test))
    folder = {test[j]: "abc"[k] for k, j in enumerate(order)}
    rows = [(sid, r["barcode"]) for sid in test for _, r in sampled(sid, genes).iterrows()]
    perm = np.random.default_rng(seed_of(f"round6ext-spotorder-{tid}-test")).permutation(len(rows))
    for f in "abc":
        os.makedirs(os.path.join(root, "patches", f))
    spot_map = {}
    for k, j in enumerate(perm):
        sid, bc = rows[j]
        pid = f"p{k + 1:04d}"
        shutil.copyfile(os.path.join(PATCHES, sid, f"{bc}.png"), os.path.join(root, "patches", folder[sid], f"{pid}.png"))
        spot_map[pid] = [sid, bc]
    write_genes(root, genes)
    return {"folders": {v: k for k, v in folder.items()}, "spots": spot_map}


def write_genes(root, genes):
    with open(os.path.join(root, "genes.txt"), "w") as fh:
        fh.write("\n".join(genes) + "\n")


def write_check(root, b):
    src = open(os.path.join(HERE, "round6_cheatsheet_ext_check_cheatsheet.py")).read()
    line = "B = None  # the allowed size in bytes, written in by the harness"
    assert src.count(line) == 1
    # the writer's copy carries a neutral docstring, with nothing about the project or the harness
    tail = src.split('"""', 2)[2]
    with open(os.path.join(root, "check_cheatsheet.py"), "w") as fh:
        fh.write(WRITER_DOC + tail.replace(line, f"B = {int(b)}  # the allowed size in bytes"))


def build(role, size=None, cheatsheet=None, trial_id=None):
    genes, draws, frames = package()
    unpack_patches()
    tid = trial_id or new_trial_id()
    root = os.path.join(TRIALS, tid)
    os.makedirs(root, exist_ok=False)
    mapping = {"trial_id": tid, "role": role, "size": size}
    if role == "writer":
        mapping["labelled"] = labelled(root, tid, genes, draws, frames)
        write_genes(root, genes)
        open(os.path.join(root, "RULES.md"), "w").write(PR.RULES_MD)
        write_check(root, size)
    elif role == "checker":
        shutil.copyfile(cheatsheet, os.path.join(root, "cheatsheet.txt"))
        open(os.path.join(root, "RULES.md"), "w").write(PR.RULES_MD)
        write_genes(root, genes)
    elif role in ("predictor", "baseline"):
        mapping["target"] = target(root, tid, genes, draws)
        if role == "predictor":
            shutil.copyfile(cheatsheet, os.path.join(root, "cheatsheet.txt"))
    elif role == "combined":
        os.makedirs(os.path.join(root, "labelled"))
        os.makedirs(os.path.join(root, "target"))
        mapping["labelled"] = labelled(os.path.join(root, "labelled"), tid, genes, draws, frames)
        write_genes(os.path.join(root, "labelled"), genes)
        mapping["target"] = target(os.path.join(root, "target"), tid, genes, draws)
    else:
        raise ValueError(role)
    os.makedirs(MAPS, exist_ok=True)
    json.dump(mapping, open(os.path.join(MAPS, f"{tid}.json"), "w"))
    return tid, root


def truth_for(tid):
    """Measured target of a predictor's spots: frame indexed by pid, and the slide of each."""
    genes, _, _ = package()
    m = json.load(open(os.path.join(MAPS, f"{tid}.json")))["target"]["spots"]
    by_slide = {}
    for pid, (sid, bc) in m.items():
        by_slide.setdefault(sid, []).append((pid, bc))
    parts = []
    for sid, items in by_slide.items():
        t = pd.read_parquet(os.path.join(PACKAGE, f"{sid}_target.parquet")).set_index("barcode")
        f = t.loc[[bc for _, bc in items], genes]
        f.index = [pid for pid, _ in items]
        parts.append(f.assign(_slide=sid))
    allp = pd.concat(parts).sort_index()
    return allp[genes], allp["_slide"].to_numpy(), genes


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("role", choices=["writer", "checker", "predictor", "baseline", "combined"])
    ap.add_argument("--size", type=int, default=None)
    ap.add_argument("--cheatsheet", default=None)
    ap.add_argument("--trial-id", default=None)
    a = ap.parse_args()
    print(json.dumps(dict(zip(("trial_id", "dir"), build(a.role, a.size, a.cheatsheet, a.trial_id)))))
