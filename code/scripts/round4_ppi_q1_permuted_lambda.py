#!/usr/bin/env python
"""Round 4 PPI, Q1.6: lambda of the permuted predictor on CCRCC (plan 11.3, addendum 1 s3).
Imports committed code from the clone only. Outputs go to --out."""
import argparse, os, sys, zlib, json
import numpy as np, pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument("--clone", required=True); ap.add_argument("--suff", required=True)
ap.add_argument("--out", required=True); ap.add_argument("--draws", type=int, default=200)
ap.add_argument("--rules", default="a_b1,b_cluster,c_crossfit")
ap.add_argument("--suffix", default="", help="appended to output file stems, e.g. _d (memo section 3)")
a = ap.parse_args()
sys.path.insert(0, a.clone)
import types, importlib, platform, time
STUBBED = []
class _Stub(types.ModuleType):
    __path__ = []
    def __getattr__(self, k):
        if k.startswith("__"): raise AttributeError(k)
        return _Stub(self.__name__ + "." + k)
    def __call__(self, *x, **y): return None
def _imp(name):
    while True:
        try:
            return importlib.import_module(name)
        except ModuleNotFoundError as e:
            miss = e.name.split(".")[0]
            if miss in STUBBED or miss == name: raise
            sys.modules[miss] = _Stub(miss); STUBBED.append(miss)
E = _imp("round4_ppi_estimator")
B = _imp("round3_b1_ppi")
Q = _imp("round4_ppi_q1_acceptance")
json.dump(dict(stubbed=STUBBED, python=platform.python_version(), numpy=np.__version__, pandas=pd.__version__,
               platform=platform.platform(), node=platform.node(), start=time.strftime("%Y-%m-%dT%H:%M:%S%z")),
          open(os.path.join(a.out, "_env.json") if os.path.isdir(a.out) else "_env.json", "w"))
print("stubbed:", STUBBED, flush=True)
for m in (E, Q, B):
    assert os.path.realpath(m.__file__).startswith(os.path.realpath(a.clone)), m.__file__
os.makedirs(a.out, exist_ok=True)

Q0 = {6: 1.0, 8: 0.86, 12: 0.46}          # Q0 donor-weighted theta2 medians, anchor rerun b1_estimates.csv
NLS = (6, 8, 12); RULES = tuple(a.rules.split(",")); V = "CCRCC"
rows, b1rows, diag, corr = [], [], [], []

def masks(d, Ld):
    Lg = B.group_mask(d, Ld) & d["valid"]
    Ug = (~B.group_mask(d, Ld)) & d["valid"]
    return Lg, Ug

for est in ("theta2", "theta3"):
    for pop in ("spot", "donor"):
        d = B.load_suff(a.suff, V, "permuted", est, pop)
        assert d is not None
        ng = d["S1"].shape[1]
        print(est, pop, "genes", ng, "valid donors", len(d["valid_donors"]), "slides", len(d["slides"]), flush=True)
        for nL in NLS:
            lam = {r: np.full((a.draws, ng), np.nan) for r in RULES}
            for k in range(a.draws):
                tag = f"q1perm|{est}|{pop}|nL{nL}|d{k}"
                Ld = B.draw_L(d["valid_donors"], nL, tag)
                Lg, Ug = masks(d, Ld)
                D, Lm, Um = Q.suff_to_donors(d, Lg, Ug)
                for r in RULES:
                    lam[r][k] = E.lambda_rule(r, pop, D, Lm, Um, seed=tag)["lam"]
            # B1's exact draw
            Ld = B.draw_L(d["valid_donors"], nL, f"{V}|nL{nL}")
            Lg, Ug = masks(d, Ld)
            D, Lm, Um = Q.suff_to_donors(d, Lg, Ug)
            b1 = {r: E.lambda_rule(r, pop, D, Lm, Um, seed=f"{V}|nL{nL}")["lam"] for r in RULES}
            for r in RULES:
                x = lam[r]
                flat = x[np.isfinite(x)]
                med = float(np.median(flat))
                pred = ""
                if r != "a_b1":
                    pred = (f"|median|<=0.1: {abs(med) <= 0.1}" if not r.startswith("d")
                            else (f"memo s3 donor median == 0: {med == 0.0}" if pop == "donor"
                                  else f"memo s3 spot median < 0.1: {med < 0.1}"))
                elif pop == "donor" and est == "theta2":
                    pred = f"Q0 figure {Q0[nL]}; B1-draw median {np.nanmedian(b1[r]):.4f}; draws median {med:.4f}"
                rows.append(dict(estimand=est, population=pop, n_L=nL, rule=r, median=med,
                                 q25=float(np.quantile(flat, .25)), q75=float(np.quantile(flat, .75)),
                                 median_of_draw_medians=float(np.median(np.nanmedian(x, axis=1))),
                                 frac_le_0p05=float((flat <= 0.05).mean()), n_cells=int(flat.size),
                                 n_nan=int(np.isnan(x).sum()), n_genes=ng, n_draws=a.draws,
                                 target="design", pred_Q1_6=pred))
                b1rows.append(dict(estimand=est, population=pop, n_L=nL, rule=r,
                                   b1_draw_median_over_genes=float(np.nanmedian(b1[r])),
                                   q0_figure=(Q0[nL] if (r == "a_b1" and pop == "donor" and est == "theta2") else np.nan),
                                   labelled=";".join(map(str, Ld)), n_genes=ng))
            # diagnostic at B1's draw (donor pairs quantities), donor pop only
            if pop == "donor":
                t, tf = E.donor_values(D)
                GL, GU = Lm.sum(0), Um.sum(0)
                tLm = E._m(t, Lm) / GL; tfLm = E._m(tf, Lm) / GL; tfUm = E._m(tf, Um) / GU
                aL = np.where(Lm, t - tLm, 0.0); bL = np.where(Lm, tf - tfLm, 0.0); dU = np.where(Um, tf - tfUm, 0.0)
                cU = GU / (GU - 1.0); cL = GL / (GL - 1.0)
                num = cL * (aL * bL).sum(0) / GL ** 2
                denU = cU * (dU ** 2).sum(0) / GU ** 2
                denL = cL * (bL ** 2).sum(0) / GL ** 2
                vt = cL * (aL ** 2).sum(0) / GL ** 2
                # correlation over labelled donors
                ca = np.sqrt((aL ** 2).sum(0) * (bL ** 2).sum(0))
                cor = (aL * bL).sum(0) / np.where(ca > 0, ca, np.nan)
                # common donor component: share of variance of donor x gene matrix explained by rank 1 (all valid donors)
                keep = (Lm | Um)[:, 0]
                def r1share(M):
                    X = M[keep]; X = X - X.mean(0, keepdims=True)
                    s = np.linalg.svd(X, compute_uv=False); return float(s[0] ** 2 / (s ** 2).sum())
                diag.append(dict(estimand=est, n_L=nL, n_genes=ng, G_L=int(GL[0]), G_U=int(GU[0]),
                                 med_numerator=float(np.nanmedian(num)), med_denU=float(np.nanmedian(denU)),
                                 med_denL=float(np.nanmedian(denL)), med_var_t_L=float(np.nanmedian(vt)),
                                 med_ratio_num_over_den=float(np.nanmedian(num / (denU + denL))),
                                 frac_genes_num_positive=float((num > 0).mean()),
                                 med_corr_t_tf_L=float(np.nanmedian(cor)), frac_genes_corr_positive=float((cor > 0).mean()),
                                 rank1_share_t=r1share(t), rank1_share_tf=r1share(tf),
                                 med_abs_corr_tf_donormean=None))
                for j in (0, ng // 2, ng - 1):
                    corr.append(dict(estimand=est, n_L=nL, gene=d["genes"][j], gene_index=j,
                                     corr_t_tf_labelled=float(cor[j]), numerator=float(num[j]),
                                     denU=float(denU[j]), denL=float(denL[j]), lambda_a=float(b1["a_b1"][j])))
                # the same ingredients for ALL valid donors (not only labelled): correlation of t, tf
                tv, tfv = t[keep], tf[keep]
                cc = [np.corrcoef(tv[:, j], tfv[:, j])[0, 1] for j in range(ng)]
                diag[-1]["med_corr_t_tf_all_valid_donors"] = float(np.nanmedian(cc))
                diag[-1]["frac_genes_corr_all_positive"] = float(np.nanmean(np.array(cc) > 0))
                diag[-1].pop("med_abs_corr_tf_donormean")
            print(est, pop, nL, "done", flush=True)

pd.DataFrame(rows).to_csv(f"{a.out}/q1_permuted_lambda{a.suffix}.csv", index=False)
pd.DataFrame(b1rows).to_csv(f"{a.out}/q1_permuted_lambda_b1draw{a.suffix}.csv", index=False)
pd.DataFrame(diag).to_csv(f"{a.out}/q1_permuted_lambda_diagnostic{a.suffix}.csv", index=False)
pd.DataFrame(corr).to_csv(f"{a.out}/q1_permuted_lambda_diagnostic_genes{a.suffix}.csv", index=False)
print(pd.DataFrame(rows).drop(columns=["pred_Q1_6"]).round(3).to_string())
print(pd.DataFrame(b1rows).drop(columns=["labelled"]).round(3).to_string())
print(pd.DataFrame(diag).round(4).to_string())
