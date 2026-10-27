"""Semi-synthetic check on real CCRCC uni_v2 patch embeddings. Aggregates only are written.
x = real embeddings (global column standardisation), groups = real donors, f=x'beta (random direction), eta_d, e simulated.
Usage: python f_LLGCLUSTER_ccrcc_semisynth.py <R> <outdir>"""
import sys, glob, json, os, numpy as np, pandas as pd, h5py, pyarrow.parquet as pq
R, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
TASK, ENC = "CCRCC", "uni_v2"
pqf = f"{R}/results/round3/B1_ppi/b1_predictions__{TASK}__{ENC}.parquet"
sch = pq.ParquetFile(pqf).schema_arrow.names
ycols = [c for c in sch if c.startswith("y__")]
t = pq.read_table(pqf, columns=["sample_id", "donor_id"] + ycols).to_pandas()
samp2don = t.drop_duplicates("sample_id").set_index("sample_id")["donor_id"].astype(str).to_dict()
# donor-shift share of variance of the real label (aggregate over genes): between-donor variance of donor means / total variance
sh = []
for c in ycols:
    y = t[c].values.astype(float); m = pd.Series(y).groupby(t.donor_id.values).transform("mean").values
    sh.append(m.var() / y.var())
s_real = float(np.nanmean(sh)); print("mean between-donor share over genes", s_real, "median", float(np.nanmedian(sh)), flush=True)
pd.DataFrame([dict(task=TASK, n_genes=len(ycols), mean_between_donor_share=s_real, median=float(np.nanmedian(sh)),
                   q10=float(np.nanquantile(sh, .1)), q90=float(np.nanquantile(sh, .9)))]).to_csv(out + "/ccrcc_donor_share.csv", index=False)
# embeddings
files = sorted(glob.glob(f"{R}/embeddings/{TASK}/{ENC}/*.h5"))
print(len(files), "embedding files", flush=True)
with h5py.File(files[0], "r") as h:
    print({k: (h[k].shape, h[k].dtype) for k in h.keys()}, flush=True)
def load(f):
    with h5py.File(f, "r") as h:
        for k in ["features", "embeddings", "emb", "X", "feats"]:
            if k in h: return np.asarray(h[k])
        for k in h.keys():
            if h[k].ndim == 2 and h[k].shape[1] > 100: return np.asarray(h[k])
rng0 = np.random.default_rng(7)
bydon = {}
for f in files:
    sid = os.path.basename(f)[:-3]
    if sid not in samp2don: continue
    E = load(f); bydon.setdefault(samp2don[sid], []).append(E)
dons = sorted(bydon); print(len(dons), "donors with embeddings", flush=True)
CAP = 400
pool = {}
for d in dons:
    E = np.vstack(bydon[d]); n_av = len(E)
    idx = rng0.choice(n_av, min(n_av, CAP), replace=False); pool[d] = (E[idx].astype(np.float64), n_av)
allx = np.vstack([pool[d][0] for d in dons]); mu, sd = allx.mean(0), allx.std(0) + 1e-8
for d in dons: pool[d] = ((pool[d][0] - mu) / sd, pool[d][1])
p = allx.shape[1]; print("p", p, flush=True)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from f_LLGCLUSTER_sim import llg, ridge_pred
avail = np.array([pool[d][1] for d in dons], float)
REPS = 150; G = len(dons) // 2
rows = []
for s in [0.0, round(min(max(s_real, 0.05), 0.6), 3), 0.6]:
    for unequal in [False, True]:
        for variant in ["clus", "twin"]:
            for r in range(REPS):
                rng = np.random.default_rng(abs(hash((s, unequal, variant, r))) % (2**31) if False else int(1e3*s)*1009 + int(unequal)*7919 + (variant == "twin")*104729 + r*15485863 % (2**31))
                perm = rng.permutation(len(dons)); tr, te = perm[:G], perm[G:2*G]
                u = rng.standard_normal(p); u /= np.linalg.norm(u)
                # population variances from the full pool (all donors, <=CAP spots each) for beta direction u
                fp = np.concatenate([pool[dons[i]][0] @ u for i in range(len(dons))])
                gp = np.concatenate([np.full(len(pool[dons[i]][0]), i) for i in range(len(dons))])
                vf = fp.var(); dm = pd.Series(fp).groupby(gp).transform("mean").values; vw = (fp - dm).var()
                c = np.sqrt(0.2 / vf); beta = c * u; vf, vw = 0.2, vw * c * c
                sig2e = 0.8 - s; R2tot = 0.2 / 1.0; R2w = vw / (vw + sig2e)
                def mk(idx):
                    X = []; y = []; g = []
                    for k, i in enumerate(idx):
                        E = pool[dons[i]][0]
                        n = 30 if not unequal else int(np.clip(round(avail[i] / avail.mean() * 30), 5, 120))
                        n = min(n, len(E)); sel = rng.choice(len(E), n, replace=False)
                        Xi = E[sel]; f = Xi @ beta
                        eta = np.sqrt(s) * (rng.standard_normal(n) if variant == "twin" else rng.standard_normal() * np.ones(n))
                        X.append(Xi); y.append(f + eta + np.sqrt(sig2e) * rng.standard_normal(n)); g.append(np.full(n, k))
                    return np.vstack(X), np.concatenate(y), np.concatenate(g)
                X, y, g = mk(tr); Xo, yo, go = mk(te)
                L, parts = llg(X, Xo); fh = ridge_pred(parts, Xo, y)
                R2 = 1 - ((yo - fh) ** 2).mean() / (yo ** 2).mean()
                rows.append(dict(s=s, unequal=unequal, variant=variant, rep=r, R2oos=R2, L=L, B=(R2 + L) / (1 + L), R2tot=R2tot, R2within=R2w, N=len(y)))
    print("done s", s, flush=True)
df = pd.DataFrame(rows)
agg = df.groupby(["s", "unequal", "variant"]).apply(lambda d: pd.Series(dict(
    n=len(d), N_mean=d.N.mean(), L_mean=d.L.mean(), R2oos_mean=d.R2oos.mean(), B_mean=d.B.mean(), B_sd=d.B.std(),
    R2tot=d.R2tot.iloc[0], R2within_mean=d.R2within.mean(),
    p_B_gt_tot=(d.B > d.R2tot).mean(), p_B_gt_within=(d.B > d.R2within).mean(),
    gap_tot_mean=(d.B - d.R2tot).mean(), mc_se_gap=d.B.std() / np.sqrt(len(d))))).reset_index()
agg.to_csv(out + "/ccrcc_semisynth_aggregate.csv", index=False); print(agg.to_string(), flush=True)
