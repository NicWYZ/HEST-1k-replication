# Round 2 methods note: the numeric-claim checker's exception classes

This note keeps one passage from a document of round 2 that is not kept, `docs_clean_report.md` (at tag `record-full-2026-11`; summarised in `docs/round02/README.md`) (tag `round2-docs-clean`), section 4, moved here word for word with its link targets adjusted to this folder. It describes the classes used in the root `.verify-exceptions` file and the per-track `.verify-exceptions-*` files read by `code/scripts/verify_numeric_claims.py`, and checked by `code/scripts/audit_exceptions.py` and `code/scripts/check_derived.py`. The entry counts are those of 21 September 2026, and "the instruction" in the passage is `docs/round02/i02/deck/post_deck_repo_instructions.md`, section 1. The rule for when an exception may be used is in `docs/WAYS_OF_WORKING.md`, "Required before any document is handed over" and "When the checker is wrong".

## Exception classes, including one that was added

| class | entries | what it covers |
|---|---|---|
| `historical` | 121 | a value measured in a superseded run, quoted in a closed record |
| `cost` | 25 | a count of files, commits, exit codes or source lines — nothing a result file holds |
| `derived` | 15 | computable in principle but not expressible in the formula language: a rank correlation, a two-level groupby, a percentile of a percentile |
| `diagnostic` | 11 | measured inside a debugging experiment and deliberately not checkpointed |
| `external` | 4 | a value whose source is outside this repository |

Plus **118 derived formulas**, which are evaluated rather than declared — checked by
[`code/scripts/check_derived.py`](../../code/scripts/check_derived.py), all 118 agreeing with
the claims they stand for.

`historical`, `cost`, `derived` and `external` are the four the instruction names.
**`diagnostic` is a fifth, added during this work and disclosed here rather than used
quietly.** It covers values measured inside a controlled debugging experiment and
deliberately not checkpointed — the float64-identity investigation, whose buggy state was
fixed rather than saved. None of the four fits: they are not costs, not superseded
results, not external, and not derivable from anything committed. Filing them as `cost`
would have been false.

Every entry in every file carries a class and a reason that stands on its own, checked by
[`code/scripts/audit_exceptions.py`](../../code/scripts/audit_exceptions.py) rather than
asserted. That check found 43 entries carrying a substantive reason but no class — written
before the scheme existed — and five of them turned out to be computable from committed
files, so they moved out of the exceptions file into checked formulas. A declared exception
asserts "this cannot be checked"; a formula gets checked.
