# T6 fragment: attacks, differential privacy, governance (Q5)

Search date 2026-10-13. Sources: PubMed, Europe PMC, arXiv, web search, PMLR and NeurIPS pages through web search. 26 query ids, 63 log rows, 85 papers in `evidence.csv` (36 marked core candidates, a deliberately generous list for the lead to cut). Read level: full text (some read selectively) for 8 papers, abstract only for the rest. All counts are provisional because of the screening limits listed at the end.

## Q5 by sub-question

**Federated or privacy-preserving expression-from-histology.** Two papers. PPML-Omics (10.1126/sciadv.adh8601) runs ST-Net inside federated DP learning; I read the bioRxiv version in full. Its spatial task reports privacy budgets of 0.01 and 0.1 and MSE of about 0.91 for every arm (central 0.908, FL+DP 0.926 and 0.910, PPML-Omics 0.911 and 0.909), so the arms differ in the third decimal and no correlation is reported. privateST (10.1038/s41598-026-55961-4, full text read) is encrypted inference on a trained ResNet-18; training used 28,263 spots from 22 patients and testing one patient. Not found: any federated fit of a head on frozen features, any shared-sums (C1) scheme, any differing gene panels across sites (queries T6-q10 on all three sources and the web).

**What is identifying.** H&E: Ganz et al. (PMID 39316996) re-identify the source patient with F1 of 50 to 62 percent, best within one resection; Bisson et al. (PMID 37205164) show labels and scanner metadata carry identifiers; Howard et al. (10.1038/s41467-021-24698-1) show site signatures in TCGA histology. Expression: linking to genotype through eQTLs (Schadt 10.1038/ng.2248; Harmanci PMID 26828419; Sadhuka 10.1101/gr.277699.123; Walker PMID 39362221 for single-cell pseudobulk). Not found: any study of re-identification from spatial-transcriptomics spots or from pathology foundation-model embeddings (T6-q05, q10, q14).

**Attacks on shared statistics.** Membership inference on aggregate genomic data (Homer 10.1371/journal.pgen.1000167; Sankararaman 10.1038/ng.436; Liu PMID 30815118 on phenotype summaries; Venkatesaramani PMID 37217251; Almadhoun 10.1093/bioinformatics/btaa475 on DP query results). Closest to C1: Huth et al. (10.1093/bioinformatics/btad531), an attack that needs the sample covariance of shared data (abstract only, PDF not retrieved). Not found: an attack specific to ridge sufficient statistics X'X and X'Y, or to PCA bases (T6-q01, q06).

**Attacks on gradients.** Zhu (arXiv 1906.08935), Geiping, Yin, Zhao; in medical imaging Hatamizadeh (10.1109/TMI.2023.3239391, read selectively) and Ziegler (arXiv 2205.03168). Secure aggregation: Bonawitz (arXiv 1611.04482) and an attack on it (Pasquini, arXiv 2111.07380).

**Cost of DP.** Imaging: DenseNet121 AUC 0.937 at epsilon 6, 0.03 below non-private (Ziegler); Lu et al. noise up to 0.1 times weight spread left AUC at 0.927 to 0.932 and 0.986 to 0.988, with no epsilon located. Tramer and Boneh (arXiv 2011.11660) find linear models on fixed features beat DP deep nets at moderate budgets. DP linear regression: Sheffet (PMLR v70), Wang AdaSSP (arXiv 1803.02596), Cai et al. minimax cost (arXiv 1902.04495), Ferrando, Cao (public second moment). Not found: DP ridge on pathology embeddings, or any DP cost measured for expression regression.

**Governance in practice.** FeTS 71 sites (10.1038/s41467-022-33407-5), EXAM 20 institutes, swarm learning (Warnat-Herresthal; Saldanha), MELLODDY ten companies, DataSHIELD, GA4GH federation (PMID 35128509), a nationwide pathology deployment (10.1038/s41746-026-02958-y, abstract only). Not found: a published data-use agreement template for histology plus expression; the legal papers found are commentaries, not agreements.

## Core candidates whose full text I did not read
Kairouz 10.1561/2200000083 (PDF of arXiv 1912.04977 saved, not read), Huth 10.1093/bioinformatics/btad531, Pati 10.1038/s41467-022-33407-5, Warnat-Herresthal 10.1038/s41586-021-03583-3, Saldanha 10.1038/s41591-022-01768-5, Dayan 10.1038/s41591-021-01506-3, Adnan 10.1038/s41598-022-05539-7, Kaissis 10.1038/s42256-021-00337-8, Babendererde 10.1038/s41746-026-02958-y, Sadhuka 10.1101/gr.277699.123, Heyndrickx 10.1021/acs.jcim.3c00799, Sheffet and Wang (arXiv versions only abstract).

## Discrepancies with section 2.4
- Hosseini et al. TMI 2023 matches 42(7):1982-1995 (10.1109/TMI.2023.3234450, title on fair hospital collaborations); it is not a privacy paper.
- privateST: exists; Sci Rep 16, article 25330, 3 June 2026, authors Kim, Kim and Han; description (encrypted inference, not FL) confirmed.
- PPML-Omics: record matches (Sci Adv 10(5):eadh8601). The text I read is the preprint.
- Kairouz et al.: Crossref lists two authors; the arXiv listing has 59.
- Adnan et al. (Sci Rep 12:1953) was confirmed as 10.1038/s41598-022-05539-7 from PubMed; abstract only.
- Not verified in my sources: Lu et al. is described as using DP; the paper adds Gaussian noise to weights and I did not find a stated epsilon.

## Not covered or limited
- Screening: Europe PMC top 100 read in full only for q01 to q04; other queries read through a keyword-filtered view. PubMed q08 (335 hits) and q09 (86): only first 10 titles read. arXiv lists screened through a filtered view. This falls short of the first-100 rule.
- Europe PMC rejected sort=RELEVANCE with HTTP 503; default order used. The first runs of PubMed and arXiv hit rate limits and were rerun.
- Not opened: an ICML 2026 paper on reconstructing images from medical foundation-model parameters (seen only on a summary site), NeurIPS proceedings pages (venues taken from citing papers, marked secondary), ACM CCS and Dwork papers (Crossref only; excluded: Analyze Gauss, Calibrating Noise, Backes microRNA).
- Not searched: Beacon v2 and DUA templates beyond the queries listed; the forward-citation search from PPML-Omics and Lu et al. was done by web search only.
