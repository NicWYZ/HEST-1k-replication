# Round 7 fedlearn, F2 citation audit: notes

Auditor run of 13 October 2026. Scope: the 91 papers cited in sections 2 to 12 of `docs/round07/tracks/fedlearn/round07_fedlearn_literature_review.md`. Per-paper detail is in `citation_audit.csv` (same directory). Neither the review nor any other file was edited.

## Totals
- 91 papers audited. Every identifier resolved to the paper named (primary record: Crossref 44, arXiv API 37, PubMed 6, Europe PMC 1, proceedings pages 3; extra records were opened for 11 papers). Titles matched for all 91.
- Claims: 69 fully supported, 20 partly, 2 not supported. In all, 22 papers have a claim-level mismatch.
- Record-level issues only, with claims fine or also flagged: 18 papers. Nine have author lists truncated at 15 plus 'et al.'. Seven have a published venue recorded only as arXiv (P126, P267, P339, P342, P389, P406, P407). Two have year/version inconsistencies (P266, P006). In total, 33 papers have some mismatch.
- Source read for the claim check: full text 53, abstract plus full text 20, abstract only 18. P188 was checked from its abstract only, since no full text was reachable.
- Read level: P183 and P267 are abstract-only papers whose claims lack the "(abstract)" mark. Four claims marked "(abstract)" state things that are not in the abstract: P159 (632 sections), P392 ('Visium', 'inter-patient'), P141 (training on spot aggregates) and P406 ('natural images').

## Most serious findings
1. **P379 SEAL (sections 4, 9, 11).** The paper credits the 1.33% gain to Phikon-v2, the encoder that improved most, not to the best encoder. In Extended Data Table 13 the best baseline (UNIv2) rose from 0.4142 to 0.4186, and all absolute gains are 0.003 to 0.006 PCC. The review's "of the order of 0.01" (sections 9 and 11) therefore overstates SEAL's gain. Filiot et al. (P385, +0.013) is correct.
2. **P344 Ziegler (section 6).** At eps=6 the global AUC of 0.937 is not "0.03 below the non-private model": the non-private DenseNet121 scored 0.935 (abstract: 0.94 for both). The 0.03 drop applies only to clients holding large CheXpert shares. The reconstruction attack also worked only when batch-normalisation layers were frozen.
3. **P006 fedRBE (sections 5, 7).** The bound "within 3.6e-13" comes from the arXiv v1 abstract (2024), while the title and the "non-identical feature sets" content come from v2 (2026), whose abstract gives no bound. The v2 full text reports a maximum of 5e-13 on simulated data.
4. **P077 Ogier du Terrail (section 4).** The review says "three hospitals". The only full text available, the medRxiv preprint, describes two hospitals (Cohorts A and B). The published body is paywalled, so the count there is unverified. The read level should say that the preprint was read.
5. **P047 Schoenpflug (section 4).** The review says "three-country". The paper describes three clients plus a server across four networks in four countries, and network restrictions (an open port, solved by hosting on AWS) rather than "firewalls".
6. **P046 (section 4).** The review conflates two ranges. Federated models were within ±2% of, or 2 to 6% below, centralised ones. The range 0.2 to 6% applies to privacy-preserving variants.
7. **P200 DataSHIELD (section 8).** It is listed under "One-round exact fits", but its GLM is iterative. It is exact, but not one-round.
8. **Section 7, segmentation.** "classification, segmentation and survival" cites six papers, none of which is a segmentation study (logged on the P099 row).
9. **Smaller overstatements:**
   - P052: the 4% loss applies to out-of-domain tasks only; in-domain the loss is 0.5%.
   - P017: 0.4K to 1.02K prompt parameters, not "about a thousand".
   - P129: 388 is hospital A's share at the 5/6 split, not the cohort size.
   - P173: the paper averages local OLS fits, not ridge fits.
   - P183: the 0.1% figure comes from simulations.
   - P289: "most" of the 14 encoders, not all.
   - P339: "at most 77 dimensions" is not supported, because the 36 appendix datasets' dimensions are not listed.
   - P378: "every metric" holds in-slide only.
   - P407: prompts are tuned locally.

## Caveats on this audit
- Full texts were the copies saved under `fedlearn_papers/`. Several of them are preprints: P077, P292, P063, P062 and the arXiv versions of P015, P171, P173, P179 and P209. A claim checked against a preprint is labelled as such where the version matters.
- Negative statements ("reports no data-size curve", "none found") were checked only for consistency with the text read. They were not proven absent.
- Venue checks beyond the record relied on arXiv comments, except that SCAFFOLD's PMLR page and the NeurIPS 2020 page for P180 were opened.
