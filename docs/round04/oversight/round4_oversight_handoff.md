> **Active context document for the oversight chat, dated 30 September 2026.**

# Handoff to the next oversight session: rounds 1 to 4, the path to the current directions, and what is running now

30 September 2026. Written by the oversight chat that ran round 3 and opened round 4, for the chat session that takes over in the new spatial transcriptomics project. Repository `NicWYZ/HEST-1k-replication`, `main` at tag `round4-data-v2` (commit `9d7277d`), with two track branches in progress. For thorough context, start from `docs/README.md`, which is now a reading guide to every document in the project, ordered by round and stage, with a short start-here path. The previous handoff, `docs/round03/00_prep/round3_oversight_handoff.md` (22 September), covers rounds 1 and 2 in detail and its sections 0, 2, 6 and 10 still hold. This one is written so that Nicolas can reconstruct, for Dr. Zhu and Dr. Zhang, exactly what was done since the last presentation and why the project is where it is. Section 3 is that narrative. Section 9 is the presentation the new session helps build.

---

## 0. Your role, and the people

The project runs as three parties, unchanged from the previous handoff.

- **Nicolas Weiyang Zhang** (Longleaf ONYEN `weiyang`, Slurm accounts `rc_htzhu_pi` and `rc_tengfei_pi`) is the first-year biostatistics PhD student whose project this is. He reads everything, understands every command before it runs, and carries documents between sessions by hand. Every memo for a Claude Science session goes to him in full, ready to paste.
- **Claude Science sessions** execute. There are now two running at once (section 7). They have SSH access to Longleaf, submit Slurm jobs, write stage reports, commit and push on their own branches. They do not make scope decisions.
- **You** supervise. Write instruction documents and decision memos; enforce the gate rule; review stage reports critically by checking numbers against files in the connected repository; consolidate results into presentations in Nicolas's style; explain concepts with derivations done slowly; do literature research; steer direction.

### 0.1 How Nicolas works

Everything in the previous handoff's section 0.1 stands. Repeated corrections this session, so treat them as fixed. Plain natural prose. No em-dashes. No colon-then-explanation constructions. No compressed or clever phrasing. Math as rendered LaTeX. Numbers at the precision the comparison needs, with the relative scale stated. Do not inflate length. Memos and instruction documents are handed over as complete standalone documents, never as diffs. When he asks how something works, derive it step by step; he asked this session for the cluster-robust variance with its influence function, the HCP weighting with the atom at infinity and the $\frac{K}{K+1}\bar F(q) \ge 1-\alpha$ condition, and a list of nineteen concepts from a PDF, and each time the full derivation was what he wanted. He has minimal biology by design; expression is a signal to predict, calibrate and use for inference. His career goal is quantitative finance, and he asked once how the current work transfers (answer in section 3.8). He prefers ML venues or top statistics journals.

Two instructions from him that stand until he says otherwise. "Don't worry about communicating the benchmark issues for now", so the benchmark-practice note (D4 in section 3.5) is not pursued and `docs/round02/i05/exec/hest_bench_issue_draft.md` stays unsent. And storage on Longleaf is not a constraint.

### 0.2 How the Claude Science sessions behave, and what to watch

They are thorough, honest about failures, and cite numbers to files. Four patterns from this session.

- They over-run open-ended tasks. Every non-analysis task in every instruction document now carries a time cap, and checker or tooling work is capped at half a day per interval.
- They misread gate rules in the permissive direction, and one P8 job was submitted before Nicolas had approved the operating plan (reported openly, harmless). Restate the gate rule verbatim in every memo.
- They flag what looks wrong in an instruction document in a numbered list rather than changing it, which is what they are told to do and is valuable. The PPI plan's section 8 has eight such points on my document (section 8.1 below); read those lists first in every plan.
- They take instructions literally. "Job names prefixed `r4ppi_`" could not be applied because the submission route replaces `--job-name`, so the documents now say jobs are identified by Slurm id. "3 mm cores" in a diagnostic threshold was wrong for four 5 mm cores, and the session reported both measures rather than choosing.

Their reports are long. Read "what was not checked", "escalations" and "proposed edits, not applied" first.

---

## 1. Where things stand on 30 September

Round 3 (22 to 24 September) ran Topic A's first experiment and Topic B's first result and the data expansion, and it changed the project's direction. The two original topics as framed are retired for reasons measured on the data (section 3.4). The project was reframed twice more, once after round 3's results (section 3.5) and once after a literature check found that one of the new directions had been occupied six weeks earlier (section 3.6). The current framing is one paper, "Labelling budgets for prediction-powered inference with clustered data", methodology first with spatial transcriptomics as the main application and ACS PUMS income as a second (section 4).

Round 4 has three parts. The data pull (stage P, 28 September, plus an addendum P8 on 30 September) is done and accepted; it added a lung Xenium task of 20 samples and 15 donors and the whole-transcriptome gene lists. Two tracks started on 30 September in concurrent Claude Science sessions, the PPI track (branch `round4-ppi`, gates Q1, Q3, Q5) and the conformal track (branch `round4-conformal`, gates C2, C4). Neither has reached its first gate. Section 7 has their state and section 8 what to look for when the first reports arrive.

Nicolas presented on 21 September and got through slide 6 of 14 (the replication and the three benchmark issues). The next presentation starts from the literature landscape and tells the whole path to the current directions. Section 9.

---

## 2. Timeline

| dates | what |
|---|---|
| early September | literature review; Topics A and B proposed |
| 12 to 16 Sept | round 1, faithful replication and instrumentation |
| 16 to 19 Sept | round 2, R0 to R8; freeze at `round2-final` |
| 20 to 21 Sept | deck built; numeric-claim gate closed; `round2-docs-clean`; half the deck presented |
| 22 Sept | round 3 opens in new sessions. S0, A0, A1, D0. A1 gate (`round3-A1`); my A1 decision memo; D1 to D3 approved |
| 23 Sept | interval 2: H0, A2, A3, D1 to D3. A3 gate (`round3-A3`, revised `round3-A3-r2`); my A3 decision memo |
| 24 Sept | interval 3: H1, A4a, A4b, B1, B2, D4. Final report (`round3-final`, revised `round3-final-r2`). My directions document |
| 25 to 27 Sept | assessment of direction; the methods and state-of-play reference; concept explanations |
| 28 Sept | round 4 data pull in a fresh session; P1 stop and decision; P7 report; `round4-data`. Originality check; both track documents revised |
| 28 to 29 Sept | concept explanations from Nicolas's list; quant-finance transferability; three extra directions |
| 30 Sept | P7 decisions memo; P8 addendum; `round4-data-v2`. Both tracks start. Working-copy and version-management notes to both sessions. `docs/README.md` rewritten as a reading guide and the oversight documents committed. The spatial transcriptomics work moves to its own Claude project. This handoff |

---

## 3. The path from the literature to the current directions, chronologically and with reasons

This is the section Nicolas needs for the advisors. Each step says what was believed, what was measured, and what changed because of it.

### 3.1 The literature landscape and the two original topics (early September)

The landscape (`docs/round00/literature_landscape.md`, deck slide 7) had four points. Accuracy has a low ceiling (best average Pearson about 0.42) and the direction is crowded. Foundation-model embeddings are dominated by nuisance variation (institution recoverable at near 100%, GLMP and others). Predicted expression is consumed downstream as if measured. Only two preprints apply valid-inference machinery to spatial transcriptomics, and neither treats the dependence of spots within slides within donors. The gap was trust rather than accuracy.

Topic A, calibrated uncertainty for histology-to-expression prediction under cohort shift, using conformal prediction with reweighting for the shift. Topic B, valid inference for population quantities using predicted expression, using prediction-powered inference with a cluster-robust variance. Both biology-light, both on HEST-1k, both connected to the semi-supervised inference literature, and chosen because their skills transfer to finance.

### 3.2 What the replication found (rounds 1 and 2, 12 to 21 September)

The previous handoff's section 6 has the full account. What matters for the story. The replication was exact (0 of 108 cells off the leaderboard by more than 0.03). The benchmark has ten properties that were not in the paper, of which three are on the presented deck (patient labels wrong on two tasks; split design worth 1.6 times the whole encoder ranking; Table A13 ranks by embedding width because the penalty is inert). And three results were the premises of the topics measured rather than argued. The head has no intercept and its predictions are spread 1.84 times too widely (the $R^2$ ladder). A slide-and-session signature lives in the features and not in the expression. The unit of inference is the donor, with a between-donor share of expression variance near 0.4, so the design effect is in the hundreds.

Two things in the deck as presented are now wrong and must be corrected at the next presentation. IDC's `TENX95` and `TENX99` were presented as probably one donor; round 3's audit of the vendor's run metadata shows they are two donors from one laboratory and one instrument three weeks apart, so the replicate-leak reading of IDC is withdrawn and its $+0.065$ is a same-laboratory, same-instrument effect (READ's $+0.090$ is the only replicate figure). And the previous deck's speaker notes for slide 11 should say precision is "set by the number of donors", not "is the number of donors".

### 3.3 Round 3, the first experiments (22 to 24 September)

Round 3 was designed in the previous handoff. A conformal harness with four fold designs (random spot, shipped patient, audited donor, slide-out), calibration held out at the highest level the training pool supports; coverage across designs (A1); the anatomy of failure (A2); reweighting and hierarchical conformal as repairs (A3); adaptive scores and a model-based comparator (A4); PPI with three variances and semi-synthetic coverage (B1, B2); and a designed expansion of the data beyond the benchmark for an institution axis (D0 to D4). Gates at A1, A3 and the end of round.

The results, in the order they matter (numbers in section 5).

1. Coverage is a property of the calibration design, not of the predictor. Random 0.894, slide-out 0.859, donor 0.802, patient 0.786, the same ordering for all twelve encoders, and encoder quality does not predict coverage under shift (range under 0.02).
2. Where the calibration scores come from decides coverage; how many there are barely matters. On one shared training set, calibrating on held-out donors covers 0.856 and calibrating on spatial blocks inside the training slides covers 0.744, block lower in 138 of 138 cells, and the donor arm did that on 38% of the spots. Coverage does not track the number of calibration units $K$ (Spearman $-0.03$). My own A1-gate reading, that the shortfall was a small-$K$ effect, was tested in A2c and refuted.
3. Feature-based reweighting cannot repair the shift. Calibration and test slides are separable at AUC 0.97 or better from the embedding and at 0.90 from eight morphology covariates alone, so the effective calibration size under importance weights collapses to a median 2%. Tissue composition identifies the slide nearly as well as the scanner signature does, so the shift is not separable into a technical part to remove and a biological part to keep.
4. The valid method for a new donor exists and is conservative. Hierarchical conformal prediction (HCP, Lee, Barber and Willett) is infinite wherever $K + 1 < 1/\alpha$, which at 90% is every unit-calibrated fold in the benchmark (1,932 of 1,932 cells). With $K = 10$ calibration donors on CCRCC it is finite everywhere and covers 0.969 at 1.95 times the pooled quantile's width; the one-score-per-donor interval covers 0.911 at 1.43 times; the pooled quantile covers 0.864 whether 6 or 10 donors calibrate it. Indiana kidney at $K = 10$ gives 0.988 at 1.91 times.
5. Adaptive scores buy little except in the upper tail. CQR 2.65 wide against 2.69 for the absolute score at matched 90% coverage; the scaled score 14.8. In the top decile of predicted values, where the absolute score covers 0.72, CQR and conformalised negative binomial reach 0.87. This is the $R^2$ ladder's over-dispersion seen from the interval side.
6. Spot-level uncertainty statements about predicted expression are off by more than an order of magnitude, and the fix is standard. The donor-clustered standard error is 29 to 68 times the spot i.i.d. one. Over 200 relabellings the spot interval covers 0.044 at nominal 0.90, the donor cluster-robust interval with a $t_{G-1}$ reference 0.913, the percentile donor bootstrap 0.711. PPI intervals are 0.85 to 0.89 as wide as classical for the encoders and 0.98 for a permuted predictor; the power-tuning weight $\lambda$ falls from about 0.7 at six labelled donors to about 0.2 at eight or more. The paper's own biomarker example on IDC is $-0.46$, $-0.70$, $+0.53$ and $+0.87$ on its four donors, each interval excluding zero, and the pooled donor-clustered interval spans zero at 59 times the spot-level width.
7. The expansion delivered donors, not an institution axis. Across all 46 organ-by-technology cells of HEST-1k there is no cell with three laboratories at three donors, and no two-laboratory cell with disease held fixed. The 23 kidney samples labelled Washington University were generated at Indiana. What the expansion did deliver is Indiana kidney (25 donor units, every technical axis fixed, donor shift costing about one point of coverage with a third of CCRCC's fold scatter), a kidney tumour-versus-non-tumour shift that is asymmetric (0.905 one way, 0.703 the other), and breast Xenium's instrument generation as a session-like axis (0.81 against 0.89).

### 3.4 The roadblocks, and why Topics A and B as framed were retired (24 September)

Before the last interval Nicolas asked whether the project should stop and rethink because the methods looked data-limited. My answer (`docs/round04/00_prep/round3_directions.md`, saved in the Project as `claude/round3-directions.md`) rested on three facts from the results above.

The unit is the donor, on both sides. With $m$ spots per donor and between-donor share $\rho$, $n$ donors of $m$ spots are worth about $n/\rho$ donor-equivalents, and no number of spots inside a donor substitutes for a donor. On the conformal side the same integer appears as $K + 1 \ge 1/\alpha$. Any method has to be stated in donors.

Feature-side methods are closed. Result 3 says anything relying on overlap between calibration and test features fails on this data, and result 7 says the institution axis cannot be measured in HEST-1k. Together they retire "calibrated uncertainty under cohort shift" as a paper. The shift that exists and is measurable is donor novelty, with session and instrument on top.

The open gap was between validity and sharpness at small $K$. HCP costs about twice the width and over-covers by seven to nine points at $K = 10$, and nobody had closed that gap for grouped data at the $K$ every biomedical study lives in.

Four things were retired at that point. The cohort-shift framing, feature reweighting, the scaled score, and any laboratory term from HEST-1k.

### 3.5 The pivot to two tracks (24 to 28 September)

The directions document put up four candidates. D1, cluster-robust prediction-powered inference (variance, small-$G$ reference, the behaviour of $\lambda$, the allocation of a labelling budget between donors and spots). D2, a sharper valid prediction set for a new donor at $K$ of 10 to 25. D3, how much measured expression predicted expression needs (D1 plus a small labelled sample on the test slide, framed for downstream users). D4, a benchmark-practice note (Nicolas has set it aside). My recommendation was one paper built as D3 with D1 as its core, with D2 as the research question for round 4 under a go or no-go.

Nicolas decided to run D1 and D3 together as a "PPI track" and D2 as a "conformal track", in two concurrent fresh sessions, after pulling all the HEST-1k data the reframed question could use. That produced three instruction documents, the data pull first (section 6) and then the two tracks.

### 3.6 The originality check, and the second reframing (28 September)

Before the tracks started, Nicolas asked how original the proposed methods were and whether the only contribution was applying existing methods to a new context. The check (`claude/round4-originality-check.md`) found two things.

Prediction-powered inference is the survey-sampling difference estimator. Mozer (arXiv:2603.19160, March 2026) shows PPI's mean estimator is the difference estimator of Cassel, Särndal and Wretman (1976) and PPI++ is the generalised regression estimator. Model-assisted estimation under two-stage and cluster sampling with cluster-level variance is textbook (Särndal, Swensson and Wretman 1992, chapter 8; Breidt and Opsomer 2017). So "cluster-robust PPI" is not a new estimator, and the paper says so on its first page. What nobody has written down, for PPI under cluster sampling, is what predictions can and cannot buy and what that implies for the labelling design. The central statement is that as units per cluster grow, the PPI-to-classical variance ratio tends to $1 - R^2_{\text{cluster}}$, the predictor's cluster-level accuracy, not its unit-level accuracy. That is general and every user of PPI with clustered data needs it.

The conformal track's problem had been taken up six weeks earlier. Mallick, Tchetgen Tchetgen, Dobriban and Lee, "Generalized Hierarchical Conformal Prediction" (GHCP, arXiv:2608.15500, 15 August 2026), start from exactly our observation that HCP is conservative at small $K$, assume $o \ge 1$ initial observations from the test group, restore hierarchical exchangeability by a random donation of a reference group's size, and are provably valid and empirically narrower than HCP. Their real-data example is ACS PUMS income. Our "small labelled sample on the test slide" idea was their setting, with a better construction. What remains open is the $o = 0$ case, whether any valid method can be sharper than HCP with no test-group observations, which is a lower-bound question.

The paper was reframed as "Labelling budgets for prediction-powered inference with clustered data" (section 4), and both track documents were rewritten. The PPI track gained the gain theorem and allocation result as its theorems, lost its within-slide conformal arm to the conformal track, and gained the ACS application so the results read as general. The conformal track now implements GHCP, cites it and does not compete with it; its candidates are kept only where they have a role beside GHCP; the $o = 0$ lower bound gets a three-day scoping with a stop rule; and its main product is the price of validity as a map over $(K, o)$.

### 3.7 The concept corrections that changed the PPI track (28 to 30 September)

While explaining the gain theorem to Nicolas (`claude/round4-concepts-explained.md`, section 1h) I found that my track document had regime B under-specified. With a few labelled units in every cluster, what the variance is depends on the target. Under the design-based target (the full-data value of this donor set, which is what every real-data coverage check uses), every cluster is observed, the clusters act as strata, the predictor's cluster-level error drops out entirely, and the gain is governed by within-cluster $R^2$. Under a superpopulation target the between-cluster term stays and cannot be reduced. So regime A's gain tracks cluster-level $R^2$ and regime B's tracks within-cluster $R^2$, and a foundation model with large slide offsets is exactly the predictor for which regime B is much better. Q3 now derives both and predicts it.

Revising Q3 exposed a fifth soft spot in round 3's estimator. B2's target is the full-data value of a fixed set of 24 donors, but its variance carries no finite-population correction, so drawing 12 of 24 donors is treated as drawing 12 from infinitely many. That alone predicts the over-coverage at $n_L = 12$ (0.94 to 0.95) that B2 saw, so Q1 now tests the correction, and its prediction 3 was rewritten to say the over-coverage is mostly the missing correction rather than $\lambda$ optimism.

### 3.8 Three further directions, and the quant-finance question

Nicolas asked whether other directions were open with the data and results in hand, and how the work transfers to quantitative finance. Three directions were added as bounded supplements or queued. Two-way clustering (Cameron, Gelbach and Miller 2011) where a second grouping crosses the donor, added to Q4 as a one-day supplement, with the expectation that no HEST task has a crossed second grouping with more than four levels. Cluster-level recalibration, predicting each donor's offset $b_s$ from its mean embedding leave-one-donor-out and checking that the variance ratio moves with the cluster-level $R^2$ it changes, added to Q2 as a one-day fifth unit, since it is the direct test of the theorem and the cheapest thing a practitioner could do before spending a budget. Active cluster selection, which clusters to label rather than how many, held for round 5; Q5 records the per-donor inputs it will need.

On transfer. Cluster-robust inference with few clusters, labelling-budget allocation under a predictor, and prediction sets for a new group are the same problems as panel data with firms or dates as clusters, analyst-coverage budgets, and forecasting for a new asset or regime. The framing was kept general for that reason.

---

## 4. The current paper, as planned

Working title, "Labelling budgets for prediction-powered inference with clustered data". Methodology first, two application domains.

- Section 2, setting. Units nested in clusters; a black-box predictor whose error has a cluster-level component; a labelling budget spent on clusters and units per cluster; two targets, confidence intervals for population quantities and prediction sets for units in new clusters.
- Section 3, inference. The model-assisted (PPI++) estimator under two-stage sampling, positioned against Mozer and Särndal et al.; the cluster-robust variance with the small-$G$ reference and the finite-population correction for the design-based target; the gain theorem (variance ratio tends to $1 - R^2_{\text{cluster}}$); corollaries on $\lambda$ and on when PPI cannot help.
- Section 4, prediction sets. HCP at $o = 0$ and GHCP at $o > 0$; the price of validity as a function of $(K, o)$ in simulation and on data; a lower bound at $o = 0$ if the scoping delivers one.
- Section 5, design. Optimal allocation between clusters and units with a predictor ($m^\star_{\text{PP}} = \sqrt{(c_d/c_s)\,\sigma^2_{e,r}/\sigma^2_{u,r}} \le m^\star$); regime A (few clusters fully labelled) against regime B (few units in every cluster), with the crossover $R^2_{\text{cluster}} < 1 - n_L/G$; the joint design, since the same $o$ labelled units per cluster serve the rectifier and GHCP.
- Section 6, applications. ACS PUMS income (comparable to the PPI package and the GHCP paper) and HEST-1k on CCRCC, Indiana kidney and lung Xenium.

The round-3 coverage results are the motivation section, not the contribution. Venue, ICML 2027 (January deadline) if round 4 finishes by mid-November, with Biometrics or JRSS-C as the fallback.

---

## 5. Key numbers, with the files they come from

All paths are under the repository root. Round-3 numbers are at `round3-final-r2`; round-4 numbers at `round4-data-v2`. Every one was read back from its file by me during this session.

**Round 3, conformal side.**
- Coverage by design at $\alpha = 0.1$, absolute score, 132 cells over 12 encoders. Random 0.894, patient 0.786, donor 0.802, slide-out 0.859 (`results/round3/A1_coverage/a1_coverage_by_design.csv`).
- Unit against block calibration on a shared training set, 0.856 against 0.744, block lower in 138 of 138 cells (`results/round3/A2_conditional/a2_unit_intervention.csv`); coverage against $K$ Spearman $-0.03$ (`a2_coverage_vs_K.csv`); top predicted decile 0.68 against 0.90 (`a2_by_stratum.csv`); level and scale shares (`a2_level_scale.csv`).
- Reweighting, AUC $\ge 0.97$ from the embedding, 0.90 from morphology, median $n_{\text{eff}}$ 2%; HCP infinite in 1,932 of 1,932 cells at $\alpha = 0.1$ (`results/round3/A3_report_numbers.csv`, `results/round3/A3_weighted/a3_by_fold.csv`).
- Scores at matched coverage, CQR 2.65, absolute 2.69, scaled 14.8; top decile 0.72 to 0.87 under CQR and conformalised NB (`results/round3/A4_scores/a4_report_numbers.csv`).
- HCP at $K = 10$ on CCRCC, 0.969 at width ratio 1.95; one-per-donor 0.911 at 1.43; pooled 0.864 (`results/round3/A4_scores/a4b_summary.csv`, `a4b_hcp_K10.csv`).
- Indiana at $K = 10$, HCP 0.988 at 1.907, pooled quantile 0.887; donor design 0.878; random 0.888 (`results/round3/D4_expansion/d4_pooled_numbers.csv`). Same file, the layout anchor (coverage moves by at most 0.0017 between the benchmark's patches and the release's) and the kidney population shift (0.905 and 0.703) and breast instrument generations (0.81 against 0.89).

**Round 3, inference side.**
- Clustered-to-spot standard-error ratio 29 to 68 on CCRCC (`results/round3/B1_ppi/b1b2_report_numbers.csv`); estimates and $\lambda$ per setting (`b1_estimates.csv`); IDC $\theta_1$ per donor and pooled (`b1_theta1_by_slide.csv`); the four acceptance identities (`b1_acceptance.csv`, 92 CCRCC rows).
- Coverage over 200 relabellings, spot i.i.d. 0.044, cluster-robust 0.913, bootstrap 0.711 (`results/round3/B2_semisynthetic/b2_coverage.csv`); width ratios 0.85 to 0.89 and 0.98 permuted (`b2_width_ratio.csv`).
- Between-donor share of expression variance about 0.3 to 0.4 (`results/round2/R6_variance/r6_variance_by_task.csv`).

**Round 3, expansion and audit.**
- Inventory of 1,276 samples and the institution criterion (`results/round3/D0_inventory/hest_inventory.csv`, `docs/round03/i01/exec/round3_d0_expansion_proposal.md`); 105 samples, 70.3 GB downloaded.
- The round-3 audit file, 148 rows (`results/round3/D3_audit/donor_audit_r3.csv`, with `d3_notes.md`); IDC four donors; the Washington University set generated at Indiana.

**Round 4, data pull (P7 report, `docs/round04/i01/data/round4_data_report.md`, accepted in `docs/round04/i02/data/round4_data_P7_decisions.md`).**
- Set L, 24 samples, 120 files, 9,358,042,424 bytes; set V, 39 samples, 195 files, 18,980,302,609 bytes (`results/round4/data/P1_selection/selection_summary.json`, `P1_download/p1_verification.csv`). Set L has 55,104 patches and 86,408 spots; set V 93,814 and 111,623.
- Embeddings, 24 of 24 samples per encoder, 55,104 rows equal to patches (`P2_embeddings/p2_acceptance.csv`).
- Morphology anchor exact on `INT1` and `NCBI783` (`P3_morphology/p3_anchor_comparison.csv`); pooled join rates 0.998939 Indiana, 0.969680 breast, 0.983903 lung; `TENX197` 0.861937 (`P3_morphology/morphology_ext_pooled.csv`, `p3_acceptance_join_and_quantiles.csv`).
- D4's probe box half-width exactly 2.0 times too large on all 30 Indiana rows, pair counts 3.64 to 3.97 times (`P3_morphology/p3_d4_geometry_discrepancy.csv`). The round-3 claim that morphology removes 31 to 34% of the probe signal is quarantined.
- The round-4 audit file, 211 rows, 24 set L (12 verified, 8 contradicted, 4 unverifiable) (`P4_audit/donor_audit_r4.csv`, `p4_notes.md`).
- Training-only gene lists, top-50 overlap with the shipped lists CCRCC 42.71, HCC 24.00, LYMPH_IDC 21.00, READ 16.50, PRAD 11.00 (`P6_genes/p6_gene_summary.csv`); one Indiana fold short at 200 and 500.

**Round 4, P8 addendum (`docs/round04/i02/data/round4_data_P8_report.md`).**
- Lung task 20 samples, 15 donor units, 15 donor folds, 45 `a4b_k10` rows, pool 14, minimum 4 training donors, 343 genes of 541 features (`results/round4/data/P5_task/p5_validation.csv`, `LUNG_XENIUM.json`).
- `NCBI865` keeps 2,142 of 2,143 patches after dropping barcode `051x019` (`P8_addendum/p8_subset_after_drop.csv`).
- Controls dropped, 61 on five Xenium sets and 220 on IDC; genes left IDC 280, PAAD 98, SKCM 282, COAD 351, benchmark LUNG 198, breast 90 (`P8_addendum/xenium_panels_genes_only.csv`).
- Four lung samples are 5 mm cores (`NCBI864`, `NCBI865`, `NCBI867`, `NCBI884`), recorded in the task file under `expansion.core_diameter_mm_source`; edge-patch fraction beyond 1.6 mm median 0.106 (`P8_addendum/lung_edge_patches.csv`, `p8_report_numbers.csv`).

**Round 4, PPI track Q0 (branch `round4-ppi`, commit `38e9c29`).**
- B1 anchor, 92 of 92 rows agree, maximum difference 0.0 (`results/round4/ppi/Q0_setup/anchor/q0_anchor_compare_summary.json`).
- ACS from `ppi_py` 0.2.3, 380,091 rows, arrays `Y`, `Yhat`, `X` (age, sex); no state, PUMA or year (`Q0_setup/acs/acs_inventory.json`).
- Lung wrapper, 60 rows, drop applied and subset relation passing (`Q0_setup/lung_wrapper/q0_lung_wrapper_check.csv`).

---

## 6. The round-4 data pull, in brief

Stage P (`docs/round04/i01/data/round4_data_pull.md`) pulled set L, the lung Xenium cell (24 samples, one laboratory), and set V, every remaining labelled Visium sample not already on disk, then embedded set L with three encoders, built morphology covariates for all 72 expansion samples, audited set L against source records, defined the lung task, and built training-only gene lists at 50, 200 and 500 for every Visium task.

It stopped once, at P1, because my prediction that set V would be 150 to 250 samples was wrong (39, because 113 labelled samples were already on disk). The decision (`docs/round04/i01/data/round4_data_P1_decision.md`) was to proceed as selected. Set V is downloaded, not embedded and not audited, with 24 uncertain-pixel-size flags travelling with its rows.

The P7 report raised nineteen escalations; the decisions memo answers each. The ones that shaped the tracks are the reinstatement of `NCBI865`, the quarantine of the D4 probe claim, the control-feature filter on Xenium panels, the lung donor count (15, not 21; HEST's 21 keys split four donors into eight labels and count unresolvable samples), and the $K = 10$ design on lung training on 4 donors. P8 applied them and tagged `round4-data-v2`.

---

## 7. What is running now

Two Claude Science sessions, started 30 September, each from its own instruction document (`docs/round04/i01/ppi/round4_ppi_track.md` on the PPI branch; the conformal document is in the Project as `claude/round4-conformal-track.md` and should appear on that branch as `docs/round04/i01/conformal/round4_conformal_track.md`). Both branch from `round4-data-v2`.

**PPI track**, branch `round4-ppi`, local clone `~/HEST-1k-replication` (the one your session is connected to), Longleaf code clone `/work/users/w/e/weiyang/hest_code/round4-ppi/`. Stages Q0 (setup, done and committed at `38e9c29`), Q1 (the estimator made right, simulation; in progress; gate), Q2 (gain theorem, allocation, recalibration test), Q3 (two labelling regimes; gate), Q4 (paper tables, ACS, gene axis, two-way supplement), Q5 (joint design table, round-5 inputs, final report; gate). Operating plan `docs/round04/tracks/ppi/round4_ppi_plan.md`, with amendments 9 (working copies) and 10 (version management). About eighteen working days.

**Conformal track**, branch `round4-conformal`, sibling clone `~/HEST-1k-replication-conformal`, Longleaf code clone `/work/users/w/e/weiyang/hest_code/round4-conformal/`. Stages C0 (setup and the A4b anchor), C1 (simulation testbed with an $o$ axis and GHCP), C2 (remaining candidates K1, K4, K5, the $o = 0$ lower-bound scoping capped at three days, the go or no-go; gate), C3 (the $(K, o)$ map on real data with a fixed output format that Q5 reads), C4 (final report; gate). About fourteen working days. As of the evening of 30 September the branch is pushed at `2411f53` with C0 (lung reader check and anchor pass), C1 (the testbed, and a code-path check of GHCP and HCP against the released GHCP code) and the start of C2's lower-bound scoping (`docs/round04/i01/conformal/round4_conf_lower_bound.md`). Operating plan `docs/round04/tracks/conformal/round4_conf_plan.md` on the branch.

**Coordination.** Disjoint write areas (`results/round4/ppi/` and `results/round4/conformal/`, `round4_ppi_*` and `round4_conf_*` scripts and documents). Shared and read-only, everything under `results/round3/` and `results/round4/data/`, the embeddings, the morphology parquets, the harness (md5 `0ad7ae8efe554c1f285e5f384a9fb7f5`). Neither writes the audit file. The conformal track reads the ACS data from the PPI track's `Q0_setup/acs/` on branch `round4-ppi`; the PPI track's Q5 reads `results/round4/conformal/C3_real/c3_o_sweep.csv` from branch `round4-conformal`. The Longleaf project tree `/work/users/w/e/weiyang/hest_replication` stays on `main` at `round4-data-v2` as the data root and nobody checks out a branch there.

**Version management** (sent to both sessions on 30 September; on the PPI branch as amendment 10). At each gate the session commits, tags, pushes, and opens a pull request into `main` with `gh pr create`, then stops. It never merges. After you accept the report, Nicolas merges on GitHub with a merge commit (never squash or rebase, since provenance records cite commit hashes). Branches are never rebased, amended after push, or force-pushed. A rejected gate is fixed with new commits on the same open pull request. The project tree on Longleaf does not follow `main` during the round.

---

## 8. What to look for in the first wave of gate reports

### 8.1 PPI track, Q1 (interval 1)

Read `docs/round04/tracks/ppi/round4_ppi_plan.md` section 8 before the report. It lists eight points in my instruction document that the session flagged rather than changed. My view on each, for the Q1 decision memo.

1. The $r = 0$ cells cannot be built with $\hat y = y - a - \epsilon$, since the spot correlation stays positive. Right. Accept an independent predictor with the same donor-and-spot structure for $r = 0$, reported.
2. The $r = 0$ acceptance band (every interval covers 0.89 to 0.91) conflicts with predictions Q1.1 and Q1.2 and is about 1.5 Monte Carlo standard errors wide. Right. Score the band against the variants and $G_L$ the predictions call valid, with the MC error beside it.
3. Q1.5 is inconsistent with the design because $\sigma_a^2 = \sigma_u^2/2$ fixes the cluster-level $R^2$ at $2/3$ in every cell, so the Q2 theorem predicts a substantial gain at large $m$ even at $\rho = 0.5$. Right, and Q1.5 will likely be refuted for exactly the reason the theorem gives. Score it as written and, in the Q1 memo, add a $\sigma_a^2/\sigma_u^2 \in \{0.25, 1, 4\}$ axis to Q2's simulation check so the cluster-level $R^2$ varies.
4. The unlabelled term $V_U = \lambda^2\,\text{Var}(p_g)/G_U$ does not vanish with $m$, so the ratio reaches $1 - R^2_{\text{cluster}}$ only when $G_U \gg n_L$; and under $\hat y = y - a - \epsilon$ the rectifier's cluster component is $(1-\lambda)u_g + \lambda a_g$, not $u_g - \lambda a_g$, with the same endpoint at the optimal $\lambda$. Both right. The theorem statement in `docs/round04/tracks/ppi/round4_ppi_theory.md` should carry the $G_U$ condition, or be stated for the labelled term alone with $V_U$ reported beside it.
5. The ACS fetch against "any download is never the session's". The plan reads Q0 step 3 as the specific authorisation. Correct reading.
6. When $U$ is the complement of $L$, the estimator is $\lambda\bar{\hat y}_U + \bar r_L$ rather than the textbook $\lambda\bar{\hat y}_{\text{all}} + \bar r_L$, and the two terms are negatively correlated under sampling without replacement, so a finite-population correction on the labelled term alone may not be the exact design variance. Right, and this is the important one. For the design-based target the memo should adopt the textbook form with predictions over all $N$ units, where the only randomness is which $L$ was drawn and the correction is exact for the mean, and keep B1's complement form as the legacy variant with its own reported coverage.
7. Q4 unit placement. Accept the plan's placement.
8. Lung and $n_L = 16$. Accept; run lung at the $n_L$ values that leave at least two unlabelled donors.

Three further things from Q0's verification note (`results/round4/ppi/Q0_setup/q0_lead_verification.md`).

- **ACS has no cluster identifiers.** The `ppi_py` census data is `Y`, `Yhat` and `X` (age, sex) only. The ACS application as specified (states and PUMAs as clusters) cannot run from it. The decision is yours at the Q1 gate. The GHCP paper builds its ACS example from PUMS microdata with PUMA groups (likely through `folktables`); either the session fetches PUMS with state and PUMA fields under an explicit authorisation like Q0's, or Nicolas supplies the file. Until then the ACS units of Q2, Q4 and C3 wait, and both tracks are told to proceed with the HEST units, which their documents already allow.
- **B1's fourth acceptance check is not what my document said.** I wrote "the permuted predictor's donor-weighted $\lambda$ is 0"; B1's committed check 4 is the median width ratio against 0.95, and it fails on 21 of 36 CCRCC rows in the committed file and in the rerun alike. The anchor (reproduction of the committed file) passes regardless. Read from the rerun, the permuted donor-weighted $\lambda$ has median 0 for $\theta_3$ but 1.0, 0.86 and 0.46 for $\theta_2$ at $n_L = 6, 8, 12$. A permuted predictor with $\lambda$ near 1 means B1's spot-level tuning is misbehaving for the mean-difference estimand, which is one more reason Q1 replaces it. Ask the report to explain it and confirm the new tuning drives it to 0.
- **Provenance frame ids.** The lung wrapper's stamp carries the lead's frame id again, despite the brief. Minor; note it, and check that later fan-outs stamp from the sub-agent's process.

Check first, as always, that the acceptance identities hold to the stated tolerances, then that the design-based and superpopulation rows are labelled and that the finite-population correction row lands where prediction Q1.3 says. Predictions Q1.1 to Q1.5 are in the plan.

### 8.2 Conformal track, C2 (interval 1 covers C0, C1 and C2)

Read `docs/round04/tracks/conformal/round4_conf_plan.md` section 8 on the branch first. The session flagged five points in my instruction document. All five are right. (1) The C1 acceptance "every method within 0.01 of nominal at no donor effect" cannot hold for HCP, which calibrates at the $(1-\alpha)(K+1)/K$ quantile and is infinite at $K \le 8$, or for one-per-donor, whose expected coverage is $\lceil (K+1)(1-\alpha) \rceil/(K+1)$; accept evaluating each method against its own expected coverage. (2) A one-encoder rerun cannot reproduce the three-encoder mean 0.969 at $10^{-12}$; accept the per-encoder comparison plus a check that the summary is the mean of the three tables. (3) Prediction C3.3 names tasks C3 does not run; it is "not tested". (4) HCP at lung $K = 8$ is also finite only at $\alpha = 0.2$, since $K + 1 = 9 < 10$; my document said so for $K = 6$ only. (5) On lung, "within-slide" means within-donor. The plan's section 3 also records `whose()` verdicts on `results/round4/data/` (the data-pull session's stamps, and three unstamped directories, `P1_selection`, `P5_task`, `P7_report`); these are read-only inputs and nothing needs doing.

- C0's anchor must reproduce A1's committed `donor` coverage to $10^{-15}$ and A4b's $K = 10$ HCP coverage to $10^{-12}$ before C1 is read.
- C1's semi-real generator must reproduce A4b's 0.969 and 1.95 within 0.02 and 0.15; if not, the generator does not represent the data and that is stop-and-report.
- GHCP must reproduce every figure in its paper that its stated settings allow before any other GHCP number is read; check whether the session found released code and recorded the commit, or implemented from the paper.
- The go or no-go criterion (coverage at least 0.89 in every cell; price of validity at most $1 + \tfrac{1}{2}(\pi_{\text{ref}} - 1)$ in two thirds of cells; a stated guarantee) is fixed before C2 runs and must appear verbatim in `docs/round04/tracks/conformal/round4_conf_plan.md`. My prediction is that no $o = 0$ candidate meets all three parts and GHCP with the K5 score goes to real data.
- The lower-bound scoping is capped at three days with a stop rule; `docs/round04/i01/conformal/round4_conf_lower_bound.md` marks every step derived, conjectured or failed. If it produced a statement, that is a decision for you and Nicolas on whether to pursue it, and it is the one place a theoretical contribution is possible.
- On lung, C3 runs $K \in \{6, 8, 10\}$ with training-donor counts recorded, and the $o$ spots come from the test donor's own core, never the capture slide.
- C3's output columns are fixed (task, label_set, encoder, method, score, alpha, o, K, fold, draw, coverage, width_mean, width_median, n_test, finite) because Q5 reads them.

### 8.3 Both

Every number against its file. Difference lists before any term is named. Predictions scored held, partly held, refuted or not tested. The numeric-claim sweep run before handover. And each report's pull request opened but not merged.

---

## 9. The next presentation

Nicolas's outline, from `ST_presentation2.pdf`.

1. From last time. (a) Our read on the literature landscape. (b) Two originally proposed topics. (c) Efforts toward those two topics.
2. Since last time. (a) Roadblocks that rendered parts of Topics A and B unviable. (b) The pivot leading to the PPI track and the conformal track. (c) Further literature review deemed parts of both tracks occupied. (d) Revised new directions. (e) New results.

Section 3 of this document is the content in that order. Mapping to slides, for the same 15-minute budget unless he says otherwise.

- 1a and 1b are slides 7 and 8 of the round-2 deck, reused. 1c is slides 9 to 11 (the $R^2$ ladder, the slide-and-session signature, the donor as the unit), compressed, plus round 3's design. Slide 4 (issue 1) needs the IDC correction stated in one line since it was presented as one donor.
- 2a is one slide with three facts and their figures. Coverage by design (A1) and the unit-against-block figure (A2b); the AUC 0.97 and 0.90 and the 2% effective size (A3); the institution criterion unsatisfiable in HEST-1k (D0, D3).
- 2b is the four-direction table from `docs/round04/00_prep/round3_directions.md` and the choice of two tracks.
- 2c is Mozer (PPI is the difference estimator) and GHCP, in one slide, with what each leaves open.
- 2d is the paper plan of section 4, one slide, with the gain theorem stated in words and the regime comparison.
- 2e is round 3's results that are new to the audience (HCP at $K = 10$; the B2 coverage bars 0.044, 0.913, 0.711; the width ratios and $\lambda$), the data pull (the lung task, 20 samples and 15 donors), and the two tracks' status at the time of the talk, with the first gate results if they have landed.

The round-2 deck. The authoritative file is `docs/round02/tracks/deck/deck_round2/HEST-1k Replication Update.pptx`, which Nicolas keeps up to date. The text export `deck_round2_slides.md`, `deck.json` and `slides/*.html` are as of 22 September and may lag his edits; read the pptx, not them, when checking what was presented. The previous handoff's section 8.5 lists three suggested note edits that may not have been applied. The deck's numbers came from `results/summary/deck_numbers.csv` built by script, with figures under `figures/deck/` from committed scripts; keep that practice, with a `deck_round4` directory, a numbers file built by script, and the numeric-claim sweep over the deck text. Style as before, figure left and bullets right, brief speaker notes covering only what is on the slide. Build the deck with the Slides artifact type when the session offers one, as the round-2 deck was.

---

## 10. Open decisions, and who owns them

- Whether to contact Dobriban and Lee about the $o = 0$ lower bound or the joint design. Nicolas with David and Dr. Zhu; never a session's decision.
- The ACS PUMS source with cluster identifiers (section 8.1). You, at the Q1 gate, with Nicolas.
- Whether the lower-bound scoping's output, if any, is pursued. You and Nicolas after C2.
- Whether the D4 population probe is rerun with the corrected box. Round 5 if the paper needs the probe; the claim stays quarantined until then.
- Whether the benchmark note is written and the issue draft sent. Nicolas and David; set aside for now.
- Whether the ten unresolved numeric claims in `docs/round02/tracks/deck/deck_speaker_scripts.md` and `docs/round00/first_year_ST_project_proposal.md` (pre-round-3 documents) are cleaned up. Round-5 housekeeping.
- The frozen `r5c_leak_summary.csv` reading. My recommendation stands, a `superseded_reading` column in a housekeeping commit.

---

## 11. Next steps beyond round 4

- Round 5 candidates, in order. Active cluster selection with the Q5 inputs; the joint design paper section from Q5 and C3; the D4 probe rerun if needed; the older Spatial Transcriptomics platform (104 samples, 31 donors, 100 µm spots) only if a track finds a use; whole-transcriptome gene axes on all Visium samples; set V's audit if it is ever grouped by donor.
- Not planned. Any institution axis from HEST-1k; any train-time method; any further expansion download.

---

## 12. Dead ends, ruled out and why

- Institution or laboratory shift from HEST-1k. No cell with three laboratories at three donors; no two-laboratory cell with disease fixed; the one kidney "laboratory" contrast was tumour against non-tumour, and the Washington University label was generated at Indiana.
- Feature-based reweighting (weighted conformal with a density ratio). Slides are identifiable from features at AUC 0.97 and from tissue composition at 0.90; $n_{\text{eff}}$ collapses to 2%; weights move coverage a long way in both directions with no mean movement.
- The scaled score as a repair. 14.8 wide at matched coverage against 2.69.
- The small-$K$ explanation of the unit-calibrated shortfall. Refuted by A2c; the shortfall is scale, and the top-decile failure is the head's over-dispersion.
- Double conformal and repeated subsampling as C2 candidates. The first is infinite at $K = 10$; the second stays only as a known method in C1.
- Within-slide split conformal as our own method. GHCP is that setting with a better construction; we implement and cite it.
- "Cluster-robust PPI" as a new estimator. It is model-assisted survey estimation under two-stage sampling; the contribution is what predictions buy and the design, not the estimator.
- Treating IDC's `TENX95` and `TENX99` as one donor, and the replicate-leak reading of IDC. Withdrawn by D3.
- The ST platform and unlabelled samples as ways to reach my set-V prediction. Not applied; the tracks need donor-labelled, spot-resolved samples.
- The 1.6 mm edge threshold as a fixed rule. Four cores are 5 mm; the diagnostic is report-only either way.

---

## 13. Standing rules and working conventions

Restate the gate rule verbatim in every memo. "Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. Contact with anyone outside the project is never the session's decision."

The rules from the previous handoff's section 10 still stand (difference lists before naming a term; audit grouping variables against outside sources; numbers from files by path and the numeric-claim sweep before handover; thresholds in units the arithmetic supports; every refit anchored to a prior result; predictions before running; no ratio with a near-zero denominator; time caps on non-analysis work). Added this session:

- One writer per file; fragments plus a merge step with collision reporting; sub-agents run no git command; the lead is the only committer and checks every hand-back against its primary tables before commit.
- Every output directory gets `PROVENANCE.txt` (job id, partition, node, date, commit, command line, config hash, `PYTHONHASHSEED`, md5 of the executed script) and a `stamp_dir()` stamp from the `longleaf-provenance` skill, written by the job on the node, from the sub-agent's own process. `whose()` before reusing anything you did not create; `sibling` or `unstamped` means ask.
- Slurm limits at about three times a sibling's measured runtime, never a blanket 16 h; memory from `sacct` (16 GB on 4 CPUs for head fitting; 32 GB for any set-V job); record the partition and account; jobs identified by Slurm id.
- Each session has its own working copy locally and on Longleaf, never checks out a branch in another's, and runs code from its own Longleaf clone on `PYTHONPATH`. The project tree is the data root only.
- Pull requests at gates, merged by Nicolas on GitHub with a merge commit after acceptance; no rebase, squash, amend or force-push; the open pull request absorbs fixes.
- Xenium panels and target lists lose `NegControl*`, `UnassignedCodeword*` and `BLANK*` features at read time, with the count recorded. A task file's `dropped_patch_barcodes` is applied before any subset assertion (the round-3 `load_set` will raise otherwise).
- Every table carries a `target` column (design-based or superpopulation) where the distinction exists.
- The D4 probe claim (31 to 34%) is quarantined; do not cite it.
- The sessions never contact anyone outside the project; the audit file is written by neither track; label changes are proposed in reports and applied by the oversight chat between intervals.

---

## 14. Documents and where they live

**In the repository** (`docs/`, index in `docs/README.md`). Round 3, `round3_execution_plan.md`, `round3_A1_stage_report.md`, `round3_A3_stage_report.md`, `round3_d0_expansion_proposal.md`, `round3_final_report.md` (read its closing page, "What round 3 established"). Round 4, `round4_data_plan.md`, `round4_data_report.md`, `round4_data_P8_report.md`, `round4_ppi_plan.md` (on `round4-ppi`), and the conformal plan on its branch once pushed. Decisions, `docs/round03/00_prep/round3_oversight_handoff.md`, `round3_execution_handoff.md`, `round3_A1_decisions.md`, `round3_A3_decisions.md`, `round4_data_pull.md`, `round4_data_P1_decision.md`, `round4_data_P7_decisions.md`, `round4_ppi_track.md`. `docs/WAYS_OF_WORKING.md` is still the most useful document for anyone new.

**In the repository, added on 30 September** (with this handoff): `docs/README.md` rewritten as the reading guide, the old flat index kept at `docs/superseded/README_index_2026-09-30.md`; `docs/round04/00_prep/round3_directions.md`, `docs/round04/00_prep/round4_originality_check.md`, `docs/round04/i01/conformal/round4_conformal_track.md`, `docs/round04/oversight/round4_oversight_handoff.md` (this document); `docs/reference/methods_and_state_of_play.md` and `docs/reference/concepts_explained_round4.md`. No existing file was moved, because every plan and report cites documents by path and the tracks run against those paths; the physical reorganisation into round folders is a between-rounds job once round 4 is merged (see the guide's opening paragraph).

**In the old Biostat Research Project** (written by this session; the repository now holds every one of them): `claude/round3-A1-decisions.md`, `claude/round3-A3-decisions.md`, `claude/round3-directions.md`, `claude/methods-and-state-of-play.md` (every method derived from scratch, every round-3 result with how and why, what has not been tried, and what the rest of HEST-1k holds), `claude/round4-data-pull.md`, `claude/round4-originality-check.md`, `claude/round4-ppi-track.md`, `claude/round4-conformal-track.md`, `claude/round4-data-P7-decisions.md`, `claude/round4-concepts-explained.md` (the nineteen concepts Nicolas asked about, with the regime B correction in its section 4), and this handoff as `claude/round4-oversight-handoff.md`.

**The Claude project.** From 1 October the spatial transcriptomics oversight chats live in their own Claude project, separate from Biostat Research. Its memory starts empty; Nicolas seeds it from `st_project_memory_seed.md` (the project-relevant memory from Biostat Research, updated to 30 September). The repository is the complete record, so the project's knowledge area only needs the documents on the guide's start-here path for chats that are not connected to the repository.

**Your working copy.** Do not work in `~/HEST-1k-replication`. It is the PPI session's working copy, checked out on `round4-ppi`. Even read-only git commands there can write lock files; this session's `git status` left a stale `.git/index.lock` that would have blocked the PPI session's next commit, and it had to be deleted. Your session should be connected to its own clone, `~/HEST-1k-replication-oversight`, which stays on `main`. Read the track branches there after `git fetch origin` with `git show origin/round4-ppi:<path>` and `git log origin/round4-conformal`. Commit your memos and deck files there on a short-lived branch; the device shell has no GitHub credentials, so Nicolas runs `git push` from his own terminal and merges the pull request. If you ever must read the other clones, use `git --no-optional-locks` and nothing that writes.

---

## 15. What you do first

1. Follow the start-here path in `docs/README.md`, then read `docs/round04/i01/data/round4_data_report.md` sections 7 and 8, both track instruction documents, `docs/round04/tracks/ppi/round4_ppi_plan.md` section 8 and `docs/round04/tracks/conformal/round4_conf_plan.md` section 8 (both on their branches).
2. Confirm you are connected to `~/HEST-1k-replication-oversight` on `main`, not to either track's clone. The conformal session's sibling clone and both of its amendments (working copies in its plan's section 2, version management in section 9) are confirmed.
3. Settle the ACS source before the Q1 gate if you can, since both tracks wait on it for their ACS units.
4. Start the running list for the presentation from section 9, and check the pptx for what was actually presented.
5. When the Q1 report arrives, work through section 8.1 in order. When the C2 report arrives, section 8.2.
