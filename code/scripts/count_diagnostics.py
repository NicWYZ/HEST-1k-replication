#!/usr/bin/env python
"""Stage 4b: count-distribution diagnostics on the benchmark's target panel.

Per (task, gene), on the RAW integer counts stored in instrumentation/<task>/spots.parquet:
  - zero fraction
  - mean, variance, Fano factor (var/mean); Poisson implies Fano = 1
  - method-of-moments NB dispersion
  - marginal (intercept-only) NB vs ZINB fit, compared by BIC

IMPORTANT SCOPE CAVEAT (paper Appendix C.3): these 50 genes per task are the most variable
genes AFTER excluding genes with non-zero counts in under 10% of spots. They are therefore
pre-screened for detection and variance-ranked. Zero fractions here are bounded above by
construction and are NOT representative of the transcriptome. Every statement derived from
this table describes the benchmark's target panel, not spatial transcriptomics counts at large.
"""
import os, warnings, json
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
import statsmodels.api as sm
from statsmodels.discrete.count_model import ZeroInflatedNegativeBinomialP

ROOT = "/work/users/w/e/weiyang/hest_replication"
OUT  = f"{ROOT}/instrumentation"

def fit_bic(y):
    """Intercept-only NB and ZINB; return (bic_nb, bic_zinb, converged flags)."""
    X = np.ones((len(y), 1))
    bic_nb = bic_zi = np.nan; c_nb = c_zi = False
    try:
        m = sm.NegativeBinomial(y, X).fit(disp=0, maxiter=200)
        bic_nb, c_nb = float(m.bic), bool(m.mle_retvals.get("converged", False))
    except Exception:
        pass
    try:
        z = ZeroInflatedNegativeBinomialP(y, X, exog_infl=X).fit(disp=0, maxiter=200)
        bic_zi, c_zi = float(z.bic), bool(z.mle_retvals.get("converged", False))
    except Exception:
        pass
    return bic_nb, bic_zi, c_nb, c_zi

rows = []
for task in sorted(os.listdir(OUT)):
    p = f"{OUT}/{task}/spots.parquet"
    if not os.path.isfile(p):
        continue
    s = pd.read_parquet(p, columns=["gene","count","spot_total_counts"])
    s["gene"] = s.gene.astype(str)
    for gene, g in s.groupby("gene", sort=True):
        y = g["count"].to_numpy(np.float64)
        yi = np.rint(y).astype(np.int64)
        mu, var = float(y.mean()), float(y.var(ddof=1))
        zf = float((yi == 0).mean())
        fano = var / mu if mu > 0 else np.nan
        # method-of-moments NB dispersion: var = mu + alpha*mu^2
        alpha = (var - mu) / (mu**2) if mu > 0 and var > mu else 0.0
        bn, bz, cn, cz = fit_bic(yi)
        rows.append(dict(task=task, gene=gene, n=len(yi), mean=mu, var=var,
                         zero_frac=zf, fano=fano, nb_alpha_mom=alpha,
                         bic_nb=bn, bic_zinb=bz, nb_converged=cn, zinb_converged=cz,
                         delta_bic=(bn - bz) if np.isfinite(bn) and np.isfinite(bz) else np.nan,
                         mean_depth=float(g.spot_total_counts.mean())))
    print(f"[done] {task}: {s.gene.nunique()} genes", flush=True)

d = pd.DataFrame(rows)
d["zinb_preferred"] = d.delta_bic > 0          # BIC_NB - BIC_ZINB > 0 favours ZINB
d["both_converged"] = d.nb_converged & d.zinb_converged
d.to_csv(f"{OUT}/count_diagnostics.csv", index=False)

print("\n=== per-task summary ===")
q = d.groupby("task").agg(
    genes=("gene","size"),
    zero_frac_med=("zero_frac","median"), zero_frac_min=("zero_frac","min"), zero_frac_max=("zero_frac","max"),
    fano_med=("fano","median"), fano_max=("fano","max"),
    zinb_pref=("zinb_preferred","sum"), converged=("both_converged","sum")).round(3)
print(q.to_string())
print("\ngenes with Fano > 1 (overdispersed vs Poisson):",
      int((d.fano > 1).sum()), "/", len(d))
print("genes where ZINB beats NB by BIC (both converged):",
      int((d.zinb_preferred & d.both_converged).sum()), "/", int(d.both_converged.sum()))
print("median delta_BIC (NB - ZINB), converged only:",
      round(float(d.loc[d.both_converged, "delta_bic"].median()), 2))
