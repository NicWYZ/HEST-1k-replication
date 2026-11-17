# Literature log A: the strongest predictor of spot-level expression from histology

*Search run on 16 November 2026 by sub-agent `lit-A` (frame `c9016697-c909-435e-82fc-ebfb9daaa857/lit-A`) of track `closeout`, under the brief's section 4 ("Literature first"). The read level is the sub-agent's: "full text" means the HTML full text read through a fetch summariser, "abstract" the listing or abstract page, "secondary" a search snippet. The lead session has not opened these pages itself, so for the track every entry is read at second hand through the sub-agent until a session opens it. No paper text is stored here. Three PDFs the fetch tool saved automatically outside the repository were deleted unread on 16 November.*

## Query log (all 16 November 2026)

| # | query or URL | engine | relevant hits |
|---|---|---|---|
| 1 | arxiv.org/abs/2406.16192 and its HTML v2 | fetch | 1 |
| 2 | HEST-Benchmark leaderboard ridge XGBoost PCA 256 encoders Pearson | web search | 3 |
| 3 | github.com/mahmoodlab/HEST README | fetch | 1 |
| 4 | benchmarking spatial gene expression prediction from histology Nature Communications 2025 Hist2ST HisToGene THItoGene BLEEP | web search | 3 |
| 5 | benchmark deep learning methods predicting spatial transcriptomics from histology Briefings in Bioinformatics 2024 2025 | web search | 3 |
| 6 | pathology foundation models gene expression prediction benchmark linear probe MLP spatial transcriptomics HEST 2025 arXiv | web search, extended | 5 |
| 7 | "spatial gene expression" prediction foundation model embeddings ridge versus MLP head comparison patient held-out Visium | web search, extended | 3 |
| 8 | DeepSpot spatial context foundation model H&E gene expression Nonchev | web search | 2 |
| 9 | THUNDER benchmark pathology foundation models tile-level spatial transcriptomics | web search | 0 |
| 10 | STFlow whole-slide flow matching spatial transcriptomics histology HEST-Bench ICML 2025 | web search | 1 |
| 11 | benchmark pathology foundation models spatial transcriptomics prediction fine-tuning versus linear probing neighbor aggregation HEST arXiv 2025 | web search, extended | 3 |
| 12 | "linear probe" "MLP" gene expression prediction pathology foundation model frozen features spatial transcriptomics comparison results | web search, extended | 2 |
| 13 | graph neural network neighboring spots frozen UNI features gene expression prediction HEST-Benchmark improvement over ridge | web search, extended | 1 |
| 14 | SpaRED SpaCKLE benchmark spatial gene expression prediction histology arXiv | web search | 1 |
| 15 | STimage-1K4M histopathology image gene expression dataset benchmark arXiv 2406 | web search | 1 |
| 16 | mclSTExp multimodal contrastive learning spatial gene expression prediction transformer neighbor spots Briefings in Bioinformatics | web search | 1 |
| 17 | THItoGene Briefings in Bioinformatics 2024 Jia predicting spatial transcriptomics histological images doi | web search | 1 |
| 18 | gene expression prediction from histology effect of number of training patients samples learning curve spatial transcriptomics | web search, extended | 1 |
| 19 | kaiko eva framework pathology foundation model evaluation spatial transcriptomics regression task | web search | 0 |
| 20 | Patho-Bench Mahmood lab benchmark tasks gene expression linear probe | web search | 0 |
| 21 | does spatial context help? gene expression prediction histology foundation model ablation neighbor tiles larger field of view Visium patient-level 2026 | web search, extended | 3 |
| 22 | HEST benchmark "MLP" probe outperforms ridge gene expression foundation model embeddings Pearson | web search, extended | 1 |
| 23 | Europe PMC REST look-ups by DOI (DeepSpot, SEQUOIA, ST-Net, THItoGene, MISO, HisToGene) | fetch | 6 abstracts |

## Papers with a finding on the four directions

| identifier | title (short), first author, year, venue | read level | finding, in the sub-agent's numbers |
|---|---|---|---|
| arXiv:2406.16192 | HEST-1k, Jaume et al., 2024, NeurIPS Datasets and Benchmarks | full text | Patient-stratified CV, top 50 genes, PCA-256 + ridge: H-Optimus-0 0.4146 mean Pearson, UNI v1.5 0.4090. Appendix: XGBoost (100 trees, depth 3) lower by about 0.02 for both; ridge at fixed $\lambda$ without PCA far lower (about 0.27), so a ridge without PCA needs its $\lambda$ tuned |
| github.com/mahmoodlab/HEST (README, leaderboard dated 03.04.26) | HEST-Benchmark leaderboard | full page | PCA-256 + ridge: H-Optimus-1 0.4229, H-Optimus-0 0.4150, UNI2-h 0.4141, Virchow2 0.4034, Phikon-v2 0.3747, ResNet50 0.3252. The best frozen encoder is about 0.009 above UNI2-h |
| arXiv:2609.05956 | STP-Bench, Lee (corresponding) et al., 2026, preprint | full text, figures not read | 21 methods mostly on UNIv2, patient-level 5-fold. Most fail to beat the UNIv2 linear probe; only methods with neighbourhood or global context (TRIPLEX, DeepSpot) beat it consistently. UNIv2, H-Optimus-1 and Virchow2 broadly comparable. More spots within a cohort gave marginal gains; pooling cancer types often hurt |
| arXiv:2506.05361 | STFlow, Huang et al., 2025, ICML | full text | HEST-Bench with UNI: STFlow 0.415, TRIPLEX 0.395, a random-forest head 0.344; removing its spatial encoding costs 0.009 |
| arXiv:2403.07592 | TRIPLEX, Chung et al., 2024, CVPR | full text | On a ResNet18 encoder, leave-one-patient-out: removing the neighbour view costs 0.044 on SCC; removing the global view costs 0.048 on BC1 |
| arXiv:2610.18769 | MIST, Howlader et al., 2026, preprint | full text | Frozen UNI + CONCH, slide-disjoint splits: a kNN-neighbour pathway adds 0.016, local plus slide pathways 0.024; random neighbours instead of spatial ones cost 0.031 |
| arXiv:2609.28563 | SpaFactor, Ruan et al., 2026, preprint | full text | Frozen GigaPath, slide-level 5-fold: spatial context adds 2.4 points of gene-wise Pearson (×100) over its spot-only head; an MLP head is about level with the spot-only head |
| arXiv:2611.13649 | single-cell expression from H&E with pathology FMs, 2026, preprint | full text | Single-cell Xenium, donor-disjoint: a 2-layer MLP beats an SGD-trained linear layer by 0.044 to 0.056; not at spot level, and the linear head is not a tuned ridge |
| arXiv:2602.14177 | SEAL, Hemker et al., 2026, preprint | full text | A linear probe on frozen Virchow2 is very strong; fine-tuning gains at most about 1.3% |
| arXiv:2504.07061 | PEKA, Pan et al., 2025 | full text | Fine-tuning the encoder adds 0.04 to 0.07; outside the four directions (it needs weights to be trained, and the split unit is unstated) |
| doi:10.1038/s41467-025-56618-y | benchmarking spatial expression prediction, C. Wang et al., 2025, Nature Communications | full text (first part) | On CNN-era encoders, single-patch methods beat neighbour-integrating ones (Hist2ST, HisToGene) |
| arXiv:2505.02980 | SpaRED/SpaCKLE, Ruiz et al., 2025, preprint | full text | Local neighbourhood information does not necessarily help (slide splits) |
| bioRxiv doi:10.1101/2022.04.25.489397 | Hist2ST, Zeng et al., 2022 | full text | Leave-one-section-out; removing the neighbour module costs about 2% relative |

Abstract-only or not relevant to the four directions: arXiv:2406.06393 (STimage-1K4M, no prediction benchmark), arXiv:2508.01490 (HESCAPE), arXiv:2501.15598 (Stem), arXiv:2306.01859 (BLEEP), arXiv:2407.08216 (mclSTExp), doi:10.1093/bib/bbad464 (THItoGene), doi:10.1101/2021.11.28.470212 (HisToGene), doi:10.1038/s41551-020-0578-x (ST-Net), doi:10.1101/2025.02.09.25321567 (DeepSpot), doi:10.1038/s41467-025-66691-y (MISO), arXiv:2603.15967 (kidney FM benchmark, ridge only, UNI2-h best), arXiv:2507.07860 (THUNDER, no expression task), arXiv:2502.06750 (Patho-Bench, no expression task).

Not retrieved: DeepSpot full text, THItoGene full text, ST-Net full text, SEQUOIA (doi:10.1038/s41467-024-54182-5), MISO full text, arXiv:2607.22861, STP-Bench's figure values, DeepPT and EGN/EGGN (DOIs not obtained), PH2ST (arXiv:2503.16816), GHIST (doi:10.1038/s41592-025-02795-z). None is needed for the choice below; the list goes to Nicolas only if a later step needs one.

## What the track takes from it

- **Encoder.** UNI2-h (`uni_v2`) is within about 0.01 of the best frozen encoder on HEST-Benchmark, and Virchow2 is slightly below it. Of the encoders on Longleaf, none is expected to be clearly stronger, though an ensemble of encoders is untested in this literature.
- **Head.** Gradient boosting and random forests lose to PCA + ridge; an MLP has clean evidence only at single-cell level; a ridge without PCA needs a tuned $\lambda$. Round 10's head uses $\alpha = 100/(256 \cdot n_{\text{genes}})$, close to no shrinkage, so a ridge with $\alpha$ tuned by inner donor-grouped CV is a fair, cheap arm.
- **More donors.** No controlled evidence; pooling across cancer types often hurt (STP-Bench).
- **Spatial context.** The best-supported direction under patient-held-out evaluation, about +0.01 to +0.03 Pearson over a linear probe on frozen FM features, with published failures on weak encoders. No paper isolates the simplest version (a ridge on the spot's embedding concatenated with its neighbours' mean against a ridge on the spot alone), which the track can test directly.
