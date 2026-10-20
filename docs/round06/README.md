# Round 6, moved to the textual project's repository

Round 6 was David's cheatsheet experiment (11 to 13 October 2026) and its extension on held-out CCRCC patients. A writer agent saw labelled spots and wrote a text cheatsheet of limited size, and a separate predictor agent used only that cheatsheet to predict expression.

## What the round established

With a size-limited cheatsheet, Opus did not beat a pathology foundation model on unseen spots, and it reached 0.8 on seen spots only by copying. In the extension on held-out CCRCC patients, any rubric-bound cheatsheet helped, size did not, and none reached the pathology model. The full account is in the new repository's `docs/round06/README.md`.

## Where the record is now

On 19 October 2026, by Nicolas's decision, the round's record, scripts and results moved to the private repository `NicWYZ/textual-st-histology`, which now holds the whole textual project. That repository was called `NicWYZ/hest-r6-data` before the move. The files there keep the paths they had here, so `docs/round06/README.md` in that repository is the round's reading guide, and every path written in this repository's documents under `docs/round06/`, `results/round6/` or `code/scripts/round6_cheatsheet*` resolves there. The copy was made from commit `33d7b1e98565110256762a28e79254aea0b9b72f` of this repository and checked by md5 for all 274 files. `docs/moved.md` lists what moved.

The round's git tags (`round6-cheatsheet-C1`, `round6-cheatsheet-C5`, `round6-cheatsheet-C7`, `round6-cheatsheet-final` and `round6-close`) stay in this repository, together with the history of every moved file.

The round 5 explainer `00_prep/round06_round5_results_explained.md` stays in this folder, since it belongs to the PPI and conformal work and was only written during round 6.
