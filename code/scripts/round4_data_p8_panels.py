#!/usr/bin/env python
"""Round 4 P8 item 3: the Xenium intersection panels with control features removed.

Source: docs/decisions/round4_data_P7_decisions.md section 2 item 10 and section 3 item 3
(proposed edit 4 of docs/round4_data_report.md). Reads P6's panel tables and writes, under
results/round4/data/P8_addendum/:
  xenium_panels_genes_only.csv       one row per set: the P6 intersection size, the number of
                                     control features dropped (in total and by family), the
                                     number of genes left, and the genes, ';'-joined
  xenium_panel_genes_only_long.csv   set_name, rank, gene for the genes only; rank is P6's rank
Control features are those whose name starts with NegControl, UnassignedCodeword or BLANK, the
rule the tracks also apply at read time. Expected: 61 dropped on five sets and 220 on IDC.
P6's files are not changed, and round 3's BREAST_XENIUM.json is not changed.

Usage, from the repository root:
  python code/scripts/round4_data_p8_panels.py
"""
import os
import re

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
P6 = "results/round4/data/P6_genes"
OUT = "results/round4/data/P8_addendum"
CONTROL = re.compile(r"^(NegControl|UnassignedCodeword|BLANK)")
FAMILIES = {"NegControlCodeword": r"^NegControlCodeword", "NegControlProbe": r"^NegControlProbe",
            "UnassignedCodeword": r"^UnassignedCodeword", "BLANK": r"^BLANK"}
EXPECTED = {"IDC": 220, "PAAD": 61, "SKCM": 61, "COAD": 61, "LUNG": 61, "BREAST_XENIUM": 61}


def main():
    panels = pd.read_csv(os.path.join(ROOT, P6, "p6_xenium_panels.csv"))
    genes = pd.read_csv(os.path.join(ROOT, P6, "p6_xenium_panel_genes.csv"))
    rows, keep_all = [], []
    for _, p in panels.iterrows():
        g = genes[genes.set_name == p.set_name].sort_values("rank")
        assert len(g) == p.panel_intersection, p.set_name
        is_ctl = g.gene.str.match(CONTROL)
        fam = {f"n_{k}": int(g.gene.str.match(v).sum()) for k, v in FAMILIES.items()}
        assert sum(fam.values()) == int(is_ctl.sum()), p.set_name
        keep = g[~is_ctl]
        keep_all.append(keep)
        rows.append(dict(set_name=p.set_name, kind=p.kind, n_samples=int(p.n_samples),
                         panel_intersection_with_controls=int(p.panel_intersection),
                         n_controls_dropped=int(is_ctl.sum()), **fam,
                         n_genes=len(keep), genes=";".join(keep.gene)))
    out = pd.DataFrame(rows)
    got = dict(zip(out.set_name, out.n_controls_dropped))
    assert got == EXPECTED, got
    os.makedirs(os.path.join(ROOT, OUT), exist_ok=True)
    out.to_csv(os.path.join(ROOT, OUT, "xenium_panels_genes_only.csv"), index=False)
    pd.concat(keep_all).to_csv(os.path.join(ROOT, OUT, "xenium_panel_genes_only_long.csv"), index=False)
    print(out.drop(columns="genes").to_string(index=False))


if __name__ == "__main__":
    main()
