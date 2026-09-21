#!/usr/bin/env python
"""Round 2, R1 follow-up: align the shard schema to round 1, and backfill config_hash.

Stage: R1, one-off schema repair of the prediction parquets after the mixed-type fold column killed a write; kept as the record of the fix.

Two defects found in review of the R1 outputs.

1. SCHEMA. The plan requires the intercept parquets to carry "the same schema as round 1
   plus a head column". Round 1's `instrumentation/<task>/preds.parquet` uses `pred` and
   `target`; the R1 shards were written with `y_pred` and `y_true_log1p`. The six join
   keys (task, encoder, fold, sample_id, barcode, gene) were correct, so joins to round 1
   worked, but a script written against round 1's column names would fail on the shards.
   This renames the two columns in place. `y_raw_count` is retained as a declared addition
   beyond round 1's schema.

2. PROVENANCE. The round-2 plan's ground rules require `config_hash` in every
   PROVENANCE.txt alongside job ID, commit, date and command line. The R0 and R1
   provenance files omitted it. This appends it, computed from the config that actually
   determined each stage's numbers.
"""
import glob
import hashlib
import json
import os

import pyarrow as pa
import pyarrow.parquet as pq

ROOT = "/work/users/w/e/weiyang/hest_replication"
PARQ = f"{ROOT}/instrumentation/round2_intercept"
RENAME = {"y_pred": "pred", "y_true_log1p": "target"}

R1_CONFIG = {
    "pipeline": "StandardScaler -> PCA(n_components=256, random_state=1), fit on train only",
    "ridge_alpha": "100/(256*50)",
    "ridge_kwargs": {"random_state": 0, "max_iter": 1000},
    "solvers": ["lsqr", "cholesky"],
    "heads": ["nointercept", "intercept", "ycentered"],
    "dtype": "float32 (inherited from the cached embeddings and AnnData reads)",
    "folds": "shipped bench_data/<task>/splits/test_*.csv",
    "metric": "Pearson pooled over the test fold (the faithful Table-1 convention)",
}
R0_CONFIG = {
    "bin_edges": [0.0, 0.15, 0.23, 0.30, 0.40, 0.50, None],
    "bin_labels": ["<=0.15", "0.15-0.23", "0.23-0.30", "0.30-0.40", "0.40-0.50", ">0.50"],
    "source_column": "pixel_size_um_estimated",
    "bin_closure": "right-closed (an edge value falls in the lower group)",
}


def cfg_hash(d):
    return hashlib.sha256(json.dumps(d, sort_keys=True).encode()).hexdigest()[:16]


def fix_shard(path, ref_cols):
    pf = pq.ParquetFile(path)
    names = pf.schema_arrow.names
    if not any(k in names for k in RENAME):
        print(f"[skip] {os.path.basename(path)}: already renamed")
        return False
    n_before = pf.metadata.num_rows
    tmp = path + ".tmp"
    writer = None
    try:
        for i in range(pf.num_row_groups):
            tbl = pf.read_row_group(i)
            tbl = tbl.rename_columns([RENAME.get(c, c) for c in tbl.column_names])
            if writer is None:
                writer = pq.ParquetWriter(tmp, tbl.schema, compression="snappy")
            writer.write_table(tbl)
    finally:
        if writer is not None:
            writer.close()
    assert pq.ParquetFile(tmp).metadata.num_rows == n_before, path
    os.replace(tmp, path)
    return True


def main():
    ref = None
    for t in sorted(os.listdir(f"{ROOT}/instrumentation")):
        p = f"{ROOT}/instrumentation/{t}/preds.parquet"
        if os.path.exists(p):
            ref = pq.ParquetFile(p).schema_arrow.names
            break
    print(f"[ref] round-1 schema: {ref}")

    shards = sorted(glob.glob(f"{PARQ}/*/preds__*.parquet"))
    print(f"[scan] {len(shards)} shards")
    n_fixed = sum(fix_shard(p, ref) for p in shards)

    # verify every shard against the requirement: round-1 schema + head (+ declared extra)
    expected = set(ref) | {"head", "y_raw_count"}
    rows, bad = [], []
    for p in shards:
        got = set(pq.ParquetFile(p).schema_arrow.names)
        ok = got == expected
        if not ok:
            bad.append((p, sorted(got ^ expected)))
        rows.append((os.path.relpath(p, ROOT), ok))
    print(f"[verify] {sum(1 for _, ok in rows if ok)}/{len(rows)} shards match "
          f"round-1 schema + {{head, y_raw_count}}")
    if bad:
        for p, diff in bad[:5]:
            print(f"  MISMATCH {p}: symmetric difference {diff}")
        raise SystemExit("schema verification failed")
    print(f"[verify] join keys present in all shards: "
          f"{sorted(set(ref) & expected & {'task','encoder','fold','sample_id','barcode','gene'})}")
    print(f"[done] {n_fixed} shards rewritten, {len(shards)-n_fixed} already correct")

    for stage, cfg in (("R0_resolution", R0_CONFIG), ("R1_intercept", R1_CONFIG)):
        h = cfg_hash(cfg)
        for pfile in sorted(glob.glob(f"{ROOT}/results/round2/{stage}/PROVENANCE*.txt")):
            txt = open(pfile).read()
            if "config_hash" in txt:
                continue
            with open(pfile, "a") as f:
                f.write(f"config_hash       : {h}\n")
                f.write(f"config            : {json.dumps(cfg, sort_keys=True)}\n")
                f.write("note              : config_hash backfilled 2026-09-17; the round-2 "
                        "ground rules require it and the original file omitted it.\n")
            print(f"[prov] {os.path.basename(pfile)} += config_hash {h}")


if __name__ == "__main__":
    main()
