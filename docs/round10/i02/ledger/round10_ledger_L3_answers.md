# Round 10, track `ledger`, Nicolas's answers at gate L3

*8 November 2026, evening. Nicolas answered gate L3 in the oversight chat through two sets of question cards, which put to him the questions of `../../i01/ledger/round10_ledger_decisions.md`, section 8. His answers are recorded here in his terms, with the choice he picked where he picked one. Where they differ from the L3 documents, these answers win (`../../i01/final-runs/round10_final_runs_brief.md`, section 2).*

## 1. The answers

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
9. **The hand-off.** In his words, "the claude science sessions create their own clones. prepare everything on the repo after all ledger content is merged." The final-runs session creates its own clone on Longleaf as its first step. The hand-off is prepared once the ledger's pull request (#38) is merged.

## 2. What changes as a result

- **The final-runs brief** is revised in place on `main`. The session makes its own clone. The track starts after #38 is merged. F3 gains an E8 step, with its literature search first. V is decided by Nicolas after F3. P10.3 and FR8 are scored, since S3 stays.
- **The writing plan's** S3 and S5 paragraphs on E8 and V are superseded by items 4 to 6. They are corrected when track `paper` starts, since these answers win over the plan.
- **The state block** no longer lists E, R7-6, R7-7, R7-5 or O5 as waiting. P is decided. E8 and V wait on F3.
