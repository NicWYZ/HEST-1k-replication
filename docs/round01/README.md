# Round 1, faithful replication and instrumentation (12 to 16 September 2026)

Round 1 was the advisors' first assignment, a replication of the HEST-1k benchmark on Longleaf, followed by an instrumentation layer (joined prediction tables and split, probe, count, penalty and morphology diagnostics) built as input for Topics A and B. One execution track ran stages 0 to 5 from the instruction `i01/exec/HEST_replication_handoff.md` and closed with one report, `i01/exec/round1_final_stage_report.md` (revision 2, 16 September). The round had no gates and no tag; its documents were first tagged with round 2's `round2-final`. The oversight review that answered the report, `docs/round02/00_prep/HEST_replication_review.md`, opened round 2, and round 2 reran or relabelled most of the diagnostics, so `docs/round02/README.md` is where several of the findings below now stand. `docs/round10/00_prep/round10_findings_survey.md`, section 2.1 (D1, D2, D5, D8), lists the ones the paper may use.

## What the round established, as it now stands

All paths are relative to the repository root unless they start with `i01/`. Section numbers refer to `i01/exec/round1_final_stage_report.md`.

1. **The pipeline reproduces the benchmark.** Against the leaderboard snapshot of 3 April 2026, 12 of 12 encoders agree at mean $|\mathrm{diff}|$ 0.00017 (maximum 0.0017, `uni_v1`), and the 108 per-task cells at mean 0.00020, maximum 0.0155, 0 of 108 over the 0.03 threshold. ResNet50 is exact at 0.3252 and H-Optimus-1 exact at 0.4229 on its first run (`results/summary/results_encoder.csv`, `results/summary/discrepancy_table.csv`; section 3.1). The between-encoder spread on `pca_ridge` is 0.0977. The two remaining differences are explained: `raw_ridge` on ResNet50 is 0.2843 against the paper's 0.314, a numerical effect of solving a nearly singular system (D1), and `uni_v1` is 0.0017 low, not chased (D4). Caveat: the 50 target genes per task were ranked on every spot, test folds included, so every absolute number here and on the leaderboard carries that selection (section 5, item 1). Round 2 measured what the selection protocol moves (`docs/round02/README.md`, finding 6).
2. **The instrumentation layer is sound.** 130,072,250 joined prediction rows passed a row-identity check with a permutation control, aligned maximum difference 4.4e-7 against about 8.0 permuted (`results/tailored/integrity/row_identity_check.csv`; section 2.4), and every invariant in `results/tailored/integrity/stage4a_integrity.csv` passes (section 3.3). Caveat: the layer covers 11 encoders, not 12, since H-Optimus-1 has no rows in it (`docs/round02/i01/exec/round2_R0_R1_stage_report.md`, section 3.7).
3. **Pooled Pearson over a multi-patient test set is inflated by between-patient variance.** The inflation is 0.0000 for single-patient test sets and +0.1920 for nine-patient random arms (section 3.4 and section 9), so every split comparison since uses Pearson computed within each slide. Caveat: the report called the metric within-patient; it is computed per slide, and differs from a per-patient value on PRAD, COAD and READ (corrected in the report).
4. **The split decomposition of round 1 (v3) is superseded.** It gave adjacency 0.0335, a pooled "slide-level signature" (blocked minus patient) of 0.1241, and a total of 0.1575, 1.61 times the encoder spread (section 3.4; `results/tailored/splits/split_decomposition_terms.csv`). The pooled 0.1241 is withdrawn: it mixes tasks where the term means different things, contains training-set size and patient identity, and on COAD is a multi-donor holdout. Round 2's v4 decomposition reproduces v3's shared arms and replaces it, with a total of 0.1586 (`results/round2/R3_splits/r3_decomposition_terms.csv`; `docs/round02/README.md`, finding 2).
5. **The probes read slides, not institutions.** Technology (0.9940) and cohort source (0.9378) are separable, but both are confounded with task by construction. Slide identity survives a spatial-block design at 0.9805 (section 3.5; `results/tailored/site_probes/`). Caveat: the report read the slide signature as stain, scanner and section; patient, biology and scan resolution also differ between its classes, and round 2's within-patient probes found a slide and scan-session signature that is in the features and not in the expression (`docs/round02/README.md`, finding 3). The IDC "institution" probe (0.6818) is inconclusive at four slides and is not an institution contrast, since both sources are 10x Genomics data (`docs/round02/00_prep/HEST_replication_review.md`, section 5.4).
6. **The "institution shift" of 0.0419 is withdrawn.** It is the mean of four per-slide gaps (0.0022, 0.0143, 0.0518, 0.0992) that track scan resolution, within one generating laboratory (`docs/round02/i01/exec/round2_R0_R1_stage_report.md`, appendix). HEST-bench has no clean institution contrast, and full HEST-1k has none either (`docs/round10/00_prep/round10_findings_survey.md`, D7).
7. **Negative binomial without zero inflation is the observation model.** NB beats Poisson on 478 of 488 converged gene-task pairs, the minimum Fano factor is 1.638, ZINB beats NB on 14 of 474, and the median AIC difference is $-2.0019$, the penalty of one unused parameter (section 3.7; `results/tailored/counts/count_diagnostics.csv`). Sparsity follows the assay: median zero fraction 0.2856 on imaging tasks against 0.6103 on sequencing tasks. Caveats: 14 NB fits that diverged while reporting convergence are flagged `nb_diverged`; the round 2 deck and the round 10 survey give ZINB's count as 28 of 488 by the stored flags, and the 474 denominator excludes the falsely converged fits by a rule that is not a column of the file (`docs/round02/tracks/deck/.verify-exceptions-deck` at tag `record-full-2026-11`). The 50 genes were selected for high dispersion and the fits are marginal over spots, so "every gene is overdispersed" is partly selection and partly between-spot biology (review, section 5.7).
8. **The benchmark's ridge penalty is inert, and Table A13 ranks encoders by width.** At $\alpha = 100/(256 \times 50)$ the fit equals OLS to $|\mathrm{diff}| \le 2.7 \times 10^{-4}$ at both feature scales, and at raw width the mean Gram condition number is $7.56 \times 10^{14}$ (section 3.8; `results/tailored/regularization/alpha_sweep.csv`). Spearman between embedding width and score is $-0.954$ on `raw_ridge` and $+0.735$ on `pca_ridge` over 11 encoders (D2). Round 2 confirmed it with H-Optimus-1 added: $-0.950$ and $+0.727$ over 12 (`results/round2/R8_raw_heads/r8_width_correlations.csv`, which carries both cohorts with an `n_encoders` column).
9. **Gene panels are disjoint across imaging tasks.** The five imaging tasks' top-50 lists share no gene, and their panels share 14 genes over all 15 samples, which blocks any across-task transfer on this benchmark (D5). Across-task shift is not identified as a scalar (Q2).
10. **The morphology layer reproduces HEST's Figure 3e** at 0.4578 on NCBI785 against the paper's 0.47 (raw counts; `results/tailored/morphology/fig3e_gate.csv`; section 3.10), over 13,530,431 segmented nuclei. The correlation is sample-specific (three of four IDC slides give $|r| \le 0.14$), and patch geometry has to be calibrated per sample, with extents from 163 to 818 px. Caveat: round 2's later morphology build gives 0.4106 (log1p) and 0.4209 (raw) on NCBI785 with the same rank order over the four slides, and the acceptance value was restated against that build (`docs/round02/i04/exec/round2_R8_stage_report.md`, section 4.3).
11. **The ridge fit does not couple targets** (held-out-gene check, maximum prediction difference 0.0000; section 3.9). This does not test the gene-selection leakage of item 1.

## Expectations and their scores

The plan of record is the instruction `i01/exec/HEST_replication_handoff.md`. Its acceptance checks, as written, scored from the round 1 report and the review:

| Expectation | Score | Where |
|---|---|---|
| Stage 1: patch barcodes match `adata.obs_names` exactly | refuted. Patches cover 92.4% of spots overall and 57.8% on SKCM; the criterion became strict subset with exact ordering (OD1), which the review approved | report, section 6; review, section 4 |
| Stage 1: ccRCC ships 6 folds, not 24 | held (D3) | report, section 4 |
| Stage 2: every encoder and task filled, no NaN | held. 350 task results, zero NaN | report, section 2.3 |
| Stage 3: no task more than 0.03 from the leaderboard | held. 0 of 108 cells | report, section 3.1 |
| Stage 3: Figure 2a's scaling correlation near $R = 0.81$ | not tested. The report gives no reproduction of it | report, section 4 (`scaling_law_inputs.csv` not regenerated) |
| Stage 4: joined table loads with the expected row count | held. 130,072,250 rows | report, sections 2.4 and 3.3 |
| Stage 4e: Figure 3e within 0.05 of 0.47 | held. 0.4578, $|\mathrm{diff}|$ 0.0122 | report, section 3.10 |
| Stage 4f: dropping 10 of 50 genes leaves the other 40 comparable | held, at 0.0000 | report, section 3.9 |
| Stage 4b: the (i) minus (ii) gap measures leakage, the (ii) minus (iii) gap site shift | partly held. The leakage gap was measured; the site-shift arm measured scan resolution within one laboratory, not site | report, section 3.6; review, section 5.4 |
| Stage 5: STFlow reaches its reported 0.415 with UNI | not tested. Set up and not trained | report, section 6 |

## What was tried and did not work

- **The penalty-confound account of D1.** A 4-fold penalty difference was thought to explain the `raw_ridge` discrepancy; the penalty sweep showed the penalty is inert, which eliminated it (section 3.8).
- **Pooled Pearson as the split metric.** Revision 1 quoted a leakage gap of 0.3143, of which 0.1568 was the pooling artefact; it was retracted for the within-slide 0.1575 (section 9).
- **Finding the Figure 3e sample by nucleus count.** The paper's figures match no per-slide total within 2,000, so they likely count a displayed region (section 3.10).
- **Size matching to turn across-task shift into one number.** Matching cannot change which task is held out (Q2).
- **Naming terms before listing what differs between arms.** "Institution", "slide-level signature" and "stain, scanner, section" were chosen at design time and carried into the conclusions; each was wrong in the form stated (review, sections 5.2 to 5.5). The rule that came from this is in `docs/EXECUTION_RULES.md`, section 4.
- **STFlow in the project environment.** Its `scprep` pins `pandas<2.1`, incompatible with the project's pandas 2.3.3, and it needs a multi-day GPU allocation (section 6).

## What reached the advisors and has changed since

The replication was the advisors' assignment. Slides 3 and 6 of the round 2 deck, presented on 21 September, carried items 1 and 8 above, and slide 5 carried item 3. They stand, with one correction: slide 3 said 12 encoders on 3 heads, while H-Optimus-1 was never run on `raw_xgb`, so that head has eleven encoders (`docs/round02/i05/exec/round2_closeout_decisions.md`, section 1.1). The withdrawn readings of items 4 to 6 were not on the slides presented.

## Open threads

- STFlow, stage 5, was never run.
- The Figure 2a scaling-law reproduction was not reported.
- Assumption diagnostics for the ridge fits (residual structure, influence) were not assessed.

## Documents kept

| Document | What it is for |
|---|---|
| `i01/exec/HEST_replication_handoff.md` | the round's plan of record: context, staged plan, acceptance checks, pitfalls of the HEST codebase, decision boundaries |
| `i01/exec/round1_final_stage_report.md` | the final report, revision 2, with the fidelity tables, diagnostics, discrepancies D1 to D6 and what was not checked |
