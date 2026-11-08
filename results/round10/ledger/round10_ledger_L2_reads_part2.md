# Round 10, track `ledger`, L2 reads, part 2: Williams, Mickey's corrigenda and the open sources

*8 November 2026. Written by the oversight chat under `docs/round10/i01/ledger/round10_ledger_brief.md`, stage L2, continuing `round10_ledger_L2_reads_part1.md`. Section 1 was read by the oversight chat itself from the two files Nicolas supplied on 8 November (`williams.pdf` replaced, `mickey_correction.pdf`). The open sources of part 1's section 4 are read by Opus subagents through the built-in browser on Nicolas's Mac, which reached arXiv and JSTOR on 8 November, and are added in section 2 when they return. Full notes are in the claude.ai project docs (`claude/round10_L2_notes_*.md`).*

## 1. Williams (1961) and Mickey's corrigenda (1960)

**Williams, W. H. (1961).** "Generating unbiased ratio and regression estimators", Biometrics 17(2), 267 to 274, JSTOR stable 2527992, DOI 10.2307/2527992 (from the JSTOR PDF; the stable URL and pages are printed on its cover page). Read level: in full, sections 1 to 7 and references. Equations (1), (2), (12) and (13) and section 3's ratio were checked against the page images of pp. 268, 269 and 273.

1. **The estimator.** Equation (2) is
$$
T_k = \bar y + \bar b(\mu_X - \bar x) + \Big(1 - \frac{n}{N}\Big)\frac{1}{k(k - 1)}\sum_{i=1}^{k}\big(b^i - \bar b\big)\big(\bar x^i - \bar x\big),
$$
where $b^i$ is any function of group $i$ and $\bar b = \sum_i b^i/k$. Its correction term is $(1 - n/N)$ times the unbiased estimator (1) of $\text{Cov}(\bar b, \bar x)$. This matches round 8's transcription (`docs/round08/i01/positioning/round08_positioning_note.md`, section 3.2). It is unbiased for any form of the coefficient (p. 268).
2. **The variance estimator.** Section 6 (p. 273) first assumes "a negligible $n/N$ (or $k/s$) and a fixed set of uncorrelated groups", rewrites $T_k$ as (12), $T_k = \bar y - \frac{1}{k(k-1)}\sum_{i \ne j} b^i(\bar x^j - \mu_X)$, and gives
$$
v(T_k) = T_k^2 - \frac{1}{k(k - 1)}\sum_{i \ne j}\bar y^i\bar y^j \qquad (13),
$$
unbiased under that assumption, with the warning that it can have high sampling error for small $k$. So Williams' own variance estimator needs $n/N$ negligible. The estimator from Mickey's section 4 in part 1 (section 1, item 1) needs no such assumption.
3. **Section 3.** Under a linear model with normal $x$ and the least-squares slope (3), $V(\hat y_b)/V(T_2) = (n - 2)(n - 6)/\{(n - 3)(n - 4)\}$ for $n > 6$, printed as 0.89 and 0.95 at $n$ of 15 and 25 (recomputed: 0.886 and 0.946). As $k$ varies the ratio is largest at $k = \sqrt{n/3}$ (confirmed on the page image, so L1 S4 B9's statement stands).
4. **Other sections.** Section 4 gives a combined stratified form (7) with an overall slope (5). Section 5 gives two-stage sampling of equal-sized primaries (11), conditionally unbiased for the mean of the selected primaries. Section 7's toy population of six pairs gives exact variances 7.914, 2.281 and 1.886 for $\bar y$, $T_2$ and $T_2^\ast$ (p. 274).
5. **Citations.** Williams cites Cochran (1953), Goodman and Hartley (1958), Hartley and Ross (1954), Nieto (1958) and Robson (1957). He does not cite Mickey (1959), whose class contains his $k = 2$ form (part 1, section 1, item 1). The two are independent constructions of the same estimator, and Mickey's is the earlier in print.

**Mickey, M. R. (1960).** "Corrigenda: Some finite population unbiased ratio and regression estimators", JASA 55(292), p. 755, December 1960, JSTOR stable 2281602, DOI 10.2307/2281602. Read in full. Mickey withdraws the claim (p. 595 of the 1959 paper) that the variable-probability part gives new estimators. He credits the results of pp. 604 and 605 to Des Raj (JASA 51, 1956, 269 to 284), and those of p. 606 to Murthy (Sankhya 18, 1957, 379 to 390). Nothing in sections 2 to 5 is corrected, so part 1's reading of sections 2 and 4 for question E stands. If the paper ever cites Mickey's section 6, it cites Des Raj and Murthy for it.

**Effect.** With both read, nothing in the sources blocks the decision on question E at L3. The `[proposed]` variance estimator of part 1 (section 1, item 1) is still waiting for Nicolas's look, a to-do he set aside on 8 November.

## 2. The open sources

Five Opus subagents read the open sources through the built-in browser on 8 November, under the part-1 brief and an addendum for browser use: `conformal_a`, `conformal_b`, `split_estimators`, `cluster_survey` and `evaluation_data`.
- **How they read.** Most read arXiv HTML, checking formulas against the authors' LaTeX behind the HTML math. `cluster_survey` read PDFs with screenshot checks, and `evaluation_data` read publisher and PMC pages. The pane's PDF viewer could not be paged for some readers, so arXiv-only papers are located by section, theorem and equation rather than page.
- **What the oversight chat checked itself.** The two findings that change part 1 or the record: the Sanguiao Sande and Zhang divisor (item 1), against Mickey's identity, and `within_full` (item 6), against the round 5 code. It also recomputed the arithmetic quoted below.
- **The fresh check.** A fresh Opus agent then checked sections 2 to 4 against the five notes. It found 40 statements the notes did not support or that overstated them, and 11 omissions, and all are corrected in this version.
- **Where the notes are.** The full notes are in the claude.ai project docs (`claude/round10_L2_notes_*.md`).
- **Two workshop papers.** Dip and Zhang (2026) and Akram and Dip (2026) are named here because they are accepted NeurIPS 2026 workshop posters, with named authors and abstracts public on neurips.cc. So they are treated as public, not as unpublished manuscripts (hard rule 8). Nothing beyond their abstracts is used.

### 2.1 Question E

1. **Sanguiao Sande and Zhang give exactly unbiased variance estimators under simple random sampling of units, at any sampling fraction, in three cases** (arXiv:2003.11423 v1; published as Sankhya A 83, 714 to 744, 2021, DOI 10.1007/s13171-020-00224-1, paywalled and not opened, so the printed numbering may differ; L0 and the brief cite it as 2020):
   - **the single split**, given $|s_2| \ge 2$. This is Mickey's $t_\alpha$ with the classical variance estimator of part 1's $s^2_A$;
   - **the full Rao-Blackwellisation**, by their section 2.2 proposition, $\hat V(\hat Y_1) - V_q(\hat Y_1 \mid s)$, with $V_q$ computed exactly;
   - **the Monte Carlo average of $K$ independent subsamples**, by the section 2.5 proposition (PDF p. 10, unnumbered) and eq. (13) (section 3.3, p. 13), which the reader checked by screenshot:
$$
\hat V\big(\hat Y^K_{GR}\big) = \frac{1}{K}\sum_{k=1}^{K}\hat V\big(\hat Y_{1k}\big) - \frac{1}{K}\sum_{k=1}^{K}\big(\hat Y_{1k} - \hat Y^K_{GR}\big)^2 .
$$
   - **What the third display targets.** It targets the variance of the Monte Carlo average actually computed, as Mickey's (4.4) does for $T_m$, with the same divisor. The $1/\{K(K - 1)\}$ that L1 transcribed is a separate display on p. 9, which estimates the Monte Carlo error alone. So part 1's correction 7 is withdrawn; L1 misread the display, and the two sources agree.
   - **Two limits.** They treat units, not clusters. Applying them to whole clusters drawn without replacement treats cluster values as units, which the source does not discuss. They do not discuss the sign of the Monte Carlo variance estimator.
2. **What this means for the `[proposed]` estimator for Williams' form.** Its two pieces $s^2_A$ and $s^2_B$ are each the single-split estimator of item 1, which is in print. What no source in this pass states is the combination over the two complementary halves, $\tfrac{1}{2}(s^2_A + s^2_B) - \tfrac{1}{4}(t_A - t_B)^2$. Sanguiao Sande and Zhang's proof of the Monte Carlo case assumes the subsamples are drawn independently given $s$ (their "IID construction"), and two complementary halves are not. That step rests on Mickey's (4.5) and (4.6) and on part 1's enumeration check, so it stays `[proposed]` for Nicolas's look.
3. **The other papers in this group.**
   - **Lu, Shi, Liu and Ding** (arXiv:2508.15664, fold-wise). They prove exact conditional unbiasedness of the point estimator (Theorem 1). Their exact finite-$N$ conservativeness identity holds only for oracle residuals (Appendix B.10, eq. 15), and their variance estimator targets the oracle estimator's variance. With cross-fitted residuals the variance result is asymptotic, and nothing is given at small $N$. Their "Supplementary Material" is Appendices A and B of the arXiv file.
   - **An, Dagdoug, Haziza and Tillé** (arXiv:2609.10904, fold-wise). They prove exact design-unbiasedness for any honest scheme with positive conditional inclusion probabilities (Proposition 2). Under SRSWOR with the uniform scheme those probabilities are $n_j/N_j$ (Remark 1). They say in section 4.2 that their variance estimator is generally not design-unbiased, only consistent (Theorem 5).
   - **Kwon, Yang and Kim** (arXiv:2604.07636). They weight by the unconditional $1/\pi_i$ and prove conditional unbiasedness only under Poisson sampling. Under SRSWOR the estimator is first-order equivalent to the oracle but not shown to be exactly unbiased. The variance estimator is consistent, with the finite-population factor carried by $\Delta_{ij}/\pi_{ij}$ in their (20).
   - **Dharamshi et al.** (arXiv:2502.11032). Their exact variance expression (8) is general. Their estimator is built for Poisson sampling, bias-corrected, with one term approximated and negatives floored at zero. Under SRSWOR the joint-inclusion terms are dropped, so it is not design-unbiased there. They do not split the sample.
   - **Zhang et al.** (arXiv:2606.28795). Following Zhang, Sanguiao-Sande and Lee (2025, JOS 41, 404 to 432, not opened), they give exactly design-unbiased MSE estimators for Rao-Blackwellised prediction estimators. The Monte Carlo average uses the same $1/T$ divisor. These are prediction estimators, not a regression-type difference estimator.
4. **Who cites Mickey and Williams.** Among the sources whose reference lists were checked for them (this group), only Kwon, Yang and Kim (2026, section 1) cite Mickey (1959) and Williams (1961), naming them with Hartley and Ross as the precedent for split-sample unbiased estimation. Sanguiao Sande and Zhang (arXiv and the published reference list), Lu et al., An et al., PPI++, Dharamshi et al. and Zhang et al. cite neither. The part-1 PPI papers were not checked for this. It bears on O5 and on how the paper credits the estimator.
5. **PPI++** (Angelopoulos, Duchi and Zrnic, arXiv:2311.01453). It fits $\hat\lambda$ on the same labelled data (eq. 8, Example 6.1). It does not discuss cross-fitting or the finite-sample bias of $\hat\lambda$, and its justification is asymptotic. This closes S6-1 item (iii) without changing a verdict.

### 2.2 Question P and the prediction-set rows

6. **`within_full` is the classical full conformal interval with the mean as the fitted model.**
   - **The formula.** Setting $1/\tau^2 = 0$ in Bersson and Hoff's Lemma 3 (arXiv:2204.08122 v1, section 2.3) gives the "distance to average" endpoint $g(y_i) = (2S - (n + 1)y_i)/(n - 1)$, with the kept set at $k = \lfloor\alpha(n + 1)\rfloor$ (their Theorem 2 rule). The reader did this substitution, and the checker and the oversight chat recomputed it. Bersson and Hoff state the lemma only for finite $\tau^2$, so the case $1/\tau^2 = 0$ is arithmetic on it, not their statement. The headers of `code/scripts/round5_conf_w1_sim.py` (lines 34 to 46) and `round5_conf_w3.py` have the same endpoint and the same $m$.
   - **The guarantee to cite.** Lei et al. (2018) Theorem 2.1, which was read, states the full conformal guarantee for i.i.d. data with a symmetric fit, and its section 2 says exchangeability suffices (Tibshirani et al. 2019, Theorem 1, states it for exchangeable data). Bersson and Hoff can be cited for the explicit interval once the substitution is checked. They credit the computational form to Shafer and Vovk (2008, JMLR 9, 371 to 421), which was not read.
   - **What the record cites now.** The record cites neither Bersson and Hoff nor Shafer and Vovk. It cites Lei et al. (rows S1.5, A1, A6), but not yet as the source of `within_full`'s guarantee.
   - **Its assumptions.** A citation needs within-donor exchangeability of the labelled spots with the test spot, which a random draw gives, and a score fitted without the target donor's labels. `within_full`'s set is bounded only for $o \ge 9$ at $\alpha = 0.1$.
7. **Three methods already public use the target group's labelled observations.** Two are published (according to GHCP's reference list) and one is an arXiv preprint. Round 8's C10 statement, that no paper compares a full conformal set from the target donor's own labels with HCP or GHCP, still holds. But the map can be claimed only as a comparison over $(K, o)$ with unequal group sizes, not as the first method to use the target donor's labels.
   - **Lee, Barber and Willett** (arXiv:2306.06342 v4), Remark 1 in section 2.2. Group sizes are equal, every group's score is centred on that group's own mean of $M$ outcomes, the test score is centred on the target's observed mean, and HCP's weights apply. The record cites Lee, Barber and Willett throughout, but never Remark 1.
   - **Dobriban and Yu's SymmPI** (arXiv:2312.16160 v3), section 5, the two-layer method (Propositions 5.1 and 5.2, Theorem 5.3). It needs the target's size to equal the reference sizes, or to be exchangeable with them. A few labelled spots against hundreds per reference donor do not meet that.
   - **Bersson and Hoff's FAB conformal** (preprint only, no journal version found).
     - **How it works.** The score is built from the other groups and calibrated on the target area's own labelled units.
     - **Its guarantee.** Coverage holds for each area in finite samples, conditional on the area's parameters, which is stronger than HCP's or GHCP's average over groups.
     - **What it needs.** Exchangeability within the area, independence across areas, and a score fitted without the target area. It places no condition on the number of areas.
     - **Its limits.** Its set is bounded only when $n_j \ge 1/\alpha - 1$, and it says nothing about a new area with no labelled units. GHCP does not cite it.
     - **For the record.** L1's "parametric route" is half right, since the working model affects width only. It belongs among row A6's sources.
8. **What the guarantees need with 4 to 16 donors.** Every guarantee read for a new group is marginal over that group. FAB's per-area guarantee is for an area that already has labelled units, and federated conformal covers only existing clients (item 9). Duchi, Gupta, Jiang and Sur (arXiv:2403.16336 v2, section 7, Proposition 7.24 and Corollary 7.25) show that, for homoskedastic sets and a non-atomic environment law, coverage conditional on the environment forces sets of infinite measure with high probability.
   - **HCP.** Its set is finite only when $1/(K_1 + 1) \le \alpha$. Round 3's bound written $2/(K + 1)$ uses $K$ for the paper's $K_1$.
   - **GHCP** (arXiv:2608.15500 v1). It was read in full through appendices D.5 and E.1, partly in E.4 to E.6 and F, and only searched in E.2, E.3 and the rest of F.
     - **Assumptions.** It needs reference groups larger than $o$. It assumes group size is uninformative (A2) and i.i.d. observations within a group (A3), which is stronger than HCP's within-group exchangeability.
     - **Calibration donors.** By the reader's own arithmetic on GHCP's eq. (5), not a statement of the paper, its weight at $+\infty$ is close to $1/(|S_{\text{cal}}| + 1)$ when donors have hundreds of spots and $o$ is small. GHCP then needs about as many calibration donors as HCP, and fewer are available with $\eta = 0.5$. This agrees with round 4's finding that the $\eta = 0.5$ forms are infinite at $K = 10$ and $\alpha = 0.1$.
     - **Small points.** Eq. (8) is as L1 wrote it. Section 3.1.1 says $o \le 20$, not "$o < 20$" as L1 quotes.
   - **Duchi et al.** Their $(\alpha, \delta)$-coverage is a second coverage notion for a new center. By the reader's reading of their quantile definition, it needs $\delta$ of order $1/(|D_2| + 1)$ or more, so with 4 to 10 calibration environments $\delta$ cannot be small. Their section 5 (Theorem 5.9) is the precedent for resizing from a few labelled points in a test environment (row A9). It needs the same number of labelled points drawn at random in every calibration environment, and HCP is resized there only with an oracle factor, with no theorem. GHCP appendix B.1 gives the validity of a studentized score built the same way in every group.
   - **More than two levels.** No remark, construction or example with more than two levels was found in Lee, Barber and Willett (appendix C read, appendix E skimmed) or in Duchi et al., so the institution axis stays "not found, not a gap". Lee, Barber and Willett's section 5 states the allocation between groups and repeats as an open question, which bears on S5's allocation rows. Their footnote 4 (distinct scores are needed only across groups) should be added to the L1 row.
9. **The other conformal rows.**
   - **Federated conformal.** Lu, Yu, Karimireddy, Jordan and Raskar (arXiv:2305.17564) cover a known mixture of the participating clients (Theorem 4.3), not a new client. The institution-axis row should say so.
   - **The A8 remark.** Round 5's transcription of Tibshirani, Barber and Ramdas (arXiv:2608.27310 v2), Theorems 3 and 7, matches the paper. Theorem 7 holds for any $\sigma$-finite measure. "Deterministic" for Theorem 3, and randomised mappings in Theorem 7's class, are round 5's readings, not the paper's words.
   - **Row A1.** The citation is Barber, Candès, Ramdas and Tibshirani (arXiv:2202.13415), Theorem 2 with unit weights and a symmetric algorithm, as written out in their section 4.3. The coverage gap is at most $\sum_i d_{\text{TV}}(R(Z), R(Z^i))/(n + 1)$, which has no computable value and does not shrink with more spots per donor. Its independent-data form (Lemma 1) does not apply to spots within a donor. Their Theorem 6, for contaminated data with independent points, is a possible start for row A10's missing search on an outlying donor. Their venue stays `[verify]`.
   - **Row A3.** Tibshirani, Barber, Candès and Ramdas (arXiv:1904.06019) has no theorem for estimated weights. Corollary 1 needs i.i.d. training points with an independent test point (their model 6), $Y \mid X$ unchanged, absolute continuity, and the likelihood ratio known up to a constant. Estimated, clipped weights appear only in an example, so A3's wording should be sharpened. Their section 2.3 is an open source for the effective-sample-size heuristic. The venue, NeurIPS 32, 2526 to 2536, comes from a reference list.
   - **Row A5.** Lei et al. section 5.2, on the locally weighted score, was not read.
   - **Lei et al.'s venue.** Lei et al. (2018) is JASA 113(523), 1094 to 1111, from two papers' reference lists. That lifts S1.5's `[verify]` from secondary sources only, and corrects round 5's reading log, which gives JRSS B.
   - **Other confirmations from reference lists.** Lee, Barber and Willett, ACM JDS, DOI 10.1145/3786352. Dobriban and Yu, JRSS B 87(5), 1353 to 1381. Duchi et al., Statistical Science 40(3), 392 to 416.

### 2.3 Question V and the few-cluster rows

10. **V. No source in this pass gives a finite-sample bound on a cluster's share of the variance either.** Every condition found is asymptotic.
    - **Yang, Qu and Li** (arXiv v1, Condition A1(iii)) require $\max_i(y_i - \bar y)^2/n \to 0$, Hájek's single-unit negligibility. Round 8 applied it with clusters as units.
    - **The effective number of clusters.** Carter, Schnepel and Steigerwald's version is reported in Cameron and Miller (2015, eq. 27, section VI.D). Pages here are those of the authors' February 2015 manuscript, since the journal pagination was not available. It is $G^\ast = G/(1 + \delta)$, and the reader notes that on the printed definitions this equals $1/\sum_g s_g^2$, with $s_g$ cluster $g$'s share of the variance. Its threshold, size distortion when $G^\ast < 20$ with normal critical values, is a simulation finding, not a theorem. The oversight chat's reading is that this share-based diagnostic is the closest published object to V found in either part.
    - **Bester, Conley and Hansen**, Proposition 1(ii) (item 11), allows any heterogeneity of cluster variances for a conservative $t_{G-1}$ test at small $\alpha$.
    - **Rubin-Bleuer and Schiopu Kratina** (2005, Annals of Statistics 33(6), 2789 to 2810) bound the largest scaled weight, not a share. Their $C_1$ to $C_3$ are Yung and Rao's conditions, which the paper says evolved from Krewski and Rao's, so S5 section 3.1 item 3 is reworded. Their first stage is with replacement, and their results are asymptotic in the number of primary units, so they do not explain round 5's under-coverage at $G$ of 15 and 24. Their Theorem 6.1 gives the variance about a superpopulation parameter as $J^{-1}[\Gamma_d + f\Gamma_m]J^{-1}$, with $f = \lim n/N$, so the model term is not small when $n_L/G$ is not small (row S6-6).
11. **B1, the conditions behind $t_{G-1}$.** Bester, Conley and Hansen was read as the February 2008 working paper. The 2011 article, J. Econometrics 165(2), 137 to 151, was not opened, so its numbering is to be checked. The paper fixes $G$ and lets each cluster grow. Proposition 1 needs a central limit theorem within each cluster, asymptotically uncorrelated clusters and equal cluster sizes, with a weighted least squares variant for unequal sizes (their Assumptions 5 and 6). The authors remark that their Assumption 3 is probably not reasonable for heterogeneous group sizes, and donors have unequal spot counts.
    - **Equal limiting design moments only** ($Q_g \equiv Q$). The $t_{G-1}$ test is shown to be conservative for $\alpha \le 2\Phi(-\sqrt 3) \approx 0.083$, or for any $\alpha \le 0.1$ when $2 \le G \le 14$, with any heterogeneity of cluster variances.
    - **Equal score variances as well.** These give the exact $\sqrt{G/(G - 1)}\,t_{G-1}$ limit.
    - **For the project.** Its 90% intervals ($\alpha = 0.1$) fall under the conservative statement only for $G \le 14$.
    - **Cameron and Miller (2015), section VI.C**, treat the pairs cluster bootstrap as a percentile-$t$ method; section II.F covers it as a variance estimator. They give no coverage result for the plain percentile interval round 3 used. They report Cameron, Gelbach and Miller's (2008) finding that pairs resampling did not remove over-rejection, and their section VIII.D Monte Carlo shows the pairs percentile-$t$ under-rejecting (0.005 at $G = 6$). Their outlier-cluster warning (manuscript p. 28) fits donor data. For the wild cluster bootstrap they recommend Webb's six-point weights below 10 clusters. S6-2's quote is in the section VI introduction (manuscript p. 23), not VI.A.

### 2.4 Evaluation and data rows (S1S2)

12. **Row D3 and Dip and Zhang (2026).** Going by the public abstract (the OpenReview full text was behind a human-verification check), the two do not contradict each other.
    - **Why they find little.** Their claim that patient splits add little rests, by their own account, on most of their 360 slides being the only slide from their donor, so slide and patient splits mostly coincide. D3's same-patient term is measured on the three tasks whose donors have several slides.
    - **How close their protocol is.** It covers 12 organs, with spot-to-study hold-out and size-matched fake studies (58% to 77% of the drop survives). It overlaps the record's split decomposition closely, so D3 cannot be presented as a new protocol, and their paper is the closest published one to cite.
    - **Before quoting them.** Their numbers should be read in the full text before the paper quotes them.
    - **Akram and Dip (2026).** Read at the abstract level only (119 sections, four organs).
13. **Other S1S2 sources.**
    - **Kömen et al. 2026** (PMC13260997) is "Towards robust foundation models for digital pathology", Nature Communications 17, 5218, DOI 10.1038/s41467-026-73923-2. It is a separate paper with a new benchmark, not the journal version of the 2024 workshop paper, and it is citable for D7 and D14. The deck-2 check's 88% to 98% center-prediction accuracy is right, and "near-100%" in older record documents comes from the preprints and should be replaced where it recurs.
    - **Kapoor and Narayanan** (arXiv:2207.07048 v1, section 2.4). D3's leakage is their type L3.2, and the site-shift term fits L3.3. The published version is Patterns 4(9), 100804 (2023), from Crossref, whose title replaces "ML-based" with "machine-learning-based".
    - **Hicks et al. 2018** is Biostatistics 19(4), 562 to 578. The sentence L1 quoted from the preprint is not in the published text, which should be cited by section 3.3. Its section 4 cautions against modelling technical confounders when biology is confounded with them, which bears on D10's wording and on E7's probe.
    - **Atta et al. 2024** (Genome Biology 25, 153) give a cell-level fix only. So the corpus's Xenium pseudo-spot tasks get no Atta-backed alternative to normalizing by the panel total. SpaNorm treats binned Xenium counts within one sample.
    - **Zimmerman et al. 2021** (Nature Communications 12, 738) is answered by a Matters Arising from Murphy and Skene (2022, DOI 10.1038/s41467-022-35519-4), which reverses its conclusion that pseudobulk is inferior. Cite it for pseudoreplication only. Its finding that GEE sandwich errors are too small below about 30 units bears on B1.
    - **Bibliographic details.** Murphy 1988 is Monthly Weather Review 116(12), 2417 to 2424 (Crossref; full text blocked). Chambers 1986 is JASA issue 396, and its abstract confirms D13's definition of a representative outlier. Hafemeister and Satija is article 296.

## 3. Corrections to L1 and to part 1 from this pass

1. **Part 1's correction 7** (the Sanguiao Sande and Zhang divisor) is withdrawn. L1 S4's table row should read $\frac{1}{K}\sum_k(\hat Y_{1k} - \hat Y^K_{GR})^2$, targeting the variance of the Monte Carlo average, with eq. (13) in section 3.3. It should add their exact single-split and full Rao-Blackwellised variance estimators, for units. Part 1 is frozen, so the correction stands here.
2. **L1 S4 B9 and section 3.** Williams' (13) needs $n/N$ negligible (section 1, item 2), and the optimum $k = \sqrt{n/3}$ is confirmed.
3. **L1 S4 and S6, the rows on the split-sample papers.** The rows on Kwon et al., Dharamshi et al., Zhang et al. (whose general results belong to Zhang, Sanguiao-Sande and Lee 2025), Lu et al. and An et al. are now full or sectional readings, as in item 3. The sections of An et al. read (3.1 to 3.4, 4.1, 4.2, 5.1, 7, 8, B.1) do not treat an intercept or level term apart from the learner (S6-4).
4. **L1 S3 rows A1, A3, A5, A6, A8 and C10, and GHCP.** They change as in items 6 to 9. GHCP section 3.1.1 says $o \le 20$. S1.5's `[verify]` on Lei et al.'s venue can be lifted from secondary sources.
5. **L1 S5 and S6 on few-cluster inference.** Rubin-Bleuer and Schiopu Kratina (S5 section 3.1 item 3 and S6-6) and Cameron and Miller (S6-2) change as in items 10 and 11.
6. **L1 S1S2.** D3, Kömen et al., Hicks et al., Zimmerman et al. and Kapoor and Narayanan change as in items 12 and 13. Dip and Zhang's title takes a colon.
7. **Bibliographic details.**
   - Breidt and Chauvet's DOI is 10.1016/j.jspi.2010.06.022, volume 141, issue 1.
   - Hidiroglou is volume 40, issue 1.
   - Fattorini is Biometrika 93(2), 269 to 278.
   - Mashreghi, Haziza and Léger is Statistics Surveys 10, 1 to 52.
   - Cameron, Gelbach and Miller 2008 is REStat 90(3), 414 to 427.
   - Bester, Conley and Hansen 2011 is J. Econometrics 165(2), 137 to 151.
   - The Moulton, Johnson and Cassel et al. DOIs resolve to the right titles, with first pages 334, 536 and 615.
   - Yang, Qu and Li exist on arXiv as v1 only.
   - Cameron and Miller's DOI, Rubin-Bleuer and Schiopu Kratina's venue and Murphy 1988's DOI are confirmed.
   - Atta and Zimmerman are articles 153 and 738.
8. **Verdicts.**
   - No "no genuine gap" verdict changes.
   - Two novelty statements narrow: C10's claim for the map (item 7), and D3's claim to a new protocol (item 12).
   - The gap round 8 left open for Williams' form was closed in part 1 by its reading of Mickey. Item 2 now shows that only the combination over the two halves rests on that reading.

## 4. What L2 still lacks

**Not reachable through the browser without signing in or a human-verification check.**
- Project Euclid, behind a CAPTCHA:
  - Mashreghi, Haziza and Léger 2016 (DOI 10.1214/16-SS113, open access; S6-2, the design-target bootstrap);
  - Bloznelis 1999 (DOI 10.1214/aop/1022874830; B8, V);
  - Breidt and Opsomer 2017 (DOI 10.1214/16-STS589; cross-fitting in model-assisted estimation).
- Bot checks: the published Cameron, Gelbach and Miller 2008 (MIT Press) and the published Lee, Barber and Willett (ACM).
- OpenReview behind a check: the full texts of Dip and Zhang (vRuKRH2BFK) and Akram and Dip (d1G4Ek1494).
- Blocked by the publisher: Murphy 1988 and Moran 1950.

**Paywalled.**
- Hidiroglou 1986 (V, E7).
- Breidt and Chauvet 2011.
- Fattorini 2006.
- Moulton 1990.
- Johnson 1978.
- Cassel, Särndal and Wretman 1976.
- The published Bester, Conley and Hansen 2011.
- Yang, Qu and Li (JASA).
- Chambers 1986.
- The published Sanguiao Sande and Zhang (Sankhya A 2021).
- Vovk, Gammerman and Shafer's book.

**Not opened or not read.**
- Zhang, Sanguiao-Sande and Lee (2025, JOS 41, 404 to 432, section 2.3.2). It is the primary source for the Monte Carlo MSE estimator with the $1/T$ divisor, and it bears on E.
- Shafer and Vovk (2008, JMLR, open). The pane gave no text from its PDF.
- Lei et al. section 5.2 (row A5).
- Kish 1965. An Internet Archive scan exists, of unclear rights status, and was not opened.
- Deville and Tillé (2004). OpenAlex lists an open copy (S5.9), not opened.

**Which ones matter.** Whether any of these is needed before L3 is the ledger's call at L3, by what each row's verdict rests on. The ones that bear on a decision are:
- Zhang, Sanguiao-Sande and Lee 2025 and Breidt and Opsomer 2017 (E);
- Bloznelis 1999 and Hidiroglou 1986 (V, B8, E7);
- Mashreghi et al. 2016 (S6-2).
