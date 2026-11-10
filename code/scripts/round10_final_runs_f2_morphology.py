"""Round 10, track final-runs, F2 option (b): round 3's nuclear instrumentation on the corpus's patches (plan, section 5b).

For every kept sample of one corpus task, the per-spot CellViT features of round 2's builder, through round 4's
verbatim transcription (`spot_features`, `assemble`, `read_cellvit`, `patch_geometry` of round4_data_morphology.py,
imported unchanged from the snapshot) on the corpus's own st/<id>.h5ad, patches/<id>.h5 and metadata/<id>.json.
Only patched spots are kept, as round 4 did. The CellViT parquet is taken from the first segmentation root that has it.

usage: round10_final_runs_f2_morphology.py <task> <donor_map.csv> <corpus_hest_dir> <out_dir>
         --cellvit-roots <dir> ... --reference <round 4 parquet> ... --predictions <donor-design prediction parquet>
Writes morph_summary.json first, then morph_per_sample.csv, morphology__<task>.parquet, and morph_anchor.csv
(the comparison with round 4's rows on shared (sample_id, barcode)) and morph_join.json (join to the predictions).
"""
import argparse, glob, json, os, sys, time
import numpy as np, pandas as pd, pyarrow as pa, pyarrow.parquet as pq
import anndata as ad, h5py

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import round4_data_morphology as M4

COLS = ["n_nuclei", "area_mean", "area_median", "frac_connective", "frac_dead", "frac_epithelial",
        "frac_inflammatory", "frac_neoplastic", "n_neoplastic", "neo_area_mean"]
SCHEMA = pa.schema([("task", pa.string()), ("sample_id", pa.string()), ("barcode", pa.string())] +
                   [(c, pa.int64() if c.startswith("n_") else pa.float64()) for c in COLS])


def find_cellvit(sid, roots):
    for r in roots:
        for p in (glob.glob(os.path.join(r, "*", "cellvit_seg", f"{sid}_cellvit_seg.parquet")) +
                  glob.glob(os.path.join(r, "cellvit_seg", f"{sid}_cellvit_seg.parquet"))):
            return p
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("task"); ap.add_argument("donor_map"); ap.add_argument("hest"); ap.add_argument("out")
    ap.add_argument("--cellvit-roots", nargs="+", required=True)
    ap.add_argument("--reference", nargs="*", default=[]); ap.add_argument("--predictions", default=None)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    mod = M4.load_builder(os.path.join(HERE, "morphology_features.py"))
    sids = sorted(pd.read_csv(a.donor_map).sample_id.astype(str).unique())
    summ = dict(task=a.task, n_samples=len(sids), started=time.strftime("%Y-%m-%dT%H:%M:%S"))
    sp = os.path.join(a.out, "morph_summary.json"); json.dump(summ, open(sp, "w"), indent=1)
    frames, per = [], []
    for sid in sids:
        t0 = time.time()
        cvp = find_cellvit(sid, a.cellvit_roots)
        if cvp is None:
            per.append(dict(sample_id=sid, status="no_cellvit")); continue
        half, src, extent, attrs, cross = M4.patch_geometry(f"{a.hest}/patches/{sid}.h5", f"{a.hest}/metadata/{sid}.json")
        cx, cy, area, cls, n_nuc = M4.read_cellvit(cvp, mod.EXPECTED)
        A = ad.read_h5ad(f"{a.hest}/st/{sid}.h5ad", backed="r")
        bc = np.asarray(A.obs_names[:], dtype=object); xy = np.asarray(A.obsm["spatial"], dtype=np.float64)
        try:
            A.file.close()
        except Exception:
            pass
        with h5py.File(f"{a.hest}/patches/{sid}.h5", "r") as f:
            patch_bc = set(M4.decode(f["barcode"][:]))
        recs = M4.spot_features(xy, cx, cy, area, cls, half, mod.EXPECTED, mod.CHUNK)
        full = M4.assemble(recs, xy, bc, mod.EXPECTED)
        keep = np.asarray([b in patch_bc for b in bc])
        sub = full.loc[keep].reset_index(drop=True)
        sub.insert(0, "sample_id", sid); sub.insert(0, "task", a.task)
        frames.append(sub[SCHEMA.names])
        nn = sub.n_nuclei.to_numpy()
        per.append(dict(sample_id=sid, status="ok", cellvit=cvp, n_nuclei_total=int(n_nuc), n_spots=int(len(bc)),
                        n_patched=int(keep.sum()), patch_barcodes_without_spot=int(len(patch_bc - set(bc))),
                        frac_patched_with_nuclei=float((nn > 0).mean()) if len(nn) else np.nan,
                        half_width_px=float(half), geometry_source=src, seconds=round(time.time() - t0, 1)))
        print(json.dumps(per[-1]), flush=True)
    pd.DataFrame(per).to_csv(os.path.join(a.out, "morph_per_sample.csv"), index=False)
    D = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=SCHEMA.names)
    summ.update(n_ok=sum(p["status"] == "ok" for p in per), n_rows=len(D))
    json.dump(summ, open(sp, "w"), indent=1)
    pq.write_table(pa.Table.from_pandas(D, schema=SCHEMA, preserve_index=False), os.path.join(a.out, f"morphology__{a.task}.parquet"))
    # anchor against round 4's rows
    rows = []
    for ref in a.reference:
        Rf = pd.read_parquet(ref)
        Rf = Rf[Rf.sample_id.astype(str).isin(sids)]
        m = D.merge(Rf, on=["sample_id", "barcode"], suffixes=("", "_r4"))
        if not len(m):
            rows.append(dict(reference=ref, n_ref_rows=len(Rf), n_matched=0)); continue
        r = dict(reference=ref, n_ref_rows=len(Rf), n_matched=len(m), n_ours_in_ref_samples=int(D.sample_id.isin(Rf.sample_id.astype(str)).sum()))
        for c in COLS:
            x, y = m[c].to_numpy(float), m[c + "_r4"].to_numpy(float)
            both = np.isfinite(x) & np.isfinite(y)
            r["max_abs_" + c] = float(np.abs(x[both] - y[both]).max()) if both.any() else np.nan
            r["nan_mismatch_" + c] = int((np.isfinite(x) != np.isfinite(y)).sum())
        rows.append(r)
    pd.DataFrame(rows).to_csv(os.path.join(a.out, "morph_anchor.csv"), index=False)
    if a.predictions:
        P = pd.read_parquet(a.predictions, columns=["sample_id", "barcode", "donor_id"])
        j = P.merge(D, on=["sample_id", "barcode"], how="left")
        jn = dict(n_pred_spots=len(P), n_with_row=int(j.n_nuclei.notna().sum()), n_with_nuclei=int((j.n_nuclei > 0).sum()),
                  donors=int(P.donor_id.nunique()),
                  donors_all_samples_ok=int(j.groupby("donor_id").n_nuclei.apply(lambda s: s.notna().all()).sum()))
        json.dump(jn, open(os.path.join(a.out, "morph_join.json"), "w"), indent=1)
        summ["join"] = jn
    summ["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S"); json.dump(summ, open(sp, "w"), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
