#!/usr/bin/env python
"""Integrity check on the Stage 4a tables, and a corrected spot count.

Stage: faithful replication stage 4, verification of the joined tables against the raw predictions.

The build's n_spots column used barcode.nunique(), which counts unique barcode STRINGS.
Xenium tasks use pseudo-Visium grid barcodes (000x002 etc.) that recur in every sample, and
Visium barcodes recur across samples too, so that column undercounts. The correct unit is the
(sample_id, barcode) pair. Verified here against the independent patch counts in
bench_data/inventory.json.
"""
import os, json, glob
import numpy as np, pandas as pd

ROOT = "/work/users/w/e/weiyang/hest_replication"
DATA = f"{ROOT}/instrumentation"                       # gitignored: the big parquets
OUT  = f"{ROOT}/results/tailored/integrity"
inv  = json.load(open(f"{ROOT}/bench_data/inventory.json"))
inv_patches = {t: sum(r.get("n_barcodes_h5", 0) for r in i["samples"]) for t, i in inv.items()}

rows = []
for task in sorted(os.listdir(OUT)):
    sp = f"{OUT}/{task}/spots.parquet"
    if not os.path.isfile(sp):
        continue
    s = pd.read_parquet(sp, columns=["sample_id","barcode","gene","fold","count","target"])
    s["sample_id"] = s.sample_id.astype(str); s["barcode"] = s.barcode.astype(str)
    pair = s.sample_id + "|" + s.barcode
    n_spots = pair.nunique()
    per_spot = s.groupby(pair, observed=True).size()
    fold_per_spot = s.groupby(pair, observed=True)["fold"].nunique()
    p = pd.read_parquet(f"{DATA}/{task}/preds.parquet", columns=["encoder","sample_id","barcode","gene"])
    rows.append(dict(
        task=task,
        n_spots=int(n_spots),
        inventory_patches=int(inv_patches.get(task, -1)),
        spots_match_inventory=bool(n_spots == inv_patches.get(task)),
        genes_per_spot_min=int(per_spot.min()), genes_per_spot_max=int(per_spot.max()),
        all_spots_50_genes=bool((per_spot == 50).all()),
        max_folds_per_spot=int(fold_per_spot.max()),
        each_spot_one_fold=bool((fold_per_spot == 1).all()),
        n_encoders=int(p.encoder.nunique()),
        pred_rows=int(len(p)),
        pred_rows_expected=int(n_spots * 50 * p.encoder.nunique()),
        counts_integral=bool(np.all(s["count"].to_numpy() == np.round(s["count"].to_numpy()))),
        target_min=float(s.target.min()), target_max=float(s.target.max()),
    ))
    print(f"[ok] {task}: {n_spots} spots (inventory {inv_patches.get(task)}), "
          f"{p.encoder.nunique()} encoders, {len(p):,} pred rows", flush=True)

d = pd.DataFrame(rows)
d["pred_rows_ok"] = d.pred_rows == d.pred_rows_expected
d.to_csv(f"{OUT}/stage4a_integrity.csv", index=False)
print()
print(d[["task","n_spots","inventory_patches","spots_match_inventory","all_spots_50_genes",
         "each_spot_one_fold","n_encoders","pred_rows","pred_rows_ok","counts_integral"]].to_string(index=False))
print()
print("TOTAL spots         :", f"{int(d.n_spots.sum()):,}")
print("TOTAL inventory     :", f"{int(d.inventory_patches.sum()):,}")
print("all match inventory :", bool(d.spots_match_inventory.all()))
print("all 50 genes/spot   :", bool(d.all_spots_50_genes.all()))
print("each spot one fold  :", bool(d.each_spot_one_fold.all()))
print("pred row counts ok  :", bool(d.pred_rows_ok.all()))
print("raw counts integral :", bool(d.counts_integral.all()))
print("TOTAL pred rows     :", f"{int(d.pred_rows.sum()):,}")
