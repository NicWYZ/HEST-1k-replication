# Round 4 data pull, acceptance of the P7 report and the decisions it asked for

30 September 2026. Written by the oversight chat after reading `docs/round04/i01/data/round4_data_report.md` at tag `round4-data` (HEAD `2905525`) and checking its numbers against the files it names. Nicolas hands this to the session that will run the short addendum in section 3. The two track documents have been revised to match; they start from the tag this addendum produces.

## 1. Acceptance

The report is accepted. The numbers I checked read back from the files exactly. `p5_validation.csv` gives 19 samples, 14 donor units, 14 donor folds, 42 `a4b_k10` rows and 3 training donors at minimum, 541 panel features of which 343 are genes. `LUNG_XENIUM.json` lists `NCBI865` under `expansion.pending_oversight` with donor `lungXen_VUILD110`, and its `a4b_k10` block records $K = 10$ with 3 draws over 14 folds. `p3_acceptance_join_and_quantiles.csv` gives `TENX197` a join rate of 0.861937. `p3_d4_geometry_discrepancy.csv` gives the D4 half-width ratio 2.0 on every Indiana row I read and pair ratios near 3.9. `donor_audit_r4.csv` has 211 rows, of which 24 are set L with 12 verified, 8 contradicted and 4 unverifiable, and the 15 resolvable lung donors are the ones the report describes, five of them with two samples. The harness md5 is unchanged at `0ad7ae8efe554c1f285e5f384a9fb7f5`.

Predictions scored as the report scores them. Prediction 2 was mine and was wrong for the reason the P1 decision recorded.

## 2. Decisions on the escalations

1. **`NCBI865`.** Reinstate it by dropping the one patch barcode. One missing expression row out of 2,143 is a defect in the shipped file, not a property of the sample, and excluding a whole donor for it is disproportionate when the lung task has 14. The drop is recorded explicitly, as a per-sample `dropped_patch_barcodes` list in the task definition, and the subset relation is asserted after the drop, not relaxed. The lung task becomes 20 samples and 15 donors, with 15 donor folds and an `a4b_k10` design whose pool of 14 leaves 4 training donors. The embedding row for that patch is excluded by barcode at read time; the embedding files are not rewritten.
2. **`TENX197` at 0.862.** Accepted as delivered. It stays in the breast set with its join rate carried in the morphology table, and any breast morphology estimand reports it.
3. **D4's probe box.** The correction to `round3_d4_probe.py` (half the extent, not the extent) is applied as a code change in the addendum, with the docstring fixed, and nothing is rerun now. The round-3 statement that morphology removes 31% to 34% of the above-chance probe signal is quarantined. Neither track cites it, and the paper does not use it until the probe is rerun, which is a round-5 item if the paper needs the probe at all. Round-3 result files are not changed.
4. **Lung donor units, 14 or 15.** Accepted. The tracks read the donor count from the task file and never hard-code it.
5. **$K = 10$ on lung.** Accepted as a property of the design. The tracks record the training-donor count beside every lung result, and the conformal track also runs $K = 6$ and $K = 8$ on lung so that the $K = 10$ head, trained on 4 donors, is not the only lung number.
6. **Edge patches on multi-donor slides.** A report-only diagnostic in the addendum. Nothing is excluded on its evidence in round 4.
7. and 8. **`NCBI885`, `NCBI886`, `NCBI887`.** Accepted as excluded.
9. **HEST fields contradicted.** Accepted; the audit file is the record. The two tracks describe lung as one laboratory, one instrument, one software generation, one pixel size, disease not fixed, and slides carrying two to five donors.
10. **Control features.** The addendum writes the control-free panel table (proposed edit 4). Both tracks also apply the filter at read time, dropping `NegControl*`, `UnassignedCodeword*` and `BLANK*`, and record the count dropped, so that the rule holds whether or not the table is used. Round 3's `BREAST_XENIUM.json` is not changed; its 61 controls are dropped when it is read.
11. **Disease not fixed on lung.** Accepted. It goes into the lung difference list in both tracks. It is also a reason the lung donor effects are expected to be large, which is useful to the paper and is said as such.
12. **`TENX141`.** Accepted as unverifiable and outside every donor unit.
13. **P2's time limit.** Accepted. The rule is a cap derived from a measured sibling, and a measured rate is a better sibling than a different encoder's total.
14. **Set V's download memory.** Recorded. Any future job over set V asks for 32 GB.
15. **Job names.** Accepted. The track documents now say that jobs are identified by Slurm id and that the intended prefix is recorded in `PROVENANCE.txt` rather than in `--job-name`.
16. **Frame id in the P3 provenance.** Accepted. The track documents now tell sub-agents to call `stamp_dir()` from their own process so the frame id is theirs.
17. Noted. 18. Noted; both tracks may use `rc_tengfei_pi`.
19. **The ten unresolved claims** in `docs/round02/tracks/deck/deck_speaker_scripts.md` and `docs/round00/first_year_ST_project_proposal.md` predate round 3 and stay as they are. They are a round-5 housekeeping item, and the numeric-claim gate for the tracks runs over the README and the tracks' own documents, as their instructions say.

Proposed edits 1, 2 and 4 are applied in the addendum. Edit 3 (the v2 extension schema) is applied. Edit 5 (making `morphology_features.py` importable) is deferred; nothing in round 4 calls it. The `docs/README.md` index entries are applied, and this memo is added to them.

## 3. The addendum, stage P8 (one day, capped; report and wait)

Run on `main` from tag `round4-data`, by the data-pull session if it is still open and otherwise by a fresh session given this memo and `docs/round04/i01/data/round4_data_pull.md`. Everything under `results/round4/data/P1_*` to `P7_*` stays as it is; P8 writes under `results/round4/data/P8_addendum/` and rewrites only the files named here. No downloads, no embeddings, no GPU.

1. **Task definition.** Rewrite `results/round4/data/P5_task/LUNG_XENIUM.json` with `NCBI865` as a member, `dropped_patch_barcodes: {"NCBI865": ["051x019"]}`, 20 samples, 15 donor units, the donor folds regenerated (15), the `random` folds regenerated at the same sizes, and `a4b_k10` regenerated with the same seed rule over 15 folds and 3 draws. Keep the previous file beside it as `LUNG_XENIUM__19_pre_P8.json`. Rerun the P5 validation and write `p5_validation.csv` again, with the earlier one kept as `p5_validation__pre_P8.csv`. Acceptance is 20, 15, 15 donor folds, 45 `a4b_k10` rows, a minimum of 4 training donors, and the subset relation holding on every sample after the drop.
2. **Schema v2.** Write `results/round3/D4_expansion/task_defs/task_def_ext.schema.v2.json` as proposed (row origin `expansion_r4`, per-sample `slide_id`, an `a4b_k10` fold key, and the `dropped_patch_barcodes` field). Do not touch the v1 file. Validate the new lung file against v2 and record the result. Writing one new file under a round-3 directory is permitted for this item only.
3. **Control features.** Write `results/round4/data/P8_addendum/xenium_panels_genes_only.csv` from `p6_xenium_panels.csv` with `NegControl*`, `UnassignedCodeword*` and `BLANK*` removed, with a column giving the count dropped per task (expected 61 on five tasks and 220 on IDC).
4. **Code corrections.** In `code/scripts/round3_d4_probe.py`, make the `patch_geometry` fallback return half the extent and fix the docstring; do not run the probe. In `code/scripts/round3_d1_download.py`, replace the patch-count equality test by the subset relation as the round-4 download script states it; run its self-test if it has one and record that no download was run. Both are ordinary commits with the reason in the message.
5. **Edge-patch diagnostic.** For each of the 20 lung samples, take the patch centres, fit the tissue centroid, and report the fraction of patches whose centre lies more than 1.6 mm from it, with the sample's HEST rectangle and the 3 mm core diameter beside it, in `results/round4/data/P8_addendum/lung_edge_patches.csv`. Report only.
6. **Index and report.** Add the proposed `docs/README.md` entries plus `docs/round04/i02/data/round4_data_P7_decisions.md` (this memo). Write `docs/round04/i02/data/round4_data_P8_report.md` in the report format, run the numeric-claim gate over it, commit, tag `round4-data-v2`, and stop.

If Nicolas decides to skip the addendum, the tracks start from `round4-data` with the lung task at 19 samples and 14 donors and apply the control filter at read time; their documents say so.
