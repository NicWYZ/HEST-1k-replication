# Ways of working

Procedures that earned their place by catching something, each with the failure it prevents. They are for the oversight session and for any session that hands over a document. Execution sessions follow `docs/EXECUTION_RULES.md`, which states the evidence rules briefly. The record itself follows the `project-record` skill, round layout.

## Who checks what

Each number has one owner, the session that produced it, which has it recomputed once, independently of the code that produced it, before handing over. The oversight session reads the grid behind any headline it repeats, and settles in the round's summary any two reports that disagree. A fresh agent at the oversight session's own tier, which did not see the drafting, checks each brief before handover and the record at each close. Such checks once caught a wrong conclusion, an unmatched comparison and a paper wrongly presented as new, each before handover.

## Literature and novelty

No result is called new without a documented literature check, which covers the survey-sampling and econometric literature as well as machine learning. Run it with independent subagents whose only task is to find the paper that already did it, continually while the work goes on, since the model tends to rediscover results it absorbed in training. Before calling a paper new to the project, search the repository for its arXiv number. Start a search from a problem met in practice and run the deep search before any derivation, because candidates that a first search found open repeatedly fell to a deeper second search in another field (`docs/round09/README.md`). Extend an earlier logged search from its date rather than repeat it. A citation carries an identifier that was opened and its read level (full text, abstract or secondary).

## Documents

**Briefs and masterplans stay living on `main` while a track runs.** The oversight session revises them in place and pushes, and the session that continues the track is told to check for updates.

**A brief names its track's folder and plan path.** A new round is filed by track, `docs/round<NN>/<track>/`, which holds the track's brief, plan, gate reports and notes, with file names carrying the full prefix. Every brief gives the plan's path there and says that the plan opens with a state block (`docs/EXECUTION_RULES.md`, section 1). Gate replies are written into the plan, not into a separate decision file.

**Relabelling a claim means sweeping for it, not editing where you remember it.** When a term is renamed or a number withdrawn, edit the passages you know about, then sweep every affected file case-insensitively for the old term and every number being withdrawn, and read each hit. In round 2 the targeted edits were correct and still left three stale statements behind, each asserting the opposite of the same document's new text, and the sweep found all three.

```bash
grep -rniE 'confound-free|within-patient|0\.0419|institution' README.md docs/
```

**Numbers in a report are re-derived from files and checked against the text mechanically.** Build a claim-to-computed-value map and assert every entry, rather than spot-checking. Assert that no comparison value is a literal copied from the text, since an audit once compared a hard-coded constant against itself and could not have failed.

**Read the whole grid before writing a headline from one corner of it.** A round 4 report led with "the donor-weighted estimator loses to the classical one on every HEST task", from the one corner of the grid where the loss was general. Across the rest of the grid the same estimator gained on two of the three tasks. Before a summary sentence goes into a report, tabulate the quantity over every axis the experiment varied and check that the sentence holds in each cell it claims.

## Quoting a number

**Read it back from the file, every time.** A number in a report, a message or a commit is quoted from the file it came from, never from recollection of what the computation printed, and never carried across a table rebuild. Twice in round 2 a number typed from memory into prose was not in the saved table, and the second time it was in a message correcting the first. When a table is recomputed on more data, every number already written from it is stale until re-read.

## Required before any document is handed over

**Run the numeric-claim sweep and fix what it flags.** Run from the repository root:

```
DOCS=$(git ls-files 'docs/*.md' 'docs/**/*.md')
python code/scripts/verify_numeric_claims.py README.md $DOCS \
    --search-dir . --exceptions .verify-exceptions --derived .verify-derived \
    --always results/summary/deck_numbers.csv
```

It exits non-zero if any claim is unresolved, so it can gate a handover. `--derived .verify-derived` supplies the formulas for claims that are a computation over cited files rather than a stored cell, and without it every one of them reads as unresolved. `--always results/summary/deck_numbers.csv` adds round 2's number table to the cited set of every scope. A track runs it over its own documents with its own exceptions file.

**Why.** The most recurrent defect of round 2 was a number typed from memory into a sentence whose citation was accurate: the named file was right and the value beside it was not in it. Re-reading your own prose does not catch this, because the sentence looks right.

**What it does.** For each claim scope (a paragraph, list item or table row) it pools the file paths cited anywhere in the enclosing subsection, extracts the numeric claims, loads each cited file, and reports any value it cannot find. A claim is satisfied by a literal value, a whole-column aggregate (mean, median, min, max, sum, std), or a group-wise aggregate over a low-cardinality key. Comparison is at the document's own precision, so 0.376 matches a stored 0.37610.

**What it does not do.** It cannot tell you the cited file is the right file for the claim, and a value can be present in it and still be the wrong quantity. It cannot verify a ratio of two files' values, a scheduler fact, or a figure from a source outside the repository.

**Exceptions files** carry those, one `value<TAB>reason` per line. A value belongs there only if it is genuinely underivable from a cited file (a ratio, an accounting fact, a withdrawn figure quoted as erroneous). It is not a place to silence a number you have not checked. Read the `uncited` count as well as the failures, since a claim in a section that cites nothing is unchecked, not verified.

## When the checker is wrong

A false failure of the numeric-claim sweep is a defect in the checker, and it is fixed in the checker, never silenced with a declared exception. Report a limitation rather than working around it, and give every fix a test that the intended case now passes and that a planted genuine error is still caught. Five such defects once accounted for most of 688 unresolved claims, and each was found by a triage pass that refused to paper a claim over with an exception.

## Decks

The advisors know spatial transcriptomics, conformal prediction and PPI, so a deck has no background slides on them and supplies instead the context and motivation of the project's own steps. An advisor deck is meant to open discussion, so slides and notes stay lean, with the design and the message ahead of numerical results. No workflow or round language, formulas on the slide when theory is discussed, and every slide says why the step was taken. Every slide is as legible as possible, with big labels, figures, text and formulas and little margin. Speaker notes cover every figure and bullet on the slide, read naturally as spoken prose, and end with an "in short" statement on slides with results or heavy method. A figure is drawn from committed results files, and the file it comes from is recorded beside it. A deck is a deliverable, not part of the record, and the round's summary records what was presented and anything in it that later work changed.
