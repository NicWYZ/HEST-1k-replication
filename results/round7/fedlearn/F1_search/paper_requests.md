# Paper requests, round 7 federated learning track (F1 step 2)

Sent to Nicolas in chat on 13 October 2026, as section 8 of the instruction asks. These are the core papers of `evidence_table.csv` whose full text the session could not retrieve from an open source (PubMed Central, Europe PMC, arXiv, bioRxiv, medRxiv, the proceedings sites or nature.com open access). Every other core paper has an open full text. Each link goes through UNC Chapel Hill's library proxy, since each paper has a DOI at a subscription publisher. Papers that arrive are saved to `~/hest-1k/fedlearn_papers/requested/`, outside the repository. Citations are read from the Crossref record of each DOI.

| # | citation | DOI | link | question, and why the abstract is not enough |
|---|---|---|---|---|
| 1 | He B, Bergenstråhle L, Stenbeck L, et al. (2020). Integrating spatial gene expression and breast tumour morphology via deep learning. Nature Biomedical Engineering 4:827-834. | `10.1038/s41551-020-0578-x` | https://login.libproxy.lib.unc.edu/login?url=https://doi.org/10.1038/s41551-020-0578-x | Q1 and Q2. ST-Net is the model PPML-Omics federates and the first spatial expression predictor from H&E. The abstract does not say how accuracy depends on the number of training patients, or how the leave-one-patient-out evaluation was set up. |
| 2 | Sankararaman S, Obozinski G, Jordan MI, et al. (2009). Genomic privacy and limits of individual detection in a pool. Nature Genetics 41:965-967. | `10.1038/ng.436` | https://login.libproxy.lib.unc.edu/login?url=https://doi.org/10.1038/ng.436 | Q5. It bounds how well membership can be detected from pooled summary statistics, as a function of the number of individuals and of statistics released. That bears directly on what C1's per-center sums reveal. The bound itself is not in the abstract. |
| 3 | Kaissis G, Ziller A, Passerat-Palmbach J, et al. (2021). End-to-end privacy preserving deep learning on multi-institutional medical imaging. Nature Machine Intelligence 3:473-484. | `10.1038/s42256-021-00337-8` | https://login.libproxy.lib.unc.edu/login?url=https://doi.org/10.1038/s42256-021-00337-8 | Q5 and Q3. It is one of the few multi-institution studies that reports both the cost in accuracy and the attack resistance of combining federated learning, secure aggregation and differential privacy. The abstract gives no numbers. |
| 4 | Hosseini SM, Sikaroudi M, Babaie M, et al. (2023). Proportionally Fair Hospital Collaborations in Federated Learning of Histopathology Images. IEEE Transactions on Medical Imaging 42:1982-1995. | `10.1109/TMI.2023.3234450` | https://login.libproxy.lib.unc.edu/login?url=https://doi.org/10.1109/TMI.2023.3234450 | Q4. A seed of section 2.4. It concerns how gains are spread across hospitals of different sizes in federated histopathology. The abstract does not give the per-hospital results that a center-level argument needs. |
| 5 | Giouroukou K, Marias K, Tsiknakis M, et al. (2026). Rethinking Privacy in Medical Imaging AI: From Metadata and Pixel-Level Identification Risks to Federated Learning and Synthetic Data Challenges. Radiology: Artificial Intelligence 8:e250273. | `10.1148/ryai.250273` | https://login.libproxy.lib.unc.edu/login?url=https://doi.org/10.1148/ryai.250273 | Q5. A review of what in medical images is identifying beyond metadata. The abstract lists the categories but not the evidence behind each. |

## What arrived

Nothing yet.

## Claims that still rest on abstracts

To be filled at F2 from the review.
