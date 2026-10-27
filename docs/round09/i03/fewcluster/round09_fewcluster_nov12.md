# Round 9, track fewcluster, NOV12 on the critical-value certificate

*27 October 2026, late evening. Written by the fewcluster session. NOV12 was pending when `round09_fewcluster_critical_value.md` was committed, and it reported after Nicolas approved its access cards. Its record is `results/round9/fewcluster/novelty/novelty_NOV12_structured.json`, with the queries and candidates CSVs beside it (38 queries).*

## Verdicts

1. **The quadratic-majorant certificate.** Not found in print as stated, provisionally. The method is classical, the Chebyshev and Markov moment-duality technique, which Pinelis (arXiv:1011.6065, read in full) describes for bounding the probability that a quadratic in a self-normalized sum is positive. What is not found is its combination with the exact moments of sampling without replacement, uniformly over the max-share class. The paper should present it as an application of that method and cite Pinelis.
2. **Claim K, critical values over the class.** Anticipated in spirit for other classes, not in this form. There are conservative finite-sample critical values under symmetry from Eaton (1974), Efron (1969), Eaton and Efron (1970), Pinelis (1994) and Dufour and Hallin (1993). Basu and DasGupta (1995) and Hendriks, IJzerman-Boon and Klaassen (2006) give worst cases over symmetric unimodal laws. None treats sampling from a finite population over a class bounding the largest standardized deviation.
3. **The band lemma.** Essentially known. With $u = (\sum y)^2/\sum y^2$ one has $t^2 = (n - 1)u/(n - u)$, so a large $t$ forces the sample into a narrow cone around the constant direction (Hotelling 1961; Efron 1969; Benjamini 1983). Jonsson (Bernoulli 2011, arXiv:1102.2072, Lemma 3.3, read) gives the sharp quantitative form. The checker verified the identity and the inequality on 20,000 random samples. The paper should cite Jonsson for it and not claim it.

## Limits, and sources for Nicolas

Eleven sources were behind paywalls or bot walls and were judged from abstracts and secondary descriptions, so verdicts 1 and 2 stay provisional. The checker did not circumvent the walls. Following Nicolas's rule for papers a session cannot retrieve, these are the ones that matter, with DOIs taken from Crossref on 27 October.

1. Eaton (1974), Annals of Statistics. https://login.libproxy.lib.unc.edu/login?url=https://doi.org/10.1214/aos/1176342725
2. Dufour and Hallin (1993), JASA. https://login.libproxy.lib.unc.edu/login?url=https://doi.org/10.2307/2290795
3. Edelman (1990), JASA. https://login.libproxy.lib.unc.edu/login?url=https://doi.org/10.2307/2289533
4. Efron (1969), JASA. https://login.libproxy.lib.unc.edu/login?url=https://doi.org/10.2307/2286068
5. Eaton and Efron (1970), JASA. https://login.libproxy.lib.unc.edu/login?url=https://doi.org/10.2307/2284581
6. Pinelis (1994), Annals of Statistics. https://login.libproxy.lib.unc.edu/login?url=https://doi.org/10.1214/aos/1176325373
7. Benjamini (1983), JASA. https://login.libproxy.lib.unc.edu/login?url=https://doi.org/10.1080/01621459.1983.10478024
8. Romano (2004), Scandinavian Journal of Statistics. https://login.libproxy.lib.unc.edu/login?url=https://doi.org/10.1111/j.1467-9469.2004.00407.x
9. Lehmann and Loh (1990), reprinted in Selected Works of E. L. Lehmann. https://login.libproxy.lib.unc.edu/login?url=https://doi.org/10.1007/978-1-4614-1412-4_51

Basu and DasGupta (1995) is already in `refs/` and was read by NOV9.

## What changes

`[proposed]` Section 4 of the paper draft keeps its content. In the next version it should credit the certificate's method to Pinelis and the cone geometry to Hotelling, Efron and Jonsson, and claim only the finite-population, max-share application and the computed values. NOV12 also saved 13 paper full texts to the project's private artifact store against its instructions. None is in this repository. They join the files listed in section 3 of `round09_fewcluster_critical_value.md` for Nicolas's decision.
