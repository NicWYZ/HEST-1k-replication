"""Round 10, track final-runs, F4 (plan 5e.2 and 5e.3): two readings of committed F3 outputs. Nothing here is estimated anew.

Modes
  s0006 <institution_config.json> <out>   for every kidney__Visium cell of F3's institution config (F1's center-design
        prediction files) and both scales: per center unit (column `fold`), the spots, donors, the median over genes of
        the median |y - f| over the unit's spots, and the median over genes of Pearson(y, f) over the unit's spots.
        F4-4 holds when S0006's median |y - f| exceeds every other center's, on every encoder and scale.
  acs <production_index.json> <regimeB_root> <t10_comparisons.csv> <out>
        (i) from F3's committed comparisons (fix1 pair, theta3, log(1 + y) or log income): per task and cost ratio c, the
        comparisons, the share where regime B is narrower, the median width ratio and the median of regime B's m_median;
        (ii) from the regcomp units' gene rows (theta3, C_fix1, A 'twostage_t|fpc', B 'regB_t', cost 'unit' in both): per
        task, budget and n_L of A, the median over genes of regime B's per-gene mean width over regime A's at the same
        budget. F4-3 holds when on ACS_STATES regime B is narrower in at least half of the unit-cost pairs and the median
        cost-matched m_median_B on ACS_STATES is below every HEST task's.
Writes a summary JSON first, then the tables.
"""
import json, os, sys
import numpy as np, pandas as pd

HEST = ["CCRCC", "CCRCC_merged", "INDIANA_KIDNEY", "LUNG_XENIUM"]


def main_s0006(cfgp, out):
    import pyarrow.parquet as pq
    cfg = json.load(open(cfgp)); rows = []
    for cell in cfg["cells"]:
        if cell["task"] != "kidney__Visium":
            continue
        tab = pq.read_table(cell["pred"])
        fold = tab.column("fold").to_numpy(zero_copy_only=False).astype(str)
        donor = tab.column("donor_id").to_numpy(zero_copy_only=False).astype(str)
        for sc in cfg["scales"]:
            genes = [c.split("__", 1)[1] for c in tab.column_names if c.startswith(f"y_{sc}__")]
            Y = np.column_stack([tab.column(f"y_{sc}__{g}").to_numpy() for g in genes]).astype(np.float64)
            F = np.column_stack([tab.column(f"f_{sc}__{g}").to_numpy() for g in genes]).astype(np.float64)
            for u in sorted(set(fold.tolist())):
                k = fold == u; y, f = Y[k], F[k]
                yc, fc = y - y.mean(0), f - f.mean(0)
                den = np.sqrt((yc ** 2).sum(0) * (fc ** 2).sum(0))
                r = np.where(den > 0, (yc * fc).sum(0) / np.where(den > 0, den, 1.0), np.nan)
                rows.append(dict(task=cell["task"], encoder=cell["encoder"], scale=sc, center_unit=u, n_spots=int(k.sum()),
                                 n_donors=len(set(donor[k].tolist())),
                                 med_abs_resid=float(np.median(np.median(np.abs(y - f), axis=0))),
                                 pearson_median=float(np.nanmedian(r))))
    D = pd.DataFrame(rows)
    hold = []
    for (e, s), d in D.groupby(["encoder", "scale"]):
        s6 = float(d.loc[d.center_unit == "S0006", "med_abs_resid"].iloc[0])
        oth = d.loc[d.center_unit != "S0006", "med_abs_resid"]
        hold.append(dict(encoder=e, scale=s, s0006=s6, others_max=float(oth.max()), holds=bool(s6 > oth.max())))
    H = pd.DataFrame(hold)
    summ = dict(prediction="F4-4", holds=bool(H.holds.all()), cells=hold)
    json.dump(summ, open(os.path.join(out, "f4_s0006_summary.json"), "w"), indent=1)
    D.to_csv(os.path.join(out, "f4_s0006_by_center.csv"), index=False)
    print(json.dumps(summ, indent=1))


def main_acs(idxp, root, t10p, out):
    t10 = pd.read_csv(t10p)
    t = t10[(t10.pair == "fix1") & (t10.estimand == "theta3") & t10.scale.isin(["log1p", "log_income"])]
    T1 = t.groupby(["task", "c"]).agg(comparisons=("median_ratio_mean_width", "size"),
                                      share_B_narrower=("median_ratio_mean_width", lambda x: float((x < 1).mean())),
                                      median_ratio=("median_ratio_mean_width", "median"),
                                      median_m_B=("m_median_B", "median")).reset_index()
    idx = json.load(open(idxp)); frames = []
    cols = ["task", "encoder", "scale", "estimand", "gene", "form", "regime", "budget", "cost", "n_L", "interval", "mean_width"]
    for u in idx["units"]:
        if u["item"] != "regcomp" or u["task"] not in HEST + ["ACS_STATES"]:
            continue
        p = os.path.join(root, u["unit"], "regcomp_genes.parquet")
        if not os.path.exists(p):
            continue
        x = pd.read_parquet(p, columns=cols)
        x = x[(x.estimand == "theta3") & (x.form == "C_fix1") & (x.cost.astype(str) == "unit") & x.scale.isin(["log1p", "log_income"])]
        if len(x):
            frames.append(x)
    G = pd.concat(frames, ignore_index=True)
    a = G[(G.regime == "A") & (G.interval == "twostage_t|fpc")]
    b = G[(G.regime == "B") & (G.interval == "regB_t")]
    k = ["task", "encoder", "scale", "budget", "gene"]
    m = a[k + ["n_L", "mean_width"]].merge(b[k + ["mean_width"]], on=k, suffixes=("_A", "_B"))
    m["r"] = m.mean_width_B / m.mean_width_A
    T2 = m.groupby(["task", "encoder", "scale", "budget", "n_L"]).r.median().rename("median_ratio_unit").reset_index()
    acs2 = T2[T2.task == "ACS_STATES"]
    cm = T1[T1.c > 1].groupby("task").median_m_B.median()
    cond_a = bool(len(acs2) > 0 and (acs2.median_ratio_unit < 1).mean() >= 0.5)
    cond_b = bool("ACS_STATES" in cm and all(cm["ACS_STATES"] < cm[h] for h in HEST if h in cm))
    summ = dict(prediction="F4-3", holds=bool(cond_a and cond_b), unit_cost_pairs_acs=int(len(acs2)),
                unit_cost_share_B_narrower_acs=float((acs2.median_ratio_unit < 1).mean()) if len(acs2) else None,
                cost_matched_median_m_B={k_: float(v) for k_, v in cm.items()}, cond_unit_cost=cond_a, cond_m=cond_b)
    json.dump(summ, open(os.path.join(out, "f4_acs_summary.json"), "w"), indent=1)
    T1.to_csv(os.path.join(out, "f4_acs_cost_matched_by_task.csv"), index=False)
    T2.to_csv(os.path.join(out, "f4_acs_unit_cost_ratio.csv"), index=False)
    print(json.dumps(summ, indent=1))


def main():
    mode = sys.argv[1]; out = sys.argv[-1]; os.makedirs(out, exist_ok=True)
    if mode == "s0006":
        main_s0006(sys.argv[2], out)
    elif mode == "acs":
        main_acs(sys.argv[2], sys.argv[3], sys.argv[4], out)
    else:
        raise SystemExit(f"unknown mode {mode}")


if __name__ == "__main__":
    main()
