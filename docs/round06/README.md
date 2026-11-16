# Round 6, the cheatsheet experiment (11 to 13 October 2026), moved to `NicWYZ/textual-st-histology`

Round 6 was David's cheatsheet experiment and its extension on held-out CCRCC patients. A writer agent saw labelled spots and wrote a text cheatsheet of limited size, and a separate predictor agent (Opus 5.5, one trial per cell, medium effort after the pilot) used only that cheatsheet to predict 50 genes from H&E patches.

## What the round established

- On the slide the writer had seen, the mean within-slide Pearson reached 0.8 only at the largest size, 0.903 at 262,144 bytes, and only by copying, since that cheatsheet listed every spot with its 50 gene values (`docs/round06/i03/cheatsheet/round06_cheatsheet_final_decisions.md`, section 2 item 1).
- On unseen spots no cheatsheet, and no session holding the labels, beat the `uni_v2` benchmark head fitted on the same spots: 0.621 against 0.757 on an unseen region and 0.672 against 0.683 on a second patient, the latter within one trial's noise (same file, item 2).
- In the extension on three held-out CCRCC patients, zero-shot prediction scored $-0.009$, every one of nine rubric-bound cheatsheets from 256 to 65,536 bytes beat it at 0.041 to 0.158, accuracy did not rise with size (rank correlation $-0.017$), and none reached the `uni_v2` head at 0.184 (`docs/round06/i06/cheatsheet/round06_cheatsheet_C7_decisions.md`, section 2 items 1 to 3).

These hold for one model, one trial per cell, and writers that learned from a few patients. The round did not test David's proposal of a database written over many training pairs. The paths above are in the new repository.

## Where the work is

The round's record, scripts and results are in the private repository `NicWYZ/textual-st-histology`, which holds the whole textual project, at the paths they had here. Its `docs/round06/README.md` is the round's summary, and every path under `docs/round06/`, `results/round6/` or `code/scripts/round6_cheatsheet*` in this repository's documents resolves there. The copy was made from commit `33d7b1e98565110256762a28e79254aea0b9b72f` of this repository and checked by md5 for all 274 files. The round's tags (`round6-cheatsheet-C1`, `round6-cheatsheet-C5`, `round6-cheatsheet-C7`, `round6-cheatsheet-final`, `round6-close`) and the history of every moved file stay in this repository.

## Presented outside the project

The advisor meeting of 12 October discussed round 6, and the textual line continued in its own repository after it. What the advisors said is recorded in `docs/round07/README.md` (formerly `round07_advisor_directions.md`, at tag `record-full-2026-11`).
