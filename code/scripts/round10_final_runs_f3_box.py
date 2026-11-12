"""Round 10, track final-runs, F3.3 (ii): question V, the box class with v0 as an argument (plan 5d.3 (ii)).

Round 9's round9_fewcluster_box.py derives v0 from the population (box_worst, line 39: v0 = max_h v_h at m) and scans
m in {2, ..., 100}. This module imports round 9's helpers unchanged (k_min, box_worst, regime_A, the cached log_R and
round9_fewcluster_strat_frontier.log_pi, thm1_frontier) and adds:

  * box_worst_v0(Ns, sds, m, lam0, v0): the same worst all-constant probability with s = ceil(1/v0) strata degenerate
    at once for a given v0; v0 = None is round 9's rule (the population's own v0 at m). Clusters with m >= N_h are
    censused and drop out, as in round 9;
  * the m grid extended by 150, 200, 300, 500, 750, 1000, 1500 and 2000;
  * per gene, for the fixed coefficient (lambda = 1) and the classical estimator (lambda = 0): Lambda0, kappa_A,
    n_min_A, the bounded requirement (the population's own v0) and the unbounded requirement (v0 = 1), each with the
    regime B shares at that m, v_h = V_h / sum_h V_h with V_h = sd_h^2 (1 - m/N_h)/m, their largest value and
    G*_B = 1 / sum_h v_h^2;
  * the LUNG_XENIUM 42-gene flag of round 9 (zlib.crc32(gene) % 7 == 0), on every row.

Modes
  anchor <config.json> <out>  round 9's anchors: (a) the bounded column on round 9's own HEST population (every row of
                              the three uni_v2 parquets, as round9_fewcluster_box.py's hest mode reads them) on round
                              9's grid, every row of i32_hest_box_genes.csv and the summary file; (b) the ACS row of
                              i32_acs_box.csv from i32_acs_states.csv; (c) the unbounded function on round 9's
                              stylised populations (equal N_h) against i32_required_m_B.csv, every (N, Lambda0, v0)
                              row, the requirement scanned over the integers from 2; (d) box_worst_v0(v0=None) against
                              round 9's box_worst on every (gene, m) of (a).
  run <config.json> <out>     production: per population (F2's population dict, read through F2.load, so the units
                              are those regime B samples), the box rows for mu (unless the config sets box false); then, when the config names an m grid,
                              the regime B coverage cells for mu (C_fix1) through round10_final_runs_f3_regimeB.
Writes box_summary.json first, then the tables.
"""
import json, math, os, sys, time, zlib
import numpy as np, pandas as pd
import round9_fewcluster_box as B9
from round9_fewcluster_box import k_min, log_R, regime_A, ALPHA
from round9_fewcluster_strat_frontier import log_pi, thm1_frontier

M_GRID_R9 = list(B9.M_GRID)
M_GRID_EXT = M_GRID_R9 + [150, 200, 300, 500, 750, 1000, 1500, 2000]


def r9g42(gene):
    return zlib.crc32(str(gene).encode()) % 7 == 0


def shares(Ns, sds, m):
    Ns = np.asarray(Ns); sds = np.asarray(sds, float)
    mm = np.minimum(m, Ns)
    Vh = sds ** 2 * (1 - mm / Ns) / mm
    tot = Vh.sum()
    v = Vh / tot if tot > 0 else np.full(len(Vh), np.nan)
    return v


def box_worst_v0(Ns, sds, m, lam0, v0=None, alpha=ALPHA):
    """round9_fewcluster_box.box_worst with v0 as an argument. Returns (low, up, v0_used, s, v0_population)."""
    Ns = np.asarray(Ns); sds = np.asarray(sds, float)
    mm = np.minimum(m, Ns)
    Vh = sds ** 2 * (1 - mm / Ns) / mm
    v = Vh / Vh.sum(); v0_pop = float(v.max())
    v0u = v0_pop if v0 is None else float(v0)
    s = math.ceil(1 / v0u - 1e-12)
    prob = mm < Ns
    lo, up = [], []
    for N, mh, p in zip(Ns, mm, prob):
        if not p:
            continue
        k = min(k_min(int(N), lam0), int(N) // 2)
        l2 = float(log_pi(int(N), int(mh), [k])[0])
        lr = log_R(int(N), int(mh)) if lam0 ** 2 >= (N - 1) / N else -np.inf
        lo.append(l2); up.append(max(l2, lr))
    lo = np.sort(lo)[::-1]; up = np.sort(up)[::-1]
    if s > len(lo):
        return 0.0, 0.0, v0u, s, v0_pop
    return math.exp(lo[:s].sum()), math.exp(up[:s].sum()), v0u, s, v0_pop


def requirement(Ns, sds, lam0, grid, v0=None):
    """First m of the grid whose upper bound is <= alpha (m_min_B) and first whose two-point bound is (twopoint)."""
    mB = mB2 = None; wB = None
    for m in grid:
        lo, up, _, _, _ = box_worst_v0(Ns, sds, m, lam0, v0)
        if mB is None and up <= ALPHA:
            mB, wB = m, up
        if mB2 is None and lo <= ALPHA:
            mB2 = m
        if mB is not None and mB2 is not None:
            break
    return mB, mB2, wB


def analyse_v0(groups, label, grid=M_GRID_EXT):
    """One row per (gene, lambda): round 9's analyse columns on the extended grid, both columns, shares at each."""
    Ns = np.array([len(e) for e in groups]); sds = np.array([e.std(ddof=1) for e in groups])
    lam_h = np.array([np.abs(e - e.mean()).max() / e.std(ddof=1) for e in groups])
    lam0 = float(lam_h.max()); G = len(groups)
    kA, nA = regime_A(np.array([e.mean() for e in groups]), G)
    row = {**label, "G": G, "N_median": float(np.median(Ns)), "N_min": int(Ns.min()), "N_max": int(Ns.max()),
           "Lambda0": lam0, "Lambda_h_median": float(np.median(lam_h)), "kappa_A": kA, "n_min_A": nA,
           "frontier_A_mid": thm1_frontier(G, 8 if G > 15 else 6)}
    for m in (5, 10, 20):
        lo, up, v0, s, _ = box_worst_v0(Ns, sds, m, lam0)
        row[f"worst_m{m}"] = up; row[f"v0_m{m}"] = v0; row[f"s_m{m}"] = s
    for col, v0 in (("bounded", None), ("unbounded", 1.0)):
        mB, mB2, wB = requirement(Ns, sds, lam0, grid, v0)
        row[f"m_min_B_{col}"] = mB; row[f"m_min_B_twopoint_{col}"] = mB2; row[f"worst_at_m_{col}"] = wB
        if mB is not None:
            v = shares(Ns, sds, mB)
            row[f"v_max_at_m_{col}"] = float(np.nanmax(v)); row[f"Gstar_B_at_m_{col}"] = float(1 / np.nansum(v ** 2))
            row[f"n_censused_at_m_{col}"] = int((np.minimum(mB, Ns) >= Ns).sum())
        else:
            row[f"v_max_at_m_{col}"] = row[f"Gstar_B_at_m_{col}"] = np.nan; row[f"n_censused_at_m_{col}"] = None
    row["m_min_B"] = row["m_min_B_bounded"]; row["m_min_B_twopoint"] = row["m_min_B_twopoint_bounded"]
    return row


def gene_groups(Y, P, by_donor, j, lam):
    e = Y[:, j] - lam * P[:, j]
    return [e[i] for i in by_donor]


def box_population(genes, Y, P, by_donor, label, grid=M_GRID_EXT, lams=(0.0, 1.0)):
    rows = []
    for j, g in enumerate(genes):
        for lam in lams:
            groups = gene_groups(Y, P, by_donor, j, lam)
            lab = {**label, "gene": g, "lambda": lam, "r9g42": r9g42(g)}
            if min(np.std(x) for x in groups) == 0:
                rows.append({**lab, "note": "constant donor"}); continue
            rows.append(analyse_v0(groups, lab, grid))
    return rows


# ------------------------------------------------------------------ anchors
def stylised(N, lam0, v0, mmax=5000):
    """Round 9's stylised population: s = ceil(1/v0) equal strata of size N degenerate at once; requirement scanned
    over the integers from 2 (box_worst_v0 with v0 given; the strata's sd does not enter at a given v0)."""
    s = math.ceil(1 / v0 - 1e-12)
    Ns = np.full(max(s, 1), N); sds = np.ones(len(Ns))
    for m in range(2, min(mmax, N)):
        _, up, _, _, _ = box_worst_v0(Ns, sds, m, lam0, v0)
        if up <= ALPHA:
            return m, s
    return None, s


def main_anchor(cfg, out):
    res = dict(config=cfg, started=time.strftime("%Y-%m-%dT%H:%M:%S"))
    sp = os.path.join(out, "box_summary.json"); json.dump(res, open(sp, "w"), indent=1)
    t0 = time.time()
    # (c) stylised table, unbounded and every v0
    st = pd.read_csv(cfg["required_m_csv"]); rows = []
    for r in st.itertuples():
        m, s = stylised(int(r.N), float(r.Lambda0), float(r.v0))
        rows.append(dict(N=int(r.N), Lambda0=r.Lambda0, v0=r.v0, strata_needed_r9=int(r.strata_needed), strata_needed=s,
                         m_min_B_r9=int(r.m_min_B), m_min_B=m, equal=(m == int(r.m_min_B)) and (s == int(r.strata_needed))))
    S = pd.DataFrame(rows); S.to_csv(os.path.join(out, "box_anchor_stylised.csv"), index=False)
    res["stylised"] = dict(rows=len(S), rows_equal=int(S.equal.sum()), seconds=round(time.time() - t0, 1),
                           v0_1_N2000=S[(S.v0 == 1.0) & (S.N == 2000)].m_min_B.tolist(),
                           v0_1_N20000=S[(S.v0 == 1.0) & (S.N == 20000)].m_min_B.tolist())
    json.dump(res, open(sp, "w"), indent=1, default=str); print(json.dumps(res["stylised"]), flush=True)
    # (b) ACS from round 9's aggregates
    t0 = time.time()
    s = pd.read_csv(cfg["acs_states_csv"]); arows = []
    for lam, d in s.groupby("lambda"):
        Ns = d.N.to_numpy(); sds = d.sd_e.to_numpy(); lam_h = np.sqrt(d.kappa_h * (d.N - 1)).to_numpy()
        lam0 = float(lam_h.max())
        kA, nA = regime_A(d.mean_e.to_numpy(), len(d))
        row = dict(task="ACS_STATES", **{"lambda": lam}, G=len(d), Lambda0=lam0, kappa_A=kA, n_min_A=nA)
        for col, v0 in (("bounded_r9grid", None), ("bounded", None), ("unbounded", 1.0)):
            grid = M_GRID_R9 if col.endswith("r9grid") else M_GRID_EXT
            mB, mB2, wB = requirement(Ns, sds, lam0, grid, v0)
            row[f"m_min_B_{col}"] = mB; row[f"m_min_B_twopoint_{col}"] = mB2
        lo, up, v0, s_, _ = box_worst_v0(Ns, sds, 5, lam0); row.update(v0_m5=v0, s_m5=s_, worst_m5=up)
        arows.append(row)
    A = pd.DataFrame(arows); ref = pd.read_csv(cfg["acs_box_csv"])
    A = A.merge(ref[["lambda", "m_min_B", "m_min_B_twopoint", "v0_m5", "s_m5", "worst_m5", "kappa_A", "n_min_A"]],
                on="lambda", suffixes=("", "_r9"))
    A.to_csv(os.path.join(out, "box_anchor_acs.csv"), index=False)
    res["acs"] = A.to_dict("records"); res["acs_seconds"] = round(time.time() - t0, 1)
    json.dump(res, open(sp, "w"), indent=1, default=str); print(json.dumps(res["acs"], default=str), flush=True)
    # (a) and (d) HEST on round 9's population
    t0 = time.time(); hrows, dmax = [], 0.0
    for task, path in cfg["hest_parquets"].items():
        df = pd.read_parquet(path)
        genes = [c[3:] for c in df.columns if c.startswith("y__")]
        don = df.donor_id.astype(str).to_numpy(); ud = np.unique(don)
        idx = [np.where(don == u)[0] for u in ud]
        Y = df[["y__" + g for g in genes]].to_numpy(float); P = df[["f__" + g for g in genes]].to_numpy(float)
        rr = box_population(genes, Y, P, idx, {"task": task}, grid=M_GRID_R9)
        hrows += rr
        # (d) v0=None against round 9's own box_worst, every gene and m, both lambdas
        for j in range(len(genes)):
            for lam in (0.0, 1.0):
                groups = gene_groups(Y, P, idx, j, lam)
                if min(np.std(x) for x in groups) == 0:
                    continue
                Ns = np.array([len(e) for e in groups]); sds = np.array([e.std(ddof=1) for e in groups])
                l0 = float(max(np.abs(e - e.mean()).max() / e.std(ddof=1) for e in groups))
                for m in M_GRID_R9:
                    a = B9.box_worst(Ns, sds, m, l0); b = box_worst_v0(Ns, sds, m, l0)
                    dmax = max(dmax, abs(a[0] - b[0]), abs(a[1] - b[1]), abs(a[2] - b[2]), abs(a[3] - b[3]))
        print(task, len(genes), round(time.time() - t0, 1), flush=True)
    H = pd.DataFrame(hrows)
    H.to_csv(os.path.join(out, "box_anchor_hest_genes.csv"), index=False)
    ref = pd.read_csv(cfg["hest_box_genes_csv"])
    cols = [c for c in ref.columns if c not in ("task", "gene", "lambda")]
    mm = H.merge(ref, on=["task", "gene", "lambda"], how="outer", suffixes=("", "_r9"), indicator=True)
    diffs = {}
    for c in cols:
        if c + "_r9" not in mm or c not in mm:
            continue
        if pd.api.types.is_numeric_dtype(ref[c]):
            x, y = pd.to_numeric(mm[c], errors="coerce"), pd.to_numeric(mm[c + "_r9"], errors="coerce")
            d = np.where(x.isna() & y.isna(), 0.0, (x - y).abs()); d = np.where(np.isnan(d), np.inf, d)
            diffs[c] = float(d.max())
        else:
            diffs[c] = int((mm[c].astype(str) != mm[c + "_r9"].astype(str)).sum())
    mm.drop(columns=["_merge"]).to_csv(os.path.join(out, "box_anchor_hest_vs_r9.csv"), index=False)
    named = mm[(mm.task == "CCRCC") & (mm.gene == "AKAP8") & (mm["lambda"] == 1.0)].iloc[0]
    res["hest"] = dict(rows=len(H), rows_ref=len(ref), rows_matched=int((mm._merge == "both").sum()), max_abs=diffs,
                       named=dict(m_min_B=named.m_min_B, m_min_B_r9=named.m_min_B_r9, worst_m10=named.worst_m10,
                                  worst_m10_r9=named.worst_m10_r9),
                       box_worst_v0_none_vs_r9_max_abs=dmax, seconds=round(time.time() - t0, 1))
    # summary file of round 9
    sm = H.groupby(["task", "lambda"]).agg(n_genes=("gene", "size"), Lambda0_median=("Lambda0", "median"),
                                          m_min_B_median=("m_min_B", "median"),
                                          frac_B_le10=("m_min_B", lambda x: float((x <= 10).mean())),
                                          frac_B_none=("m_min_B", lambda x: float(x.isna().mean())),
                                          n_min_A_median=("n_min_A", "median")).reset_index()
    rs = pd.read_csv(cfg["hest_box_summary_csv"])
    sm2 = sm.merge(rs, on=["task", "lambda"], suffixes=("", "_r9"))
    for c in ("n_genes", "Lambda0_median", "m_min_B_median", "frac_B_le10", "frac_B_none", "n_min_A_median"):
        sm2["d_" + c] = (sm2[c] - sm2[c + "_r9"]).abs()
    sm2.to_csv(os.path.join(out, "box_anchor_hest_summary.csv"), index=False)
    res["hest_summary_max_d"] = {c: float(sm2[c].max()) for c in sm2.columns if c.startswith("d_")}
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    json.dump(res, open(sp, "w"), indent=1, default=str)
    print(json.dumps({k: v for k, v in res.items() if k not in ("config", "acs")}, indent=1, default=str))


def main_run(cfg, out):
    import round10_final_runs_f2_regimeB as F2
    import round10_final_runs_f3_regimeB as RB
    import pyarrow as pa, pyarrow.parquet as pq
    res = dict(config=cfg, started=time.strftime("%Y-%m-%dT%H:%M:%S"), populations=[])
    sp = os.path.join(out, "box_summary.json"); json.dump(res, open(sp, "w"), indent=1)
    rows = []; sink = dict(rows=[], grows=[], widths=[], wr=[])
    for pop in cfg["populations"]:
        t0 = time.time()
        data = F2.load(pop)
        lab = dict(task=pop["task"], encoder=pop["encoder"], scale=pop["scale"], population="regimeB_units")
        if cfg.get("box", True):
            rows += box_population(data["genes"], data["Y"], data["P"], data["by_donor"], lab)
        info = dict(task=pop["task"], encoder=pop["encoder"], scale=pop["scale"], G=len(data["donors"]),
                    n_units=int(len(data["didx"])), n_genes=len(data["genes"]), box_seconds=round(time.time() - t0, 1))
        res["populations"].append(info)
        json.dump(res, open(sp, "w"), indent=1, default=str)
        print(json.dumps(info), flush=True)
        if cfg.get("m_grid"):
            rcfg = dict(R=cfg.get("R", 2000), m_grid=cfg["m_grid"], forms=cfg.get("forms", ["C_fix1"]))
            pinfo, _ = RB.run_population(pop, rcfg, sink, log=lambda s: print(s, flush=True), data=data)
            pinfo.pop("genes"); info["coverage"] = pinfo
            json.dump(res, open(sp, "w"), indent=1, default=str)
    Bx = pd.DataFrame(rows)
    Bx.to_csv(os.path.join(out, "box_genes.csv"), index=False)
    res["box_rows"] = len(Bx)
    if sink["grows"]:
        G = pd.DataFrame(sink["grows"], columns=F2.GSCHEMA.names)
        pd.DataFrame(sink["rows"]).to_csv(os.path.join(out, "box_coverage_cells.csv"), index=False)
        pq.write_table(pa.Table.from_pandas(G, schema=F2.GSCHEMA, preserve_index=False), os.path.join(out, "box_coverage_genes.parquet"))
        res["coverage_rows"] = len(G)
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    json.dump(res, open(sp, "w"), indent=1, default=str)
    print(json.dumps({k: v for k, v in res.items() if k != "config"}, indent=1, default=str)[:6000])


def main():
    mode, cfgp, out = sys.argv[1:4]
    cfg = json.load(open(cfgp)); os.makedirs(out, exist_ok=True)
    np.seterr(all="ignore")
    if mode == "anchor":
        main_anchor(cfg, out)
    elif mode == "run":
        main_run(cfg, out)
    else:
        raise SystemExit(f"unknown mode {mode}")


if __name__ == "__main__":
    main()
