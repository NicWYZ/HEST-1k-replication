# Round 10, track `final-runs`, decisions at gate F2

*Written on 11 November 2026 by the fifth session of track `final-runs` (frame `10b1be42-01a3-406b-b386-7580e28b98ad`). It records Nicolas's reply, given in the session, to the F2 report `docs/round10/i03/final-runs/round10_final_runs_F2_report.md` (tag `round10-final-runs-F2`, commit `02398cab`). Item numbers in brackets are those of the report's section 7, and "section 8" is the report's list of what was not checked.*

## 1. The reply

Nicolas, 11 November, in the session: "Any open question/decision that can be resolved through further analysis should be carried over to the next session, while any deviations that are settled should be recorded and decided until the round finishes."

This session reads the reply as two rules. A point that further analysis can resolve stays open and goes to the next session as work, listed in section 3 below. A deviation that is already settled is recorded in section 2 as decided, and stands for the rest of round 10 without being reopened. The scores of the report's section 5 stand as reported, including FR4 for $\theta_3$ at its threshold on CCRCC.

## 2. Settled deviations, recorded as decided for the rest of round 10

1. **FR6's frontier clause** [1] is scored on $\kappa$ of the fixed-coefficient residual $z - f$ against `kappa_sup`, from `diagnostics/f2_fr6.csv`, with `kappa_star_v1` reported beside it. FR6 is refuted under every reading.
2. **The fixed coefficient's cost** [2] is the share of genes where `fix1`'s median width exceeds `classical`'s. Plan section 5.3's claim that the median-width and mean-width readings agree was wrong. FR4 is scored on the median width, which the plan named, and the mean-width reading is reported beside it wherever the share is quoted.
3. **Rule (a) is rule (b) on the donor target** [4]. Round 4's `a_b1` and `b_cluster` are one formula there, and later stages report them as one arm.
4. **Kluger et al.'s cluster bootstrap runs under regime A's design** [5], simple random sampling of clusters with $\pi = n_L/G$, not under round 7's Bernoulli designs.
5. **The superpopulation interval is `fix1_nofpc`** [6], round 7's `round5_superpop` row, reported against the design target as a stated limit. No model term is computed, since round 5's script computes none.
6. **`frac_nonzero_y` is passed to `factor_rows` as missing** [7]. `pc1_share` is unchanged and one column of round 9's table stays empty.
7. **The switch rule's Monte Carlo error** [8] is the approximation $\text{ratio}\sqrt{2/(R - 1)}$, in place of the bootstrap over draws. The verdict, $\hat V_w$ primary for the cross-fitted form, stands.
8. **Jobs whose harness or `sacct` state reads failed with complete outputs** [10] (the first 21 regime A units, refit Slurm `8823487` and `8823488`) are taken as complete on their `PROVENANCE.txt` status, which every later stage reads in place of the harness state.
9. **$R^2_c$ in F2.6** [11] is round 9's squared correlation of donor values with donor predictions (`R2c_mean`), not F1's D12.
10. **The queue waits over four hours** [12] on the night of 10 November, given without the four-hour notice, are recorded as an escalation. Nothing further is done about them.
11. **The provenance index covers every stage** [13] through its stage argument (default F1), and each later gate runs it over all stages so far.
12. **The fourth session's missing notes and checkboxes** [14] are fixed in commit `59b7977d`.
13. **The `Pathology` sub-agent's searches before its frame-id message** [15] are recorded. No job, git or data was touched.
14. **The corpus estimands** [16] are $\mu$, with $\theta_1$ to $\theta_3$ on all six corpus tasks through option (b). The F1 report's sentence on $\theta_1$ was wrong.
15. **Option (c) is closed.** Option (b) delivered CellViT's covariates on every corpus task, so nothing is built from option (c), and its search stands as evidence (report, section 6.9).

## 3. Open points carried to the next session

Each can be resolved by further analysis. The next session plans them beside F3's methods, scores them in the F3 report, and runs them on committed code from the committed F2 inputs.

1. **The cells with one unlabelled cluster** [3]. Recompute the limits summaries of the report's section 6.4 without the 54 cells where $G - n_L = 1$, and report both versions.
2. **Regime B's toy shortfall** [9]. Explain why F1's toy enumeration gives 0.76 to 0.80 of the true variance for round 5's $\theta_3$ regime B variance while the real tasks give a median of 0.998, by comparing the toy populations' within-cluster sizes and heterogeneity with the real tasks'.
3. **The bootstrap arms under `hoptimus0` and `resnet50`** (section 8), which F2 ran under `uni_v2` only.
4. **The limits arms on `norm_refit`** (section 8), which F2 left out (1,452 of regime A's 1,722 cells).
5. **Regime B on the HEST tasks' normalised scale** (section 8). $\theta_1$ stays outside regime B, since its form does not cover it, and that is settled.
6. **LUNG_XENIUM on round 9's 42-gene subset** (section 8), tabulated beside the 343-gene rows for every comparison with round 9.
7. **The cells where coverage rises with $\kappa(e)$** (report, section 6.6, and section 8), examined one by one as the check that could contradict the shortfall's reading.

Already part of F3, and unchanged: P10.1 part 2, P10.3, FR7 and FR8.

## 4. How the work goes on

Nicolas, 10 November: the session that ran a gate does bookkeeping only, and new work starts with a new session. The next session reads this file with the plan's state block. It writes F3's methods into the plan (brief F3 items 1 to 5, with E8's literature search first) together with the plan for section 3's open points, before any job.
