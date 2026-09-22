> **Closed record, dated 19 September 2026.** Round-2 decision memo, supplied by Nicolas and committed in round 3's S0. Not maintained; numbers in it may have been superseded by later execution and results.

# Round 2: decisions on the R5 report and directives to the end of the round

19 September 2026. Response from the oversight chat to the round-2 stage report covering R4 and R5 (`NicWYZ/HEST-1k-replication`). This memo resolves every item the report asked a decision on, adds one pre-R6 stage the report proposed and the oversight chat agrees is necessary, and sets the next report.

---

## 0. The gate rule for this interval

The plan named report-and-wait gates at R1, R3 and R5 and named none after that. The round is therefore finished out in one interval. **The next report is due when R8 is complete, and not before, no matter what happens in between.** The interval contains, in the order given in § 3, the pre-R6 provenance audit (R5b), the replicate-leak extension (R5c), R6, R7, R8, and the idle-capacity items carried over from the last memo. Nothing after R8 is started, set up, staged or piloted; there is nothing after R8 in this round.

There are no interim reports and no interim stop-and-report conditions. Anything that would previously have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the R8 report, and work continues. If a defect invalidates a completed stage's numbers, fix it and rerun inside the interval, and say so in the report. The one action that is never taken inside the interval is contact with anyone outside the project (§ 1.1).

---

## 1. Decisions on the report's open items

### 1.1 Reporting to the HEST authors (report § 10 item 1)

**Not the session's decision, and not the oversight chat's.** Contacting the benchmark's authors is an action taken on behalf of the lab, and it is Nicolas's call with David. What the session does is prepare the material so that the decision can be made on a finished draft rather than a summary.

Write `docs/hest_bench_issue_draft.md` in the form of a GitHub issue, since HEST's README names issues as the preferred channel. It covers, in this order, the IDC same-donor pair with the 10x page's own `donorCount: 1` and replicate language quoted and the measured +0.0651 cost; the COAD patient field; READ's same-specimen pairs; the within-task gene-panel heterogeneity with the R2 and R5 tables; and, as questions rather than claims, the NCBI784 exclusion, the Table A4 count of four versus three, and the absence of any H&E scan provenance. Every number cites the repository file it comes from. The draft is committed and not sent.

### 1.2 The provenance audit before R6 (report § 10 item 2)

**Approved, as stage R5b, and it blocks R6.** The report's argument is correct. Two of the tasks examined so far carry patient labels that do not mean what they say, in opposite directions, and R6's entire design rests on the patient being the unit. A well-estimated decomposition of the wrong quantity is worse than no decomposition. Specification in § 2.1.

### 1.3 The R6 specification change for IDC (report § 10, last paragraph)

**Approved, and generalised.** The unit for R6 is the donor as established by the audit, recorded in a new `donor_id` column, not HEST's `patient` field. IDC has three donors, one of which contributes two sections; its between-donor component is estimated across three, and its within-donor component becomes estimable from the TENX pair. The same rule applies to every task: wherever the audit finds that the `patient` field merges or splits donors, `donor_id` supersedes it. Revised R6 specification in § 2.3.

### 1.4 Probe 1's either/or rule (report § 3.2, § 8 item 5)

**Retired.** The rule in the last memo assumed the two components were alternatives; the data show both, with the session axis the stronger. The report's framing stands: slides are individually identifiable within one patient at one nominal resolution, sessions are almost perfectly separable, and composition explains 1.4% of it. That is the cleanest evidence in the repository that pathology encoders carry a technical signature independent of tissue, and it goes into the Topic A motivation as such.

### 1.5 Probe 2's withdrawal and replacement (report § 3.3)

**Accepted.** The per-fold balanced accuracy under leave-one-slide-out was recall on a single class and sat at the majority-class baseline; the pooled score is the right statistic. The result, resolution class at chance within patient 1 while a 0.0066 µm/px session difference is decodable at 0.98 within patient 2, changes what the round-0 resolution finding means. The alignment of resolution with patient identity in PRAD, SKCM and PAAD stands as a fact about the benchmark's design; the mechanism is that the encoder reads session and slide, and nominal pixel size is a proxy for session, not the thing encoded. The README's scan-resolution subsection is updated to say exactly that (§ 2.6).

### 1.6 The R3 number that changes (report § 7.4)

**Accepted.** The R3 report is frozen; this report supersedes it on IDC's `random − patient` total. The README's key findings and benchmark-properties sections carry the corrected reading, which is the controlled +0.0651 replicate leak and its 54% share of IDC's gap, not the confounded 0.1361. The `donor_out_matched` arm is not reported anywhere; the report's own diagnosis of why it is wrong is correct.

### 1.7 The replicate leak generalises or it does not (report § 9 item 3)

**Extend it, as stage R5c.** One task makes an anecdote; a second makes a benchmark property. READ's two same-specimen pairs are the closest analogue and the design transfers directly. Any further same-donor pairs the audit finds are added. Specification in § 2.2.

### 1.8 The open questions (report § 8 items 1 to 4)

Items 1 to 3 (the 33-versus-41 panel count, which GEO record NCBI785 is, the Table A4 count) go into the author draft as questions and are otherwise closed; none affects a conclusion. Item 4 (NCBI784) is folded into R5b, since HEST-1k's metadata table is already on disk and its `patient` and `subseries` entries for NCBI784 can be read without downloading anything.

---

## 2. Directives

### 2.1 R5b, provenance audit of all 72 benchmark samples

Reading task, no compute. For every sample, from the primary source (10x dataset page, GEO record, or the publication's methods) rather than from HEST's metadata, record the donor-count statement, any replicate, section or block language, the HEST `patient` label, and whether the two agree. Output `results/round2/R5b_audit/donor_audit.csv` with columns `task, sample_id, hest_patient, source_url, donor_statement, donor_id, donor_label_status, notes`, where `donor_label_status` is one of `verified`, `contradicted`, `unverifiable`. `donor_id` is the audited donor; where the source is silent it equals the HEST label and the status is `unverifiable`.

Order of work, by risk. First the TENX-sourced samples in PAAD (TENX116, TENX126, TENX140), SKCM (TENX115, TENX117), LUNG (TENX118, TENX141) and COAD (TENX111, TENX147, TENX148, TENX149), because 10x reuses blocks across demonstrations and this is where the IDC fault came from. Then the NCBI-sourced samples in LYMPH_IDC and HCC. Then CCRCC's 24 INT samples, which come from one study and should be resolvable from that paper's supplement in one pass. PRAD is already verified from its subseries strings and needs only the row filled in. READ is already characterised.

Also record NCBI784's `patient` and `subseries` entries from HEST-1k's metadata and state whether it is the other Sample #1 replicate.

Acceptance is every row filled with a status, and a one-paragraph summary per task of what changed. R6 does not start until this file exists.

### 2.2 R5c, replicate leak on READ and any audit-found pairs

The design of report § 6.1, unchanged. For each slide in a same-donor pair, hold it out; draw two training sets of identical size, one from the pool that includes the partner slide and one from the pool that excludes it; same test spots, same pipeline, same within-slide metric; three encoders. READ has two pairs (ZEN48/ZEN49, ZEN36/ZEN40), so the arms are drawn from the other pair plus or minus the partner. Report per slide and pooled, with the leak as a share of READ's `random − patient` gap from R3.

Save the per-gene within-slide Pearson for both arms, because R7 will read it. The IDC run from § 6.1 should be rerun with per-gene output if it did not save it.

If R5b finds further pairs, add them here before R6 starts on those tasks.

### 2.3 R6, donor-level estimands (revised)

As specified in the previous memo's § 2.3, with these changes.

The grouping variable is `donor_id` from R5b. The three components are within-slide sampling variance (spot bootstrap), between-slide-within-donor, and between-donor. Which tasks contribute to which component is now determined by structure rather than by task list. CCRCC (24 donors, one slide each) and LYMPH_IDC (4, one each) contribute between-donor only, and CCRCC is the best-powered task for that component. PRAD (2 donors, 15 and 8 slides) contributes all three, and its between-slide-within-donor component includes the scan-session effect R4 found, which should be said. IDC (3 donors, one with two sections) and READ (2 donors, each with two sections) contribute a within-donor component from a single pair each and a between-donor component on few degrees of freedom. COAD stays flagged and excluded from between-donor unless R5b resolves it. PAAD, SKCM, LUNG and HCC contribute between-donor on two or three donors, pending R5b.

Report the three components and their ratios per task and gene, and a pooled between-donor estimate that uses CCRCC and PRAD with the rest as a sensitivity check. The nuclear-area-by-resolution table stays, with `resolution_uncertain` as a column, and it now also carries scan session for PRAD patient 2.

### 2.4 R7, per-gene decomposition (revised)

As specified, plus the per-gene replicate leak from R5c on IDC and READ. The join to R6 uses the between-donor variance, not between-patient. On PRAD, the novel-slide and patient-identity terms per gene are reported with the scan-session caveat from R4.

### 2.5 R8

`hoptimus1` on `raw_ridge` and `raw_xgb`. Head fitting on cached embeddings, no GPU. It is the falsification test of D2; it should rank poorly on `raw_ridge` given its 1536-dimensional width. Report where it lands.

**STFlow stays deferred.** It is not part of R8 and is not started.

### 2.6 README and documents

Three edits to the README, all before the R8 report. The scan-resolution subsection says that resolution is aligned with patient identity in PRAD, SKCM and PAAD, that within one patient nominal resolution is not decodable while scan session is, and that the resolution covariate is therefore a proxy for session. The key findings section carries the replicate leak and drops any remaining reference to the withdrawn institution figure. The benchmark-properties section adds the IDC same-donor pair, the IDC panel differences, and the missing scan provenance, each with its file path.

The author-issue draft of § 1.1 goes in `docs/`. The `PYTHONHASHSEED=0` sweep across older scripts, the § 1.3 rank supplement from the last memo, and the solver-sensitivity footnote are completed in this interval as idle-capacity work.

### 2.7 One small addition

From the R4 probe-3 run on IDC, report the slide-identity confusion matrix. If the TENX95 and TENX99 rows confuse with each other more than either does with the NCBI slides, that is the embedding-side corroboration of the same-donor finding, obtained from a run that already exists.

---

## 3. Order of operations

1. **R5b** first. It blocks R6.
2. **R5c** on READ, alongside R5b; extended to any new pairs when R5b finds them.
3. **R6**, once `donor_audit.csv` exists.
4. **R7**, once R6's between-donor variance exists.
5. **R8**, at any point; it depends on nothing.
6. The § 2.6 and § 2.7 items, at any point.

**One report, when R8 is complete, and then stop.** It covers R5b through R8 and the § 2.6 and § 2.7 items. No interim reports; escalations go in the report. Nothing is sent to anyone outside the project.

---

## 4. On the report itself

Two things worth carrying forward. The report withdrew probe 2's first numbers by finding the majority-class baseline sitting exactly where they were, and it found that by writing down the class-size asymmetry in the arm-difference table before naming the term. That is the procedural rule doing what it was adopted for. And the `donor_out_matched` design was rejected by reading per-fold training sizes rather than the mean, which is the same discipline the round-1 review asked for. The audit in § 2.1 is the same idea applied to labels instead of arms, and it should be treated as part of the standing procedure from here on: no grouping variable is used for inference until its meaning has been checked against a source outside the file that carries it.
