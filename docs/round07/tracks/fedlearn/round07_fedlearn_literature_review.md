# Round 7, the federated learning track, literature review

Living document of the execution session, first written on 13 October 2026 for the F2 gate. It is frozen at the round's close. It answers the questions of section 2.2 of `docs/round07/i01/fedlearn/round07_fedlearn_track.md`, gives a verdict on each route and candidate concept, and states what the search found on novelty. It does not choose the paper's framing and does not take a side between the advisors.

## 1. How this review was made, and how to read it

**Sources and search.** Seven theme sub-agents searched PubMed, Europe PMC (which also covers bioRxiv and medRxiv), arXiv, a general web search, and the proceedings of NeurIPS, PMLR, OpenReview and MICCAI on 13 October 2026, following the protocol in `docs/round07/tracks/fedlearn/round07_fedlearn_plan.md`. AAAI pages were seen through the web search only. The merged search log is `results/round7/fedlearn/F1_search/search_log.csv`, and the number of query identifiers each theme ran on each kind of source is in `results/round7/fedlearn/F1_search/search_coverage_by_theme_and_source.csv`. The merged evidence table is `results/round7/fedlearn/F1_search/evidence_table.csv`. Every paper cited here has a row there, and is cited by its row number (P001 and so on). The table gives each paper's identifier, title, authors, year, venue and read level. Section 13 lists the identifiers of every paper cited.

**Core papers and read levels.** The lead chose the core papers, those an answer or a verdict rests on, and re-verified each record against Crossref, PubMed, Europe PMC, arXiv or a proceedings page (columns `lead_verified_from` and `lead_check`). A read level of "full text" means the full text was opened and its methods, results and discussion were read where they bear on the questions, not every line. Where a paper was read in a preprint version, the table says so. A claim that rests on a paper read at the abstract level says "(abstract)" beside the citation. Three reader sub-agents read the core papers that the theme sub-agents had left at abstract level, and their notes are in `results/round7/fedlearn/F1_search/reading/`.

**Grades.** Each answer carries one of the grades of the instruction. **Strong** means several independent studies on this problem or one very close to it. **Moderate** means one study on this problem, or several on a close neighbour. **Weak** means only adjacent problems, or one small study. **None found** names the search that found nothing.

**Scope of every absence.** Every statement that something was not found holds within the sources and queries in the search log, and only there.

## 2. Q1. Is accuracy limited by data?

**Answer.** Not established. No study was found that measures how the accuracy of predicting spatial expression from histology changes with the number of training patients, slides or centers for a head on frozen foundation-model embeddings. The indirect evidence points more to limits in the representation and in the within-slide signal than to a shortage of paired data, but it does not exclude a data effect.

**Evidence.** All numbers in this section are in the `summary` column of `results/round7/fedlearn/F1_search/evidence_table.csv`, or in the reading notes named beside them.

- *Direct curves for spatial prediction.* None was found (queries T3-q01, T3-q10, T3-q11 on every source). HEST-1k [P123], STPath [P125], STFlow [P126], HESCAPE [P127] and the benchmark of Wang et al. [P124] report none. The nearest result is VOICE [P378], a vision and expression foundation model on Xenium cells, where in the evaluation within slides, 75 training slides beat 24 on every metric, by 0.013 to 0.047, although on a held-out ovary slide the larger model did worse (`results/round7/fedlearn/F2_audit/citation_audit.csv`). That is a two-point comparison in slides, for a model trained end to end, with a per-gene Pearson over all cells of a slide, not the project's within-slide metric over spots.
- *Bulk prediction does show a data effect.* SEQUOIA [P130] reports that the number of well-predicted genes tracked training-set size across 16 cancers, and that downsampling BRCA to 20, 30 and 40% lowered every metric. HE2RNA [P129] split TCGA colorectal patients between an expression-pretraining hospital and an MSI-training hospital, in proportions from 388 against 78 patients to all patients in the MSI hospital (`results/round7/fedlearn/F2_audit/citation_audit.csv`). Bulk targets are slide-level, so these results do not transfer directly to within-slide accuracy.
- *Encoder scale matters little for expression.* In HEST-1k [P123] the benchmark score rose with log model size (R=0.81) but only weakly with the number of pretraining patches (R=0.48, P=0.13). Among seven top encoders pretrained on about 21K to 3.1M slides, Gustafsson et al. [P157] found TCGA-BRCA PAM50 correlations between 0.571 and 0.596.
- *The within-slide part is the hard part.* Nguyen et al. [P134] decompose error on HEST-1k cohorts into slide-level and within-slide parts, find that gene-average differences carry much of the aggregate score, and show that a closed-form affine head reaches the best overall results. If that holds, more data for the same head would buy little within-slide accuracy, and the bottleneck David described sits in the representation.
- *Transfer across cohorts is weak.* Models trained on one breast subtype generalised poorly to others in Wang et al. [P124]. Retrieval across cancers fell on unseen TCGA cohorts, and 5% of target pairs (8 samples) lifted LUAD from 10.7% to 43.5% R@10 in Winter et al. [P135]. Gustafsson et al. [P157] report 0.443 mean PAM50 Pearson when a TCGA-BRCA model was applied unchanged to SCAN-B. A small amount of target-center data closing a large gap is what a federation could supply.
- *Omics federation gains little from more studies.* In SwarmMAP [P005], training on 1, 2 or 3 heart studies gave weighted F1 0.947, 0.957 and 0.958 (reading notes, `results/round7/fedlearn/F1_search/reading/R3/reading_notes.csv`).
- *Theory.* Zhao, Wang and Lin [P235] show that when parameters differ across devices, pooling more devices can raise error, and that with strong differences local data alone is best.

**Grade.** Weak. No study addresses the question directly, and the indirect evidence comes from bulk prediction, from encoder scaling and from other modalities.

## 3. Q2. What data do centers hold?

**Answer.** Paired H&E and spatial transcriptomics exists in public pools of about a thousand slides, which overlap. Paired H&E and bulk RNA-seq exists at the scale of thousands of patients in TCGA and in clinical cohorts. H&E alone exists at the scale of hundreds of thousands to millions of slides inside single health systems. A federation could use the first for a supervised head, the second for weak supervision at the slide level, and the third only for self-supervised pretraining of an encoder.

**Evidence.** Numbers are from the `summary` column of `results/round7/fedlearn/F1_search/evidence_table.csv` and from `results/round7/fedlearn/F1_search/reading/R3/reading_notes.csv`.

- *Paired H&E and spatial.* HEST-1k [P123] has 1,229 samples from 153 cohorts in its NeurIPS version, with 2.1 million expression and morphology pairs. STimage-1K4M [P131] has 1,149 slides and 4,293,195 spots, 86.5% of the slides Visium, with brain and breast over-represented (reading notes). OmiCLIP [P132] (abstract) curated 2.2 million pairs, STORM [P159] 632 sections (a count from its main text, which the citation audit opened), STHELAR [P142] (abstract) 31 Xenium sections, and SpaRED [P392] (abstract) 26 public spatial transcriptomics datasets. These pools draw on the same public studies and were not de-duplicated by the search.
- *Paired H&E and bulk RNA-seq.* HE2RNA [P129] used 8,725 TCGA patients over 28 cancer types, and SEQUOIA [P130] 7,584 tumours with external validation on 1,368. BiSCALE [P164] (abstract) combined 2,109 bulk samples with 141,000 spots.
- *H&E alone.* Virchow [P147] was pretrained on about 1.5 million slides from one cancer center, Virchow2 [P152] (abstract) on 3.1 million slides, and Prov-GigaPath [P156] (abstract) on 171,189 slides from a network of 28 cancer centers. The last is an existing multi-site health network pooling H&E centrally.
- *How each enters a model.* A supervised head on paired spots is HEST-bench's design [P123]. Weak supervision from slide-level expression is HE2RNA and SEQUOIA [P129, P130], and single-cell prediction from spot-level data is sCellST [P141] (abstract). Self-supervised pretraining on H&E is the route of Virchow and Prov-GigaPath [P147, P156 (abstract)]. No federated version of the second or third was found for expression (T3 queries q01 to q09 and q21).

**Grade.** Moderate. The public pools are documented. How much paired data sits in clinical centers outside public archives is not documented in any source found.

## 4. Q3. What would be federated?

**Answer.** Four routes have different evidence. A head on frozen embeddings fitted from summary statistics in one round is exact in algebra and has close precedents in classification, but no application to expression. An iterative nonlinear head is the best-evidenced route in computational pathology, for classification. Parameter-efficient fine-tuning of an encoder is evidenced in radiology, not in pathology at real multi-site scale. Federated pretraining of an encoder is evidenced in ultrasound and MRI, not in pathology. Numbers are from the `summary` column of `results/round7/fedlearn/F1_search/evidence_table.csv`.

**Route 1, a head from summary statistics in one round.** What leaves a site is the count, the sums of embeddings and expression, and the cross-products of section 2.3 of the instruction. A site needs only a pass over its embeddings, and there is one round. The exactness of the pooled fit is algebra. Lin and Zeng [P205] show that combining maximum-likelihood summaries loses no asymptotic efficiency when the effect is shared, and that a shared nuisance parameter such as a common intercept needs the joint summaries (reading notes `results/round7/fedlearn/F1_search/reading/R2/reading_notes.csv`). DataSHIELD [P200] fits generalised linear models at the data's home site with only summaries returned, equal to the pooled fit, though iteratively rather than in one round. DLMM [P186] and Limpoco et al. [P188] fit linear mixed models exactly from per-site cross-products or from means, covariances and sizes sent once. Closed-form heads on frozen features have been federated for classification. FedDBL [P050] fits a broad-learning head on frozen pathology features in one round for histopathological tiles, cutting communication from 4.6 GB to 276.5 KB per client. Fed3R [P222] fits a ridge classifier from aggregated client statistics. AFL [P223] gives an analytic solution identical for any partition of the data. A single-author preprint [P225] solves federated ridge regression exactly from summed Gram matrices, on synthetic data only, and two further preprints use additive sufficient statistics on frozen backbones, one to keep a ridge head exact under requests to add or delete data [P406] (abstract), and one to aggregate a least-squares head after local prompt tuning [P407] (abstract). Both test on image and text benchmarks, not pathology. The principal component basis can be formed exactly from the summed second moments. The federated PCA papers found are approximate or streaming [P179, P180], or lossless by masking [P258]. None found forms the basis from summed centred second moments and then fits a head, although that is the same additive algebra.

**Route 2, an iterative nonlinear head.** Model updates leave a site every round, a site needs a GPU or a strong CPU, and there are tens to hundreds of rounds. In federated attention-based multiple-instance learning on three simulated TCGA sites, Lu et al. [P015] report federated AUC below centralised training (about 0.86 against 0.92 for breast subtyping, about 0.976 against 0.985 for kidney) and above single-site models. Saldanha et al. [P014] ran swarm learning across three countries, and for BRAF in QUASAR local models reached AUROC 0.707 to 0.736, a merged model 0.757 and the swarm model 0.763. Adnan et al. [P018] report 0.823 for federated and differentially private federated training against 0.839 pooled. Cong et al. [P017] federate only 0.4K to 1.02K prompt parameters per round on frozen patch embeddings and gain 0.11 to 0.13 mean AUC over local training (`results/round7/fedlearn/F2_audit/citation_audit.csv`). Ogier du Terrail et al. [P077] trained behind hospitals' firewalls and improved over local models (AUC 0.60 against 0.57 on one cohort). The version read is the medRxiv preprint, which describes two hospitals. For expression, the only federated study is PPML-Omics [P001]. In its published Table 2, federated ST-Net had a test MSE of 0.93120 against 0.90904 centrally, so federation without noise was slightly worse (reading notes `results/round7/fedlearn/F1_search/reading/R2/reading_notes.csv` and `results/round7/fedlearn/F1_search/reading/R3/reading_notes.csv`).

**Route 3, parameter-efficient fine-tuning of the encoder.** Low-rank or adapter updates leave a site every round, and a site needs a GPU. Alkhunaizi et al. [P052] report about 4% accuracy lost per ten-fold cut in exchanged parameters for vision transformers on out-of-domain, non-identical medical tasks, and about 0.5% for in-domain tasks (`results/round7/fedlearn/F2_audit/citation_audit.csv`). Federated LoRA on BiomedCLIP across four chest X-ray cohorts [P093] raised mean AUC from 0.687 to 0.802 against 0.812 pooled. CoM3eT [P094] trained under 2.5% of parameters and reached performance comparable to pooled data across hospitals. No federated fine-tuning of a pathology foundation model at real multi-site scale was found. Centrally, fine-tuning pathology encoders for expression gained little. SEAL [P379] improved all five encoders on HEST-Bench, by at most 1.33% average PCC, and the best baseline, UNIv2, went from 0.4142 to 0.4186 (`results/round7/fedlearn/F2_audit/citation_audit.csv`), and Filiot et al. [P385] raised mean HEST Pearson from 0.398 to 0.411.

**Route 4, federated pretraining.** Encoder updates leave a site every round, and a site needs substantial GPU capacity. UltraFedFM [P102] pretrained an ultrasound model across 16 clients in 9 countries on 1,015,754 unlabelled images. No pathology example was found. Since encoder pretraining scale bears weakly on expression accuracy [P123, P157], this route has the least direct support for the problem.

**Real deployments.** FeTS [P044] ran across 71 sites on six continents, EXAM [P045] across 20 institutes, and TheODen [P048] across German hospitals behind firewalls. Schoenpflug et al. [P047] document the network restrictions (an open server port, solved by hosting the server on AWS) and the IT effort of a federation of three clients spanning four networks in four countries. The review of 15 pathology federations by Schoenpflug et al. [P046] finds federated models on par with centralised ones (within 2%) or 2 to 6% below them, and privacy-preserving variants 0.2 to 6% below (`results/round7/fedlearn/F2_audit/citation_audit.csv`).

**Grade.** Strong for the exactness of route 1 as statistics, and for route 2 in pathology classification. None found for any route applied to expression from histology, other than PPML-Omics for route 2.

## 5. Q4. Heterogeneity across centers

**Answer.** Methods exist for non-identical data, personalisation and batch effects in general and in omics, and scanner and site signatures in pathology embeddings are well documented. No federated method for centers that measure different gene panels was found. For a linear head, center-level differences can be handled by center-specific intercepts or random effects, for which exact one-round methods exist.

**Evidence.** Numbers are from `results/round7/fedlearn/F1_search/evidence_table.csv` and the reading notes named.

- *Generic methods.* FedProx [P266] adds a proximal term and reports a 22% average accuracy gain over FedAvg under strong heterogeneity, against FedAvg with dropped stragglers rather than pooled training (`results/round7/fedlearn/F1_search/reading/R3/reading_notes.csv`). SCAFFOLD [P267] (abstract) corrects client drift with control variates. FedBN [P268] keeps batch normalisation local, which targets scanner-type feature shift, and lost to FedAvg at one of four neuroimaging sites (`results/round7/fedlearn/F1_search/reading/R2/reading_notes.csv`). The survey of Kairouz et al. [P273] gives the taxonomy of non-identical data and the case for personalisation in the cross-silo setting.
- *Pathology.* Frozen foundation-model embeddings carry scanner signatures. Thiringer et al. [P289] found that most of 14 encoders cluster by scanner on 384 breast cancer slides scanned on five devices, that predicted probabilities shift between scanners, and that larger or newer models were not more robust (`results/round7/fedlearn/F1_search/reading/R2/reading_notes.csv`). Howard et al. [P355] and Kömen et al. [P389] show tissue-source-site signatures in TCGA features. FedSDA [P042] aligns stain distributions across clients and raised AUROC on a six-scanner prostate set from 78.99 to 90.38 under FedAvg, against federated baselines only (`results/round7/fedlearn/F1_search/reading/R2/reading_notes.csv`). The pathology review [P046] reports gains of 4 to 20% from domain alignment against 0 to 3% from changes to aggregation.
- *Omics batch effects.* Garst et al. [P292] found that a federated network on three acute myeloid leukaemia cohorts failed when one cohort was RNA-seq and two microarray until each gene was standardised locally (`results/round7/fedlearn/F1_search/reading/R3/reading_notes.csv`, preprint version). fedRBE [P006] federates limma's batch correction for non-identical feature sets. Its first arXiv version reports agreement with the centralised result to within 3.6e-13 (abstract of v1), and the current version reports maximum differences of at most 5e-13 on simulated data, as the citation audit found (`results/round7/fedlearn/F2_audit/citation_audit.csv`). Federated Harmony [P004] integrates spatial expression batches from summaries.
- *Partial overlap.* Ayme et al. [P287] (abstract) fit linear prediction when centers record different covariates, from aggregated covariance blocks. The mismatch is in inputs, not in response genes. No method for response genes that differ across centers was found (T5 queries q03, q04, q09; T1 query q10; T6 query q10).
- *Platforms.* Janesick et al. [P294] measured the same breast tumour by Visium (18,536 targeted genes) and Xenium (313 genes), with Xenium's median per-gene sensitivity 8.4 times Visium's on the panel genes (`results/round7/fedlearn/F1_search/reading/R2/reading_notes.csv`). A Visium site and a Xenium site therefore differ in which genes they measure and in counts per unit area.
- *Center effects in a linear model.* DLMM [P186] and Limpoco et al. [P188] give exact one-round mixed models with site random effects. FETA [P209] borrows from source sites to improve a target population's model. Jackson et al. [P293] (abstract) report that federated gains in a six-site HIV consortium varied with site size and heterogeneity.

**Grade.** Moderate for scanner and site effects in pathology embeddings and for generic heterogeneity methods. None found for differing gene panels in expression prediction.

## 6. Q5. Privacy and governance

**Answer.** H&E slides can be linked to their patient, expression profiles can be linked to genotypes, and repeated covariance queries can reconstruct individual records exactly. Gradient inversion is documented in medical imaging and is weakened by realistic training. Differential privacy costs a few points of accuracy at moderate budgets in imaging, and for linear regression its cost falls as sample size grows. Large multi-site federations in medical imaging have run under data-sharing agreements and analysis at the data's home site.

**Evidence.** Numbers are from `results/round7/fedlearn/F1_search/evidence_table.csv` and the reading notes named.

- *What is identifying in H&E.* Ganz et al. [P063] matched slides to their source patient within a cohort. The arXiv version reports F1 of 50.16%, 52.30% and 62.31%, and the published abstract reports up to 80.1%, so which version a number comes from must be stated. Site signatures are learnable from TCGA slides [P355].
- *What is identifying in expression and in aggregates.* Homer et al. [P315] showed that a person's presence in a DNA pool can be detected from pooled allele frequencies when they contribute about 1% or less (`results/round7/fedlearn/F1_search/reading/R3/reading_notes.csv`). Sadhuka et al. [P321] link expression profiles to genotypes through eQTLs with higher accuracy than earlier models in datasets of up to 22,000 individuals (abstract). Sankararaman et al. [P316] (abstract) bound the power of such membership tests.
- *Attacks on shared covariances.* Huth et al. [P329] reconstructed a site's individual values exactly (maximum error 2e-12) from repeated mean and covariance queries with chosen vectors, on a DataSHIELD test set, and zero-mean noise was averaged away by repetition (`results/round7/fedlearn/F1_search/reading/R2/reading_notes.csv`). The threat model is an analyst who can send arbitrary queries. A single fixed release of each site's sums is not the interface attacked, which is the reader's reading and not a claim of the paper.
- *Attacks on gradients.* Hatamizadeh et al. [P062] show that earlier gradient inversion attacks fail when clients update batch-normalisation statistics over several batches. Ziegler et al. [P344] reconstructed chest X-rays from federated updates. PPML-Omics [P001] blocks an iDLG attack on ST-Net with its decentralised differential privacy (`results/round7/fedlearn/F1_search/reading/R2/reading_notes.csv`).
- *The cost of differential privacy.* Adnan et al. [P018] report external accuracy 0.707 with differential privacy against 0.741 federated and 0.768 pooled at epsilon 2.90. Ziegler et al. [P344] report a global AUC of 0.937 at epsilon 6, matching the non-private model, with AUC about 0.03 lower on clients holding large shares of one dataset (`results/round7/fedlearn/F2_audit/citation_audit.csv`). Their reconstruction attack succeeded on models with frozen batch-normalisation layers. In PPML-Omics [P001] the spatial MSE was 0.98808 at a total budget of 1 and 0.93005 at 5, against 0.90904 centrally (published Table 2). For regression from sufficient statistics, AdaSSP [P339] perturbs the cross-products once and its excess error shrinks as the number of samples times epsilon squared grows, on 36 UCI datasets whose main-text examples have at most 77 dimensions (`results/round7/fedlearn/F1_search/reading/R3/reading_notes.csv`). Tramèr and Boneh [P342] find linear models on fixed features beat private deep networks at moderate budgets.
- *Governance in practice.* FeTS [P044] and EXAM [P045] ran across 71 and 20 sites. EUCAIM [P113] uses data-sharing and transfer agreements, a data access committee and a federated processing environment. DataSHIELD [P200] runs analysis at the data's home site. Rieke et al. [P043] set out the regulatory and technical issues. No published data-use agreement template for histology with expression was found (T6 queries q07 and q08).

**Grade.** Moderate for the attacks and the cost of differential privacy in imaging and genomics. None found for attacks on, or the cost of privacy for, foundation-model embeddings or spatial expression specifically (T6 queries q05, q10, q14).

## 7. Q6. Prior art

**Answer.** Within the sources and queries of the search log, one paper federates the prediction of expression from histology, PPML-Omics [P001]. It trains ST-Net end to end on 23 breast cancer patients with decentralised differential privacy and reports MSE rather than a correlation. No paper was found that fits a head on frozen pathology foundation-model embeddings from per-center summary statistics, that handles centers with different gene panels, or that federates a reference database of embeddings and expression.

**Evidence.** privateST [P002] encrypts inference on a locally trained model and is not federated learning. Its average PCC over 100 genes was 0.317 against 0.324 unencrypted. Federated and swarm learning in single-cell and spatial omics is well developed, for cell-type annotation (scFed [P003], SwarmMAP [P005]), batch correction (FedscGen [P007] (abstract), fedRBE [P006] (abstract), Federated Harmony [P004]) and spatial clustering of expression without images (INFL [P023]). Federated computational pathology addresses classification, response prediction and survival [P014, P015, P017, P018, P077, P099]. Swarm learning has been applied to blood transcriptomes [P013]. Forward searches from PPML-Omics, scFed, FedscGen and Federated Harmony found no federated histology-to-expression paper (T1 notes in `results/round7/fedlearn/F1_search/fragments/T1/notes.md`).

**Grade.** Strong as a statement about what the search found, since seven themes and their forward searches converged on the same single paper. It remains bounded by the sources searched.

## 8. Q7. Statistical methods for a biostatistics methods paper

**Answer.** The methods most suited are those that are exact or nearly exact from one round of summaries. Exact sufficient-statistic fits of linear models and linear mixed models, exact federated principal components from summed second moments, and communication-efficient estimators for the nonlinear case are all established. What is not established is inference for a prediction head whose error has a center-level component.

**Evidence.** Numbers are from `results/round7/fedlearn/F1_search/evidence_table.csv`.

- *Exact fits from summaries.* Lin and Zeng [P205], DLMM [P186] and Limpoco et al. [P188] in one round, and DataSHIELD [P200] iteratively, since its generalised linear models return summaries at each iteration.
- *Communication-efficient estimation.* Jordan, Lee and Yang [P171] use a surrogate likelihood from one site's data and the others' gradients to beat simple averaging in a few rounds. ODAL [P183] (abstract) reaches relative bias below 0.1% against pooled logistic regression in simulations when second-order gradients are sent. Dobriban and Sheng [P173] show that one-step weighted averaging of local least-squares fits raises estimation error and interval length considerably while raising prediction error much less, which argues for summing statistics rather than averaging fits.
- *Federated principal components.* Fan et al. [P179] aggregate local eigenspaces at the whole-sample rate when there are not too many machines. Grammenos et al. [P180] give a streaming, differentially private version. FedSVD [P258] is lossless by masking.
- *Transfer and heterogeneity.* FETA [P209] borrows from source sites for an under-represented target, and Zhao, Wang and Lin [P235] give the trade-off between aggregation variance and heterogeneity bias.
- *Inference.* None of the papers found treats valid uncertainty for a prediction head with center-level error. The project's rounds 4 and 5 showed that what predictions buy under cluster sampling is governed by their accuracy at the cluster level (`docs/round04/tracks/ppi/round4_ppi_theory.md`, section 2), which is the open problem here.

**Grade.** Strong for exact one-round linear and mixed-model fits. None found for inference on a federated prediction head with center-level error.

## 9. Q8. The alternatives

**Answer.** Each alternative has some evidence and none has evidence that it beats a head on frozen embeddings for within-slide accuracy at scale. The routes are compared here on evidence only.

**Evidence.** Numbers are from `results/round7/fedlearn/F1_search/evidence_table.csv` and from `docs/round06/README.md`.

- *A textual knowledge base.* No paper was found that applies a text knowledge base or cheatsheet to histology-to-expression prediction (T7 queries q03, q04, q10). The nearest relatives work on reasoning tasks, such as Dynamic Cheatsheet [P393]. The project's own evidence is round 6. On three held-out kidney cancer patients, every rubric-bound cheatsheet from 256 to 65,536 bytes beat the zero-shot baseline but none reached the `uni_v2` head fitted on the same spots, which scored 0.184 (`docs/round06/README.md`, "What the round established"). Round 6 used one model and one trial per cell, so it tested a small version of the route, not David's proposal at scale.
- *Retrieval in a joint embedding space.* BLEEP [P163] predicts from the nearest reference spots, on one liver dataset. In VOICE [P378], fusing retrieval with direct regression raised macro PCC from 0.3810 to 0.3904 in its 24-slide model. HESCAPE [P127] found that contrastive image and expression pretraining lowered direct expression prediction relative to plain encoders and named batch effects as the cause.
- *Scaling public data centrally.* STPath [P125] pools HEST-1k and STimage-1K4M and does not isolate a data-size effect. VOICE [P378] is the only data-size comparison found (section 2).
- *Better or fine-tuned encoders.* SEAL [P379] raised the best baseline encoder from 0.4142 to 0.4186 Pearson on HEST-Bench, and Filiot et al. [P385] raised the mean from 0.398 to 0.411 (section 4, and `results/round7/fedlearn/F2_audit/citation_audit.csv`).

**Grade.** Weak for every alternative, as for federated learning itself on this problem.

## 10. Q9. How to show viability with public data

**Answer.** Centers can be simulated from studies in HEST-1k and STimage-1K4M, or from TCGA tissue source sites for bulk targets. Evaluation should keep a center out of training entirely, as preserved-site cross-validation does, and also hold out donors within centers. Because the project's metric removes slide-level offsets, a center offset in the predictions does not change it, so a federation should be judged on the within-slide metric and on a pooled correlation beside it.

**Evidence.** Numbers are from `results/round7/fedlearn/F1_search/evidence_table.csv` and `results/round7/fedlearn/F1_search/reading/R3/reading_notes.csv`.

- *Stand-ins for centers.* HEST-1k [P123] and STimage-1K4M [P131] are assembled from many studies, and STimage-1K4M's authors limited pooled training to one tissue because of batch effects across datasets (reading notes). HEST-1k has no laboratory contrast with disease held fixed (`docs/reference/methods_and_state_of_play.md`, section 23), so any center simulated from its labs mixes lab with study and disease. SpaRED [P392] (abstract) curates 26 public spatial transcriptomics datasets.
- *Evaluation.* Howard et al. [P355] show that standard cross-validation in TCGA inflates accuracy because sites leak, and propose splits that never share a site between training and validation. Kömen et al. [P389] show site signatures survive in foundation-model features.
- *Metric.* STRank [P401] (abstract) argues for learning relative rather than absolute expression because absolute values carry batch effects. Nguyen et al. [P134] show that slide-level gene means carry much of an aggregate score.

**Grade.** Moderate for leave-one-site-out evaluation, from TCGA. Weak for simulating centers from spatial data, since no paper was found that does it.

## 11. The routes and the candidate concepts, with a verdict on each

| route or concept | verdict | reasons | papers |
|---|---|---|---|
| Route 1, one-round head from summary statistics | conditional | exact in algebra and established for linear and mixed models, with closed-form-head precedents on frozen features; conditional on Q1 (whether more centers raise within-slide accuracy, not established) and on releasing the sums under a fixed interface with secure aggregation or noise | P050, P186, P188, P200, P205, P222, P223, P225, P329, P339 |
| Route 2, iterative nonlinear head | conditional | federated performance near pooled in pathology classification; the one expression study found federation without noise slightly worse than central; conditional on site compute and on evidence for expression | P001, P014, P015, P017, P018, P077 |
| Route 3, parameter-efficient fine-tuning | not supported for a first paper | evidence is from radiology; central fine-tuning gained little on HEST-Bench (section 4) | P052, P093, P094, P379, P385 |
| Route 4, federated pretraining | not supported for a first paper | no pathology example; encoder scale bears weakly on expression accuracy | P102, P123, P157 |
| C1, one-shot federated head with center intercepts | conditional | as route 1; center-specific intercepts are exact one-round random or fixed effects; the within-slide metric is unaffected by center intercepts, so their value shows only in a pooled metric | P186, P188, P205, P222, P329, P339, P134 |
| C2, iterative federation of a nonlinear head or adapters | conditional | as routes 2 and 3 | P014, P015, P017, P052, P093 |
| C3, weak supervision from H&E and bulk RNA-seq | conditional | bulk data are abundant and bulk prediction shows a data-size effect; no federated version found; conditional on spatial signal being learnable from slide-level targets for a within-slide metric | P129, P130, P141, P164 |
| C4, a federated reference database | not supported as privacy-preserving | retrieval adds little over direct regression in the one study found; answering nearest-neighbour queries releases individual expression records, and no privacy analysis of such a database was found | P163, P378, P329 |

## 12. The novelty statement

Within the sources and queries in the search log (`results/round7/fedlearn/F1_search/search_log.csv`, themes T1, T2, T5 and T6, run on 13 October 2026), no paper was found that fits a prediction head for spatial gene expression on frozen pathology foundation-model embeddings from per-center summary statistics, or that handles centers measuring different gene panels in expression prediction. The only federated study of expression prediction from histology found is PPML-Omics [P001], which trains an end-to-end network with differential privacy. The algebra of fitting a ridge or closed-form head from summed statistics is not new. It is established for linear and mixed models [P186, P188, P200, P205] and has been used for ridge and closed-form heads on frozen features, mostly for classification [P050, P222, P223, P406 (abstract), P407 (abstract)]. A claim of novelty for C1 can therefore rest only on its application to expression from histology and on what is learned there, such as the role of center-level error, not on the estimator.

## 13. Identifiers of the papers cited

Each paper is a row of `results/round7/fedlearn/F1_search/evidence_table.csv`.

| paper | first author, year | title | venue | identifier | read level |
|---|---|---|---|---|---|
| P001 | Juexiao Zhou, 2024 | PPML-Omics: A privacy-preserving federated machine learning method protects patients’ privacy in omic data | Science Advances, vol 10, issue 5, eadh8601 | `10.1126/sciadv.adh8601` | full text |
| P002 | Hakin Kim, 2026 | privateST: a feasible framework for privacy-preserving spatial transcriptomics prediction from histopathology images | Scientific Reports, vol 16, issue 1, 25330 | `10.1038/s41598-026-55961-4` | full text |
| P003 | Shuang Wang, 2023 | scFed: federated learning for cell type classification with scRNA-seq | Briefings in Bioinformatics | `10.1093/bib/bbad507` | full text |
| P004 | Ruizhi Yuan, 2025 | Harmony-based data integration for distributed single-cell multi-omics data | PLOS Computational Biology, vol 21, issue 9, e1013526 | `10.1371/journal.pcbi.1013526` | full text |
| P005 | Oliver Lester Saldanha, 2026 | SwarmMAP: swarm learning for decentralized cell type annotation in single cell sequencing data | npj Systems Biology and Applications, vol 12, issue 1, 41 | `10.1038/s41540-026-00667-6` | full text |
| P006 | Yuliya Burankova, 2024 | Batch effects can impair federated learning in multi-center omics studies | arXiv | `arXiv:2412.05894` | abstract only |
| P007 | Mohammad Bakhtiari, 2025 | FedscGen: privacy-preserving federated batch effect correction of single-cell RNA sequencing data | Genome Biology, vol 26, issue 1, 216 | `10.1186/s13059-025-03684-6` | abstract only |
| P013 | Stefanie Warnat-Herresthal, 2021 | Swarm Learning for decentralized and confidential clinical machine learning | Nature, vol 594, issue 7862, 265-270 | `10.1038/s41586-021-03583-3` | full text |
| P014 | Oliver Lester Saldanha, 2022 | Swarm learning for decentralized artificial intelligence in cancer histopathology | Nature Medicine, vol 28, issue 6, 1232-1239 | `10.1038/s41591-022-01768-5` | full text |
| P015 | Ming Y. Lu, 2022 | Federated learning for computational pathology on gigapixel whole slide images | Medical Image Analysis, vol 76, 102298 | `10.1016/j.media.2021.102298` | full text |
| P017 | Cong Cong, 2026 | Flexible and scalable federated learning with deep feature prompts for digital pathology | npj Digital Medicine, vol 9, issue 1, 578 | `10.1038/s41746-026-02710-6` | full text |
| P018 | Mohammed Adnan, 2022 | Federated learning and differential privacy for medical image analysis | Scientific Reports, vol 12, issue 1, 1953 | `10.1038/s41598-022-05539-7` | full text |
| P023 | Rongyu Zhang, 2026 | Key-Embedded Privacy for Decentralized AI in Biomedical Omics | arXiv | `arXiv:2603.28334` | full text |
| P042 | Cheng-Chang Tsai, 2025 | FedSDA: Federated Stain Distribution Alignment for Non-IID Histopathological Image Classification | arXiv preprint | `2511.12044` | full text |
| P043 | Rieke N, 2020 | The future of digital health with federated learning | NPJ digital medicine | `10.1038/s41746-020-00323-1` | full text |
| P044 | Pati S, 2022 | Federated learning enables big data for rare cancer boundary detection | Nature communications | `10.1038/s41467-022-33407-5` | full text |
| P045 | Dayan I, 2021 | Federated learning for predicting clinical outcomes in patients with COVID-19 | Nature medicine | `10.1038/s41591-021-01506-3` | full text |
| P046 | Lydia A. Schoenpflug, 2024 | A review on federated learning in computational pathology | Computational and Structural Biotechnology Journal 23:3938-3945 | `10.1016/j.csbj.2024.10.037` | full text |
| P047 | Schoenpflug LA, 2025 | Navigating real-world challenges: A case study on federated learning in computational pathology | Journal of pathology informatics | `PMC12357140` | full text |
| P048 | Babendererde N, 2026 | Nationwide federated learning for histopathology: secure deployment across Germany behind firewalls | NPJ digital medicine | `10.1038/s41746-026-02958-y` | full text |
| P050 | Tianpeng Deng, 2023 | FedDBL: Communication and Data Efficient Federated Deep-Broad Learning for Histopathological Tissue Classification | arXiv preprint | `2302.12662` | full text |
| P052 | Naif Alkhunaizi, 2024 | Probing the Efficacy of Federated Parameter-Efficient Fine-Tuning of Vision Transformers for Medical Image Classification | arXiv preprint | `2407.11573` | full text |
| P062 | Hatamizadeh, Ali, 2023 | Do Gradient Inversion Attacks Make Federated Learning Unsafe? | IEEE Transactions on Medical Imaging | `10.1109/TMI.2023.3239391` | full text |
| P063 | Ganz J, 2025 | Re-identification from histopathology images | Medical image analysis | `39316996` | full text |
| P077 | Ogier du Terrail J, 2023 | Federated learning for predicting histological response to neoadjuvant chemotherapy in triple-negative breast cancer | Nature medicine | `36658418` | full text |
| P093 | Sanjaya Poudel, 2026 | Federated LoRA Adaptation of BiomedCLIP Across Four International Chest X-Ray Cohorts | arXiv preprint | `2609.02101` | full text |
| P094 | J. Raphael Schäfer, 2026 | CoM$^3$eT: A foundation model for medical image analysis through federated, multidimensional context integration | arXiv preprint | `2608.16268` | full text |
| P099 | Bao Li, 2023 | Point Transformer with Federated Learning for Predicting Breast Cancer HER2 Status from Hematoxylin and Eosin-Stained Whole Slide Images | arXiv preprint | `2312.06454` | full text |
| P102 | Jiang Y, 2025 | From pretraining to privacy: federated ultrasound foundation model with self-supervised learning | NPJ digital medicine | `10.1038/s41746-025-02085-0` | full text |
| P113 | Martínez RM, 2026 | Building trust and privacy in cross-border health data sharing for European cancer research | Radiology advances | `42006397` | full text |
| P123 | Jaume, Guillaume, 2024 | HEST-1k: A Dataset for Spatial Transcriptomics and Histology Image Analysis | NeurIPS 2024 Datasets and Benchmarks Track (preprint arXiv:2406.16192) | `arXiv:2406.16192` | full text |
| P124 | Wang C, 2025 | Benchmarking the translational potential of spatial gene expression prediction from histology | Nature Communications 2025 | `10.1038/s41467-025-56618-y` | full text |
| P125 | Huang T, 2025 | STPath: a generative foundation model for integrating spatial transcriptomics and whole-slide images | npj Digital Medicine 2025 | `10.1038/s41746-025-02020-3` | full text |
| P126 | Huang, Tinglin, 2025 | Scalable Generation of Spatial Transcriptomics from Histology Images via Whole-Slide Flow Matching | arXiv preprint; ICML 2025 per the arXiv comment | `arXiv:2506.05361` | full text |
| P127 | Gindra, Rushin H., 2025 | A Large-Scale Benchmark of Cross-Modal Learning for Histology and Gene Expression in Spatial Transcriptomics | arXiv preprint (also listed as an ICCV 2025 workshop paper in a web-search result; that page was not opened) | `arXiv:2508.01490` | full text |
| P129 | Schmauch B, 2020 | A deep learning model to predict RNA-Seq expression of tumours from whole slide images | Nature Communications 2020 | `10.1038/s41467-020-17678-4` | full text |
| P130 | Pizurica M, 2024 | Digital profiling of gene expression from histology images with linearized attention | Nature Communications 2024 | `10.1038/s41467-024-54182-5` | full text |
| P131 | Chen J, 2024 | STimage-1K4M: A histopathology image-gene expression dataset for spatial transcriptomics | NeurIPS 2024 Datasets and Benchmarks Track (preprint arXiv:2406.06393) | `PMID:38947920` | full text |
| P132 | Chen W, 2025 | A visual-omics foundation model to bridge histopathology with spatial transcriptomics | Nature Methods 2025 | `10.1038/s41592-025-02707-1` | abstract only |
| P134 | Nguyen, Duc T., 2026 | Is H&E Image-to-Spatial Transcriptomics Simpler Than It Looks? | arXiv preprint | `arXiv:2609.32857` | full text |
| P135 | Winter, Dominik, 2026 | Data-Efficient Multimodal Alignment for Histopathology-based Molecular Prediction | arXiv preprint | `arXiv:2606.29949` | full text |
| P141 | Chadoutaud L, 2026 | sCellST predicts single-cell gene expression from H& E images | Nature Communications 2026 | `10.1038/s41467-025-67965-1` | abstract only |
| P142 | Giraud-Sauveur F, 2026 | STHELAR, a multi-tissue dataset linking spatial transcriptomics and histology for cell type annotation | Scientific Data 2026 | `10.1038/s41597-026-06937-6` | abstract only |
| P147 | Vorontsov E, 2024 | A foundation model for clinical-grade computational pathology and rare cancers detection | Nature Medicine 2024 | `10.1038/s41591-024-03141-0` | full text |
| P152 | Zimmermann, Eric, 2024 | Virchow2: Scaling Self-Supervised Mixed Magnification Models in Pathology | arXiv preprint | `arXiv:2408.00738` | abstract only |
| P156 | Xu H, 2024 | A whole-slide foundation model for digital pathology from real-world data | Nature 2024 | `10.1038/s41586-024-07441-w` | abstract only |
| P157 | Gustafsson, Fredrik K., 2024 | Evaluation and Prognostic Validation of Deep Regression Models for WSI-Based Gene-Expression Prediction | arXiv preprint | `arXiv:2410.00945` | full text |
| P159 | Xiang, Jinxi, 2026 | A Multimodal Foundation Model of Spatial Transcriptomics and Histology for Biological Discovery and Clinical Prediction | arXiv preprint | `arXiv:2604.03630` | abstract only |
| P163 | Xie, Ronald, 2023 | Spatially Resolved Gene Expression Prediction from Histology Images via Bi-modal Contrastive Learning | NeurIPS 2023 (Advances in Neural Information Processing Systems 36) | `https://proceedings.neurips.cc/paper_files/paper/2023/hash/df656d6ed77b565e8dcdfbf568aead0a-Abstract-Conference.html` | full text |
| P164 | Zheng H, 2026 | Multi-Scale Mapping of Gene Expression from Whole-slide Images for Identifying Phenotype-Associated Subpopulations | Advanced Science 2026 | `10.1002/advs.202521151` | abstract only |
| P171 | Jordan, Michael I., 2019 | Communication-Efficient Distributed Statistical Inference | Journal of the American Statistical Association 114(526) | `https://doi.org/10.1080/01621459.2018.1429274` | full text |
| P173 | Dobriban, Edgar, 2021 | Distributed linear regression by averaging | The Annals of Statistics | `https://doi.org/10.1214/20-AOS1984` | full text |
| P179 | Fan, Jianqing, 2019 | Distributed estimation of principal eigenspaces | The Annals of Statistics | `https://doi.org/10.1214/18-aos1713` | full text |
| P180 | Grammenos, Andreas, 2020 | Federated Principal Component Analysis | Advances in Neural Information Processing Systems 33 (NeurIPS 2020) | `1907.08059` | full text |
| P183 | Duan, Rui, 2020 | Learning from electronic health records across multiple sites: A communication-efficient and privacy-preserving distributed algorithm | Journal of the American Medical Informatics Association 27(3) | `https://doi.org/10.1093/jamia/ocz199` | abstract only |
| P186 | Luo, Chongliang, 2022 | DLMM as a lossless one-shot algorithm for collaborative multi-site distributed linear mixed models. | Nature communications | `35354802` | full text |
| P188 | Limpoco, Marie Analiz April, 2025 | Linear Mixed Modeling of Federated Data When Only the Mean, Covariance, and Sample Size Are Available. | Statistics in Medicine (2025) | `39663139` | full text |
| P200 | Gaye, Amadou, 2014 | DataSHIELD: taking the analysis to the data, not the data to the analysis | International Journal of Epidemiology | `https://doi.org/10.1093/ije/dyu188` | full text |
| P205 | Lin, D. Y., 2010 | On the relative efficiency of using summary statistics versus individual-level data in meta-analysis | Biometrika | `https://doi.org/10.1093/biomet/asq006` | full text |
| P209 | Li, Sai, 2023 | Targeting underrepresented populations in precision medicine: A federated transfer learning approach | Annals of Applied Statistics 17(4) | `https://doi.org/10.1214/23-AOAS1747` | full text |
| P222 | Fanì, Eros, 2024 | Accelerating Heterogeneous Federated Learning with Closed-form Classifiers | arXiv preprint (ICML 2024 per arXiv comment) | `2406.01116` | full text |
| P223 | He, Run, 2024 | AFL: A Single-Round Analytic Approach for Federated Learning with Pre-trained Models | arXiv preprint (CVPR 2025 per arXiv comment) | `2405.16240` | full text |
| P225 | Alsulaimawi, Zahir, 2026 | One-Shot Federated Ridge Regression: Exact Recovery via Sufficient Statistic Aggregation | arXiv preprint | `2601.08216` | full text |
| P235 | Xuyang Zhao, 2023 | The Aggregation–Heterogeneity Trade-off in Federated Learning | The Thirty Sixth Annual Conference on Learning Theory | `https://proceedings.mlr.press/v195/zhao23b.html` | full text |
| P258 | Chai, Di, 2021 | Practical Lossless Federated Singular Vector Decomposition over Billion-Scale Data | arXiv preprint | `2105.08925` | full text |
| P266 | Tian Li, 2020 | Federated Optimization in Heterogeneous Networks | MLSys 2020 (arXiv 1812.06127, first posted 2018) | `1812.06127` | full text |
| P267 | Sai Praneeth Karimireddy, 2020 | SCAFFOLD: Stochastic Controlled Averaging for Federated Learning | ICML 2020, PMLR 119 (karimireddy20a) | `1910.06378` | abstract only |
| P268 | Xiaoxiao Li, 2021 | FedBN: Federated Learning on Non-IID Features via Local Batch Normalization | ICLR 2021 | `2102.07623` | full text |
| P273 | Kairouz, Peter, 2021 | Advances and Open Problems in Federated Learning | Foundations and Trends in Machine Learning 14(1-2):1-210 (arXiv:1912.04977) | `10.1561/2200000083` | full text |
| P287 | Alexis Ayme, 2026 | Handling Covariate Mismatch in Collaborative Linear Prediction | arXiv preprint | `2602.02083` | abstract only |
| P289 | Erik Thiringer, 2026 | Scanner-Induced Domain Shifts Undermine the Robustness of Pathology Foundation Models | arXiv preprint | `2601.04163` | full text |
| P292 | Swier Garst, 2025 | A comprehensive experimental comparison between federated and centralized learning | Database 2025:baaf016 | `10.1093/database/baaf016` | full text |
| P293 | Nicholas J. Jackson, 2026 | Federated Learning Performance Depends on Site Variation in Global HIV Data Consortia | medRxiv preprint (2026) | `10.64898/2026.03.25.26349286` | abstract only |
| P294 | Amanda Janesick, 2023 | High resolution mapping of the tumor microenvironment using integrated single-cell, spatial and in situ analysis | Nature Communications 14(1):8353 | `10.1038/s41467-023-43458-x` | full text |
| P315 | Homer, Nils, 2008 | Resolving Individuals Contributing Trace Amounts of DNA to Highly Complex Mixtures Using High-Density SNP Genotyping Microarrays | PLoS Genetics | `10.1371/journal.pgen.1000167` | full text |
| P316 | Sankararaman, Sriram, 2009 | Genomic privacy and limits of individual detection in a pool | Nature Genetics | `10.1038/ng.436` | abstract only |
| P321 | Sadhuka, Shuvom, 2023 | Assessing transcriptomic reidentification risks using discriminative sequence models. | Genome research | `10.1101/gr.277699.123` | abstract only |
| P329 | Huth, Manuel, 2023 | Accessibility of covariance information creates vulnerability in Federated Learning frameworks. | Bioinformatics (Oxford, England) | `10.1093/bioinformatics/btad531` | full text |
| P339 | Wang, Yu-Xiang, 2018 | Revisiting differentially private linear regression: optimal and adaptive prediction & estimation in unbounded domain | arXiv; UAI 2018 per the arXiv comment | `1803.02596` | full text |
| P342 | Tramèr, Florian, 2020 | Differentially Private Learning Needs Better Features (or Much More Data) | arXiv; ICLR 2021 per the arXiv comment | `2011.11660` | full text |
| P344 | Ziegler, Joceline, 2022 | Defending against Reconstruction Attacks through Differentially Private Federated Learning for Classification of Heterogeneous Chest X-Ray Data | arXiv | `2205.03168` | full text |
| P355 | Howard, Frederick M., 2021 | The impact of site-specific digital histology signatures on deep learning model accuracy and bias | Nature Communications | `10.1038/s41467-021-24698-1` | full text |
| P378 | Luo, 2026 | VOICE: A Vision-Omics Foundation Model Integrating Direct and Retrieval-Based Prediction of In-situ Single-Cell Gene Expression | arXiv preprint | `arXiv:2608.08366` | full text |
| P379 | Hemker, 2026 | Towards Spatial Transcriptomics-driven Pathology Foundation Models | arXiv preprint | `arXiv:2602.14177` | full text |
| P385 | Filiot, 2026 | Robustifying pathology foundation models via fine-tuning | arXiv preprint | `arXiv:2607.22861` | full text |
| P389 | Kömen, 2024 | Do Histopathological Foundation Models Eliminate Batch Effects? A Comparative Study | arXiv; AIM-FM workshop at NeurIPS 2024 per the arXiv comment | `arXiv:2411.05489` | full text |
| P392 | Mejia, 2024 | SpaRED benchmark: Enhancing Gene Expression Prediction from Histology Images with Spatial Transcriptomics Completion | arXiv preprint | `arXiv:2407.13027` | abstract only |
| P393 | Suzgun, 2025 | Dynamic Cheatsheet: Test-Time Learning with Adaptive Memory | arXiv preprint | `arXiv:2504.07952` | full text |
| P401 | Nishimura, 2025 | Learning Relative Gene Expression Trends from Pathology Images in Spatial Transcriptomics | NeurIPS 2025 (main conference) | `https://proceedings.neurips.cc/paper_files/paper/2025/hash/7d535a224c8ae54ba75bac0457b6b279-Abstract-Conference.html` | abstract only |
| P406 | Quan, 2026 | Exact Federated Continual Unlearning for Ridge Heads on Frozen Foundation Models | arXiv; accepted at ECML-PKDD 2026 per the arXiv comment | `arXiv:2603.12977` | abstract only |
| P407 | Qiu, 2026 | FedOPAL: One-Shot Federated Learning via Analytic Visual Prompt Tuning | arXiv; accepted at FLICS 2026 per the arXiv comment | `arXiv:2607.08368` | abstract only |

## 14. Claims that rest on abstracts

The following papers are cited above at the abstract level only. Each claim they support is marked "(abstract)" where it is made, except where a full-text paper in the same sentence carries the claim. P077 is read in its medRxiv preprint version, P001 in its published version, and P063 and P062 in their arXiv versions.

| paper | read level | cited in |
|---|---|---|
| P006 | abstract only | sections 5, 7 |
| P007 | abstract only | sections 7 |
| P132 | abstract only | sections 3 |
| P141 | abstract only | sections 3, 11 |
| P142 | abstract only | sections 3 |
| P152 | abstract only | sections 3 |
| P156 | abstract only | sections 3 |
| P159 | abstract only | sections 3 |
| P164 | abstract only | sections 3, 11 |
| P183 | abstract only | sections 8 |
| P267 | abstract only | sections 5 |
| P287 | abstract only | sections 5 |
| P293 | abstract only | sections 5 |
| P316 | abstract only | sections 6 |
| P321 | abstract only | sections 6 |
| P392 | abstract only | sections 3, 10 |
| P401 | abstract only | sections 10 |
| P406 | abstract only | sections 4, 12 |
| P407 | abstract only | sections 4, 12 |
