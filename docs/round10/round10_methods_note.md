# Round 10, methods note

*15 November 2026. Written at the round's close. It keeps, word for word, the parts of four decision files that define how the final runs were designed and scored and that no kept document states in full. The decision files themselves are at the tag `record-full-2026-11`. What stands now is in `README.md`.*

## 1. Nicolas's answers at gate L3 (8 November)

From `round10_ledger_L3_answers.md` (at tag `record-full-2026-11`), section 1, items 1 to 8. They describe the estimator, the coefficient and the scope that `i01/final-runs/round10_final_runs_brief.md`, `tracks/final-runs/round10_final_runs_plan.md` and every final-runs report use, and they win where they differ from `i01/ledger/round10_ledger_decisions.md`. Items 4 and 5 were later settled at gate F3 (section 4 below and `README.md`).

1. **E, the estimator.** Accepted as written. The final runs use the two-fold cross-fitted difference estimator in Mickey's form, with round 9's within-fold variance primary for that form, the exactly unbiased variance and $\max(\hat V, \hat V_w)$ beside it, and the switch rule of decisions section 1.1.
2. **The variance identity** (decisions section 1.2, item 3). Nicolas chose "I've checked it, lift it". The `[proposed]` label is lifted. The paper may show the exactly unbiased estimator in an appendix, with the identity behind it, credited to Mickey's (4.4).
3. **R7-6, the coefficient.** A fixed coefficient of 1, as recommended. The paper's primary estimator is the difference estimator with the coefficient fixed at 1 at every number of labelled clusters. The two-fold cross-fitted form is reported beside it from 6 labelled clusters, the classical estimator is the control, and no coefficient is fitted on the same clusters it is applied to.
4. **P, prediction sets.** In his words, "Keep S3; whether E8 is kept or not is deferred to after further analysis". So S3 stays with the narrowed claims of decisions section 3. E8 is not dropped. Its analysis runs in the final runs at F3 (his answer to item 6 below), and he decides E8 on that evidence.
5. **V, the share bound.** In his words, "further analysis first, then decide based on empirical evidence". The ledger's recommendation (unbounded first) is not adopted now. F3 reports both columns as the brief defines them, and Nicolas decides how the paper states regime B after F3.
6. **Where E8's analysis runs.** In the final runs, at F3. The literature search of the brief's section 7 comes first, then the analysis, and Nicolas decides at F3.
7. **The other recommendations** (decisions section 6). All accepted.
   - **R7-7.** `rej_t` where its support and one balance variable allow, the cluster-level cube design as the alternative, both rerun matched, with rejection on two balance variables reported as a limit.
   - **R7-5.** Broska and Howes reported as published, with `bh_t` and `bh_t_fpc` beside it, the correction credited to Cameron and Miller (2015) and Bell and McCaffrey (2002), and nothing about it claimed as the project's own.
   - **O5.** Nothing classical or in print is claimed. The estimator is credited to Mickey (1959) and Williams (1961), and round 9's theorems stay candidates.
8. **The departure from the ledger brief.** Confirmed. The 6-minute exact enumeration on toy populations in the cloud workspace (`results/round10/ledger/round10_ledger_L3_reads.md`, section 2) stands.

## 2. The F1 reply: corpus tasks, morphology covariate and breast Xenium's center design (10 November)

From `round10_final_runs_F1_decisions.md` (at tag `record-full-2026-11`), sections 1 to 3, describing the data of `i02/final-runs/round10_final_runs_F1_report.md` and every later stage. Option (c) was closed at F2 (section 3, item 15 below), and option (b) delivered the covariates on all six corpus tasks, so they carry $\mu$ and $\theta_1$ to $\theta_3$.

**Confirmed.** The corpus tasks are kidney Visium, breast ST, bowel Visium, brain Visium, breast Xenium and lung Xenium, with the counts of the report's section 3. Breast Visium is dropped. The audit's exclusions stand as listed in the report's section 7, item 2. These are the pooled-donor sections, the sections with a second donor's tissue, the kidney organoids, the unresolved RRST brain sections, the duplicate measurements and the unverifiable samples. The 89 samples kept on naming evidence stay in. Both flags are kept as the report states them. INT4 and INT24 stay as two donors (the 24-donor set primary, the merged set the sensitivity row), and NCBI599 and NCBI714 are not merged.

**Options (b) and (c), both.** Option (b) extends round 3's nuclear instrumentation (`frac_neoplastic`, `m_std`) to the corpus's patches, which is new computation on data already on Longleaf. Option (c) defines a corpus covariate from what the corpus carries. Under the brief's section 7, (c) starts with a literature search by sub-agents across survey sampling, econometrics and machine learning, with the queries logged. The search is reported to Nicolas, and a derivation or construction starts only after he has seen it and agreed the gap is genuine.

**Grouped** (Nicolas, 10 November, after the explanation given in the session and summarised here). Breast Xenium's center design holds out S0253 and S0254 together, and the files in `F1/predict/breast__Xenium__<encoder>__center_grouped/` are the center-design files of record.

In the corpus a breast Xenium "center" is a study: S0178, S0228, S0253, S0254 and S0255. Studies S0253 and S0254 hold sections of the same two donors (donor map `F1/audit_verdicts/donor_map__breast__Xenium.csv` on Longleaf, samples TENX94 to TENX97). Holding out S0253 alone would leave those donors' S0254 sections in the training set. The fold would then not be donor-disjoint, and its predictions would score the head on donors it had seen. The prediction script refuses such a fold, which is why the first runs stopped (Slurm `8687463`, `8687469`, `8687541`). Their donor designs completed and passed.

## 3. Settled deviations at gate F2 (11 November)

From `round10_final_runs_F2_decisions.md` (at tag `record-full-2026-11`), section 2. They fix how the F2 report (`i03/final-runs/round10_final_runs_F2_report.md`) and the later stages read and score its outputs, and they stood for the rest of round 10. Item numbers in brackets are those of the F2 report's section 7.

1. **FR6's frontier clause** [1] is scored on $\kappa$ of the fixed-coefficient residual $z - f$ against `kappa_sup`, from `diagnostics/f2_fr6.csv`, with `kappa_star_v1` reported beside it. FR6 is refuted under every reading.
2. **The fixed coefficient's cost** [2] is the share of genes where `fix1`'s median width exceeds `classical`'s. Plan section 5.3's claim that the median-width and mean-width readings agree was wrong. FR4 is scored on the median width, which the plan named, and the mean-width reading is reported beside it wherever the share is quoted.
3. **Rule (a) is rule (b) on the donor target** [4]. Round 4's `a_b1` and `b_cluster` are one formula there, and later stages report them as one arm.
4. **Kluger et al.'s cluster bootstrap runs under regime A's design** [5], simple random sampling of clusters with $\pi = n_L/G$, not under round 7's Bernoulli designs.
5. **The superpopulation interval is `fix1_nofpc`** [6], round 7's `round5_superpop` row, reported against the design target as a stated limit. No model term is computed, since round 5's script computes none.
6. **`frac_nonzero_y` is passed to `factor_rows` as missing** [7]. `pc1_share` is unchanged and one column of round 9's table stays empty.
7. **The switch rule's Monte Carlo error** [8] is the approximation $\text{ratio}\sqrt{2/(R - 1)}$, in place of the bootstrap over draws. The verdict, $\hat V_w$ primary for the cross-fitted form, stands.
8. **Jobs whose harness or `sacct` state reads failed with complete outputs** [10] (the first 21 regime A units, refit Slurm `8823487` and `8823488`) are taken as complete on their `PROVENANCE.txt` status, which every later stage reads in place of the harness state.
9. **$R^2_c$ in F2.6** [11] is round 9's squared correlation of donor values with donor predictions (`R2c_mean`), not F1's D12.
10. **The queue waits over four hours** [12] on the night of 10 November, given without the four-hour notice, are recorded as an escalation. Nothing further is done about them.
11. **The provenance index covers every stage** [13] through its stage argument (default F1), and each later gate runs it over all stages so far.
12. **The fourth session's missing notes and checkboxes** [14] are fixed in commit `59b7977d`.
13. **The `Pathology` sub-agent's searches before its frame-id message** [15] are recorded. No job, git or data was touched.
14. **The corpus estimands** [16] are $\mu$, with $\theta_1$ to $\theta_3$ on all six corpus tasks through option (b). The F1 report's sentence on $\theta_1$ was wrong.
15. **Option (c) is closed.** Option (b) delivered CellViT's covariates on every corpus task, so nothing is built from option (c), and its search stands as evidence (report, section 6.9).

## 4. Gates F3 and F4

The F3 decisions are kept whole in `i05/final-runs/round10_final_runs_F3_decisions.md`. Nicolas's reply at F4, recorded in `docs/round10/README.md` (formerly `round10_final_runs_F4_decisions.md`, at tag `record-full-2026-11`) on 15 November, was "Gate approved, close the track, leave any open items in the report." The final report's proposal of a further tag on the citation-fix commit was not taken up, so the gate tag stays on `fad48334` and the branch head carries the fix.
