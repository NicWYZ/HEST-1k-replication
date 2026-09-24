#!/usr/bin/env python
"""Round 3, stage D4 step 0: task definitions for the expansion sets.

Stage: D4 (round3_execution_plan.md section 13.7, transcribing docs/decisions/round3_A3_decisions.md
section 7). Written FIRST, before any D4 arm runs, as section 13.7 requires.

WHAT THIS WRITES, under results/round3/D4_expansion/task_defs/:

  CCRCC_hest_layout.json  the 24 CCRCC benchmark samples on HEST-1k-layout inputs, for the
                          layout anchor of section 13.7.1. Its `samples`, `folds` and
                          `target_genes` are COPIED VERBATIM from the committed benchmark file
                          results/round3/task_defs/CCRCC.json, because the anchor's whole point
                          is that nothing but the layout changes: same donor grouping (A1's,
                          which is the benchmark_r2 row of donor_audit_r3.csv), same fold
                          membership, same 50 target genes, same seeds. Only `paths` differ.
  INDIANA_KIDNEY.json     the 23 Indiana atlas samples plus the three single-donor papilla
                          samples, 26 samples and 25 donor units (NCBI701 and NCBI702 are one
                          participant). NCBI563 to NCBI566 are NOT members: section 13.7
                          excludes the four contradicted papilla samples from any donor unit.
  KIDNEY_POP54.json       the 54-sample kidney analysis set, carrying a per-sample `population`
                          (cordeliers_ccRCC, 24; indiana_nontumour, 30) and a `population_out`
                          fold list with both directions. The four contradicted papilla samples
                          ARE members here, because section 13.10 item 5 keeps them as test
                          spots and only bars them from donor units; the flag
                          `excluded_from_donor_units` marks them and the analysis script honours
                          it.
  BREAST_XENIUM.json      the 18 breast Xenium samples, 15 donor groups.

SCHEMA. These are task_def_version 1 files in the A0 format, with the extra columns section 13.7
requires (lab, source, population, instrument_generation, preservation, region, the audit
statuses, and the unpatched fraction per sample). results/round3/task_defs/task_def.schema.json
sets `additionalProperties: false`, so the extra columns are a documented EXTENSION rather than a
silent schema break: task_def_ext.schema.json in this directory is schema v1 with the new
properties added, every v1 requirement kept, and the expansion files are validated against BOTH
(v1 with additionalProperties relaxed, and the extension as written).

GROUPING. `donor_id` comes from the `expansion_d3` rows of results/round3/D3_audit/donor_audit_r3.csv
for the three expansion sets, which is section 13.10 item 2's instruction, and from the
`benchmark_r2` rows for CCRCC_hest_layout, which is the same instruction read the other way: that
file is a benchmark task. Where the two origins disagree on a sample, both statuses are recorded
(`donor_label_status` from the row origin this file uses, `donor_label_status_other_origin` from
the other) and nothing is chosen between them.

SPOTS. Every expansion arm uses patched spots only (section 13.2 item 3, the subset relation), so
`n_spots` is the number of spots that have BOTH a HEST-1k patch and expression, `n_expr_spots` is
the expression file's own count, and `unpatched_fraction` is 1 - n_spots/n_expr_spots. The patch
barcode list being a subset of the expression barcode list is asserted per sample, not assumed.

Usage: round3_d4_task_defs.py
"""
import json
import os
import subprocess
import sys
import time
import zlib

import anndata as ad
import h5py
import numpy as np
import pandas as pd

ROOT = "/work/users/w/e/weiyang/hest_replication"
OUT = f"{ROOT}/results/round3/D4_expansion/task_defs"
AUDIT = f"{ROOT}/results/round3/D3_audit/donor_audit_r3.csv"
MEMBERS = f"{ROOT}/results/round3/D0_inventory/expansion_set_members.csv"
BENCH_CCRCC = f"{ROOT}/results/round3/task_defs/CCRCC.json"
V1_SCHEMA = f"{ROOT}/results/round3/task_defs/task_def.schema.json"

# R0's bins, verbatim from code/scripts/round2_r0_resolution_columns.py, so an expansion
# sample's resolution_group is on the same scale as a benchmark sample's.
BIN_EDGES = [0.0, 0.15, 0.23, 0.30, 0.40, 0.50, np.inf]
BIN_LABELS = ["<=0.15", "0.15-0.23", "0.23-0.30", "0.30-0.40", "0.40-0.50", ">0.50"]

PAPILLA_CONTRADICTED = ["NCBI563", "NCBI564", "NCBI565", "NCBI566"]
PAPILLA_SINGLE_DONOR = ["NCBI562", "NCBI567", "NCBI568"]
JANESICK = ["NCBI783", "NCBI784", "NCBI785"]
N_PATIENT_GROUPS = 6          # grouped folds that supply the `random` design's test size only



def validate(inst, schema, path="$", root=None):
    """A self-contained validator for the draft-07 subset results/round3/task_defs/
    task_def.schema.json actually uses: type, required, properties, additionalProperties,
    items, enum, const, minItems, minLength, minimum. Returns a list of error strings.

    Written rather than imported because `jsonschema` is not installed in the project
    environment on Longleaf and adding a package to the analysis environment in the middle of
    a round is a larger change than a forty-line checker. Every keyword the committed schema
    contains is handled; an UNHANDLED keyword is reported as an error rather than ignored, so
    the checker cannot silently pass a file by not understanding the rule.
    """
    KNOWN = {"$schema", "title", "type", "required", "properties", "additionalProperties",
             "items", "enum", "const", "minItems", "minLength", "minimum", "description",
             "definitions", "$ref"}
    root = schema if root is None else root
    if "$ref" in schema:
        ref = schema["$ref"]
        assert ref.startswith("#/"), f"{path}: only local $ref is supported, got {ref}"
        node = root
        for part in ref[2:].split("/"):
            node = node[part]
        return validate(inst, node, path, root)
    errs = []
    unknown = set(schema) - KNOWN
    if unknown:
        return [f"{path}: schema keyword(s) this checker does not implement: {sorted(unknown)}"]
    TYPES = {"object": dict, "array": list, "string": str, "integer": int, "number": (int, float),
             "boolean": bool, "null": type(None)}
    if "type" in schema:
        want = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        ok = False
        for w in want:
            t = TYPES[w]
            if w in ("integer", "number") and isinstance(inst, bool):
                continue
            if isinstance(inst, t):
                ok = True
        if not ok:
            return [f"{path}: expected type {want}, got {type(inst).__name__}"]
    if "const" in schema and inst != schema["const"]:
        errs.append(f"{path}: expected const {schema['const']!r}, got {inst!r}")
    if "enum" in schema and inst not in schema["enum"]:
        errs.append(f"{path}: {inst!r} is not one of {schema['enum']}")
    if "minLength" in schema and isinstance(inst, str) and len(inst) < schema["minLength"]:
        errs.append(f"{path}: shorter than minLength {schema['minLength']}")
    if "minimum" in schema and isinstance(inst, (int, float)) and inst < schema["minimum"]:
        errs.append(f"{path}: {inst} below minimum {schema['minimum']}")
    if isinstance(inst, dict):
        for k in schema.get("required", []):
            if k not in inst:
                errs.append(f"{path}: missing required property {k!r}")
        props = schema.get("properties", {})
        for k, v in inst.items():
            if k in props:
                errs += validate(v, props[k], f"{path}.{k}", root)
            elif schema.get("additionalProperties") is False:
                errs.append(f"{path}: additional property {k!r} is not allowed")
    if isinstance(inst, list):
        if "minItems" in schema and len(inst) < schema["minItems"]:
            errs.append(f"{path}: {len(inst)} items, minItems {schema['minItems']}")
        if "items" in schema:
            for i, v in enumerate(inst):
                errs += validate(v, schema["items"], f"{path}[{i}]", root)
    return errs



def build_ext_schema(v1):
    """The D4 extension: schema v1 with section 13.7's extra columns declared.

    Everything v1 REQUIRES is kept, including its `additionalProperties: false`, so the
    extension is strict: a typo in one of the new column names fails validation rather than
    being silently accepted. The additions are exactly (a) the per-sample columns section 13.7
    names plus the traceability columns this generator writes, (b) a top-level `expansion`
    block, (c) a `population_out` fold list, and (d) `script_md5` in `provenance`, which the
    round-3 standing provenance rule requires.
    """
    S = json.loads(json.dumps(v1))
    S["title"] = ("Round-3 task definition, version 1, D4 expansion extension "
                  "(round3_execution_plan.md section 13.7)")
    st = {"type": ["string", "null"]}
    num = {"type": ["number", "null"]}
    S["properties"]["samples"]["items"]["properties"].update({
        "source": {"type": "string"}, "population": {"type": "string"},
        "instrument_generation": {"type": "string"}, "preservation": {"type": "string"},
        "region": {"type": "string"}, "disease": {"type": "string"},
        "disease_group": {"type": "string"},
        "donor_label_status_row_origin": {"enum": ["benchmark_r2", "expansion_d3"]},
        "donor_label_status_other_origin": st, "donor_id_other_origin": st,
        "resolution_uncertain_rederived": {"type": "string"},
        "pixel_size_um_embedded": num, "magnification_hest": {"type": "string"},
        "scanner": {"type": "string"},
        "n_expr_spots": {"type": "integer", "minimum": 1},
        "n_patch_spots": {"type": "integer", "minimum": 1},
        "unpatched_fraction": {"type": "number", "minimum": 0},
        "excluded_from_donor_units": {"type": "boolean"},
        "in_benchmark": {"type": "boolean"},
        "hest_dataset_title": {"type": "string"}})
    S["properties"]["samples"]["items"]["required"] = sorted(set(
        S["properties"]["samples"]["items"]["required"]) | {
        "source", "population", "instrument_generation", "preservation", "region",
        "unpatched_fraction", "n_expr_spots", "n_patch_spots",
        "donor_label_status_row_origin", "excluded_from_donor_units"})
    S["properties"]["folds"]["properties"]["population_out"] = {
        "$ref": "#/definitions/foldList"}
    S["properties"]["provenance"]["properties"]["script_md5"] = {"type": "string"}
    S["properties"]["expansion"] = {"type": "object"}
    S["required"] = sorted(set(S["required"]) | {"expansion"})
    return S


def resolution_group(px):
    return str(pd.cut([px], bins=BIN_EDGES, labels=BIN_LABELS, right=True)[0])


def patch_barcodes(p):
    with h5py.File(p, "r") as f:
        k = "barcode" if "barcode" in f else "barcodes"
        b = np.asarray(f[k][:]).reshape(-1)
        return [x.decode() if isinstance(x, (bytes, np.bytes_)) else str(x) for x in b]


def expr_barcodes_and_panel(p):
    A = ad.read_h5ad(p, backed="r")
    bc = [str(x) for x in A.obs_names]
    panel = [str(x) for x in A.var_names]
    try:
        A.file.close()
    except Exception:
        pass
    return bc, panel


def grouped_folds(units, n_groups):
    """Deterministic grouped k-fold over UNITS (no seed): sorted units dealt round robin.

    Used only for the `patient` key, which build_fold_specs() reads for the `random` design's
    test size (`test_size_from_fold: "patient"` in the A0 schema). The expansion sets have no
    shipped benchmark fold, so one has to be constructed; dealing sorted units round robin is
    reproducible without a seed and balances unit count per group.
    """
    us = sorted(units)
    groups = [[] for _ in range(n_groups)]
    for i, u in enumerate(us):
        groups[i % n_groups].append(u)
    return groups


def fold_list(samples_of_unit, groups):
    out = []
    for k, g in enumerate(groups):
        test = sorted(s for u in g for s in samples_of_unit[u])
        train = sorted(s for u, ss in samples_of_unit.items() if u not in set(g) for s in ss)
        out.append(dict(fold=str(k), train=train, test=test))
    return out


def loo_folds(samples_of_unit):
    out = []
    for u in sorted(samples_of_unit):
        test = sorted(samples_of_unit[u])
        train = sorted(s for v, ss in samples_of_unit.items() if v != u for s in ss)
        out.append(dict(fold=str(u), train=train, test=test))
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    aud = pd.read_csv(AUDIT, dtype=str)
    mem = pd.read_csv(MEMBERS)
    ext = aud[aud.row_origin == "expansion_d3"].set_index("sample_id")
    ben = aud[aud.row_origin == "benchmark_r2"].set_index("sample_id")
    commit = subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"], capture_output=True,
                            text=True).stdout.strip()

    set_of = {"kidney_visium_cell": sorted(mem.loc[mem.set_name == "institution_kidney_visium",
                                                   "sample_id"]),
              "institution_breast_xenium": sorted(mem.loc[mem.set_name == "institution_breast_xenium",
                                                          "sample_id"])}
    home = {s: "kidney_visium_cell" for s in set_of["kidney_visium_cell"]}
    home.update({s: "institution_breast_xenium" for s in set_of["institution_breast_xenium"]})
    assert len(set_of["kidney_visium_cell"]) == 54 and len(set_of["institution_breast_xenium"]) == 18

    # ---------------------------------------------------- per-sample facts, read from the files
    facts = {}
    for sid, setname in sorted(home.items()):
        ebc, panel = expr_barcodes_and_panel(f"{ROOT}/hest_ext/{setname}/st/{sid}.h5ad")
        pbc = patch_barcodes(f"{ROOT}/hest_ext/{setname}/patches/{sid}.h5")
        es, pset = set(ebc), set(pbc)
        assert pset <= es, (f"{sid}: {len(pset - es)} patch barcodes are not expression "
                            f"barcodes; the D1 subset relation does not hold")
        facts[sid] = dict(set_name=setname, n_expr_spots=len(ebc), n_patch_spots=len(pbc),
                          n_spots=len(pset & es), panel=panel,
                          unpatched_fraction=1.0 - len(pset & es) / len(ebc))
        print(f"  [{sid}] expr {len(ebc):6d}  patched {len(pbc):6d}  "
              f"unpatched {facts[sid]['unpatched_fraction']:.4f}  panel {len(panel)}", flush=True)

    def sample_row(sid, population, instrument_generation, use_origin="expansion_d3"):
        f = facts[sid]
        src = ext.loc[sid] if use_origin == "expansion_d3" else ben.loc[sid]
        oth = ben.loc[sid] if (use_origin == "expansion_d3" and sid in ben.index) else (
            ext.loc[sid] if (use_origin == "benchmark_r2" and sid in ext.index) else None)
        e = ext.loc[sid]                       # the audit's own metadata columns, either way
        px_est = float(e.pixel_size_um_estimated)
        return dict(
            sample_id=sid,
            donor_id=(None if pd.isna(src.donor_id) or src.donor_id == "" else str(src.donor_id)),
            hest_patient=(None if pd.isna(e.hest_patient) or e.hest_patient == ""
                          else str(e.hest_patient)),
            donor_label_status=str(src.donor_label_status),
            lab=str(e.lab),
            lab_label_status=str(e.lab_label_status),
            session=None,
            resolution_group=resolution_group(px_est),
            pixel_size_um=px_est,
            resolution_uncertain=(str(e.resolution_uncertain_hest).lower() == "true"),
            n_spots=int(f["n_spots"]),
            # ------------- section 13.7's extra columns -------------
            source=str(e.hest_lab_provisional) if pd.notna(e.hest_lab_provisional) else str(e.lab),
            population=population,
            instrument_generation=instrument_generation,
            preservation=str(e.preservation),
            region=str(e.region),
            disease=str(e.disease),
            donor_label_status_row_origin=use_origin,
            donor_label_status_other_origin=(None if oth is None
                                             else str(oth.donor_label_status)),
            donor_id_other_origin=(None if oth is None else str(oth.donor_id)),
            resolution_uncertain_rederived=str(e.resolution_uncertain_rederived),
            pixel_size_um_embedded=(None if pd.isna(e.pixel_size_um_embedded) or
                                    e.pixel_size_um_embedded == "" else
                                    float(e.pixel_size_um_embedded)),
            magnification_hest=str(e.magnification_hest),
            scanner=str(e.scanner),
            n_expr_spots=int(f["n_expr_spots"]),
            n_patch_spots=int(f["n_patch_spots"]),
            unpatched_fraction=float(f["unpatched_fraction"]),
            excluded_from_donor_units=bool(sid in PAPILLA_CONTRADICTED),
            in_benchmark=(str(e.in_benchmark).lower() == "true"),
            hest_dataset_title=str(e.hest_dataset_title),
        )

    def paths_for(setname):
        return dict(adata=f"hest_ext/{setname}/st/{{sample_id}}.h5ad",
                    patches=f"hest_ext/{setname}/patches/{{sample_id}}.h5",
                    embeddings=f"embeddings_ext/{setname}/{{encoder}}/{{sample_id}}.h5",
                    target_genes="per-fold; see results/round3/D4_expansion/d4_fold_genes__<task>.json")

    def provenance(inputs):
        return dict(generated_by="code/scripts/round3_d4_task_defs.py",
                    generated_at=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                    commit=commit,
                    script_md5=__import__("hashlib").md5(
                        open(os.path.abspath(__file__), "rb").read()).hexdigest(),
                    inputs=inputs, pythonhashseed=os.environ.get("PYTHONHASHSEED", "unset"))

    def panel_intersection(ids):
        return sorted(set.intersection(*[set(facts[s]["panel"]) for s in ids]))

    defs = {}

    # ------------------------------------------------------------------ 1. CCRCC layout anchor
    bench = json.load(open(BENCH_CCRCC))
    ccrcc_ids = sorted(s["sample_id"] for s in bench["samples"])
    assert len(ccrcc_ids) == 24
    rows = []
    for s in bench["samples"]:
        sid = s["sample_id"]
        r = dict(s)                             # A1's row, verbatim: donor_id, statuses, folds
        f = facts[sid]
        r.update(source=str(ext.loc[sid, "hest_lab_provisional"]),
                 population="cordeliers_ccRCC",
                 instrument_generation="not_applicable_visium",
                 preservation=str(ext.loc[sid, "preservation"]),
                 region=str(ext.loc[sid, "region"]),
                 disease=str(ext.loc[sid, "disease"]),
                 donor_label_status_row_origin="benchmark_r2",
                 donor_label_status_other_origin=str(ext.loc[sid, "donor_label_status"]),
                 donor_id_other_origin=str(ext.loc[sid, "donor_id"]),
                 resolution_uncertain_rederived=str(ext.loc[sid, "resolution_uncertain_rederived"]),
                 pixel_size_um_embedded=(None if pd.isna(ext.loc[sid, "pixel_size_um_embedded"])
                                         else float(ext.loc[sid, "pixel_size_um_embedded"])),
                 magnification_hest=str(ext.loc[sid, "magnification_hest"]),
                 scanner=str(ext.loc[sid, "scanner"]),
                 n_expr_spots=int(f["n_expr_spots"]),
                 n_patch_spots=int(f["n_patch_spots"]),
                 unpatched_fraction=float(f["unpatched_fraction"]),
                 excluded_from_donor_units=False,
                 in_benchmark=True,
                 hest_dataset_title=str(ext.loc[sid, "hest_dataset_title"]))
        # n_spots on the HEST layout is the patched-spot count, not the benchmark's
        r["n_spots"] = int(f["n_spots"])
        rows.append(r)
    defs["CCRCC_hest_layout"] = dict(
        task_def_version=1, task="CCRCC", label_set="shipped", source="hest_ext",
        st_technology="Visium", repo_root_relative=True,
        paths=dict(paths_for("kidney_visium_cell"),
                   target_genes="bench_data/CCRCC/var_50genes.json"),
        target_genes=dict(bench["target_genes"]),
        samples=rows, flags=dict(bench["flags"]),
        folds=json.loads(json.dumps(bench["folds"])),
        provenance=provenance([os.path.relpath(BENCH_CCRCC, ROOT), os.path.relpath(AUDIT, ROOT),
                               "hest_ext/kidney_visium_cell/st/<sample_id>.h5ad",
                               "hest_ext/kidney_visium_cell/patches/<sample_id>.h5"]),
        expansion=dict(
            set_name="kidney_visium_cell", layout="hest_1k",
            arm="layout_anchor",
            purpose="section 13.7.1: the layout anchor. Every field except `paths` and the "
                    "spot counts is copied from the committed benchmark task definition, so "
                    "the only difference between this arm and A1's CCRCC rows is which "
                    "patches the embeddings were computed from and which spots survive "
                    "patching.",
            donor_grouping_origin="benchmark_r2",
            spots="patched spots only (the embedding barcode list), which for CCRCC is "
                  "1,032 to 4,975 of 1,084 to 4,975 expression spots per sample",
            contradicted_papilla_excluded=[]))

    # ------------------------------------------------------------------ 2. Indiana donor set
    ind_ids = sorted([s for s in set_of["kidney_visium_cell"]
                      if s.startswith("NCBI") and s not in PAPILLA_CONTRADICTED])
    assert len(ind_ids) == 26, ind_ids
    ind_rows = [sample_row(s, "indiana_nontumour",
                           "not_applicable_visium") for s in ind_ids]
    unit_of = {r["sample_id"]: r["donor_id"] for r in ind_rows}
    assert all(unit_of.values()), "an Indiana sample has no donor_id"
    samples_of_unit = {}
    for s, u in unit_of.items():
        samples_of_unit.setdefault(u, []).append(s)
    assert len(samples_of_unit) == 25, f"{len(samples_of_unit)} donor units, expected 25"
    ind_panel = panel_intersection(ind_ids)
    defs["INDIANA_KIDNEY"] = dict(
        task_def_version=1, task="INDIANA_KIDNEY", label_set="shipped", source="hest_ext",
        st_technology="Visium", repo_root_relative=True,
        paths=paths_for("kidney_visium_cell"),
        target_genes=dict(
            list=ind_panel, n=len(ind_panel),
            selection="CANDIDATE PANEL, not the target list. The gene intersection over the "
                      "26 samples' own var_names, in sorted order. The 50 target genes are "
                      "chosen PER FOLD on the fold's training samples only, by "
                      "code/scripts/round2_r2_gene_check.py::get_k_genes (HEST's own "
                      "get_k_genes, criteria='var', k=50, min_cells_pct=0.10) run on the "
                      "training samples' patched spots, with genes off this intersection "
                      "dropped as round 2 R2 did; the per-fold lists are written to "
                      "results/round3/D4_expansion/d4_fold_genes__INDIANA_KIDNEY.json.",
            selection_used_test_spots=False),
        samples=ind_rows,
        flags=dict(patient_labels_unreliable=False, same_specimen_pairs=True,
                   idc_attribution_unresolved=False),
        folds=dict(patient=fold_list(samples_of_unit,
                                     grouped_folds(samples_of_unit, N_PATIENT_GROUPS)),
                   donor=loo_folds(samples_of_unit), slide_out=[],
                   random=dict(n_repeats=5, test_size_from_fold="patient",
                               seed_source="crc32")),
        provenance=provenance([os.path.relpath(AUDIT, ROOT), os.path.relpath(MEMBERS, ROOT),
                               "hest_ext/kidney_visium_cell/st/<sample_id>.h5ad",
                               "hest_ext/kidney_visium_cell/patches/<sample_id>.h5"]),
        expansion=dict(
            set_name="kidney_visium_cell", layout="hest_1k", arm="indiana_donor_set",
            purpose="section 13.7.2. 23 atlas samples plus the three single-donor papilla "
                    "samples; 25 donor units because NCBI701 and NCBI702 are one participant.",
            donor_grouping_origin="expansion_d3",
            spots="patched spots only",
            contradicted_papilla_excluded=PAPILLA_CONTRADICTED,
            same_specimen_pairs=["NCBI701;NCBI702"],
            designs_run=["random", "donor (25% rule)", "A4b K=10 (24 in pool, 10 calibration, "
                         "14 training)"],
            difference_list_for_donor=[
                "donor", "disease (reference, diabetic, acute kidney injury)",
                "region where stated (NCBI701 medulla against NCBI702 cortex; the papilla "
                "samples against the atlas samples)",
                "section and capture area"],
            held_fixed=["laboratory (Indiana University, Eadon)", "instrument", "objective",
                        "preservation (fresh frozen, OCT)", "pixel size to within the set's "
                        "own spread"]))

    # ------------------------------------------------------------------ 3. kidney population set
    pop_ids = sorted(set_of["kidney_visium_cell"])
    pop_rows = []
    for s in pop_ids:
        popn = "cordeliers_ccRCC" if s.startswith("INT") else "indiana_nontumour"
        origin = "benchmark_r2" if s in ben.index else "expansion_d3"
        pop_rows.append(sample_row(s, popn, "not_applicable_visium",
                                   use_origin="expansion_d3"))
        pop_rows[-1]["population"] = popn
    n_cor = sum(r["population"] == "cordeliers_ccRCC" for r in pop_rows)
    assert n_cor == 24 and len(pop_rows) - n_cor == 30, (n_cor, len(pop_rows))
    cor_ids = [r["sample_id"] for r in pop_rows if r["population"] == "cordeliers_ccRCC"]
    ind30 = [r["sample_id"] for r in pop_rows if r["population"] == "indiana_nontumour"]
    pop_panel = panel_intersection(pop_ids)
    pop_unit = {r["sample_id"]: r["donor_id"] for r in pop_rows}
    pop_units = {}
    for s, u in pop_unit.items():
        pop_units.setdefault(u, []).append(s)
    defs["KIDNEY_POP54"] = dict(
        task_def_version=1, task="KIDNEY_POP54", label_set="shipped", source="hest_ext",
        st_technology="Visium", repo_root_relative=True,
        paths=paths_for("kidney_visium_cell"),
        target_genes=dict(
            list=pop_panel, n=len(pop_panel),
            selection="CANDIDATE PANEL, not the target list: the gene intersection over all 54 "
                      "samples, sorted. The 50 target genes are chosen per fold on the training "
                      "POPULATION's samples only (get_k_genes as above) and then restricted to "
                      "this intersection panel, per section 13.7.3's 'training-only gene "
                      "selection on the intersection panel'.",
            selection_used_test_spots=False),
        samples=pop_rows,
        flags=dict(patient_labels_unreliable=False, same_specimen_pairs=True,
                   idc_attribution_unresolved=False),
        folds=dict(patient=fold_list(pop_units, grouped_folds(pop_units, N_PATIENT_GROUPS)),
                   donor=loo_folds(pop_units), slide_out=[],
                   random=dict(n_repeats=5, test_size_from_fold="patient", seed_source="crc32"),
                   population_out=[dict(fold="test_indiana_nontumour", train=cor_ids,
                                        test=ind30),
                                   dict(fold="test_cordeliers_ccRCC", train=ind30,
                                        test=cor_ids)]),
        provenance=provenance([os.path.relpath(AUDIT, ROOT), os.path.relpath(MEMBERS, ROOT),
                               "hest_ext/kidney_visium_cell/st/<sample_id>.h5ad",
                               "hest_ext/kidney_visium_cell/patches/<sample_id>.h5"]),
        expansion=dict(
            set_name="kidney_visium_cell", layout="hest_1k", arm="population_out",
            purpose="section 13.7.3. Both directions of the population-and-source shift.",
            donor_grouping_origin="expansion_d3",
            spots="patched spots only",
            contradicted_papilla_excluded=PAPILLA_CONTRADICTED,
            contradicted_papilla_note="section 13.10 item 5: NCBI563 to NCBI566 remain test "
                                      "spots and remain eligible as TRAINING spots, and are "
                                      "excluded from every donor-level calibration set and "
                                      "from donor-level clustering. Marked by "
                                      "samples[].excluded_from_donor_units.",
            term_name="population-and-source shift",
            never_call_it="a laboratory term (section 13.2 item 4)",
            difference_list_for_population_out=[
                "tissue state (tumour against non-tumour)",
                "anatomical region (cortex and papilla against tumour)",
                "disease (clear cell renal cell carcinoma against reference, diabetic kidney "
                "disease, acute kidney injury and calcium oxalate stone disease)",
                "preservation, partly (12 FFPE and 12 fresh frozen against 30 fresh "
                "frozen/OCT)",
                "laboratory (INSERM UMR-S 1138 Centre de Recherche des Cordeliers against "
                "Indiana University)",
                "instrument", "objective", "pixel size",
                "the pixel-size provenance flag (D3 re-derived resolution_uncertain for all 30 "
                "Indiana samples and contradicted HEST's 20x magnification)"]))

    # ------------------------------------------------------------------ 4. breast Xenium
    br_ids = sorted(set_of["institution_breast_xenium"])
    br_rows = [sample_row(s, "breast_xenium_idc",
                          "prototype" if s in JANESICK else "production") for s in br_ids]
    for r in br_rows:
        d = r["disease"].lower()
        r["disease_group"] = ("CCH_DCIS" if d.startswith("cch") else
                              "DCIS" if d.startswith("dcis") else "IDC")
    br_unit = {r["sample_id"]: r["donor_id"] for r in br_rows}
    br_units = {}
    for s, u in br_unit.items():
        br_units.setdefault(u, []).append(s)
    assert len(br_units) == 15, f"{len(br_units)} breast donor groups, expected 15"
    br_panel = panel_intersection(br_ids)
    defs["BREAST_XENIUM"] = dict(
        task_def_version=1, task="BREAST_XENIUM", label_set="shipped", source="hest_ext",
        st_technology="Xenium", repo_root_relative=True,
        paths=paths_for("institution_breast_xenium"),
        target_genes=dict(
            list=br_panel, n=len(br_panel),
            selection="CANDIDATE PANEL, not the target list: the gene intersection over the 18 "
                      "samples' own var_names, sorted. This is the set's common panel as the "
                      "files carry it. The 50 target genes are chosen per fold on the training "
                      "samples only (get_k_genes as above) and restricted to this panel.",
            selection_used_test_spots=False),
        samples=br_rows,
        flags=dict(patient_labels_unreliable=True, same_specimen_pairs=True,
                   idc_attribution_unresolved=False),
        folds=dict(patient=fold_list(br_units, grouped_folds(br_units, 5)),
                   donor=loo_folds(br_units), slide_out=[],
                   random=dict(n_repeats=5, test_size_from_fold="patient", seed_source="crc32")),
        provenance=provenance([os.path.relpath(AUDIT, ROOT), os.path.relpath(MEMBERS, ROOT),
                               "hest_ext/institution_breast_xenium/st/<sample_id>.h5ad",
                               "hest_ext/institution_breast_xenium/patches/<sample_id>.h5"]),
        expansion=dict(
            set_name="institution_breast_xenium", layout="hest_1k", arm="breast_donor",
            purpose="section 13.7.4. One laboratory, two instrument generations, 15 donor "
                    "groups.",
            donor_grouping_origin="expansion_d3",
            spots="patched spots only",
            contradicted_papilla_excluded=[],
            strata=dict(
                instrument_generation_by_sample="3 prototype (NCBI783, NCBI784, NCBI785) "
                                                "against 15 production",
                instrument_generation_by_donor_group="2 prototype against 13 production, "
                                                     "because NCBI784 and NCBI785 share a "
                                                     "donor (section 13.10 item 3)",
                disease_by_sample="10 IDC, 7 DCIS, 1 CCH/DCIS"),
            difference_list_for_donor=["donor", "disease", "block source",
                                       "instrument generation for some pairs", "run date",
                                       "slide"],
            held_fixed=["laboratory (10x Genomics)", "platform (Xenium)",
                        "panel family", "preservation (FFPE)"],
            no_source_term="No source term is reported from this set: D3 established all 18 "
                           "samples are one laboratory."))

    # --------------------------------------------------------------------------- write + validate
    for name, td in defs.items():
        p = f"{OUT}/{name}.json"
        with open(p, "w") as f:
            json.dump(td, f, indent=2, sort_keys=False)
            f.write("\n")
        print(f"[write] {p}", flush=True)

    v1 = json.load(open(V1_SCHEMA))
    rows = []
    have_js = True          # the validator below is self-contained; no jsonschema needed

    def relaxed(node):
        """v1 with additionalProperties dropped everywhere: the expansion files must satisfy
        every REQUIREMENT v1 states, while being allowed the section 13.7 columns."""
        if isinstance(node, dict):
            return {k: relaxed(v) for k, v in node.items() if k != "additionalProperties"}
        if isinstance(node, list):
            return [relaxed(v) for v in node]
        return node

    v1r = relaxed(v1)
    ext_schema = build_ext_schema(v1)
    with open(f"{OUT}/task_def_ext.schema.json", "w") as f:
        json.dump(ext_schema, f, indent=1)
        f.write("\n")
    print(f"[write] {OUT}/task_def_ext.schema.json", flush=True)
    for name, td in defs.items():
        errs = {tag: validate(td, sch) for tag, sch in
                (("v1_relaxed", v1r), ("v1_strict", v1), ("ext", ext_schema))}
        err_v1r = "; ".join(errs["v1_relaxed"][:3])
        err_strict = "; ".join(errs["v1_strict"][:3])
        err_ext = "; ".join(errs["ext"][:3])
        ids = [s["sample_id"] for s in td["samples"]]
        units = {s["donor_id"] for s in td["samples"] if not s.get("excluded_from_donor_units")}
        uf = [s["unpatched_fraction"] for s in td["samples"]]
        req_cols = ["lab", "source", "population", "instrument_generation", "preservation",
                    "region", "donor_label_status", "lab_label_status", "unpatched_fraction"]
        rows.append(dict(
            task_def=name, task=td["task"], set_name=td["expansion"]["set_name"],
            arm=td["expansion"]["arm"], n_samples=len(ids),
            n_samples_unique=len(set(ids)), n_donor_units=len(units),
            n_donor_ids_null=sum(s["donor_id"] is None for s in td["samples"]),
            n_folds_donor=len(td["folds"]["donor"]),
            n_folds_patient=len(td["folds"]["patient"]),
            n_folds_population_out=len(td["folds"].get("population_out", [])),
            random_n_repeats=td["folds"]["random"]["n_repeats"],
            candidate_panel_n=td["target_genes"]["n"],
            selection_used_test_spots=td["target_genes"]["selection_used_test_spots"],
            n_spots_total=sum(s["n_spots"] for s in td["samples"]),
            n_expr_spots_total=sum(s["n_expr_spots"] for s in td["samples"]),
            unpatched_fraction_min=round(float(np.min(uf)), 6),
            unpatched_fraction_median=round(float(np.median(uf)), 6),
            unpatched_fraction_max=round(float(np.max(uf)), 6),
            required_extra_columns_present=all(
                all(c in s for c in req_cols) for s in td["samples"]),
            folds_cover_every_sample=all(
                sorted(set(f["train"]) | set(f["test"])) == sorted(set(ids))
                for key in ("patient", "donor") for f in td["folds"][key]),
            folds_disjoint=all(not (set(f["train"]) & set(f["test"]))
                               for key in ("patient", "donor") for f in td["folds"][key]),
            jsonschema_available=have_js,
            v1_relaxed_error=err_v1r,
            v1_strict_error=err_strict,
            ext_schema_error=err_ext,
            excluded_from_donor_units=";".join(
                s["sample_id"] for s in td["samples"] if s.get("excluded_from_donor_units")),
        ))
    V = pd.DataFrame(rows)
    V.to_csv(f"{ROOT}/results/round3/D4_expansion/d4_task_defs_validation.csv", index=False)
    print("\n" + V.drop(columns=["v1_strict_error"]).to_string(index=False), flush=True)
    print("\nv1_strict errors (expected: the section 13.7 columns are an extension):", flush=True)
    for _, r in V.iterrows():
        print(f"  {r.task_def}: {r.v1_strict_error or 'none'}", flush=True)

    # per-sample table, for the report
    per = []
    for name, td in defs.items():
        for s in td["samples"]:
            per.append(dict(task_def=name, **{k: v for k, v in s.items() if k != "folds"}))
    pd.DataFrame(per).to_csv(
        f"{ROOT}/results/round3/D4_expansion/d4_task_def_samples.csv", index=False)
    assert all(not r["v1_relaxed_error"] for r in rows), "a task definition fails relaxed v1"
    assert all(not r["ext_schema_error"] for r in rows), \
        "a task definition fails the D4 extension schema"
    print("\n[ok] every expansion task definition satisfies v1's requirements", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
