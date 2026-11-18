"""fcheck: section 2.2 group table from the job ledger, and whose() verdicts on every input directory.
Own code; no project module imported."""
import glob, json, os
import numpy as np, pandas as pd
R = "/work/users/w/e/weiyang/hest_replication/results/round11/closeout"
ME = {"project_id": "proj_8450e231133d", "frame_id": "c9016697-c909-435e-82fc-ebfb9daaa857/fcheck",
      "plan": "docs/round11/closeout/round11_closeout_plan.md"}
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40); pd.set_option("display.max_rows", 400)
f = f"{R}/final/gate_v1/job_ledger.csv"
L = pd.read_csv(f)
print("ledger rows (excluding header)", len(L), "unique ids", L.slurm_job_id.nunique())
def secs(s):
    if not isinstance(s, str) or not s: return np.nan
    dd = 0
    if "-" in s: dd, s = s.split("-"); dd = int(dd)
    p = [int(v) for v in s.split(":")]
    while len(p) < 3: p.insert(0, 0)
    return dd * 86400 + p[0] * 3600 + p[1] * 60 + p[2]
def gb(s):
    if not isinstance(s, str) or not s: return np.nan
    u = s[-1]; v = float(s[:-1]) if u in "KMGT" else float(s)
    return v * {"K": 1 / 1024 ** 2, "M": 1 / 1024, "G": 1, "T": 1024}.get(u, 1 / 1024 ** 3)
L["sec"] = L.elapsed.map(secs); L["rss_gb"] = L.max_rss.map(gb)
groups = {"A6 pilot": [(9529112, 9529116)], "donor chains": [(9530242, 9530256)], "center predictions": [(9530257, 9530260)],
          "institution": [(9530261, 9530261)], "conformal R10": [(9530262, 9530276)], "conformal P": [(9530277, 9530292), (9544479, 9544479)],
          "conformal E": [(9530293, 9530308)], "split check": [(9609677, 9609686)], "kidney E pieces+merges": [(9609687, 9609706)],
          "aggregation v4": [(9665851, 9665851)], "gate bookkeeping": [(9667100, 9667100)]}
out = []
for k, rr in groups.items():
    m = np.zeros(len(L), bool)
    for a, b in rr: m |= (L.slurm_job_id >= a) & (L.slurm_job_id <= b)
    g = L[m]
    out.append(dict(group=k, jobs=len(g), states=dict(g.state.value_counts()), wall_min_s=g.sec.min(), wall_max_s=g.sec.max(),
                    peak_rss_gb=round(g.rss_gb.max(), 2) if g.rss_gb.notna().any() else None,
                    partitions=",".join(sorted(g.partition.dropna().astype(str).unique()))))
o = pd.DataFrame(out); o.to_csv("fcheck_ledger_groups.csv", index=False); print(o.to_string())
print("FAILED:", L[L.state.str.startswith("FAILED")][["slurm_job_id", "name"]].to_string())
print("CANCELLED:", L[L.state.str.startswith("CANCELLED")][["slurm_job_id", "name", "sec"]].to_string())
print("missing from ledger 9530302:", 9530302 not in set(L.slurm_job_id))
# whose()
def whose(d):
    p = os.path.join(d, "_provenance.json")
    if not os.path.exists(p): return "unstamped", None
    s = json.load(open(p))
    if s.get("project_id") != ME["project_id"]: return "other_project", s.get("frame_id")
    if s.get("frame_id") == ME["frame_id"]: return "mine", s.get("frame_id")
    if s.get("plan") == ME["plan"]: return "sibling", s.get("frame_id")
    return "foreign_session", s.get("frame_id")
dirs = sorted(set(glob.glob(f"{R}/a6/donor/*") + glob.glob(f"{R}/a6/conformal/*") + glob.glob(f"{R}/predict/*")
                  + [f"{R}/a6/inst", f"{R}/a6/inst/center_v1", f"{R}/final/gate_v1", "/work/users/w/e/weiyang/hest_replication/results/round3/A1_coverage"]))
W = pd.DataFrame([dict(dir=d.replace(R + "/", ""), verdict=whose(d)[0], frame_id=whose(d)[1]) for d in dirs if os.path.isdir(d)])
W.to_csv("fcheck_inputs_whose.csv", index=False); print(W.verdict.value_counts().to_dict()); print(W[W.verdict != "sibling"].to_string())
open("inputs.txt", "w").write(f + "\n")
