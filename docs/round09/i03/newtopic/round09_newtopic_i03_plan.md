# Round 9, track newtopic, the plan for interval 3

*27 October 2026. Written by the newtopic session before any work of the interval. Living while interval 3 runs. Changes are appended at the end with their date, and the text above them is not rewritten.*

## 1. The decision that opens it

Interval 2's report (`docs/round09/i02/newtopic/round09_newtopic_i02_report.md`, section 5) offered E1 (a bounded interval on F1), E2 (fold the track's results into option A) and E3 (close the track). On 27 October Nicolas answered "explore f1" and supplied two papers, Bao, Ding and Wang, "Singular vector and singular subspace distribution for the matrix denoising model" (arXiv:1809.10476, Annals of Statistics), and Bao, Ding, Wang and Wang, "Statistical inference for principal components of spiked covariance matrices" (arXiv:2008.11903). The first is the suspect interval 2's checker named. Full texts stay outside the repository.

## 2. The object

F1 studies ridge reduced-rank regression. With $X$ an $n\times p$ matrix of iid $N(0,1)$ entries, $Y = XB + E$, $B = \sqrt\theta\,uv^\top$, $E$ with iid $N(0,1)$ entries, $p/n\to\gamma$ and $q/n\to c$, it takes the top right singular vector $\hat v$ of $F = HY$ with $H = X(X^\top X + n\lambda I)^{-1}X^\top$. Interval 2 found a threshold $\theta^*(\gamma,c,\lambda)$ below that of PCA of $Y$ and an overlap formula, both numerically accurate, with the overlap's normalising factor matched to the PCA case rather than derived and a cross term assumed to vanish.

## 3. Steps

- **G1 Corollary check.** Read the main theorems and assumptions of the two supplied papers, of Benaych-Georges and Nadakuditi (2012) and of Ding and Yang (2021), and decide whether, conditional on $X$, the threshold and overlap follow by direct application. The conditional model is a deterministic rank-one signal $a v^\top$ with $a = \sqrt\theta HXu$ plus noise $HW$ whose left covariance is $H^2$ and whose right side is orthogonally invariant.
- **G2 Derivation.** Derive the threshold and the overlap from first principles in the conditional model, including the normalising factor and the cross term, and compare with interval 2's formula to three decimals.
- **G3 Verification.** A fresh subagent that sees only the statements re-derives or numerically verifies them, in the manner of track fewcluster.
- **G4 Extensions.** General feature covariance $\Sigma$, a nuisance factor that may correlate with the features, and rank above one, each first as a numerical study.
- **G5 Positioning.** A focused novelty check of the sharpened statement, including the finance literature on factors estimated through characteristics (instrumented and projected PCA, supervised PCA).
- **G6 Report** to Nicolas.

## 4. Stop rules

- **S1.** If a published theorem, applied conditionally on $X$ with its assumptions checked, gives the threshold and the overlap, the result is recorded as a corollary and the interval closes with a short note.
- **S2.** If the derivation of G2 disagrees with interval 2's formula beyond Monte Carlo error and the gap cannot be traced, the session reports that before going further.
- **S3.** If under realistic feature spectra (a decaying spectrum like the embeddings') the ridge estimator never beats PCA of the outcomes by a material margin (a threshold ratio below 0.9 or an overlap gain above 0.1 at some penalty), the result is kept as a note and not developed into a paper.

## 5. Predictions, written before the work

- **H1.** Neither supplied paper covers the conditional model directly, because both assume noise with independent entries (an identity left covariance), while $HW$ has left covariance $H^2$.
- **H2.** The first-principles derivation reproduces interval 2's threshold to three decimals over its grid.
- **H3.** The derived normalising factor agrees with interval 2's matched one to within one percent.
- **H4.** With a decaying feature spectrum, ridge gains over PCA most when $u$ lies along the leading eigenvectors of $\Sigma$, and little when it lies along the tail.
