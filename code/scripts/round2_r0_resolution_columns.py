#!/usr/bin/env python
"""Round 2, stage R0: standardise the scan-resolution columns.

Adds `pixel_size_um` (a standardised copy of `pixel_size_um_estimated`) and
`resolution_group` to `results/tailored/integrity/sample_metadata.csv` and to every
joined prediction parquet under `instrumentation/<task>/`.

Bins are fixed by the round-2 execution plan and separate the observed clusters
(0.137, 0.2125, 0.25-0.274, 0.34-0.36, 0.45-0.46, 0.57-0.69 um/px):
    <=0.15, 0.15-0.23, 0.23-0.30, 0.30-0.40, 0.40-0.50, >0.50

Idempotent: a file that already carries both columns is left untouched.
Every parquet rewrite streams row groups and lands via os.replace, so an
interrupted run cannot leave a truncated table in place.
"""
import json
import os
import sys
import time

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

ROOT = "/work/users/w/e/weiyang/hest_replication"
META = f"{ROOT}/results/tailored/integrity/sample_metadata.csv"
INSTR = f"{ROOT}/instrumentation"

BIN_EDGES = [0.0, 0.15, 0.23, 0.30, 0.40, 0.50, np.inf]
BIN_LABELS = ["<=0.15", "0.15-0.23", "0.23-0.30", "0.30-0.40", "0.40-0.50", ">0.50"]

SAMPLE_COL_CANDIDATES = ("sample_id", "sample", "sid", "sample_name")


def assign_groups(px: pd.Series) -> pd.Series:
    """Right-closed bins, so an edge value falls in the lower group."""
    return pd.cut(px, bins=BIN_EDGES, labels=BIN_LABELS, right=True).astype(str)


# ---------------------------------------------------------------- sample metadata
def update_metadata():
    sm = pd.read_csv(META)
    assert "pixel_size_um_estimated" in sm.columns, sm.columns.tolist()
    src = sm["pixel_size_um_estimated"]
    assert src.notna().all(), "null pixel size in sample_metadata.csv"

    sm["pixel_size_um"] = src.astype(float)
    sm["resolution_group"] = assign_groups(sm["pixel_size_um"])
    assert sm["resolution_group"].ne("nan").all(), "unbinned sample"

    tmp = META + ".tmp"
    sm.to_csv(tmp, index=False)
    os.replace(tmp, META)
    print(f"[meta] {META}: {len(sm)} samples, both columns present, kept "
          f"pixel_size_um_estimated alongside pixel_size_um")
    print("[meta] group counts: "
          + ", ".join(f"{k}={v}" for k, v in sm["resolution_group"].value_counts().sort_index().items()))
    return sm


# ------------------------------------------------------------------- parquet edit
def find_sample_col(schema_names):
    for cand in SAMPLE_COL_CANDIDATES:
        if cand in schema_names:
            return cand
    return None


def add_columns(path, px_map, grp_map):
    pf = pq.ParquetFile(path)
    names = pf.schema_arrow.names
    scol = find_sample_col(names)
    n_rows_before = pf.metadata.num_rows

    if scol is None:
        print(f"[skip] {path}: no sample column among {SAMPLE_COL_CANDIDATES}; "
              f"columns={names}")
        return dict(path=path, action="skipped_no_sample_col", columns=names)
    if "pixel_size_um" in names and "resolution_group" in names:
        print(f"[skip] {path}: already carries both columns")
        return dict(path=path, action="already_present", n_rows=n_rows_before)

    comp = (pf.metadata.row_group(0).column(0).compression or "snappy").lower()
    if comp == "uncompressed":
        comp = "none"

    tmp = path + ".tmp"
    writer = None
    seen = set()
    t0 = time.time()
    try:
        for i in range(pf.num_row_groups):
            tbl = pf.read_row_group(i)
            samples = tbl.column(scol).to_pylist()
            seen.update(samples)
            missing = {s for s in set(samples) if s not in px_map}
            if missing:
                raise KeyError(f"{path}: samples absent from sample_metadata.csv: "
                               f"{sorted(missing)[:5]}")
            px = pa.array([px_map[s] for s in samples], type=pa.float64())
            gr = pa.array([grp_map[s] for s in samples], type=pa.string())
            for nm, arr in (("pixel_size_um", px), ("resolution_group", gr)):
                if nm in tbl.column_names:
                    tbl = tbl.set_column(tbl.column_names.index(nm), nm, arr)
                else:
                    tbl = tbl.append_column(nm, arr)
            if writer is None:
                writer = pq.ParquetWriter(tmp, tbl.schema, compression=comp)
            writer.write_table(tbl)
    finally:
        if writer is not None:
            writer.close()

    n_rows_after = pq.ParquetFile(tmp).metadata.num_rows
    assert n_rows_after == n_rows_before, (
        f"{path}: row count changed {n_rows_before} -> {n_rows_after}")
    os.replace(tmp, path)
    dt = time.time() - t0
    print(f"[ok]   {os.path.relpath(path, ROOT)}: +2 cols, {n_rows_before:,} rows, "
          f"{len(seen)} samples, {dt:.0f}s, compression={comp}")
    return dict(path=path, action="updated", n_rows=n_rows_before,
                n_samples=len(seen), seconds=round(dt, 1))


def verify(path, px_map, grp_map):
    """Re-read only the three relevant columns and check the join is exact."""
    pf = pq.ParquetFile(path)
    names = pf.schema_arrow.names
    scol = find_sample_col(names)
    if scol is None or "pixel_size_um" not in names:
        return None
    tbl = pq.read_table(path, columns=[scol, "pixel_size_um", "resolution_group"])
    df = tbl.to_pandas()
    assert df["pixel_size_um"].notna().all(), f"{path}: null pixel_size_um"
    assert df["resolution_group"].ne("nan").all(), f"{path}: unbinned rows"
    g = df.groupby(scol).agg(px=("pixel_size_um", "nunique"),
                             gp=("resolution_group", "nunique"))
    assert (g.px == 1).all() and (g.gp == 1).all(), f"{path}: non-constant per sample"
    for s, row in df.groupby(scol).first().iterrows():
        assert abs(row["pixel_size_um"] - px_map[s]) < 1e-12, f"{path}/{s}: px mismatch"
        assert row["resolution_group"] == grp_map[s], f"{path}/{s}: group mismatch"
    return dict(path=path, n_rows=len(df), n_samples=int(df[scol].nunique()))


def main():
    sm = update_metadata()
    px_map = dict(zip(sm["sample_id"], sm["pixel_size_um"].astype(float)))
    grp_map = dict(zip(sm["sample_id"], sm["resolution_group"]))

    task_dirs = sorted(
        d for d in os.listdir(INSTR)
        if os.path.isdir(f"{INSTR}/{d}") and os.path.exists(f"{INSTR}/{d}/preds.parquet"))
    print(f"[scan] {len(task_dirs)} task directories with preds.parquet: {task_dirs}")

    report, verified = [], []
    for t in task_dirs:
        for fn in ("preds.parquet", "spots.parquet"):
            p = f"{INSTR}/{t}/{fn}"
            if not os.path.exists(p):
                print(f"[warn] {p} absent")
                continue
            report.append(dict(task=t, file=fn, **add_columns(p, px_map, grp_map)))
            v = verify(p, px_map, grp_map)
            if v:
                verified.append(dict(task=t, file=fn, **v))

    total = sum(r["n_rows"] for r in verified if r["file"] == "preds.parquet")
    print(f"\n[verify] {len(verified)} parquets re-read and checked; "
          f"total prediction rows = {total:,}")

    outdir = f"{ROOT}/results/round2/R0_resolution"
    os.makedirs(outdir, exist_ok=True)
    pd.DataFrame(report).to_csv(f"{outdir}/r0_column_report.csv", index=False)
    pd.DataFrame(verified).to_csv(f"{outdir}/r0_verification.csv", index=False)

    # the per-task resolution table that the README subsection reproduces
    rows = []
    for t, g in sm.groupby("task"):
        pat = g["patient"].fillna("UNKNOWN").astype(str)
        ct = pd.crosstab(g["resolution_group"], pat)
        shared = int(((ct > 0).sum(axis=1) > 1).sum())
        rows.append(dict(
            task=t, n_samples=len(g), n_patients=pat.nunique(),
            n_resolution_groups=int(g["resolution_group"].nunique()),
            px_min=round(g["pixel_size_um"].min(), 4),
            px_max=round(g["pixel_size_um"].max(), 4),
            spread=round(g["pixel_size_um"].max() / g["pixel_size_um"].min(), 3),
            groups_with_multiple_patients=shared,
            resolution_predicts_patient=bool(g["resolution_group"].nunique() > 1 and shared == 0),
            distinct_px="; ".join(
                f"{k:.4f}x{v}" for k, v in
                g["pixel_size_um"].round(4).value_counts().sort_index().items())))
    res = pd.DataFrame(rows).sort_values("spread", ascending=False)
    res.to_csv(f"{outdir}/resolution_by_task.csv", index=False)
    print("\n[table] resolution_by_task.csv")
    print(res.drop(columns="distinct_px").to_string(index=False))
    print(f"\n[global] pixel size {sm.pixel_size_um.min():.4f}-{sm.pixel_size_um.max():.4f} um/px, "
          f"spread {sm.pixel_size_um.max()/sm.pixel_size_um.min():.2f}x")

    with open(f"{outdir}/PROVENANCE.txt", "w") as f:
        f.write(
            "Round 2, stage R0 — scan-resolution columns\n"
            f"slurm_job_id      : {os.environ.get('SLURM_JOB_ID', 'NA')}\n"
            f"slurm_partition   : {os.environ.get('SLURM_JOB_PARTITION', 'NA')}\n"
            f"node              : {os.environ.get('SLURMD_NODENAME', 'NA')}\n"
            f"date              : {time.strftime('%Y-%m-%dT%H:%M:%S%z')}\n"
            f"repo_commit       : {os.popen(f'git -C {ROOT} rev-parse HEAD').read().strip()}\n"
            f"script            : code/scripts/round2_r0_resolution_columns.py\n"
            f"command_line      : {' '.join(sys.argv)}\n"
            f"pythonhashseed  : {os.environ.get('PYTHONHASHSEED', 'unset')}\n"
            f"bin_edges         : {BIN_EDGES}\n"
            f"bin_labels        : {BIN_LABELS}\n"
            "plan              : round2_execution_plan.md stage R0 item 2 "
            "(artifact 584a9657-b0a0-4a50-bdfd-7099414273a6)\n"
            "review            : HEST_replication_review.md section 5.3 "
            "(artifact 63c03ac9-4a17-4fc0-892f-eb7860f1cba9)\n"
            f"files_updated     : {sum(1 for r in report if r['action'] == 'updated')}\n"
            f"prediction_rows   : {total}\n")
    print(json.dumps({"updated": sum(1 for r in report if r["action"] == "updated"),
                      "rows": total}, indent=0))


if __name__ == "__main__":
    main()
