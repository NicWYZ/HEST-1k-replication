# Round 9, in preparation (from 24 October 2026)

Round 9 has no masterplan yet. The claude-science session (branch `claude-science`) is looking for a methodological core for the paper before the round opens. Its first document is the direction scan, and the round opens through `/project-state-keeping` once Nicolas has chosen among its options (decision D1 in CLAUDE.md).

## Documents

| Document | Date | Role |
|---|---|---|
| `00_prep/round09_direction_scan.md` | 24 to 25 Oct | the direction scan, with 14 candidate directions each checked for novelty by an independent subagent, four proposer subagents, an open-problem mining pass, cluster-level diagnostics of the real tasks (a shared depth factor carries 0.650 of between-donor variance on CCRCC), and an out-of-sample test of donor-level prediction. No direction survived with a substantive open remainder. Its section 4 lists the options for Nicolas |
| `00_prep/round09_direction_scan_addendum.md` | 25 Oct | the verdict of the last checker (HCPWIDTH), partly open: no finite-sample width law, switching point or valid optimal merger for hierarchical conformal sets was found, in a setting GHCP already occupies. It bears on option C |
| `00_prep/round09_stud_and_depth.md` | 26 Oct | steps S3 and S4: the studentized prediction-set idea is mostly taken (GHCP appendix B.1) and buys at most 0.130 of width even with an oracle scale; a depth-outlier donor breaks HCP coverage, and a donor depth auxiliary explains a median 0.523 of between-donor variance on CCRCC where predictions explain none |

## Results

`results/round9/scan/` (search logs and verdicts), `results/round9/diagnostics/` (cluster-level diagnostics, aggregates only), `results/round9/between/` (the between-donor head test, with predictions written before the run and scored after).
