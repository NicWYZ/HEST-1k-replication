#!/usr/bin/env python
"""C3.4 diagnostic: top-decile coverage of the CQR score inside GHCP and within_plain, CCRCC only.

Quantile heads: round3_a4_scores.fit_cqr / cqr_predict imported unmodified (A4's scope: 6 evenly
spaced genes via gene_subset, quantiles 0.05 and 0.95, HiGHS, T pre-subsampled to 2500 spots,
calibration draw 0 only). Base head and folds are round4_conf_c3's. Score s = max(qlo - y, y - qhi)
(Romano et al.), interval [qlo - q, qhi + q]. Top decile = the highest of ten per-gene quantile bins of
the BASE head's prediction pooled over the design's test spots (round 3 A4 `_deciles_for_design`,
H.bin_edges_quantile, bin 9).

Methods (alpha = 0.1 only): ghcp_noad (eta 0), ghcp_r05_noad (eta 0.5, eq. 8 pool), within_plain, and
the o = 0 cross-donor references hcp and pooled, each with score abs and cqr. GHCP with the CQR score is
run WITHOUT within-group adaptation: the adaptation shrinks a group mean of signed residuals, which
is not defined for the signed CQR score, so the paired abs comparison is also the no-adaptation form.
Pools and donor draws use the same seeds as C.o_rows (same variant name), so abs and cqr share them.
Assumptions and guarantees are those of the host methods (README, round4_conf_c3 docstring); the
CQR score changes the interval shape, not the guarantee. abs rows are computed on all genes
('all') and on the CQR gene subset ('cqr6'); cqr rows only on 'cqr6'.
Usage: run_c34.py <encoder> <outdir>
"""
import hashlib, json, os, platform, sys, time, types
import numpy as np
import pandas as pd
import round4_conf_c3 as C
import round4_conf_io as IO
import round4_conf_sim as SIM
import round3_a4_scores as A4

EXPECT_MD5 = "2d8418677cf8290eec89a14c315b92cd"
ALPHA = 0.1
VARS = ("ghcp_noad", "ghcp_r05_noad")


def cpu_info():
    v = m = ""
    for line in open("/proc/cpuinfo"):
        if line.startswith("vendor_id") and not v:
            v = line.split(":", 1)[1].strip()
        if line.startswith("model name") and not m:
            m = line.split(":", 1)[1].strip()
    return dict(vendor=v, model=m, node=platform.node())


def ghcp_signed(X, N, init, o, beta, variant, seed_key):
    """Copy of C.ghcp_cols with m = 0 and the scores taken as given (no abs). X list of per-donor
    score arrays (n_j, g), init (o, g). Returns q (g,)."""
    v = C.GHCP_VARIANTS[variant]
    rng = np.random.default_rng(C.crc(seed_key + "|" + variant))
    S = SIM.restricted_pool(N, o, v["eta"], rng, v["rule"])
    if len(S) == 0:
        L = o + 1
        q, _ = C.wq_cols(init[:o], np.full(o, 1.0 / L), 1.0 / L, [beta])
        return q[0]
    J0 = int(S[rng.integers(len(S))])
    Scal = [int(j) for j in S if j != J0]
    M = len(Scal) + 1
    sc = [X[j] for j in Scal]
    wt = [np.full(len(X[j]), 1.0 / (M * len(X[j]))) for j in Scal]
    sc.append(init[:o])
    wt.append(np.full(o, 1.0 / (M * N[J0])))
    q, _ = C.wq_cols(np.concatenate(sc, axis=0), np.concatenate(wt), (N[J0] - o) / (M * N[J0]), [beta])
    return q[0]


def main(enc, outdir):
    md5 = hashlib.md5(open(C.__file__, "rb").read()).hexdigest()
    assert md5 == EXPECT_MD5, md5
    out = os.path.join(outdir, f"c34_ccrcc24_{enc}")
    os.makedirs(out, exist_ok=True)
    IO.code_head = C._read_head
    IO.stamp(out, track="conformal-C3", note=f"C3.4 CQR top-decile diagnostic {enc}")
    T = C.load_task("CCRCC:24", enc)
    H = T.H
    specs = [s for s in T.specs(K=10, n_cal_draws=C.N_CAL_DRAWS) if int(s["cal_draw"]) == 0]
    ng = len(T.genes)
    gi = A4.gene_subset(ng, 6)
    args = types.SimpleNamespace(cqr_budget_s=0.0, cqr_timebox_s=1200.0, cqr_subsample=2500,
                                 cqr_presubsample=1)
    t0 = time.time()
    # pass 1: base predictions of every fold -> per-gene decile bins pooled over folds
    preds = []
    for sp in specs:
        Tm = H.apply_size_match(sp, T.task)
        _, Yl = T._labels(sp)
        pipe, A, reg, _ = H.fit_base(T.X[Tm], Yl[Tm])
        preds.append(reg.predict(pipe.transform(T.X[sp["E"]].astype(np.float64, copy=False))))
    pooled = np.concatenate(preds, axis=0)
    dec_all = np.empty(pooled.shape, dtype=np.int8)
    for j in range(ng):
        dec_all[:, j] = H.bin_edges_quantile(pooled[:, j].astype(float), A4.N_DECILES)
    off = np.cumsum([0] + [len(p) for p in preds])
    print(f"pass1 done {time.time()-t0:.0f}s, {len(specs)} folds, {pooled.shape}", flush=True)
    rows, fits_log = [], []

    def add(fold, method, score, gset, o, ld, cov, widths, top):
        keep = rows_keep
        sel_top = top & keep[:, None]
        sel_all = np.broadcast_to(keep[:, None], top.shape)
        fin = np.isfinite(widths)
        rows.append(dict(fold=fold, method=method, score=score, gene_set=gset, alpha=ALPHA, o=o,
                         label_draw=ld, n_top=int(sel_top.sum()), cov_top=int((cov & sel_top).sum()),
                         n_all=int(sel_all.sum()), cov_all=int((cov & sel_all).sum()),
                         wsum_top=float(widths[sel_top & fin].sum()), wn_top=int((sel_top & fin).sum()),
                         fin_top=bool(fin[sel_top].all()), fin_all=bool(fin[sel_all].all())))

    for fi, sp in enumerate(specs):
        fit = T.fit(sp)
        Tm = H.apply_size_match(sp, T.task)
        _, Yl = T._labels(sp)
        pipe, A, reg, _ = H.fit_base(T.X[Tm], Yl[Tm])
        A_C = pipe.transform(T.X[sp["C"]].astype(np.float64, copy=False))
        A_E = pipe.transform(T.X[sp["E"]].astype(np.float64, copy=False))
        assert np.allclose(reg.predict(A_E), fit.P_E, rtol=0, atol=1e-10)
        cstate = dict(cqr_seconds=0.0, cqr_fallback=False, base={})
        mods, frows = A4.fit_cqr(A, Yl[Tm].astype(np.float64, copy=False), gi, cstate,
                                 f"CCRCC|24|c34|{enc}|{fit.fold}|{sp['cal_draw']}", args)
        ok = np.array([mods.get((j, A4.CQR_QUANTILES[0])) is not None and
                       mods.get((j, A4.CQR_QUANTILES[1])) is not None for j in gi])
        assert ok.all(), "a CQR fit failed"
        qlo_C, qhi_C = A4.cqr_predict(mods, A_C, gi)
        qlo_E, qhi_E = A4.cqr_predict(mods, A_E, gi)
        P_C = reg.predict(A_C)
        Y_C = fit.R_C + P_C
        SC = np.maximum(qlo_C[:, :] - Y_C[:, gi], Y_C[:, gi] - qhi_C)
        SE = np.maximum(qlo_E - fit.Y_E[:, gi], fit.Y_E[:, gi] - qhi_E)
        fits_log.append(dict(fold=fit.fold, n_T=int(Tm.sum()), seconds=round(sum(r["seconds"] for r in frows), 1),
                             n_T_used=int(np.median([r["n_T_used"] for r in frows])),
                             fallback=any(r["subsample_fallback"] for r in frows)))
        top_all = dec_all[off[fi]:off[fi + 1]] == A4.N_DECILES - 1
        top6 = top_all[:, gi]
        R = fit.R_E
        n_E = fit.n_E
        cq_w0 = qhi_E - qlo_E
        # sets of score arrays
        fake = types.SimpleNamespace(task_key=fit.task_key, fold=fit.fold, lab_C=fit.lab_C,
                                     groups=fit.groups, R_C=SC)
        ctx_c = C._GhcpCtx(fake)
        ctx_a = fit.ctx()
        rows_keep = np.ones(n_E, bool)
        # o = 0 references: hcp and pooled, abs and cqr
        labs = fit.lab_C.astype(str)
        K = len(fit.groups)
        Nk = np.array([int((labs == g).sum()) for g in fit.groups])
        w = np.concatenate([np.full(Nk[k], 1.0 / ((K + 1) * Nk[k])) for k in range(K)])
        order = np.concatenate([np.flatnonzero(labs == g) for g in fit.groups])
        if fi == 0:
            o0 = C.o0_rows(fit, alphas=(ALPHA,), methods=("hcp",))[0]
            qchk, _ = C.wq_cols(fit.S_C[order], w, 1.0 / (K + 1), [1 - ALPHA])
            assert abs(o0["width_mean"] - 2 * qchk[0].mean()) < 1e-9, (o0["width_mean"], 2 * qchk[0].mean())
        for score, S_C, Sfull in (("abs", fit.S_C, None), ("cqr", SC, None)):
            Sc = S_C[order]
            q_h, _ = C.wq_cols(Sc, w, 1.0 / (K + 1), [1 - ALPHA])
            q_h = q_h[0]
            q_p, _ = C.split_q_cols(S_C, [ALPHA])
            q_p = q_p[0]
            for method, q in (("hcp", q_h), ("pooled", q_p)):
                if score == "abs":
                    for gset, cols, top in (("all", slice(None), top_all), ("cqr6", gi, top6)):
                        cov = np.abs(R[:, cols]) <= q[cols]
                        wd = np.broadcast_to(2 * q[cols], cov.shape)
                        add(fit.fold, method, "abs", gset, 0, -1, cov, wd, top)
                else:
                    cov = SE <= q
                    wd = cq_w0 + 2 * q
                    add(fit.fold, method, "cqr", "cqr6", 0, -1, cov, wd, top6)
        for ld in range(C.N_LABEL_DRAWS):
            perm = C.label_stream(fit, ld)
            for o in C.O_GRID:
                if n_E - o < 10:
                    continue
                lab = perm[:o]
                rows_keep = np.ones(n_E, bool)
                rows_keep[lab] = False
                init_a = R[lab]
                init_c = SE[lab]
                seed = f"{fit.task_key}|{fit.fold}|K{fit.K}|cal{fit.cal_draw}|o{o}|ld{ld}"
                for variant in VARS:
                    q, c, fc, Kn = C.ghcp_cols(ctx_a, init_a, o, [1 - ALPHA], variant, fit.n_T_donors, seed)
                    q = q[0]
                    for gset, cols, top in (("all", slice(None), top_all), ("cqr6", gi, top6)):
                        cov = np.abs(R[:, cols] - c[cols]) <= q[cols]
                        add(fit.fold, variant, "abs", gset, o, ld, cov,
                            np.broadcast_to(2 * q[cols], cov.shape), top)
                    qc = ghcp_signed(ctx_c.X, ctx_c.N, init_c, o, 1 - ALPHA, variant, seed)
                    add(fit.fold, variant, "cqr", "cqr6", o, ld, SE <= qc, cq_w0 + 2 * qc, top6)
                q, _ = C.split_q_cols(np.abs(init_a), [ALPHA])
                q = q[0]
                for gset, cols, top in (("all", slice(None), top_all), ("cqr6", gi, top6)):
                    cov = np.abs(R[:, cols]) <= q[cols]
                    add(fit.fold, "within_plain", "abs", gset, o, ld, cov,
                        np.broadcast_to(2 * q[cols], cov.shape), top)
                q, _ = C.split_q_cols(init_c, [ALPHA])
                qc = q[0]
                add(fit.fold, "within_plain", "cqr", "cqr6", o, ld, SE <= qc, cq_w0 + 2 * qc, top6)
        if (fi + 1) % 4 == 0:
            print(f"  fold {fi+1}/{len(specs)} {time.time()-t0:.0f}s", flush=True)
    d = pd.DataFrame(rows)
    d.to_csv(f"{out}/c34_rows__{enc}.csv", index=False)
    pd.DataFrame(fits_log).to_csv(f"{out}/c34_cqr_fits__{enc}.csv", index=False)
    IO.write_provenance(out, "C3_c34", os.path.abspath(__file__),
                        dict(enc=enc, alpha=ALPHA, genes=[int(g) for g in gi], cqr_subsample=2500,
                             cal_draw=0, c3_md5=md5), extra=dict(rows=len(d), cpu=cpu_info()))
    json.dump(dict(rows=len(d), folds=len(specs), genes=[T.genes[g] for g in gi], cpu=cpu_info(),
                   seconds=round(time.time() - t0, 1)), open(f"{out}/run_info.json", "w"), indent=1)
    print("done", len(d), cpu_info(), flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
