"""Round 10, track final-runs, F3.3 (iv): aggregate the balance units and score P10.1 part 2 (plan 5d.3 (iv), 4a).

usage: round10_final_runs_f3_balance_aggregate.py <designs_dir> <out_dir> <s5_matched_csv>
Reads <designs_dir>/bal_<unit>/balance_cells.csv for every production unit whose PROVENANCE.txt reads COMPLETED
(bal_smoke and the anchors are excluded) and writes, summaries first:
  f3_balance_units.csv     unit, status, Slurm id, rows
  f3_balance_matched.csv   per domain, scale, gene scope, n_L, p_a and design: cells where D2 own is supported at that
                           p_a and every matched design is present (round 7 S5's table rule), with the medians over
                           cells of coverage_all, coverage and the width ratios wr_D0cl (to D0 classical, round 7's
                           column) and wr_D0same (to D0 under the same estimator)
  f3_balance_limits.csv    the same for the two-variable limit arms (HEST only)
  f3_p101_part2.csv        the P10.1 part 2 score on round 7's 18 tissue cells at n_L 8
  f3_balance_cells.csv     every cell row of every unit
Designs: D0_classical, D0_fix1 (srs_t); D2_rej_t, D2_rej_t_fix1 (balance own, rej_t); cube_S4b, cube_S4b_fix1
(Hajek, simulated pi_gh, t_{n-rank}); cube_S4b_HT, cube_S4b_HT_fix1 (Horvitz-Thompson). Round 7's other six designs
are not rerun in F3, so P10.1 part 2 is scored on the three designs both rounds share.
"""
import glob, json, os, sys
import numpy as np, pandas as pd


def unit_status(d):
    p = os.path.join(d, "PROVENANCE.txt")
    if not os.path.exists(p):
        return None, None
    kv = dict(l.split(": ", 1) for l in open(p).read().splitlines() if ": " in l and not l.startswith(" "))
    return kv.get("status"), kv.get("slurm_job_id")

DOMAIN = {"CCRCC": "tissue", "CCRCC_merged": "tissue", "INDIANA_KIDNEY": "tissue", "LUNG_XENIUM": "tissue", "ACS_STATES": "census"}
CELL = ["task", "encoder", "scale", "estimand", "gene_scope", "G", "n_L"]
DESIGNS = {"D0_classical": ("D0", "none", "classical", "srs_t"), "D0_fix1": ("D0", "none", "fix1", "srs_t"),
           "D2_rej_t": ("D2", "own", "classical", "rej_t"), "D2_rej_t_fix1": ("D2", "own", "fix1", "rej_t"),
           "cube_S4b": ("cube", "pi,1,own", "classical", "H|sim|res"), "cube_S4b_fix1": ("cube", "pi,1,own", "fix1", "H|sim|res"),
           "cube_S4b_HT": ("cube", "pi,1,own", "classical", "HT|sim|res"), "cube_S4b_HT_fix1": ("cube", "pi,1,own", "fix1", "HT|sim|res")}
LIMITS = {"D2lim_pcE2_rej_t": ("D2lim", "pcE2", "classical", "rej_t"), "D2lim_pcE2_rej_t_fix1": ("D2lim", "pcE2", "fix1", "rej_t"),
          "D2lim_own_pcE1_rej_t": ("D2lim", "own_pcE1", "classical", "rej_t"),
          "D2lim_own_pcE1_rej_t_fix1": ("D2lim", "own_pcE1", "fix1", "rej_t")}
R7_SHARED = ("D0_classical", "D2_rej_t", "cube_S4b")
P101_CELLS = dict(task=("CCRCC", "CCRCC_merged", "INDIANA_KIDNEY"), encoder=("uni_v2", "hoptimus0", "resnet50"),
                  estimand=("theta2", "theta3"), scale="log1p", gene_scope="all", n_L=8)


def label(c, table):
    out = []
    for nm, (d, b, e, v) in table.items():
        m = (c.design == d) & (c.balance == b) & (c.estimator == e) & (c.variance == v)
        out.append(c[m].assign(dname=nm))
    return pd.concat(out, ignore_index=True)


def matched(c, table, pa):
    L = label(c, table)
    srs = L[L.dname.isin(["D0_classical", "D0_fix1"])]
    d2 = L[~L.dname.isin(["D0_classical", "D0_fix1"])]
    d2 = d2[d2.p_a.isna() | np.isclose(d2.p_a.fillna(-1), pa)]
    x = pd.concat([srs, d2], ignore_index=True)
    sup = L[(L.dname == "D2_rej_t") & np.isclose(L.p_a.fillna(-1), pa)][CELL].drop_duplicates() if "D2_rej_t" in table else \
        L[np.isclose(L.p_a.fillna(-1), pa)][CELL].drop_duplicates()
    x = x.merge(sup, on=CELL)
    full = x.groupby(CELL).dname.nunique()
    need = len(set(table) | {"D0_classical", "D0_fix1"})
    keep = full[full == need].index
    x = x.set_index(CELL).loc[keep].reset_index() if len(keep) else x.iloc[0:0]
    return x.assign(p_a_cell=pa)


def summarise(x):
    x = x.assign(domain=x.task.map(DOMAIN).fillna("corpus"))
    return x.groupby(["domain", "scale", "gene_scope", "n_L", "p_a_cell", "dname"]).agg(
        n_cells=("task", "size"), coverage_all=("coverage_all_median", "median"),
        coverage_all_min=("coverage_all_median", "min"), coverage=("coverage_median", "median"),
        wr_D0cl=("wr_D0cl", "median"), wr_D0same=("wr_D0same", "median")).reset_index().rename(columns={"p_a_cell": "p_a"})


def order_score(ref, new, designs):
    """strict: identical rank order; resolved: no pair whose reference values differ by >= 0.01 swaps."""
    r = {d: float(ref[d]) for d in designs}; n = {d: float(new[d]) for d in designs}
    strict = sorted(designs, key=r.get) == sorted(designs, key=n.get)
    swaps = []
    for i, a in enumerate(designs):
        for b in designs[i + 1:]:
            if abs(r[a] - r[b]) >= 0.01 and np.sign(r[a] - r[b]) != np.sign(n[a] - n[b]):
                swaps.append(f"{a}/{b}")
    tied = [f"{a}/{b}" for i, a in enumerate(designs) for b in designs[i + 1:] if abs(r[a] - r[b]) < 0.01]
    return strict, swaps, tied


def main(bd, out, s5):
    os.makedirs(out, exist_ok=True)
    units, parts = [], []
    for d in sorted(glob.glob(os.path.join(bd, "bal_*"))):
        u = os.path.basename(d)
        if u in ("bal_smoke", "bal_aggregate") or u.startswith("bal_anchor"):
            continue
        st, sid = unit_status(d)
        f = os.path.join(d, "balance_cells.csv")
        n = 0
        if st == "COMPLETED" and os.path.exists(f):
            x = pd.read_csv(f); n = len(x); parts.append(x.assign(unit=u))
        units.append(dict(unit=u, status=st, slurm_job_id=sid, rows=n))
    pd.DataFrame(units).to_csv(os.path.join(out, "f3_balance_units.csv"), index=False)
    c = pd.concat(parts, ignore_index=True)
    rows, lim = [], []
    for pa in (0.1, 0.01):
        rows.append(summarise(matched(c, DESIGNS, pa)))
        lim.append(summarise(matched(c, LIMITS, pa)))
    M = pd.concat(rows, ignore_index=True); M.to_csv(os.path.join(out, "f3_balance_matched.csv"), index=False)
    pd.concat(lim, ignore_index=True).to_csv(os.path.join(out, "f3_balance_limits.csv"), index=False)
    # P10.1 part 2 on round 7's 18 tissue cells at n_L 8
    ref = pd.read_csv(s5); ref = ref[(ref.domain == "tissue") & (ref.n_L == 8)]
    sc = []
    for pa in (0.1, 0.01):
        x = matched(c, DESIGNS, pa)
        q = P101_CELLS
        x = x[x.task.isin(q["task"]) & x.encoder.isin(q["encoder"]) & x.estimand.isin(q["estimand"]) &
              (x.scale == q["scale"]) & (x.gene_scope == q["gene_scope"]) & (x.n_L == q["n_L"])]
        new = x.groupby("dname").wr_D0cl.median(); ncell = x.groupby("dname").task.size()
        rr = ref[np.isclose(ref.p_a, pa)].set_index("design")
        for fam, names in (("classical", R7_SHARED), ("fix1", ("D0_fix1", "D2_rej_t_fix1", "cube_S4b_fix1"))):
            if not all(nm in new.index for nm in names):
                sc.append(dict(p_a=pa, family=fam, verdict="not tested", note="designs missing")); continue
            nn = {r7: new[nm] for r7, nm in zip(R7_SHARED, names)}
            strict, swaps, tied = order_score(rr["wr_D0cl"], nn, list(R7_SHARED))
            sc.append(dict(p_a=pa, family=fam, n_cells=int(min(ncell[nm] for nm in names)),
                           **{f"r7_{d}": float(rr.loc[d, "wr_D0cl"]) for d in R7_SHARED},
                           **{f"r10_{d}": float(nn[d]) for d in R7_SHARED},
                           strict_same_order=bool(strict), resolved_swaps=";".join(swaps), tied_in_reference=";".join(tied),
                           verdict="held" if not swaps else "refuted"))
    pd.DataFrame(sc).to_csv(os.path.join(out, "f3_p101_part2.csv"), index=False)
    c.to_csv(os.path.join(out, "f3_balance_cells.csv"), index=False)
    print(json.dumps(dict(units=len(units), completed=sum(u["status"] == "COMPLETED" for u in units), cell_rows=len(c),
                          matched_rows=len(M)), indent=1))
    print(pd.DataFrame(sc).to_string())


if __name__ == "__main__":
    main(*sys.argv[1:4])
