# Audit of the F1 "corollary" claim (ridge-RRR spectral threshold and overlap)

**Verdict: corollary_with_gap.** The gaps are small and technical or citation-level; I found no new mathematics needed. Residual (ridge vs PCA threshold, optimal lambda) is a short proposition at most.

Scope declaration: both PDFs were downloaded and the model, assumptions and main theorems were read from extracted text (Liu et al. Sections 1-2 plus Thm 1-2; Chapon et al. Sections 1-2 incl. Thm 2.1-2.3, Cor 2.1). Proofs were not read. Monte Carlo replicate counts are small (3-12) and are labelled provisional.

## 1. Assumption check

Dimension dictionary for Liu et al. (their X_n is p x n, p/n -> c_L, W has E|sqrt(n) w|^2 = 1): F/sqrt(q) is n_obs x q, so their p = n_obs, their n = q, c_L = n_obs/q = 1/c, W = E/sqrt(q). Their "right singular vectors" (eigenvectors of X*X, eqs. (12)-(13)) are the vhat of F in R^q.

| Item | Status |
|---|---|
| Conditioning on X | Legitimate: E is independent of X, so given X, Sigma=H^2 and A=sqrt(theta/q) H X u v' are deterministic and W has iid N(0,1/q) entries. Liu et al. state results for deterministic sequences. Transfer to almost every X needs (i) Assumption 3/4 constants to hold a.s. along X, and (ii) Prop. 1 error bounds depending only on those constants, so the conditional O_P(n^-1/2) integrates out. Routine but unwritten. |
| Assumption 1 (real or complex, bounded 4th moment) | Real Gaussian covered. |
| Assumption 2 | c_L = 1/c in (0,inf). OK. |
| Assumption 3 (||A|| bounded, rank O(n^(1/3)), ||Sigma|| bounded) | rank(A)=1; ||Sigma||<=1; ||A||=sqrt(theta/q)||HXu|| <= sqrt(theta n/q)(1+o(1)). OK. |
| Assumption 4 (gaps > c0; integral t^2 dH/(gamma_k-t)^2 < 1/c_L) | The integral condition is exactly phi'(gamma)>0 (distant spike, phi' = 1 - c_L * int t^2/(gamma-t)^2 dH). In finite-n form it is equivalent to eta_1>0 in eq. (13). So the Liu distant-spike condition IS the BBP-type threshold for F1, and the overlap eta*(Xi'a)^2/gamma_1 goes to 0 as eta goes to 0. The gap condition gamma_1-gamma_2>c0 is weaker: gamma_1 detaches from the top of the H^2 spectrum before the distant condition holds (numerically gamma_1 = 2.34 vs gamma_2 = 0.904 at theta=0.2, where eta<0; tables below). My argument that the integral condition implies the gap condition (the integral diverges at a square-root edge) is not checked against a paper. |
| Below / at threshold | **Not covered by Liu et al.** Thm 1-2 treat distant spikes only; close spikes (phi'<=0) and the exact threshold are not treated. |
| Chapon et al. Thm 2.2 | Orientation: their model is n^-1/2 X D^(1/2) + P with D on the column side, so it must be applied to F'/sqrt(q) (q x n_obs), with D = diag(eigenvalues of H^2), N=q, n=n_obs, c=q/n. Thm 2.2 counts eigenvalues in compact intervals outside supp(mu), so it gives the 'no outlier below threshold' half as well as the location above. Cor 2.1 (explicit omega^2 g(x)=1) needs Assumption 6, which fails here (weights of HXu on H's eigenvectors are not proportional to nu), so the general Thm 2.2(1) with the 1x1 weighted measure Lambda_* is the tool. Assumption 5 for r=1 means convergence of the scalar weighted measure Lambda_n; a.s. convergence follows from the SVD of X (V'u uniform on the sphere, independent of singular values). Assumption 3(2): top eigenvalue of H^2 converges to the edge by Bai-Yin. |
| Real vs complex entries | **Chapon et al. Assumption 2 is complex Gaussian.** With real Gaussian E an orthogonal rotation to H's eigenbasis preserves the law, but the theorem as stated does not cover real entries. First-order universality is expected, but neither paper states it. This is the main literal gap in claim (b). |
| Does Chapon give the overlap? | No: eigenvalue location only. The overlap comes only from Liu Thm 1, valid above threshold. |

## 2. Numerical check (check_liu_F1.py; gamma=2, c=0.1, lam=0.3, u=e1, v=e1)

Prediction on realized X: R = aa' + H^2, a = sqrt(theta/q) H X u, gamma_1 and Xi the top eigenpair, eta = 1 - (1/q) sum_(i>=2) gamma_i^2/(gamma_1-gamma_i)^2, overlap = eta (Xi'a)^2/gamma_1, top eigenvalue phi(gamma_1) = gamma_1 + (gamma_1/q) sum_(i>=2) gamma_i/(gamma_1-gamma_i). Monte Carlo: SVD of F = HY, |<vhat,v>|^2 and sigma_1^2/q. n=1500 (p=3000, q=150), 8 replicates per theta (means):

|   theta |   mc_overlap |   pred_overlap |    eta |   mc_top_eig |   pred_top_eig |
|--------:|-------------:|---------------:|-------:|-------------:|---------------:|
|     0.4 |       0.3027 |         0.4179 | 0.526  |      11.8309 |        12.0096 |
|     0.7 |       0.7243 |         0.7364 | 0.8447 |      13.6015 |        13.7378 |
|     1.1 |       0.8544 |         0.8552 | 0.9358 |      16.2071 |        16.4974 |
|     2   |       0.9327 |         0.9323 | 0.9805 |      23.1842 |        23.237  |

Mean overlap gap |MC - prediction| at theta=0.7 is 0.0121 and at theta=1.1 is 0.0008. The per-realization absolute error is 0.0257 (theta=0.7) and 0.0088 (theta=1.1); it includes genuine MC fluctuation of the overlap given X, so the formula is not shown biased at theta>=0.7. The top-eigenvalue prediction (Thm 2) is within 0.05-0.29 on values 11.8-23.2 (at most about 2.4% relative). Scaling check (liu_scale_check.csv; 12/6/3 replicates at n=750/1500/3000), abs_err = mean |MC-pred| per realization:

|             |   mc_overlap |   pred_overlap |   abs_err |
|:------------|-------------:|---------------:|----------:|
| (0.4, 750)  |       0.4578 |         0.4426 |    0.1008 |
| (0.4, 1500) |       0.3979 |         0.4403 |    0.0801 |
| (0.4, 3000) |       0.3496 |         0.4169 |    0.0734 |
| (0.7, 750)  |       0.7413 |         0.7278 |    0.0668 |
| (0.7, 1500) |       0.7303 |         0.7352 |    0.0294 |
| (0.7, 3000) |       0.7468 |         0.7348 |    0.0173 |

At theta=0.7 the error shrinks with n. At theta=0.4 (near the threshold) it does not shrink visibly at these n and replicate counts (provisional: 0.10, 0.08, 0.07). Finer scan (liu_scan_n1500.csv, 6 replicates; eta<0 means below the distant-spike threshold, where the formula does not apply, and its numbers are meaningless):

|   theta |   mc_overlap |   pred_overlap |     eta |   gamma1 |
|--------:|-------------:|---------------:|--------:|---------:|
|     0.1 |       0.0327 |        -2.9267 | -6.0124 |   1.6048 |
|     0.2 |       0.0183 |        -0.6036 | -0.9271 |   2.3414 |
|     0.3 |       0.1967 |         0.1375 |  0.1844 |   3.1773 |
|     0.4 |       0.4816 |         0.4275 |  0.5368 |   3.972  |
|     0.5 |       0.5189 |         0.5633 |  0.6822 |   4.6346 |
|     0.7 |       0.7246 |         0.7385 |  0.8464 |   6.3197 |
|     1.1 |       0.8528 |         0.8576 |  0.9375 |   9.472  |

Realized-X threshold, root of eta_1(theta)=0 (threshold_vs_lambda.py; one X per gamma, n=2000, finite-n error about 0.005; lam=0, gamma=2 gives 0.312 vs the exact sqrt(c)=0.316):

|   gamma |   lam |   theta_star_realized |   theta_PCA |
|--------:|------:|----------------------:|------------:|
|     2   |  0    |                0.3118 |      0.3162 |
|     2   |  0.05 |                0.2968 |      0.3162 |
|     2   |  0.1  |                0.2878 |      0.3162 |
|     2   |  0.3  |                0.271  |      0.3162 |
|     2   |  1    |                0.2582 |      0.3162 |
|     2   |  3    |                0.259  |      0.3162 |
|     0.5 |  0    |                0.2306 |      0.3162 |
|     0.5 |  0.05 |                0.2122 |      0.3162 |
|     0.5 |  0.1  |                0.2043 |      0.3162 |
|     0.5 |  0.3  |                0.1944 |      0.3162 |
|     0.5 |  1    |                0.1954 |      0.3162 |
|     0.5 |  3    |                0.2107 |      0.3162 |
|     0.2 |  0    |                0.1455 |      0.3162 |
|     0.2 |  0.05 |                0.1413 |      0.3162 |
|     0.2 |  0.1  |                0.1387 |      0.3162 |
|     0.2 |  0.3  |                0.1349 |      0.3162 |
|     0.2 |  1    |                0.1355 |      0.3162 |
|     0.2 |  3    |                0.1418 |      0.3162 |

Note: an earlier draft of the threshold script computed H X u in the eigenbasis incorrectly; it was rewritten and the new numbers cross-checked against the direct Monte Carlo (theta=0.2: MC overlap 0.018; theta=0.3: 0.20; consistent with theta*(0.3)=0.271).

## 3. Literature (web search; OpenAlex and Semantic Scholar not queried; absence calls are provisional)
- Johnstone-Onatski, Ann. Stat. 48(3), 2020 ("Testing in high-dimensional spiked models"): keywords list multiple response regression and canonical correlations; it concerns subcritical-spike testing and per-case thresholds, i.e. eigenvalues and tests, not singular-vector overlap, and OLS only. Only the abstract page was seen; I did not verify the threshold formulas inside.
- lam=0 is standard. For p<n, F'F = Y'P_X Y is a noncentral Wishart. Rotating by P_X's eigenbasis gives a p x q Gaussian matrix plus a rank-one mean, i.e. the iid additive model of Benaych-Georges-Nadakuditi (JMVA 2012), Ding (2020) and Bao-Ding-Wang (Ann. Stat. 2021, arXiv:1809.10476). The threshold is sqrt(gamma c) (realized 0.2306 at gamma=0.5, lam=0 vs sqrt(0.05)=0.2236). For p>n, H=I and F=Y, which is PCA of Y with threshold sqrt(c).
- Bao-Ding-Wang-Wang, "Statistical inference for principal components of spiked covariance matrices" (arXiv:2008.11903): a spiked covariance paper, not a regression or ridge-hat-matrix statement (judged from the search snippet only; not read in full).
- Bao-Hu-Pan-Zhou 2019 (arXiv:1704.02408) and Bykhovskaya-Gorin (Ann. Stat. 2022; arXiv:2306.16393; review arXiv:2411.15625) treat canonical correlations and Johansen-type reduced-rank regression (lam=0 with inverse sample covariances). Mukherjee-Zhu 2011 (reduced rank ridge) is methodological and Bunea-She-Wegkamp (arXiv:1004.2995) is non-asymptotic. Ding-Yang (spiked separable covariance), cited in Liu et al. as the route to general separable noise, was not read.
- No paper found that states the ridge (lam>0) threshold or the overlap of the top singular vector of HY.

## 4. Verdict: corollary_with_gap
1. Real entries: Chapon et al. is complex-Gaussian only, so (b) as stated does not cover real E. Liu et al. covers real, but only above threshold. Fix: cite a real-case outlier-location result, or state the sub-threshold half for complex noise or via universality. Qualitative gap; formulas are not expected to change.
2. Overlap and top-eigenvalue statements are proved only above the threshold (distant spike). At or below it the two papers prove nothing for the overlap (overlap going to 0 is expected, not shown).
3. Chapon Cor 2.1 does not apply (Assumption 6 fails). The general Thm 2.2 with a weighted measure must be used.
4. Conditional-to-unconditional transfer, a.s. convergence of Lambda_n and of the spectrum of H^2: routine but unwritten.
5. 'Routine' limit computation is real algebra: gamma_1 solves 1 = a'(gamma_1 - H^2)^(-1) a, an integral against the weighted spectral measure; eta and (Xi'a)^2 need the same resolvent integrals. It is doable from Marchenko-Pastur but not a one-line corollary. Numerically, the session's formulas agree with Liu on realized X (0.023, per the task), and my independent check agrees to 0.012-0.001 in mean overlap at theta=0.7, 1.1 for n=1500.

## 5. Residual
The comparison with PCA of Y is slightly more than a remark but less than a theorem. From the realized-X table, ridge thresholds lie below the PCA-of-Y threshold sqrt(c)=0.316: gamma=2 gives 0.271 at lam=0.3 with a minimum of about 0.258 near lam=1 to 3 (OLS equals PCA there); gamma=0.5 gives 0.194 vs OLS 0.231; gamma=0.2 gives 0.135 vs OLS 0.146. Being below PCA already happens for OLS when gamma<1 (known via the lam=0 reduction above). The new content is only the ridge improvement over OLS (strict for gamma>1; 7-16% at gamma=0.5 and 0.2 in these single realizations) and the interior optimal lam. That is a one-parameter optimization of an explicit formula that follows from the corollary: a short proposition with a figure at most, and its novelty rests on the provisional literature absence in Section 3.
