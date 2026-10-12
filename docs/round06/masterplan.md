# Round 6, the cheatsheet experiment, masterplan

Written on 11 October 2026 by the oversight chat, after Nicolas confirmed the skeleton in chat the same day. The full instruction to the execution session is `i01/cheatsheet/round06_cheatsheet_track.md`. Amendments are appended at the end as dated lines and the text above them is not rewritten.

## Why this round

Round 5 closed on 9 October with the paper's estimator defined and the next methods question named (`docs/round05/README.md`, `docs/round05/i04/ppi/round5_ppi_E5_decisions.md` section 5). Before that work resumes, David proposed a short experiment by email, and Nicolas decided on 11 October to run it as round 6. The paper's next round becomes round 7.

David's design, as he described it. In the baseline, the agent's working directory holds the histology image only and the agent predicts the expression of 50 highly variable genes. In the second version, the directory holds the histology image and a text cheatsheet, and the prompt asks the agent "to use the histology-gene relationships described in the cheatsheet file as a reference to help it to make predictions". He asked to "experiment with varying size constraints for the cheatsheet and see how large the files needs to be in order to achieve a prediction accuracy of, say, 80%".

Nicolas set the purpose on 11 October. The point is not a strict natural-language account of how histology relates to expression. It is whether one-shot or few-shot prediction with a general-purpose language model can beat pathology foundation models. So no restriction is put on what a cheatsheet contains. Nicolas also raised the risk that an agent which has seen the expression leaks it into its own predictions. The design handles it by never letting a writer predict, and by scoring on spots or slides the writer did not see.

David also sent the GLMP paper (Zhang et al., "Mitigating Batch Effects in Histopathology via Language-Mediated Robust Embedding Generation", UNC, with David and Dr. Zhu among the authors). It has no expression-prediction experiment and no limit on text length, so it does not answer David's question. One of its practices carries over directly. Its prompt ablation shows that a text description keeps what the prompt asks for and drops the rest, so the prompts here are fixed in advance and identical across sizes and arms (instruction section 6.3). Two others could not be carried over. GLMP evaluates on data published after the model's training cutoff, and both SKCM slides are from 2023, so here the network is blocked during trials instead (instruction section 6.5). GLMP shows a slide to the model through about 250 patches per prompt and cluster-representative patches, and here each agent decides for itself how to look at its patches. The PDF is on Nicolas's Mac at `~/hest-1k/glmp.pdf` and is not in the repository.

## Goal

Measure, for three Claude models, how prediction accuracy on HEST-bench's metric grows with the size of a cheatsheet written by a separate agent that saw the expression, in three arms that separate copying from learning. Compare every point with pathology foundation models given the same labelled spots. The round hands David an answer to his question and hands Nicolas a reading on whether few-shot prediction with a general-purpose model can beat the benchmark's encoders. It hands nothing to the PPI paper, and no claim of novelty is made.

## Design

**Roles.** A writer is a fresh agent that sees H&E patches with their measured expression and writes `cheatsheet.txt` of at most $b$ bytes. A predictor is a fresh agent that sees H&E patches and the cheatsheet and writes predictions for every patch. A baseline predictor sees only the patches. A combined session, used for $b = \infty$, sees the labelled spots and the target patches together and predicts directly. Every session is a separate headless Claude Code process with no project context, confined to its own directory. No session ever reads a file it wrote in another role.

**Data.** HEST-bench task `SKCM`, two Xenium slides from two patients, `TENX115` (3,886 spots under tissue) and `TENX117` (1,830 spots), with the task's 50 genes and HEST-bench's own expression target (`results/round3/D0_inventory/hest_inventory.csv`). Slide S1, the one writers learn from, is `TENX115` and slide S2 is `TENX117`. Predictors see patches under new random IDs with no positions, which is what the benchmark's encoders see. Writers see positions and a low-resolution image of their section as well. In arm B that image has the held-out blocks masked out, because otherwise a writer could describe the held-out region from it and a predictor could match its patches to it.

**Scored spots.** S1 is cut into a 4 by 4 grid of blocks over the tissue's bounding box, alternate blocks are held out in a checkerboard, and spots within 165 µm of a held-out block's edge (three spot spacings, more than one patch width of 112 µm) are not scored, so no scored patch shares pixels with a training patch. S1* is 500 spots drawn from the held-out blocks and S2* is 500 spots drawn from S2, both with fixed seeds. Every arm and every comparator is scored on S1* or S2*.

**Arms.**

| Arm | Writer sees expression of | Predictor scored on | What it measures |
|---|---|---|---|
| A, same slide | every S1 spot | S1* | David's design. How many bytes reproduce the expression of spots the writer saw |
| B, held-out region | S1 spots in the training blocks | S1* | whether what the writer passes on transfers to unseen spots of the same section |
| C, held-out slide | every S1 spot | S2* | whether it transfers to another patient, which is the benchmark's own setting |

Arms A and C share their writers, so each such cheatsheet is scored on both. The writer is not told which arm it serves, because the prompts are identical across arms. A writer that spends bytes on keys for individual patches helps arm A and not arm C, so the difference between A and C mixes copying with how each writer chose to spend its bytes. The C3 analysis tags every cheatsheet by what it contains so that this can be read.

**Metric.** HEST-bench's metric. For gene $g$, $y_{\cdot g}$ is the measured target over the scored spots and $\hat y_{\cdot g}$ the predictions. Accuracy is

$$
\bar r = \frac{1}{50}\sum_{g=1}^{50} \operatorname{corr}\left(\hat y_{\cdot g},\, y_{\cdot g}\right)
$$

with a gene whose predictions are constant counted as $0$ and flagged. Two small departures from HEST-bench are deliberate. A constant gene counts as $0$ rather than being left undefined, and the score is over 500 sampled spots rather than every test spot. The comparator anchor of instruction C0.4 is computed on every spot. Over the size grid $\mathcal{B}$ and a threshold $\tau$, the size needed is

$$
b^*(\tau) = \min\{\, b \in \mathcal{B} : \bar r(b) \ge \tau \,\}
$$

where $\bar r(b)$ is the mean over replicates. It is reported as a bracket between adjacent grid sizes, or as not reached. Two thresholds are reported. One is $\tau = 0.8$, David's figure. The other is the $\bar r$ of the `uni_v2` benchmark head on the same spots, the primary comparator, so that $b^*$ says how large a cheatsheet must be for the model to match a pathology foundation model. The other comparators are reported beside it.

**Sizes.** $\mathcal{B} = \{0,\ 4{,}096,\ 32{,}768,\ 262{,}144,\ \infty\}$ bytes, where $b = 0$ is the baseline and $b = \infty$ the combined session. For scale, the expression of S1's 1,741 spots with a benchmark patch, at one byte per value, is $1{,}741 \times 50 = 87{,}050$ bytes, so the largest finite size can hold all of it three times over and $b^*(0.8)$ in arm A can be bracketed below $\infty$.

**Models.** Haiku 5.5, Sonnet 5.5 and Opus 5.5, each at medium reasoning effort (high in the C1 pilot, see the amendments), with the writer and predictor of a replicate on the same model.

**Comparators, which need no language model.**

- The benchmark's own head (PCA to 256 components and ridge, as in round 1's faithful runs) on `uni_v2` and `hoptimus1` embeddings, the two best encoders on SKCM in round 1 at 0.661 and 0.659 mean Pearson over the two directions (`results/summary/discrepancy_table.csv`). It is fitted on the same spots each arm's writer saw, so arm A's is in-sample, arm B's uses the training blocks and arm C's uses all of S1.
- A size-matched codebook. k-means on `uni_v2` embeddings of the writer's spots, with each scored spot predicted by its nearest cluster's mean at one byte per gene, so $b = 50k$ and $k = \min(\lfloor b/50 \rfloor, n)$ for $n$ writer spots, which is $81$ and $655$ at the two smaller sizes and every writer spot at the largest, where the codebook becomes nearest-neighbour lookup. It shows what $b$ bytes of labels buy a reader that has the encoder, and its centroids are not counted in $b$.

## Choices the oversight chat made

Nicolas did not ask for these. Each has a reason and he can change any of them before the session starts.

- The predictor prompt says the cheatsheet was written by someone who measured these genes and asks the agent to use it as a reference. It does not say the file describes histology-gene relationships, as David's wording did, because nothing restricts what the file contains.
- Writer and predictor of a replicate use the same model, so that each model is measured as a whole system.
- Inside a trial the agent cannot start sub-agents of its own, which keeps the cost of a trial bounded and comparable across models. It has Python with the usual scientific libraries and no pretrained model weights, since a trial has no network to fetch them.
- A trial stops after 80 turns, a cap the pilot will show to be loose or tight.

## Three points explained

**Why scored spots are a sample.** A predictor looks at every patch it is given, so its cost grows with the number of patches. Scoring 500 spots rather than all of them cuts the predictor's cost several times, and 500 spots already pin each gene's correlation to within about $\pm 0.045$. Arms A and B are scored on the same 500 spots, S1*, drawn from the held-out blocks. In arm A the writer saw those spots and in arm B it did not, while the predictor sees the same patches in both, so the difference between A and B is whether the writer had seen the scored spots and nothing else. Arm C is scored on 500 spots of S2, all of which are unseen.

**What the size-matched codebook is.** A reference that needs no language model, asking what $b$ bytes of expression information buy a reader that is a pathology foundation model. The writer's spots are grouped into $k$ clusters by their `uni_v2` embeddings, and each cluster's mean of each gene is stored at one byte, which is $50k$ bytes. A scored spot is predicted by the means of the cluster whose centre is nearest its embedding. At 4,096 bytes that allows $k = 81$. The cluster centres are not counted in $b$.

**What a replicate is.** One repeat of a condition with fresh agents. Two writers given the same inputs write different cheatsheets, and two predictors given the same cheatsheet predict differently, so each condition runs twice. For a cheatsheet condition, replicate 1 is one fresh writer with the predictors that use its file and replicate 2 is a second fresh writer with its own predictors. For the baseline and the combined session a replicate is one more fresh session. The reported value is the mean of the two, with both shown.

## Trial count

Two replicates per cell, where a replicate is one writer and the predictors that use its cheatsheet.

| Sessions per model | Count |
|---|---|
| Baseline predictors, 2 on S1* (serving A and B) and 2 on S2* (serving C) | 4 |
| Writers, 3 sizes, 2 replicates, for all of S1 (serving A and C) and for the training blocks (serving B) | 12 |
| Predictors, 3 sizes, 2 replicates, for arms A, B and C | 18 |
| Combined sessions ($b = \infty$), 1 in arm A as a check and 2 each in arms B and C | 5 |
| **Total** | **39** |

Over the three models this is 117 sessions. The pilot in the first interval runs 12 of them, which count towards the grid if the C1 memo accepts the harness unchanged. If the cost the pilot measures puts the grid beyond the budget Nicolas sets at the C1 gate, the cuts are taken in this order. First the arm A combined session runs on Haiku only. Then Haiku runs one replicate. Then the 4,096-byte size is dropped for Sonnet. Arms and models are kept.

## The track

One track, `cheatsheet`, on branch `round6-cheatsheet`, run by a Claude Code cloud session that Nicolas starts from the Claude desktop app, so that usage is billed to his account. Claude Code rather than Claude Science, by Nicolas's rule of 11 October, since Claude Science shows no advantage for this job and the trials themselves must be scriptable headless Claude Code processes. Each trial is a child process in the session's container, confined by bubblewrap to its own directory, with network only to the Anthropic API. The oversight chat checked on 11 October that a child session authenticates and runs inside such a confinement. The one step on Longleaf is a packaging job that extracts the two slides' patches, targets and embeddings, which Nicolas runs and pushes from Longleaf to a private repository, `NicWYZ/hest-r6-data`, for the session to pull. Transcripts go to the same private repository. Neither goes into the public project repository, because that would republish HEST data and could expose credentials.

In the second interval the grid can be split by model across up to three cloud sessions running at once `[proposed]`, since a model's trials depend on nothing outside it while arms A and C share writers. Each session has its own container with 2 CPUs, so the split adds compute, but all of them draw on the same usage limits of Nicolas's account. The C1 memo decides whether to split.

| Interval | Stages | Gate |
|---|---|---|
| i01 | C0, setup. Confirm child sessions in the container, build the isolation and pass the leak probes, build the data package on Longleaf and the blinded trial inputs, compute the comparators with the round-1 anchor, write and test the harness and scorer. C1, pilot. Four sessions per model, measuring tokens, cost, time and failure modes, and projecting the cost of the grid | C1 |
| i02 | C2, the grid. C3, the analysis and the closing report | C3, end of track |

## Predictions

The oversight chat's, written before any run. The instruction numbers them for scoring.

1. At $b = 0$, Opus's $\bar r$ on S1* is between 0.05 and 0.35, and Haiku's is below Opus's.
2. In arm C no model reaches the `uni_v2` comparator's $\bar r$ on S2* at any finite size.
3. In arm C Opus's combined session is above its own 262,144-byte value and below the `uni_v2` comparator.
4. In arm A no model reaches $\bar r = 0.8$ at 32,768 bytes, and at least one model reaches it at 262,144 bytes.
5. In arm B, each model's $\bar r$ at 262,144 bytes is within 0.05 of its value at 32,768 bytes, and below its arm A value at 262,144 bytes.
6. Replicate means are ordered Opus, then Sonnet, then Haiku, in at least two thirds of the pairs of arm and finite size that are run.

## Schedule

Nicolas gave no dates for this round. The estimate is three to four days for i01, a day for the gate, two to four days for C2 depending on usage limits and whether it is split, and a day for C3, which puts the close around 20 October. The PPI paper's next round starts after it.

## Open questions

R6-1, how trials are billed, was settled on 11 October. They run in a cloud session on Nicolas's own usage. R6-2, the second interval's grid and whether to split it, was settled at the C1 gate on 12 October. The full grid runs at medium effort in one session.

| # | Question | Who decides | Default |
|---|---|---|---|
| R6-3 | Whether and when results go to David | Nicolas | nothing is sent by any session |

## What closes the round

The C3 report is reviewed, its closing memo is written and its pull request is merged. Then the close check of the project-state-keeping skill runs.

## Amendments

- 11 October, evening, before any session started. Execution moved from a Claude Code session on Longleaf to a cloud session started from the desktop app, at Nicolas's request, with one packaging job left on Longleaf. Open question R6-1 was settled by this, and the split of the second interval by model was proposed. The text above was revised in place because nothing had been handed over (`docs/progress-log.md`, entry of the same evening).
- 11 October, 22:50. A cloud session cannot link to Nicolas's Mac, so the package and the transcripts move through the private repository `NicWYZ/hest-r6-data` instead. Nicolas decided that the instruction and this masterplan stay living documents on `main`, revised in place with a dated line, and that he tells the session to check for updates rather than pasting changes.
- 12 October, at the C1 gate (`i02/cheatsheet/round06_cheatsheet_C1_decisions.md`). Reasoning effort becomes medium for every trial, by Nicolas's decision after the pilot's cost and run time, so the pilot's trials are kept as a high-effort reference and every grid slot is run afresh. Trials are excluded only for signs of a leak, not for refused network attempts. One sentence telling agents there is no internet access is added to every prompt. The grid runs in one session at up to four trials at once, which settles R6-2. The scale note now uses the 1,741 S1 spots with a benchmark patch (C1 report, E1). The section "Three points explained" was added for Nicolas.
- 12 October, 02:10. Nicolas cut the grid to Opus 5.5 alone at medium effort with one replicate per cell, 20 sessions, to save time and cost (C1 memo, section 3.4). The model axis now rests on the pilot's single high-effort cell for Haiku and Sonnet, and the trial count above describes the original plan.
