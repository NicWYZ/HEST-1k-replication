#!/usr/bin/env python
"""Merge the part files of the Lung o sweep, check row counts against the design, write c3_o_sweep__LUNG.csv etc."""
import sys, os, glob, json
import pandas as pd
import round4_conf_c3 as C
out = sys.argv[1]
parts = sorted(glob.glob(f"{out}/parts/part__*.csv.gz"))
d = pd.concat([pd.read_csv(p) for p in parts], ignore_index=True)
side = [x for p in sorted(glob.glob(f"{out}/parts/design__*.json")) for x in json.load(open(p))]
exp = sum(s["expected_rows"] for s in side)
chk = dict(n_parts=len(parts), n_fits=len(side), rows=len(d), expected_rows=exp)
assert len(d) == exp, chk
assert chk["n_fits"] == 3 * 15 * 3, chk            # encoders x folds x calibration draws
rows = d.to_dict("records")
# per-cell checks: methods/alpha/o counts
g = d.groupby(["encoder", "fold", "cal_draw", "method", "alpha", "o"]).size()
bad = g[(g != 20) & (g.index.get_level_values("o") > 0)]
bad0 = g[(g != 1) & (g.index.get_level_values("o") == 0)]
assert len(bad) == 0 and len(bad0) == 0, (bad.head(), bad0.head())
assert list(C.to_c3(rows).columns) == ["task","label_set","encoder","method","score","alpha","o","K","fold","draw","coverage","width_mean","width_median","n_test","finite"]
dd = C.to_c3(rows)
assert not dd.duplicated(["encoder","method","alpha","o","fold","draw"]).any()
C.write_frag(rows, out, "LUNG", stage="C3_lung_o", script=os.path.abspath(__file__), cfg=chk, note="Lung o sweep merged tables")
json.dump(dict(chk, methods=sorted(d.method.unique()), o=sorted(d.o.unique().tolist()),
               by_method=d.groupby("method").size().to_dict(),
               skipped=[{k: s[k] for k in ("enc","fold","cal_draw","n_E","skipped_o")} for s in side if s["skipped_o"]]),
          open(f"{out}/design_check.json","w"), indent=1)
print(json.dumps(chk))
