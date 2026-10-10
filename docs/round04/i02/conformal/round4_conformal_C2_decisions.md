# Round 4, the conformal track, the C2 decision memo

2 October 2026. Written by the oversight chat after reading `docs/round04/i01/conformal/round4_conf_C2_report.md` at tag `round4-conf-C2` (`fe36f6b`, pull request #3), `docs/round04/i01/conformal/round4_conf_lower_bound.md` and `docs/round04/i01/conformal/round4_conf_candidate_definitions.md`, and checking the report's numbers against the files it names. Nicolas hands this to the conformal session in full. Transcribe it into `docs/round04/tracks/conformal/round4_conf_plan.md` as section 12 before anything in it runs. Interval 2 (C3 and C4, ending at the C4 gate) starts when the transcription is committed and Nicolas has merged pull request #3.

**The gate rule, in the wording Nicolas approved.** Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. This track's gates are C2 (the go or no-go) and C4. Contact with anyone outside the project is never the session's decision.

---

## 1. Acceptance

The C2 report is accepted, and the verdict under the fixed criterion stands. No candidate goes forward. Every number I checked reads back as quoted from `c1_report_numbers.csv`, `c1_acceptance.csv`, `c2_criterion.csv`, `c2_report_numbers.csv` and `c1_pool_rule_summary.csv`. The two literal acceptance failures (HCP at $K = 50$ against nominal, and the semi-real width ratio at $N = 500$) are read as the report reads them: the first is HCP's own calibration level and passes against it, and the second is the secondary setting, with the primary setting (CCRCC spot counts) passing both parts at 0.0041 and 0.035. The GHCP reproduction, 254 of 254 values within Monte Carlo error with the cause of the non-identity traced to the interpreter, passes and is not rerun.

Predictions scored as the report scores them. Most of mine on magnitudes were wrong, and C1.5 was wrong in direction. Section 3 says what the grid shows instead and what C3 does with it.

## 2. Decisions on the report's open items

1. **The quantile tie convention** (section 7.1). Keep this track's convention. With $n$ finite calibration scores and the test atom of mass $\frac{1}{n+1}$, the split conformal threshold is the $\lceil (n+1)(1-\alpha) \rceil$-th smallest score, and the standard exchangeability argument gives coverage at least $1 - \alpha$. At $n = 9$ and $\alpha = 0.1$ that is the ninth of nine, finite. The released code's upward resolution at the exact tie returns $+\infty$ there, which is valid and strictly more conservative. C3 runs the standard convention as primary and reports the code's finiteness beside it in every cell where the two differ, which at $\alpha = 0.1$ is $K = 10$ at $o = 0$. The paper states the convention in one sentence.
2. **The pool rule** (section 6.5). The paper's rule, equation (8), is primary in C3 because the corollary is stated for it. The code's rule runs as the secondary variant in every C3 cell at $\alpha = 0.1$, as in C1. The paper says, in one sentence with the worked example, that the released code's pool is one group larger than equation (8) and that the published tables were produced under the code's rule. Whether the authors are told is Nicolas's decision with David and Dr. Zhu; never the session's.
3. **A Python 3.13 rebuild** for a bit-identical reproduction. No. The reproduction criterion was within Monte Carlo error, it is met, and the cause of the residual is identified and recorded. Nothing further is spent on it.
4. **The shipped summaries outside the paper's tables** (section 7.3). Recorded, not pursued.
5. **The released repeated-subsampling baseline** averaging quantiles rather than the set of Dunn, Wasserman and Ramdas (escalation 5). Recorded. C3 does not run repeated subsampling.
6. **K6's tables from the stopped local run** (escalation 7). Accepted as they are, since K6 does not go forward.

## 3. What C1 shows, and what it changes in C3

I read `c1_grid.csv` directly at normal tails, $N = 500$, $\tau = 0$, share 0.3, $\alpha = 0.1$. Three facts shape C3.

- **The size donation costs one reference group, and at $K$ near $1/\alpha$ that is the whole budget.** At $K = 10$, GHCP at $o = 0$ calibrates on 9 groups with a test atom of mass exactly $\alpha$, so it covers 0.999 at a price of 2.09 where HCP covers 0.983 at 1.50. At $o = 5$ and $o = 10$ GHCP is still wider than HCP at $o = 0$ (prices 1.78 and 1.62), and its coverage stays above 0.987 at every $o$ up to 100. At $K = 20$ the cost is small (GHCP 0.944 at $o = 0$ against HCP 0.941) and at $K = 50$ it is gone. GHCP's gain from $o$ is almost entirely the adaptation; without it (`ghcp_noad`) the price at $K = 10$, $o = 100$ is 1.35 against 1.03 with it.
- **The within-donor split at $o \ge 25$ is nominal and narrower than GHCP at every $K$.** It covers 0.928 at $o = 25$ and 0.902 at $o = 100$ (its expected values are $\lceil (n+1)(1-\alpha)\rceil/(n+1)$ with $n$ the calibrating half), at prices 0.82 and 0.68 against the mixture oracle. This is the cheapest valid method once a slide carries 25 labelled spots, and it beats GHCP on width in every cell the report lists.
- **Below $o = 25$ the comparator is infinite only because it was built as the GHCP paper's Std-CP**, which spends $\lfloor o/2 \rfloor$ observations on recentring and calibrates on the rest. A plain within-donor split that calibrates on all $o$ observations with no recentring is finite from $o = 9$ at $\alpha = 0.1$ and valid by the same argument. It was not in C1.

So the $(K, o)$ map has three regions at small $K$. At $o = 0$, HCP. For $0 < o < 25$, GHCP is finite where the within split is not, but on this generator it is as wide as HCP or wider. From $o = 25$, the within-donor split. The joint-design consequence, which the PPI track's Q5 will state, is that at $K$ near 10 fewer than about 25 labelled spots per test slide buy nothing for the prediction set.

**C3 changes.**

1. Add the plain within-donor split (all $o$ observations calibrate the absolute score, no recentring) as a method at every $o \ge 5$, named `within_plain`, beside the Std-CP form, which keeps the name `within`. Its assumptions and guarantee go in the docstring before it runs.
2. The scaled score is dropped from C3, since K5 fails the criterion. The CQR score stays, but only as the top-decile diagnostic of prediction C3.4, inside GHCP and `within_plain`, on CCRCC only, with the quantile heads of round 3's A4 (`code/scripts/round3_a4_scores.py` or its successor) imported unmodified. If those heads cannot be reused inside a day, C3.4 is scored "not tested" and the report says why.
3. Prediction C3.2 is replaced, because C1 refuted its premise. **C3.2 (revised).** At $K = 10$ on every HEST task GHCP covers at least 0.97 at every $o$ and is wider than `within_plain` at every $o \ge 25$; at $o \le 10$ GHCP's width is within 10% of HCP's at $o = 0$ or above it. On the CCRCC $K$ sweep GHCP's coverage at $o = 25$ falls from above 0.97 at $K = 10$ to 0.93 to 0.95 at $K = 20$. Score the original C3.2 as "not tested, premise refuted in C1" and the revised one as a prediction written before C3 ran.
4. **Prediction C3.6**, new. The recentred cross-donor interval (the pooled `donor`-design quantile after shifting by the labelled spots' mean residual) covers within 0.03 of the pooled quantile's cross-donor coverage at $o = 5$ and within 0.02 of nominal at $o \ge 50$ on CCRCC and Indiana, and under-covers by at least 0.03 at every $o$ on lung, where the failure includes scale.
5. The `c3_o_sweep.csv` columns stay exactly as fixed (task, label_set, encoder, method, score, alpha, o, K, fold, draw, coverage, width_mean, width_median, n_test, finite), with `within_plain` as a `method` value. Q5 reads this file.

Everything else in C3 runs as the instruction document and addendum 1 say. Fan-out stays at eight units by task and axis.

## 4. ACS in C3

The PPI track's Q0 `ppi_py` file has no clusters and is used for nothing. Nicolas has fetched the 2018 ACS PUMS person file (1-Year, 50 states and DC, every column) through `folktables`, and the PPI track is placing it at `results/round4/ppi/Q0_setup/acs_pums2018/` in the Longleaf project tree with an md5 check against `raw_manifest.json`. C3's ACS units read that directory read-only, verify the md5s against the manifest beside it before reading anything else, and record the PPI commit whose provenance it carries. `whose()` will return `sibling`; this memo is the permission. Reproduce the GHCP paper's ACS tables (5, 12, 13) by running the released code's own `real_data/acs/` processing at commit `d1a69f4a` on that file, which is the acceptance the instruction sets, and only then run C3's ACS rows. If the directory is not there when C3 starts, run the HEST units and add ACS when it appears, as the instruction allows; if it is still absent when the HEST units finish, the C4 report says so and ACS is not run.

## 5. The lower-bound scoping, closed

The scoping ends here, with the cap unspent, and the session does no more theory in this track. What it produced, and where it goes.

- **Propositions 1 and 2** are derived with proofs, and I checked Proposition 1's algebra and the step-3 construction of Proposition 2. The exchangeable analogue of Proposition 2 (a valid distribution-free set with $n < (1-\alpha)/\alpha$ calibration points must be infinite with positive probability) is standard, so the group-level version is a direct lift rather than a new result. Proposition 1, the quantitative coverage floor for methods that are finite almost surely, I have not seen stated, but it is a remark, not a contribution. Both go into the paper's prediction-set section as one remark with the proofs in an appendix, stating that for $K + 1 < 1/\alpha$ the price of validity is characterised (infinite expected width for every valid method, the forced infinite probability $1 - \alpha(K+1)$ attained by randomised HCP, and the floor $1 - \beta^\star$ for finite outcomes), and that for $K + 1 \ge 1/\alpha$ the question is open.
- **The switch rule** is invalid as stated (the point-mass counterexample), the repaired rule is valid only with laws revealed exactly, does not dominate HCP, and loses $K\gamma$ at finite $N_k$. It is not pursued and K6 is dropped. The section 5 conjecture is reported in the paper as open, in one sentence.
- Whether to write to Dobriban and Lee about the $o = 0$ question, the pool rule or the tie convention is Nicolas's decision with David and Dr. Zhu.

## 6. Where interval 2 runs

Every C3 and C4 job runs on Longleaf through Slurm, under `rc_tengfei_pi` as recorded, with walls sized from a sibling's `sacct` and never a blanket limit. Nicolas's section-11 instructions covered the C1 and C2 work they named and do not carry forward. Nothing runs locally unless Nicolas asks for that specific task in chat; each such request is recorded as a numbered extension of plan section 11 before the task runs. If a job has not started four hours after submission, the session tells Nicolas in chat what the job needs (inputs and sizes, memory, expected runtime, queue state) and keeps waiting; it does not move the job or harvest its inputs. Light gate-table work (merges, the criterion table, figures, the numeric-claim sweep) is covered by Nicolas's section-11 item 4 and stays as it is.

## 7. Procedural points

1. **The pull request.** Pull request #3 is open at `fe36f6b`. Nicolas merges it with a merge commit after handing over this memo. The C4 pull request follows plan section 9.
2. **The instruction document** is on `main` as `docs/round04/i01/conformal/round4_conformal_track.md`; this memo will be beside it as `round4_conformal_C2_decisions.md`. Neither is added to the branch.
3. **Writing.** `docs/round04/i01/conformal/round4_conf_lower_bound.md` and the C2 report render; keep display equations with each `$$` on its own line in the C4 report and the C3 outputs' documentation.
4. **Sub-agent frame ids.** Each brief states the sub-agent's own frame id, and the lead checks the stamp on each hand-back before merge.

## 8. What the C4 report decides

Besides the instruction's C3 and C4 content, the C4 report scores C3.1, revised C3.2, C3.3 (expected "not tested"), C3.4, C3.5 and C3.6, confirms that `c3_o_sweep.csv` carries `within_plain`, and closes with the one-page "What the conformal track established", whose last paragraph states what the paper's prediction-set section says. Report and wait.
