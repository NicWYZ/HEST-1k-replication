"""Round 6 cheatsheet track, C1: summary tables and the grid projection.

Reads results/round6/cheatsheet/C1_pilot/manifest.csv and writes beside it
  c1_trials.csv        one row per slot: the trial that counts, attempts, exclusions
  c1_by_model_role.csv tokens, cost, turns and wall time per model and role
                       (counted trials), plus all attempts' cost
  c1_projection.csv    the masterplan's grid per model and role, with the
                       pilot's mean cost and wall time per counted trial and the
                       attempts-per-slot factor, giving projected cost and wall
  c1_vs_comparators.csv the twelve pilot scores beside the comparators on S1*

The projection assumes a writer's cost does not depend on its size and that a
role's cost is the same in every arm. Neither was measured in the pilot, which
ran one size and one arm per role. Both assumptions are stated in the report.
"""
import os

import numpy as np
import pandas as pd

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
D = os.path.join(REPO, "results/round6/cheatsheet/C1_pilot")
COMP = os.path.join(REPO, "results/round6/cheatsheet/C0_comparators/comparators.csv")

# masterplan "Trial count", sessions per model
GRID = {"baseline": 4, "writer": 12, "predictor": 18, "combined": 5}
# the masterplan's cut order, each step's change to the grid
CUTS = [
    ("cut 1: arm A combined session on Haiku only", {"sonnet": {"combined": -1}, "opus": {"combined": -1}}),
    ("cut 2: Haiku runs one replicate", {"haiku": {"baseline": -2, "writer": -6, "predictor": -9, "combined": -2}}),
    ("cut 3: 4,096-byte size dropped for Sonnet", {"sonnet": {"writer": -4, "predictor": -6}}),
]


def main():
    m = pd.read_csv(os.path.join(D, "manifest.csv"))
    m["model_short"] = m["model"].str.replace("claude-", "").str.replace("-5-5", "")
    for c in ("cost_usd", "wall_s", "input_tokens", "output_tokens", "cache_read", "cache_write", "turns"):
        m[c] = pd.to_numeric(m[c], errors="coerce")
    att = m.groupby("slot").agg(attempts=("trial_id", "size"),
                                excluded=("status", lambda s: int((s == "excluded").sum())),
                                failed=("status", lambda s: int((s == "failed").sum())),
                                cost_all_attempts=("cost_usd", "sum"),
                                wall_all_attempts=("wall_s", "sum")).reset_index()
    done = m[m["status"] == "done"].copy()
    trials = done.merge(att, on="slot", how="right")
    trials.to_csv(os.path.join(D, "c1_trials.csv"), index=False)

    g = done.groupby(["model_short", "role"]).agg(
        n=("trial_id", "size"), input_tokens=("input_tokens", "sum"), output_tokens=("output_tokens", "sum"),
        cache_read=("cache_read", "sum"), cache_write=("cache_write", "sum"), cost_usd=("cost_usd", "sum"),
        turns=("turns", "sum"), wall_s=("wall_s", "sum")).reset_index()
    a = m.groupby(["model_short", "role"]).agg(attempts=("trial_id", "size"),
                                                 cost_all_attempts=("cost_usd", "sum"),
                                                 wall_all_attempts=("wall_s", "sum")).reset_index()
    g = g.merge(a, on=["model_short", "role"], how="outer")
    g.to_csv(os.path.join(D, "c1_by_model_role.csv"), index=False)

    rows = []
    for model in ("haiku", "sonnet", "opus"):
        for role, n in GRID.items():
            r = g[(g.model_short == model) & (g.role == role)]
            if r.empty:
                rows.append({"model": model, "role": role, "grid_sessions": n})
                continue
            r = r.iloc[0]
            counted = 0 if pd.isna(r["n"]) else int(r["n"])
            if counted:
                # cost and wall per counted trial, including every attempt it took
                cost_per = r["cost_all_attempts"] / counted
                wall_per = r["wall_all_attempts"] / counted
                basis = "per counted trial, all attempts included"
            else:
                # no attempt counted: per attempt, a lower bound on the cost per counted trial
                cost_per = r["cost_all_attempts"] / r["attempts"]
                wall_per = r["wall_all_attempts"] / r["attempts"]
                basis = "per attempt (no attempt counted), a lower bound"
            rows.append({"model": model, "role": role, "grid_sessions": n,
                         "pilot_counted": counted, "pilot_attempts": int(r["attempts"]),
                         "cost_per_counted_usd": cost_per, "wall_per_counted_s": wall_per,
                         "projected_cost_usd": cost_per * n, "projected_wall_s": wall_per * n, "basis": basis})
    p = pd.DataFrame(rows)
    p.to_csv(os.path.join(D, "c1_projection.csv"), index=False)

    # cost of each cut in the masterplan's order, cumulative
    unit = {(r.model, r.role): r.cost_per_counted_usd for r in p.itertuples() if pd.notna(getattr(r, "cost_per_counted_usd", np.nan))}
    total = float(p["projected_cost_usd"].sum())
    cuts = [{"step": "full grid", "projected_cost_usd": total, "saving_usd": 0.0}]
    for name, change in CUTS:
        saving = -sum(unit.get((mod, role), 0.0) * k for mod, d in change.items() for role, k in d.items())
        total -= saving
        cuts.append({"step": name, "projected_cost_usd": total, "saving_usd": saving})
    pd.DataFrame(cuts).to_csv(os.path.join(D, "c1_cuts.csv"), index=False)

    comp = pd.read_csv(COMP)
    s1 = comp[comp["scored_set"] == "S1star"]
    sc = done[done["role"] != "writer"][["model_short", "role", "arm", "size", "trial_id", "rbar"]]
    sc.to_csv(os.path.join(D, "c1_vs_comparators.csv"), index=False)
    print(trials[["slot", "trial_id", "status", "attempts", "excluded", "rbar", "cost_usd", "wall_s"]].to_string(index=False))
    print(g.to_string(index=False))
    print(p.to_string(index=False))
    print(pd.DataFrame(cuts).to_string(index=False))
    print(s1[["comparator", "encoder", "arm", "size", "rbar"]].to_string(index=False))


if __name__ == "__main__":
    main()
