# Round 9, track fewcluster, the brief

*Written on 26 October 2026 by the claude-science session, which hands this track to an independent session and takes no further part in it. It is a starting point, not an instruction. The session working on branch `claude-science-fewcluster` plans its own work.*

## 1. The direction

Nicolas chose this direction on 26 October (option B of `docs/round09/00_prep/round09_direction_scan.md`, section 4). The problem is valid inference when only a few clusters are labelled (4 to 16 of 14 to 50) and the clusters' contributions are skewed, with machine-learning predictions free for every unit of every cluster. The aim is a methodological result with a formal guarantee that survives the literature check. It could be a procedure whose coverage is guaranteed in finite samples, or bounded explicitly, under a condition a user can check or defend, or a sharp impossibility or minimax result that says what no procedure can do at these sizes, together with what the predictions or the design can and cannot buy. It is tested on the project's tasks.

## 2. Why this direction

Several independent novelty checkers named it the only remainder of the round 9 scan with technical substance (`round09_direction_scan.md`, section 2; the SIGN, PROXY and SENS entries of `results/round9/scan/scan_structured_results.json`). They also warned that it may be impossible without assumptions that bound the population (a Bahadur-Savage type limit), which would be classical. Every interval the project has run at these sizes under-covers. In round 9's probe runs the median coverage of every regression interval was 0.739 to 0.892 at nominal 0.90 (`results/round9/probe/probe_medians.csv`), and in round 7's skewed simulation every design-based interval under-covered with an accurate variance, so the shortfall is the reference distribution and not the variance (`docs/round07/oversight/round07_ppi_results_explained.md`, Part B).

## 3. What is already known

Treat these as prior art, cite them and do not re-derive them as results. The verdicts and logs are in `results/round9/scan/`, and the round 8 note covers the survey-sampling side.

- The setting is two-stage survey sampling, and PPI with a fixed coefficient is the difference estimator (Mozer, arXiv:2603.19160). The regression estimator on cluster values, its design variance and the finite-population factor are Cochran's. The exactly unbiased split-sample regression estimator is Williams (1961), with the design-based cross-fitting papers of 2025 and 2026 (round 8 note, section 3.2).
- Small-sample corrections. The $t$ reference with $n - 1$ degrees of freedom, CR2 and Bell and McCaffrey (2002), Satterthwaite degrees of freedom, and Imbens and Kolesár (2016). Cornish-Fisher refinements of cluster-robust inference with about ten clusters (Gafarov and Ura, arXiv:2603.24786).
- Randomization and resampling with few clusters. Sign-change tests under approximate symmetry (Canay, Romano and Shaikh 2017), the wild bootstrap with few large clusters (Canay, Santos and Shaikh 2021), Ibragimov and Müller (2010, 2016), and Hagemann's permutation tests. Pseudo-population bootstraps with design replay (Booth, Butler and Hall 1994; Wang, Peng and Kim 2022; Cohen and Fogarty 2022 for rejective designs).
- Balanced and rejective selection of clusters and its interval (Yang, Qu and Li, JASA 2023, appendix A5).
- Cluster-robust PPI (Broska and Howes, arXiv:2610.09601), which names a small-sample correction and the wild cluster bootstrap as future work.
- Classical skewness corrections (Johnson's modified $t$, Hall's transformation, Edgeworth expansions under sampling without replacement), Cochran's rule for sample size under skewness, and finite-population Berry-Esseen bounds. These were cited from memory by the checkers and need checking `[verify]`.

## 4. What the data show

From round 9's preparation, all on the HEST-1k tasks with uni_v2 predictions unless stated.

- Donor means are skewed on Visium. Median skewness over genes is 2.053 on CCRCC, 1.215 on INDIANA_KIDNEY and 0.169 on LUNG_XENIUM (`results/round9/diagnostics/c0_task_medians.csv`).
- One shared factor, close to sequencing depth, carries 0.650 of between-donor variance on CCRCC, 0.313 on INDIANA_KIDNEY and 0.343 on LUNG_XENIUM (`results/round9/diagnostics/c0_shared_donor_factor.csv`). Library-size normalization reduces it on CCRCC to 0.338 and leaves the donor means skewed (`results/round9/norm/norm_summary.csv`).
- The skew on CCRCC comes mostly from one donor, INT5, the donor with the largest average expression (z = 3.98). Histology does not flag it, since its prediction outlyingness ranks 15th of 24 and its embedding outlyingness 22nd (`results/round9/stud/atypical_donor_diagnostics.csv`). Hierarchical conformal prediction covers it at 0.310 (`results/round9/stud/stud_per_donor_coverage.csv`).
- Labelling that donor with certainty, found by a probe of three spots per donor, lifts CCRCC coverage from 0.825 to 0.885 at 8 labelled donors (`results/round9/probe/takeall_medians.csv`). The design is classical two-phase stratification (`docs/round09/00_prep/round09_probe_novelty.md`).
- Out of sample, the predictions explain none of the between-donor variance for the median gene on Visium. Several lung genes reach a leave-one-donor-out R^2 near 0.9 (`results/round9/between/between_head_medians.csv`, `results/round9/between/between_head_by_gene.csv`).

So the few-cluster problem in this application is driven by rare atypical clusters, and these are technical outliers that the free predictions cannot see. A useful result may need to say what a user can check, or must assume, about such clusters.

## 5. Resources

- **Data.** HEST-1k is gated and stays on Longleaf under `/work/users/w/e/weiyang/hest_replication` (`MANIFEST.md`). The per-spot prediction files are `results/round3/B1_ppi/b1_predictions__<TASK>__<encoder>.parquet` for CCRCC and the other benchmark tasks, `results/round4/ppi/Q2_theory/predictions/` for LUNG_XENIUM and the two ACS tasks, and `results/round4/ppi/Q2_theory/predictions_INDIANA_KIDNEY/` for INDIANA_KIDNEY. Their columns are `y__<gene>`, `f__<gene>`, `donor_id`, `sample_id`, `barcode` and `m_std`. Donor-level aggregates from round 9 are under `results/round9/claude_science/` on Longleaf. Only aggregates enter the repository. ACS PUMS 2018 is also at `~/hest-1k/acs_pums2018` on Nicolas's Mac. It is not gated, and its states and PUMAs give clusters at G = 51 and G = 265.
- **Compute.** Longleaf through the session's compute connector. The project Python is `env/miniforge3/envs/hest/bin/python`. Compute goes to batch jobs, never to the login node (the connector's notes for `ssh:longleaf`).
- **Code to reuse.** `code/scripts/round9_probe_feasibility.py` and `code/scripts/round9_probe_takeall.py` (design-based intervals under random and take-all selection of donors), `code/scripts/round9_c0_diagnostics.py`, and the round 5 and round 7 PPI scripts.

## 6. Rules that matter most here

The full set is in the branch's `CLAUDE.md`. Three bear most on this direction.

- A literature check for novelty before any claim, run continually by independent subagents, under the vocabulary of survey sampling, econometrics and statistics as well as machine learning. The model is prone to rediscovering results it absorbed in training. Do not re-propose a direction already graded in `results/round9/scan/scan_structured_results.json`, unless the new claim differs in a way you can state.
- Subagents cannot use OpenAlex unless Nicolas approves its credential card. Tell them to use arXiv, Crossref, Semantic Scholar and web search, and to space their calls. Full-text copies of papers stay out of the repository.
- Predictions are written before every run and scored after it.

## 7. The other track

Track `newtopic` runs at the same time on branch `claude-science-newtopic`, looking for a fresh direction outside clustered PPI and hierarchical conformal prediction. The two tracks are independent. Do not edit its files.
