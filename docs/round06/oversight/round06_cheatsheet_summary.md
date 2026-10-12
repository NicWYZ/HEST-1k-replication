# Predicting expression from histology with a language model and a size-limited cheatsheet

12 October 2026. A two-page summary in place of slides.

## The question

David asked the following. An agent predicts the expression of 50 genes from H&E patches. A second agent, which has seen the measured expression, writes a text cheatsheet of limited size that the first may read. How large must the cheatsheet be for the predictions to reach a target accuracy, such as a mean Pearson correlation of 0.8?

The broader question behind it is whether one-shot or few-shot prediction with a general-purpose language model can match a pathology foundation model given the same labelled spots.

## Design

**Data.** HEST-bench's melanoma task (SKCM), two Xenium slides from two patients, with the benchmark's 50 genes and its target $\log(1 + \text{count})$. Writers learn from slide S1 (1,741 spots with a patch). Slide S2 (1,293 spots) is a second patient.

**Separate writer and predictor.** Each is a fresh agent. If one agent wrote the cheatsheet and then predicted, it would still have the measurements in its context and the size limit would mean nothing. With separate agents the file is the only channel from the measurements to the predictions.

**Three arms**, to tell copying apart from learning.

| arm | writer sees the expression of | predictor is scored on | what it measures |
|---|---|---|---|
| A | every spot of S1 | 500 spots of S1 the writer saw | how many bytes reproduce what the writer saw |
| B | spots in half of S1's blocks | 500 spots in the other half | transfer to unseen spots of the same section |
| C | every spot of S1 | 500 spots of S2 | transfer to another patient, the benchmark's own setting |

**Sizes.** 4,096, 32,768 and 262,144 bytes. Two more points anchor each arm. At $b = 0$ the predictor sees only the images. At $b = \infty$ one agent receives the labelled spots and the target images together.

**Comparators.** The benchmark's own prediction head (PCA to 256 components, then ridge regression) on `uni_v2` and `hoptimus1` embeddings, fitted on exactly the spots each arm's writer saw. There is also a size-matched codebook, which stores per-cluster gene means for $k = \min(\lfloor b/50 \rfloor, n)$ clusters of the embeddings of the writer's $n$ spots, and so asks what $b$ bytes buy a reader that has the encoder.

## Method

For gene $g$, with measured values $y_{\cdot g}$ and predictions $\hat y_{\cdot g}$ over the 500 scored spots, accuracy is HEST-bench's mean Pearson correlation

$$
\bar r = \frac{1}{50}\sum_{g=1}^{50} \operatorname{corr}\left(\hat y_{\cdot g},\, y_{\cdot g}\right)
$$

and the size needed to reach a threshold $\tau$ is

$$
b^*(\tau) = \min\{\, b : \bar r(b) \ge \tau \,\}
$$

reported as a bracket between the sizes tried.

## Implementation

- **Isolation.** Every agent ran as its own fresh Claude session, confined so that it saw only its own folder, with file names that did not reveal the sample, and could reach nothing on the network except the model's API. Deliberate attempts to read files outside the folder or to reach other hosts all failed.
- **Inputs.** The predictor saw the patches under random IDs with no positions, which is what the benchmark's encoders see. The prompts were fixed in advance and identical across arms and sizes. Writers were asked to use as much of their allowance as helps.
- **Runs.** The results below come from Claude Opus 5.5, one run per arm and size, 20 runs in all. They took 13 minutes and cost about 8 US dollars. A smaller pilot also tried Haiku and Sonnet on the unseen-region arm, shown at the end of the results.

## Results

| arm | image only | 4 KB | 32 KB | 256 KB | labels in hand | benchmark head (`uni_v2`) |
|---|---|---|---|---|---|---|
| A, spots the writer saw | 0.43 | 0.57 | 0.65 | **0.90** | 0.92 | 0.87 (in-sample) |
| B, unseen region | 0.43 | 0.49 | 0.55 | 0.62 | 0.68 | 0.76 |
| C, second patient | 0.35 | 0.65 | 0.65 | 0.67 | 0.58 | 0.68 |

![Mean Pearson against cheatsheet size](../../../results/round6/cheatsheet/C3_report/rbar_vs_bytes.png)

1. **Zero-shot prediction is already well above chance.** From images alone, Opus reached 0.43 on the first slide and 0.35 on the second patient.
2. **A cheatsheet helps everywhere.** On the second patient, 4 KB of text lifted accuracy from 0.35 to 0.65, and larger cheatsheets added only 0.025 more.
3. **It never beat the pathology model on unseen spots.** In arm B the best value was 0.62 against 0.76. On the second patient it was 0.67 against 0.68, a gap that one trial cannot separate from chance. The agent that held every labelled spot also stayed below the pathology model.
4. **The 0.8 target was reached only by copying.** In arm A at 256 KB, the writer listed every spot with an image fingerprint and its 50 gene values, and the predictor looked the scored spots up.

### Pilot across three models

Before the main grid, a pilot ran Haiku, Sonnet and Opus at high reasoning effort on the unseen-region arm (B), at three points. These were image only, a 32 KB cheatsheet, and the labelled spots in hand. Opus then reran the same three points at medium effort as part of the main grid. Each bar is one run on the same 500 spots.

| model and effort | image only | 32 KB cheatsheet | labels in hand | cost per run, US dollars |
|---|---|---|---|---|
| Haiku, high | 0.19 | 0.55 | 0.67 | 0.01 to 0.03 |
| Sonnet, high | 0.34 | 0.40 | 0.67 | 0.06 to 0.17 |
| Opus, high | 0.50 | 0.60 | 0.70 | 0.31 to 1.45 |
| Opus, medium | 0.43 | 0.55 | 0.68 | 0.14 to 0.85 |

![Pilot across models and effort](round06_cheatsheet_pilot.png)

- **Every model gained from a cheatsheet and gained more from the labels**, and none reached the pathology model's 0.76 on these spots.
- **With the labels in hand the three models nearly tie**, at 0.67 to 0.70. The models differ most when working from the image alone, where Opus is clearly ahead.
- **Sonnet's cheatsheet helped least**, 0.34 to 0.40. With one run per bar this may be that writer's draw rather than a property of the model.
- **Medium effort cost Opus about 0.4 times as much** and scored 0.01 to 0.08 lower. Only the image-only gap is larger than the roughly 0.05 that one run cannot resolve. The medium-effort runs also had two extra prompt sentences, saying there is no internet access and asking writers to use their allowance, so effort is not the only difference.

## Discussion

**The answer to David's question.** A cheatsheet reaches 0.8 only when it is large enough to hold the measurements themselves, between 32 KB and 256 KB here. Descriptions that could transfer to new tissue level off around 0.65.

**Language model against pathology model.** Given the same labelled spots, few-shot prediction with Opus did not beat a linear head on frozen pathology embeddings. It came closest on a new patient.

**What the large cheatsheets became.** From about 32 KB up, the writers added feature-extraction code to their descriptions, and at 256 KB they also wrote out training tables of every spot. The predictor then ran a small hand-built image model. So at those sizes the comparison is between a hand-built image model and a pretrained one, and the pretrained one wins.

**Where the useful content sits.** Most of what transferred to another patient fit in about 4 KB of class descriptions and per-class gene means.

**Limits.** Every value is a single trial, so differences under about 0.05 are within noise. The data are one cancer type and one pair of slides. Both slides are public and were certainly in the model's training data as datasets, although no trial could reach the network.

**Not pursued further.** The results give no reason to think a language model with a cheatsheet would outperform the pathology encoders, and the experiment does not feed the prediction-powered inference work.
