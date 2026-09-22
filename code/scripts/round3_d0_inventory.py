#!/usr/bin/env python
"""Round 3, stage D0. Inventory of full HEST-1k and the expansion-set proposal.

Nothing is downloaded by this script beyond the HuggingFace *file listing* (a JSON
tree of paths and byte sizes) and the release metadata table that is already on
disk. The actual data download is stage D1 and needs explicit approval.

Stages
------
listing    query the HuggingFace API for MahmoodLab/hest: the resolved revision,
           the repo refs (to detect a release newer than the metadata table on
           disk), and the recursive file tree with per-blob byte sizes.
inventory  join the listing to HEST's own metadata table and write one row per
           sample with organ/species/technology/oncotree/cohort/patient/pixel
           size/spot count and bytes per component.
sets       apply the three selection rules and write one row per candidate set.

Usage
-----
python round3_d0_inventory.py --stage listing
python round3_d0_inventory.py --stage inventory sets
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import platform
import re
import socket
import subprocess
import sys
import zlib
from pathlib import Path

PROJECT_ROOT_DEFAULT = "/work/users/w/e/weiyang/hest_replication"
REPO_ID = "MahmoodLab/hest"
# HEST's own release metadata table, as shipped inside the HEST source tree.
METADATA_REL = "code/HEST/assets/HEST_v1_1_0.csv"
BENCH_META_REL = "results/tailored/integrity/sample_metadata.csv"
OUT_REL = "results/round3/D0_inventory"

# The four components stage D1 would download. Everything else in the repo
# (wsis/, thumbnails/, transcripts/, ...) is listed but not part of the ask.
WANTED_COMPONENTS = ["patches", "st", "cellvit_seg", "metadata"]


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def _git_commit(root: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=30,
        )
        return out.stdout.strip() or "unavailable"
    except Exception:
        return "unavailable"


def _config_hash(cfg: dict) -> str:
    """Stable hash of the config. json.dumps with sorted keys, then crc32 and
    sha256 of the *bytes*, so nothing depends on Python's randomised string
    hashing (WAYS_OF_WORKING: never hash() a string for an identifier)."""
    blob = json.dumps(cfg, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:%s crc32:%08x" % (hashlib.sha256(blob).hexdigest()[:32],
                                     zlib.crc32(blob))


def write_provenance(out_dir: Path, root: Path, cfg: dict, extra: dict) -> None:
    lines = [
        "dir              : %s" % out_dir,
        "stage            : round3 D0 (inventory of full HEST-1k, expansion proposal)",
        "script           : code/scripts/round3_d0_inventory.py",
        "created          : %s" % _dt.datetime.now().astimezone().isoformat(),
        "operator         : weiyang (Nicolas Weiyang Zhang)",
        "slurm_job_id     : %s" % os.environ.get("SLURM_JOB_ID", "not-under-slurm"),
        "slurm_partition  : %s" % os.environ.get("SLURM_JOB_PARTITION", "not-under-slurm"),
        "slurm_nodelist   : %s" % os.environ.get("SLURM_JOB_NODELIST", "not-under-slurm"),
        "node             : %s" % socket.gethostname(),
        "platform         : %s" % platform.platform(),
        "python           : %s" % sys.version.split()[0],
        "executable       : %s" % sys.executable,
        "commit           : %s" % _git_commit(root),
        "command_line     : %s" % " ".join([sys.executable] + sys.argv),
        "pythonhashseed   : %s" % os.environ.get("PYTHONHASHSEED", "unset"),
        "config           : %s" % json.dumps(cfg, sort_keys=True),
        "config_hash      : %s" % _config_hash(cfg),
        "downloads        : NONE. HuggingFace API listing only (paths + byte sizes).",
    ]
    for k, v in extra.items():
        lines.append("%-17s: %s" % (k, v))
    (out_dir / "PROVENANCE.txt").write_text("\n".join(lines) + "\n")


# --------------------------------------------------------------------------
# stage: listing
# --------------------------------------------------------------------------
def stage_listing(out_dir: Path, repo_id: str) -> dict:
    import pandas as pd
    from huggingface_hub import HfApi

    api = HfApi()
    who = {}
    try:
        who = api.whoami()
        whoami = who.get("name", "unknown")
    except Exception as exc:  # token missing or rejected
        whoami = "whoami-failed: %r" % (exc,)

    info = api.dataset_info(repo_id, files_metadata=False)
    refs = api.list_repo_refs(repo_id, repo_type="dataset")
    state = {
        "repo_id": repo_id,
        "resolved_revision_sha": info.sha,
        "last_modified": str(getattr(info, "lastModified", None)),
        "gated": getattr(info, "gated", None),
        "private": getattr(info, "private", None),
        "downloads": getattr(info, "downloads", None),
        "whoami": whoami,
        "branches": [{"name": b.name, "target_commit": b.target_commit} for b in refs.branches],
        "tags": [{"name": t.name, "target_commit": t.target_commit} for t in refs.tags],
    }
    try:
        cd = getattr(info, "cardData", None)
        state["card_data"] = dict(cd.to_dict()) if cd is not None else None
    except Exception as exc:
        state["card_data"] = "unavailable: %r" % (exc,)

    rows = []
    for item in api.list_repo_tree(repo_id, repo_type="dataset", recursive=True,
                                   revision=info.sha):
        kind = type(item).__name__
        rows.append({
            "path": item.path,
            "kind": "file" if kind == "RepoFile" else "dir",
            "size_bytes": getattr(item, "size", None),
            "blob_id": getattr(item, "blob_id", None),
            "lfs_size": (item.lfs.size if getattr(item, "lfs", None) else None),
        })
    df = pd.DataFrame(rows)
    df.to_csv(out_dir / "hf_file_listing.csv.gz", index=False, compression="gzip")

    files = df[df["kind"] == "file"]
    state["n_tree_entries"] = int(len(df))
    state["n_files"] = int(len(files))
    state["n_files_missing_size"] = int(files["size_bytes"].isna().sum())
    state["total_bytes_all_components"] = int(files["size_bytes"].fillna(0).sum())
    state["top_level"] = (
        files["path"].str.split("/").str[0].value_counts().to_dict()
    )
    state["root_level_files"] = sorted(
        p for p in files["path"] if "/" not in p
    )
    # The release metadata tables live at the repo root as HEST_v<maj>_<min>_<pat>.csv.
    # These are metadata, not data: fetching them is in scope for D0, and the newest
    # one tells us whether a release newer than the on-disk v1_1_0 exists.
    from huggingface_hub import hf_hub_download

    release_csvs = sorted(p for p in state["root_level_files"]
                          if re.match(r"^HEST_v\d+_\d+_\d+\.csv$", p))
    state["release_csvs_in_repo"] = release_csvs
    fetched = {}
    meta_dir = out_dir / "release_tables"
    meta_dir.mkdir(exist_ok=True)
    for name in release_csvs:
        try:
            p = hf_hub_download(repo_id=repo_id, filename=name, repo_type="dataset",
                                revision=info.sha)
            dst = meta_dir / name
            dst.write_bytes(Path(p).read_bytes())
            n = sum(1 for _ in dst.open("r", encoding="utf-8-sig")) - 1
            fetched[name] = {"path": str(dst), "n_data_lines": n,
                             "sha256": hashlib.sha256(dst.read_bytes()).hexdigest()}
        except Exception as exc:
            fetched[name] = "fetch-failed: %r" % (exc,)
    state["release_tables_fetched"] = fetched

    (out_dir / "hf_repo_state.json").write_text(json.dumps(state, indent=2, default=str))
    return state


# --------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", nargs="+", required=True,
                    choices=["listing", "inventory", "sets"])
    ap.add_argument("--project-root", default=PROJECT_ROOT_DEFAULT)
    ap.add_argument("--repo-id", default=REPO_ID)
    args = ap.parse_args()

    root = Path(args.project_root)
    out_dir = root / OUT_REL
    out_dir.mkdir(parents=True, exist_ok=True)
    cfg = {"stages": args.stage, "repo_id": args.repo_id,
           "metadata_rel": METADATA_REL, "wanted_components": WANTED_COMPONENTS}
    extra = {}

    if "listing" in args.stage:
        st = stage_listing(out_dir, args.repo_id)
        print(json.dumps({k: v for k, v in st.items()
                          if k not in ("branches", "tags")}, indent=2, default=str))
        print("BRANCHES", [b["name"] for b in st["branches"]])
        print("TAGS", [t["name"] for t in st["tags"]])
        extra["hf_revision"] = st["resolved_revision_sha"]

    write_provenance(out_dir, root, cfg, extra)
    print("OK stages=%s out=%s" % (args.stage, out_dir))


if __name__ == "__main__":
    main()
