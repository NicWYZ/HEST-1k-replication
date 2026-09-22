> **Superseded on 22 September 2026 by `docs/round3_A1_stage_report.md`, and moved here rather
> than deleted.** This was the live note written when the session parked mid-interval-1. Its
> A0 numbers are correct and are restated in the stage report; its D0 section was explicitly
> labelled as unverified leads and several of those leads were refined once the D0 tables were
> built, in particular the institution-set finding, which the proposal states precisely. Read
> the stage report and `docs/round3_d0_expansion_proposal.md` instead of this file.

> **Live note, opened 2026-09-22.** Where round 3 stood when the session parked, and what the next
> session does first. Deleted or folded into the A1 stage report once interval 1 closes.

# Round 3 park note, 22 September 2026

The session parked mid-interval-1 because Nicolas was about to lose internet. Nothing is held only
in a session. This note records what is verified, what is still queued on Longleaf, and the first
three actions on pickup.

## Interval 1 status

| stage | state |
|---|---|
| S0 | complete, committed at `e32e1d5` |
| task definitions | complete, eleven files in `results/round3/task_defs/` |
| A0 harness | acceptance checks passed on two encoders; a third encoder's run is still queued |
| A1 | not started |
| D0 | partial: the HuggingFace listing is captured, the inventory tables are not built yet |

## A0 passed, and by a wide margin

Both stop-condition checks pass. Numbers below are read back from the files named, not from the
sub-agent's report.

**H1, the anchor to the prior result.** With the calibration fraction set to zero on the `patient`
design, the harness reproduces R1b's `intercept_f64` per-task Pearson on 20 of 20 encoder-task
cells, two encoders (`hoptimus0`, `resnet50`) over all ten tasks. The largest absolute difference
is $5.6 \times 10^{-17}$ against a tolerance of $10^{-6}$, so the agreement is at floating-point
resolution rather than merely inside tolerance, and the harness is the R1b pipeline.
Files: `results/round3/A0_smoke/h1_by_task__hoptimus0__h1.csv`, `h1_by_task__resnet50__h1.csv`,
each citing the R1b table it was checked against in its `r1b_source` column.

**H2, harness correctness.** On `random` with the `abs` score, marginal coverage pooled over folds
passes on 20 of 20 cells. The worst deviation from nominal 0.90 is 0.0012, on LUNG with
`resnet50`, against a tolerance of 0.02, so the worst cell sits about 17 times inside the bound. No
fold produced an infinite conformal quantile. Files: `h2_coverage__hoptimus0__h2.csv`,
`h2_coverage__resnet50__h2.csv`.

**H3, disjointness.** 368 fold rows across all four designs, `random`, `patient`, `donor` and
`slide_out`. Every row has $T$, $C$ and $E$ disjoint on (sample id, barcode), and the scaler and PCA
fit-row count equal to $|T|$ with zero difference in the fitted means and variances against $T$.
Files: `h3_disjointness__*.csv`.

H4 is partly evidenced: explicit parquet schemas, summaries written before parquets, and provenance
carrying job id, the partition actually used, node, commit, command line and config hash are all
present in `PROVENANCE__*.txt`. The determinism half of H4, a byte-identical rerun, was not
reached.

## A1 sizing, measured rather than estimated

The `#SBATCH` directives written into `submit_job`'s command string **are** honoured: `sacct`
records ReqCPUS 4 and ReqMem 32G for jobs 2042057 and 2042058, as requested. An earlier suspicion
that they were dropped came from job 2037596, which recorded 1 CPU and 1000M; whatever caused that
was specific to that job's script and does not apply generally. Establish it once more with a probe
before the twelve-encoder sweep rather than trusting either observation.

Measured cost of the H2 run, which is ten tasks on one design with five repeats: 22 minutes wall
for `hoptimus0` (job 2042057) and 16 minutes for `resnet50` (job 2042058), both at 4 CPUs and
32 GB on partition `spill`. A1 is four designs and two scores, so budget on the order of two hours
per encoder and set the harness ceiling from queue time plus that, not from that alone. Queue wait
on the day was 13 to 35 minutes for 4-CPU jobs.

## Still queued on Longleaf, and safe to leave

Two jobs were PENDING at park and were deliberately not cancelled. They write into the directories
already listed above, so their outputs are recoverable without re-running anything.

| job | ask | what it is |
|---|---|---|
| 2042059 | 4 CPU, 32 G, 10 h wall, `spill` | the third encoder's A0 acceptance run |
| 2044616 | 4 CPU, 8 G, 2 h wall, `spill` | the D0 inventory build |

Check them with `sacct -j 2042059,2044616 -o JobID,State,Elapsed,MaxRSS` and read their outputs
from `results/round3/A0_smoke/` and `results/round3/D0_inventory/` on Longleaf.

## First three actions on pickup

1. `git pull --ff-only origin main` in the Longleaf tree, which is behind at `fce1ad8`.
2. Read the two queued jobs' state and outputs, and fold the third encoder's H1 and H2 rows into the
   acceptance tables. Finish D0 from `hf_file_listing.csv.gz` and `release_tables/`, which are
   already on disk, so the HuggingFace listing does not need re-fetching.
3. Run A1, then write `docs/round3_A1_stage_report.md`. A1 runs `slide_out` only on PRAD, READ and
   IDC under audited labels, for the reason in `docs/round3_execution_plan.md` § 10 item 3.

Then stop at the gate and wait for the decision memo.

## D0 leads, not yet verified against files

The D0 track established these before it was stopped, and its inventory tables were not built, so
they are recorded here as leads rather than as results. Each is to be re-derived from
`results/round3/D0_inventory/` once job 2044616 lands, and none of them should be quoted in the A1
report until it has been. They are written down now because they bear on a decision Nicolas owns.

**The institution set's stated criterion may not be satisfiable anywhere in HEST.** No
organ-by-technology cell is reported to support three distinct generating institutions with three
or more labelled donors each. The best case is two: human kidney on Visium, with a Sorbonne cohort
at 24 donors and a WashU/KPMP cohort at 22. Human breast on Visium, which the earlier review named
as a candidate, is reported as only eight unlabelled 10x product-page samples, and human breast on
legacy Spatial Transcriptomics as a single Stockholm lab with byte-identical section pairs across
its cohorts, which is the IDC trap again rather than an institution contrast. If that holds, the
handoff's institution set cannot be built as specified and the choice, between two institutions,
a different organ, or a different axis, is Nicolas's to make on the D0 proposal.

**HEST has moved on from the release on disk.** Releases v1_1_0 through v1_3_0 exist at the
repository root, growing from 1,229 to 1,276 samples; the project's table is v1_1_0. From v1_2_1
onward HEST corrected the COAD patient labels to TENX147 as Patient 5, TENX148 as Patient 2 and
TENX149 as Patient 1. That matches round 2's R5b donor audit exactly, which reached the same
three-donor mapping from the 10x and GEO records rather than from HEST. The audit was right, and
upstream now agrees with it. TENX111 is reported as still unlabelled upstream, which is also what
the audit found.

**The upstream patient field is worse than the benchmark subset suggested.** Of 1,276 samples,
870 are reported to carry no patient label, 114 to carry a whitespace-only label that is
nonetheless non-null, and only 292 to be usable. Twenty-seven of 78 human label strings are reused
across cohorts, so a donor has to be keyed on the pair (dataset_title, patient) rather than on the
label alone. Fifteen pairs of sample ids are reported byte-identical including their expression,
one of them across two different kidney cohorts. If these hold, D3's audit is not a formality on
the expansion sets, and the donor-power set's donor count has to be built from the keyed pair.
