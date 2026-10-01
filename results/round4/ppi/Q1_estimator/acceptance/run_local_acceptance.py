"""Local runner for round4_ppi_q1_acceptance.py (plan section 12.1). The round-3 harness
imports packages absent on this machine (scanpy and others) at module level; the acceptance
uses only round3_b1_ppi.load_suff, draw_L, group_mask and NL_SETTINGS, which need none of
them, so missing packages are replaced by empty stub modules before the import."""
import sys, types, importlib
missing = []
for m in ["scanpy", "anndata", "h5py", "sklearn", "sklearn.decomposition", "sklearn.linear_model",
          "sklearn.preprocessing", "torch"]:
    try:
        importlib.import_module(m)
    except Exception:
        mod = types.ModuleType(m); mod.__getattr__ = lambda name: types.SimpleNamespace()
        sys.modules[m] = mod; missing.append(m)
print("stubbed:", missing)
sys.path.insert(0, "code/scripts")
import round4_ppi_q1_acceptance as A
sys.exit(A.main(sys.argv[1:]))
