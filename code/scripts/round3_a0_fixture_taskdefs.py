#!/usr/bin/env python
"""Round 3, stage A0: FIXTURE task-definition files for the harness smoke and acceptance runs.

Stage: A0, the conformal harness (round3_execution_plan.md section 4.2).

WHY THIS EXISTS, AND WHY IT IS NOT THE REAL GENERATOR.
`results/round3/task_defs/<task>.json` is written by the Housekeeping (S0) track. At the time
the A0 harness had to be smoke-tested those files did not exist -- only `SCHEMA.md` and
`task_def.schema.json` were in that directory. The harness must not be blocked on them and,
more importantly, must not be built against an imagined contract. So this script writes
FIXTURE task definitions that conform to `results/round3/task_defs/task_def.schema.json`,
into a directory of its own:

    results/round3/A0_smoke/fixture_task_defs/<task>.json

Never into `results/round3/task_defs/`. One writer per file (handoff section 7): that
directory belongs to the S0 track. When the real files land, the harness is pointed at them
with `--task-def` and nothing here is used again. `round3_a0_harness.py` records which
task-def file it read, and whether it was a fixture, in its provenance.

Every value is read from a file and every file is named in `provenance.inputs`; nothing is
typed from memory, which is rule 1 of the schema. The one place this fixture is weaker than
the real generator will be is `n_spots`: the schema asks for spots under tissue read from the
AnnData, and this reads `n_spots_adata` from `bench_data/hest_bench_sample_inventory.csv`,
which is where an earlier stage recorded exactly that value after reading the AnnData. Opening
72 h5ad files to re-derive a number already on disk is not worth a batch job. Declared here
rather than hidden.

Usage: round3_a0_fixture_taskdefs.py [task ...]        (default: all ten benchmark tasks)
"""
import csv
import glob
import hashlib
import json
import os
import subprocess
import sys
import time

ROOT = "/work/users/w/e/weiyang/hest_replication"
BD = f"{ROOT}/bench_data"
OUT = f"{ROOT}/results/round3/A0_smoke/fixture_task_defs"

META = f"{ROOT}/results/tailored/integrity/sample_metadata.csv"
AUDIT = f"{ROOT}/results/round2/R5b_audit/donor_audit.csv"
INV = f"{BD}/hest_bench_sample_inventory.csv"

# The plan's slide_out task list, section 4.2 design table: "one slide, on the multi-slide
# tasks PRAD, COAD, READ, LYMPH_IDC, and IDC under audited labels". Taken verbatim; the
# harness additionally refuses to run slide_out on a fold whose pool has no other slide.
SLIDE_OUT_TASKS = ("PRAD", "COAD", "READ", "LYMPH_IDC")
SLIDE_OUT_TASKS_AUDITED = ("IDC",)

N_RANDOM_REPEATS = 5          # section 4.2 design table: "5 repeats"


def rows(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def sample_ids(task):
    """Sample order EXACTLY as round2_r1b_heads.load_task sees it: sorted adata paths."""
    return [os.path.basename(p)[:-5]
            for p in sorted(glob.glob(f"{BD}/{task}/adata/*.h5ad"))]


def split_sets(task, kind, k):
    p = f"{BD}/{task}/splits/{kind}_{k}.csv"
    return sorted({os.path.basename(r["expr_path"]).replace(".h5ad", "")
                   for r in rows(p)})


def session_of(task, subseries, hest_patient):
    """Session, the schema's 'non-null only where a session contrast exists inside one donor,
    which in the benchmark is PRAD patient 2 alone'.

    PRAD's `subseries` in sample_metadata.csv is `patient_2_V1_6`, `patient_2_H3_4` and so on:
    donor, then a capture batch letter-number, then a replicate index. The session is the
    batch, so the replicate index is dropped. Read from the file, not assumed: for every other
    task `subseries` carries no such structure and session is null.

    Observation for the S0 track, recorded rather than acted on: PRAD *patient 1* also spans
    three batches (V1, H1, H2) by the same rule, so the schema's "patient 2 alone" understates
    the benchmark. This fixture follows the schema prose so that it stays interchangeable with
    the real files, and the harness reads whatever the file says.
    """
    if task != "PRAD" or hest_patient != "patient 2":
        return None
    parts = subseries.split("_")
    return "_".join(parts[:-1]) if len(parts) >= 4 else subseries


def build(task, label_set, meta, audit, inv, commit):
    ids = sample_ids(task)
    assert ids, f"{task}: no adata files under {BD}/{task}/adata"

    samples = []
    for sid in ids:
        m = meta[sid]
        a = audit.get(sid)
        # Schema rule 3: a sample missing from the audit gets a null donor_id and
        # donor_label_status "unverifiable", and the generator fails loudly rather than
        # inventing one. Here it fails loudly, because all 72 benchmark samples are audited.
        assert a is not None, (f"{sid} absent from {AUDIT}; a fixture must not invent a "
                               f"donor_id")
        hp = (m["patient"] or "").strip() or None
        samples.append(dict(
            sample_id=sid,
            donor_id=(a["donor_id"] or None),
            hest_patient=hp,
            donor_label_status=a["donor_label_status"],
            lab=m["cohort_prefix"],
            # Never "verified": the benchmark's lab field has never been audited and D3 is
            # the stage that audits it (schema, samples[] table).
            lab_label_status="unverified",
            session=session_of(task, m["subseries"], hp),
            resolution_group=m["resolution_group"],
            pixel_size_um=float(m["pixel_size_um"]),
            resolution_uncertain=(m["resolution_uncertain"].strip().lower()
                                  in ("true", "1", "yes")),
            n_spots=int(inv[sid]["n_spots_adata"]),
        ))

    donor_of = {s["sample_id"]: s["donor_id"] for s in samples}

    gj = json.load(open(f"{BD}/{task}/var_50genes.json"))
    genes = list(gj["genes"])           # file order, schema rule 4

    n_folds = len(glob.glob(f"{BD}/{task}/splits/test_*.csv"))
    patient_folds = []
    for k in range(n_folds):
        te = split_sets(task, "test", k)
        tr = split_sets(task, "train", k)
        assert set(tr) | set(te) == set(ids) and not (set(tr) & set(te)), \
            f"{task} fold {k}: shipped train/test are not a partition of the task"
        patient_folds.append(dict(fold=str(k), train=tr, test=te))

    # donor: leave-one-donor-out by donor_id. fold id IS the held-out donor_id.
    donor_folds = []
    for d in sorted({s["donor_id"] for s in samples}):
        te = sorted(s for s in ids if donor_of[s] == d)
        tr = sorted(s for s in ids if donor_of[s] != d)
        if not tr:
            continue                    # a one-donor task has no donor design
        donor_folds.append(dict(fold=d, train=tr, test=te))

    so_list = (SLIDE_OUT_TASKS_AUDITED if label_set == "audited" else SLIDE_OUT_TASKS)
    slide_folds = []
    if task in so_list and len(ids) > 1:
        for s in ids:
            slide_folds.append(dict(fold=s, train=sorted(x for x in ids if x != s),
                                    test=[s]))

    td = dict(
        task_def_version=1,
        task=task,
        label_set=label_set,
        source="hest_bench",
        st_technology=meta[ids[0]]["st_technology"],
        repo_root_relative=True,
        paths=dict(
            adata=f"bench_data/{task}/adata/{{sample_id}}.h5ad",
            patches=f"bench_data/{task}/patches/{{sample_id}}.h5",
            embeddings=f"embeddings/{task}/{{encoder}}/{{sample_id}}.h5",
            target_genes=f"bench_data/{task}/var_50genes.json",
        ),
        target_genes=dict(
            list=genes,
            n=len(genes),
            selection=("The benchmark's shipped 50-gene list, read verbatim from "
                       f"bench_data/{task}/var_50genes.json in file order. HEST-bench chose "
                       "it as the 50 most expressed genes over ALL spots of the task, test "
                       "spots included, so selection_used_test_spots is true; this is the "
                       "benchmark's property, not a choice of this project, and it is why "
                       "round 3 track D selects gene lists on training samples only."),
            selection_used_test_spots=True,
        ),
        samples=samples,
        flags=dict(
            patient_labels_unreliable=(task == "COAD"),
            same_specimen_pairs=(task == "READ"),
            idc_attribution_unresolved=(task == "IDC"),
        ),
        folds=dict(
            patient=patient_folds,
            donor=donor_folds,
            slide_out=slide_folds,
            random=dict(n_repeats=N_RANDOM_REPEATS,
                        test_size_from_fold="patient",
                        seed_source="crc32"),
        ),
        provenance=dict(
            generated_by=("code/scripts/round3_a0_fixture_taskdefs.py (FIXTURE, stage A0; "
                          "NOT the S0 generator for results/round3/task_defs/)"),
            generated_at=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            commit=commit,
            inputs=[
                f"bench_data/{task}/adata/*.h5ad (sample list and order)",
                f"bench_data/{task}/var_50genes.json",
                f"bench_data/{task}/splits/train_*.csv",
                f"bench_data/{task}/splits/test_*.csv",
                "results/tailored/integrity/sample_metadata.csv",
                "results/round2/R5b_audit/donor_audit.csv",
                "bench_data/hest_bench_sample_inventory.csv (n_spots_adata -> n_spots)",
            ],
            pythonhashseed=os.environ.get("PYTHONHASHSEED"),
        ),
    )
    return td


TYPES = {"object": dict, "array": list, "string": str, "integer": int, "number": (int, float),
         "boolean": bool, "null": type(None)}
HANDLED = {"$schema", "title", "type", "required", "additionalProperties", "properties",
           "items", "minItems", "minLength", "minimum", "enum", "const", "$ref",
           "definitions", "description"}


def validate_draft07(inst, sch, root, path="$"):
    """A strict subset of JSON Schema draft-07: exactly the keywords
    results/round3/task_defs/task_def.schema.json uses, and a hard failure on any keyword
    this function does not implement. Raises AssertionError naming the JSON path."""
    unknown = set(sch) - HANDLED
    assert not unknown, f"{path}: validator does not implement schema keywords {sorted(unknown)}"

    if "$ref" in sch:
        ref = sch["$ref"]
        assert ref.startswith("#/"), f"{path}: only local refs supported, got {ref}"
        node = root
        for part in ref[2:].split("/"):
            node = node[part]
        return validate_draft07(inst, node, root, path)

    if "const" in sch:
        assert inst == sch["const"], f"{path}: {inst!r} != const {sch['const']!r}"
    if "enum" in sch:
        assert inst in sch["enum"], f"{path}: {inst!r} not in enum {sch['enum']}"
    if "type" in sch:
        want = sch["type"] if isinstance(sch["type"], list) else [sch["type"]]
        py = tuple(t for w in want for t in
                   (TYPES[w] if isinstance(TYPES[w], tuple) else (TYPES[w],)))
        # JSON has no separate bool/int, Python does; a bool must not satisfy "integer".
        okbool = "boolean" in want
        assert isinstance(inst, py) and (okbool or not isinstance(inst, bool)), \
            f"{path}: {type(inst).__name__} is not {want}"
    if "minLength" in sch:
        assert len(inst) >= sch["minLength"], f"{path}: shorter than {sch['minLength']}"
    if "minimum" in sch:
        assert inst >= sch["minimum"], f"{path}: {inst} < minimum {sch['minimum']}"
    if "minItems" in sch:
        assert len(inst) >= sch["minItems"], f"{path}: fewer than {sch['minItems']} items"

    if isinstance(inst, dict):
        for k in sch.get("required", []):
            assert k in inst, f"{path}: missing required key {k!r}"
        props = sch.get("properties", {})
        if sch.get("additionalProperties") is False:
            extra = set(inst) - set(props)
            assert not extra, f"{path}: additional properties {sorted(extra)}"
        for k, v in inst.items():
            if k in props:
                validate_draft07(v, props[k], root, f"{path}.{k}")
    if isinstance(inst, list) and "items" in sch:
        for i, v in enumerate(inst):
            validate_draft07(v, sch["items"], root, f"{path}[{i}]")


def main():
    tasks = sys.argv[1:] or sorted(d for d in os.listdir(BD)
                                   if os.path.isdir(f"{BD}/{d}") and not d.startswith("."))
    os.makedirs(OUT, exist_ok=True)
    commit = subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"],
                            capture_output=True, text=True).stdout.strip()
    meta = {r["sample_id"]: r for r in rows(META)}
    audit = {r["sample_id"]: r for r in rows(AUDIT)}
    inv = {r["sample_id"]: r for r in rows(INV)}

    schema_path = f"{ROOT}/results/round3/task_defs/task_def.schema.json"
    schema = json.load(open(schema_path))
    try:
        import jsonschema
        validate = lambda d: jsonschema.validate(d, schema)          # noqa: E731
        how = f"jsonschema {jsonschema.__version__}"
    except ImportError:
        # The project environment is PINNED (env/REBUILD.md) and adding a package to it to
        # validate a fixture is not a trade worth making, so the validator below is used
        # instead. It covers the keywords task_def.schema.json actually uses and FAILS on an
        # unrecognised keyword rather than passing silently, which is the property that
        # matters: a validator that ignores what it does not understand certifies nothing.
        validate = lambda d: validate_draft07(d, schema, schema)     # noqa: E731
        how = ("jsonschema absent; using the local draft-07 subset validator in this file "
               "(strict: an unhandled keyword raises)")
    print(f"[validator] {how}", flush=True)

    written = []
    for task in tasks:
        label_sets = ["shipped", "audited"] if task == "IDC" else ["shipped"]
        for ls in label_sets:
            td = build(task, ls, meta, audit, inv, commit)
            validate(td)
            name = task if ls == "shipped" else f"{task}_audited"
            p = f"{OUT}/{name}.json"
            blob = json.dumps(td, indent=2, sort_keys=False) + "\n"
            with open(p, "w") as f:
                f.write(blob)
            written.append((name, p, len(td["samples"]),
                            len(td["folds"]["patient"]), len(td["folds"]["donor"]),
                            len(td["folds"]["slide_out"]), td["target_genes"]["n"],
                            hashlib.sha256(blob.encode()).hexdigest()[:12]))
            print(f"[{name}] samples={len(td['samples'])} "
                  f"folds patient={len(td['folds']['patient'])} "
                  f"donor={len(td['folds']['donor'])} "
                  f"slide_out={len(td['folds']['slide_out'])} "
                  f"genes={td['target_genes']['n']} -> {p}", flush=True)

    with open(f"{OUT}/FIXTURE_INDEX.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["name", "path", "n_samples", "n_folds_patient", "n_folds_donor",
                    "n_folds_slide_out", "n_genes", "sha256_12"])
        w.writerows(written)
    print(f"\nwrote {len(written)} fixture task definitions to {OUT}")


if __name__ == "__main__":
    main()
