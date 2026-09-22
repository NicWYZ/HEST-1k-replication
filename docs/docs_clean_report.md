# Closing the numeric-claim gate

Written 21 September 2026 against tag `round2-docs-clean`. Companion to
[`closeout_gate_report.md`](closeout_gate_report.md), which this supersedes on one point of
fact: that report gave the scope as 437 unresolved claims across eleven documents, and the
**pre-triage** figure was **688 across thirteen of sixteen**.

Both numbers are dated snapshots, not current totals. 688 is what the sixteen documents
measured at tag `round2-final-deck`, before any of this work; the current total is **zero**.
Quoting either as "the total" without saying when it was measured is how the 437 came to be
reported as complete in the first place.

---

## 1. The pre-triage scope was larger than reported, and why

`closeout_gate_report.md` was not wrong about the documents it assessed. It was incomplete
about which documents those were. Two were missing from its table:

- **`round2_R0_R1_stage_report.md` had never been assessed at all.** Its sweep run was
  killed for memory during the closeout, so its claims appear in no figure reported
  before now. It contributes **228** — the largest count in the repository.
- **`closeout_gate_report.md` itself** contributes **19**. It did not exist when its own
  table was made.

The rest is re-measurement drift of a few claims per document from the sweep fixes below.
So 437 was the correct sum over the fourteen documents assessed at the time, and 688 is the
sum over all sixteen. Both figures are sums of their own tables rather than estimates, and
`claims − verified = unresolved` holds exactly in each.

The before-table was measured in a detached git worktree at tag `round2-final-deck`, not in
the working tree. By the time it was taken, the triage was already editing documents, and a
working-tree measurement would have been neither before nor after. Git holds the exact
pre-triage state, so this is a before rather than an approximation of one. It is also
about 200 times faster: a worktree checks out only tracked files, about 90 MB, while the
working tree carries 64 GB of untracked artifacts and the resolver walks its search
directories. Running all sixteen documents in **one** invocation rather than one each
matters as much — the resolver indexes once per process, so sixteen invocations walked the
tree sixteen times, which is most of why the closeout's per-document runs took hours.

---

## 2. Before and after, per document

Reproduce with `python code/scripts/sweep_table.py before|after|compare`.

| document | claims before | unresolved before | claims after | unresolved after |
|---|---|---|---|---|
| `docs/round2_R0_R1_stage_report.md` | 275 | **228** | 275 | 0 |
| `docs/round2_R3_stage_report.md` | 257 | **100** | 266 | 0 |
| `docs/round2_R5_stage_report.md` | 162 | **90** | 161 | 0 |
| `docs/r5_idc_provenance.md` | 63 | **56** | 60 | 0 |
| `docs/HEST_replication_review.md` | 112 | **54** | 112 | 0 |
| `docs/round1_final_stage_report.md` | 169 | **50** | 169 | 0 |
| `docs/HEST_replication_handoff.md` | 56 | **31** | 49 | 0 |
| `docs/hest_bench_issue_draft.md` | 56 | **21** | 56 | 0 |
| `docs/WAYS_OF_WORKING.md` | 33 | **20** | 38 | 0 |
| `docs/closeout_gate_report.md` | 27 | **19** | 40 | 0 |
| `docs/round2_R8_stage_report.md` | 144 | **11** | 149 | 0 |
| `docs/round2_execution_plan.md` | 36 | **6** | 36 | 0 |
| `docs/round2_closeout_report.md` | 11 | **2** | 11 | 0 |
| `README.md` | 225 | 0 | 225 | 0 |
| `docs/README.md` | 0 | 0 | 0 | 0 |
| `docs/deck_master_outline.md` | 160 | 0 | 162 | 0 |
| **total, 16 documents** | **1,786** | **688** | **1,809** | **0** |
| `docs/literature_landscape.md` † | — | — | 20 | 0 |
| `docs/round2_results_synthesis.md` † | — | — | 105 | 0 |
| `docs/docs_clean_report.md` † | — | — | 58 | 0 |
| **total, 19 documents** | | | **1,992** | **0** |

**A note on this table's own totals.** The 16-document subtotal was first typed rather than computed, and typed wrong -- 1,806 where the rows give 1,809. That is the exact fault this exercise exists to catch, in the report about the exercise, and it was caught by review rather than by me. Both totals are now derived from the table's own rows by `code/scripts/fix_subtotal.py`, which asserts that the subtotal plus the three late rows equals the total, so they cannot drift apart again.

† Not in the sixteen and so not in the before column. The first two arrived on the remote
while this work was finishing — two of the three documents originally withheld — and were
brought into scope on arrival: 18 and 13 unresolved respectively, now zero. The third is
this report, which is put through the same gate rather than exempted.

Claim counts move between the two columns for three reasons, all of them deliberate:
journal volume-and-page references and identifier digits are no longer parsed as data (the
handoff loses 7, the provenance document 3); several documents gained changelog sections,
which contain numbers of their own (the gate report gains 15, this stage's
`WAYS_OF_WORKING.md` 5); and four genuine document errors were corrected, listed in § 5.

**The two columns are not measured by the same checker, and that matters.** The `before`
column is the pre-fix checker on the pre-triage tree; the `after` column is the post-fix
checker on the triaged tree. Re-measuring the *same fourteen documents* the closeout
assessed gives 1,484 claims and 441 unresolved under the new checker against 1,047 verified
and 437 unresolved under the old — so about 4 of the difference between 437 and 688 is the
checker changing under itself, and the rest is the two documents that were missing. Neither
figure is wrong; they answer slightly different questions, and a clean before/after arrow
between them would have implied a precision this measurement does not have.

---

## 3. What the sweep was getting wrong

Fifteen defects in the checker accounted for most of the 688. Thirteen were found against the original sixteen documents and two more against the two that arrived late. Each was found the same way:
a triage pass declined to silence a claim with a declared exception and reported it as a
tool limitation instead, against an instruction to reach zero. Reaching zero by
declaration would have looked better and fixed nothing.

| # | defect | effect |
|---|---|---|
| 1 | citation scoping was flat, not hierarchical | a file named once in a `##` preamble was invisible to every `###` subsection beneath it, so a report that says "all numbers in this section come from X" had every one of those numbers flagged. The largest single cause. |
| 2 | scientific notation was unreadable | `3.15e-02` parsed as two claims, `3.15` and `02` |
| 3 | comma-grouped integers in a cited record split at the comma | a document could not resolve against a figure another document recorded |
| 4 | the derived language had no group-filtered statistic | "the mean over the three encoders for PAAD" was neither a cell nor a column, so a computable quantity had no way to be checked |
| 5 | a digit run inside a UUID was read as a claim | `4142` out of `art_5d580e1c-1647-4142-…` in a figure link |
| 6 | column names and key values could not contain spaces, hyphens or parentheses | `"TOTAL random - patient"` and `"training-set size"` were unreachable by any formula |
| 7 | a filter was a single key | and the patient label is not unique across tasks, so `@patient="patient 2"` silently selected the wrong rows |
| 8 | glob citations did not resolve | `acceptance__*__f64.csv` matched nothing, so a "worst over twelve encoders" claim read as uncited |
| 9 | no percentile statistic, and a formula over literals alone was refused | a 95th percentile and "106 times float32 epsilon" had no expressible form |
| 10 | a citation written with a literal placeholder did not parse as a path | `acceptance__<encoder>.csv` resolved against nothing, so whole blocks of claims were checked against no file at all. This alone took the largest document from 228 unresolved to 121. |
| 11 | entry keys were document-agnostic | a formula keyed `117` for a COAD ratio would have **verified** the journal volume in "PNAS 117:30266" in a different document — a false pass, which is worse than a false failure because nothing ever reports it. Keys can now be scoped to a document. |
| 12 | bibliographic volume-and-page numbers were parsed as data | 7 references in the handoff alone |
| 13 | numbers inside a URL were read as data | a publisher's article id (`s41592-025-02814-z`) and an arXiv id both parse as numbers. Half of one document's unresolved count. |
| 14 | only the START page of a journal page range was protected | in a citation of the form `Nature Methods 23:1447-1457`, the end page was scanned as its own claim |
| 15 | the formula checker used its own precision rule | it counted an exponent's characters as decimal places, so two formulas the sweep accepts were reported as mismatches. Both callers now share one parser: a checker that disagrees with the checker is worse than no second check. |

Three of these deserve their own note, because fixing them changed a result rather than a
count.

**Defect 2 had to carry precision, not just value.** `3.15e-02` is 0.0315 known to 1e-4, so
the tolerance follows the exponent. Left at the mantissa's two decimals the window would
have been ±0.005 — 150 times the value's own precision, wide enough to match almost
anything. A check that passes everything is the same as no check.

**One correction in this stage had only ever been made in a local working copy.** The
outline's nuclear-area/GATA3 line mixed two morphology builds — its headline value came
from round 1's build while the other three came from the current one. That was found and
fixed earlier in the closeout, but the edit went to a local mirror rather than to the
repository, and it was reported as done. The currency check caught it again here because
it runs against the repository; the line is now corrected in the repository, with round 1's
figure kept as a labelled comparison and a changelog entry. Fixing it then made the check
fire on that changelog entry itself, so check 3 was given the same retraction-awareness
check 1 already had — verified in both directions, since a planted genuinely stale line is
still caught.

**Defects 13 and 14 were found by the last two documents, not by the first sixteen.** A
literature survey cites differently from a results report — URLs, page ranges, other
people's figures — and it exercised parts of the parser nothing else had. That is an
argument for the gate covering every document rather than the ones expected to be
numerically dense.

**Defect 11 is the only one whose absence would have made the sweep report a false
clean.** The other twelve cause false failures, which are noisy but self-announcing. A
false pass is silent, so it gets a fixture that asserts the leak *does not* happen.

**Defect 7 was caught by the derived class doing its job.** Two formulas I wrote myself
disagreed with the documents they stood for: a within-patient fold-ratio came out 2.55
instead of 1.02 because the patient filter spanned three tasks, and an inter-session
pixel-size gap came out 0.0080 instead of 0.0066 because I had written it as the
within-patient range rather than the separation between the two scan clusters. Both had
previously been *declared* exceptions, where they sat unexamined. Evaluating them exposed
both.

Every fix ships with a fixture that the intended case now passes **and** that a planted
genuine error is still caught. Both directions matter: a check that fires on everything
identifies nothing, and so does one that fires on nothing. The UUID fix in particular had
to prove that a wrong value beside a UUID was not swallowed by the wider token window, and
the hierarchical-scoping fix had to prove that sibling sections still do **not** share
citations — that direction was the original bug.

---

## 4. Exception classes, including one that was added

| class | entries | what it covers |
|---|---|---|
| `historical` | 121 | a value measured in a superseded run, quoted in a closed record |
| `cost` | 25 | a count of files, commits, exit codes or source lines — nothing a result file holds |
| `derived` | 15 | computable in principle but not expressible in the formula language: a rank correlation, a two-level groupby, a percentile of a percentile |
| `diagnostic` | 11 | measured inside a debugging experiment and deliberately not checkpointed |
| `external` | 4 | a value whose source is outside this repository |

Plus **117 derived formulas**, which are evaluated rather than declared — checked by
[`code/scripts/check_derived.py`](../code/scripts/check_derived.py), all 117 agreeing with
the claims they stand for.

`historical`, `cost`, `derived` and `external` are the four the instruction names.
**`diagnostic` is a fifth, added during this work and disclosed here rather than used
quietly.** It covers values measured inside a controlled debugging experiment and
deliberately not checkpointed — the float64-identity investigation, whose buggy state was
fixed rather than saved. None of the four fits: they are not costs, not superseded
results, not external, and not derivable from anything committed. Filing them as `cost`
would have been false.

Every entry in every file carries a class and a reason that stands on its own, checked by
[`code/scripts/audit_exceptions.py`](../code/scripts/audit_exceptions.py) rather than
asserted. That check found 43 entries carrying a substantive reason but no class — written
before the scheme existed — and five of them turned out to be computable from committed
files, so they moved out of the exceptions file into checked formulas. A declared exception
asserts "this cannot be checked"; a formula gets checked.

---

## 5. Repository gaps closed

Four gaps the instruction named, and one it did not.

**The donor audit is reproducible.** It was a reading task — vendor pages, subseries
strings, an upstream issue thread — so no script can redo it, and none existed to regenerate
its output either, which left `donor_id`, the grouping variable two stages depend on, with
no regeneration path. It now splits in two:
[`donor_verdicts.csv`](../results/round2/R5b_audit/donor_verdicts.csv) holds the irreducible
human judgements, and
[`code/scripts/round2_r5b_audit.py`](../code/scripts/round2_r5b_audit.py) rebuilds
`donor_audit.csv` from it and the source map, reproducing the committed file byte for byte.
The one derivable field — the COAD donor label from its subseries string — is not merely
applied but *asserted* against the recorded verdict. That assertion was proved live rather
than assumed: perturbing one verdict makes the script refuse, naming the sample and both
values.

**H-Optimus-1's raw-head cells are in the summary table**, and getting there found a
pre-existing fault. The instruction named the wrong script — it reads that table; a
different one writes it, from a normalised results tree — and the run in question was still
in the benchmark's own output naming. Copying it into the expected layout (checksums and
task sets verified, source left in place) and re-running the aggregator produced eleven new
rows where one was expected: the aggregator had been parsing a raw run directory as a
configuration and the task name as the encoder. It went unnoticed because the committed
tables predate that run, so nobody had re-run the aggregator since. Patched to skip the raw
naming — restoring the assumption its own docstring states — the result is exactly one added
row, byte-identical on re-run, and both new values agree with the stage's independent
by-task output to four decimals.

**The IDC attribution stays probable and unresolved.** One fetch attempt was made and
recorded; it was rate-limited, and per the instruction it was not retried. The log now has
four attempts with their targets and outcomes. Reading the audit first made the target
precise: the decisive donor statement sits on the page of only *one* of the two samples.

**The rank convention is stated.** The raw-head leaderboard averages all ten tasks; the
paper and every other project table exclude one. Both conventions were computed: every
substantive claim survives either, and only a single rank integer moves.

**Two documents arrived on the remote mid-commit and were brought into scope.** A push
added `literature_landscape.md` and `round2_results_synthesis.md` — two of the three
documents originally withheld. There was no file overlap with the gate work, so the commit
was rebased onto that push rather than forced over it, and the two were measured, triaged
and taken to zero like the rest. The landscape document's numbers are mostly other
people's published figures, which is what the `external` class is for, and each entry names
the study it came from so a reader can check it at the source.

**And one gap nobody had noticed:** two result files that three documents cite existed
nowhere in the repository. They were project artifacts that had never been committed. Both
were restored and verified against their stored checksums, and the stage provenance was
regenerated to list them.

---

## 6. What was not done

**Six document errors were found and corrected** while triaging, each with a changelog
line in its own document. They are the return on this exercise, and none changes a
conclusion: a digit transposition (0.217627 for 0.217672); a mean reported where a maximum
belonged; a worst-cell attribution naming two encoders where three supply the worst cells;
a mean gene overlap of 27.2 where the table gives 25.2; a rounding error in the fourth
decimal of a decomposition step; and a float32-epsilon multiple stated as 3022× where the
worst cell divided by epsilon is 3095×. A seventh correction softened an arithmetic
identity to the rounded characterisation it actually is: 106 × float32 epsilon is
1.2636e-05, not the 1.265e-05 the document quoted, because the measured multiple is 106.12.

**Not done, and why.**

- **`raw_xgb` for H-Optimus-1 remains unrun.** Its run has no completed folds and it was
  measured at a per-split rate that could not fit any reasonable wall. The instruction
  leaves it closed and it stays closed.
- **The fixture data for the checker's self-tests was recreated mid-session**, not
  restored, after a cache-invalidation test deliberately modified it. The individual
  fixture counts are therefore not comparable across that point. Every property still has
  a fixture that proves both directions — the intended case passes and a planted genuine
  error is still caught — and each was verified at the time of its change; but anyone
  reading the fixture numbers as a regression baseline should know they were re-established
  partway through.
- **The on-disk value cache is an optimisation with a cost.** It stands at about 2.5 GB
  under `.verify-cache` (gitignored). It is what makes the largest document measurable in
  about four seconds rather than not at all, and it invalidates correctly on file size or
  mtime, verified with a fixture. It can be deleted at any time; the next run simply
  re-reads.
- **One citation style in the closed records is broader than it looks.** The handoff cites
  `results.json`, which resolves by basename to 2,150 per-split files. Those are small
  enough to read in full under the byte budget, so its claims verify — but a family
  citation that expanded past the budget would be *disclosed on the row* rather than
  reported as a missing number, and no such row remains.
- **A concurrent-write loss happened and was recovered.** Four tracks and this session were
  all given the same two shared claim files. The exceptions file survived because every
  writer appended; the derived file was rewritten by one track, discarding 15 entries from
  another and the 5 this session had moved in. Recovered in full from a backup and merged
  with collision reporting, and the merged file was then verified to contain every writer's
  entries. The cause was mine: several concurrent writers on one file with no protocol.
  The fix for next time is one writer per file, or a per-track fragment merged at the end.
- **Not assessed:** whether any of the 117 derived formulas is the *most natural* expression
  of its claim, as opposed to a correct one. They are checked, not reviewed for elegance.
