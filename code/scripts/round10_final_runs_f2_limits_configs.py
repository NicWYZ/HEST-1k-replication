"""Round 10, track final-runs, F2.1: configs of the limits arms, one per regime A unit (plan, section 5.2).

Reads results/round10/final_runs/F2/configs/regimeA/f2_regimeA__<unit>.json and writes
results/round10/final_runs/F2/configs/limits/f2_limits__<unit>.json with the same cluster values, selection and n grid,
R_lim 2000 (round 5's n_sub), B_kluger 2000 (round 7's B_BOOT) and chunk 100; plus f2_limits__smoke.json (the first two
CCRCC uni_v2 log1p populations of mu and theta3, the draw check, and round 5's E4b reference cell as the anchor).
usage: round10_final_runs_f2_limits_configs.py <repo root>
"""
import glob, json, os, sys

root = sys.argv[1]
src = os.path.join(root, "results/round10/final_runs/F2/configs/regimeA")
dst = os.path.join(root, "results/round10/final_runs/F2/configs/limits"); os.makedirs(dst, exist_ok=True)
BASE = "/work/users/w/e/weiyang/hest_replication/results"
n = 0
for p in sorted(glob.glob(os.path.join(src, "f2_regimeA__*.json"))):
    c = json.load(open(p)); unit = os.path.basename(p)[len("f2_regimeA__"):-len(".json")]
    if unit.startswith("smoke") or c.get("anchor_r9"):
        continue
    o = dict(stage="F2.1-limits", unit=f"limits__{unit}", cluster_values=c["cluster_values"], select=c.get("select"),
             n_grid=c["n_grid"], extra_n=c.get("extra_n", {}), R_lim=2000, B_kluger=2000, chunk=100,
             regimeA_config=os.path.relpath(p, root).replace(os.sep, "/"))
    json.dump(o, open(os.path.join(dst, f"f2_limits__{unit}.json"), "w"), indent=1); n += 1
smoke = dict(stage="F2.1-limits", unit="limits__smoke",
             cluster_values=[f"{BASE}/round10/final_runs/F2/cluster_values_v1/cluster_values__CCRCC.parquet"],
             select={"task": ["CCRCC"], "encoder": ["uni_v2"], "scale": ["log1p"], "estimand": ["theta3", "mu"]},
             max_pops=2,
             n_grid=[4, 6, 8, 10, 12, 16], extra_n={}, R_lim=2000, B_kluger=2000, chunk=100, check_draws=20000,
             anchor_r5=dict(task="CCRCC", vtag="CCRCC", arm="uni_v2", estimand="theta3", n_L=8, draws=2000, check_genes=5,
                            cluster_values=f"{BASE}/round10/final_runs/F2/cluster_values_v1/cluster_values__CCRCC.parquet",
                            pred_parquet=f"{BASE}/round3/B1_ppi/b1_predictions__CCRCC__uni_v2.parquet",
                            e4b_script=f"{BASE}/round10/final_runs/_snapshots/9185bc6be157ee9c62d8d1067e5ad9e14f53984e/code/scripts/round5_ppi_e4b_rejective.py",
                            e4b_grid="/work/users/w/e/weiyang/hest_code/round10-final-runs/results/round5/ppi/E4b_rejective/e4b_grid.csv"))
json.dump(smoke, open(os.path.join(dst, "f2_limits__smoke.json"), "w"), indent=1)
print(n, "unit configs and the smoke config written to", dst)
