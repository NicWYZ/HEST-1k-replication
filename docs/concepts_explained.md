# Concepts in this replication, explained

*Written in response to a request to explain what these terms are, what they do, and why they exist. Numbers are from this project's own result tables, cited by path so each can be checked.*

---

## 1. Patch and pitch

These are two different lengths that are easy to conflate, and conflating them produced a real bug in this project.

**Pitch** is the spacing of the measurement grid — the centre-to-centre distance between neighbouring spots where expression was actually measured. It is a property of the *assay*. On Visium the capture spots sit on a fixed hexagonal grid; on the imaging-based tasks a pseudo-Visium grid is imposed to make them comparable.

**Patch** is the image crop handed to the encoder — the square of pixels cut around each spot, resized to 224×224 because that is what these vision models ingest. It is a property of the *pipeline*, not the assay.

**Why both exist.** The expression target comes from the spot; the image features come from the patch. They are two windows on the same location and they need not be the same size.

**Why it matters here.** Neither is constant across this benchmark. Slides were scanned at different magnifications, so the physical size of the region behind a 224×224 patch varies:

| quantity | range across the 72 samples |
|---|---|
| patch extent in slide pixels | **163 – 818 px** |
| scale factor (source region ÷ 224) | **0.727 – 3.654** |

A factor below 1 means the source region is *smaller* than 224 px and gets upsampled — that happens in 7 of 72 samples. Two samples of the **same task and same assay** (SKCM) differ by a factor of two: 409 px versus 818 px.

**The consequence.** Any hardcoded patch size — in pixels *or* in microns — is wrong for most of this benchmark. When I computed morphology features (how many nuclei sit near each spot, how large they are), I first used a fixed region and got a plausible-looking but wrong answer. The fix was to read the extraction geometry recorded in each patch file and calibrate per sample. And because patches are *larger* than the pitch — the ratio is about 1.1 — **neighbouring patches overlap**, so a nucleus can legitimately belong to more than one spot's patch and must be counted for each.

Evidence: [`instrumentation/patch_scale_sources.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/instrumentation/patch_scale_sources.csv), [`code/scripts/morphology_features_v2.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/morphology_features_v2.py).

---

## 2. Site predictability and probe design

**The question.** A "site" here means a source of batch structure: a slide, a scanner, an institution, an assay. Site predictability asks: *can you tell which site a patch came from, using only the encoder's feature vector?*

**What a probe is.** A deliberately weak classifier — logistic regression — trained on the frozen embeddings to predict a site label. It is not meant to be a good model of anything. It is a measuring instrument: if a simple linear classifier can read the site off the features, the information is unambiguously there.

**Why this exists at all.** It is the empirical test of *exchangeability*, which is the assumption underneath conformal prediction and most uncertainty quantification. Exchangeability roughly means the calibration data and the test data are drawn from the same distribution — that the model cannot tell them apart. If a probe can separate slides, then held-out data from a new slide is **not** exchangeable with your calibration data, and a single global prediction interval has no coverage guarantee there. That is the whole motivation for site-aware calibration.

**Probe design is where this gets subtle**, and I got it wrong once before getting it right.

- **What you predict** matters. Predicting *slide identity* is a different question from predicting *institution*. I originally did the former when the specification asked for the latter.
- **How you split** matters more. If you split spots randomly within a slide, the classifier can succeed by matching a test patch against its own immediate neighbours — adjacent tissue that looks nearly identical. That measures local texture continuity, not a slide-wide signature. Holding out whole contiguous *blocks* of the slide removes that shortcut.

| probe design | balanced accuracy |
|---|---|
| random spot split (shortcut available) | 0.9898 |
| spatial block split (shortcut removed) | **0.9805** |

The block design was *verified before the accuracy was read*: the median distance from a test spot to its nearest training spot widened **2.83×**. The drop of only 0.009 shows the separability is a genuine slide-level signature.

- **Confounding** matters most of all. Three labels were probed, and only one is interpretable:

| probe | accuracy | chance | usable? |
|---|---|---|---|
| assay technology | 0.9940 | 0.50 | **no** — the imaging and sequencing tasks are different organs, so this may be reading tissue |
| cohort source | 0.9378 | 0.20 | **no** — most sources appear in only one task, same problem |
| institution, within IDC | 0.6818 | 0.50 | **yes** — same tissue, same gene panel, only the institution differs |

The one clean contrast is also the weakest and is **underpowered**: with four folds, only 2 of 11 encoders is distinguishable from chance. So slides are provably identifiable; whether *institutions* are remains unresolved in this data.

Evidence: [`code/scripts/site_probe_v2.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/site_probe_v2.py), [`code/scripts/spatial_block_probe.py`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/code/scripts/spatial_block_probe.py).

---

## 3. Matching train or test sizes

**The problem it solves.** When you compare two evaluation designs and one scores lower, you want to conclude the *design* caused it. But changing a design usually changes more than one thing at once, and sample size is the sneakiest passenger.

Two distinct mechanisms, both real:

**Training size** changes how good the model is. Train on 28,521 spots instead of 7,015 and you get a better model, regardless of any distribution shift. So if design A trains on more data than design B, their difference mixes "shift" with "less training data".

**Test size and composition** changes the *metric*, not the model. This is less obvious and it bit this project. A correlation is scaled by the variance of the truth in the test set. A test set of one patient has a narrow range of expression; a test set pooling nine patients has a wide one. The same model scores higher on the wider one — see §5 below.

**What matching does.** Fix the quantity you are not interested in by construction, so only the thing you are studying varies. In the split decomposition, the random and blocked designs were built to have **exactly the fold sizes of the benchmark's own shipped folds**, so the only difference is *which* spots are grouped together. In the site-shift experiment, both training and test sizes were fixed with runtime assertions, so the only difference is whether the test slide appeared in training.

**Matching is not always sufficient, and saying so is part of the result.** In the across-task experiment I matched training volume and the dependence on task size *barely moved*. The reason is structural: matching cannot change which task is held out, and the amount of in-domain data is a property of the task. So I reported the per-task pattern instead of a single number — see §4.

An earlier version of the split comparison did **not** hold the metric fixed across designs, and that is why its headline number was wrong by more than half. Matching sizes was necessary but not sufficient; the metric had to be matched too.

---

## 4. Across task versus within task

**Within task** = train and test on the same tissue type, e.g. train on some breast slides and test on other breast slides. This is what the benchmark does.

**Across task** = train on *other* tissue types and test on the held-out one, e.g. train on colon, lung, pancreas and skin, then test on breast. It asks whether a model learns transferable morphology-to-expression structure or something organ-specific.

**Why it exists.** It is the strongest form of distribution shift available in this benchmark, and it is the realistic deployment scenario: a lab applying a model to a tissue it was not trained on.

**Two obstacles, both discovered rather than anticipated:**

1. **The target genes are incompatible.** The five imaging-based tasks' top-50 gene lists are *completely disjoint* — zero overlap. Even the underlying assay panels share only **14 genes** across all samples. So an across-task model literally cannot predict the benchmark's own targets. The experiment runs on the shared gene subset, with a within-task baseline on **the same genes**, so the comparison measures shift rather than gene-set difficulty.

2. **The answer is not a single number.** With training volume matched, the cost of going across task tracks how much in-domain data the task has:

| held-out task | in-domain training spots | shift (within − across) |
|---|---|---|
| IDC | 26,652 | +0.1453 |
| COAD | 7,825 | +0.0593 |
| PAAD | 5,047 | -0.0195 |
| LUNG | 2,603 | +0.0089 |
| SKCM | 1,517 | -0.0295 |

Read the sign: **IDC**, with the most in-domain data, loses the most by training elsewhere. The two smallest tasks are slightly *negative* — a size-matched mix of four other organs beats their own scarce data. Task diversity substitutes for task specificity when in-domain data is thin. So "across-task shift = X" would be a statement about which task you chose, not about shift, which is why this is reported as not identified.

---

## 5. Split designs

A "split design" is the rule deciding which measurements go into training and which into testing. It sounds like bookkeeping. It turns out to matter more than which foundation model you use.

The reference scale: across eleven encoders, from ResNet50 to H-optimus-0, the **entire spread in benchmark score is 0.0898 Pearson** ([`reports/results_encoder.csv`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/reports/results_encoder.csv)). Hold that number in mind.

Four designs were compared, each isolating one mechanism. All use **within-patient Pearson** so the metric is identical across designs (§5.4 explains why that is essential).

| design | rule | what it permits |
|---|---|---|
| `random` | spots assigned at random | everything: same slide, adjacent tissue |
| `blocked` | contiguous grid blocks held out per slide | same slide, but not adjacent tissue |
| `patient` | whole patients held out (**the benchmark's own**) | nothing — no shared slide or patient |
| `source_seen` / `source_unseen` | test slide's institution present in / absent from training | isolates institution |

### 5.1 Spatial adjacency

**What it is.** Patches that are neighbours on the slide are neighbouring pieces of the same tissue: same tumour region, same stain, same section, same scanner pass. They look nearly identical, and because expression varies smoothly in space, they have nearly identical expression too.

**What goes wrong.** Under a random split, a test patch's immediate neighbours are almost certainly in the training set. The model can score well by effectively looking up a neighbour rather than learning morphology→expression. It is a form of leakage that requires no bug — just an innocuous split rule.

**Size:** **0.0335** Pearson, or **0.37×** the entire encoder spread. Positive in 30/30 encoder–task cells. Measured as `random − blocked`: both designs keep the same slides and the same fold sizes, so only adjacency differs.

### 5.2 Slide identity

**What it is.** A slide-wide technical signature: staining batch and intensity, section thickness, scanner colour profile, focus. It applies uniformly across the whole slide, so unlike adjacency it survives spatial blocking.

**What goes wrong.** If any spot from a slide is in training, the model can learn that slide's signature and use it as a shortcut on the rest of that slide. This is the batch effect that breaks generalisation to a genuinely new slide.

**Size:** **0.1241** Pearson, **1.38×** the encoder spread. Positive in 30/30 cells. Measured as `blocked − patient`: adjacency is already removed in both arms, so this is the slide-level signature alone.

This is the larger of the two mechanisms — about four-fifths of the total. And it is corroborated independently by the probe in §2: slides are separable at 0.980 balanced accuracy even under block splitting, so the signature the regression exploits is demonstrably present in the features.

**Together: 0.1575 Pearson**, positive in 30 of 30 cells — **1.75× the entire between-encoder spread.** The benchmark's patient-stratified design is doing more work than the choice of foundation model.

### 5.3 Site shift

**What it is.** Distribution shift from crossing an *institutional* boundary — different hospital, different protocol, different equipment — rather than merely a new slide from the same source.

**Why it is separate.** Slide identity asks "was this slide in training?" Site shift asks "was this *institution* in training?" The second is the deployment question: a new lab adopting the model is a new institution, not just a new slide.

**Size:** **0.0419** Pearson — smaller than slide identity, but still about half the entire encoder spread. Measured only on IDC, the one task containing two cohort sources of the same tissue on the same gene panel. Both arms evaluate on a single slide, so this contrast carries no metric artefact by construction.

A separate size-matched design, varying only whether the test *slide* was seen, gives **+0.3213** across 4 encoders × 7 tasks (positive in 262/264 cells). These are different contrasts — slide novelty versus institution novelty — and are reported separately rather than averaged.

### 5.4 Metric artefact: pooled versus within-patient Pearson

**This one is not about splitting at all.** It is about how the score is computed once you have split, and it is the subtlest item on the list.

**The mechanism.** Pearson correlation is covariance divided by the product of standard deviations. The denominator includes the standard deviation of the *true* expression across whatever spots are in the test set. Pool nine patients together and that spread is large — it includes all the between-patient differences in expression. A model that merely predicts "this patient is high, that patient is low" scores well without resolving any within-tissue structure. Evaluate on one patient and that easy variance disappears; only fine-grained spatial structure is left.

**So a pooled correlation rewards test-set heterogeneity**, and designs that differ in how many patients land in each test fold are not being scored on the same thing.

| design | patients per test fold | pooled | within-patient | inflation |
|---|---|---|---|---|
| `blocked` | 8.9 | 0.6659 | 0.4639 | **+0.2020** |
| `patient` | 2.5 | 0.3736 | 0.3587 | **+0.0149** |
| `random` | 8.9 | 0.6880 | 0.4960 | **+0.1920** |
| `source_seen` | 1.0 | 0.5870 | 0.5870 | **+0.0000** |
| `source_unseen` | 1.0 | 0.5452 | 0.5452 | **+0.0000** |

Read the last column against the second: the inflation is a near-mechanical function of how many patients the test set spans. **Exactly 0.0000** for the single-patient arms. **+0.19 to +0.20** for the nine-patient arms.

**Why this matters concretely.** My first version of this analysis used pooled Pearson and reported the leakage gap as **+0.3143**. Of that, **+0.1770 — 56% — was this artefact**, because the random design's test folds pooled many patients while the benchmark's patient folds held out one at a time. The corrected figure is **0.1575**. The conclusion survived — leakage still exceeds the entire encoder ranking — but the number was inflated nearly twofold and the decomposition into mechanisms was impossible until the metric was fixed.

**The general lesson.** When comparing evaluation designs, hold the *metric* fixed as carefully as you hold sample sizes fixed. A metric whose value depends on test-set composition is not a constant yardstick, and using it to compare designs measures the designs' composition instead of their leakage. The within-patient version is computed per patient and then averaged, so test-set composition cannot enter.

---

## Why any of this exists

The downstream goal is calibrated uncertainty for spatial-expression prediction: not just a prediction per gene per spot, but an interval you can trust. Every concept above is a precondition for that:

- **Patch/pitch** — get the geometry right or the morphological covariates are wrong.
- **Probes** — test whether exchangeability, the assumption conformal prediction rests on, actually holds. It does not, across slides.
- **Size matching** — so a measured effect is attributable to the mechanism, not to sample size.
- **Across/within task** — establish how far a calibration transfers.
- **Split designs** — quantify what each boundary costs, which sets the target a site-aware method must recover.
- **The metric artefact** — because a wrong yardstick makes all four of the above unmeasurable.

The concrete handoff to the calibration work: a global conformal interval should be expected to under-cover across slide boundaries by roughly **0.124** Pearson-equivalent, and that is the quantity a site-aware method has to recover. Full argument in [`reports/motivation_draft.md`](https://github.com/NicWYZ/HEST-1k-replication/blob/main/reports/motivation_draft.md).
