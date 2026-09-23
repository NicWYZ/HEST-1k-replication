# Round 3, A3 stage report

23 September 2026. Covers interval 2: H0, A2, A3, D1, D2 and D3. Written against
`docs/round3_execution_plan.md`, whose section 12 is this session's transcription of
`docs/decisions/round3_A1_decisions.md`. Report-and-wait gate. Nothing in interval 3 has been
started, set up, staged or piloted, and nothing will be until the decision comes back.

Numbers are quoted at the precision the comparison needs, and every one was read back from the file
named beside it. Full precision stays in the files. Every source term in this report is subject to
one limitation, stated here once and repeated where it bites: **HEST-1k contains no organ-by-
technology cell with three laboratories at three or more donors each once disease state is held
fixed, checked across all 46 cells, so the institution axis this round is a two-source contrast**
(`results/round3/D0_inventory/`). D3 narrows it further; see section 6.9.

---

## 1. Stage and status

| stage | status |
|---|---|
| H0, housekeeping from the A1 escalations | complete; item 5 (determinism) closes A0's H4 as "not byte-identical, no coverage number moved" |
| A2, conditional coverage and the anatomy of failure | complete; every planned output written, fragments merged with zero collisions |
| A3, weighted and hierarchical conformal | complete; all four acceptance checks pass with zero failures; no harness edit was needed |
| D1, download of the approved sets | complete and verified; the memo's patch-equals-spot check fails and is replaced by a subset relation, escalated |
| D2, embeddings for the expansion sets | `resnet50` complete; `hoptimus0` and `uni_v2` pending in the Slurm queue; **the anchor check fails** |
| D3, donor and laboratory audit | complete inside its cap; three findings change round-3 set descriptions and one would change a benchmark donor label, all escalated |

The A2 headline is narrower and stronger than any of the six A2 predictions. What breaks coverage
under donor shift is the calibration unit, and it breaks coverage by making the interval too narrow,
not by putting it in the wrong place. On one shared proper-training set, calibrating on held-out
donors covers 0.8562 and calibrating on spatial blocks covers 0.7442, block below unit in every one
of 138 encoder-task-fold cells (`results/round3/A3_report_numbers.csv`), and the level-versus-scale decomposition puts the larger share
of the shortfall on scale in all five groups it was run on (`results/round3/A2_conditional/a2_level_scale.csv`).

A3's headline is that no weighting repairs coverage under donor or slide shift, for a reason the
stage measures directly. Calibration and test slides are almost perfectly separable: the embedding
classifier's held-out AUC is at least 0.9747 on every one of 966 shifted fold cells, and the eight
morphology covariates alone reach a median of 0.9003. Feature-based weights therefore collapse the
effective calibration size, to a median 2.13% of the calibration set for W1, and move coverage a
long way per fold in both directions with almost no mean movement (+0.0023, sd 0.0746), costing
LYMPH_IDC 0.150 and 0.168. The covariate weights either have no support or nothing to do. HCP is
infinite in exactly the fold cells where $K + 1 < 1/\alpha$, which at $\alpha = 0.10$ is every
unit-calibrated fold, and where it is finite at $\alpha = 0.20$ it over-covers. Every number in this
paragraph is recomputed in `results/round3/A3_report_numbers.csv`.

## 2. What was run

Repository commits this interval: `d3ce2b7` (memo committed and transcribed), `60718a0` (H0 items 1
to 4, the A2 strata answerable from A1's outputs, D3), `45da293` (D1, D2), `d0e012c` (A2 harness
reruns, H0 item 5, the fragment merge), and the A3 commit that carries this report.

The work ran as five parallel tracks, per section 12.8: Housekeeping, Anatomy, Mechanisms,
Expansion, Audit. A3 then ran on the Mechanisms track. Sub-agents ran no git command; the local clone
was the only committer, and every sub-agent result was checked by the lead before commit (the checks
are listed in section 3).

**Scripts.** `code/scripts/round3_a0_harness.py`, extended behind seven off-by-default flags (md5 `0ad7ae8efe554c1f285e5f384a9fb7f5`); `code/scripts/round3_a2_anatomy.py`;
`code/scripts/round3_a2_mechanisms.py`; `code/scripts/round3_a2_merge.py`;
`code/scripts/round3_d3_build_audit.py`; `code/scripts/round3_d1_*.py`;
`code/scripts/round3_d2_embed.py`; `code/scripts/round3_a3_weighted.py` (md5
`70927b656860286c6a612694ec4b3785`), which imports the harness unmodified; and
`code/scripts/round3_a3_report_numbers.py`, which recomputes every pooled number in this report.

**Jobs.** All CPU jobs landed on `spill` though `general` was requested, as in A1. The A2 jobs peaked well below
their memory requests (sacct MaxRSS in the Mechanisms job table), so the interval-1 sizing suffices for every A2 mode.

**A queue intervention changed five submitted jobs, and is recorded because of that.** The group's
fairshare on `rc_htzhu_pi` stood at about 0.007, so jobs start early only through backfill, and the
five A2 jobs still pending after 2 h 40 min had been submitted with 16 h limits, which blocks
backfill. On the lead's diagnosis the Mechanisms track lowered their limits in place to 3 h with
`scontrol update`, bounded from a sibling job's measured runtime; all five started within minutes.
Nothing about the jobs' work, resources or seeds changed. The note is under `config.queue_note` in
`results/round3/A2_conditional/PROVENANCE__mechanisms__tables.txt`. The lead made the same change to the two
pending D2 GPU jobs, 2128386 (`hoptimus0`, 6 h to 4 h) and 2128582 (`uni_v2`, 6 h to 3 h), which moved
their estimated start from the evening of 23 September to early that morning; the D2 script caches
per sample, so a timeout costs only the unwritten samples. Their anchor checks are not in this report. Carried forward: time limits at
about three times the expected runtime, never a blanket 16 h.

## 3. Acceptance checks

**H4, determinism (H0 item 5).** `results/round3/H0_determinism/determinism_diff.csv`. The
`resnet50` A1 job was rerun from the harness pinned at `d3ce2b7`, with A1's command lines verbatim
except the output directory, and both config hashes reproduced A1's. The result is **not
byte-identical, and no coverage number moved.** 4 of 16 files are byte-identical: the calibration-unit
and disjointness files, which record $T$, $C$, $E$ and the fitted scaler and PCA statistics, so the
splits and the preprocessing reproduce bit for bit. In the other 12, only width, interval-score,
conformal-quantile and $\hat\sigma$-diagnostic columns move, by at most 2.911e-06 absolute and
4.228e-07 relative. `coverage`, `n_covered`, `miss_above` and `miss_below` are identical in every
file; the lead recomputed that equality from the files. A second run, which is not the H0 rerun and
must not be conflated with it, ran the A2-extended harness with A1's `slideout` command line and no
A2 flag: its eight outputs were byte-identical to A1. The same command line
therefore reproduced A1 bit for bit on one node and not on another, which points to floating-point
reduction order differing between nodes. That reading was not tested directly.

**A2b anchor arm.** `results/round3/A2_conditional/a2_unit_intervention.csv` against
`results/round3/A1_coverage/a1_by_fold__<enc>__main.csv`. The anchor arm, A1's own proper-training
set with A1's own calibration set refit in the A2 run, reproduces A1's per-fold coverage to a
maximum absolute difference below $10^{-15}$ over 138 cells (3 encoders by 46 donor folds), which is
double-precision resolution. The intervention is therefore comparable to A1. No A2b fold fell below
the 1,000-spot floor on $T$; `a2_dropped_folds.csv` is empty.

**The harness's default behaviour is unchanged.** Established by rerunning, not asserted: the
byte-identical regression above. H3 also passed in every A2 run, disjointness and "scaler and PCA
saw only $T$" reproducing in every fold (`h3_disjointness__<enc>__mech_main.csv` and siblings in
`results/round3/A2_conditional/`).

**The A2 fragment merge.** `results/round3/A2_conditional/a2_merge_report.json`.
`a2_by_stratum.csv` has 10,289 rows (4,952 from the Anatomy fragment, 5,337 from the spot fragment)
and `a2_prad_donor_sharing.csv` has 355 (148 paired, 207 arm), with **zero** cross-fragment and zero
within-fragment key collisions. The two tracks named the same concepts differently; the merge
harmonises them by an explicit rename map recorded in the report, and the first merge attempt, which
keyed on the base columns alone, reported every spot-fragment row as a duplicate. That was a
keying error, not a data collision.

**The lead's verification of the Mechanisms hand-back.** Recomputed from the committed tables and
A1's committed files, not copied: the anchor maximum; the arm means and the 138-of-138 count; both
Spearman correlations in section 6.2; that `a2_coverage_vs_K.csv`'s coverage equals A1's `by_fold`
coverage exactly for all 348 folds; the simulation band counts; the PRAD paired mean and standard
deviation; an independent refit of the A2b `C_block` level-scale regression, reproducing its
intercept and both coefficients; the decile and tertile coverages from `n_covered` and
`n_spot_gene`. One correction came out of it and is carried in section 7: the 39 block-calibrated
folds include COAD's `patient` folds, not only HCC, LUNG and SKCM.

**A3 acceptance.** `results/round3/A3_weighted/a3_acceptance.csv`, 30 rows over six jobs, zero
failures. On `random`, each weighting's coverage is within 0.005 of `none` on the same spot subset:
worst cases 4.120e-03 (W1), 1.056e-03 (W1b), 2.082e-03 (W2) and 0 (W3). W1's held-out AUC on
`random` is within 5.801e-02 of 0.5 against a tolerance of 0.10; the in-sample AUC is inflated on a
null shift with 256 features, so the check uses a refit-on-half, score-the-other-half AUC and both
are recorded. No fold has a non-positive or non-finite weight after clipping. W3 at $\alpha = 0.1$
on `random`, where the unit is the spot, reproduces the unweighted interval exactly, 0 difference in
coverage and width over 330 cells per encoder. A fourth check was added because it is free: the
`none` weighting reproduces A1's committed per-fold coverage to 3.330669e-16, so A3's folds are A1's
folds and every weighted number sits beside an unweighted one that reproduces the A1 gate. The lead
recomputed that last check over 447 fold rows (`results/round3/A3_report_numbers.csv`), confirmed that the merged A3 tables are exact
concatenations of the per-encoder files, and confirmed the W3 infinite-interval predicate in every
one of 1,932 cells.

**D1 verification.** `results/round3/D1_download/d1_summary.json`. 105 samples, 525 files and
70,260,258,915 bytes expected and present, no missing file and no size mismatch. The memo's
criterion that each sample's patch count equal its spot count fails on 94 of 105 samples; see
section 6.9 and section 7, item 3.

**D2 anchor check: FAILS.** `results/round3/D2_embeddings/anchor_check_consolidated.csv` and
`results/round3/D1_download/round3_d1_d2_expansion_note.md`. The criterion was agreement with the
cached benchmark embeddings to about $10^{-5}$ relative on the 28 samples present in both layouts.
For `resnet50` over 108,837 matched barcodes, the per-row relative L2 difference has a median of
per-sample medians of 0.0633 and a maximum of 0.1552, three to four orders of magnitude above the
criterion. Section 6.9 gives what differs.

## 4. What differs between the arms of each comparison

Written out before the terms are named, per the standing rule.

**A2b, `C_unit` against `C_block`.** Identical: the proper-training set $T$ (one mask, so the head,
scaler and PCA-256 are fit once per fold and draw and shared), the test set $E$, the score,
$\alpha$, the size-match target and the number of calibration spots after matching, the encoder, the
task, the fold and the calibration draw. Differs: the source of the calibration scores, and nothing
else. `C_unit` takes them from the donors A1's calibration-unit rule held out of the pool; `C_block`
from buffered spatial blocks (grid 6, 2.5-pitch buffer, about 20% of blocks) carved from the slides
that form $T$.

**A2b, `anchor_a1` against `C_unit`.** Differs: the proper-training set loses the carved blocks and
their buffer, and `C_unit` is subsampled to `C_block`'s size whenever it is larger, which it was in
every task. Identical: the identity of the calibration units, $E$, the score, $\alpha$, the encoder
and the fold. `anchor_a1` is A1 exactly.

**A2d, A1's own `slide_out` draws, same-donor calibration slide against none (Anatomy).** The test
slide is fixed. Differs: whether a calibration slide shares the test slide's donor, and with it,
because a calibration slide leaves $T$ in A1, how many same-donor slides remain in training; on
PRAD also resolution class and capture session, shared in 80% of same-donor draws and in none of the
others. Five test slides qualify.

**A2d, `slide_out` against `slide_out_cal_other_donor` (Mechanisms).** Identical: the test slide,
the pool of candidate training slides, the calibration unit (the slide), the number of draws, the
score, $\alpha$, the size-match target and the encoder. Differs: which slides may be calibration
slides. The other-donor arm leaves every same-donor slide in $T$. On PRAD the two donors share
neither resolution class nor session, so this arm is not a clean donor-only contrast.

**A2c, the between-unit share.** Not a like-for-like quantity of calibration information: it is
computed over the $K$ calibration units together with the test unit, whose scores use test labels,
because with $K = 1$ one unit has no between-unit variance. Every table carrying it has
`uses_test_labels = True`. Section 12.9 item 4; section 7, item 9.

**A2f, A1's unit-calibrated folds against A1's block-calibrated folds.** Not a controlled contrast.
The block group is the folds whose pools held fewer than two units, which are HCC, LUNG and SKCM
`donor` and `patient` and COAD `patient`, so the groups differ in task, tissue, spot count, training
size and $K$ as well as calibration unit. The A2b arms are the controlled version of the same
contrast, which is why both are reported.

**A3 weightings.** The five arms differ only in the weight vector: fold, $T$, head, scaler, PCA,
$E$, score, $\alpha$ and size match are computed once per fold and shared. `none` sees nothing and
runs through the same weighted-quantile code. **W1** sees everything the encoder represents,
including the slide signature, stain and scanner: logistic regression on the PCA-256 features fit on
$T$, class-balanced, L2 at a fixed, untuned $C = 1$, clipped at the 99.5th percentile of the
calibration weights. **W1b** sees tissue composition only, the eight morphology covariates, and
cannot see the slide as an image; it runs on the morphology-joined spots, so its rows also differ in
spot set and are compared with `none` on that same subset. **W2** sees resolution group and, on PRAD
only, capture session; on the six single-resolution-group tasks it is identically unweighted.
**W3** sees the unit structure of the calibration set and no features; its unit is the fold's
recorded `calibration_unit`, so on block-calibrated folds the unit is a spatial block of a training
slide and its guarantee is not the one the stage wants.

## 5. Predictions against outcomes

The eight predictions are the memo's section 9, quoted in plan section 12.4 before anything ran.
Every pooled number in the outcome column is recomputed in `results/round3/A3_report_numbers.csv` by
`code/scripts/round3_a3_report_numbers.py`; per-row sources are the A2 files named in section 6.

| # | stage | prediction | outcome |
|---|---|---|---|
| 1 | A2b | block calibration on the same $T$ under-covers the held-out donor by 0.10 to 0.20; unit calibration reproduces A1 | **Second clause holds**: `C_unit` minus A1 is +0.00048, sd 0.00918. **First clause holds in the mean and in direction, not in range**: `C_block` minus A1 is −0.1115, direction right in 138 of 138 cells, but only 31.9% of cells fall inside [−0.20, −0.10]; per task `C_block` minus A1 runs from −0.058 (READ) to −0.283 (IDC `audited`) |
| 2 | A2c | shortfall grows with the between-unit share and shrinks with $K$; the simulation reproduces fold means within their dispersion; block folds sit below it | **First clause fails**: Spearman −0.0825 with the share (wrong sign) and −0.0265 with $K$. **Second holds** for unit-calibrated folds, 79.9% inside the simulated 5-95% band. **Third holds**: 0 of 39 block folds inside |
| 3 | A2a | `scaled` has lower across-slide coverage sd than `abs` under `random` on every task; PRAD's under-covering fold is the one calibrated on patient 2's slides, and its between-unit share is the smaller | **First clause fails narrowly**: 10 of 11 task files, LUNG the exception. **Second holds**: the fold holding out patient 1, calibrated on four of patient 2's slides, covers 0.8146 against 0.9280 (`results/round3/A2_conditional/a2_by_stratum.csv`, stratum `prad_fold`). **Third fails**: that fold's share is the larger, 0.044 to 0.046 against 0.018 to 0.026 |
| 4 | A2d | same-donor calibration covers a few points higher within PRAD, less than the 0.14 between-task figure | **Not settled; two contrasts disagree and measure different things.** A1's own draws: +0.0805 under `abs` over 5 test slides by 12 encoders, positive in all 60 pairs (+0.0071 under `scaled`). The other-donor arm: +0.0027, sd 0.0421, over 23 test slides by 3 encoders. Section 6.5 |
| 5 | A2e | width orders with encoder Pearson under every design; coverage range stays under 0.02 | **Holds for mean width**, Spearman −0.874 to −0.972 by design; **not for median width** under `patient` and `slide_out`. Coverage range 0.0018 to 0.0154, under 0.02 |
| 6 | A2f | block folds fail on level; unit folds fail without a consistent sign | **Fails on both clauses.** Block folds fail on scale, not level; unit folds carry a consistent positive miss asymmetry |
| 7 | A3 | W1 collapses $n_{\text{eff}}$ on every different-slide fold; W1b does not; W2 has no support on PRAD and SKCM `patient`; W3 infinite at $\alpha = 0.1$ outside CCRCC, finite and near nominal at $\alpha = 0.2$ where $K \ge 4$, inert on block folds; nothing repairs the two-sample tasks | **W1 clause holds**: held-out AUC at least 0.9747, $n_{\text{eff}}$ a median 2.13% of calibration size and under 5% in 82.1% of cells. **W1b clause fails**: median 9.34%, at or above 30% in only 20.8% of cells. **W2 clause holds**: no support in 18 of 18 cells on each. **W3 at $\alpha = 0.1$: the memo's parenthetical fails and section 12.9 item 2's reading holds**; CCRCC `donor` ($K = 6$) is infinite, and the only finite cells are SKCM `patient`, block-calibrated at $K = 9$. **At $\alpha = 0.2$** finite on CCRCC and PRAD as predicted, over-covering at 0.9143 to 0.9904 in the mean. **Not inert on block folds**: finite W3 lifts coverage by 0.1547 there. **Two-sample clause**: holds in substance, fails in arithmetic; section 6.8 |
| 8 | D3 | the eleven-sample breast source resolves to one laboratory; `TENX98`/`TENX99` are the vendor's replicate pair; the Washington University samples split into healthy and diseased donors with one scanner | **First holds** (10x Genomics). **Second holds**, and D3 finds `TENX95` misassigned in round 2 as a consequence. **Third is overtaken**: the 23 samples split into 6 reference, 11 diabetic and 6 acute-injury donors on one instrument, but they were generated at Indiana, not Washington University |

## 6. Results

### 6.1 The calibration-unit intervention (A2b)

`results/round3/A2_conditional/a2_unit_intervention.csv`, pooled in `results/round3/A3_report_numbers.csv`; `abs` score, three encoders, the `donor`
design on the eight task files with at least two units in the pool.

On one shared $T$ (`results/round3/A3_report_numbers.csv`), held-out-unit calibration covers 0.8562 and size-matched spatial-block
calibration covers 0.7442. The difference is 0.1120 with an across-fold sd of 0.0725, and block
covers less than unit in 138 of 138 cells. Block intervals are about a third narrower, mean width
1.8112 against 2.7239.

| task file | folds | `C_unit` | `C_block` | difference | `C_block` minus A1 |
|---|---|---|---|---|---|
| CCRCC shipped | 24 | 0.8660 | 0.7928 | 0.0733 | −0.0714 |
| COAD shipped | 4 | 0.8688 | 0.7236 | 0.1452 | −0.1467 |
| IDC audited | 3 | 0.8337 | 0.5521 | 0.2816 | −0.2826 |
| IDC shipped | 4 | 0.8297 | 0.6132 | 0.2165 | −0.2159 |
| LYMPH_IDC shipped | 4 | 0.8163 | 0.7212 | 0.0951 | −0.0967 |
| PAAD shipped | 3 | 0.8980 | 0.7309 | 0.1670 | −0.1601 |
| PRAD shipped | 2 | 0.8690 | 0.8063 | 0.0627 | −0.0676 |
| READ shipped | 2 | 0.8041 | 0.7560 | 0.0480 | −0.0584 |

One thing to weigh. The memo's size-match rule subsamples the larger calibration set, and `C_unit`
was larger in every task, so the `C_unit` arm ran on a mean 37.9% of A1's calibration spots and
67.4% of its training spots. It still reproduced A1 within 0.0005 in the mean, while the block arm
on the identical $T$ and head lost 0.11. That contrast is the cleanest statement of the mechanism
this interval produced.

### 6.2 Coverage against $K$ and the between-unit share, and the simulation (A2c)

`results/round3/A2_conditional/a2_coverage_vs_K.csv` and `a2_simulated_coverage.csv`; figure
`fig_a2_coverage_vs_K.png`; pooled numbers in `results/round3/A3_report_numbers.csv`. 348 folds over three encoders, `abs`, coverage read from A1's committed
files.

The share and $K$ do not predict the shortfall: Spearman −0.0825 with the share, the opposite sign
to the prediction, and −0.0265 with $K$. Per fold, $K$ takes only the values 1, 2, 4, 5, 6, 7 and 8
(`a2_coverage_vs_K.csv`). Tabulated per calibration draw, as the Anatomy strata do, one SKCM
`patient` fold reaches $K = 9$ (`a2_by_stratum.csv`, stratum `n_cal_units_K`), but that fold is
block-calibrated and its $K$ counts spatial blocks within slides, which are not exchangeable groups
in the sense the $K \ge 9$ condition needs. No unit-calibrated fold has $K$ above 6, and every fold at $K = 7$ or 8 is
block-calibrated, so the gradient is barely identified and the condition cannot be tested on this data. The Anatomy strata's
coverage-against-$K$ gradient, which pools over $K$ levels, is steeply negative for the same reason:
the high-$K$ levels are almost all block folds.

What separates the folds is again the calibration unit. The 309 unit-calibrated folds cover 0.8587;
the 39 block-calibrated folds cover 0.6780 and have the *lower* between-unit share, the reverse of
what a share mechanism would give. The location-shift simulation, 1,000 replicates per fold, puts
79.9% of unit-calibrated folds inside its 5-95% band and none of the 39 block folds, and its
simulated coverage, pooled by $K$, is 0.889 to 0.901 at every $K$: a pure location shift with these variances
predicts near-nominal coverage regardless of $K$ and cannot account for the block folds' deficit.

The simulation carries two declared simplifications: calibration units are capped at 2,000
simulated spots, and the test unit's coverage is evaluated analytically rather than drawn.

### 6.3 Level against scale (A2f)

`results/round3/A2_conditional/a2_level_scale.csv`, figure `fig_a2_anatomy.png`. Shortfall regressed
on the standardised slide offset $|b_s|/s_y$ (level) and $\log(w^\star/\hat w)$ (scale), per group.

| group | slides | $R^2$ | level share | scale share | mean $w^\star/\hat w$ | mean miss asymmetry |
|---|---|---|---|---|---|---|
| A1, unit-calibrated | 573 | 0.9011 | 0.1910 | 0.7101 | 0.9767 | 0.3284 |
| A1, block-calibrated | 45 | 0.8565 | 0.0585 | 0.7980 | 1.8262 | 0.1587 |
| A2b anchor | 210 | 0.9165 | 0.2212 | 0.6953 | 0.9838 | 0.3407 |
| A2b `C_unit` | 210 | 0.9079 | 0.2052 | 0.7027 | 0.9905 | 0.3604 |
| A2b `C_block` | 210 | 0.9616 | 0.1502 | 0.8114 | 1.3692 | 0.2816 |

Scale carries the larger share in every group. Block-calibrated intervals are 37 to 83% too narrow
for the held-out slide and have the *lowest* miss asymmetry; unit-calibrated intervals are close to
the right width and carry a consistent positive asymmetry, misses above the interval more often than
below. Going from `C_unit` to `C_block` on the identical $T$ moves $w^\star/\hat w$ from 0.9905 to
1.3692 and leaves the level term unchanged by construction. Spatial-block calibration scores
understate the score spread a held-out donor produces. $b_s$ and $w^\star$ use test labels and are
diagnostics throughout. The five fits were assessed on $R^2$ and coefficient $t$ statistics only.

### 6.4 Strata (A2a)

`results/round3/A2_conditional/a2_by_stratum.csv` (merged).

**Predicted-value decile**, pooled over designs and encoders, `abs`: coverage 0.8825 in the bottom
decile, 0.9004 to 0.8999 in deciles 1 to 3, then falling to 0.6777 in the top decile, while width
narrows slightly from 2.845 to 2.686. The failure is one-sided, at the upper tail, and it holds under
each design separately.

**Neoplastic-fraction tertile**: 0.8598, 0.8719 and 0.8301 from lowest to highest, a spread about a
fifth of the decile spread. The tertile bins are unequal in size, and 95.98% of spots join the
morphology file (91.18% on CCRCC); unjoined spots are excluded from that stratum.

**PRAD by fold.** Under `donor`, the fold holding out patient 1 (8 test slides, calibration on 4 of
patient 2's slides, $K = 4$) covers 0.8146 at width 1.918; the fold holding out patient 2 (15 test
slides, calibration on 2 of patient 1's slides, $K = 2$) covers 0.9280 at width 2.655.

**`scaled` against `abs` under `random`**, across-slide sd of coverage: `scaled` is lower on 10 of
11 task files; LUNG is the exception.

**Slides.** CCRCC's `INT5` covers 0.26 under both shift designs and is the only slide with mean
coverage below 0.50. It enters the level-scale fits as an ordinary row.

**Other Anatomy strata**, all in `a2_by_stratum.csv`, rows from the `anatomy` fragment. PRAD
patient 2's two capture sessions cover alike under every design, and above the slides with no
recorded session, which are every other task; session is recorded only for those PRAD slides, so the
stratum is a PRAD contrast rather than a session effect. Calibration sharing a resolution group or
session with the test slide goes with higher coverage under `donor` and `slide_out` and lower under
`patient`, with no consistent sign. Slides whose donor label is `unverifiable` cover lowest under
`donor` and `slide_out`, and `contradicted` slides lowest under `patient`; the three tasks with
entirely unverifiable labels account for the first group, so the stratum is confounded with task.

### 6.5 Donor sharing within PRAD (A2d)

`results/round3/A2_conditional/a2_prad_donor_sharing.csv` (merged).

The two contrasts give different answers because they hold different things fixed (section 4).
Within A1's own draws, a draw with a same-donor calibration slide covers 0.0805 more than one
without, under `abs`, positive in all 60 pairs, with wider intervals; but only five PRAD test slides
qualify, the same-donor draws also share resolution class and session in 80% of pairs, and in A1 a
calibration slide leaves $T$, so those draws also train on fewer same-donor slides. Under `scaled`
the same contrast is +0.0071. The dedicated other-donor arm, on all 23 test slides, gives +0.0027
(sd 0.0421, 69 slide-encoder pairs) and reaches the same coverage with intervals about 8% wider.

A reading consistent with both, untested: donor sharing matters through what is left in training,
not through the calibration scores. Neither contrast is a clean donor-only comparison on PRAD, since
the two donors share neither resolution class nor session.

### 6.6 Width by encoder (A2e)

`results/round3/A2_conditional/a2_width_by_encoder.csv`. Mean width orders with benchmark Pearson
under every design, Spearman −0.874 (`slide_out`) to −0.972 (`patient`); median width does under
`random` and `donor` but not under `patient` or `slide_out`. The coverage range across the 12
encoders is 0.0018 under `random` and at most 0.0154 under any design. Encoder quality buys width,
not coverage.

### 6.7 The R7 per-gene join

`results/round3/A2_conditional/a2_pergene_join.csv`. Section 4.4's prediction that gene-level
shortfall correlates positively with round 2's per-gene split penalty is not supported. Spearman
over the 50 genes, averaged over the three R7 encoders within gene, is positive on six task files
and negative on five, from −0.1853 (PAAD) to +0.4694 (HCC); over the 33 task-encoder cells it is
positive on 16 and negative on 17.

### 6.8 Weighted and hierarchical conformal (A3)

`results/round3/A3_weighted/`: `a3_by_task.csv`, `a3_by_slide.csv`, `a3_by_fold.csv`,
`a3_weights.csv`, `a3_w2_basis.csv`; figures `fig_a3_coverage_vs_neff.png` and `fig_a3_hcp_by_K.png`.
Every pooled number below is recomputed in `results/round3/A3_report_numbers.csv` from `a3_by_fold.csv`: designs `patient`, `donor` and
`slide_out`, score `abs`, $\alpha = 0.10$, 966 fold cells per weighting (three encoders), each
weighting paired with `none` on the same cell and spot subset.

**W1, the embedding classifier.** Calibration and test are separable almost perfectly: held-out AUC
at least 0.9747 and at or above 0.9 in 100% of cells. The weights collapse $n_{\text{eff}}$ to a
median 2.13% of the calibration size, under 5% in 82.1% of cells and at most 15.8%. The mean coverage
move is +0.0023 but its sd is 0.0746, so individual folds move a great deal. The largest gains are on
the two-sample tasks, SKCM +0.1315 (`donor`) and +0.1511 (`patient`), HCC +0.0668 and +0.0750, LUNG
+0.0608 and +0.0620, each with wider intervals; the folds the prediction named barely move, PRAD
`slide_out` +0.0017 and CCRCC `donor` +0.0062. **W1 does substantial harm on LYMPH_IDC**: `donor`
0.8179 to 0.6680 and `patient` 0.8048 to 0.6371, by narrowing mean width from 2.4390 to 1.6347 and
from 2.3154 to 1.5208 on an $n_{\text{eff}}$ under 2% of the calibration set.

**W1b, composition only.** The eight morphology covariates separate calibration from test almost as
well as the full embedding, median held-out AUC 0.9003, so composition is slide-specific too.
$n_{\text{eff}}$ is a median 9.34% of the calibration size, at or above 30% in only 20.8% of cells.
The coverage move is +0.0056 in the mean and −0.0006 in the median, toward nominal in 58.6% of cells.
The one large move is SKCM, `donor` 0.6619 to 0.9401 and `patient` 0.6740 to 0.9685, and it deserves
a caveat rather than a headline: it rests on an $n_{\text{eff}}$ of about 4% of the calibration set,
and on `patient` it arrives with a narrower mean width than unweighted, 2.3249 against 2.5839, which
is the signature of a quantile set by a handful of heavily weighted spots, not of a repaired
interval. On IDC and CCRCC, where the prediction put the largest gains, W1b moves coverage down
slightly. W1b ran on the morphology-joined spots, a median 98.43% and a minimum 75.20% of a fold's
calibration and test spots.

**W2, resolution group and session.** W2 either has no support or has nothing to do. On the six
single-resolution-group tasks (CCRCC, COAD, HCC, LUNG, LYMPH_IDC, READ) its cell is constant and it
is identically unweighted. On the others it lacks support almost everywhere: 100% of cells on PRAD
and SKCM `donor` and `patient`, PAAD `donor` and `patient` and IDC `audited` `donor`; 91.7% on IDC
`audited` `patient` and IDC `shipped` `donor` and `patient`; 83.3% on IDC `audited` `slide_out`. The
only place it can vary and mostly has support is PRAD `slide_out`, 18.8% without support. Pooled,
its coverage move is −0.0039 in the mean and 0.0000 in the median (`a3_w2_basis.csv` gives each
task's cell structure).

**W3, hierarchical conformal.** Over 1,932 nominal fold cells at the two $\alpha$ levels, the
interval is infinite in exactly the cells where $K + 1 < 1/\alpha$, with no exception. At
$\alpha = 0.10$ that is every unit-calibrated fold: unit-calibrated folds have $K \le 6$. The only
three finite cells are SKCM `patient` at $K = 9$, covering 0.9272 in the mean (minimum 0.8844), and
that fold is block-calibrated, so **the one place HCP is usable at $\alpha = 0.10$ in this benchmark
is the place where its guarantee is for a new block of a training slide rather than a new donor.**
At $\alpha = 0.20$ the interval is finite from $K = 4$: on unit-calibrated folds CCRCC `donor`
($K = 6$) covers 0.9143 (minimum 0.2796), CCRCC `patient` ($K = 5$) 0.9258, PRAD `donor` and `patient`
($K = 4$) 0.9904 and 0.9892, and PRAD `slide_out` ($K = 6$) 0.9256 (minimum 0.5728). That is at or
above 0.80 in the mean but not per fold, and well above nominal: HCP's upper bound
$1 - \alpha + 2/(K+1)$ exceeds 1 at every $K$ on these folds and does not bind. Finite W3 lifts coverage
by 0.1470 (sd 0.0685) over `none` on 495 unit-calibrated cells and by 0.1547 (sd 0.0434) on 120
block-calibrated ones, with mean per-cell width ratios of 1.715 and 1.463; at $\alpha = 0.20$ it
lands at 0.9230 on unit folds and 0.7104 on block folds. The feasible-level fallback, the interval
at $1 - 1/(K+1)$, covers 0.9822 in the mean against a mean guaranteed level of 0.7287 over 966 cells,
and meets its guarantee in 97.62% of them.

**The two-sample tasks.** "No weighting repairs them" fails in arithmetic and holds in substance. W1
lifts HCC, LUNG and SKCM and W1b lifts SKCM to near or above nominal, but on $n_{\text{eff}}$ of 2 to
11% of the calibration set, overshooting on SKCM, while the same machinery costs LYMPH_IDC 0.15.
Weighting moves coverage a long way in whichever direction the few surviving calibration spots
point; that is not a repair.

**Plan section 4.5's own predictions.** "Coverage gain is monotone in $n_{\text{eff}}$" is too strong:
Spearman correlations of the coverage move with $n_{\text{eff}}$ as a fraction of calibration size are
+0.333 (W1), +0.146 (W1b) and +0.387 (W2), the last reflecting W2's zero moves at
$n_{\text{eff}} = 1$. "The scaled score narrows intervals at matched coverage" fails. On the
unweighted rows `scaled_clip` against `abs` moves coverage from 0.8377 to 0.8437 while mean width
rises from 2.5366 to 7.9679, a ratio of means of 3.14; the median per-cell ratio is 1.08, so the
damage is a heavy right tail. The $\hat\sigma$ lower clip hits the harness's $10^{-3}$ floor in
21.43% of cells, so the ridge on absolute residuals still predicts near-zero $\hat\sigma$ on a fifth
of folds.

**IDC `audited`**, per section 7 item 1, is tagged throughout: unweighted coverage is 0.8377 over all
966 cells and 0.8384 over the 885 without it.

### 6.9 Track D

**D1.** `results/round3/D1_download/`. The three approved sets, 105 samples (31 of them already in
the benchmark), downloaded at HEST revision `7e8d5a0b0aace41d8c8ec0f6ecea80e4ad2a61ec` and verified
file by file against the listing. The memo's check that patch count equals spot count holds on 11 of
105 samples. What holds on all 105 is that the patch barcodes are a subset of the expression
barcodes: 65,464 of 424,301 spots, 15.4%, have no patch, from 0.0000 (INT13) to 0.3591 (TENX95)
per sample (`d1_patch_spot_audit.json`, `round3_d1_d2_expansion_note.md`). HEST's own benchmark
code is built for this relation: it reads the barcodes from the embedding file and subsets the
expression matrix to them, so the patch barcode list is the reference set and the count criterion
was the wrong test. Why HEST's patching drops a given spot was not established. Section 7, item 3.

**D2.** `results/round3/D2_embeddings/`. `resnet50` embedded for all 76 samples of the two analysis
sets; `hoptimus0` (Slurm 2128386) and `uni_v2` (Slurm 2128582) were still pending on `l40-gpu` at
the time of writing. The anchor check fails (section 3). The patch windows are the same, the
coordinate axes being swapped and offset by half a patch, but the pixel values differ by a few grey
levels everywhere, with correlation 0.96 to 0.99 per sample, which is the signature of a different
resampling of the same image rather than a different region. The kept spot sets also differ between
the two layouts. The two layouts' patches are therefore not interchangeable, and no expansion result
may be read against a benchmark result until that is understood. Section 7, item 4.

**D3.** `results/round3/D3_audit/donor_lab_audit_ext.csv` (76 rows, one citation per row) and
`d3_notes.md`.

- **Breast Xenium.** The eleven `TENX191` to `TENX202` sections are from one 10x Genomics
  laboratory, eleven blocks with eleven distinct clinical profiles, mostly DCIS. With the seven
  earlier 10x and NCBI samples, all 18 breast Xenium samples are one laboratory, so the breast cell
  has no institution contrast at all, and the "disease fixed" description in section 12.6 does not
  hold.
- **The `TENX95` question.** HEST maps `TENX95` to the pre-designed-panel dataset and `TENX98` and
  `TENX99` to the entire-sample-area Replicates 2 and 1, identically in all five release tables. The
  benchmark IDC task's four samples are four distinct donors. Round 2's merge of `TENX95` with
  `TENX99` is contradicted. Section 7, item 1.
- **Kidney.** The 23 samples HEST attributes to Washington University were generated at Indiana
  University (GSE183456), on the same instrument and objective as the seven Indiana papilla samples.
  The kidney set therefore has two laboratories, Cordeliers (Paris) and Indiana, confounded with
  tumour against non-tumour, and with preservation for half the ccRCC arm. Four papilla samples are
  multi-donor capture areas and may not serve as donor units.
- **`resolution_uncertain`** clears against source for 32 samples, including all 30 Indiana kidney
  samples, where the embedded pixel size is wrong and the estimate right; HEST's `magnification` of
  20x is contradicted for those 30 (both sources state a 10x objective).
- **The held-out kidney additions.** `NCBI538` to `NCBI540` are three consecutive sections of one
  PFA-fixed organoid block, not kidney tissue; `TENX71` is unresolved.

**What this does to the source axis.** With breast one laboratory and kidney's two laboratories
confounded with tumour status, D4's source contrast is weaker than section 12.6 assumed, on top of
the no-three-laboratory limitation stated at the top of this report.

### 6.10 H0: the per-document sweep table

`results/round3/H0_housekeeping/sweep_by_document.csv`, the whole docs tree plus the README, run with
the corrected command.

| document | claims | verified | unresolved | uncited | derived mismatch | derived error |
|---|---|---|---|---|---|---|
| `README.md` | 231 | 231 | 0 | 0 | 0 | 0 |
| `docs/HEST_replication_handoff.md` | 49 | 49 | 0 | 0 | 0 | 0 |
| `docs/HEST_replication_review.md` | 112 | 112 | 0 | 0 | 0 | 0 |
| `docs/README.md` | 6 | 6 | 0 | 0 | 0 | 0 |
| `docs/WAYS_OF_WORKING.md` | 38 | 38 | 0 | 0 | 0 | 0 |
| `docs/closeout_gate_report.md` | 41 | 41 | 0 | 0 | 0 | 0 |
| `docs/deck_master_outline.md` | 162 | 162 | 0 | 0 | 0 | 0 |
| `docs/deck_speaker_scripts.md` | 98 | 93 | 5 | 0 | 0 | 0 |
| `docs/docs_clean_report.md` | 62 | 62 | 0 | 0 | 0 | 0 |
| `docs/first_year_ST_project_proposal.md` | 21 | 16 | 5 | 0 | 0 | 0 |
| `docs/hest_bench_issue_draft.md` | 56 | 56 | 0 | 0 | 0 | 0 |
| `docs/literature_landscape.md` | 20 | 20 | 0 | 0 | 0 | 0 |
| `docs/r5_idc_provenance.md` | 60 | 60 | 0 | 0 | 0 | 0 |
| `docs/round1_final_stage_report.md` | 169 | 169 | 0 | 0 | 0 | 0 |
| `docs/round2_R0_R1_stage_report.md` | 275 | 275 | 0 | 0 | 0 | 0 |
| `docs/round2_R3_stage_report.md` | 266 | 265 | 0 | 0 | 0 | 1 |
| `docs/round2_R5_stage_report.md` | 161 | 161 | 0 | 0 | 0 | 0 |
| `docs/round2_R8_stage_report.md` | 149 | 149 | 0 | 0 | 0 | 0 |
| `docs/round2_closeout_report.md` | 11 | 11 | 0 | 0 | 0 | 0 |
| `docs/round2_execution_plan.md` | 36 | 36 | 0 | 0 | 0 | 0 |
| `docs/round2_results_synthesis.md` | 105 | 105 | 0 | 0 | 0 | 0 |
| `docs/round3_A1_stage_report.md` | 153 | 153 | 0 | 0 | 0 | 0 |
| `docs/round3_d0_expansion_proposal.md` | 24 | 24 | 0 | 0 | 0 | 0 |
| `docs/round3_execution_plan.md` | 75 | 75 | 0 | 0 | 0 | 0 |
| **total** | 2,380 | 2,369 | 10 | 0 | 0 | 1 |

The ten unresolved claims are in two documents outside round 3's scope, the deck speaker scripts and
the first-year proposal, and the one derived error is the `round2_R3_stage_report.md` formula that
cites a gitignored parquet, now listed in the README's known limitations. Section 12.7's gate sweep,
over the README and `docs/round3_*.md` including this report, is run at commit time; its result is
in the commit message.

`docs/r5_idc_provenance.md` now shows 60 of 60 verified, but that is partly spurious: 41 of its
claims were unresolved before this interval and pass now only because the release tables they cite
were committed, and the checker confirms that a number is present in a cited file, not that it is
the right quantity. Its line 47 carries the `TENX95` misassignment D3 found. Section 7, item 7.
COAD `TENX111`'s 6,643 is the pre-filter grid, 73 by 91 positions, of which 505 are absent from the
AnnData's 6,138 rows (`results/round3/H0_housekeeping/tenx111_spot_count.md`).

## 7. Discrepancies, open questions and escalations

1. **The IDC `audited` label set rests on a contradicted merge.** D3 finds `TENX95` misassigned in
   `docs/r5_idc_provenance.md` and round 2's merge of `TENX95` with `TENX99` contradicted by HEST's
   own metadata in all five releases. `donor_audit.csv` is frozen per section 12.7. Until decided,
   everything built on IDC `audited` groups two donors as one: A1's and A2's IDC `audited` rows, round
   2's R5c figure of +0.0652, and `docs/hest_bench_issue_draft.md`. A2b's largest per-task deficit,
   0.283, is on IDC `audited`. Decision needed: supersede `donor_audit.csv` with a round-3 audit file,
   or not.
2. **CCRCC's donor labels are unsourced.** Round 2 records them `verified` against a GEO series
   that states no donor identifier; one pair (`INT24`, `INT4`) may be one donor profiled twice. If
   merged, CCRCC `donor` drops from six calibration units to five.
3. **The patch-equals-spot criterion is replaced by a subset relation** in D1. Decision needed:
   accept the subset relation as the D1 criterion, and decide whether expansion analyses use the
   patched spots only.
4. **The D2 anchor check fails.** The two layouts' patches differ by resampling and kept-spot set.
   Decision needed before any expansion result is read against the benchmark: re-embed the benchmark
   samples from HEST-1k patches so both sides share a layout, or characterise the difference first.
5. **Breast Xenium is one laboratory.** The breast institution cell has no source contrast.
6. **Kidney is Indiana against Cordeliers, not Washington University against Indiana,** and the
   contrast is confounded with tumour status and partly with preservation.
7. **The numeric-claim checker passes spuriously** when a cited file happens to contain the number.
   `r5_idc_provenance.md` is the live case.
8. **The Mechanisms hand-back named the block-calibrated folds as HCC, LUNG and SKCM;** they also
   include COAD `patient`, 3 of the 39. No number changes; sections 4 and 6 above use the corrected
   list.
9. **A2c's between-unit share includes the test unit** and therefore uses test labels (section 12.9
   item 4). It is labelled a diagnostic throughout.
10. **The determinism drift is attributed to node-dependent reduction order by inference only.**
11. **Section 12.9, the six memo points flagged rather than changed**, restated for the decision:
    (1) section 4's "once Nicolas approves the sets" read as a leftover, D1 ran; (2) the W3 prediction
    at $\alpha = 0.1$ "outside CCRCC's donor design" conflicts with the memo's own $K \ge 9$ condition,
    since CCRCC `donor` has $K = 6$; A3 settles it for item 2's reading, CCRCC `donor` being infinite
    at $\alpha = 0.1$ and the only finite cells SKCM `patient`, block-calibrated at $K = 9$; (3) section 2.1's
    "two task files" lists three items, and CCRCC `patient` ($K = 5$) also clears $K \ge 4$; (4) A2c's
    share, as item 9; (5) A2b's `C_unit` arm is fit on $T$ minus `C_block`, so an anchor arm was
    added and passes; (6) the determinism rerun ran first on the harness track, H0's document items
    in parallel.

12. **Corrections to the Mechanisms A3 hand-back, found on recomputation, none of which changes a
    conclusion** (`results/round3/A3_report_numbers.csv`). The hand-back's `scaled_clip` width-inflation factor was the mean of per-cell
    ratios, 2.233 on this report's cell set, quoted beside means whose ratio is 3.1412; this report
    quotes the ratio of means and the median ratio. Its LYMPH_IDC unweighted baselines differed by a
    few thousandths from the recomputed 0.8179 (`donor`) and 0.8048 (`patient`), which both
    `a3_by_fold.csv` and `a3_by_task.csv` give. The hand-back said the 16 h A2 jobs "waited 2 to 10 hours"; they waited
    about 2 h 40 min before their limits were lowered, and 5 to 12 h was the scheduler's estimate.
13. **The Mechanisms track ran read-only git queries on the local clone** against a brief that said no
    git at all, and declared it. No write was made; the local clone remained the only committer.
14. **The per-encoder A3 source CSVs stay on Longleaf** under `results/round3/A3_weighted/`; the
    committed merged tables are verified exact concatenations of them. The per-gene A3 parquets,
    about 160 MB, also stay there (gitignored).

## 8. What was not checked

- Whether the determinism drift is floating-point reduction order; thread counts, BLAS build and
  CPU model were not read on either node.
- Regression diagnostics for the five level-scale fits beyond $R^2$ and $t$ statistics.
- A2b on HCC, LUNG and SKCM, which have fewer than two units in the pool and are A2f's block group
  for that reason.
- Behaviour at $K \ge 9$ with exchangeable units: no unit-calibrated fold in the benchmark has $K$
  above 6 (block counts reach 9 in one SKCM `patient` fold).
- `scaled` in the spot strata and the A2c moments, which are `abs` only (the unclipped `scaled`
  width is dominated by the $10^{-3}$ $\hat\sigma$ floor).
- Why the neoplastic-fraction tertile bins are unequal in size.
- Whether HEST ingests the post-Xenium H&E or the DAPI image for the Xenium samples; the region of
  21 of the 23 atlas kidney samples; `TENX71`'s generating laboratory.
- The mechanism behind the D2 resampling difference, and the D2 anchor for `hoptimus0` and `uni_v2`.
- Whether W1's classifier is calibrated as a probability model; the density ratio is validated only
  by the `random` control.
- Sensitivity of any A3 result to W1's $C$, the 99.5th-percentile clip or the $\hat\sigma$ clip
  percentiles.
- Why W1 costs LYMPH_IDC 0.15 of coverage, and whether SKCM's W1b lift is stable across draws.
- W1, W1b and W2 at $\alpha = 0.20$; only `none` and W3 ran there, as the memo asks.
- Unclipped `scaled` in a paired run; A4 owns that comparison.
- HCP at $K > 9$; no fold has it.

## 9. Proposed next step

Work stops here for the decision. The decisions this report needs, in the order they block interval
3:

1. **IDC `audited`** (section 7, item 1): supersede `donor_audit.csv` with a round-3 audit file that
   separates `TENX95` and `TENX99`, or keep the round-2 file frozen and carry IDC `audited` only as a
   flagged contrast. Every IDC `audited` number in rounds 2 and 3 depends on this.
2. **The D2 layout** (item 4): re-embed the benchmark's 28 anchor samples from HEST-1k patches so
   expansion and benchmark share one layout, or characterise the resampling difference first. No
   expansion result can be set beside a benchmark result until this is settled.
3. **The D1 criterion** (item 3): accept the patch-subset relation.
4. **D4's source axis**: with breast Xenium one laboratory and kidney Indiana against Cordeliers
   confounded with tumour status, decide whether D4 runs as a two-source contrast with those
   confounds stated, or is re-scoped. The no-three-laboratory limitation holds either way.
5. **A3's consequences for interval 3.** The finding that carries forward is A2's: coverage under
   shift is set by the calibration unit and fails through scale. A3 adds that feature-based
   reweighting cannot help when calibration and test are this separable, and that HCP needs
   $K \ge 9$ exchangeable units, which no unit-calibrated fold here has. The A4 comparisons already
   transcribed in plan section 12.5 stand; the decision may wish to add HCP at $\alpha = 0.20$ on
   CCRCC as the memo's section 7 proposed, and to drop W1b from further stages.
