# Classical sources, pass 2 theme B (19 October 2026)

Every web search after the fourth was refused because the shared WebSearch budget (200 per turn) was used up. WebFetch only works on URLs that appeared in this conversation or in search results, plus arXiv. Direct downloads (curl) are blocked by the egress policy, and DOI links typed from memory were blocked pending permission. WebFetch extracts through a small model, so quotes are capped near 125 characters and long equations come back garbled. Nothing below is reproduced from memory.

## What could be read, with exact short quotations

### Raudenbush (1997), Psychological Methods 2(2):173-185
Source: https://www.ipr.northwestern.edu/documents/required-reading/2014/Session%208-9%20Raudenbush.pdf (open reading-list copy). Quotes as returned by the extraction, page numbers as reported by it.

- p. 177, no-covariate optimal n, Eq 9: "This result duplicates the familiar result of Cochran" (the paper says its optimal cluster size equals Cochran's 1977 two-stage result).
- p. 177, budget: "In particular, T monetary units are available." The constraint is Eq 6 and J = T/(nC1 + C2) is Eq 7 (C1 cost per person, C2 cost per cluster). The equation bodies were garbled; not read.
- p. 179, covariate case, Eq 23 and 24: "one obtains, to a close approximation (see the Appendix), n(optimal) as the solution to" followed by an equation (24). The formula body was lost. The text states "both the between-cluster variance and the within-cluster variances are now residual variances conditional on the effects of the covariate X." So the covariate result is Cochran's form with residual variances, but it is stated as an approximate solution to an equation, not as an explicit closed form. Whether it reduces to m* times sqrt((1-R2_w)/(1-R2_c)) must be checked in the Appendix [verify].
- p. 179: "so that the adjusted intracluster correlation is smaller than the unadjusted intracluster correlation."
- p. 182 (Final Remarks): "collecting cluster-level covariates would increase C2".
- Numerical example (paraphrase from the extraction): rho = .05, C2/C1 = 10, optimal n rises from 14 without covariate to 19 with it; sampling variance falls from about .0226 to about .0091 (Tables 2 and 3). The covariate used Bloom (1995) values, 73% of between-cluster and 48% of within-cluster variance explained.
- Section headings: Optimal Allocation and Precision With No Covariate (Cost of Data Collection; Optimal Allocation); Optimal Allocation and Precision With a Covariate (Model; Estimation; Optimal Allocation; Relative Efficiency of the Two Designs); Use of an Aggregated or Between-Cluster Covariate; Contextual Effects Models; Final Remarks; Appendix.

### Broska and Howes (2026), arXiv:2610.09601, Appendix C and Section 2.6
Read through WebFetch of https://arxiv.org/pdf/2610.09601. Formulas as returned by the extraction.

- eta_p = Var(p_g) / (mu_p (1 - mu_p)).
- Eq 21: V^PP = (1/(kappa^2 G mu_p)) (V_eps - V_epsZ^2 / V_Z).
- V_eps = V_Ys + (eta_p (1 - mu_p) + mu_p) V_Yd ; V_Z = (V_fs + eta_p V_fd)/(1 - mu_p) ; V_epsZ = V_Yfs + eta_p V_Yfd.
- Eq 22: rho = V_epsZ / sqrt(V_eps V_Z).
- Sec 2.6: "may cost less than obtaining labels from a new cluster" (no figures). Sec 4: "Labeling a whole cluster can be cheaper per unit than obtaining labels from different clusters" and a cost model is left as future work.

### Hedges and Hedberg (FCSM paper), https://apps.bea.gov/icsp/fcsm/assets/docs/J4_Hedberg_2013FCSM.pdf
- R1^2 = 1 - sigma_A1^2 / sigma_1^2 and R2^2 = 1 - sigma_A2^2 / sigma_2^2 (level-specific covariate R-squared); three-level adds R3^2 = 1 - sigma_A3^2 / sigma_3^2.
- Relative costs c3 = 50, c2 = 10, c1 = 1. No closed-form optimal allocation; it uses the CRT-Power optimal design wizard.

### Särndal, Swensson and Wretman, Model Assisted Survey Sampling: table of contents only
Source https://www.lehmanns.ch/media/751449/1 (a publisher or bookseller contents page; edition not stated).
- Chapter 4 "Unbiased Estimation for Cluster Sampling and Sampling in Two or More Stages".
- Chapter 6 "The Regression Estimator"; chapter 7 "Regression Estimators for Element Sampling Designs"; chapter 8 "Regression Estimators for Cluster Sampling and Two-Stage Sampling".
- Chapter 12 "Searching for Optimal Sampling Designs", with "12.8 Allocation Problems in Two-Stage Sampling" at p. 471 as listed.
No formulas were available.

### PracTools documentation, clusOpt2
Source https://search.r-project.org/CRAN/refmans/PracTools/html/clusOpt2.html.
- "Compute the sample sizes that minimize the variance of the pwr-estimator of a total in a two-stage sample."
- Arguments: C1 "unit cost per primary sampling unit (PSU)", C2 "unit cost per element", tot.cost "total budget for variable costs".
- References given: "Sample Survey Methods and Theory" (Hansen, Hurwitz, and Madow, 1953, chap. 6, sect. 16) and Valliant, Dever, Kreuter (2018, sect. 9.3.1). No formulas on the page.

### Maxim and Harrington (1984), PE&RS 50(11):1613-1627 [title garbled in extraction]
Source https://asprs.org/wp-content/uploads/pers/1984journal/nov/1984_nov_1613-1627.pdf.
- Restates Cochran: "Cochran (1977) shows that the optimal number of subcells to sample can be calculated as" (formula illegible in extraction). Budget constraint written C1 n + C2 n m <= B. Appendix B extends Cochran's proof by minimising variance times cost with the Cauchy-Schwarz inequality.

### Others read only at abstract level
Koh (1999) nonlinear cost c1 n^p + c2 n^p m^q two-stage allocation; Murakami (1950) double sampling with C = c1 L + c2 n; Reilly (1996) B = n C1 + n2 C2; Madden (1976) dissertation on auxiliary information in prediction approach to cluster sampling; Nangsue and Berger (2014) regression estimator for stratified two-stage sampling. None gave a usable formula.

## What could not be read (library items)
1. Cochran (1977), Sampling Techniques, 3rd ed.: sec 10.6 optimum m with cost, ch 7 (regression estimator, separate and combined) and any regression-estimator extension under two-stage sampling, ch 5, 9-11 stratified versus cluster sampling with costs. No open copy or excerpt was reachable. The section numbers 7.9-7.10 remain [verify].
2. Särndal, Swensson and Wretman (1992): ch 8 (regression estimators for cluster and two-stage sampling) and ch 12, section 12.8 (p. 471).
3. Kish (1965), Survey Sampling: design effect and optimum cluster size with costs. Not reached.
4. Hansen, Hurwitz and Madow (1953), Vol I ch 6 sec 16 (location given by PracTools), Vol II.
5. Valliant, Dever and Kreuter (2018), sec 9.3.1.
6. Raudenbush (1997) Appendix and equations 9, 23, 24 as typeset (the extraction lost them).
7. Moerbeek (2006), Snijders and Bosker (1993), Bloom, Richburg-Hayes and Black (2007), Hagesaether and Zhang (2009), Kennel and Valliant (2019), Innocenti et al. (2019, 2021), Nedyalkova and Tille (2008), Cohen (1998): not reached.
