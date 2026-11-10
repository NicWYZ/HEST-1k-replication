"""Round 10, track final-runs, F2.1: the limits arms of regime A (plan, section 5.2).

On the same populations as round10_final_runs_f2_regimeA.py (one task, encoder, scale, estimand, gene: G donor values
z_g with predictions f_g) and on the FIRST R_lim of its draws (the same seed tag `task|encoder|scale|estimand|gene|n_L`,
and rng.random((R_lim, G)) is the first R_lim rows of rng.random((R, G))), this driver runs

  * same-sample tuning by round 4's rules a_b1 and b_cluster, and the cross-fitted rule c_crossfit_design, through
    round 4's lambda_rule and round 5's design_whole_clusters(..., lin=True) and (..., lin=True, xf=True), called
    unchanged through round 5's BAL.estimate_srs_like (the call E4b makes), with the draws as columns. For the
    donor-weighted target, a_b1 is round 4's donor-pairs rule, the same formula as b_cluster (round 4's docstring),
    so no spot-level statistics enter; the job checks the two agree draw for draw. Rule none is run as the control
    and must equal the classical estimator of round10_final_runs_estimators.py draw for draw.
  * round 4's own PPI++ form of the same rules (estimate, theta = cU mean_U(f) + mean_L(z - lam f), with U the
    unlabelled complement) with round 4's variances, interval CR1_t|fpc.
  * Kluger et al.'s cluster bootstrap through round 7's kluger_draw (B = round 7's B_BOOT unless the config sets B_kluger)
    under the regime's design, simple random sampling of n_L clusters, so pi = n_L/G and xi the labelled mask. Draws are
    passed as columns in chunks of `chunk`; one bootstrap count matrix is shared by the draws of a chunk, as round 7
    shared it by the genes of a draw.

usage: round10_final_runs_f2_limits.py <config.json> <out_dir>
config: cluster_values, select, n_grid, extra_n (as regime A), R_lim, B_kluger, chunk, label; optional max_pops, part ([k, K]: the populations whose index
        in the sorted groupby is k modulo K), check_draws
        (regenerate the regime A draws at R and assert the first R_lim agree) and anchor_r5 (see run_anchor).
Writes limits_summary.json first, then limits_cells.parquet (regime A's schema) and limits_diag.parquet.
"""
import importlib.util, json, os, sys, time
import numpy as np, pandas as pd, pyarrow as pa, pyarrow.parquet as pq
import round4_ppi_estimator as R4
import round5_ppi_balance as BAL
import round7_ppi_s2_comparators as S2
import round10_final_runs_estimators as E
from round10_final_runs_f2_regimeA import row, selected, seed_of, KEYS, SCHEMA

RULES = ("none", "a_b1", "b_cluster", "c_crossfit_design")
LIN, XF, CR1 = "textbook_t|fpc|lin", "textbook_t|fpc|lin|xf", "CR1_t|fpc"
DIAG = pa.schema([(k, pa.string()) for k in KEYS] + [("G", pa.int64()), ("n", pa.int64()), ("arm", pa.string()),
                 ("R", pa.int64()), ("lam_mean", pa.float64()), ("lam_median", pa.float64()),
                 ("frac_lam0", pa.float64()), ("frac_lam1", pa.float64()), ("boot_drop_mean", pa.float64())])


def tlohi(th, v, df):
    lo, hi = R4.t_interval(th, v, df)
    ok = np.isfinite(th) & np.isfinite(v) & (v >= 0) & np.isfinite(df) & (df >= 1)
    return lo, hi, ok


def masks(L, G):
    R = L.shape[0]
    Lm = np.zeros((G, R), bool)
    Lm[L.T, np.arange(R)[None, :]] = True
    return Lm


def limits(z, f, L, theta, tag, B, chunk):
    """All limits arms on one population at one n_L. L (R, n) labelled indices. Returns (rows, diag, checks)."""
    G = len(z); R, n = L.shape
    Lm = masks(L, G)
    Z = np.ascontiguousarray(np.broadcast_to(z[:, None], (G, R))); F = np.ascontiguousarray(np.broadcast_to(f[:, None], (G, R)))
    out, diag, chk, keep = [], [], {}, {}
    D = BAL.stats_arrays(Z, F)
    for rule in RULES:
        o, lam = BAL.estimate_srs_like(Z, F, Lm, rule, f"{tag}|limits|{rule}")
        keep[rule] = o
        ivs = (LIN, XF) if rule == "c_crossfit_design" else (LIN,)
        for iv in ivs:
            th, v, df = o[iv]
            lo, hi, ok = tlohi(th, v, df)
            out.append(dict(arm=f"r4_{rule}", variance=iv, **row(th, theta, lo, hi, ok, v)))
        if rule != "c_crossfit_design":
            chk[f"xf_minus_lin_{rule}"] = float(np.nanmax(np.abs(o[XF][1] - o[LIN][1])))
        res = R4.estimate("donor", D, Lm, ~Lm, lam)
        v, df = R4.variances(res, G_pop=G)[CR1]
        lo, hi, ok = tlohi(res["theta"], v, np.broadcast_to(df, v.shape).astype(float))
        out.append(dict(arm=f"r4ppi_{rule}", variance=CR1, **row(res["theta"], theta, lo, hi, ok, v)))
        cu = np.asarray(lam["cU"], float)
        diag.append(dict(arm=f"r4_{rule}", R=R, lam_mean=float(np.mean(cu)), lam_median=float(np.median(cu)),
                         frac_lam0=float(np.mean(cu == 0)), frac_lam1=float(np.mean(cu == 1)), boot_drop_mean=np.nan))
    # controls: rule none is the classical estimator; a_b1 equals b_cluster for the donor-weighted target
    c0 = E.classical(z, f, L)
    th0, v0, _ = keep["none"][LIN]
    chk["none_vs_classical"] = float(max(np.abs(th0 - c0["est"]).max(), np.abs(v0 - c0["v"]).max()))
    chk["a_b1_vs_b_cluster"] = float(max(np.abs(keep["a_b1"][LIN][0] - keep["b_cluster"][LIN][0]).max(),
                                         np.abs(keep["a_b1"][LIN][1] - keep["b_cluster"][LIN][1]).max()))
    # Kluger et al.'s cluster bootstrap, round 7's kluger_draw unchanged
    cols = {k: np.full(R, np.nan) for k in ("ptd", "lo", "hi", "omega", "boot_drop")}
    for a in range(0, R, chunk):
        m = min(chunk, R - a)
        pi = np.full((G, m), n / G)
        o = S2.kluger_draw(Z[:, a:a + m], F[:, a:a + m], pi, Lm[:, a:a + m],
                           np.random.default_rng(seed_of(f"{tag}|kluger|c{a}")), B=B)
        for k in cols:
            cols[k][a:a + m] = o[k]
    ok = np.isfinite(cols["lo"]) & np.isfinite(cols["hi"]) & np.isfinite(cols["ptd"])
    out.append(dict(arm="kluger_ptd", variance="cluster_boot", **row(cols["ptd"], theta, cols["lo"], cols["hi"], ok)))
    om = cols["omega"]
    diag.append(dict(arm="kluger_ptd", R=R, lam_mean=float(np.nanmean(om)), lam_median=float(np.nanmedian(om)),
                     frac_lam0=float(np.nanmean(om == 0)), frac_lam1=float(np.nanmean(om == 1)),
                     boot_drop_mean=float(np.nanmean(cols["boot_drop"]))))
    return out, diag, chk


def _snap_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


def run_anchor(cfg, out):
    """Round 5's E4b reference cell through the limits arm: round 5's draws (E4b's cand_idx, candidate 0) and seeds,
    this track's cluster values in round 5's donor and gene order, BAL.estimate_srs_like per draw with genes as columns,
    summarised by E4b's own summarise (both read from round 5's snapshot). Also checks that the production call with
    draws as columns gives the same rule none, a_b1 and b_cluster estimates and variances on the same draws."""
    A = cfg["anchor_r5"]
    e4b = _snap_module(A["e4b_script"], "r5_e4b_snapshot")
    from round5_ppi_e2_regimeB import load_arm
    data = load_arm(A["pred_parquet"], A["arm"], A["vtag"])
    donors_all = np.asarray(data["donors"]); donors = [str(d) for d in donors_all]; genes = list(data["genes"])
    cv = pd.read_parquet(A["cluster_values"])
    cv = cv[(cv.task == A["task"]) & (cv.encoder == A["arm"]) & (cv.scale == "log1p") & (cv.estimand == A["estimand"])]
    Zp = cv.pivot(index="donor", columns="gene", values="z"); Fp = cv.pivot(index="donor", columns="gene", values="f")
    vd = [d for d in donors if d in Zp.index and np.isfinite(Zp.loc[d].to_numpy(float)).all()]
    vid = np.array([donors.index(d) for d in vd])
    gl = [g for g in genes if g in Zp.columns]
    zbar = Zp.loc[vd, gl].to_numpy(float); fbar = Fp.loc[vd, gl].to_numpy(float)
    G, ng = zbar.shape; theta = zbar.mean(0); nL = int(A["n_L"]); est = A["estimand"]
    acc, Ls = {}, []
    for d in range(int(A["draws"])):
        cand = e4b.cand_idx(donors_all, A["vtag"], nL, d, 0)
        lm = np.isin(vid, cand)
        Lm = np.ascontiguousarray(np.broadcast_to(lm[:, None], (G, ng)))
        Ls.append(np.flatnonzero(lm))
        for rule in ("none", "c_crossfit_design", "a_b1", "b_cluster"):
            o, _ = BAL.estimate_srs_like(zbar, fbar, Lm, rule, f"q2|{A['vtag']}|nL{nL}|m0|d{d}|{est}|donor|{rule}")
            for iv, (th, v, df) in o.items():
                acc.setdefault((rule, iv), []).append((th, v, df, d))
    rows, generows = [], []
    cell = dict(vtag=A["vtag"], arm=A["arm"], estimand=est, G=G, n_L=nL, design="D0", balance="none", p_a=1.0,
                n_draws=int(A["draws"]))
    e4b.summarise(acc, theta, cell, gl, rows, generows, gene_rows=False)
    s = pd.DataFrame(rows)
    ref = pd.read_csv(A["e4b_grid"])
    ref = ref[(ref.vtag == A["vtag"]) & (ref.arm == A["arm"]) & (ref.estimand == est) & (ref.n_L == nL) &
              (ref.design == "D0") & (ref.balance == "none") & (ref.n_sub == int(A["draws"]))]
    m = s.merge(ref, on=["vtag", "arm", "estimand", "G", "n_L", "design", "balance", "p_a", "n_draws", "rule", "interval",
                         "n_sub"], how="left", suffixes=("", "_r5"))
    for c in ("n_genes", "coverage_median", "width_median", "emp_var_median", "est_var_over_emp_var_median", "coverage_mean"):
        m["d_" + c] = (m[c] - m[c + "_r5"]).abs()
    m.to_csv(os.path.join(out, "limits_anchor_r5.csv"), index=False)
    # production call (draws as columns) against the per-draw call, rules without randomness
    L = np.array(Ls); dev = {}
    for j in range(min(ng, int(A.get("check_genes", 5)))):
        Lm = masks(L, G); Z = np.repeat(zbar[:, [j]], len(L), 1); F = np.repeat(fbar[:, [j]], len(L), 1)
        for rule in ("none", "a_b1", "b_cluster"):
            o, _ = BAL.estimate_srs_like(Z, F, Lm, rule, "unused")
            th_ref = np.array([x[0][j] for x in acc[(rule, LIN)]]); v_ref = np.array([x[1][j] for x in acc[(rule, LIN)]])
            dev[rule] = max(dev.get(rule, 0.0), float(np.abs(o[LIN][0] - th_ref).max()), float(np.abs(o[LIN][1] - v_ref).max()))
    key = m[(m.rule == "c_crossfit_design") & (m.interval == XF)].iloc[0]
    return dict(G=G, genes=ng, rows=len(m), rows_matched=int(m.coverage_median_r5.notna().sum()),
                coverage_median=float(key.coverage_median), coverage_median_r5=float(key.coverage_median_r5),
                width_median=float(key.width_median), width_median_r5=float(key.width_median_r5),
                max_d_coverage_median=float(m.d_coverage_median.max()), max_d_width_median=float(m.d_width_median.max()),
                max_d_n_genes=float(m.d_n_genes.max()), columns_vs_draws_maxdev=dev)


def main():
    cfg = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    summ = dict(config=cfg, started=time.strftime("%Y-%m-%dT%H:%M:%S"))
    sp = os.path.join(out, "limits_summary.json"); json.dump(summ, open(sp, "w"), indent=1)
    if cfg.get("anchor_r5"):
        summ["anchor_r5"] = run_anchor(cfg, out); json.dump(summ, open(sp, "w"), indent=1)
        print(json.dumps(summ["anchor_r5"]), flush=True)
        if cfg.get("anchor_only"):
            return
    cv = pd.concat([pd.read_parquet(p) for p in cfg["cluster_values"]], ignore_index=True)
    cv = cv[selected(cv, cfg.get("select"))]
    R, B, chunk = int(cfg["R_lim"]), int(cfg.get("B_kluger", S2.B_BOOT)), int(cfg.get("chunk", 100))
    rows, drows, n_pop, n_skip, t0 = [], [], 0, [], time.time()
    chk_max, draw_check = {}, None
    part = cfg.get("part")
    for ip, (key, g) in enumerate(cv.groupby(KEYS, sort=True)):
        if part and ip % int(part[1]) != int(part[0]):
            continue
        g = g.sort_values("donor"); z = g.z.to_numpy(float); f = g.f.to_numpy(float); G = len(z)
        tagk = "|".join(key)
        if not (np.isfinite(z).all() and np.isfinite(f).all()):
            n_skip.append(tagk); continue
        if cfg.get("max_pops") and n_pop >= int(cfg["max_pops"]):
            break
        n_pop += 1; theta = z.mean()
        ngrid = sorted(set(cfg["n_grid"]) | set(cfg.get("extra_n", {}).get(key[0], [])))
        for n in ngrid:
            if n >= G:
                continue
            tag = f"{tagk}|{n}"
            L = np.argsort(np.random.default_rng(seed_of(tag)).random((R, G)), axis=1)[:, :n]
            if cfg.get("check_draws") and draw_check is None:
                Lfull = np.argsort(np.random.default_rng(seed_of(tag)).random((int(cfg["check_draws"]), G)), axis=1)[:R, :n]
                draw_check = dict(tag=tag, equal=bool((Lfull == L).all()))
            res, dg, chk = limits(z, f, L, theta, tag, B, chunk)
            for k, v in chk.items():
                chk_max[k] = max(chk_max.get(k, 0.0), v)
            for r in res:
                rows.append(dict(zip(KEYS, key), G=G, n=n, **r))
            for r in dg:
                drows.append(dict(zip(KEYS, key), G=G, n=n, **r))
        if n_pop % 25 == 0:
            print(f"{n_pop} populations, {len(rows)} rows, {time.time() - t0:.0f}s", flush=True)
    tol = 1e-10 * max(1.0, float(np.nanmax(np.abs(cv.z.to_numpy(float)))) ** 2) if len(cv) else 1e-10
    failed = {k: v for k, v in chk_max.items() if k in ("none_vs_classical", "a_b1_vs_b_cluster") and v > tol}
    d = pd.DataFrame(rows, columns=SCHEMA.names); dd = pd.DataFrame(drows, columns=DIAG.names)
    summ.update(n_populations=n_pop, n_skipped=len(n_skip), skipped=n_skip[:200], n_rows=len(d), checks_max=chk_max,
                check_tol=tol, checks_failed=failed, draw_check=draw_check, R_lim=R, B_kluger=B, chunk=chunk,
                seconds=round(time.time() - t0, 1), finished=time.strftime("%Y-%m-%dT%H:%M:%S"))
    json.dump(summ, open(sp, "w"), indent=1)
    pq.write_table(pa.Table.from_pandas(dd, schema=DIAG, preserve_index=False), os.path.join(out, "limits_diag.parquet"))
    pq.write_table(pa.Table.from_pandas(d, schema=SCHEMA, preserve_index=False), os.path.join(out, "limits_cells.parquet"))
    print(json.dumps({k: v for k, v in summ.items() if k != "config"}, indent=1))
    if failed or (draw_check is not None and not draw_check["equal"]):
        raise SystemExit(f"control check failed: {failed} {draw_check}")


if __name__ == "__main__":
    main()
