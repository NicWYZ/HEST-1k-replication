# `docs/` — document index

One row per document in this directory, in chronological order by the date the document
itself states (its own header/opening line — not filesystem mtime; two documents below
carry no date at all, and that is noted rather than papered over with a file timestamp).
Regenerate this list by hand when a document is added, removed, or renamed — it is not
script-generated.

| # | Document | Date (from the document) | What it is | Status |
|---|---|---|---|---|
| 1 | [`HEST_replication_handoff.md`](HEST_replication_handoff.md) | 12 September 2026 | Original handoff for the HEST-1k replication: stage-by-stage execution plan, ground rules, and reporting format for the round-1 (faithful-replication) work. | Current — still the cited source for the original stage plan and ground rules. |
| 2 | [`round1_final_stage_report.md`](round1_final_stage_report.md) | Revision 2, generated 2026-09-16 | Round 1's comprehensive final report: the faithful-replication result, the instrumentation layer, and the first pass at tailored analyses. | **CLOSED — historical record, not maintained.** Frozen per the project's own rule that a stage report is written once and not edited afterward. It contains numbers round 2 later withdrew (e.g. the "institution shift" scalar, the COAD same-patient reading) — see `round2_R0_R1_stage_report.md`'s relabelling note for what changed and why. Do not cite its withdrawn numbers as current. |
| 3 | [`HEST_replication_review.md`](HEST_replication_review.md) | Written 16 September 2026 | Independent audit of the round-1 replication and instrumentation layer (against commit `eb670fa` and the final stage report, revision 2): what to keep, what three attribution claims the data don't support as stated, and the scan-resolution/patient-identity confound the round-1 report didn't discuss. | Current — the audit that motivated round 2's plan. |
| 4 | [`round2_execution_plan.md`](round2_execution_plan.md) | Prepared 16 September 2026 | Round 2's execution plan: implements the review's Sections 6–7, specifies stages R0–R8, and sets the reporting format (its Section 13) that every subsequent round-2 stage report follows. | Current — round 2's stage reports still cite its Section 13 for reporting format. |
| 5 | [`round2_R0_R1_stage_report.md`](round2_R0_R1_stage_report.md) | 17 September 2026 | Stage report for round 2's R0 (scan-resolution columns, README relabelling) and R1 (a report-and-wait boundary). Contains the relabelling note explaining exactly which round-1 claims were withdrawn and why. | Frozen stage report, per the project's write-once convention; its content is restated (not replaced) by `round2_R3_stage_report.md`. |
| 6 | [`round2_R3_stage_report.md`](round2_R3_stage_report.md) | Prepared 18 September 2026 | Stage report covering R0, R1, R1b, R2 and R3, restating the R0/R1 results so the document stands alone. Implements `round2_R1_decisions.md` (pending — see below) and the execution plan. | Frozen stage report. |
| 7 | [`round2_R5_stage_report.md`](round2_R5_stage_report.md) | Prepared 18 September 2026 | Stage report for the interval opened by `round2_R3_decisions.md` (pending — see below), covering R4 and R5 only. | Frozen stage report. |
| 8 | [`round2_R8_stage_report.md`](round2_R8_stage_report.md) | Prepared 19 September 2026 | Stage report covering R5b (donor provenance audit), R5c (replicate-leak generalisation), R6 (donor-grouped variance/theta), R7 (per-gene decomposition), R8 (H-Optimus-1 on raw heads), written under the R5 decisions memo (`round2_R5_decisions.md`, pending — see below). | Frozen stage report. |
| 9 | [`round2_closeout_report.md`](round2_closeout_report.md) | 19 September 2026 | Round 2's closeout: the two restatements (θ₁ against `morphology_v2`, the pooled between-donor estimate), the repository freeze at commit `3161a61` tagged `round2-final`. | Current — the authoritative summary of what round 2 concluded and where the repository stood at freeze. |
| 10 | [`WAYS_OF_WORKING.md`](WAYS_OF_WORKING.md) | No date in the document | Running list of process rules, each tied to the failure it prevents (e.g. "a relabelled claim must be swept for, not just edited where remembered"). Added to as each round finds a new one. | Current — living document by design; not dated because it has no single authorship date, only accretion. |
| 11 | [`hest_bench_issue_draft.md`](hest_bench_issue_draft.md) | No date in the document | Draft GitHub issue for the HEST-1k authors, covering the IDC same-donor replicate pair, the Table A4 Xenium sample-count discrepancy, and missing H&E scan provenance. | **UNSENT — draft only.** The document says explicitly that sending it is Nicolas's call, not this session's. Item 1's evidence carries an unresolved attribution caveat (whether HEST's own metadata assignment of TENX99 vs TENX95 to the two "FFPE Human Breast" GEO pages is correct) that could not be closed because the source 10x pages returned HTTP 429 on every re-fetch attempt — treat item 1 as open, not settled. |
| 12 | [`deck_master_outline.md`](deck_master_outline.md) | 22 September 2026 (title-slide credit line; the only date the document gives) | Master outline for the round-2 progress-update deck: twelve main slides plus two backup slides, speaker notes, figure references into `figures/deck/`. | Current — the live outline for the upcoming presentation. |

## Pending — not yet in `docs/`

Six documents that later reports in this list cite or implement are referenced repeatedly
across `docs/`, `README.md`, and the `code/scripts/` docstrings, but are not present anywhere
in the repository (checked by filename search, not just in `docs/`). They are Nicolas's to
supply, not this session's to draft, so they are listed here as pending rather than omitted
silently:

- `round2_R1_decisions.md` — the oversight chat's decisions on the R0/R1 report; implemented by `round2_R3_stage_report.md`.
- `round2_R3_decisions.md` — decisions opening the R4/R5 interval; implemented by `round2_R5_stage_report.md`.
- `round2_R5_decisions.md` — the "R5 decisions memo" that closes round 2 in a single interval with no interim stop-and-report conditions; implemented by `round2_R8_stage_report.md`.
- `round2_closeout_decisions.md` — the closeout memo `round2_closeout_report.md` is written against, later extended for the deck (its own section 1.3).
- `deck_figures_and_repo_update.md` — the instruction memo behind the current deck-and-repository-refresh work itself: every `code/scripts/` Stage: line for this round of work cites a section of it, and `deck_master_outline.md` calls it "the companion instructions to the execution session," but the file itself is not checked in anywhere in the repository.
- `r5_idc_provenance.md` — cited as a completed R5 deliverable in `round2_R5_stage_report.md`'s stage table and referenced from `README.md` and `hest_bench_issue_draft.md`, but not found anywhere in the repository under that name. This is flagged here as a document reference with no corresponding file, established by filename search rather than by confirming its absence is intentional — it may simply be misplaced rather than genuinely missing.

*Note on method: dates in the table above were read from each document's own opening lines,
not from `ls -la` timestamps, which reflect when a file was last touched on Longleaf (all
recently, from the round-2 reorganisation) rather than when it was written.*
