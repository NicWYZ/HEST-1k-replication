#!/usr/bin/env python
"""Lung K sweep at o = 0 for one encoder. Usage: run_lung_k.py <encoder>. Environment: R4CONF_FRAME_ID."""
import os, sys, time, subprocess, hashlib, json
FRAG = "/work/users/w/e/weiyang/hest_replication/results/round4/conformal/C3_real/frag_Lung_K"
CORE = "/work/users/w/e/weiyang/hest_replication/results/round4/conformal/C3_real/frag_core/code"
sys.path.insert(0, CORE)
enc = sys.argv[1]
md5 = hashlib.md5(open(f"{CORE}/round4_conf_c3.py", "rb").read()).hexdigest()
assert md5 == "2d8418677cf8290eec89a14c315b92cd", md5
import round4_conf_c3 as C
import pandas as pd
import round4_conf_io as IO
IO.stamp(FRAG, track="conformal-C3", note="Lung K sweep o=0 (track Lung K)")
os.makedirs(FRAG+"/code", exist_ok=True)
cpu = subprocess.run("lscpu | grep -i 'model name\\|vendor'", shell=True, capture_output=True, text=True).stdout.strip().replace("\n", " | ")
print("cpu:", cpu, flush=True)
T = C.load_task("LUNG_XENIUM", enc)
folds = T.fold_names()
rows, counts = [], {}
t0 = time.time()
for K in C.K_GRID_LUNG:
    specs = T.specs(K, n_cal_draws=C.N_CAL_DRAWS, folds=None)
    counts[K] = len(specs)
    for sp in specs:
        fit = T.fit(sp)
        assert fit.K == K, (fit.K, K)
        rows += C.o0_rows(fit, alphas=C.ALPHAS)
    print(f"K={K} specs={len(specs)} rows={len(rows)} t={time.time()-t0:.0f}s", flush=True)
exp = sum(n * 3 * 2 for n in counts.values())
assert len(rows) == exp, (len(rows), exp)
tag = f"LUNG_{enc}"
os.environ["R4C3_CODE_CLONE"] = "/work/users/w/e/weiyang/hest_code/round4-conformal"
C.write_frag(rows, FRAG, tag, stage="C3_Lung_K", script=os.path.abspath(__file__),
             cfg=dict(task="LUNG_XENIUM", enc=enc, K=list(C.K_GRID_LUNG), alphas=list(C.ALPHAS),
                      n_cal_draws=C.N_CAL_DRAWS, folds=folds, specs_per_K=counts,
                      core_md5=md5, cpu=cpu))
with open(f"{FRAG}/PROVENANCE.txt", "a") as f:
    f.write(f"cpu_{enc}: {cpu} ; node {os.uname().nodename} ; folds {folds} ; specs_per_K {counts} ; rows {len(rows)} (expected {exp})\n")
os.makedirs("out", exist_ok=True)
for fn in os.listdir(FRAG):
    if tag in fn:
        os.system(f"cp {FRAG}/{fn} out/")
pd.DataFrame(rows).to_pickle(f"out/rows_{tag}.pkl")
json.dump(dict(counts=counts, folds=folds, expected=exp, rows=len(rows), cpu=cpu), open(f"out/meta_{tag}.json", "w"))
print("done", len(rows), time.time() - t0)
