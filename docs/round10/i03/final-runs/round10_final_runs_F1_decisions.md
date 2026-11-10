# Round 10, track `final-runs`, decisions at gate F1

*Written on 10 November 2026 by the second session of track `final-runs` (frame `862fd1a1-1068-44b1-a365-9bc7cae686fe`). It records Nicolas's reply, given in the session, to the F1 report `docs/round10/i02/final-runs/round10_final_runs_F1_report.md` (tag `round10-final-runs-F1`). Item numbers follow the three points of the report's section 7 that were put to him.*

## 1. The task list and the audit's exclusions

**Confirmed.** The corpus tasks are kidney Visium, breast ST, bowel Visium, brain Visium, breast Xenium and lung Xenium, with the counts of the report's section 3. Breast Visium is dropped. The audit's exclusions stand as listed in the report's section 7, item 2. These are the pooled-donor sections, the sections with a second donor's tissue, the kidney organoids, the unresolved RRST brain sections, the duplicate measurements and the unverifiable samples. The 89 samples kept on naming evidence stay in. Both flags are kept as the report states them. INT4 and INT24 stay as two donors (the 24-donor set primary, the merged set the sensitivity row), and NCBI599 and NCBI714 are not merged.

## 2. The morphology covariate on the corpus

**Options (b) and (c), both.** Option (b) extends round 3's nuclear instrumentation (`frac_neoplastic`, `m_std`) to the corpus's patches, which is new computation on data already on Longleaf. Option (c) defines a corpus covariate from what the corpus carries. Under the brief's section 7, (c) starts with a literature search by sub-agents across survey sampling, econometrics and machine learning, with the queries logged. The search is reported to Nicolas, and a derivation or construction starts only after he has seen it and agreed the gap is genuine. Until (b) or (c) delivers a covariate, the corpus tasks carry $\theta_1$ only.

## 3. Breast Xenium's center design

**Nicolas asked for an explanation.** It was given in the session on 10 November and is summarised here. His choice is open.

In the corpus a breast Xenium "center" is a study: S0178, S0228, S0253, S0254 and S0255. Studies S0253 and S0254 hold sections of the same two donors (donor map `F1/audit_verdicts/donor_map__breast__Xenium.csv` on Longleaf, samples TENX94 to TENX97). Holding out S0253 alone would leave those donors' S0254 sections in the training set. The fold would then not be donor-disjoint, and its predictions would score the head on donors it had seen. The prediction script refuses such a fold, which is why the first runs stopped (Slurm `8687463`, `8687469`, `8687541`). Their donor designs completed and passed.

There are two choices.

- **Grouped (run, the session's proposal).** The two studies are held out together. This gives 4 held-out units from 5 centers (S0178, S0228, S0253 with S0254, and S0255), and every fold is donor-disjoint. Breast Xenium then stays on the center axis beside kidney, bowel and brain Visium, at the 4-unit minimum. Its median spot-level Pearson on $\log(1 + y)$ under `uni_v2` is 0.686 against 0.746 for the donor design (`results/round10/final_runs/F1/aggregate/f1_predictions.csv`). The files are in `F1/predict/breast__Xenium__<encoder>__center_grouped/`.
- **Donor design only.** Breast Xenium leaves the center axis, as lung Xenium (3 centers) and breast ST (2 centers) do. The center-axis analyses of F2 and F3, FR8 among them, then rest on three tasks.

## 4. How the work goes on

Nicolas, 10 November: this session does bookkeeping only, and any new work starts with a new session. The next session reads this file with the plan's state block. It writes F2's methods into the plan's section 5, and the plans for options (b) and (c) of item 2, before any job. It also asks Nicolas for his choice on item 3 if this file has not recorded it by then.
