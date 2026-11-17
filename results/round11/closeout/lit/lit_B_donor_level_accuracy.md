# Literature log B: donor-level accuracy of histology-predicted expression

*Search run on 16 November 2026 by sub-agent `lit-B` (frame `c9016697-c909-435e-82fc-ebfb9daaa857/lit-B`) of track `closeout`, under the brief's section 4 ("any published report of donor-level (not spot-level) accuracy of such predictors"). Read levels are the sub-agent's, as in log A; for the track every entry is at second hand until a session opens it. Full texts were read through Europe PMC's REST service. No paper text is stored here. This is a literature check that informs the predictor choice. It is not a novelty check, and nothing here is claimed as new (`docs/EXECUTION_RULES.md`, section 4).*

## Query log (all 16 November 2026)

| # | query | engine | relevant hits |
|---|---|---|---|
| 1 | pseudo-bulk patient-level correlation predicted gene expression histology spatial transcriptomics held-out patients | web search, extended | 4 |
| 2 | HE2RNA Schmauch 2020 Nature Communications genes significantly predicted | web search | 1 |
| 3 | SEQUOIA Pizurica 2024 digital profiling linearized transformer | web search | 1 |
| 4 | DeepPT Hoang 2024 Nature Cancer ENLIGHT | web search | 1 |
| 5 | tRNAsformer Alsaafin 2023 Communications Biology | web search | 1 |
| 6 | Path2omics histology gene expression prediction fresh frozen FFPE | web search | 2 |
| 7 | MOSBY spatial transcriptomics bulk RNA histology model | web search | 1 (not opened) |
| 8 | spatial gene expression prediction histology evaluation pitfalls slide-level mean expression inflates correlation | web search, extended | 3 |
| 9 | STimage Nature Communications 2026 pseudo-bulk correlation 0.48 | web search | 2 |
| 10 | histology expression prediction gene-mean error held-out genes held-out individuals | web search, extended | 1 |
| 11 | "ST-Net" He 2020 TCGA bulk validation | web search | 1 |
| 12 | Europe PMC: "DeepSpot" spatial transcriptomics H&E | Europe PMC API | 3 |
| 13 | histology-predicted gene expression "within-patient" "between-patient" correlation decomposition | web search, extended | 2 (no decomposition) |
| 14 | spatial transcriptomics prediction aggregated slide-level predictions vs bulk HEST pseudobulk | web search, extended | 4 |
| 15 | gene expression prediction pooled across slides inflated by between-slide differences | web search, extended | 2 (no direct test) |
| 16 | prediction-powered inference clustered data cluster-level correlation arXiv | web search, extended | 2 |
| 17 | Battese Harter Fuller 1988 error-components model | web search | 1 |
| 18 | Hidiroglou You 2016 comparison of unit level and area level small area estimators | web search | 1 |
| 19 | satellite imagery poverty between-village vs within-village Yeh 2020 | web search | 1 |
| 20 | Corral Molina Nguyen 2021 Pull your small area estimates up by the bootstraps | web search | 1 (not opened) |
| 21 | generalized regression estimator two-stage cluster sampling variance cluster-level residuals | web search | 1 |
| 22 | Fay Herriot 1979 estimates of income for small places | web search | 1 |
| 23 | prediction-powered inference small area estimation domain means | web search | 2 |
| 24 | Newhouse Merfeld small area estimation poverty Mexico satellite | web search | 1 (not opened) |

## Papers

| identifier | title (short), first author, year, venue | read level | finding |
|---|---|---|---|
| doi:10.1038/s41467-020-17678-4 | HE2RNA, Schmauch et al., 2020, Nature Communications | full text (first part) | Bulk RNA from TCGA slides, patient-split CV, per-gene Pearson across held-out patients. Best genes about 0.38 to 0.46; the share of significant genes depends on the correction and on cohort size |
| Europe PMC PMC10033650 | tRNAsformer, Alsaafin et al., 2023, Communications Biology | full text (first part) | Relative RMSE about 0.96 to 0.98, so little gain over predicting the mean |
| doi:10.21203/rs.3.rs-3193270/v1 | DeepPT preprint, Hoang et al., 2023 (Nature Cancer 2024 version not confirmed) | full text of preprint | Thousands of genes with across-patient r > 0.4 in most cancers; signature scores beat their member genes (an aggregation gain); 200-sample training subsets still give many significant genes |
| doi:10.1038/s41467-024-54182-5 | SEQUOIA, Pizurica et al., 2024, Nature Communications | full text (first part) | Average across-patient r 0.504 with UNI features and linearized attention (gene set unclear); UNI against ResNet raised r by 145 to 250%; downsampling lowered every metric. Its spatial check, within-slide median PCC 0.168 (breast), is lower than its bulk across-patient value, but the two metrics differ |
| doi:10.1101/2025.02.26.640189 | Path2Omics, Hoang et al., 2025, preprint | full text (first part) | Median per-gene across-patient r 0.27 (FFPE) and 0.36 (fresh-frozen) |
| doi:10.1038/s41467-025-56618-y | spatial prediction benchmark, C. Wang et al., 2025, Nature Communications | full text | Pseudo-bulk against TCGA bulk as one correlation per image (across genes): 0.33 to 0.53 by method. Not a between-donor accuracy |
| doi:10.1038/s41467-026-68487-0 | STimage, Tan et al., 2026, Nature Communications | full text (first part) | Pseudo-bulk against bulk, about 0.48, apparently across genes per patient |
| doi:10.1002/advs.202514351 | HiST, Li et al., 2026, Advanced Science | full text (first part) | Pseudo-bulk against bulk across genes per patient, 0.67 to 0.76 |
| arXiv:2603.14897 | BiTro, Yu et al., 2026, preprint | full text (first part) | Joint training on bulk (patient-level) and spatial targets helps modestly both ways; no across-patient per-gene number |
| doi:10.64898/2026.09.15.751768 | Chen and Hicks, 2026, bioRxiv | full text (first part) | Splits MSE into a gene-mean part and a within-gene part for held-out genes; gene means carry most of the gain. Nearest decomposition found, but over genes, not donors |
| arXiv:2508.01490 | Gindra et al., 2025, preprint | full text | Patient-level splits are harder; batch effects may confound the image-expression link |
| doi:10.1093/bib/bbag090 | review, Beachum et al., 2026, Briefings in Bioinformatics | full text (first part) | Dataset size strongly influences how many genes are well predicted |
| https://www150.statcan.gc.ca/pub/12-001-x/2019003/article/00001/02-eng.htm | Kennel and Valliant, 2019, Survey Methodology | full text, section 2 | Under two-stage sampling the GREG variance is set by the between-cluster spread of cluster residual totals, so a predictor helps a population mean to the extent it explains cluster totals |
| doi:10.1038/s41467-020-16185-w | Yeh et al., 2020, Nature Communications | full text (first part) | Satellite predictors of wealth: village-level $r^2$ 0.67 to 0.70 for levels, 0.15 to 0.17 for changes, 0.51 for district-aggregated changes; skill comes mostly from separating clusters |
| JSTOR 2288915 | Battese, Harter and Fuller, 1988, JASA | abstract | Nested-error unit-level model for county means |
| doi:10.1080/01621459.1979.10482505 | Fay and Herriot, 1979, JASA | secondary | Area-level model; area covariates must explain between-area variation |
| Statistics Canada 12-001-x 2016001 article 14540 | Hidiroglou and You, 2016, Survey Methodology | abstract | Unit-level estimators beat area-level ones in a design-based simulation |
| arXiv:2610.09601 | Broska and Howes, 2026, Cluster-Robust PPI | abstract | Precision gains depend on the labelling design |
| arXiv:2609.20758 | Prediction-Powered Smoothing and Validation, 2026 | abstract | Fay-Herriot-type smoothing of domain-level PPI estimates |

Abstract or secondary only: ST-Net (doi:10.1038/s41551-020-0578-x), BLEEP (arXiv:2306.01859), DeepSpot (doi:10.1101/2025.02.09.25321567, README only), NeurIPS 2026 workshop "Patient-Held-Out Evaluation of Pathology Foundation Models" (neurips.cc/virtual/2026/177227). Not opened: MOSBY (doi:10.1038/s41598-024-69198-6), Corral, Molina and Nguyen 2021, Newhouse et al., an AACR 2026 abstract, Kluger et al. (arXiv:2501.18577, already in the project's record).

## What the track takes from it

- **No published donor-level accuracy for spatial-trained predictors was found** in the form the project measures (per gene, across held-out donors, donor-mean prediction against donor-mean measurement). The pseudo-bulk checks in print correlate across genes within a patient, which mean expression differences between genes dominate. This is a search result for the predictor choice, not a claim of novelty.
- **Levers that raise across-patient accuracy in bulk predictors:** more training patients, pathology-pretrained encoders over ImageNet ones, and slide-level aggregation. The project already uses pathology encoders, and its spot predictions are averaged to donor means, so the levers left are more training donors and a stronger slide or neighbourhood summary.
- **Round 9's donor-mean head** (`docs/round09/README.md`, "What was tried and did not work") is not repeated, since nothing here supplies a reason that would change its outcome at 15 to 51 donors.
- **The statistical anchor** for "the gain follows donor-level accuracy" is the cluster-sampling variance of model-assisted estimators (Kennel and Valliant 2019) and the small-area literature. The finding is classical in substance.
