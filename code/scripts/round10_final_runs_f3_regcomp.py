"""Round 10, track final-runs, F3.3 (i): regime A against regime B, cost-matched as in round 5's E3 (plan 5d.3 (i)).

Cells are round 5's E3 part 'regcomp' cells, taken from round5_ppi_e3_twolevel.part_cells unchanged: budgets
B in {2400, 4800, 9600}; regime A labels n_L in {4, 6, 8, 12} donors (n_L <= G - 2) with m_A = B // n_L spots in
each; regime B labels every valid donor at m_g = min(M_g, max(1, round(B' M_g / N))), at B' = B (cost 'unit') and at
the cost-matched B' = n_L (c + B / n_L) - c G for c in {10, 100, 1000} where it is positive. theta2 draws are
stratified by group with m_g raised to at least 4, as round 5's run_part does. Seeds are round 5's: the cell tag
'regcomp|<regime>|B<budget>|<cost>|nL<n_L>|m<m>', labelled donors 'r5e3|<vtag>|<tag>|d<d>' (round 3's draw_L), units
'r5e3u|<vtag>|<tag>|d<d>|<est>', cross-fit halves 'r5e3x|<vtag>|<tag>|d<d>|<est>'. So the first 200 draws of every
cell are round 5's draws and every arm of a draw sees the same units.

Arms on every draw.
  Regime A  C_fix1, the two-stage estimator with the coefficient fixed at 1 at both stages (plan 5d.3 (i)):
              theta_A = Fbar_U + (1/n_L) sum_{g in L} ebar_g,
              V_A = (1 - n_L/G) s^2_ebar / n_L + (1/(G n_L)) sum_{g in L} V_g,   t with n_L - 1 df,
            where ebar_g = zhat_g - fbar_g and zhat_g, V_g are round 5's within stage with the within coefficient
            fixed at 1 (round10_final_runs_estimators._tl_fixed, i.e. round5_ppi_twolevel.estimate with one inserted
            line). For the mean, ebar_g is the labelled mean of y - f and V_g = (1 - m_g/M_g) s^2_{e,g} / m_g; for
            theta3 and theta2 they are round 5's form C unit contributions on the residual y - f. This is round 5's
            regime A between stage with lambda_c = c_U = 1, so no coefficient is estimated and no cross-fitting term
            enters. Interval name 'twostage_t|fpc'.
            C_ppi and C_classical, round 5's regime A (round5_ppi_twolevel.estimate, regime_b False), with intervals
            'textbook_t|fpc|lin' (no cross-fitting term) and 'textbook_t|fpc|lin|xf' (round 5's primary).
  Regime B  C_fix1, C_ppi, C_classical through round10_final_runs_estimators.regime_b_formC, interval 'regB_t'.
The two-fold cross-fitted form of F2 is defined on whole clusters and is not formed in two-stage regime A.

usage: round10_final_runs_f3_regcomp.py run <config.json> <out_dir>
       round10_final_runs_f3_regcomp.py compare_r5 <config.json> <out_dir>
config (run): populations [F2's population dict, optional R and cells (a filter dict that replaces the config's)], R, regimes (subset of A, B), budgets (subset), costs (subset of
        'unit', 10, 100, 1000; default all), n_L (subset), anchor {ref_csv, draws} (optional: the listed cells are
        also run at 'draws' and their C_ppi and C_classical rows compared with round 5's rows).
config (compare_r5): new_csv, ref_csv (round 5's e3_regcomp file), ref_merged (e3_regime_comparison.csv),
        new_genes, ref_genes, vtag, arm, named [{regime, budget, cost, n_L, m, estimand, interval, estimator}].
Writes regcomp_summary.json first, then regcomp_cells.csv (round 5's summary columns) and regcomp_genes.parquet.
"""
import json, os, sys, time
import numpy as np, pandas as pd, pyarrow as pa, pyarrow.parquet as pq
import round4_ppi_estimator as R4
import round4_ppi_q2_masking as Q2
import round5_ppi_e3_twolevel as E3
import round5_ppi_twolevel as TL
import round10_final_runs_estimators as E
import round10_final_runs_f2_regimeB as F2

RCSCHEMA = pa.schema(list(F2.GSCHEMA) + [pa.field("regime", pa.string()), pa.field("budget", pa.float64()),
                                          pa.field("cost", pa.string()), pa.field("n_L", pa.int64()),
                                          pa.field("m_label", pa.string()), pa.field("m_median", pa.float64()),
                                          pa.field("interval", pa.string())])
B_FORMS = (("C_fix1", "fixed1"), ("C_ppi", "crossfit"), ("C_classical", "classical"))
KEYS = ["vtag", "arm", "part", "regime", "budget", "cost", "n_L", "m", "estimand", "interval", "n_draws", "estimator"]
CMP = ["n_genes", "emp_var_median", "est_var_over_emp_var_median", "coverage_median", "coverage_mean", "coverage_min",
       "lambda_median", "lambda_frac_zero", "m_median"]


def regimeA_fix1(T, Lmask, sel, seed):
    """Two-stage regime A with the coefficient fixed at 1 at both stages (module docstring)."""
    o = E._tl_fixed()(T, Lmask, sel, "C_fix1", seed, regime_b=False, xf=False)
    Lc = Lmask & T["valid"]; nL = int(Lc.sum()); Gv = int(T["valid"].sum())
    Fbar = T["fbar"][T["valid"]].mean(0)
    Lm = Lc[:, None]
    ebar = np.where(Lm, o["zhat"] - T["fbar"], 0.0)
    em = ebar.sum(0) / nL
    s2 = np.where(Lm, (ebar - em) ** 2, 0.0).sum(0) / (nL - 1.0)
    var = (1.0 - nL / Gv) * s2 / nL + np.where(Lm, o["V"], 0.0).sum(0) / (Gv * nL)
    return dict(theta=Fbar + em, var=var, df=float(nL - 1), lam_w=o["lam_w"], zhat=o["zhat"], V=o["V"])


def cell_tag(c):
    return f"regcomp|{c['regime']}|B{c['budget']}|{c['cost']}|nL{c['n_L']}|m{c['m']}"


def run_cell(data, T, vtag, est, c, R, label):
    """R draws of one regcomp cell for one estimand. Returns round 4's acc and arrays per (interval, arm)."""
    tag = cell_tag(c); acc = {}; arr = {}
    rb = c["regime"] == "B"
    for d in range(R):
        if rb:
            Lmask = T["valid"].copy()
        else:
            Ld = Q2.B1.draw_L(list(data["donors"]), c["n_L"], f"r5e3|{vtag}|{tag}|d{d}")
            Lmask = np.isin(data["donors"], Ld)
        m = c["mg"] if c["m"] == "prop" else c["m"]
        if est == "theta2" and T["kind"] == "theta2":
            if np.isscalar(m) and 0 < m < 4:
                continue
            if not np.isscalar(m):
                m = np.maximum(m, 4)
        sel = E3.units(data, T, Lmask, m, E3.rng_of(f"r5e3u|{vtag}|{tag}|d{d}|{est}"))
        seed = f"r5e3x|{vtag}|{tag}|d{d}|{est}"
        outs = []
        if rb:
            for nm, coef in B_FORMS:
                o = E.regime_b_formC(T, sel, seed, coef)
                outs.append((nm, "regB_t", o, o["var"]))
        else:
            o = regimeA_fix1(T, Lmask, sel, seed)
            outs.append(("C_fix1", "twostage_t|fpc", o, o["var"]))
            for nm in ("C_ppi", "C_classical"):
                o = TL.estimate(T, Lmask, sel, nm, seed, regime_b=False, xf=True)
                outs.append((nm, "textbook_t|fpc|lin", o, o["var_noxf"]))
                outs.append((nm, "textbook_t|fpc|lin|xf", o, o["var"]))
        for nm, iv, o, v in outs:
            df = np.full(o["theta"].shape, o["df"], dtype=float)
            lo, hi = R4.t_interval(o["theta"], v, df)
            lw = o["lam_w"][Lmask & T["valid"]]
            lmed = np.nanmedian(lw, axis=0) if lw.size else np.zeros(T["ng"])
            Q2._acc(acc, (label, "donor", "design", nm, iv), o["theta"], v, lo, hi, lmed, T["theta_full"])
            a = arr.setdefault(iv, {}).setdefault(nm, dict(th=[], v=[], df=[]))
            a["th"].append(o["theta"]); a["v"].append(v); a["df"].append(df)
    return acc, {iv: {nm: {k: np.array(x) for k, x in a.items()} for nm, a in d_.items()} for iv, d_ in arr.items()}


def select_cells(cells, cfg):
    out = []
    for c in cells:
        if cfg.get("regimes") and c["regime"] not in cfg["regimes"]:
            continue
        if cfg.get("budgets") and int(round(float(c["cost"].split("_B")[-1]) if c["cost"] != "unit" else c["budget"])) not in cfg["budgets"]:
            continue
        if cfg.get("costs") and c["regime"] == "B":
            ck = "unit" if c["cost"] == "unit" else float(c["cost"].split("_")[2])
            if ck not in [x if x == "unit" else float(x) for x in cfg["costs"]]:
                continue
        if cfg.get("n_L"):
            nl = c["n_L"] if c["regime"] == "A" else (int(c["cost"].split("_nL")[1].split("_")[0]) if c["cost"] != "unit" else None)
            if nl is not None and nl not in cfg["n_L"]:
                continue
        out.append(c)
    return out


def run_population(pop, cfg, R, cells_filter, sink, part_label="regcomp", log=print):
    t0 = time.time()
    data = F2.load(pop)
    arm = pop.get("arm", pop["encoder"])
    Tset = E3.build(data, pop["vtag"], arm)
    cells = select_cells(E3.part_cells("regcomp", data, Tset), cells_filter)
    info = dict(task=pop["task"], encoder=pop["encoder"], scale=pop["scale"], G=len(data["donors"]),
                n_units=int(len(data["didx"])), n_genes=len(data["genes"]), n_cells=len(cells),
                load_seconds=round(time.time() - t0, 1), cells=[])
    for est in pop["estimands"]:
        if est not in Tset:
            info["cells"].append(dict(estimand=est, skipped="not built")); continue
        T = Tset[est]
        est_out = "mu" if T["kind"] == "mean" else est
        keys = dict(task=pop["task"], encoder=pop["encoder"], scale=pop["scale"], estimand=est_out)
        if pop.get("cluster_values"):
            info.setdefault("cv_check", {})[est_out] = F2.check_cluster_values(T, data, pop["cluster_values"], keys, est_out)
        for c in cells:
            tc = time.time()
            acc, arr = run_cell(data, T, pop["vtag"], est, c, R, est_out if part_label == "regcomp" else est)
            cell = dict(vtag=pop["vtag"], arm=arm, task=pop["task"], encoder=pop["encoder"], scale=pop["scale"],
                        G=len(data["donors"]), part="regcomp", regime=c["regime"], budget=c["budget"], cost=c["cost"],
                        n_L=c["n_L"], m=c["m"])
            mmed = float(np.median(c["mg"])) if c["m"] == "prop" else float(c["m"])
            if c["m"] == "prop":
                cell["m_median"] = mmed
            E3.summarise(acc, cell, data["genes"], sink["rows"], [])
            for iv, a in arr.items():
                for g in F2.gene_rows(a, T["theta_full"], keys, data["genes"], int(T["valid"].sum()), int(round(mmed))):
                    g.update(regime=c["regime"], budget=float(c["budget"]), cost=c["cost"], n_L=int(c["n_L"]),
                             m_label=str(c["m"]), m_median=mmed, interval=iv)
                    sink["grows"].append(g)
            info["cells"].append(dict(estimand=est_out, tag=cell_tag(c), seconds=round(time.time() - tc, 1)))
            log(json.dumps(dict(pop=pop["task"] + "|" + pop["encoder"] + "|" + pop["scale"], est=est_out, cell=cell_tag(c),
                                R=R, s=round(time.time() - tc, 1))))
    info["seconds"] = round(time.time() - t0, 1)
    return info


def compare_rows(mine, ref, vtag, arm):
    """Round 5's summary rows of the same cells, estimators and intervals, joined on round 5's keys."""
    ref = ref[(ref.vtag == vtag) & (ref.arm == arm) & (ref.part == "regcomp")].copy()
    a = mine.copy()
    for d in (a, ref):
        d["budget"] = d["budget"].astype(float); d["m"] = d["m"].astype(str); d["n_L"] = d["n_L"].astype(int)
        d["n_draws"] = d["n_draws"].astype(int)
    a = a[a.estimator.isin(["C_ppi", "C_classical"])]
    mm = a.merge(ref, on=KEYS, how="left", suffixes=("", "_r5"), indicator=True)
    for c in CMP:
        if c in mm and c + "_r5" in mm:
            x, y = mm[c].astype(float), mm[c + "_r5"].astype(float)
            mm["d_" + c] = np.where(x.isna() & y.isna(), 0.0, (x - y).abs())
    return mm


def main_run(cfg, out):
    summ = dict(config=cfg, started=time.strftime("%Y-%m-%dT%H:%M:%S"), populations=[])
    sp = os.path.join(out, "regcomp_summary.json"); json.dump(summ, open(sp, "w"), indent=1)
    R = int(cfg.get("R", 2000))
    log = lambda s: print(s, flush=True)
    if cfg.get("anchor"):
        A = cfg["anchor"]; asink = dict(rows=[], grows=[])
        t0 = time.time()
        for pop in A["populations"]:
            summ.setdefault("anchor_populations", []).append(run_population(pop, A, int(A["draws"]), A, asink, log=log))
        mm = compare_rows(pd.DataFrame(asink["rows"]), pd.read_csv(A["ref_csv"]), A["populations"][0]["vtag"],
                          A["populations"][0].get("arm", A["populations"][0]["encoder"]))
        mm.drop(columns=["_merge"]).to_csv(os.path.join(out, "regcomp_anchor_r5.csv"), index=False)
        dcols = [c for c in mm.columns if c.startswith("d_")]
        summ["anchor"] = dict(rows=len(mm), rows_matched=int((mm._merge == "both").sum()), seconds=round(time.time() - t0, 1),
                              **{f"max_{c}": float(mm[c].max()) for c in dcols})
        named = []
        for nm in A.get("named", []):
            sel = mm
            for k, v in nm.items():
                sel = sel[sel[k].astype(str) == str(v)]
            if len(sel):
                r = sel.iloc[0]
                named.append(dict(nm, **{c: float(r[c]) for c in ("emp_var_median", "coverage_median", "est_var_over_emp_var_median")},
                                  **{c + "_r5": float(r[c + "_r5"]) for c in ("emp_var_median", "coverage_median", "est_var_over_emp_var_median")}))
        summ["anchor"]["named"] = named
        pd.DataFrame(asink["rows"]).to_csv(os.path.join(out, "regcomp_anchor_cells.csv"), index=False)
        json.dump(summ, open(sp, "w"), indent=1, default=str); log(json.dumps(summ["anchor"], default=str))
    sink = dict(rows=[], grows=[])
    for pop in cfg.get("populations", []):
        summ["populations"].append(run_population(pop, cfg, int(pop.get("R", R)), pop.get("cells", cfg), sink, log=log))
        json.dump(summ, open(sp, "w"), indent=1, default=str)
    if cfg.get("fix1_census_check"):
        summ["fix1_census_check"] = census_check(cfg["fix1_census_check"])
    summ["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    json.dump(summ, open(sp, "w"), indent=1, default=str)
    pd.DataFrame(sink["rows"]).to_csv(os.path.join(out, "regcomp_cells.csv"), index=False)
    G = pd.DataFrame(sink["grows"], columns=RCSCHEMA.names)
    pq.write_table(pa.Table.from_pandas(G, schema=RCSCHEMA, preserve_index=False), os.path.join(out, "regcomp_genes.parquet"))
    print(json.dumps({k: v for k, v in summ.items() if k != "config"}, indent=1, default=str)[:6000])


def census_check(pops):
    """Identity check of the two-stage fixed estimator: with every unit of the labelled donors observed, ebar_g must
    equal zbar_g - fbar_g, V_g must be 0, and theta_A = Fbar_U + mean_L(zbar - fbar); for the mean, ebar_g must also
    equal the donor mean of y - f computed directly from the spots. Returns the largest absolute differences."""
    out = []
    for pop in pops:
        data = F2.load(pop); Tset = E3.build(data, pop["vtag"], pop.get("arm", pop["encoder"]))
        for est in pop["estimands"]:
            T = Tset[est]
            rng = np.random.default_rng(12345)
            Lmask = np.zeros(T["G"], bool); Lmask[rng.choice(np.flatnonzero(T["valid"]), 8, replace=False)] = True
            sel = E3.units(data, T, Lmask, 0, rng)
            o = regimeA_fix1(T, Lmask, sel, "census")
            Lc = Lmask & T["valid"]
            direct = T["fbar"][T["valid"]].mean(0) + (T["zbar"] - T["fbar"])[Lc].mean(0)
            r = dict(task=pop["task"], encoder=pop["encoder"], scale=pop["scale"], estimand="mu" if T["kind"] == "mean" else est,
                     max_abs_theta=float(np.abs(o["theta"] - direct).max()),
                     max_abs_ebar=float(np.abs((o["zhat"] - T["fbar"])[Lc] - (T["zbar"] - T["fbar"])[Lc]).max()),
                     max_abs_V=float(np.abs(o["V"][Lc]).max()))
            if T["kind"] == "mean":
                e = data["Y"] - data["P"]
                dm = np.vstack([e[data["by_donor"][g]].mean(0) for g in range(T["G"])])
                r["max_abs_ebar_vs_spots"] = float(np.abs((o["zhat"] - T["fbar"])[Lc] - dm[Lc]).max())
            out.append(r)
    return out


def main_compare(cfg, out):
    """Round 5's script run unchanged: its regcomp rows against round 5's committed rows (raw file and merged table),
    and its gene rows against round 5's committed gene rows, every numeric column."""
    res = dict(config=cfg, started=time.strftime("%Y-%m-%dT%H:%M:%S"))
    new, ref = pd.read_csv(cfg["new_csv"]), pd.read_csv(cfg["ref_csv"])
    k = [c for c in KEYS if c in new.columns]
    num = [c for c in new.columns if c not in k and pd.api.types.is_numeric_dtype(new[c])]
    for nm, R_ in (("raw", ref), ("merged", pd.read_csv(cfg["ref_merged"]))):
        R_ = R_[(R_.vtag == cfg["vtag"]) & (R_.arm == cfg["arm"]) & (R_.part == "regcomp")]
        a, b = new.copy(), R_.copy()
        for d in (a, b):
            d["budget"] = d["budget"].astype(float); d["m"] = d["m"].astype(str)
        mm = a.merge(b, on=k, how="outer", suffixes=("", "_r5"), indicator=True)
        r = dict(rows_new=len(a), rows_ref=len(b), rows_matched=int((mm._merge == "both").sum()))
        for c in num:
            if c + "_r5" in mm:
                x, y = mm[c].astype(float), mm[c + "_r5"].astype(float)
                d = np.where(x.isna() & y.isna(), 0.0, (x - y).abs())
                r[f"max_abs_{c}"] = float(np.nanmax(np.where(np.isnan(d), np.inf, d)))
        r["max_abs_all"] = max(v for kk, v in r.items() if kk.startswith("max_abs_"))
        res[nm] = r
        if nm == "merged":
            named = []
            for q in cfg.get("named", []):
                s = mm
                for kk, v in q.items():
                    s = s[s[kk].astype(str) == str(v)]
                if len(s):
                    x = s.iloc[0]
                    named.append(dict(q, **{c: float(x[c]) for c in ("emp_var_median", "est_var_over_emp_var_median", "coverage_median")},
                                      **{c + "_r5": float(x[c + "_r5"]) for c in ("emp_var_median", "est_var_over_emp_var_median", "coverage_median")}))
            res["named"] = named
            mm.drop(columns=["_merge"]).to_csv(os.path.join(out, "regcomp_r5_unchanged_vs_merged.csv"), index=False)
    if cfg.get("new_genes") and cfg.get("ref_genes"):
        gn, gr = pd.read_csv(cfg["new_genes"]), pd.read_csv(cfg["ref_genes"])
        kg = [c for c in gn.columns if not pd.api.types.is_float_dtype(gn[c])]
        for d in (gn, gr):
            d["budget"] = d["budget"].astype(float); d["m"] = d["m"].astype(str)
        kg = [c for c in kg if c in gr.columns] + ["budget"]
        kg = list(dict.fromkeys(kg))
        mm = gn.merge(gr, on=kg, how="outer", suffixes=("", "_r5"), indicator=True)
        r = dict(rows_new=len(gn), rows_ref=len(gr), rows_matched=int((mm._merge == "both").sum()), keys=kg)
        for c in gn.columns:
            if c not in kg and c + "_r5" in mm and pd.api.types.is_numeric_dtype(gn[c]):
                x, y = mm[c].astype(float), mm[c + "_r5"].astype(float)
                d = np.where(x.isna() & y.isna(), 0.0, (x - y).abs())
                r[f"max_abs_{c}"] = float(np.nanmax(np.where(np.isnan(d), np.inf, d)))
        res["genes"] = r
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    json.dump(res, open(os.path.join(out, "regcomp_r5_compare.json"), "w"), indent=1, default=str)
    print(json.dumps({k: v for k, v in res.items() if k != "config"}, indent=1, default=str))


def main():
    mode, cfgp, out = sys.argv[1:4]
    cfg = json.load(open(cfgp)); os.makedirs(out, exist_ok=True)
    np.seterr(all="ignore")
    if mode == "run":
        main_run(cfg, out)
    elif mode == "compare_r5":
        main_compare(cfg, out)
    else:
        raise SystemExit(f"unknown mode {mode}")


if __name__ == "__main__":
    main()
