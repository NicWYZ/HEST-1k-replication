#!/usr/bin/env python
"""Reorganise the HEST replication repository into a canonical layout.

WHY. The repo grew organically and accumulated four problems:
  1. Experiment directory names were inconsistent. HEST's benchmark.py names output
     `<exp_code>::<timestamp>`, and exp_code was chosen ad hoc per wave, so the same
     regression head appears as `faithful_pca_ridge__X`, `faithful_ridge__X`,
     `faithful_xgb__resnet50`, `a14_xgb_raw__X` and `probe_xgb_nopca__resnet50`.
  2. Runs killed at their wall limit were completed by a second job with a `_part2`
     exp_code, so one (head, encoder) pair is split across two directories -- and the
     parent additionally holds a PARTIAL task directory (the task it died entering),
     which has no results_kfold.json and must not be mistaken for a result.
  3. instrumentation/ was a flat dump of ~60 tailored diagnostic outputs spanning eight
     unrelated questions, while results/tailored/ held only one experiment.
  4. reports/ mixed narrative documents with summary CSVs.

CANONICAL LAYOUT PRODUCED
  results/faithful/<head>/<encoder>/<task>/     one of the paper's four configurations
  results/tailored/<question>/                  our own diagnostics, grouped by question
  results/summary/                              the aggregated official tables
  code/configs/<head>__<encoder>.yaml           one config per faithful run
  figures/fig_<topic>.png                       content-named, not stage-named

SELECTION RULE for results (the load-bearing part). For each (head, encoder, task) the
source is the experiment directory that actually contains
`<task>/<encoder>/results_kfold.json`. If more than one does, the newest timestamp wins.
Task directories WITHOUT that file are partial runs and are dropped. This is why the merge
is done per task rather than per directory: taking a whole directory would either discard
a completed task or resurrect a partial one.

Run with --dry-run first; it prints the full plan and touches nothing.
"""
import os, re, sys, json, shutil
from collections import defaultdict

ROOT = "/work/users/w/e/weiyang/hest_replication"
DRY = "--dry-run" in sys.argv

HEAD_OF_EXP = {"faithful_pca_ridge": "pca_ridge", "faithful_ridge": "ridge_nopca",
               "faithful_xgb": "xgb_pca", "a14_xgb_raw": "xgb_raw",
               "probe_xgb_nopca": "xgb_raw"}
DROP_EXP = {"smoke_resnet50_IDC"}          # smoke test, superseded by the faithful runs
EXP_RE = re.compile(r"^(?P<code>[A-Za-z0-9_]+?)(?P<part>_part\d+)?__(?P<enc>[A-Za-z0-9_]+)::(?P<ts>[\d-]+)$")

# tailored diagnostics: basename prefix -> question area. Longest prefix wins.
AREA = {
    "split_decomposition": "splits",
    "site_probe_v2": "site_probes", "idc_institution_probe": "site_probes",
    "spatial_block_probe": "site_probes",
    "cohort_shift": "shift", "across_task_shift": "shift", "site_shift_matched": "shift",
    "count_diagnostics_v2": "counts",
    "morphology_summary_v2": "morphology", "morphology_qc": "morphology",
    "fig3e_gate": "morphology", "patch_scale_sources": "morphology",
    "alpha_sweep": "regularization",
    "heldout_gene_check": "genes",
    "stage4a_integrity": "integrity", "stage4a_summary": "integrity",
    # gitignored parquet intermediate from the Figure 3.e gate; filed with its
    # experiment so the untracked working tree matches the committed layout
    "fig3e_per_spot": "morphology",
    "row_identity_check": "integrity", "sample_metadata": "integrity",
}
# superseded by a v2 rerun; git history retains them
DROP_TAILORED = ("split_comparison", "site_predictability", "count_diagnostics.csv",
                 "morphology_summary__")
SUMMARY = {"results_encoder.csv", "results_task.csv", "results_gene.csv", "results_split.csv",
           "head_comparison_paper9.csv", "faithful_pca_ridge_task_matrix.csv",
           "discrepancy_table_v2.csv", "scaling_law_inputs.csv", "hest_leaderboard_030426.csv"}
DROP_REPORTS = {"final_stage_report.md", "concepts_explained.md", "HEST_replication_handoff.md",
                "stage01_report.md", "replication_memo.md", "replication_memo_v2.md",
                "motivation_draft.md", "discrepancy_table.csv", "discrepancy_encoder_level.csv",
                ".gitkeep"}
FIG_RENAME = {"stage3_replication.png": "fig_replication_fidelity.png",
              "stage4b_split_decomposition.png": "fig_split_decomposition.png",
              "stage4c_count_diagnostics_v2.png": "fig_count_diagnostics.png",
              "stage4d_site_probe_v2.png": "fig_site_predictability.png"}
DROP_FIGS = {"stage4b_count_diagnostics.png", "stage4c_split_comparison.png",
             "stage4d_site_predictability.png", ".gitkeep"}
SCRIPT_RENAME = {"count_diagnostics_v2.py": "count_diagnostics.py",
                 "morphology_features_v2.py": "morphology_features.py",
                 "site_probe_v2.py": "site_probe.py"}
DROP_SCRIPTS = {"count_diagnostics.py", "morphology_features.py", "site_predictability.py",
                "split_comparison.py", "split_comparison_v2.py"}

plan = []          # (kind, src, dst)  dst None => delete
def act(kind, src, dst=None): plan.append((kind, src, dst))

# ---------------------------------------------------------------- results/faithful+tailored
# index every (head, encoder, task) -> candidate source dirs that have results_kfold.json
cand = defaultdict(list)
extra = {}         # (head, enc) -> exp dir holding dataset_results.csv (newest)
partial = []
for tree in ("faithful", "tailored"):
    base = f"{ROOT}/results/{tree}"
    if not os.path.isdir(base): continue
    for exp in sorted(os.listdir(base)):
        p = os.path.join(base, exp)
        if not os.path.isdir(p): continue
        # DROP_EXP is checked BEFORE the regex: the smoke-test directory is named
        # `smoke_resnet50_IDC::<ts>` with no `__<encoder>` segment, so it fails to parse
        # and would otherwise be reported as unclassified rather than dropped.
        if exp.split("::")[0] in DROP_EXP:
            act("DELETE_DIR", p); continue
        m = EXP_RE.match(exp)
        if not m:
            act("SKIP_UNPARSED", p); continue
        code, enc, ts = m.group("code"), m.group("enc"), m.group("ts")
        if code in DROP_EXP or code.replace("_part2", "") in DROP_EXP:
            act("DELETE_DIR", p); continue
        head = HEAD_OF_EXP.get(code.replace("_part2", ""))
        if head is None:
            act("SKIP_UNKNOWN_HEAD", p); continue
        for task in sorted(os.listdir(p)):
            tp = os.path.join(p, task)
            if not os.path.isdir(tp): continue
            kf = os.path.join(tp, enc, "results_kfold.json")
            if os.path.isfile(kf):
                cand[(head, enc, task)].append((ts, tp, enc))
            else:
                partial.append(tp)
        dr = os.path.join(p, "dataset_results.csv")
        if os.path.isfile(dr):
            prev = extra.get((head, enc))
            if prev is None or ts > prev[0]: extra[(head, enc)] = (ts, dr)

for (head, enc, task), srcs in sorted(cand.items()):
    ts, tp, e = max(srcs, key=lambda t: t[0])
    dst = f"{ROOT}/results/faithful/{head}/{enc}/{task}"
    act("MOVE_TASK", tp, dst)
    if len(srcs) > 1:
        for ts2, tp2, _ in srcs:
            if tp2 != tp: act("DROP_OLDER_DUP", tp2)
for (head, enc), (ts, dr) in sorted(extra.items()):
    act("MOVE_FILE", dr, f"{ROOT}/results/faithful/{head}/{enc}/dataset_results.csv")
for tp in partial: act("DROP_PARTIAL_TASK", tp)

# ---------------------------------------------------------------- instrumentation -> tailored
INST = f"{ROOT}/instrumentation"
if os.path.isdir(INST):
    for b in sorted(os.listdir(INST)):
        sp = os.path.join(INST, b)
        if not os.path.isfile(sp): continue
        if b == "PROVENANCE.txt":
            act("MOVE_FILE", sp, f"{ROOT}/results/tailored/PROVENANCE.txt"); continue
        if any(b.startswith(d) or b == d for d in DROP_TAILORED):
            act("DELETE_FILE", sp); continue
        hit = None
        for k in sorted(AREA, key=len, reverse=True):
            if b.startswith(k): hit = k; break
        if hit is None:
            act("SKIP_UNCLASSIFIED", sp); continue
        # Drop the now-meaningless _v2 marker (the v1 outputs are being removed) -- but ONLY
        # from the SCRIPT-NAME stem, never blanket. A bare b.replace("_v2","",1) corrupted
        # `split_decomposition__uni_v2.csv` into `__uni.csv`, because the first "_v2" in that
        # name is the ENCODER uni_v2, not a version marker. Strip by matching known stems.
        V2_STEMS = ("count_diagnostics_v2", "morphology_summary_v2", "site_probe_v2")
        nb = b
        for st in V2_STEMS:
            if b.startswith(st):
                nb = st.replace("_v2", "") + b[len(st):]
                break
        act("MOVE_FILE", sp, f"{ROOT}/results/tailored/{AREA[hit]}/{nb}")

# ---------------------------------------------------------------- reports -> summary / delete
REP = f"{ROOT}/reports"
if os.path.isdir(REP):
    for b in sorted(os.listdir(REP)):
        sp = os.path.join(REP, b)
        if not os.path.isfile(sp): continue
        if b in SUMMARY:      act("MOVE_FILE", sp, f"{ROOT}/results/summary/{b}")
        elif b in DROP_REPORTS: act("DELETE_FILE", sp)
        else:                 act("SKIP_UNCLASSIFIED", sp)

# ---------------------------------------------------------------- configs
CFG = f"{ROOT}/code/configs"
for b in sorted(os.listdir(CFG)):
    sp = os.path.join(CFG, b)
    if not os.path.isfile(sp): continue
    stem = b[:-5] if b.endswith(".yaml") else b
    if stem.startswith("h1_") or stem.startswith("pilot_") or "smoke" in stem or "_part2" in stem:
        act("DELETE_FILE", sp); continue
    done = False
    for pre, h in HEAD_OF_EXP.items():
        if stem.startswith(pre + "__"):
            act("MOVE_FILE", sp, f"{CFG}/{h}__{stem.split('__', 1)[1]}.yaml"); done = True; break
    if not done: act("SKIP_UNCLASSIFIED", sp)

# ---------------------------------------------------------------- figures + scripts
FIG = f"{ROOT}/figures"
for b in sorted(os.listdir(FIG)):
    sp = os.path.join(FIG, b)
    if not os.path.isfile(sp): continue
    if b in FIG_RENAME:  act("MOVE_FILE", sp, f"{FIG}/{FIG_RENAME[b]}")
    elif b in DROP_FIGS: act("DELETE_FILE", sp)
    else:                act("SKIP_UNCLASSIFIED", sp)

SCR = f"{ROOT}/code/scripts"
for b in sorted(os.listdir(SCR)):
    sp = os.path.join(SCR, b)
    if not os.path.isfile(sp): continue
    if b in DROP_SCRIPTS:      act("DELETE_FILE", sp)
    elif b in SCRIPT_RENAME:   act("MOVE_FILE", sp, f"{SCR}/{SCRIPT_RENAME[b]}")

# ---------------------------------------------------------------- report + execute
kinds = defaultdict(int)
for k, s, d in plan: kinds[k] += 1
print("=== PLAN ===")
for k in sorted(kinds): print(f"  {k:22s} {kinds[k]:5d}")
unclass = [s for k, s, d in plan if k.startswith("SKIP")]
if unclass:
    print("\n!!! UNCLASSIFIED (refusing to proceed):")
    for s in unclass: print("   ", s.replace(ROOT + "/", ""))
    sys.exit(1)
print("\n=== sample moves ===")
for k, s, d in plan[:6] + plan[-6:]:
    print(f"  {k:22s} {s.replace(ROOT+'/','')}" + (f"\n      -> {d.replace(ROOT+'/','')}" if d else ""))
if DRY:
    json.dump([[k, s, d] for k, s, d in plan], open("/tmp/reorg_plan.json", "w"), indent=1)
    print(f"\nDRY RUN: {len(plan)} operations planned, nothing changed.")
    sys.exit(0)

n_mv = n_rm = 0
for k, s, d in plan:
    if d is None:
        if os.path.isdir(s):  shutil.rmtree(s); n_rm += 1
        elif os.path.isfile(s): os.remove(s);   n_rm += 1
    else:
        os.makedirs(os.path.dirname(d), exist_ok=True)
        if os.path.isdir(s) and os.path.isdir(d):
            for item in os.listdir(s):
                shutil.move(os.path.join(s, item), os.path.join(d, item))
            shutil.rmtree(s)
        else:
            shutil.move(s, d)
        n_mv += 1
# prune now-empty directories
for base in (f"{ROOT}/results/faithful", f"{ROOT}/results/tailored", f"{ROOT}/instrumentation",
             f"{ROOT}/reports"):
    for dirpath, dirnames, filenames in os.walk(base, topdown=False):
        if not dirnames and not filenames:
            os.rmdir(dirpath)
for d in (f"{ROOT}/instrumentation", f"{ROOT}/reports"):
    if os.path.isdir(d) and not os.listdir(d): os.rmdir(d)
print(f"\nEXECUTED: {n_mv} moved, {n_rm} removed.")
