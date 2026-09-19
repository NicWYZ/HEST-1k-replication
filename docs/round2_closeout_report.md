# Round 2 closeout report

19 September 2026. Against the closeout memo of the same date. Repository frozen at `3161a61`,
tagged **`round2-final`** and pushed.

**The two restatements are done and the freeze is in place.** θ₁'s acceptance value is restated
against `morphology_v2` at **0.410577** (log1p) / **0.420947** (raw), tolerance 1e-3, carried in
`round2_r6_theta.py` and `results/round2/R6_theta/r6_theta_acceptance.csv`; round 1's 0.457791 is
kept as a historical value with one line recording that the difference is the morphology build and
not the computation, and no failure is recorded. The pooled between-donor estimate is stated as
**0.376** (CCRCC + LYMPH_IDC) with the directive's CCRCC + PRAD pairing at **0.122** beside it as
an artefact of averaging one well-determined value with a truncated zero, and the flag on that
substitution stays, as the memo asked. `raw_xgb` is in the README's known gaps as deliberately not
run, with its measured 70 minutes per split. The authors' draft is unchanged and unsent.

**The verification sweep is written, run, and now a required step — and what it found first was
not wrong numbers.** `code/scripts/verify_numeric_claims.py` extracts every numeric claim from a
document with the files cited in its subsection, re-reads them, and flags what it cannot find,
accepting literal values, whole-column aggregates and group-wise aggregates; it exits non-zero so
it can gate a handover, and it was self-tested against planted errors before use (that regression
then caught a real bug in it). Two findings outweigh the digits. **Fifteen files the documents
cite were not in the repository at all** — `r3_per_task_terms.csv`, `r4_probes_v2.csv`,
`r5_idc_replicate_leak.csv` and twelve more existed only as session artifacts, so anyone cloning
the repo could not open the evidence; all are now committed. And **the README and the R8 report
quoted different values for the same width–score correlation**, −0.954 against −0.950, because one
used round 1's 11-encoder cohort and the other round 2's twelve; both are right, neither said
which, and both now sit in `r8_width_correlations.csv` with an `n_encoders` column. The gate now
passes at exit 0 over all three documents: **296 claims verified, 0 unresolved, 99 uncited** — the
uncited count is the honest remaining gap, since a claim in a section citing nothing is unchecked
rather than verified.

**The IDC attribution is unresolved, and I spent the third attempt badly.** All three fetches of
the "Pre-designed Panel" page returned HTTP 429, and no other route was tried. README known-gaps
item 10 now states the attribution as unresolved, the evidence on both sides — identical 541-entry
panels and 96.1% of TENX errors landing on the partner, against a 2.1-fold spot-count difference
and Janesick being the source for neither — and the fact that the **+0.0652 measurement does not
depend on the label**. The process error: the memo says three attempts *spaced by an hour*;
attempts 1 and 2 were 175 minutes apart, but attempt 3 went out **12 minutes** after attempt 2,
because a notification returned early and I re-ran the fetch without re-applying the spacing guard.
Having made three I stopped rather than exceed the cap, but attempt 3 was worth less than it should
have been, so this is weaker evidence of a persistent block than three properly spaced failures
would be. If the attribution matters before the deck, one properly spaced attempt would be worth
more than what I have.
