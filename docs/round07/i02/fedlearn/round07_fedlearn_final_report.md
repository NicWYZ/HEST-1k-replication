# Round 7, the federated learning track, closing report (F4)

Execution session `8a6be84e-6b5d-4289-aaaf-100d3c5b6c05`, branch `round7-fedlearn`, 14 October 2026. This report closes interval i02 and the track. It follows section 10 of the instruction (`docs/round07/i01/fedlearn/round07_fedlearn_track.md`), the F2 decision memo (`docs/round07/i02/fedlearn/round07_fedlearn_F2_decisions.md`) and the plan's amendments A1 to A11 (`docs/round07/tracks/fedlearn/round07_fedlearn_plan.md`). Results directories below are under `results/round7/fedlearn/`.

## 1. Stage and status

F3 (F3.00, F3.0, V1, V2, V3, V4) and F4 are complete. Both F3.0 anchors pass. Every experiment the memo fixed has run in full on all of its tasks and encoders. F4 is the end-of-track gate. The branch, the tag `round7-fedlearn-final` and one pull request go to GitHub together, and the session stops.

Time caps (A11). F3.00 to V2 ran from 02:12 to 07:05 UTC on 14 October, against a cap of two days. V3 and V4 ran inside the same window, against a cap of one day.

## 2. What was run

**Code deliveries.** Four bundles were applied by `git merge --ff-only` in `hest_code/round7-fedlearn`, each with a read-only snapshot (`results/round7/fedlearn/code_deliveries.csv`, logs in `results/round7/fedlearn/deliveries/`).

| delivery | Slurm job | commit delivered | what it added |
|---|---|---|---|
| 2 | 4820166 | `fb62f73e` | the i02 scripts |
| 3 | 4824673 | `89d698a6` | the loader fix of section 7, item 1 |
| 4 | 4839667 | `30dffb3d` | V2's all-centers scoring of section 7, item 2 |

**Scripts and md5s** (at `30dffb3d`, the same at `89d698a6` except `round7_fedlearn_v2.py`, whose md5 there is `885bf63339074729fed7066d2434fbd0`).

| script | md5 |
|---|---|
| `code/scripts/round7_fedlearn_common.py` | `69a4cdb299564fc079b683f0a3219dbc` |
| `code/scripts/round7_fedlearn_head.py` | `b5bd975c4f1745d27e7ebb56ead75392` |
| `code/scripts/round7_fedlearn_design.py` | `88a2d4c8dc0ed8c75337d29435ae64a1` |
| `code/scripts/round7_fedlearn_f300_grouping.py` | `aacf1aea20e2b33fdd965c6fc37cb3d7` |
| `code/scripts/round7_fedlearn_f30_anchor.py` | `98f6ba21e67e74a010a6d25cc9110add` |
| `code/scripts/round7_fedlearn_v1.py` | `4bede77b0a8e22d9b85146f162e534dc` |
| `code/scripts/round7_fedlearn_v2.py` | `5136d78036162e0b60427cfb6af24dcf` |
| `code/scripts/round7_fedlearn_v3.py` | `0d9fe879ba8471c8a876b634a7e08368` |
| `code/scripts/round7_fedlearn_v4.py` | `ec186e1e5deb37e47031fd3cdbb64f77` |
| `code/scripts/round2_r2_gene_check.py` (HEST's `get_k_genes`) | `e267b1e6038daa893647202dd47ffb04` |

F3.00 and the first F3.0 attempt ran from `fb62f73e`, where `round7_fedlearn_head.py` had md5 `edcfe81b0bcbcfd72b477849299ee6ae` and `round7_fedlearn_f30_anchor.py` had `5df5fe81508171ab51a870e2dd8cb09e`.

**Jobs.** All ran on partition `spill` under `rc_htzhu_pi`. Seven were submitted under `rc_tengfei_pi` and moved while pending, and the twelve V jobs had memory lowered from 64 GB to 32 GB and the time limit from 8 h to 4 h while pending, after F3.0 peaked at 18.6 GiB (`results/round7/fedlearn/r7fl_slurm_jobs.csv`, `results/round7/fedlearn/job_accounting.csv`). No job waited four hours. Wall time and peak memory are from `sacct`. Memory is `MaxRSS` of the batch step, which `sacct` reports in KiB, converted to GiB. Every value is in `results/round7/fedlearn/job_accounting.csv` in KiB, so the GiB figures are derived.

| stage | Slurm jobs | wall time | peak memory |
|---|---|---|---|
| F3.00 | 4824298 | 3 s | 0.13 GiB |
| F3.0 attempt 1 (failed) | 4824300 | 7 min 57 s | 18.6 GiB |
| F3.0 attempt 2 | 4824765 | 7 min 56 s | 18.6 GiB |
| V1, three tasks | 4825169, 4825170, 4825172 | 5 to 40 min | 1.8 to 6.8 GiB |
| V2 run 1, five tasks | 4825173 to 4825175, 4825188, 4825201 | 6 to 14 min | 1.8 to 10.7 GiB |
| V3 | 4825203 | 27 min 42 s | 6.3 GiB |
| V4, three tasks | 4825204, 4825205, 4825208 | 35 min to 1 h 5 min | 2.0 to 6.8 GiB |
| V2 run 2, five tasks | 4839784, 4839791, 4839835 to 4839837 | 7 to 57 min | 1.7 to 10.6 GiB |

**Sub-agents in i02.** Reader 4 (frame `64e490e6-a211-4130-a1ca-63569be57c5f`) read P006, P183, P267, P287 and P321 in full from PMC, Europe PMC and arXiv, as memo section 4 item 5 asked. Its brief allowed those hosts and the web search only. It declared no deviation and requested no other host (`results/round7/fedlearn/F1_search/reading/R4/reading_notes.csv`). At Nicolas's request, a link-finding sub-agent (frame `eeade669-d2de-4732-90f4-34c658d0432e`) looked for free versions of requested papers 1, 3 and 5. It returned links only, wrote no file and requested no host. It could not use Unpaywall because no contact email was available (`results/round7/fedlearn/F1_search/paper_requests.md`). Nicolas then obtained paper 1. Papers 2 and 4 had already arrived. The lead read papers 1, 2 and 4 (`results/round7/fedlearn/F1_search/reading/R5_requested/reading_notes.csv`).

**Sources reached.** As at F2, plus the three supplied PDFs. No new host was requested.

## 3. Acceptance checks and exit items

**Exit item 1, both F3.0 anchors pass** (`results/round7/fedlearn/F3_anchor_attempt2/f30_summary.json`).
- *Faithful anchor.* HEST-bench's own `train_test_reg` on round 1's six `CCRCC` splits with `uni_v2` gives a mean `pearson_mean` of 0.263995, against round 1's 0.264 (`results/faithful/pca_ridge/uni_v2/CCRCC/results_kfold.json`). The difference is $5.1 \times 10^{-6}$ against a tolerance of $10^{-3}$. Each split matches round 1's stored value to its four decimals (`results/round7/fedlearn/F3_anchor_attempt2/f30_faithful.csv`). The session's scikit-learn copy of the faithful head differs from HEST's by at most $8.5 \times 10^{-5}$ in `pearson_mean` on any split. This is close agreement, not the identical predictions that A5 asked for (section 7, item 4).
- *Exact anchor.* The exact head fitted from per-center sums and from pooled spot arrays agree to a largest relative difference of $7.6 \times 10^{-15}$ over five center splits, against $10^{-8}$ (`results/round7/fedlearn/F3_anchor_attempt2/f30_exact.csv`). The splits are both V2(a) source splits and the first V2(b) partition of each task, on 19,083 to 134,333 spots.
- The first attempt (`results/round7/fedlearn/F3_anchor/`) stopped with an error before the exact check was evaluated (section 7, item 1). One fix was made, and the second attempt passed both checks, so no stop condition applies.

**Exit item 2, every experiment the memo fixed has run in full.** V1: 3 tasks × 3 encoders, every size, 20 draws (one at the full pool), with the faithful head at the two largest sizes (`results/round7/fedlearn/V1/CCRCC/v1_draws.csv`, `results/round7/fedlearn/V1/INDIANA_KIDNEY/v1_draws.csv`, `results/round7/fedlearn/V1/LUNG_XENIUM/v1_draws.csv`). V2: (a) 2 tasks × 3 encoders × 10 hold-out draws and leave one center out, and (b) 3 tasks × 3 encoders × 10 partitions, both schemes (`results/round7/fedlearn/V2_run2/CCRCC/v2_rows.csv`, `results/round7/fedlearn/V2_run2/INDIANA_KIDNEY/v2_rows.csv`, `results/round7/fedlearn/V2_run2/LUNG_XENIUM/v2_rows.csv`, `results/round7/fedlearn/V2_run2/KIDNEY_POP54/v2_rows.csv`, `results/round7/fedlearn/V2_run2/BREAST_XENIUM/v2_rows.csv`). V3: 10 partitions × 5 budgets × 20 noise draws, with no failed Cholesky factorisation (`results/round7/fedlearn/V3/v3_summary.csv`). V4: 3 tasks × 3 encoders × 10 partitions × 10 masks, both schemes (`results/round7/fedlearn/V4/CCRCC/v4_rows.csv`, `results/round7/fedlearn/V4/INDIANA_KIDNEY/v4_rows.csv`, `results/round7/fedlearn/V4/LUNG_XENIUM/v4_rows.csv`). The output directories are named `results/round7/fedlearn/V1/` to `results/round7/fedlearn/V4/` rather than the instruction's `results/round7/fedlearn/F3_V1/` to `results/round7/fedlearn/F3_V3/` (section 7, item 6).

**Exit item 3, every prediction scored.** Section 5.

**Exit item 4, numbers read back, and the sweep.** Every number below was read from the file named beside it. The numeric-claim sweep result is in section 8.

**Exit item 5, the provenance index.** `results/round7/fedlearn/provenance_index.csv` covers all 20 jobs that wrote a `PROVENANCE.txt` (97 script records). Every recorded commit is an ancestor of the gate commit, and every recorded md5 matches the script at its commit. The failed first F3.0 attempt wrote no `PROVENANCE.txt`. Every output directory carries this session's frame id in `_provenance.json`.

**F3.00, the corrected grouping** (`results/round7/fedlearn/F3_00_grouping/sources_by_group.csv`, `f300_summary.json`). With the two 10x spellings and the two TGen spellings merged, 3 of 18 organ and technology groups have two or more sources with expression and embeddings. Breast Xenium has 10x Genomics (lab, 7 samples) and the unresolved bioRxiv study (study, 11 samples). Kidney Visium has five labs, of which the Sorbonne (24 samples), Washington University (23) and Indiana University (7) carry donor units. Lung Xenium has TGen (22 samples) and 10x Genomics (2). This agrees with F2's count after the merge.

## 4. The variables that differ between the arms of each comparison

- **V1, one size against another.** The number of training donors and which donors they are. The test donors, the genes, the encoder and the head are fixed within a curve. Exact against faithful head: the basis (float64 eigendecomposition of the pooled standardised cross-products against scikit-learn's PCA in float32 with `random_state=1`), the ridge solver (Cholesky against `lsqr` with at most 1,000 iterations) and the precision of the expression values.
- **V2, local against federated.** The training donors, and therefore the centers they come from and the number of training spots. The test spots, the genes and the encoder are fixed. In V2(a), lab, study, disease and protocol all differ between the two sources, so a gain or loss from adding the other source cannot be assigned to any one of them.
- **V2, federated against intercept.** The slopes come from within-center centred sums in the intercept arm and from pooled centred sums in the federated arm, and the intercept arm adds the center's own intercept $\alpha_k$. The basis is the same.
- **V2, federated against centred.** The centring of each center's embeddings before the basis and the ridge are fitted, and at prediction the subtraction of the test center's own mean embedding over all of its spots. That subtraction uses no labels but uses the test spots, which is a transductive step.
- **V2, within against leave one center out.** The test spots (a quarter of a center's donors against all of a center's donors) and the training set (all centers' remaining donors against the other centers' donors only). Their difference is not a pure effect of leaving a center out.
- **V3, private against non-private.** Spot clipping, the Gaussian noise on every released sum, and the larger ridge penalty. Clipped against unclipped non-private: clipping only.
- **V4, masked against full overlap.** Which centers' labels fit each gene, and with them each gene's centring and intercept. The basis, the penalty, the test spots and the scored genes are the same.

## 5. Predictions against outcomes

The metric is the within-slide Pearson correlation unless stated. Each prediction's own text is in the instruction section 9, memo section 6 and plan A10.

| prediction | source | outcome | score |
|---|---|---|---|
| F.6, the rise from 1 to 4 donors exceeds the rise from 4 to the largest size, in every task and encoder | oversight | 9 of 9 cells. The rise from 1 to 4 is 0.041 to 0.131 and the rise from 4 to the largest size is 0.021 to 0.029 (`results/round7/fedlearn/V1/CCRCC/v1_summary.csv`, `results/round7/fedlearn/V1/INDIANA_KIDNEY/v1_summary.csv`, `results/round7/fedlearn/V1/LUNG_XENIUM/v1_summary.csv`) | held |
| F.6, in at least 7 of the 9 cells | session | 9 of 9 | held |
| F.7, `CCRCC` with `uni_v2` at the largest size (17 donors) within 0.02 of its value at half that size | oversight and session | 0.1472 at 17 donors against 0.1370 at 8, a difference of 0.0102 (`results/round7/fedlearn/V1/CCRCC/v1_summary.csv`) | held |
| F.8, leave one lab out below held-out donors within the lab, in every group and encoder where V2(a) runs | oversight | in all 12 cells of 2 tasks × 3 encoders × 2 centers, by 0.052 to 0.173 (`results/round7/fedlearn/V2_run2/CCRCC/v2_rows.csv`, `results/round7/fedlearn/V2_run2/INDIANA_KIDNEY/v2_rows.csv`, `results/round7/fedlearn/V2_run2/LUNG_XENIUM/v2_rows.csv`, `results/round7/fedlearn/V2_run2/KIDNEY_POP54/v2_rows.csv`, `results/round7/fedlearn/V2_run2/BREAST_XENIUM/v2_rows.csv`) | held |
| F.8, held in kidney, not predicted for breast | session | held in kidney, and also in breast | held for kidney, refuted for breast |
| F.9, adding another lab's slides changes a lab's held-out accuracy by less than 0.02 in either direction | oversight | in 8 of 12 cells. The kidney atlas loses 0.021 to 0.035 in all three encoders, and 10x breast gains 0.022 with `resnet50` | refuted |
| F.9, less than 0.02 in breast, more than 0.02 in kidney | session | breast in 5 of 6 cells. Kidney exceeds 0.02 for the atlas (3 of 3) but not for the Sorbonne cohort (changes of 0.0004 to 0.0028) | partly held |
| F.10, the center intercept changes the within-slide metric by less than 0.005 on held-out donors within centers | oversight and session | the largest change in 15 task and encoder cells is 0.0022 (`results/round7/fedlearn/V2_run2/CCRCC/v2_paired.csv`, `results/round7/fedlearn/V2_run2/INDIANA_KIDNEY/v2_paired.csv`, `results/round7/fedlearn/V2_run2/LUNG_XENIUM/v2_paired.csv`, `results/round7/fedlearn/V2_run2/KIDNEY_POP54/v2_paired.csv`, `results/round7/fedlearn/V2_run2/BREAST_XENIUM/v2_paired.csv`, scheme `within`) | held |
| F.10, and it raises the pooled Pearson over those donors' spots | oversight and session | over all centers' held-out spots together it rises in `KIDNEY_POP54` (3 of 3 encoders, by 0.0018 to 0.0026) and in 2 of 3 breast encoders, and falls in all 9 pseudo-center cells, by 0.008 to 0.033 (scheme `within_all_centers`) | refuted |
| V2(c), centring raises the leave-one-center-out pooled Pearson in kidney, and changes the within-slide metric by less than 0.01 | session | the centred and federated predictions on a left-out center differ by a constant per gene, so neither correlation can change (equal to $7 \times 10^{-16}$). Within centers, the within-slide change is at most 0.0022 | not tested by this design (first part); held (second part) |
| F3.0, the federated and pooled exact heads agree below $10^{-10}$ | session | $7.6 \times 10^{-15}$ | held |
| F.11, at $\varepsilon = 10$ within 0.01 of the non-private federated head, and at $\varepsilon = 1$ more than 0.02 below it | oversight | 0.0225 below at $\varepsilon = 10$, and 0.107 below at $\varepsilon = 1$ (`results/round7/fedlearn/V3/v3_paired.csv`) | partly held |
| V3, at $\varepsilon = 10$ the loss is more than 0.01, because spot-level clipping alone costs accuracy | session | the loss is 0.0225, but clipping alone costs 0.0004 | held, with its stated reason refuted |
| F.12, fitting each gene from half the centers lowers the within-slide metric by less than 0.01 against full overlap, on every task | oversight and session | the loss is 0.010 to 0.023 on held-out donors within centers, and 0.0075 to 0.015 leaving one center out. It is below 0.01 only in `INDIANA_KIDNEY` leaving one center out (`results/round7/fedlearn/V4/CCRCC/v4_paired.csv`, `results/round7/fedlearn/V4/INDIANA_KIDNEY/v4_paired.csv`, `results/round7/fedlearn/V4/LUNG_XENIUM/v4_paired.csv`) | refuted |

## 6. Results

### V1, the learning curve (`results/round7/fedlearn/V1/CCRCC/v1_summary.csv`, `results/round7/fedlearn/V1/INDIANA_KIDNEY/v1_summary.csv`, `results/round7/fedlearn/V1/LUNG_XENIUM/v1_summary.csv`, `results/round7/fedlearn/V1/CCRCC/v1_draws.csv`, `results/round7/fedlearn/V1/INDIANA_KIDNEY/v1_draws.csv`, `results/round7/fedlearn/V1/LUNG_XENIUM/v1_draws.csv`, `results/round7/fedlearn/V1/CCRCC/v1_genes.json`, `results/round7/fedlearn/V1/INDIANA_KIDNEY/v1_genes.json`, `results/round7/fedlearn/V1/LUNG_XENIUM/v1_genes.json`)

The test donors are 6 of 23 units for `CCRCC`, 6 of 25 for `INDIANA_KIDNEY` and 4 of 15 for `LUNG_XENIUM`. The training pools hold 17, 19 and 11 units. Values are the mean over 20 draws with the standard deviation over draws in brackets, and one draw at the full pool.

| task | encoder | 1 donor | 4 donors | 8 donors | full pool |
|---|---|---|---|---|---|
| `CCRCC` | `uni_v2` | 0.061 (0.024) | 0.119 (0.020) | 0.137 (0.010) | 0.147 |
| `CCRCC` | `hoptimus0` | 0.048 (0.034) | 0.115 (0.030) | 0.139 (0.015) | 0.143 |
| `CCRCC` | `resnet50` | 0.049 (0.026) | 0.101 (0.020) | 0.118 (0.013) | 0.122 |
| `INDIANA_KIDNEY` | `uni_v2` | 0.064 (0.028) | 0.114 (0.018) | 0.132 (0.009) | 0.139 |
| `INDIANA_KIDNEY` | `hoptimus0` | 0.058 (0.025) | 0.111 (0.017) | 0.131 (0.009) | 0.140 |
| `INDIANA_KIDNEY` | `resnet50` | 0.042 (0.022) | 0.083 (0.014) | 0.095 (0.009) | 0.105 |
| `LUNG_XENIUM` | `uni_v2` | 0.351 (0.064) | 0.482 (0.009) | 0.501 (0.004) | 0.505 |
| `LUNG_XENIUM` | `hoptimus0` | 0.358 (0.068) | 0.487 (0.010) | 0.505 (0.004) | 0.511 |
| `LUNG_XENIUM` | `resnet50` | 0.245 (0.047) | 0.349 (0.008) | 0.366 (0.005) | 0.374 |

Accuracy still rises at the largest sizes the project holds, but slowly. From 8 donors to the full pool it rises by 0.004 to 0.011 in the two kidney tasks. The step from 16 donors to the full pool (17 or 19) is between −0.001 and 0.002. The pooled Pearson follows the same shape at a higher level. The exact head and the faithful head agree to within 0.006 in the summary means and to within 0.007 in any single draw at the two largest sizes. The spread over draws does not include the variation from the choice of the fixed test donors.

### V2, the simulated federation (`results/round7/fedlearn/V2_run2/CCRCC/v2_summary.csv`, `results/round7/fedlearn/V2_run2/INDIANA_KIDNEY/v2_summary.csv`, `results/round7/fedlearn/V2_run2/LUNG_XENIUM/v2_summary.csv`, `results/round7/fedlearn/V2_run2/KIDNEY_POP54/v2_summary.csv`, `results/round7/fedlearn/V2_run2/BREAST_XENIUM/v2_summary.csv`, `v2_paired.csv`, `v2_rows.csv`)

Run 2 reproduces run 1's per-center rows to $3 \times 10^{-15}$ and adds the all-centers scoring (section 7, item 2). Means are over draws, with the standard deviation over draws.

**(b) Pseudo-centers, where only the donors differ.** The federated head beats the local head on held-out donors within centers in all 9 cells, by 0.026 to 0.038 in `CCRCC`, 0.016 to 0.020 in `INDIANA_KIDNEY` and 0.025 to 0.032 in `LUNG_XENIUM` (paired over 10 partitions, standard deviations 0.008 to 0.027). With `uni_v2` on `CCRCC` the local head scores 0.181 (0.048) and the federated head 0.219 (0.052). This is the V1 effect at about a third of the donors against all of them.

**(a) Real sources, where lab, study and disease all differ.**

| task | encoder | center | local, own held-out donors | federated minus local (paired, sd, number of 10 draws above 0) | left out, all donors of the center |
|---|---|---|---|---|---|
| `BREAST_XENIUM` | `uni_v2` | 10x Genomics | 0.669 (0.065) | +0.018 (0.011, 10) | 0.605 |
| `BREAST_XENIUM` | `uni_v2` | bioRxiv study | 0.684 (0.059) | −0.001 (0.008, 4) | 0.632 |
| `KIDNEY_POP54` | `uni_v2` | Sorbonne cohort | 0.191 (0.035) | +0.003 (0.007, 6) | 0.092 |
| `KIDNEY_POP54` | `uni_v2` | kidney atlas | 0.112 (0.014) | −0.021 (0.012, 0) | 0.032 |

The other two encoders show the same pattern (`results/round7/fedlearn/V2_run2/CCRCC/v2_rows.csv`, `results/round7/fedlearn/V2_run2/INDIANA_KIDNEY/v2_rows.csv`, `results/round7/fedlearn/V2_run2/LUNG_XENIUM/v2_rows.csv`, `results/round7/fedlearn/V2_run2/KIDNEY_POP54/v2_rows.csv`, `results/round7/fedlearn/V2_run2/BREAST_XENIUM/v2_rows.csv`). Adding the Sorbonne ccRCC cohort to the atlas's own donors lowers the atlas's held-out accuracy in every draw and every encoder, by 0.021 to 0.035. Adding the atlas to the Sorbonne cohort changes it by less than 0.003. A head trained on one source and applied to the other loses 0.05 to 0.17 against the within-source figure. The left-out figures and the within figures are on different test donors (section 4).

**Intercept and centring.** On held-out donors within centers, the intercept arm and the centred arm each change the within-slide metric by at most 0.0022 in any cell. Over all centers' held-out spots scored together, the intercept raises the pooled Pearson where the centers are real sources. In `KIDNEY_POP54` the rise is 0.0018 to 0.0026. It lowers the pooled Pearson where they are random partitions, by 0.026 to 0.033 in `CCRCC` and 0.008 to 0.018 in the other two tasks. The mechanism proposed is that the intercept $\alpha_k$ is a center's mean expression minus its mean score. In pseudo-centers there is no center effect to capture, so $\alpha_k$ carries only the composition of a few training donors and adds error for the held-out donors. If this is right, the pseudo-center loss should shrink as centers grow, and it should be smallest in the task with the most spots per donor. That check was not run. With one test center, a change to every prediction by the same constant per gene leaves both correlations unchanged. This is why the intercept and centred arms equal the federated arm when one center is left out of two, to $7 \times 10^{-16}$.

### V3, spot-level differential privacy (`results/round7/fedlearn/V3/v3_calibration.json`, `v3_summary.csv`, `v3_paired.csv`)

The clip norms from the first center of the first partition (22,870 training spots) are $C_x = 18.51$ and $C_y = 8.84$, which give $\Delta = 380.2$. With $\delta = 10^{-5}$, the analytic Gaussian mechanism gives $\sigma = 190.0$ at $\varepsilon = 10$ and $\sigma = 1418.3$ at $\varepsilon = 1$, and the achieved $\delta$ matches the target to 1 part in $10^{10}$.

| arm | within-slide, mean (sd) | minus non-private unclipped, paired over 10 partitions (sd) |
|---|---|---|
| non-private, unclipped | 0.2189 (0.0517) | |
| non-private, clipped | 0.2185 (0.0506) | −0.0004 (0.0070) |
| $\varepsilon = 10$ | 0.1964 (0.0376) | −0.0225 (0.0166) |
| $\varepsilon = 5$ | 0.1812 (0.0329) | −0.0377 (0.0204) |
| $\varepsilon = 2$ | 0.1521 (0.0312) | −0.0668 (0.0259) |
| $\varepsilon = 1$ | 0.1115 (0.0314) | −0.1074 (0.0317) |
| $\varepsilon = 0.5$ | 0.0794 (0.0279) | −0.1395 (0.0351) |

Private rows are means over 200 draws (10 partitions × 20). At $\varepsilon = 10$ all 10 partitions fall below the non-private head. Clipping costs nothing measurable, so the loss comes from the noise and from the penalty that guards against it. The added penalty has a median of $1.0 \times 10^{5}$ at $\varepsilon = 10$, against the faithful $\lambda = 0.0078$. How much of the loss is the penalty and how much the noise itself was not separated (section 8). The unit of privacy is one spot. Protection of a whole patient follows by group privacy at a much larger cost.

### V4, partial gene overlap (`results/round7/fedlearn/V4/CCRCC/v4_summary.csv`, `results/round7/fedlearn/V4/INDIANA_KIDNEY/v4_summary.csv`, `results/round7/fedlearn/V4/LUNG_XENIUM/v4_summary.csv`, `v4_paired.csv`)

When each of three centers measures a random 25 of the 50 genes, on average 6.3 to 6.5 genes are measured by no training center within centers and 12.6 when one center is left out. Those genes are excluded from both arms. On the genes that remain, fitting each gene from the centers that measure it lowers the within-slide metric on held-out donors within centers by 0.018 to 0.023 in `CCRCC`, 0.010 to 0.013 in `INDIANA_KIDNEY` and 0.015 to 0.019 in `LUNG_XENIUM`. Masked is below full overlap in 97 to 100 of 100 partition and mask pairs. The paired standard deviations are 0.004 to 0.011. A proposed mechanism is that a gene measured by one center is fitted from that center alone, and V2(b) shows a single center losing 0.016 to 0.038 against all three. This is consistent with the size of the loss but was not checked gene by gene (section 8).

## 7. Discrepancies, open questions and escalations

1. *F3.0's first attempt failed on a data property* (job 4824300, `results/round7/fedlearn/r7fl_slurm_jobs.csv`). `LUNG_XENIUM` sample `NCBI865` has a patch barcode, `051x019`, with no expression row. The committed task file lists it under `dropped_patch_barcodes`, and round 4's `load_set_dropped` applies that list. The session's loader did not apply it. It now drops those barcodes and asserts, as round 3's `load_set` does, that every barcode is present and selects exactly one row (commit `89d698a6`). This was a crash before either check was evaluated, not a failed tolerance, and the second attempt passed both. Recorded under the decision boundaries, which list a new property of the data and an acceptance check fixed and rerun.
2. *V2's first run scored the pooled Pearson per center.* A3 defines it over all test spots together. Within one center the intercept cannot move a correlation, so F.10's second part could not be scored from run 1. V2 was rerun with the same designs and seeds and an added scheme `within_all_centers` (delivery 4, jobs 4839784 to 4839837, `results/round7/fedlearn/r7fl_slurm_jobs.csv`). Run 1 is kept in `results/round7/fedlearn/V2/`. V3 and V4 still report the pooled Pearson as a mean over centers, and their headline metric is within-slide, so they were not rerun.
3. *The memo expected the centred arm to differ from the others when one of two centers is left out* (A7). Its predictions do differ, but only by a constant per gene, which neither metric can see. Scoring centring across centers needs a metric that pools several test centers, or an error measure such as mean squared error. Proposed for the oversight chat.
4. *The faithful replica is close to HEST's head but not identical* (A5 asked for the same predictions). The largest split-level difference in `pearson_mean` is $8.5 \times 10^{-5}$ (`results/round7/fedlearn/F3_anchor_attempt2/f30_summary.json`). A likely cause is that HEST's expression values arrive as a float64 data frame while the session's loader casts them to float32 before the `lsqr` ridge. This was not checked. The faithful head is used only as a comparator in V1.
5. *Ownership of reused inputs* (`results/round7/fedlearn/F3_reuse_verdicts.csv`). `whose()` on the project tree's inputs gives `unstamped` for the benchmark data, the round 1 embeddings, the round 3 expansion embeddings and expression files, and the round 1 result. The lung Xenium embeddings are `sibling`, stamped by frame `dab7c82a-7762-41ec-aaf1-9a41e6afaff2` of the round 4 transfer session. Each was read only, and each is an input the instruction or a committed task definition names. The question of reuse goes to the oversight chat here.
6. *Output directory names.* The instruction names `results/round7/fedlearn/F3_V1/`, `results/round7/fedlearn/F3_V2/` and `results/round7/fedlearn/F3_V3/`, and the session wrote `results/round7/fedlearn/V1/`, `results/round7/fedlearn/V2/`, `results/round7/fedlearn/V3/` and `results/round7/fedlearn/V4/`, with F3.0 in `results/round7/fedlearn/F3_anchor_attempt2/` and the failed attempt in `results/round7/fedlearn/F3_anchor/`. Nothing was moved after the jobs ran, since provenance records the paths.
7. *The link-finding sub-agent's brief did not carry its frame id* (plan, escalations). It wrote no files and ran no job. Later briefs follow section 6 of `docs/EXECUTION_RULES.md`.
8. *The breast 10x center has 1 held-out sample of 7 in each V2(a) draw*, so its within-center figure rests on one slide per draw.
9. *`docs/EXECUTION_RULES.md`* was read on 14 October at `main` commit `a7008bb1`. It added no rule the plan did not already follow.

## 8. What was not checked

- Whether the V3 loss comes mainly from the noise or from the added penalty, for example with a smaller penalty arm and its Cholesky failure rate.
- Gene-by-gene V4 losses against the number of centers measuring each gene.
- Whether the pseudo-center intercept loss shrinks with center size.
- Variation from the choice of V1's fixed test donors, which the draw spread does not include.
- The cause of the replica's $8.5 \times 10^{-5}$ difference from HEST's head (`results/round7/fedlearn/F3_anchor_attempt2/f30_summary.json`).
- Any federated method other than the exact one-round head. No iterative head, adapter or private pretraining was run.

The screening shortfalls that the theme sub-agents declared at F2 still limit the review. Titles beyond the first 100 by relevance were not screened for broad queries. Several themes screened titles through a keyword filter before reading. The arXiv API returned HTTP 429 during the parallel searches, so some rows used the arXiv website search. Web-search rows have no hit totals (`docs/round07/i01/fedlearn/round07_fedlearn_F2_report.md`, section 7, item 6).

## 9. The viability verdict revised, the recommendation, and what is not established

**Revised verdicts** (F2's are in section 11 of the literature review).

| route or concept | F2 verdict | revised verdict and the experiments behind it |
|---|---|---|
| Route 1 and C1, one-round head from summary statistics | conditional | **Conditional, with the condition narrowed.** The head is exact (F3.0) and cheap (minutes per task). It gains accuracy when centers are exchangeable, since three pseudo-centers federated beat one by 0.016 to 0.038 (V2(b)), and V1 shows accuracy still rising at the largest pools the project holds. Across real sources the gain is small or negative. 10x breast gains 0.018, the bioRxiv breast study and the Sorbonne cohort change by less than 0.003, and the kidney atlas loses 0.021 (V2(a), `uni_v2`). Sources: `results/round7/fedlearn/V2_run2/CCRCC/v2_paired.csv`, `results/round7/fedlearn/V2_run2/INDIANA_KIDNEY/v2_paired.csv`, `results/round7/fedlearn/V2_run2/LUNG_XENIUM/v2_paired.csv`, `results/round7/fedlearn/V2_run2/BREAST_XENIUM/v2_rows.csv`, `results/round7/fedlearn/V2_run2/KIDNEY_POP54/v2_rows.csv`. Center intercepts add nothing to the within-slide metric, and they help the pooled metric only across real sources. |
| Spot-level differential privacy on the released sums | not assessed at F2 | **Costly at useful budgets.** 0.0225 lost at $\varepsilon = 10$ and 0.107 at $\varepsilon = 1$, against a non-private 0.219 (V3, `results/round7/fedlearn/V3/v3_paired.csv`, `results/round7/fedlearn/V3/v3_summary.csv`). |
| Centers measuring different genes | gap found (F.4) | **A real cost, and an open method problem.** 0.010 to 0.023 lost within centers (V4, `results/round7/fedlearn/V4/CCRCC/v4_paired.csv`, `results/round7/fedlearn/V4/INDIANA_KIDNEY/v4_paired.csv`, `results/round7/fedlearn/V4/LUNG_XENIUM/v4_paired.csv`), and no method in the literature addresses it (review sections 6 and 15). |
| Routes 2 to 4, C2 to C4 | as at F2 | Not tested in i02, so they stand as at F2. |

**Recommendation for the proof-of-concept paper.** For the method, the exact one-round head from per-center sums, with the faithful benchmark head as the comparator and the equality of federated and pooled fits as the first result. The substantive questions are the two where the experiments found a measurable cost and the review found no method. The first is partial gene overlap. A natural candidate is to share strength across genes, for example through a low-rank or multi-task coefficient matrix, so that a gene measured by one center borrows from the others. The second is the accuracy cost of releasing sums privately. For the data, `KIDNEY_POP54` and `BREAST_XENIUM` as real two-source federations, and pseudo-center partitions of `CCRCC`, `INDIANA_KIDNEY` and `LUNG_XENIUM` as the control in which only donors differ. Every source contrast mixes lab, study and disease, and the paper should say so. Whether this is the paper to write, and its framing, are decisions for Nicolas and his advisors.

**What is not established.**
- That federation raises accuracy across real centers. Two real federations of two sources each gave mixed signs.
- Any novelty claim. The literature check found no federated head on frozen pathology embeddings from summary statistics, but the estimator itself is established (review section 12).
- Patient-level privacy.
- Any result at more than three centers or on data outside HEST-1k.
- Any inference, such as intervals for a federated head's accuracy with a center-level error component.

## 10. Proposed next step

The track ends at this gate. Proposals for the oversight chat:

1. Decide whether the closing recommendation is taken forward as the methods paper, and if so whether the method of a first interval targets partial gene overlap or private release.
2. Answer the reuse question of section 7, item 5.
3. Decide whether a metric that pools test centers, or mean squared error, should be added before any claim about centring or intercepts.
4. Run the three cheap checks of section 8 (the V3 penalty, V4 by gene, intercepts by center size) if the paper goes ahead.

**Numeric-claim sweep.** `code/scripts/verify_numeric_claims.py` was run over this report and the literature review with `--search-dir . --exceptions .verify-exceptions-round7-fedlearn --derived .verify-derived --always results/summary/deck_numbers.csv` (output in `results/round7/fedlearn/F4_numeric_sweep.txt`). The exceptions file is unchanged, as memo section 4 item 8 asks. Every value it cannot match falls into one of the five kinds below, each with how it was checked. The counts are in the output file.

- *Memory in GiB* (section 2). These are derived from `sacct`'s KiB values in `results/round7/fedlearn/job_accounting.csv` by division by $1024^2$.
- *0.0102* (section 5, F.7, and this list). This is the difference of 0.14720 and 0.13700 in `results/round7/fedlearn/V1/CCRCC/v1_summary.csv`.
- *−0.001* (section 6, V1, and this list). This is the difference between the full-pool and 16-donor means for `CCRCC` with `hoptimus0` in the same file (0.14277 and 0.14369).
- *$8.5 \times 10^{-5}$* (sections 7 and 8, and this list). This is `replica_max_abs_diff_vs_hest` = 8.4516e-05 in `results/round7/fedlearn/F3_anchor_attempt2/f30_summary.json`. The checker does not read scientific notation in prose.
- *22,288* (review section 6, and this list). This appears as a comma-grouped integer inside a free-text cell of `results/round7/fedlearn/F1_search/reading/R4/reading_notes.csv`, which the checker does not match (the known limitation recorded at F2).

**The pull request** for this gate is #30 (`round7-fedlearn` into `main`), opened after the branch and the tag `round7-fedlearn-final` were pushed together.

---

## What the federated learning track established

The track asked whether federated learning is viable for predicting gene expression from H&E histology, and what a first methods paper should do. Interval i01 reviewed 406 papers and inventoried the data on disk. Interval i02 ran six scoping experiments on Longleaf.

The review found one federated histology-to-expression study (PPML-Omics) and no method that fits a prediction head on frozen pathology foundation-model embeddings from per-center summary statistics. The closed-form algebra of such a head is established elsewhere, so any novelty would rest on the application and on what the application reveals. No method was found for centers that measure different gene panels, none for the privacy cost of releasing high-dimensional embedding statistics, and none for inference with a center-level error component.

The experiments established five things.

1. A ridge head on 256 principal components of frozen embeddings can be fitted from per-center sums once, with no iteration, and it equals the pooled fit to $7.6 \times 10^{-15}$. It reproduces the benchmark head that round 1 replicated, at 0.263995 against 0.264 (`results/round7/fedlearn/F3_anchor_attempt2/f30_summary.json`).
2. Accuracy rises steeply up to about 4 to 8 training donors and slowly after that, and it is still rising at the largest pools the project holds.
3. When centers differ only in their donors, pooling three centers' sums beats one center alone by 0.016 to 0.038 in the within-slide metric (`results/round7/fedlearn/V2_run2/CCRCC/v2_paired.csv`, `results/round7/fedlearn/V2_run2/INDIANA_KIDNEY/v2_paired.csv`, `results/round7/fedlearn/V2_run2/LUNG_XENIUM/v2_paired.csv`). When centers are real sources that differ in lab, study and disease, pooling helped one center, left two unchanged and hurt one. A head carried from one source to another lost 0.05 to 0.17.
4. Spot-level differential privacy on the released sums cost 0.0225 at $\varepsilon = 10$ and 0.107 at $\varepsilon = 1$, against 0.219 (`results/round7/fedlearn/V3/v3_paired.csv`, `results/round7/fedlearn/V3/v3_summary.csv`). The cost came from the noise, not from clipping.
5. Fitting each gene only from the centers that measure it cost 0.010 to 0.023 when each center measured half the genes (`results/round7/fedlearn/V4/CCRCC/v4_paired.csv`, `results/round7/fedlearn/V4/INDIANA_KIDNEY/v4_paired.csv`, `results/round7/fedlearn/V4/LUNG_XENIUM/v4_paired.csv`).

Center intercepts do not change the within-slide metric, and they help the pooled metric only across real sources. A correlation scored within one test center cannot detect them.

Taken together, a one-round federated head is exact and practical. The project's data do not show that federation across real centers improves accuracy. The two costs that are measurable and have no method in the literature are partial gene overlap and private release, and they are where a methods paper could contribute.
