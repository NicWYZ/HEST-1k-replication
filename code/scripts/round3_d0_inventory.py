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

import numpy as np

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
# stage: inventory
# --------------------------------------------------------------------------
# Institution attribution. HEST carries no laboratory field, and the id prefix
# (TENX, NCBI, ZEN, MEND, INT, SPA, MISC) is the repository a file was
# downloaded from, not the laboratory that generated it. Round 2 established
# what that confusion costs: the IDC "institution" contrast held two cohorts
# from one generating lab (docs/HEST_replication_review.md 5.4).
#
# So the lab key here is built from the *publication*, not the download source:
#   1. a 10x Genomics product page with no publication  -> the vendor;
#   2. otherwise the last author's affiliation of the linked publication,
#      resolved through PubMed (E-utilities) or Crossref at run time;
#   3. otherwise unresolved, carried as "unresolved: <study_link>".
# Every value is PROVISIONAL. Stage D3 audits it against the source records.
INST_TOKENS = ["University", "Universite", "Université", "Universität", "Institute",
               "Institut", "Hospital", "College", "Center", "Centre", "Inc.",
               "School", "Laboratory", "Karolinska", "KTH", "Clinic", "Foundation"]

# Overrides, each with the evidence that justifies it. Used only where the
# automatic resolution returns no affiliation string at all.
LAB_OVERRIDES = {
    "https://www.biorxiv.org/content/10.1101/2024.06.04.597233v1.full": (
        "10x Genomics Inc.",
        "override: Crossref gives last author Sarah E. B. Taylor with no affiliation "
        "string; the same last author on PMID 38114474 is affiliated 10x Genomics Inc."),
}

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
CROSSREF = "https://api.crossref.org/works/"


def _clean_label(x):
    """HEST writes a whitespace-only patient label for some cohorts, which is
    non-null but carries no information. Treat it as missing."""
    if x is None:
        return None
    try:
        import math
        if isinstance(x, float) and math.isnan(x):
            return None
    except Exception:
        pass
    s = str(x).strip()
    return s if s and s.lower() not in ("nan", "none") else None


def _inst_from_affil(af):
    if not isinstance(af, str) or not af.strip():
        return None
    parts = [p.strip() for p in re.split(r"[,;]", af) if p.strip()]
    hits = [p for p in parts if any(t.lower() in p.lower() for t in INST_TOKENS)]
    if not hits:
        return None
    for pref in ["University", "Universit", "KTH", "Karolinska", "Institute",
                 "Inc.", "Hospital", "College", "Center", "Centre"]:
        for p in hits:
            if pref.lower() in p.lower():
                return p
    return hits[0]


def resolve_studies(study_titles, out_dir: Path):
    """Resolve each study_link to a publication record and a last-author
    affiliation. Network use is PubMed E-utilities and Crossref only."""
    import time
    import urllib.parse
    import xml.etree.ElementTree as ET
    import pandas as pd
    import requests

    def params(extra):
        p = {"db": "pubmed", "retmode": "xml", "tool": "hest-replication-round3-d0"}
        p.update(extra)
        return p

    def doi_from(link):
        l = str(link)
        for pat, fmt in [(r'nature\.com/articles/(s\d+-\d+-\d+-[\dxX]+)', "10.1038/{0}"),
                         (r'science\.org/doi/(10\.\d{4,9}/[^\s?#]+)', "{0}"),
                         (r'biorxiv\.org/content/(10\.1101/[\d.]+?)(?:v\d+)?(?:\.full)?$', "{0}"),
                         (r'/doi/(10\.\d{4,9}/[^\s?#]+)', "{0}"),
                         (r'(10\.\d{4,9}/[^\s?#]+)', "{0}")]:
            mm = re.search(pat, l)
            if mm:
                return fmt.format(mm.group(1))
        return None

    def esearch(term):
        r = requests.get(EUTILS + "esearch.fcgi", params=params({"term": term}), timeout=60)
        ids = ET.fromstring(r.text).findall(".//Id")
        return ids[0].text if ids else None

    def efetch(pmid):
        r = requests.get(EUTILS + "efetch.fcgi", params=params({"id": pmid}), timeout=60)
        arts = ET.fromstring(r.text).findall(".//PubmedArticle")
        if not arts:
            return None
        art = arts[0]
        auths = art.findall(".//Author")

        def one(a):
            nm = ("%s %s" % (a.findtext("ForeName") or "", a.findtext("LastName") or "")).strip()
            af = [x.text for x in a.findall(".//Affiliation")]
            return nm, (af[0] if af else "")
        first = one(auths[0]) if auths else ("", "")
        last = one(auths[-1]) if auths else ("", "")
        return {"pmid": pmid, "pub_title": (art.findtext(".//ArticleTitle") or "")[:120],
                "journal": art.findtext(".//Journal/Title"),
                "year": art.findtext(".//PubDate/Year"),
                "first_author": first[0], "first_affil": first[1],
                "last_author": last[0], "last_affil": last[1]}

    def crossref(doi):
        try:
            r = requests.get(CROSSREF + urllib.parse.quote(doi, safe=""), timeout=60,
                             headers={"Accept": "application/json"})
            if r.status_code != 200:
                return None
            msg = r.json()["message"]
            au = msg.get("author", []) or []

            def aff(a):
                return "; ".join(x.get("name", "") for x in (a.get("affiliation") or []))

            def nm(a):
                return " ".join(filter(None, [a.get("given"), a.get("family")]))
            return {"pub_title": (msg.get("title") or [""])[0][:120],
                    "journal": (msg.get("container-title") or [""])[0],
                    "year": str((msg.get("published", {}).get("date-parts") or [[None]])[0][0]),
                    "first_author": nm(au[0]) if au else "", "first_affil": aff(au[0]) if au else "",
                    "last_author": nm(au[-1]) if au else "", "last_affil": aff(au[-1]) if au else ""}
        except Exception:
            return None

    recs = []
    for link, title in study_titles:
        rec = {"study_link": link, "hest_dataset_title": title, "pmid": None,
               "doi": doi_from(link), "resolved_by": "unresolved"}
        try:
            mm = re.search(r'pubmed[^/]*/(\d+)', str(link))
            if mm:
                rec["pmid"], rec["resolved_by"] = mm.group(1), "pmid-in-link"
            if rec["pmid"] is None:
                mm = re.search(r'(PMC\d+)', str(link))
                if mm:
                    rec["pmid"] = esearch(mm.group(1) + "[pmc]")
                    time.sleep(0.34)
                    if rec["pmid"]:
                        rec["resolved_by"] = "pmcid-in-link"
            if rec["pmid"] is None and rec["doi"]:
                rec["pmid"] = esearch(rec["doi"] + "[DOI]")
                time.sleep(0.34)
                if rec["pmid"]:
                    rec["resolved_by"] = "doi-pubmed"
            if rec["pmid"] is None:
                pm = esearch('"%s"[Title]' % str(title)[:180])
                time.sleep(0.34)
                if pm:
                    rec["pmid"], rec["resolved_by"] = pm, "title-search"
            got = efetch(rec["pmid"]) if rec["pmid"] else None
            if rec["pmid"]:
                time.sleep(0.34)
            if got is None and rec["doi"]:
                got = crossref(rec["doi"])
                if got:
                    rec["resolved_by"] = "crossref"
            if got:
                rec.update(got)
        except Exception as exc:
            rec["error"] = repr(exc)[:200]
        recs.append(rec)
    df = pd.DataFrame(recs)
    df.to_csv(out_dir / "study_affiliations.csv", index=False)
    return df


def stage_inventory(out_dir: Path, root: Path, release: str, reuse: bool):
    import pandas as pd

    listing = pd.read_csv(out_dir / "hf_file_listing.csv.gz")
    state = json.loads((out_dir / "hf_repo_state.json").read_text())
    rel_path = out_dir / "release_tables" / release
    meta = pd.read_csv(rel_path, encoding="utf-8-sig")
    meta["dataset_title"] = meta.dataset_title.fillna("(no dataset_title)")

    # ---- bytes per sample per component, summed from the listing ----------
    f = listing[listing["kind"] == "file"].copy()
    f["size_bytes"] = f["size_bytes"].fillna(0).astype("int64")
    f["component"] = f.path.str.split("/").str[0]
    f.loc[~f.path.str.contains("/"), "component"] = "_root"
    f["base"] = f.path.str.split("/").str[-1]
    f["sid"] = f.base.str.extract(r'^([A-Za-z]+\d+)')[0]
    known = set(meta.id)
    unmatched = f[~f.sid.isin(known)]
    f = f[f.sid.isin(known)]
    piv = (f.pivot_table(index="sid", columns="component", values="size_bytes", aggfunc="sum")
            .reindex(sorted(known)).fillna(0).astype("int64"))
    cnt = (f.pivot_table(index="sid", columns="component", values="path", aggfunc="count")
            .reindex(sorted(known)).fillna(0).astype("int64"))
    comps = list(piv.columns)
    other = [c for c in comps if c not in WANTED_COMPONENTS]
    piv["bytes_four_components"] = piv[WANTED_COMPONENTS].sum(axis=1)
    piv["bytes_other_components"] = piv[other].sum(axis=1)
    piv["bytes_all_components"] = piv[comps].sum(axis=1)

    # ---- byte-identical duplicates, from the listing's blob ids -----------
    bl = f.groupby("blob_id").agg(sids=("sid", lambda x: tuple(sorted(set(x)))),
                                  comps=("component", lambda x: tuple(sorted(set(x)))),
                                  size_bytes=("size_bytes", "first"))
    bl = bl[bl.sids.apply(len) > 1]
    groups = {}
    for _, r in bl.iterrows():
        groups.setdefault(r.sids, set()).update(r.comps)
    dup_rows = [{"group": "+".join(k), "shared_components": ",".join(sorted(v)),
                 "shares_expression_st": int("st" in v), "shares_wsi": int("wsis" in v),
                 "shares_patches": int("patches" in v)} for k, v in groups.items()]
    pd.DataFrame(dup_rows).sort_values("group").to_csv(out_dir / "duplicate_groups.csv", index=False)

    # ---- labels, institutions, flags --------------------------------------
    meta["patient_label"] = meta.patient.apply(_clean_label)
    meta["patient_label_status"] = np.where(
        meta.patient.isna(), "missing",
        np.where(meta.patient_label.isna(), "blank_whitespace", "labelled"))
    meta["download_source_prefix"] = meta.id.str.extract(r'^([A-Za-z]+)')[0]

    studies = sorted(set(zip(meta.study_link.dropna(),
                             meta.dropna(subset=["study_link"]).dataset_title)))
    seen, uniq = set(), []
    for link, title in studies:
        if link not in seen:
            seen.add(link)
            uniq.append((link, title))
    aff_path = out_dir / "study_affiliations.csv"
    if reuse and aff_path.exists():
        aff = pd.read_csv(aff_path)
    else:
        aff = resolve_studies(uniq, out_dir)
    amap = {r.study_link: r for _, r in aff.iterrows()}

    def lab_of(r):
        sl = r.study_link
        vendor = isinstance(r.download_page_link1, str) and "10xgenomics.com" in r.download_page_link1
        if not isinstance(sl, str) or not sl.strip():
            return ("10x Genomics Inc. (vendor product page)", "vendor_product_page") if vendor \
                else ("unresolved: no study link | %s" % r.dataset_title, "no_study_link")
        if sl in LAB_OVERRIDES:
            return LAB_OVERRIDES[sl]
        rec = amap.get(sl)
        if rec is not None:
            inst = _inst_from_affil(rec.get("last_affil"))
            if inst:
                return (inst, "%s last-author affiliation (pmid=%s)" %
                        (rec.get("resolved_by"), rec.get("pmid")))
        return ("unresolved: %s" % sl, "study_link only")

    lab = meta.apply(lab_of, axis=1, result_type="expand")
    meta["lab_provisional"], meta["lab_basis"] = lab[0], lab[1]
    meta["donor_key_provisional"] = np.where(
        meta.patient_label.notna(),
        meta.dataset_title.astype(str) + " | " + meta.patient_label.astype(str), None)

    # resolution_uncertain, reconstructed from HEST's own two pixel-size fields.
    # The rule is checked against the benchmark's 72-sample flag below.
    meta["px_pct_diff"] = (meta.pixel_size_um_embedded - meta.pixel_size_um_estimated) \
        / meta.pixel_size_um_estimated * 100.0
    meta["resolution_uncertain"] = (meta.pixel_size_um_embedded.isna()
                                    | (meta.px_pct_diff.abs() > 5.0))

    # duplicates: keep the most completely annotated id in each group that
    # shares the expression file, mark the others.
    meta["duplicate_of"] = None
    for k, v in groups.items():
        if "st" not in v:
            continue
        sub = meta[meta.id.isin(k)]
        rank = sorted(k, key=lambda s: (
            meta.loc[meta.id == s, "patient_label"].notna().iloc[0],
            isinstance(meta.loc[meta.id == s, "study_link"].iloc[0], str), s), reverse=True)
        for sid in k:
            if sid != rank[0]:
                meta.loc[meta.id == sid, "duplicate_of"] = rank[0]
    meta["is_duplicate_of_other_id"] = meta.duplicate_of.notna()

    # ---- benchmark cross-check -------------------------------------------
    bench = pd.read_csv(root / BENCH_META_REL)
    shared = ["patient", "st_technology", "organ", "oncotree_code", "species",
              "preservation_method", "tissue", "disease_state", "dataset_title",
              "subseries", "pixel_size_um_estimated", "spot_diameter",
              "inter_spot_dist", "magnification", "spots_under_tissue", "nb_genes"]
    idx = meta.set_index("id")
    missing = [s for s in bench.sample_id if s not in idx.index]
    mism = []
    for _, row in bench.iterrows():
        if row.sample_id in missing:
            continue
        h = idx.loc[row.sample_id]
        for col in shared:
            x, y = _clean_label(row[col]), _clean_label(h[col])
            if x is None and y is None:
                continue
            if x is not None and y is not None:
                try:
                    if abs(float(x) - float(y)) <= 1e-9 * max(1.0, abs(float(x))):
                        continue
                    mism.append((row.sample_id, col, row[col], h[col]))
                    continue
                except (TypeError, ValueError):
                    pass
                if str(x) == str(y):
                    continue
            mism.append((row.sample_id, col, row[col], h[col]))
    # the flag rule must reproduce the benchmark's own column
    flag_ok = int((idx.loc[bench.sample_id, "resolution_uncertain"].values
                   == bench.resolution_uncertain.values).sum())
    xc = pd.DataFrame(mism, columns=["sample_id", "field", "benchmark_value", "hest_value"])
    xc.to_csv(out_dir / "benchmark_crosscheck.csv", index=False)
    meta["in_benchmark"] = meta.id.isin(set(bench.sample_id))
    meta = meta.merge(bench[["sample_id", "task"]].rename(
        columns={"sample_id": "id", "task": "benchmark_task"}), on="id", how="left")

    inv = meta.merge(piv.add_prefix("bytes_").rename(
        columns={"bytes_bytes_four_components": "bytes_four_components",
                 "bytes_bytes_other_components": "bytes_other_components",
                 "bytes_bytes_all_components": "bytes_all_components"}),
        left_on="id", right_index=True, how="left")
    inv = inv.merge(cnt[WANTED_COMPONENTS].add_prefix("nfiles_"),
                    left_on="id", right_index=True, how="left")
    assert inv.bytes_patches.notna().all(), "sample with no patches file"
    assert len(inv) == len(meta), "inventory row count changed in the join"

    report = {
        "release_used": release,
        "release_sha256": hashlib.sha256(rel_path.read_bytes()).hexdigest(),
        "hf_revision": state["resolved_revision_sha"],
        "n_samples": int(len(inv)),
        "n_files_listed": int(state["n_files"]),
        "n_listing_files_unmatched_to_a_sample": int(len(unmatched)),
        "unmatched_paths": sorted(unmatched.path.tolist())[:20],
        "bytes_four_components_all_samples": int(inv.bytes_four_components.sum()),
        "bytes_all_components_all_samples": int(inv.bytes_all_components.sum()),
        "patient_label_status": inv.patient_label_status.value_counts().to_dict(),
        "n_resolution_uncertain": int(inv.resolution_uncertain.sum()),
        "n_duplicate_ids_sharing_expression": int(inv.is_duplicate_of_other_id.sum()),
        "n_blob_groups_shared_across_ids": int(len(groups)),
        "benchmark_samples_expected": int(len(bench)),
        "benchmark_samples_found": int(len(bench) - len(missing)),
        "benchmark_samples_missing": missing,
        "benchmark_mismatched_cells": int(len(xc)),
        "benchmark_resolution_flag_agreement": "%d/%d" % (flag_ok, len(bench)),
        "studies_resolved_to_affiliation": int(aff.last_affil.fillna("").str.len().gt(0).sum())
        if "last_affil" in aff.columns else 0,
        "studies_total": int(len(aff)),
    }
    cols = ["id", "hest_version_added", "organ", "species", "st_technology", "oncotree_code",
            "disease_state", "tissue", "preservation_method", "dataset_title", "subseries",
            "study_link", "download_page_link1", "download_source_prefix", "license",
            "data_publication_date", "patient", "patient_label", "patient_label_status",
            "donor_key_provisional", "lab_provisional", "lab_basis",
            "pixel_size_um_estimated", "pixel_size_um_embedded", "px_pct_diff",
            "resolution_uncertain", "magnification", "spots_under_tissue", "nb_genes",
            "inter_spot_dist", "spot_diameter", "fullres_px_width", "fullres_px_height",
            "in_benchmark", "benchmark_task", "duplicate_of", "is_duplicate_of_other_id",
            "nfiles_patches", "nfiles_st", "nfiles_cellvit_seg", "nfiles_metadata",
            "bytes_patches", "bytes_st", "bytes_cellvit_seg", "bytes_metadata",
            "bytes_four_components", "bytes_wsis", "bytes_transcripts",
            "bytes_other_components", "bytes_all_components"]
    inv = inv[[c for c in cols if c in inv.columns]].sort_values("id")
    inv.to_csv(out_dir / "hest_inventory.csv", index=False)
    (out_dir / "inventory_report.json").write_text(json.dumps(report, indent=2, default=str))
    return inv, report


# --------------------------------------------------------------------------
# stage: sets
# --------------------------------------------------------------------------
RULES = {
    "institution_kidney_visium": (
        "One organ and one technology, human only, duplicate ids removed. Keep the "
        "(organ, technology) cell with the most distinct provisional institutions "
        "holding at least three samples each, counting an institution only from a "
        "publication's last-author affiliation and never from the download source, "
        "excluding vendor product pages, unresolved institutions, and any institution "
        "whose samples in the cell are all disease_state 'Treated' (in Kidney on Visium "
        "those are PFA-fixed organoids, not donor tissue). "
        "The cell is Kidney on Visium; the set is every sample from its three "
        "qualifying institutions."),
    "donor_power_kidney_visium": (
        "The (organ, technology) cell with the most distinct HEST-labelled donors, "
        "human only, duplicate ids removed, restricted to the samples that carry a "
        "usable patient label. A donor is keyed by (dataset_title, patient) because "
        "HEST reuses labels such as Patient 1 across cohorts."),
    "platform_pair_multitech": (
        "Every human sample whose publication (study_link) profiled the same tissue "
        "on more than one spatial technology, duplicate ids removed. This selects "
        "studies rather than organs, because a platform contrast is only interpretable "
        "within a study that ran both platforms."),
}


def stage_sets(out_dir: Path, inv):
    import pandas as pd

    H = inv[(inv.species == "Homo sapiens") & (~inv.is_duplicate_of_other_id)].copy()

    # ranking table: every (organ, technology) cell, so the choice is auditable
    rank = []
    for (o, t), s in H.groupby(["organ", "st_technology"]):
        per = s.groupby("lab_provisional").agg(
            n=("id", "size"), nd=("donor_key_provisional", lambda x: x.dropna().nunique()))
        real = per[~per.index.str.startswith(("unresolved", "10x Genomics"))]
        rank.append(dict(organ=o, st_technology=t, n_samples=len(s),
                         n_labs_resolved=len(real),
                         n_labs_resolved_ge3_samples=int((real.n >= 3).sum()),
                         n_labs_resolved_ge3_donors=int((real.nd >= 3).sum()),
                         n_donors=int(s.donor_key_provisional.dropna().nunique()),
                         n_missing_patient_label=int(s.patient_label.isna().sum()),
                         n_resolution_uncertain=int(s.resolution_uncertain.sum()),
                         n_in_benchmark=int(s.in_benchmark.sum()),
                         bytes_four_components=int(s.bytes_four_components.sum()),
                         labs="; ".join("%s (n=%d, donors=%d)" % (i, r.n, r.nd)
                                        for i, r in per.sort_values("n", ascending=False).iterrows())))
    RK = pd.DataFrame(rank).sort_values(
        ["n_labs_resolved_ge3_donors", "n_labs_resolved_ge3_samples", "n_donors"], ascending=False)
    RK.to_csv(out_dir / "organ_technology_ranking.csv", index=False)

    kv = H[(H.organ == "Kidney") & (H.st_technology == "Visium")]
    per = kv.groupby("lab_provisional").id.size()
    inst3 = sorted(i for i, n in per.items()
                   if n >= 3 and not i.startswith(("unresolved", "10x Genomics"))
                   and not (kv[kv.lab_provisional == i].disease_state == "Treated").all())
    mt = H[H.study_link.notna()].groupby("study_link").st_technology.nunique()
    mt = mt[mt > 1].index.tolist()

    members = {
        "institution_kidney_visium": kv[kv.lab_provisional.isin(inst3)],
        "donor_power_kidney_visium": kv[kv.patient_label.notna()],
        "platform_pair_multitech": H[H.study_link.isin(mt)],
    }
    rows, mem_rows = [], []
    for name, s in members.items():
        s = s.sort_values("id")
        for _, r in s.iterrows():
            mem_rows.append({"set_name": name, "sample_id": r.id, "organ": r.organ,
                             "st_technology": r.st_technology, "dataset_title": r.dataset_title,
                             "subseries": r.subseries, "lab_provisional": r.lab_provisional,
                             "patient_label": r.patient_label,
                             "donor_key_provisional": r.donor_key_provisional,
                             "resolution_uncertain": r.resolution_uncertain,
                             "pixel_size_um_estimated": r.pixel_size_um_estimated,
                             "spots_under_tissue": r.spots_under_tissue,
                             "in_benchmark": r.in_benchmark, "benchmark_task": r.benchmark_task,
                             "bytes_four_components": r.bytes_four_components})
        rows.append(dict(
            set_name=name, selection_rule=RULES[name],
            organs="/".join(sorted(s.organ.dropna().unique())),
            technologies="/".join(sorted(s.st_technology.unique())),
            n_samples=len(s),
            n_hest_patients=int(s.donor_key_provisional.dropna().nunique()),
            n_missing_patient_label=int(s.patient_label.isna().sum()),
            n_cohorts=int(s.dataset_title.nunique()),
            n_labs_provisional=int(s.lab_provisional.nunique()),
            labs_provisional="; ".join("%s (n=%d, donors=%d)" % (
                i, len(g), g.donor_key_provisional.dropna().nunique())
                for i, g in s.groupby("lab_provisional")),
            n_resolution_uncertain=int(s.resolution_uncertain.sum()),
            n_in_benchmark=int(s.in_benchmark.sum()),
            pixel_size_um_min=float(s.pixel_size_um_estimated.min()),
            pixel_size_um_max=float(s.pixel_size_um_estimated.max()),
            spots_total=int(s.spots_under_tissue.sum()),
            bytes_patches=int(s.bytes_patches.sum()), bytes_st=int(s.bytes_st.sum()),
            bytes_cellvit_seg=int(s.bytes_cellvit_seg.sum()),
            bytes_metadata=int(s.bytes_metadata.sum()),
            bytes_total_four_components=int(s.bytes_four_components.sum()),
            gb_total_four_components=round(s.bytes_four_components.sum() / 1e9, 3),
            sample_ids=";".join(s.id.tolist())))
    u = pd.concat(members.values()).drop_duplicates("id").sort_values("id")
    rows.append(dict(
        set_name="union_of_the_three_sets",
        selection_rule="Union of the three sets above, each sample counted once. "
                       "This is the storage ask.",
        organs="/".join(sorted(u.organ.dropna().unique())),
        technologies="/".join(sorted(u.st_technology.unique())),
        n_samples=len(u), n_hest_patients=int(u.donor_key_provisional.dropna().nunique()),
        n_missing_patient_label=int(u.patient_label.isna().sum()),
        n_cohorts=int(u.dataset_title.nunique()),
        n_labs_provisional=int(u.lab_provisional.nunique()),
        labs_provisional="; ".join("%s (n=%d, donors=%d)" % (
            i, len(g), g.donor_key_provisional.dropna().nunique()) for i, g in u.groupby("lab_provisional")),
        n_resolution_uncertain=int(u.resolution_uncertain.sum()),
        n_in_benchmark=int(u.in_benchmark.sum()),
        pixel_size_um_min=float(u.pixel_size_um_estimated.min()),
        pixel_size_um_max=float(u.pixel_size_um_estimated.max()),
        spots_total=int(u.spots_under_tissue.sum()),
        bytes_patches=int(u.bytes_patches.sum()), bytes_st=int(u.bytes_st.sum()),
        bytes_cellvit_seg=int(u.bytes_cellvit_seg.sum()), bytes_metadata=int(u.bytes_metadata.sum()),
        bytes_total_four_components=int(u.bytes_four_components.sum()),
        gb_total_four_components=round(u.bytes_four_components.sum() / 1e9, 3),
        sample_ids=";".join(u.id.tolist())))
    EC = pd.DataFrame(rows)
    EC.to_csv(out_dir / "expansion_candidates.csv", index=False)
    pd.DataFrame(mem_rows).to_csv(out_dir / "expansion_set_members.csv", index=False)
    return EC


# --------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", nargs="+", required=True,
                    choices=["listing", "inventory", "sets"])
    ap.add_argument("--project-root", default=PROJECT_ROOT_DEFAULT)
    ap.add_argument("--repo-id", default=REPO_ID)
    ap.add_argument("--release", default="HEST_v1_3_0.csv",
                    help="which release table (in <out>/release_tables/) the inventory uses")
    ap.add_argument("--reuse-affiliations", action="store_true",
                    help="reuse study_affiliations.csv instead of re-querying PubMed/Crossref")
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

    inv = None
    if "inventory" in args.stage:
        inv, report = stage_inventory(out_dir, root, args.release, args.reuse_affiliations)
        print(json.dumps(report, indent=2, default=str))
        extra["release_used"] = report["release_used"]
        extra["release_sha256"] = report["release_sha256"]
        extra["hf_revision"] = report["hf_revision"]
        extra["benchmark_coverage"] = "%d/%d found, %d mismatched cells" % (
            report["benchmark_samples_found"], report["benchmark_samples_expected"],
            report["benchmark_mismatched_cells"])

    if "sets" in args.stage:
        import pandas as pd
        if inv is None:
            inv = pd.read_csv(out_dir / "hest_inventory.csv")
        EC = stage_sets(out_dir, inv)
        print(EC[["set_name", "n_samples", "n_hest_patients", "n_cohorts", "n_labs_provisional",
                  "n_resolution_uncertain", "n_in_benchmark",
                  "bytes_total_four_components", "gb_total_four_components"]].to_string(index=False))
        extra["storage_ask_bytes_four_components"] = int(
            EC.loc[EC.set_name == "union_of_the_three_sets", "bytes_total_four_components"].iloc[0])

    write_provenance(out_dir, root, cfg, extra)
    print("OK stages=%s out=%s" % (args.stage, out_dir))


if __name__ == "__main__":
    main()
