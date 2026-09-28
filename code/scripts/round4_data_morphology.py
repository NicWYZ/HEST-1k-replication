#!/usr/bin/env python
"""Round 4, stage P, sub-stage P3: per-spot CellViT morphology for the expansion sets.

Stage: round 4 data pull, P3 morphology covariates.

Two stages, selected with --stage.

  anchor   Rerun the round-2 builder on one CCRCC and one IDC benchmark sample and compare,
           column by column, against instrumentation/morphology_v2/<task>_morph.parquet.
           Also dumps the per-sample patch geometry of every expansion sample, so the
           expansion stage's geometry choice is made from measured attributes and not
           assumed. Writes no expansion output.

  expand   Builds instrumentation/morphology_ext/<set>/morphology.parquet for the
           expansion sets named in the config, one row per patched spot.

THE BUILDER. code/scripts/morphology_features.py is a round-2 script with no functions: the
per-sample computation sits inside two module-level loops, its roots are hardcoded absolute
paths, and it skips any task whose output parquet already exists (all ten do). So it cannot be
called as a library and an unmodified rerun against the real tree is a no-op that writes
nothing. It is therefore imported unmodified here, with sys.argv set so its task list is empty
and its loops do not execute, for its two constants (EXPECTED, CHUNK), and its per-sample
computation is transcribed verbatim into spot_features() below. The anchor stage is the proof
that the transcription is the same builder: it must reproduce morphology_v2 to 1e-6 on every
column of both anchor samples, and this script stops if it does not.

GEOMETRY. morphology_features.py takes the patch half-width in WSI pixels as 112 * factor,
where factor is an attribute of the patches/<sid>.h5 'img' dataset, so the patch extent is
224 * factor. patch_scale_sources.csv records that 112 / pixel_size_um_estimated equals
224 * factor on all 72 benchmark samples, that is, it is the full extent and not the half-width.
Round 3's D4 probe (round3_d4_probe.py, patch_geometry) returned 112 / pixel_size_um_estimated
as the HALF-width when no 'factor' attribute was found, which is twice the extent this builder
uses. This script re-derives the extent from each patch file's own attributes and halves it,
and records the attribute it used per sample, so the expansion is on the same geometry as the
benchmark. No value is copied from patch_scale_sources.csv.

COORDINATES. Spot centres come from the AnnData obsm['spatial'] of the same release that
supplied the CellViT parquet, so the two are in one frame and the HEST-1k against benchmark
patch-coordinate relation (axis swap plus half a source patch, README property 11) does not
enter. The relation is measured per sample anyway and written to the geometry table.
"""
import argparse
import hashlib
import importlib.util
import json
import os
import platform
import subprocess
import sys

import anndata as ad
import geopandas as gpd
import h5py
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from scipy.spatial import cKDTree


# --------------------------------------------------------------------------- builder import
def load_builder(path):
    """Import morphology_features.py unmodified without letting its loops run.

    Its task list is `[t for t in tasks if t in sys.argv[1].split(",")]` when argv has an
    argument, so a token that is not a benchmark task directory leaves it empty.
    """
    saved = sys.argv
    sys.argv = [path, "__round4_p3_no_task__"]
    try:
        spec = importlib.util.spec_from_file_location("morphology_features_round2", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    finally:
        sys.argv = saved
    assert mod.EXPECTED == {"neoplastic", "inflammatory", "connective", "epithelial", "dead"}, \
        f"unexpected class set in builder: {mod.EXPECTED}"
    assert isinstance(mod.CHUNK, int) and mod.CHUNK > 0
    return mod


# --------------------------------------------------------------- the builder's inner loop
def spot_features(xy, cx, cy, area, cls, half, expected, chunk):
    """Verbatim transcription of the per-sample body of morphology_features.py.

    For each spot, every nucleus whose centroid lies in the square [cx +- half, cy +- half],
    found as a KD-tree ball query at the circumscribing radius followed by an exact box filter.
    """
    tree = cKDTree(np.c_[cx, cy])
    recs = []
    for s0 in range(0, len(xy), chunk):
        block = xy[s0:s0 + chunk]
        balls = tree.query_ball_point(block, r=half * np.sqrt(2.0), workers=-1)
        for li, idxs in enumerate(balls):
            if not idxs:
                continue
            ii = np.asarray(idxs)
            inbox = (np.abs(cx[ii] - block[li, 0]) <= half) & (np.abs(cy[ii] - block[li, 1]) <= half)
            ii = ii[inbox]
            if ii.size == 0:
                continue
            a_, c_ = area[ii], cls[ii]
            rec = dict(spot=s0 + li, n_nuclei=int(ii.size),
                       area_mean=float(a_.mean()), area_median=float(np.median(a_)))
            for k_ in sorted(expected):
                rec[f"frac_{k_}"] = float((c_ == k_).mean())
            neo = a_[c_ == "neoplastic"]
            rec["n_neoplastic"] = int(neo.size)
            rec["neo_area_mean"] = float(neo.mean()) if neo.size else np.nan
            recs.append(rec)
    return recs


def assemble(recs, xy, bc, expected):
    """The builder's frame assembly, minus its task/sample_id/in_patch_set inserts."""
    feat = pd.DataFrame(recs).set_index("spot") if recs else pd.DataFrame()
    full = pd.DataFrame(index=np.arange(len(xy))).join(feat)
    for col in ("n_nuclei", "n_neoplastic"):
        if col not in full.columns:
            full[col] = 0
        full[col] = full[col].fillna(0).astype(int)
    for k_ in sorted(expected):
        if f"frac_{k_}" not in full.columns:
            full[f"frac_{k_}"] = np.nan
    for col in ("area_mean", "area_median", "neo_area_mean"):
        if col not in full.columns:
            full[col] = np.nan
    full.insert(0, "barcode", bc)
    return full


def read_cellvit(path, expected):
    nuc = gpd.read_parquet(path)
    assert nuc.geometry.notna().all(), f"{path}: null geometry"
    cls = nuc["class"].astype(str).str.lower().to_numpy()
    unknown = set(np.unique(cls)) - expected
    assert not unknown, f"{path}: unexpected classes {unknown}"
    cent = nuc.geometry.centroid
    area = nuc.geometry.area.to_numpy()
    assert (area > 0).all(), f"{path}: non-positive area"
    return cent.x.to_numpy(), cent.y.to_numpy(), area, cls, len(nuc)


def decode(a):
    return np.array([x.decode() if isinstance(x, (bytes, np.bytes_)) else str(x)
                     for x in np.asarray(a).reshape(-1)], dtype=object)


# --------------------------------------------------------------------------------- geometry
def patch_geometry(patch_h5, meta_json, pse_fallback=None):
    """Half-width in WSI pixels, re-derived from this patch file's own extent record.

    Returns (half, source, extent_px, attrs, crosschecks). The patch EXTENT is the quantity the
    attributes record; the half-width is half of it. Preference order is the value the
    extraction itself used.
    """
    with h5py.File(patch_h5, "r") as f:
        at = {str(k): np.asarray(v).ravel()[0] for k, v in f["img"].attrs.items()}
    attrs = {k: str(v) for k, v in at.items()}
    pse, pse_src = None, "none"
    if meta_json and os.path.isfile(meta_json):
        with open(meta_json) as fh:
            md = json.load(fh)
        for key in ("pixel_size_um_estimated", "pixel_size_um_embedded", "pixel_size"):
            if md.get(key) not in (None, ""):
                pse, pse_src = float(md[key]), f"metadata:{key}"
                break
    if pse is None and "pixel_size" in at:
        pse, pse_src = float(at["pixel_size"]), "patch_attr:pixel_size"
    if pse is None and pse_fallback:
        pse, pse_src = float(pse_fallback), "task_def_or_selection_pixel_size"
    if "factor" in at:
        extent, src = 224.0 * float(at["factor"]), "224x_patch_attr_factor"
    elif "downsample" in at:
        extent, src = 224.0 * float(at["downsample"]), "224x_patch_attr_downsample"
    elif "patch_size_level0" in at:
        extent, src = float(at["patch_size_level0"]), "patch_attr_patch_size_level0"
    elif pse is not None:
        extent, src = 112.0 / pse, "112_over_pixel_size_um_estimated"
    else:
        raise AssertionError(f"{patch_h5}: no usable patch extent attribute and no pixel size")
    cross = dict(
        extent_from_pixel_size=(112.0 / pse) if pse else np.nan,
        pixel_size_um_used=pse if pse else np.nan,
        pixel_size_source=pse_src,
        pixel_size_attr=float(at["pixel_size"]) if "pixel_size" in at else np.nan,
        extent_from_pixel_size_attr=(112.0 / float(at["pixel_size"])) if "pixel_size" in at else np.nan,
        patch_size_src_attr=float(at["patch_size_src"]) if "patch_size_src" in at else np.nan,
        patch_size_attr=float(at["patch_size"]) if "patch_size" in at else np.nan,
        patch_size_target_attr=float(at["patch_size_target"]) if "patch_size_target" in at else np.nan,
    )
    return extent / 2.0, src, extent, attrs, cross


def coord_relation(patch_h5, bc_to_xy):
    """Measure how the patch-file coordinates relate to the AnnData spot centres."""
    with h5py.File(patch_h5, "r") as f:
        if "coords" not in f:
            return dict(coord_rel="no_coords_dataset")
        pc = np.asarray(f["coords"][:], dtype=np.float64)
        pb = decode(f["barcode"][:])
    keep = [i for i, b in enumerate(pb) if b in bc_to_xy]
    if not keep:
        return dict(coord_rel="no_shared_barcodes")
    idx = np.asarray(keep)
    sp = np.asarray([bc_to_xy[pb[i]] for i in idx], dtype=np.float64)
    d_direct = np.median(pc[idx] - sp, axis=0)
    d_swap = np.median(pc[idx][:, ::-1] - sp, axis=0)
    return dict(coord_rel="measured",
                coord_direct_dx=float(d_direct[0]), coord_direct_dy=float(d_direct[1]),
                coord_swap_dx=float(d_swap[0]), coord_swap_dy=float(d_swap[1]),
                coord_n_shared=int(len(idx)))


# ----------------------------------------------------------------------------------- anchor
ANCHOR_COLS = ["n_nuclei", "area_mean", "area_median", "frac_connective", "frac_dead",
               "frac_epithelial", "frac_inflammatory", "frac_neoplastic",
               "n_neoplastic", "neo_area_mean"]


def coldiff(a, b):
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    both_nan = np.isnan(a) & np.isnan(b)
    d = np.abs(a - b)
    d[both_nan] = 0.0
    n_nan_mismatch = int((np.isnan(a) ^ np.isnan(b)).sum())
    d[np.isnan(d)] = np.inf
    return float(np.nanmax(d)) if d.size else 0.0, n_nan_mismatch


def run_anchor(cfg, mod, outdir):
    root = cfg["repo_root"]
    rows, ok = [], True
    for spec in cfg["anchor"]:
        task, sid = spec["task"], spec["sample_id"]
        ph = f"{root}/bench_data/{task}/patches/{sid}.h5"
        with h5py.File(ph, "r") as f:
            at = dict(f["img"].attrs)
            factor = float(np.asarray(at["factor"]).ravel()[0])
            patch_bc = set(decode(f["barcode"][:]))
        half = 112.0 * factor
        assert half > 0
        from huggingface_hub import hf_hub_download
        fp = hf_hub_download("MahmoodLab/hest", f"cellvit_seg/{sid}_cellvit_seg.parquet",
                             repo_type="dataset", cache_dir=os.environ.get("HF_HOME"))
        cx, cy, area, cls, n_nuc = read_cellvit(fp, mod.EXPECTED)
        A = ad.read_h5ad(f"{root}/bench_data/{task}/adata/{sid}.h5ad", backed="r")
        bc = np.asarray(A.obs_names[:], dtype=object)
        xy = np.asarray(A.obsm["spatial"], dtype=np.float64)
        try:
            A.file.close()
        except Exception:
            pass
        recs = spot_features(xy, cx, cy, area, cls, half, mod.EXPECTED, mod.CHUNK)
        full = assemble(recs, xy, bc, mod.EXPECTED)
        full["in_patch_set"] = [b in patch_bc for b in bc]

        ref = pd.read_parquet(f"{root}/{cfg['morphology_v2_dir']}/{task}_morph.parquet")
        ref = ref[ref.sample_id == sid].reset_index(drop=True)
        n_row_match = int(len(ref) == len(full))
        bc_match = int(n_row_match and bool((ref["barcode"].to_numpy() == full["barcode"].to_numpy()).all()))
        row = dict(task=task, sample_id=sid, factor=factor, half_width_px=half,
                   patch_extent_px=2 * half, n_nuclei_total=n_nuc,
                   n_rows_new=len(full), n_rows_ref=len(ref),
                   rows_match=n_row_match, barcodes_match=bc_match)
        worst = 0.0
        for cname in ANCHOR_COLS:
            if not (n_row_match and bc_match):
                row[f"maxabs_{cname}"] = np.inf
                worst = np.inf
                continue
            d, nm = coldiff(full[cname].to_numpy(), ref[cname].to_numpy())
            row[f"maxabs_{cname}"] = d
            row[f"nanmismatch_{cname}"] = nm
            worst = max(worst, d if np.isfinite(d) else np.inf)
            if nm:
                worst = np.inf
        ipsd = int((full["in_patch_set"].to_numpy() != ref["in_patch_set"].to_numpy()).sum()) \
            if (n_row_match and bc_match and "in_patch_set" in ref.columns) else -1
        row["in_patch_set_mismatches"] = ipsd
        row["max_abs_diff_all_columns"] = worst
        row["reproduces_1e-6"] = bool(np.isfinite(worst) and worst <= 1e-6 and ipsd == 0)
        ok = ok and row["reproduces_1e-6"]
        rows.append(row)
        print(f"[anchor] {task}/{sid}: rows {len(full)} vs {len(ref)}, "
              f"max abs diff {worst:.3g}, reproduces={row['reproduces_1e-6']}", flush=True)
    A = pd.DataFrame(rows)
    A.to_csv(f"{outdir}/p3_anchor_comparison.csv", index=False)
    print(f"[write] {outdir}/p3_anchor_comparison.csv")
    return bool(ok), A


# -------------------------------------------------------------------------------- geometry scan
def scan_geometry(cfg, outdir):
    root = cfg["repo_root"]
    rows = []
    for setname, s in cfg["sets"].items():
        ext = s["hest_ext_set"]
        for sid, pse_taskdef in sample_list(cfg, setname):
            ph = f"{root}/hest_ext/{ext}/patches/{sid}.h5"
            mj = f"{root}/hest_ext/{ext}/metadata/{sid}.json"
            half, src, extent, attrs, cross = patch_geometry(ph, mj, pse_fallback=pse_taskdef)
            A = ad.read_h5ad(f"{root}/hest_ext/{ext}/st/{sid}.h5ad", backed="r")
            bc = np.asarray(A.obs_names[:], dtype=object)
            xy = np.asarray(A.obsm["spatial"], dtype=np.float64)
            try:
                A.file.close()
            except Exception:
                pass
            rel = coord_relation(ph, {b: xy[i] for i, b in enumerate(bc)})
            rows.append(dict(set_name=setname, sample_id=sid, half_width_px=half,
                             geometry_source=src, patch_extent_px=extent,
                             pixel_size_um_taskdef=pse_taskdef,
                             extent_from_taskdef_pixel_size=112.0 / pse_taskdef,
                             n_spots_adata=len(bc),
                             patch_attrs=json.dumps(attrs, sort_keys=True), **cross, **rel))
    G = pd.DataFrame(rows)
    G.to_csv(f"{outdir}/p3_geometry_scan.csv", index=False)
    print(f"[write] {outdir}/p3_geometry_scan.csv ({len(G)} samples)")
    return G


def sample_list(cfg, setname):
    """Sample ids and the pixel size the project already recorded, from the named source.

    The pixel size is used only as a last-resort geometry fallback and as a cross-check
    against the patch file's own extent attribute; it is never the primary geometry.
    """
    s = cfg["sets"][setname]
    out = []
    if "task_def" in s:
        with open(f"{cfg['repo_root']}/{s['task_def']}") as fh:
            td = json.load(fh)
        for smp in td["samples"]:
            if s.get("population") and smp.get("population") != s["population"]:
                continue
            out.append((smp["sample_id"], float(smp["pixel_size_um"])))
    else:
        sel = pd.read_csv(f"{cfg['repo_root']}/{s['selection_csv']}")
        sel = sel[sel["set"] == s["selection_set"]]
        for r in sel.itertuples():
            out.append((str(r.sample_id), float(r.pixel_size_um_estimated)))
    out = sorted(out)
    assert len(out) == s["n_expected"], \
        f"{setname}: {len(out)} samples selected, expected {s['n_expected']}"
    return out


# ---------------------------------------------------------------------------------- expansion
SCHEMA = pa.schema([
    ("set_name", pa.string()),
    ("sample_id", pa.string()),
    ("barcode", pa.string()),
    ("n_nuclei", pa.int32()),
    ("area_mean", pa.float64()),
    ("area_median", pa.float64()),
    ("frac_connective", pa.float64()),
    ("frac_dead", pa.float64()),
    ("frac_epithelial", pa.float64()),
    ("frac_inflammatory", pa.float64()),
    ("frac_neoplastic", pa.float64()),
    ("n_neoplastic", pa.int32()),
    ("neo_area_mean", pa.float64()),
])

QS = [0.05, 0.25, 0.5, 0.75, 0.95]


def quantiles(v, prefix):
    out = {}
    q = np.quantile(np.asarray(v, dtype=np.float64), QS) if len(v) else [np.nan] * len(QS)
    for k, qq in zip(QS, q):
        out[f"{prefix}_q{int(k * 100):02d}"] = float(qq)
    out[f"{prefix}_mean"] = float(np.mean(v)) if len(v) else np.nan
    out[f"{prefix}_sd"] = float(np.std(v, ddof=1)) if len(v) > 1 else np.nan
    return out


def run_expand(cfg, mod, outdir, geom):
    root = cfg["repo_root"]
    gidx = {(r.set_name, r.sample_id): r for r in geom.itertuples()}
    summary, tables = [], {}
    for setname, s in cfg["sets"].items():
        ext = s["hest_ext_set"]
        frames = []
        for sid, pse in sample_list(cfg, setname):
            g = gidx[(setname, sid)]
            half, src = float(g.half_width_px), str(g.geometry_source)
            cvp = f"{root}/hest_ext/{ext}/cellvit_seg/{sid}_cellvit_seg.parquet"
            assert os.path.isfile(cvp), f"{sid}: no CellViT parquet at {cvp}"
            cx, cy, area, cls, n_nuc = read_cellvit(cvp, mod.EXPECTED)
            A = ad.read_h5ad(f"{root}/hest_ext/{ext}/st/{sid}.h5ad", backed="r")
            bc = np.asarray(A.obs_names[:], dtype=object)
            xy = np.asarray(A.obsm["spatial"], dtype=np.float64)
            try:
                A.file.close()
            except Exception:
                pass
            with h5py.File(f"{root}/hest_ext/{ext}/patches/{sid}.h5", "r") as f:
                patch_bc = set(decode(f["barcode"][:]))
            n_unpatched = int(sum(1 for b in bc if b not in patch_bc))
            # D1's subset criterion. A failure is recorded, not worked around: a patch barcode
            # with no expression row has no spot centre and so cannot get a morphology row.
            missing = sorted(patch_bc - set(bc))
            n_missing = len(missing)

            recs = spot_features(xy, cx, cy, area, cls, half, mod.EXPECTED, mod.CHUNK)
            full = assemble(recs, xy, bc, mod.EXPECTED)
            full.insert(0, "sample_id", sid)
            full.insert(0, "set_name", setname)
            keep = np.asarray([b in patch_bc for b in bc])
            sub = full.loc[keep].reset_index(drop=True)
            frames.append(sub)

            nn = sub["n_nuclei"].to_numpy()
            row = dict(set_name=setname, hest_ext_set=ext, sample_id=sid,
                       n_spots_expression=int(len(bc)),
                       n_patch_barcodes=int(len(patch_bc)),
                       n_patch_barcodes_without_expression=n_missing,
                       patch_barcodes_without_expression=";".join(missing[:10]),
                       subset_relation_holds=bool(n_missing == 0),
                       excluded_pending_oversight=bool(sid in cfg.get("flagged_samples", {})),
                       flag_note=cfg.get("flagged_samples", {}).get(sid, ""),
                       n_patched_spots=int(keep.sum()),
                       n_unpatched_spots=n_unpatched,
                       unpatched_fraction=float(n_unpatched / len(bc)),
                       n_nuclei_total=int(n_nuc),
                       nucleus_spot_pairs=int(nn.sum()),
                       spots_with_nuclei=int((nn > 0).sum()),
                       join_rate=float((nn > 0).mean()) if len(nn) else np.nan,
                       join_rate_over_all_patch_barcodes=float((nn > 0).sum() / len(patch_bc)),
                       half_width_px=half, patch_extent_px=2.0 * half,
                       geometry_source=src,
                       pixel_size_um_taskdef=pse,
                       extent_from_taskdef_pixel_size=112.0 / pse,
                       extent_ratio_attr_over_pixelsize=float(2.0 * half / (112.0 / pse)),
                       classes_present="|".join(sorted(np.unique(cls))),
                       coord_rel=str(getattr(g, "coord_rel", "")),
                       coord_direct_dx=float(getattr(g, "coord_direct_dx", np.nan)),
                       coord_direct_dy=float(getattr(g, "coord_direct_dy", np.nan)),
                       coord_swap_dx=float(getattr(g, "coord_swap_dx", np.nan)),
                       coord_swap_dy=float(getattr(g, "coord_swap_dy", np.nan)))
            row.update(quantiles(nn, "n_nuclei"))
            summary.append(row)
            print(f"  [{setname}/{sid}] {n_nuc:,} nuclei, half {half:.2f}px ({src}), "
                  f"{int(nn.sum()):,} pairs, join {row['join_rate']:.4f}, "
                  f"median {row['n_nuclei_q50']:.0f}", flush=True)
        tables[setname] = pd.concat(frames, ignore_index=True)

    # benchmark reference quantiles from morphology_v2, patched spots only
    for task in cfg["anchor_reference_tasks"]:
        M = pd.read_parquet(f"{root}/{cfg['morphology_v2_dir']}/{task}_morph.parquet")
        M = M[M["in_patch_set"]] if "in_patch_set" in M.columns else M
        for sid, gsub in M.groupby("sample_id"):
            nn = gsub["n_nuclei"].to_numpy()
            row = dict(set_name=f"benchmark_{task}", hest_ext_set="bench_data", sample_id=sid,
                       n_spots_expression=np.nan, n_patched_spots=int(len(nn)),
                       n_unpatched_spots=np.nan, unpatched_fraction=np.nan,
                       n_nuclei_total=np.nan, nucleus_spot_pairs=int(nn.sum()),
                       spots_with_nuclei=int((nn > 0).sum()),
                       join_rate=float((nn > 0).mean()),
                       half_width_px=np.nan, patch_extent_px=np.nan,
                       geometry_source="morphology_v2_reference",
                       pixel_size_um_taskdef=np.nan,
                       extent_from_taskdef_pixel_size=np.nan,
                       extent_ratio_attr_over_pixelsize=np.nan,
                       classes_present="", coord_rel="",
                       coord_direct_dx=np.nan, coord_direct_dy=np.nan,
                       coord_swap_dx=np.nan, coord_swap_dy=np.nan)
            row.update(quantiles(nn, "n_nuclei"))
            summary.append(row)

    S = pd.DataFrame(summary)
    # summary before the bulk tables
    S.to_csv(f"{outdir}/morphology_ext_summary.csv", index=False)
    print(f"[write] {outdir}/morphology_ext_summary.csv ({len(S)} rows)")

    pooled = []
    for setname, T in tables.items():
        nn = T["n_nuclei"].to_numpy()
        r = dict(set_name=setname, n_samples=int(T.sample_id.nunique()),
                 n_patched_spots=int(len(T)), nucleus_spot_pairs=int(nn.sum()),
                 join_rate=float((nn > 0).mean()))
        r.update(quantiles(nn, "n_nuclei"))
        pooled.append(r)
    for task in cfg["anchor_reference_tasks"]:
        M = pd.read_parquet(f"{root}/{cfg['morphology_v2_dir']}/{task}_morph.parquet")
        M = M[M["in_patch_set"]] if "in_patch_set" in M.columns else M
        nn = M["n_nuclei"].to_numpy()
        r = dict(set_name=f"benchmark_{task}", n_samples=int(M.sample_id.nunique()),
                 n_patched_spots=int(len(M)), nucleus_spot_pairs=int(nn.sum()),
                 join_rate=float((nn > 0).mean()))
        r.update(quantiles(nn, "n_nuclei"))
        pooled.append(r)
    P = pd.DataFrame(pooled)
    P.to_csv(f"{outdir}/morphology_ext_pooled.csv", index=False)
    print(f"[write] {outdir}/morphology_ext_pooled.csv")

    written = []
    for setname, T in tables.items():
        d = f"{root}/{cfg['out_morph_root']}/{setname}"
        os.makedirs(d, exist_ok=True)
        tbl = pa.Table.from_pandas(T[[f.name for f in SCHEMA]], schema=SCHEMA,
                                   preserve_index=False)
        pq.write_table(tbl, f"{d}/morphology.parquet")
        written.append((setname, d, len(T)))
        print(f"[write] {d}/morphology.parquet ({len(T):,} spot rows)")
    return S, P, written


# ------------------------------------------------------------------------------- provenance
def provenance(path, cfg, cfg_path, script_path, extra, name="PROVENANCE.txt"):
    def md5(p):
        h = hashlib.md5()
        with open(p, "rb") as fh:
            for b in iter(lambda: fh.read(1 << 20), b""):
                h.update(b)
        return h.hexdigest()

    cfg_bytes = open(cfg_path, "rb").read()
    lines = [
        f"job_id          : {os.environ.get('SLURM_JOB_ID', 'NA')}",
        f"partition_used  : {os.environ.get('SLURM_JOB_PARTITION', 'NA')}",
        f"node            : {platform.node()}",
        f"date            : {extra.get('date', '')}",
        f"commit          : {extra.get('commit', 'NA')}",
        f"command_line    : {' '.join(sys.argv)}",
        f"config_md5      : {hashlib.md5(cfg_bytes).hexdigest()}",
        f"config_path     : {cfg_path}",
        f"PYTHONHASHSEED  : {os.environ.get('PYTHONHASHSEED', 'unset')}",
        f"script_md5      : {md5(script_path)}   ({script_path})",
        f"builder_md5     : {md5(cfg['repo_root'] + '/' + cfg['builder'])}   ({cfg['builder']})",
        f"python          : {platform.python_version()}  {sys.executable}",
        f"numpy/pandas    : {np.__version__} / {pd.__version__}",
        f"geopandas/pyarrow: {gpd.__version__} / {pa.__version__}",
        "",
        "config it hashes:",
        cfg_bytes.decode(),
        "",
    ]
    for k, v in extra.items():
        if k not in ("date", "commit"):
            lines.append(f"{k}: {v}")
    with open(f"{path}/{name}", "w") as fh:
        fh.write("\n".join(lines) + "\n")


def stamp(path, note, frame_id, project_id, date):
    with open(f"{path}/_provenance.json", "w") as fh:
        json.dump(dict(writer="claude-science", project_id=project_id, frame_id=frame_id,
                       track="P3 morphology", plan="round4 stage P", note=note,
                       host=platform.node(), created_at=date), fh, indent=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=("anchor", "expand"))
    ap.add_argument("--config", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--geometry", default=None, help="expand: p3_geometry_scan.csv from anchor")
    a = ap.parse_args()

    with open(a.config) as fh:
        cfg = json.load(fh)
    os.makedirs(a.outdir, exist_ok=True)
    mod = load_builder(f"{cfg['repo_root']}/{cfg['builder']}")
    date = subprocess.run(["date", "-Is"], capture_output=True, text=True).stdout.strip()
    extra = dict(date=date, commit=cfg.get("commit", "NA"), stage=a.stage)

    if a.stage == "anchor":
        ok, A = run_anchor(cfg, mod, a.outdir)
        G = scan_geometry(cfg, a.outdir)
        extra["anchor_reproduces_1e-6"] = ok
        extra["anchor_max_abs_diff"] = float(A["max_abs_diff_all_columns"].max())
        extra["geometry_sources"] = dict(G.geometry_source.value_counts()).__str__()
        provenance(a.outdir, cfg, a.config, os.path.abspath(__file__), extra,
                   name="PROVENANCE__p3_anchor.txt")
        stamp(a.outdir, "P3 anchor: morphology builder against morphology_v2 on two benchmark "
                        "samples, plus the expansion samples' patch geometry",
              cfg["frame_id"], cfg["project_id"], date)
        if not ok:
            print("[STOP] anchor did not reproduce morphology_v2 to 1e-6; "
                  "the builder is NOT adjusted. Expansion not run.", flush=True)
            sys.exit(3)
        print("[ok] anchor reproduces morphology_v2 to 1e-6 on every column.", flush=True)
        return

    assert a.geometry, "--geometry is required for --stage expand"
    G = pd.read_csv(a.geometry)
    S, P, written = run_expand(cfg, mod, a.outdir, G)
    extra["sets_written"] = "; ".join(f"{s}:{n} rows -> {d}" for s, d, n in written)
    extra["min_join_rate_expansion"] = float(
        S.loc[~S.set_name.str.startswith("benchmark_"), "join_rate"].min())
    provenance(a.outdir, cfg, a.config, os.path.abspath(__file__), extra,
               name="PROVENANCE__p3_expand.txt")
    stamp(a.outdir, "P3 expansion: per-spot CellViT morphology summary for the Indiana kidney "
                    "and breast Xenium sets", cfg["frame_id"], cfg["project_id"], date)
    for setname, d, n in written:
        provenance(d, cfg, a.config, os.path.abspath(__file__),
                   dict(extra, set_name=setname, n_rows=n))
        stamp(d, f"P3 expansion morphology parquet for set {setname}",
              cfg["frame_id"], cfg["project_id"], date)


if __name__ == "__main__":
    main()
