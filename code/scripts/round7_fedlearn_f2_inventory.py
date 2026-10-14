#!/usr/bin/env python
"""Round 7 federated learning track, F2 step 4: read-only inventory of the data on disk.

Stage F2 step 4 of docs/round07/i01/fedlearn/round07_fedlearn_track.md, submitted in F0.

WHAT IT READS. File names and sizes under the Longleaf project tree, and the headers of
expression (.h5ad), embedding and patch (.h5) files, that is their dataset shapes and nothing
else. No array is loaded. It also reads three kinds of committed table from the track's code
clone: results/round3/D0_inventory/hest_inventory.csv (organ, technology, disease, provisional
lab and donor key per sample) and the task definitions under results/round3/task_defs/,
results/round3/D4_expansion/task_defs/ and results/round4/data/P5_task/ (task membership, donor
and lab per sample).

WHAT IT WRITES, into its working directory, which is its stamped output directory
results/round7/fedlearn/F2_inventory/ in the project tree, in this order (summaries first):
  inventory_summary.json   counts, the walk's completeness and the run's checks
  centers_by_group.csv     one row per organ and technology on disk, with the labs and donors
                           on disk and whether two or more centers could be formed
  inventory.csv            one row per sample on disk
  file_listing.csv         one row per file under the walked roots (path, size, kind, header)
  PROVENANCE.txt, _provenance.json

It never writes outside its working directory and never runs git except a read-only
`git --no-optional-locks rev-parse HEAD` on the code clone, inside write_provenance.
"""
import argparse
import csv
import glob
import json
import os
import sys
import time

import h5py
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import round7_fedlearn_common as C  # noqa: E402

EXCLUDE_TOP = {"env", ".git", "code"}
DATA_ROOTS = ("bench_data", "embeddings", "embeddings_ext", "hest_ext")
TASK_DEF_GLOBS = (
    "results/round3/task_defs/*.json",
    "results/round3/D4_expansion/task_defs/*.json",
    "results/round4/data/P5_task/*.json",
)


def classify(rel):
    """Kind, set and encoder of a file from its path relative to the project tree."""
    parts = rel.split("/")
    ext = os.path.splitext(rel)[1].lower()
    top = parts[0]
    set_ = parts[1] if len(parts) > 2 and top in DATA_ROOTS else ""
    if top in ("embeddings", "embeddings_ext") and ext == ".h5" and len(parts) >= 4:
        return "embedding", set_, parts[-2]
    if ext == ".h5ad" and top in DATA_ROOTS:
        return "expression", set_, ""
    if "patches" in parts[:-1] and ext == ".h5" and top in DATA_ROOTS:
        return "patches", set_, ""
    if "cellvit_seg" in parts[:-1] and top in DATA_ROOTS:
        return "segmentation", set_, ""
    if "metadata" in parts[:-1] and top in DATA_ROOTS:
        return "metadata", set_, ""
    return "other", set_, ""


def h5ad_shape(path):
    with h5py.File(path, "r") as f:
        def index_len(g):
            if isinstance(g, h5py.Dataset):  # pre-0.7 anndata layout, obs and var as one table
                return int(g.shape[0])
            key = g.attrs.get("_index", "_index")
            if isinstance(key, bytes):
                key = key.decode()
            return int(g[key].shape[0])
        n_obs = index_len(f["obs"])
        n_var = index_len(f["var"])
    return n_obs, n_var


def h5_shape(path, keys):
    with h5py.File(path, "r") as f:
        for k in keys:
            if k in f:
                s = f[k].shape
                return int(s[0]), (int(s[1]) if len(s) > 1 else None), k
        return None, None, ",".join(sorted(f.keys()))


def walk(root, deadline):
    rows, complete = [], True
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        if rel_dir == ".":
            dirnames[:] = sorted(d for d in dirnames if d not in EXCLUDE_TOP)
        else:
            dirnames.sort()
        for fn in sorted(filenames):
            p = os.path.join(dirpath, fn)
            rel = os.path.relpath(p, root)
            try:
                size = os.lstat(p).st_size
            except OSError:
                size = -1
            rows.append((rel, size))
        if time.time() > deadline:
            complete = False
            break
    return rows, complete


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame-id", required=True)
    ap.add_argument("--root", default=C.ROOT)
    ap.add_argument("--clone", default=C.CLONE)
    ap.add_argument("--cap-minutes", type=float, default=45.0)
    a = ap.parse_args()

    out = os.getcwd()
    C.stamp_dir(out, a.frame_id, note="round 7 fedlearn F2 inventory (read-only listing and headers)")
    t0 = time.time()
    config = dict(root=a.root, clone=a.clone, exclude_top=sorted(EXCLUDE_TOP), data_roots=list(DATA_ROOTS),
                  task_def_globs=list(TASK_DEF_GLOBS), cap_minutes=a.cap_minutes,
                  inventory="results/round3/D0_inventory/hest_inventory.csv")

    inv = pd.read_csv(os.path.join(a.clone, config["inventory"]), dtype=str, keep_default_na=False)
    ids = set(inv["id"])

    # Task definitions: membership, donor and lab per sample.
    task_rows = []
    for g in TASK_DEF_GLOBS:
        for p in sorted(glob.glob(os.path.join(a.clone, g))):
            try:
                d = json.load(open(p))
            except Exception:
                continue
            if not isinstance(d, dict) or "samples" not in d or "task" not in d:
                continue
            name = os.path.splitext(os.path.basename(p))[0]
            for s in d["samples"]:
                task_rows.append(dict(task_file=os.path.relpath(p, a.clone), task=name,
                                      sample_id=str(s.get("sample_id", "")), task_donor=str(s.get("donor_id") or ""),
                                      task_lab=str(s.get("lab") or "")))
    T = pd.DataFrame(task_rows, columns=["task_file", "task", "sample_id", "task_donor", "task_lab"])

    # Walk the tree and read headers.
    files, complete = walk(a.root, t0 + 60 * a.cap_minutes)
    L = []
    for rel, size in files:
        kind, set_, enc = classify(rel)
        stem = os.path.basename(rel).split(".")[0]
        sid = stem if stem in ids else ""
        n_rows = n_cols = None
        header = err = ""
        if sid and kind in ("expression", "embedding", "patches"):
            try:
                if kind == "expression":
                    n_rows, n_cols = h5ad_shape(os.path.join(a.root, rel))
                    header = "obs,var"
                elif kind == "embedding":
                    n_rows, n_cols, header = h5_shape(os.path.join(a.root, rel), ["embeddings"])
                else:
                    n_rows, n_cols, header = h5_shape(os.path.join(a.root, rel), ["barcodes", "img"])
            except Exception as e:
                err = f"{type(e).__name__}: {e}"[:200]
        L.append(dict(path=rel, size_bytes=size, kind=kind, sample_id=sid, set=set_, encoder=enc,
                      n_rows=n_rows, n_cols=n_cols, header_key=header, header_error=err))
    L = pd.DataFrame(L, columns=["path", "size_bytes", "kind", "sample_id", "set", "encoder", "n_rows",
                                 "n_cols", "header_key", "header_error"])
    L["n_rows"] = L["n_rows"].astype("Int64")
    L["n_cols"] = L["n_cols"].astype("Int64")

    # One row per sample on disk (a sample is on disk if any expression, embedding or patch file names it).
    S = L[(L.sample_id != "") & L.kind.isin(["expression", "embedding", "patches"])]
    meta_cols = ["id", "organ", "species", "st_technology", "oncotree_code", "disease_state", "dataset_title",
                 "lab_provisional", "lab_basis", "donor_key_provisional", "patient_label_status", "in_benchmark",
                 "benchmark_task", "spots_under_tissue", "nb_genes"]
    rows = []
    for sid, g in S.groupby("sample_id", sort=True):
        e = g[g.kind == "expression"]
        m = g[g.kind == "embedding"]
        p = g[g.kind == "patches"]
        t = T[T.sample_id == sid]
        encs = sorted(set(m.encoder))
        emb_sets = sorted(set(m["set"]))
        n_spots = sorted(set(int(x) for x in e.n_rows.dropna()))
        n_genes = sorted(set(int(x) for x in e.n_cols.dropna()))
        n_emb = sorted(set(int(x) for x in m.n_rows.dropna()))
        rows.append(dict(
            sample_id=sid,
            expression_sets=";".join(sorted(set(e["set"]))), n_expression_files=len(e),
            n_spots_expression=";".join(map(str, n_spots)), n_genes_expression=";".join(map(str, n_genes)),
            patch_sets=";".join(sorted(set(p["set"]))),
            n_patches=";".join(map(str, sorted(set(int(x) for x in p.n_rows.dropna())))),
            encoders_with_embeddings=";".join(encs), n_encoders=len(encs), embedding_sets=";".join(emb_sets),
            n_spots_embedding=";".join(map(str, n_emb)),
            tasks=";".join(sorted(set(t.task))), task_donor=";".join(sorted(set(t.task_donor) - {""})),
            task_lab=" | ".join(sorted(set(t.task_lab) - {""})),
            header_errors=int((g.header_error != "").sum()),
        ))
    I = pd.DataFrame(rows)
    M = inv[meta_cols].rename(columns={"id": "sample_id"})
    I = M.merge(I, on="sample_id", how="right", validate="one_to_one")
    I["has_expression"] = I["n_expression_files"] > 0
    I["has_embeddings"] = I["n_encoders"] > 0
    lead = ["sample_id", "organ", "st_technology", "lab_provisional", "donor_key_provisional", "task_donor",
            "tasks", "encoders_with_embeddings", "n_spots_expression", "n_genes_expression", "has_expression",
            "has_embeddings"]
    I = I[lead + [c for c in I.columns if c not in lead]]

    # One row per organ and technology.
    G = []
    for (organ, tech), g in I.groupby(["organ", "st_technology"], sort=True):
        ge = g[g.has_expression]
        gee = ge[ge.has_embeddings]
        labs_e = ge.lab_provisional.replace("", "(unresolved)")
        labs_ee = gee.lab_provisional.replace("", "(unresolved)")
        def donors(x):
            d = set(x.donor_key_provisional) - {""}
            return len(d)
        lab_detail = "; ".join(
            f"{lab} (samples={len(h)}, with_embeddings={int(h.has_embeddings.sum())}, donors={donors(h)})"
            for lab, h in ge.assign(_lab=labs_e).groupby("_lab", sort=True))
        resolved_e = sorted(set(labs_e) - {"(unresolved)"})
        resolved_ee = sorted(set(labs_ee) - {"(unresolved)"})
        common = None
        for lab, h in gee.groupby("lab_provisional"):
            if lab == "":
                continue
            s = set()
            for v in h.encoders_with_embeddings:
                s |= set(v.split(";")) if v else set()
            common = s if common is None else (common & s)
        G.append(dict(
            organ=organ, st_technology=tech, n_samples_on_disk=len(g), n_samples_with_expression=len(ge),
            n_samples_with_expression_and_embeddings=len(gee),
            n_labs_with_expression=len(resolved_e), n_labs_with_expression_and_embeddings=len(resolved_ee),
            n_donor_keys_with_expression=donors(ge), n_samples_unresolved_lab=int((labs_e == "(unresolved)").sum()),
            two_plus_labs_with_expression=len(resolved_e) >= 2,
            two_plus_labs_with_expression_and_embeddings=len(resolved_ee) >= 2,
            encoders_common_to_labs=";".join(sorted(common)) if common else "",
            tasks=";".join(sorted({t for v in g.tasks for t in v.split(";") if t})),
            labs=lab_detail,
        ))
    G = pd.DataFrame(G)

    checks = dict(
        n_files_listed=int(len(L)), walk_complete=bool(complete),
        n_samples_on_disk=int(len(I)), n_samples_with_expression=int(I.has_expression.sum()),
        n_samples_with_embeddings=int(I.has_embeddings.sum()),
        n_benchmark_samples_on_disk=int((I.in_benchmark == "True").sum()),
        n_header_errors=int((L.header_error != "").sum()),
        n_groups=int(len(G)), n_groups_two_plus_labs_with_expression=int(G.two_plus_labs_with_expression.sum()),
        n_groups_two_plus_labs_with_expression_and_embeddings=int(G.two_plus_labs_with_expression_and_embeddings.sum()),
        all_sample_ids_in_inventory=bool(set(I.sample_id) <= ids),
        n_task_def_files=int(T.task_file.nunique()), n_task_rows=int(len(T)),
        n_task_samples_not_on_disk=int(len(set(T.sample_id) - set(I.sample_id))),
        wall_seconds=round(time.time() - t0, 1),
    )
    json.dump(dict(config=config, checks=checks), open("inventory_summary.json", "w"), indent=2)
    G.to_csv("centers_by_group.csv", index=False, quoting=csv.QUOTE_MINIMAL)
    I.to_csv("inventory.csv", index=False)
    L.to_csv("file_listing.csv", index=False)

    cmd = " ".join([sys.executable] + sys.argv)
    C.write_provenance(out, "F2 step 4 (submitted in F0)", a.frame_id, cmd, config, [os.path.abspath(__file__), C.__file__],
                       extra=dict(walk_complete=complete, outputs="inventory_summary.json centers_by_group.csv inventory.csv file_listing.csv"))
    print(json.dumps(checks, indent=1), flush=True)


if __name__ == "__main__":
    main()
