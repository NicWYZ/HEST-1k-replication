# Round 5, the prediction-set track: operating plan

Branch `round5-conformal`. Written 7 October 2026 by the execution session. The instruction document is `docs/round05/i01/conformal/round5_conformal_track.md` on `main`, md5 `970bc28669e0c6354980b51d2030f27e`, which is identical to the copy Nicolas handed over. This plan transcribes its sections 6 and 7 unchanged as sections 2 and 3 below. Section 4 lists what in the instruction looks wrong or unclear. Section 5 records extensions Nicolas asks for in chat. Nothing in the instruction is changed here.

## 1. Starting point

The starting commit is `d82c3f33ce37fe2d7dbf5b527bfee9a9fb9ee935` on `main`, the merge of pull request 14. The branch was created from it in the local clone `~/hest-1k/HEST-1k-replication-conformal` with `git switch --no-track -c round5-conformal`. The option `--no-track` was needed because `.git/config` cannot be written from the sandbox.

Before the branch was made, the clone was on `round4-conformal` at `e20890747aa49d1b614d2309ec4f1bfe0877fa8a`. There was no `.git/index.lock`. The tracked file `docs/.DS_Store` had an uncommitted change made by Finder. As section 5 of the instruction requires, I told Nicolas and waited. On his instruction the file was restored with `git restore docs/.DS_Store`, which left the tree clean. The branch `round4-conformal` was not changed and is still at that commit.

The three md5s of section 3 of the instruction were read from `main` at the starting commit. They are `76fda34ee622e299bbaa806e5c8da98a` for `code/scripts/round4_conf_sim.py`, `2d8418677cf8290eec89a14c315b92cd` for `code/scripts/round4_conf_c3.py` and `0ad7ae8efe554c1f285e5f384a9fb7f5` for `code/scripts/round3_a0_harness.py`. All three match the instruction. They are confirmed again in the Longleaf clone in W0.

The gates are W2 and W5. At each gate the branch is committed, tagged, pushed and a pull request into `main` is opened, and the session stops. The session never merges.

## 2. The plan, transcribed from section 6 of the instruction

Three stages of experiments, one of theory that runs beside them, and a closing stage. Gates at W2 and W5.

### W0. Setup and anchors (half a day, capped at one day)

1. Read this document, `docs/WAYS_OF_WORKING.md`, the closing page and sections 4 and 6 of `docs/round04/i02/conformal/round4_conf_final_report.md`, `docs/round04/i01/conformal/round4_conf_C2_report.md` sections 6 and 7, `docs/round04/i02/conformal/round4_conformal_C2_decisions.md`, `docs/round04/i03/conformal/round4_conformal_C4_decisions.md`, `docs/round04/i01/conformal/round4_conf_lower_bound.md` in full, and part A5 of `docs/round05/00_prep/deck2/deck2_new_results_explained.md`. Transcribe section 6 into `docs/round05/tracks/conformal/round5_conf_plan.md` with the predictions of section 7. List anything in this document that looks wrong in a numbered section of the plan and in the W2 report. Do not change it.
2. Create the branch in the reused local clone as section 5 says, and make the Longleaf clone. Confirm the three md5s of section 3 in the Longleaf clone. Read the project tree's HEAD with `git --no-optional-locks rev-parse HEAD` and record it. If it is not `9d7277d`, record that as an escalation and change nothing. Run `whose()` on `results/round4/`. Confirm that the released GHCP code is at its path and at commit `d1a69f4a`, and find or rebuild its environment.
3. **Anchors, all on Longleaf.**
   - `round4_conf_sim.py` unmodified, on the cells `normal|K10|N500|share0.3|tau0.0` and `normal|K20|N500|share0.3|tau0.0` with 5,000 replicates, reproduces the matching rows of `c1_grid.csv`. Those rows were computed on a laptop, so the tolerance is $10^{-4}$ on coverage, $10^{-6}$ relative on the price of validity, and identical infinite fractions. Report the largest difference in each column.
   - `selftest` of `round4_conf_c3.py` passes. For `CCRCC:24` with `uni_v2` at $K = 10$, the rows at $o = 0$ and at $o = 25$ reproduce `c3_o_sweep.csv.gz` with coverage difference 0.0 and width difference at most $3 \times 10^{-10}$, which is the cross-vendor floor round 4 measured.
   - `round4_conf_c1_codepath.py` reproduces the mismatch counts of `ghcp_repro_longleaf/setup/c1_codepath.csv`.

Nothing in W1 starts until all three pass.

### W1. The simulation map, completed (three days; no gate, reported with W2)

**Why.** The paper's map needs every valid method on one grid, and the round-4 grid cannot say where the plain split overtakes HCP, where GHCP overtakes the plain split, or what a properly centred within-cluster set does between 9 and 25 labelled units.

**Script.** `code/scripts/round5_conf_w1_sim.py`. It imports the round-4 module unmodified, registers `within_plain` and `within_full` through `register_fast`, builds its own cells, and calls `run_cell` with the seed tag round 4 used, so that every round-4 row is reproduced and every replicate is paired across methods and across $o$.

**The grid.** $K \in \{9, 10, 12, 14, 16, 18, 20, 25, 30, 50\}$. $o \in \{0, 3, 5, 9, 10, 12, 15, 17, 20, 25, 35, 50, 100\}$. Units per calibration cluster $N \in \{21, 100, 500\}$ and the unequal setting, where 21 is the GHCP paper's group size. Between-cluster share of score variance $\in \{0.1, 0.3, 0.5, 0.9\}$ at $\tau = 0$ and $\tau = 0.3$, plus the cell with no cluster effect. The share of 0.9 is added because the GHCP paper's design has cluster effects that large, as its HCP width of 33.5 against 5.3 for the within-group baseline shows. Normal and $t_3$ tails, and the two semi-real cells. $\alpha \in \{0.1, 0.2\}$. 5,000 replicates. Methods are `pooled`, `hcp` and `one_per` at $o = 0$, and `ghcp`, `ghcp_noad`, `ghcp_r05`, `within`, `within_plain` and `within_full` at every $o$ they are defined for. Fan out by $K$, ten units, and split a $K$ into several jobs by cell where a sibling's runtime says so.

**Acceptance.**

1. Every (cell, method, $o$) already in `c1_grid.csv` at $K \in \{9, 10, 12, 20, 25, 50\}$ is reproduced at the W0 tolerances.
2. `within_plain` is infinite in every replicate for $o < 9$ at $\alpha = 0.1$ and for $o < 4$ at $\alpha = 0.2$, and finite in every replicate otherwise. `within` is infinite for $o < 17$ at $\alpha = 0.1$.
3. Wherever `within_plain` is finite its coverage is within three Monte Carlo standard errors of $\lceil (o + 1)(1 - \alpha) \rceil/(o + 1)$, which at $\alpha = 0.1$ is 0.900, 0.909, 0.923, 0.938, 0.944, 0.905, 0.923, 0.917, 0.902 and 0.901 at $o = 9$, 10, 12, 15, 17, 20, 25, 35, 50 and 100. The same holds for `within` with $n = o - \lfloor o/2 \rfloor$ in place of $o$.
4. `within_full` is finite in every replicate from $o = 9$ at $\alpha = 0.1$ and from $o = 4$ at $\alpha = 0.2$, and infinite below. Its coverage is within three Monte Carlo standard errors of the same expected value as `within_plain`'s.

**Predictions.** Unless a cell is named, they are read at normal tails, $\tau = 0$, 500 units per cluster and $\alpha = 0.1$.

1. W1.1. At $K \le 10$ GHCP is the narrowest valid method in no cell at any $o$.
2. W1.2. At $K \ge 20$ and share at least 0.3, GHCP is the narrowest valid method at $o = 3$ and $o = 5$, with a price 3 to 10% below HCP's.
3. W1.3. At $o \in \{9, 10, 12\}$ and share 0.3, `within_plain` is narrower than GHCP for $K \le 15$ and wider for $K \ge 25$, and `within_full` is narrower than GHCP at every $K$ up to 50.
4. W1.4. `within_full` is narrower than `within` at every $o$ from 20 to 50, by 5 to 18%, and wider at $o = 17$, where `within` calibrates on 9 scores. From $o = 9$ the narrowest valid method is `within_full` at every $K$ and every share of 0.3 or more. So in this generator GHCP's cells are those below 9 labelled units.
5. W1.5. At share 0.9 and $K = 20$, GHCP at $o = 5$ is at least 15% narrower than HCP, and `within_full` from $o = 9$ is at least 40% narrower than GHCP.

**Outputs.** `results/round5/conformal/W1_sim/w1_grid.csv` (one row per cell, method and $o$, with the columns of `c1_grid.csv`), `w1_narrowest_valid.csv` (one row per cell and $o$ with the narrowest valid method, its price, the runner-up, the margin and whether the margin exceeds two Monte Carlo standard errors), `w1_acceptance.csv`, `w1_report_numbers.csv`, `fig_w1_map.png`.

### W2. GHCP's own settings, with the missing comparators (three days; gate)

**Why.** The paper should show that at 20 groups our numbers agree with the GHCP paper's, and say what the map looks like in that paper's own designs once the within-group methods are on it and the number of groups is varied.

**Part 1, the paper's simulation designs.** Run the released launchers for the fixed design and for the Poisson design, unmodified, through `round4_conf_c1_ghcp_repro.py`, at $\alpha \in \{0.1, 0.2\}$ and $o \in \{0, 2, 5, 8, 9, 10, 12, 15, 17, 20\}$, with the released Std-CP kept on. Add `within_plain` and `within_full`, and this track's own `hcp` and `ghcp`, through a wrapper `code/scripts/round5_conf_w2_wrapper.py` that draws the same replicates from the released generator with the launcher's seeds. The released code is not edited. Then vary the number of reference groups over $\{10, 12, 15, 20, 30, 50\}$ in the fixed design, through the launcher's own argument if it has one and through the wrapper if it does not. 1,000 replicates per setting, as the paper.

**Part 2, the paper's census task.** Build the released pipeline's input on Longleaf from the raw person files under `raw/2018/1-Year/` with the released code's own processing under its `real_data/acs/`, as round 4 did on the Mac. Record its md5 and its row count, which should be 378,817, and run the released census experiment with the round-4 commands. Then add the two within-group methods through the wrapper, extend $o$ to the grid of part 1, and vary the number of calibration PUMAs over $\{10, 15, 20, 30, 50\}$.

Fan out by design and by number of groups. Size each job from `repro_jobs_sacct.csv`, where one chunk of the fixed design took one to three and a half hours on one core.

**Acceptance.**

1. Run the launchers first with the paper's own values of $o$, which are 0, 5, 10, 15 and 20. Their output equals the `ours` column of `c1_ghcp_reproduction.csv` for tables T2 and T3 to $10^{-9}$, since both ran on Longleaf under one environment. Only then run the extended grid. If the environment had to be rebuilt and the values differ, the test is the agreement rule of `round4_conf_c1_ghcp_compare.py` against the `paper` column, and the difference is an escalation.
2. On every replicate, the wrapper's HCP and GHCP coverage indicators equal the launcher's, and their widths agree to $10^{-9}$. The wrapper is not used until this passes.
3. The census run on Longleaf agrees with `acs_paper_reference.csv` under the same agreement rule at 53 of 53 values. Digit-for-digit agreement with round 4's local run is not expected, because that run used Python 3.13.
4. `within_plain` and `within_full` meet W1's acceptance checks 2 to 4 in these designs.

**Predictions.** In the fixed design at 20 groups and $\alpha = 0.1$ unless another setting is named.

1. W2.1. `within_full` is finite in every replicate from $o = 9$, and at $o \in \{10, 15, 20\}$ it is at least 40% narrower than GHCP, whose widths there are 21.2, 17.5 and 13.6.
2. W2.2. `within_plain` is within 25% of GHCP's width at $o = 10$ and wider than GHCP at $o = 20$, because it does not centre and the cluster effects in this design are large.
3. W2.3. At $o = 5$ and $o = 8$ GHCP is the narrowest valid method, and at $o = 5$ it is 10 to 25% narrower than HCP.
4. W2.4. At $o = 5$, GHCP is wider than HCP with 10 groups, and its width is 0.75 to 0.92 of HCP's with 20 or more.
5. W2.5. On the census task with 20 calibration PUMAs, GHCP remains the narrowest valid method at every $o \le 20$, so the paper's own finding stands with the comparators added. With 10 it is wider than HCP at $o \le 10$.

**Outputs.** `results/round5/conformal/W2_ghcp_settings/w2_sim_designs.csv`, `w2_census.csv`, `w2_narrowest_valid.csv`, `w2_wrapper_check.csv`, `w2_acceptance.csv`, `w2_report_numbers.csv`, `fig_w2_fixed_design.png`, `fig_w2_census.png`. Report W1 and W2 together as `docs/round05/i01/conformal/round5_conf_W2_report.md`, with the state of the W4 document, tag `round5-conf-W2`, and stop.

### W3. Real data above 10 calibration donors (four days; no gate, reported at W5)

**Why.** Every real study the paper speaks to has more than 9 clusters, and round 4 mapped labelled units only at 10.

**Script.** `code/scripts/round5_conf_w3.py`, which imports `round4_conf_c3.py` unmodified and adds `within_full`. The labelled units at each $o$ are the first $o$ of the round-4 label stream, so every round-4 row is reproduced.

**Part 1, the fine grid at 10 calibration donors.** $o \in \{3, 5, 9, 10, 12, 15, 17, 20, 25, 50, 100\}$ on both kidney cancer sets, Indiana and lung, with `ghcp`, `ghcp_noad`, `within`, `within_plain`, `within_full` and `recentred`, and `pooled`, `hcp` and `one_per` at $o = 0$.

**Part 2, the sweep over $K$ with labelled units.** $K \in \{10, 12, 14, 16, 18, 20\}$ on both kidney cancer sets and $K \in \{10, 14, 18, 20\}$ on Indiana, each at $o \in \{0, 5, 10, 15, 17, 25, 50\}$ with the methods of part 1. The number of training donors falls as $K$ rises, from 13 to 3 on kidney cancer with 24 donors, from 12 to 2 on the merged set and from 14 to 4 on Indiana, and is written on every row. Comparisons between methods are made within a $K$.

**Part 3, the sweep in which only $K$ changes.** On kidney cancer with 24 donors and on Indiana, fix the head at the training donors of the $K = 20$ design, and calibrate on the first $K$ donors of that design's calibration permutation for each $K$ of part 2. The calibration sets are nested and the head is the same at every $K$. This is the sweep to read across $K$.

Lung has 15 donors and stays at $K = 10$. The census task is covered by W2, since its state design cannot go above 10 calibration clusters with a guarantee.

Fan out by task and part, eight units.

**The output format is fixed**, because the inference track reads it. `results/round5/conformal/W3_real/w3_map_by_task.csv` has columns task, part, alpha, K, n_T_donors, o, method, valid, coverage, coverage_sd_folds, width_mean, finite, narrowest_valid. Coverage and width are means over encoders of the mean over folds of the per-fold mean over draws, as round 4. `valid` says whether the method carries a guarantee, and `narrowest_valid` marks one method per task, part, alpha, K and $o$.

**Acceptance.**

1. Every row of part 1 and part 2 that exists in `c3_o_sweep.csv.gz`, in the round-4 $K$ sweep or in `frag_CCRCC_K/ghcp_o25/` is reproduced with coverage difference 0.0 and width difference at most $3 \times 10^{-10}$.
2. `within_plain` and `within` cover within 0.005 of their expected values of W1's acceptance check 3 on every task. Round 4's rows were within 0.002.
3. `within_full` covers within 0.005 of the same expected value as `within_plain` on every task.

**Predictions.** At $\alpha = 0.1$.

1. W3.1. At $K = 10$ on every task, GHCP is wider than HCP at $o = 3$ and $o = 5$ by a factor of 1.2 to 1.5, and from $o = 9$ the narrowest valid method is `within_full`, at 0.45 to 0.65 of HCP's width for $o$ from 9 to 15.
2. W3.2. `within_full` is 5 to 15% narrower than `within_plain` at every $o$ from 9, and 5 to 12% narrower than `within` from $o = 20$. The first margin is small because on these tasks a donor's offset is well under one standard deviation of its residuals.
3. W3.3. On kidney cancer at $o = 5$, GHCP's width is within 8% of HCP's at every $K$ from 12 to 20, so on these data GHCP has no cell below 9 labelled units where it is narrower by a margin that matters.
4. W3.4. In part 3 the within-cluster methods do not change with $K$ and GHCP's width falls with $K$. At $o$ from 9 to 25 GHCP is not the narrowest valid method by more than 5% at any $K$ up to 20.
5. W3.5. Indiana repeats kidney cancer's pattern in parts 2 and 3.

**Outputs.** `results/round5/conformal/W3_real/w3_o_sweep.csv.gz` and `w3_K_sweep.csv.gz` with the fifteen columns of round 4's `c3_o_sweep.csv` and `n_T_donors`, `w3_fixed_head.csv.gz`, `w3_map_by_task.csv`, `w3_by_fold.csv`, `w3_acceptance.csv`, `w3_report_numbers.csv`, `fig_w3_map.png`, `fig_w3_fixed_head.png`.

### W4. Two theory questions (five working days in total, capped; run by the lead beside W1 to W3)

Write `docs/round05/tracks/conformal/round5_conf_theory.md` as you go, with each step marked derived, conjectured or failed. `docs/round04/i01/conformal/round4_conf_lower_bound.md` is a record and is not edited. Keep a reading log at the head of the new document, one row per paper, with its identifier, whether the full text, the abstract only or nothing could be opened, the sections read and the date. A paper whose full text was not opened is not cited for anything beyond its abstract.

**Part A, whether the two propositions are in print (at most one and a half days).** Proposition 1 is the coverage floor $1 - \beta^\star(K, \alpha)$ for a valid method that is finite almost surely when $K + 1 < 1/\alpha$. Proposition 2 is that every valid method returns an infinite set with probability at least $1 - \alpha(K + 1)$. The degenerate hierarchical model, in which every group's law is a point mass, is ordinary exchangeable data with $n = K$, so a statement for ordinary data with $n + 1 < 1/\alpha$ transfers. Read Tibshirani, Barber and Ramdas in full first, then Vovk, Gammerman and Shafer on universality, Angelopoulos, Barber and Bates, Lei and Wasserman, Barber, Candès, Ramdas and Tibshirani, Vovk on conditional validity, Lee, Barber and Willett, the GHCP paper, and Dunn, Wasserman and Ramdas. For each proposition the outcome is one of three statements. It is in print, with the paper, the theorem number and the statement transcribed. Or it is a direct corollary of a named result, with the few lines written out. Or it was not found after the search the log records.

**Part B, whether HCP can be beaten when $K + 1 \ge 1/\alpha$ (at most three and a half days).** Unused time from part A may be spent here. The order of work is this.

1. Transcribe the optimality theorem of Tibshirani, Barber and Ramdas with its number, and say which sense of optimal it uses. Then write down three senses of "beaten" for grouped data. A method is dominated if another valid method is no wider in expectation under every law and narrower under some. It is beaten at a law if another valid method is narrower in expectation under that law. It is beaten in the minimax sense over a named class of laws. Say which of these the ordinary-data theorem answers.
2. Take randomised HCP as the baseline. Deterministic HCP is beaten by its own randomisation whenever the threshold's level is rounded up, and that is not the question.
3. Work first in the model of the round-4 document in which each group's law is seen exactly. The data are then $K$ laws drawn from $\Pi$, and the test unit is one draw from a further law that is not seen. Ask whether the universality argument lifts, that is, whether every valid method must satisfy the permutation form of validity of the round-4 document's section 2 and nothing more, and whether HCP is a conformal method for some score on that model.
4. Settle what is already known from round 4. The repaired switching rule is valid, is narrower than HCP when the groups look alike and is wider otherwise, so HCP is beaten at the homogeneous law and that rule does not dominate it. State this as a result with its conditions, including the loss at finite group sizes that section 8.4 of the round-4 document found.
5. Then attempt the question of dominance. Either construct a valid method that is never wider than randomised HCP and narrower somewhere, or show that none exists, or record the steps that failed.

Small numerical probes are allowed, as scripts `code/scripts/round5_conf_w4_*.py` with outputs under `results/round5/conformal/W4_theory/`. No method from this stage is run on the simulation grid or on real data. The four candidates of round 4 are closed and are not reopened.

**Stop rule.** At each cap write the document as a record of what exists and stop. The oversight chat decides at the gates whether anything is pursued.

**Predictions.**

1. W4.1. Proposition 2 is a direct corollary of a named universality or impossibility result for ordinary data, and is not found stated for groups.
2. W4.2. Proposition 1's floor is not found.
3. W4.3. Part B ends with the statement of step 4 written as a result and with dominance unresolved.

### W5. The closing report (two days; gate, end of track)

`results/round5/conformal/W5_map/w5_map.csv`, the map as one table, with source (simulation, the GHCP paper's designs, real data), the setting, $K$, $o$, the narrowest valid method, its width or price, the runner-up and the margin. One figure per source.

`docs/round05/i02/conformal/round5_conf_final_report.md` in the format of section 8, covering W1 to W4, the full predictions-against-outcomes table, an "Escalations" section, a section listing every statement of the round-4 closing page and of `docs/round04/i03/conformal/round4_conformal_C4_decisions.md` that this round changes with the old and new values, and a closing page titled "What the round-5 prediction-set track established", at most one page, every sentence naming its file. The closing page ends with one paragraph on what the paper's prediction-set section should say about GHCP, in numbers. Run the numeric-claim sweep. Tag `round5-conf-final`. Then stop.

**Time.** About fourteen working days with the gates, the theory stage running beside the others.

## 3. Predictions, transcribed from section 7 of the instruction

The stage predictions above, numbered W1.1 to W1.5, W2.1 to W2.5, W3.1 to W3.5 and W4.1 to W4.3, are the track's predictions. Copy them into `docs/round05/tracks/conformal/round5_conf_plan.md` before running and score each in the report of its gate as held, partly held, refuted or not tested. They are the oversight chat's. In round 4 most of its magnitude predictions were refuted and one was wrong in direction, so a refuted prediction is an ordinary outcome and is reported as plainly as a held one.

## 4. Points in the instruction that look wrong or unclear

These are listed under W0 item 1 and repeated in the W2 report. The instruction is not changed. How each one is handled until the oversight chat replies is stated beside it.

1. **The released Std-CP in the fixed design is not finite only from $o = 17$.** Section 2.3 calls `within` the GHCP paper's Std-CP and says it is finite from $o = 17$ at 90%. In the round-4 summary of our run of the released fixed design, Std-CP at $\alpha = 0.1$ is infinite in 648, 416 and 96 of 1000 replicates at $o = 5$, 10 and 15. So it is finite in some replicates at $o = 5$, which a half-split on $o$ units cannot be. Its mean finite width also rises with $o$, from 4.477936 at $o = 5$ to 5.295397 at $o = 20$ (`results/round4/conformal/C1_testbed/ghcp_repro_longleaf/compare/ours_fixedN21_summary_by_alpha_o_method.csv`). In the census reproduction Std-CP behaves as `within` would. At $\alpha = 0.2$ it is infinite at $o = 5$ and finite at $o = 10$ (`results/round4/conformal/C3_real/frag_ACS_o/acs_ghcp_reproduction.csv`). So in the released simulation launchers either Std-CP is a different construction or $o$ counts something else. Handling. Before W2 acceptance check 4 runs, I read the released fixed-design launcher and record exactly what its Std-CP calibrates on. Our `within` keeps the definition of section 2.3. The released Std-CP is reported beside it under its own name and is not called `within` unless the two agree replicate by replicate.
2. **W1 acceptance check 2 gives the finiteness of `within` only at $\alpha = 0.1$.** At $\alpha = 0.2$ a split on $n = o - \lfloor o/2 \rfloor$ scores is finite when $n \ge 4$, that is from $o = 7$. I check `within` at both levels. At $\alpha = 0.2$ it should be infinite below $o = 7$ and finite from $o = 7$, which on the W1 grid means finite from $o = 9$.
3. **$K = 15$ is in `c1_grid.csv` but not in the W1 grid.** The round-4 grid has $K \in \{5, 7, 9, 10, 12, 15, 20, 25, 50\}$ (`results/round4/conformal/C1_testbed/c1_grid.csv`), and acceptance check 1 names $\{9, 10, 12, 20, 25, 50\}$, which is consistent with the W1 grid. Prediction W1.3 speaks of $K \le 15$, which the W1 grid tests up to $K = 14$. The round-4 grid also has $N = 2000$ cells and the methods `dwr_rep` and `ghcp_r05code`, which W1 does not run. I read acceptance check 1 as covering the rows of `c1_grid.csv` whose cell, method and $o$ are all in the W1 grid. Adding $K = 15$ is a scope change, so it is a proposal and is not run.
4. **GHCP at $N = 21$ with $o \ge 21$.** GHCP needs a reference group with more than $o$ observations to donate a size. When every calibration group has 21 units, no group qualifies at $o \in \{25, 35, 50, 100\}$. In round 4, with an empty pool, GHCP reduces to the within-group split (`docs/round04/i01/conformal/round4_conf_C2_report.md` section 6.3). In W1, rows where GHCP's pool is empty are flagged in a column and are not counted as GHCP cells in `w1_narrowest_valid.csv`. I also confirm that the generator's test cluster has more than $o$ units at every $o$ on the grid, or record where it does not.
5. **The working on `within_full` checks out.** With $c(r) = (S + r)/(o + 1)$, the difference $(r_i - c)^2 - (r - c)^2$ factors as $(r_i - r)\bigl(r_i + r - 2c(r)\bigr)$. This is a quadratic in $r$ with leading coefficient $-(o - 1)/(o + 1)$. So the condition $s_i(r) \ge s(r)$ holds on the closed interval between its roots $r_i$ and $(2S - (o + 1) r_i)/(o - 1)$. A candidate outside every interval has count 1, and it is kept only when $1 > \alpha (o + 1)$, so the set is bounded once $\alpha (o + 1) \ge 1$. At $\alpha = 0.1$ that is from $o = 9$, and at $\alpha = 0.2$ from $o = 4$. The kept set has coverage $(o + 1 - \lfloor \alpha (o + 1) \rfloor)/(o + 1)$, which equals $\lceil (o + 1)(1 - \alpha) \rceil/(o + 1)$. This is the analytic check. The brute-force check runs in W1 before the method is used. This item is recorded as agreement, not as an error.
6. **The expected coverages in W1 acceptance check 3 are right.** I recomputed $\lceil (o + 1)(1 - \alpha) \rceil/(o + 1)$ at $\alpha = 0.1$ for each listed $o$ and they match to the three decimals given.
7. **The census `--target_index` is not the number of calibration PUMAs.** Section 3 of the instruction says it "appears to set the number of calibration groups". In the released `code/marginal/run_acs_experiments.py` (commit d1a69f4a) it is the row position of the target individual inside the target PUMA (default 20, lines 107 to 115, 1584 to 1585). The number of non-target PUMAs is `--n_puma_groups` (line 2394, default 20). Found by sub-agent 630c1298 (`results/round5/conformal/W2_ghcp_settings/part2/w2_part2_findings.md`). The PUMA-count sweep uses `--n_puma_groups` through the census wrapper's `--n-puma`.
8. **In the census task, "n calibration PUMAs" is split between training and calibration.** The released HCP calibrates on a restricted pool of $\lceil (1-\eta) n \rceil$ PUMAs with $\eta = 0.5$ and fits its global forest on the rest (`methods/donor_hcp.py`, `get_hcp_train_cal_split`, lines 154 to 172). So with 10 or 15 PUMAs it calibrates on 5 or 8, and it is infinite at $\alpha = 0.1$. Prediction W2.5's clause "with 10 it is wider than HCP at $o \le 10$" therefore cannot be scored by width at $\alpha = 0.1$.
9. **Prediction W1.4 contradicts itself.** Its first sentence says `within_full` is wider than `within` at $o = 17$. Its second says that from $o = 9$ the narrowest valid method is `within_full` at every $K$. At $o = 17$ both cannot hold. The W2 report scores the two sentences separately.
10. **Item 1 is resolved.** The released Std-CP fits a local random forest on a random half of the labelled units and calibrates on the other half with a randomised quantile. That quantile is infinite with probability $(n_{cal}+1)(1-\alpha) - n_{cal}$, which reproduces round 4's infinite counts (`results/round5/conformal/W2_ghcp_settings/part1/w2_stdcp_finiteness.csv`). It is reported as `released_stdcp`, beside `within`.
11. **The W2 wrapper accepted only the launcher's $o$ grid.** The validated wrapper (md5 766b6699bd939e767be124c64cc03174) asserted that every output $o$ lies in the launcher grid $\{0, 5, 10, \dots, 35\}$. So the first sim-design jobs, which used the extended grid $\{0, 2, 5, 8, 9, 10, 12, 15, 17, 20\}$, stopped at the assertion within seconds, before computing any replicate. Their job directories (`job1`, `job2`) are kept as failed attempts. The lead changed the wrapper so that its loop covers the launcher grid plus the requested $o$ values, while the random-stream emulation still runs only for launcher-grid $o$, in launcher order (md5 9c64eb0f6b56912e06654442f4a1ae6a, commit c8c061a). In a same-node regression on Longleaf (8 replicates of chunk 0 in each released design), all 464 rows per design at the shared $o$ values are identical to the old wrapper's, with width difference 0, and the random-stream self-test is unchanged (`results/round5/conformal/W2_ghcp_settings/sim_designs/regress_wrapper_ogrid/`). The production reruns write to `job1b`, `job2b` and so on.

## 5. Extensions requested by Nicolas in chat

Instructions, decisions and extensions given by Nicolas in chat on 7 October 2026. Items 5 and 6 are the local compute extensions.

1. **One pull request per gate.** There is exactly one pull request at W2 and one at W5. Each is opened only after its gate report is written, and Nicolas merges it after he and the oversight chat have reviewed the report. The session never merges. A rejected gate is fixed with new commits on the same open pull request.
2. **No push to GitHub between gates.** The branch and its tag are pushed only at a gate, together with that gate's pull request. Between gates, commits reach the Longleaf clone `/work/users/w/e/weiyang/hest_code/round5-conformal/` as a git bundle carried in a job's inputs, and the clone is fast-forwarded from the bundle. So commit hashes are the same as on the branch, and the clone is still updated only by fast-forward. This replaces the instruction's "fast-forward from your pushed branch" for the time between gates. From interval 2 the clone never fetches from GitHub. It is updated only from bundles, as section 6 item 4.2 sets out (W2 decision memo section 4 item 2).
3. **Parallel work always goes to sub-agents.** Every task that can run in parallel is given to its own sub-agent, as section 4 of the instruction says for each stage's units. This includes the three W0 anchors once the Longleaf clone exists. Each brief carries the sub-agent's own frame id and the stamp sentence of section 4. Sub-agents run no git command, and the lead checks every returned stamp and commits.
4. **The W0 c3 anchor is accepted as passing (7 October 2026).** At the literal tolerances the anchor did not pass (`results/round5/conformal/W0_anchors/c3_uni_v2/w0_c3_anchor.csv`), and a diagnostic, approved by Nicolas, broke the differences down by the vendor of the round-4 reference (`results/round5/conformal/W0_anchors/c3_uni_v2_diag/w0_c3_diag_by_vendor.csv`). The six folds whose reference ran on Intel, the rerun's vendor, agree to 8.881784197001252e-16. All 223 width_mean rows above 3e-10 are in the 18 AMD-reference folds, with a maximum of 1.91047000441813e-08. Coverage is identical on every row. Nicolas decided that the anchor passes on same-vendor agreement and identical coverage. The cross-vendor drift on $o > 0$ rows, at most 1.91047000441813e-08 in width, is an escalation for the W2 report and the width tolerance for W3's cross-vendor reproduction checks. Coverage stays at 0.0.
5. **Extension 1, local reading of result tables (7 October 2026).** Nicolas allowed small local tabulations of returned result files (reads, filters, group-bys) for writing the W1 and W2 report, for this interval only. Merges, figures and all computation stay on Longleaf.
6. **Extension 2, local compute where faster (7 October 2026).** Nicolas wrote in chat that if local compute is faster, it should be used. For the rest of this interval, up to the W2 gate, a task runs on his Mac when that is clearly faster than Longleaf. Each local run's PROVENANCE.txt records the host, library versions, the md5 of every script and input, and the command line. The exception is runs that must match an existing Longleaf result at a tight tolerance: W2 acceptance checks 1 and 2, and any table whose rows sit beside Longleaf rows. Those stay on Longleaf, because round 4 found that the two platforms' Python versions give the released GHCP code different random streams. Each table is produced on one platform only.

7. **Extension 3, local compute in interval 2 (8 October 2026).** Nicolas wrote in chat that local compute is preferred if it is genuinely faster, until he says stop. It applies on the same terms as extension 2. Each local run's PROVENANCE.txt records the host, library versions, the md5 of every script and input, and the command line, and each table comes from one platform. Runs that must reproduce Longleaf rows at a tight tolerance stay on Longleaf, and so does any run whose inputs live only there. That covers the W3 production, which reproduces round-4 rows to $1.91 \times 10^{-8}$ from embeddings on Longleaf. Merges, tabulations, figures and the numeric-claim sweep of this track's documents run locally when that is faster.

Apart from extensions 1 to 3 above, nothing runs on Nicolas's Mac except git operations in this clone and reading committed files, unless he asks for a specific task here first. Merges, comparisons, figures and the numeric-claim sweep run on Longleaf by default. Before this was written down, two small comparisons ran locally on files already in the clone. One checked the instruction's quoted numbers against the round-4 tables for section 4. The other rechecked the W0 sim anchor's 120 returned rows against `c1_grid.csv`. Both are recorded here and in the W2 report.

## 6. The W2 decision memo, transcribed

The oversight chat's memo of 8 October 2026 is committed unchanged as `docs/round05/i02/conformal/round5_conformal_W2_decisions.md`. This section transcribes what it changes. Interval 2 (W3, the rest of W4, W5) starts once this section and the memo are committed locally.

**6.1 The gate rule.** No stage after a gate starts until the oversight chat has reviewed the report and replied, and that means every stage. Inside an interval there are no interim reports or stop conditions. Anything that would have halted work is handled under the decision boundaries, recorded in the "Escalations" section of the next report, and work continues. Contact with anyone outside the project is never the session's decision. This track's gates are W2 and W5.

**6.2 Acceptance of W2.** The W2 report is accepted.

- W1 checks 3 and 4 pass against chance.
- W2 check 1 passes under the agreement rule.
- W2 check 4 passes.
- W1.4's first sentence is the one that holds.
- W2.4 and W2.5 could not be scored as written at 90%.

Nicolas merges pull request #16. Nothing is pushed to `round5-conformal` until that merge has happened.

**6.3 Readings for the paper** (memo section 3; used in the W5 closing page).

1. *The map in simulation.* At 90%, normal tails and share 0.3 or more, the narrowest method is HCP at $o = 0$, GHCP at 3 to 5 labelled units from about 14 calibration clusters, and `within_full` from $o = 9$. The exception at $o = 17$ is discreteness, stated in one sentence.
2. *GHCP's own designs.* From 9 labelled units `within_full` is 3 to 4 times narrower than GHCP at every number of groups. Below 9, GHCP is the narrowest method finite in every replicate from 20 groups. On the census, GHCP is narrowest at every $o \ge 2$ with 30 or 50 PUMAs, and `within_full` is narrower at $o = 9$ and 10 with 20. GHCP's guarantee held throughout.
3. *The number of groups.* The released code calibrates HCP on half of the reference groups. So every GHCP-design row states, per method, how many groups it calibrates on and how many it uses to fit its score.

**6.4 Code delivery and provenance** (memo section 4, shared with the inference track; it replaces any earlier practice).

1. One GitHub push per gate: the branch and the tag together, then one pull request. Nothing is pushed while a gate pull request is open and unmerged.
2. Commits reach Longleaf as `git bundle create <file> <last delivered>..round5-conformal`. A short Slurm job in `/work/users/w/e/weiyang/hest_code/round5-conformal/` runs `git bundle verify`, `git fetch <file> round5-conformal` and `git merge --ff-only FETCH_HEAD`, then prints the new HEAD. A failed fast-forward changes nothing and is recorded. The clone never fetches from GitHub, and is never rebased, reset or switched to another branch.
3. The same job writes the delivered commit's `code/` to `/work/users/w/e/weiyang/hest_code/round5-conformal_snapshots/<full hash>/` with `git archive` and removes write permission from it. Jobs put that snapshot's `code/scripts` on `PYTHONPATH`, run scripts from there, and run from their own output directory. They never run from the clone or from scripts copied loose into a job directory. Committed data files are read from the clone. Nothing is edited on Longleaf.
4. Each delivery is one row of `results/round5/conformal/code_deliveries.csv`: date, Slurm job id, HEAD before and after, bundle md5, the commits carried, and the snapshot path.
5. Every job records its snapshot commit and the md5 of each script it ran. Commits that change only documents or results need not be delivered.
6. Before each gate push, `results/round5/conformal/provenance_index.csv` lists one row per job and script, with two checks. The first is that the recorded commit is an ancestor of the gate tag. The second is that the md5 equals the script's md5 at that commit. Failures are listed in the report. At W5 it also covers every W0 to W2 job.
7. Results come back by the route in use and are committed locally.
8. Only the lead cancels a Slurm job, after confirming it with `squeue -u weiyang` and the track's job ledger. A sub-agent never runs `scancel`; it asks the lead.
9. New sweep exceptions go to `.verify-exceptions-round5-conformal`, and this track sweeps its own documents with `--exceptions` pointing at it. The W2 lines already in `.verify-exceptions` stay. The README is swept by the oversight chat. No file outside this track's areas is edited.

Staging committed scripts into jobs (W2 report, escalation 4) ends here, and snapshots replace it. The first delivery carries everything from the clone's HEAD, `aec684f`, to the commit that adds the memo.

**6.5 W3, changed.**

1. Reproduction tolerances: coverage agrees exactly, and width agrees within $1.91 \times 10^{-8}$, in place of $3 \times 10^{-10}$. Every W3 job records its CPU model. A row whose coverage differs is reported with both CPU models. W3 uses no random forest, so its production is not pinned to a node class.
2. The fixed-design T2 chunks are not rerun on round 4's node class.
3. W3.1 is amended. Its last clause reads: "and from $o = 9$ the narrowest valid method is `within_full`, except at $o = 17$, at 0.45 to 0.65 of HCP's width for $o$ from 9 to 15". Both the amended and the original wording are scored.
4. In `w3_map_by_task.csv`, $K$ is the number of calibration donors and `n_T_donors` the number the head was trained on.

**6.6 W4.** Part A is accepted as closed. W4.1 is scored as partly held at W5. Part B step 5, dominance, runs beside W3 under part B's cap of three and a half days, plus part A's unused time.

**6.7 W5, with one addition.** `w5_map.csv` places every row on one axis: the number of clusters each method calibrates on. For each W2 method, it gives the number of groups calibrated on and the number used to fit the score, read from the released code (`methods/donor_hcp.py`, `get_hcp_train_cal_split`, and the matching GHCP and Std-CP code). The closing page's GHCP paragraph states items 2 and 3 of 6.3 in numbers.

**6.8 Answers to the W2 escalations.** All thirteen are accepted or resolved as follows:

- escalation 1: by 6.5 item 1;
- escalation 4: by 6.4 item 3;
- escalation 5: no rerun;
- escalation 6: one node class per production table, with the W2 tables as the record, and their differences from part 1 and round 4 stated once at W5;
- escalation 9: both HCPs are reported where they differ;
- escalation 12: by 6.4 item 8.

The README value 0.1018 is the oversight chat's to fix.

## 7. The W5 decision memo, transcribed

The oversight chat's memo of 9 October 2026 is committed unchanged as `docs/round05/i03/conformal/round5_conformal_W5_decisions.md`. It closes the track. This section transcribes it. After it, the session pushes `round5-conformal` once, opens one pull request into `main` and stops.

**7.1 The gate rule.** As 6.1. This was the track's last gate.

**7.2 Acceptance of W5.** The closing report (`docs/round05/i02/conformal/round5_conf_final_report.md`, tag `round5-conf-final`, `33aa6c4`, pull request #18) is accepted and the track is complete. The predictions are scored as the report scores them.

- W3 acceptance checks 1 and 3 fail as written. Both are accepted without a rerun.
- Check 1's two failing round-4 rows are `within` at $o = 10$, where the half split calibrates on 5 scores. One differs by one test spot in coverage, the other by $5.9 \times 10^{-8}$ in median width.
- Check 3's coverage is exact. Its mean width differs by at most $1.08 \times 10^{-8}$ and its median width by at most $1.4 \times 10^{-7}$, only where one run used an E5-2680 v4 or E5-2643 v3 node (`results/round5/conformal/W3_real/merged/w3_p3p2_by_cpu.csv`).
- The code-delivery rules worked. There were four deliveries with one snapshot each, no script ran from the clone, and the lead made both cancellations after checking the queue. The provenance index traces every record.

**7.3 Four corrections, recorded here and in the memo only.** The report, `.verify-exceptions-round5-conformal` and the result files stay as committed.

1. The rows matched in W3 check 1 number 1,694,142, the sum of the six rows of `W3_real/merged/w3_reproduction.csv`, not 1,693,662 as the report and the exceptions file give. The failing matches are four, two in part 1 and two in part 2, from the same two round-4 rows.
2. The provenance index covers 87 Slurm jobs and the local runs. The 88 distinct values of `slurm_job_id` in `provenance_index.csv` include `none`, which marks local runs.
3. The closing page says the simulation's map holds on every task at $K = 10$. On Indiana at $o$ from 9 to 15 the plain split is narrower than `within_full`, by at most 2% (W3.2, margin down to $-0.0192$ in `W3_real/w3_report_numbers.csv`).
4. The W2 memo's "3 to 4 times narrower" for `within_full` against GHCP from 9 labelled units is, wherever the released GHCP is finite, 2.0 to 4.1 times over $o$ from 9 to 20 and every number of groups, and 2.6 to 4.1 times at 20 groups (`W2_ghcp_settings/w2_sim_designs.csv`). The ratio is largest at $o = 9$ and smallest at $o = 17$ to 20. With 10 groups GHCP is infinite in every replicate at $o$ from 9 to 12, and with 12 groups at $o = 9$.

**7.4 Readings for the paper's prediction-set section** (memo section 3).

1. *The map on real data at $K = 10$, at 90%.* HCP with no labelled target spots is the narrowest valid method up to $o = 5$ on every task. From $o = 9$, `within_full` is 0.416 to 0.677 of HCP's width on every task. It is the narrowest method there except at $o = 17$, where `within` is narrower by discreteness, and on Indiana at $o$ from 9 to 15, where the plain split is narrower by at most 2%. `within_full` covers 0.900 to 0.923 at $o$ of 10, 25 and 100, in line with its guarantee $\lceil (o+1)(1-\alpha) \rceil/(o+1)$, which W3's check 2 confirms to within 0.005 (`W5_map/w5_report_numbers.csv`).
2. *The within-donor family.* Round 4 recommended the plain split from $o = 10$ and `within` from $o = 25$. `within_full` replaces both from $o = 9$. On CCRCC it is 2.116 wide at $o = 10$ against the plain split's 2.321, 1.967 at $o = 25$ against 2.137 and 2.300, and 1.709 at $o = 100$ against 1.754 and 2.109 (`w5_report_numbers.csv`).
3. *GHCP and the number of calibration clusters.* At $K = 10$ GHCP is 1.23 to 1.55 times HCP's width and covers 0.992 to 0.999. As $K$ rises on CCRCC, GHCP at $o = 5$ becomes narrower than HCP from $K = 12$, reaching 0.831 at $K = 20$, and 0.796 on the merged label set. On Indiana, at $K$ from 14 to 20, it stays within 4% of HCP. With the head held fixed, GHCP at $o = 5$ on CCRCC falls from 5.30 to 2.70 as $K$ goes from 10 to 20, against HCP's 4.47 to 3.25, so the calibration count alone produces the fall (`w5_report_numbers.csv`, parts 2 and 3).
4. *GHCP's own designs.* From 9 labelled units `within_full` is 2 to 4 times narrower than GHCP at every number of groups where GHCP is finite. Below 9, GHCP is the narrowest method finite in every replicate from 20 groups, at 0.825 of HCP's width at $o = 5$. The released code calibrates HCP on half of the reference groups, so the design of 20 groups sits at 10 calibration clusters on the map's axis, the same as the real-data map at $K = 10$ (`W5_map/w5_method_groups.csv`, `w5_map.csv`). Every row of the paper's map states, per method, the clusters it calibrates on and the clusters it fits its score on.
5. *Theory.* Two parts of Proposition 2 are direct corollaries of Tibshirani, Barber and Ramdas, Theorems 3 and 7. The bound for randomised methods and the floor of Proposition 1 rest on the round-4 proofs and were not found in print. The paper gives one remark with the proofs in an appendix. For $K + 1 \ge 1/\alpha$, in the revealed-law model, HCP is not tight, and no valid symmetric method is narrower than HCP at a configuration of continuous laws, none lying wholly below HCP's threshold, without being wider at another configuration. That other configuration contains one group whose scores are all equal, so the paper states the result with that condition. Whether HCP is dominated in expected width is open, and the paper says so in its discussion.

**7.5 The two items the report left open.** The two unreproduced round-4 rows are not rerun, since the cause is understood and the effect is one test spot in coverage on one row and a width difference in the eighth decimal place on the other. Dominance of HCP in expected width is not pursued in this round, and the paper states it as open.

**7.6 Answers to the W5 escalations.** All nine are accepted:

- escalation 1: by 7.5;
- escalation 2: the pattern by CPU family is recorded as an inference;
- escalation 3: the cancellations followed the W2 memo's rule;
- escalation 4: the comparison rules did not change;
- escalation 5: accepted, with the whole file on Longleaf and each piece's md5 committed;
- escalations 6 and 7: accepted, the stray file as left;
- escalation 8: accepted, since every stamp carries the frame id assigned to its unit;
- escalation 9: accepted, since the choices were committed before the merge.

**7.7 What the session does before stopping.**

1. Commit this section and the memo in one commit. Nothing else is edited.
2. Pull request #18 is merged (9 October 2026). Push `round5-conformal` once, with no tag, and open one pull request into `main` carrying that commit. Nothing is delivered to Longleaf, since the commit changes documents only.
3. Stop. The track is closed.
