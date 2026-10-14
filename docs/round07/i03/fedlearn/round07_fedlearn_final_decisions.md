# Round 7, the federated learning track, decisions at the closing gate (F4)

14 October 2026. Written by the oversight chat after reviewing the closing report (`docs/round07/i02/fedlearn/round07_fedlearn_final_report.md`, pull request #30, tag `round7-fedlearn-final`). The track ends at this gate, so this memo opens no interval. It lives on `main` only. Nothing further is committed or pushed on branch `round7-fedlearn`.

**What was read and checked.** The whole report, its closing page, and the files behind the headline numbers. The numbers below were recomputed from the files on the branch.
- `results/round7/fedlearn/V1/CCRCC/v1_summary.csv` gives 0.061, 0.119, 0.137 and 0.147 for `uni_v2` at 1, 4 and 8 donors and the full pool of 17.
- In `results/round7/fedlearn/V2_run2/*/v2_paired.csv`, the federated head minus the local head on pseudo-centers, scheme `within`, within-slide metric, is 0.0263 to 0.0378 on `CCRCC`, 0.0162 to 0.0200 on `INDIANA_KIDNEY` and 0.0249 to 0.0323 on `LUNG_XENIUM`. At least 8 of 10 partitions are positive in every cell.
- The intercept arm minus the federated arm in the pooled Pearson over all centers' held-out spots (scheme `within_all_centers`) is 0.0018 to 0.0026 on `KIDNEY_POP54` and −0.0331 to −0.0078 on the three pseudo-center tasks.
- `results/round7/fedlearn/V3/v3_paired.csv` gives −0.0004 for clipping alone, −0.0225 at $\varepsilon = 10$ and −0.1074 at $\varepsilon = 1$.
- In `results/round7/fedlearn/V4/*/v4_paired.csv` the masked head minus the full-overlap head, within-slide, is −0.0231 to −0.0183 on `CCRCC`, −0.0131 to −0.0105 on `INDIANA_KIDNEY` and −0.0187 to −0.0152 on `LUNG_XENIUM` within centers. It is below zero in 97 to 100 of 100 pairs within centers and in 100 of 100 leaving one center out.

**The gate rule** is section 2 of `docs/EXECUTION_RULES.md`. The track has no later stage, so nothing more is set up, staged, piloted or run under it.

## 1. Acceptance

The closing gate is accepted, and the federated learning track is complete. Both F3.0 anchors pass, every experiment the F2 memo fixed has run in full, every prediction is scored, and the provenance index covers every job that wrote a record. The report keeps its claims inside what the experiments show, scores four of the oversight chat's predictions as refuted or partly held without softening them, and separates the cases where centers differ only in donors from the cases where they differ in lab, study and disease. The rerun of V2 to score the pooled metric over all centers was the right call and was handled under the decision boundaries. Nicolas can merge pull request #30.

## 2. What the track establishes, for the record

These are the readings the project carries forward. They are statements about HEST-1k data the project holds, with the exact one-round ridge head on 256 principal components of frozen embeddings.

1. **The method is exact and cheap.** The head fitted from per-center sums equals the pooled fit to $7.6 \times 10^{-15}$ and reproduces round 1's benchmark value (0.263995 against 0.264). This is the paper's first result if the paper goes ahead. It is not a new estimator (review, section 12).
2. **More donors help, with diminishing returns.** Accuracy rises steeply to about 4 to 8 training donors and slowly after, and it is still rising at the largest pools held. With `uni_v2` on `CCRCC` the step from 8 donors to 17 is 0.010.
3. **Federation helps when centers are exchangeable, not clearly when they are real sources.** Pooling three pseudo-centers beats one by 0.016 to 0.038. Across the two real two-source federations, pooling helped 10x breast by 0.018, left the bioRxiv breast study and the Sorbonne cohort within 0.003, and cost the kidney atlas 0.021. The 10x breast gain rests on one held-out slide per draw, drawn from 7 slides (escalation 8), so it is the weakest of the four. Every source contrast mixes lab, study and disease.
4. **Center intercepts do not matter for the within-slide metric.** A within-slide correlation cannot see a constant shift per gene and slide. Over the pooled spots of several centers they help slightly across real sources and hurt on pseudo-centers, which fits the session's mechanism that the intercept then carries only the composition of a few donors. That mechanism is not checked.
5. **Spot-level differential privacy on the released sums is costly.** The head loses 0.0225 at $\varepsilon = 10$ and 0.107 at $\varepsilon = 1$, against 0.219 without privacy. Clipping alone costs 0.0004, so the loss is from the noise and the larger penalty that guards against it, in a split not yet measured. Protecting a whole patient would cost more.
6. **Partial gene overlap has a measurable cost.** When each of three centers measures a random half of 50 genes, fitting each gene from the centers that measure it costs 0.010 to 0.023 within centers. The review found no method for it.

What is not established is listed in section 9 of the report and stands as written. The project's data do not show that federation across real centers improves accuracy, nothing is shown beyond three centers or outside HEST-1k, and no novelty is claimed.

## 3. Answers to the escalations

1. **The dropped lung barcode.** Accepted. The fix applies the committed task file's own list and asserts one row per barcode, as round 3's loader does. Recorded as a new property of the data.
2. **The pooled metric scored per center in V2's first run.** Accepted, including the rerun and keeping run 1 as a record. V3 and V4 report within-slide as their headline, so they stand without a rerun.
3. **The centred arm on one left-out center.** Accepted. With one test center the centred and federated predictions differ by a constant per gene, and neither metric can see it. The V2(c) prediction is scored correctly as not tested by this design. See proposal 3 below.
4. **The faithful replica's difference of $8.5 \times 10^{-5}$.** Accepted. It is far below any difference the report interprets, and the faithful head is only a comparator in V1. Not pursued.
5. **Reuse of unstamped and sibling inputs.** Accepted. Reading inputs that the instruction or a committed task definition names, without rebuilding or overwriting them, needs no question. The `whose()` question exists to stop a session from rebuilding or overwriting another session's outputs. The verdicts are recorded in `results/round7/fedlearn/F3_reuse_verdicts.csv`, which is enough. `docs/EXECUTION_RULES.md` section 4 now says this (revision of 14 October).
6. **Output directory names.** Accepted. `V1/` to `V4/`, `F3_anchor/` and `F3_anchor_attempt2/` stay where provenance records them.
7. **The link-finding sub-agent's brief without its frame id.** Accepted. It wrote nothing and ran no job.
8. **One held-out breast slide per draw.** Accepted, and carried into reading 3 above.
9. **`docs/EXECUTION_RULES.md` read at `a7008bb1`.** Noted.

## 4. Answers to the proposals

1. **Whether the recommendation becomes the methods paper, and which problem its first method targets.** This is Nicolas's decision with Dr. Zhu and David, and is recorded as open question R7-4 in `CLAUDE.md`. The track gives them the evidence. The oversight chat's view, for that discussion, is that partial gene overlap is the better first target. Its cost is measured, the review found no method, and the problem is statistical (borrowing strength across genes through a low-rank or multi-task coefficient matrix), which suits a methods paper and the project's existing machinery. Private release enters a large differential privacy literature in which the contribution would be an application. Until they decide, no federated learning track is opened.
2. **The reuse question.** Answered in section 3, item 5.
3. **A metric that pools test centers, or mean squared error.** Yes, before any claim about intercepts or centring, in whichever track takes the paper forward. Not run now.
4. **The three cheap checks** (the V3 split between penalty and noise, V4 gene by gene, intercepts against center size). Deferred to the first interval of a follow-up track if the paper goes ahead. They are listed in the round's README so they are not lost.

## 5. What happens now

The session's work is finished. Nicolas merges pull request #30. The oversight chat records the track's close in the round's README, the progress log and `CLAUDE.md`. Round 7 closes when the inference track has also finished.
