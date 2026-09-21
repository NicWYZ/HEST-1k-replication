# Closeout gate report (section 2.6)

Written 21 September 2026, against commit `a220974` and tag `round2-final-deck`.

**This file corrects the gate accounting in `a220974`'s commit message, which was
incomplete.** That message named four documents as failing the numeric-claim sweep and
presented the list as the complete accounting. It was not: seven more documents also had
unresolved claims, one of which is this round's own closeout report and one of which is a
document that same commit added, and one document was not assessed at all. The full table
is below. The omission was mine, not the sweep's -- the data was in front of me when I
wrote that message.

## 1. The sweep, every document

`code/scripts/verify_numeric_claims.py`, one document per process, 64 GB, with
`--always results/summary/deck_numbers.csv` and each document's own exceptions file.

| document | claims | verified | unresolved | uncited |
|---|---|---|---|---|
| `README.md` | 225 | 225 | **0** | 0 |
| `docs/deck_master_outline.md` | 160 | 160 | **0** | 0 |
| `docs/README.md` | 0 | 0 | 0 | 0 |
| `docs/round2_closeout_report.md` | 11 | 9 | 2 | 0 |
| `docs/round2_execution_plan.md` | 36 | 30 | 6 | 0 |
| `docs/round2_R8_stage_report.md` | 144 | 133 | 11 | 0 |
| `docs/WAYS_OF_WORKING.md` | 33 | 13 | 20 | 0 |
| `docs/hest_bench_issue_draft.md` | 56 | 35 | 21 | 0 |
| `docs/round1_final_stage_report.md` | 169 | 118 | 51 | 0 |
| `docs/r5_idc_provenance.md` | 63 | 11 | 52 | 0 |
| `docs/HEST_replication_review.md` | 112 | 58 | 54 | 0 |
| `docs/HEST_replication_handoff.md` | 56 | 25 | 31 | 0 |
| `docs/round2_R5_stage_report.md` | 162 | 72 | 90 | 0 |
| `docs/round2_R3_stage_report.md` | 257 | 158 | 99 | 0 |
| `docs/round2_R0_R1_stage_report.md` | — | — | — | **not assessed** |

The uncited column is **zero for every document**, which is the one property the sweep
was built to enforce: there is no claim anywhere whose enclosing subsection cites no file
at all.

`docs/round2_R0_R1_stage_report.md` was **not assessed**. Its run was killed for memory
at 64 GB. That is a gap in this gate, not a pass, and it is the one document whose claim
counts are unknown.

## 2. What the unresolved entries are, and what I did not do

I have triaged the two documents that are at zero and **not** the other twelve. What
follows is the shape of the unresolved entries from reading a sample of each, not a
per-claim classification, and it should not be read as one.

- **Closed historical records** — `round1_final_stage_report.md`,
  `HEST_replication_review.md`, `HEST_replication_handoff.md`,
  `round2_execution_plan.md`. These quote numbers round 2 superseded, and the plan quotes
  the withdrawn 0.0419 scalar because it was written before the withdrawal. Forcing them
  to zero would mean editing records. They are correctly non-clean.
- **External-source documents** — `r5_idc_provenance.md` is a reading task whose figures
  are DOIs, GEO accessions and vendor-page counts. Adding DOI, accession and arXiv-id
  patterns to the parser cut its unresolved count but did not eliminate it, and no
  repository file can support a vendor page's donor count.
- **Delivered stage reports** — `round2_R3_stage_report.md` (99) and
  `round2_R5_stage_report.md` (90) are the largest counts in the table and are **not**
  explained by either category above. These are round-2 reports citing round-2 files.
  They deserve investigation and have not had it. Two candidate causes, neither
  confirmed: the reports quote many per-fold and per-encoder figures that exist only
  inside tables too large for the sweep's 200 MB read cap, and they quote derived
  quantities (differences, shares, dispersions) that are in no file as a cell.
- **Maintained documents with small counts** — `round2_closeout_report.md` (2) and
  `round2_R8_stage_report.md` (11) are small enough to triage and have not been.
  `WAYS_OF_WORKING.md` (20) is prose about process; most of its numbers are costs and
  durations with no result file behind them, and it arguably needs its own exceptions
  file rather than a citation for each.

**So the instruction's "zero unresolved" is met for the README and the deck outline, and
is not met for the repository as a whole.** I am reporting that rather than closing the
gap, because closing it honestly means triaging roughly 350 unresolved entries across
twelve documents, and guessing at them would put wrong reasons into a durable record.

## 3. The three-paragraph report section 2.6 asks for

**What was regenerated.** `results/summary/` regenerates byte-identical from
`build_summary_tables.py`, so nothing there had drifted. `MANIFEST.md` was regenerated
after extending `make_manifest.py`, which as written did not satisfy the instruction: it
summarised each tree as one line and hashed only under `results/`, so the round-2
instrumentation subtrees appeared nowhere by name. It now emits a per-subtree table and
hashes the 390 `instrumentation/` parquets — 1,444 files hashed against 1,054 before, and
a grand total unchanged at 3,195 files and 64.4 GB, which is correct because the widened
walk no longer double-counts what the tree summaries had counted. All twelve
`results/round2/` stages gained a directory-level `PROVENANCE.txt`. All 57 scripts under
`code/scripts/` and `code/figures/` gained a `Stage:` line and all compile.
`env/requirements.lock` was refreshed for ten transitive packages that had drifted in
since 13 September, none scientific. The seven deck figures and
`results/summary/deck_numbers.csv` were regenerated inside the repository from the
committed scripts rather than uploaded.

**What was removed or renamed, and why.** Nothing was deleted. Three duplicate pairs were
retired to a `superseded/` subdirectory inside their own stage, each decided by reading
the files: `replicate_leak__*.csv` covers IDC only against `replicate_leak_v2__*.csv`
covering IDC and READ, so the narrower file is superseded and the citation that pointed at
it understated the evidence; `donor_variance_components.csv` and the unprefixed
`pergene_*.csv` pair carry the same numbers with one fewer written digit than their
`r6_`/`r7_`-prefixed siblings. Four citations across two documents were repointed. One
stray archive left in the tree by a failed bundling job was moved rather than deleted. The
`R5b_audit` provenance entry was corrected twice: it first named a script that does not
exist, because that stage was a source-reading task with no script to rerun.

**What could not be brought up to date.** The gate above: one document not assessed, and
roughly 350 unresolved claims across twelve documents untriaged. Beyond the gate: the four
round-2 decision memos, the results synthesis and the literature landscape are Nicolas's
to supply and are listed as pending in `docs/README.md` rather than reconstructed;
`code/scripts/round2_r5b_audit.py` does not exist and the R5b audit is therefore not
rerunnable from a script, which the README records as a reproducibility gap;
`raw_xgb` for H-Optimus-1 was never run, at about 70 minutes per split;
`results/summary/results_encoder.csv` still lacks H-Optimus-1's raw-head cells even
though R8 produced them; the IDC same-donor attribution rests on a vendor page associated
with one of the two samples and is recorded as probable rather than settled; nine of the
72 donor labels are unverifiable; and there are no bootstrap intervals on the variance
components and no nested-ANOVA diagnostics.
