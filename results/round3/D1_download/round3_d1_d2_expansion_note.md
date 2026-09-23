# Round 3, interval 2, Expansion track: D1 complete, D2 partial, anchor check failed

Written by the Expansion track. Not a stage report. Every number below is read back from a file
named beside it; paths are relative to `/work/users/w/e/weiyang/hest_replication` on Longleaf
unless stated otherwise.

## Step 0, the two set definitions

`results/round3/D0_inventory/expansion_set_members.csv` in the local clone went from 133 to 155
data rows. The 133 pre-existing rows are a byte-identical prefix of the new file: the original
sha256 is `e69f1152...614bfec8` over 52,342 bytes, the new file is 59,540 bytes, and
`new[:52342] == orig` holds. The script also reconstructed all 133 pre-existing rows from
`hest_inventory.csv` and got them byte-for-byte, which is what establishes that the added rows are
formatted identically to the existing block rather than merely parseable.

`institution_breast_xenium`, 18 rows. Human, organ Breast, `st_technology` exactly Xenium,
`oncotree_code` IDC, flagged duplicates removed. 140 human Breast samples in the release, 21 of
them Xenium, 18 of the 21 IDC (2 ILC, 1 with no code); no duplicate flag on any of the 18, so the
duplicate removal is a no-op here. 22.903 GB over the four components, 4 in the benchmark
(NCBI783, NCBI785, TENX95, TENX99). NCBI783, NCBI784 and NCBI785 are also in
`platform_pair_multitech`, which is why the union is 105 and not 108.

`kidney_visium_cell_extras`, 4 rows. NCBI538, NCBI539, NCBI540 (`disease_state` Treated, KTH,
subseries "PFA fixed kidney_organoid_{1,2,3}") and TENX71 (`lab_basis` vendor_product_page).
1.526 GB. The Kidney-on-Visium human non-duplicate cell is 58 samples; D0's institution set is 54;
these are the four it excludes. Kept out of every analysis set, left for D3.

The selection rule and the four per-sample reasons are in
`results/round3/D0_inventory/expansion_set_members_rules.txt`. They are there and not in the CSV
because the table has no free-text column and the pre-existing rows had to stay byte-identical, so
adding a column was not available. That is a new file in a directory this track otherwise does not
touch; the lead should decide whether it belongs there or folded into
`expansion_candidates.csv`, which already has a `selection_rule` column.

## D1, the download

Job 2126787, partition spill (requested general), node c0913, commit d3ce2b7, PYTHONHASHSEED 0,
config hash `sha256:860ece3765decdabe38c5be84cbc44bb crc32:67cff89f`. Facts and the full sample
list are in `hest_ext/PROVENANCE.txt`.

Revision. The pinned `7e8d5a0b0aace41d8c8ec0f6ecea80e4ad2a61ec` from `inventory_report.json` was
used, and the repository's `main` resolves to the same sha today, so HuggingFace has not moved on
since D0.

105 samples, 525 files, 70,260,258,915 bytes on disk against 70,260,258,915 bytes expected from
`results/round3/D0_inventory/hf_file_listing.csv.gz`. Every file present, every byte size matched,
no exceptions (`hest_ext/d1_summary.json`). Four components only; no `wsis/`, `transcripts/`,
`xenium_seg/` or anything else was requested, because the allow list was the explicit set of 525
file paths rather than directory globs. Download wall time 241 s for the three sets.

One physical home per sample, assigned by the set order kidney, breast Xenium, platform-pair, so
NCBI783/784/785 live under `institution_breast_xenium`: 58, 18 and 29 owned samples respectively
(`hest_ext/sample_home_map.csv`). `du` on `hest_ext` went from 0 to 70,260,654,592 bytes; `df -h
/work` read 556T available before and 555T after; the home quota line was unchanged at 4163M of
51200M, since nothing was written to home.

## D1 verification: the patch count does not equal the spot count, and should not

The specified check fails for 94 of the 105 samples. It fails because it is the wrong relation, and
the right one holds exactly. Read back from `hest_ext/d1_verification.csv` and
`hest_ext/d1_patch_spot_audit.json`:

- patch count is at or below the expression file's spot count for 105 of 105 samples;
- the patch barcodes are a subset of the expression file's barcodes for 105 of 105, with zero patch
  barcodes absent from the expression file anywhere in the set;
- barcodes are unique within both files for all 105;
- 65,464 of 424,301 spots have no patch, a 15.4 percent drop overall. Per sample the dropped
  fraction runs from 0.0000 (INT13) through a median of 0.0161 to 0.3591 (TENX95). By set: kidney
  retains 115,785 of 116,842 spots (99.10 percent), breast Xenium 134,333 of 165,640 (81.10),
  platform-pair 108,719 of 141,819 (76.66).

HEST's own benchmark code is built for this relation: `predict_single_split` reads the barcodes out
of the embedding file and then subsets the expression matrix to them
(`load_adata(expr_path, genes=genes, barcodes=barcodes)`). The patch barcode list is the reference
set, not the spot list. The equality form of the check would only pass on a sample where patching
dropped nothing, which is 11 of 105 here.

## D2, embeddings

Extraction path. Round 1 produced `embeddings/<task>/<encoder>/<sample>.h5` through HEST's own
`code/HEST/src/hest/bench/benchmark.py`, driven by the `code/configs/<head>__<encoder>.yaml` files
(seed 1, batch_size 128, num_workers 4, `embed_dataroot` pointing at `embeddings/`). Inside
`predict_single_split` the sequence is `encoder_factory(model_name)` from
`trident.patch_encoder_models`, then `precision = encoder.precision`, then
`H5PatchDataset(tile_h5_path, img_transform=encoder.eval_transforms)`, then a `DataLoader` with
those two config values, then `embed_tiles`, which runs the forward pass under
`torch.amp.autocast('cuda', dtype=precision)` and appends each batch to the h5 with `save_hdf5`.

`code/scripts/round3_d2_embed.py` (staged as `d2.py`) imports those same four objects rather than
reimplementing them, and writes to `embeddings_ext/<set>/<encoder>/<sample>.h5` via a `.tmp` file
and `os.replace`, so a sample is either absent or complete and a killed job resumes. TRIDENT's
installed commit is `f3eb7f301ce34f875306b545e6cfefc5d3335a5c`, matching the pin in
`env/REBUILD.md` and `env/requirements.lock`; the script exits non-zero if it ever does not. Round 1
ran on `l40-gpu`, so D2 requests the same partition; the observed device is an NVIDIA L40S, torch
2.14.0+cu130, and `resnet50`'s `encoder.precision` is `torch.float32`.

Status. `resnet50` is complete for both sets: 58 of 58 kidney (115,785 patches, 710 s) and 18 of 18
breast Xenium (48,556 patches written across two jobs). `hoptimus0` (Slurm 2128386) and `uni_v2`
(Slurm 2128582) are still PENDING on `l40-gpu` with reason Priority; `squeue --start` returns N/A
for both, so Slurm is not offering an estimate. Nothing about them has run.

A defect worth recording. The first `resnet50` breast job (2128583) died partway through the set at
`assert dset.dtype == val.dtype` in `code/HEST/src/hest/bench/utils/file_utils.py:65`.
`benchmark._to_numpy` casts a unicode barcode array to `S<max_len>` recomputed per batch, so a
sample whose barcode string lengths differ between batches trips that assert. Round 1 never met it
because the samples it processed did not vary that way. The fix is a `collate_fn` that hands the
barcodes over as dtype object, which routes `save_hdf5` down the variable-length-string branch it
already has; images, transforms, batch order, encoder, seed and barcode values are untouched, and
only the h5 string dtype of the barcode column changes. The 58 kidney `resnet50` files were written
before the fix and keep a fixed-width barcode dtype; their embeddings are unaffected. Which sample
crashed is an inference from the sorted iteration order (the one after TENX95), because the log
prints no sample name before the traceback.

## The anchor check: it fails, and here is how the layouts differ

For `resnet50`, over all 28 anchor samples and 108,837 barcodes matched by barcode
(`out/anchor_check_consolidated.csv`):

- per-row relative L2, `||new - bench|| / ||bench||`: median of the per-sample medians 0.0633,
  maximum over samples 0.1552;
- element-wise relative difference: median of the per-sample medians 0.0705; the maximum is exactly
  1.0, which is an artefact of the metric rather than a finding, because `resnet50` output is
  post-ReLU and one of the two values is exactly zero for some elements;
- 0 of 28 samples agree at 1e-5 relative. The disagreement is four orders of magnitude above the
  float32 floor.

`hoptimus0` and `uni_v2` have not been measured, because their jobs have not run.

The cause is not patch size and not resolution. From `hest_ext/anchor_patch_compare.csv` and
`hest_ext/anchor_coord_relation.csv`:

1. **Geometry agrees.** `patch_size_src` in the HEST-1k file equals `patch_size` in the benchmark
   file for 28 of 28 samples (244, 245, 308, 409 or 527 depending on the sample), the `downsample`
   and `factor` attributes agree to the printed digits, and both files are 224x224x3 uint8.
2. **The two layouts address the same window.** `bench_coords == hest1k_coords` with its two axes
   exchanged, plus a constant offset of half the source patch size, holds exactly for 27 of 28
   samples over 108,837 shared barcodes. The exception is NCBI785, where the residual is a constant
   [-1, -1] on all 3,960 of its shared barcodes, i.e. the offset is 153 rather than 154 for a
   308-pixel source patch. Without the axis exchange the residual reaches 7,859 to 97,889 pixels
   (largest axis per sample), and without the offset it is exactly the half-patch constant, so both
   terms are real and the relation is not a coincidence.
3. **The pixel content differs anyway.** For matched barcodes on four samples
   (`hest_ext/anchor_layout_diagnostic.csv`, 24 barcodes each): mean absolute difference 3.75 to
   9.76 grey levels, maximum absolute difference 97 to 150, 74 to 95 percent of bytes differing, and
   Pearson correlation between the two 224x224x3 arrays with a per-sample median of 0.96 to 0.99 and
   a minimum over compared barcodes of 0.94. Across all 28 anchors the
   maximum absolute byte difference is 203. For 0 of 24 barcodes on any of the four samples was the
   benchmark patch better matched by a different HEST-1k patch, so the barcode-to-row alignment is
   correct in both files and this is not a row scrambling.
4. **The retained spot set differs, in both directions.** INT1 has 1,032 patches against the
   benchmark's 1,084, all 1,032 shared. NCBI783 has 3,501 against 3,005, with 532 present only in
   HEST-1k and 36 only in the benchmark. Barcode sets are identical for 5 of 28 anchors.

The reading: same field of view, same nominal patch size, same downsample factor, different pixel
values, consistent with a different resampling of the source crop down to 224 pixels (different
interpolation kernel or a sub-pixel sampling grid offset), together with a different tissue filter
deciding which spots get a patch. High correlation with a few grey levels of everywhere-difference
is the signature of resampling, not of a different location; a different location would show
correlation near zero and a mean absolute difference an order of magnitude larger. This has not
been confirmed against the two patching implementations' source, which is the next step if the
mechanism matters.

**Consequence for round 3.** Expansion embeddings and round-1 cached benchmark embeddings are not
interchangeable, per barcode, at any tolerance a numerical identity check would accept. Any round-3
result that pools expansion samples with benchmark samples must use embeddings re-extracted from
HEST-1k patches for both, which is what D2 does for all 76 samples including the 28 anchors. The
memo's instruction to download the 31 benchmark samples rather than reuse the benchmark copies is
what makes that possible; this result is the reason it was the right instruction.

## To resume the two pending encoders

```
# Slurm 2128386 (hoptimus0) and 2128582 (uni_v2), l40-gpu, PENDING (Priority), 6 h wall each.
# Each runs, in order:
d2.py --set kidney_visium_cell        --encoder <enc> --config d2_config.json
d2.py --set institution_breast_xenium --encoder <enc> --config d2_config.json
# writing embeddings_ext/<set>/<enc>/<sample>.h5 plus, in embeddings_ext/,
#   anchor_check__<set>__<enc>.csv
#   d2_extraction__<set>__<enc>.csv
#   d2_summary__<set>__<enc>.json
#   PROVENANCE__<set>__<enc>.txt
# Per-sample caching means a resubmit after a kill costs only the unwritten samples.
```

## Not checked

- `hoptimus0` and `uni_v2` embeddings and their anchor figures. The jobs have not run.
- The platform-pair set is downloaded and verified but deliberately not embedded, per the memo.
- Why the two patching implementations resample differently. The difference is measured, not traced
  to source; the claim that it is resampling rather than something else rests on the correlation and
  magnitude pattern plus the exact coordinate relation, not on reading both patching codebases.
- Whether the differing tissue filter changes which spots are biologically usable. Only counts and
  set relations were computed.
- INT13's image difference (median mean-absolute 9.76 grey levels, Pearson 0.955) is about twice
  the other three anchors examined. Not investigated.
- Nothing was compared for `cellvit_seg` or `metadata` beyond file presence and byte size.
- The cached-file check on resume compares row count only, not content; a file written by a
  different encoder build with the same row count would be accepted as cached.
