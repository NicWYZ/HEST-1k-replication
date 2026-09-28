#!/usr/bin/env python
"""Round 4 stage P5: the LUNG_XENIUM task definition, in the A0 format with the D4 extension schema.

Source rule: docs/round4_data_plan.md section 3 P5 and section 8 items 3 and 4. The definition is
built from results/round4/data/P4_audit/donor_audit_r4.csv on the donor units that remain.
  members     the set-L rows with donor_unit_eligible True (20 TGen fibrosis TMA cores, 15 donors),
              minus NCBI865, which fails P1's subset relation and is excluded pending the oversight
              chat (the lead's ruling under plan section 5). That leaves 19 samples and 14 donors.
  not members NCBI885 and NCBI886 (whole-capture-area sections of one 17-donor TMA block), TENX118
              (donor unverifiable), TENX141 (no readable source). All four are recorded in
              expansion.not_members with the audit's reason.
Folds
  donor       leave one donor out, over the 14 donors.
  patient     6 grouped folds (sorted donors dealt round robin), exactly as round 3 D4 built them,
              used only for the `random` design's test size.
  random      n_repeats 5, test size from `patient`, crc32 seeds (the A0 rule).
  a4b_k10     round 3 A4b's design as round 3 D4 implemented it (round3_d4_sets.a4b_specs): per
              donor fold, from the remaining pool, K = 10 calibration donors are the first 10 of
              rng.permutation(sorted pool) with rng = default_rng(crc32(f"{task}|a4b_k10|{fold}|cal{draw}")),
              for draws 0, 1 and 2. The extension schema has no `a4b_k10` fold key, so the lists are
              materialised under expansion.a4b_k10, and a v2 key is proposed in the report.
Gene panel: every member shares one 541-feature var list, of which 198 are control features
(NegControlCodeword, NegControlProbe, UnassignedCodeword) and 343 are genes. target_genes records
the 343 genes as the panel; gene selection on Xenium is the panel (plan section 3 P6).

Validation uses round 3 D4's own validator and relaxed-v1 rule, imported unmodified from
code/scripts/round3_d4_task_defs.py: relaxed v1, v1 strict (expected to fail on the extension
columns), task_def_ext.schema.json as committed (expected to fail only on the row-origin enum,
which has no 'expansion_r4'), and that schema with 'expansion_r4' added to the enum (must pass).

Reads committed files only. Usage, from the repository root:
  python code/scripts/round4_data_task_lung.py
"""
from __future__ import annotations

import copy
import datetime as dt
import hashlib
import importlib.util
import json
import os
import re
import zlib

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TASK = "LUNG_XENIUM"
AUDIT = "results/round4/data/P4_audit/donor_audit_r4.csv"
INV = "results/round3/D0_inventory/hest_inventory.csv"
MORPH = "results/round4/data/P3_morphology/morphology_ext_summary.csv"
PANEL = "results/round4/data/P5_task/panel_job/lung_genes_by_sample.json"
V1 = "results/round3/task_defs/task_def.schema.json"
EXT = "results/round3/D4_expansion/task_defs/task_def_ext.schema.json"
D4TD = "code/scripts/round3_d4_task_defs.py"
OUT = "results/round4/data/P5_task"
PENDING = {"NCBI865": "fails P1's subset relation (patch barcode 051x019 has no expression row); "
                      "excluded from set L's task membership pending the oversight chat"}
A4B_K, A4B_DRAWS, N_PATIENT_GROUPS = 10, 3, 6
CONTROL = re.compile(r"^(NegControlCodeword|NegControlProbe|UnassignedCodeword)")


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def load_d4():
    spec = importlib.util.spec_from_file_location("d4td", os.path.join(ROOT, D4TD))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)          # module level holds constants and functions only
    return m


def main():
    d4 = load_d4()
    aud = pd.read_csv(os.path.join(ROOT, AUDIT), dtype=str, keep_default_na=False)
    L = aud[aud.row_origin == "expansion_r4"].copy()
    assert len(L) == 24, len(L)
    inv = pd.read_csv(os.path.join(ROOT, INV), low_memory=False).set_index("id")
    mo = pd.read_csv(os.path.join(ROOT, MORPH))
    mo = mo[mo.set_name == "lung_xenium"].set_index("sample_id")
    assert len(mo) == 24
    genes = json.load(open(os.path.join(ROOT, PANEL)))

    elig = L[L.donor_unit_eligible == "True"]
    members = elig[~elig.sample_id.isin(PENDING)].sort_values("sample_id")
    not_members = L[~L.sample_id.isin(members.sample_id)].sort_values("sample_id")
    assert len(elig) == 20 and elig.donor_unit_id.nunique() == 15
    assert len(members) == 19 and members.donor_unit_id.nunique() == 14

    panels = {tuple(genes[s]) for s in members.sample_id}
    assert len(panels) == 1, "members do not share one var list"
    feats = list(next(iter(panels)))
    gene_list = [g for g in feats if not CONTROL.match(g)]
    controls = [g for g in feats if CONTROL.match(g)]

    def resolution_group(px):
        return str(pd.cut([px], d4.BIN_EDGES, labels=d4.BIN_LABELS, right=True)[0])

    samples, slide_of = [], {}
    for _, r in members.iterrows():
        sid = r.sample_id
        m = mo.loc[sid]
        px = float(r.pixel_size_um_source or r.pixel_size_um_estimated)
        slide_of[sid] = r.source_slide_id
        samples.append(dict(
            sample_id=sid, donor_id=r.donor_unit_id, hest_patient=inv.loc[sid, "patient_label"],
            donor_label_status=r.donor_label_status, lab=r.lab, lab_label_status=r.lab_label_status,
            session=None, resolution_group=resolution_group(px), pixel_size_um=px,
            resolution_uncertain=bool(inv.loc[sid, "resolution_uncertain"]),
            n_spots=int(m.n_patched_spots), source=r.lab.split(",")[0],
            population="tgen_lung_fibrosis_tma", instrument_generation=r.instrument_generation,
            preservation=r.preservation, region=r.region, disease=r.disease,
            donor_label_status_row_origin="expansion_r4",
            donor_label_status_other_origin=None, donor_id_other_origin=None,
            pixel_size_um_embedded=float(r.pixel_size_um_embedded),
            magnification_hest=r.magnification_hest, scanner=r.scanner,
            n_expr_spots=int(m.n_spots_expression), n_patch_spots=int(m.n_patched_spots),
            unpatched_fraction=float(m.unpatched_fraction), excluded_from_donor_units=False,
            in_benchmark=bool(inv.loc[sid, "in_benchmark"]),
            hest_dataset_title=inv.loc[sid, "dataset_title"]))
        if r.resolution_uncertain_rederived:
            samples[-1]["resolution_uncertain_rederived"] = r.resolution_uncertain_rederived

    samples_of_unit = {}
    for s in samples:
        samples_of_unit.setdefault(s["donor_id"], []).append(s["sample_id"])
    for u in samples_of_unit:
        samples_of_unit[u].sort()
    donor = d4.loo_folds(samples_of_unit)
    patient = d4.fold_list(samples_of_unit, d4.grouped_folds(samples_of_unit, N_PATIENT_GROUPS))

    donor_of = {s["sample_id"]: s["donor_id"] for s in samples}
    a4b = []
    for fd in donor:
        units = sorted({donor_of[s] for s in fd["train"]})
        assert len(units) > A4B_K, (fd["fold"], len(units))
        for draw in range(A4B_DRAWS):
            rng = np.random.default_rng(zlib.crc32(f"{TASK}|a4b_k10|{fd['fold']}|cal{draw}".encode()))
            pick = sorted(rng.permutation(np.array(units, dtype=object))[:A4B_K].tolist())
            a4b.append(dict(fold=str(fd["fold"]), cal_draw=draw, n_pool_donors=len(units),
                            calibration_donors=pick,
                            training_donors=sorted(set(units) - set(pick)),
                            calibration_samples=sorted(s for s in fd["train"] if donor_of[s] in pick),
                            training_samples=sorted(s for s in fd["train"] if donor_of[s] not in pick)))

    now = dt.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
    td = dict(
        task_def_version=1, task=TASK, label_set="audited", source="hest_ext",
        st_technology="Xenium", repo_root_relative=True,
        paths=dict(adata="hest_ext/lung_xenium/st/{sample_id}.h5ad",
                   patches="hest_ext/lung_xenium/patches/{sample_id}.h5",
                   embeddings="embeddings_ext/lung_xenium/{encoder}/{sample_id}.h5",
                   target_genes="the panel; see target_genes"),
        target_genes=dict(list=gene_list, n=len(gene_list),
                          selection=(f"THE PANEL. Every member shares one {len(feats)}-feature var list, "
                                     f"of which {len(controls)} are control features (NegControlCodeword, "
                                     "NegControlProbe, UnassignedCodeword) and are excluded here; the "
                                     f"remaining {len(gene_list)} genes are the panel. On Xenium, gene "
                                     "selection is the panel (plan section 3 P6)."),
                          selection_used_test_spots=False),
        samples=samples,
        flags=dict(patient_labels_unreliable=True, same_specimen_pairs=True,
                   idc_attribution_unresolved=False),
        folds=dict(patient=patient, donor=donor, slide_out=[],
                   random=dict(n_repeats=5, test_size_from_fold="patient", seed_source="crc32")),
        provenance=dict(generated_by="code/scripts/round4_data_task_lung.py", generated_at=now,
                        commit="recorded by the lead's commit, not read here",
                        script_md5=md5(os.path.abspath(__file__)),
                        inputs=[f"{p} md5 {md5(os.path.join(ROOT, p))}" for p in
                                (AUDIT, INV, MORPH, PANEL, V1, EXT, D4TD)],
                        pythonhashseed=os.environ.get("PYTHONHASHSEED", "unset")),
        expansion=dict(
            set_name="lung_xenium", layout="hest_1k", arm="lung_donor_set",
            purpose=("Round 4 P5. The third multi-donor task: 19 TGen fibrosis TMA cores from 14 "
                     "donors, one laboratory, one instrument (XETG00048), one software generation, "
                     "pixel size 0.2125 um, FFPE 5 um sections."),
            donor_grouping_origin="expansion_r4 rows of donor_audit_r4.csv",
            spots="patched spots only",
            members_n_samples=len(samples), members_n_donors=len(samples_of_unit),
            pending_oversight=[dict(sample_id=k, reason=v, donor_id=L.set_index("sample_id").loc[k, "donor_unit_id"])
                               for k, v in PENDING.items()],
            not_members=[dict(sample_id=r.sample_id, donor_label_status=r.donor_label_status,
                              reason=(r.multi_donor_detail if r.sample_id in ("NCBI885", "NCBI886")
                                      else (r.notes or r.donor_statement or r.contradictions))[:300])
                         for _, r in not_members[~not_members.sample_id.isin(PENDING)].iterrows()],
            source_slide_id=slide_of,
            slides_shared_across_donors={sl: sorted({donor_of[s] for s in ss})
                                         for sl, ss in pd.Series(slide_of).groupby(pd.Series(slide_of)).groups.items()},
            panel=dict(n_features=len(feats), n_control_features=len(controls), n_genes=len(gene_list)),
            a4b_k10=dict(K=A4B_K, draws=A4B_DRAWS,
                         seed_rule="default_rng(zlib.crc32(f'{task}|a4b_k10|{fold}|cal{draw}')), first K of permutation(sorted pool)",
                         folds=a4b),
            difference_list_for_donor=["donor", "disease (IPF, control, sarcoidosis, IPAF, ILD not specified, cHP, CTD-ILD)",
                                       "region (less- or more-affected section)", "TMA core and slide"],
            held_fixed=["laboratory (TGen, Banovich lab)", "instrument (XETG00048)",
                        "instrument software 1.1.2.4 / xenium-1.1.0.2", "panel (343 genes)",
                        "preservation (FFPE, 5 um)", "pixel size 0.2125 um"],
            designs_run=["random", "donor (leave one donor out)", "A4b K=10 (13 in pool, 10 calibration, 3 training)"]),
    )

    # ---- validation with D4's own validator and relaxed-v1 rule
    v1 = json.load(open(os.path.join(ROOT, V1)))
    ext = json.load(open(os.path.join(ROOT, EXT)))

    def relaxed(node):
        if isinstance(node, dict):
            return {k: relaxed(v) for k, v in node.items() if k != "additionalProperties"}
        if isinstance(node, list):
            return [relaxed(v) for v in node]
        return node

    # The round-3 extension schema enumerates donor_label_status_row_origin as benchmark_r2 and
    # expansion_d3. Round-3 files are not edited; ext_r4 is the committed schema with exactly one
    # change, 'expansion_r4' appended to that enum, and is proposed as part of v2 in the report.
    ext_r4, n_enum = copy.deepcopy(ext), [0]

    def add_origin(node):
        if isinstance(node, dict):
            if node.get("enum") == ["benchmark_r2", "expansion_d3"]:
                node["enum"] = node["enum"] + ["expansion_r4"]
                n_enum[0] += 1
            for v in node.values():
                add_origin(v)
        elif isinstance(node, list):
            for v in node:
                add_origin(v)
    add_origin(ext_r4)
    assert n_enum[0] >= 1, "row-origin enum not found in the extension schema"

    errs = {tag: d4.validate(td, sch) for tag, sch in
            (("v1_relaxed", relaxed(v1)), ("v1_strict", v1), ("ext", ext), ("ext_r4", ext_r4))}
    ids = [s["sample_id"] for s in samples]
    checks = dict(
        task_def=TASK, n_samples=len(ids), n_samples_unique=len(set(ids)),
        n_donor_units=len(samples_of_unit), n_folds_donor=len(donor), n_folds_patient=len(patient),
        n_a4b_rows=len(a4b), a4b_min_training_donors=min(len(a["training_donors"]) for a in a4b),
        panel_n_features=len(feats), panel_n_genes=len(gene_list),
        folds_cover_every_sample=all(sorted(set(f["train"]) | set(f["test"])) == sorted(ids)
                                     for key in ("patient", "donor") for f in td["folds"][key]),
        folds_disjoint=all(not (set(f["train"]) & set(f["test"]))
                           for key in ("patient", "donor") for f in td["folds"][key]),
        a4b_disjoint=all(not (set(a["calibration_donors"]) & set(a["training_donors"])) for a in a4b),
        v1_relaxed_error="; ".join(errs["v1_relaxed"][:3]),
        v1_strict_error="; ".join(errs["v1_strict"][:3]),
        ext_schema_error="; ".join(errs["ext"][:3]),
        ext_r4_enum_edits=n_enum[0],
        ext_r4_schema_error="; ".join(errs["ext_r4"][:3]))
    os.makedirs(os.path.join(ROOT, OUT), exist_ok=True)
    pd.DataFrame([checks]).to_csv(os.path.join(ROOT, OUT, "p5_validation.csv"), index=False)
    with open(os.path.join(ROOT, OUT, f"{TASK}.json"), "w") as f:
        json.dump(td, f, indent=1)
        f.write("\n")
    print(json.dumps({k: v for k, v in checks.items() if k != "v1_strict_error"}, indent=1))
    assert not checks["v1_relaxed_error"], checks["v1_relaxed_error"]
    assert all("expansion_r4" in e for e in errs["ext"]), errs["ext"]
    assert not checks["ext_r4_schema_error"], checks["ext_r4_schema_error"]
    assert checks["folds_cover_every_sample"] and checks["folds_disjoint"] and checks["a4b_disjoint"]


if __name__ == "__main__":
    main()
