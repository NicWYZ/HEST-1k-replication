"""Round 7 federated learning track, interval i02: data loading, the exact head, the faithful
head and the metrics, shared by F3.0, V1, V2, V3 and V4.

Settings are those of amendment A3 of docs/round07/tracks/fedlearn/round07_fedlearn_plan.md.

The exact head (instruction section 2.3). Every quantity comes from per-center sums in float64,
held in a Stats object: n, sx = sum x, sy = sum y, Sxx = sum x x^T, Sxy = sum x y^T. The pooled
mean and population standard deviation of each embedding dimension come from the same sums. The
basis V is the top-k eigenvectors of the standardised centred cross-product matrix (numpy eigh,
float64), and the ridge is a Cholesky solve on unnormalised sums with lambda = 100 / (k q), the
faithful head's penalty. Predictions add the mean expression back.

The faithful head replicates HEST-bench's predict_single_split: StandardScaler and PCA(256,
random_state=1) on float32 embeddings, cast to float32, then sklearn Ridge(solver="lsqr",
fit_intercept=False, max_iter=1000) with the same lambda.
"""
import json
import os
import zlib

import h5py
import numpy as np
from scipy.linalg import cho_factor, cho_solve

ROOT = "/work/users/w/e/weiyang/hest_replication"
K_PC = 256
LAM_NUM = 100.0
MIN_SLIDE_SPOTS = 50


# ----------------------------------------------------------------------------- seeds
def rng_for(*parts):
    return np.random.default_rng(zlib.crc32("|".join(str(p) for p in parts).encode()))


# ----------------------------------------------------------------------------- task data
def load_td(clone, rel):
    return json.load(open(os.path.join(clone, rel)))


def donor_units(td):
    """sample_id -> donor unit. CCRCC merges INT24 into INT4 (instruction F3 V1)."""
    m = {s["sample_id"]: str(s["donor_id"]) for s in td["samples"]}
    if td["task"] == "CCRCC":
        m = {k: ("INT4" if v == "INT24" else v) for k, v in m.items()}
    return m


def emb_path(td, sid, enc):
    return f"{ROOT}/{td['paths']['embeddings'].format(encoder=enc, sample_id=sid)}"


def adata_path(td, sid):
    return f"{ROOT}/{td['paths']['adata'].format(sample_id=sid)}"


def read_barcodes_and_X(path):
    with h5py.File(path, "r") as f:
        k = "barcodes" if "barcodes" in f else "barcode"
        b = np.asarray(f[k][:]).reshape(-1)
        bc = [x.decode() if isinstance(x, (bytes, np.bytes_)) else str(x) for x in b]
        X = np.asarray(f["embeddings"][:], dtype=np.float32)
    return bc, X


def read_raw_adata(td, sid, bc):
    import anndata as ad
    A = ad.read_h5ad(adata_path(td, sid))
    return A[bc].copy()


def load_expression(td, sid, bc, genes):
    """log(1 + count) of the h5ad matrix on the embedding file's spots and the given genes."""
    import anndata as ad
    A = ad.read_h5ad(adata_path(td, sid))
    missing = [g for g in genes if g not in A.var_names]
    assert not missing, f"{sid}: {len(missing)} target genes absent, first {missing[:3]}"
    sub = A[bc, genes]
    Y = sub.X.toarray() if hasattr(sub.X, "toarray") else np.asarray(sub.X)
    return np.log1p(np.asarray(Y, dtype=np.float64)).astype(np.float32)


def load_samples(td, sids, enc, genes):
    """dict sid -> (X float32, Y float32, barcodes)."""
    out = {}
    for sid in sids:
        bc, X = read_barcodes_and_X(emb_path(td, sid, enc))
        out[sid] = (X, load_expression(td, sid, bc, genes), bc)
    return out


def select_genes(td, sids, enc, k=50):
    """HEST's get_k_genes (criteria var, min_cells_pct 0.10) on the given samples' patched spots,
    through code/scripts/round2_r2_gene_check.py."""
    from round2_r2_gene_check import get_k_genes
    # Outside CCRCC the task definition's target list is the candidate panel (the gene intersection,
    # or for Xenium the panel without control features); selection is restricted to it.
    panel = None if td["task"] == "CCRCC" else list(td["target_genes"]["list"])
    adatas = []
    for sid in sids:
        bc, _ = read_barcodes_and_X(emb_path(td, sid, enc))
        A = read_raw_adata(td, sid, bc)
        if panel is not None:
            A = A[:, [g for g in panel if g in A.var_names]].copy()
        adatas.append(A)
    genes, n_common = get_k_genes(adatas, k=k)
    return list(genes), int(n_common)


# ----------------------------------------------------------------------------- sums
class Stats:
    __slots__ = ("n", "sx", "sy", "Sxx", "Sxy")

    def __init__(self, n, sx, sy, Sxx, Sxy):
        self.n, self.sx, self.sy, self.Sxx, self.Sxy = n, sx, sy, Sxx, Sxy

    @classmethod
    def of(cls, X, Y):
        X = np.asarray(X, dtype=np.float64)
        Y = np.asarray(Y, dtype=np.float64)
        return cls(float(len(X)), X.sum(0), Y.sum(0), X.T @ X, X.T @ Y)

    def __add__(self, o):
        return Stats(self.n + o.n, self.sx + o.sx, self.sy + o.sy, self.Sxx + o.Sxx, self.Sxy + o.Sxy)

    def centred(self):
        """The sums of the same rows after subtracting their own mean embedding."""
        m = self.sx / self.n
        return Stats(self.n, np.zeros_like(self.sx), self.sy.copy(),
                     self.Sxx - self.n * np.outer(m, m), self.Sxy - np.outer(m, self.sy))

    @property
    def mean_x(self):
        return self.sx / self.n

    @property
    def mean_y(self):
        return self.sy / self.n


def total(stats_list):
    t = stats_list[0]
    for s in stats_list[1:]:
        t = t + s
    return t


# ----------------------------------------------------------------------------- the exact head
def _lam(q, k=K_PC):
    return LAM_NUM / (k * q)


def basis_from(st, k=K_PC):
    N = st.n
    mx = st.sx / N
    C = st.Sxx - N * np.outer(mx, mx)
    var = np.clip(np.diag(C) / N, 0.0, None)
    sd = np.sqrt(var)
    sd[sd == 0] = 1.0
    Cz = C / np.outer(sd, sd)
    Cz = 0.5 * (Cz + Cz.T)
    w, U = np.linalg.eigh(Cz)
    idx = np.argsort(w)[::-1][: min(k, len(w))]
    return mx, sd, U[:, idx], Cz


class Head:
    """Linear prediction y = intercept + ((x - mx) / sd) V B."""

    def __init__(self, mx, sd, V, B, intercept, kind, alphas=None):
        self.mx, self.sd, self.V, self.B, self.intercept, self.kind = mx, sd, V, B, intercept, kind
        self.alphas = alphas or {}

    def scores(self, X):
        return ((np.asarray(X, dtype=np.float64) - self.mx) / self.sd) @ self.V

    def predict(self, X, center=None):
        a = self.alphas.get(center, self.intercept) if center is not None else self.intercept
        return a + self.scores(X) @ self.B


def _solve(A, Bv):
    c, low = cho_factor(A)
    return cho_solve((c, low), Bv)


def fit_exact(st, k=K_PC, lam=None, basis=None):
    """The exact pooled head from a Stats object (instruction section 2.3)."""
    mx, sd, V, Cz = basis if basis is not None else basis_from(st, k)
    N = st.n
    my = st.sy / N
    q = len(my)
    lam = _lam(q, V.shape[1]) if lam is None else lam
    if basis is not None:
        C = st.Sxx - N * np.outer(st.sx / N, st.sx / N)
        Cz = C / np.outer(sd, sd)
        mx_fit = st.sx / N
        # centring for the ridge is on the fitting rows' own mean, expressed in the basis frame
        Czy = (st.Sxy - N * np.outer(mx_fit, my)) / sd[:, None]
        A = V.T @ Cz @ V + lam * np.eye(V.shape[1])
        B = _solve(A, V.T @ Czy)
        icpt = my - (((mx_fit - mx) / sd) @ V) @ B
        return Head(mx, sd, V, B, icpt, "exact")
    Czy = (st.Sxy - N * np.outer(mx, my)) / sd[:, None]
    A = V.T @ Cz @ V + lam * np.eye(V.shape[1])
    B = _solve(A, V.T @ Czy)
    return Head(mx, sd, V, B, my, "exact")


def fit_exact_pooled_arrays(X, Y, k=K_PC):
    """The same head computed from pooled spot arrays, not sums, for the F3.0 anchor."""
    X = np.asarray(X, dtype=np.float64)
    Y = np.asarray(Y, dtype=np.float64)
    mx = X.mean(0)
    sd = X.std(0)
    sd[sd == 0] = 1.0
    Xc = (X - mx) / sd
    Cz = Xc.T @ Xc
    Cz = 0.5 * (Cz + Cz.T)
    w, U = np.linalg.eigh(Cz)
    V = U[:, np.argsort(w)[::-1][:k]]
    my = Y.mean(0)
    Z = Xc @ V
    A = Z.T @ Z + _lam(Y.shape[1], V.shape[1]) * np.eye(V.shape[1])
    B = _solve(A, Z.T @ (Y - my))
    return Head(mx, sd, V, B, my, "exact_pooled_arrays")


def fit_intercept(stats_by_center, k=K_PC):
    """Federated head with center-specific intercepts: basis from the pooled sums, slopes from
    within-center centred sums, alpha_k = mean_y_k - mean_score_k B. A center not in the fit gets
    the spot-weighted mean of the alphas."""
    centers = list(stats_by_center)
    tot = total([stats_by_center[c] for c in centers])
    mx, sd, V, _ = basis_from(tot, k)
    q = len(tot.sy)
    W = np.zeros_like(tot.Sxx)
    Wy = np.zeros_like(tot.Sxy)
    for c in centers:
        s = stats_by_center[c]
        m = s.sx / s.n
        W += s.Sxx - s.n * np.outer(m, m)
        Wy += s.Sxy - s.n * np.outer(m, s.sy / s.n)
    Wz = W / np.outer(sd, sd)
    Wzy = Wy / sd[:, None]
    A = V.T @ Wz @ V + _lam(q, V.shape[1]) * np.eye(V.shape[1])
    B = _solve(A, V.T @ Wzy)
    alphas, wts = {}, {}
    for c in centers:
        s = stats_by_center[c]
        alphas[c] = s.sy / s.n - (((s.sx / s.n) - mx) / sd) @ V @ B
        wts[c] = s.n
    a_out = sum(wts[c] * alphas[c] for c in centers) / sum(wts.values())
    return Head(mx, sd, V, B, a_out, "intercept", alphas)


def fit_centred(stats_by_center, k=K_PC):
    """Federated head on center-centred embeddings. Predict with X minus the center's own mean."""
    st = total([stats_by_center[c].centred() for c in stats_by_center])
    h = fit_exact(st, k)
    h.kind = "centred"
    return h


# ----------------------------------------------------------------------------- the faithful head
def fit_faithful(X, Y, k=K_PC, seed=1):
    from sklearn.decomposition import PCA
    from sklearn.linear_model import Ridge
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
    pipe = Pipeline([("scaler", StandardScaler()), ("PCA", PCA(n_components=k, random_state=seed))])
    Z = pipe.fit_transform(np.asarray(X, dtype=np.float32)).astype(np.float32)
    reg = Ridge(solver="lsqr", alpha=LAM_NUM / (Z.shape[1] * Y.shape[1]), random_state=seed,
                fit_intercept=False, max_iter=1000).fit(Z, Y)

    class _F:
        kind = "faithful"

        def predict(self, Xt, center=None):
            return reg.predict(pipe.transform(np.asarray(Xt, dtype=np.float32)).astype(np.float32))
    return _F()


# ----------------------------------------------------------------------------- metrics
def _pearson_cols(Y, P):
    Y = np.asarray(Y, dtype=np.float64)
    P = np.asarray(P, dtype=np.float64)
    Yc = Y - Y.mean(0)
    Pc = P - P.mean(0)
    den = np.sqrt((Yc ** 2).sum(0) * (Pc ** 2).sum(0))
    with np.errstate(invalid="ignore", divide="ignore"):
        r = (Yc * Pc).sum(0) / den
    r[den == 0] = np.nan
    return r


def within_slide(Y, P, slides, min_spots=MIN_SLIDE_SPOTS):
    """Mean over test slides (with at least min_spots spots) of the mean over genes of the
    per-slide Pearson correlation; genes whose correlation is undefined on a slide are skipped."""
    vals = []
    for s in np.unique(slides):
        m = slides == s
        if m.sum() < min_spots:
            continue
        r = _pearson_cols(Y[m], P[m])
        if np.isfinite(r).any():
            vals.append(np.nanmean(r))
    return float(np.mean(vals)) if vals else float("nan"), len(vals)


def pooled_pearson(Y, P):
    r = _pearson_cols(Y, P)
    return float(np.nanmean(r))


def rel_diff(P, Q):
    return float(np.max(np.abs(np.asarray(P) - np.asarray(Q))) / np.max(np.abs(np.asarray(Q))))
