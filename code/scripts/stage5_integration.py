#!/usr/bin/env python
"""Stage 5 pilot, part 1: does STFlow load OUR cached HEST embeddings correctly?

Stage: faithful replication stage 5, fine-tuning integration; never ran (CUDA-only against a saturated GPU queue) and is kept as the unexecuted plan.

Checked before spending GPU time, because integration bugs live here and the GPU queue is 1,266 deep.

WHY REUSING OUR EMBEDDINGS IS LEGITIMATE, not a substitution: STFlow's hest_utils/encoder.py defines
only ciga_loader, ibot_uni, gigapath and gigapathslide. `uni_v1_official` is NOT an extractor -- it
appears only as (a) a path component under embed_dataroot and (b) a key in train.py's dim table,
`"uni_v1_official": 1024`. STFlow therefore consumes whatever 1024-dim embeddings sit at that path,
and our HEST-pipeline UNI v1 features are the intended input. The 1024-dim constraint is asserted.

DEPENDENCIES, measured rather than assumed (importlib.util.find_spec against env/miniforge3/envs/hest):
  present  : torch torchvision timm transformers huggingface_hub h5py anndata scanpy numpy pandas
             scipy sklearn matplotlib tqdm PIL einops mygene
  missing  : torch_geometric scprep wandb gigapath trainer
  of those, only THREE are on the uni_v1 training path:
    torch_geometric -> model/transformer.py (the denoiser)          REQUIRED
    scprep          -> data/normalize_utils.py                      REQUIRED
    wandb           -> app/flow/train.py line 3, imported at module top but used only behind
                       args.use_wandb (default False); the import must still resolve  REQUIRED
    gigapath        -> hest_utils/gigapath_slide_encoder.py only -- a different encoder  NOT NEEDED
    trainer         -> app/hest/benchmark.py; this is the LOCAL module stflow/app/hest/trainer.py,
                       not a PyPI package, so it resolves by sys.path and needs no install
An earlier version of this script installed einops (already present) and omitted scprep and wandb.

Layout bridge: STFlow reads {embed}/{task}/{encoder}/fp32/{sample}.h5; ours are one level shallower.
Symlinks supply the expected shape without duplicating 40+ GB.
"""
import os, sys, glob, json, importlib, importlib.util
import numpy as np, pandas as pd, h5py

ROOT = "/work/users/w/e/weiyang/hest_replication"
SRC, EMB = f"{ROOT}/bench_data", f"{ROOT}/embeddings"
S5 = f"{ROOT}/code/stage5/embed_shim"
TASKS = ["IDC", "READ"]
ENC_SRC, ENC_DST = "uni_v1", "uni_v1_official"

for m in ("torch_geometric", "scprep", "wandb"):
    assert importlib.util.find_spec(m) is not None, f"{m} still missing after install"
print("[deps] torch_geometric, scprep, wandb all importable", flush=True)

made = 0
for t in TASKS:
    d = f"{S5}/{t}/{ENC_DST}/fp32"
    os.makedirs(d, exist_ok=True)
    for f in sorted(glob.glob(f"{EMB}/{t}/{ENC_SRC}/*.h5")):
        link = f"{d}/{os.path.basename(f)}"
        if not os.path.islink(link) and not os.path.exists(link):
            os.symlink(f, link); made += 1
print(f"[shim] {made} symlinks under {S5}", flush=True)

sys.path.insert(0, f"{ROOT}/code/stage5/STFlow")
ds_mod = importlib.import_module("stflow.data.dataset")
print(f"[import] stflow.data.dataset OK -> "
      f"{[n for n in dir(ds_mod) if not n.startswith('_')][:10]}", flush=True)

rows = []
for t in TASKS:
    genes = json.load(open(f"{SRC}/{t}/var_50genes.json"))["genes"]
    for f in sorted(glob.glob(f"{S5}/{t}/{ENC_DST}/fp32/*.h5")):
        sid = os.path.basename(f)[:-3]
        with h5py.File(f, "r") as h:
            E, B, C = h["embeddings"][:], h["barcodes"][:], h["coords"][:]
        assert E.shape[1] == 1024, f"{sid}: dim {E.shape[1]} != the 1024 STFlow declares"
        assert E.shape[0] == B.shape[0] == C.shape[0], f"{sid}: row mismatch"
        rows.append(dict(task=t, sample_id=sid, n_spots=int(E.shape[0]), dim=int(E.shape[1]),
                         n_genes=len(genes), embed_dtype=str(E.dtype),
                         finite=bool(np.isfinite(E).all())))
        print(f"  {t}/{sid}: {E.shape[0]:6d} x {E.shape[1]}  finite={np.isfinite(E).all()}", flush=True)

d = pd.DataFrame(rows)
d.to_csv(f"{ROOT}/results/tailored/integrity/stage5_integration.csv", index=False)
print()
print(d.to_string(index=False))
print(f"\nsamples wired {len(d)} over {d.task.nunique()} tasks | all 1024-dim "
      f"{bool((d.dim==1024).all())} | all finite {bool(d.finite.all())} | "
      f"spots {int(d.n_spots.sum()):,}")
