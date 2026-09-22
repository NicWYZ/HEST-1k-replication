# Instructions: closing the gate the closeout report left open

21 September 2026. For the execution session on `NicWYZ/HEST-1k-replication`, following `docs/closeout_gate_report.md` at `6acbef2`. None of this touches the presentation, which has been built against the repository as it stands. There is no deadline on this beyond "before round 3 starts." One report at the end.

The gate report was right to stop rather than guess at 437 entries. What follows is the triage policy it asked for, so the work can proceed without inventing reasons.

---

## 1. Triage policy for the unresolved claims

Every document in `docs/` gets one of three treatments, decided by what the document is, not by its count.

**Historical records** (`round1_final_stage_report.md`, `HEST_replication_review.md`, `HEST_replication_handoff.md`, `round2_execution_plan.md`, and all four decision memos once supplied). These are not edited. Each gets a one-line banner at the top stating the date, that it is a closed record, and that numbers in it may have been superseded by later stages; and an exceptions file that marks every unresolved claim as `historical`. The sweep then passes at zero unresolved for them by construction, and the banner is what tells a reader why. The point is that a record is not made false by later work, and the repository should say so once rather than per number.

**External-source documents** (`r5_idc_provenance.md`). Claims whose source is a DOI, accession, vendor page or issue thread get an exceptions entry naming the external source. Anything left after that is a real gap and is fixed.

**Maintained documents** (README, `deck_master_outline.md`, `WAYS_OF_WORKING.md`, `hest_bench_issue_draft.md`, and every round-2 stage report including the closeout). These must reach zero unresolved by fixing, not by exception, with two allowed exception classes: `derived` (a difference, ratio, share or dispersion computed from cited cells; the exceptions entry gives the formula and the cells) and `cost` (a wall time, queue time, file count or byte count with no result file behind it, allowed only in `WAYS_OF_WORKING.md` and the stage reports' process sections). If the sweep cannot read a cited file because it exceeds the 200 MB cap, that is the sweep's limitation, not the document's, and it is fixed in the sweep (§ 2), not by exception.

The order of work is the two largest maintained documents first, since they carry the most numbers the deck rests on indirectly: `round2_R3_stage_report.md` (99) and `round2_R5_stage_report.md` (90). Then `round2_R8_stage_report.md` (11), `round2_closeout_report.md` (2), `hest_bench_issue_draft.md` (21), `WAYS_OF_WORKING.md` (20). Then the historical set with its banners. Then `r5_idc_provenance.md`.

For every claim triaged, the exceptions file records the claim text, the class, and the reason. A claim that turns out to be wrong is corrected in the document with a one-line changelog entry at the bottom of that document, not silently.

## 2. The sweep itself

Two defects to fix before the triage, since both would otherwise produce false unresolved entries.

- `round2_R0_R1_stage_report.md` was killed at 64 GB. The sweep loads cited files whole; make it read CSVs in chunks or with column selection so that a per-document run stays under 16 GB. Then assess that document.
- Add support for the `derived` class: given an exceptions entry with a formula over named cells, the sweep evaluates it and verifies the claim rather than skipping it. That turns most of the R3 and R5 counts into verified claims instead of exceptions.

Report, per document, the counts before and after.

## 3. Repository gaps the closeout named

- `results/summary/results_encoder.csv` is missing H-Optimus-1's `raw_ridge` cells even though R8 produced them. Add them via `build_summary_tables.py`, not by hand, and confirm the file regenerates byte-identical afterwards.
- `code/scripts/round2_r5b_audit.py` does not exist. The audit was a reading task, so a script cannot redo the reading, but it can regenerate `donor_audit.csv` from two inputs that should be committed as the audit's record: `hest_source_map.csv` (which exists) and a new `donor_verdicts.csv` holding each sample's manually determined `donor_id`, `donor_label_status` and the source citation. The script joins them, applies the COAD subseries rule, and writes `donor_audit.csv`; assert it reproduces the committed file exactly. The README's reproducibility gap then closes.
- The four decision memos, the results synthesis and the literature landscape are pending from Nicolas. When they arrive, commit under `docs/decisions/` and `docs/`, add them to `docs/README.md`, banner them as historical per § 1, and run the sweep over them.
- The commit-message accounting rule from the gate report becomes a line in `WAYS_OF_WORKING.md`: a commit message that summarises a gate states the full table or points to the file that does, never a subset.

## 4. Not in scope

`raw_xgb` for H-Optimus-1 stays closed. The IDC attribution stays as recorded unless a properly spaced page fetch is attempted; one attempt, an hour clear of any prior attempt, is allowed, and the result is recorded either way. The nine unverifiable donor labels, the missing bootstrap intervals and the nested-ANOVA diagnostics stay in the known-limitations list.

## 5. Report

Three paragraphs when done: the per-document before-and-after table for the sweep; what was corrected in any document and why; and anything that could not be resolved, with the reason. Tag the final commit `round2-docs-clean`.
