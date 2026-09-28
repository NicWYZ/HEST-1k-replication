"""Round-4 stage P, P2 acceptance: one encoder's embeddings for set L.

Checks, per sample of set L:
  - the embedding file exists under embeddings_ext/lung_xenium/<encoder>/<sample>.h5
  - the patch file exists under hest_ext/lung_xenium/patches/<sample>.h5
  - embedding row count equals patch count
  - the barcode column is readable by the same h5py read the D4 readers use
    (code/scripts/round3_d4_sets.py `patched_barcodes`, and
     code/scripts/round3_d4_layout_anchor.py): key "barcodes" or "barcode",
    reshape(-1), decode bytes, alongside "embeddings" and "coords"
  - the embedding barcode list equals the patch barcode list, in order

usage: round4_data_p2_accept.py --encoder <enc> --config d2_config.json --out-dir .
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import platform

import h5py
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--encoder", required=True)
ap.add_argument("--config", default="d2_config.json")
ap.add_argument("--real-emb-root", required=True)
ap.add_argument("--real-ext-root", required=True)
ap.add_argument("--set", dest="set_name", default="lung_xenium")
ap.add_argument("--out-dir", default=".")
args = ap.parse_args()

CFG = json.load(open(args.config))
MEMBERS = sorted(CFG["sets"][args.set_name]["members"])
OUT = os.path.abspath(args.out_dir)
os.makedirs(OUT, exist_ok=True)


def dec(arr):
    a = np.asarray(arr).reshape(-1)
    return [x.decode() if isinstance(x, (bytes, np.bytes_)) else str(x) for x in a]


FIELDS = ["set", "encoder", "sample_id", "embedding_file", "embedding_present",
          "patch_file_present", "n_patches", "n_embedding_rows", "rows_equal_patches",
          "emb_dim", "n_coords", "barcodes_readable", "barcode_key", "n_barcodes",
          "barcodes_match_patches_in_order", "first_barcode", "dtype", "accepted", "error"]

rows = []
for sid in MEMBERS:
    p_emb = os.path.join(args.real_emb_root, args.set_name, args.encoder, f"{sid}.h5")
    p_pat = os.path.join(args.real_ext_root, args.set_name, "patches", f"{sid}.h5")
    rec = {k: "" for k in FIELDS}
    rec.update({"set": args.set_name, "encoder": args.encoder, "sample_id": sid,
                "embedding_file": p_emb,
                "embedding_present": str(os.path.isfile(p_emb)),
                "patch_file_present": str(os.path.isfile(p_pat)),
                "n_patches": -1, "n_embedding_rows": -1, "emb_dim": -1, "n_coords": -1,
                "n_barcodes": -1})
    try:
        with h5py.File(p_pat, "r") as f:
            k = "img" if "img" in f else ("imgs" if "imgs" in f else "images")
            rec["n_patches"] = int(f[k].shape[0])
            pk = "barcodes" if "barcodes" in f else "barcode"
            pbc = dec(f[pk][:])
        with h5py.File(p_emb, "r") as f:
            k = "barcodes" if "barcodes" in f else "barcode"
            rec["barcode_key"] = k
            bc = dec(f[k][:])
            X = np.asarray(f["embeddings"][:], dtype=np.float32)
            xy = np.asarray(f["coords"][:], dtype=np.float64)
            rec.update({"n_embedding_rows": int(X.shape[0]), "emb_dim": int(X.shape[1]),
                        "n_coords": int(xy.shape[0]), "n_barcodes": len(bc),
                        "barcodes_readable": str(len(bc) == X.shape[0] and all(
                            isinstance(x, str) and x != "" for x in bc)),
                        "first_barcode": bc[0] if bc else "",
                        "dtype": str(f["embeddings"].dtype)})
        rec["rows_equal_patches"] = str(rec["n_embedding_rows"] == rec["n_patches"])
        rec["barcodes_match_patches_in_order"] = str(bc == pbc)
    except Exception as exc:
        rec["error"] = f"{type(exc).__name__}: {exc}"
    rec["accepted"] = str(rec["embedding_present"] == "True"
                          and rec["rows_equal_patches"] == "True"
                          and rec["barcodes_readable"] == "True"
                          and rec["barcodes_match_patches_in_order"] == "True"
                          and not rec["error"])
    rows.append(rec)
    print(f"  {sid} rows {rec['n_embedding_rows']} patches {rec['n_patches']} "
          f"dim {rec['emb_dim']} bc {rec['n_barcodes']} readable {rec['barcodes_readable']} "
          f"order {rec['barcodes_match_patches_in_order']} accepted {rec['accepted']} "
          f"{rec['error']}", flush=True)

n_ok = sum(1 for r in rows if r["accepted"] == "True")
summary = {
    "stage": "round4_P2_acceptance", "set": args.set_name, "encoder": args.encoder,
    "n_samples": len(rows), "n_accepted": n_ok,
    "n_missing_embeddings": sum(1 for r in rows if r["embedding_present"] != "True"),
    "n_rows_ne_patches": sum(1 for r in rows if r["rows_equal_patches"] != "True"),
    "n_barcodes_unreadable": sum(1 for r in rows if r["barcodes_readable"] != "True"),
    "n_barcode_order_mismatch": sum(1 for r in rows
                                    if r["barcodes_match_patches_in_order"] != "True"),
    "samples_not_accepted": [r["sample_id"] for r in rows if r["accepted"] != "True"],
    "total_embedding_rows": sum(r["n_embedding_rows"] for r in rows if r["n_embedding_rows"] > 0),
    "total_patches": sum(r["n_patches"] for r in rows if r["n_patches"] > 0),
    "emb_dims": sorted({r["emb_dim"] for r in rows if r["emb_dim"] > 0}),
    "dtypes": sorted({r["dtype"] for r in rows if r["dtype"]}),
    "reader": "h5py, key barcodes|barcode, reshape(-1), decode; embeddings and coords; "
              "the read round3_d4_sets.patched_barcodes and round3_d4_layout_anchor use",
    "script_md5": hashlib.md5(open(os.path.abspath(__file__), "rb").read()).hexdigest(),
    "slurm_job_id": os.environ.get("SLURM_JOB_ID", "NA"),
    "slurm_partition": os.environ.get("SLURM_JOB_PARTITION", "NA"),
    "node": platform.node(),
    "pythonhashseed": os.environ.get("PYTHONHASHSEED", "unset"),
    "created": dt.datetime.now().astimezone().isoformat(),
}
json.dump(summary, open(os.path.join(OUT, f"p2_acceptance__{args.set_name}__{args.encoder}.json"),
                        "w"), indent=2)
print("ACCEPT_SUMMARY " + json.dumps(summary), flush=True)

with open(os.path.join(OUT, f"p2_acceptance__{args.set_name}__{args.encoder}.csv"),
          "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=FIELDS)
    w.writeheader()
    w.writerows(rows)
print("OK" if n_ok == len(rows) else "NOT ACCEPTED", flush=True)
