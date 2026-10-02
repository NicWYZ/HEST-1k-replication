#!/usr/bin/env python
"""Round 4 conformal C3, Lung o sweep runner (thin wrapper over round4_conf_c3, unedited).
Usage: run_lung_o.py ENC FOLD_LO FOLD_HI OUTDIR.  One part file per (encoder, fold): all 3 calibration
draws at K = 10, o = 0 methods plus the o > 0 methods, 20 label draws, o grid (5,10,25,50,100,200),
alphas (0.1, 0.2). Idempotent: a part that exists is skipped. A sidecar JSON records the design
check of each fit (labelled-spot source, n_E, skipped o, expected row count)."""
import sys, os, json, time, hashlib, subprocess
import numpy as np, pandas as pd
import round4_conf_c3 as C
import round4_conf_io as IO
enc, lo, hi, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
K = 10
os.makedirs(f"{out}/parts", exist_ok=True)
IO.code_head = C._read_head
IO.stamp(out, track="conformal-C3-lung-o", note="Lung Xenium o sweep, K=10, abs score, 3 encoders")
T = C.load_task("LUNG_XENIUM", enc)
folds = T.fold_names()[lo:hi]
td = T.td
samples = {s["sample_id"]: s for s in td["samples"]}
fdef = {str(f["fold"]): f for f in td["folds"]["donor"]}
donor_of = T.meta["donor_of"]
for fold in folds:
    part = f"{out}/parts/part__{enc}__{fold}.csv.gz"
    if os.path.exists(part):
        print("skip", part); continue
    t0 = time.time(); rows = []; side = []
    for sp in T.specs(K=K, n_cal_draws=C.N_CAL_DRAWS, folds=[fold]):
        fit = T.fit(sp)
        # label-source check: every evaluation (and so every labelled) spot is in a core of the held-out donor
        test_cores = set(fdef[fold]["test"])
        used = set(map(str, np.unique(fit.samp_E)))
        assert used <= test_cores, (fold, used, test_cores)
        assert {donor_of[s] for s in used} == {fold}, (fold, {donor_of[s] for s in used})
        slides = {samples[s].get("slide_id") for s in test_cores}
        other_same_slide = sorted(s for s, v in samples.items() if v.get("slide_id") in slides and s not in test_cores)
        r0 = C.o0_rows(fit, alphas=C.ALPHAS)
        r1 = C.o_rows(fit, o_grid=C.O_GRID, label_draws=range(C.N_LABEL_DRAWS), alphas=C.ALPHAS)
        rows += r0 + r1
        kept = [o for o in C.O_GRID if o not in fit.skipped_o]
        side.append(dict(enc=enc, fold=fold, cal_draw=int(sp["cal_draw"]), n_E=int(fit.n_E), test_cores=sorted(test_cores),
                         labelled_from_cores_only=True, capture_slide_ids=sorted(map(str, slides)),
                         other_cores_same_capture_slide=other_same_slide, skipped_o=list(map(int, fit.skipped_o)),
                         kept_o=kept, n_rows=len(r0) + len(r1), n_rows_o0=len(r0),
                         expected_rows=6 + len(kept) * C.N_LABEL_DRAWS * 15,
                         n_T_donors=int(fit.n_T_donors), n_C=int(fit.n_C), n_C_donors=int(fit.n_C_donors)))
        print(f"{enc} {fold} cal{sp['cal_draw']} n_E={fit.n_E} rows={len(r0)+len(r1)} t={time.time()-t0:.0f}s", flush=True)
    pd.DataFrame(rows).to_csv(part, index=False)
    json.dump(side, open(f"{out}/parts/design__{enc}__{fold}.json", "w"), indent=1)
jd = f"{out}/jobs/{enc}_{lo}_{hi}"
cpu = subprocess.run("lscpu | grep -i 'vendor id\\|model name' | sed 's/  */ /g'", shell=True, capture_output=True, text=True).stdout.replace("\n", "; ")
IO.write_provenance(jd, "C3_lung_o", os.path.abspath(__file__), dict(enc=enc, lo=lo, hi=hi, K=K, o_grid=C.O_GRID, alphas=C.ALPHAS,
    label_draws=C.N_LABEL_DRAWS, cal_draws=C.N_CAL_DRAWS), extra=dict(cpu=cpu, c3_md5=IO.md5(C.__file__), folds=",".join(folds),
    frame_id=os.environ.get("R4CONF_FRAME_ID"), node_features=os.popen("scontrol show node $(hostname -s) 2>/dev/null | grep -o 'ActiveFeatures=[^ ]*'").read().strip()),
    clone=os.environ.get("R4C3_CODE_CLONE"))
print("done")
