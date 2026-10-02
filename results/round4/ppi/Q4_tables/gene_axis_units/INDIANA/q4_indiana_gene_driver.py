#!/usr/bin/env python
"""Round 4 PPI Q4 gene axis, Indiana: runs round3_b1_ppi.py --predict in donor mode on INDIANA_KIDNEY with the
UNION of the training-only 200-gene fold lists (results/round4/data/P6_genes/genes__INDIANA_KIDNEY__200.csv) as the
target gene list. Same in-memory patch as round4_ppi_q2_indiana_predict_driver.py (donor labels from the task def).
Usage: q4_indiana_gene_driver.py ENCODER OUT_DIR_REL TASKDEF GENELIST_CSV"""
import sys, json, hashlib
import pandas as pd
import round3_b1_ppi as B
enc, out_rel, td_path, gl = sys.argv[1:5]
td = json.load(open(td_path))
d = pd.read_csv(gl)
genes = sorted(set(d.gene))
cand = set(td["target_genes"]["list"])
missing = [g for g in genes if g not in cand]
assert not missing, missing[:5]
td["target_genes"] = dict(td["target_genes"], list=genes, n=len(genes),
    selection="Q4 gene axis: union of the 25 training-only fold lists of genes__INDIANA_KIDNEY__200.csv (md5 %s)" % hashlib.md5(open(gl, "rb").read()).hexdigest())
copy = "INDIANA_KIDNEY__q4_union_genes.json"
json.dump(td, open(copy, "w"), indent=1)
print("[driver] n genes", len(genes), "task-def copy md5", hashlib.md5(open(copy, "rb").read()).hexdigest(), flush=True)
labels = {s["sample_id"]: s["donor_id"] for s in td["samples"]}
B.donor_labels_from_audit = lambda task: dict(labels)
print("[driver] module file:", B.__file__, "n_samples", len(labels), "n_donors", len(set(labels.values())), flush=True)
sys.exit(B.main(["--predict", enc, "--task-def", copy, "--design", "donor", "--out-dir", out_rel,
                 "--morph-dir", "results/round4/ppi/Q2_theory/morph_links"]))
