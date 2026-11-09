# Round 10, track `final-runs`, the kickoff

*8 November 2026. Written by the oversight chat for the hand-off to track `final-runs`, after Nicolas merged the ledger's pull request (#38). The text below is what Nicolas pastes into the Claude Science project to start the first session. The project's own instructions (`docs/project_instructions.md`, "The Claude Science project") already tell the session how to start, so the kickoff only names the track and the few facts that instructions cannot know.*

## The text to paste

> Your track is `final-runs` of round 10 in `NicWYZ/HEST-1k-replication`, on branch `round10-final-runs`, which already exists on GitHub. Your brief is `docs/round10/i01/final-runs/round10_final_runs_brief.md`. Read it with `docs/EXECUTION_RULES.md`, `docs/round10/masterplan.md`, and Nicolas's L3 answers in `docs/round10/i02/ledger/round10_ledger_L3_answers.md`, which win where they differ from the brief.
>
> You run on Longleaf. Create your own clone at `/work/users/w/e/weiyang/hest_code/round10-final-runs/` over SSH and check out the branch. If that path already exists, stop and ask me.
>
> Your track has no plan yet. Write `docs/round10/tracks/final-runs/round10_final_runs_plan.md` on the branch first, opening with a state block, before any job. Your first steps after the plan are the housekeeping of the brief's section 1 and then stage F1.
>
> The brief lives on `main` and may be revised while you run. When I tell you to check for updates, fetch `main` and read the brief again.

## What the session needs that is already in place

- **The ledger's evidence** on `main`, merged with #38, including the enumeration output that F1's acceptance test reads (`results/round10/ledger/checks/l3_split_variance_check_output.txt`).
- **The anchors' source files** on `main`, at the paths the brief names (`results/round5/ppi/E4b_rejective/e4b_grid.csv`, `results/round7/ppi/S5_numbers/run1/s5_matched_cells.csv`).
- **The numeric-claim checker** with its R7.6 fix and the round's exceptions (`code/scripts/verify_numeric_claims.py`, `.verify-exceptions`).
- **GitHub access over SSH** from Nicolas's Longleaf account (`docs/environment.md`).
- **The prediction files and the corpus** on Longleaf, read only, at the paths of the brief's section 3.
