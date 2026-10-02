#!/usr/bin/env python
"""Round 4 conformal C3, Indiana o sweep: one encoder, one fold shard. Thin driver over
round4_conf_c3 (md5 2d8418677cf8290eec89a14c315b92cd, unedited). INDIANA_KIDNEY, K = 10,
3 calibration draws, 20 label draws, o grid (5,10,25,50,100,200), alphas (0.1, 0.2), score abs.
usage: run_indiana_o.py ENC SHARD NSHARD OUTROOT   (folds with index % NSHARD == SHARD)"""
import hashlib, os, sys, time, json
import round4_conf_c3 as C
enc, shard, nshard, outroot = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
md5 = hashlib.md5(open(C.__file__, "rb").read()).hexdigest()
assert md5 == "2d8418677cf8290eec89a14c315b92cd", md5
T = C.load_task("INDIANA_KIDNEY", enc)
allf = T.fold_names()
folds = [f for i, f in enumerate(allf) if i % nshard == shard]
print("folds total", len(allf), "this shard", len(folds), flush=True)
rows, skipped, t0 = [], {}, time.time()
for sp in T.specs(K=10, n_cal_draws=C.N_CAL_DRAWS, folds=folds):
    fit = T.fit(sp)
    rows += C.o0_rows(fit, alphas=C.ALPHAS)
    rows += C.o_rows(fit, o_grid=C.O_GRID, label_draws=range(C.N_LABEL_DRAWS), alphas=C.ALPHAS)
    skipped[f"{sp['fold']}|{sp['cal_draw']}"] = dict(skipped_o=list(fit.skipped_o), n_E=int(fit.n_E))
    print(sp["fold"], sp["cal_draw"], len(rows), round(time.time() - t0), flush=True)
tag = f"INDIANA_{enc}_s{shard}of{nshard}"
out = os.path.join(outroot, tag)
C.write_frag(rows, out, tag, stage="C3_Indiana_o", script=os.path.abspath(__file__),
             cfg=dict(task="INDIANA_KIDNEY", enc=enc, K=10, shard=shard, nshard=nshard, folds=folds,
                      module_md5=md5, cpu_vendor=os.environ.get("CPU_VENDOR", "?"),
                      node=os.environ.get("NODE", "?"), assumption="lung n_match n/a; Indiana n_match from round3_d4_sets"),
             note=f"Indiana o sweep {tag}")
json.dump(skipped, open(os.path.join(out, "skipped_o.json"), "w"))
print("done", len(rows), round(time.time() - t0))
