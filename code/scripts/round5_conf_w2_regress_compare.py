import glob, sys, json, pandas as pd, numpy as np
old, new, out = sys.argv[1], sys.argv[2], sys.argv[3]
res = []
for des in ("fixedN21", "poissonNmean25"):
    a = pd.concat([pd.read_csv(f) for f in glob.glob(f"{old}/{des}/*.csv") if "rows" in f])
    b = pd.concat([pd.read_csv(f) for f in glob.glob(f"{new}/{des}/*.csv") if "rows" in f])
    key = ["chunk", "experiment", "alpha", "o", "method"]
    b_sh = b[b.o.isin(a.o.unique())]
    m = a.merge(b_sh, on=key, how="outer", suffixes=("_old", "_new"), indicator=True)
    both = m[m._merge == "both"]
    w = both.width_old.astype(float); v = both.width_new.astype(float)
    d = (w - v).abs(); d[np.isinf(w) & np.isinf(v)] = 0
    res.append(dict(design=des, rows_old=len(a), rows_new_shared_o=len(b_sh), matched=len(both),
                    only_old=int((m._merge == "left_only").sum()), only_new=int((m._merge == "right_only").sum()),
                    covered_mismatch=int((both.covered_old != both.covered_new).sum()),
                    finite_mismatch=int((both.finite_old != both.finite_new).sum()),
                    max_abs_width_diff=float(d.max()), new_o_values=sorted(int(x) for x in b.o.unique()),
                    new_rows_total=len(b)))
r = pd.DataFrame(res); r.to_csv(out, index=False); print(r.to_string())
ok = (r.only_old == 0).all() and (r.only_new == 0).all() and (r.covered_mismatch == 0).all() and (r.finite_mismatch == 0).all() and (r.max_abs_width_diff == 0).all()
print("PASS" if ok else "FAIL"); sys.exit(0 if ok else 3)
