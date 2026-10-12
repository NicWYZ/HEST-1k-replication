"""Round 6 cheatsheet track, C0.3: build the data package on Longleaf.

Runs from a `git archive` copy of the track's commit (see
round6_cheatsheet_package.sbatch), inside the job's own output directory,
and reads the project tree read-only. It writes everything the cloud
container needs and nothing blinded: blinding happens when trial directories
are built in the container.

Inputs (project tree, read only)
  bench_data/SKCM/adata/{sid}.h5ad          raw counts, 541 genes
  bench_data/SKCM/patches/{sid}.h5          img (n,224,224,3) uint8, barcode, coords
  bench_data/SKCM/splits/{train,test}_{0,1}.csv
  bench_data/SKCM/var_50genes.json
  embeddings/SKCM/{uni_v2,hoptimus1}/{sid}.h5

The target is the round-1 faithful pipeline's: HEST benchmark.py's
normalize=True applies log1p only to the 50-gene subset of the raw counts,
rows aligned to the embedding file's barcodes. That is rebuilt here exactly as
code/scripts/verify_row_identity.py rebuild() does, which matched benchmark.py
to 8.9e-16 on SKCM (results/tailored/integrity/row_identity_check.csv).

The spot universe of each slide is the set of spots that have a benchmark
patch (and therefore an embedding). That is fewer than the inventory's spots
under tissue, and the counts are written to package_summary.json.

Outputs, in the current directory under package/
  genes.json                      the 50 genes, in var_50genes.json order
  S1_spots.parquet, S2_spots.parquet   barcode, row order, coords in full-res
                                  px, x_um, y_um, in_tissue, and for S1 the
                                  block, held-out flag, eligibility and S1*
  S1_target.parquet, S2_target.parquet barcode + 50 genes, log1p(count)
  S1_counts.parquet, S2_counts.parquet barcode + 50 genes, raw counts
  {S1,S2}_{uni_v2,hoptimus1}.npy  float32 embeddings in *_spots row order
  S1_patches_*.tar                every S1 patch as PNG, named {barcode}.png
  S2star_patches_*.tar            the 500 S2* patches as PNG
  S1_overview.png, overview.json  the patch mosaic of S1 (see below)
  splits.json                     which slide each round-1 split trains/tests on
  package_summary.json            counts, shares, bounding box, pixel sizes
  MANIFEST.tsv                    md5 and bytes of every file above

The overview. No whole-slide image or thumbnail of these two samples was ever
downloaded to Longleaf (round3_d1_download.py, round4_data_download.py:
"never wsis/"), so the low-resolution image of the section is built as a
mosaic of the S1 patches, each pasted at its position and downsampled, with
white where there is no patch. overview.json gives its origin and scale in
micrometres so the container can mask blocks in the same frame.
"""
import argparse
import datetime
import hashlib
import io
import json
import os
import platform
import socket
import sys
import tarfile
import zlib

import h5py
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from PIL import Image

PROJECT_ID = "proj_3a4e23273fb6"
TASK = "SKCM"
S1, S2 = "TENX115", "TENX117"
ENCODERS = ("uni_v2", "hoptimus1")
GRID = 4
BUFFER_UM = 165.0
N_STAR = 500
PATCH_UM = 112.0
OVERVIEW_LONG_SIDE = 1500
SHARD_BYTES = 90 * 1024 * 1024


def md5(path, chunk=1 << 20):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def seed_of(key):
    return zlib.crc32(key.encode())


def decode(arr):
    return [x.decode() if isinstance(x, (bytes, np.bytes_)) else str(x) for x in np.asarray(arr).reshape(-1)]


def read_patches(path):
    with h5py.File(path, "r") as f:
        bk = "barcode" if "barcode" in f else "barcodes"
        ik = "img" if "img" in f else "imgs"
        bc = decode(f[bk][:])
        coords = np.asarray(f["coords"][:], dtype=np.float64)
        attrs = {k: (v.item() if hasattr(v, "item") else v) for k, v in f[ik].attrs.items()}
        imgs = f[ik][:]
    return bc, coords, imgs, attrs


def read_embeddings(path):
    with h5py.File(path, "r") as f:
        bk = "barcodes" if "barcodes" in f else "barcode"
        return decode(f[bk][:]), np.asarray(f["embeddings"][:], dtype=np.float32)


def load_target(adata_path, barcodes, genes):
    """verify_row_identity.rebuild(): log1p of raw counts, adata[barcodes, genes]."""
    import anndata as ad
    A = ad.read_h5ad(adata_path)
    sub = A[barcodes, genes]
    X = sub.X.toarray() if hasattr(sub.X, "toarray") else np.asarray(sub.X)
    counts = np.asarray(X, dtype=np.float64)
    target = np.log1p(counts)
    check = None
    try:
        import scanpy as sc
        B = ad.read_h5ad(adata_path)
        sc.pp.log1p(B)
        sb = B[barcodes, genes]
        Y = sb.X.toarray() if hasattr(sb.X, "toarray") else np.asarray(sb.X)
        check = float(np.max(np.abs(np.asarray(Y, dtype=np.float64) - target)))
    except ImportError:
        pass
    obs = A.obs.loc[barcodes]
    return counts, target, obs, A.n_obs, check


def write_parquet(df, path):
    fields = []
    for c in df.columns:
        t = pd.api.types
        if t.is_bool_dtype(df[c]):
            fields.append(pa.field(c, pa.bool_()))
        elif t.is_integer_dtype(df[c]):
            fields.append(pa.field(c, pa.int64()))
        elif t.is_float_dtype(df[c]):
            fields.append(pa.field(c, pa.float64()))
        else:
            fields.append(pa.field(c, pa.string()))
    schema = pa.schema(fields)
    pq.write_table(pa.Table.from_pandas(df, schema=schema, preserve_index=False), path)


def png_bytes(img):
    buf = io.BytesIO()
    Image.fromarray(np.asarray(img, dtype=np.uint8)).save(buf, format="PNG", optimize=False)
    return buf.getvalue()


def write_shards(prefix, names, imgs, outdir):
    """PNG patches into tar shards of at most SHARD_BYTES each."""
    paths, k, size, tf = [], 0, 0, None
    for name, img in zip(names, imgs):
        data = png_bytes(img)
        if tf is None or size + len(data) + 1024 > SHARD_BYTES:
            if tf is not None:
                tf.close()
            k += 1
            p = os.path.join(outdir, f"{prefix}_{k:02d}.tar")
            tf = tarfile.open(p, "w")
            paths.append(p)
            size = 0
        ti = tarfile.TarInfo(name=f"{name}.png")
        ti.size = len(data)
        ti.mtime = 0
        tf.addfile(ti, io.BytesIO(data))
        size += len(data) + 1024
    if tf is not None:
        tf.close()
    return paths


def blocks_for(x_um, y_um, bbox):
    """4x4 grid over the bounding box. i indexes rows (y), j columns (x)."""
    x0, y0, x1, y1 = bbox
    bw, bh = (x1 - x0) / GRID, (y1 - y0) / GRID
    j = np.clip(((x_um - x0) // bw).astype(int), 0, GRID - 1)
    i = np.clip(((y_um - y0) // bh).astype(int), 0, GRID - 1)
    heldout = ((i + j) % 2) == 1
    # distance from the spot to the nearest edge of its own block, all four edges
    dx = np.minimum(x_um - (x0 + j * bw), (x0 + (j + 1) * bw) - x_um)
    dy = np.minimum(y_um - (y0 + i * bh), (y0 + (i + 1) * bh) - y_um)
    d_any = np.minimum(dx, dy)
    # distance to the nearest edge shared with another block (internal edges only)
    inf = np.inf
    dl = np.where(j > 0, x_um - (x0 + j * bw), inf)
    dr = np.where(j < GRID - 1, (x0 + (j + 1) * bw) - x_um, inf)
    dt = np.where(i > 0, y_um - (y0 + i * bh), inf)
    db = np.where(i < GRID - 1, (y0 + (i + 1) * bh) - y_um, inf)
    d_internal = np.minimum.reduce([dl, dr, dt, db])
    return i, j, heldout, d_any, d_internal, (bw, bh)


def axis_check(coords, imgs, um_per_px, n_pairs=300, seed_key="round6-axis-check"):
    """Which column of coords is the image x axis? Neighbouring patches overlap, so
    under the right reading their shared pixels agree. Returns the mean absolute
    pixel difference over the overlaps for (col0 = x) and (col1 = x)."""
    rng = np.random.default_rng(seed_of(seed_key))
    scale = um_per_px / 0.5  # full-res px -> patch px
    res = {}
    for name, (cx, cy) in (("col0_is_x", (0, 1)), ("col1_is_x", (1, 0))):
        diffs = []
        order = rng.permutation(len(coords))[:n_pairs]
        for a in order:
            d = np.hypot(*(coords - coords[a]).T) * scale
            d[a] = np.inf
            b = int(np.argmin(d))
            dx = int(round((coords[b, cx] - coords[a, cx]) * scale))
            dy = int(round((coords[b, cy] - coords[a, cy]) * scale))
            if abs(dx) >= 200 or abs(dy) >= 200:
                continue
            A = imgs[a].astype(np.int16)
            B = imgs[b].astype(np.int16)
            ya, xa = max(0, dy), max(0, dx)
            yb, xb = max(0, -dy), max(0, -dx)
            h, w = 224 - abs(dy), 224 - abs(dx)
            diffs.append(np.abs(A[ya:ya + h, xa:xa + w] - B[yb:yb + h, xb:xb + w]).mean())
        res[name] = (float(np.mean(diffs)) if diffs else None, len(diffs))
    return res


def overview(x_um, y_um, imgs, bbox):
    """Mosaic of patches. Returns the image and its frame (origin, um per px)."""
    half = PATCH_UM / 2
    ox, oy = bbox[0] - half, bbox[1] - half
    w_um, h_um = bbox[2] - bbox[0] + PATCH_UM, bbox[3] - bbox[1] + PATCH_UM
    um_per_px = max(w_um, h_um) / OVERVIEW_LONG_SIDE
    W, H = int(np.ceil(w_um / um_per_px)), int(np.ceil(h_um / um_per_px))
    canvas = Image.new("RGB", (W, H), (255, 255, 255))
    side = max(1, int(round(PATCH_UM / um_per_px)))
    for x, y, img in zip(x_um, y_um, imgs):
        tile = Image.fromarray(np.asarray(img, dtype=np.uint8)).resize((side, side), Image.BILINEAR)
        canvas.paste(tile, (int(round((x - half - ox) / um_per_px)), int(round((y - half - oy) / um_per_px))))
    frame = {"origin_x_um": ox, "origin_y_um": oy, "um_per_px": um_per_px, "width_px": W,
             "height_px": H, "patch_side_px": side, "built_from": "mosaic of S1 benchmark patches"}
    return canvas, frame


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--proj", required=True, help="project tree root (read only)")
    ap.add_argument("--out", default="package")
    ap.add_argument("--frame-id", required=True)
    a = ap.parse_args()
    bd = os.path.join(a.proj, "bench_data", TASK)
    emb = os.path.join(a.proj, "embeddings", TASK)
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=False)
    summary = {"task": TASK, "S1": S1, "S2": S2}

    genes = json.load(open(os.path.join(bd, "var_50genes.json")))["genes"]
    assert len(genes) == 50 and len(set(genes)) == 50
    json.dump({"genes": genes}, open(os.path.join(out, "genes.json"), "w"), indent=1)

    splits = {}
    for k in (0, 1):
        tr = pd.read_csv(os.path.join(bd, "splits", f"train_{k}.csv"))
        te = pd.read_csv(os.path.join(bd, "splits", f"test_{k}.csv"))
        sid = lambda df: [os.path.basename(p).replace(".h5ad", "") for p in df["expr_path"]]
        splits[f"split{k}"] = {"train": sid(tr), "test": sid(te)}
    json.dump(splits, open(os.path.join(out, "splits.json"), "w"), indent=1)
    summary["splits"] = splits

    slides = {}
    for tag, sid in (("S1", S1), ("S2", S2)):
        bc, coords, imgs, attrs = read_patches(os.path.join(bd, "patches", f"{sid}.h5"))
        assert len(set(bc)) == len(bc), f"{sid}: duplicated patch barcodes"
        assert imgs.shape[1:] == (224, 224, 3) and imgs.dtype == np.uint8, imgs.shape
        embs = {}
        for enc in ENCODERS:
            ebc, E = read_embeddings(os.path.join(emb, enc, f"{sid}.h5"))
            assert set(ebc) == set(bc), f"{sid} {enc}: embedding barcodes differ from patch barcodes"
            pos = {b: r for r, b in enumerate(ebc)}
            embs[enc] = E[[pos[b] for b in bc]]
        counts, target, obs, n_obs, check = load_target(os.path.join(bd, "adata", f"{sid}.h5ad"), bc, genes)
        slides[tag] = dict(sid=sid, bc=bc, coords=coords, imgs=imgs, attrs=attrs, embs=embs,
                           counts=counts, target=target, obs=obs, n_obs=n_obs)
        summary[f"{tag}_n_adata_obs"] = int(n_obs)
        summary[f"{tag}_n_patched_spots"] = len(bc)
        summary[f"{tag}_patch_attrs"] = {k: str(v) for k, v in attrs.items()}
        summary[f"{tag}_log1p_scanpy_maxabsdiff"] = check
        summary[f"{tag}_in_tissue_all"] = bool(np.all(obs["in_tissue"].to_numpy() == 1)) if "in_tissue" in obs else None

    # pixel size: patch extent is 112 um and patch_size is that extent in full-res px
    for tag in ("S1", "S2"):
        s = slides[tag]
        ps = float(s["attrs"]["patch_size"]) if "patch_size" in s["attrs"] else None
        s["um_per_fullres_px"] = PATCH_UM / ps if ps else None
        summary[f"{tag}_um_per_fullres_px_from_patch_size"] = s["um_per_fullres_px"]
    summary["coords_frame"] = ("bench patch h5 'coords', full-resolution pixels of the HEST image, patch box "
                               "centres, column 0 = x and column 1 = y as stored; x_um = coords * um_per_fullres_px")

    # S1 blocks, eligibility and S1*
    s1 = slides["S1"]
    for tag in ("S1", "S2"):
        s = slides[tag]
        chk = axis_check(s["coords"], s["imgs"], s["um_per_fullres_px"])
        summary[f"{tag}_axis_check_mean_abs_diff_and_pairs"] = chk
        if chk["col1_is_x"][0] is not None and chk["col0_is_x"][0] is not None \
                and chk["col1_is_x"][0] < chk["col0_is_x"][0]:
            s["coords"] = s["coords"][:, ::-1].copy()
            summary[f"{tag}_coords_swapped"] = True
        else:
            summary[f"{tag}_coords_swapped"] = False
    x_um = s1["coords"][:, 0] * s1["um_per_fullres_px"]
    y_um = s1["coords"][:, 1] * s1["um_per_fullres_px"]
    bbox = (float(x_um.min()), float(y_um.min()), float(x_um.max()), float(y_um.max()))
    i, j, held, d_any, d_int, (bw, bh) = blocks_for(x_um, y_um, bbox)
    eligible = held & (d_any >= BUFFER_UM)
    elig_bc = sorted(np.asarray(s1["bc"])[eligible].tolist())
    # fewer eligible spots than N_STAR is recorded, not fixed here: S1* is then every eligible spot
    n_star1 = min(N_STAR, len(elig_bc))
    summary["S1star_short_of_500"] = len(elig_bc) < N_STAR
    star1 = set(np.random.default_rng(seed_of("round6-S1star")).choice(elig_bc, n_star1, replace=False).tolist())
    n = len(s1["bc"])
    summary.update({
        "S1_bbox_um_xmin_ymin_xmax_ymax": bbox, "S1_block_w_um": bw, "S1_block_h_um": bh,
        "S1_n_training": int((~held).sum()), "S1_n_heldout": int(held.sum()),
        "S1_share_training": float((~held).sum() / n), "S1_share_heldout": float(held.sum() / n),
        "S1_n_eligible_all_edges": int(eligible.sum()),
        "S1_n_eligible_internal_edges_only": int((held & (d_int >= BUFFER_UM)).sum()),
        "S1_buffer_rule": "held-out spots whose centre is within 165 um of any edge of their own block are not eligible",
        "S1star_seed": seed_of("round6-S1star"), "S2star_seed": seed_of("round6-S2star"),
    })
    s1_spots = pd.DataFrame({
        "barcode": s1["bc"], "row": np.arange(n), "x_fullres": s1["coords"][:, 0], "y_fullres": s1["coords"][:, 1],
        "x_um": x_um, "y_um": y_um, "in_tissue": s1["obs"]["in_tissue"].to_numpy().astype(np.int64),
        "block_i": i.astype(np.int64), "block_j": j.astype(np.int64), "heldout": held,
        "dist_edge_um": d_any, "dist_internal_edge_um": d_int, "eligible": eligible,
        "in_S1star": np.array([b in star1 for b in s1["bc"]]),
    })

    s2 = slides["S2"]
    s2_sorted = sorted(s2["bc"])
    star2 = set(np.random.default_rng(seed_of("round6-S2star")).choice(s2_sorted, N_STAR, replace=False).tolist())
    m = len(s2["bc"])
    s2_spots = pd.DataFrame({
        "barcode": s2["bc"], "row": np.arange(m), "x_fullres": s2["coords"][:, 0], "y_fullres": s2["coords"][:, 1],
        "x_um": s2["coords"][:, 0] * s2["um_per_fullres_px"], "y_um": s2["coords"][:, 1] * s2["um_per_fullres_px"],
        "in_tissue": s2["obs"]["in_tissue"].to_numpy().astype(np.int64),
        "in_S2star": np.array([b in star2 for b in s2["bc"]]),
    })

    files = []
    for tag, spots, s in (("S1", s1_spots, s1), ("S2", s2_spots, s2)):
        p = os.path.join(out, f"{tag}_spots.parquet"); write_parquet(spots, p); files.append(p)
        for kind, M in (("target", s["target"]), ("counts", s["counts"])):
            df = pd.DataFrame(M, columns=genes); df.insert(0, "barcode", s["bc"])
            p = os.path.join(out, f"{tag}_{kind}.parquet"); write_parquet(df, p); files.append(p)
        for enc in ENCODERS:
            p = os.path.join(out, f"{tag}_{enc}.npy"); np.save(p, s["embs"][enc]); files.append(p)
    files += write_shards("S1_patches", s1["bc"], s1["imgs"], out)
    idx2 = [r for r, b in enumerate(s2["bc"]) if b in star2]
    files += write_shards("S2star_patches", [s2["bc"][r] for r in idx2], s2["imgs"][idx2], out)

    ov, frame = overview(x_um, y_um, s1["imgs"], bbox)
    p = os.path.join(out, "S1_overview.png"); ov.save(p); files.append(p)
    p = os.path.join(out, "overview.json"); json.dump(frame, open(p, "w"), indent=1); files.append(p)

    summary["n_S1star"] = len(star1)
    summary["n_S2star"] = len(star2)
    summary["created_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    p = os.path.join(out, "package_summary.json"); json.dump(summary, open(p, "w"), indent=1, default=str)
    files += [os.path.join(out, "genes.json"), os.path.join(out, "splits.json"), p]

    with open(os.path.join(out, "MANIFEST.tsv"), "w") as fh:
        fh.write("file\tbytes\tmd5\n")
        for f in sorted(set(files)):
            sz = os.path.getsize(f)
            assert sz <= 95 * 1024 * 1024, f"{f} is {sz} bytes"
            fh.write(f"{os.path.basename(f)}\t{sz}\t{md5(f)}\n")
    print(json.dumps(summary, indent=1, default=str))


if __name__ == "__main__":
    main()
