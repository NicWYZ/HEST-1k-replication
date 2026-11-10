"""Round 10, track final-runs, F2 option (b): fetch HEST-1k's CellViT segmentations for the corpus samples without one.

Nicolas approved this download in the session on 10 November 2026 (plan, section 5b, item 4, and the dated note of
that day). Only `cellvit_seg/<sample>_cellvit_seg.parquet` files are fetched, at the revision of round 3's file
listing, for the kept samples of the corpus tasks whose segmentation is not already on Longleaf. Nothing else.

usage: round10_final_runs_f2_cellvit_download.py <listing.csv.gz> <audit_verdicts_dir> <set_dir> <out_dir>
                                                 --revision <sha> --have-roots <dir> ...
Writes into <set_dir>/cellvit_seg/ and, in <out_dir>, cellvit_download_summary.json (first) and
cellvit_download_verification.csv.
"""
import argparse, csv, glob, gzip, json, os, re, sys

TASKS = ["kidney__Visium", "brain__Visium", "bowel__Visium", "breast__Spatial_Transcriptomics",
         "breast__Xenium", "lung__Xenium"]


def have_ids(roots):
    ids = set()
    for r in roots:
        for p in glob.glob(os.path.join(r, "*", "cellvit_seg", "*_cellvit_seg.parquet")) + \
                 glob.glob(os.path.join(r, "*", "*", "cellvit_seg", "*_cellvit_seg.parquet")):
            ids.add(os.path.basename(p)[:-len("_cellvit_seg.parquet")])
    return ids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("listing"); ap.add_argument("verdicts"); ap.add_argument("set_dir"); ap.add_argument("out")
    ap.add_argument("--revision", required=True); ap.add_argument("--have-roots", nargs="+", required=True)
    ap.add_argument("--repo-id", default="MahmoodLab/hest")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    have = have_ids(a.have_roots)
    listed = {}
    with gzip.open(a.listing, "rt", newline="") as fh:
        for row in csv.DictReader(fh):
            m = re.fullmatch(r"cellvit_seg/(.+)_cellvit_seg\.parquet", row["path"])
            if row["kind"] == "file" and m:
                listed[m.group(1)] = int(float(row["size_bytes"]))
    need, per_task = {}, {}
    for t in TASKS:
        with open(os.path.join(a.verdicts, f"donor_map__{t}.csv")) as fh:
            ids = sorted({r["sample_id"] for r in csv.DictReader(fh)})
        miss = [s for s in ids if s not in have]
        per_task[t] = dict(samples=len(ids), on_longleaf=len(ids) - len(miss), missing=len(miss),
                           missing_listed=sum(s in listed for s in miss),
                           missing_not_listed=[s for s in miss if s not in listed])
        for s in miss:
            if s in listed:
                need[s] = listed[s]
    summ = dict(stage="F2", unit="cellvit_download", repo_id=a.repo_id, revision=a.revision,
                n_have_before=len(have), per_task=per_task, n_files=len(need), bytes_expected=sum(need.values()))
    from huggingface_hub import HfApi, snapshot_download
    import huggingface_hub
    summ["huggingface_hub"] = huggingface_hub.__version__
    summ["repo_main_sha_now"] = HfApi().dataset_info(a.repo_id, revision="main").sha
    json.dump(summ, open(os.path.join(a.out, "cellvit_download_summary.json"), "w"), indent=1)
    print(json.dumps(summ, indent=1), flush=True)
    patterns = sorted(f"cellvit_seg/{s}_cellvit_seg.parquet" for s in need)
    os.makedirs(a.set_dir, exist_ok=True)
    snapshot_download(repo_id=a.repo_id, repo_type="dataset", revision=a.revision, allow_patterns=patterns,
                      local_dir=a.set_dir, max_workers=4)
    import pyarrow.parquet as pq
    rows, ok = [], 0
    for s in sorted(need):
        p = os.path.join(a.set_dir, "cellvit_seg", f"{s}_cellvit_seg.parquet")
        size = os.path.getsize(p) if os.path.exists(p) else -1
        nrows = pq.ParquetFile(p).metadata.num_rows if size > 0 else -1
        good = size == need[s] and nrows > 0
        ok += good
        rows.append(dict(sample_id=s, path=p, bytes_listed=need[s], bytes_on_disk=size, n_rows=nrows, ok=good))
    with open(os.path.join(a.out, "cellvit_download_verification.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    summ.update(n_ok=ok, n_failed=len(rows) - ok, bytes_on_disk=sum(r["bytes_on_disk"] for r in rows if r["ok"]))
    json.dump(summ, open(os.path.join(a.out, "cellvit_download_summary.json"), "w"), indent=1)
    print(f"verified {ok} of {len(rows)} files", flush=True)
    sys.exit(0 if ok == len(rows) else 1)


if __name__ == "__main__":
    main()
