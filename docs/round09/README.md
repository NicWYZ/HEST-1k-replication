# Round 9, two independent tracks on few-cluster inference and a fresh direction (from 26 October 2026)

Round 9's preparation (24 to 26 October, `00_prep/`) looked for a methodological core and found none that survived the literature check, along with an empirical account of where donor-level information lies in spatial transcriptomics. On 26 October Nicolas deferred the design and empirical paper (option A) and opened two tracks, each run by its own independent session on its own branch. The plan is `masterplan.md`.

**Tracks.** `fewcluster` (option B, valid inference with few labelled clusters under skew) on branch `claude-science-fewcluster`, and `newtopic` (option C, a fresh direction from the data in hand) on branch `claude-science-newtopic`. **Starts from** branch `claude-science` at the commit that adds `masterplan.md`. Each track keeps its own documents in its folders, and this guide lists them on its own branch.

## Gates

Each track's session sets its own milestones and records them here on its branch.

| Date | Track | Milestone | Report | Answered by |
|---|---|---|---|---|
| 27 Oct | newtopic | end of interval 2 | `i02/newtopic/round09_newtopic_i02_report.md` | Nicolas's choice among E1, E2 and E3, pending |
| 26 Oct | newtopic | end of interval 1 | `i01/newtopic/round09_newtopic_i01_report.md` | Nicolas, 26 Oct, "breadth first", recorded in `i02/newtopic/round09_newtopic_i02_plan.md` |

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
| `i01/newtopic/round09_newtopic_i01_plan.md` | 26 Oct, living | track newtopic's plan for interval 1, with six criteria for a direction fixed before the search, five proposer lenses, data-first diagnostics, a checker wave and predictions W1 to W3 |
| `i01/newtopic/round09_newtopic_i01_report.md` | 26 Oct | track newtopic's report of interval 1. Two waves (five lens proposers with 45 raw ideas, three open-problem miners over 61 papers) and nine checkers found nothing open. BOUNDARY, LLGCLUSTER and RRRIDGE are partly open with thin theory remainders, and the N3 diagnostics added no direction. It proposes a short feasibility interval on RRRIDGE (C1) with a stop rule, against C2 and closing the track (C3) |
| `i02/newtopic/round09_newtopic_i02_plan.md` | 26 Oct, living | track newtopic's plan for interval 2, opened by Nicolas's request for breadth-first experiments. Five feasibility tracks (RRRIDGE, BOUNDARY, SCALE, LLGCLUSTER, four fresh checkers), each with a stop rule and predictions F1 to F5 |
| `i02/newtopic/round09_newtopic_i02_report.md` | 27 Oct | track newtopic's report of interval 2. Of five breadth-first tracks, F2 to F4 stopped at lemma or proposition size (stops confirmed by fresh auditors), F5's four checkers passed nothing, and F1 survives as a short note. Ridge reduced-rank regression detects a rank-one response factor below PCA's threshold, not found in print and not a direct case of the spiked separable theorem. Options E1 (bounded note on F1), E2 (fold into option A) and E3 (close) |

## Results

`results/round9/scan/` (search logs and verdicts), `results/round9/diagnostics/` (cluster-level diagnostics, aggregates only), `results/round9/between/` (the between-donor head test), `results/round9/stud/`, `results/round9/norm/` and `results/round9/probe/` (the preparation's later runs, each with predictions written before the run and scored after). Each track writes to `results/round9/<track>/`. Track newtopic's search logs and verdicts are in `results/round9/newtopic/` (one queries and one candidates CSV per subagent, and `newtopic_structured_results.json`).
