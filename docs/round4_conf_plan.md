# Round 4, the conformal track: operating plan

Instruction: `round4_conformal_track.md` (oversight chat, 30 September 2026, revised after the data-pull
report), sha256 `18c19e7364176988e5c56840b8c1021f62f747a28bf172cedeb5358f4157fda2`, handed over by Nicolas. The instruction file itself is not committed on this
branch, because `docs/decisions/` is not one of this track's areas; the proposal to add it there is in
the C2 report. Branch `round4-conformal` from tag `round4-data-v2` (`9d7277d`). This file is the
transcription the instruction requires before anything runs (its section 6, C0 item 1). It is
updated each time a decision memo hands work back, and never after a gate without one.

## 1. Stages and gates

| stage | length | gate | status |
|---|---|---|---|
| C0 setup | half a day, capped at one day | none, reported with C2 | in progress |
| C1 simulation testbed and known methods | three days | none, reported with C2 | not started |
| C2 candidates, lower-bound scoping, go or no-go | four days | **REPORT AND WAIT** | not started |
| C3 real data, the $(K, o)$ map | four days | none | **blocked until the C2 decision memo is handed back and transcribed here** |
| C4 closing report | two days | **REPORT AND WAIT, end of track** | blocked behind C3 |

The gate rule, verbatim from the instruction:

**The gate rule, in the wording Nicolas approved.** Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. This track's gates are C2 (the go or no-go) and C4. Contact with anyone outside the project is never the session's decision.

So there is one report inside C0 to C2, the C2 report, and one after C3 to C4, the final report.
Nothing of C3 is set up, staged or piloted before the C2 memo arrives.

## 2. Working copies and code routing (Nicolas, 30 September, answering the session)

Each session has its own working copy, locally and on Longleaf, and never checks out a branch in a
working copy the other session uses. Locally the PPI track works in `~/HEST-1k-replication` and this
track in the sibling clone `~/HEST-1k-replication-conformal`, cloned from the local repository, with
`origin` pointing at GitHub. On Longleaf the project tree `/work/users/w/e/weiyang/hest_replication`
stays on `main` at `round4-data-v2`; nobody checks out a branch there, because it is the data root
the harness's `ROOT` points to. This track's code runs from its own clone under
`/work/users/w/e/weiyang/hest_code/round4-conformal/`, put on `PYTHONPATH` in every job script.
Every job records that clone's HEAD and the md5 of the script it executed. Before the first job the
harness in that clone is confirmed at md5 `0ad7ae8efe554c1f285e5f384a9fb7f5`. If the project tree is
found on a branch other than `main`, that is reported and not changed.

State at C0 (read, 30 September): the project tree is on `main` at `9d7277d`, exactly tag
`round4-data-v2`, with two untracked shard files at its root that this track did not create and does
not touch; its harness has md5 `0ad7ae8efe554c1f285e5f384a9fb7f5`; `hest_code/` did not yet exist.
The local clone's harness also has md5 `0ad7ae8efe554c1f285e5f384a9fb7f5`.

## 3. Recorded in C0

**`whose()` on `results/round4/data/`** (each stage directory's `_provenance.json`, read on
Longleaf; the parent directory carries no stamp of its own):

| directory | verdict | stamping frame |
|---|---|---|
| `results/round4/data/P0_setup/` | `foreign_session` | `dab7c82a-7762-41ec-aaf1-9a41e6afaff2` |
| `results/round4/data/P1_download/` | `foreign_session` | `dab7c82a-7762-41ec-aaf1-9a41e6afaff2` |
| `results/round4/data/P1_selection/` | `unstamped` | none |
| `results/round4/data/P2_embeddings/` | `foreign_session` | `dab7c82a-7762-41ec-aaf1-9a41e6afaff2` |
| `results/round4/data/P3_morphology/` | `foreign_session` | `dab7c82a-7762-41ec-aaf1-9a41e6afaff2` |
| `results/round4/data/P4_audit/` | `foreign_session` | `dab7c82a-7762-41ec-aaf1-9a41e6afaff2` |
| `results/round4/data/P5_task/` | `unstamped` | none |
| `results/round4/data/P6_genes/` | `foreign_session` | `dab7c82a-7762-41ec-aaf1-9a41e6afaff2` |
| `results/round4/data/P7_report/` | `unstamped` | none |
| `results/round4/data/P8_addendum/` | `foreign_session` | `dab7c82a-7762-41ec-aaf1-9a41e6afaff2` |

The stamped directories belong to the data-pull session, which is a different session of this
project, and three directories are unstamped. This track only reads them, as the instruction names
them as the sources, and reads the committed copies at `round4-data-v2`. Nothing there is reused as
this track's output or rebuilt. Recorded for the Escalations section of the C2 report.

**The lung task file** (`results/round4/data/P5_task/LUNG_XENIUM.json` at `round4-data-v2`), against
the counts in the instruction. The file wins where they differ; here they agree.

| quantity | instruction | file |
|---|---|---|
| samples | 20 | 20 |
| donors | 15 | 26 |
| donors with two samples, with one | 5, 10 | 5, 10 |
| `folds.a4b_k10` rows | 15 folds by 3 draws | 45 rows, 15 folds, draws [0, 1, 2] |
| training donors per `a4b_k10` row | 4 | 4 to 4 |
| target genes, control features in the list | 343, none | 343, 0 |
| `dropped_patch_barcodes` | `NCBI865`: `051x019` | {"NCBI865": ["051x019"]} |
| capture slides | two to five donors each | 4 slide ids |
| 5 mm cores | `NCBI864`, `NCBI865`, `NCBI867`, `NCBI884` | NCBI864, NCBI865, NCBI867, NCBI884 |

The wrapper that applies the drop list before the round-3 loader's subset assertion is exercised on
`NCBI865` in the C0 job, with 2,142 rows expected.

## 4. Section 6 of the instruction, verbatim

## 6. The plan

### C0. Setup (half a day, capped at one day)

1. Read this document, `docs/WAYS_OF_WORKING.md`, `docs/round3_final_report.md` section 6.3 and its closing page, `docs/round3_A3_stage_report.md` section 6.8, `docs/round4_data_report.md` and `docs/decisions/round4_data_P7_decisions.md`. Transcribe section 6 into `docs/round4_conf_plan.md`, including the go or no-go criterion verbatim. Flag anything that looks wrong in the C2 report rather than changing it.
2. Create the branch and directories. Run `whose()` on `results/round4/data/` and record the verdict. Read the lung task file and record its sample count, donor count, `a4b_k10` fold count and dropped barcodes in the plan; the counts in this document are what the file is expected to say, and the file wins.
3. **Anchor.** Rerun `round3_a4b_hcp.py`'s $K = 6$ arm on CCRCC for one encoder and reproduce A1's committed `donor` coverage to $10^{-15}$, and its $K = 10$ HCP coverage to `a4b_summary.csv` at $10^{-12}$. Nothing in C1 starts until this passes.

### C1. The simulation testbed and the known methods (three days; no gate, reported with C2)

**Why.** The candidates have to be compared against a known truth, with the oracle width available, before anything runs on real data. The testbed is also where the paper's "price of validity as a function of $K$" figure comes from.

**Script.** `round4_conf_sim.py`, with the generator, every method and the oracle behind one interface, so C2's candidates plug in without touching C1's code.

**The generator.** Hierarchical scores, with an $o$ axis. Each replicate draws $K$ calibration donors, one test donor with 500 test spots, and additionally $o \in \{0, 5, 10, 25, 50, 100\}$ initial observations from the test donor that the $o > 0$ methods may use and the $o = 0$ methods ignore. For donor $k$, a location shift $a_k \sim N(0, \sigma_a^2)$ and a scale multiplier $b_k = \exp(\tau\,\eta_k)$ with $\eta_k \sim N(0, 1)$; for spot $i$ of donor $k$, a residual $r_{ki} = a_k + b_k\,\epsilon_{ki}$ with $\epsilon$ standard normal or Student $t_3$ (two tail settings); the score is $s_{ki} = |r_{ki}|$. A third generator resamples residuals from the round-3 score-moment files so that one setting is anchored to CCRCC's measured between-donor and within-donor score variances; call it the semi-real setting and report its fitted parameters. Grid: $K \in \{5, 7, 9, 10, 12, 15, 20, 25, 50\}$; $N_k \in \{100, 500, 2000\}$ (equal, and one unequal setting with $N_k$ log-uniform over that range); the between-donor share of score variance $\in \{0.1, 0.3, 0.5\}$ set through $\sigma_a$ at $\tau = 0$, plus $\tau \in \{0, 0.3\}$; $\alpha \in \{0.1, 0.2\}$. 5,000 replicates per cell; each replicate draws $K$ calibration donors and one test donor with 500 test spots. Fan out by $K$, nine units.

**The known methods.** (1) The pooled spot-level quantile. (2) HCP. (3) One score per donor, single draw. (4) Dunn, Wasserman and Ramdas's repeated subsampling, implemented as the paper states it, with the guarantee recorded as the paper states it. (5) GHCP at every $o > 0$, with its within-group adaptation on and off. (6) Within-test-group split conformal alone at $o > 0$, using only the $o$ observations, as the naive comparator GHCP should beat at small $o$. (7) The oracle $q^\star$, from a $10^6$-spot draw of new donors per cell, and at $o > 0$ the oracle for the test donor itself, its own $(1-\alpha)$ score quantile, which is what enough test observations would reveal.

**Metrics per cell and method.** Realised coverage for the new donor's spots, its across-replicate standard deviation, the fraction of replicates with an infinite interval, mean half-width, and the price of validity $\hat q / q^\star$. Monte Carlo standard error beside every coverage.

**Acceptance.** At $K = 50$ and share 0.1, HCP's coverage is within 0.01 of nominal. GHCP reproduces every figure in its paper that its stated settings allow, within Monte Carlo error, before any other GHCP number is read. At $\sigma_a = 0$ and $\tau = 0$ (no donor effect), every method's coverage is within 0.01 of nominal and the pooled quantile's price of validity is within 0.02 of 1. HCP is infinite exactly when $K + 1 < 1/\alpha$. On the semi-real setting at $K = 10$, HCP's coverage and width ratio to pooled reproduce A4b's 0.969 and 1.95 within 0.02 and 0.15.

**Predictions.**

1. HCP covers at least $1 - \alpha$ in every cell; its price of validity is 1.8 to 2.2 at $K = 10$, 1.3 to 1.5 at $K = 25$ and 1.1 to 1.2 at $K = 50$, higher under $t_3$ tails.
2. The pooled quantile under-covers in proportion to the between-donor share (about 0.87 at share 0.3, 0.83 at 0.5) at every $K$, with no $K$ dependence.
3. The one-per-donor interval covers at nominal with an across-replicate standard deviation three to five times HCP's; repeated subsampling reduces that spread at the same mean.
4. GHCP at $o = 25$ covers at or above $1 - \alpha$ in every cell and has a price of validity below 1.4 at $K = 10$, and at $o = 100$ below 1.15; within-group split conformal alone matches it at $o \ge 100$ and is worse at $o \le 25$.
5. The gap between HCP at $o = 0$ and GHCP at $o = 5$ is the largest single step in the whole $(K, o)$ map.

**Outputs.** `results/round4/conformal/C1_testbed/c1_grid.csv` (one row per cell, method and $o$), `c1_ghcp_reproduction.csv`, `c1_acceptance.csv`, `c1_report_numbers.csv`, `fig_c1_price_of_validity.png` (the $(K, o)$ map).

### C2. The remaining candidates, the lower-bound scoping, and the go or no-go (four days; gate)

**The criterion, fixed here.** A candidate goes forward to real data if, at $\alpha = 0.1$, across every C1 cell at its $o$, (a) its realised coverage is at least 0.89 in every cell, (b) its price of validity is at most $1 + \tfrac{1}{2}(\pi_{\text{ref}} - 1)$ in at least two thirds of the cells, where $\pi_{\text{ref}}$ is the reference method's price in the same cell, HCP at $o = 0$ and GHCP at $o > 0$, and (c) it carries a stated guarantee, finite-sample under hierarchical exchangeability or model-based with the model named. A candidate that meets (a) and (b) without (c) is reported as a heuristic and does not go forward alone. Whatever the candidates do, C3 runs; the criterion decides only whether any candidate joins the known methods there.

**The candidates**, each behind the C1 interface, with assumptions and guarantee in the docstring before it runs. Double conformal and repeated subsampling are dropped as candidates (the first is infinite at $K = 10$; the second stays as a known method in C1).

- **K1, smoothed HCP at $o = 0$.** The smoothed conformal construction of Vovk, Gammerman and Shafer applied at the donor level, so that the guarantee holds with equality in expectation. State the threshold rule and its guarantee before running. Expected to recover little; it is cheap and it bounds what tie-handling alone can do.
- **K4, a group-level quantile model at $o = 0$.** Per calibration donor its empirical $(1-\alpha)$ score quantile $q_k$; a location-scale model across donors; the new donor's quantile predicted as $\hat q = \bar q + t_{K-1,\,1-\alpha'}\, s_q \sqrt{1 + 1/K}$ for $\alpha' \in \{0.5, 0.25, 0.1\}$. Not distribution-free; model-based, conditional on the $q_k$ being approximately normal across donors, checked in the semi-real setting. The route most likely to be sharp and least likely to be safe under $t_3$ tails; say so.
- **K5, an adaptive score inside HCP and GHCP.** The scaled score $|r|/\hat\sigma$ with a within-donor scale estimate and, in C3, the CQR score, tested under $\tau = 0.3$. The guarantee is the host method's, unchanged. The question is width at matched coverage and top-decile coverage.

Fan out by candidate, three units.

**The lower-bound scoping at $o = 0$ (three days, capped, run by the lead in parallel with the candidate units).** The question is whether any distribution-free method with finite-sample coverage $1 - \alpha$ for a spot of a new group, given $K$ exchangeable calibration groups and no observation from the test group, can have expected width below HCP's by more than a vanishing amount, or whether HCP is minimax-optimal in a sense that can be stated. Work from the standard lower-bound arguments for exchangeable conformal (the impossibility of conditional validity, Lei and Wasserman 2014 and Vovk 2012, and the Foygel Barber et al. 2021 limits) lifted to the group level, where the object the test group contributes is a whole score distribution rather than a score. Write `docs/round4_conf_lower_bound.md` as you go, with each step marked derived, conjectured or failed. Stop rule. If after three days there is no statement with a proof sketch, write the document as a record of what was tried and stop; the scoping is then reported as no-go on the theory and nothing further is spent on it. If there is a statement, the report says what it is and the oversight chat decides whether it is pursued.

**Predictions.**

1. K1 recovers less than a tenth of the gap at $K = 10$; the atom's mass, not tie-breaking, is what costs width.
2. K4 at $\alpha' = 0.5$ covers 0.88 to 0.92 at a price of validity 1.1 to 1.3 under normal tails and under-covers by three to six points under $t_3$ tails at share 0.5; at $\alpha' = 0.25$ it covers at or above 0.90 everywhere at a price of 1.2 to 1.4, and it meets (a) and (b) but not (c).
3. K5 leaves marginal coverage unchanged and reduces width at matched coverage by 5 to 15% under $\tau = 0.3$, inside HCP and inside GHCP alike.
4. No $o = 0$ candidate meets all three parts of the criterion; GHCP at $o \ge 5$ is the method that goes to real data, with K5 as its score.
5. The lower-bound scoping produces a conjecture with a partial argument, not a theorem, inside its three days.

**Outputs.** `results/round4/conformal/C2_candidates/c2_grid.csv`, `c2_criterion.csv` (one row per candidate and $o$ with (a), (b), (c) and the verdict), `c2_report_numbers.csv`, `fig_c2_candidates.png`, `docs/round4_conf_candidate_definitions.md` and `docs/round4_conf_lower_bound.md`. Report C1 and C2 together, predictions against outcomes, the criterion table, and stop.

### C3. Real data, the $(K, o)$ map (four days; no gate)

**The tasks.** CCRCC (24 donors and merged), Indiana kidney (25 donor units), lung Xenium (15 donors), and ACS PUMS income with states as groups, the dataset the GHCP paper uses, fetched by the PPI track in its Q0 into `results/round4/ppi/Q0_setup/acs/` (read it there; if it is not present when C3 starts, run the HEST tasks and add ACS when it appears, recording the commit you read it from). Three encoders on the HEST tasks; the package predictor on ACS.

**The $K$ axis.** The $K = 10$ design from the task definitions, and on CCRCC a sweep $K \in \{4, 6, 8, 10, 12, 14, 16, 18, 20\}$ through the calibration fraction, with the training-donor count recorded beside each $K$ since it falls as $K$ rises. On lung the $K = 10$ design trains on 4 donors, so run $K \in \{6, 8, 10\}$ there and read the three together; at $K = 6$ HCP is finite only at $\alpha = 0.2$, and that row is still reported. Methods at $o = 0$ are the pooled quantile, HCP, one-per-donor, and any $o = 0$ candidate that passed C2.

**The $o$ axis.** For each test donor, $o \in \{5, 10, 25, 50, 100, 200\}$ labelled spots drawn uniformly from the test donor's own spots (on lung a donor's core or cores, never the capture slide, which carries other donors), 20 draws with crc32 seeds. Methods are GHCP (with and without within-group adaptation), within-slide split conformal alone (the $o$ spots as the only calibration), and the recentred cross-donor interval (the pooled cross-donor quantile of round 3's `donor` design after shifting predictions by the labelled spots' mean residual), which is the cheapest thing a practitioner would try. Absolute score and, for K5, the scaled and CQR scores. Coverage and width for the slide's remaining spots, per slide, then the metric convention. This is the arm that was in the PPI track's plan as within-slide conformal; it lives here now and runs GHCP as the reference.

**The output format is fixed**, because the PPI track's Q5 reads it. `results/round4/conformal/C3_real/c3_o_sweep.csv` with columns task, label_set, encoder, method, score, alpha, o, K, fold, draw, coverage, width_mean, width_median, n_test, finite, and the by-task pooled version `c3_o_sweep_by_task.csv`. Also `c3_K_sweep.csv`, `c3_by_fold.csv`, `c3_report_numbers.csv`, `fig_c3_K_sweep.png`, `fig_c3_o_sweep.png`.

**Acceptance.** The $K = 10$, $o = 0$ pooled, HCP and one-per-donor rows on CCRCC reproduce `a4b_summary.csv` to $10^{-12}$ before any other row is read. GHCP on ACS with the GHCP paper's settings reproduces its reported numbers within Monte Carlo error where the settings are stated.

**Predictions.**

1. HCP's coverage on CCRCC falls from about 0.99 at $K = 4$ (finite only at $\alpha = 0.2$) to about 0.95 at $K = 20$, and its width ratio to pooled from above 3 to about 1.4; the pooled quantile stays at 0.86 to 0.87 at every $K$.
2. GHCP at $o = 25$ covers 0.90 to 0.94 on every HEST task at $K = 10$ with a width ratio to pooled of 1.2 to 1.4; at $o = 100$ its width is within 10% of within-slide split conformal, which is at nominal from $o = 50$ on.
3. Recentring alone recovers more than half of the cross-donor shortfall at $o = 25$ on the unit-calibrated tasks and less than a third on the block-calibrated ones (HCC, LUNG, SKCM), where the failure is scale.
4. The top-decile shortfall (0.72 under the cross-donor absolute score) closes to 0.85 or above under GHCP with the CQR score at $o \ge 25$.
5. Indiana reproduces the CCRCC pattern with a smaller gap (its fold scatter is a third of CCRCC's); lung Xenium has a larger one; ACS sits between, and the GHCP paper's ACS numbers are reproduced.

Fan out by task and axis, eight units.

### C4. The closing report (two days; gate, end of track)

`docs/round4_conf_final_report.md` in the format of section 8, covering C1 to C3, the full predictions-against-outcomes table, an "Escalations" section, and a closing page titled "What the conformal track established", at most one page, every sentence naming its file, ending with a one-paragraph statement of what the prediction-set section of the paper says and whether the lower-bound scoping produced anything worth pursuing. Run the numeric-claim sweep. Tag `round4-conf-final`. Then stop.

**Time.** About fourteen working days with the gates.

---

## 7. Predictions for the track, consolidated

The stage predictions above, numbered C1.1 to C1.5, C2.1 to C2.5 and C3.1 to C3.5, are the track's predictions. Copy them into `docs/round4_conf_plan.md` before running and score each in the closing report as held, partly held, refuted or not tested.

## 5. Decision boundaries, verbatim (instruction section 9)

## 9. Decision boundaries

**You decide alone.** Sub-agent structure; seeds; replicate counts above 5,000; the exact form of the semi-real generator's fit; job sizing; implementation details of a candidate that its definition leaves open, provided the docstring records the choice before the run.

**Record as an escalation and continue.** The lung task file disagreeing with the counts in this document (use the file); any acceptance check failing at a tolerance the dtype supports (fix, rerun, say so); any candidate whose stated guarantee you cannot verify against its source paper (run it, mark (c) as unmet, say why); any new property of the data.

**Stop and report.** The C0 anchor failing. The C1 acceptance on the semi-real setting failing to reproduce A4b, which would mean the generator does not represent the data.

**Never yours.** Spending more than three days on the lower-bound scoping; revising the go or no-go criterion after C2 starts; contact with anyone outside the project; changes to `main`, to round-3 files, to the data-pull outputs, to the audit file, or to the PPI track's areas; any download.

## 6. Fan-out and hand-back

**Fan-out.** Every stage below names its parallel units. Dispatch one sub-agent per unit with a written brief that includes, verbatim, "Stamp every output directory with `stamp_dir()` from the `longleaf-provenance` skill. Before reusing or rebuilding any output you did not create, run `whose()` on it; if the verdict is `sibling` or `unstamped`, ask me rather than rebuilding." Each sub-agent writes its own fragment under its own directory; the lead merges, recomputes every pooled number from the merged tables into a `<stage>_report_numbers.csv`, and commits.

The units, as this session runs them. C1: nine sub-agents, one per $K \in \{5, 7, 9, 10, 12, 15, 20, 25, 50\}$,
after the lead has committed `round4_conf_sim.py` with the GHCP reproduction passing. C2: three
sub-agents (K1, K4, K5), with the lead running the lower-bound scoping at the same time. C3, after
the memo only: eight sub-agents, one per task and axis (CCRCC $K$, CCRCC $o$, Indiana $K$, Indiana $o$,
lung $K$, lung $o$, ACS $K$, ACS $o$). Sub-agents run no git command and write only their own fragment
directory; the lead checks each hand-back against its primary tables, merges with a collision check
on colliding keys, recomputes pooled numbers into the stage's report-numbers file, and commits.

## 7. Conventions fixed before running

These are implementation choices the instruction leaves to the session (section 9, "you decide
alone"), written here before anything runs so that none of them is chosen after seeing an outcome.

1. **The between-donor share.** It is the share of *score* variance, $\operatorname{Var}(E[s \mid k]) / \operatorname{Var}(s)$
   with $s = |r|$, not the residual share $\sigma_a^2 / (\sigma_a^2 + 1)$. $\sigma_a$ is solved numerically per
   tail setting to hit 0.1, 0.3 and 0.5 at $\tau = 0$, and the solved values are recorded. At
   $\tau = 0.3$ the same $\sigma_a$ is kept and the realised share is recorded beside the cell.
2. **$t_3$ tails** use the unscaled $t_3$ distribution; every reported metric is either a coverage or a
   ratio, so the scale does not enter.
3. **The oracle** $q^\star$ for a cell is the $(1-\alpha)$ quantile of the new-donor score mixture, from
   $10^6$ spots over freshly drawn donors (one spot per donor, so that the mixture is over donors).
4. **Coverage per replicate** is the fraction of the test donor's 500 spots covered; a cell's
   coverage is the mean over 5,000 replicates, reported with its across-replicate sd and the Monte
   Carlo standard error $\text{sd}/\sqrt{5000}$. Price of validity and mean half-width are computed
   over finite replicates, with the infinite fraction beside them; a cell with any infinite
   replicate has an infinite price.
5. **Criterion (a)** reads "realised coverage" as the cell's mean coverage over replicates.
   **Criterion (b)** in cells where the reference price is infinite (HCP at $\alpha = 0.1$ and $K \le 8$,
   that is $K = 5$ and $K = 7$): the bound $1 + \tfrac12(\pi_{\text{ref}} - 1)$ is then infinite. The primary
   reading counts such a cell as meeting (b) when the candidate is finite in it and not otherwise.
   The secondary reading leaves those cells out of the two-thirds count. Both are reported; the
   verdict uses the primary.
6. **The semi-real generator** resamples, per gene, from the per (fold, unit, gene) score moments of
   CCRCC in `results/round3/A2_conditional/a2_score_moments__<enc>.parquet`, and a cell's coverage is
   the mean over genes, so that it is on the same footing as A4b's per-fold means.

## 8. Flags for the C2 report (things in the instruction that look wrong)

Recorded now, not acted on; each is repeated in the C2 report.

1. **C1 acceptance at $\sigma_a = 0$, $\tau = 0$.** "Every method's coverage is within 0.01 of nominal"
   cannot hold by construction for the methods whose coverage has a known upward offset. With no
   donor effect HCP's threshold is the $(1-\alpha)(K+1)/K$ quantile of the score distribution, which is
   the 0.99 quantile at $K = 10$, $\alpha = 0.1$, and HCP is infinite for $K \le 8$. The one-per-donor
   interval covers $\lceil (K+1)(1-\alpha) \rceil / (K+1)$ in expectation, 0.909 at $K = 10$ and 0.9375 at
   $K = 15$. The check is evaluated as written for every method and reported; for these methods it is
   also evaluated against the method's own expected coverage under no donor effect, and the report
   says which reading passes.
2. **The C0 anchor against `a4b_summary.csv`.** The summary's HCP coverage 0.969 is a mean over three
   encoders, so a one-encoder rerun cannot reproduce it at $10^{-12}$. The anchor compares the rerun's
   per-fold rows with the committed one-encoder table `a4b_hcp_K10__<enc>.csv` at $10^{-12}$, and
   separately checks that the summary value is the mean of the three committed per-encoder tables at
   $10^{-12}$. The $10^{-15}$ comparison with A1's `donor` coverage is a same-quantity comparison and is
   run as written; A4b's own anchor met it at $2.2 \times 10^{-16}$, but the rerun may land on a
   different node, where round 3 measured width drift up to $9.5 \times 10^{-7}$, so a miss is first
   checked for a count flip at a boundary before it is read as a failure. A failure of the anchor is
   a stop-and-report condition.
3. **Prediction C3.3** names the block-calibrated tasks HCC, LUNG and SKCM, none of which is among
   C3's tasks (CCRCC, Indiana, lung Xenium, ACS). As written it is expected to be scored "not tested".
4. **Lung $K = 8$.** The instruction notes that HCP at $K = 6$ is finite only at $\alpha = 0.2$; the same
   holds at $K = 8$, since $K + 1 = 9 < 10$.
5. **"Within-slide" on lung.** Lung slides carry two to five donors, so C3's within-slide split
   conformal and per-slide metrics are within-donor (the donor's own core or cores) on lung.
