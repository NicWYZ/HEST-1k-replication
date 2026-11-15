# F3 source inventories

*Written on 11 November 2026 by three read-only sub-agents of the sixth session of track `final-runs` (lead frame 7744bd42-579b-40da-aa6c-80d67b9dbbdc), for plan section 5d. They ran on Longleaf's login node with ls, cat, sed, grep, awk, head, wc, md5sum and zcat only, ran no job and no git command, and wrote nothing on Longleaf. The lead checked the anchor values quoted in plan section 5d against these files, and each anchor is re-read from its source file by the anchor job that reproduces it.*

## `f3_inventory_prediction_sets.md`, Sets inventory (frame 4fe3c3a6-884c-4195-9111-b1313463f837)

**Declared deviations.**

- Indiana final file's gene list versus C3's per-fold D4 gene lists not checked (parquet schema not read; no python on login node).
- Raw-count availability in instrumentation/ for INDIANA_KIDNEY and LUNG_XENIUM not checked.
- One login-node shell line began with a no-op `python3 -c 1 2>/dev/null` by mistake (read and wrote nothing); otherwise only ls/cat/sed/grep/awk/head/wc/md5sum/zcat used.

## `f3_inventory_designs.md`, Designs inventory (frame 94e92b9e-39ce-4829-aea9-3b57d8ff1a52)

**Declared deviations.**

- Parquet schemas were not opened, because the login node allows no python. The y__/f__ column names of BULK/round10/final_runs/F2/refit_norm/*/norm/*.parquet and the columns of f2_gene_diag.parquet are inferred from code, not read.
- round5_ppi_balance.py line count was not taken; 217 is quoted from ledger L1_S5. The bodies of round9_fewcluster_strat_frontier.py, round7_ppi_s1_masking.py, round7_ppi_weighting.py and round5_ppi_e3_sim.py were indexed by grep (functions, grids, seeds) and not read line by line.
- Compute sizes were tabulated for E3 CCRCC uni_v2 only, for round 7 S4b from its final report, and for all F2 regime B units. The other round 5 E3 task ledgers, the round 5 E4b ledgers and the round 7 S1/S3 rows of r7ppi_slurm_jobs.csv (172 and 134 rows) were located but not tabulated.
- Row counts quoted from earlier documents (for example 210 of 232 in E3.4) were copied from the committed score files and not recounted from the gene-level files.

## `f3_inventory_joint_openpoints.md`, Joint inventory (frame 21c4b2db-c6b2-4f7c-85c8-420b0e2aa49d)

**Declared deviations.**

- Parquet schemas (refit_norm predictions, cluster values, gene-level outputs) were not opened, since the login-node rule excludes python; column presence for point 5 is inferred from the producing code path and marked unverified.
- Corpus regime B units' n_units and the F1 formC_check job's ledger size were not read.
- Whether round 5's E5 width_ratio and F2's median_wr_ppi are the same functional was not checked.
