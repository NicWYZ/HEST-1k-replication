# Round 4, the conformal track, the C4 decision memo (end of track)

2 October 2026. Written by the oversight chat after reading `docs/round4_conf_final_report.md` at tag `round4-conf-final` (`d65626f`, pull request #5) and checking its numbers against `results/round4/conformal/C3_real/c3_report_numbers.csv`, `c3_o_sweep_by_task.csv`, `c3_K_sweep_by_task.csv` and `c3_merge_checks.csv`. Nicolas hands this to the conformal session in full. It closes the track; there is no further stage, and the session does nothing after transcribing it as plan section 13 except what section 3 lists.

**The gate rule, in the wording Nicolas approved.** Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. Contact with anyone outside the project is never the session's decision.

---

## 1. Acceptance

The final report is accepted and the track is complete. Every number I checked reads back as quoted. The C3 grid is complete as instructed: CCRCC (24 donors and the 23-donor merge), Indiana, lung and ACS, three encoders on the HEST tasks, $o \in \{0, 5, 10, 25, 50, 100, 200\}$ with $K = 10$, the CCRCC $K$ sweep from 4 to 20 at both $\alpha$ with the training-donor count recorded, lung at $K \in \{6, 8, 10\}$, and `within_plain` present as a method in `c3_o_sweep.csv.gz`. The anchors (A4b to $10^{-12}$ in coverage, the merge with zero duplicated keys, the $K$ and $o$ units agreeing on their shared rows) pass. The GHCP paper's ACS tables reproduce at 53 of 53 values.

Predictions scored as the report scores them. The two that did not hold (C3.5's lung and ACS ordering, C3.6 on CCRCC and lung) are both cases where the real tasks have smaller cross-donor shortfalls than round 3 led me to expect, and the recentred interval over-covers rather than under-covers. Both are findings, not problems.

## 2. What the record says, for the paper

Three readings of the C3 tables go into the paper's prediction-set section beside the five points the report's closing page lists.

1. **The three regions of the $(K, o)$ map hold on real data.** At $K = 10$ GHCP covers 0.98 to 1.00 at every $o$ on every HEST task, is 1.23 to 1.49 times HCP's width at $o \le 10$, and is 1.5 to 2.3 times `within_plain`'s width wherever both are finite. `within_plain` covers 0.90 to 0.92 from $o = 10$ on every task. The joint-design statement is as the C2 memo put it: at $K$ near 10, fewer than about ten labelled spots per test slide buy nothing for the prediction set, and from ten on the within-donor split is the cheapest valid choice.
2. **Within the within-donor family, the plain split is the only finite choice below $o = 25$, and the recentred half-split (`within`, the GHCP paper's Std-CP form) is narrower from $o = 25$ on.** On CCRCC `within_plain` is finite at $o = 10$ (coverage 0.91, mean width 2.32) where `within` is infinite; at $o = 25$ `within` has width 2.14 against 2.30, and at $o = 100$ 1.75 against 2.11, both at coverage 0.90. The paper says so in one sentence, so a practitioner knows which to use at which $o$.
3. **The recentred cross-donor interval is a usable heuristic above $o = 25$ on CCRCC and lung but over-covers**, by 0.03 to 0.04, because the shift is applied to a quantile that was already conservative on those tasks; on Indiana it is at nominal from $o = 50$. It has no guarantee and is reported as the practitioner's shortcut, not a recommendation.

The ACS rows (escalation 1) use states and the PPI track's task definition and predictor, which is what the paper's ACS application uses on the inference side, so the two halves of the paper read the same dataset. The reproduction of the GHCP paper's own ACS task (California PUMAs) is the acceptance check and is cited as such. Nothing more is run.

## 3. What the session does before stopping

1. Transcribe this memo as plan section 13.
2. Nothing else. The pull request #5 stays open for Nicolas to merge with a merge commit; the session does not touch it.

## 4. Records and decisions on the escalations

- 1 (ACS grouping): accepted, read as in section 2.
- 2 (no manifest on Longleaf): accepted; the PPI track's transfer check covers the Longleaf copy and the parquet md5 matches.
- 3 (ACS $K \le 10$ within fold; the cross-fold extension to $K = 20$ has only a heuristic guarantee): the extension is not used in the paper.
- 4 (stamps carrying the lead's frame id, again): recorded. This happened in three sessions in a row despite the brief; the fix goes into `docs/WAYS_OF_WORKING.md` as a procedure (the lead writes each sub-agent's frame id into its brief and checks the stamp before merge), which the oversight chat applies on `main`.
- 5 (lung size-matching target): accepted as the core unit's documented choice.
- 6 (widths agree across CPU vendors to $10^{-10}$): recorded; coverage is unaffected and the tolerance rule of `WAYS_OF_WORKING.md` already covers it.
- 7, 8, 9: recorded. Local runs under Nicolas's section 11 item 7 were his instruction and are his.

## 5. Open decisions, above the sessions

- Whether to tell Dobriban and Lee about the pool rule and the tie convention: Nicolas with David and Dr. Zhu.
- Whether the $o = 0$ improvability question is pursued anywhere: not in this project's round 4 or 5; it is recorded as open.

## 6. Hand-off to the PPI track

The PPI track's Q5 reads `results/round4/conformal/C3_real/c3_o_sweep.csv.gz` from `main` after pull request #5 is merged, with `within_plain` as a method value, and records the merge commit. A separate note tells that session so.
