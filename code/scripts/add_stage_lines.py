#!/usr/bin/env python
"""Add a `Stage:` line to the docstring of every code/scripts/ file missing one.

Stage: closeout repository refresh (deck_figures_and_repo_update.md section 2.5).

Every script already has a module docstring; fourteen do not say which stage they
belong to or which memo clause asked for them, which is the part a reader needs
first. The line is inserted after the docstring's summary line.

Each edit is compiled before it is kept, and reverted if it does not compile.
An earlier automated multi-file patch in this project broke every file it
touched, and the only reason nothing was lost was that its guard reverted them;
this keeps that guard.
"""
import ast
import os
import sys

ROOT = os.environ.get("HEST_ROOT", "/work/users/w/e/weiyang/hest_replication")
D = f"{ROOT}/code/scripts"
APPLY = "--apply" in sys.argv

STAGE = {
    "aggregate_results.py":
        "faithful replication, results aggregation "
        "(HEST_replication_handoff.md stage 4)",
    "build_summary_tables.py":
        "faithful replication, derived summary tables "
        "(HEST_replication_handoff.md stage 4); rerun after any results change",
    "reorganize_repo.py":
        "round-1 closeout, one-off repository reorganisation; kept as the record "
        "of how the current layout was produced",
    "round2_r1b_d3_d4.py":
        "R1b, directives D3 and D4 (round2_R1_decisions.md) -- the COAD patient-label "
        "audit and the pixel-size cross-check against HEST's embedded values",
    "round2_r1b_ladder.py":
        "R1b, the four-rung R2 ladder (round2_R1_decisions.md Decision 2)",
    "round2_r1_fix_schema.py":
        "R1, one-off schema repair of the prediction parquets after the mixed-type "
        "fold column killed a write; kept as the record of the fix",
    "round2_r2_fold_hvg.py":
        "R2, per-fold training-only gene selection "
        "(round2_R1_decisions.md directive D2)",
    "round2_r2_gene_check.py":
        "R2, verbatim reimplementation of the benchmark's gene selection, run as a "
        "gate before the fold comparison (round2_R1_decisions.md directive D2)",
    "round2_r2_rank_supplement.py":
        "R2 supplement, ranking sensitivity on a FIXED gene set "
        "(round2_R5_decisions.md directive 2.6)",
    "round2_r5c_replicate_leak.py":
        "R5c, replicate leak generalised to every known same-donor pair "
        "(round2_R5_decisions.md directive 2.2)",
    "round2_r5_donor_out.py":
        "R5, corrected donor-grouped split arm after the audit found two samples "
        "labelled as separate patients are one donor",
    "round2_r5_replicate_leak.py":
        "R5, first replicate-leak measurement on IDC; superseded for coverage by "
        "round2_r5c_replicate_leak.py, which extends the same design to READ",
    "round2_split_v4.py":
        "R3, the five split designs including buffered blocks and "
        "leave-one-slide-out (round2_execution_plan.md stage R3)",
    "verify_numeric_claims.py":
        "closeout, the numeric-claim sweep "
        "(round2_closeout_decisions.md; extended for the deck in section 1.3)",
    'across_task_shift.py':
        'tailored analysis, cross-task generalisation',
    'alpha_sweep.py':
        "tailored analysis, ridge-penalty sweep establishing the benchmark's fixed alpha is far from optimal",
    'build_instrumentation.py':
        'faithful replication stage 4, building the joined per-spot prediction tables',
    'check_instrumentation.py':
        'faithful replication stage 4, verification of the joined tables against the raw predictions',
    'cohort_shift.py':
        'tailored analysis, cohort-source probe; confounded by construction, since most sources occur in one task only',
    'count_diagnostics.py':
        'tailored analysis, the observation model: Poisson against negative binomial against zero-inflated NB',
    'fig3e_gate.py':
        'faithful replication, the Figure 3e acceptance gate',
    'heldout_gene_check.py':
        'tailored analysis, first look at gene-selection leakage; superseded by round2_r2_fold_hvg.py, which measures selection and ranking separately',
    'inventory_hest_bench.py':
        'faithful replication stage 1, inventory of the hest-bench snapshot',
    'make_manifest.py':
        'closeout, regenerating MANIFEST.md for the large artifacts left on Longleaf (deck_figures_and_repo_update.md section 2.4)',
    'metadata_join.py':
        'faithful replication stage 4, joining HEST sample metadata onto the prediction tables',
    'morphology_features.py':
        'tailored analysis, per-spot nuclear morphology (v1); superseded by morphology_features_v2.py',
    'morphology_qc.py':
        'tailored analysis, quality control on the morphology features',
    'reorganize_repo.py':
        'round-1 closeout, one-off repository reorganisation; kept as the record of how the current layout was produced',
    'round2_head_intercept.py':
        'R1, the three-head intercept refit (round2_execution_plan.md stage R1); superseded by round2_r1b_heads.py, which adds the exact and float64 solver families',
    'round2_r0_resolution_columns.py':
        'R0, adding pixel_size_um and resolution_group (round2_execution_plan.md stage R0 item 2)',
    'round2_r1b_heads.py':
        'R1b, the intercept refit across three solver families including float64 (round2_R1_decisions.md Decision 1)',
    'round2_r4_probes.py':
        'R4, the slide, session, resolution and composition-adjusted probes (round2_R3_decisions.md decision 2.1)',
    'round2_r5d_confusion.py':
        'R5d, the IDC partner-confusion probe (round2_R5_decisions.md directive 2.2)',
    'round2_r6_donor_variance.py':
        'R6, nested variance components on the audited donor labels (round2_R5_decisions.md directive 2.3)',
    'round2_r6_theta.py':
        'R6, the slide-level estimand theta1 (round2_R5_decisions.md directive 2.4)',
    'round2_r7_pergene.py':
        'R7, the per-gene decomposition (round2_R5_decisions.md directive 2.5)',
    'site_probe.py':
        "tailored analysis, first site/cohort probe; its labelling was withdrawn in round 2 (see the README's benchmark-properties section)",
    'site_shift_matched.py':
        'tailored analysis, the matched site-shift contrast whose 0.0419 scalar round 2 withdrew as not an institution contrast',
    'spatial_block_probe.py':
        'tailored analysis, slide-identity probe under spatial-block cross-validation',
    'split_decomposition.py':
        'tailored analysis, the v3 split decomposition; extended by round2_split_v4.py, which adds the buffered and size-matched arms',
    'stage5_integration.py':
        'faithful replication stage 5, fine-tuning integration; never ran (CUDA-only against a saturated GPU queue) and is kept as the unexecuted plan',
    'verify_row_identity.py':
        'faithful replication stage 4, row-identity check between the joined tables and their sources',
}

changed, skipped, failed = [], [], []

for fn, stage in sorted(STAGE.items()):
    p = f"{D}/{fn}"
    if not os.path.exists(p):
        skipped.append((fn, "absent"))
        continue
    src = open(p).read()
    try:
        doc = ast.get_docstring(ast.parse(src))
    except SyntaxError as e:
        skipped.append((fn, f"does not parse: {e}"))
        continue
    if not doc:
        skipped.append((fn, "no module docstring"))
        continue
    if "Stage:" in doc:
        skipped.append((fn, "already has a Stage line"))
        continue

    # Insert after the docstring's first line, keeping a blank line around it.
    first = doc.split("\n", 1)[0]
    i = src.find(first)
    if i < 0:
        skipped.append((fn, "summary line not locatable in source"))
        continue
    cut = i + len(first)
    new = src[:cut] + f"\n\nStage: {stage}." + src[cut:]

    try:
        compile(new, p, "exec")
    except SyntaxError as e:
        failed.append((fn, str(e)))
        continue
    if APPLY:
        open(p, "w").write(new)
        # Re-read and re-compile what is actually on disk, then revert if broken.
        back = open(p).read()
        try:
            compile(back, p, "exec")
        except SyntaxError as e:
            open(p, "w").write(src)
            failed.append((fn, f"reverted: {e}"))
            continue
    changed.append(fn)

print(f"{'APPLIED' if APPLY else 'DRY RUN'}")
print(f"\nwould add a Stage line to {len(changed)} scripts:")
for fn in changed:
    print(f"  {fn}")
if skipped:
    print(f"\nskipped {len(skipped)}:")
    for fn, why in skipped:
        print(f"  {fn}: {why}")
if failed:
    print(f"\nFAILED (left unchanged) {len(failed)}:")
    for fn, why in failed:
        print(f"  {fn}: {why}")
    sys.exit(1)
