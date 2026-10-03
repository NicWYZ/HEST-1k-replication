# Q4a recompute, merged outputs

The merge was done by `code/scripts/round4_ppi_q4a_merge.py` (md5 4766341fa9dec648a90d50267fab3614), run as `python round4_ppi_q4a_merge.py --stage i3/q4a --res res_i3` in the lead workspace on 2 October 2026 with PYTHONHASHSEED=0.
Inputs were the per-unit tarballs below, plus copies of `Q3_regimes/q3_regime_comparison.csv` and `Q2_theory/q2_fitted_components.csv.gz` from this tree.

All unit runs were local under plan section 12.4.

| Task | Unit frame | Tarball artifact version |
|---|---|---|
| CCRCC and CCRCC_merged | 30f92869-3c48-4ca7-aea4-4a59afc9e6e0 | cc1406df-130e-49c0-90bf-0588db29d004 |
| INDIANA_KIDNEY | 29d26232-3024-422c-8c8b-0dd27509ba09 | e7e5703d-e267-4bdd-a90d-6e7777a32780 |
| ACS_STATES and ACS_CA_PUMA | e2341968-ca72-46c3-a417-31beb69f6202 | 1fe4ab8b-e62a-4873-8215-de139b1310e5 |
| LUNG_XENIUM | 040a77a6-04af-44f8-9fc3-a5a62d075ff8 | b8aa491c-776b-4433-b346-0e591c26e7d8 |

In every unit the rows for rules none and c_crossfit reproduce the interval-2 merged files with maximum absolute difference 0.0 (files in `unit_records/`).
CCRCC_merged regime A has no interval-2 counterpart, so it has nothing to reproduce against.
The per-gene grid `q4a_variance_grid_genes.csv.gz` (md5 652e03908bde822e392ebee4c1b1bff9, 78227165 bytes) is too large to commit, as in Q2. It is kept as artifact version 5c67808d-e6c7-4bb1-9f19-8449ea0b3e35.

The `exit_code 1` lines in the unit PROVENANCE files come from the macOS `/usr/bin/time -l` wrapper, which fails in the sandbox after each script has finished. Completion was judged from the summary JSON, the final log lines and the row counts.
Four lung cost-ratio runs (resnet50 and permuted at cd10 and cd1000) failed when the local repo moved to `/Users/nicolaszhang/hest-1k/`. They were rerun from the new path with the same seeds after their partial files were deleted.
