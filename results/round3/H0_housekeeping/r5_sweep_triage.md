# H0 item 2: triage of the unresolved claims in `docs/r5_idc_provenance.md`

Two hours, as the A1 decision memo allows, then stopped. Written 22 September 2026 by the H0
housekeeping track. What follows is the record of what the forty-one unresolved claims were, what
they are now, and what was changed. The document's findings were not rewritten.

## 1. The forty-one claims, and why the count is now zero without anyone having fixed them

The A1 report records forty-one unresolved claims in this document under the corrected sweep
invocation, measured on the cluster working copy at the A1 commit. Run today at `d3ce2b7` with the
same invocation, the document reports sixty claims and zero unresolved. The change is not a repair.
It is stage D0: the citation this document names for most of its numbers is `HEST_v1_1_0.csv`,
HEST-1k's own per-sample metadata table, which R5 could not read (HTTP 401, gated dataset, recorded
in the document's own section 6). D0 downloaded HEST's release tables into
`results/round3/D0_inventory/release_tables/`, so that basename now resolves inside the repository
and every claim citing it is checked against a 1,229-row metadata table of every HEST sample.

This is not a property of the clone. The same invocation run on the Longleaf working copy at the
same commit, where the untracked working data is present (job 2126477, partition actually used
spill, node c151606), also reports sixty claims and zero unresolved for this document, and reports
the document's own single-document run identically.

Reproducing the forty-one is a one-flag change, which is how they were identified for this triage:

```
python code/scripts/verify_numeric_claims.py docs/r5_idc_provenance.md \
    --search-dir . --exceptions .verify-exceptions --derived .verify-derived \
    --always results/summary/deck_numbers.csv --exclude-dir release_tables
```

That run wrote forty-one rows, across twenty lines and eleven distinct values, in the document as it
stood before this triage:

| value | claims | what the document states it is |
|---|---|---|
| 280 | 17 | real gene targets in the shared pre-designed breast panel |
| 0.2740 | 5 | NCBI783's pixel size in µm/px |
| 0.3639 | 5 | NCBI785's pixel size in µm/px |
| 313 | 3 | real gene targets in panel design PD_260, from the raw GEO `gene_panel.json` |
| 288 | 3 | NCBI783's real-gene count after its eight-probe add-on |
| 321 | 2 | NCBI785's real-gene count in HEST's ingested files |
| 261 | 2 | control probes in TENX95 and TENX99 |
| 533 | 1 | panel entries shared between NCBI783 and each TENX sample |
| 253 | 1 | control probes in NCBI783 |
| 220 | 1 | control probes in NCBI785 |
| 784 | 1 | not a claim; the middle of the sample-id run `NCBI783/784/785` |

## 2. What the release table actually matches, which is the part worth reporting

The forty-one claims pass because the value is present somewhere in the cited table, not because it
is present as the quantity claimed. Checked cell by cell in
`results/round3/D0_inventory/release_tables/HEST_v1_1_0.csv`:

- 280 matches `spots_under_tissue` for SPA14, NCBI196 and NCBI189, none of them IDC samples.
- 313, 321, 288, 533, 253, 261 and 220 likewise each match some other sample's
  `spots_under_tissue`.
- 0.2740 matches `pixel_size_um_estimated` for TENX159, TENX149 and MISC42, not for NCBI783, whose
  stored value is 0.2739598559774087 and which the document's section 1 table rounds to four
  decimals.
- 0.3639 is the one honest match: it is NCBI785's own `pixel_size_um_estimated`.
- 784 is a token the number parser takes out of a sample-id run, in the same class as the UUID
  defect already recorded in `docs/WAYS_OF_WORKING.md`. It is a checker defect, not a claim, and it
  is reported here rather than declared as an exception.

The sweep's docstring states this limitation itself: it checks that a value is in the cited file,
not that the cited file is the right file for the value. This document is the case where that
limitation bites hardest, because a reading task's numbers come from vendor pages and GEO records
and its one repository-resident citation is a table of every sample in HEST-1k. A zero on this
document is therefore weak evidence, and the A3 report should quote it as such.

## 3. What was changed

1. A closed-record banner at the top, in the style of the banners in `docs/decisions/`, stating
   that nothing in the document is maintained and that the IDC attribution question it answered
   from the vendor pages is reopened by HEST v1.3.0's sibling ids and is now stage D3's.
2. A paragraph after the title naming the repository files that carry the panel and resolution
   quantities as the document states them, so that those claims are checked against the right
   quantity instead of against the release table: `r5_idc_panels_observed.csv` for per-sample panel
   composition, `r5_idc_panel_pairs.csv` for the pairwise shared-entry counts including the
   500-entry intersection, and `sample_metadata.csv` for pixel size. These three files are R5b's
   own outputs and the document's section 5 already names the computation behind them; what was
   missing was the citation.
3. One entry in `.verify-exceptions`, for 313, the PD_260 panel-designer real-gene count. That
   number is read from a raw GEO `gene_panel.json`, which is not in the repository and is not
   derivable from anything that is; the repository's own ingested count for the same sample is 321,
   and the gap between them is the open discrepancy the document reports. The same value is used
   for the same quantity in `docs/round2_R5_stage_report.md`, and the entry covers both.

The entry is written with the `external:` class that the file's own r5 block already uses, rather
than the `historical:` class the memo names, because the exceptions file's header rule ties the
class to the reason and the reason here is a source outside the repository rather than a
superseded measurement. This is a deviation from the memo's wording, recorded rather than silent.

## 4. Not checked, and left open

- The document's findings were not re-derived. Nothing here revisits whether TENX95 and TENX99 are
  one donor; that is D3's, and the banner says so.
- Section 1's pixel sizes are rounded restatements of `sample_metadata.csv`'s stored values
  (0.2740 against 0.2739598559774087). They were left as the document wrote them. Under the
  checker's precision rule a document may write fewer decimals than the source carries, so whether
  this pair matches depends on whether the comparison truncates or rounds; it was not established
  which, and 0.2740 currently resolves against an unrelated sample's pixel size in any case.
- 500, the four-sample panel intersection, is silenced globally by an exceptions entry belonging to
  another document (a round-2 planning threshold of 500 spots). It is now also legitimately cited
  through `r5_idc_panel_pairs.csv`, but the exceptions file is value-keyed, not document-keyed, so
  one document's declaration silences every other document's use of the same number. That is a
  structural limitation of the exceptions format, reported rather than worked around.
- No attempt was made to fix the checker. That is the rule in `docs/WAYS_OF_WORKING.md` for a false
  failure, but the checker is not this track's file to edit, so the two defects found here, the
  sample-id fragment and the wrong-quantity match, are reported.
