#!/usr/bin/env python
"""Round 4 PPI Q2 Indiana-kidney driver: runs round3_b1_ppi.py --predict (calibration-fraction-zero donor mode)
on INDIANA_KIDNEY. No committed file is edited. Two things differ from calling B1 directly:
  1. B.donor_labels_from_audit is replaced in memory by the donor labels of the task definition itself
     (donor_audit_r3.csv has no benchmark_r2 rows for this expansion task, so B1's partition assertion would
     compare against an empty set).
  2. The shipped task definition lists the 31,915-gene CANDIDATE PANEL (its target 50 genes are chosen per fold).
     A copy of the task definition is written to the working directory with target_genes.list replaced by 50
     genes: the 50 most frequently selected across the 25 donor-level ('pool') folds of
     results/round3/D4_expansion/d4_fold_genes__INDIANA_KIDNEY.json, ties broken alphabetically.
Usage: indiana_predict_driver.py ENCODER OUT_DIR_REL TASKDEF"""
import sys, json, collections, hashlib
import round3_b1_ppi as B
enc, out_rel, td_path = sys.argv[1:4]
ROOT = B.ROOT
td = json.load(open(td_path))
fg = json.load(open(f"{ROOT}/results/round3/D4_expansion/d4_fold_genes__INDIANA_KIDNEY.json"))
cnt = collections.Counter(g for v in fg["selections"].values() if v["design"] == "pool" for g in v["genes"])
genes = [g for g, _ in sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0]))[:50]]
cand = set(td["target_genes"]["list"])
assert len(genes) == 50 and all(g in cand for g in genes)
td["target_genes"] = dict(td["target_genes"], list=sorted(genes), n=50,
    selection="Q2 driver: 50 most frequently selected genes over the 25 pool folds of d4_fold_genes__INDIANA_KIDNEY.json, ties alphabetical")
copy = "INDIANA_KIDNEY__q2_50genes.json"
json.dump(td, open(copy, "w"), indent=1)
json.dump({g: cnt[g] for g in sorted(genes)}, open("q2_gene_selection_counts.json", "w"), indent=1)
print("[driver] genes:", sorted(genes), "min count in 25 folds:", min(cnt[g] for g in genes), flush=True)
print("[driver] task-def copy md5", hashlib.md5(open(copy, "rb").read()).hexdigest(), flush=True)
labels = {s["sample_id"]: s["donor_id"] for s in td["samples"]}
B.donor_labels_from_audit = lambda task: dict(labels)
print("[driver] module file:", B.__file__, "n_samples", len(labels), "n_donors", len(set(labels.values())), flush=True)
sys.exit(B.main(["--predict", enc, "--task-def", copy, "--design", "donor", "--out-dir", out_rel,
                 "--morph-dir", "results/round4/ppi/Q2_theory/morph_links"]))
