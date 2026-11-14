"""Round 10, track final-runs, F4 aggregate (plan 5e.5). Selects and merges committed or recorded outputs; estimates nothing.

usage: round10_final_runs_f4_aggregate.py <clone> <base> <out>
Steps (summaries first):
  1. the F4 index of the all-spot mu units (F4/f4_allspot_harness_jobs.csv and F4/f4_allspot_remaining.tsv; task from each
     unit's F3 config), and their completeness (PROVENANCE status, all-spot anchor);
  2. F3's regcomp and box aggregates, run unchanged on the all-spot units (<out>/allspot_regcomp, <out>/allspot_box);
  3. merged tables: F3's committed regcomp comparisons and box task summary with every mu row of the HEST and corpus tasks
     replaced by the all-spot rows (column mu_spots: 'all' for those, 'n/a' for theta rows and ACS, whose units are not spots);
  4. beside them: the mu check (means_v2, compare_v2), the readings (S0006, ACS) and E8's m = 15 rows from F3's t29;
  5. a manifest with the md5 of every input.
"""
import csv, hashlib, json, os, subprocess, sys
import pandas as pd

clone, base, out = sys.argv[1:4]
os.makedirs(out, exist_ok=True)
F3A = os.path.join(clone, "results/round10/final_runs/F3")
F4R = os.path.join(clone, "results/round10/final_runs/F4")
MC = os.path.join(base, "F4/mu_check")
HEST = ["CCRCC", "CCRCC_merged", "INDIANA_KIDNEY", "LUNG_XENIUM"]
summ = dict(stage="F4", out=out); sp = os.path.join(out, "f4_aggregate_summary.json")
inputs = []


def dump():
    json.dump(summ, open(sp, "w"), indent=1, default=str)


def status(d):
    p = os.path.join(d, "PROVENANCE.txt")
    if not os.path.exists(p):
        return "missing"
    return next((l.split(":", 1)[1].strip() for l in open(p) if l.startswith("status:")), "no status")


# 1. index
units = [(r["unit"], r["mode"], r["config"]) for r in csv.DictReader(open(os.path.join(F4R, "f4_allspot_harness_jobs.csv")))]
for line in open(os.path.join(F4R, "f4_allspot_remaining.tsv")):
    u, m, cfg, _ = line.rstrip("\n").split("\t"); units.append((u, m, cfg))
idx = dict(units=[]); rows = []
for u, m, cfgp in units:
    task = json.load(open(cfgp))["populations"][0]["task"]
    d = os.path.join(MC, u); st = status(d)
    ap = os.path.join(d, "mu_allspot_anchor.json")
    anc = json.load(open(ap))["passed"] if os.path.exists(ap) else None
    idx["units"].append(dict(item=m, unit=u, task=task)); rows.append(dict(unit=u, item=m, task=task, status=st, anchor_passed=anc))
U = pd.DataFrame(rows); U.to_csv(os.path.join(out, "f4_allspot_units.csv"), index=False)
json.dump(idx, open(os.path.join(out, "f4_allspot_index.json"), "w"), indent=1)
summ.update(units=len(U), completed=int((U.status == "COMPLETED").sum()), anchors_passed=int((U.anchor_passed == True).sum()),
            duplicates=int(U.unit.duplicated().sum()))
dump()
if summ["completed"] != len(U) or summ["anchors_passed"] != len(U):
    raise SystemExit("incomplete all-spot units; see f4_allspot_units.csv")

# 2. F3 aggregates on the all-spot units
py = sys.executable; sd = os.path.dirname(os.path.abspath(__file__))
f2sum = os.path.join(clone, "results/round10/final_runs/F2/aggregate_regimeB/f2_regimeB_summary.csv")
gdiag = os.path.join(base, "F2/diagnostics/diagnostics_v2/f2_gene_diag.parquet")
ip = os.path.join(out, "f4_allspot_index.json")
rc1 = subprocess.call([py, os.path.join(sd, "round10_final_runs_f3_regcomp_aggregate.py"), MC, ip, os.path.join(out, "allspot_regcomp")])
rc2 = subprocess.call([py, os.path.join(sd, "round10_final_runs_f3_box_aggregate.py"), MC, ip, f2sum, gdiag, os.path.join(out, "allspot_box")])
summ.update(regcomp_aggregate_rc=rc1, box_aggregate_rc=rc2); dump()

# 3. merged tables
def merged(f3_path, f4_path, name):
    a = pd.read_csv(f3_path); b = pd.read_csv(f4_path)
    repl = a.estimand.eq("mu") & a.task.ne("ACS_STATES") if "estimand" in a.columns else a.task.ne("ACS_STATES")
    a = a[~repl].copy(); a["mu_spots"] = "n/a"
    b = b[b.estimand.eq("mu")].copy() if "estimand" in b.columns else b.copy(); b["mu_spots"] = "all"
    m = pd.concat([a, b], ignore_index=True, sort=False)
    m.to_csv(os.path.join(out, name), index=False); inputs.extend([f3_path, f4_path])
    return dict(f3_rows_kept=len(a), f4_rows=len(b), rows=len(m))
summ["regcomp_comparisons"] = merged(os.path.join(F3A, "regimeB/aggregate_v1/regcomp/f3_regcomp_comparisons.csv"),
                                     os.path.join(out, "allspot_regcomp/f3_regcomp_comparisons.csv"), "f4_regcomp_comparisons_merged.csv")
summ["box_task_summary"] = merged(os.path.join(F3A, "regimeB/aggregate_v1/box/f3_box_task_summary.csv"),
                                  os.path.join(out, "allspot_box/f3_box_task_summary.csv"), "f4_box_task_summary_merged.csv")
dump()

# 4. beside
for src, dst in [(os.path.join(MC, "means_v2/mu_check_populations.csv"), "f4_mu_check_populations.csv"),
                 (os.path.join(MC, "compare_v2/mu_part3_compare.json"), "f4_mu_part3_compare.json"),
                 (os.path.join(MC, "compare_v2/mu_part3_width_ratio.csv"), "f4_mu_part3_width_ratio.csv"),
                 (os.path.join(MC, "compare_v2/mu_part3_regcomp_cells.csv"), "f4_mu_part3_regcomp_cells.csv"),
                 (os.path.join(base, "F4/readings/readings_v1/s0006/f4_s0006_by_center.csv"), "f4_s0006_by_center.csv"),
                 (os.path.join(base, "F4/readings/readings_v1/s0006/f4_s0006_summary.json"), "f4_s0006_summary.json"),
                 (os.path.join(base, "F4/readings/readings_v1/acs/f4_acs_summary.json"), "f4_acs_summary.json"),
                 (os.path.join(base, "F4/readings/readings_v1/acs/f4_acs_cost_matched_by_task.csv"), "f4_acs_cost_matched_by_task.csv"),
                 (os.path.join(base, "F4/readings/readings_v1/acs/f4_acs_unit_cost_ratio.csv"), "f4_acs_unit_cost_ratio.csv")]:
    open(os.path.join(out, dst), "wb").write(open(src, "rb").read()); inputs.append(src)
t29 = os.path.join(F3A, "aggregate/t29_e8_joint_on_grid.csv"); inputs.append(t29)
e = pd.read_csv(t29)
e15 = e[(e.m == 15) & (e.on_o_grid == True) & ((e.overall_needs_extra_labels == True) | (e.diff_width_median < 0))]
e15.to_csv(os.path.join(out, "f4_e8_m15_rows.csv"), index=False)
summ["e8_m15"] = dict(rows=len(e15), overall_methods=e15.overall_method.value_counts().to_dict(),
                      noextra_methods=e15.noextra_method.value_counts().to_dict(), K=sorted(e15.K.unique().tolist()),
                      parts=sorted(e15.part.unique().tolist()))

# 5. manifest
man = {p: hashlib.md5(open(p, "rb").read()).hexdigest() for p in sorted(set(inputs))}
json.dump(man, open(os.path.join(out, "f4_aggregate_manifest.json"), "w"), indent=1)
summ["finished"] = True; dump()
print(json.dumps(summ, indent=1, default=str))
