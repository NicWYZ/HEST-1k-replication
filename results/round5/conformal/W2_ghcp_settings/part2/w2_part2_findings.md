# W2 part 2, the census task: findings (frame 630c1298-6055-44d9-bf49-39588dece318)

Everything below was run on Longleaf under Slurm. Output root:
/work/users/w/e/weiyang/hest_replication/results/round5/conformal/W2_ghcp_settings/part2/

## 1. The input (item 1)
- Raw files: results/round4/ppi/Q0_setup/acs_pums2018/raw/2018/1-Year/psam_p06.csv. whose() verdict on that directory: **sibling**
  (stamp frame 489504c4-ba56-4908-816f-a5c52417f390, track round4-ppi, same project; stamp downloaded and classified with
  whose(project_id=proj_3a4e23273fb6, frame_id=630c1298-...)). It was read only. Permission to read it is
  docs/decisions/round4_conformal_C2_decisions.md section 4 ("whose() will return sibling; this memo is the permission").
- md5 of psam_p06.csv = fe1e2321f1b69cad23486d2c8f582d28, equal to raw_manifest.json (checked in the job before reading).
- Built with the released real_data/acs/download_acs_ca_pums.py main(), unmodified (md5 87a6d1442372df57f732836e606c3cd7), run with folktables'
  own cache pointing at the raw file (download=True in the released script, but the file exists, so folktables does not download; the
  job asserts the cache holds only the symlink afterwards). Only the module attribute OUT_PATH was set from outside.
- Result: input/data/acs_data_all50states.csv, **378,817 rows**, md5 **52c89ae44af23ce972a02c13e4ee5648** (census_input_record.json).
- Round 4's local record (frag_ACS_o/ghcp_repro/ logs, PROVENANCE) gives the row count 378,817 and the cohort counts but no md5 of the
  local CSV, so the md5 cannot be compared. The row count agrees. The cohort counts printed by the released loader on Longleaf
  (released_a10/paper-results/acs/logs/run_alpha10.log) equal the round-4 log line for line: 378817 -> 98793 -> 51615 -> 22893 -> 13707 -> 13700 -> 12285,
  265 PUMAs, 212 eligible, group sizes 21 to 252, median 46.

## 2. What --target_index does (item 2)
File: /work/users/w/e/weiyang/hest_code/ghcp_code/code/marginal/run_acs_experiments.py (commit d1a69f4a).
- Line 2404 (argparse, default 20; help text: "Fixed within-PUMA target row index (history uses indices 0..o-1; need size > max(o, target_index))").
- Line 2618 `_set_target_index(args.target_index)`; lines 111-115 set the module globals TARGET_INDEX and MIN_TARGET_PUMA_SIZE = TARGET_INDEX + 1.
- Used at lines 1584-1585 and 1946-1948 (x_target = X[target_index], true_y = Y[target_index] of the target PUMA), 988-989, and
  1464 / 1292 (a target PUMA needs at least target_index + 1 rows).
- **It is the position of the target individual inside the target PUMA, not the number of calibration PUMAs.** The suggestion in the brief
  that it "appears to set the number of calibration PUMAs" is wrong; 20 and 20 coincide in the round-4 command.
- The number of calibration PUMAs is **--n_puma_groups** (line 2394, default 20, help "Number of non-target PUMAs"), copied to
  config['n_puma_groups'] at line 2820, read at line 1416 and passed as n_calib_groups to sample_calibration_and_target_uniform
  (def at line 1287; draws `size=int(n_calib_groups)` PUMAs without replacement at lines 1307-1313). The round-4 commands do not pass it,
  so 20 is the default; the driver run_section_3_2.py -> run_acs_yoep_fb_min21_permute.py never passes it either (it only writes
  "n_puma_groups": 20 into seeds_manifest.json, line 52).
- So 10, 15, 20, 30, 50 calibration PUMAs are obtained with --n_puma_groups on run_acs_experiments.py directly (the released launcher
  run_section_3_2.py cannot vary it). The census wrapper takes --n-puma and sets the same config key. Eligible target PUMAs number 212
  (size >= 21), so 50 is feasible (the sampler returns None if the pool is not larger than the number drawn).
- Side effect to know when the number is varied: the PUMA draw uses rng.choice(size=n) from the same seed, so draws for different n are
  not nested subsets of each other.

## 3. Acceptance 3 (item 3)
Round-4 commands (suite_main.log and suite_stdcp.log) run through the released driver on a byte-checked copy of the released tree
(copy verified file by file against the original by md5 before running; the original is read-only):
  run_section_3_2.py --alphas A --B 1000 --n_workers 4 --skip_stdcp, then
  recompute_acs_stdcp_randomized_min21.py --B 1000 --n_workers 4 --alphas A --skip_plot, for A = 0.1 and A = 0.2.
Result (w2_census_acceptance_released.csv, job 15b618f0): **53 of 53 values agree**, table 5: 12/12, table 12: 18/18, table 13: 22/22,
5_text: 1/1. The agreement rule is round 4's: |ours - paper| <= half_unit + 2 sqrt(paper_se^2 + ours_se^2), half_unit 0.0005 for coverage and 0.5
for width, ours_se = sd(ddof 1)/sqrt(1000); inf agrees with inf. The script that wrote round 4's acs_ghcp_reproduction.csv is not in the repository; I
rebuilt the rule and checked that it reproduces round 4's tolerance column on all rows (max difference 9.1e-13). Largest |ours - paper| / tolerance = 2.1e-4.
Beside the requirement, the Longleaf values equal round 4's local (Python 3.13) values: max |difference| 5.8e-11 over the 51 finite rows,
although digit-for-digit agreement was not expected.
Reduction: alpha 0.05 and 0.15 were not run (round 4 ran four alphas; no acceptance value uses them). Declared in deviations.
Environment: Python 3.11.16 in ghcp_venv, numpy 2.4.6, pandas 3.0.3, scikit-learn 1.8.0 (the released pins). No rebuild was needed.

## 4. The census wrapper (item 4): code/scripts/round5_conf_w2_census.py
It calls the released run_one_replicate per replicate with the config main() builds for the round-4 command (seeds 456 + 1009 b, row permutation
456 + 1009 b + 811). GHCP (released Donor-HCP), HCP, and Std-CP (studentized, randomized, local RF; the recompute script's path) are the released
function's outputs. within_plain and within_full come from round5_conf_w1_sim.f_within_plain and f_within_full, on the residuals
y - mu of the released HCP global random forest (fit_global on the replicate's HCP training split; the model HCP's own scores use). The
interval is mu(x_t) + [centre - q, centre + q] in dollars; within_full is the convex hull of the kept set and the exact set's coverage and an
is-it-one-interval flag are recorded. Assumptions and guarantees are in the script's docstring, written before any run:
within_plain and within_full both have expected coverage ceil((o+1)(1-alpha))/(o+1) (column expected_cov); finite iff o >= 9 at 0.1 and o >= 4 at 0.2.
Arguments: --alpha, --n-puma, --o (subset of 0,2,5,8,9,10,12,15,17,20), --B, --workers, --rep-from/--rep-to (chunks), --acs-csv, --out,
--check-against / --check-stdcp (released detailed CSVs), --skip-stdcp.
Validation on the round-4 setting (alpha 0.1, 20 PUMAs, o in 0,5,10,15,20, B = 1000 in four chunks of 250; w2_census_wrapper_check_merged.csv):
for GHCP at every o, HCP, and Std-CP at every o, 1000 of 1000 replicates have **identical coverage indicators** and widths within 1.2e-10 absolute (relative 4.8e-16);
the 1e-9 criterion holds everywhere. Std-CP is also reproduced.
Note on the width tolerance: widths are about 1e5 dollars, so 1e-9 absolute is about 1e-14 relative; the observed differences are at the 1e-16 relative level, which is floating-point rounding; I did not investigate their source.
Smoke on the full o grid with 10 calibration PUMAs, alpha 0.2, 8 replicates (job be550cf3) ran: within_full infinite for o = 2 only, finite from o = 5.
Environment note (record and continue): round4_conf_sim imports pyarrow, which ghcp_venv lacks. The wrapper appends the project env's site-packages
AFTER the venv's, so only pyarrow is taken from it (numpy, pandas, scipy, scikit-learn stay those of ghcp_venv; PROVENANCE records pyarrow_from and numpy_from).
Nothing in ghcp_venv was changed.

## 5. Numbers from the validation run (alpha 0.1, 20 PUMAs, 1000 replicates; w2_census_validation_summary_alpha10_K20_B1000.csv)
GHCP width (mean) 523195, 315773, 247714, 200557, 174906 at o = 0, 5, 10, 15, 20; HCP 531277.
within_plain (coverage, mean finite width): o=10 0.899, 227231; o=15 0.931, 269878; o=20 0.903, 180732; expected 0.909, 0.938, 0.905.
within_full: o=10 0.906, 221958; o=15 0.937, 262920; o=20 0.908, 170742; same expected values; the kept set was one interval in every replicate.
Both are infinite in every replicate at o = 5 (expected coverage 1.0). These are one setting at B = 1000 with no paired standard errors; they are not the W2 map.

## 6. Reading the queue (for sizing)
Elapsed: released alpha 0.1 2:22:19 and alpha 0.2 2:14:55 on 4 cores (steps 1 and 2 together); wrapper chunk of 250 replicates at 5 o values with Std-CP 0:28 to 1:46
(node contention); 8-replicate smoke 1:44. I did not time a full-grid, 1000-replicate job; the 8-replicate full-grid smoke took 52 s at 10 PUMAs. MaxRSS under 0.5 GB per 4-core job.
