# Is this a stopping point? The oversight chat's answer of 7 November 2026

*Written for Nicolas, who asked before round 10 starts whether the project has reached the point where what it first set out to do is complete, whether the questions asked at the start are answered adequately, whether all available data have been used, and whether the federated project's corpus is of use. Numbers are quoted from the files named; the data card figures are from `NicWYZ/ST-Fed-Learn`, `docs/round01/tracks/data/data_card.md` and `docs/round01/i02/data/round01_data_G2_report.md`, read on 7 November.*

## 1. Not a stopping point

The project has answered its two questions in method and in part in substance, and has not finished either. Three things stand between the record and a paper that answers them adequately.

**The inference numbers are not final.** Every tuned interval of rounds 5 to 7 was computed with round 5's estimator and variance, which round 8 found to be Williams' estimator without one factor and round 9 found to inflate widths by 1.09 to 1.53 times on HEST (`docs/round09/i03/fewcluster/round09_fewcluster_williams.md`). Nothing in the record reports the Topic B answers with a corrected, cited estimator.

**Topic A's original axis was never measured.** The proposal asked how coverage behaves when the held-out patient comes from a different institution or technology. Round 3 retired that framing because HEST-1k's benchmark subset has no organ and technology cell with three laboratories at three donors (root `README.md`, known limitation 14), and the project answered with the donor axis instead. The federated corpus changes that (section 3).

**The "how many measured slides" deliverable is answered only on three tasks with 15 to 25 donors.** The frontier says a scale-free guarantee at $G = 24$ needs 13 labelled donors under a 3-standard-deviation restriction (`results/round9/fewcluster/feasibility/s3_required_n.csv`), and the exactly unbiased forms cover 0.84 to 0.86 at 8 (`round09_fewcluster_williams.md`, section 2). Whether these hold on tasks with 50 donors or across centers is untested.

## 2. What is answered, and how well

| Question from the proposal | Answer in the record | Adequate? |
|---|---|---|
| Are a model's implied intervals honest for a new donor? | No. Spot-level conformal covers 0.802 donor-out against 0.894 random (`docs/round03/i01/exec/round3_A1_stage_report.md`) | yes, on the donor axis |
| Does the ranking by Pearson match the ranking by calibration? | The coverage ordering by calibration design is the same for all twelve encoders, so calibration is a property of the design, not the encoder | yes |
| How does coverage degrade across sites or technologies? | Not measured; HEST-1k's benchmark subset has no institution axis | no |
| What valid prediction set should be used, and at what width? | HCP with no labelled target spots, the target donor's own full conformal set from 9 labelled spots, GHCP from 12 calibration donors (`results/round5/conformal/W5_map/w5_report_numbers.csv`) | yes, on round 3's predictor; a rerun on the final prediction files is pending |
| A valid interval for $\theta$ that is narrower when the predictor is good | The model-assisted difference estimator under donor sampling, with the gain through cluster-level accuracy; 0.845 to 0.891 width ratio on CCRCC (`results/round3/final_report/final_report_numbers.csv`) | in method yes; the numbers need the corrected estimator |
| How many measured slides make H&E-only inference trustworthy? | 13 of 24 for a scale-free guarantee, about 8 for coverage near 0.85 | partly; three tasks, provisional theory |
| The estimands $\theta_1$ to $\theta_3$ | $\theta_2$ and $\theta_3$ on CCRCC, INDIANA_KIDNEY and LUNG_XENIUM, $\theta_1$ as an illustration | yes, pending the normalization decision D5 |

## 3. Data used, and data available

The record used 72 benchmark samples for the replication, three tasks for the paper (CCRCC 24 donors, INDIANA_KIDNEY 25, LUNG_XENIUM 15) with predictions from three encoders, and ACS PUMS. Of the 205 samples round 7 inventoried on Longleaf (`docs/round07/i01/fedlearn/round07_fedlearn_F2_report.md`), 63 have no embeddings, and nine of the twelve benchmark encoders were never used for prediction files (`claude/round10_survey_F_assets_inventory.md` in the project docs, section 7(e)).

The federated project's corpus holds every human HEST-1k sample plus 2 STimage-1K4M slides, 691 in 108 centers, 18 organs and 6 platforms, 242 distinct donor labels, 1,459,762 patched spots, harmonised raw counts with Ensembl ids, and embeddings from five encoders, all under `/work/users/w/e/weiyang/st_fed_learn/data/` on Longleaf, written only by that project's data track. Fifteen organ and platform pairs have three or more centers, among them kidney Visium (62 samples, 6 centers, 50 donors), bowel Visium (73, 10, 16), brain Visium (42, 9, 19), lung Xenium (24, 4, 22), breast Xenium (21, 5, 11) and prostate Visium (35, 6, 7).

**It is of use, in three ways.**

1. **Topic A's institution axis exists there.** Kidney Visium with 6 centers and 50 donors, and bowel and brain with 9 to 10 centers, allow leave-one-center-out calibration, which is the question the proposal posed and round 3 could not measure.
2. **Donor-richer tasks for Topic B.** Kidney Visium at 50 donors lets the few-donor intervals, the frontier's required-cluster numbers and the design comparison be tested at $G$ twice the present tasks', and across centers.
3. **The depth factor and INT5 become testable as general facts** rather than one task's.

**What using it costs and requires.** Prediction files for each new task (a held-out ridge head on frozen embeddings, cheap on Longleaf, with the donor or center held out); an audit of the corpus's donor labels on the tasks used, since HEST's own labels were wrong in both directions on the benchmark subset (`docs/environment.md`); a note on licences, since 115 samples carry none and 29 are marked `Internal` (data card, section 3); and reading that project's tree read-only, with provenance stamped as `docs/EXECUTION_RULES.md` requires. No download is needed.

## 4. What the oversight chat recommends `[proposed]`

Round 10 as opened, with one addition. Question DATA (masterplan) decides whether the tasks extend to the corpus, and if so, the ledger's L0 scope adds a data stage to the final-runs brief (task definitions, donor audit, prediction files) before the inference and prediction-set stages. The recommendation is to extend to at least kidney Visium (the institution axis and 50 donors) and one more organ with many centers, and to keep ACS. That makes the paper answer the proposal's questions as posed, on data no earlier round had.
