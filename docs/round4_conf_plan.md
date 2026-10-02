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
| donors | 15 | 15 |
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

## 9. Amendment, 30 September 2026: version management (oversight chat note)

A note from the oversight chat, handed over by Nicolas on 30 September 2026, covers how accepted
work reaches `main`. It applies from the next gate (C2) on. Everything the instruction already says
still holds: commits only on `round4-conformal`, a tag at each gate, and no merge into `main` by this
session. The action items, transcribed before any of them is run:

1. **At each gate (C2 and C4), in this order.**
   1. Commit the gate report and everything it cites on `round4-conformal`, run the numeric-claim
      sweep, tag the commit (`round4-conf-C2`, `round4-conf-final`), and push the branch and the tag.
   2. Open a pull request from `round4-conformal` into `main` with `gh pr create`, titled
      "Round 4 conformal track, gate C2" (or "Round 4 conformal track, final"). The description
      gives the tag, the head commit, the path of the gate report, and one paragraph on what the
      stage produced. No reviewers, labels or auto-merge.
   3. Stop, as the gate rule already requires.
2. **Never** merge the pull request, push to `main`, or change `main` in any other way. After the
   oversight chat accepts the report, Nicolas merges it on GitHub with a merge commit.
3. **Branch rules**, because every provenance record cites commit hashes. Never rebase, squash,
   amend a pushed commit, or force-push `round4-conformal`.
4. **After a merge**, keep working on `round4-conformal` as before. Do not merge or pull `main` into
   the branch unless the oversight chat asks. The PPI track's merged work will be in `main` and not
   in this branch, which is intended. The ACS data under `results/round4/ppi/Q0_setup/acs/` is read
   from the `round4-ppi` branch, recording the commit read.
5. **If a gate is not accepted**, fix with new commits on `round4-conformal` and push. Move the tag
   only if the oversight chat asks. The open pull request picks up the new commits; no second pull
   request is opened.
6. **The Longleaf project tree** `/work/users/w/e/weiyang/hest_replication` does not follow `main`
   during the round. It stays at `round4-data-v2` as the data root. Nothing is pulled, fetched into
   it or checked out there. It is updated once, between rounds. (This track's jobs only read its
   branch name with `git rev-parse`, which changes nothing.)
7. **If `gh` fails**, push the branch and tag anyway, put the GitHub compare URL for
   `main...round4-conformal` in the report, and say so under escalations. Nicolas then opens the
   pull request.

How item 1.2 will be carried out, proposed and not yet approved. The `gh` CLI cannot verify TLS
certificates from this session's sandbox, so `gh pr create` is expected to fail here. The
proposal is to open the pull request through the GitHub REST API (`POST /repos/NicWYZ/HEST-1k-replication/pulls`)
with the same title, head, base and description, and no reviewers, labels or auto-merge. That is
the same request `gh pr create` makes. If the REST call also fails, item 7 applies. Either way the
route used is recorded under escalations in the gate report. If Nicolas prefers the item 7
fallback to be used straight away, the REST call is not made.

## 10. Addendum 1, 30 September 2026 (oversight chat, interval 1)

Handed over by Nicolas as `round4_conformal_addendum1.md`. Transcribed before any of it is acted
on. It does not move the C2 gate, and nothing in it starts C3. The gate rule it restates is the one
in section 1 of this plan, unchanged.

1. **The five flags of section 8 are all accepted.**
   1. C1 acceptance with no donor effect. Every method is evaluated against its own expected
      coverage under no donor effect: for HCP its calibration level $(1-\alpha)(K+1)/K$ where
      finite, for one-per-donor $\lceil (K+1)(1-\alpha)\rceil/(K+1)$. The literal reading is
      reported beside it.
   2. The C0 anchor is accepted as done (per-encoder comparison at $10^{-12}$ plus the check that
      `a4b_summary.csv` is the mean of the three committed tables).
   3. Prediction C3.3 is scored "not tested".
   4. Lung: HCP is finite only at $\alpha = 0.2$ at $K = 6$ and at $K = 8$; both rows are reported.
   5. "Within-slide" on lung means within-donor, the donor's own core or cores.
   The conventions of section 7 are accepted as written, including the primary and secondary
   readings of criterion (b). The criterion is unchanged.
2. **GHCP pool rule.** The primary implementation in C1, C2 and C3 is the rule for which the paper's
   validity theorem is stated. The other rule runs as a secondary variant in
   `c1_ghcp_reproduction.csv` and in every C1 cell at $\alpha = 0.1$. The C2 report (a) shows the
   difference on one small worked example, (b) says which rule the theorem covers, quoting the
   paper, (c) says whether the two rules' coverage differs by more than Monte Carlo error in any
   cell, and (d) records the repository commit read (`d1a69f4a35b260b592d3ea39d7c7ad7133459cba`).
   If the paper does not say which rule its theorem covers, that is an escalation, the paper's rule
   stays primary, and work continues.
3. **Lower-bound scoping, remaining cap to 3 October**, in this order, each marked derived,
   conjectured or failed in `docs/round4_conf_lower_bound.md`, stopping at the cap wherever it is:
   1. step 3 of Proposition 2 (the equivariance construction) written in full;
   2. whether randomised HCP attains Proposition 1's floor with equality;
   3. case 3 ($|J_h| = 1$) of the section 5 argument;
   4. the finite-$N_k$ version, with the distance check widened by a DKW band.
   No literature search on whether the propositions are known; the oversight chat does that.
4. **Added candidate K6, the switch rule of the lower-bound document's section 5.** Finite $N_k$,
   $d$ widened by $2\epsilon_N$ from a DKW band at level 0.01, $\delta$ from the probe's worst
   configuration at that $d$. Runs through the C1 grid at $\alpha = 0.1$ behind the C1 interface,
   with assumptions and guarantee in the docstring before it runs, scored against the fixed
   criterion. Part (c) is unmet unless items 3.3 and 3.4 are derived. Cap one day, from the candidate
   budget. It is a fourth C2 fan-out unit. The criterion is not changed by adding it.
5. **Prediction C2.6**, as written by the oversight chat: K6 covers at least 0.89 in every cell and
   meets (b) only in cells with between-donor share 0.1, so it fails (b) overall, and its price of
   validity equals HCP's at shares 0.3 and 0.5.
6. **ACS source changed (C3 only, not before the C2 memo).** The `ppi_py` census file has no state or
   PUMA and is not used. C3 reads, read-only, the 2018 ACS PUMS 1-Year person file for the 50 states
   and DC that the PPI track fetches through `folktables` into
   `results/round4/ppi/Q0_setup/acs_pums2018/` on Longleaf, recording the PPI commit its provenance
   carries. `whose()` will return `sibling`, and the addendum is the permission to read it. The GHCP
   paper's ACS numbers are reproduced by applying the released code's own `real_data/acs/`
   processing, with its defaults at the commit above, to that file; the year and horizon are
   confirmed from the released loader, and a mismatch is an escalation.
7. **Procedure.** Opening the gate pull request through the GitHub REST API (section 9) is accepted;
   the route used is recorded in the report. The full instruction document is on `main` at
   `docs/decisions/round4_conformal_track.md`; it is not added to this branch.

## 11. Instructions from Nicolas during interval 1 (1 October 2026)

1. **Local execution.** "If longleaf queue is long, run anything you can locally." The Longleaf
   queue held about 34,000 pending jobs and none of this track's jobs started in about ten hours,
   so the C1 grid, the GHCP reproduction and the C2 candidate runs execute on the local machine.
   Their PROVENANCE files record `slurm_job_id: none` and the local host. Real-data work that needs
   the Longleaf embeddings (C3) stays on Longleaf. Recorded under escalations in the C2 report.
2. **No pushes between gates.** Commits are made locally on `round4-conformal` and nothing is
   pushed until a gate's report is written; the branch and tag are then pushed together with the
   gate pull request (section 9).
3. **All compute back to Longleaf.** "Stop any local compute task and move all compute onto
   longleaf. My laptop is dying." Item 1 is withdrawn from that point. The C1 grid had already
   finished locally and is not rerun. The local GHCP reproduction was stopped and rerun on Longleaf
   (33 Slurm jobs, chunk subsets merged by the launchers' own aggregation). The four C2 candidate
   units stopped their local runs and reran on Longleaf; their partial local outputs are quarantined
   and unused.
4. **No local compute by default.** "Do not default any task to local compute unless I ask." Two
   later permissions, each for a named step: the merge, released plot scripts and comparison of the
   GHCP reproduction (Longleaf general and spill fully allocated, about 13,700 jobs pending), and
   the light gate table work (C1 merge and acceptance, C2 merge and criterion, the two figures, the
   numeric-claim sweep). The final reproduction job did in the end run on Longleaf; only a 9-second
   Python 3.13 check of one launcher ran locally under the first permission. Earlier, inside a
   one-hour local window Nicolas offered ("local compute can be available to you for the next
   hour"), one diagnostic of a few seconds recomputed two code-path draws.
5. **GitHub.** The stored credential was updated with pull-request read and write access, used only
   at the gate.
6. **ACS.** Downloaded and added as context; read in C3 only (section 10 item 6).
7. **Local compute for interval 2** (2 October 2026, in chat, with the C2 memo). "Local compute
   is allowed and preferred if it will genuinely speed up the process, until I tell you to stop
   it." This is Nicolas's explicit request under section 12.6, recorded here before any task runs
   under it. It covers C3 and C4 tasks where running locally is genuinely faster than the Longleaf
   queue; each such task records the local host in its PROVENANCE. It ends when Nicolas says stop.
   Work that needs Longleaf-resident inputs too large to copy (the HEST embeddings) stays on
   Longleaf.
8. **ACS source fallback** (same message). "If the PPI track has not put the ACS files on
   Longleaf, use the local copies I gave you." The local copy is `~/acs_pums2018/` (read-only grant:
   `acs_pums2018_all_columns.parquet`, `raw/`, `raw_manifest.json`, `fetch_info.json`,
   `folktables_stdout.txt`). The md5 check against `raw_manifest.json` of section 12.4 applies to
   whichever copy is read, and the C4 report records which one it was.
9. **Nine hours without permissions** (2 October 2026, about 04:20 UTC). "I will not be available to
   grant permission for anything for about 9 hours, so if anything is gated on my permission just
   work around it." For that window no task waits on an approval: no new network domains, host
   paths or credentials are requested; a unit that meets a block uses what is already reachable
   and records the gap as an escalation for C4. The 4-hour unstarted-job note of section 12.6 is
   still written, for Nicolas to read on return, and nobody waits on it. Never-yours items
   (outside contact, `main`, pushes between gates) and the C4 gate are unchanged.


## 12. The C2 decision memo, 2 October 2026 (oversight chat), verbatim

Handed over by Nicolas as `round4_conformal_C2_decisions.md` (it will be on `main` beside the
instruction document and is not added to this branch). Transcribed before anything in it runs.
Headings are renumbered under this section; the text is unchanged. Interval 2 starts when this
transcription is committed and pull request #3 is merged. Section 12.6 allows local work only for a
task Nicolas names in chat; section 11 item 7 is his later, general permission. I read item 7 as
governing until he withdraws it, and flag the difference to him with this transcription.

2 October 2026. Written by the oversight chat after reading `docs/round4_conf_C2_report.md` at tag `round4-conf-C2` (`fe36f6b`, pull request #3), `docs/round4_conf_lower_bound.md` and `docs/round4_conf_candidate_definitions.md`, and checking the report's numbers against the files it names. Nicolas hands this to the conformal session in full. Transcribe it into `docs/round4_conf_plan.md` as section 12 before anything in it runs. Interval 2 (C3 and C4, ending at the C4 gate) starts when the transcription is committed and Nicolas has merged pull request #3.

**The gate rule, in the wording Nicolas approved.** Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. This track's gates are C2 (the go or no-go) and C4. Contact with anyone outside the project is never the session's decision.

---

### 12.1 Acceptance

The C2 report is accepted, and the verdict under the fixed criterion stands. No candidate goes forward. Every number I checked reads back as quoted from `c1_report_numbers.csv`, `c1_acceptance.csv`, `c2_criterion.csv`, `c2_report_numbers.csv` and `c1_pool_rule_summary.csv`. The two literal acceptance failures (HCP at $K = 50$ against nominal, and the semi-real width ratio at $N = 500$) are read as the report reads them: the first is HCP's own calibration level and passes against it, and the second is the secondary setting, with the primary setting (CCRCC spot counts) passing both parts at 0.0041 and 0.035. The GHCP reproduction, 254 of 254 values within Monte Carlo error with the cause of the non-identity traced to the interpreter, passes and is not rerun.

Predictions scored as the report scores them. Most of mine on magnitudes were wrong, and C1.5 was wrong in direction. Section 3 says what the grid shows instead and what C3 does with it.

### 12.2 Decisions on the report's open items

1. **The quantile tie convention** (section 7.1). Keep this track's convention. With $n$ finite calibration scores and the test atom of mass $\frac{1}{n+1}$, the split conformal threshold is the $\lceil (n+1)(1-\alpha) \rceil$-th smallest score, and the standard exchangeability argument gives coverage at least $1 - \alpha$. At $n = 9$ and $\alpha = 0.1$ that is the ninth of nine, finite. The released code's upward resolution at the exact tie returns $+\infty$ there, which is valid and strictly more conservative. C3 runs the standard convention as primary and reports the code's finiteness beside it in every cell where the two differ, which at $\alpha = 0.1$ is $K = 10$ at $o = 0$. The paper states the convention in one sentence.
2. **The pool rule** (section 6.5). The paper's rule, equation (8), is primary in C3 because the corollary is stated for it. The code's rule runs as the secondary variant in every C3 cell at $\alpha = 0.1$, as in C1. The paper says, in one sentence with the worked example, that the released code's pool is one group larger than equation (8) and that the published tables were produced under the code's rule. Whether the authors are told is Nicolas's decision with David and Dr. Zhu; never the session's.
3. **A Python 3.13 rebuild** for a bit-identical reproduction. No. The reproduction criterion was within Monte Carlo error, it is met, and the cause of the residual is identified and recorded. Nothing further is spent on it.
4. **The shipped summaries outside the paper's tables** (section 7.3). Recorded, not pursued.
5. **The released repeated-subsampling baseline** averaging quantiles rather than the set of Dunn, Wasserman and Ramdas (escalation 5). Recorded. C3 does not run repeated subsampling.
6. **K6's tables from the stopped local run** (escalation 7). Accepted as they are, since K6 does not go forward.

### 12.3 What C1 shows, and what it changes in C3

I read `c1_grid.csv` directly at normal tails, $N = 500$, $\tau = 0$, share 0.3, $\alpha = 0.1$. Three facts shape C3.

- **The size donation costs one reference group, and at $K$ near $1/\alpha$ that is the whole budget.** At $K = 10$, GHCP at $o = 0$ calibrates on 9 groups with a test atom of mass exactly $\alpha$, so it covers 0.999 at a price of 2.09 where HCP covers 0.983 at 1.50. At $o = 5$ and $o = 10$ GHCP is still wider than HCP at $o = 0$ (prices 1.78 and 1.62), and its coverage stays above 0.987 at every $o$ up to 100. At $K = 20$ the cost is small (GHCP 0.944 at $o = 0$ against HCP 0.941) and at $K = 50$ it is gone. GHCP's gain from $o$ is almost entirely the adaptation; without it (`ghcp_noad`) the price at $K = 10$, $o = 100$ is 1.35 against 1.03 with it.
- **The within-donor split at $o \ge 25$ is nominal and narrower than GHCP at every $K$.** It covers 0.928 at $o = 25$ and 0.902 at $o = 100$ (its expected values are $\lceil (n+1)(1-\alpha)\rceil/(n+1)$ with $n$ the calibrating half), at prices 0.82 and 0.68 against the mixture oracle. This is the cheapest valid method once a slide carries 25 labelled spots, and it beats GHCP on width in every cell the report lists.
- **Below $o = 25$ the comparator is infinite only because it was built as the GHCP paper's Std-CP**, which spends $\lfloor o/2 \rfloor$ observations on recentring and calibrates on the rest. A plain within-donor split that calibrates on all $o$ observations with no recentring is finite from $o = 9$ at $\alpha = 0.1$ and valid by the same argument. It was not in C1.

So the $(K, o)$ map has three regions at small $K$. At $o = 0$, HCP. For $0 < o < 25$, GHCP is finite where the within split is not, but on this generator it is as wide as HCP or wider. From $o = 25$, the within-donor split. The joint-design consequence, which the PPI track's Q5 will state, is that at $K$ near 10 fewer than about 25 labelled spots per test slide buy nothing for the prediction set.

**C3 changes.**

1. Add the plain within-donor split (all $o$ observations calibrate the absolute score, no recentring) as a method at every $o \ge 5$, named `within_plain`, beside the Std-CP form, which keeps the name `within`. Its assumptions and guarantee go in the docstring before it runs.
2. The scaled score is dropped from C3, since K5 fails the criterion. The CQR score stays, but only as the top-decile diagnostic of prediction C3.4, inside GHCP and `within_plain`, on CCRCC only, with the quantile heads of round 3's A4 (`code/scripts/round3_a4_scores.py` or its successor) imported unmodified. If those heads cannot be reused inside a day, C3.4 is scored "not tested" and the report says why.
3. Prediction C3.2 is replaced, because C1 refuted its premise. **C3.2 (revised).** At $K = 10$ on every HEST task GHCP covers at least 0.97 at every $o$ and is wider than `within_plain` at every $o \ge 25$; at $o \le 10$ GHCP's width is within 10% of HCP's at $o = 0$ or above it. On the CCRCC $K$ sweep GHCP's coverage at $o = 25$ falls from above 0.97 at $K = 10$ to 0.93 to 0.95 at $K = 20$. Score the original C3.2 as "not tested, premise refuted in C1" and the revised one as a prediction written before C3 ran.
4. **Prediction C3.6**, new. The recentred cross-donor interval (the pooled `donor`-design quantile after shifting by the labelled spots' mean residual) covers within 0.03 of the pooled quantile's cross-donor coverage at $o = 5$ and within 0.02 of nominal at $o \ge 50$ on CCRCC and Indiana, and under-covers by at least 0.03 at every $o$ on lung, where the failure includes scale.
5. The `c3_o_sweep.csv` columns stay exactly as fixed (task, label_set, encoder, method, score, alpha, o, K, fold, draw, coverage, width_mean, width_median, n_test, finite), with `within_plain` as a `method` value. Q5 reads this file.

Everything else in C3 runs as the instruction document and addendum 1 say. Fan-out stays at eight units by task and axis.

### 12.4 ACS in C3

The PPI track's Q0 `ppi_py` file has no clusters and is used for nothing. Nicolas has fetched the 2018 ACS PUMS person file (1-Year, 50 states and DC, every column) through `folktables`, and the PPI track is placing it at `results/round4/ppi/Q0_setup/acs_pums2018/` in the Longleaf project tree with an md5 check against `raw_manifest.json`. C3's ACS units read that directory read-only, verify the md5s against the manifest beside it before reading anything else, and record the PPI commit whose provenance it carries. `whose()` will return `sibling`; this memo is the permission. Reproduce the GHCP paper's ACS tables (5, 12, 13) by running the released code's own `real_data/acs/` processing at commit `d1a69f4a` on that file, which is the acceptance the instruction sets, and only then run C3's ACS rows. If the directory is not there when C3 starts, run the HEST units and add ACS when it appears, as the instruction allows; if it is still absent when the HEST units finish, the C4 report says so and ACS is not run.

### 12.5 The lower-bound scoping, closed

The scoping ends here, with the cap unspent, and the session does no more theory in this track. What it produced, and where it goes.

- **Propositions 1 and 2** are derived with proofs, and I checked Proposition 1's algebra and the step-3 construction of Proposition 2. The exchangeable analogue of Proposition 2 (a valid distribution-free set with $n < (1-\alpha)/\alpha$ calibration points must be infinite with positive probability) is standard, so the group-level version is a direct lift rather than a new result. Proposition 1, the quantitative coverage floor for methods that are finite almost surely, I have not seen stated, but it is a remark, not a contribution. Both go into the paper's prediction-set section as one remark with the proofs in an appendix, stating that for $K + 1 < 1/\alpha$ the price of validity is characterised (infinite expected width for every valid method, the forced infinite probability $1 - \alpha(K+1)$ attained by randomised HCP, and the floor $1 - \beta^\star$ for finite outcomes), and that for $K + 1 \ge 1/\alpha$ the question is open.
- **The switch rule** is invalid as stated (the point-mass counterexample), the repaired rule is valid only with laws revealed exactly, does not dominate HCP, and loses $K\gamma$ at finite $N_k$. It is not pursued and K6 is dropped. The section 5 conjecture is reported in the paper as open, in one sentence.
- Whether to write to Dobriban and Lee about the $o = 0$ question, the pool rule or the tie convention is Nicolas's decision with David and Dr. Zhu.

### 12.6 Where interval 2 runs

Every C3 and C4 job runs on Longleaf through Slurm, under `rc_tengfei_pi` as recorded, with walls sized from a sibling's `sacct` and never a blanket limit. Nicolas's section-11 instructions covered the C1 and C2 work they named and do not carry forward. Nothing runs locally unless Nicolas asks for that specific task in chat; each such request is recorded as a numbered extension of plan section 11 before the task runs. If a job has not started four hours after submission, the session tells Nicolas in chat what the job needs (inputs and sizes, memory, expected runtime, queue state) and keeps waiting; it does not move the job or harvest its inputs. Light gate-table work (merges, the criterion table, figures, the numeric-claim sweep) is covered by Nicolas's section-11 item 4 and stays as it is.

### 12.7 Procedural points

1. **The pull request.** Pull request #3 is open at `fe36f6b`. Nicolas merges it with a merge commit after handing over this memo. The C4 pull request follows plan section 9.
2. **The instruction document** is on `main` as `docs/decisions/round4_conformal_track.md`; this memo will be beside it as `round4_conformal_C2_decisions.md`. Neither is added to the branch.
3. **Writing.** `docs/round4_conf_lower_bound.md` and the C2 report render; keep display equations with each `$$` on its own line in the C4 report and the C3 outputs' documentation.
4. **Sub-agent frame ids.** Each brief states the sub-agent's own frame id, and the lead checks the stamp on each hand-back before merge.

### 12.8 What the C4 report decides

Besides the instruction's C3 and C4 content, the C4 report scores C3.1, revised C3.2, C3.3 (expected "not tested"), C3.4, C3.5 and C3.6, confirms that `c3_o_sweep.csv` carries `within_plain`, and closes with the one-page "What the conformal track established", whose last paragraph states what the paper's prediction-set section says. Report and wait.

## 13. The C4 decision memo, 2 October 2026 (oversight chat), verbatim

Handed over by Nicolas as `round4_conformal_C4_decisions.md`. Headings are renumbered under this
section; the text is unchanged. It closes the track. Per section 13.3 nothing further is done:
this transcription is committed on the local branch only, and pull request #5 is not touched.

2 October 2026. Written by the oversight chat after reading `docs/round4_conf_final_report.md` at tag `round4-conf-final` (`d65626f`, pull request #5) and checking its numbers against `results/round4/conformal/C3_real/c3_report_numbers.csv`, `c3_o_sweep_by_task.csv`, `c3_K_sweep_by_task.csv` and `c3_merge_checks.csv`. Nicolas hands this to the conformal session in full. It closes the track; there is no further stage, and the session does nothing after transcribing it as plan section 13 except what section 3 lists.

**The gate rule, in the wording Nicolas approved.** Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. Contact with anyone outside the project is never the session's decision.

---

### 13.1 Acceptance

The final report is accepted and the track is complete. Every number I checked reads back as quoted. The C3 grid is complete as instructed: CCRCC (24 donors and the 23-donor merge), Indiana, lung and ACS, three encoders on the HEST tasks, $o \in \{0, 5, 10, 25, 50, 100, 200\}$ with $K = 10$, the CCRCC $K$ sweep from 4 to 20 at both $\alpha$ with the training-donor count recorded, lung at $K \in \{6, 8, 10\}$, and `within_plain` present as a method in `c3_o_sweep.csv.gz`. The anchors (A4b to $10^{-12}$ in coverage, the merge with zero duplicated keys, the $K$ and $o$ units agreeing on their shared rows) pass. The GHCP paper's ACS tables reproduce at 53 of 53 values.

Predictions scored as the report scores them. The two that did not hold (C3.5's lung and ACS ordering, C3.6 on CCRCC and lung) are both cases where the real tasks have smaller cross-donor shortfalls than round 3 led me to expect, and the recentred interval over-covers rather than under-covers. Both are findings, not problems.

### 13.2 What the record says, for the paper

Three readings of the C3 tables go into the paper's prediction-set section beside the five points the report's closing page lists.

1. **The three regions of the $(K, o)$ map hold on real data.** At $K = 10$ GHCP covers 0.98 to 1.00 at every $o$ on every HEST task, is 1.23 to 1.49 times HCP's width at $o \le 10$, and is 1.5 to 2.3 times `within_plain`'s width wherever both are finite. `within_plain` covers 0.90 to 0.92 from $o = 10$ on every task. The joint-design statement is as the C2 memo put it: at $K$ near 10, fewer than about ten labelled spots per test slide buy nothing for the prediction set, and from ten on the within-donor split is the cheapest valid choice.
2. **Within the within-donor family, the plain split is the only finite choice below $o = 25$, and the recentred half-split (`within`, the GHCP paper's Std-CP form) is narrower from $o = 25$ on.** On CCRCC `within_plain` is finite at $o = 10$ (coverage 0.91, mean width 2.32) where `within` is infinite; at $o = 25$ `within` has width 2.14 against 2.30, and at $o = 100$ 1.75 against 2.11, both at coverage 0.90. The paper says so in one sentence, so a practitioner knows which to use at which $o$.
3. **The recentred cross-donor interval is a usable heuristic above $o = 25$ on CCRCC and lung but over-covers**, by 0.03 to 0.04, because the shift is applied to a quantile that was already conservative on those tasks; on Indiana it is at nominal from $o = 50$. It has no guarantee and is reported as the practitioner's shortcut, not a recommendation.

The ACS rows (escalation 1) use states and the PPI track's task definition and predictor, which is what the paper's ACS application uses on the inference side, so the two halves of the paper read the same dataset. The reproduction of the GHCP paper's own ACS task (California PUMAs) is the acceptance check and is cited as such. Nothing more is run.

### 13.3 What the session does before stopping

1. Transcribe this memo as plan section 13.
2. Nothing else. The pull request #5 stays open for Nicolas to merge with a merge commit; the session does not touch it.

### 13.4 Records and decisions on the escalations

- 1 (ACS grouping): accepted, read as in section 2.
- 2 (no manifest on Longleaf): accepted; the PPI track's transfer check covers the Longleaf copy and the parquet md5 matches.
- 3 (ACS $K \le 10$ within fold; the cross-fold extension to $K = 20$ has only a heuristic guarantee): the extension is not used in the paper.
- 4 (stamps carrying the lead's frame id, again): recorded. This happened in three sessions in a row despite the brief; the fix goes into `docs/WAYS_OF_WORKING.md` as a procedure (the lead writes each sub-agent's frame id into its brief and checks the stamp before merge), which the oversight chat applies on `main`.
- 5 (lung size-matching target): accepted as the core unit's documented choice.
- 6 (widths agree across CPU vendors to $10^{-10}$): recorded; coverage is unaffected and the tolerance rule of `WAYS_OF_WORKING.md` already covers it.
- 7, 8, 9: recorded. Local runs under Nicolas's section 11 item 7 were his instruction and are his.

### 13.5 Open decisions, above the sessions

- Whether to tell Dobriban and Lee about the pool rule and the tie convention: Nicolas with David and Dr. Zhu.
- Whether the $o = 0$ improvability question is pursued anywhere: not in this project's round 4 or 5; it is recorded as open.

### 13.6 Hand-off to the PPI track

The PPI track's Q5 reads `results/round4/conformal/C3_real/c3_o_sweep.csv.gz` from `main` after pull request #5 is merged, with `within_plain` as a method value, and records the merge commit. A separate note tells that session so.
