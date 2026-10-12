"""Round 6 extension, cheatsheet track, C4.3: build the data package on Longleaf.

Runs from a `git archive` copy of the track's commit (see
round6_cheatsheet_ext_package.sbatch), inside the job's own output directory,
and reads the project tree read-only. Nothing here is blinded. Blinding
happens when trial directories are built on the Mac.

Inputs (project tree, read only)
  bench_data/CCRCC/adata/{sid}.h5ad      raw counts
  bench_data/CCRCC/patches/{sid}.h5      img (n,224,224,3) uint8, barcode, coords
  bench_data/CCRCC/splits/{train,test}_{0..5}.csv
  bench_data/CCRCC/var_50genes.json
  embeddings/CCRCC/{uni_v2,virchow2}/{sid}.h5
  results/round3/D0_inventory/hest_inventory.csv   subseries, spots under tissue
  code/HEST/assets/HEST_v1_1_0.csv                 HEST's own metadata

The target is the round-1 faithful pipeline's, log1p of the raw counts of the
50 genes of var_50genes.json, rows aligned to the patch file's barcodes, rebuilt
as code/scripts/verify_row_identity.py rebuild() does and as round 6's package
did (round6_cheatsheet_package.py load_target, reused unchanged).

Steps, in the order of instruction section 6.1
  1. the 12 FFPE slides, confirmed from both metadata tables
  2. the draw of 10 slides and the draw of 3 test slides
  3. per slide, k-means strata on the standardised target and the 500-spot sample
  4. the representativeness check, every value recorded
  5. patches of the sampled spots as PNG, positions, targets, the overview
     mosaic of every patched spot, and both encoders' embeddings of every
     patched spot

Outputs, in the current directory under package/
  genes.json, draws.json, splits.json, ffpe_check.csv
  strata.csv                 per slide and cluster: size, share, floor, allocation
  representativeness.csv     per slide and gene: the four moments and the two tests
  {sid}_spots.parquet        every patched spot: barcode, row, position, cluster, sampled
  {sid}_target.parquet       barcode + 50 genes, log1p(count), every patched spot
  {sid}_counts.parquet       barcode + 50 genes, raw counts, every patched spot
  {sid}_{uni_v2,virchow2}.npy  float32 embeddings in {sid}_spots row order
  {sid}_patches.tar          the 500 sampled patches as PNG, named {barcode}.png
  {sid}_overview.png         mosaic of every patched spot, long side 1,500 px
  overview.json              each mosaic's origin and scale
  package_summary.json       counts, pixel sizes, axis checks, escalations
  MANIFEST.tsv               md5 and bytes of every file above
"""
import argparse
import datetime
import hashlib
import io
import json
import os
import tarfile
import zlib

import h5py
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from PIL import Image

TASK = "CCRCC"
ENCODERS = ("uni_v2", "virchow2")
N_SLIDES, N_TEST, N_SAMPLE, K_STRATA = 10, 3, 500, 8
MIN_SHARE, FLOOR = 0.02, 10
PATCH_UM = 112.0
OVERVIEW_LONG_SIDE = 1500
MAX_BAD_GENES = 5


def int_key(sid):
    return int(sid[3:])


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



def write_tar(path, names, imgs):
    with tarfile.open(path, "w") as tf:
        for name, img in zip(names, imgs):
            data = png_bytes(img)
            ti = tarfile.TarInfo(name=f"{name}.png")
            ti.size = len(data)
            ti.mtime = 0
            tf.addfile(ti, io.BytesIO(data))


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



def overview(x_um, y_um, imgs):
    """Mosaic of every patched spot. Returns the image and its frame."""
    half = PATCH_UM / 2
    bbox = (float(x_um.min()), float(y_um.min()), float(x_um.max()), float(y_um.max()))
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
             "height_px": H, "patch_side_px": side, "bbox_um": bbox,
             "built_from": "mosaic of every benchmark patch of the slide"}
    return canvas, frame


def ffpe_set(proj):
    """The FFPE slides of the task, read from both metadata tables."""
    inv = pd.read_csv(os.path.join(proj, "results/round3/D0_inventory/hest_inventory.csv"), low_memory=False)
    inv = inv[inv["benchmark_task"].astype(str) == TASK] if (inv["benchmark_task"].astype(str) == TASK).any() \
        else inv[inv["dataset_title"].astype(str).str.contains("Tertiary lymphoid structures generate")]
    meta = pd.read_csv(os.path.join(proj, "code/HEST/assets/HEST_v1_1_0.csv"), low_memory=False)
    meta = meta.set_index("id")
    rows = []
    for _, r in inv.sort_values("id", key=lambda s: s.map(int_key)).iterrows():
        sid = r["id"]
        m = meta.loc[sid] if sid in meta.index else None
        rows.append({
            "sample_id": sid, "inventory_subseries": r["subseries"],
            "inventory_preservation_method": r.get("preservation_method"),
            "inventory_patient": r.get("patient"), "inventory_spots_under_tissue": r.get("spots_under_tissue"),
            "hest_subseries": None if m is None else m.get("subseries"),
            "hest_preservation_method": None if m is None else m.get("preservation_method"),
            "hest_patient": None if m is None else m.get("patient"),
            "ffpe_by_inventory_subseries": "ffpe" in str(r["subseries"]).lower(),
            "ffpe_by_hest_subseries": m is not None and "ffpe" in str(m.get("subseries")).lower(),
            "ffpe_by_hest_preservation": m is not None and "ffpe" in str(m.get("preservation_method")).lower(),
        })
    return pd.DataFrame(rows)


def allocate(sizes):
    """Floors and largest-remainder allocation of N_SAMPLE over the clusters."""
    sizes = np.asarray(sizes, dtype=np.int64)
    n = int(sizes.sum())
    floors = np.where(sizes >= MIN_SHARE * n, np.minimum(FLOOR, sizes), 0)
    rest = N_SAMPLE - int(floors.sum())
    beyond = sizes - floors
    quota = rest * beyond / beyond.sum()
    base = np.floor(quota).astype(np.int64)
    left = rest - int(base.sum())
    # ties in the remainder go to the cluster listed first
    order = np.argsort(-(quota - base), kind="stable")
    base[order[:left]] += 1
    alloc = floors + base
    assert alloc.sum() == N_SAMPLE and np.all(alloc <= sizes), (alloc, sizes)
    return floors, alloc


def strata_and_sample(sid, bc, target):
    """k-means strata on the standardised target, then the 500-spot sample."""
    from sklearn.cluster import KMeans
    sd = target.std(axis=0)
    Z = (target - target.mean(axis=0)) / np.where(sd > 0, sd, 1.0)
    # rows in barcode order, so the clustering does not depend on file order
    order = np.argsort(np.asarray(bc))
    km = KMeans(n_clusters=K_STRATA, n_init=10, random_state=seed_of(f"round6ext-strata-{sid}")).fit(Z[order])
    raw = np.empty(len(bc), dtype=np.int64)
    raw[order] = km.labels_
    # clusters are numbered by their smallest barcode, which fixes their order
    bc_arr = np.asarray(bc)
    firsts = sorted((min(bc_arr[raw == c].tolist()), int(c)) for c in np.unique(raw))
    relabel = {c: k for k, (_, c) in enumerate(firsts)}
    lab = np.array([relabel[c] for c in raw])
    sizes = np.bincount(lab, minlength=len(firsts))
    floors, alloc = allocate(sizes)
    rng = np.random.default_rng(seed_of(f"round6ext-sample-{sid}"))
    chosen = set()
    for c in range(len(sizes)):
        members = sorted(bc_arr[lab == c].tolist())
        if alloc[c]:
            chosen.update(rng.choice(members, int(alloc[c]), replace=False).tolist())
    assert len(chosen) == N_SAMPLE
    table = pd.DataFrame({"sample_id": sid, "cluster": np.arange(len(sizes)), "n_spots": sizes,
                          "share": sizes / sizes.sum(), "floor": floors, "allocated": alloc})
    return lab, np.array([b in chosen for b in bc]), table


def representativeness(sid, genes, target, sampled):
    full_m, full_s = target.mean(axis=0), target.std(axis=0)
    sam_m, sam_s = target[sampled].mean(axis=0), target[sampled].std(axis=0)
    with np.errstate(divide="ignore", invalid="ignore"):
        dm = np.abs(sam_m - full_m) / full_s
        ratio = sam_s / full_s
    ok_m = np.where(full_s > 0, dm <= 0.1, sam_m == full_m)
    ok_s = np.where(full_s > 0, (ratio >= 0.9) & (ratio <= 1.1), sam_s == 0)
    return pd.DataFrame({"sample_id": sid, "gene": genes, "mean_all": full_m, "sd_all": full_s,
                         "mean_sample": sam_m, "sd_sample": sam_s, "abs_mean_diff_over_sd": dm,
                         "sd_ratio": ratio, "mean_ok": ok_m, "sd_ok": ok_s, "gene_ok": ok_m & ok_s})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--proj", required=True, help="project tree root (read only)")
    ap.add_argument("--out", default="package")
    a = ap.parse_args()
    bd = os.path.join(a.proj, "bench_data", TASK)
    emb = os.path.join(a.proj, "embeddings", TASK)
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=False)
    summary = {"task": TASK, "escalations": []}
    files = []

    def keep(name):
        p = os.path.join(out, name)
        files.append(p)
        return p

    genes = json.load(open(os.path.join(bd, "var_50genes.json")))["genes"]
    assert len(genes) == 50 and len(set(genes)) == 50
    json.dump({"genes": genes}, open(keep("genes.json"), "w"), indent=1)

    splits = {}
    for k in range(6):
        tr = pd.read_csv(os.path.join(bd, "splits", f"train_{k}.csv"))
        te = pd.read_csv(os.path.join(bd, "splits", f"test_{k}.csv"))
        splits[f"split{k}"] = {"train": tr["sample_id"].tolist(), "test": te["sample_id"].tolist()}
    json.dump(splits, open(keep("splits.json"), "w"), indent=1)

    # 1. the FFPE set, from both tables
    chk = ffpe_set(a.proj)
    chk.to_csv(keep("ffpe_check.csv"), index=False)
    assert len(chk) == 24, len(chk)
    agree = chk["ffpe_by_inventory_subseries"] == chk["ffpe_by_hest_subseries"]
    assert agree.all(), chk[~agree]
    ffpe = sorted(chk.loc[chk["ffpe_by_inventory_subseries"], "sample_id"].tolist(), key=int_key)
    assert len(ffpe) == 12, ffpe
    summary["ffpe_slides"] = ffpe
    summary["ffpe_hest_preservation_values"] = sorted(
        chk.loc[chk["sample_id"].isin(ffpe), "hest_preservation_method"].astype(str).unique().tolist())
    summary["frozen_hest_preservation_values"] = sorted(
        chk.loc[~chk["sample_id"].isin(ffpe), "hest_preservation_method"].astype(str).unique().tolist())
    summary["ffpe_patients_distinct"] = int(chk.loc[chk["sample_id"].isin(ffpe), "hest_patient"].nunique())

    # 2. the two draws
    s_slides, s_split = seed_of("round6ext-slides"), seed_of("round6ext-split")
    ten = sorted(np.random.default_rng(s_slides).choice(ffpe, N_SLIDES, replace=False).tolist(), key=int_key)
    test = sorted(np.random.default_rng(s_split).choice(ten, N_TEST, replace=False).tolist(), key=int_key)
    train = [s for s in ten if s not in test]
    draws = {"ffpe": ffpe, "seed_slides": s_slides, "slides": ten, "left_out": [s for s in ffpe if s not in ten],
             "seed_split": s_split, "test": test, "train": train,
             "call": "numpy.random.default_rng(seed).choice(list sorted by the number after INT, size, replace=False)",
             "numpy": np.__version__}
    json.dump(draws, open(keep("draws.json"), "w"), indent=1)
    summary["draws"] = draws

    # 3 to 5, slide by slide
    inv_spots = dict(zip(chk["sample_id"], chk["inventory_spots_under_tissue"]))
    strata, rep, frames, per_slide = [], [], {}, {}
    for sid in ten:
        bc, coords, imgs, attrs = read_patches(os.path.join(bd, "patches", f"{sid}.h5"))
        assert len(set(bc)) == len(bc), f"{sid}: duplicated patch barcodes"
        assert imgs.shape[1:] == (224, 224, 3) and imgs.dtype == np.uint8, imgs.shape
        info = {"n_patched_spots": len(bc), "inventory_spots_under_tissue": int(inv_spots[sid]),
                "patch_attrs": {k: str(v) for k, v in attrs.items()},
                "role": "test" if sid in test else "train"}
        if len(bc) != int(inv_spots[sid]):
            info["note"] = "patched spots differ from the inventory's spots under tissue"
        embs = {}
        for enc in ENCODERS:
            ebc, E = read_embeddings(os.path.join(emb, enc, f"{sid}.h5"))
            assert set(ebc) == set(bc) and len(ebc) == len(bc), f"{sid} {enc}: embedding barcodes differ"
            pos = {b: r for r, b in enumerate(ebc)}
            embs[enc] = E[[pos[b] for b in bc]]
            info[f"{enc}_dim"] = int(E.shape[1])
        counts, target, obs, n_obs, check = load_target(os.path.join(bd, "adata", f"{sid}.h5ad"), bc, genes)
        info["n_adata_obs"] = int(n_obs)
        info["log1p_scanpy_maxabsdiff"] = check
        info["counts_are_integers"] = bool(np.all(counts == np.round(counts)))
        info["counts_min_max"] = [float(counts.min()), float(counts.max())]
        ps = float(attrs["patch_size"]) if "patch_size" in attrs else None
        um_px = PATCH_UM / ps if ps else None
        info["um_per_fullres_px_from_patch_size"] = um_px
        info["patch_um_per_px"] = PATCH_UM / 224
        assert um_px, f"{sid}: no patch_size attribute, pixel size cannot be confirmed"
        ax = axis_check(coords, imgs, um_px, seed_key=f"round6ext-axis-check-{sid}")
        info["axis_check_mean_abs_diff_and_pairs"] = ax
        swapped = ax["col1_is_x"][0] is not None and ax["col0_is_x"][0] is not None \
            and ax["col1_is_x"][0] < ax["col0_is_x"][0]
        if swapped:
            coords = coords[:, ::-1].copy()
        info["coords_swapped"] = bool(swapped)
        x_um, y_um = coords[:, 0] * um_px, coords[:, 1] * um_px

        lab, sampled, table = strata_and_sample(sid, bc, target)
        strata.append(table)
        r = representativeness(sid, genes, target, sampled)
        rep.append(r)
        bad = int((~r["gene_ok"]).sum())
        info["genes_failing_representativeness"] = bad
        info["genes_constant_over_sample"] = [g for g, s in zip(genes, r["sd_sample"]) if s == 0]
        if bad > MAX_BAD_GENES:
            summary["escalations"].append(f"{sid}: {bad} of 50 genes fail the representativeness check, sample kept")

        spots = pd.DataFrame({
            "barcode": bc, "row": np.arange(len(bc)), "x_fullres": coords[:, 0], "y_fullres": coords[:, 1],
            "x_um": x_um, "y_um": y_um, "cluster": lab.astype(np.int64), "sampled": sampled})
        if "in_tissue" in obs:
            spots["in_tissue"] = obs["in_tissue"].to_numpy().astype(np.int64)
        write_parquet(spots, keep(f"{sid}_spots.parquet"))
        for kind, M in (("target", target), ("counts", counts)):
            df = pd.DataFrame(M, columns=genes)
            df.insert(0, "barcode", bc)
            write_parquet(df, keep(f"{sid}_{kind}.parquet"))
        for enc in ENCODERS:
            np.save(keep(f"{sid}_{enc}.npy"), embs[enc])
        idx = np.flatnonzero(sampled)
        write_tar(keep(f"{sid}_patches.tar"), [bc[i] for i in idx], imgs[idx])
        ov, frame = overview(x_um, y_um, imgs)
        ov.save(keep(f"{sid}_overview.png"))
        frames[sid] = frame
        per_slide[sid] = info
        print(sid, json.dumps(info, default=str), flush=True)
        del imgs

    pd.concat(strata).to_csv(keep("strata.csv"), index=False)
    pd.concat(rep).to_csv(keep("representativeness.csv"), index=False)
    json.dump(frames, open(keep("overview.json"), "w"), indent=1)
    summary["slides"] = per_slide
    summary["target"] = "log1p (natural log of one plus the raw count) of the 50 genes of var_50genes.json"
    summary["created_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    json.dump(summary, open(keep("package_summary.json"), "w"), indent=1, default=str)

    with open(os.path.join(out, "MANIFEST.tsv"), "w") as fh:
        fh.write("file\tbytes\tmd5\n")
        for f in sorted(set(files)):
            fh.write(f"{os.path.basename(f)}\t{os.path.getsize(f)}\t{md5(f)}\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "slides"}, indent=1, default=str))


if __name__ == "__main__":
    main()
