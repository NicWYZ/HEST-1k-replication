"""Round 10, track final-runs, F2.4: configs of regime B, one unit per (task, encoder) (plan, section 5.4).

HEST tasks (CCRCC, CCRCC_merged, INDIANA_KIDNEY, LUNG_XENIUM) on the prediction parquets round 5's E3 read, log(1 + y);
ACS by state on round 4's package parquet with round 5's theta2 kind 'mean' (reported as mu); the six corpus tasks on
their donor-design prediction files of record with the option (b) spot features, both scales, as cluster values v2
lists them. Estimands theta3 and theta2, m in {3, 4, 6, 8, 10, 15, 20, 30}, R = 2,000. Each population names the
cluster values its zbar is checked against.
usage: round10_final_runs_f2_regimeB_configs.py <repo root>
"""
import json, os, sys

root = sys.argv[1]
H = "/work/users/w/e/weiyang/hest_replication/results"
CV = f"{H}/round10/final_runs/F2"
dst = os.path.join(root, "results/round10/final_runs/F2/configs/regimeB"); os.makedirs(dst, exist_ok=True)
M = [3, 4, 6, 8, 10, 15, 20, 30]
PQ = {"CCRCC": f"{H}/round3/B1_ppi/b1_predictions__CCRCC__{{e}}.parquet",
      "CCRCC_merged": f"{H}/round3/B1_ppi/b1_predictions__CCRCC_merged__{{e}}.parquet",
      "INDIANA_KIDNEY": f"{H}/round4/ppi/Q2_theory/predictions_INDIANA_KIDNEY/b1_predictions__INDIANA_KIDNEY__{{e}}.parquet",
      "LUNG_XENIUM": f"{H}/round4/ppi/Q2_theory/predictions/b1_predictions__LUNG_XENIUM__{{e}}.parquet"}
units = {}
for t, p in PQ.items():
    for e in ("uni_v2", "hoptimus0", "resnet50"):
        units[f"{t}__{e}"] = [dict(task=t, vtag=t, encoder=e, arm=e, scale="log1p", source="r5", parquet=p.format(e=e),
                                   estimands=["theta3", "theta2"], cluster_values=f"{CV}/cluster_values_v1/cluster_values__{t}.parquet")]
units["ACS_STATES__pkg"] = [dict(task="ACS_STATES", vtag="ACS_STATES", encoder="pkg", arm="package", scale="log_income",
                                 source="r5", theta2_kind="mean", parquet=f"{H}/round4/ppi/Q2_theory/predictions/ACS_STATES.parquet",
                                 estimands=["theta3", "theta2"],
                                 cluster_values=f"{CV}/cluster_values_v1b_acs/cluster_values__ACS_STATES.parquet")]
cc = json.load(open(os.path.join(root, "results/round10/final_runs/F2/configs/f2_cluster_values_v2_corpus.json")))
for p in cc["populations"]:
    for sc in p["scales"]:
        units.setdefault(f"{p['task']}__{p['encoder']}", []).append(
            dict(task=p["task"], vtag=p["task"], encoder=p["encoder"], arm=p["encoder"], scale=sc["name"], source="corpus",
                 path=p["path"], morph_path=p["morph_path"], y_prefix=sc["y_prefix"], f_prefix=sc["f_prefix"],
                 donor_col=p.get("donor_col", "donor_id"), estimands=["theta3", "theta2"],
                 cluster_values=f"{CV}/cluster_values_v2_corpus/cluster_values__{p['task']}.parquet"))
for u, pops in units.items():
    json.dump(dict(stage="F2.4", unit=f"regimeB__{u}", R=2000, m_grid=M, populations=pops),
              open(os.path.join(dst, f"f2_regimeB__{u}.json"), "w", newline="\n"), indent=1)
print(len(units), "unit configs written to", dst)
