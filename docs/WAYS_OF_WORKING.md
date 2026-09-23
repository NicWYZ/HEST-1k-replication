# Ways of working

Procedures that earned their place by catching something. Each entry names the failure it
prevents. Added to when a round finds a new one; nothing here is aspirational.

---

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

---

## Acceptance checks

**State a threshold in the units the arithmetic supports.** Round 2's R1 gate set absolute
tolerances of 1e-6 and 1e-4 on a float32 pipeline whose measured accumulation floor is ~1e-5
relative. Three of four checks failed on arithmetic that was in fact correct. Before fixing an
identity threshold, work out what the dtype and the summation length permit: at n training rows,
random-walk accumulation predicts about sqrt(n)*eps relative error, and the observed median was
0.87x that prediction.

**When a check fails, decide whether the threshold was wrong or the claim was wrong — before
proposing a restatement.** These need different evidence. A wrong threshold is established by
showing the quantity does not move when the mechanism it blames is removed (here: the failing
figure was identical to four significant figures under an exact solver, and the worst cell was the
same fold and gene for every encoder). A wrong claim is established by the quantity changing. Do
not weaken a threshold until the first case is demonstrated.

**A check that compares two new arms to each other cannot certify agreement with the old result.**
Round 2's R1 gate compared two round-2 heads and would have passed had both been wrong together.
The check that mattered was added: the control arm must reproduce round 1's stored per-task values
(110 of 110 cells within 3.7e-4). Every refit needs at least one arm anchored to the prior result.

---

## Scheduler (UNC Longleaf, account `rc_htzhu_pi`)

**A small CPU job's priority here is effectively fixed. There is no lever; plan around the wait.**
`sprio` decomposes it: for a 4-core CPU job, 182 = age 0 + fairshare 4 + partition 177. The cluster
config explains why none of that moves:

```
PriorityWeightAge = 1000    PriorityMaxAge = 60-00:00:00
PriorityWeightFairShare = 2000    PriorityWeightPartition = 10000
```

Age is normalised by `PriorityMaxAge`, so **one hour of queue age is worth about 0.7 points and a
full day about 17**, against a baseline of 182 that the partition factor dominates. Fairshare
contributes 4 of 182 at this account's usage (0.0022 against RawUsage 4.8M), and it drifts *down*
as the account runs jobs.

Two consequences, the second of which corrects an earlier note in this file:

- Shortening a wall to chase backfill does not work. Measured in round 2: identical jobs went from
  starting within a minute to pending for over 90 minutes with no wall change, and a 2 h → 50 min
  reduction did not help but did kill an encoder at the limit (`exit_code 143`). Ask for the wall
  the work needs. Both `general` and `spill` allow `MaxTime=11-00:00:00`, so a generous wall costs
  nothing.
- Cancelling and resubmitting does **not** meaningfully reset priority, because there was almost no
  age to lose. An earlier version of this note claimed it did, inferred from a single
  resubmit-then-long-wait sequence; the config shows that inference was wrong, and the long wait was
  cluster load rather than anything the resubmission caused. Resubmit freely when the code needs
  fixing — just do not expect resubmitting to *help*, and do not resubmit a job that is merely slow.

What still holds: if a stage is too long for one job, split it by unit and submit the pieces
together, because that is about wall-clock and failure isolation rather than priority.

**The submission harness has its own clock, and it counts queue time.** `run_timeout_s` is
measured from submission, not from the job starting, and when it expires the harness cancels the
Slurm job. In round 2 a two-minute D3/D4 check was submitted with a 2 h ceiling, waited longer than
that in `PENDING`, and was killed before it ever ran (`error_kind: timeout_ceiling`, no outputs)
while its siblings with 10 h and 25 h ceilings survived the same wait. Set the ceiling from
**expected queue time plus runtime**, not from runtime; on this cluster that means hours even for
a job that computes for seconds. The Slurm `--time` wall is a separate limit and should still be
sized to the work.

**Record the partition the job actually ran on.** Jobs requesting `general` routinely land on
`spill`. `$SLURM_JOB_PARTITION`, not the request, belongs in provenance.

**`-p` is a request, not a destination, and the rerouting is driven by the memory ask.** Measured
in round 2: nine jobs submitted with `#SBATCH -p general_big` landed as five on `spill`, three on
`general` and only one on `general_big` — the one asking for 96 GB. The 48 GB and 64 GB jobs were
rerouted. So `general_big` is reachable only by asking for memory in the hundreds of GB.

**Do not inflate a memory request to reach an emptier partition.** It is available capacity on
1.5 TB nodes where memory, not cores, is the scarce resource, so an inflated ask displaces jobs that
genuinely need those nodes. When `general` is saturated (round 2 saw 18,294 pending against 4,569
running, with 5,320 cores idle but no schedulable memory), the honest options are to wait, to ask
the PI about an account with better fairshare, or to cut the work — not to misreport what the job
needs.

**Size memory from `sacct`, not from a guess.** `sacct -o MaxRSS --units=G` on the completed R1
encoder jobs gives a peak of **16.7 GB**, most between 11 and 13 GB, for the head-fitting stages
over this benchmark (largest task 74k spots x 1536-dim embeddings). Round 2's R1b and R3 were
requested at 48-64 GB, which is a 3-4x over-ask; 32 GB with the float64 arms would be honest. An
over-ask does not slow scheduling much here — priority dominates — but it does make the job fit
fewer backfill gaps, so right-size at submission rather than after.

**Do not compute on the login node.** Its system python has no pandas or pyarrow, and a monitoring
daemon kills work there. Send inspection through the scheduler like everything else.

---

## Provenance

Every new output directory gets `PROVENANCE.txt` with job ID, partition, node, date, commit,
command line **and a config hash** with the config it hashes. The hash is the element most easily
forgotten — round 2 shipped two stages without it and had to backfill — and it is the one that
answers "were these two runs the same experiment?".

---

## Naming a term

**Before a term in a decomposition or a probe is given a name, list every variable that differs
between its arms, in writing.** Round 1 named a contrast "institution shift" when its arms shared
a generating laboratory and differed in scan resolution; it named a slide-identity probe's content
"stain, scanner, section" when resolution varied four-fold in the same task. Both survived to a
conclusion because the label was chosen at design time and never re-checked against metadata
sitting in the same directory. The list is cheap and it is the only thing that catches this.

**Do not pool a term across strata where it means different things.** Round 1's single
slide-signature number averaged over tasks where the contrast was slide identity and tasks where it
also carried same-patient information; per task, the term ranges from 0.026 to 0.294. A term is
poolable only if its arm-difference list is the same in every stratum.

## Auditing a grouping variable

**Audit a grouping variable against something outside the dataset before grouping by it.** Every
term in this project that separates "same X" from "different X" is only as good as the column that
says which X a sample belongs to, and HEST's `patient` field is wrong in both directions. In COAD
it collapses three distinct patients into one label and leaves a fourth sample unlabelled, so the
shipped patient split does not separate patients at all and the per-task term computed on it cannot
be read as a patient effect -- it was round 2's largest such term and was reported as a striking
same-patient result before the labels were checked. In IDC it does the mirror image: two samples
carry different patient labels and are sections of one specimen from one donor, which the
originating vendor's own page states. In READ the labels are right but understate themselves, since
each pair is a replicate of one specimen rather than merely one patient. Nothing in the files
reveals any of this; it took reading the upstream issue tracker, the GEO subseries strings and the
vendor dataset pages. The audit is now a stage of its own (`R5b_audit`), its verdicts carry a
`donor_label_status` column rather than being assumed, and nine of the 72 samples are recorded as
unverifiable rather than inferred. Budget for it: the audit found something in three of the ten
tasks, and two of the three findings invalidated a number already written down.

## Writing outputs, and watching a job run

**Name the schema for anything written after expensive compute.** All three R3 runs completed
every design and fold — about 35 CPU-hours across three jobs — and then died on the final
`pq.write_table`, because the per-gene `fold` column holds an integer for the shipped-split designs
and a slide id for `slide_out`, and pandas-to-arrow type inference read `int64` from the leading
rows and failed on the first `slide_out` row. Pass an explicit `pa.schema` and cast the columns to
match. This is not belt-and-braces: the failure is **pyarrow version-dependent** — on a newer
pyarrow the same frame infers `string` and writes fine, so a local smoke test passes while the
cluster run dies. Naming the types removes the version dependence rather than making the failure
less likely.

**Write the cheapest outputs first.** R3's summary CSVs survived that crash only because they
happen to be written before the parquet, so the stage's reported results were intact and only the
per-gene table needed regenerating. That was luck. Order the writes deliberately: summaries and
acceptance tables before bulk per-row tables.

**Never pipe a long job's output through `tail`.** `python script.py | tail -40` buffers everything
until the process exits, so there is no progress visibility for the whole run — for a five-hour job
that means five hours blind. Let stdout go to the log in full and `tail` the *file* when inspecting.
(A traceback does survive in the last 40 lines, so failure diagnosis is preserved; it is progress
monitoring that is lost.)

**`sacct` `TotalCPU` reads `00:00:00` for running jobs on this cluster**, so it cannot be used to
tell a working job from a hung one. Use `srun --jobid=<id> --overlap -n1 ps -eo pid,etime,time,pcpu,rss,args`
and read the process's own `TIME` and `%CPU`. A job at ~99% CPU with process CPU time tracking
elapsed time is working.

**The submission harness's run clock counts queue time.** A 10-second harvest job given
`run_timeout_s=3600` was killed before it ran, because it sat in the queue longer than that. Set
generous ceilings on every job regardless of how long it runs.

**Commit messages go through a file, not `-m`.** A message containing embedded double quotes broke
the shell quoting and staged the files without committing — silently, since the failure surfaced
only as a non-zero exit with empty output. Write the message to a file and use `git commit -F`.

**A commit message that summarises a gate states the full table, or points to the file that does.
Never a subset.** Commit `a220974`'s message named four documents as failing the numeric-claim
sweep and presented that as the complete accounting. Eleven documents had unresolved claims that
day. The two largest counts — `round2_R3_stage_report` and `round2_R5_stage_report` — went
unmentioned, and one document, `round2_R0_R1_stage_report`, had never been assessed at all and was
not disclosed as such. The per-document data was available when that message was written, so this
was an omission, not something the sweep failed to surface. Corrected in `2f20dc4` and
`docs/closeout_gate_report.md`.

There is a second, sharper lesson from the same episode. The correcting file itself then said
"roughly `350` unresolved entries across twelve documents" where summing its own table
(`results/summary/closeout_gate_sweep.tsv`) gives 437 across eleven — an estimate where a sum was
available, understating by about 20%, in the file written to fix an inaccurate accounting. So the
rule has two halves: state the full table, **and sum it rather than estimating it.** Fixed in
`6acbef2`.

## Quoting a number

**Read it back from the artifact, every time.** Two corrections in this round were the same
failure: a number typed from memory into prose that the saved table did not contain. The second was
in a message *correcting the first*. A number in a report, a message or a commit is quoted from the
file it came from, in the same cell that reads the file — never from recollection of what the
computation printed, and never carried across a table rebuild. When a table is recomputed on more
data, every number already written from it is stale until re-read: R3's total sd stayed at the
two-encoder value after the third encoder landed.

## Seeding

**Never seed an RNG from `hash()` on a string.** Python randomises `str` hashing per process unless
`PYTHONHASHSEED` is set, so `default_rng(SEED + hash(slide_id) % 1000)` draws a different sample on
every run. The same slide id gives `213`, `700`, `780` on three successive interpreters. In R3 this
made the `slide_out` arm the only non-reproducible design in the script — 450 of 6138 rows moved
between two runs, up to 0.046 — while every integer-seeded design reproduced bit-exactly. Use
`zlib.crc32(s.encode())`, which is stable across processes and versions.

The same applies to any **identifier** derived by hashing, not just seeds: a `config_hash` computed
over a tuple containing strings is randomised per run and identifies nothing, which is the opposite
of what a provenance record is for.

**Compare a rerun against the previous run whenever a rerun happens anyway.** R3's per-gene
regeneration reran the whole computation, so diffing its summary CSVs against the reported ones cost
nothing and caught this. A rerun for any reason is a free determinism check; take it.

**Do not quote a ratio whose denominator is within noise of zero.** COAD's
patient-to-novel-slide ratio read 199x, then ~115x on a rerun, then 117x recomputed from the
4-decimal saved table rather than the full-precision column (`results/round2/R3_splits/r3_per_task_terms.csv`)
— because its denominator is 0.11 of its own standard deviation. A quantity that moves with
rounding alone is not a result. Report the numerator and denominator with their dispersion, and say
which one is resolved from zero.

## Sweeping for a defect, and the guard that makes it safe

**Sweep with an AST, not a regex.** Checking whether any script still depended on Python's
randomised string hashing, a regex for `hash(` returned four hits in four scripts — and all four
were the *comments and docstrings of the fixes themselves*, explaining why `crc32` replaced
`hash()`. A regex cannot tell code from prose about code. `ast.walk` looking for a `Call` whose
`func` is `Name(id="hash")` returned **none**, which is the answer: the codebase is seed-independent
by construction. Prefer that to setting `PYTHONHASHSEED=0` at submission, which only holds for as
long as whoever submits remembers.

**Every automated multi-file edit gets a compile-and-revert guard.** Adding one provenance line to
seven scripts, the first attempt sliced the payload string twice and wrote a broken fragment into a
multi-line implicit concatenation, breaking five files. Nothing was lost, because the patch copied
each file, applied the edit, compiled it, and moved the backup back on failure. The run reported
five reversions and every script still compiled. Write the guard before the edit, not after the
first breakage: `shutil.copy` → edit → `py_compile.compile(doraise=True)` → `os.remove` the backup
or `shutil.move` it back, then re-verify the whole directory compiles at the end.

**Record the ambient state a result could depend on, not just the code.** Provenance files now
carry `pythonhashseed` alongside the job id, node, commit and config hash. It should always have
been there — the determinism failure that cost a withdrawn ratio was invisible precisely because
nothing recorded whether the interpreter's seed was fixed.

## When the checker is wrong

A checker that reports a failure which is not one is worse than no checker: it trains
whoever reads it to skim past the output, and the one real failure goes with the rest. So
when a claim fails a check, the first question is which of the two is at fault, and the
answer is not always the document.

The numeric-claim sweep reached **688 unresolved claims across thirteen documents**
(`/tmp/sweep_before.csv`, reproduced by `code/scripts/sweep_table.py before`). Five
defects in the sweep accounted for most of them, and each was found the same way — by a
triage pass refusing to paper a claim over with a declared exception and reporting it as
a tool limitation instead:

1. **Citation scoping was flat, not hierarchical.** A file named once in a `##` section's
   preamble was invisible to every `###` subsection beneath it, so a report that says
   "all numbers in this section come from X" and then discusses X in subsections had every
   one of those numbers flagged. This was the single largest cause. Sibling sections still
   do not share citations — that direction *was* the original bug, where one section's file
   was carried across later unrelated paragraphs and values were checked against the wrong
   source. Both directions have a fixture: hierarchical inheritance verifies, sibling
   inheritance is refused.
2. **Scientific notation was unreadable.** `3.15e-02` parsed as two claims, `3.15` and
   `02`. The fix has to carry the precision as well as the value, because the exponent sets
   how finely the mantissa's digits pin the number down, so the tolerance has to
   follow the exponent. Without that the window would
   have been ±0.005, 150 times the value's own precision and wide enough to match almost
   anything — a check that passes everything, which is the same as no check.
3. **Comma-grouped integers in a cited record split.** a grouped integer became two separate numbers at the comma.
4. **The derived formula language could not express a group-filtered statistic.** "The
   mean over the three encoders for PAAD" was neither a single cell nor a whole column, so
   a computable quantity had no way to be checked.
5. **A digit run inside a UUID was read as a claim** — `4142` out of
   `art_5d580e1c-1647-4142-…` in a figure link. Fixing it exposed a second fault: the
   window the token test searched was ±8 characters, far narrower than a 36-character
   UUID, so that test had silently never fired for any long token.

Three rules come out of this.

**A false failure is a defect in the checker, and it is fixed in the checker.** Not with a
declared exception per claim: an exception says "this number is legitimately unverifiable",
and using it to silence a tool bug makes that statement false 100 times over and leaves
the bug for the next document.

**Report the limitation rather than working around it.** Four of the five above were found
because a triage pass left claims open and said why, against an instruction to reach zero.
Reaching zero by declaration would have looked better and fixed nothing.

**A check that fires on everything identifies nothing — and so does one that fires on
nothing.** Both failure directions need a fixture. Every fix above ships with a test that
the intended case now passes *and* that a planted genuine error is still caught; the UUID
fix in particular had to prove that a wrong value sitting beside a UUID was not swallowed
by the wider window.

## Required before any document is handed over

**Run the numeric-claim sweep and fix what it flags.** This is a required step, not advisory.
The gate is two invocations over one document set, and this is what `code/scripts/sweep_table.py`
actually runs. Run from the repository root:

```
DOCS=$(ls docs/*.md | grep -v deck_master_outline)
python code/scripts/verify_numeric_claims.py README.md $DOCS \
    --search-dir . --exceptions .verify-exceptions --derived .verify-derived \
    --always results/summary/deck_numbers.csv

python code/scripts/verify_numeric_claims.py docs/deck_master_outline.md \
    --search-dir . --exceptions docs/.verify-exceptions-deck --derived .verify-derived \
    --always results/summary/deck_numbers.csv
```

Each invocation exits non-zero if any claim is unresolved, so either can gate a handover.

**Why it is in this shape, since a shorter command does not reproduce the gate.**
`--derived .verify-derived` supplies the formulas for claims that are a computation over cited
files rather than a stored cell, and without it every one of them is read as unresolved.
`--always results/summary/deck_numbers.csv` adds the deck's number table to the cited set of every
scope, which is how the deck documents and the proposal quote it without repeating the citation in
each paragraph. `docs/deck_master_outline.md` goes in its own invocation because it keeps its own
exceptions file, `docs/.verify-exceptions-deck`; measured against the repository-root exceptions
file it reports unresolved claims that it does not have. An earlier revision of this section printed
the command without the last two flags, and run as printed it reported more unresolved claims than
the gate does, on documents that pass it. The escalation that found this is in
`docs/round3_A1_stage_report.md`, under discrepancies, open questions and escalations.

All documents go through one invocation per group rather than one per document: the resolver indexes
each search directory once per process, so per-document runs walk the tree once per document, which
is most of why the closeout's per-document sweep took hours.

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

**Two things it found at the round-2 freeze that were not wrong numbers, and mattered more.**
Fifteen files the documents cite were not in the repository at all — they existed only as session
artifacts — so a reader cloning the repo could not open the evidence for those claims. And the
README and the R8 report quoted *different* values for the same width–score correlation (−0.954
against −0.950) because one used round 1's 11-encoder cohort and the other round 2's 12; both were
right and neither said which. Broken citations and unlabelled cohorts are the failure modes a
numeric sweep surfaces on the way to checking the numbers.
