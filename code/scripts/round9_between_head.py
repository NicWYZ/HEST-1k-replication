"""Round 9 (claude-science): does a between-donor head predict donor means better than the pooled spot-level head?

Inputs (outside the repository, derived from gated data): C0 cluster summaries (donor x gene means of y and of the
existing leave-donor-out spot predictions f) and C1 donor-mean embeddings over the same joined spots.
Predictors of the donor mean ybar_g, all scored out of sample:
  pooled  : a + c * fbar_g, (a, c) fitted on the training donors (recalibrated pooled head)
  between : ridge of ybar on the top-k PCs of donor-mean embeddings (PCA on all donors, label-free)
  shrink  : pooled + ridge of the pooled residual on the same PCs (between block shrunk toward the pooled head)
Ridge penalty per gene chosen by exact inner leave-one-out on the training donors.
Designs: lodo (train on G-1 donors) and train8 (train on 8 random donors, score the rest; 200 repeats).
Usage: python round9_between_head.py <c0_csv_gz> <c1_dir> <outdir>
"""
import sys, glob, numpy as np, pandas as pd

LAMS = np.logspace(-3, 3, 25)

def ridge_fit_predict(X, Y, Xnew):
    xm, ym = X.mean(0), Y.mean(0)
    Xc, Yc = X - xm, Y - ym
    U, s, Vt = np.linalg.svd(Xc, full_matrices=False)
    n = X.shape[0]
    UtY = U.T @ Yc
    best = np.full(Y.shape[1], np.inf); bestB = np.zeros((X.shape[1], Y.shape[1]))
    for lam in LAMS:
        lam_s = lam * (s ** 2).mean()
        dd = s ** 2 / (s ** 2 + lam_s)
        H_diag = (U ** 2) @ dd + 1.0 / n
        fit = U @ (dd[:, None] * UtY)
        err = (((Yc - fit) / (1 - H_diag)[:, None]) ** 2).sum(0)
        B = Vt.T @ ((s / (s ** 2 + lam_s))[:, None] * UtY)
        upd = err < best
        best[upd] = err[upd]; bestB[:, upd] = B[:, upd]
    return ym + (Xnew - xm) @ bestB

def line_fit_predict(F, Y, Fnew):
    out = np.empty((Fnew.shape[0], Y.shape[1]))
    for j in range(Y.shape[1]):
        coef = np.linalg.lstsq(np.column_stack([np.ones(F.shape[0]), F[:, j]]), Y[:, j], rcond=None)[0]
        out[:, j] = coef[0] + coef[1] * Fnew[:, j]
    return out

def run(Y, F, M, train_sets, k):
    Mc = M - M.mean(0)
    U, s, Vt = np.linalg.svd(Mc, full_matrices=False)
    P = U[:, :k] * s[:k]
    ss = {a: np.zeros(Y.shape[1]) for a in ("constant", "pooled", "between", "shrink")}
    sst = np.zeros(Y.shape[1])
    for tr, te in train_sets:
        Yt = Y[tr]
        pc = line_fit_predict(F[tr], Yt, F[te])
        rb = ridge_fit_predict(P[tr], Yt, P[te])
        res_tr = Yt - line_fit_predict(F[tr], Yt, F[tr])
        rs = pc + ridge_fit_predict(P[tr], res_tr, P[te])
        ss["constant"] += ((Y[te] - Yt.mean(0)) ** 2).sum(0)
        ss["pooled"] += ((Y[te] - pc) ** 2).sum(0)
        ss["between"] += ((Y[te] - rb) ** 2).sum(0)
        ss["shrink"] += ((Y[te] - rs) ** 2).sum(0)
        sst += ((Y[te] - Y.mean(0)) ** 2).sum(0)
    return ss, sst

if __name__ == "__main__":
    c0, c1dir, outdir = sys.argv[1:4]
    d = pd.read_csv(c0)
    rng = np.random.default_rng(20261025)
    rows = []
    for path in sorted(glob.glob(f"{c1dir}/c1_donor_mean_emb__*.npz")):
        _, task, enc = path.split("/")[-1][:-4].split("__")
        z = np.load(path, allow_pickle=True)
        donors = [str(x) for x in z["donors"]]; M = z["M"]
        g = d[(d.task == task) & (d.encoder == enc)]
        Yd = g.pivot(index="donor", columns="gene", values="mean_y").loc[donors]
        Fd = g.pivot(index="donor", columns="gene", values="mean_f").loc[donors]
        Y, F = Yd.values, Fd.values
        G = len(donors)
        designs = {"lodo": [(np.setdiff1d(np.arange(G), [h]), np.array([h])) for h in range(G)]}
        sets = []
        for _ in range(200):
            tr = np.sort(rng.choice(G, 8, replace=False)); sets.append((tr, np.setdiff1d(np.arange(G), tr)))
        designs["train8"] = sets
        for dn, sets in designs.items():
            kk = min(G - 3, 10) if dn == "lodo" else 5
            ss, sst = run(Y, F, M, sets, kk)
            for j, gene in enumerate(Yd.columns):
                rows.append(dict(task=task, encoder=enc, design=dn, k=kk, gene=gene,
                                 **{f"R2_{a}": 1 - ss[a][j] / sst[j] for a in ss}))
        print(task, enc, G, flush=True)
    out = pd.DataFrame(rows)
    out.to_csv(f"{outdir}/between_head_by_gene.csv", index=False)
    med = out.groupby(["task", "encoder", "design"])[["R2_constant", "R2_pooled", "R2_between", "R2_shrink"]].median().round(3)
    med.to_csv(f"{outdir}/between_head_medians.csv")
    print(med.to_string())
