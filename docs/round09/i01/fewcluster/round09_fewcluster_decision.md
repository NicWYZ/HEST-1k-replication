# Round 9, track fewcluster, interval 1 decision memo (step S4)

*26 October 2026. Written by the fewcluster session at the end of interval 1. It reads the novelty map (S2) against the computations and the frontier note (S3), says which claim the track takes forward, and fixes interval 2. One check is still open. The precise-statement novelty check NOV6 is waiting on Nicolas's approval of its network access, and its verdict will go in a later document. Recommendations are `[proposed]`.*

## 1. What interval 1 did

The plan (`round09_fewcluster_plan.md`) started from a finite-population form of the Bahadur and Savage impossibility and wrote four candidate claims. Five independent checkers graded them with 321 logged queries (`results/round9/fewcluster/novelty/`). The session then proved the frontier (claim F) and computed it exactly. A fresh agent proved it again from the statements alone and checked it by brute force (`results/round9/fewcluster/verify/`). Forward citations of the closest papers were screened through OpenAlex once Nicolas approved the credential (`results/round9/fewcluster/novelty/openalex_forward_citations.csv`, 275 citing works). The HEST computations could not run because Longleaf was unreachable all day.

## 2. The claims

| Claim | Verdict | What follows |
|---|---|---|
| Lemma (unrestricted impossibility) | folklore | the total-variation form of Bahadur and Savage (1956). The explicit constant $(1 - \alpha - n/G)/(1 - n/G)$ is unconditional (two checkers read it as conditional and the verifier settled it). It is cited, not claimed |
| F (max-share frontier) | partly open in all five checks, proved | taken forward. Pötscher and Preinerstorfer (arXiv:2412.17470, Gaussian regression) and Hendriks, IJzerman-Boon and Klaassen (2006, the iid limit) are the precedents a referee will name. No forward citation of Hendriks et al. (2 works), Bloznelis (7), Chiang, Sasaki and Wang (2), or Preinerstorfer and Pötscher's two size papers of 2015 and 2018 (29 distinct citing works) states it. The nearest new item is Hansen, "Jackknife standard errors for clustered regression" (Review of Economic Studies, 2026, doi:10.1093/restud/rdag050, read from its abstract), which shows worst-case coverage zero for conventional cluster-robust intervals under normal errors, a neighbour of Theorem 1 in a different model |
| K (exact critical value below the frontier) | partly open | not pursued now. The worst case over a max-share class is not always a few-valued population (`s3_general_search_G15_n6.csv`), so an exact $c$ needs a certified global search, and the project's data lie beyond the frontier, where no $c$ exists |
| B (bounded residuals) | taken | the original PPI paper's appendices B and E, with Waudby-Smith and Ramdas's betting interval. Cited as the way out when a user can bound the residuals in absolute units |
| D (what the design buys) | mostly taken | take-all strata are classical (Hidiroglou 1986, Lavallée and Hidiroglou 1988). Corollary 4 of the frontier note adds that no fixed-size design blind to the outcomes beats simple random sampling |

## 3. What the frontier says, in the project's terms

At the sizes the project works with, a guarantee from scale-free information alone needs a promise about how far any one cluster can sit from the rest, and the promise has to be strong. From `results/round9/fewcluster/feasibility/s3_required_n.csv`, at $\alpha = 0.10$, a user who can rule out residuals beyond $\Lambda$ standard deviations needs to label at least the number of clusters below before any location and scale equivariant interval can be valid.

| $\Lambda$ | $G = 15$ | $G = 24$ | $G = 51$ |
|---|---|---|---|
| 2.0 | 8 | 9 | 9 |
| 2.5 | 10 | 10 | 14 |
| 3.0 | 10 | 13 | 16 |
| 3.5 | 10 | 17 | 22 |
| 4.0 | 14 | 17 | 27 |

The CCRCC donor INT5 has a z-score of 3.98 among the 24 donors in average expression over genes (`results/round9/stud/atypical_donor_diagnostics.csv`), which is not yet a residual for any one gene. A user who cannot rule out such a donor needs 17 of 24 donors labelled for a scale-free guarantee. The alternatives are a bound in absolute units (claim B) or a first phase that finds the donor (the probe, classical two-phase sampling). This is the formal version of what the project has seen since round 5. Every interval tried at 4 to 16 clusters under-covered on skewed tasks, and no change of variance estimator or reference distribution could have fixed that, because the obstruction is in what the class allows, not in the method.

## 4. Predictions

Scored in `results/round9/fewcluster/feasibility/predictions_scored.md`. P5 and P8 held, P7 partly held, P4 and P6 refuted, and P1 to P3 not tested. P5 and P8 were written with the frontier at $\kappa_2(k^\ast)$, which the verifier showed is one step too low. They are scored as written, and the corrected frontier is the column `kappa_sup` of `s3_frontier_exact.csv`.

## 5. Interval 2 `[proposed]`

The track takes the frontier forward and tries to make it a result a paper can lead with or carry as its theory section. The steps are these.

- **I2-1. Close the novelty question.** Collect NOV6 once Nicolas acts on its card. Read Pötscher and Preinerstorfer (arXiv:2412.17470) and Hendriks et al. (2006) in full in the session and write down how Theorems 1 and 2 differ from their results, formula by formula.
- **I2-2. The coefficient tuned from the sample.** Theorem 1 already covers PPI with a least-squares coefficient. The possibility half is shown only for a fixed coefficient. For the tuned coefficient the samples that defeat a finite critical value are those on which the residuals are affine in the predictions, not only constant, so the frontier should depend on $f$ and be at least as strict as the fixed-coefficient one. State and prove that version, and measure how much tuning moves the frontier on the project's prediction vectors. This is where the predictions enter the theory, and it is the part least likely to be routine.
- **I2-3. Stratified and two-phase designs.** The frontier under stratified sampling, with a take-all stratum chosen from a probe, in product form over strata. Expected to be a corollary. It is needed for the design recommendation.
- **I2-4. The real tasks.** Per-gene residual max-share on CCRCC, INDIANA_KIDNEY and LUNG_XENIUM against the frontier (predictions P1 to P3, already written), and ACS by state with the GBM predictions. Needs Longleaf.
- **I2-5. Position.** A short note on what of the frontier, I2-2 and I2-3 is new after I2-1, and whether it can lead the PPI paper. That is Nicolas's decision D1, possibly with David.

Each step writes predictions before it runs. Each statement that becomes a claim gets a fresh-agent proof check and a novelty check of its exact form.

## 6. For Nicolas

- Approve or decline the network card of NOV6, the precise-statement novelty check.
- Turn on the UNC VPN when convenient, for I2-4.
- Decision D1. Whether a sharp impossibility of this kind, with its design consequence (how many clusters must be labelled for a given defended $\Lambda$), is the kind of result the PPI paper should lead with. The session's view is that it explains the record's failures cleanly and is probably a theory section rather than a paper on its own, unless I2-2 gives the predictions a role that is not routine.
