"""b1, H1(b) and the H4 arithmetic: round 3 split conformal coverage aggregated from the per-fold files.

Definition (round 3 A1 stage report, section 6.1; the per-fold file is the most granular committed file):
  a cell is one (task, label_set, encoder, design, score); its coverage is the plain mean of its folds' coverage;
  a design's coverage is the plain mean over its cells; a task's coverage is the plain mean over the 12 encoders.
Implemented here with csv + numpy only. H4: the encoder spread is max - min of the benchmark Pearson over the 12
encoders (a1_vs_benchmark_pearson.csv), and the ratio of the random-minus-patient total to it.
usage: b1_h1b_h4.py <out_dir>
"""
import csv, glob, json, os, sys
from collections import defaultdict
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b1_common as C

out = sys.argv[1]
A1 = C.CLONE + "/results/round3/A1_coverage"
files = sorted(glob.glob(A1 + "/a1_by_fold__*__main.csv")) + sorted(glob.glob(A1 + "/a1_by_fold__*__slideout.csv"))
folds = defaultdict(list)
nrows = 0
for p in files:
    C.note_input(p)
    with open(p) as fh:
        for r in csv.DictReader(fh):
            nrows += 1
            folds[(r["task"], r["label_set"], r["encoder"], r["design"], r["score"])].append(float(r["coverage"]))
cell = {k: float(np.mean(v)) for k, v in folds.items()}
res = dict(files=len(files), fold_rows=nrows, cells=len(cell))
rows = []
for design in ("random", "slide_out", "donor", "patient"):
    for score in ("abs", "scaled"):
        sel = {k: v for k, v in cell.items() if k[3] == design and k[4] == score}
        vals = np.array(list(sel.values()))
        noaud = np.array([v for k, v in sel.items() if not (k[0] == "IDC" and k[1] == "audited")])
        noship = np.array([v for k, v in sel.items() if not (k[0] == "IDC" and k[1] == "shipped")])
        rows.append(dict(design=design, score=score, cells=len(vals),
                         encoders=len({k[2] for k in sel}), tasks=len({(k[0], k[1]) for k in sel}),
                         coverage_mean=float(vals.mean()), sd_across_cells=float(vals.std(ddof=1)),
                         mean_without_IDC_audited=float(noaud.mean()), cells_without_IDC_audited=len(noaud),
                         mean_without_IDC_shipped=float(noship.mean()), cells_without_IDC_shipped=len(noship)))
with open(os.path.join(out, "b1_h1b_by_design.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); [w.writerow(r) for r in rows]
trow = []
for design in ("random", "slide_out", "donor", "patient"):
    for (t, ls) in sorted({(k[0], k[1]) for k in cell}):
        v = [cell[k] for k in cell if k[0] == t and k[1] == ls and k[3] == design and k[4] == "abs"]
        if v:
            trow.append(dict(task=t, label_set=ls, design=design, score="abs", encoders=len(v), coverage_mean=float(np.mean(v))))
with open(os.path.join(out, "b1_h1b_by_task.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(trow[0])); w.writeheader(); [w.writerow(r) for r in trow]
res["by_design"] = rows
res["CCRCC"] = [r for r in trow if r["task"] == "CCRCC"]
# H4 arithmetic
bp = C.note_input(A1 + "/a1_vs_benchmark_pearson.csv")
with open(bp) as fh:
    b = {r["encoder"]: float(r["benchmark_pca_ridge_avg_paper9"]) for r in csv.DictReader(fh)}
dp = C.note_input(C.CLONE + "/results/round2/R3_splits/r3_decomposition_terms.csv")
with open(dp) as fh:
    terms = {r["term"]: r for r in csv.DictReader(fh)}
tot = float(terms["TOTAL random - patient"]["mean"])
spread = max(b.values()) - min(b.values())
res["H4"] = dict(encoders=len(b), best=max(b, key=b.get), best_value=max(b.values()), worst=min(b, key=b.get),
                 worst_value=min(b.values()), encoder_spread=spread, total_random_minus_patient=tot,
                 ratio_total_over_spread=tot / spread,
                 same_patient_other_slide=float(terms["same patient, other slide"]["mean"]),
                 sum_of_four_first_terms=sum(float(terms[k]["mean"]) for k in
                                             ("training-set size", "spatial adjacency, size matched",
                                              "residual adjacency (buffer)")) )
json.dump(res, open(os.path.join(out, "b1_h1b_h4_summary.json"), "w"), indent=1)
C.write_inputs(out)
print(json.dumps(res, indent=1))
