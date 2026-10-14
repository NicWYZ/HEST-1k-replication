#!/usr/bin/env python
"""Round 7 federated learning track, F3.00: the corrected center grouping (plan amendment A4).

Reads results/round7/fedlearn/F2_inventory/inventory.csv from the code clone (committed at the F2
gate) and the committed task definitions. Merges vendor spellings, keeps each unresolved study as
its own source, and adds a source label, a source kind (lab or study) and a study label. Writes,
into its working directory (results/round7/fedlearn/F3_00_grouping/ in the project tree):
  sources_by_group.csv   one row per organ and technology, with the sources on disk
  sample_sources.csv     one row per sample on disk with its source
Reads only committed tables; no data file is opened.
"""
import argparse
import json
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import round7_fedlearn_common as C  # noqa: E402

MERGE = {
    "10x Genomics Inc. (vendor product page)": "10x Genomics Inc.",
    "Translational Genomics Research Institute (TGen)": "Translational Genomics Research Institute",
}


def source_of(lab):
    lab = (lab or "").strip()
    if lab == "":
        return "(no lab recorded)", "unresolved"
    if lab.startswith("unresolved:"):
        return "study: " + lab.split("unresolved:", 1)[1].strip(), "study"
    return MERGE.get(lab, lab), "lab"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame-id", required=True)
    ap.add_argument("--clone", default=C.CLONE)
    a = ap.parse_args()
    out = os.getcwd()
    C.stamp_dir(out, a.frame_id, note="round 7 fedlearn F3.00 corrected grouping")
    inv = pd.read_csv(os.path.join(a.clone, "results/round7/fedlearn/F2_inventory/inventory.csv"),
                      dtype=str, keep_default_na=False)
    rows = []
    for r in inv.itertuples():
        src, kind = source_of(r.lab_provisional)
        rows.append(dict(sample_id=r.sample_id, organ=r.organ, st_technology=r.st_technology,
                         lab_provisional=r.lab_provisional, source=src, source_kind=kind,
                         study=r.dataset_title, disease_state=r.disease_state,
                         donor_key_provisional=r.donor_key_provisional, task_donor=r.task_donor,
                         tasks=r.tasks, has_expression=r.has_expression, has_embeddings=r.has_embeddings,
                         encoders_with_embeddings=r.encoders_with_embeddings,
                         n_spots_expression=r.n_spots_expression, n_genes_expression=r.n_genes_expression))
    S = pd.DataFrame(rows)
    G = []
    for (o, t), g in S.groupby(["organ", "st_technology"], sort=True):
        ge = g[(g.has_expression == "True") & (g.has_embeddings == "True")]
        det = []
        for src, h in ge.groupby("source", sort=True):
            donors = set(h.task_donor) - {""} or set(h.donor_key_provisional) - {""}
            det.append(f"{src} [{h.source_kind.iloc[0]}] (samples={len(h)}, donor_units={len(donors)}, "
                       f"disease={';'.join(sorted(set(h.disease_state)))}, studies={h.study.nunique()})")
        resolved = sorted(set(ge.source) - {"(no lab recorded)"})
        G.append(dict(organ=o, st_technology=t, n_samples_on_disk=len(g),
                      n_samples_with_expression_and_embeddings=len(ge),
                      n_sources_with_expression_and_embeddings=len(resolved),
                      n_labs=int((ge.drop_duplicates("source").source_kind == "lab").sum()),
                      n_studies_as_sources=int((ge.drop_duplicates("source").source_kind == "study").sum()),
                      min_samples_per_source=int(ge.groupby("source").size().min()) if len(ge) else 0,
                      two_plus_sources=len(resolved) >= 2,
                      tasks=";".join(sorted({x for v in g.tasks for x in v.split(";") if x})),
                      sources="; ".join(det)))
    G = pd.DataFrame(G)
    G.to_csv("sources_by_group.csv", index=False)
    S.to_csv("sample_sources.csv", index=False)
    summary = dict(n_samples=len(S), n_groups=len(G), n_groups_two_plus_sources=int(G.two_plus_sources.sum()),
                   groups_two_plus_sources=[f"{r.organ} {r.st_technology}" for r in G[G.two_plus_sources].itertuples()],
                   merged_spellings=MERGE)
    json.dump(summary, open("f300_summary.json", "w"), indent=2)
    C.write_provenance(out, "F3.00", a.frame_id, " ".join([sys.executable] + sys.argv), dict(merge=MERGE),
                       [os.path.abspath(__file__), C.__file__])
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
