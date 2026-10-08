# Round 5, the prediction-set track, the W2 decision memo

8 October 2026. Written by the oversight chat after reading `docs/round5_conf_W2_report.md` at tag `round5-conf-W2` (`aec684f`, pull request #16), `docs/round5_conf_plan.md` and `docs/round5_conf_theory.md`, and checking the report against `w1_grid.csv`, `w1_whole_grid_counts.csv`, `w2_sim_designs.csv` and `w2_census.csv`. Nicolas hands this to the prediction-set session in full. Transcribe it into `docs/round5_conf_plan.md` as section 6, and commit this memo unchanged as `docs/decisions/round5_conformal_W2_decisions.md`, before anything in it runs. Interval 2 (W3, the rest of W4, and the W5 report) starts when both are committed locally.

**The gate rule, in the wording Nicolas approved.** Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. Contact with anyone outside the project is never the session's decision.

This track's gates are W2 and W5.

---

## 1. Acceptance

The W2 report is accepted. Every number I checked reads back as quoted, and the predictions are scored as the report scores them. The report reads the whole grid before it states the map, which is what the map needed.

- **W1 acceptance checks 3 and 4 pass.** The literal reading fails, but the number of cells beyond three Monte Carlo standard errors is what chance gives for exact methods (52 and 26 against 42 and 32 expected, 34 against 42 for `within_full`). The seed check is the right test of the one outlying cell, and it came out as chance.
- **W2 acceptance check 1 passes under the agreement rule**, as the instruction allows when the values differ. The cause is the CPU model under the released random forest, which part 1 showed by reproducing a round-4 chunk on a node of round 4's class.
- **W2 acceptance check 4 passes.** The one cell beyond three standard errors over-covers.
- **Prediction W1.4 contradicted itself.** That was my error. Its first sentence is the one that holds.
- **Predictions W2.4 and W2.5 could not be scored as written at 90%.** The released code calibrates HCP on half of the groups, which I did not know when I wrote them.

Nicolas merges pull request #16 after reading this memo. Nothing is pushed to `round5-conformal` until that merge has happened (section 4 item 1).

## 2. What I checked

In `w1_grid.csv`, cell `normal|K20|N500|share0.3|tau0.0` at 90%, HCP has half-width 2.91 at coverage 0.941, GHCP at $o = 5$ has 2.73 at 0.944, and at $o = 10$ `within_plain` has 2.50 at 0.907 and `within_full` 1.99 at 0.908. `w1_whole_grid_counts.csv` gives `within_full` as narrowest in 1,350 of 1,440 cells at share 0.3 and in 1,440 of 1,440 at share 0.9. In `w2_sim_designs.csv`, fixed design, 20 groups, 90%, the released GHCP is 27.55 wide at $o = 5$ against 33.40 for HCP, and from $o = 9$ `within_full` is 5.14 to 6.22 wide against 22.82 to 13.59 for the released GHCP. In `w2_census.csv` with 20 PUMAs, `within_full` is 210,334 and 221,958 dollars wide at $o = 9$ and 10, against 253,653 and 247,714 for GHCP, and GHCP is the narrower at $o = 12$ to 17. All of these are as the report quotes them.

## 3. Readings for the paper

1. **The map in simulation.** At 90%, normal tails and a between-cluster share of 0.3 or more, the narrowest method with a finite-sample guarantee is HCP with no labelled test units, GHCP at 3 to 5 labelled units once there are about 14 calibration clusters, and from 9 labelled units the full conformal set inside the test cluster. The one exception is $o = 17$, where the half split's rank is the largest of 9 scores and so sits lower than the full set's rank of 17 out of 18. That is discreteness, not a property of either method, and the paper says so in one sentence. With no cluster effect, or under $t_3$ tails at share 0.1, centring on a few residuals adds noise and other methods lead.
2. **GHCP's own designs.** From 9 labelled units the full conformal set inside the target group is 3 to 4 times narrower than GHCP at every number of groups tried. Below 9 GHCP is the narrowest method finite in every replicate once there are 20 or more groups. On the census task GHCP is narrowest at every $o \ge 2$ with 30 or 50 PUMAs, and with 20 PUMAs the full conformal set is narrower at $o = 9$ and 10. GHCP's guarantee held in every setting.
3. **What the number of groups means.** The released code calibrates HCP on half of the reference groups and fits its forest on the other half. So the GHCP paper's design of 20 groups calibrates HCP on 10 groups, the same number as our real-data map at $K = 10$. The two results agree once the size of the cluster effects is matched. In the paper's fixed design the between-group spread dwarfs the within-group spread (HCP 33.40 wide against `within_full` 5.14 to 6.22 at 20 groups). In W1 at share 0.9, GHCP is also the narrowest method at $K = 10$ and $o = 5$, which was the one exception to prediction W1.1. On the tissue tasks the share is smaller and GHCP is wider than HCP at $K = 10$. The paper's map uses one axis for the number of clusters a method calibrates on, so every GHCP-design row must state, per method, how many groups it calibrates on and how many it uses to fit its score.

## 4. How code reaches Longleaf, how the branch reaches GitHub, and what both tracks share

This section is word for word the same in the inference track's E2 decision memo and the prediction-set track's W2 decision memo, so the two tracks work the same way. It replaces the sentence of each instruction document that says the Longleaf clone is updated "by fast-forward from your pushed branch", and any plan extension or practice that says otherwise.

1. **GitHub sees one push per gate.** At a gate you commit the report, tag it, push the branch and the tag together, and open one pull request into `main`. Nothing is pushed between gates. Nicolas merges the pull request with a merge commit after the gate report has been reviewed. Do not push the branch again until that pull request is merged, because a push to a branch with an open pull request adds its commits to that pull request.
2. **Commits reach Longleaf as a git bundle.** In the local clone, create it with `git bundle create <file> <last delivered commit>..<your branch>`. Copy the file to Longleaf by the route you already use for inputs. A short Slurm job then runs, in your Longleaf code clone (`/work/users/w/e/weiyang/hest_code/round5-ppi/` or `/work/users/w/e/weiyang/hest_code/round5-conformal/`), `git bundle verify <file>`, `git fetch <file> <your branch>` and `git merge --ff-only FETCH_HEAD`, and prints the new HEAD. If the fast-forward fails, the job changes nothing and the failure is recorded. The clone never fetches from GitHub, is never rebased or reset, and never has another branch checked out.
3. **Jobs run from a fixed snapshot of a delivered commit.** The same delivery job writes the delivered commit's `code/` directory to `/work/users/w/e/weiyang/hest_code/<your branch>_snapshots/<full commit hash>/` with `git -C <clone> archive <commit> code | tar -x -C <that directory>`, and then removes write permission from it. A job puts that snapshot's `code/scripts` on `PYTHONPATH`, runs its scripts from there, and runs from its own output directory. It never runs scripts from the clone itself, and no script is copied loose into a job directory. Because a snapshot never changes, a new delivery can be made while jobs are still running on an earlier snapshot. Committed data files that a job reads, such as a round-4 table, are read from the clone, since no track changes them. Nothing is edited on Longleaf. A fix is a new local commit, a new delivery and a new snapshot.
4. **Each delivery is one row of `code_deliveries.csv`** in your results directory (`results/round5/ppi/` or `results/round5/conformal/`), with the date, the Slurm job id, the clone's HEAD before and after, the bundle's md5, the commits it carried and the snapshot's path.
5. **Every job records** the commit of the snapshot it ran from and the md5 of each script it executed. A commit that changes only documents or results need not be delivered.
6. **Before each gate push, two checks go into the report.** Every commit recorded in any `PROVENANCE.txt` of the interval is an ancestor of the gate tag. And every script md5 in any of them equals the md5 of that script at the commit the record names. List any record that fails either check. `provenance_index.csv` in your results directory has one row per job and script, with the job id, the unit, the script path, the md5, the recorded commit and the result of both checks. Commit the index, including rows for units whose own `PROVENANCE.txt` stays on Longleaf.
7. **Results** computed on Longleaf come back to the local clone by the route already in use and are committed there.
8. **Only the lead cancels a Slurm job,** and only after confirming with `squeue -u weiyang` and the track's job ledger that the job is the track's own. A sub-agent never runs `scancel`. It asks the lead.
9. **Files both tracks would otherwise edit.** Each track declares the exceptions of its numeric-claim sweep in its own file, `.verify-exceptions-round5-ppi` or `.verify-exceptions-round5-conformal`, and sweeps its own documents with `--exceptions` pointing at that file. Lines already in `.verify-exceptions` stay there. The README is swept by the oversight chat, not by the tracks. Neither track edits any other file outside its own areas.

**What this means for this track now.** Item 2 of section 5 of `docs/round5_conf_plan.md` already delivers commits as bundles. Its last sentence, which let the clone fetch from GitHub after a gate push, is replaced by item 2 above. The practice in the report's escalation 4, of staging committed scripts into a job while the clone stayed behind, ends with this memo, and snapshots replace it. The first delivery of interval 2 carries everything from the clone's current HEAD to the commit that adds this memo, and makes the first snapshot. At the W5 gate, `provenance_index.csv` also carries rows for every W0 to W2 job, read from their `PROVENANCE.txt` files, with the two checks applied. New sweep exceptions go to `.verify-exceptions-round5-conformal`. The lines this track added to `.verify-exceptions` for W2 stay.

## 5. Interval 2

### W3. As instructed, with these changes

1. **Tolerances for the reproduction rows.** Coverage must agree exactly. The width tolerance is the cross-vendor drift W0 measured, $1.91 \times 10^{-8}$, as Nicolas decided (report escalation 1), in place of the instruction's $3 \times 10^{-10}$. Every W3 job records its CPU model. A row whose coverage differs is reported with the CPU models of both runs. W3 uses no random forest, so its production is not pinned to a node class.
2. **No rerun of the fixed-design T2 chunks on round 4's node class** (escalation 5). The agreement rule settles acceptance, and the cause is understood.
3. **Prediction W3.1 is amended before W3 runs.** Its last clause now reads "and from $o = 9$ the narrowest valid method is `within_full`, except at $o = 17$, at 0.45 to 0.65 of HCP's width for $o$ from 9 to 15". The exception is the discreteness of section 3 item 1. Score both the amended and the original wording.
4. **The map's number of clusters.** In `w3_map_by_task.csv`, $K$ is the number of calibration donors, as now, and `n_T_donors` the number the head was trained on.

### W4. Part B continues

Step 5, dominance, runs beside W3 under part B's cap of three and a half days. Part A's unused time may be added to it, as the instruction allows. Part A is accepted as closed. Its outcome for Proposition 2 is that the probability bound for randomised methods was not found in print, and that two corollaries of Tibshirani, Barber and Ramdas give weaker statements. Score W4.1 as partly held on that basis at W5.

### W5. As instructed, with one addition

`w5_map.csv` places every row on one axis, the number of clusters each method calibrates on. Each W2 row gives, per method, the number of groups it calibrates on and the number it uses to fit its score, read from the released code (`methods/donor_hcp.py`, `get_hcp_train_cal_split`, and the matching code for GHCP and Std-CP). The closing page's paragraph on GHCP states section 3 items 2 and 3 in numbers.

## 6. Answers to the escalations

1. **Cross-vendor drift.** Recorded as Nicolas decided. Section 5, W3 item 1.
2. **`whose()` on `results/round4/`.** Accepted. Reading inputs the instruction names is not rebuilding.
3. **W1 checks 3 and 4.** Section 1.
4. **Staged scripts.** Replaced by section 4 item 3.
5. **The T2 rerun.** Not wanted.
6. **Node class.** Accepted, with one class per production table as you did. The W2 tables are the record. Their differences from part 1 and from round 4 are within what escalation 6 measured and are stated once in the W5 report.
7. **The released Std-CP.** Accepted. It stays `released_stdcp`, beside `within`.
8. **The census PUMA count and the half split.** Accepted, and section 5, W5 builds on it.
9. **Ties between this track's HCP and the released HCP.** Accepted. Report both where they differ.
10. **The wrapper's $o$ grid.** Accepted. The same-node regression was the right check.
11. **Cancelled launcher jobs.** Accepted.
12. **The `scancel` on another user's job.** Section 4 item 8 now governs this for both tracks.
13. **Record defects.** Accepted, since the merge recomputes every number from the rows.

The README value of 0.1018 that the sweep could not find predates this track and is the oversight chat's to fix.
