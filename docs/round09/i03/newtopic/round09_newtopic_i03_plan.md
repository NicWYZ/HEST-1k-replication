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

## 6. Changes and results (27 October 2026)

**G1, the two supplied papers.** Bao, Ding and Wang (arXiv:1809.10476) assume white noise with independent entries, and Bao, Ding, Wang and Wang (arXiv:2008.11903) take $Q = TXX^\ast T^\ast$ with an identity middle weight and a spiked $\Sigma = I + S$. Neither covers the conditional F1 model, whose noise $HW$ has left covariance $H^2$. H1 held.

**G2, the derivation.** Conditional on $X$, write $t_i = h_i^2$ for the eigenvalues of $H^2$, $\nu$ for their law over the $n$ eigen-directions of $H$, $\alpha$ for the law with weights proportional to $t_i s_i$ (the squared components of $HXu$ on those directions), and $\beta^2 = \theta m_a$ with

$$
m_a = \int \frac{s^3}{(s+\lambda)^2}\, \mu_\gamma(ds).
$$

With $\tilde m$ the root of the generalised Marchenko-Pastur equation, the session's formulas are

$$
\zeta(\tilde m) = -\frac{1}{\tilde m} + \int \frac{t\, \nu(dt)}{1 + c\, t\, \tilde m}, \qquad P(\tilde m) = -\tilde m \int \frac{\alpha(dt)}{1 + c\, t\, \tilde m},
$$

with threshold $\theta^\ast = 1/\{m_a P(\tilde m_\ast)\}$ at the critical point $\zeta'(\tilde m_\ast) = 0$, and overlap

$$
|\langle \hat v, v\rangle|^2 = \tilde m\, P(\tilde m)\, \frac{\zeta'(\tilde m)}{P'(\tilde m)} \quad \text{at the root of } \theta\, m_a\, P(\tilde m) = 1 .
$$

They reproduce PCA's threshold $\sqrt c$ and overlap when $H = I$, and Kargin's $\sqrt{\gamma c}$ for least squares. Against interval 2's threshold grid the largest difference is 0.0012, from interval 2's edge bisection, so H2 partly held. The derived overlap equals interval 2's matched-factor overlap to four decimals in 48 cells, so H3 held. A fresh simulation ($n = 1500$, 10 replicates, 32 cells) differs from the theory by at most 0.037 in the 24 cells with $\theta \ge 1.5\theta^\ast$ and 0.023 in the 16 cells with $\theta \ge 2.5\theta^\ast$. Tables in `results/round9/newtopic/i03/` (`g2_threshold_grid_vs_f1.csv`, `g2_overlap_mine_vs_f1.csv`, `g2_overlap_sim_vs_theory.csv`), code in `code/scripts/round9_newtopic_i03_corollary_check.py`.

**S1, the corollary check beyond the supplied papers.** Conditional on $X$, the model $F/\sqrt q = A + \Sigma^{1/2} W$ with $\Sigma = H^2$ and $A = \sqrt{\theta/q}\, HXu\, v^\top$ is exactly the model of Liu, Liu, Pan, Zhang and Zhang (arXiv:2310.13939, v2 May 2025). They allow a general symmetric bounded $\Sigma$, a deterministic $A$ of rank $O(n^{1/3})$ and real or complex entries with a fourth moment, and their Theorems 1 and 2 give the spiked eigenvalues and both singular vectors' projections. Rotated to $H$'s eigenbasis, the model is also that of Chapon, Couillet, Hachem and Mestre (arXiv:1207.0471, Theorem 2.2, complex Gaussian), whose outlier equation with $\Lambda_\ast = \beta^2\alpha$ is the session's $\beta^2 P = 1$ term by term. Hachem, Loubaton, Mestre, Najim and Vallet (arXiv:1106.1497) assume bi-unitarily invariant noise and do not apply. Liu et al.'s Theorem 1 evaluated on realised $X$ ($n = 1500$, 3 seeds) matches the session's limiting overlap within 0.023 in 12 cells (`s1_liu2310_13939_vs_mine.csv`). The session's reading is that stop rule S1 triggers. A fresh agent audits that reading before the interval closes, and steps G3 to G5 are not run.
