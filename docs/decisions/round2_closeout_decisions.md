# Round 2 closeout: decisions on the R8 report

19 September 2026. Response from the oversight chat to the R5b–R8 stage report. Round 2 is accepted as complete. This memo closes three loose ends, confirms two numbers the report asked for a ruling on, and freezes the repository for Monday's presentation. Nothing new is started.

---

## 0. Scope

This is a closeout interval, not a stage. Only the items in § 2 are run. No new analysis, no new stage, nothing from the "what was not checked" list beyond what is listed below. Round 3 opens after Monday, once the advisors have weighed in.

**One report when § 2 is done, or by Sunday evening, whichever is first.** Short, three paragraphs at most. If an item is not finished by then, say so and stop rather than continuing into Monday.

---

## 1. Decisions

**1.1 `raw_xgb` for H-Optimus-1 is closed, not finished.** `raw_ridge` settles D2 on its own, with Spearman $-0.95$ between width and score and H-Optimus-1 landing 7th of 12 exactly where its 1536 dimensions place it. Thirty-four CPU-hours to confirm the same conclusion on a second head is not a good use of the allocation. Record it in the README's known-gaps list as deliberately not run, with the measured 70 minutes per split so a future session knows the cost.

**1.2 The pooled between-donor estimate is 0.376**, the CCRCC and LYMPH_IDC pairing, which is the one with enough degrees of freedom and verified labels. The directive's CCRCC-and-PRAD pairing giving 0.122 is reported beside it as an artefact of averaging one well-determined value with a truncated zero, since PRAD has two donors and its raw moment estimate is negative for 68% of genes. The report was right to substitute and right to flag the substitution; both belong in the file, with 0.376 as the estimate.

**1.3 The $\theta_1$ acceptance value is restated against `morphology_v2`.** The threshold was defined against a superseded build, the computation reproduces the v1 build exactly to six decimals, and the substantive finding is unchanged (rank order identical across the four IDC slides, between-slide spread 0.486 against 0.506). Restate, record the v1 value as historical with one line saying why it differs, and do not record a failure.

**1.4 The authors' draft stays unsent**, with the IDC blocking note in place. Whether it goes anywhere is decided after Monday.

---

## 2. What to run

**2.1 One attempt at the IDC attribution.** Fetch the "FFPE Human Breast with Pre-designed Panel" page that HEST's `download_page_link1` associates with TENX95, and read its donor statement. Rate limiting is expected, so: at most three attempts spaced by an hour, then stop. If it resolves, update `donor_audit.csv`, the R5c summary and the authors' draft, and lift the blocking note if the page confirms one donor. If it does not resolve, write one paragraph in the README stating the attribution as unresolved, the evidence on both sides, and the fact that the $+0.065$ measurement does not depend on it. Either outcome is fine. Do not look for the information through other routes.

**2.2 The $\theta_1$ restatement** per § 1.3, and the pooled estimate per § 1.2.

**2.3 A verification sweep, and then make it standing procedure.** The report names its most recurrent defect: a number typed from memory into a sentence whose citation was accurate, caught twice by review. Write a small script that extracts every numeric claim from a markdown document along with the file path cited nearby, re-reads that file, and flags any value it cannot find. Run it over the synthesis document, the authors' draft and the README, and fix what it flags. Add it to `docs/WAYS_OF_WORKING.md` as a required step before any document is handed over.

**2.4 Freeze the repository.** Once § 2.1 to § 2.3 are done, tag the commit `round2-final` and push. The Monday deck will quote numbers from that state, so it needs to be identifiable later.

---

## 3. Explicitly not run

The nine unverifiable donor samples stay unverifiable with their status recorded. No bootstrap intervals on the variance components, since with two donors no resampling makes the donor term informative. No assumption diagnostics for the nested ANOVA. No extension of the between-session result, since PRAD patient 2 is the only place in the benchmark where session varies with donor held fixed. All four are already in the report's "what was not checked" section, which is where they belong.

---

## 4. Note

The round is in good shape. The two things worth carrying into round 3 are the procedural rules that produced most of its findings: write out everything that differs between two arms before naming the term, and do not use a grouping variable for inference until its meaning has been checked against a source outside the file that carries it. Both caught errors this round that would otherwise have propagated into Topic A.
