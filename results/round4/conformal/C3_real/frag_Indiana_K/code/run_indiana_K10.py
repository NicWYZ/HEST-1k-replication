#!/usr/bin/env python
"""Round 4, conformal track, C3, Indiana kidney K = 10, o = 0 (fragment frag_Indiana_K).
One encoder per run. Methods pooled, hcp, one_per at alpha 0.1 and 0.2, every held-out donor unit
(fold) and every calibration draw, through round4_conf_c3 (md5 checked). Writes
<out>/c3_o_sweep__indiana_K10_<enc>.csv (fixed columns), c3_full__, c3_by_fold__, c3_K_sweep__
tables, _provenance.json, PROVENANCE.txt and cpu_vendor.txt, and fails if the row count differs from
the design (folds x draws x methods x alphas)."""
import argparse, hashlib, os, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
import round4_conf_c3 as C

MD5 = "2d8418677cf8290eec89a14c315b92cd"
K = 10
ap = argparse.ArgumentParser()
ap.add_argument("--encoder", required=True)
ap.add_argument("--out", required=True)
a = ap.parse_args()
mod = C.__file__
got = hashlib.md5(open(mod, "rb").read()).hexdigest()
assert got == MD5, (mod, got)
os.makedirs(a.out, exist_ok=True)
vendor = subprocess.run("lscpu | grep -E 'Vendor ID|Model name'; hostname", shell=True,
                        capture_output=True, text=True).stdout
open(f"{a.out}/cpu_vendor.txt", "w").write(vendor)
print(vendor, flush=True)
T = C.load_task("INDIANA_KIDNEY", a.encoder)
folds = T.fold_names()
specs = T.specs(K=K, n_cal_draws=C.N_CAL_DRAWS, folds=folds)
print("folds", len(folds), "specs", len(specs), flush=True)
assert len(folds) == 25 and len(specs) == 25 * C.N_CAL_DRAWS, (len(folds), len(specs))
rows, t0 = [], time.time()
for i, sp in enumerate(specs):
    fit = T.fit(sp)
    rows += C.o0_rows(fit, alphas=C.ALPHAS, methods=C.O0_METHODS)
    if i % 5 == 0:
        print(i, len(rows), round(time.time() - t0), "s", flush=True)
d = pd.DataFrame(rows)
exp = 25 * C.N_CAL_DRAWS * len(C.O0_METHODS) * len(C.ALPHAS)
assert len(d) == exp, (len(d), exp)
assert list(C.to_c3(rows).columns) == C.FIXED_COLS
assert (d["o"] == 0).all() and (d["K"] == K).all()
C.write_frag(rows, a.out, tag=f"indiana_K10_{a.encoder}", stage="C3_Indiana_K", script=__file__,
             cfg=dict(encoder=a.encoder, K=K, md5_module=MD5, n_folds=len(folds),
                      rows=len(d), expected_rows=exp),
             note=f"C3 Indiana K=10 o=0, {a.encoder}")
print("done", len(d), "rows", round(time.time() - t0), "s", flush=True)
