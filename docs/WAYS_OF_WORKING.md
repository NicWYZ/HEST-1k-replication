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
