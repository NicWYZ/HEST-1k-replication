# Track newtopic, results

Aggregates and novelty-check logs of round 9's track `newtopic` (branch `claude-science-newtopic`). Per-spot data stay on Longleaf, and full-text copies of papers stay out of git.

- `propose_<LENS>_queries.csv` and `propose_<LENS>_candidates.csv`, one pair per proposer subagent of step N2, in the format of `results/round9/scan/`.
- `check_<SLUG>_queries.csv` and `check_<SLUG>_candidates.csv`, one pair per checker of step N4.
- `newtopic_structured_results.json`, every subagent's structured output with its declared deviations.
- `i03/`, interval 3 on F1. `g2_*.csv` hold the derivation checks (threshold grid against interval 2, overlap against interval 2 and against simulation), `s1_liu2310_13939_vs_mine.csv` the comparison with Liu et al.'s Theorem 1 on realised features, and `audit/` the fresh auditor's note, scripts and tables. Code in `code/scripts/round9_newtopic_i03_corollary_check.py`.
