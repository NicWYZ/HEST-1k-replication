> **Closed record, dated 24 September 2026.** The oversight chat's assessment after round 3, written for Nicolas and David and held in the Biostat Research project until it was committed here on 30 September. Its recommendation was refined by `round4_originality_check.md` four days later.

# After round 3: what we know, and the direction for the first paper

24 September 2026. Written by the oversight chat for Nicolas and David, from `docs/round03/i03/exec/round3_final_report.md` at tag `round3-final-r2`. Every number is read from a file named in that report; this document quotes them at the precision the argument needs.

---

## 1. The question this document answers

Round 3 was the first experiment for each of the two topics and the start of the data expansion. Before its last interval Nicolas asked whether the project should stop and rethink, because the methods looked data-limited. The answer depended on four results that had not yet landed (A4b, B1, B2 and the Indiana donor task). They have now landed, and they settle it. The original framing of Topic A should be retired. The reframed project is not data-limited, and it has a paper in it. Section 4 says which paper.

## 2. What round 3 established, in the order it matters

1. **The donor is the unit of every uncertainty statement, and the number of spots is nearly irrelevant.** A donor-clustered standard error is 29 to 68 times the spot i.i.d. one on CCRCC. Over 200 relabellings, a spot i.i.d. interval covers the donor-level quantity 4% of the time at nominal 90%; a donor cluster-robust interval with a $t_{G-1}$ reference covers 91%; a percentile donor bootstrap covers 71% (`b1b2_report_numbers.csv`, `b2_coverage.csv`). On the prediction-interval side, calibrating conformal intervals on held-out donors covers 0.856 and calibrating on spatial blocks inside the training slides covers 0.744, block lower in 138 of 138 cells on one shared training set, and the unit arm did that on 38% of the calibration spots (`a2_unit_intervention.csv`).
2. **A valid prediction interval for a new donor exists once there are enough donors, and the known method is conservative.** With $K = 10$ calibration donors on CCRCC, hierarchical conformal prediction is finite in every cell and covers 0.969 at 1.95 times the width of the pooled spot-level quantile; on Indiana it covers 0.988 at 1.91 times (`a4b_summary.csv`, `d4_pooled_numbers.csv`). The one-score-per-donor interval covers 0.911 at 1.43 times. The pooled quantile covers 0.864 whether 6 or 10 donors calibrate it, so its shortfall is not a small-$K$ effect.
3. **Feature-based reweighting cannot repair donor or slide shift here.** Calibration and test slides are separable at AUC 0.97 or better from the embedding and at 0.90 from eight morphology covariates alone; the weights collapse the effective calibration size to a median 2% (`A3_report_numbers.csv`). This closes the covariate-shift framing.
4. **Adaptive scores buy almost nothing at matched coverage, except in the upper tail.** CQR is 2.65 wide against 2.69 for the absolute score at 90%; the scaled score is 14.8. In the top decile of predicted values, where the absolute score covers 0.72, CQR and conformalised negative binomial reach 0.87 (`a4_report_numbers.csv`).
5. **Prediction-powered inference under donor clustering works and its gain is modest.** With donor-clustered variance, PPI intervals are 0.85 to 0.89 as wide as classical for the three encoders in the donor-weighted population and 0.98 for a permuted predictor; $\lambda$ falls from about 0.7 at six labelled donors to about 0.2 at eight or more (`b2_width_ratio.csv`, `b1_estimates.csv`). Better-predicted genes gain more (Spearman $-0.6$ to $-0.7$ between a gene's Pearson and its width ratio).
6. **The expansion delivered a second donor task and not an institution axis.** HEST-1k has no two-laboratory cell with disease held fixed (`README.md` known limitation 14). Indiana's 25 donor units, with laboratory, instrument and preservation fixed, show donor shift costing one point of coverage with a third of CCRCC's fold scatter. The kidney tumour-versus-non-tumour shift is asymmetric (0.91 one way, 0.70 the other) and perfectly decodable. Instrument generation on breast Xenium is a session-like axis (0.81 against 0.89).
7. **Two round-2 claims were corrected by the audits.** IDC's four samples are four donors, so the replicate-leak reading of IDC is withdrawn and its $+0.065$ becomes a same-laboratory, same-instrument effect; READ's $+0.090$ is the only replicate figure. And the benchmark's patches are not the HEST-1k release's patches, though no result moves with the layout (coverage by at most 0.002).

## 3. The three facts that constrain any direction

**The unit is the donor, on both sides.** Results 1, 2 and 5 are one fact seen from the confidence-interval side and the prediction-interval side. With $m$ spots per donor and between-donor share $\rho$, $n_{\text{donors}} \times m$ spots are worth about $n_{\text{donors}} / \rho$ donor-equivalents, and no number of spots inside a donor substitutes for a donor. On the conformal side the same integer appears as $K + 1 \ge 1/\alpha$. Any method the project proposes has to be stated in donors.

**Feature-side methods are closed.** Result 3 says that anything relying on overlap between calibration and test features will fail on this kind of data, because slides are identifiable from the features and even from tissue composition. Result 6 says the institution axis cannot be measured in HEST-1k. Together they retire the framing "calibrated uncertainty under cohort shift" as a paper title. The shift that exists and is measurable is donor novelty, with session and instrument novelty on top.

**The gap that is open is between validity and sharpness at small $K$.** Result 2 says the valid method exists and costs about twice the width, over-covering by seven to nine points. Nobody has closed that gap for grouped data at $K$ between 10 and 25, which is the range every biomedical study with repeated measures lives in. That is a methodological problem, it is motivated by our data, and it is not data-limited, because it is tested on simulation first and on two real tasks second.

## 4. The candidate directions

| | direction | what it would claim | what it needs | novelty | risk |
|---|---|---|---|---|---|
| D1 | Cluster-robust prediction-powered inference | PPI with the donor as cluster: variance, small-$G$ reference, the behaviour of $\lambda$ under clustering, the covariance-estimand subtlety B1 found, and the allocation of a labelling budget between donors and spots per donor | theory (mostly standard), simulation, CCRCC and Indiana as illustrations | moderate; the hierarchical case is open in the PPI literature | low |
| D2 | Sharper valid prediction sets for a new donor | a method with finite-sample validity for a new group that is less conservative than HCP at $K$ of 10 to 25, and the price of validity as a function of $K$ | theory, simulation, CCRCC and Indiana; the round-3 harness runs it unchanged | higher; competes in a crowded field | moderate to high |
| D3 | How much measured expression does predicted expression need | D1 plus a within-slide calibration arm (a small labelled sample on the test slide restores exchangeability without any cross-donor assumption) and the allocation result, framed for the people who use predicted expression downstream | benchmark data in hand; two days of harness work | moderate; the framing is new for spatial transcriptomics | low |
| D4 | A benchmark-practice note | the ten properties of HEST-bench and the split-design result | written | low as a paper, high as a service | political; David's call |

Four things are retired. The cohort-shift framing, feature reweighting, the scaled score, and any laboratory term from HEST-1k.

## 5. Recommendation

**One paper, built as D3 with D1 as its methodological core.** The claim is that inference with predicted spatial expression is valid only when the donor is treated as the unit, that a small labelled sample per donor or per slide is what makes prediction intervals and confidence intervals valid, and that the labelling budget should be spent on donors first. Round 3's coverage results are the motivation section, not the contribution; the calibration-unit rule and the donor-clustered variance are the practical recommendations; the allocation result is the statistics. This is the paper the results support today, it is not data-limited, and it transfers directly to clustered semi-supervised inference anywhere.

**D2 is the research question for round 4, with a go or no-go after a two-week scoping study.** The scoping study is simulation only, with the hierarchical model the A2c harness already writes moments for. Its question is how much of HCP's over-coverage at $K = 10$ can be recovered while keeping a finite-sample guarantee, by three routes that already have a foothold in the data. Repeated one-score-per-group subsampling with a proper aggregation (the single draw already covers 0.911 at 1.43 times); an adaptive score inside the hierarchical quantile (result 4's upper-tail gain); and a group-level quantile model with a finite-$K$ correction. If one route recovers half the gap in simulation with the guarantee intact, D2 becomes the second paper and the more ambitious one. If none does, the paper says what the price of validity is and stops there, which is still a result.

**D4 is a short note, and whether it is written is David's decision.** Its content is done and checked; it should not consume round 4.

**Venue.** For the D3 paper, a top applied statistics journal (Annals of Applied Statistics or Biometrics) fits the content better than an ML conference, because the contribution is design and inference rather than a new estimator, and the ST application is the point. AISTATS 2027 is too soon for anything but D4. If D2 produces a method, ICML or NeurIPS 2027 is the right target for it. Nicolas's preference for ML venues is met by D2, and the D3 paper is the one that makes the spring 2027 deadline with margin.

## 6. What round 4 contains, in outline

The full plan is the oversight chat's next document. In outline, four weeks.

1. The within-slide labelled-subset design on the benchmark. For $m$ in $\{25, 50, 100, 200\}$ labelled spots per test slide, coverage of within-slide conformal against the cross-donor designs, and the PPI width when the same $m$ spots are the labelled set. All data in hand; two days of harness work.
2. The allocation result. For a fixed labelling budget $B = n_L \times m$, the variance of the donor-clustered PPI estimator as a function of the split, derived and then checked on CCRCC and Indiana by masking. This is classical two-stage sampling with predictions added and is the paper's theorem.
3. The D2 scoping study, simulation only, two weeks, with the go or no-go criterion written before it runs.
4. The morphology build on the expansion samples, so Indiana joins CCRCC as a Topic B task, and the housekeeping the final report escalated (the frozen R5c file, README limitation 8, the task-definition schema, the compute notes).

Not in round 4: any further expansion download, any institution axis, any GPU work beyond what item 4 needs.

## 7. What to tell the advisors

Round 3 measured, from four directions, that the donor is the unit of every uncertainty statement about predicted expression, that the spot-level intervals in current use are off by an order of magnitude, and that the valid alternatives exist and cost about a factor of two in width. The institution axis is not measurable in HEST-1k, which is a fact about the archive and is now documented. The IDC pair from round 2 turned out to be two donors, and the correction is on the record. The first paper is on inference and design for predicted expression with the donor as the unit, targeted at an applied statistics journal for spring 2027, and a second, more ambitious method paper on sharper valid prediction sets for new groups is being scoped in round 4 with a go or no-go in two weeks.

## 8. The two decisions that are above the sessions

Whether the frozen round-2 result file `r5c_leak_summary.csv` is corrected in place or left with the README's note beside it; the oversight chat's recommendation is to leave it and add a `superseded_reading` column in a round-4 housekeeping commit, so the file's numbers stay and only their label changes. And whether the benchmark note (D4) is written and sent; that is Nicolas's and David's decision, and nothing in round 4 depends on it.
