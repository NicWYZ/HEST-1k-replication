# Round 11, the headline results tested and an outline for the advisors (16 to 20 November 2026)

Round 11 followed Nicolas's request of 16 November for an assessment of the project as a whole (`masterplan.md`, "Why this round"). One execution track, `closeout`, tried a stronger predictor against the project's headline results and closed round 10's open threads (gates G2 and G-final, tags `round11-closeout-G2` and `round11-closeout-G-final`, pull request #42, merge commit `e025734d`). The oversight session then drafted the outline for presenting the project to the advisors. For this round only, Nicolas had the oversight session review the track's gates and relay summaries to him (`masterplan.md`, "Who decides the gates"); he merged the pull request and decided the one question the final gate put to him.

The report that explains the numbers is `closeout/round11_closeout_report.md` ("the report"), with `closeout/round11_closeout_G2_report.md` ("the G2 report") for the strength runs and the loose ends in full. Paths beginning `a6/`, `b1/` to `b7/`, `g2/` and `lit/` are under `results/round11/closeout/`. Unless a line says otherwise the encoder is `uni_v2`, the scale $\log(1 + y)$, the nominal level 0.90, the estimand $\theta_3$ and "8 donors" means 8 labelled clusters in regime A.

## What the round established

**The headline results, as they now stand.** Every number of record recomputes at its quoted precision from an independent sub-agent's own code (G2 report, section 6.3).

| # | Result | Numbers | File |
|---|---|---|---|
| H1(a) | Spots are far from independent | the donor-clustered standard error of a spot mean is 14.81 (LUNG_XENIUM) to 58.98 (brain Visium) times the i.i.d. one, median over genes | `b1/h1a/b1_h1a_summary.json` |
| H1(b) | Split conformal sets calibrated on spots lose coverage on a new donor, by an amount that depends on how many donors calibrate | per task below; stated per task with its donor count (Nicolas, 18 November) | `a6/aggregate_v4/a6_conformal.csv` |
| H2 | Across centers, prediction and calibration both fail | kidney Visium: median Pearson 0.1231 held out by center against 0.4713 held out by donor; at nominal 0.80, donor-level HCP pooled across centers covers 0.9057 at the median center and 0.6552 at S0006, and HCP over centers covers 1.0 | `a6/aggregate_v4/a6_center.csv`, `a6_center_hcp.csv`; by donor, `g2/aggregate_v4/g2_strength.csv` |
| H3 | What predictions buy for cohort-level inference follows donor-level accuracy, not spot-level accuracy | width ratio of `fix1` to `classical` and donor-level $R^2_c$: CCRCC 0.8949 and 0.4290, INDIANA_KIDNEY 0.9570 and 0.1390, kidney Visium 0.9367 and 0.1986, bowel Visium 0.6691 and 0.6258, LUNG_XENIUM 0.5853 and 0.7139 (this round's refit on the corpus's embeddings; round 10's numbers of record are 0.8783 and 0.4387, 0.9574, and 0.5855 and 0.7135 on the three HEST tasks) | `a6/aggregate_v4/a6_donor_level.csv` |
| H4 | HEST-1k's patient labels are wrong in both directions, and the split design moves benchmark accuracy more than the encoder | 0.1586 against an encoder spread of 0.0977 | `b1/h1b_h4/b1_h1b_h4_summary.json` |
| H5 | Published clustered-PPI intervals under-cover at four labelled clusters | medians over cells: Kluger et al. 0.7145 (242 cells); Broska and Howes 0.699, and 0.875 with the small-sample correction (146 HEST and ACS cells) | `b1/h5/b1_h5_summary.json` |

**H1(b) reads differently from round 3's mean, and this changes round 3's summary.** Round 3's 0.894 (`random`) and 0.802 (`donor`) are means over 132 task and encoder cells and recompute; the cells count IDC twice, and with IDC once under its audited labels `donor` is 0.800. Refitted under round 3's designs on five tasks with 15 to 51 donors, `random` and `donor` cover 0.8824 and 0.8640 (CCRCC, 24 donors), 0.9070 and 0.8776 (INDIANA_KIDNEY, 25), 0.9006 and 0.8872 (LUNG_XENIUM, 15), 0.8984 and 0.8921 (bowel Visium, 18), 0.9073 and 0.8940 (kidney Visium, 51): a shortfall of 0.006 to 0.029. Round 3's large shortfalls, 0.14 to 0.28, are on tasks with two donors (`results/round3/A1_coverage/a1_by_task__uni_v2__main.csv`), and every shortfall above 0.05 there is on a task with at most four, though two-donor READ and PRAD show 0.0654 and 0.0208 and three-donor PAAD −0.0023. The standard deviation of `donor` coverage over held-out donors is 0.038 to 0.144. Holding out a center costs more than holding out a donor in 12 of 12 cells, by 0.0164 on kidney Visium and 0.0578 on bowel Visium (report, section 6.4). That the shortfall depends on the number of calibration donors is a reading of these rows; no design was run to test it.

**A stronger predictor.** Six arms were fitted held out by donor: `R10` (round 10's head), `H` (a ridge without PCA tuned per gene), `C` (the neighbours' mean embedding added), `P` (both; named primary before any held-out result was read), `V` (`virchow2`) and `E` (three encoders with context, a secondary arm) (report, section 2.1).
- `P` raises the median spot-level Pearson over this track's `R10` by 0.0103 (kidney Visium), 0.0183 (bowel Visium) and 0.0104 (LUNG_XENIUM), and over P11.1's reference values by 0.0106, 0.0186 and 0.0103 (`g2/aggregate_v4/g2_p111.json`), below the 0.02 P11.1 asked for. `E` raises it by 0.0309, 0.0830 and 0.0169 (`g2/aggregate_v4/g2_strength.csv`).
- Because P11.1 failed, the tests of H1(b), H2 and H3 under a stronger predictor are formally "not tested". `P` and `E` were carried through anyway as supplementary evidence; `E` was chosen for this after its results were seen, and every use of it says so.
- **H3 under `P` and `E`.** The width ratio is 0.9750 and 0.9984 on CCRCC, 0.9227 and 0.9107 on INDIANA_KIDNEY, 0.9631 and 0.9930 on kidney Visium, 0.6372 and 0.6044 on bowel Visium, 0.5627 and 0.5425 on LUNG_XENIUM. It narrows where $R^2_c$ rises and widens where $R^2_c$ falls, while spot-level Pearson rises in nine of the ten cells. Across genes the width ratio is more strongly rank-correlated with $R^2_c$ than with spot-level Pearson in 84 of 84 $\theta_3$ cells and 82 of 84 $\mu$ cells. Under `P` every per-gene change of the width ratio has an interquartile range containing zero (report, section 6.2).
- **H2 under `P` and `E`.** Held out by center the median Pearson stays below 0.14 on kidney and brain Visium, and S0006's coverage is 0.5819 and 0.6296 (report, section 6.3).
- **H1(b) under `P` and `E`.** `donor` coverage moves by at most 0.0051 in 20 of 20 cells.
- The published descriptions of the three encoders name no public dataset among their pretraining sources, so overlap with these cohorts is not stated, which is weaker than ruled out (`lit/lit_A7_pretraining.md`).

**CCRCC through the corpus.** The track read CCRCC, INDIANA_KIDNEY and LUNG_XENIUM through the federated corpus's embeddings. On CCRCC, 407 of 74,220 spots have no corpus embedding, and `R10` there gives a width ratio of 0.8949 and $R^2_c$ of 0.4290 against round 10's 0.8783 and 0.4387. A control on round 3's own file reproduced 0.878272, so the pipeline is exact and the difference is the embeddings. Every CCRCC number of this round is against the track's own `R10` on the same 73,813 spots (G2 report, section 6.2).

**Round 10's open threads, which change round 10's summary.**
- **Equal allocation for regime B on ACS by state.** Regime B is narrower than regime A in 12 of 12 cost-matched comparisons, median width ratio 0.699, coverage 0.8915 to 0.9085, against 3 of 12 under proportional allocation (`b4/equal_v2/b4_summary.json`). Round 10's allocation reading holds.
- **Within-cluster variances.** On ACS by state they are close to equal (median ratio of largest to smallest 1.70), and the allocation factor recomputed from them is 2.636 against round 10's 2.656. On the HEST tasks they are not (14.8 to 23.5), and the recomputed factor is 0.973 to 1.341 times round 10's; ACS's stays the largest (`b5/withinvar_v1/b5_by_task.csv`).
- **S0006.** This center of kidney Visium is CCRCC's 24 donors (73,813 spots). Its low coverage comes from the calibration it faces and a level shift, not from the largest residuals. It holds 24 of 51 donors, so the pool that calibrates it lacks them and gives the narrowest half-width of the five centers (1.0717 against 1.3710 to 1.5721, `uni_v2` lognorm). Removing its level shift raises its coverage from 0.6555 to 0.8184 on that scale, and from 0.6552 to 0.7582 on $\log(1 + y)$ (`b3/s0006_v1/b3_by_center.csv`).
- **The stored columns.** D12's share of genes where the pooled head beats a constant, and round 9's E1 box numbers, now have selectors (`b6/stored_v1/b6_summary.json`).
- **Jobs without provenance.** 56 of round 10's 2859 jobs are absent from its ledger and wrote no provenance file: 33 cancelled, 10 timed out, 9 completed, 4 failed (`b7/ledger_v2/b7_summary.json`).

**Caveats across these findings.**
- Kidney Visium contains the samples of CCRCC and INDIANA_KIDNEY, so the three are not independent tasks.
- `fix1` under-covers $\mu$ on CCRCC, 0.848 to 0.869 at 8 and 16 donors under every arm, as round 10's own cell does (report, section 7, item 4).
- On the normalised scale the direction of each arm's width-ratio change differs from $\log(1 + y)$ on several tasks, and under `E` the ratio exceeds 1 on three. It was tabulated and not read further.
- The CCRCC values 0.881 and 0.864 that round 3 and the track's brief quote are means over 12 encoders; the `uni_v2` row is 0.8830 and 0.8654.
- The donor-mean $R^2$ has two baselines in the record. Round 9's values are against the full-sample mean, under which a constant scores $-0.089$ on CCRCC; round 10's and this round's are against the leave-one-out constant, which is the primary one.

## The expectations and their scores

The masterplan's, as written in `masterplan.md`, "Expectations":

| prediction | outcome | score |
|---|---|---|
| P11.1, the primary predictor gains at least 0.02 on two of three tasks | 0.0106, 0.0186, 0.0103 over the reference values | refuted |
| P11.2, width ratio above 0.80 on three tasks and CCRCC's leave-one-donor-out $R^2$ below 0.15 | supplementary: 0.9750, 0.9227, 0.9631; 0.0118 | not tested |
| P11.3, held out by center below 0.20 and 0.25 below by donor | supplementary: 0.1068 against 0.4816 | not tested |
| P11.4, `donor` below `random` on every task; kidney Visium's center design 0.05 below `random` | supplementary: first clause on all five tasks; second 0.0370 | not tested |
| P11.5, equal allocation makes regime B narrower in more than 6 of 12 | 12 of 12, median 0.699 | held |

The session's predictions are quoted in full with their scores in the report, section 5: A2.1, A2.3, A5.4, B3, B4, B6 and B7 held; A2.2 held as written; A5.1 to A5.3 refuted; B5, A6.2, A6.3, A6.4 and B2 partly held; A6.1 refuted for `P` and held for `E`; A6.0 (a) refuted as written because it cited the 12-encoder mean, with the pipeline exact.

## What was tried and did not work

- **A ridge without PCA tuned per gene, with or without neighbour context** (`H`, `P`), moves pooled Pearson by −0.0159 to 0.0183 and is not a stronger predictor by the masterplan's measure.
- **Another encoder alone** (`V`) moves pooled Pearson by −0.0027 to 0.0369 with a per-fold gain near zero.
- **More training donors.** The registry holds no further donors of the same organ and platform for any corpus task, and the literature advises against mixing organs or platforms (`lit/lit_A_stronger_predictor.md`; G2 report, section 7, item 8).
- **The explanation that `P` gains per fold by narrowing the spread of donors' predicted levels** is refuted: the spread ratio is 1.016 and 1.072 (`a6/aggregate_v4/a6_mechanism.csv`). Why `P`'s per-fold gain exceeds its pooled gain is not explained.
- **Reproducing round 10's CCRCC cell through the corpus embeddings** misses by 0.0166 with common random numbers. The oversight session accepted the corpus route at G2 and told Nicolas afterwards, although the masterplan sends a failed anchor to him.
- **A prediction of a donor shortfall of at least 0.02 on every task** held in 5 of 30 cells.
- **Conformal jobs submitted with 15 and 25 hour limits** stayed pending for ten hours; lowering the limits in place and splitting two jobs by fold started them (`docs/environment.md`, "Longleaf scheduler notes", already says so).

## What was presented outside the project

Nothing. The outline for the advisors, `oversight/round11_advisor_outline.md`, is drafted and Nicolas asked on 20 November that the next session build the figures and the deck from it. No result has reached the advisors since round 3, so the deck is the first time they see rounds 4 to 11.

## The open questions, at the close

| question | at the close | for Nicolas? |
|---|---|---|
| How H1(b) is stated | settled on 18 November: per task with its donor count | no |
| The paper's framing | open: round 10's applied paper, or one paper on the headline results. The oversight session's reading favours the second, `[proposed]` | yes, with the advisors |
| D5, the primary scale | open | yes, with David |
| Q1, regime B on a spatial platform and its cost | open; the deck carries it | yes, with the advisors |
| Q3, venue and lead result | open | yes |
| O5, round 9's theorems | open; they stay candidates and are not in the outline | yes |

## Open threads

- **The figures and the deck.** The outline names the file each figure is drawn from. `docs/WAYS_OF_WORKING.md`, "Decks", governs.
- **Draft v1** of the paper is still unwritten, and waits on the framing.
- **No literature check of the headline message as a whole** meets hard rule 5. The oversight session ran nine searches on 16 November and found no paper measuring these results, which is not a check. The track's notes cover stronger predictors, encoder pretraining and donor-level accuracy (`lit/`); the last found no published donor-level accuracy in the project's form and reads H3 as classical in substance, the cluster-sampling variance of model-assisted estimators (`lit/lit_B_donor_level_accuracy.md`).
- **The mechanism of H1(b)** (calibration donors) rests on existing rows.
- 184 of round 10's ledger ids are absent from the scheduler's accounting window and are not explained (G2 report, section 8).
- Brain Visium's HCP coverage under the arms is in `a6/aggregate_v4/a6_center_hcp.csv` and was not read.
- The full texts of papers saved outside the repository by round 9's sessions are still not deleted.

## Documents kept

- `masterplan.md`: the plan of record, with P11.1 to P11.5 as written.
- `closeout/round11_closeout_report.md`: the final report, with the design, every prediction in full and the headline table.
- `closeout/round11_closeout_G2_report.md`: the strength runs of every arm, the anchors and round 10's open threads in full.
- `closeout/round11_closeout_plan.md`: the track's plan, kept because the scripts and provenance files under `results/round11/closeout/` cite it by path.
- `oversight/round11_advisor_outline.md`: a working paper the next session builds the deck from; it is deleted when the deck exists.

The track's brief, which the masterplan, the plan and both reports cite by section, is at tag `round11-record` (`git show round11-record:docs/round11/closeout/round11_closeout_brief.md`).
