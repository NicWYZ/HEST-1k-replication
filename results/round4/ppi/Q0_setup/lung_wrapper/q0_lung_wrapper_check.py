#!/usr/bin/env python
"""Q0 lung wrapper check. Run from the job workdir: python q0_lung_wrapper_check.py OUTDIR"""
import csv, json, os, sys, traceback
import round4_ppi_data as R

out = sys.argv[1]
CLONE = os.environ["CLONE"]
_m = R.d4()
_files = {"round3_d4_sets": _m.__file__, "round3_a0_harness": _m.H.__file__,
          "round3_a3_weighted": _m.A3.__file__, "round2_r2_gene_check": _m.GC.__file__,
          "round4_ppi_data(staged)": R.__file__}
for _k, _v in _files.items():
    print("module_file", _k, os.path.abspath(_v))
    if not _k.endswith("(staged)"):
        assert os.path.abspath(_v).startswith(CLONE + "/"), f"{_k} not imported from clone: {_v}"
REPO = "/work/users/w/e/weiyang/hest_replication"
ENCS = ["hoptimus0", "uni_v2", "resnet50"]
lung = R.read_task(f"{REPO}/results/round4/data/P5_task/LUNG_XENIUM.json")
breast = R.read_task(f"{REPO}/results/round3/D4_expansion/task_defs/BREAST_XENIUM.json")
npatch = {s["sample_id"]: s["n_patch_spots"] for s in lung["samples"]}
assert len(npatch) == 20

rows = []
for s in sorted(npatch):
    for enc in ENCS:
        r = R.check_sample(lung, s, enc, apply_drop=True)
        b = R.check_sample(lung, s, enc, apply_drop=False)
        r.update(n_patch_spots_task=npatch[s], rows_after_equals_task=r["rows_after"] == npatch[s],
                 dropped_barcodes=";".join(R.dropped_for(lung, s)),
                 subset_ok_without_drop=b["subset_ok"], n_missing_without_drop=b["n_missing"])
        rows.append(r)
fields = list(rows[0].keys())
with open(f"{out}/q0_lung_wrapper_check.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)

# NCBI865: real round3 load_set raises before the drop (a task def restricted to NCBI865)
td1 = dict(lung); td1["samples"] = [s for s in lung["samples"] if s["sample_id"] == "NCBI865"]
genes = lung["target_genes"]["list"][:3]
demo = {}
for enc in ENCS:
    try:
        R.d4().load_set(td1, enc, genes); demo[enc] = "NO ERROR"
    except AssertionError as e:
        demo[enc] = "AssertionError: " + str(e)
    X, Y, samp, bc, xy = R.load_lung(td1, enc, genes)
    demo[enc + "_load_lung_rows"] = int(X.shape[0])
    demo[enc + "_load_lung_Y_shape"] = list(Y.shape)

kept_l, n_l = R.filter_xenium_controls(lung["target_genes"]["list"])
kept_b, n_b = R.filter_xenium_controls(breast["target_genes"]["list"])
summary = dict(round3_load_set_on_NCBI865_before_drop=demo,
    lung_target_list_len=len(lung["target_genes"]["list"]), lung_controls_removed=n_l, lung_kept=len(kept_l),
    breast_target_list_len=len(breast["target_genes"]["list"]), breast_controls_removed=n_b, breast_kept=len(kept_b),
    lung_sample_table=R.lung_sample_table(lung),
    all_rows_after_equal_task=all(r["rows_after_equals_task"] for r in rows),
    all_subset_ok_after_drop=all(r["subset_ok"] for r in rows),
    subset_fails_without_drop=sorted({(r["sample_id"], r["encoder"]) for r in rows if not r["subset_ok_without_drop"]}))
summary["subset_fails_without_drop"] = [list(x) for x in summary["subset_fails_without_drop"]]
json.dump(summary, open(f"{out}/q0_lung_wrapper_summary.json", "w"), indent=1)
with open(f"{out}/q0_lung_sample_table.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(summary["lung_sample_table"][0])); w.writeheader(); w.writerows(summary["lung_sample_table"])
print(json.dumps({k: v for k, v in summary.items() if k != "lung_sample_table"}, indent=1))
