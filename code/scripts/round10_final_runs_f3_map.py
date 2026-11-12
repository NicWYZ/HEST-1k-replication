#!/usr/bin/env python
"""Round 10, track final-runs, F3.1: the prediction-set map (plan section 5d.1) and the set side of E8 for
ACS by state (plan section 5d.4 item 3). Nothing in this file is a result.

The refit path is round 5's W3 over round 4's C3, imported unchanged (round5_conf_w3.py, round4_conf_c3.py).
For every (task, encoder, K, fold, calibration draw) the base head is refitted on the design's training donors,
so the K calibration donors and the target donor are outside the head's training set. This module adds:

  scale      Both scales from one fit. The scaler and the PCA do not see the outcome and the ridge's alpha
             depends only on the number of genes, so the head on log(1 + 1e4 y / n) is a second Ridge
             (round 3's settings: alpha of fit_base, intercept, cholesky) on the same PCA features
             (5d.1 item 4; the smoke job checks it equals fit_base refitted on that outcome). n is each spot's
             h5ad total, recovered with round10_final_runs_f2_refit_norm.lib_sizes (as round 9's C2 did). The
             raw count is expm1 of the log1p label for CCRCC (as F2 did), and the loader's raw counts for
             INDIANA_KIDNEY and LUNG_XENIUM.
  methods    C3's o = 0 methods (pooled, hcp, one_per), all eight C3 o-methods (ghcp, ghcp_noad, ghcp_r05,
             ghcp_r05_noad, ghcp_r05code, within, within_plain, recentred), W3's within_full, and `xgene`,
             the cross-gene studentized set of 5d.1 item 5 in the map's design (below).
  final      5d.1 item 9: within, within_plain and within_full from the target donor's residuals in the
             final leave-one-donor-out file, at the same o and label draws (round 4's label stream on the
             fold's evaluation rows), as methods `<name>_final`. Where the final file lacks spots or genes,
             the refit-path values on the same rows and genes are written as `<name>_refitsub`.
  kidney     5d.1 item 10: a corpus loader for kidney Visium on F1's inputs (task JSON, audited donor map,
             frozen embeddings), with F1's head (round3_a0_harness.fit_base, then a Ridge on lognorm).
  scores     5d.1 item 7: abs, scaled_clip, cqr, nb_conformal (round3_a4_scores, imported unchanged) inside
             hcp at o = 0 and within_plain at o in {9, 15, 25, 50}, and the model interval nb (`nb_model`,
             no conformal guarantee), at K = 10, alpha 0.1, log1p.
  acs        5d.4 item 3: round 4's ACS by state conformal code, imported unchanged, with within_full added.

XGENE (assumption and guarantee, written before anything runs). For calibration donor k, its first o residuals
in C3's seeded within-donor order form its block b_k, and the test donor's o labelled residuals form b_t.
sigma_j = sqrt(mean over all K + 1 blocks of r^2) + 1e-6, a symmetric function of the blocks. A donor's scale is
c = median over genes of max(rms_j(b), 0.1 sigma_j) / sigma_j. Calibration donor k's other N_k - o spots score
|r| / (sigma_j c_k) with weight 1 / ((K + 1)(N_k - o)), the test donor carries mass 1 / (K + 1) at +inf (HCP), and
the interval is yhat +- q_j sigma_j c_t. Each donor's score is built by the same rule from its own block and from
symmetric quantities, so under hierarchical exchangeability of donors and within-donor exchangeability the
coverage is >= 1 - alpha, as for round 9's construction. Round 9's xgene floored the block RMS at 1e-6 and its
per-gene method at 0.1 sigma_j; 5d.1 item 5 names the 0.1 sigma_j floor, which is what runs here. The calibration
donors' blocks are fixed by C3's donor permutation; the test block follows the label draw.

Seeds. Every seed of C3 and W3 is a zlib.crc32 key (round4_conf_c3.crc); this module adds the kidney calibration
draw, crc32("kidney__Visium|f3map|donor|<target>|cal<draw>"), shared by encoders and scales so the designs are
paired, and CQR's subsample keys, crc32("<task>|f3map|scores|<fold>|cal<draw>|cqr_sub|g<j>|q<q>").

usage:
  round10_final_runs_f3_map.py map --task KEY --encoder E --part 1|2 [--K k ...] [--folds a,b] [--cal-draws 0,1,2]
                                   [--no-final] [--max-specs n] --out DIR
  round10_final_runs_f3_map.py scores --task KEY --encoder uni_v2 [--folds a,b] [--cal-draws 0,1,2]
                                   [--cqr-genes n] [--skip cqr,nb] --out DIR
  round10_final_runs_f3_map.py acs --pred PARQUET --out DIR [--draws 0-19] [--workers 4]
  round10_final_runs_f3_map.py checkfit --task KEY --encoder E --fold F --out DIR   (smoke: fit_ext equals C3's fit)
"""
import argparse
import hashlib
import json
import math
import os
import sys
import time
import types
import zlib

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import round4_conf_c3 as C  # noqa: E402
import round5_conf_w3 as W3  # noqa: E402

ROOT = C.ROOT
BULK = f"{ROOT}/results"
FR = f"{BULK}/round10/final_runs"
CLONE = "/work/users/w/e/weiyang/hest_code/round10-final-runs"
ACS_CODE = f"{CLONE}/results/round4/conformal/C3_real/frag_ACS_o/code/round4_conf_c3_acs_o.py"
ACS_CODE_MD5 = "f9d411a8703b09031cf5f759f369695c"

P1_O = W3.P1_O
P2_O = W3.P2_O
# Part 2 at K = 10 is the same spec, head and label draws as part 1 at K = 10, so its rows are read from part 1.
P2_K = {"CCRCC:24": (12, 14, 16, 18, 20), "CCRCC:23_merged": (12, 14, 16, 18, 20),
        "INDIANA_KIDNEY": (14, 18, 20), "LUNG_XENIUM": (6, 8), "kidney__Visium": (20, 30, 40)}
SCALES = ("log1p", "norm")
FINAL_METHODS = ("within", "within_plain", "within_full")
SCORE_O = (9, 15, 25, 50)
KIDNEY = dict(task="kidney__Visium", json="/work/users/w/e/weiyang/st_fed_learn/data/tasks/kidney__Visium.json",
              donor_map=f"{FR}/F1/audit_verdicts/donor_map__kidney__Visium.csv")
OUT_COLS = (C.FIXED_COLS + C.EXTRA_COLS +
            ["part", "scale", "wf_frac_not_interval", "n_genes", "join_frac", "y_final_maxabs"])


def crc(key):
    return zlib.crc32(key.encode())


def md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def log(*a):
    print(*a, flush=True)


# ================================================================== HEST loaders with the normalised scale
CAP = {}


def _install_capture():
    """Wrap the three loaders C3 calls so that the spot barcodes (and raw counts) are kept. The wrappers pass every
    return value through unchanged."""
    H = C._r3("round3_a0_harness")
    D4 = C._r3("round3_d4_sets")
    if getattr(H, "_f3cap", False):
        return
    base_lt, base_ls, base_lsd = H.load_task, D4.load_set, C.IO.load_set_dropped

    def lt(td, e):
        out = base_lt(td, e)
        CAP["ccrcc"] = dict(samp=out[2], bc=out[3])
        return out

    def ls(td, enc, union):
        out = base_ls(td, enc, union)
        CAP["d4"] = dict(Yraw=out[1], samp=out[2], bc=out[3])
        return out

    def lsd(*a, **k):
        out = base_lsd(*a, **k)
        CAP["lung"] = dict(Yraw=out[1], samp=out[2], bc=out[3])
        return out
    H.load_task, D4.load_set, C.IO.load_set_dropped = lt, ls, lsd
    H._f3cap = True


def load_hest(task_key, enc):
    import round10_final_runs_f2_refit_norm as RN
    _install_capture()
    CAP.clear()
    T = C.load_task(task_key, enc, log=log)
    kind = C.TASKS[task_key]["kind"]
    cap = CAP[kind]
    samp = np.asarray(cap["samp"]).astype(str)
    assert len(samp) == T.X.shape[0] and (samp == np.asarray(T.samp).astype(str)).all(), "captured rows differ"
    T.bc = np.asarray(cap["bc"]).astype(str)
    lib = RN.lib_sizes(ROOT, RN.adata_template(ROOT, T.td, T.task), T.samp, T.bc)
    ok = np.isfinite(lib) & (lib > 0)
    if not ok.all():
        raise SystemExit(f"{task_key}: {int((~ok).sum())} spots without a library size")
    T.lib = lib
    T.kind = kind
    if kind == "ccrcc":
        cnt = np.expm1(T.Y.astype(np.float64))
        T.frac_integer = float(np.mean(np.abs(cnt - np.round(cnt)) < 1e-3))
        T.Ynorm = np.log1p(cnt * (1e4 / lib)[:, None]).astype(T.Y.dtype)
        T.f3_labels = lambda spec: (list(T.genes), T.Y, T.Ynorm)
    elif kind == "lung":
        Yraw = cap["Yraw"].astype(np.float64)
        d = float(np.max(np.abs(np.log1p(Yraw) - T.Y)))
        assert d == 0.0, f"lung log1p labels differ from the captured raw counts by {d}"
        T.frac_integer = float(np.mean(np.abs(Yraw - np.round(Yraw)) < 1e-9))
        T.Ynorm = np.log1p(Yraw * (1e4 / lib)[:, None])
        T.f3_labels = lambda spec: (list(T.genes), T.Y, T.Ynorm)
    else:
        T.frac_integer = float(np.mean(np.abs(T.Yraw - np.round(T.Yraw)) < 1e-9))

        def lab(spec):
            genes, Ylog = T._labels(spec)
            cols = [T.col_of[g] for g in genes]
            Yn = np.log1p(T.Yraw[:, cols].astype(np.float64) * (1e4 / lib)[:, None])
            return list(genes), Ylog, Yn
        T.f3_labels = lab
    T.task_key = task_key
    log(f"[f3map] {task_key} {enc}: library sizes for {len(lib):,} spots, integer share {T.frac_integer:.7f}")
    return T


# ================================================================== kidney Visium (corpus) loader
def load_kidney(enc):
    import round10_final_runs_f1_predict as F1P
    H = C._r3("round3_a0_harness")
    td = json.load(open(KIDNEY["json"]))
    genes = [str(g) for g in td["genes_top50"]]
    dm = pd.read_csv(KIDNEY["donor_map"], dtype=str).drop_duplicates("sample_id").set_index("sample_id")["donor_id"]
    samples = [s for s in td["samples"] if s["sample_id"] in dm.index]     # F1's --only-mapped
    parts = []
    t0 = time.time()
    for s in samples:
        E, Y, b, lib, nd = F1P.load_sample(s, enc, genes)
        parts.append((s["sample_id"], s["center_id"], dm[s["sample_id"]], E, Y, b, lib))
    T = types.SimpleNamespace()
    T.H, T.kind, T.task_key, T.task, T.out_task = H, "kidney", "kidney__Visium", "kidney__Visium", "kidney__Visium"
    T.label_set, T.enc, T.donor_set = "corpus_audited", enc, "51"
    T.X = np.concatenate([p[3] for p in parts])
    Y = np.concatenate([p[4] for p in parts])
    T.lib = np.concatenate([p[6] for p in parts]).astype(np.float64)
    T.samp = np.concatenate([[p[0]] * len(p[5]) for p in parts]).astype(str)
    T.bc = np.concatenate([p[5] for p in parts]).astype(str)
    T.donor = np.concatenate([[p[2]] * len(p[5]) for p in parts]).astype(str)
    T.genes = genes
    T.Ylog = np.log1p(Y)
    T.Ynorm = np.log1p(1e4 * Y / np.maximum(T.lib, 1)[:, None])        # F1's lognorm, exactly
    T.donors = sorted(set(T.donor.tolist()))
    T.frac_integer = float(np.mean(np.abs(Y - np.round(Y)) < 1e-9))
    T.f3_labels = lambda spec: (list(T.genes), T.Ylog, T.Ynorm)
    T.fold_names = lambda: list(T.donors)
    log(f"[f3map] kidney__Visium {enc}: {T.X.shape[0]:,} spots x {T.X.shape[1]} dims, {len(samples)} samples, "
        f"{len(T.donors)} donors, {time.time() - t0:.0f}s")

    def specs(K, n_cal_draws=C.N_CAL_DRAWS, folds=None):
        out = []
        for d in T.donors:
            if folds is not None and d not in set(map(str, folds)):
                continue
            E = T.donor == d
            pool = sorted(x for x in T.donors if x != d)
            if len(pool) <= K:
                continue
            for draw in range(n_cal_draws):
                rng = np.random.default_rng(crc(f"kidney__Visium|f3map|donor|{d}|cal{draw}"))
                pick = set(rng.permutation(np.array(pool, dtype=object))[:K].tolist())
                Cm = np.isin(T.donor, sorted(pick))
                Tm = ~E & ~Cm
                out.append(dict(task=T.task, design="f3map_donor", fold=d, cal_draw=draw, T=Tm, C=Cm, E=E,
                                info=dict(n_cal_units=len(pick)), n_train_natural=int(Tm.sum()),
                                n_train_matched=int(Tm.sum())))
        return out
    T.specs = specs
    return T


def load_any(task_key, enc):
    return load_kidney(enc) if task_key == "kidney__Visium" else load_hest(task_key, enc)


# ================================================================== one fit, both scales
def fit_ext(T, spec):
    """C3's TaskData.fit for both scales from one PCA pipeline. Returns ({scale: Fit}, extras)."""
    from sklearn.linear_model import Ridge
    H = T.H
    Tm = spec["T"] if T.kind == "kidney" else H.apply_size_match(spec, T.task)
    Cm, Em = spec["C"], spec["E"]
    if int(Tm.sum()) < H.MIN_T_SPOTS or int(Cm.sum()) < H.MIN_C_SPOTS:
        raise ValueError(f"{T.task_key} {spec['fold']} draw{spec['cal_draw']}: |T|={int(Tm.sum())} |C|={int(Cm.sum())}")
    genes, Ylog, Ynorm = T.f3_labels(spec)
    pipe, A, reg, ra = H.fit_base(T.X[Tm], Ylog[Tm])
    regn = Ridge(alpha=ra, random_state=0, fit_intercept=True, solver="cholesky").fit(
        A, Ynorm[Tm].astype(np.float64, copy=False))
    A_C = pipe.transform(T.X[Cm].astype(np.float64, copy=False))
    A_E = pipe.transform(T.X[Em].astype(np.float64, copy=False))
    if T.kind == "kidney":
        lab_C = T.donor[Cm].astype(object)
        don_T = set(T.donor[Tm].tolist())
    else:
        donor_of = T.meta["donor_of"]
        don_T = {donor_of[s] for s in np.unique(T.samp[Tm])}
        lab_C = np.array([donor_of[s] for s in T.samp[Cm]], dtype=object)
    fits = {}
    for scale, Y, rg in (("log1p", Ylog, reg), ("norm", Ynorm, regn)):
        P_C, P_E = rg.predict(A_C), rg.predict(A_E)
        Y_C, Y_E = Y[Cm].astype(np.float64, copy=False), Y[Em].astype(np.float64, copy=False)
        rs = [np.corrcoef(P_E[:, j], Y_E[:, j])[0, 1] if Y_E[:, j].std() > 0 and P_E[:, j].std() > 0 else np.nan
              for j in range(len(genes))]
        f = C.Fit(task_key=T.task_key, task=T.task, out_task=T.out_task, label_set=T.label_set, enc=T.enc,
                  donor_set=T.donor_set, fold=str(spec["fold"]), cal_draw=int(spec["cal_draw"]),
                  K=int(spec["info"]["n_cal_units"]), genes=list(genes), P_E=P_E, Y_E=Y_E, R_E=Y_E - P_E,
                  S_C=np.abs(Y_C - P_C), R_C=Y_C - P_C, lab_C=lab_C, samp_E=T.samp[Em], n_T_donors=len(don_T),
                  n_T_natural=int(spec["n_train_natural"]), n_T_matched=int(spec["n_train_matched"]),
                  n_C=int(Cm.sum()), n_C_donors=len(set(lab_C.tolist())), n_E=int(Em.sum()),
                  pearson_mean=float(np.nanmean(rs)), cal_donors=sorted(set(lab_C.tolist())))
        f.bc_E = T.bc[Em]
        f.Y_C = Y_C
        fits[scale] = f
    ex = dict(A=A, A_C=A_C, A_E=A_E, reg=reg, ra=ra, Tm=Tm, Cm=Cm, Em=Em, Ylog=Ylog, genes=genes)
    return fits, ex


# ================================================================== xgene in the map's design
def xgene_rows(fit, o_grid, label_draws=range(C.N_LABEL_DRAWS), alphas=C.ALPHAS, min_eval=10):
    rows = []
    base = fit.base_row()
    sl = fit.slides
    R = fit.R_E
    G = R.shape[1]
    ctx = fit.ctx()
    K = len(fit.groups)
    betas = [1 - a for a in alphas]
    skipped = [o for o in o_grid if o >= 1 and (ctx.N <= o).any()]
    for ld in label_draws:
        perm = C.label_stream(fit, ld)
        for o in o_grid:
            if o < 1 or fit.n_E - o < min_eval or o in skipped:
                continue
            lab = perm[:o]
            keep = np.ones(fit.n_E, bool)
            keep[lab] = False
            init = R[lab]
            Bst = np.vstack([x[:o] for x in ctx.X] + [init])
            sig = np.sqrt((Bst ** 2).mean(axis=0)) + 1e-6
            floor = 0.1 * sig

            def cg(b):
                return float(np.median(np.maximum(np.sqrt((b ** 2).mean(axis=0)), floor) / sig))
            cK = [cg(x[:o]) for x in ctx.X]
            ct = cg(init)
            S = np.vstack([np.abs(x[o:]) / (sig[None, :] * ck) for x, ck in zip(ctx.X, cK)])
            w = np.concatenate([np.full(len(x) - o, 1.0 / ((K + 1) * (len(x) - o))) for x in ctx.X])
            q, fc = C.wq_cols(S, w, 1.0 / (K + 1), betas)
            for i, a in enumerate(alphas):
                m = C.centred_metrics(R, keep, np.zeros(G), q[i] * ct * sig, sl)
                rows.append(C._row(base, "xgene", a, o, ld, m, fc[i], K, int(keep.sum())))
    fit.xgene_skipped_o = skipped
    return rows


# ================================================================== item 9: the final leave-one-donor-out files
def final_path(task_key, enc, scale):
    if task_key == "kidney__Visium":
        return f"{FR}/F1/predict/kidney__Visium__{enc}/pred__kidney__Visium__{enc}__donor.parquet"
    name = {"CCRCC:24": "CCRCC", "CCRCC:23_merged": "CCRCC_merged", "INDIANA_KIDNEY": "INDIANA_KIDNEY",
            "LUNG_XENIUM": "LUNG_XENIUM"}[task_key]
    if scale == "norm":
        return f"{FR}/F2/refit_norm/{name}__{enc}/norm/b1_predictions__{name}__{enc}.parquet"
    if name.startswith("CCRCC"):
        return f"{BULK}/round3/B1_ppi/b1_predictions__{name}__{enc}.parquet"
    if name == "INDIANA_KIDNEY":
        return f"{BULK}/round4/ppi/Q2_theory/predictions_INDIANA_KIDNEY/b1_predictions__INDIANA_KIDNEY__{enc}.parquet"
    return f"{BULK}/round4/ppi/Q2_theory/predictions/b1_predictions__LUNG_XENIUM__{enc}.parquet"


class FinalFile:
    def __init__(self, task_key, enc, scale):
        import pyarrow.parquet as pq
        self.path = final_path(task_key, enc, scale)
        names = pq.read_schema(self.path).names
        if task_key == "kidney__Visium":
            ypre, fpre = ("y_log1p__", "f_log1p__") if scale == "log1p" else ("y_lognorm__", "f_lognorm__")
        else:
            ypre, fpre = "y__", "f__"
        self.genes = [n[len(ypre):] for n in names if n.startswith(ypre)]
        cols = ["sample_id", "barcode"] + [ypre + g for g in self.genes] + [fpre + g for g in self.genes]
        df = pd.read_parquet(self.path, columns=cols)
        self.key = pd.Index(df["sample_id"].astype(str) + "|" + df["barcode"].astype(str))
        assert self.key.is_unique, f"{self.path}: duplicated (sample_id, barcode)"
        self.Y = df[[ypre + g for g in self.genes]].to_numpy(np.float64)
        self.F = df[[fpre + g for g in self.genes]].to_numpy(np.float64)
        self.md5 = md5(self.path)

    def residuals_for(self, fit):
        gpos = {g: i for i, g in enumerate(self.genes)}
        gi = [j for j, g in enumerate(fit.genes) if str(g) in gpos]
        fi = [gpos[str(fit.genes[j])] for j in gi]
        keys = pd.Index([f"{s}|{b}" for s, b in zip(fit.samp_E.astype(str), fit.bc_E.astype(str))])
        pos = self.key.get_indexer(keys)
        present = pos >= 0
        Rf = np.zeros((fit.n_E, len(gi)))
        Yf = np.full((fit.n_E, len(gi)), np.nan)
        Rf[present] = self.Y[pos[present]][:, fi] - self.F[pos[present]][:, fi]
        Yf[present] = self.Y[pos[present]][:, fi]
        ymax = float(np.nanmax(np.abs(Yf[present] - fit.Y_E[present][:, gi]))) if present.any() else float("nan")
        return np.array(gi, int), Rf, present, ymax


def _within_three(base, R, keep, init, sl, o, ld, suffix, alphas, extra):
    rows = []
    G = R.shape[1]
    m0 = o // 2
    c = init[:m0].mean(axis=0) if m0 > 0 else np.zeros(G)
    n_test = int(keep.sum())
    q, fc = C.split_q_cols(np.abs(init[m0:] - c), alphas)
    for i, a in enumerate(alphas):
        rows.append(dict(C._row(base, "within" + suffix, a, o, ld, C.centred_metrics(R, keep, c, q[i], sl), fc[i],
                                o - m0, n_test), **extra))
    q, fc = C.split_q_cols(np.abs(init), alphas)
    for i, a in enumerate(alphas):
        rows.append(dict(C._row(base, "within_plain" + suffix, a, o, ld,
                                C.centred_metrics(R, keep, np.zeros(G), q[i], sl), fc[i], o, n_test), **extra))
    for a in alphas:
        m = W3.wf_m(o, a)
        met, fin, fni = W3.wf_metrics(R, keep, init, m, sl)
        r = dict(C._row(base, "within_full" + suffix, a, o, ld, met, fin, o, n_test), **extra)
        r["wf_frac_not_interval"] = fni
        rows.append(r)
    return rows


def final_rows(fit, ff, o_grid, label_draws=range(C.N_LABEL_DRAWS), alphas=C.ALPHAS, min_eval=10):
    gi, Rf, present, ymax = ff.residuals_for(fit)
    sub = (len(gi) < len(fit.genes)) or (not present.all())
    base = fit.base_row()
    sl = fit.slides
    extra = dict(n_genes=len(gi), join_frac=float(present.mean()), y_final_maxabs=ymax)
    Rr = fit.R_E[:, gi]
    rows = []
    for ld in label_draws:
        perm = C.label_stream(fit, ld)
        permp = perm[present[perm]]
        for o in o_grid:
            if o < 1 or int(present.sum()) - o < min_eval:
                continue
            lab = permp[:o]
            keep = present.copy()
            keep[lab] = False
            rows += _within_three(base, Rf, keep, Rf[lab], sl, o, ld, "_final", alphas, extra)
            if sub:
                rows += _within_three(base, Rr, keep, Rr[lab], sl, o, ld, "_refitsub", alphas, extra)
    return rows


# ================================================================== the map driver
def write_table(rows, path):
    d = pd.DataFrame(rows)
    for c in OUT_COLS:
        if c not in d:
            d[c] = np.nan
    d[OUT_COLS].to_csv(path, index=False)
    return d


def by_fold(d):
    keys = ["task", "encoder", "scale", "part", "method", "alpha", "o", "K", "fold", "n_T_donors"]
    g = d.groupby(keys, dropna=False)
    return g.agg(coverage=("coverage", "mean"), width_mean=("width_mean", "mean"),
                 width_median=("width_median", "mean"), n_test=("n_test", "mean"),
                 finite_frac=("finite", "mean"), n_draws=("draw", "nunique")).reset_index()


def run_map(a):
    os.makedirs(a.out, exist_ok=True)
    t0 = time.time()
    T = load_any(a.task, a.encoder)
    folds = a.folds.split(",") if a.folds else T.fold_names()
    cal_draws = [int(x) for x in a.cal_draws.split(",")]
    plan = [(10, (0,) + P1_O)] if a.part == 1 else [(K, P2_O) for K in (a.K or P2_K[a.task])]
    ffs = {}
    if a.part == 1 and not a.no_final:
        for s in SCALES:
            ffs[s] = FinalFile(a.task, a.encoder, s)
            log(f"[f3map] final file {s}: {ffs[s].path} ({len(ffs[s].genes)} genes, md5 {ffs[s].md5})")
    rows, timing, done_final = [], [], set()
    n_spec = 0
    for K, og in plan:
        specs = [s for s in T.specs(K, n_cal_draws=max(cal_draws) + 1, folds=folds) if s["cal_draw"] in cal_draws]
        for sp in specs:
            if a.max_specs and n_spec >= a.max_specs:
                break
            t1 = time.time()
            fits, _ = fit_ext(T, sp)
            t_fit = time.time() - t1
            for scale in SCALES:
                fit = fits[scale]
                t2 = time.time()
                rr = []
                if 0 in og:
                    rr += C.o0_rows(fit, alphas=C.ALPHAS, methods=C.O0_METHODS, dwr_reps=C.DWR_REPS)
                ogp = tuple(o for o in og if o > 0)
                rr += C.o_rows(fit, o_grid=ogp, label_draws=range(C.N_LABEL_DRAWS), alphas=C.ALPHAS,
                               methods=C.O_METHODS)
                t3 = time.time()
                rr += W3.wf_rows(fit, ogp)
                t4 = time.time()
                rr += xgene_rows(fit, ogp)
                t5 = time.time()
                if scale in ffs and (fit.fold, scale) not in done_final:
                    rr += final_rows(fit, ffs[scale], ogp)
                    done_final.add((fit.fold, scale))
                t6 = time.time()
                for r in rr:
                    r.update(part=a.part, scale=scale)
                rows += rr
                timing.append(dict(task=a.task, encoder=a.encoder, scale=scale, part=a.part, K=K, fold=fit.fold,
                                   cal_draw=fit.cal_draw, n_T_donors=fit.n_T_donors, n_E=fit.n_E, n_C=fit.n_C,
                                   n_genes=len(fit.genes), pearson_mean=fit.pearson_mean,
                                   s_fit_both_scales=round(t_fit, 2), s_c3=round(t3 - t2, 2),
                                   s_within_full=round(t4 - t3, 2), s_xgene=round(t5 - t4, 2),
                                   s_final=round(t6 - t5, 2), rows=len(rr),
                                   xgene_skipped_o=",".join(map(str, fit.xgene_skipped_o))))
            n_spec += 1
            log(f"[f3map] {a.task} p{a.part} {a.encoder} K{K} {sp['fold']} cal{sp['cal_draw']} "
                f"fit {t_fit:.0f}s total {time.time() - t0:.0f}s")
    tag = f"{a.task.replace(':', '_')}__{a.encoder}__p{a.part}"
    pd.DataFrame(timing).to_csv(os.path.join(a.out, f"map_timing__{tag}.csv"), index=False)
    d = pd.DataFrame(rows)
    by_fold(d).to_csv(os.path.join(a.out, f"map_by_fold__{tag}.csv"), index=False)
    write_table(rows, os.path.join(a.out, f"map_full__{tag}.csv.gz"))
    info = dict(task=a.task, encoder=a.encoder, part=a.part, folds=folds, cal_draws=cal_draws,
                plan=[dict(K=K, o_grid=list(og)) for K, og in plan], rows=len(rows), specs=n_spec,
                wall_seconds=round(time.time() - t0, 1), frac_integer=getattr(T, "frac_integer", None),
                final_files={s: dict(path=f.path, md5=f.md5, n_genes=len(f.genes)) for s, f in ffs.items()},
                methods=list(C.O0_METHODS) + list(C.O_METHODS) + ["within_full", "xgene"] +
                [m + "_final" for m in FINAL_METHODS])
    json.dump(info, open(os.path.join(a.out, f"map_info__{tag}.json"), "w"), indent=1)
    log(f"[f3map] done {len(rows)} rows {time.time() - t0:.0f}s")


def run_checkfit(a):
    """Smoke check: fit_ext's log1p Fit equals C3's TaskData.fit on the same spec; the shared-pipeline
    normalised head equals fit_base refitted on the normalised outcome; the labels equal the final files' y."""
    os.makedirs(a.out, exist_ok=True)
    T = load_any(a.task, a.encoder)
    if a.fold == "first":
        a.fold = str(T.fold_names()[0])
    sp = [s for s in T.specs(10, n_cal_draws=1, folds=[a.fold])][0]
    fits, ex = fit_ext(T, sp)
    out = dict(task=a.task, encoder=a.encoder, fold=a.fold, frac_integer=getattr(T, "frac_integer", None))
    if T.kind != "kidney":
        ref = T.fit(sp)
        out["c3_fit_R_E_maxabs"] = float(np.max(np.abs(ref.R_E - fits["log1p"].R_E)))
        out["c3_fit_R_C_maxabs"] = float(np.max(np.abs(ref.R_C - fits["log1p"].R_C)))
    genes, Ylog, Ynorm = T.f3_labels(sp)
    pipe2, A2, reg2, ra2 = T.H.fit_base(T.X[ex["Tm"]], Ynorm[ex["Tm"]])
    P2 = reg2.predict(pipe2.transform(T.X[ex["Em"]].astype(np.float64, copy=False)))
    out["norm_head_vs_fit_base_maxabs"] = float(np.max(np.abs(P2 - fits["norm"].P_E)))
    for s in SCALES:
        ff = FinalFile(a.task, a.encoder, s)
        gi, Rf, present, ymax = ff.residuals_for(fits[s])
        out[f"final_{s}_join_frac"] = float(present.mean())
        out[f"final_{s}_n_genes_common"] = int(len(gi))
        out[f"final_{s}_n_genes_fit"] = len(fits[s].genes)
        out[f"final_{s}_y_maxabs"] = ymax
    out["passed"] = bool(out.get("c3_fit_R_E_maxabs", 0.0) == 0.0 and out.get("c3_fit_R_C_maxabs", 0.0) == 0.0
                         and out["norm_head_vs_fit_base_maxabs"] < 1e-8
                         and out["final_norm_y_maxabs"] < 1e-5 and out["final_log1p_y_maxabs"] < 1e-5)
    json.dump(out, open(os.path.join(a.out, f"checkfit__{a.task.replace(':', '_')}__{a.encoder}.json"), "w"),
              indent=1)
    log(json.dumps(out, indent=1))


# ================================================================== item 7: the adaptive scores in the map design
def run_scores(a):
    import round3_a4_scores as A4S
    os.makedirs(a.out, exist_ok=True)
    t0 = time.time()
    T = load_any(a.task, a.encoder)
    H = T.H
    folds = a.folds.split(",") if a.folds else T.fold_names()
    cal_draws = [int(x) for x in a.cal_draws.split(",")]
    skip = set(a.skip.split(",")) if a.skip else set()
    alpha = 0.1
    rows, timing = [], []
    cqr_args = types.SimpleNamespace(cqr_budget_s=0, cqr_subsample=2500, cqr_presubsample=True, cqr_timebox_s=1e18)
    nb_args = types.SimpleNamespace(nb_tol=1e-6, nb_solver="newton-cholesky", nb_score_tol=1e-3)
    specs = [s for s in T.specs(10, n_cal_draws=max(cal_draws) + 1, folds=folds) if s["cal_draw"] in cal_draws]
    for sp in specs:
        t1 = time.time()
        fits, ex = fit_ext(T, sp)
        fit = fits["log1p"]
        A, A_C, A_E, reg, ra = ex["A"], ex["A_C"], ex["A_E"], ex["reg"], ex["ra"]
        Y_T = ex["Ylog"][ex["Tm"]].astype(np.float64, copy=False)
        G = len(fit.genes)
        Y_E, P_E, Y_C = fit.Y_E, fit.P_E, fit.Y_C
        lab = fit.lab_C.astype(str)
        K = len(fit.groups)
        sizes = {g: int((lab == g).sum()) for g in fit.groups}
        w = np.array([1.0 / ((K + 1) * sizes[g]) for g in lab])
        sl_all = fit.slides
        t_fit = time.time() - t1
        mach = {}
        mach["abs"] = dict(gi=np.arange(G), S_C=np.abs(fit.R_C),
                           S_E=lambda idx: np.abs(fit.R_E[idx]),
                           iv=lambda q, idx: (P_E[idx] - q, P_E[idx] + q))
        sig = H.fit_sigma(A, Y_T, reg, ra)
        raw_C, raw_E = sig.predict(A_C), sig.predict(A_E)
        lo_c = max(float(np.percentile(raw_C, A4S.SIGMA_CLIP_LO_PCT)), H.SIGMA_FLOOR)
        hi_c = max(float(np.percentile(raw_C, A4S.SIGMA_CLIP_HI_PCT)), lo_c * (1 + 1e-12))
        s_C, u_E = np.clip(raw_C, lo_c, hi_c), np.clip(raw_E, lo_c, hi_c)
        mach["scaled_clip"] = dict(gi=np.arange(G), S_C=np.abs(fit.R_C) / s_C,
                                   S_E=lambda idx: np.abs(fit.R_E[idx]) / u_E[idx],
                                   iv=lambda q, idx: (P_E[idx] - q * u_E[idx], P_E[idx] + q * u_E[idx]))
        t_sig = time.time() - t1 - t_fit
        t_cqr = 0.0
        if "cqr" not in skip:
            gq = np.arange(G) if not a.cqr_genes else np.arange(min(a.cqr_genes, G))
            st = dict(cqr_seconds=0.0, cqr_fallback=False, base={})
            key = f"{T.task_key}|f3map|scores|{fit.fold}|cal{fit.cal_draw}"
            tq = time.time()
            mods, crow = A4S.fit_cqr(A, Y_T, gq, st, key, cqr_args)
            qlo_C, qhi_C = A4S.cqr_predict(mods, A_C, gq)
            qlo_E, qhi_E = A4S.cqr_predict(mods, A_E, gq)
            t_cqr = time.time() - tq
            mach["cqr"] = dict(gi=gq, S_C=np.maximum(qlo_C - Y_C[:, gq], Y_C[:, gq] - qhi_C),
                               S_E=lambda idx, qlo_E=qlo_E, qhi_E=qhi_E, gq=gq: np.maximum(
                                   qlo_E[idx] - Y_E[idx][:, gq], Y_E[idx][:, gq] - qhi_E[idx]),
                               iv=lambda q, idx, qlo_E=qlo_E, qhi_E=qhi_E: (qlo_E[idx] - q, qhi_E[idx] + q),
                               n_fail=int(sum(1 for r in crow if r.get("failure"))),
                               n_sub=int(sum(1 for r in crow if r.get("subsample_fallback"))))
        t_nb = 0.0
        if "nb" not in skip:
            tn = time.time()
            cnt_T, cnt_C, cnt_E = (np.round(np.expm1(v)) for v in (Y_T, Y_C, Y_E))
            gnb = np.arange(G)
            nbm, a_g, grows = A4S.fit_nb(A, cnt_T, gnb, ra, list(fit.genes), nb_args, base={})
            gok = np.array([nbm.get(j) is not None for j in gnb])
            gnb, a_g = gnb[gok], a_g[gok]
            mu_C = A4S.nb_predict(nbm, A_C, gnb)
            mu_E = A4S.nb_predict(nbm, A_E, gnb)
            F_C = A4S.nb_cdf(cnt_C[:, gnb], mu_C, a_g)

            def nb_iv(q, idx, mu_E=mu_E, a_g=a_g):
                sh = mu_E[idx].shape
                qq = np.minimum(q, 0.5)
                lo = np.log1p(A4S.nb_ppf(np.array(np.broadcast_to(0.5 - qq, sh)), mu_E[idx], a_g))
                hi = np.log1p(A4S.nb_ppf(np.array(np.broadcast_to(np.minimum(0.5 + qq, 1.0), sh)), mu_E[idx], a_g))
                hi = np.where(np.broadcast_to(q, sh) >= 0.5, np.inf, hi)
                return lo, hi
            mach["nb_conformal"] = dict(gi=gnb, S_C=np.abs(F_C - 0.5),
                                        S_E=lambda idx, mu_E=mu_E, a_g=a_g, gnb=gnb: np.abs(
                                            A4S.nb_cdf(cnt_E[idx][:, gnb], mu_E[idx], a_g) - 0.5),
                                        iv=nb_iv, n_guard_fail=int(sum(1 for r in grows if not r.get("guard_pass"))))
            nb_lo = np.log1p(A4S.nb_ppf(alpha / 2.0, mu_E, a_g))
            nb_hi = np.log1p(A4S.nb_ppf(1.0 - alpha / 2.0, mu_E, a_g))
            t_nb = time.time() - tn
        base = fit.base_row()
        allidx = np.arange(fit.n_E)
        for sc, mm in mach.items():                                   # hcp at o = 0
            q, fc = C.wq_cols(mm["S_C"], w, 1.0 / (K + 1), [1 - alpha])
            lo, hi = mm["iv"](q[0][None, :], allidx)
            met = C.interval_metrics(Y_E[:, mm["gi"]], lo, hi, sl_all)
            rows.append(dict(C._row(base, "hcp", alpha, 0, 0, met, fc[0], K, fit.n_E), score=sc,
                             n_genes=len(mm["gi"])))
        if "nb" not in skip:
            met = C.interval_metrics(Y_E[:, gnb], nb_lo, nb_hi, sl_all)
            rows.append(dict(C._row(base, "nb_model", alpha, 0, 0, met, True, 0, fit.n_E), score="nb",
                             n_genes=len(gnb)))
        for ld in range(C.N_LABEL_DRAWS):                             # within_plain at o
            perm = C.label_stream(fit, ld)
            for o in SCORE_O:
                if fit.n_E - o < 10:
                    continue
                labi = perm[:o]
                keep = np.ones(fit.n_E, bool)
                keep[labi] = False
                kidx = np.flatnonzero(keep)
                slk = C._Slides(fit.samp_E[kidx])
                for sc, mm in mach.items():
                    q, fc = C.split_q_cols(mm["S_E"](labi), [alpha])
                    lo, hi = mm["iv"](q[0][None, :], kidx)
                    met = C.interval_metrics(Y_E[kidx][:, mm["gi"]], lo, hi, slk)
                    rows.append(dict(C._row(base, "within_plain", alpha, o, ld, met, fc[0], o, len(kidx)), score=sc,
                                     n_genes=len(mm["gi"])))
                if "nb" not in skip:
                    met = C.interval_metrics(Y_E[kidx][:, gnb], nb_lo[kidx], nb_hi[kidx], slk)
                    rows.append(dict(C._row(base, "nb_model", alpha, o, ld, met, True, 0, len(kidx)), score="nb",
                                     n_genes=len(gnb)))
        timing.append(dict(task=a.task, encoder=a.encoder, fold=fit.fold, cal_draw=fit.cal_draw,
                           n_T=int(ex["Tm"].sum()), n_C=fit.n_C, n_E=fit.n_E, n_genes=G, s_fit=round(t_fit, 2),
                           s_sigma=round(t_sig, 2), s_cqr=round(t_cqr, 2),
                           cqr_genes=int(len(mach["cqr"]["gi"])) if "cqr" in mach else 0,
                           s_cqr_per_gene=(round(t_cqr / max(1, len(mach["cqr"]["gi"])), 3) if "cqr" in mach else None),
                           cqr_failures=mach.get("cqr", {}).get("n_fail"), cqr_subsampled=mach.get("cqr", {}).get("n_sub"),
                           s_nb=round(t_nb, 2), nb_guard_fail=mach.get("nb_conformal", {}).get("n_guard_fail"),
                           s_total=round(time.time() - t1, 2)))
        log(f"[f3map scores] {a.task} {fit.fold} cal{fit.cal_draw} total {time.time() - t0:.0f}s {timing[-1]}")
    tag = f"{a.task.replace(':', '_')}__{a.encoder}"
    pd.DataFrame(timing).to_csv(os.path.join(a.out, f"scores_timing__{tag}.csv"), index=False)
    d = pd.DataFrame(rows)
    keys = ["task", "encoder", "score", "method", "alpha", "o", "K", "fold", "n_T_donors", "n_genes"]
    d.groupby(keys).agg(coverage=("coverage", "mean"), width_mean=("width_mean", "mean"),
                        width_median=("width_median", "mean"), finite_frac=("finite", "mean"),
                        n_draws=("draw", "nunique")).reset_index().to_csv(
        os.path.join(a.out, f"scores_by_fold__{tag}.csv"), index=False)
    d[C.FIXED_COLS + C.EXTRA_COLS + ["score", "n_genes"]].to_csv(
        os.path.join(a.out, f"scores_full__{tag}.csv.gz"), index=False)
    log(f"[f3map scores] done {len(d)} rows {time.time() - t0:.0f}s")


# ================================================================== 5d.4 item 3: ACS by state, within_full added
ACS_O = (0, 3, 5, 9, 10, 12, 15, 17, 20, 25, 30, 50, 100, 200)
_ACS = {}


def _acs_module():
    if "A" not in _ACS:
        import importlib.util
        assert md5(ACS_CODE) == ACS_CODE_MD5, f"{ACS_CODE}: md5 differs from {ACS_CODE_MD5}"
        os.environ.setdefault("R4CONF_SCRIPTS", HERE)
        spec = importlib.util.spec_from_file_location("round4_conf_c3_acs_o", ACS_CODE)
        A = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(A)
        A.O_GRID = ACS_O      # round 4's grid (0, 5, 10, 25, 50, 100, 200) joined with the map's o = m grid
        _ACS["A"] = A
    return _ACS["A"]


def _acs_init(data, poolq):
    _acs_module().init_worker(data, poolq)


def _acs_wf(d):
    A = _acs_module()
    RES, FOLD = A.DATA
    out = []
    for f in sorted(set(FOLD.values())):
        fs = sorted(s for s in FOLD if FOLD[s] == f)
        for t in fs:
            K = len(fs) - 1
            xt = RES[t][np.random.default_rng(A.crc(f"ACS|perm|{t}|{d}")).permutation(len(RES[t]))]
            for o in A.O_GRID:
                if o == 0:
                    continue
                init, ev = xt[:o], xt[o:]
                for a in A.ALPHAS:
                    m = W3.wf_m(o, a)
                    if o < 2 or m == 0:
                        q, cov = math.inf, 1.0
                    else:
                        L, Hh, is_int, lo, hi = W3.wf_hull(init[:, None], m)
                        c, q = float((L[0] + Hh[0]) / 2), float((Hh[0] - L[0]) / 2)
                        if not math.isfinite(q):
                            cov = 1.0
                        elif bool(is_int[0]):
                            cov = float(np.mean(np.abs(ev - c) <= q))
                        else:
                            cov = float(np.mean(W3.wf_exact_count(lo[:, 0], hi[:, 0], ev) >= m))
                    fin = int(math.isfinite(q))
                    out.append((f, t, K, d, o, "within_full", a, cov, 2 * q if fin else math.inf, len(ev), fin, fin))
    return out


def _acs_draw(d):
    return _acs_module().one_draw(d) + _acs_wf(d)


def run_acs(a):
    from concurrent.futures import ProcessPoolExecutor
    os.makedirs(a.out, exist_ok=True)
    A = _acs_module()
    t0 = time.time()
    argv0 = sys.argv
    sys.argv = [argv0[0], a.pred]          # round 4's load() reads the parquet path from argv[1]
    try:
        data = A.load()
    finally:
        sys.argv = argv0
    poolq = A.pooled_q(data)
    lo, hi = (int(x) for x in a.draws.split("-"))
    draws = list(range(lo, hi + 1))
    with ProcessPoolExecutor(a.workers, initializer=_acs_init, initargs=(data, poolq)) as ex:
        res = list(ex.map(_acs_draw, draws))
    cols = ["fold", "state", "K", "draw", "o", "method", "alpha", "coverage", "width", "n_test", "finite", "finite_code"]
    df = pd.DataFrame([r for rr in res for r in rr], columns=cols)
    g = df.groupby(["method", "alpha", "o", "fold", "draw"], sort=True)

    def agg(x):                              # round 4's main(), unchanged in substance
        fw = x.loc[x.finite == 1, "width"]
        return pd.Series(dict(K=int(x.K.iloc[0]), coverage=x.coverage.mean(),
                              width_mean=fw.mean() if len(fw) else math.inf,
                              width_median=fw.median() if len(fw) else math.inf,
                              n_test=int(x.n_test.sum()), finite=x.finite.mean()))
    sw = g.apply(agg, include_groups=False).reset_index()
    sw.insert(0, "task", A.TASK)
    sw.insert(1, "label_set", A.LABEL_SET)
    sw.insert(2, "encoder", A.ENC)
    sw.insert(4, "score", A.SCORE)
    sw = sw[["task", "label_set", "encoder", "method", "score", "alpha", "o", "K", "fold", "draw", "coverage",
             "width_mean", "width_median", "n_test", "finite"]]
    sw["k_meets_alpha01"] = (1.0 / (sw["K"] + 1)) <= 0.1 + 1e-12
    sw.to_csv(os.path.join(a.out, "acs_o_sweep.csv"), index=False)
    df.to_csv(os.path.join(a.out, "acs_o_sweep_by_state.csv.gz"), index=False)
    json.dump(dict(draws=draws, workers=a.workers, rows_fold=len(sw), rows_state=len(df), o_grid=list(ACS_O),
                   seconds=round(time.time() - t0, 1), acs_code=ACS_CODE, acs_code_md5=ACS_CODE_MD5,
                   pred=a.pred, pred_md5=md5(a.pred)),
              open(os.path.join(a.out, "acs_info.json"), "w"), indent=1)
    log(f"[f3map acs] {len(draws)} draws, {len(sw)} fold rows, {time.time() - t0:.0f}s")


# ================================================================== main
def main(argv=None):
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="mode", required=True)
    m = sub.add_parser("map")
    m.add_argument("--task", required=True)
    m.add_argument("--encoder", required=True)
    m.add_argument("--part", type=int, choices=[1, 2], required=True)
    m.add_argument("--K", type=int, nargs="*", default=None)
    m.add_argument("--folds", default=None)
    m.add_argument("--cal-draws", default="0,1,2")
    m.add_argument("--no-final", action="store_true")
    m.add_argument("--max-specs", type=int, default=0)
    m.add_argument("--out", required=True)
    s = sub.add_parser("scores")
    s.add_argument("--task", required=True)
    s.add_argument("--encoder", default="uni_v2")
    s.add_argument("--folds", default=None)
    s.add_argument("--cal-draws", default="0,1,2")
    s.add_argument("--cqr-genes", type=int, default=0)
    s.add_argument("--skip", default="")
    s.add_argument("--out", required=True)
    c = sub.add_parser("acs")
    c.add_argument("--pred", required=True)
    c.add_argument("--out", required=True)
    c.add_argument("--draws", default="0-19")
    c.add_argument("--workers", type=int, default=4)
    k = sub.add_parser("checkfit")
    k.add_argument("--task", required=True)
    k.add_argument("--encoder", required=True)
    k.add_argument("--fold", required=True)
    k.add_argument("--out", required=True)
    a = p.parse_args(argv)
    {"map": run_map, "scores": run_scores, "acs": run_acs, "checkfit": run_checkfit}[a.mode](a)


if __name__ == "__main__":
    main()
