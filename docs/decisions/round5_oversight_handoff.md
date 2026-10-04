> **Active context document for the oversight chat, dated 4 October 2026.** It replaces `round4_oversight_handoff.md` as the place to start. That document's sections 3, 5, 6 and 12 still hold and are pointed to below, not repeated.

# Handoff to the next oversight session. Round 4 from start to close, the second advisor deck in preparation, and what comes next

4 October 2026. Written by the oversight chat that ran round 4 and prepared the second advisor deck, for the oversight session that takes over. Repository `NicWYZ/HEST-1k-replication`. When this was written `main` was at `b1f1a7e` and pull request #11 (branch `deck-update2-prep`) was open with the deck preparation and this handoff on it. Nicolas merges it before the next session starts, so on `main` everything named here should be present. If `docs/deck2/` is missing, the merge has not happened yet.

Start from `docs/README.md`, the reading guide. Then read this document, then the three files in `docs/deck2/`. The previous handoff, `docs/decisions/round4_oversight_handoff.md` (30 September), has the path from the literature review to the start of round 4, and the handoff before it, `round3_oversight_handoff.md` (22 September), has rounds 1 and 2.

Copies of this handoff. In the repository at `docs/decisions/round5_oversight_handoff.md`. In the Claude project as `claude/round5-oversight-handoff.md`. And as a file sent to Nicolas in the chat.

---

## 1. Roles and people

Three parties, unchanged.

- **Nicolas Weiyang Zhang** (Longleaf ONYEN `weiyang`, Slurm accounts `rc_htzhu_pi` and `rc_tengfei_pi`). First-year biostatistics PhD student at UNC. The project is his. He reads everything, reads every command before it runs, makes the decisions at his level, and says which ones need his advisors. He carries documents between sessions by hand and merges every pull request himself.
- **Dr. Hongtu Zhu** (PI) and **Dr. Daiwei (David) Zhang** (GRA supervisor, iStar author, GLMP co-author). They set spatial transcriptomics as the year's focus and want methods, with a submittable paper by spring 2027. They know spatial transcriptomics, conformal prediction and PPI. They have seen slides 1 to 6 of the first deck (21 September) and nothing since.
- **Claude Science sessions** execute on Longleaf. They do not make scope decisions. Two ran in round 4, one per track. Both tracks are closed and no session is running now.
- **You**, the oversight chat. You write instruction documents and decision memos, enforce the gate rule, review reports by reading numbers back from files, explain, do literature research, build presentations in Nicolas's style, and steer. You do not decide what goes to people outside the project.

---

## 2. How Nicolas works

These were stated by him, several of them more than once after a correction. Treat them as fixed.

**Writing.** Plain, natural prose. No em-dashes. No sentence that states something, then a colon, then the explanation. No compressed or clever phrasing. Math as rendered LaTeX, with each `$$` on its own line. Numbers at the precision the comparison needs, with the relative scale stated. Full precision belongs in files. Do not inflate length.

**Explaining.** When he asks how something works, derive it slowly and step by step. For the deck's explainer he asked for the key ideas and mechanisms, with the algebra left out, and with a sentence every time a step is skipped so he is never left wondering how a line followed.

**Documents.** Memos and instruction documents for execution sessions are complete standalone documents, never diffs. Frozen reports are not edited. Past working documents that served their purpose are not reconstructed. He wants a full handoff at every session boundary.

**Deliveries.** One file per deliverable. In this session I renamed two files between deliveries and left the old cards in the chat, and he read it as two versions. Keep a file's name fixed, overwrite it in place, and say in the message what changed. If a name must change, say so in the same message.

**Compute.** Every job runs on Longleaf by default. Nothing runs on his Mac unless he asks for that specific task in chat (section 15).

**Background and aims.** He has minimal biology by design. Expression is a signal to predict, calibrate and use for inference. His career goal is quantitative research in finance, so directions are judged by how well their skills transfer. He prefers ML venues (NeurIPS, ICML, AISTATS) or top statistics journals. He wants the paper's scope broad and useful beyond spatial transcriptomics, and he was concerned the contribution might only be existing methods applied to a new context. He frames the work as exploratory first-year work that may or may not become the dissertation.

**Standing instructions from earlier that still hold.** The benchmark-practice note is set aside and `docs/hest_bench_issue_draft.md` stays unsent. Storage on Longleaf is not a constraint.

**What he said about the second deck.** This is the most recent guidance and section 8 applies it.

1. No language about round numbers, the repository, or anything that belongs to our workflow.
2. The pivot and the revised direction are one slide, placed after the originality check.
3. A slide explains the data sets we worked with and why they were chosen.
4. His advisors know the field and the two tools. What they lack is our own methodology work and what motivated each step. So there are no background slides, and every slide must make clear why we did what it shows, so the work does not look arbitrary.
5. Where theory is involved, the formulas are on the slide, properly typeset. He gave the example that tuning $\lambda$ cannot be discussed without showing PPI++.
6. Do not mention contacting the GHCP authors.
7. Do not mention venues yet.
8. The last slide asks Dr. Zhu and Dr. Zhang how the directions sound and whether they see directions worth exploring from our work.
9. Do not build the slides until he says so.
10. Two points I raised about slide content are deferred until he has read the explainer (section 12).
11. Speaker notes cover only what is on the slide. Time budget 15 to 20 minutes.

---

## 3. How the collaborating sessions behave, and what the oversight chat got wrong

Each pattern is tied to the rule that came from it. The rules are in `docs/WAYS_OF_WORKING.md`.

**The Claude Science sessions.**

- They write a headline from one corner of a grid. The Q3 report said the donor-weighted estimator loses on every HEST task, from a table taken at the largest number of labelled donors under one target. Across the grid it gained on two of three tasks. Read the whole grid before accepting any summary sentence.
- They offer an explanation that the data cannot support. The Q5 report explained a median ratio of several hundred as "dominated by a few draws", which a median cannot be. Test the stated mechanism, not only the number.
- They read a permission to run locally as carrying over to the next interval. The rule is now that Longleaf is the default and a local run needs Nicolas to ask for that task in chat, recorded in the plan before it runs.
- Sub-agents stamped output directories with the lead's frame id in three sessions in a row. The lead now writes each sub-agent's frame id into its brief and checks every returned stamp.
- A pull request that the report said existed did not, because the token lacked the scope. Check on GitHub that a pull request exists before telling Nicolas to merge it.
- They flag what looks wrong in an instruction in a numbered list and do not change it. Those lists were right nearly every time. Read them first.
- They take wording literally. Tolerances and thresholds must be worked out by the author before they go into an instruction.

**The oversight chat, in round 4.** Nicolas should know these, since several shaped the results.

- My addendum said the tuning rule was unchanged for the design-based target. It was wrong. The rule was minimising the wrong objective, and fixing it at the Q3 gate is why the lung gain is stable in the final tables.
- I proposed a pre-test for $\lambda$ (rule d). On real data it did worse than plain cross-fitting and was dropped.
- At the Q5 gate I guessed that a diagnostic column was wrong. It was the interval that was wrong (section 7.3).
- Most of my magnitude predictions were refuted, and two were wrong in direction. The scored predictions are in section 5 of each report.
- A sentence of mine on the allocation condition was wrong and the session's theory document was right.

**The oversight chat, on the deck.** These are my own slips in the last two days, so that you do not repeat them.

- I gave three different totals for the talk's length before adding the per-slide allowances properly. Add them by arithmetic.
- I quoted the ACS sample as 380,091 people, which is the size of a different file. The task has 1,659,616. Every number goes through the numbers script.
- I said I had deleted a superseded file and had not. Check with a listing.
- I read "background" as background on the field. He meant the motivation for our own steps.

---

## 4. Where things stand

Round 4 is complete. Both tracks were accepted at their final gates and all their pull requests are merged. The results are six statements, listed in section 7.5, and they are the "new results" of the next presentation.

A literature check on 4 October changed how two of the six are described. The break-even rule for tuning is already published for independent data, and the limit in the gain theorem is a standard formula in the design of cluster-randomised trials. The comparison of the two labelling regimes was not found anywhere and is now the result to lead with (section 7.5).

The second advisor deck is prepared and not built. There is an outline in its third revision (16 slides), an explainer for Nicolas, the literature check, a numbers file built by script, and 13 figures. Nicolas is reading the explainer. Two points about slide wording wait for him, and so does the choice of cuts to reach 15 to 20 minutes. The date of the presentation was not stated in this session.

Nothing is running on Longleaf for this project. Round 5 has not been planned beyond a list of candidates (section 13).

---

## 5. Timeline

Dates before 30 September are in the previous handoff's section 2.

| dates | what |
|---|---|
| 30 Sept | Both tracks start. Reading guide and oversight documents merged (pull request #1). Addendum 1 to each track, answering the points the sessions flagged. Q1 simulation run locally at Nicolas's request. Q1 report late evening (`round4-ppi-Q1`) |
| 1 Oct | Q1 decision memo. Pull request #2 merged. Nicolas fetches ACS PUMS 2018 with cluster identifiers on his Mac. The rule that Longleaf is the default is set. C2 report in the evening (`round4-conf-C2`) |
| 2 Oct | C2 decision memo, pull request #3 merged. Q3 report (`round4-ppi-Q3`), Q3 decision memo, pull request #4 merged. Conformal final report (`round4-conf-final`), C4 decision memo, pull requests #5 and #7 merged, conformal track closed. Ways-of-working additions merged (#6). Addendum 2 to the PPI track. PPI final report (`round4-ppi-final`). Q5 decision memo with the closing unit Q5a. The three clones on Nicolas's Mac moved under `~/hest-1k` |
| 3 Oct | Q5a finished overnight. Q5a closing memo. Pull requests #8, #9 and #10 merged. `main` at `b1f1a7e`. Round 4 closed. First outline of the second deck and the explainer drafted |
| 4 Oct | Nicolas's eleven points on the outline. Literature check. Outline revision 2, explainer corrections, numbers file, figures, pull request #11. His clarification on background, outline revision 3 (16 slides). This handoff |

---

## 6. The path before round 4

The previous handoff's section 3 is the full account and still holds. In brief, for orientation.

The literature review found that accuracy of histology-to-expression prediction has a low ceiling and that almost nobody asks how to do valid inference with the predictions. Two topics followed, calibrated uncertainty under cohort shift (Topic A) and inference for population quantities (Topic B). The replication in rounds 1 and 2 was exact and found that the unit of inference is the donor. Round 3 ran the first experiment for each topic. Coverage turned out to be a property of how calibration data are held out. Feature reweighting could not repair the shift. The public data have no institution axis. Topic A as framed was retired. An originality check on 28 September then found that PPI is the survey-sampling difference estimator (Mozer 2026), so a cluster-robust PPI is not a new estimator, and that GHCP (Mallick, Tchetgen Tchetgen, Dobriban and Lee, August 2026) had taken the labelled-test-group conformal setting six weeks earlier. The paper was reframed as "Labelling budgets for prediction-powered inference with clustered data".

One correction from that period must be stated at the next presentation. Two breast-cancer samples presented on 21 September as probably one donor are two donors from one laboratory.

---

## 7. Round 4, chronologically and with reasons

### 7.1 The PPI track, first interval (30 September to 1 October)

**What was believed.** Round 3's estimator had known soft spots. Its variance carried no finite-population correction although its target was a fixed set of donors, and $\lambda$ was tuned on the same donors it was applied to.

**What was found.** In simulation, tuning $\lambda$ on the same clusters under-covers with four clusters (0.86 to 0.87 at nominal 0.90) and gives the narrowest intervals, so the method that looks best is the one that fails. Cross-fitting over two halves of the labelled clusters restores 0.90. For the design-based target the finite-population factor is needed, and without it coverage rises to 0.98 with 12 clusters labelled. No bootstrap was competitive. The spot-weighted slope has skewed donor contributions and its $t$ interval under-covers by three to five points even with twenty donors.

**What changed.** The donor-weighted estimand became the paper's primary one. The textbook form of the estimator, with predictions over the whole population, was adopted for the design-based target. The `ppi_py` census file has no cluster identifiers, so Nicolas fetched ACS PUMS 2018 himself through `folktables`. The raw fetch is on his Mac at `~/hest-1k/acs_pums2018` (2.6 GB, not in the repository) and a verified copy is in the Longleaf project tree.

### 7.2 The PPI track, second and third intervals (1 to 2 October)

**The gain theorem and what it rests on.** With many units per cluster, the PPI-to-classical variance ratio tends to $1 - R^2_{\text{cluster}}$, where $R^2_{\text{cluster}}$ is the squared correlation across clusters of the true and predicted cluster-level contributions. The session pointed out that for the donor-weighted slope and difference a cluster's contribution is a within-donor contrast, so a donor-constant shift in the predictions cancels. Recalibrating donor offsets therefore cannot help and was dropped.

**The tuning objective.** I read the full grid at the Q3 gate and found $\lambda$ falling as more donors were labelled. The rule was minimising a variance that includes a term for the unlabelled donors, which the design-based form does not have. The corrected rule tunes $\lambda$ on the labelled donors alone. It is the regression coefficient of survey sampling and is named `c_crossfit_design` in the tables.

**The tuning cost.** The gap between the observed ratio and the floor is the cost of estimating $\lambda$ from a few clusters,

$$
\text{ratio} = 1 - R^2_{\text{cluster}} + \text{MSE}(\hat\lambda)\,\frac{\sigma_p^2}{\sigma_u^2},
$$

which gives the break-even count $n_L > 4 + 2/R^2_{\text{cluster}}$. This explains why lung and census income gain and most kidney cases do not. It explains the pattern across tasks and does not predict single cells.

**The two regimes.** Regime A labels a few clusters fully. Regime B labels a few units in every cluster. In regime B, for the design-based target, every cluster is observed, the clusters act as strata, and the ratio is $1 - R^2_{\text{within}}$. At equal numbers of labelled units regime B gave the narrower interval on every task when regime A had 8 or fewer donors. The optimal number of units per cluster is $m^\star = \sqrt{(c_{\text{cluster}}/c_{\text{unit}})\,\sigma^2_{\text{within}}/\sigma^2_{\text{between}}}$, and a predictor moves it toward more clusters exactly when $R^2_{\text{within}} \ge R^2_{\text{cluster}}$, which held for every encoder except `uni_v2` on kidney cancer.

### 7.3 The PPI track's closing unit (2 to 3 October)

Two things were found in the final tables and fixed in a one-day unit, Q5a.

**The spot-weighted PPI rows are nuisance rows.** A permuted predictor, which carries no information, cut the variance of spot-weighted estimands to 0.29 to 0.40 of classical on kidney cancer and 0.09 to 0.13 on lung. What it removes is the between-donor variance of the design-weight sums. The rows stay in the tables marked `nuisance`, and the paper treats this as a finding about the choice of estimand.

**The design-target variance under cross-fitting was missing a term.** With two halves carrying different $\lambda_g$, each labelled donor's contribution carries $(\lambda_g - c_U)\bar F$, where $c_U$ is the average $\lambda$ over labelled donors and $\bar F$ the population mean of the prediction term. Without it the estimated variance on census income by state was 204 to 1,069 times the empirical one. With it the ratio is 0.89 to 1.04. On the HEST tasks the term is negligible because the slope weights are centred. The corrected interval is `textbook_t|fpc|lin`. The derivation is in `docs/decisions/round4_ppi_Q5a_closing.md` and the estimator definition.

One qualification for the paper. The closing page's ranges for the HEST tasks are for the within-donor slope $\theta_3$. The group difference $\theta_2$ shows smaller gains and is reported beside it.

### 7.4 The conformal track (30 September to 2 October)

**What was believed.** That a method sharper than hierarchical conformal prediction (HCP) might exist when the test cluster has no labelled units, and that GHCP would be the method when it has some.

**What was found.** GHCP was reproduced from its released code, 254 of 254 simulation values and 53 of 53 values in its census tables. Four candidate methods with no labelled test units were tried against a criterion fixed in advance, and none went forward. On real data with 10 calibration donors, GHCP with 5 or 10 labelled spots is 1.2 to 1.5 times wider than HCP with none, because donating one reference group costs the whole margin when $K$ is near $1/\alpha$. A plain split inside the test donor that calibrates on all its labelled spots (`within_plain`) is valid from 9 labelled spots at 90%, covers 0.91, and is about half GHCP's width. From 25 spots the recentred half-split (`within`) is narrower still. The cross-donor shortfall of the naive interval is real on kidney cancer (0.86) and small on the other tasks.

**The lower bound.** Two short propositions for $K + 1 < 1/\alpha$. Every valid method must return an infinite set with probability at least $1 - \alpha(K+1)$, and a method that is finite must over-cover by a stated amount. The scoping was closed with its time cap unspent. Whether HCP can be beaten when $K + 1 \ge 1/\alpha$ stays open.

**Two discrepancies in GHCP's released code.** Its restricted pool keeps one more group than the paper's equation, and it resolves an exact quantile tie upward. Whether the authors are told is for Nicolas with David and Dr. Zhu. It is not mentioned on the slides.

### 7.5 The six results, and what the literature check did to them (4 October)

1. A valid interval with 4 to 12 labelled clusters. Cross-fitted $\lambda$, a cluster-level variance, a $t$ reference, the finite-population factor, and the extra term of section 7.3. The combination was not found in the literature. Each ingredient is known.
2. What predictions buy. The ratio tends to $1 - R^2_{\text{cluster}}$. This is the cluster-randomised-trial formula for a covariate (Raudenbush 1997; Bloom, Richburg-Hayes and Black 2007), carried over to a black-box predictor. It was not found stated for PPI.
3. The price of tuning. The break-even rule is the rule of Mani, Xu, Lipton and Oberst (arXiv:2505.20178) for independent data, with clusters in place of units. The consequence is ours, that the count that matters is labelled clusters and the $R^2$ that matters is the cluster-level one.
4. Where to put the labels. The comparison of the two regimes with a predictor and a cost per cluster and per unit was not found anywhere. **This is the result to lead with.**
5. Prediction sets for a new cluster, mapped over calibration clusters and labelled test units. The margin over GHCP is narrow and sits in what that paper did not vary (fewer than 20 groups, and a plain within-group split). The first lower-bound proposition follows closely from Tibshirani, Barber and Ramdas (arXiv:2608.27310, 27 August 2026). The coverage floor was not found.
6. One design for both targets. Tens of labelled units in every cluster serve the confidence interval and the prediction set together.

The check also found that the open conformal question must be reworded, because Tibshirani, Barber and Ramdas settle optimality for ordinary exchangeable data. It stands only for grouped data.

**How far to trust the literature check.** Pages were read through a tool that returns summaries. Titles, authors and dates are confirmed. Theorem numbers and quoted formulas are not. `docs/deck2/deck2_literature_check.md` section 6 lists what was confirmed, what was only reported, and what nobody has read. The GLMP paper could not be found and David should be asked for the reference.

---

## 8. The current plan

### 8.1 The paper

Working title "Labelling budgets for prediction-powered inference with clustered data". Methodology first, with spatial transcriptomics as the main application and census income as the second. The section plan in the previous handoff's section 4 stands with these changes from the literature check.

- Lead with the design result (regimes A and B, the allocation). Present the gain and tuning results as the two facts it rests on, each with its source.
- Cite Mani and colleagues, Lavenberg and Welch, Raudenbush, Bloom and colleagues, Hagesæther and Zhang, Kennel and Valliant, Kluger and colleagues, Shirota and Mozer in the first two pages.
- Add a comparison with GHCP in its own setting of 20 groups.
- State the lower bound as a short proposition that follows from recent universality results, with the coverage floor as the part not found elsewhere.
- Treat the spot-weighted rows as a finding about estimand choice.

The previous handoff named ICML 2027 as a possible venue. Nicolas has asked that venues not be mentioned to the advisors yet, so this stays out of the deck.

### 8.2 The second advisor deck

Nicolas's structure, from `ST_presentation2.pdf`, is two parts. Part 1 is from last time (our read on the literature, the two original topics, efforts toward them). Part 2 is since last time (roadblocks, the pivot, the originality check, revised directions, new results). `docs/deck2/deck2_outline.md`, revision 3, maps it to 16 slides.

| slide | content | figure |
|---|---|---|
| 1 | title and roadmap | |
| 2 | our read on the literature | |
| 3 | the two original topics | |
| 4 | efforts toward the two topics, with the correction on the two breast samples | three-panel strip, not yet assembled |
| 5 | roadblocks | F1 |
| 6 | what the first experiments established | F2 |
| 7 | the originality check | |
| 8 | the pivot and the revised direction | F3 |
| 9 | the data sets and why they were chosen | table |
| 10 | result 1, a valid interval | F4 |
| 11 | result 2, what predictions buy | F5, F6 |
| 12 | result 3, the price of tuning | F7, F8 |
| 13 | result 4, where to put the labels | F9, F10 |
| 14 | result 5, prediction sets for a new donor | F12, F11 |
| 15 | result 6, one design for both targets | table |
| 16 | summary, next steps, questions for the advisors | |

The per-slide allowances sum to 23.5 minutes. The outline carries a cut list that reaches about 20, and one further step below that. Nicolas chooses.

The explainer's part A uses the same slide numbers (10 to 15), so it and the outline agree.

**Still to do before the deck can be built.**

- Nicolas's answers on the two held points and the cuts (section 12).
- The strip for slide 4, from the first deck's figures `figures/deck/fig05_r2_ladder`, `fig06_session_signature` and `fig07_theta_and_variance`.
- Numbers on slides 2 to 6 that come from rounds 2 and 3 or from the literature are not yet in the deck's numbers file. The file has the coverage-by-design and interval-coverage rows. It does not have the classifier AUC of 0.97, the 2% effective sample size, the 1.84 scale ratio, the 30 to 40% between-donor share, or the three literature facts. Add them to `code/scripts/deck2_numbers.py` from the files in section 9 before the slides quote them.
- The numeric-claim sweep has not been run over the three `docs/deck2/` documents. Run it before the deck is handed over.

**How to build it, when he says.** Use the Slides artifact type if the session offers one, as the first deck was. Figure on the left and bullets on the right. Short speaker notes that cover only what is on the slide. Apply every point of section 2's list. Keep the practice of a numbers file built by script and figures from committed scripts. The first deck's authoritative file is `docs/deck_round2/HEST-1k Replication Update.pptx`.

---

## 9. Key numbers, with the files they come from

Every number here was read back in this session from `results/summary/deck2_numbers.csv`, which `code/scripts/deck2_numbers.py` builds from the primary files named below, or from the primary file directly where marked. Paths are from the repository root. Round-3 numbers not listed here are in the previous handoff's section 5.

**Data sets** (`results/round4/ppi/Q5_joint/q5_cluster_table.csv`, `results/round4/ppi/Q4a_recompute/q4a_table61.csv`, `results/round4/ppi/Q0_setup/acs_pums2018/acs_pums_task_def.json`).

| task | clusters | units | median units per cluster | genes |
|---|---|---|---|---|
| kidney cancer, Visium (CCRCC) | 24 donors | 74,220 spots | 2,893 | 50 |
| Indiana kidney, Visium | 25 donor units | 31,425 spots | 673 | 50 |
| lung, Xenium | 15 donors | 19,083 patches | 1,124 | 343 |
| census income, ACS 2018 | 51 states or 265 California areas | 1,659,616 people | | |

**Roadblocks and first experiments.**
- Coverage at nominal 0.90 by calibration design. Random 0.89, slide-out 0.86, donor 0.80, patient 0.79 (`results/round3/A1_coverage/a1_coverage_by_design.csv`).
- Calibrating on other donors 0.86 against blocks of the training slides 0.74 (`results/round3/A2_conditional/a2_unit_intervention.csv`).
- Minimum held-out AUC of the calibration-against-test classifier 0.97, median effective sample size 2.1% (`results/round3/A3_report_numbers.csv`, read directly).
- Interval coverage for a population quantity. Spot-level 0.04, donor-clustered with $t$ 0.91, donor bootstrap 0.71 (`results/round3/B2_semisynthetic/b2_coverage.csv`).
- Prediction-to-target scale ratio 1.84 (`results/summary/deck_numbers.csv`, row citing `results/round2/R1b_heads/r1b_ladder_pooled.csv`, read directly).

**Result 1** (`results/round4/ppi/Q1_estimator/q1_coverage_by_G.csv`, `q1_report_numbers.csv`, `results/round4/ppi/Q5a/q5a_design_variance_before_after.csv`).
- Simulation, superpopulation target, four labelled clusters. Tuning on the same clusters covers 0.87 and 0.86 under the two rules. Cross-fitted covers 0.90 at every cluster count from 4 to 20.
- Width against classical at four clusters with an informative predictor. Same-cluster tuning 0.74 and 0.61, cross-fitted 1.01.
- Design target without the finite-population factor. 0.91, 0.93, 0.95, 0.98, 1.00 at 4, 6, 8, 12, 20 labelled clusters. With it and cross-fitting, 0.89 throughout.
- Census income by state, estimated over empirical variance. 204 to 1,069 before the extra term, 0.89 to 1.04 after.

**Result 2** (`results/round4/ppi/Q2_theory/q2_cluster_r2.csv`, `results/round4/ppi/Q4a_recompute/q4a_table61.csv`, `results/round4/ppi/Q4_tables/q4_gene_axis_summary.csv`, `results/round4/ppi/Q2_theory/theorem_v3/q2_sim_theorem_v3.csv`).

| task, predictor | $R^2_{\text{cluster}}$ | floor | observed ratio, 8 labelled clusters |
|---|---|---|---|
| lung, `hoptimus0` | 0.73 | 0.27 | 0.43 |
| lung, `uni_v2` | 0.71 | 0.29 | 0.47 |
| lung, `resnet50` | 0.65 | 0.35 | 0.54 |
| census by state | 0.70 | 0.30 | 0.43 |
| census, California areas | 0.88 | 0.12 | 0.19 |
| kidney cancer, `uni_v2` | 0.44 | 0.56 | 0.84 |
| kidney cancer, `hoptimus0` | 0.29 | 0.71 | 0.96 |
| kidney cancer, `resnet50` | 0.20 | 0.80 | 1.00 |
| Indiana, `hoptimus0` | 0.19 | 0.81 | 0.98 |

- Permuted predictor, observed ratio 0.96 to 1.07 on every task at 6 or more labelled clusters.
- Across 459 genes on kidney cancer, rank correlation of the gain with cluster-level $R^2$ is $-0.86$ to $-0.90$, and with unit-level correlation $-0.36$ to $-0.51$.
- Simulation with the oracle $\lambda$. The ratio sits 0.03 to 0.08 above the floor.
- Spot-weighted rows with a permuted predictor. 0.29 to 0.40 on kidney cancer, 0.09 to 0.13 on lung (`results/round4/ppi/Q5a/q5a_spot_weighted_permuted.csv`).

**Result 3** (`q2_cluster_r2.csv`, `q2_sim_theorem_v3.csv`).
- Predicted against observed tuning cost in simulation, largest difference 0.043 over 24 settings.
- Break-even counts. Lung 6.7 to 7.1. Census 6.3 and 6.8. Kidney cancer 8.6 (`uni_v2`), 11.0, 14.0. Indiana 14.7, 18.4, 43.0.

**Result 4** (`q2_cluster_r2.csv`, `results/round4/ppi/Q4_tables/q4_main_table.csv`, `q4_report_numbers.csv`, `results/round4/ppi/Q3_regimes/q3_report_numbers.csv`, `results/round4/ppi/Q2_theory/q2_report_numbers.csv`).
- Regime B over regime A width at an equal budget of 2,400 labelled units. Kidney cancer 0.46 and 0.64 when A has 4 and 8 donors. Indiana 0.74 and 0.92. Lung 0.40 and 0.58.
- With a cluster costing 10 units, regime B is narrower in 216 of 232 comparisons.
- Regime B, PPI width over classical. Kidney cancer 0.80 to 0.84 for the encoders and 0.87 for the permuted predictor. Indiana 0.83 to 0.84 and 0.88. Lung 0.42 to 0.49 and 0.66. The predicted value $\sqrt{1 - R^2_{\text{within}}}$ is within 0.05 of each.
- $R^2_{\text{within}}$. Kidney cancer 0.37 to 0.38 for the encoders and 0.24 permuted. Lung 0.77 to 0.83 and 0.57.
- Optimal units per cluster at a cost ratio of 100, classical then with a predictor. Kidney cancer 121 and 108. Indiana 236 and 188. Lung 172 and 121. Census by state 379 and 89.

**Result 5** (`results/round4/conformal/C3_real/c3_report_numbers.csv`, `c3_o_sweep_by_task.csv`, `results/round4/conformal/C2_candidates/lower_bound/c2_lb_beta_star.csv`).
- HCP on kidney cancer by calibration donors $K$. Coverage 0.97 and width 1.95 times the naive interval at $K = 10$, falling to 0.94 and 1.36 at $K = 20$. The naive interval covers 0.86 to 0.87 throughout.
- At $K = 10$, mean width, kidney cancer. HCP with no labelled spots 4.11. GHCP 5.46, 5.06, 4.43 at 5, 10, 25 labelled spots, covering above 0.99. Plain within-donor split 2.32 at 10 spots, covering 0.91, and 2.30 at 25. Recentred split 2.14 at 25, covering 0.93. Indiana and lung show the same order.
- Lower bound at 90%. Forced probability of an infinite set 0.50, 0.40, 0.30, 0.20, 0.10 at $K = 4$ to 8. Coverage floor for finite methods 0.951, 0.923, 0.910, 0.903, 0.901.
- GHCP reproduction, 254 of 254 simulation values and 53 of 53 census values.

**Result 6** (`results/round4/ppi/Q5_joint/q5_joint_design.csv`).

| task | labelled units per cluster | interval width against classical | its coverage | cheapest valid set | its coverage |
|---|---|---|---|---|---|
| kidney cancer | 14 | 0.83 | 0.89 | `within_plain` | 0.91 |
| kidney cancer | 84 | 0.81 | 0.89 | `within` | 0.92 |
| Indiana | 6 | 0.84 | 0.90 | GHCP, width 4.56 | 1.00 |
| Indiana | 51 | 0.84 | 0.90 | `within` | 0.92 |
| lung | 36 | 0.43 | 0.90 | `within` | 0.93 |

The outline's slide 15 shows four of these rows and leaves out Indiana at 6, where GHCP is the only finite set. Its line "not yet tested, fewer than 6 labelled spots per donor" is consistent with the file.

**Not established.** The list is the explainer's part C. The three that matter most for the talk are these. The final design-target tuning rule and the corrected variance were never run in simulation. On the real tasks the final design-target interval covers 0.85 to 0.89. And the reading that regime B's gain on the Visium tasks is mostly the design and not the encoder has no dedicated check.

---

## 10. What is running now

Nothing. Both round-4 sessions finished and both tracks are closed by memo (`round4_conformal_C4_decisions.md`, `round4_ppi_Q5a_closing.md`).

| branch | state |
|---|---|
| `main` | `b1f1a7e` before pull request #11 is merged |
| `round4-ppi` | `8cca44f`, merged as #8, kept |
| `round4-conformal` | `e208907`, merged as #7, kept |
| `deck-update2-prep` | pull request #11, open when this was written |

Tags added in round 4 are `round4-ppi-Q1`, `round4-ppi-Q3`, `round4-ppi-final` (the report before Q5a), `round4-conf-C2` and `round4-conf-final`. There is no tag for the close of round 4 on `main`. If one is wanted, it is Nicolas's to create.

The Longleaf project tree `/work/users/w/e/weiyang/hest_replication` was held on `main` at `round4-data-v2` as the data root during the round. I could not check its present state from this session. The track code clones are under `/work/users/w/e/weiyang/hest_code/`.

---

## 11. What to look for in what comes next

No reports are due. Three things will arrive.

**Nicolas's reading of the explainer.** He may ask for derivations. Give them slowly, from `docs/round4_ppi_theory.md` and `docs/round4_conf_lower_bound.md`, and say when a step is skipped. He will then settle the two held points.

**The deck build.** Before any slide text is final, check each number on it against `results/summary/deck2_numbers.csv`, add the missing rows named in section 8.2, and run the sweep. Check each slide against the list in section 2. Check that the slides for results 2 and 3 say "carried over to clusters" and name their sources, since an advisor who knows Mani and colleagues or the trial-design literature will otherwise think we claim them.

**The advisors' response.** The last slide asks three questions. Their answers decide round 5's scope, so do not write round-5 instructions before the meeting unless Nicolas asks.

One known fault in the tooling. `code/scripts/verify_numeric_claims.py` raises a `TypeError` in `_small_file_values` when a cited file has empty cells. I worked around it inside one process to get a clean sweep for pull request #10 and did not change the script. By the project's own rule a false failure is fixed in the checker, with a fixture, so this is owed.

---

## 12. Open decisions and who owns them

| decision | owner |
|---|---|
| Slide 11. Whether to add a footnote that the floor (measured on all donors) and the observed ratio (masking draws at 8 labelled donors) come from two computations | Nicolas, after reading the explainer |
| Slide 13. Whether to say that most of regime B's gain on the Visium tasks comes from the design and not the encoder (permuted 0.87 against 0.80 to 0.84 on kidney cancer, 0.66 against 0.42 to 0.49 on lung) | Nicolas, after reading the explainer |
| Which cuts bring the talk to 15 to 20 minutes | Nicolas |
| When the slides are built | Nicolas |
| Whether to tell the GHCP authors about the pool rule and the tie convention, or raise the lower bound with them | Nicolas with David and Dr. Zhu. Never a session's decision |
| Which result the paper leads with, and whether the scope is right for a first paper | Dr. Zhu and Dr. Zhang, asked on slide 16 |
| Venue | Nicolas with his advisors, not raised yet |
| The GLMP reference | ask David |
| Whether round 5 runs, and with what scope | Nicolas, after the meeting |
| A tag on `main` for the close of round 4 | Nicolas |
| The physical reorganisation of `docs/` into round folders, which the reading guide deferred until round 4 was merged | you propose, Nicolas decides. It needs a script that rewrites references and a sweep afterwards |
| The D4 probe rerun, the ten unresolved claims in two pre-round-3 documents, the `r5c_leak_summary.csv` reading | carried from the previous handoff, round-5 housekeeping |
| Whether the benchmark note is written | Nicolas and David. Set aside |

---

## 13. Next steps, and what is not planned

**Before the presentation.** Settle section 12's first four rows. Finish the preparation in section 8.2. Build the deck. Read the full texts that the slides lean on before they are cited by theorem number, which are Mani and colleagues (the cross-fitting corollary), Tibshirani, Barber and Ramdas, and Shirota.

**Round 5 candidates,** in the order the closing memos left them.

1. Active cluster selection, which clusters to label and not only how many. The inputs are in `results/round4/ppi/Q5_joint/q5_cluster_table.csv` (261 donor rows with mean embeddings, residuals and offsets).
2. A regression-form spot-weighted estimand, under which donor-level weight sums cancel and a PPI gain would be real.
3. A comparison with GHCP in its own setting of 20 groups.
4. The paper's joint design section from the Q5 and C3 outputs, and writing.
5. A simulation of the final design-target rule and variance, which were validated only on masking draws.
6. The reading list in the literature check's section 6.

**Not planned.** Any institution axis from HEST-1k. Any train-time method. Any further data download. Any further search for a method sharper than HCP with no labelled test units. Recalibration of donor offsets. A pre-test for $\lambda$. Any bootstrap interval.

---

## 14. Dead ends

The previous handoff's section 12 stands. Round 4 added these.

- **A pre-test for $\lambda$.** The draws that pass are the ones with a large estimated slope, so it selects a biased $\lambda$. Ratio 1.17 against 1.03 for plain cross-fitting on kidney cancer `uni_v2` with 16 donors.
- **Bootstrap intervals with few clusters.** The percentile cluster bootstrap under-covers and the wild cluster bootstrap did not beat the plain interval.
- **Tuning $\lambda$ on the clusters it is applied to.** Under-covers with few clusters while looking narrowest.
- **Recalibrating donor offsets.** No out-of-sample skill, and the donor-weighted estimands are invariant to it.
- **Two-way clustering.** No HEST task has a second grouping that crosses the donor.
- **Spot-weighted PPI rows as evidence of a gain.** A permuted predictor produces the same gain.
- **Four candidate prediction-set methods with no labelled test units.** A smoothed HCP, a model-based donor quantile, an adaptive score, and a rule switching between pooled and HCP. None met the criterion. The switch rule is invalid, with a counterexample.
- **GHCP with a few labelled units at about 10 calibration clusters.** Wider than HCP with none.
- **The `ppi_py` census file for anything clustered.** It has no cluster identifiers.
- **Claiming the break-even rule or the gain limit as new.** Both exist for simpler settings.
- **Background slides on the field or the tools.** The advisors know them.

---

## 15. Standing rules and conventions

The gate rule goes verbatim into every memo to an execution session.

"Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. Contact with anyone outside the project is never the session's decision."

The previous handoff's section 13 stands. `docs/WAYS_OF_WORKING.md` now also carries the rules from round 4, each with the failure behind it.

- Longleaf is where work runs. A local run needs Nicolas to ask for that task in chat, is written into the plan before it runs, does not carry across a gate, and records host, library versions and md5s in place of the Slurm fields.
- A job that has waited four hours is reported to Nicolas and keeps waiting. A pending job may be resized from a sibling's measurement or switched between the two approved accounts. It is not moved.
- A job runs from its own output directory, never from inside the code clone.
- The lead writes each sub-agent's frame id into its brief and checks the stamp before merging.
- Read the whole grid before writing a headline.
- Work out a method's own expected value before setting a tolerance on "nominal".
- Each `$$` on its own line.
- A file too large for GitHub is committed compressed with the md5 of the plain file recorded.
- Pull requests at gates, merged by Nicolas with a merge commit. No rebase, squash, amend or force-push.

For the deck. Every number from the numbers file built by script. Every figure from a committed script, with plain labels. No number typed in.

Every prediction is written before the run and scored afterwards. Every number is read back from its file before it is asserted.

---

## 16. Documents and where they live

**Added in round 4 and after, in the repository.** The reading guide `docs/README.md` lists each with its date and role.

- PPI track. `docs/round4_ppi_plan.md`, `round4_ppi_Q1_report.md`, `round4_ppi_Q3_report.md`, `round4_ppi_final_report.md` (its closing page is the summary, and section 10 is Q5a), `round4_ppi_theory.md`, `round4_ppi_estimator_definition.md`. Decisions in `docs/decisions/` as `round4_ppi_track.md`, `round4_ppi_addendum1.md`, `round4_ppi_Q1_decisions.md`, `round4_ppi_Q3_decisions.md`, `round4_ppi_addendum2.md`, `round4_ppi_Q5_decisions.md`, `round4_ppi_Q5a_closing.md`.
- Conformal track. `docs/round4_conf_plan.md`, `round4_conf_C2_report.md`, `round4_conf_final_report.md`, `round4_conf_candidate_definitions.md`, `round4_conf_lower_bound.md`. Decisions as `round4_conformal_track.md`, `round4_conformal_addendum1.md`, `round4_conformal_C2_decisions.md`, `round4_conformal_C4_decisions.md`.
- The second deck. `docs/deck2/deck2_outline.md` (revision 3), `docs/deck2/deck2_new_results_explained.md` (what, why, how and the theory for each of the six results, then the results not on the slides, then what is not established), `docs/deck2/deck2_literature_check.md`. `code/scripts/deck2_numbers.py` writes `results/summary/deck2_numbers.csv` (464 rows). `code/scripts/deck2_figures.py` writes `figures/deck2/f01` to `f13`.
- This handoff, `docs/decisions/round5_oversight_handoff.md`.

**In the Claude project.** The project had no documents before today. This handoff is there as `claude/round5-oversight-handoff.md`. The project's memory holds two facts, that jobs run on Longleaf by default and that the clones live under `~/hest-1k`. The project's instructions still say that round 4 is running as two tracks. That line is out of date and Nicolas may want to change it.

**On Nicolas's Mac,** under `~/hest-1k`, which the next session has as context.

| folder | what it is | use |
|---|---|---|
| `HEST-1k-replication-oversight` | the oversight clone, on `main` | yours. It was at `b1f1a7e` when this was written and needs a pull after the merge. `.oversight-scratch/` inside it holds stale lock files and stray files that I moved aside, none of them needed |
| `HEST-1k-replication-PPI` | the PPI session's clone, on `round4-ppi` at `8cca44f` | read only. Do not run git there except with `git --no-optional-locks` |
| `HEST-1k-replication-conformal` | the conformal session's clone, on `round4-conformal` at `e208907` | read only, same rule |
| `acs_pums2018` | the raw census fetch, 2.6 GB | not in the repository. Leave it |

A plain `git status` in a clone can leave `.git/index.lock` behind on this mount and block the next commit there. The device shell cannot delete files without permission from Nicolas. In earlier sessions the device shell also had no GitHub credentials, so commits made on the Mac were pushed by Nicolas from his terminal. In this session I worked in a separate clone in the cloud workspace and pushed from there. That clone does not carry over, so check which route you have before promising a push.

---

## 17. What to do first

1. Confirm that pull request #11 is merged and that the oversight clone on the Mac has been pulled. `docs/deck2/` and this file should be on `main`.
2. Read `docs/README.md`, this handoff, and the three files in `docs/deck2/`. Then the closing pages of `docs/round4_ppi_final_report.md` and `docs/round4_conf_final_report.md`.
3. Do not build slides. Wait for Nicolas to say he has read the explainer, and answer what he asks about it.
4. With him, settle the two held points and the cuts (section 12).
5. Add the missing rows to the numbers script and assemble the strip for slide 4 (section 8.2).
6. Fix the checker's fault on empty cells, with a fixture, and run the sweep over the `docs/deck2/` documents.
7. When he says so, build the deck from outline revision 3 under the rules in section 2.
8. After the meeting, plan round 5 from section 13 and the advisors' answers.
