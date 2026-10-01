
import os, sys, json, hashlib, importlib.util, glob, subprocess
import numpy as np
out = sys.argv[1]; libs = sys.argv[2]
sys.path.insert(0, libs)
os.environ["PATH"] = os.path.join(libs, "bin") + os.pathsep + os.environ["PATH"]
import importlib.metadata as md
ver = None
for d in glob.glob(os.path.join(libs, "ppi_python-*.dist-info")):
    ver = os.path.basename(d).split("-")[1].replace(".dist-info","")
info = {"ppi_python_version": ver}
try:
    from ppi_py.datasets import load_dataset
    info["loader_import"] = "ppi_py.datasets.load_dataset (package import)"
except Exception as e:
    info["loader_import_error"] = repr(e)[:300]
    p = os.path.join(libs, "ppi_py", "datasets", "datasets.py")
    spec = importlib.util.spec_from_file_location("ppi_datasets_file", p)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    load_dataset = m.load_dataset
    info["loader_import"] = "ppi_py/datasets/datasets.py loaded by path (package __init__ import failed)"
data = load_dataset(out, "census_income")
def h(p, a):
    x = hashlib.new(a)
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): x.update(b)
    return x.hexdigest()
files = {}
for p in sorted(glob.glob(os.path.join(out, "*"))):
    if os.path.isfile(p) and not os.path.basename(p).startswith(("_", "PROV")) and not p.endswith(".json"):
        files[os.path.basename(p)] = {"bytes": os.path.getsize(p), "md5": h(p, "md5"), "sha256": h(p, "sha256")}
info["files"] = files
inv = {"npz_keys": list(data.files), "arrays": {}}
for k in data.files:
    a = data[k]
    d = {"shape": list(a.shape), "dtype": str(a.dtype)}
    if a.dtype.kind in "fiu" and a.size:
        af = a.astype(float)
        if a.ndim == 1:
            d.update(min=float(np.nanmin(af)), max=float(np.nanmax(af)), mean=float(np.nanmean(af)), n_nan=int(np.isnan(af).sum()), n_unique=int(len(np.unique(a))), n_le_0=int((af <= 0).sum()))
        else:
            d["col_min"] = np.nanmin(af, 0).tolist(); d["col_max"] = np.nanmax(af, 0).tolist(); d["col_mean"] = np.nanmean(af, 0).tolist()
            d["col_n_unique"] = [int(len(np.unique(a[:, j]))) for j in range(a.shape[1])]
    elif a.dtype.kind in "OUS":
        d["first_values"] = [str(v) for v in a.ravel()[:5]]
    inv["arrays"][k] = d
info["inventory"] = inv
json.dump(info, open(os.path.join(out, "acs_fetch_raw.json"), "w"), indent=1)
print(json.dumps(info, indent=1)[:6000])
