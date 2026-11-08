# Round 10, track `ledger`, L2 reads, part 2: Williams, Mickey's corrigenda and the open sources

*8 November 2026. Written by the oversight chat under `docs/round10/i01/ledger/round10_ledger_brief.md`, stage L2, continuing `round10_ledger_L2_reads_part1.md`. Section 1 was read by the oversight chat itself from the two files Nicolas supplied on 8 November (`williams.pdf` replaced, `mickey_correction.pdf`). The open sources of part 1's section 4 are read by Opus subagents through the built-in browser on Nicolas's Mac, which reached arXiv and JSTOR on 8 November, and are added in section 2 when they return. Full notes are in the claude.ai project docs (`claude/round10_L2_notes_*.md`).*

## 1. Williams (1961) and Mickey's corrigenda (1960)

**Williams, W. H. (1961).** "Generating unbiased ratio and regression estimators", Biometrics 17(2), 267 to 274, JSTOR stable 2527992, DOI 10.2307/2527992 (from the JSTOR PDF; the stable URL and pages are printed on its cover page). Read level: in full, sections 1 to 7 and references. Equations (1), (2), (12) and (13) and section 3's ratio were checked against the page images of pp. 268, 269 and 273.

1. **The estimator.** Equation (2) is
$$
T_k = \bar y + \bar b(\mu_X - \bar x) + \Big(1 - \frac{n}{N}\Big)\frac{1}{k(k - 1)}\sum_{i=1}^{k}\big(b^i - \bar b\big)\big(\bar x^i - \bar x\big),
$$
where $b^i$ is any function of group $i$ and $\bar b = \sum_i b^i/k$. Its correction term is $(1 - n/N)$ times the unbiased estimator (1) of $\text{Cov}(\bar b, \bar x)$. This matches round 8's transcription (`docs/round08/i01/positioning/round08_positioning_note.md`, section 3.2). It is unbiased for any form of the coefficient (p. 268).
2. **The variance estimator.** Section 6 (p. 273) first assumes "a negligible $n/N$ (or $k/s$) and a fixed set of uncorrelated groups", rewrites $T_k$ as (12), $T_k = \bar y - \frac{1}{k(k-1)}\sum_{i \ne j} b^i(\bar x^j - \mu_X)$, and gives
$$
v(T_k) = T_k^2 - \frac{1}{k(k - 1)}\sum_{i \ne j}\bar y^i\bar y^j \qquad (13),
$$
unbiased under that assumption, with the warning that it can have high sampling error for small $k$. So Williams' own variance estimator needs $n/N$ negligible. The estimator from Mickey's section 4 in part 1 (section 1, item 1) needs no such assumption.
3. **Section 3.** Under a linear model with normal $x$ and the least-squares slope (3), $V(\hat y_b)/V(T_2) = (n - 2)(n - 6)/\{(n - 3)(n - 4)\}$ for $n > 6$, printed as 0.89 and 0.95 at $n$ of 15 and 25 (recomputed: 0.886 and 0.946). As $k$ varies the ratio is largest at $k = \sqrt{n/3}$ (confirmed on the page image, so L1 S4 B9's statement stands).
4. **Other sections.** Section 4 gives a combined stratified form (7) with an overall slope (5). Section 5 gives two-stage sampling of equal-sized primaries (11), conditionally unbiased for the mean of the selected primaries. Section 7's toy population of six pairs gives exact variances 7.914, 2.281 and 1.886 for $\bar y$, $T_2$ and $T_2^\ast$ (p. 274).
5. **Citations.** Williams cites Cochran (1953), Goodman and Hartley (1958), Hartley and Ross (1954), Nieto (1958) and Robson (1957). He does not cite Mickey (1959), whose class contains his $k = 2$ form (part 1, section 1, item 1). The two are independent constructions of the same estimator, and Mickey's is the earlier in print.

**Mickey, M. R. (1960).** "Corrigenda: Some finite population unbiased ratio and regression estimators", JASA 55(292), p. 755, December 1960, JSTOR stable 2281602, DOI 10.2307/2281602. Read in full. Mickey withdraws the claim (p. 595 of the 1959 paper) that the variable-probability part gives new estimators. He credits the results of pp. 604 and 605 to Des Raj (JASA 51, 1956, 269 to 284), and those of p. 606 to Murthy (Sankhya 18, 1957, 379 to 390). Nothing in sections 2 to 5 is corrected, so part 1's reading of sections 2 and 4 for question E stands. If the paper ever cites Mickey's section 6, it cites Des Raj and Murthy for it.

**Effect.** With both read, nothing in the sources blocks the decision on question E at L3. The `[proposed]` variance estimator of part 1 (section 1, item 1) is still waiting for Nicolas's look, a to-do he set aside on 8 November.

## 2. The open sources

*To be added when the five reading subagents return.*
