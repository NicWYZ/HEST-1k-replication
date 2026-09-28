# Round 4, stage P: decision on the P1 stop

28 September 2026. From the oversight chat to the Claude Science session running the data pull, handed over by Nicolas. Answers `results/round4/data/P1_selection/STOP_NOTE.md` at commit `c31e36e`. Commit this as `docs/decisions/round4_data_P1_decision.md` and record it in `docs/round4_data_plan.md`.

## The decision

Option 1. Proceed with set V as selected (39 samples, 19.0 GB) and set L as selected (24 samples, 9.4 GB). The selection rule stands as written. Nothing is added to it.

## Why

The stop was the right call under the plan's section 9 and the selection is correct. Prediction 2 in the plan was wrong, and the reason is in the note's own table. The prediction was written from the archive's 172 labelled Visium and Xenium samples without subtracting the 113 already on disk from the benchmark and the round-3 expansion. It is scored as refuted in the P7 report, with that reason.

The two readings that would reach the predicted range are not applied. The older Spatial Transcriptomics platform (104 samples) has 100 µm spots, a few hundred spots per section and an uncertain pixel size on every sample, and no round-4 stage uses it. Samples with no label or a whitespace label (299) cannot be donor units and are what the label requirement exists to exclude. Storage is not the constraint; the tracks' needs are, and the tracks need donor-labelled samples. If either track later finds a use for the ST platform, it comes back as a proposal.

## Three things to carry into the later stages

1. **Set L's two unlabelled samples** stay in the download and in the embedding. P4 tries to resolve their donors from the source record. If it cannot, they are recorded `unverifiable`, excluded from every donor unit, and the lung task definition in P5 is built on the donor units that remain, which is 19 to 21 depending on what P4 finds. The P7 report states the count P5 used.
2. **Set L's two benchmark LUNG samples** are downloaded again in the HEST-1k layout like every other expansion sample, per the round-3 decision that the two layouts are not mixed. P5's lung task definition uses the HEST-1k layout copies, and the benchmark LUNG task is untouched.
3. **Set V's 24 samples with an uncertain pixel size** are downloaded as they are. Set V is not embedded or audited in this stage, and the flag travels with the rows so that no track groups by donor on them without noticing.

## The P0 finding

The old patch-count test in `round3_d1_download.py` printing "FAILURES PRESENT" on a valid sample is a stale check, replaced in round 3 by the subset relation. Do not edit the round-3 script. `round4_data_*` scripts use the subset relation; the P7 report lists the stale check under proposed edits.

## What continues

P1's download starts on receipt of this memo, set L first, then set V. P2 through P6 as planned. The one gate is P7. The gate rule is unchanged, and no stage after P7 starts until the oversight chat has replied to the P7 report.
