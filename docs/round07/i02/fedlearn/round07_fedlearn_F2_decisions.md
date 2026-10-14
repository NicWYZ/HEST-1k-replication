# Round 7, the federated learning track, decisions at the F2 gate

13 October 2026. Written by the oversight chat for the execution session of the federated learning track, after reviewing the F2 report (`docs/round07/i01/fedlearn/round07_fedlearn_F2_report.md`, pull request #28, tag `round7-fedlearn-F2`). This memo opens interval i02. Commit it unchanged at this path on your branch.

**What was read and checked.** The whole report, the literature review (`docs/round07/tracks/fedlearn/round07_fedlearn_literature_review.md`), the search log, the evidence table, the citation audit and its fixes, and the inventory's outputs. The headline counts were recomputed from the files. `results/round7/fedlearn/F1_search/search_log.csv` has 695 rows and 219 query identifiers. `evidence_table.csv` has 406 papers, 91 marked as cited, 72 of them read at full text and 19 at the abstract. `results/round7/fedlearn/F2_audit/citation_audit.csv` has 91 rows with claims judged fully supported in 69, partly in 20 and not in 2. `results/round7/fedlearn/F2_inventory/inventory_summary.json` records 205 samples on disk, 142 with embeddings, 72 benchmark samples and no header errors. The faithful anchor of 0.264 for `pca_ridge` on `CCRCC` with `uni_v2` is in `results/summary/discrepancy_table.csv`. The committed tasks `KIDNEY_POP54` (54 samples) and `BREAST_XENIUM` (18 samples) exist under `results/round3/D4_expansion/task_defs/`.

**The gate rule, in the wording Nicolas approved.** Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. Contact with anyone outside the project is never the session's decision.

## 1. Acceptance

The F2 gate is accepted. All six exit items are met, with the limits the report states. The review answers every question with a grade, keeps the novelty statement to the search log, and corrects the oversight chat's own starting points where they were wrong (escalation 3). The decision to stop reader R1 rather than push after the gate was right. Predictions F.1 to F.4 held and F.5 partly held, as scored.

## 2. Instruction revisions you have not fetched

The instruction on `main` gained a revision on the evening of 13 October, after your session started from `3c328ccc`. Nicolas has not told you to fetch it, so its content is given here in full, and it applies from now. Round 7's inference track runs at the same time on branch `round7-ppi`, with areas `results/round7/ppi/`, `code/scripts/round7_ppi_*.py`, `docs/round07/**/round07_ppi_*.md` and `.verify-exceptions-round7-ppi`, and it uses the same Slurm accounts. So the rule on queued jobs in section 4 of the instruction becomes this. A pending job of this track's own may be switched between `rc_htzhu_pi` and `rc_tengfei_pi`. Only the lead cancels a Slurm job, and only after confirming with `squeue -u weiyang` and the track's job ledger, which from now is `results/round7/fedlearn/r7fl_slurm_jobs.csv`, that the job is this track's own. A sub-agent never runs `scancel`, and you never write in the inference track's areas. Transcribe this into the plan as an amendment, and copy the ledger of the plan into that file before the first job of i02.

## 3. What the review establishes for the paper

1. **The premise is not yet supported.** No study measures within-slide accuracy against the number of training patients or centers for a head on frozen embeddings, and the indirect evidence points more to the representation and the weak within-slide signal than to a shortage of data (review, section 2, grade weak). V1 is therefore the experiment that decides whether the paper's argument can be "more centers give more accuracy", or must become "more centers give accuracy that transfers, at a cost that is small".
2. **The estimator is not new.** Fitting a ridge or closed-form head from summed statistics is established for linear and mixed models and has been used on frozen features for classification (review, section 12). Any novelty rests on the application to expression and on what it shows about center-level error.
3. **The gap that is open** is centers that measure different gene panels (none found, F.4), privacy cost for high-dimensional embedding statistics (none found), and inference for a federated head whose error has a center-level component (none found). The first two are cheap to probe, so V3 and V4 are added below.
4. **Routes 3 and 4 are out for a first paper,** and C4 is not supported as privacy-preserving. These verdicts are accepted. The paper's method is C1, with C3 as the most interesting extension to propose for later.

## 4. Answers to the escalations and open questions

1. **The lab field.** Accepted. F3.00 below recomputes the grouping first.
2. **PPML-Omics' versions.** Accepted. Quote the published table, as the review does.
3. **The starting points that differed.** Accepted, and thank you. Grammenos et al. is now recorded as streaming and approximate, and the exact basis comes from summed centred second moments, which the review notes no paper states with a head.
4. **Unreachable sources.** Accepted. No further action.
5. **Reader R1.** Read in full during i02 the papers it left that the review cites at the abstract level and that bear on the paper, which are P006, P183, P267, P287 and P321, from open full texts only. A sub-agent's request for network access to a host the brief did not name is answered no. Record it and continue. P293 and P401 may stay at the abstract level.
6. **Screening shortfalls.** Accepted as declared. The closing report repeats them in its limits.
7. **Read level.** Accepted as defined.
8. **The checker.** Accepted. The oversight chat will fix the matching of comma-grouped integers in free-text cells through its own pull request. Keep your exceptions file as it is.

**Open question 1, the provenance index script.** It reads git objects and provenance files and no data, so it is bookkeeping, not a local run. Keep running it in the Mac clone.

**Open question 2, a center as a study.** Yes. In V2 a center is a source, meaning a lab or a study, whichever F3.00 can resolve. Every table names which, and the report says plainly that lab, study and disease are mixed in every source contrast.

## 5. Interval i02, the experiments as fixed

Everything runs on Longleaf from delivered snapshots, with the exact head of instruction section 2.3 (float64 eigendecomposition and Cholesky solve) unless stated, 256 principal components as the benchmark's head uses, and the ridge penalty of the faithful head. Outputs go where the instruction's F3 says, with `F3_00_grouping/`, `F3_V3/` and `F3_V4/` added. The time caps are two days for F3.00 to V2 together and one day for V3 and V4 together.

**F3.00, the corrected grouping.** As the report proposes. Merge vendor spellings, keep unresolved studies as their own source, add a source label and a study label from the committed task definitions, and rewrite `centers_by_group.csv` as `results/round7/fedlearn/F3_00_grouping/sources_by_group.csv`.

**F3.0, the anchors.** As the report proposes. The faithful `pca_ridge` refit for `uni_v2` on `CCRCC` on round 1's split matches 0.264 within 0.001, and the exact head from per-center sums matches the exact pooled head's predictions to a relative difference below $10^{-8}$. A failure of either after one fix is a stop.

**V1, the learning curve.** As the report proposes, on `CCRCC` with `INT4` and `INT24` merged, `INDIANA_KIDNEY` and `LUNG_XENIUM`, with the three encoders, a fixed quarter of donors held out (at least three), training donors on a doubling grid from 1 to the maximum and 20 draws each. Report the within-slide metric and the pooled Pearson over test spots with the spread over draws. Add one curve per task with the faithful head at the largest two sizes, so that the exact and faithful heads can be compared where both run.

**V2, the simulated federation.** As the report proposes, with these settings.
- (a) Sources. Kidney Visium through `KIDNEY_POP54`, with the Sorbonne cohort against the kidney atlas, on the 50 genes of the `CCRCC` task (all are measured on Visium). Breast Xenium through `BREAST_XENIUM`, with 10x against the second study, on the genes both sources measure, the top 50 by variance computed on the training sources only. Lung Xenium is reported and not scored.
- (b) Pseudo-centers. $K = 3$ random partitions of donors in `CCRCC`, `INDIANA_KIDNEY` and `LUNG_XENIUM`, with 10 partitions per task.
- (c) Center-centred embeddings, as the report proposes. A left-out center is centred on its own mean embedding, which uses no label. Say so in the report, since it is a transductive step a deployed federation would also take.
- Arms. A local head, the federated head, the federated head with a center intercept (a left-out center gets the spot-weighted mean of the others' intercepts), and in (c) the centred head.
- Scoring. Leave one center out, and held-out donors within each center, with the within-slide metric and the pooled Pearson.

**V3, the cost of differential privacy, added.** Each center releases its sums once with Gaussian noise calibrated after AdaSSP [P339], with embedding rows clipped to a fixed norm chosen before the run from a training center only, at $\varepsilon \in \{0.5, 1, 2, 5, 10\}$ per center and $\delta = 10^{-5}$, on V2(b) for `CCRCC` with `uni_v2`. Report the within-slide metric against the non-private federated head, with 20 noise draws per budget. Write the calibration into the plan before the run.

**V4, partial gene overlap, added.** On V2(b), each center measures a random half of the 50 target genes, drawn independently per center with a fixed seed. Each gene's head is fitted from the centers that measure it, and the principal-component basis from all centers, since it uses no expression. Compare with the full-overlap fit on the same partitions, with 10 masks.

**F4, the closing report,** as the instruction says, with the review updated for the papers read in i02.

## 6. Predictions for interval i02

The oversight chat's F.6 to F.10 stand as written in the instruction. Score your own predictions of report section 9 beside them. Two more of the oversight chat's, written before any run.

- **F.11** In V3, at $\varepsilon = 10$ the within-slide metric is within 0.01 of the non-private federated head, and at $\varepsilon = 1$ it is more than 0.02 below it.
- **F.12** In V4, fitting each gene from half the centers lowers the within-slide metric by less than 0.01 against full overlap, on every task.

## 7. What the session does next

1. Commit this memo unchanged at `docs/round07/i02/fedlearn/round07_fedlearn_F2_decisions.md` on your branch.
2. Transcribe sections 2, 4 and 5 into the plan as amendments, with the predictions of section 6.
3. Run F3.00, F3.0, V1, V2, V3 and V4, read the five papers of escalation 5, and write the closing report at `docs/round07/i02/fedlearn/round07_fedlearn_final_report.md`. Then commit, tag `round7-fedlearn-final`, push, open the pull request, and stop.
