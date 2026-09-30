#!/usr/bin/env python
"""Round 4 stage P8 item 1: LUNG_XENIUM.json rebuilt with NCBI865 reinstated.

Source: docs/decisions/round4_data_P7_decisions.md section 2 item 1 and section 3 item 1,
transcribed in docs/round4_data_plan.md section 9. This script supersedes nothing: P5's builder,
code/scripts/round4_data_task_lung.py, stays as it ran, and the 19-sample file it wrote is kept as
results/round4/data/P5_task/LUNG_XENIUM__19_pre_P8.json.

Changes from P5, and only these:
  members     all 20 donor-unit-eligible TGen fibrosis TMA cores, 15 donors. NCBI865 is a member,
              with its one patch barcode that has no expression row, 051x019, listed in the
              top-level `dropped_patch_barcodes`. The subset relation after the drop is ASSERTED from
              results/round4/data/P8_addendum/p8_subset_after_drop.csv, which the Longleaf check
              wrote by reading every member's patch and expression files; it is not relaxed. The
              embedding row for a dropped barcode is excluded by barcode at read time; the embedding
              files are not rewritten.
  counts      n_patch_spots and n_spots are the patch count after the drop (asserted equal to P3's
              n_patched_spots on every member).
  folds       donor LOO over 15 donors; patient re-grouped over 15 donors into the same 6 groups;
              random unchanged in its parameters (5 repeats, test size from `patient`, crc32);
              a4b_k10 regenerated with the same seed rule over 15 folds and 3 draws. The a4b_k10
              lists are canonical under folds.a4b_k10 (schema v2) and are also kept, identical and
              asserted equal, under expansion.a4b_k10, where the 19-sample file had them.
  slide_id    per sample (schema v2); expansion.source_slide_id is kept.
  core size   each sample's core diameter from its GEO title (3 mm or 5 mm), recorded under
              expansion.core_diameter_mm_source and added to the donor difference list.
Validation: relaxed v1, v1 strict (fails by design), the committed extension schema v1 (fails on the
v2 additions, by design) and task_def_ext.schema.v2.json (must pass), with round 3 D4's own
validator imported unmodified.

Reads committed files only. Usage, from the repository root:
  python code/scripts/round4_data_p8_task_lung.py
"""
from __future__ import annotations

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
SUBSET = "results/round4/data/P8_addendum/p8_subset_after_drop.csv"
V1 = "results/round3/task_defs/task_def.schema.json"
EXT = "results/round3/D4_expansion/task_defs/task_def_ext.schema.json"
EXT2 = "results/round3/D4_expansion/task_defs/task_def_ext.schema.v2.json"
D4TD = "code/scripts/round3_d4_task_defs.py"
OUT = "results/round4/data/P5_task"
DROPPED = {"NCBI865": ["051x019"]}
A4B_K, A4B_DRAWS, N_PATIENT_GROUPS = 10, 3, 6
CONTROL = re.compile(r"^(NegControlCodeword|NegControlProbe|UnassignedCodeword)")


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def load_d4():
    spec = importlib.util.spec_from_file_location("d4td", os.path.join(ROOT, D4TD))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)          # module level holds constants and functions only
    return m


def relaxed(node):
    if isinstance(node, dict):
        return {k: relaxed(v) for k, v in node.items() if k != "additionalProperties"}
    if isinstance(node, list):
        return [relaxed(v) for v in node]
    return node


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
    sub = pd.read_csv(os.path.join(ROOT, SUBSET)).set_index("sample_id")

    members = L[L.donor_unit_eligible == "True"].sort_values("sample_id")
    not_members = L[~L.sample_id.isin(members.sample_id)].sort_values("sample_id")
    assert len(members) == 20 and members.donor_unit_id.nunique() == 15

    # the subset relation after the drop, asserted on every member from the Longleaf check
    assert sorted(sub.index) == sorted(members.sample_id), "subset check does not cover the members"
    assert sub.subset_holds_after_drop.all() and (sub.n_missing_after_drop == 0).all()
    for sid, row in sub.iterrows():
        listed = DROPPED.get(sid, [])
        assert row.n_dropped == len(listed), sid
        assert (str(row.dropped) if row.n_dropped else "") == ";".join(sorted(listed)), sid
        assert int(row.n_patches_after_drop) == int(mo.loc[sid, "n_patched_spots"]), sid
    assert set(DROPPED) <= set(sub.index)

    panels = {tuple(genes[s]) for s in members.sample_id}
    assert len(panels) == 1, "members do not share one var list"
    feats = list(next(iter(panels)))
    gene_list = [g for g in feats if not CONTROL.match(g)]
    controls = [g for g in feats if CONTROL.match(g)]

    def resolution_group(px):
        return str(pd.cut([px], d4.BIN_EDGES, labels=d4.BIN_LABELS, right=True)[0])

    samples, slide_of, core_of = [], {}, {}
    for _, r in members.iterrows():
        sid = r.sample_id
        m = mo.loc[sid]
        n_patch = int(sub.loc[sid, "n_patches_after_drop"])
        px = float(r.pixel_size_um_source or r.pixel_size_um_estimated)
        slide_of[sid] = r.source_slide_id
        cm = re.findall(r"_(\d)mm'", r.donor_statement)
        assert len(cm) == 1, (sid, cm)
        core_of[sid] = int(cm[0])
        samples.append(dict(
            sample_id=sid, donor_id=r.donor_unit_id, hest_patient=inv.loc[sid, "patient_label"],
            donor_label_status=r.donor_label_status, lab=r.lab, lab_label_status=r.lab_label_status,
            session=None, resolution_group=resolution_group(px), pixel_size_um=px,
            resolution_uncertain=bool(inv.loc[sid, "resolution_uncertain"]),
            n_spots=n_patch, source=r.lab.split(",")[0],
            population="tgen_lung_fibrosis_tma", instrument_generation=r.instrument_generation,
            preservation=r.preservation, region=r.region, disease=r.disease,
            donor_label_status_row_origin="expansion_r4",
            donor_label_status_other_origin=None, donor_id_other_origin=None,
            pixel_size_um_embedded=float(r.pixel_size_um_embedded),
            magnification_hest=r.magnification_hest, scanner=r.scanner,
            n_expr_spots=int(m.n_spots_expression), n_patch_spots=n_patch,
            unpatched_fraction=float(m.unpatched_fraction), excluded_from_donor_units=False,
            in_benchmark=bool(inv.loc[sid, "in_benchmark"]),
            hest_dataset_title=inv.loc[sid, "dataset_title"],
            slide_id=r.source_slide_id))
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
    n_pool = sorted({a["n_pool_donors"] for a in a4b})
    n_train = min(len(a["training_donors"]) for a in a4b)

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
        dropped_patch_barcodes=DROPPED,
        flags=dict(patient_labels_unreliable=True, same_specimen_pairs=True,
                   idc_attribution_unresolved=False),
        folds=dict(patient=patient, donor=donor, slide_out=[],
                   random=dict(n_repeats=5, test_size_from_fold="patient", seed_source="crc32"),
                   a4b_k10=a4b),
        provenance=dict(generated_by="code/scripts/round4_data_p8_task_lung.py", generated_at=now,
                        commit="recorded by the lead's commit, not read here",
                        script_md5=md5(os.path.abspath(__file__)),
                        inputs=[f"{p} md5 {md5(os.path.join(ROOT, p))}" for p in
                                (AUDIT, INV, MORPH, PANEL, SUBSET, V1, EXT, EXT2, D4TD)],
                        pythonhashseed=os.environ.get("PYTHONHASHSEED", "unset")),
        expansion=dict(
            set_name="lung_xenium", layout="hest_1k", arm="lung_donor_set",
            supersedes="results/round4/data/P5_task/LUNG_XENIUM__19_pre_P8.json (P5, 19 samples, 14 donors)",
            purpose=(f"Round 4 P5, rebuilt in P8. The third multi-donor task: {len(samples)} TGen "
                     f"fibrosis TMA cores from {len(samples_of_unit)} donors, one laboratory, one "
                     "instrument (XETG00048), one software generation, pixel size 0.2125 um, FFPE 5 um "
                     "sections; disease not fixed; slides carry two to five donors."),
            donor_grouping_origin="expansion_r4 rows of donor_audit_r4.csv",
            spots="patched spots only, after dropped_patch_barcodes",
            members_n_samples=len(samples), members_n_donors=len(samples_of_unit),
            reinstated=[dict(sample_id=k, donor_id=donor_of[k], dropped_patch_barcodes=v,
                             decision="docs/decisions/round4_data_P7_decisions.md section 2 item 1",
                             read_rule=("drop these barcodes from the patch file and exclude the "
                                        "matching embedding rows by barcode at read time; the subset "
                                        "relation holds after the drop"))
                        for k, v in DROPPED.items()],
            not_members=[dict(sample_id=r.sample_id, donor_label_status=r.donor_label_status,
                              reason=(r.multi_donor_detail if r.sample_id in ("NCBI885", "NCBI886")
                                      else (r.notes or r.donor_statement or r.contradictions))[:300])
                         for _, r in not_members.iterrows()],
            source_slide_id=slide_of,
            slides_shared_across_donors={sl: sorted({donor_of[s] for s in ss})
                                         for sl, ss in pd.Series(slide_of).groupby(pd.Series(slide_of)).groups.items()},
            core_diameter_mm_source=core_of,
            panel=dict(n_features=len(feats), n_control_features=len(controls), n_genes=len(gene_list)),
            a4b_k10=dict(K=A4B_K, draws=A4B_DRAWS,
                         seed_rule="default_rng(zlib.crc32(f'{task}|a4b_k10|{fold}|cal{draw}')), first K of permutation(sorted pool)",
                         canonical="folds.a4b_k10 (schema v2); this copy is identical",
                         folds=a4b),
            difference_list_for_donor=["donor", "disease (IPF, control, sarcoidosis, IPAF, ILD not specified, cHP, CTD-ILD)",
                                       "region (less- or more-affected section)", "TMA core and slide",
                                       "core diameter (3 mm or 5 mm, from the GEO title)"],
            held_fixed=["laboratory (TGen, Banovich lab)", "instrument (XETG00048)",
                        "instrument software 1.1.2.4 / xenium-1.1.0.2", f"panel ({len(gene_list)} genes)",
                        "preservation (FFPE, 5 um)", "pixel size 0.2125 um"],
            designs_run=["random", "donor (leave one donor out)",
                         f"A4b K=10 ({n_pool[0]} in pool, 10 calibration, {n_train} training)"]),
    )
    assert td["folds"]["a4b_k10"] == td["expansion"]["a4b_k10"]["folds"]

    # ---- validation with D4's own validator
    v1 = json.load(open(os.path.join(ROOT, V1)))
    ext = json.load(open(os.path.join(ROOT, EXT)))
    ext2 = json.load(open(os.path.join(ROOT, EXT2)))
    errs = {tag: d4.validate(td, sch) for tag, sch in
            (("v1_relaxed", relaxed(v1)), ("v1_strict", v1), ("ext", ext), ("ext_v2", ext2))}
    ids = [s["sample_id"] for s in samples]
    checks = dict(
        task_def=TASK, n_samples=len(ids), n_samples_unique=len(set(ids)),
        n_donor_units=len(samples_of_unit), n_folds_donor=len(donor), n_folds_patient=len(patient),
        n_a4b_rows=len(a4b), a4b_n_pool_donors=";".join(map(str, n_pool)),
        a4b_min_training_donors=n_train,
        panel_n_features=len(feats), panel_n_genes=len(gene_list),
        n_dropped_patch_barcodes=sum(len(v) for v in DROPPED.values()),
        subset_holds_after_drop_all=bool(sub.subset_holds_after_drop.all()),
        folds_cover_every_sample=all(sorted(set(f["train"]) | set(f["test"])) == sorted(ids)
                                     for key in ("patient", "donor") for f in td["folds"][key]),
        folds_disjoint=all(not (set(f["train"]) & set(f["test"]))
                           for key in ("patient", "donor") for f in td["folds"][key]),
        a4b_disjoint=all(not (set(a["calibration_donors"]) & set(a["training_donors"])) for a in a4b),
        a4b_copy_identical=True,
        v1_relaxed_error="; ".join(errs["v1_relaxed"][:3]),
        v1_strict_error="; ".join(errs["v1_strict"][:3]),
        ext_schema_error="; ".join(errs["ext"][:3]),
        ext_v2_schema_error="; ".join(errs["ext_v2"][:3]))
    os.makedirs(os.path.join(ROOT, OUT), exist_ok=True)
    pd.DataFrame([checks]).to_csv(os.path.join(ROOT, OUT, "p5_validation.csv"), index=False)
    with open(os.path.join(ROOT, OUT, f"{TASK}.json"), "w") as f:
        json.dump(td, f, indent=1)
        f.write("\n")
    print(json.dumps({k: v for k, v in checks.items() if k not in ("v1_strict_error", "ext_schema_error")},
                     indent=1))
    assert not checks["v1_relaxed_error"], checks["v1_relaxed_error"]
    assert errs["ext"], "the v1 extension schema should reject the v2 additions"
    assert not checks["ext_v2_schema_error"], checks["ext_v2_schema_error"]
    assert (len(ids), len(samples_of_unit), len(donor), len(a4b), n_train) == (20, 15, 15, 45, 4)
    assert checks["folds_cover_every_sample"] and checks["folds_disjoint"] and checks["a4b_disjoint"]


if __name__ == "__main__":
    main()
