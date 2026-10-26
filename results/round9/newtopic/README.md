# Track newtopic, results

Aggregates and novelty-check logs of round 9's track `newtopic` (branch `claude-science-newtopic`). Per-spot data stay on Longleaf, and full-text copies of papers stay out of git.

- `propose_<LENS>_queries.csv` and `propose_<LENS>_candidates.csv`, one pair per proposer subagent of step N2, in the format of `results/round9/scan/`.
- `check_<SLUG>_queries.csv` and `check_<SLUG>_candidates.csv`, one pair per checker of step N4.
- `newtopic_structured_results.json`, every subagent's structured output with its declared deviations.
