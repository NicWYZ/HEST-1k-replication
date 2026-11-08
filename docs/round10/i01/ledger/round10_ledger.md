# Round 10, the methods ledger

*8 November 2026. Written by the oversight chat under `round10_ledger_brief.md`, stage L3. It consolidates the L1 rows, the L2 and L3 readings and the decisions, so that the paper can be written and the final runs briefed without a further search. The evidence for every row is on branch `round10-ledger` under `results/round10/ledger/`: the L1 rows by section (`round10_ledger_L1_S1S2.md`, `_S3.md`, `_S4.md`, `_S5.md`, `_S6.md`) with their query logs, and the readings (`round10_ledger_L2_reads_part1.md`, `round10_ledger_L2_reads_part2.md`, `round10_ledger_L3_reads.md`). Full reading notes are in the claude.ai project docs (`claude/round10_L2_notes_*.md`, `claude/round10_L3_notes_*.md`). The decisions are in `round10_ledger_decisions.md`. Result ids are those of `../../00_prep/round10_findings_survey.md`, section 2.*

## How to read it

**One block per result.** Each block gives:
- the existing method the result applies;
- its sources, with the read level reached across L1 to L3;
- the code in `code/scripts/` that implements it;
- what the final runs must redo;
- what the paper still needs before it cites the result;
- the gap verdict.

What the record validated about each result, and where, is field 6 of the result's L1 row, with its file paths, and is repeated here only where L2 or L3 changed it. Identifiers for sources named here without one are in the L1 rows (L1 S1S2, section A, and each row's sources field).

**Read levels.**
- **full**: read in full by the oversight chat or a subagent, with formulas checked against the page.
- **sections**: the named sections read in full.
- **summary**: read through a summarising fetch tool, formulas not checked.
- **abstract**: the abstract only.
- **secondary**: known through another source that was read.
- **unread**: not opened.

**Status labels** are the findings survey's (classical, in print, empirical, own and provisional). A "gap" is recorded only with the failed searches in the L1 query logs. No row here claims novelty (hard rule 5).

## 0. What the ledger settled

- **E, decided.** The two-fold cross-fitted difference estimator in Mickey's form, which is Williams' form for even $n$, with round 9's within-fold variance as the primary interval. The exactly unbiased variance and its nonnegative upper version are reported beside it, under a switch rule written before the runs (`round10_ledger_decisions.md`, section 1).
- **Recommended.** R7-6, a fixed coefficient of 1 as primary. P, keep prediction sets and drop E8. V, state regime B unbounded first. R7-7, R7-5 and O5 (same document, sections 2, 3, 4 and 6).
- **Scored.** P10.2 held (same document, section 7).
- **Gaps.** The logged searches found no gap for the methods the applied paper applies. One gap is recorded and waits on Nicolas: round 9's frontier theorems (B13) were not found in print after over 500 queries, and whether that gap is genuine is his call. The results recorded as the project's own are the measured comparisons, the frontier theorems of B13 and B14, the coverage floor of A8 and the map of A6, all provisional.
- **One reading for Nicolas to check.** The variance identity behind the exactly unbiased estimator for complementary folds is `[proposed]` (same document, section 1.2, item 3).

## S1. Motivation

**D2. Low accuracy ceiling, small encoder spread, a head without intercept.**
- Method: the HEST-Benchmark protocol (PCA to 256 components, ridge, per-gene Pearson); the mean squared error skill score decomposition for the $R^2$ ladder.
- Sources: HEST-1k, arXiv:2406.16192 (sections, 5.2 for the protocol); Murphy 1988, Monthly Weather Review 116(12), 2417 to 2424 (secondary, through the climpred documentation; publisher blocked).
- Code: `aggregate_results.py`, `build_summary_tables.py`, `round2_r1b_heads.py`, `round2_r1b_ladder.py`.
- Final runs: none, unless the head changes.
- Before citing: Murphy 1988 in the original; the HEST-Benchmark code reference for the absent intercept; the pooled $R^2$'s scope stated.
- Gap: none.

**D3. Split design costs more than encoder choice.**
- Method: grouped (blocked) cross-validation; the leakage taxonomy's non-independence type.
- Sources: Roberts et al. 2017, Ecography 40(8), doi:10.1111/ecog.02881 (abstract); Howard et al. 2021, Nature Communications, doi:10.1038/s41467-021-24698-1 (full); Kapoor and Narayanan, arXiv:2207.07048, published in Patterns 4(9), 100804 (section 2.4, where D3 is their type L3.2 and the site term fits L3.3); Dip and Zhang 2026 and Akram and Dip 2026, NeurIPS 2026 workshop posters (abstracts).
- Code: `split_decomposition.py`, `round2_split_v4.py`.
- Final runs: none.
- Before citing: Dip and Zhang's full text before quoting their numbers. Their protocol overlaps D3's closely, so D3 is presented as a measurement on three multi-slide tasks, not as a new protocol (L2 part 2, item 12).
- Gap: none.

**D9. The donor carries the variance.**
- Method: the design effect of cluster sampling (Kish), the Moulton factor, pseudoreplication.
- Sources: Kalton, Brick and Lê 2005, UN chapter VI (sections, citable secondary for Kish); Kish 1965 (unread); Moulton 1990 (abstract); Cameron and Miller 2015, JHR 50(2) (sections); Zimmerman et al. 2021, Nature Communications 12, 738, cited for pseudoreplication only, since Murphy and Skene's Matters Arising (2022) reverses its pseudobulk conclusion (L2 part 2, item 13); Squair et al. 2021, doi:10.1038/s41467-021-25960-2 (full).
- Code: `round3_b1_ppi.py`.
- Final runs: the donor-clustered against i.i.d. ratio on the corpus tasks (F2).
- Before citing: state the range with or without the merged donor set; read the slide-offset clause back from round 3's result files.
- Gap: none.

**B1. Spot-level intervals do not cover; donor cluster-robust intervals do.**
- Method: the cluster-robust sandwich with $G/(G - 1)$ and $t_{G-1}$; the ultimate-cluster variance; the percentile pairs bootstrap as comparator.
- Sources: Liang and Zeger 1986, Biometrika 73(1), 13 to 22 (sections, section 2 and Theorem 1); Cameron and Miller 2015 (sections, including VI.C on the pairs bootstrap as percentile-$t$, read in L2); Bester, Conley and Hansen, working paper of 2008 (full; the 2011 article in J. Econometrics 165(2) unread). Their Proposition 1 shows $t_{G-1}$ conservative with equal limiting design moments for $\alpha \le 0.083$, or for $\alpha \le 0.1$ when $G \le 14$ (L2 part 2, item 11). Särndal et al., Result 4.5.1 and (4.3.17) for the ultimate-cluster variance (full, chapter 4).
- Code: `round3_b1_ppi.py`, `round3_b2_semisynthetic.py`, `round3_final_report_numbers.py`.
- Final runs: none for the motivation.
- Before citing: say that Bester et al.'s conditions (equal cluster sizes, a CLT within each cluster) are not met by donors of unequal size.
- Gap: none.

**Inference with predicted outcomes, and uncertainty for predicted spatial expression (positioning).**
- Method: prediction-powered inference and its corrections for predicted outcomes; conformal intervals for imputed spatial expression.
- Sources: Angelopoulos, Bates, Fannjiang, Jordan and Zrnic, arXiv:2301.09633 (abstract); PPI++, arXiv:2311.01453 (sections); Wang, McCormick and Leek 2020, PNAS 117, doi:10.1073/pnas.2001238117, from the bioRxiv preprint 10.1101/2020.01.21.914002 (sections); TISSUE (Sun et al. 2024, Nature Methods 21, 444 to 454, doi:10.1038/s41592-024-02184-y, preprint read in full, `round10_ledger_L1_S3.md`, question P), whose calibration groups are clusters of genes and cells, predicted from single-cell references, not histology; Testa, Lei and Roeder 2026, bioRxiv (abstract).
- Code: none.
- Final runs: none.
- Before citing: the published PNAS text for Wang, McCormick and Leek.
- Gap: none. A positioning point, not a result.

**A4 (motivation). The valid prediction set costs width.** As A4 in S3.

## S2. Data

**D6. HEST's patient labels are wrong in both directions.**
- Method: a provenance audit of the grouping variable against sources outside the dataset.
- Sources: HEST-1k (sections 3.1, 8); HEST issue #133; Toker et al. 2016 (preprint, sections).
- Code: `round2_r5b_audit.py`, `round3_h1_build_audit_r3.py`, `round3_d3_build_audit.py`, `round4_data_task_lung.py`.
- Final runs: a donor audit of every corpus task before it enters (F1).
- Before citing: HEST's version and the issue by URL.
- Gap: none.

**D7. No institution axis in the benchmark subset; the corpus has one.**
- Method: leave-one-site-out evaluation.
- Sources: Howard et al. 2021 (full); Kömen et al. 2026, "Towards robust foundation models for digital pathology", Nature Communications 17, 5218 (sections, PMC13260997), which replaces the "near-100%" figure of older documents with 88% to 98% center-prediction accuracy (L2 part 2, item 13); WILDS (abstract); the corpus data card (`NicWYZ/ST-Fed-Learn`, full).
- Code: `round3_d3_build_audit.py`, `site_probe.py`, `site_shift_matched.py`.
- Final runs: task definitions and center counts from the corpus registry (F1).
- Before citing: say that the corpus's "center" is a study cluster, not a laboratory, so the axis tests study shift.
- Gap: none.

**D10. One shared technical factor dominates between-donor variation on CCRCC.**
- Method: PCA of donor means, with the leading component read as depth or detection.
- Sources: Hicks et al. 2018, Biostatistics 19(4), 562 to 578, cited by section 3.3 (the preprint's sentence is not in the published text), whose section 4 cautions against modelling technical confounders when biology is confounded with them (L2 part 2, item 13); Risso et al. 2014, doi:10.1038/nbt.2931 (full); Bhuva et al. 2024, doi:10.1186/s13059-024-03241-7 (full), on library size carrying spatial biology.
- Code: `round9_c0_diagnostics.py`.
- Final runs: the factor share on every corpus task, on both scales (F2).
- Before citing: do not call the factor purely technical (Bhuva et al.).
- Gap: none.

**D11 and D5. Library-size normalization and the scale of the estimands.**
- Method: global scaling with the shifted logarithm, set against HEST's $\log(1 + y)$ of raw counts.
- Sources: L1 S1S2 row S2.4 lists the conventions with read levels (HEST full; Ahlmann-Eltze and Huber 2023 full; Lun 2018 full; Booeshaghi et al. full; Anders and Huber 2010 full; Squair et al. 2021 full; Bhuva et al. 2024 full; Hafemeister and Satija, SpaNorm and Crowell et al. abstract; Atta et al. 2024, Genome Biology 25, 153, which gives a cell-level fix only).
- Code: `round9_c2_normalized_summaries.py`.
- Final runs: every inference cell on $\log(1 + y)$ and on the corpus's $\log(1 + 10^4 y/n)$, with the difference reported (F2; decisions section 5).
- Before citing: the scale the paper calls primary, which is decided after F2.
- Gap: none. The choice is a decision.

**D12. Little out-of-sample donor-level information for the median gene.**
- Method: leave-one-cluster-out $R^2$ against a constant.
- Sources: Campbell and Thompson 2008 (abstract); Snijders and Bosker 1994 (abstract).
- Code: `round9_between_head.py`, `round9_depth_probe_diagnostics.py`.
- Final runs: the same on the corpus tasks (F1, after the prediction files exist).
- Before citing: state the baseline. The record's $R^2$ is relative to the full-sample mean, and the leave-one-out constant is the convention to report.
- Gap: none.

**D13. INT5, a technical-outlier donor invisible to histology.**
- Method: cluster-level outlier diagnostics; the representative outlier; the max-share $\kappa(e)$.
- Sources: Chambers 1986, JASA issue 396 (abstract confirms the definition, L2 part 2, item 13); Christensen, Pearson and Johnson 1992 (abstract).
- Code: `round9_stud_feasibility.py` (its diagnostics file has no committed writer, so the final runs regenerate it from committed code), `round9_fewcluster_hest_kappa.py`.
- Final runs: INT5's raw library size and detection rate, and the atypical-donor diagnostics on the corpus kidney task (F1).
- Before citing: Chambers in full if the paper uses his term.
- Gap: none.

**D14. Encoders agree with each other more than with the labels; Xenium pseudo-spots.**
- Method: within-slide correlations; Moran's I.
- Sources: HEST section 3.2 for pseudo-Visium spots (sections); Moran 1950 (unread, publisher blocked).
- Code: `round9_newtopic_n3_diagnostics.py`.
- Final runs: none.
- Before citing: Moran 1950 or a textbook definition.
- Gap: none.

**ACS PUMS 2018.**
- Method: the folktables ACSIncome filter, a cross-fitted gradient boosting predictor, states as clusters.
- Sources: folktables, arXiv:2108.04884 (abstract).
- Code: `round4_ppi_acs_pums2018_fetch.py`, `round4_ppi_acs_pums2018_analyze.py`.
- Final runs: the same task, with the estimator of E (F2).
- Before citing: the paper must say the finite population is the ACS sample itself, since survey weights are not used; cite the Census PUMS documentation with versions.
- Gap: none.

## S3. Prediction sets for a new donor (kept if Nicolas accepts P)

**A1. Spot-level split conformal under-covers for a new donor.**
- Method: split conformal; coverage loss under non-exchangeability.
- Sources: Lei et al. 2018, JASA 113(523), 1094 to 1111 (the record read the full text; the venue confirmed from two reference lists, L2 part 2, item 9); Barber, Candès, Ramdas and Tibshirani, arXiv:2202.13415, Theorem 2 with unit weights (sections). Its gap term has no computable value and does not shrink with more spots per donor.
- Code: `round3_a0_harness.py`, `round3_a1_tables.py`.
- Final runs: none unless the head changes; the institution-axis analogue on the corpus (F3).
- Before citing: Barber et al.'s venue (`[verify]`).
- Gap: none.

**A2. The calibration unit, not its size, decides coverage.**
- Method: hierarchical exchangeability.
- Sources: Lee, Barber and Willett, arXiv:2306.06342 v4, ACM JDS, DOI 10.1145/3786352 (sections, including Remark 1 and appendix C; footnote 4 to be added); Dunn, Wasserman and Ramdas, JASA 2023 (sections in the record).
- Code: `round3_a0_harness.py`, `round3_a2_mechanisms.py`, `round3_a3_report_numbers.py`.
- Final runs: none.
- Before citing: Lee, Barber and Willett's numbering in the published version.
- Gap: none.

**A3. Feature reweighting cannot repair donor shift.**
- Method: weighted conformal under covariate shift; Kish's effective sample size.
- Sources: Tibshirani, Barber, Candès and Ramdas, arXiv:1904.06019 (sections). Corollary 1 needs a known likelihood ratio; estimated, clipped weights appear only in an example, so A3's wording is sharpened to that (L2 part 2, item 9). Bhattacharyya and Barber (abstract).
- Code: `round3_a3_weighted.py`.
- Final runs: none.
- Before citing: a source for the effective sample size (Tibshirani et al. section 2.3, or Kish).
- Gap: none.

**A4. HCP is valid once $K + 1 \ge 1/\alpha$.**
- Method: hierarchical conformal prediction.
- Sources: Lee, Barber and Willett (sections; Theorem 1 with the upper bound $1 - \alpha + 2/(K_1 + 1)$, so the paper describes over-coverage as finite-$K$ slack, not conservativeness).
- Code: `round3_a4b_hcp.py`, `round4_conf_sim.py`, `round4_conf_c3.py`, `round4_conf_c1_codepath.py`.
- Final runs: HCP rows on the final prediction files and the corpus tasks (F3).
- Before citing: none beyond A2's.
- Gap: none.

**A5. Adaptive scores buy little except in the upper tail.**
- Method: CQR; the locally weighted score; a conformalized negative binomial head.
- Sources: Romano, Patterson and Candès, arXiv:1905.03222 (abstract); Lei et al. section 5.2 (unread).
- Code: `round3_a4_scores.py`.
- Final runs: full gene scope, with a valid width comparison, not the matched-coverage diagnostic (F3).
- Before citing: CQR and Lei et al. section 5.2 read.
- Gap: none.

**A6. The map over calibration donors $K$ and labelled target spots $o$.**
- Method: HCP; GHCP; split conformal and full conformal inside the target donor.
- Sources:
  - GHCP, arXiv:2608.15500 v1 (full through appendices D.5 and E.1). It needs reference groups larger than $o$, uninformative group size (A2) and i.i.d. units within a group (A3). Its within-group comparator is a split, and it has no full conformal comparison.
  - `within_full`, which is the classical full conformal interval with the mean as the fitted model. The guarantee is Lei et al. 2018, Theorem 2.1, with exchangeability sufficing (Tibshirani et al. 2019, Theorem 1). The explicit interval is Bersson and Hoff's Lemma 3 at $1/\tau^2 = 0$, arithmetic on their lemma (L2 part 2, item 6).
  - Methods already using the target group's labels: Lee, Barber and Willett's Remark 1, SymmPI's two-layer method (Dobriban and Yu, JRSS B 87(5)), Bersson and Hoff's FAB conformal (sections).
- Code: `round4_conf_c3.py`, `round4_conf_sim.py`, `round5_conf_w3.py`, `round5_conf_w5_map.py`, `round5_conf_w5_numbers.py`.
- Final runs: the map on the final prediction files, with standard errors on the width margins (F3, P10.3).
- Before citing: Shafer and Vovk 2008 if the computational form is credited.
- Gap: none for the methods. The map is a measured comparison, own and provisional, and is not claimed as the first use of the target donor's labels.

**A7. GHCP's released code reproduces its paper; its pool rule differs by one group.**
- Method: reproduction against the paper's tables and eq. (8).
- Sources: GHCP v1. Eq. (8) is as L1 wrote it, and section 3.1.1 says $o \le 20$.
- Code: `round4_conf_c1_ghcp_repro.py`, `round4_conf_c1_ghcp_compare.py`, `round4_conf_c1_codepath.py`.
- Final runs: none.
- Before citing: telling the authors is a contact outside the project (hard rule 7).
- Gap: not applicable.

**A8. Below $K + 1 < 1/\alpha$ valid sets have infinite expected width; the coverage floor.**
- Method: universality and impossibility for conformal prediction.
- Sources: Tibshirani, Barber and Ramdas, arXiv:2608.27310 v2, Theorems 3 and 7 (sections; round 5's transcription matches, and Theorem 7 holds for any $\sigma$-finite measure); Duchi, Gupta, Jiang and Sur, Statistical Science 40(3), Proposition 7.24 and Corollary 7.25 (sections).
- Code: `round4_conf_c2_lower_bound.py`, `round5_conf_w4_hcp_pointwise.py`.
- Final runs: none.
- Before citing: a fresh check of round 4's proofs, and a search on the survey-sampling side before the floor is called the project's own (hard rule 5).
- Gap: the first half is in print. The floor is own and provisional.

**A9. Studentizing by a donor's own few spots buys little.**
- Method: studentized scores built the same way in every group.
- Sources: GHCP appendix B.1 (full); Duchi et al. section 5, Theorem 5.9 (sections), which needs the same number of random labelled points in every calibration environment.
- Code: `round9_stud_feasibility.py`.
- Final runs: rerun to the final-runs standard on the final prediction files (F3).
- Before citing: none.
- Gap: none.

**A10. INT5 breaks HCP; the cross-gene studentized set covers it.**
- Method: per-donor diagnosis of a failure of hierarchical exchangeability.
- Sources: as A9; Barber et al. 2023, Theorem 6, as a start for a search on an outlying group (not run).
- Code: `round9_stud_feasibility.py`.
- Final runs: regenerate the per-donor diagnostics from committed code (F3).
- Before citing: the correction (0.878 is INT10's value) carried into the text. A search on conformal prediction with a contaminated group if INT5 is presented as more than a diagnostic.
- Gap: not assessed.

**Institution axis on the corpus.**
- Method: HCP with centers as groups; leave-one-center-out evaluation.
- Sources:
  - Lee, Barber and Willett, and Duchi et al. Neither states a construction with more than two levels, so a three-level construction is recorded as not found, not as a gap (L2 part 2, item 8).
  - Federated conformal (Lu, Yu, Karimireddy, Jordan and Raskar, arXiv:2305.17564) covers a known mixture of existing clients, not a new one (L2 part 2, item 9).
  - Duchi et al.'s $(\alpha, \delta)$-coverage needs $\delta$ of order $1/(K + 1)$.
- Code: none in this repository. The corpus's leave-one-center-out code is in `NicWYZ/ST-Fed-Learn` and scores point predictions only.
- Final runs: HCP over centers at the $\alpha$ each task's center count allows, and donor-level HCP pooled across centers as the comparator (F3).
- Before citing: confirmed center and donor counts from the registry.
- Gap: not established.

## S4. Valid inference with predicted expression

**B2. PPI is the difference estimator and PPI++ the GREG estimator.**
- Method: the difference estimator with a fixed predictor (Cassel, Särndal and Wretman 1976); the model-assisted estimator under two-stage sampling.
- Sources:
  - Breidt and Opsomer 2017, Statistical Science 32(2), eq. (4), (5) and the unbiased variance estimator on p. 192 (full, L3).
  - Särndal, Swensson and Wretman 1992, Result 6.3.1 (pp. 222 to 223) for the difference estimator, and Results 4.2.1 and 4.3.1 for one- and two-stage cluster sampling (full, chapters 4, 6 and 8).
  - Cochran 1977, Theorem 7.1, eq. (7.8), Theorems 10.1 and 10.2, and (11.22) and (11.24) (full, chapters 7, 9 to 11).
  - Mozer, arXiv:2603.19160 (abstract).
  - Cassel et al. 1976, Biometrika 63, 615 to 620 (secondary, through Särndal et al. and Breidt and Opsomer).
- Code: `round4_ppi_estimator.py` (`estimate`, `estimate_textbook`), `round5_ppi_estimator.py` (`design_whole_clusters`).
- Final runs: the estimator of E and the fixed coefficient (F2).
- Before citing: neither textbook prints the two-stage difference estimator with an auxiliary as one formula, so the paper states the combination and cites both pieces (L2 part 1, item 6).
- Gap: none.

**B3. PPI under donor clustering is valid with a modest gain.**
- Method: as B2, with the cluster-robust variance for the superpopulation comparison.
- Sources: as B2 and B1.
- Code: `round3_b1_ppi.py`, `round4_ppi_estimator.py`.
- Final runs: superseded by F2's design-target numbers.
- Before citing: quote round 3's ratios only as a superpopulation comparison.
- Gap: none.

**B4. The gain follows cluster-level accuracy; the limit $1 - R^2_{\text{cluster}}$.**
- Method: the variance of the regression or difference estimator on cluster values; the covariate formula of cluster-randomised trials.
- Sources: Cochran 1977, chapter 7 (full); Raudenbush 1997, Psychological Methods 2(2), 173 to 185 (sections, read by round 8 from an open copy; `round10_ledger_L1_S5.md`, S5.6); Hagesæther and Zhang 2009 (full in round 8); Broska and Howes, arXiv:2610.09601 (sections and appendices in full in L2).
- Code: `round4_ppi_q4_merge.py`.
- Final runs: the gene-axis correlation on the final runs' cells (F2).
- Before citing: none.
- Gap: none.

**B5, B9, B10 and B11. The estimator and its variance (question E).**
- Method: the exactly unbiased split-sample regression estimator (Mickey 1959; Williams 1961) in the two-fold form of the decision, with round 9's within-fold variance. The exactly unbiased estimator $\hat V$ and $\max(\hat V, \hat V_w)$ are reported beside it, and the finite-population factor applies.
- Sources:
  - Mickey 1959, JASA 54(287), 594 to 612, sections 2 and 4 (full), with his 1960 corrigendum, JASA 55(292), p. 755 (full). The corrigendum withdraws the claim on p. 595 that the variable-probability part gives new estimators and credits section 6's results to Des Raj and Murthy, and it leaves sections 2 to 5 unchanged.
  - Williams 1961, Biometrics 17(2), 267 to 274 (full). His variance (13) needs $n/N$ negligible.
  - Sanguiao Sande and Zhang, arXiv:2003.11423 (full; Sankhya A 83, 2021, unread).
  - Zhang, Sanguiao-Sande and Lee 2025, JOS 41(1), 404 to 432 (full, L3).
  - Lu, Shi, Liu and Ding, arXiv:2508.15664, and An, Dagdoug, Haziza and Tillé, arXiv:2609.10904 (sections).
  - Kwon, Yang and Kim, arXiv:2604.07636 (sections).
  - Mani, Xu, Lipton and Oberst, ICML 2026 (sections), for the cost of same-sample tuning.
- Code:
  - Williams' and the fold-wise forms exist only in `round9_fewcluster_williams.py`.
  - Round 5's estimator is `round4_ppi_estimator.lambda_rule('c_crossfit_design')` with `round5_ppi_estimator.design_whole_clusters(lin=True, xf=True)`.
  - The new estimator module is the final runs' first code task (F1).
- Final runs: every regime-A interval with the decided form, the fixed coefficient and the classical control. Round 9's comparison is rerun with the `lin` term in the `R5` arm, to settle whether the intervals of rounds 5 to 7 carried the level-dependent variance (L1 S4, section 0, a code reading that says they did not).
- Before citing: Nicolas's look at the identity (`[proposed]`), and the published Sanguiao Sande and Zhang for numbering.
- Gap: none.

**B6. The level term; spot-weighted estimands; form C and the constant control.**
- Method: the regression estimator's intercept. Form C is the **combined** regression estimator with cluster means (Cochran 7.50, p. 202; Shao and Wang's $\hat Y_{CS}$), not the separate one (L2 part 1, item 7). The ratio-to-size mechanism under unequal cluster sizes. Estimand choice under informative cluster size.
- Sources: Cochran sections 7.9 to 7.11 and 9A.1 (full); Shao and Wang 2014, Statistica Sinica 24, 395 to 414, DOI 10.5705/ss.2012.064 (full); Seaman, Pavlou and Copas 2014 (sections); Song, Kluger, Parikh and Gu, arXiv:2601.20819 (sections), for reporting beside a reference analysis.
- Code: `round5_ppi_twolevel.py`, `round5_ppi_e2_regimeB.py`, `round5_ppi_e2_levelcheck.py`, `round5_ppi_e3_twolevel.py`.
- Final runs: form C in regime B with the fixed coefficient and the cross-fitted one, the constant and permuted controls, on both scales (F2).
- Before citing: none.
- Gap: none.

**B7. What predictions buy on each task.**
- Method: as B2, B4 and B6.
- Code: `round5_ppi_e5_joint.py`, `round4_ppi_q4a_merge.py`.
- Final runs: all of it, on the four tasks and the corpus tasks, both regimes and both scales (F2).
- Gap: none.

**B8. Under-coverage with few donors, from skewed donor contributions.**
- Method: the finite-population $t$ interval and its normal approximation's dependence on skewness; Johnson's (1978) modified $t$ as a diagnostic.
- Sources: Cochran section 2.15 (full; rule (2.69), $n > 25G_1^2$, and the advice to enumerate extreme units completely); Hájek's condition via Li and Ding 2017 (summary); Bloznelis 1999 (full, L3; unspecified constant); Johnson 1978 (unread, paywalled).
- Code: `round5_ppi_estimator.py` (`johnson_interval`), `round5_ppi_e1_diag.py`.
- Final runs: the coverage grid against each gene's skewness and largest share (F2).
- Before citing: Johnson 1978 if the modified $t$ is named.
- Gap: none.

**B12. Published few-cluster comparators under-cover at four clusters; `bh_t`.**
- Method: Broska and Howes's interval; Kluger et al.'s cluster bootstrap; CR1 and Bell and McCaffrey's corrections.
- Sources:
  - Broska and Howes, arXiv:2610.09601 v1 (full for sections 1 to 4 and appendices A, C, D and E). One coefficient, no cluster intercept, normal quantile, no finite-population factor, and section 4 says the variance estimator has no small-sample correction.
  - Kluger, Lu, Zrnic, Wang and Bates, arXiv:2501.18577 v3 (sections, including appendix B.1).
  - Bell and McCaffrey 2002 (full); Cameron and Miller 2015 (sections); Imbens and Kolesár 2016 (sections).
- Code: `round7_ppi_s2_comparators.py` (`bh3`, `bh_variants`, `kluger_draw`), `round7_ppi_weighting.py`.
- Final runs: `bh`, `bh_t`, `bh_t_fpc` and Kluger et al. beside the decided estimator, matched by cell (F2).
- Before citing: none.
- Gap: none. The correction is classical and Broska and Howes's section 4 is the citation for its absence from their paper.

## S5. How many donors, and which

**B11 and the coverage shortfall.** As S4 above. The final runs report it on the corpus kidney task at about 50 donors as well.

**B13. The frontier (Theorems 1 to 3) and the required number of clusters.**
- Method: the nonexistence of bounded valid procedures over unrestricted classes, applied to a finite population under a max-share restriction.
- Sources:
  - Bahadur and Savage 1956 (full in L2). Corollary 3, p. 1117, is the citation.
  - Gleser and Hwang 1987 (full).
  - Dufour 1997, Econometrica 65(6) (summary; the original is to be read before it is credited).
  - Hendriks, IJzerman-Boon and Klaassen 2006 (summary); Lanke 1974 (full in round 9).
  - Pötscher and Preinerstorfer (summary).
  - Neither classical paper contains round 9's finite-population lemma or Theorems 1 to 3. Round 9's "total variation $n/G$" is an analogy (L2 part 1, item 4).
- Code: `round9_fewcluster_frontier.py`, `round9_fewcluster_feasibility.py`, `round9_fewcluster_tuned.py`, `round9_fewcluster_exact_tuned.py`, `round9_fewcluster_hest_kappa.py`, `round9_fewcluster_strat_frontier.py`.
- Final runs: re-cite the frontier per task, the corpus kidney task included, against each gene's residual max-share (F2).
- Before citing: which theorems the paper keeps (not this track's decision); Dufour 1997 in the original; the nine paywalled sources of round 9's NOV12 list for B14.
- Gap: recorded by round 9 as not found after over 500 queries, and unchanged by L1's eight queries. Own and provisional (O5).

**B14. Certified critical values below the frontier.**
- Method: moment-duality bounds on a quadratic in a self-normalised sum.
- Sources: Pinelis, arXiv:1011.6065 (summary); Jonsson 2011, Bernoulli 17(1) (summary).
- Code: under `results/round9/fewcluster/crit/`, not `code/scripts/`.
- Final runs: none.
- Before citing: the code moved into `code/scripts/` if values are reported.
- Gap: a sharp computable critical value is open. The record has no usable positive interval at the real sizes.

**E1. Regime A against regime B, with costs.**
- Method: cluster against stratified sampling under a linear cost, with residual variances when a predictor is used.
- Sources: Cochran Theorems 10.1 and 10.2 with $f_2 = 1$ (regime A) and $f_1 = 1$ (regime B) (full); Särndal et al. Results 4.2.1 and 4.3.1 (full); Broska and Howes (full) for the superpopulation version.
- Code: `round5_ppi_e3_twolevel.py`, `round5_ppi_twolevel.py`, `round5_ppi_e3_merge.py`, `round9_fewcluster_box.py`, `round9_fewcluster_regimeB_acs.py`, `round9_fewcluster_strat_frontier.py`.
- Final runs: both regimes cost-matched with the decided estimator and the fixed coefficient, and the required units per cluster for regime B under round 9's box class (`code/scripts/round9_fewcluster_box.py`, `docs/round09/i03/fewcluster/round09_fewcluster_stratified.md`) at each population's own observed $(\Lambda_0, v_0)$, the bounded column, and at the same $\Lambda_0$ with $v_0 = 1$, the unbounded column, together with the design simulation's coverage of the regime B interval at each of those $m$, reporting each task's largest share and $G^\ast$ (F3; decisions, section 4).
- Before citing: V stated as decisions section 4 proposes; Q1 (whether regime B can be bought on a spatial platform) deferred to the next advisor deck.
- Gap: none for the comparison. The few-cluster regime-B numbers are own, provisional and conditional on V.

**E2. The optimal number of units per cluster with a predictor.**
- Method: the optimal subsample size under a two-stage cost with covariate-adjusted components.
- Sources: Snijders 2001, eqs. (12) and (13) (summary); Raudenbush 1997, Table 3 (sections, read by round 8; reproduced to within one unit there); Cochran section 10.6 (full, chapter 10).
- Code: `round5_ppi_e5_allocation.py`.
- Final runs: recompute from the final runs' components (F3).
- Before citing: Moerbeek 2006 if cited.
- Gap: none.

**E3. Rejective selection and `rej_t`.**
- Method: rejective sampling on the Mahalanobis distance; Yang, Qu and Li's Corollary A5 at the cluster level; the regression estimator after rejection.
- Sources: Yang, Qu and Li, arXiv:2109.09930 v1, the only arXiv version (sections in round 8; JASA 118(542) unread, `round10_ledger_L1_S5.md`, row S5.7); Morgan and Rubin 2012, Annals of Statistics 40(2), DOI 10.1214/12-AOS1008 (summary); Fuller 2009, Biometrika 96(4) (full in L2; asymptotic, and advises stratifying first); Lu, Liu, Liu and Ding, arXiv:2207.02540 (summary).
- Code: `round5_ppi_balance.py`, `round5_ppi_e4b_rejective.py`, `round7_ppi_d2.py`.
- Final runs: rerun matched against simple random selection under the decided estimator (F3).
- Before citing: the JASA statement of Corollary A5.
- Gap: none.

**E4. Weighting with simulated inclusion probabilities fails under rejection.**
- Method: Horvitz-Thompson and Hájek with Monte Carlo inclusion probabilities; non-measurable designs.
- Sources: Fattorini 2006, Biometrika 93(2), 269 to 278 (abstract); Aronow and Samii 2013 (summary); Legg and Yu 2010 (summary); Fuller 2009, eq. (16).
- Code: `round7_ppi_weighting.py`.
- Final runs: not rerun. The paper reports round 7's diagnosis as a limit.
- Before citing: Fattorini in full if his replication guidance is cited.
- Gap: none.

**E5. The cluster-level cube design.**
- Method: balanced sampling by the cube method with simulated pair probabilities.
- Sources: Deville and Tillé 2004 (abstract); Chauvet 2011, JOS 27(4) (summary); Breidt and Chauvet 2011, JSPI 141(1), DOI 10.1016/j.jspi.2010.06.022 (unread, paywalled).
- Code: `round7_ppi_s3_cube.py`, `round7_ppi_s4b_cube3.py`.
- Final runs: rerun matched, with the achieved balance reported (F3).
- Before citing: Breidt and Chauvet, and Deville and Tillé, in full.
- Gap: none.

**E6. Greedy k-center selection has no design-based variance.**
- Method: purposive selection (Neyman 1934); the core-set rule.
- Sources: Neyman 1934 (summary of a scan); Sener and Savarese 2018 (summary).
- Code: `round7_ppi_s4_kcenter.py`.
- Final runs: not rerun. Re-derive the reported range from `s4_grid.csv` with the encoder subset named.
- Before citing: Neyman's DOI.
- Gap: none.

**E7. A probe of a few spots per donor, then a take-all stratum.**
- Method: two-phase sampling for stratification with a take-all stratum.
- Sources: Hidiroglou 2001 (full in round 9); Hidiroglou and Lavallée 1988 (abstract); Beaumont, Haziza and Ruiz-Gazen 2013 (summary); Rao 1973 (metadata); Cochran chapter 12 (unread); Hidiroglou 1986 (unread).
- Code: `round9_probe_feasibility.py`, `round9_probe_takeall.py`, `round9_fewcluster_takeall_kappa.py`.
- Final runs: the probe and take-all design with the decided estimator. The two-phase variance for a stratum chosen in phase one is used, or the paper states that the variance conditions on the first phase (F3).
- Before citing: Rao 1973 and Särndal et al. section 9.4 (Result 9.4.1, p. 351, read in L2) for the two-phase variance.
- Gap: none.

**E8. The joint design.** Recommended dropped to a sentence in the discussion (decisions section 3). Searches found nothing that splits one budget between PPI and prediction sets (L1 S5.12).

**V. A bound on one cluster's share of the design variance.** No finite-sample bound found. The asymptotic conditions, the Bloznelis bound, the $G^\ast$ diagnostic and the take-all practice are in decisions section 4, with the sources and read levels of L1 S5 section 3.5, L2 and L3.

## S6. Limits and cautions

**S6-1. Same-cluster tuning of the coefficient.**
- Method: single-sample against cross-fit PPI++.
- Sources: Mani et al., ICML 2026 (sections); PPI++, arXiv:2311.01453, which fits the coefficient on the same labelled data with an asymptotic justification (sections, L2 part 2, item 5); Eyre and Madras, ICML 2025 (sections); Song et al. 2026 (sections).
- Code: `round4_ppi_estimator.py` (`lambda_rule`), `round4_ppi_q1_sim.py`.
- Final runs: rules (a) to (c) rerun under the decided estimator (F2).
- Before citing: the cluster-level statement is the analogue with clusters as units, supported by simulation.
- Gap: none.

**S6-2. Cluster bootstraps at few clusters.**
- Method: the pairs cluster bootstrap with percentile, BCa and bootstrap-$t$; the wild cluster bootstrap.
- Sources: Cameron, Gelbach and Miller 2008, REStat 90(3), 414 to 427 (NBER version in sections); MacKinnon, Nielsen and Webb 2023 (sections); Cameron and Miller 2015, section VI.C (sections); Hesterberg 2015 (sections); Mashreghi, Haziza and Léger 2016, Statistics Surveys 10 (full, L3).
- Code: `round4_ppi_estimator.py` (`bootstrap`, `bootstrap_textbook`), `round4_ppi_q1b_sim.py`.
- Final runs: the pairs percentile bootstrap, the wild cluster bootstrap-$t$ with Webb's six-point weights, and a design-based bootstrap-$t$ that reproduces the finite-population factor (Rao and Wu's rescaling), beside the decided estimator (F2). For the design target a with-replacement bootstrap's variance is $\frac{n - 1}{n(1 - f)}$ times the unbiased one. That is below 1 at 4 labelled clusters on the tasks with more than 16 clusters and above 1 from 8, so the design-based version would widen it at 4 and narrow it from 8 (L3 reads, section 1.4, a `[proposed]` reading).
- Before citing: the published REStat text for page numbers.
- Gap: none.

**S6-3. The finite-population factor for the design target.**
- Method: the factor $1 - n/G$; conventional cluster errors are conservative when a large share of clusters is sampled.
- Sources: Cochran chapter 2 (full); Abadie, Athey, Imbens and Wooldridge, arXiv:1710.02926 (sections; QJE volume and pages `[verify]`).
- Code: `round4_ppi_estimator.py` (`fpc_factor`).
- Final runs: with and without the factor on the design target (F2).
- Before citing: the QJE citation.
- Gap: none.

**S6-4. The level term and comparators without an intercept.** As B6.

**S6-5. Spot-weighted estimands and the permuted predictor.**
- Method: the ratio-to-size mechanism; estimand choice under informative cluster size.
- Sources: Cochran section 9A.1 and 11.8, eqs. (9A.2), (9A.4) (full); Seaman, Pavlou and Copas 2014 (sections).
- Code: `round4_ppi_q2_masking.py`.
- Final runs: only if spot-weighted rows stay in the paper.
- Before citing: none.
- Gap: none.

**S6-6. Superpopulation against design-target intervals at moderate $G$.**
- Method: the two-phase (model then design) framework.
- Sources: Rubin-Bleuer and Schiopu Kratina 2005, Annals of Statistics 33(6), 2789 to 2810 (sections in L2). Their Theorem 6.1 gives the superpopulation variance as $J^{-1}[\Gamma_d + f\Gamma_m]J^{-1}$, so the model term is not small when $n_L/G$ is not small (L2 part 2, item 10). Abadie et al. 2020 and 2023.
- Code: `round5_ppi_e3_sim.py`, `round5_ppi_e5_superpop.py`.
- Final runs: the superpopulation interval with the model term, as a stated limit (F2).
- Before citing: none.
- Gap: none.

**S6-7 and S6-8. Broska and Howes's interval and Kluger et al.'s bootstrap.** As B12.

**S6-9. Reporting negative results.**
- Sources: Song et al. 2026 (sections); Morris, White and Crowther 2019 (sections), which ask for coverage with its Monte Carlo standard error and the share of failed analyses reported; Boulesteix et al. 2013 and 2015 (full).
- Final runs: every coverage with its Monte Carlo standard error, and the share of draws that formed no interval (F2, F3).

## Sources the paper relies on most, with read levels

| Source | Identifier | Read level | Rows |
|---|---|---|---|
| Cochran 1977 | *Sampling Techniques*, 3rd ed., Wiley | full for sections 2.5 to 2.8, 2.15, 4.11, chapters 5, 7, 9, 9A, 10, 11 | B2, B4, B6, B8, E1, E2 |
| Särndal, Swensson and Wretman 1992 | *Model Assisted Survey Sampling*, Springer | full for chapters 4 and 6 and for chapter 8 except book pp. 318 to 321, missing from the copy; sections of 7 and 9 | B2, B6, E1, E7 |
| Mickey 1959, with the 1960 corrigendum | JASA 54(287), 594 to 612; JASA 55(292), 755 | full | E |
| Williams 1961 | Biometrics 17(2), 267 to 274, DOI 10.2307/2527992 | full | E |
| Zhang, Sanguiao-Sande and Lee 2025 | JOS 41(1), 404 to 432, DOI 10.1177/0282423X241277719 | full | E |
| Breidt and Opsomer 2017 | Statistical Science 32(2), 190 to 205, DOI 10.1214/16-STS589 | full | B2, R7-6 |
| Sanguiao Sande and Zhang | arXiv:2003.11423 v1 (Sankhya A 83, 2021, unread) | full | E |
| Lu, Shi, Liu and Ding; An, Dagdoug, Haziza and Tillé | arXiv:2508.15664; arXiv:2609.10904 | sections | E |
| Bickel and Freedman 1984 | Annals of Statistics 12(2), 470 to 482 | full | V |
| Bloznelis 1999 | Annals of Probability 27(4), 2089 to 2108 | full | V, B8 |
| Mashreghi, Haziza and Léger 2016 | Statistics Surveys 10, 1 to 52, DOI 10.1214/16-SS113 | full | S6-2 |
| Bahadur and Savage 1956; Gleser and Hwang 1987 | Ann. Math. Statist. pp. 1115 to 1122; Ann. Statist. | full | B13 |
| Fuller 2009 | Biometrika 96(4), 933 to 944 | full | E3 |
| Broska and Howes 2026 | arXiv:2610.09601 v1 | full for sections 1 to 4 and appendices | B4, B12 |
| Kluger et al. | arXiv:2501.18577 v3 | sections | B12 |
| Lee, Barber and Willett | arXiv:2306.06342 v4; ACM JDS, DOI 10.1145/3786352 | sections | A2, A4, A6 |
| GHCP (Mallick et al.) | arXiv:2608.15500 v1 | full through E.1 | A6, A7, A9 |
| Lei et al. 2018 | JASA 113(523), 1094 to 1111 | full in the record | A1, A6 |
| Tibshirani, Barber and Ramdas | arXiv:2608.27310 v2 | sections | A8 |
| Duchi, Gupta, Jiang and Sur | Statistical Science 40(3), 392 to 416 | sections | A8, A9 |
| Cameron and Miller 2015 | JHR 50(2), 317 to 372 | sections | B1, S6-2, V |
| Bester, Conley and Hansen | working paper 2008 (J. Econometrics 165(2) unread) | full | B1 |
| Mani, Xu, Lipton and Oberst | ICML 2026, PMLR 306 | sections | S6-1, R7-6 |
