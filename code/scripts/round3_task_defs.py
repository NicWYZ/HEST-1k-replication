#!/usr/bin/env python
"""Round 3, stage S0 -- generate the round-3 task-definition files.

Stage: round 3 S0 (task definitions), per docs/round3_execution_plan.md sections 4.1 and 4.2
and the fixed contract in results/round3/task_defs/SCHEMA.md +
results/round3/task_defs/task_def.schema.json.

Writes one JSON file per (task, label set) into results/round3/task_defs/:
  <TASK>.json        label_set "shipped", for each benchmark task discovered under bench_data/
  IDC_audited.json   label_set "audited", TENX95 and TENX99 merged into one donor

Every value is read from a file; nothing is typed from memory.  Two runs of this script
produce byte-identical outputs (see --generated-at below).

Usage:
    python round3_task_defs.py [--root ROOT] [--outdir DIR] [--schema PATH]

Determinism note: provenance.generated_at is NOT wall-clock.  The schema requires the field
and the task requires byte-identical reruns, so it is set to the HEAD commit's committer date
(deterministic given the commit).  The wall-clock run time is recorded in PROVENANCE.txt.
"""

import argparse
import csv
import json
import os
import re
import subprocess
import sys
import zlib
from collections import OrderedDict

DEFAULT_ROOT = "/work/users/w/e/weiyang/hest_replication"

# ---------------------------------------------------------------- fixed inputs

AUDIT_REL = "results/round2/R5b_audit/donor_audit.csv"
META_REL = "results/tailored/integrity/sample_metadata.csv"
SCHEMA_REL = "results/round3/task_defs/task_def.schema.json"

# Section 4 / section 2 task-level flags.  Explicit, per the handoff.
FLAGS = {
    "patient_labels_unreliable": {"COAD"},
    "same_specimen_pairs": {"READ"},
    "idc_attribution_unresolved": {"IDC"},
}

# The only session contrast inside one donor in the whole benchmark: PRAD patient 2's two
# scan sessions.  Membership is the sample-id sub-clustering given in the handoff; the
# script cross-checks it against pixel_size_um below and fails if the two groups overlap.
PRAD_SESSIONS = OrderedDict(
    [
        (
            "PRAD_p2_sess1_MEND139_MEND146",
            ["MEND139", "MEND140", "MEND141", "MEND142", "MEND143", "MEND144", "MEND145", "MEND146"],
        ),
        (
            "PRAD_p2_sess2_MEND147_MEND153",
            ["MEND147", "MEND148", "MEND149", "MEND150", "MEND151", "MEND152", "MEND153"],
        ),
    ]
)

# Round 2's R2_fold_hvg stage established that the benchmark's 50 target genes were ranked
# over all spots of all samples of the task, test folds included.
GENE_SELECTION = (
    "The benchmark's own 50 target genes for this task, read verbatim and in file order from "
    "{gene_file} as shipped with HEST-bench. This generator neither selected nor reordered "
    "them. Round 2 stage R2 (results/round2/R2_fold_hvg/) established that HEST ranked these "
    "genes over the all-sample gene intersection using all spots, test folds included, which "
    "is why selection_used_test_spots is true."
)

RANDOM_DESIGN = OrderedDict(
    [("n_repeats", 5), ("test_size_from_fold", "patient"), ("seed_source", "crc32")]
)


class GeneratorError(RuntimeError):
    pass


# ---------------------------------------------------------------- small helpers


def read_csv_rows(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def blank_to_none(v):
    if v is None:
        return None
    v = v.strip()
    return None if v == "" or v.lower() in ("nan", "na", "none") else v


def to_bool(v, where):
    s = str(v).strip().lower()
    if s in ("true", "1", "t", "yes"):
        return True
    if s in ("false", "0", "f", "no"):
        return False
    raise GeneratorError("non-boolean value %r at %s" % (v, where))


def slug(s):
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")


def natural_fold_key(k):
    return (0, int(k)) if str(k).isdigit() else (1, str(k))


def crc32_seed(*parts):
    """Stable across processes and versions; never hash() on a string."""
    return zlib.crc32("|".join(str(p) for p in parts).encode("utf-8"))


# ---------------------------------------------------------------- readers


def read_split_members(path):
    """Return (sample_ids, id_column). Checks which column holds the sample id."""
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames or []
        rows = list(reader)
    if not fieldnames:
        raise GeneratorError("split file has no header: %s" % path)
    if "sample_id" in fieldnames:
        col = "sample_id"
    else:
        # fall back: the single column whose values look like HEST sample ids
        cands = [
            f
            for f in fieldnames
            if rows and all(re.fullmatch(r"[A-Z]+[0-9]+", (r.get(f) or "").strip()) for r in rows)
        ]
        if len(cands) != 1:
            raise GeneratorError(
                "cannot identify the sample-id column in %s (header=%r)" % (path, fieldnames)
            )
        col = cands[0]
    ids = [(r[col] or "").strip() for r in rows]
    if not ids:
        raise GeneratorError("empty split file: %s" % path)
    if len(set(ids)) != len(ids):
        raise GeneratorError("duplicate sample ids in %s" % path)
    return ids, col


def read_gene_list(path):
    with open(path, encoding="utf-8") as fh:
        obj = json.load(fh)
    if isinstance(obj, dict):
        if "genes" not in obj:
            raise GeneratorError("no 'genes' key in %s (keys=%r)" % (path, sorted(obj)))
        genes = obj["genes"]
    elif isinstance(obj, list):
        genes = obj
    else:
        raise GeneratorError("unexpected JSON type in %s" % path)
    if not isinstance(genes, list) or not genes:
        raise GeneratorError("empty or non-list gene list in %s" % path)
    return [str(g) for g in genes]


def read_n_spots(h5ad_path):
    """Actual AnnData row count, read from the file, not copied from metadata."""
    import anndata

    try:
        ad = anndata.read_h5ad(h5ad_path, backed="r")
        try:
            return int(ad.n_obs)
        finally:
            try:
                ad.file.close()
            except Exception:
                pass
    except Exception as exc:
        # fall back to the raw obs index, so a backed-mode quirk cannot silently substitute
        # a metadata value for a real row count
        import h5py

        with h5py.File(h5ad_path, "r") as f:
            obs = f["obs"]
            idx = obs.attrs.get("_index", "_index")
            if isinstance(idx, bytes):
                idx = idx.decode()
            n = int(obs[idx].shape[0])
        sys.stderr.write("read_n_spots: anndata failed on %s (%s); used h5py obs index\n" % (h5ad_path, exc))
        return n


def git_head(root):
    def run(args):
        return subprocess.check_output(args, cwd=root).decode().strip()

    try:
        commit = run(["git", "rev-parse", "HEAD"])
        date = run(["git", "show", "-s", "--format=%cI", "HEAD"])
        dirty = run(["git", "status", "--porcelain"]) != ""
    except Exception as exc:  # pragma: no cover
        raise GeneratorError("cannot read git HEAD in %s: %s" % (root, exc))
    return commit, date, dirty


# ---------------------------------------------------------------- build


def discover_tasks(root):
    bench = os.path.join(root, "bench_data")
    tasks = []
    for name in sorted(os.listdir(bench)):
        d = os.path.join(bench, name)
        if (
            os.path.isdir(d)
            and os.path.isdir(os.path.join(d, "splits"))
            and os.path.isfile(os.path.join(d, "var_50genes.json"))
            and os.path.isdir(os.path.join(d, "adata"))
        ):
            tasks.append(name)
    if not tasks:
        raise GeneratorError("no benchmark tasks found under %s" % bench)
    return tasks


def load_tables(root):
    audit = {}
    for r in read_csv_rows(os.path.join(root, AUDIT_REL)):
        audit[(r["task"].strip(), r["sample_id"].strip())] = r
    meta = {}
    for r in read_csv_rows(os.path.join(root, META_REL)):
        meta[(r["task"].strip(), r["sample_id"].strip())] = r
    return audit, meta


def build_task_def(root, task, label_set, audit, meta, commit, commit_date, inputs_rel):
    """Return (obj, extras) where extras carries the facts the validation table reports."""
    bench = os.path.join(root, "bench_data", task)

    # ---- shipped patient folds, read from the split files
    split_dir = os.path.join(bench, "splits")
    fold_ids = sorted(
        (m.group(1) for m in (re.fullmatch(r"train_(.+)\.csv", f) for f in os.listdir(split_dir)) if m),
        key=natural_fold_key,
    )
    if not fold_ids:
        raise GeneratorError("no train_<k>.csv under %s" % split_dir)
    patient_folds = []
    id_cols = set()
    for k in fold_ids:
        tr_path = os.path.join(split_dir, "train_%s.csv" % k)
        te_path = os.path.join(split_dir, "test_%s.csv" % k)
        if not os.path.isfile(te_path):
            raise GeneratorError("train_%s.csv has no matching test file in %s" % (k, split_dir))
        tr, c1 = read_split_members(tr_path)
        te, c2 = read_split_members(te_path)
        id_cols.update([c1, c2])
        patient_folds.append(
            OrderedDict([("fold", str(k)), ("train", list(tr)), ("test", list(te))])
        )

    # ---- declared samples: the union over the shipped splits, cross-checked
    declared = sorted({s for f in patient_folds for s in f["train"] + f["test"]})
    on_disk = sorted(
        f[: -len(".h5ad")] for f in os.listdir(os.path.join(bench, "adata")) if f.endswith(".h5ad")
    )
    if set(declared) != set(on_disk):
        raise GeneratorError(
            "%s: split membership %r does not match adata/ contents %r" % (task, declared, on_disk)
        )

    # ---- per-sample records
    missing_audit, missing_meta, spot_disagreements = [], [], []
    recs = {}
    for sid in declared:
        a = audit.get((task, sid))
        m = meta.get((task, sid))
        if m is None:
            missing_meta.append(sid)
            continue
        if a is None:
            missing_audit.append(sid)
            donor_id, donor_status = None, "unverifiable"
        else:
            donor_id = blank_to_none(a["donor_id"])
            donor_status = a["donor_label_status"].strip()
            if donor_id is None:
                missing_audit.append(sid)
                donor_status = "unverifiable"

        n_spots = read_n_spots(os.path.join(bench, "adata", "%s.h5ad" % sid))
        meta_spots = blank_to_none(m.get("spots_under_tissue"))
        meta_spots = int(float(meta_spots)) if meta_spots is not None else None
        if meta_spots is not None and meta_spots != n_spots:
            spot_disagreements.append((sid, n_spots, meta_spots))

        recs[sid] = OrderedDict(
            [
                ("sample_id", sid),
                ("donor_id", donor_id),
                ("hest_patient", blank_to_none(m.get("patient"))),
                ("donor_label_status", donor_status),
                ("lab", (m.get("dataset_title") or "").strip()),
                ("lab_label_status", "unverified"),
                ("session", None),
                ("resolution_group", (m.get("resolution_group") or "").strip()),
                ("pixel_size_um", float(m["pixel_size_um"])),
                ("resolution_uncertain", to_bool(m["resolution_uncertain"], "%s/%s" % (task, sid))),
                ("n_spots", n_spots),
                ("_meta_spots", meta_spots),
                ("_st_technology", (m.get("st_technology") or "").strip()),
            ]
        )
    if missing_meta:
        raise GeneratorError("%s: samples absent from %s: %r" % (task, META_REL, missing_meta))
    if missing_audit:
        raise GeneratorError(
            "%s: samples absent from %s (written as donor_id null / unverifiable, then refused "
            "rather than inventing a donor): %r" % (task, AUDIT_REL, missing_audit)
        )
    for r in recs.values():
        if not r["lab"]:
            raise GeneratorError("%s/%s: empty dataset_title, cannot derive lab" % (task, r["sample_id"]))
        if not r["resolution_group"]:
            raise GeneratorError("%s/%s: empty resolution_group" % (task, r["sample_id"]))

    # ---- shipped vs audited donor labels
    # Under the audited label set donor_id is the audit's verdict verbatim.  Under the shipped
    # label set a donor group the audit MERGED but HEST's patient field separates is split back
    # to one donor per distinct HEST patient label -- which in this benchmark is IDC's
    # TENX95/TENX99 alone.  Every other task is unchanged.
    split_back = []
    if label_set == "shipped":
        by_donor = {}
        for sid in declared:
            by_donor.setdefault(recs[sid]["donor_id"], []).append(sid)
        for did, members in sorted(by_donor.items()):
            labels = {recs[s]["hest_patient"] for s in members}
            if len(members) > 1 and len(labels) > 1:
                if None in labels:
                    raise GeneratorError(
                        "%s: audit donor %s merges samples whose HEST patient labels differ but "
                        "at least one is missing (%r); cannot split back for the shipped label "
                        "set without inventing a label" % (task, did, sorted(map(str, labels)))
                    )
                for s in members:
                    new_id = "%s_shipped_%s" % (task, slug(str(recs[s]["hest_patient"])))
                    split_back.append((s, did, new_id))
                    recs[s]["donor_id"] = new_id
    elif label_set != "audited":
        raise GeneratorError("unknown label_set %r" % label_set)

    # ---- sessions
    sessions_used = []
    if task == "PRAD":
        assigned = set()
        for name, members in PRAD_SESSIONS.items():
            present = [s for s in members if s in recs]
            if len(present) != len(members):
                raise GeneratorError(
                    "PRAD session %s: expected %r, missing %r"
                    % (name, members, sorted(set(members) - set(present)))
                )
            donors = {recs[s]["donor_id"] for s in present}
            if len(donors) != 1:
                raise GeneratorError("PRAD session %s spans donors %r" % (name, donors))
            for s in present:
                recs[s]["session"] = name
            assigned.update(present)
            sessions_used.append((name, sorted(present), sorted(donors)[0]))
        # cross-check the sub-clustering against the pixel sizes, which is the physical
        # signature of the two scan sessions
        ranges = [
            (n, min(recs[s]["pixel_size_um"] for s in m), max(recs[s]["pixel_size_um"] for s in m))
            for n, m, _ in sessions_used
        ]
        (n1, lo1, hi1), (n2, lo2, hi2) = ranges
        if not (hi1 < lo2 or hi2 < lo1):
            raise GeneratorError(
                "PRAD session pixel-size ranges overlap: %s [%r,%r] vs %s [%r,%r]"
                % (n1, lo1, hi1, n2, lo2, hi2)
            )

    # ---- fold designs
    donors = sorted({recs[s]["donor_id"] for s in declared})
    donor_folds = []
    if len(donors) > 1:
        for d in donors:
            test = sorted(s for s in declared if recs[s]["donor_id"] == d)
            train = sorted(s for s in declared if recs[s]["donor_id"] != d)
            donor_folds.append(OrderedDict([("fold", str(d)), ("train", train), ("test", test)]))

    slide_folds = []
    if len(declared) > 1:
        for s in declared:
            slide_folds.append(
                OrderedDict(
                    [("fold", str(s)), ("train", sorted(x for x in declared if x != s)), ("test", [s])]
                )
            )

    # ---- genes
    gene_file_rel = "bench_data/%s/var_50genes.json" % task
    genes = read_gene_list(os.path.join(root, gene_file_rel))

    st_tech = sorted({recs[s]["_st_technology"] for s in declared})
    if len(st_tech) != 1 or not st_tech[0]:
        raise GeneratorError("%s: st_technology is not unique: %r" % (task, st_tech))

    samples = []
    for sid in declared:
        r = OrderedDict((k, v) for k, v in recs[sid].items() if not k.startswith("_"))
        samples.append(r)

    obj = OrderedDict(
        [
            ("task_def_version", 1),
            ("task", task),
            ("label_set", label_set),
            ("source", "hest_bench"),
            ("st_technology", st_tech[0]),
            ("repo_root_relative", True),
            (
                "paths",
                OrderedDict(
                    [
                        ("adata", "bench_data/%s/adata/{sample_id}.h5ad" % task),
                        ("patches", "bench_data/%s/patches/{sample_id}.h5" % task),
                        ("embeddings", "embeddings/%s/{encoder}/{sample_id}.h5" % task),
                        ("target_genes", gene_file_rel),
                    ]
                ),
            ),
            (
                "target_genes",
                OrderedDict(
                    [
                        ("list", genes),
                        ("n", len(genes)),
                        ("selection", GENE_SELECTION.format(gene_file=gene_file_rel)),
                        ("selection_used_test_spots", True),
                    ]
                ),
            ),
            ("samples", samples),
            (
                "flags",
                OrderedDict(
                    [(k, task in v) for k, v in sorted(FLAGS.items())]
                ),
            ),
            (
                "folds",
                OrderedDict(
                    [
                        ("patient", patient_folds),
                        ("donor", donor_folds),
                        ("slide_out", slide_folds),
                        ("random", OrderedDict(RANDOM_DESIGN)),
                    ]
                ),
            ),
            (
                "provenance",
                OrderedDict(
                    [
                        ("generated_by", "code/scripts/round3_task_defs.py"),
                        ("generated_at", commit_date),
                        ("commit", commit),
                        ("inputs", inputs_rel(task)),
                        ("pythonhashseed", os.environ.get("PYTHONHASHSEED")),
                    ]
                ),
            ),
        ]
    )

    extras = {
        "adata_counts": {s: recs[s]["n_spots"] for s in declared},
        "id_columns": sorted(id_cols),
        "spot_disagreements": spot_disagreements,
        "meta_spots_total": sum(
            recs[s]["_meta_spots"] for s in declared if recs[s]["_meta_spots"] is not None
        ),
        "donors": donors,
        "split_back": split_back,
        "sessions": sessions_used,
        "labs": sorted({recs[s]["lab"] for s in declared}),
    }
    return obj, extras


# ---------------------------------------------------------------- validation


def validate_obj(obj, schema, extras):
    """Schema validation plus the per-file assertions.  Returns an ordered result row."""
    import jsonschema

    row = OrderedDict()
    declared = [s["sample_id"] for s in obj["samples"]]
    donors = sorted({s["donor_id"] for s in obj["samples"]})
    designs = ["patient", "donor", "slide_out"]

    try:
        jsonschema.Draft7Validator(schema).validate(obj)
        row["schema_valid"] = "pass"
        schema_msg = ""
    except jsonschema.ValidationError as exc:
        row["schema_valid"] = "FAIL"
        schema_msg = "%s at %s" % (exc.message, list(exc.absolute_path))

    msgs = [schema_msg] if schema_msg else []

    ok = True
    for d in designs:
        for f in obj["folds"][d]:
            if not set(f["train"] + f["test"]).issubset(declared):
                ok = False
                msgs.append("%s fold %s leaves declared samples" % (d, f["fold"]))
    row["folds_subset_of_samples"] = "pass" if ok else "FAIL"

    ok = True
    for d in designs:
        for f in obj["folds"][d]:
            if set(f["train"]) & set(f["test"]):
                ok = False
                msgs.append("%s fold %s train/test overlap" % (d, f["fold"]))
    row["no_train_test_overlap"] = "pass" if ok else "FAIL"

    tests = [set(f["test"]) for f in obj["folds"]["patient"]]
    union, disjoint = set(), True
    for t in tests:
        if union & t:
            disjoint = False
        union |= t
    row["patient_tests_partition_samples"] = (
        "pass" if disjoint and union == set(declared) else "FAIL"
    )
    if row["patient_tests_partition_samples"] == "FAIL":
        msgs.append("patient test sets do not partition the declared samples")

    dmap = {s["sample_id"]: s["donor_id"] for s in obj["samples"]}
    if obj["folds"]["donor"]:
        held = [f["fold"] for f in obj["folds"]["donor"]]
        ok = sorted(held) == donors and len(set(held)) == len(held)
        for f in obj["folds"]["donor"]:
            if {dmap[s] for s in f["test"]} != {f["fold"]}:
                ok = False
            if {dmap[s] for s in f["train"]} & {f["fold"]}:
                ok = False
        row["donor_folds_partition_donors"] = "pass" if ok else "FAIL"
        ok2 = all(
            sorted(f["train"]) == sorted(set(declared) - set(f["test"])) for f in obj["folds"]["donor"]
        )
        row["donor_train_is_complement"] = "pass" if ok2 else "FAIL"
    else:
        row["donor_folds_partition_donors"] = "n/a"
        row["donor_train_is_complement"] = "n/a"
    if row["donor_folds_partition_donors"] == "FAIL":
        msgs.append("donor folds do not partition the donors")
    if row["donor_train_is_complement"] == "FAIL":
        msgs.append("donor fold train set is not the complement of its test set")

    if obj["folds"]["slide_out"]:
        held = [f["fold"] for f in obj["folds"]["slide_out"]]
        ok = sorted(held) == sorted(declared) and all(
            f["test"] == [f["fold"]] and sorted(f["train"]) == sorted(set(declared) - {f["fold"]})
            for f in obj["folds"]["slide_out"]
        )
        row["slide_folds_partition_slides"] = "pass" if ok else "FAIL"
    else:
        row["slide_folds_partition_slides"] = "n/a"
    if row["slide_folds_partition_slides"] == "FAIL":
        msgs.append("slide_out folds do not partition the slides")

    row["gene_count_matches_n"] = (
        "pass" if len(obj["target_genes"]["list"]) == obj["target_genes"]["n"] else "FAIL"
    )
    if row["gene_count_matches_n"] == "FAIL":
        msgs.append("gene list length != target_genes.n")

    # Spot sums: the file's per-sample n_spots must equal, sample by sample, the AnnData row
    # counts recorded at read time (extras["adata_counts"], a separate record from the object
    # being validated), the total must be their sum, and none may be zero.
    total = sum(s["n_spots"] for s in obj["samples"])
    counts = extras["adata_counts"]
    ok = (
        sorted(counts) == sorted(declared)
        and all(s["n_spots"] == counts[s["sample_id"]] for s in obj["samples"])
        and total == sum(counts.values())
        and all(s["n_spots"] > 0 for s in obj["samples"])
    )
    row["spot_sum_consistent"] = "pass" if ok else "FAIL"
    if not ok:
        msgs.append("per-sample n_spots or their sum disagrees with the AnnData read")
    row["_total_spots"] = total
    row["_notes"] = "; ".join(m for m in msgs if m)
    return row


# ---------------------------------------------------------------- main


def serialise(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=DEFAULT_ROOT)
    ap.add_argument("--outdir", default=None, help="default <root>/results/round3/task_defs")
    ap.add_argument("--schema", default=None, help="default <root>/" + SCHEMA_REL)
    args = ap.parse_args(argv)

    root = os.path.abspath(args.root)
    outdir = args.outdir or os.path.join(root, "results", "round3", "task_defs")
    schema_path = args.schema or os.path.join(root, SCHEMA_REL)
    with open(schema_path, encoding="utf-8") as fh:
        schema = json.load(fh)

    commit, commit_date, dirty = git_head(root)
    tasks = discover_tasks(root)
    audit, meta = load_tables(root)

    def inputs_rel(task):
        return [
            AUDIT_REL,
            META_REL,
            "bench_data/%s/adata/<sample_id>.h5ad" % task,
            "bench_data/%s/splits/test_<k>.csv" % task,
            "bench_data/%s/splits/train_<k>.csv" % task,
            "bench_data/%s/var_50genes.json" % task,
        ]

    # ---- build everything in memory first, so the validation table can be written first
    built = []  # (filename, obj, extras, text)
    for task in tasks:
        obj, extras = build_task_def(root, task, "shipped", audit, meta, commit, commit_date, inputs_rel)
        built.append(("%s.json" % task, obj, extras, serialise(obj)))
    if "IDC" in tasks:
        obj, extras = build_task_def(root, "IDC", "audited", audit, meta, commit, commit_date, inputs_rel)
        built.append(("IDC_audited.json", obj, extras, serialise(obj)))

    rows = []
    for fname, obj, extras, _text in built:
        v = validate_obj(obj, schema, extras)
        donors = sorted({s["donor_id"] for s in obj["samples"]})
        donor_tests = {tuple(sorted(f["test"])) for f in obj["folds"]["donor"]}
        slide_tests = {tuple(sorted(f["test"])) for f in obj["folds"]["slide_out"]}
        row = OrderedDict(
            [
                ("filename", fname),
                ("task", obj["task"]),
                ("label_set", obj["label_set"]),
                ("st_technology", obj["st_technology"]),
                ("n_samples", len(obj["samples"])),
                ("n_donors", len(donors)),
                ("n_slides", len(obj["samples"])),
                ("n_genes", obj["target_genes"]["n"]),
                ("n_patient_folds", len(obj["folds"]["patient"])),
                ("n_donor_folds", len(obj["folds"]["donor"])),
                ("n_slide_out_folds", len(obj["folds"]["slide_out"])),
                ("total_n_spots_adata", v.pop("_total_spots")),
                ("total_spots_under_tissue_metadata", extras["meta_spots_total"]),
                ("n_spot_count_disagreements", len(extras["spot_disagreements"])),
                ("slide_out_equals_donor_design", str(bool(slide_tests) and slide_tests == donor_tests)),
                ("split_id_columns", "|".join(extras["id_columns"])),
                ("n_distinct_labs", len(extras["labs"])),
                ("n_sessions", len(extras["sessions"])),
                (
                    "flags_true",
                    "|".join(k for k, val in sorted(obj["flags"].items()) if val) or "none",
                ),
            ]
        )
        notes = v.pop("_notes")
        row.update(v)
        checks = [val for key, val in v.items()]
        row["all_pass"] = "pass" if all(c in ("pass", "n/a") for c in checks) else "FAIL"
        row["notes"] = notes
        rows.append(row)

    os.makedirs(outdir, exist_ok=True)

    # ---- the validation table is written BEFORE any other output of this run
    val_path = os.path.join(outdir, "task_def_validation.csv")
    with open(val_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)

    for fname, _obj, _extras, text in built:
        with open(os.path.join(outdir, fname), "w", encoding="utf-8") as fh:
            fh.write(text)

    # ---- stdout report (the job log is the record of what was read)
    print("root            : %s" % root)
    print("commit          : %s%s" % (commit, "  (WORKING TREE DIRTY)" if dirty else ""))
    print("generated_at    : %s  (HEAD committer date, for byte-identical reruns)" % commit_date)
    print("PYTHONHASHSEED  : %r" % os.environ.get("PYTHONHASHSEED"))
    print("tasks discovered: %s" % ", ".join(tasks))
    print("outdir          : %s" % outdir)
    print("validation      : %s" % val_path)
    for fname, obj, extras, _t in built:
        print(
            "  %-18s samples=%2d donors=%2d patient_folds=%d donor_folds=%2d slide_folds=%2d "
            "genes=%d spots=%d"
            % (
                fname,
                len(obj["samples"]),
                len({s["donor_id"] for s in obj["samples"]}),
                len(obj["folds"]["patient"]),
                len(obj["folds"]["donor"]),
                len(obj["folds"]["slide_out"]),
                obj["target_genes"]["n"],
                sum(s["n_spots"] for s in obj["samples"]),
            )
        )
        for sid, n_adata, n_meta in extras["spot_disagreements"]:
            print("      SPOT DISAGREEMENT %s: adata=%d spots_under_tissue=%d" % (sid, n_adata, n_meta))
        for sid, old, new in extras["split_back"]:
            print("      shipped-label donor split: %s  %s -> %s" % (sid, old, new))
        for name, members, donor in extras["sessions"]:
            print("      session %s (donor %s): %s" % (name, donor, ",".join(members)))
        print("      labs: %s" % " | ".join(extras["labs"]))
    n_fail = sum(1 for r in rows if r["all_pass"] != "pass")
    print("files=%d  failing=%d" % (len(rows), n_fail))
    print("crc32 self-check (determinism marker): %d" % crc32_seed(commit, *[b[0] for b in built]))
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
