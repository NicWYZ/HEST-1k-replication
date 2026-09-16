#!/usr/bin/env python
"""Stage 4b: count-distribution diagnostics on the benchmark's target panel.

Per (task, gene), on the RAW integer counts stored in instrumentation/<task>/spots.parquet:
  - zero fraction
  - mean, variance, Fano factor (var/mean); Poisson implies Fano = 1
  - method-of-moments NB dispersion
  - marginal (intercept-only) POISSON, NB and ZINB fits, compared by AIC

Handoff 4c specifies "per-gene maximum-likelihood fits of Poisson, NB, and ZINB with AIC" and
"tabulate how often ZINB is preferred over NB". A first version fit only NB and ZINB and compared
them by BIC. Both are now corrected: Poisson is included as the no-overdispersion reference, and
AIC is the reported criterion. BIC is retained alongside because it penalises the extra ZINB
parameter more heavily, so reporting both shows whether the NB-vs-ZINB verdict is criterion-
dependent -- it should not be, and saying so requires having computed it.

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

def fit_ic(y):
    """Intercept-only Poisson, NB and ZINB. Returns AIC and BIC for each plus converged flags.

    Poisson has no dispersion parameter, so AIC_poisson - AIC_nb quantifies the evidence for
    overdispersion; the Fano factor says the same thing without a likelihood."""
    X = np.ones((len(y), 1))
    out = dict(aic_pois=np.nan, bic_pois=np.nan, aic_nb=np.nan, bic_nb=np.nan,
               aic_zinb=np.nan, bic_zinb=np.nan,
               pois_converged=False, nb_converged=False, zinb_converged=False)
    try:
        p = sm.Poisson(y, X).fit(disp=0, maxiter=200)
        out.update(aic_pois=float(p.aic), bic_pois=float(p.bic),
                   pois_converged=bool(p.mle_retvals.get("converged", False)))
    except Exception:
        pass
    try:
        m = sm.NegativeBinomial(y, X).fit(disp=0, maxiter=200)
        out.update(aic_nb=float(m.aic), bic_nb=float(m.bic),
                   nb_converged=bool(m.mle_retvals.get("converged", False)))
    except Exception:
        pass
    try:
        z = ZeroInflatedNegativeBinomialP(y, X, exog_infl=X).fit(disp=0, maxiter=200)
        out.update(aic_zinb=float(z.aic), bic_zinb=float(z.bic),
                   zinb_converged=bool(z.mle_retvals.get("converged", False)))
    except Exception:
        pass
    return out

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
        ic = fit_ic(yi)
        rows.append(dict(task=task, gene=gene, n=len(yi), mean=mu, var=var,
                         zero_frac=zf, fano=fano, nb_alpha_mom=alpha,
                         **ic,
                         delta_aic=(ic["aic_nb"] - ic["aic_zinb"]),
                         delta_bic=(ic["bic_nb"] - ic["bic_zinb"]),
                         delta_aic_overdisp=(ic["aic_pois"] - ic["aic_nb"]),
                         mean_depth=float(g.spot_total_counts.mean())))
    print(f"[done] {task}: {s.gene.nunique()} genes", flush=True)

d = pd.DataFrame(rows)
# handoff 4c reports the AIC verdict; BIC is kept to show the verdict is not criterion-dependent
d["zinb_preferred"]     = d.delta_aic > 0      # AIC_NB - AIC_ZINB > 0 favours ZINB
d["zinb_preferred_bic"] = d.delta_bic > 0
d["nb_beats_poisson"]   = d.delta_aic_overdisp > 0
d["both_converged"] = d.nb_converged & d.zinb_converged
d.to_csv(f"{OUT}/count_diagnostics_v2.csv", index=False)

print("\n=== per-task summary ===")
q = d.groupby("task").agg(
    genes=("gene","size"),
    zero_frac_med=("zero_frac","median"), zero_frac_min=("zero_frac","min"), zero_frac_max=("zero_frac","max"),
    fano_med=("fano","median"), fano_max=("fano","max"),
    zinb_pref=("zinb_preferred","sum"), converged=("both_converged","sum")).round(3)
print(q.to_string())
print("\ngenes with Fano > 1 (overdispersed vs Poisson):",
      int((d.fano > 1).sum()), "/", len(d))
print("genes where NB beats Poisson by AIC (overdispersion):",
      int((d.nb_beats_poisson & d.pois_converged & d.nb_converged).sum()), "/",
      int((d.pois_converged & d.nb_converged).sum()))
print("genes where ZINB beats NB by AIC (both converged):",
      int((d.zinb_preferred & d.both_converged).sum()), "/", int(d.both_converged.sum()))
print("same verdict under BIC:",
      int((d.zinb_preferred == d.zinb_preferred_bic).sum()), "/", len(d))
print("genes where ZINB beats NB by BIC (both converged):",
      int((d.zinb_preferred & d.both_converged).sum()), "/", int(d.both_converged.sum()))
print("median delta_AIC (NB - ZINB), converged only:",
      round(float(d.loc[d.both_converged, "delta_aic"].median()), 2))
print("median delta_AIC (Poisson - NB):",
      round(float(d.loc[d.pois_converged & d.nb_converged, "delta_aic_overdisp"].median()), 1))
