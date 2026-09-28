# P1 and P2 lead verification (2026-09-28)

Checked by the lead from the handed-back tables, results/round4/data/P1_selection/selection.csv
and results/round4/data/P3_morphology/morphology_ext_summary.csv, not from the track's prose.

P1 (p1_verification.csv, 63 rows)
- Every selected sample present: the 63 rows join one to one with selection.csv (0 unmatched).
- lung_xenium: 24 samples, 120/120 files, 0 size mismatches, 9,358,042,424 bytes present equal to
  selection.csv's bytes_four_components on every row; subset relation holds on 23 of 24.
- donor_labelled_v: 39 samples, 195/195 files, 0 size mismatches, 18,980,302,609 bytes, equal per
  row; subset relation holds on 39 of 39; resolution_uncertain on 24, equal to selection.csv.
- NCBI865: 1 of 2,143 patch barcodes (051x019) has no expression row; set_L_member_for_task False
  on NCBI865 only (23 True); the column is empty on set V.
- Unpatched fraction, lung_xenium: min 0.282733, median 0.379772, max 0.757519 (mean 0.414785,
  sd 0.119870). The lead's earlier message carried the median as 0.395; this file governs.
- Set L's per-sample patch and expression counts and unpatched fraction equal P3's
  morphology_ext_summary.csv on all 24.

P2 (results/round4/data/P2_embeddings/p2_acceptance.csv, 72 rows)
- 24/24 accepted per encoder; 55,104 embedding rows against 55,104 patches for each encoder; rows
  equal patches, barcodes readable and in patch order on 72/72; per-sample patch counts equal P1's.
- Dimensions 1536 (hoptimus0, uni_v2) and 1024 (resnet50), stored float32 in all three.
- Each PROVENANCE__lung_xenium__<encoder>.txt carries round3_d2_embed.py md5
  3b9e47a045993bc2bd38790466486178 and records the use of rc_tengfei_pi.
- The handed-back scripts have the md5s computed inside the jobs: round4_data_download.py
  8420374d957de7cf9b3e3068c42d332a, round4_data_p2_accept.py e0e32d959b90daeef7a4568141eb6246.

Correction to the track's not_checked list. The track reports that D2's internal rev-parse
recorded e00d9bd in the P2 PROVENANCE files, disagreeing with 71451d7. It did not: every P2
d2_summary and d2_stdout records 71451d7cc8e538cb54ab8cd6ab712a42de080bb4, and the lead read the
Longleaf working copy's HEAD as that commit. e00d9bd appears only in P0's files, which ran before
the working copy was synced to 71451d7. There is no disagreement.

Job accounting: results/round4/data/P7_report/stageP_sacct.psv (lead's sacct query) agrees with
the track's job table. Set V's job 2751561 MaxRSS 16777920K equals its 16G request.
