# Round 10, the writing plan for draft v1

*8 November 2026. Written by the oversight chat as track `ledger`'s stage L3 output, for track `paper`, which drafts v1 after F4's pull request is merged (`../../masterplan.md`). It turns the applied outline of `../../00_prep/round10_findings_survey.md`, section 4.2, into a plan section by section. For each section it gives what the section says, the results it quotes and the final-runs stage they come from, the methods and their citations as the ledger records them (`../../i01/ledger/round10_ledger.md`), and what may and may not be claimed. Where Nicolas's L3 answer (`docs/round10/i02/ledger/`) differs, his answer wins.*

## 1. The paper

**What it answers.** The proposal's two questions, on HEST-1k and the federated corpus, with ACS PUMS 2018 as a public second domain:
- calibrated prediction sets for a new donor's histology-predicted expression (topic A);
- valid inference about a population quantity from predicted expression (topic B).

**What it contributes.** The application of methods that exist, cited to their sources, together with:
- the measured answers on real data;
- the design guidance on how many donors to label, and which;
- an account of why the intervals fall short with few donors.

**Working title** `[proposed]`. "Uncertainty for histology-predicted gene expression: calibrated prediction sets and valid inference with few donors". The venue (Q3) is Nicolas's decision after F4. The structure below suits an applied statistics journal and can be cut for a machine-learning venue.

**What it is not.** A methods paper. Round 9's theorems enter only as the explanation of the shortfall, and only those Nicolas keeps (O5).

## 2. Section by section

### 2.1 Introduction and motivation (S1)

- **Says.** Predicted expression is used downstream as if measured, prediction accuracy has a low ceiling, and the donor, not the spot, is the unit of every uncertainty statement.
- **Quotes.** D2 and D3 (replication files, no rerun), D9 and B1 (round 3 files, with the D9 ratio rerun on the corpus tasks at F2), A4 (F3).
- **Cites.**
  - HEST-1k.
  - Kish through Kalton, Brick and Lê for the design effect.
  - Liang and Zeger, Cameron and Miller, and Bester, Conley and Hansen for cluster-robust inference.
  - Lee, Barber and Willett for HCP.
  - The prediction-powered inference papers (Angelopoulos et al.; PPI++) and Wang, McCormick and Leek for inference on predicted outcomes.
  - TISSUE as the nearest spatial-transcriptomics precedent for intervals on predicted expression, whose calibration unit is the one A1 shows fails for a new donor.
- **Claims.** That these facts hold on these data. Nothing about the methods is the paper's.

### 2.2 Data (S2)

- **Says.** The tasks, the donor audit, the corpus tasks and their audit, the predictions (held-out ridge heads on frozen embeddings), the two expression scales, the depth factor, INT5, and the ACS task with its finite population stated as the ACS sample itself.
- **Quotes.** D6, D7 and D10 to D14, with the corpus counts and audit from F1 and the factor shares on both scales from F2.
- **Cites.** HEST-1k and issue #133; the corpus data card; Hicks et al. 2018 (section 3.3), Risso et al. 2014 and Bhuva et al. 2024 for the factor; Ahlmann-Eltze and Huber 2023 and Lun 2018 for the scales; Chambers 1986 if INT5 is called a representative outlier; folktables and the Census PUMS documentation for ACS.
- **Claims.** Data facts only.

### 2.3 Prediction sets for a new donor (S3, if Nicolas keeps P)

- **Says.** Spot-level conformal under-covers for a new donor, and coverage is set by the calibration design, not the encoder. Feature reweighting cannot repair it. HCP is the valid method with no labelled target spots, and the full conformal set inside the target donor takes over once a few of its spots are labelled. GHCP becomes competitive only with more calibration donors. Below $K + 1 < 1/\alpha$ no valid set is finite. INT5 is the case a hierarchical method misses. The institution axis is measured on the corpus.
- **Quotes.** A1 to A3 (round 3 files), and A4, A5, A6, A9, A10 and the institution axis from F3.
- **Cites.**
  - Lei et al. 2018 for split and full conformal and the guarantee behind `within_full`, with Bersson and Hoff's Lemma 3 for the explicit interval.
  - Barber et al. 2023 for coverage under non-exchangeability.
  - Tibshirani et al. 2019 for weighted conformal.
  - Lee, Barber and Willett, Dunn, Wasserman and Ramdas, and GHCP.
  - SymmPI and FAB conformal as methods that also use the target group's labels.
  - Tibshirani, Barber and Ramdas for the impossibility.
  - Duchi et al. for multi-environment coverage and resizing.
- **Claims.** The map over $K$ and $o$ as a measured comparison, own and provisional, not the first use of the target donor's labels (ledger, A6). The coverage floor of A8 as a remark with its proof in an appendix, provisional, after a fresh check of the proof and a survey-side search (hard rule 5).

### 2.4 Valid inference with predicted expression (S4)

- **Says.** PPI with a fixed coefficient is the survey difference estimator, exactly unbiased with an exact variance under simple random sampling of donors. With a fitted coefficient, the two-fold cross-fitted form of Mickey and Williams keeps exact unbiasedness at any sampling fraction. Form C and the constant predictor remove the level term in regime B. What predictions buy on each task, and why it tracks cluster-level accuracy.
- **Quotes.** B2 to B7 and B10 from F2. B9 as a correction to earlier rounds belongs in a supplement, not the main text.
- **Cites.**
  - Breidt and Opsomer 2017 (eq. 4 and 5), Cochran 1977 (Theorem 7.1, eq. 7.8, Theorems 10.1 and 10.2), and Särndal, Swensson and Wretman 1992 (Results 6.3.1, 4.2.1, 4.3.1), with Cassel, Särndal and Wretman 1976 through them.
  - Mickey 1959 (sections 2 and 4) and Williams 1961 for the estimator, and Mickey's (4.4) for the form of the variance estimator, with Zhang, Sanguiao-Sande and Lee 2025 (eq. 9) beside it.
  - Mozer for the PPI and difference-estimator identity.
  - Cochran 7.50 for form C as the combined regression estimator.
  - Raudenbush 1997 and Hagesæther and Zhang 2009 for the $1 - R^2_{\text{cluster}}$ limit.
  - Broska and Howes, and Kluger et al., as the published PPI methods for clustered data.
- **Display.** The difference estimator and its variance on cluster values. The two-fold form with $\hat V_w$, and $\hat V$ in an appendix with the identity behind it, once Nicolas has seen it.
- **Claims.** None of the methods. The measured gains are the paper's.

### 2.5 How many donors, and which (S5)

- **Says.** Coverage falls short at 4 to 12 labelled donors on real tasks because a few donors carry most of the variance, which round 9's frontier makes precise. It sets out how many donors a guarantee needs. It compares regime A with regime B at equal cost, gives the allocation formula, compares balanced selection with simple random selection and shows why weighting and k-center fail, and presents the probe and take-all design for the atypical donor.
- **Quotes.** B8 and B11 from F2, B13 per task from F2, and E1 to E7 from F3. E4 and E6 come from round 7's files.
- **Cites.**
  - Cochran 2.15 and Hájek's condition (via Li and Ding) for the normal approximation, and Bloznelis 1999 for the finite-sample bound without a usable constant.
  - Bahadur and Savage 1956 and Gleser and Hwang 1987 for the impossibility technique.
  - Cochran chapters 9 to 11 and Särndal et al. chapter 4 for regimes A and B.
  - Snijders 2001 and Raudenbush 1997 for the allocation formula.
  - Yang, Qu and Li, Fuller 2009 and Morgan and Rubin for rejective selection.
  - Deville and Tillé and Breidt and Chauvet for the cube design.
  - Fattorini, Legg and Yu, and Aronow and Samii for weighting.
  - Neyman 1934 for purposive selection.
  - Hidiroglou 2001, Hidiroglou and Lavallée 1988 and Rao 1973 for the take-all design.
  - Carter, Schnepel and Steigerwald via Cameron and Miller for $G^\ast$.
- **Claims.** The measured comparisons as the paper's. The frontier theorems that Nicolas keeps as own and provisional, with their antecedents credited. Regime B's few-cluster numbers stated unbounded first (decisions, section 4). No cost claim for spatial platforms (Q1, deferred).

### 2.6 Limits and cautions (S6)

- **Says.** Same-sample tuning under-covers. Percentile and BCa cluster bootstraps are not competitive at few clusters. The finite-population factor is needed for the design target and wrong for the superpopulation one. Spot-weighted estimands let a permuted predictor appear to help. The superpopulation interval has a model term at moderate $G$. Published few-cluster comparators under-cover at four clusters without a small-sample correction.
- **Quotes.** S6-1 to S6-8 from F2.
- **Cites.**
  - Mani et al. 2026 and PPI++ for same-sample tuning.
  - Cameron, Gelbach and Miller 2008, MacKinnon, Nielsen and Webb 2023, Hesterberg 2015 and Mashreghi, Haziza and Léger 2016 for the bootstraps.
  - Abadie et al. for the finite-population factor.
  - Seaman, Pavlou and Copas for estimand choice.
  - Rubin-Bleuer and Schiopu Kratina for the superpopulation variance.
  - Broska and Howes's section 4, Cameron and Miller and Bell and McCaffrey for `bh_t`.
  - Song et al. and Morris, White and Crowther for reporting.
- **Claims.** Negative results on methods in print, as measured here.

### 2.7 Discussion

What a user of histology-predicted expression should do at each number of donors, what remains open (a usable interval below the frontier, B14; the joint design, E8), and the scale question.

## 3. Figures and tables `[proposed]`

1. Coverage by calibration design across encoders (A1).
2. The width map over $K$ and $o$ (A6, F3).
3. Width ratio against cluster-level $R^2$ by gene (B4, F2).
4. Coverage against residual max-share with the frontier marked, per task (B8, B13, F2).
5. Regime A against regime B at equal cost (E1, F3).
6. The design comparison at 8 labelled clusters (E3 to E6, F3).

Table 1 lists the tasks. Table 2 maps each method to its source, from the ledger. Every figure is made from a committed results file by committed code.

## 4. Reads before the paper cites a source

None of these blocks a decision (`results/round10/ledger/round10_ledger_L3_reads.md`, section 4, on branch `round10-ledger`). Each must be read before the sentence that cites it is final. Track `paper` sends them to Nicolas as lists of at most 10 with UNC proxy links.

1. Dip and Zhang 2026 and Akram and Dip 2026, full texts, before D3 is presented.
2. Murphy 1988, for D2's ladder.
3. Johnson 1978, if the modified $t$ is named.
4. Kish 1965, the cluster sampling and design effect chapters, or keep Kalton, Brick and Lê.
5. Moulton 1990.
6. Chambers 1986, if INT5 is called a representative outlier.
7. Moran 1950, or a textbook definition.
8. Breidt and Chauvet 2011 and Deville and Tillé 2004 (E5).
9. Fattorini 2006 (E4).
10. Hidiroglou 1986 and Rao 1973 (E7).
11. Shafer and Vovk 2008, if the computational form of full conformal is credited.
12. Lei et al. 2018, section 5.2 (A5), and CQR in full.
13. The published versions, for equation and page numbers, of:
    - Sanguiao Sande and Zhang (Sankhya A 2021);
    - Yang, Qu and Li (JASA 2023);
    - Bester, Conley and Hansen (2011);
    - Cameron, Gelbach and Miller (2008);
    - Lee, Barber and Willett (ACM JDS);
    - Abadie et al. (QJE).
14. Round 9's NOV12 list of nine sources, if B14 is mentioned beyond a sentence.

## 5. Decisions the text waits on

- Q3, the venue.
- R7-6, which decides the primary estimator of S4.
- V, which decides how regime B is stated in S5.
- Which of round 9's theorems are kept (O5).
- P.
- The primary scale (D5), after F2.
- R7-7 and R7-5.
- Whether the variance identity of the decisions document (section 1.2, item 3) appears.
- Q1, at the next advisor deck.

## 6. How track `paper` works

- **Drafting.** Draft v1 in `docs/round10/tracks/paper/`, in Nicolas's style: plain prose, no em-dashes, no sentence that states something and explains it after a colon, math as rendered LaTeX, and derivations that show every expression and skip only algebra.
- **Numbers.** Every number is quoted from the F4 report's table of quoted numbers, or from the file it names.
- **Checks.** The numeric-claim sweep runs on the draft, and a fresh agent checks it before Nicolas sees it (masterplan).
- **Literature.** A literature check by subagents runs on every sentence that could read as a claim of novelty (hard rule 5).
