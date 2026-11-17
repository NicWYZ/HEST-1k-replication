# Round 11, track `closeout`, the brief

*16 November 2026. Written by the oversight session under `../masterplan.md`. A fresh agent checked it before handover and its findings were worked in. Living on `main` while the track runs: the oversight session revises it in place, and the session that continues the track is told to check for updates.*

## 1. Where it runs, and where the plan is

- **Rules.** `docs/EXECUTION_RULES.md` as it stands at the commit the branch starts from.
- **Branch.** `round11-closeout`, from `main`. Gate tags are `round11-closeout-<gate>`.
- **The plan.** `docs/round11/closeout/round11_closeout_plan.md` on the branch, opening with a `state` block with `unit: closeout` (`docs/EXECUTION_RULES.md`, section 1). The first session writes it before any job.
- **Compute.** Every job runs on Longleaf, reached by SSH as `weiyang`, from a read-only snapshot of a recorded commit (`docs/EXECUTION_RULES.md`, sections 4 and 5). Nothing computes on the machine the session works from. The code clone on Longleaf is `/work/users/w/e/weiyang/hest_code/round11-closeout/`, and bulk outputs go under `/work/users/w/e/weiyang/hest_replication/results/round11/closeout/`. If either path exists, stop and ask Nicolas rather than reuse or remove it.
- **The working folder.** Two directories under `results/faithful/` whose names contain `::` are in the repository and may be absent from the session's folder, where the file system cannot hold them. They are round 1's and are not this track's. Never stage their absence as a deletion: stage files by path, and check the staged list before every commit.

## 2. Goal

Round 10 produced the numbers of an applied paper (`docs/round10/README.md`). Before the project is presented to Dr. Zhu and Dr. Zhang, two things remain.

**Part A.** Every prediction in the project comes from a ridge head on frozen embeddings. The headline results below will be challenged on that ground. Part A tests whether they survive a stronger predictor.

**Part B.** Round 10 left open threads (`docs/round10/README.md`, "Open threads" and "Caveats that apply across these findings"). Part B closes those a session can close.

The track ends with one table that says, for each headline result, its number, its file, and whether it stood.

## 3. The headline results

Each is quoted from the file named, read on 16 November. Unless a row says otherwise the encoder is `uni_v2`, the scale $\log(1 + y)$ and the nominal level 0.90.

| # | Result | Numbers | File |
|---|---|---|---|
| H1 | The donor is the unit of uncertainty | (a) The ratio of the donor-clustered to the i.i.d. standard error of the spot mean, median over genes, is 14.81 (LUNG_XENIUM) to 58.98 (brain Visium) by task. (b) Round 3's split conformal with the absolute score, mean over 132 task and encoder cells, covers 0.894 under design `random`, 0.859 under `slide_out` and 0.802 under `donor` (audited donors); on CCRCC, 0.881 and 0.864 under `random` and `donor` | `results/round10/final_runs/F2/report_tables/r10b_d9_by_task.csv`; `docs/round03/i01/exec/round3_A1_stage_report.md`, the coverage tables |
| H2 | Across centers, prediction and calibration both fail | On kidney Visium the median Pearson is 0.412 to 0.483 held out by donor and 0.004 to 0.123 held out by center, across three encoders. Donor-level HCP pooled across centers, at nominal 0.80, covers 0.655 on center S0006 against 0.906 at the median center, and HCP over centers covers 1.0 at the median | `results/round10/final_runs/F1/aggregate/f1_predictions.csv`; `results/round10/final_runs/F3/institution/production/inst_fr8.csv` |
| H3 | What predictions buy for cohort-level inference follows donor-level accuracy, not spot-level accuracy, and is modest on most Visium tasks | For $\theta_3$ at 8 labelled donors, the median width ratio of `fix1` to `classical` and the median donor-level $R^2_c$ are 0.878 and 0.439 (CCRCC), 0.957 and 0.139 (INDIANA_KIDNEY), 0.937 and 0.199 (kidney Visium), 0.669 and 0.626 (bowel Visium), 0.585 and 0.714 (LUNG_XENIUM). The leave-one-donor-out median $R^2$ of the donor mean against the leave-one-out constant is 0.021 on CCRCC and 0.382 on kidney Visium | `results/round10/final_runs/F2/report_tables/r10_buy_uni_v2_primary_n8.csv`; `results/round10/final_runs/F1/diagnostics/d12_lodo_r2_medians__r3_CCRCC_uni_v2.csv`; `results/round10/final_runs/F1/aggregate/f1_d12.csv` |
| H4 | HEST-1k's patient labels are wrong in both directions, and split design costs more than encoder choice | no number is rerun; the files are re-read | `results/round2/R5b_audit/donor_audit.csv`; `results/round2/R3_splits/r3_decomposition_terms.csv` |
| H5 | Published clustered-PPI intervals under-cover at four labelled clusters | Kluger et al.'s cluster bootstrap covers 0.7145, the median over all cells of the limits table. Broska and Howes's interval covers 0.699, and 0.875 with the small-sample correction, medians over the HEST and ACS cells | `results/round10/final_runs/F2/report_tables/r07_limits_ranges.csv`; `results/round10/final_runs/F4/paper_numbers.csv`, keys `S6.bh.n4`, `S6.bh_t.n4` |

**Two baselines for the donor-mean $R^2$.** Round 9's values (`results/round9/between/between_head_medians.csv`, $-0.066$ on CCRCC) are against the full-sample mean, under which a constant scores $-0.089$. Round 10's are against the leave-one-out constant. Every $R^2$ of a donor mean in this track names its baseline, and the leave-one-out constant is the primary one.

**Notes on the table, from gate G2.** `slide_out`'s mean is over 36 cells, not 132. The 132 cells count IDC twice, under its shipped and its audited labels; with IDC once, `donor` is 0.800 and `random` 0.895. H4's encoder spread is in `results/round3/A1_coverage/a1_vs_benchmark_pearson.csv`. H5's Broska and Howes values come from `results/round10/final_runs/F2/report_tables/r02_regimeA_grid_ranges.csv`. The recomputed values are in `round11_closeout_G2_report.md`, section 6.3, on the branch.

The definitions of every quantity (the estimands, `fix1`, `classical`, HCP, the designs, the scales) are in `docs/round10/round10_methods_note.md`, `docs/round10/i05/final-runs/round10_final_runs_report.md`, `docs/round10/tracks/final-runs/round10_final_runs_plan.md` and `docs/round03/i01/exec/round3_A1_stage_report.md`. Kidney Visium contains the samples of CCRCC and INDIANA_KIDNEY, so those three tasks are not independent.

## 4. Part A, a stronger predictor

**The question.** Do H1(b), H2 and H3 change when the ridge head on frozen embeddings is replaced by the strongest predictor the project can fairly build?

**Literature first.** Before choosing, search for what published benchmarks of histology-to-expression prediction find to be the strongest approaches, with the search logged in the results directory, and for any published report of donor-level (not spot-level) accuracy of such predictors. Round 9 found that a head fitted on donor means did worse than the pooled head (`docs/round09/README.md`, "What was tried and did not work"), so do not repeat that without a reason the search supplies.

**What counts as stronger.** The session chooses, and says why, among directions such as these, alone or combined:
- a stronger encoder among those whose embeddings are already on Longleaf;
- a higher-capacity head on frozen embeddings (a tuned ridge without the PCA step, a multilayer perceptron, gradient boosting);
- more training donors, from the federated corpus's other donors of the same organ and platform;
- spatial context, from the embeddings of neighbouring spots.

An inventory of the embeddings, prediction files and task definitions on Longleaf comes first, with `whose()` verdicts recorded.

**No download.** Any download of data, code or model weights is not the session's decision. If the search concludes that no fair stronger predictor can be built from what is on Longleaf, stop at gate G1 with the proposal, what it needs and what it would cost. Otherwise there is no gate before the runs.

**Standards.**
1. **Anchors first.** Before any new predictor, the pipeline refits round 10's `uni_v2` ridge head and reproduces these cells, from the prediction files and task definitions on Longleaf:
   - kidney Visium, median Pearson held out by donor 0.471 and by center 0.123 (`f1_predictions.csv`), within 0.005;
   - CCRCC, the leave-one-donor-out median $R^2$ of the donor mean against the leave-one-out constant, 0.021, within 0.005;
   - CCRCC, $\theta_3$ at 8 labelled donors, the median width ratio 0.878 and the median coverage of `fix1` 0.8965 (`paper_numbers.csv`, key `B8.CCRCC.fix1`), within the Monte Carlo error of round 10's design simulation, which the report states. At gate G2 the width ratio came to 0.8949 on the corpus's embeddings while a control on round 3's own file reproduced 0.878 exactly, so the difference is the inputs. The corpus route is accepted, and every comparison on CCRCC is made against the track's own ridge arm on the corpus's embeddings.
2. **The primary predictor is named before its results are seen.** The plan designates one predictor as primary, with its tuning rule, before any held-out result of a new predictor is read. Every predictor that is run is reported. The masterplan's predictions are scored on the primary one.
3. **No leakage.** Every prediction is held out by donor, and by center for H2. Every tuning choice (hyperparameters, early stopping, model selection, any normalisation fitted on data) is made inside the training fold, with inner splits grouped by donor, and by center for H2. When donors are added from the corpus, they are matched to the task's donors across identifier schemes first (center S0006 of kidney Visium is CCRCC's donors), a held-out donor never appears in training under another identifier, and a held-out center contributes no donor to training. The gene lists are round 10's.
4. **One change at a time.** For any predictor that changes the inputs (more donors, spatial context, another encoder), a ridge arm on the same inputs and folds is run beside it, so that the head and the inputs are separated.
5. **Stronger must be shown.** The report gives the donor-held-out median spot-level Pearson of each new predictor beside round 10's ridge on the same task, encoder and scale, with its spread over folds. A predictor that does not meet the masterplan's P11.1 is reported as not stronger, and P11.2 to P11.4 are then scored "not tested".
6. **The same quantities.** For each new predictor, on CCRCC, INDIANA_KIDNEY, LUNG_XENIUM, kidney Visium and bowel Visium at least, and on the other corpus tasks where the cost allows, on both scales:
   - the leave-one-donor-out $R^2$ of the donor mean against the leave-one-out constant, and the donor-level $R^2_c$;
   - the coverage of `fix1` and `classical` and the width ratio of `fix1` to `classical`, for $\theta_3$ and $\mu$, at 4, 8 and 16 labelled donors, with round 10's design simulation;
   - held out by center on kidney Visium and brain Visium, the median Pearson, and at nominal 0.80 the coverage of donor-level HCP pooled across centers and of HCP over centers, as `inst_fr8.csv` was produced;
   - split conformal coverage with the absolute score under round 3's designs `random`, `slide_out` and `donor`, and under a center design where the task has centers.
7. **The grid before the headline.** Each conclusion is checked in every task, scale and estimand cell it claims, and a difference is called a change only beside its fold-to-fold or Monte Carlo spread.
8. **Pretraining overlap.** The report says what each encoder's published description states about pretraining on these cohorts, or that it states nothing.

**After gate G2.** The primary predictor did not meet P11.1, so P11.2 to P11.4 are scored "not tested". The quantities of standard 6 are still run for the primary predictor and for the three-encoder arm with context, the latter labelled as chosen after its results were seen, and the final report gives them beside the formal verdicts as supplementary evidence.

**Predictions.** The masterplan's P11.1 to P11.4 are the oversight session's. The session writes its own, with numbers, into its plan before the first run of each stage.

## 5. Part B, the open threads of round 10

In this order, which puts first what the headline results rest on.

1. **The headline numbers, recomputed.** A fresh sub-agent recomputes every number in the table of section 3 independently of the code that produced it, from the Longleaf outputs where the committed file is an aggregate. Round 10 checked 41 of the numbers table's 443 values against reports and the rest only by their selectors (`docs/round10/i05/final-runs/round10_final_runs_report.md`, section 8). The values outside section 3 stay as round 10 left them, and the report says so.
2. **H1(b) on the final footing.** Round 3's conformal designs differ in how the test spots are held out from the spots that train and calibrate, and round 10's prediction files are held out by donor or by center only. Refit the `uni_v2` ridge head under `random`, `slide_out`, `donor` and, where the task has centers, a center design, on CCRCC, kidney Visium, bowel Visium and LUNG_XENIUM, and report split conformal coverage with the absolute score. The anchor is round 3's CCRCC row.
3. **S0006.** On kidney Visium, center S0006 has the lowest pooled HCP coverage, and its median absolute residual is the largest in 5 of 6 encoder and scale cells but not under `uni_v2` on the normalised scale (`results/round10/final_runs/F4/aggregate/f4_s0006_summary.json`). From the existing prediction files and with no new fit, say what makes its coverage low in that cell, or record that one look did not explain it.
4. **Equal allocation for regime B on ACS by state,** which round 10's allocation reading says removes regime B's disadvantage, was not run. Run it beside the proportional allocation, with `fix1`, $\theta_3$ and the cost ratio 10.
5. **The allocation factor's assumption.** Measure whether within-cluster variances are equal across clusters on ACS by state and the HEST tasks, which the factor of F4-3b assumes.
6. **Stored columns.** The share of genes where the pooled head beats a constant (D12) and round 9's E1 box numbers were not found in a stored column (`docs/round10/i05/final-runs/round10_final_runs_report.md`, section 7, item 4). Compute and store them, or say that the paper cannot quote them.
7. **The job ledger.** List the round 10 jobs that wrote no provenance file, as far as `sacct` still shows them.

Not in this track: the paper full texts saved outside the repository (they wait on Nicolas), and the decisions D5, O5, Q1 and Q3.

## 6. Gates and the final report

- **Who replies.** For this round the oversight session reviews each gate and relays the reply, under `../masterplan.md`, "Who decides the gates". A substantive issue still goes to Nicolas, so the report's section 7 marks which of its items it considers substantive.
- **G1** only if section 4's no-download rule stops the work.
- Other intermediate gates are the session's to set, at significant results or roadblocks.
- **The final gate** is `G-final`, tag `round11-closeout-G-final`, with one pull request into `main`. The final report is `docs/round11/closeout/round11_closeout_report.md`. It opens with the headline table, one row per result H1 to H5: the number as recomputed (for H4, that the files were re-read), its file, the value under the primary predictor where Part A applies, and a verdict. The verdict is "stood" where the masterplan's matching prediction held (P11.4 for H1(b), P11.3 for H2, P11.2 for H3), "changed" with the new number where it was refuted, and "not tested" otherwise. The report then follows `docs/EXECUTION_RULES.md`, section 7, and states each prediction in full as written before its run.

## 7. Paths the track writes to

- `docs/round11/closeout/` for the plan, the gate reports, the literature log and any methods note.
- `results/round11/closeout/` for aggregates, the job ledger, `code_deliveries.csv` and `provenance_index.csv`. Only aggregates enter the repository.
- `code/scripts/round11_closeout_*`.
- `.verify-exceptions-round11-closeout`.

## 8. Not the session's decision

The framing, venue or authorship of the paper, and which results it keeps. Any download. Contact with anyone outside the project. A claim of novelty. Changes to `main`, to earlier rounds' files or to another project's corpus, which is read only. If a result of this track changes a headline, report it at the gate and do not rewrite earlier rounds' documents.
