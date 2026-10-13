# T4 notes: distributed and federated statistical estimation (Q7)

Date 2026-10-13 (revised after the lead's request to complete every protocol query on every source). Fragment: `search_log.csv` (122 rows, 48 query ids), `evidence.csv` (95 papers). Full texts are in `/Users/nicolaszhang/hest-1k/fedlearn_papers/T4/`, not in this repository. Statements hold only within the sources and queries in the search log.

## What was found, by question (Q7)

**One-shot and communication-efficient estimation.** Foundations: Zhang, Duchi and Wainwright (arXiv 1209.4129), DANE (PMLR v32 shamir14), Lee et al. (arXiv 1503.04337), Battey et al. (10.1214/17-AOS1587), Jordan, Lee and Yang (10.1080/01621459.2018.1429274), Fan, Guo and Wang (10.1080/01621459.2021.1969238), one-round M-estimation (PMLR v130 bao21a), debias-and-average LDA (PMLR v54 tian17a), information limits of one-shot schemes (NeurIPS 2019, arXiv 1911.00731), CEDAR (PMID 36305019); review arXiv 2304.06245. The surrogate-likelihood family (ODAL 10.1093/jamia/ocz199, ODAC PMID 32626900, ODACH, ADAP, heterogeneity-aware 10.1093/biomet/asab007, competing-risks versions) sends gradients or Hessians and is near-pooled, not exact.

**Distributed ridge and sufficient statistics.** Averaging local ridge fits (Dobriban and Sheng, 10.1214/20-AOS1984; PMLR/ICML version sheng20a, arXiv 1903.09321) loses little prediction accuracy but inflates estimation error and interval length. Exact recovery from summed Gram matrices appears in arXiv 2601.08216 (single-author preprint; synthetic experiments only; linear models only). Closest matches to a frozen-encoder head are classification papers: Fed3R (arXiv 2406.01116), AFL (arXiv 2405.16240, which reports numerical drift without a regularisation step), FedCOF (arXiv 2412.14326), FedPFT (arXiv 2402.01862). Queries T4-q03, q11, q12 and q16 found no paper on federated ridge for continuous high-dimensional outputs such as expression.

**Federated PCA.** Approximate aggregation of local eigenspaces (10.1214/18-aos1713), streaming differentially private PCA (Grammenos et al.), secure PCA (SF-PCA), masking-based lossless federated SVD (arXiv 2105.08925), sketching (PMID 41336158), quantised distributed PCA (NeurIPS 2021), Balcan et al. (NeurIPS 2014), PCA under batch effects (10.1093/bioadv/vbac026). No paper found that forms the PCA basis exactly from summed centred second moments and then fits a head, although the algebra is additive; that route is not documented in the sources searched.

**Mixed and random-effects models.** DLMM (PMID 35354802) and the mean/covariance/n version (PMID 39663139) are exact and one-round for linear mixed models; dPQL, FedGMMAT and the 2024 and 2026 summary-statistic GLMM preprints cover generalised cases. Centre as a random effect is supported by published methods for the linear case.

**Transfer learning and heterogeneity.** FETA (10.1214/23-AOAS1747), Trans-Lasso and its GLM version, federated transfer with differential privacy (arXiv 2403.11343), ReFIT, multi-task learning from summary statistics (arXiv 2307.02388). Zhao, Wang and Lin (COLT 2023, PMLR v195 zhao23b) prove that aggregating more devices can hurt when parameters differ across them, which bears on Q1 and Q9.

**Inference.** Federated causal inference (10.1002/sim.9868), robust inference for federated meta-learning (arXiv 2301.00718), Bayesian federated inference (PMIDs 38589978, 41626974, 41647937), federated conformal prediction (arXiv 2305.17564, 2302.06322; PMLR plassier24a). Summary-statistics versus individual-data equivalence: Lin and Zeng (10.1093/biomet/asq006; PMID 19847795), PMID 32056197. None handles centre-level (cluster) error of a prediction head.

**DataSHIELD.** Wolfson 2010, Gaye et al. 2014 (10.1093/ije/dyu188), Marcon et al. 2021, Avraam et al. 2025, Armadillo, PLoS ONE accuracy test, dsSurvival, federated GAMLSS, LifeCycle consortium.

**Not found.** Nothing in T4 queries on federated prediction of expression from histology, no application of these methods to pathology embeddings, and no learning curve in the number of centres for such a head.

## Core candidates (23; the lead decides)
- https://doi.org/10.1080/01621459.2018.1429274 — Jordan, 2019: Communication-Efficient Distributed Statistical Inference (full text)
- https://doi.org/10.1214/17-AOS1587 — Battey, 2018: Distributed testing and estimation under sparse high dimensional models (abstract only)
- https://doi.org/10.1214/20-AOS1984 — Dobriban, 2021: Distributed linear regression by averaging (full text)
- https://doi.org/10.1080/01621459.2021.1969238 — Fan, 2023: Communication-Efficient Accurate Statistical Estimation (abstract only)
- https://doi.org/10.1214/18-aos1713 — Fan, 2019: Distributed estimation of principal eigenspaces (full text)
- 1907.08059 — Grammenos, 2020: Federated Principal Component Analysis (full text)
- https://doi.org/10.1093/jamia/ocz199 — Duan, 2020: Learning from electronic health records across multiple sites: A communicat (abstract only)
- 35354802 — Luo, 2022: DLMM as a lossless one-shot algorithm for collaborative multi-site distribu (full text)
- 39663139 — Limpoco, 2025: Linear Mixed Modeling of Federated Data When Only the Mean, Covariance, and (full text)
- https://doi.org/10.1093/ije/dyu188 — Gaye, 2014: DataSHIELD: taking the analysis to the data, not the data to the analysis (full text)
- https://doi.org/10.1093/biomet/asq006 — Lin, 2010: On the relative efficiency of using summary statistics versus individual-le (abstract only)
- 32056197 — Chen, 2020: Relative efficiency of using summary versus individual data in random-effec (abstract only)
- https://doi.org/10.1214/23-AOAS1747 — Li, 2023: Targeting underrepresented populations in precision medicine: A federated t (full text)
- https://doi.org/10.1002/sim.9868 — Xiong, 2023: Federated causal inference in heterogeneous observational data (abstract only)
- 2402.01862 — Beitollahi, 2024: Parametric Feature Transfer: One-shot Federated Learning with Foundation Mo (full text)
- 2406.01116 — Fanì, 2024: Accelerating Heterogeneous Federated Learning with Closed-form Classifiers (full text)
- 2405.16240 — He, 2024: AFL: A Single-Round Analytic Approach for Federated Learning with Pre-train (full text)
- 2412.14326 — Goswami, 2024: Covariances for Free: Exploiting Mean Distributions for Training-free Feder (full text)
- 2601.08216 — Alsulaimawi, 2026: One-Shot Federated Ridge Regression: Exact Recovery via Sufficient Statisti (full text)
- 39635226 — Li, 2024: Federated Learning in Healthcare: A Benchmark Comparison of Engineering and (abstract only)
- https://proceedings.mlr.press/v195/zhao23b.html — Xuyang Zhao, 2023: The Aggregation–Heterogeneity Trade-off in Federated Learning (full text)
- 2105.08925 — Chai, 2021: Practical Lossless Federated Singular Vector Decomposition over Billion-Sca (full text)
- 2307.02388 — Knight, 2023: Multi-Task Learning with Summary Statistics (full text)

## Reading level
Records marked full text were retrieved and read for abstract, introduction or method summary, the results or experiment sections and the conclusion; proofs, appendices and most proof-heavy sections were not read. Abstract only: Battey et al. (Project Euclid blocked), Fan, Guo and Wang (arXiv copy saved), Lin and Zeng (PDF saved; text extract ended in references), ODAL JAMIA (PMC copy was only abstract-sized). Their DOIs: 10.1214/17-AOS1587, 10.1080/01621459.2021.1969238, 10.1093/biomet/asq006, 10.1093/jamia/ocz199.

## Discrepancies with the scan
- Seeds confirmed as described: Jordan, Lee and Yang (JASA 114(526), 2019); Battey et al. (Ann Stat 2018; 'Distributed testing and estimation under sparse high dimensional models'); Dobriban and Sheng (Ann Stat 2021, 'Distributed linear regression by averaging'); Fan, Guo and Wang (JASA 118(542), 2023, online 2021); Gaye et al. (Int J Epidemiol 2014); Duan et al. (JAMIA 27(3), 2020); Li, Cai and Duan (Ann Appl Stat 17(4), 2023, DOI 10.1214/23-AOAS1747).
- Grammenos et al. (NeurIPS 2020) is a streaming, differentially private PCA, not an exact PCA from summed covariances.
- Duan et al. 2020 (ODAL) is one-shot but needs one lead site's patient data and is not lossless, unlike DLMM.
- fedRBE: arXiv 2412.05894 (Burankova et al.) is titled 'Batch effects can impair federated learning in multi-center omics studies' on its abs page; outside T4, the lead should check.

## Coverage and what was not done
- Every protocol query (q01 to q10) was run on PubMed, Europe PMC, arXiv, the web search, NeurIPS proceedings search and (through the web search tool, because PMLR has no working search endpoint) PMLR. Eight follow-up queries (q11 to q18), five quoted PubMed variants (q22 to q26), three web follow-ups (q19 to q21) and three forward-citation searches (q27 to q29) were added. The arXiv API throttled the first attempts; the final run used 6 s spacing with 60 s waits and completed for all 18 queries.
- Lists were retrieved to 100 hits by relevance; titles were screened by reading a keyword-prefiltered subset (306 of about 2,100 distinct titles) in addition to the first 8 to 12 titles of each list read directly. Titles outside the prefilter were not read; papers whose titles lack the prefilter words could be missed. For PubMed lists over 100 hits (q04, q06, q13) and Europe PMC lists over 100, only the first 100 were screened.
- NeurIPS search matches all words in a record, so the full protocol strings mostly returned nothing; shortened variants were also run (ids ending in v).
- arXiv queries are AND of all words, not exact phrases; zero-hit arXiv rows may reflect that.
- Forward citations only for DLMM, ODAL (PSB) and FETA, first 14 citing records each. OpenAlex and Semantic Scholar were not used.
- Karr et al. 2005 (10.1198/106186005x47714) dropped: no abstract opened.
