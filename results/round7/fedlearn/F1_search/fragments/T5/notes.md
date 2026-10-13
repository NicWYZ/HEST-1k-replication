# T5 fragment notes: heterogeneity across centres (Q4)

Searched 2026-10-13. Sources: PubMed, Europe PMC, arXiv (search page after API 429s), web search, and local title scans of NeurIPS 2019-2025, PMLR (ICML 2019-2025, AISTATS 2020-2025) and MICCAI 2024-2025 index pages. 83 papers included (24 core candidates). All reads are abstract level unless a row says otherwise; full texts of 18 papers are saved to fedlearn_papers/T5, but only excerpts were read, so no row is marked full text. Counts are provisional.

## By question (Q4)
**Non-IID and personalisation (generic methods).** FedProx (1812.06127; abstract states a 22% average accuracy gain over FedAvg in highly heterogeneous settings), SCAFFOLD (1910.06378), FedBN (2102.07623), personalisation (Per-FedAvg, FedPer, FedRep, Ditto, Marfoq et al. 2022 kNN memorisation, 2024 Bayesian PFL), and surveys. All natural-image or benchmark data. Nothing found that tests them on regression of expression.
**Pathology stain/scanner shift.** BottleGAN, Shen et al. orchestral GAN, FedSDA (AAAI 2026 / 2511.12044), FedStain, FedHisto-PAST (frozen HIBOU-B encoder), PathFL, HER2 stain-augmented FL, and the Schoenpflug review (domain alignment 4-20% vs 0-3% for aggregation changes). Scanner shift in frozen foundation-model embeddings is documented by Thiringer et al. (2601.04163), not in a federated setting. All are classification or segmentation.
**Batch and site effects in omics.** fedRBE (2412.05894; handles non-identical feature sets), FedscGen, Federated Harmony, Garst et al. 2025 (federated learning sensitive to batch effects that coincide with site), HIV consortium preprint (gains depend on site size and between-site heterogeneity; FedAvg/FedProx worse under heterogeneity in simulation). Random-effects / one-shot summary-statistic methods: Limpoco et al., PEAL, FedGMMAT, dMEGA, ODAL, FETA.
**Partial label overlap.** Only classification/segmentation: FedMLP, FedIA, UFPS, multi-organ segmentation (2206.07156), heterogeneous private label sets (2508.18774). Nothing found for regression targets (genes) that differ across sites.
**Partial feature overlap.** Covariate mismatch in collaborative linear prediction (2602.02083; aggregated covariance blocks, ridge) is the closest statistical match, but mismatch is in covariates, not in output genes. Also Fed-ReMasker (2609.28105), FLIC (2301.11447), LASER-VFL, multimodal missing-data methods.
**Platform / gene panel.** Descriptive only: Janesick 2023, Xenium off-target probes, SpatialBench, Genome Biology 2026 platform comparison, Nature Methods 2026 Xenium panel study; HESCAPE (2508.01490) pools six gene panels. No federated method for differing gene panels was found within the sources and queries in the search log.

## Queries with no relevant result
q05 on PubMed (1 hit) and arXiv (2 hits, both pathology stain papers); q06 PubMed (0); q07 PubMed (0); q09 arXiv (0), PubMed (1); q12 (federated learning + spatial transcriptomics + histology + expression) PubMed 0, arXiv 0; q15 arXiv 0; q19 and q20 arXiv 0. Proceedings title scans: q03a, q03b, q05 returned 0 federated titles. Zero counts are for the exact strings run (arXiv ANDs all terms).

## Core candidates and why
FedProx, SCAFFOLD, FedBN (method family named by the review); FedSDA, FedStain, Cong et al. FedDFP (federation on frozen features under stain shift); fedRBE, Federated Harmony, FedscGen (batch correction); Garst et al., HIV preprint, Schoenpflug review (evidence on heterogeneity cost); Limpoco, PEAL, ODAL, FETA (one-shot sums with site effects); 2602.02083, Fed-ReMasker, FLIC (partial feature overlap); Thiringer (scanner shift in embeddings); HESCAPE and Janesick (multi-panel/platform context); Marfoq (C4-like memorisation). Core flags are provisional for the lead.
Core candidates whose full text was NOT retrieved: FETA 10.1214/23-aoas1747 (Project Euclid blocked), Limpoco 10.1002/bimj.70080, PEAL 10.1038/s41746-026-02861-6, ODAL 10.1093/jamia/ocz199, Schoenpflug 10.1016/j.csbj.2024.10.037, Janesick 10.1038/s41467-023-43458-x, TheODen Germany study 10.1038/s41746-026-02958-y, Marfoq (PMLR v162 marfoq22a). Full texts retrieved but only excerpts read: see saved list in fedlearn_papers/T5.

## Discrepancies
- Lu et al. MIA 2022: seed DOI 10.1016/j.media.2022.102298 does not resolve; the paper is 10.1016/j.media.2021.102298 (vol 76, article 102298); description matches.
- Federated Harmony: PLoS Comp Biol 2025 title is "Harmony-based data integration for distributed single-cell multi-omics data"; the method name appears in the abstract.
- fedRBE (arXiv:2412.05894) is titled "Batch effects can impair federated learning in multi-center omics studies"; fedRBE is introduced inside it.
- scFed: Crossref gives 2023 (online); seed said 2024 25(1).
- Duan JAMIA 2020 (10.1093/jamia/ocz199) is ODAL, one-shot logistic regression, narrower than the seed description.
- Wang et al. Nat Commun 2025 (10.1038/s41467-025-56618-y): abstract does not mention weak transfer across studies; unverified.
- Off-target Xenium paper: PMC version reports 21 of 280 genes, eLife reviewed preprint 14 of 313.
- Cong et al.: Crossref gives npj Digital Medicine vol 9, article 578, matching the seed.

## Not covered
Not run on arXiv (HTTP 429): nine broader follow-up queries (q22-q30). OpenReview searched only through four web searches. MICCAI 2020-2023 and NeurIPS 2025 not scanned. EPMC/PubMed top-100 for q01-q04, q07, q08, q11 were keyword-screened, not read title by title. HEST-1k, STPath, STFlow were not opened (other themes). FedEdgeR (bioRxiv 10.64898/2026.09.17.752480) excluded: no abstract available.
