# Ways of working

Procedures that earned their place by catching something, kept for the oversight chat and for any session that hands over a document. Execution sessions follow `docs/EXECUTION_RULES.md`, which states the evidence rules briefly. On 6 November 2026, when the record moved to the project-record skill, this file was cut to what is still in use. The Longleaf notes and data quirks moved to `docs/environment.md`, the guardrails register and the procedures of the per-gate memo workflow were removed, and the longer lessons stay in the repository's history and in the round documents that recorded them.

## Audits by the oversight chat

Each number has one owner, the session that produced it, which recomputes it once with its own code before handing over. The oversight chat audits a sample of each final report's numbers against the files at a round's close, reads the grid behind any headline it repeats, and has a fresh agent at its own tier, which did not see the drafting, check each brief before handover and the record at each close. In rounds 7 and 8 fresh-agent checks of gate memos and of round 8's scope caught a wrong conclusion, an unmatched comparison and a paper wrongly presented as new, each before handover (`docs/progress-log.md`, 14 and 19 October).

## Literature and novelty

No result is called new without a documented literature check, which covers the survey-sampling and econometric literature as well as machine learning. Run it with independent subagents whose only task is to find the paper that already did it, continually while the work goes on, since the model tends to rediscover results it absorbed in training. Before calling a paper new to the project, search the repository for its arXiv number. Round 9's lesson is to start a search from a problem someone has met in practice and to run the deep search before any derivation, because candidates that a first search found open repeatedly fell to a deeper second search in another field (`docs/round09/README.md`, "Carried forward"). A citation carries an identifier that was opened and its read level (full text, abstract or secondary).

## Documents

**Relabelling a claim means sweeping for it, not editing where you remember it.** When a term is
renamed or a number withdrawn, edit the passages you know about, then sweep every affected file
case-insensitively for the old term and every number being withdrawn, and read each hit. In round 2
stage R0 the targeted edits were correct and still left three stale statements behind — a standing
answer to a research question, a "what was not checked" item, and a figure caption — each of which
asserted the opposite of the same document's new text. The sweep found all three. One-line version:

```bash
grep -rniE 'confound-free|within-patient|0\.0419|institution' README.md docs/
```

**A stage report is written once and then frozen.** Round 1 produced one comprehensive report at
the end because it had no report-and-wait gates; that document is a record of what round 1
concluded and is not edited afterwards, not even to add a pointer, because annotating a record is a
smaller version of rewriting it. Corrections live in the current round's report and in the README.
A consequence to state rather than hide: a frozen report still contains the claims later rounds
withdrew, so the current round's report says which ones and where.

**Numbers in a report are re-derived from files and checked against the text mechanically.** Build
a claim-to-computed-value map and assert every entry, rather than spot-checking. Round 2's R0/R1
report passed 40 of 40 claims this way — and the first pass of that same audit contained an entry
that compared a hard-coded constant against itself, so it could not have failed. Assert that no
comparison value is a literal copied from the text.

**Read the whole grid before writing a headline from one corner of it.** Round 4's PPI Q3 report
led with "the donor-weighted estimator loses to the classical one on every HEST task". The table
behind it was taken at the largest number of labelled donors under one of the two targets, which
was the one corner where the loss was general. Across the rest of the grid the same estimator
gained on two of the three tasks. The numbers in the table were right and the sentence over them was
too wide. Before a summary sentence goes into a report, tabulate the quantity over every axis the
experiment varied and check that the sentence holds in each cell it claims.

## Quoting a number

**Read it back from the artifact, every time.** Two corrections in this round were the same
failure: a number typed from memory into prose that the saved table did not contain. The second was
in a message *correcting the first*. A number in a report, a message or a commit is quoted from the
file it came from, in the same cell that reads the file — never from recollection of what the
computation printed, and never carried across a table rebuild. When a table is recomputed on more
data, every number already written from it is stale until re-read: R3's total sd stayed at the
two-encoder value after the third encoder landed.

## Required before any document is handed over

**Run the numeric-claim sweep and fix what it flags.** This is a required step, not advisory.
The gate is two invocations over one document set. `code/scripts/sweep_table.py` ran the same
two invocations over the flat layout of round 2 and is kept as that round's record, so use the
commands below, which follow the layout by round of 9 October 2026. Run from the repository root:

```
DOCS=$(git ls-files 'docs/*.md' 'docs/**/*.md' | grep -v -e deck_master_outline -e docs/moved.md)
python code/scripts/verify_numeric_claims.py README.md $DOCS \
    --search-dir . --exceptions .verify-exceptions --derived .verify-derived \
    --always results/summary/deck_numbers.csv

python code/scripts/verify_numeric_claims.py docs/round02/tracks/deck/deck_master_outline.md \
    --search-dir . --exceptions docs/round02/tracks/deck/.verify-exceptions-deck --derived .verify-derived \
    --always results/summary/deck_numbers.csv
```

Each invocation exits non-zero if any claim is unresolved, so either can gate a handover.

**Why it is in this shape, since a shorter command does not reproduce the gate.**
`--derived .verify-derived` supplies the formulas for claims that are a computation over cited
files rather than a stored cell, and without it every one of them is read as unresolved.
`--always results/summary/deck_numbers.csv` adds the deck's number table to the cited set of every
scope, which is how the deck documents and the proposal quote it without repeating the citation in
each paragraph. `docs/round02/tracks/deck/deck_master_outline.md` goes in its own invocation because it keeps its own
exceptions file, `docs/round02/tracks/deck/.verify-exceptions-deck`; measured against the repository-root exceptions
file it reports unresolved claims that it does not have. An earlier revision of this section printed
the command without the last two flags, and run as printed it reported more unresolved claims than
the gate does, on documents that pass it. The escalation that found this is in
`docs/round03/i01/exec/round3_A1_stage_report.md`, under discrepancies, open questions and escalations.

**Why.** The most recurrent defect of round 2 was a number typed from memory into a sentence
whose *citation was accurate* — the named file was the right file, the value beside it was not in
it. Review caught it twice: the COAD decomposition terms in the authors' draft (0.2938 and a
0.026–0.163 range, both carried from round 1's superseded v3 decomposition), and two gene-set
predictability values in an escalation message. Both read as checked, because the citation had
been. Nothing else in the process catches this; re-reading your own prose does not, because the
sentence looks right.

**What it does.** For each claim scope — a paragraph, list item or table row — it pools the file
paths cited anywhere in the enclosing subsection, extracts the numeric claims, loads each cited
file, and reports any value it cannot find. A claim is satisfied by a literal value, a whole-column
aggregate (mean, median, min, max, sum, std), or a group-wise aggregate over a low-cardinality key
— because "mean over the three encoders for probe X" is a legitimate quotation that appears nowhere
in the file as a cell. Comparison is at the document's own precision, so 0.376 matches a stored
0.37610.

**What it does NOT do, and this is the more dangerous half.** It cannot tell you the cited file is
the *right* file for the claim. A value can be present in the cited file and still be the wrong
quantity. The second review finding of round 2 turned on exactly that, and no script settles it.
It also cannot verify a ratio of two files' values, a scheduler fact, or a figure from a source
outside the repository.

**`.verify-exceptions`** carries those, one `value<TAB>reason` per line. A value belongs there only
if it is genuinely underivable from a cited file — a ratio, an accounting fact, a withdrawn figure
quoted *as* erroneous, a round-1 result whose source file was not carried forward. It is not a
place to silence a number you have not checked. Every number in a handover document is then either
present in a cited file or has a written reason why not, which is the property worth having.

**Read the `uncited` count, not just the failures.** A claim in a section that cites nothing is not
verified — it is unchecked. At the round-2 freeze the three documents carried 286 verified claims,
0 unresolved, and 102 uncited; the uncited ones are concentrated in summary prose and are the
honest remaining gap, not a clean bill.

## When the checker is wrong

A false failure of the numeric-claim sweep is a defect in the checker, and it is fixed in the checker, never silenced with a declared exception. Report a limitation rather than working around it, and give every fix a test that the intended case now passes and that a planted genuine error is still caught. Five such defects once accounted for most of 688 unresolved claims, and each was found by a triage pass that refused to paper a claim over with an exception.

## Deck conventions

Speaker notes cover only what is on the slide. For advisor decks, no workflow or round language, formulas on the slide when theory is discussed, and every slide says why the step was taken (by 4 October). The speaker notes matter. They address every figure and every bullet point on the slide, read naturally as spoken prose, and on slides with results or heavy method end with an "in short" statement. Every slide is as legible as possible, with big labels, figures, text and formulas and little margin (19 October).
