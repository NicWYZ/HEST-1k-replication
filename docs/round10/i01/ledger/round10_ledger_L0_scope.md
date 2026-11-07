# Round 10, track `ledger`, L0 scope

*7 November 2026. Written by the oversight chat under `round10_ledger_brief.md`, after Nicolas's answers of 7 November (DATA, D5, V, O3; `masterplan.md`, amendments). It fixes the paper's sections, the results each rests on, where the open questions bite, and the data the round uses. L1 subagents write the ledger rows from it, one per section.*

## 1. The paper's sections and the results each rests on

Numbers in parentheses are the finding ids of `../../00_prep/round10_findings_survey.md`, section 2.

| # | Section | Results it rests on | Open questions that bite |
|---|---|---|---|
| S1 | Motivation. Predicted expression is used as if measured; the donor is the unit of every uncertainty statement | D2, D3, D9, B1, A4 | none |
| S2 | Data. The HEST tasks, their audit, the depth factor, INT5, ACS | D6, D7, D10 to D14; the corpus extension of section 3 | DATA (decided), D5 |
| S3 | Prediction sets for a new donor (Topic A) | A1 to A10; the institution axis once the corpus tasks exist | P (whether the section stays), the GHCP full-text check |
| S4 | Valid inference with predicted expression (Topic B) | B2 to B12 | E (estimator), R7-6 (coefficient), D5 |
| S5 | How many donors, and which. Few-donor coverage, the frontier, regimes, allocation, balanced selection, the probe | B8, B11, B13, B14, E1 to E7 | V, Q1 (deferred), R7-7, R7-5, O5 |
| S6 | Limits and cautions. Spot-weighted estimands, the level term, same-cluster tuning, bootstraps, superpopulation intervals, published few-cluster comparators | B5, B6, B12 | none |

For every result the ledger row gives the existing method applied, its source with an identifier that was opened and its read level, the implementing script in `code/scripts/`, what the record validated and where, and what is missing. The subagents' reading of each source is recorded by section and page. A gap is recorded only with the queries that failed to fill it.

## 2. What the ledger decides or recommends at L3

- **E, the estimator** (the ledger decides). After reading Williams (1961), Mickey (1959) if retrievable, Sanguiao Sande and Zhang (2020), Lu, Shi, Liu and Ding (2025) and An, Dagdoug, Haziza and Tillé (2026): which exactly unbiased form the final runs use, with which variance estimator, from which source.
- **R7-6 and P** (the ledger recommends, Nicolas decides).
- **V** (decided by Nicolas to be settled by the literature and by testing). The ledger searches survey sampling for bounds on a cluster's share of the design variance, or for how few-cluster designs state such a condition, and the final runs test regime B's numbers with and without it.
- **D5** (decided to be settled by testing). The ledger records the spatial transcriptomics conventions for the expression scale an inference is made about, with sources; the final runs carry both scales.

## 3. The data the round uses

Nicolas decided on 7 November to use as much of the existing data as possible. The round therefore uses the four tasks in hand (CCRCC, INDIANA_KIDNEY, LUNG_XENIUM, ACS PUMS 2018) and extends to the federated project's corpus on Longleaf (`/work/users/w/e/weiyang/st_fed_learn/data/`, read only, no new download; `NicWYZ/ST-Fed-Learn`, `docs/round01/tracks/data/data_card.md`). The corpus holds every human HEST-1k sample with harmonised raw counts, five encoders' embeddings and a registry of samples, centers and panels.

**Criteria for a task in the paper.** At least 10 donors, since HCP needs $K + 1 \ge 1/\alpha$ at $\alpha = 0.1$ and few-donor inference needs more; donor labels audited on that task, since HEST's own labels were wrong in both directions on the benchmark subset (`docs/environment.md`); one platform per task; the measured panel's intersection or its top-50 genes as the gene set, as the corpus's task definitions already provide.

**Candidate tasks from the data card** (samples, centers, donors): kidney Visium (62, 6, 50), lung Xenium (24, 4, 22), brain Visium (42, 9, 19), bowel Visium (73, 10, 16), breast Xenium (21, 5, 11), breast Visium (10, 9, 10). The single-center groups (breast ST 108 samples, skin Visium 63, heart Visium 42) are candidates if their donor counts pass. Prostate Visium (35, 6, 7) and the rest fail the donor criterion. The final-runs track's data stage confirms every count from the registry, audits donor labels, records licences (115 corpus samples carry none and 29 are marked internal), and builds the held-out prediction files (a ridge head on frozen embeddings, donor and center held out) with provenance stamps. Kidney Visium contains CCRCC and INDIANA_KIDNEY, so the paper's kidney results become one multi-center task with the two earlier tasks as its anchors.

**What the extension adds to the questions.** The institution axis for S3 (leave-one-center-out calibration on tasks with 4 to 10 centers), donor-rich tasks for S4 and S5 (kidney at 50 donors tests the frontier's required-cluster numbers at twice the earlier $G$), and the depth factor and INT5 as general facts for S2.

## 4. What L1 does not do

It does not derive, recommend new methods, read the lab's unpublished manuscript, or contact anyone. It does not decide E, P, R7-6 or V. It records what exists, where, and what is missing.
