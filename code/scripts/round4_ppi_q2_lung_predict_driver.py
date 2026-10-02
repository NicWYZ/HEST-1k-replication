#!/usr/bin/env python
"""Round 4 PPI Q2 lung driver: runs round3_b1_ppi.py's --predict path (calibration-fraction-zero donor mode)
on LUNG_XENIUM with the round4_ppi_data lung reader in place of the harness load. No committed file is edited;
two attributes of the imported modules are replaced in memory:
  H.load_task        -> round4_ppi_data.load_lung (NCBI865 barcode 051x019 dropped first), log1p of raw counts
  B.donor_labels_from_audit -> donor labels of the task definition itself (no round-3 audit rows exist for lung)
The task definition is read from a copy whose only change is label_set 'audited' -> 'lung_donor_set' (B1 refuses
label_set == 'audited', a guard written for IDC). Usage: lung_predict_driver.py ENCODER OUT_DIR_REL TASKDEF_COPY"""
import sys, os, numpy as np
import round4_ppi_data as R
import round3_b1_ppi as B
enc, out_rel, tdcopy = sys.argv[1:4]
H = B.H
ROOT = H.ROOT

def load_task(td, e):
    genes = list(td["target_genes"]["list"])
    X, Yraw, samp, bc, xy = R.load_lung(td, e, genes)
    Y = np.log1p(Yraw.astype(np.float32)).astype(np.float32)
    return X, Y, samp, bc, xy, genes

def donor_labels(task):
    td = R.read_task(tdcopy)
    return {s["sample_id"]: s["donor_id"] for s in td["samples"]}

H.load_task = load_task
B.donor_labels_from_audit = donor_labels
print("[driver] module files:", B.__file__, H.__file__, R.__file__, flush=True)
sys.exit(B.main(["--predict", enc, "--task-def", tdcopy, "--design", "donor", "--out-dir", out_rel,
                   "--morph-dir", "results/round4/ppi/Q2_theory/morph_links"]))
