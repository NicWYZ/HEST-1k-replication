# F3 E8 (plan 5d.4 items 2 to 5), track directory RESUME

Track dir: /work/users/w/e/weiyang/hest_replication/results/round10/final_runs/F3/e8/ (stamped, frame 4ca471b7-8d08-41d9-a9df-67fff51f4222).
Per-unit CSV: F3/e8/e8_units.csv (sole writer: the E8 sub-agent). Staging: /work/users/w/e/weiyang/.claude-science-scratch/tmp/e8_s7/.
Spec: plan section 5d.4 (lines 343 to 349) and Part 1 of results/round10/final_runs/F3/inventory/f3_inventory_joint_openpoints.md.
Plan approved by the lead (b66915a6) on 13 Nov 2026, with points: regB_boot_B = 200 column; ACS GRID override restored and recorded;
cells with no valid or no no-extra set written with a reason and counted; checks JSON with the spot check at CCRCC uni_v2 log1p p1 K10 o10.

Units
1. anchor_e5: round5_ppi_e5_joint.py unchanged from snapshot 3c1de525, git shim serving w3_map_by_task.csv (md5 4ee7bbf2). Job script e8_s7/job_f3_e8_anchor_e5.sh. Output F3/e8/anchor_e5/anchor_e5.json.
2. e8_overlay_check: round10_final_runs_f3_e8_joint.py (staged, md5 1927815b0f66644af95127f95847695c) overlaid on snapshot 3c1de525. Job script e8_s7/job_f3_e8_joint.sh (STAGED, DRIVER_MD5 substituted). Output F3/e8/e8_overlay_check/e8/.
3. e8_joint (production): after the lead commits the script and job script, the same job script with STAGED=none and DRIVER_MD5=none at that commit.
Success is read only from <unit>/PROVENANCE.txt status COMPLETED.

State
- DONE 15:40 EST 13 Nov. e8_joint (Slurm 9120588, commit 9450861b) COMPLETED; e8_joint.csv, e8_set_cells.csv and e8_checks.json are byte-identical (md5 954d06e9, 57eb3bb8, f60da1e3) to e8_overlay_check's.
- anchor_e5_v2 (Slurm 9121186, commit 07016c8c) COMPLETED and passed (354/354 rows, max abs diff 4.440892098500626e-16 <= 1e-12). anchor_e5 (Slurm 9104185) FAILED_rc6 on its exact-0 criterion, left as is per the lead.
- Small outputs copied (not committed) into the clone at results/round10/final_runs/F3/e8/: anchor_e5.json (from anchor_e5_v2), PROVENANCE_anchor_e5_v2.txt, e8_joint.csv, e8_set_cells.csv, e8_checks.json, PROVENANCE_e8_joint.txt, e8_units.csv, RESUME.md.
- Nothing outstanding for this track.
