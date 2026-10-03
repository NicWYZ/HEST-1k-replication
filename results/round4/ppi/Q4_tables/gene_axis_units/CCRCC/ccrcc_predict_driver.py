#!/usr/bin/env python
"""Round 4 PPI Q4 CCRCC gene-axis driver: runs round3_b1_ppi.py --predict (donor mode) on CCRCC with the
UNION of the training-only 200-gene fold lists (results/round4/data/P6_genes/genes__CCRCC__200.csv, 24 donor
folds) as the target gene list, predicted for every donor (lead decision of 2 Oct 2026). No committed file is
edited. A copy of the task definition is written to the working directory with target_genes.list replaced
(sorted union) and paths.target_genes pointed at a non-existent file so the harness's on-disk list check
(which compares with the benchmark's 50-gene file) does not fire.
Usage: ccrcc_predict_driver.py ENCODER OUT_DIR_REL TASKDEF GENES_CSV"""
import sys, json, hashlib, collections, csv
import round3_b1_ppi as B
enc, out_rel, td_path, gcsv = sys.argv[1:5]
td = json.load(open(td_path))
rows = list(csv.DictReader(open(gcsv)))
folds = sorted({r["fold"] for r in rows})
cnt = collections.Counter(r["gene"] for r in rows)
genes = sorted(cnt)
assert len(folds) == 24 and len(genes) == 459, (len(folds), len(genes))
td["target_genes"] = dict(td["target_genes"], list=genes, n=len(genes),
    selection="Q4 driver: union of the 24 donor-fold 200-gene training-only lists of P6_genes/genes__CCRCC__200.csv")
td["paths"] = dict(td["paths"], target_genes="bench_data/CCRCC/__q4_union_genes_no_such_file.json")
copy = "CCRCC__q4_union459.json"
json.dump(td, open(copy, "w"), indent=1)
json.dump({g: cnt[g] for g in genes}, open("q4_gene_fold_counts.json", "w"), indent=1)
print("[driver] genes", len(genes), "in all folds", sum(v == 24 for v in cnt.values()), flush=True)
print("[driver] task-def copy md5", hashlib.md5(open(copy, "rb").read()).hexdigest(), flush=True)
print("[driver] module file:", B.__file__, flush=True)
sys.exit(B.main(["--predict", enc, "--task-def", copy, "--design", "donor", "--out-dir", out_rel]))
