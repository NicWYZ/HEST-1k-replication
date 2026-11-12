# E8 literature search, sub-agent summaries and declared deviations

*Merged on 11 November 2026 by the lead (frame 7744bd42-579b-40da-aa6c-80d67b9dbbdc) from the structured returns of the three sub-agents of plan section 5d.4. The summaries are the sub-agents' own words. The lead's reading goes into the F3 report. No paper text is kept here. The queries, sources and papers not retrieved are in the three CSV files beside this one.*

## Survey (frame b7388d0c-f604-4f00-9aca-7b71f08198cb)

Queries 37, sources graded 29, not retrieved 3.

**Summary.** No source found splits one labelling budget between a design-based (or PPI) estimator and prediction sets for units within clusters; this absence is provisional after 23 web and 10 CrossRef searches. Survey sampling offers allocation of one sample across several estimation goals (Kish, Bankier, Longford, Choudhry-Rao-Hidiroglou, Tam), PPI allocation across estimands (Ye and Yoganarasimhan), and splits between model training and estimation (Sanguiao Sande and Zhang; Riano) or training and conformal calibration (Zhang and Tuoto). The closest design analogue is Zimmerman (2006): one spatial design for parameter estimation and prediction, with the two goals found antithetical. Remote sensing practice (Stehman 2009; Olofsson et al. 2014) reuses one probability reference sample for a model-assisted area estimate and for map accuracy, but accuracy is a population parameter, not a unit prediction set. Wieczorek (2023) notes that within-cluster conformal sets for an already-sampled cluster can use that cluster's data only. On validity of reuse, only Dobriban and Lin (arXiv:2303.00203) treat it: using the same data for a confidence interval and a prediction set needs multiplicity control or a joint coverage region for joint validity; marginal validity of each is not addressed as a reuse problem by any source found.

**Declared deviations.**

- Survey-sampling angle only, run by this one agent; no further subagents were spawned.
- Cap applied to searches: 23 web searches and 10 CrossRef title searches (33 of 40); 4 further log rows are record lookups or full-text reads of items already found (16 arXiv ids, 2 arXiv HTML texts, 5 DOIs, 2 blocked StatCan pages).
- www150.statcan.gc.ca is blocked by the sandbox allowlist and access was not requested because the brief grants none; Longford (2006), Choudhry et al. (2012) and the 2015 Survey Methodology allocation paper were read only from search-tool page text, and the 2015 paper is in not_retrieved.
- Read depth: full text (partial) for Zhang and Tuoto and for Dobriban and Lin only; all other entries are abstract-level or secondary, so the closeness grades rest on abstracts.
- Bankier (1988) and Kish (1976) are graded from secondary descriptions plus CrossRef metadata, not from the papers.
- The absence of a same-problem source is provisional, based on 33 searches from one angle.
- Earlier-round sources (Broska and Howes 2026, GHCP, Ilyas et al. 2026, Csillag et al.) were not re-searched, as they fall outside this angle and were already logged.

## Conformal (frame 6a5495e6-aa89-465b-b296-1cf783a63926)

Queries 30, sources graded 16, not retrieved 2.

**Summary.** From the conformal side, no source splits one labelling budget between design-based or PPI inference for a population estimand and prediction sets, or reuses the same labelled units for both. The closest source is Chen and Li (arXiv:2609.33482). They divide a trusted label budget between a prediction-powered estimation step and an untouched conformal calibration split, and give an oracle allocation rule. Their PPI step learns a quantile function rather than targeting a population estimand, and the split is disjoint. Csillag et al. (arXiv:2510.16166) use one labelled set to calibrate conformal sets that then bound a population mean, so one set of labels yields both, but the sets are only an intermediate step. Ye, Lyu and Tao share one budget across many PPI estimates and have no prediction sets. Ilyas et al. price calibration labels for sets alone. GHCP's full text compares against HCP, the Dunn et al. methods and within-group split conformal, not a within-group full conformal set. No source found addresses the joint validity of a population interval and prediction sets built from the same labelled units. These presence and absence calls rest on 30 queries and partly on abstracts, so they are provisional.

**Declared deviations.**

- Ran 30 queries (23 web, 7 arXiv API), within the 40-query and 60-minute cap; no further searches.
- Did not delegate to further subagents; this subagent covered only the conformal angle.
- openreview.net was blocked by the allowlist and access was not requested, because the brief grants none; Ilyas et al. rests on the ICML poster abstract only.
- Full texts (2609.33482, 2510.16166, 2608.15500, 2604.12497, 2303.01422, 2608.02766) were read in selected sections plus keyword scans, not end to end.
- Six evidence entries (Einbinder et al., Gazin et al., Bersson and Hoff, Broska and Howes, Dunn et al. venue, Das et al.) rest on search-result excerpts or listings, marked secondary or abstract only; author lists for Das et al. and Gazin et al. are incomplete.
- The Csillag et al. venue (ICML 2026) was not verified; only the arXiv v1 page was read.

## PPI (frame ccd7704d-50e1-46f2-b7c0-645a1d82355d)

Queries 30, sources graded 18, not retrieved 2.

**Summary.** Within the PPI and ML literature, no source splits one labelling budget between design-based inference for a population estimand and prediction sets for target units, and none uses clusters. The nearest sources reuse one labelled sample for a PPI-type correction and a conformal set. Csillag et al. (ICML 2026, PMLR 306) fit a conformal set-predictor on labelled data and then use it to produce a population CI. Yoo et al. (IEEE WCL 2026) and Einbinder et al. (TPAMI 2025) use the same labels as a PPI rectifier and to calibrate a prediction set. Chen and Li (arXiv 2609.33482) split trusted labels between PPI-style bias correction and final conformalization, with a benefit-cost rule. In each, one use only serves the other. Budget allocation across several goals exists only for estimation tasks (Ye and Yoganarasimhan; Ye, Lyu and Tao). Broska and Howes give cluster-robust PPI and point to an untested cross- and within-cluster allocation. No source states a validity result for reporting both an interval and a prediction set from the same labelled units. Csillag et al. and Yoo et al. prove validity of the final output only. GHCP's full text compares against HCP and within-test-group split conformal, not PPI.

**Declared deviations.**

- No further subagents were spawned. This angle (PPI and ML) was covered by one searcher, with 30 logged queries in about 45 minutes, under the cap.
- Full-text reads were keyword scans of arXiv HTML (GHCP, Csillag et al., Broska and Howes, Chen and Li), not complete readings. Every other source was read at abstract level only, so the absence of a budget split or of a joint-validity result is provisional for papers read only in abstract.
- For Einbinder et al. the TPAMI DOI lookup failed (proxy error), so I used the arXiv abstract 2412.11174; PubMed supplied the bibliographic details. Huang, Wu and Wang were read on arXiv 2502.17773 because the SSRN record had no abstract.
- Venues for Zrnic and Candes (ICML 2024) and Fisch et al. (NeurIPS 2024) rest on secondary listings (Semantic Scholar; a citing paper's references) and were not opened at the venue.
- Of the 28 HCP-citing works and 119 PPI-citing works returned by the filtered OpenAlex searches, most were screened by title only. The citing-work coverage is OpenAlex's index as of today and may miss recent preprints.
- Multi-task PPI (arXiv 2605.29249) was seen but left out of evidence because I did not read its full author list.
