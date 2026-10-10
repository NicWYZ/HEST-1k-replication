# Round 5, the prediction-set track, the W5 decision memo (end of track)

9 October 2026. Written by the oversight chat after reading `docs/round05/i02/conformal/round5_conf_final_report.md` at tag `round5-conf-final` (`33aa6c4`, pull request #18), `docs/round05/tracks/conformal/round5_conf_plan.md` section 6 and `docs/round05/tracks/conformal/round5_conf_theory.md` section B.5, and checking the report against `w3_acceptance.csv`, `w3_reproduction.csv`, `w3_report_numbers.csv`, `w5_report_numbers.csv`, `w5_map.csv`, `provenance_index.csv`, `code_deliveries.csv`, `.verify-exceptions-round5-conformal` and `W2_ghcp_settings/w2_sim_designs.csv`. Nicolas hands this to the prediction-set session in full. It closes the track. The session transcribes it into `docs/round05/tracks/conformal/round5_conf_plan.md` as section 7, commits this memo unchanged as `docs/round05/i03/conformal/round5_conformal_W5_decisions.md`, and then does only what section 6 lists.

**The gate rule, in the wording Nicolas approved.** Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. Contact with anyone outside the project is never the session's decision.

---

## 1. Acceptance

The closing report is accepted and the track is complete. Every number I checked reads back as quoted, except the two counts of section 2, and the predictions are scored as the report scores them. W3 ran as instructed on all four tasks, every job from a read-only snapshot, and the merge recomputed every number from rows that all record the same snapshot. W4 part B stayed inside its cap.

Acceptance checks 1 and 3 of W3 fail as written, and I accept both without a rerun. Check 1 already uses the W2 memo's tolerances, and two round-4 rows still differ. Both are `within` at $o = 10$, where the half split calibrates on 5 scores. One differs by one test spot in coverage and the other by $5.9 \times 10^{-8}$ in median width, about three times the tolerance. Check 3 has a tolerance of zero. Its coverage is exact, its mean width differs by at most $1.08 \times 10^{-8}$ and its median width by at most $1.4 \times 10^{-7}$, and the differences occur only where one of the two runs used an E5-2680 v4 or E5-2643 v3 node (`w3_p3p2_by_cpu.csv`).

The code-delivery rules worked. Four deliveries, one snapshot each, no script run from the clone, and the two cancellations made by the lead after checking the queue. The provenance index traces every record.

## 2. What I checked, and four corrections for the record

1. **The number of matched rows in W3 check 1 is 1,694,142, not 1,693,662.** The six rows of `results/round5/conformal/W3_real/merged/w3_reproduction.csv` sum to 1,694,142. `.verify-exceptions-round5-conformal` declares 1,693,662 as that sum, so the sweep passed a wrong value. The failing matches are four, two in part 1 and two in part 2, and they are the same two round-4 rows.
2. **The provenance index covers 87 Slurm jobs and the local runs.** The 88 distinct values of `slurm_job_id` in `provenance_index.csv` include `none`, which marks local runs.
3. **The closing page says that on HEST at $K = 10$ the simulation's map holds on every task.** On Indiana at $o$ from 9 to 15 the plain split is narrower than `within_full`, by at most 2% (W3.2, margin down to $-0.0192$ in `W3_real/w3_report_numbers.csv`). The paper says so.
4. **My W2 memo said the full conformal set inside the target group is 3 to 4 times narrower than GHCP from 9 labelled units.** Wherever the released GHCP is finite, the files give 2.0 to 4.1 times over $o$ from 9 to 20 and every number of groups, and 2.6 to 4.1 times at 20 groups (`W2_ghcp_settings/w2_sim_designs.csv`, `within_full` against `released_ghcp`). The ratio is largest at $o = 9$ and smallest at $o = 17$ to 20. With 10 groups GHCP is infinite in every replicate at $o$ from 9 to 12, and with 12 groups at $o = 9$.

These corrections are recorded here only. The report, the exceptions file and the result files stay as committed.

## 3. Readings for the paper's prediction-set section

1. **The map on real data at $K = 10$, at 90%.** HCP with no labelled target spots is the narrowest valid method up to $o = 5$ on every task. From $o = 9$ the full conformal set inside the target donor is 0.416 to 0.677 of HCP's width on every task. It is the narrowest method there except at $o = 17$, where `within` is narrower by discreteness, and on Indiana at $o$ from 9 to 15, where the plain split is narrower by at most 2%. `within_full` covers 0.900 to 0.923 at $o$ of 10, 25 and 100, in line with its guarantee $\lceil (o+1)(1-\alpha) \rceil/(o+1)$, which W3's check 2 confirms to within 0.005 (`W5_map/w5_report_numbers.csv`).
2. **The within-donor family.** Round 4 recommended the plain split from $o = 10$ and the half split `within` from $o = 25$. `within_full` replaces both from $o = 9$. On CCRCC it is 2.116 wide at $o = 10$ against the plain split's 2.321, 1.967 at $o = 25$ against 2.137 and 2.300, and 1.709 at $o = 100$ against 1.754 and 2.109 (`w5_report_numbers.csv`).
3. **GHCP and the number of calibration clusters.** At $K = 10$ GHCP is 1.23 to 1.55 times HCP's width and covers 0.992 to 0.999, so it is wide and conservative there. As $K$ rises on CCRCC, GHCP at $o = 5$ becomes narrower than HCP from $K = 12$, reaching 0.831 at $K = 20$, and 0.796 on the merged label set. On Indiana, at $K$ from 14 to 20, it stays within 4% of HCP. With the head held fixed, GHCP at $o = 5$ on CCRCC falls from 5.30 to 2.70 as $K$ goes from 10 to 20, against HCP's 4.47 to 3.25, so the calibration count alone produces the fall (`w5_report_numbers.csv`, parts 2 and 3).
4. **GHCP's own designs.** From 9 labelled units the full conformal set inside the target group is 2 to 4 times narrower than GHCP at every number of groups where GHCP is finite. Below 9 GHCP is the narrowest method finite in every replicate from 20 groups, at 0.825 of HCP's width at $o = 5$. The released code calibrates HCP on half of the reference groups, so the design of 20 groups sits at 10 calibration clusters on the map's axis, the same as the real-data map at $K = 10$ (`W5_map/w5_method_groups.csv`, `w5_map.csv`). Every row of the paper's map states, per method, the clusters it calibrates on and the clusters it fits its score on.
5. **Theory.** Two parts of Proposition 2 are direct corollaries of Tibshirani, Barber and Ramdas, Theorems 3 and 7. The bound for randomised methods and the floor of Proposition 1 rest on the round-4 proofs and were not found in print. The paper gives one remark with the proofs in an appendix. For $K + 1 \ge 1/\alpha$, in the revealed-law model of the theory document, HCP is not tight, and no valid symmetric method is narrower than HCP at a configuration of continuous laws, none lying wholly below HCP's threshold, without being wider at another configuration. That other configuration contains one group whose scores are all equal, so the paper states the result with that condition. Whether HCP is dominated in expected width is open, and the paper says so in its discussion.

## 4. The two items the report leaves to the oversight chat

1. **The two unreproduced round-4 rows.** Not rerun. The cause is understood, and the effect is one test spot in coverage on one row and a width difference in the eighth decimal place on the other.
2. **Dominance of HCP in expected width.** Not pursued in this round. The paper states it as open.

## 5. Answers to the escalations

1. **The two round-4 rows.** Section 4 item 1.
2. **Part 3 against part 2.** Accepted. The pattern by CPU family is recorded as an inference, as the report says.
3. **Cancellations.** Accepted. They followed the W2 memo's rule.
4. **Delivery 4.** Accepted. The comparison rules did not change.
5. **The split `w3_K_sweep` file.** Accepted, with the whole file on Longleaf and each piece's md5 committed.
6. **Partitions.** Accepted.
7. **The stray file.** Accepted as left.
8. **Unit-level stamps.** Accepted, since every stamp carries the frame id assigned to its unit.
9. **Scoring choices.** Accepted. They were committed before the merge.

## 6. What the session does before stopping

1. Transcribe this memo as plan section 7 and commit it, with this memo unchanged as `docs/round05/i03/conformal/round5_conformal_W5_decisions.md`, in one commit. Nothing else is edited.
2. After Nicolas has merged pull request #18, push `round5-conformal` once and open one pull request into `main` carrying that commit. No tag. Nothing is delivered to Longleaf, since the commit changes documents only.
3. Stop. The track is closed.
