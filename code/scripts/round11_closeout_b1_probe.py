"""b1 probe: schemas of the inputs and whose() verdicts. Reads only, computes nothing.
usage: b1_probe.py <out_dir>"""
import glob, json, os, sys
import pyarrow.parquet as pq
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b1_provenance_kernel as K

PID = "proj_8450e231133d"
FID = "c9016697-c909-435e-82fc-ebfb9daaa857/b1"
PLAN = "docs/round11/closeout/round11_closeout_plan.md"
R = "/work/users/w/e/weiyang/hest_replication/results"
F = R + "/round10/final_runs"
files = [
    R + "/round3/B1_ppi/b1_predictions__CCRCC__uni_v2.parquet",
    R + "/round4/ppi/Q2_theory/predictions_INDIANA_KIDNEY/b1_predictions__INDIANA_KIDNEY__uni_v2.parquet",
    R + "/round4/ppi/Q2_theory/predictions/b1_predictions__LUNG_XENIUM__uni_v2.parquet",
    F + "/F1/predict/kidney__Visium__uni_v2/pred__kidney__Visium__uni_v2__donor.parquet",
    F + "/F1/predict/kidney__Visium__uni_v2/pred__kidney__Visium__uni_v2__center.parquet",
    F + "/F1/predict/brain__Visium__uni_v2/pred__brain__Visium__uni_v2__donor.parquet",
    F + "/F2/morphology/kidney__Visium/morphology__kidney__Visium.parquet",
    F + "/F2/regimeA/CCRCC__uni_v2/regimeA_cells.parquet",
    F + "/F2/limits/CCRCC__uni_v2__p0of2/limits_cells.parquet",
]
out = sys.argv[1]
B1 = os.path.dirname(os.path.abspath(out))
for d, note in ((B1, "B1 root: independent recomputation of the round 11 headline table"),
                (os.path.join(B1, "scripts"), "B1 scripts copied from the sub-agent's local folder")):
    K.stamp_dir(d, track="closeout", plan=PLAN, note=note, project_id=PID, frame_id=FID)
rep = {}
for p in files:
    d = dict(exists=os.path.exists(p))
    if d["exists"]:
        md = pq.read_metadata(p)
        names = md.schema.names
        d.update(rows=md.num_rows, ncols=len(names),
                 nonprefixed=[c for c in names if not (c.startswith("y_") or c.startswith("f_"))],
                 first_y=[c for c in names if c.startswith("y_")][:3],
                 first_f=[c for c in names if c.startswith("f_")][:3],
                 whose=K.whose(os.path.dirname(p), project_id=PID, frame_id=FID, plan=PLAN)["verdict"])
    rep[p] = d
# directories listing
rep["_F1_predict_dirs"] = sorted(os.listdir(F + "/F1/predict"))
rep["_kidney_files"] = sorted(os.listdir(F + "/F1/predict/kidney__Visium__uni_v2"))
rep["_limits_units"] = sorted(os.listdir(F + "/F2/limits"))
rep["_regimeA_units"] = sorted(os.listdir(F + "/F2/regimeA"))
for dd in ["/F2/regimeA", "/F2/limits", "/F2/morphology/kidney__Visium", "/F1/predict/kidney__Visium__uni_v2",
           "/F3/institution/production", "/F1/diag_r3_CCRCC"]:
    rep["_whose" + dd] = K.whose(F + dd, project_id=PID, frame_id=FID, plan=PLAN)["verdict"] if os.path.exists(F + dd) else "missing"
json.dump(rep, open(os.path.join(out, "probe.json"), "w"), indent=1)
print(json.dumps(rep, indent=1))
