# Round 9, two independent tracks on few-cluster inference and a fresh direction (from 26 October 2026)

Round 9's preparation (24 to 26 October, `00_prep/`) looked for a methodological core and found none that survived the literature check, along with an empirical account of where donor-level information lies in spatial transcriptomics. On 26 October Nicolas deferred the design and empirical paper (option A) and opened two tracks, each run by its own independent session on its own branch. The plan is `masterplan.md`.

**Tracks.** `fewcluster` (option B, valid inference with few labelled clusters under skew) on branch `claude-science-fewcluster`, and `newtopic` (option C, a fresh direction from the data in hand) on branch `claude-science-newtopic`. **Starts from** branch `claude-science` at the commit that adds `masterplan.md`. Each track keeps its own documents in its folders, and this guide lists them on its own branch.

## Gates

Each track's session sets its own milestones and records them here on its branch. None yet.

## Documents

| Document | Date | Role |
|---|---|---|
| `masterplan.md` | 26 Oct, living | the round's plan, with the two tracks, their branches and briefs, the open questions D1 to D6, and what closes the round |
| `00_prep/round09_direction_scan.md` | 24 to 25 Oct | the direction scan, with 14 candidate directions each checked for novelty by an independent subagent, four proposer subagents, an open-problem mining pass, cluster-level diagnostics of the real tasks (a shared depth factor carries 0.650 of between-donor variance on CCRCC), and an out-of-sample test of donor-level prediction. No direction survived with a substantive open remainder. Its section 4 lists the options for Nicolas |
| `00_prep/round09_direction_scan_addendum.md` | 25 Oct | the verdict of the last checker (HCPWIDTH), partly open. No finite-sample width law, switching point or valid optimal merger for hierarchical conformal sets was found, in a setting GHCP already occupies. It bears on option C |
| `00_prep/round09_stud_and_depth.md` | 26 Oct | steps S3 and S4. The studentized prediction-set idea is mostly taken (GHCP appendix B.1) and buys at most 0.130 of width even with an oracle scale. A depth-outlier donor breaks HCP coverage, and a donor depth auxiliary explains a median 0.523 of between-donor variance on CCRCC where predictions explain none |
| `00_prep/round09_normalization_check.md` | 26 Oct | library-size normalization removes about half of the shared donor factor on CCRCC (0.650 to 0.338) and leaves the predictions with no between-donor information for the median gene |
| `00_prep/round09_probe_designs.md` | 26 Oct | probe-then-label feasibility. A three-spot probe per donor narrows CCRCC intervals, but regression intervals under-cover. A take-all stratum of the one probe-atypical donor lifts CCRCC coverage from 0.825 to 0.885 at 0.779 of the width. The design is classical two-phase sampling |
| `00_prep/round09_probe_novelty.md` | 26 Oct | the PROBE verdict, mostly taken (two-phase sampling; Broska and Howes; Kluger and Bates), with the session's account of every direction examined |
| `i01/fewcluster/round09_fewcluster_brief.md` | 26 Oct | the brief for track fewcluster, with the direction, what is already known, the data facts, resources and rules |
| `i01/newtopic/round09_newtopic_brief.md` | 26 Oct | the brief for track newtopic, with the direction, what not to re-propose, the lessons of the scan and an inventory of the data in hand |
| `i01/fewcluster/round09_fewcluster_plan.md` | 26 Oct, living until S4 | track fewcluster's plan for interval 1. A finite-population Bahadur and Savage lemma (no finite-length interval is valid over all populations when $\alpha < 1 - n/G$), four candidate claims (a max-share frontier, an exactly calibrated interval, bounded residuals, what the design buys), a five-theme novelty map and feasibility computations with predictions written first |
| `i01/fewcluster/round09_fewcluster_frontier.md` | 26 Oct | the max-share frontier. Under simple random sampling of $n$ of $G$ clusters, a location and scale equivariant interval (every PPI, $t$, sign-change and wild-bootstrap interval) can be valid in finite samples over a max-share class exactly when $\kappa_0 < \kappa_2(k^\ast - 1)$, with the two-point population extremal and simple random sampling minimax among designs. At 8 of 24 this means every residual within 1.91 standard deviations. Proved by the session and again by a fresh agent, which corrected an off-by-one. Literature position provisional |
| `i01/fewcluster/round09_fewcluster_decision.md` | 26 Oct | track fewcluster's interval 1 decision. The frontier is taken forward, the bounded-residual interval and take-all design are prior art, and an exact critical value is deferred. A scale-free guarantee at 90% needs 13 of 24 clusters labelled when residuals beyond 3 standard deviations are ruled out, and 17 at 4. Interval 2 adds the tuned coefficient, stratified designs, the real tasks and a position note |
| `i02/fewcluster/round09_fewcluster_tuned.md` | 26 Oct | the frontier for PPI with a coefficient fitted on the sample, and the real tasks. The defeating samples are those on which residuals are affine in the predictions, so the frontier depends on $f$ and falls to 0.37 to 0.74 of the fixed-coefficient one on synthetic predictions. Corrects the earlier remark on spikes at high-leverage clusters. Every task's median gene lies beyond both frontiers at its middle design size. Proved twice; novelty check NOV7 pending |

## Results

`results/round9/scan/` (search logs and verdicts), `results/round9/diagnostics/` (cluster-level diagnostics, aggregates only), `results/round9/between/` (the between-donor head test), `results/round9/stud/`, `results/round9/norm/` and `results/round9/probe/` (the preparation's later runs, each with predictions written before the run and scored after). Each track writes to `results/round9/<track>/`.
