# Q0, the lead's check of the three hand-backs

Written by the lead before commit, 30 September 2026. Each number below was read back from the
file named beside it. The Q1 report carries the escalations; this note is the verification record.

## B1 anchor (Slurm 3074938, rc_tengfei_pi, spill, c151417)

`anchor/q0_anchor_compare_summary.json` records 92 committed CCRCC rows of
`results/round3/B1_ppi/b1_acceptance.csv`, 92 rerun rows, 92 compared, 92 agreeing, and a maximum
absolute difference of 0.0 at a tolerance of 1e-10. The anchor passes. The lead also compared the
rerun's `b1_estimates.csv` (kept on Longleaf, not committed, since it duplicates a committed file)
against the committed one on all 1,200 CCRCC rows, and found a maximum absolute difference of 0.0
on `lam`, `theta_pp` and `se_cluster_pp`.

The instruction words the fourth identity as "the permuted predictor's donor-weighted lambda is
0". B1's committed check 4 is a different statistic, the median PPI-to-classical width ratio
against 0.95, and it fails on 21 of its 36 CCRCC rows in the committed file and in the rerun alike
(`anchor/run/b1_acceptance.csv`). Read from the rerun's estimates, the permuted donor-weighted
lambda has median 0 for $\theta_3$ at every $n_L$, but for $\theta_2$ its median is 1.0, 0.86 and
0.46 at $n_L = 6$, 8 and 12. This goes to the Q1 report as an escalation. The anchor, which is
reproduction of the committed file, is unaffected.

## ACS data (Slurm 3078654 fetch, 3078825 task definition; an earlier attempt 3074937 failed)

`acs/acs_inventory.json` records the file `census_income.npz` from ppi_py 0.2.3's own loader,
md5 `9d49f41eaa4563dffaeec3ef8f354169`, which the lead recomputed on the harvested copy. It
holds three arrays, `Y` (380,091 incomes in dollars), `Yhat` (the package's predictions) and an
unlabelled two-column `X` read as age and sex. State, PUMA and survey year are absent. The data
file itself stays on Longleaf under `results/round4/ppi/Q0_setup/acs/` and is not committed.
`acs_task_def.json` marks the cluster fields absent and carries the unit's proposed transform
(log of one plus the positive part of income) and its proposal to restrict to age 16 or over,
neither applied. The file `acs/acs_nonpositive_income_finding__local.json` was computed in the
sub-agent's local workspace, not on Longleaf, and is renamed to say so.

The first fetch attempt failed on the unit's own import-path bug, not on a network refusal, and its
note is kept under the name the unit gave it.

## Lung wrapper (Slurm 3074935, rc_tengfei_pi, spill, c151412)

`lung_wrapper/q0_lung_wrapper_check.csv` has 60 rows (20 samples by 3 encoders). For `NCBI865`
every encoder shows 2,143 embedding rows, one removed (`051x019`) and 2,142 after, with the subset
relation passing after the drop and failing without it. Rows after the drop equal the task file's
`n_patch_spots` on all 60 rows. `lung_wrapper/q0_lung_wrapper_summary.json` records the round-3
`load_set` raising on `NCBI865` for all three encoders, the lung target list at 343 genes with 0
controls removed, and the breast list at 151 with 61 removed. The module that ran,
`code/scripts/round4_ppi_data.py`, has md5 `2a26eb3ce74815e3e7c63cccd0527398` in the job's
provenance and in the committed copy. It ran from the job workdir, staged, because it was not yet in
the clone. Everything it imported came from the clone.

Discrepancy recorded, file not altered. `lung_wrapper/_provenance.json` carries the lead's frame
id rather than the sub-agent's, although the brief asked each sub-agent to stamp from its own
process. The acs and anchor stamps carry their sub-agents' frame ids. The lung PROVENANCE.txt also
records the partition but not the account, which `sacct` gives as rc_tengfei_pi after the lead
moved the pending job.

## Jobs cancelled before the working-copy note took effect

Slurm 3074092, 3074101 and 3074111 were cancelled while pending, with `sacct` elapsed 00:00:00, so
nothing they would have produced exists.
