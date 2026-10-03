# Q5a closing unit (plan section 15.3), records

All reruns used the same seeds, inputs and arguments as Q4a. They ran locally (plan section 15.6), on commit a8e6b43 (masking md5 15f51917a5fb79702ba239e520e7ff86, estimator d79e69aa65800b9d24de556e019a0c64, regimes 6097231bc238c0a23387ce76029acefd). Every old row and column reproduces the committed Q4a values with maximum absolute difference 0.0 (files in `unit_records/`). The exception is $4.4 \times 10^{-16}$ in regime B `width_ratio_median` against the interval-2 file on CCRCC, a floating-point difference.

| Task | Unit frame | Output artifact version |
|---|---|---|
| CCRCC and CCRCC_merged | 30f92869-3c48-4ca7-aea4-4a59afc9e6e0 | ffac2f6d-f745-446e-8f7f-f90872165236 |
| INDIANA_KIDNEY | 29d26232-3024-422c-8c8b-0dd27509ba09 | 6d3e949e-fff0-4ca0-bc02-e4e243140a00 |
| ACS_STATES and ACS_CA_PUMA | e2341968-ca72-46c3-a417-31beb69f6202 | 6b42eb85-b20d-43ef-9343-4b344351a729 (per-draw dumps ea8cf6f9-2a53-439e-a16b-fcaf4ff6186a) |
| LUNG_XENIUM | 040a77a6-04af-44f8-9fc3-a5a62d075ff8 | e3b5cffe-25f6-42f8-a48e-40c05beffce0 |
| CCRCC gene axis | 8a3ad045-482e-4604-9184-5d7d08b4ba73 | a44ae8a7-a891-40dc-8272-db2a1d4ee5e1 |
| Indiana gene axis | 8c744e5a-ce3d-4fdb-98b9-29297bf7255d | 9d932018-d1c0-471a-b93c-dae45fa5dc75 |

Merged with `code/scripts/round4_ppi_q4a_merge.py` over the Q5a outputs, plus the Q4a c_d/c_s = 1000 files, which were not rerun. Then `code/scripts/round4_ppi_q4_merge.py --q5a` over the Q4 unit tables. The per-gene grid `q4a_variance_grid_genes.csv.gz` (md5 cbf2fa0bdea6e0f0e6bf4194f3061183) is not committed because of its size.

The unclipped lambda columns are empty on rows that were not rerun: the lung regime B rows at c_d/c_s = 1000, the ACS regime B rows at the fixed m x G budgets, and the ACS masking rows at n_L = 20 from the Q4 ACS unit.
