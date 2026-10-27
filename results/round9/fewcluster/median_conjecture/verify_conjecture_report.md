# Check of the proof sketch for the Paul–Kuchibhotla (arXiv:2403.06357) Remark-1 conjecture

## 1. Their exact setting (arXiv PDF, current version v2 of 27 Jul 2026, Remark 1; read directly)
* Remark 1 restates Lanke (1974, Thm 2): no real-valued, locally bounded g_L, g_R on R^n with
  P(g_L(X_n) < θ < g_R(X_n)) > 1-α for every X_n with iid components from a *continuous distribution symmetric about θ*
  (open interval, strict coverage). They say Lanke's claim is false for log2(1/α) <= n < log2(2/α)
  (the a-anchored interval from their eq. (5) is bounded, valid for n >= log2(1/α), not shift-invariant).
* Conjecture (verbatim idea): "no shift-invariant, locally bounded confidence interval for the median exists when n < log2(2/α)".
  "Shift-invariant" and "locally bounded" are NOT formally defined; "median" class is not restated there. Natural reading used here:
  g(x + c1) = g(x) + c for all c in R; g bounded on bounded sets of R^n.
* Their Thm 1 class: independent X_i with a common median θ0 (P(X<=θ0)>=1/2, P(X>=θ0)>=1/2), closed intervals, coverage >= 1-α;
  the shift-invariant order-statistic interval is finite iff n >= log2(2/α).
* v2 still lists it as a conjecture.

## 2. Verdict on the analyst's sketch: proved_with_changes
**The sketch as written has the flaw you suspected.** Two clusters with mass 1/2+eps (near) / 1/2-eps (far), eps>0 => unique median m in the near cluster.
* far cluster all n points: Y+2θ·1, Y in K=[-1,1]^n => g_L >= 2θ-M > m  => forced miss, probability (1/2-eps)^n.
* near cluster all n points: only g_R <= M, g_L >= -M. But m ∈ (-1,1) can lie inside [-M, M] (M = sup_K|g| may exceed 1), so no miss is forced.
  => only 2^-n, which is Lanke's bound, not 2^(1-n). Letting eps<0 just swaps the roles. Sketch with eps>0 does NOT give 2^(1-n).
* For eps=0 (centre θ of a symmetric distribution, Lanke's class) BOTH events do force a miss and the sketch works — but the median is then
  non-unique (every point of [1, 2θ-1]); this is legitimate in Lanke's/the paper's setting (cover the centre of symmetry / any median).

**Repair (works also when a unique median is required): three clusters.**
P_{η,D}: mass (1-η)/2 uniform on A=[-1,1]; mass (1-η)/2 uniform on B=[2D-1,2D+1]; mass η uniform on C=[D-w,D+w].
Continuous, symmetric about D, and for η>0 its median is unique (=D), because F is strictly increasing on C and F(D)=1/2.
Let M = max(sup_K |g_L|, sup_K |g_R|) < ∞ (local boundedness at K=[-1,1]^n) and take D > M (w small).
* All n points in A (prob ((1-η)/2)^n): g_R(X) <= M < D = θ  => θ not in the interval (open or closed).
* All n points in B (prob ((1-η)/2)^n): X = Y + 2D·1 with Y in K, shift invariance gives g_L(X) = g_L(Y)+2D >= 2D-M > D = θ => miss.
* Disjoint events, so P(miss) >= 2((1-η)/2)^n = 2^(1-n)(1-η)^n. Only g_L bounded below and g_R bounded above on K are used.
Hence a valid interval (coverage >= 1-α over all continuous distributions with unique median, or over symmetric ones) needs
α >= 2^(1-n)(1-η)^n for all η>0, i.e. α >= 2^(1-n), i.e. n >= log2(2/α). So **no shift-invariant, locally bounded CI exists for n < log2(2/α)**
(in the symmetric class with strict coverage > 1-α, η=0 is attained and it is also impossible at n = log2(2/α)). The threshold is sharp:
their Thm-1 interval [X_(⌊n/2⌋-c), X_(⌈n/2⌉+c+1)] is shift-invariant, bounded, and valid for n >= log2(2/α).
Where the argument is tight: it is exactly where eq. (5)'s interval escapes — a fixed anchor a breaks g(x+c1)=g(x)+c, so cluster B does not force a miss.
Caveats: (i) the forced-miss events are subsets of the miss event, so the bound is on the (outer) probability if the miss event is non-measurable;
(ii) "shift-invariant" only needs to hold for the single shift c=2D per D (equivariance on the cluster configuration), not as a global property;
(iii) the proof does not cover randomized intervals unless g is allowed to depend on an independent U in a locally bounded, shift-equivariant way (extension is routine, not checked).

## 3. Numerical check (verify_conjecture.py; Monte Carlo 4e5 reps, D=1e4, η=1e-3 — provisional MC, ±~0.001)
* n=3,4,5: min miss over all order-statistic intervals ([X_(i),X_(j)] for all i<=j, mean±c·range for c in 0.5,1,2,5) at θ=D:
  0.2488, 0.1245, 0.0622 vs predicted forced bound 2((1-η)/2)^n = 0.2493, 0.1245, 0.0622 (2^(1-n)=0.25, 0.125, 0.0625). No candidate below the bound.
* Two-cluster (analyst) variant: forced bound is only (1/2-eps)^n, not 2^(1-n) (confirmed analytically; the simulated miss of [X(1),X(n)] there is higher only because the median sits inside the near cluster and the min–max interval misses it often, not because of the cluster event).
* Non-shift-invariant interval of eq. (5), a=0, n=3, α=0.2 (log2(1/α)=2.32 < 3 < log2(2/α)=3.32; threshold ⌊n/2⌋-c_{n,2α}=1): miss 0.1244 / 0.1258 under
  P_{η,D} for η=1e-3 / 0.2, <= α=0.2, while every shift-invariant interval has miss >= 0.249 > α at η=1e-3. This illustrates the gap n in [log2(1/α), log2(2/α)) concretely.
  (Only checked on three-cluster and two-point laws, not a proof of validity; the validity is the paper's (5).)

## 4. Novelty (provisional; screening incomplete)
* Semantic Scholar citations endpoint for arXiv:2403.06357 returned only 2 citing items (a cloud-segmentation paper, and "Merging uncertainty sets via majority vote", arXiv:2401.09379 — neither addresses the conjecture); the index is clearly incomplete/lagging (several 429s). 
* Crossref has no record for the arXiv preprint (title search returned nothing relevant). arXiv API quoted-boolean queries gave zero hits except the paper itself; four web searches (conjecture wording, Lanke 1974 impossibility, finite-population/equivariant median CI) surfaced no paper that proves, refutes, or even discusses the conjecture. arXiv v2 (Jul 2026) still states it as a conjecture.
* Related but not the same: Lanke 1974 (original impossibility, Scand. J. Stat.; claim corrected by Paul–Kuchibhotla); Kuchibhotla–Balakrishnan–Wasserman "Median regularity and honest inference" (arXiv:2206.02954; finite-sample impossibility via median-bias characterisation, mentions nonexistence of finite-sample CIs for mean only);
  Paul–Kuchibhotla "Finite sample valid confidence sets of mode" (arXiv:2503.23711). No finite-population or equivariant-version of the conjectured impossibility found (finite-population median CIs under SRS exist in the survey-sampling literature but are not about this).
* Verdict: no evidence in the retrieved sources that the conjecture has been proved/refuted; the proof above is short and uses a standard cluster/scale argument that is the same device as Lanke's, so it is likely to be easy and plausibly known to the authors or in a later version — treat as "not found taken", not as "verified novel". Did NOT use OpenAlex (per instructions).
