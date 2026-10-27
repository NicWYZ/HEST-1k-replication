# Round 9, track newtopic, the closing report

*27 October 2026. Written by the newtopic session after Nicolas chose O1 ("O1") in answer to the interval 3 report. Frozen once committed. It closes track `newtopic` (option C) of round 9.*

## 1. The decision

The interval 3 report (`docs/round09/i03/newtopic/round09_newtopic_i03_report.md`, section 5) offered O1 (close the track), O2 (keep F1 as a remark) and O3 (a direction from outside the session). Nicolas chose O1 on 27 October. The track ends here and starts no further work. Its branch, `claude-science-newtopic`, stays as it is until Nicolas decides how the round 9 branches reach `main` (decision D4 in `CLAUDE.md`).

## 2. What the track established

The track looked for a statistics-forward methods direction outside clustered PPI and hierarchical conformal prediction, using HEST-1k and ACS PUMS 2018. It found none with an open core that would carry a paper. Each reading below names its file.

1. **Interval 1, the search.** Five proposer lenses wrote 45 raw ideas, of which they found 24 fully and 21 partly in print. Three open-problem miners and nine checkers found nothing open. Three remainders (BOUNDARY, LLGCLUSTER, RRRIDGE) were partly open and thin (`docs/round09/i01/newtopic/round09_newtopic_i01_report.md`, `results/round9/newtopic/newtopic_structured_results.json`).
2. **Interval 1, the data.** Pathology encoders agree with each other far more than with the labels, their predictions are smoother than the labels, and the HEST Xenium files on Longleaf are pseudo-spots (`results/round9/newtopic/n3_predictions_scored.md`).
3. **Interval 2, breadth first.** Four of five feasibility tracks stopped at lemma or proposition size, and fresh auditors confirmed the three stops they examined. Local-linear boundary tests lose power at estimated boundaries (F2). A noise ceiling identified across scales needs a latent shape beyond Poisson noise (F3). An iid performance bound over-claims only when the features carry the donor shift, and its group correction is one leverage term inside Atanasov et al.'s framework (F4). Four fresh checkers passed nothing (F5) (`docs/round09/i02/newtopic/round09_newtopic_i02_report.md`, `results/round9/newtopic/i02/`).
4. **Interval 3, F1.** Ridge reduced-rank regression detects a rank-one response factor below the threshold of PCA of the outcomes. Its threshold and overlap, derived and validated by the session, are a corollary of Liu, Liu, Pan, Zhang and Zhang (arXiv:2310.13939) applied conditionally on the features, and a fresh auditor confirmed this with small technical gaps (`docs/round09/i03/newtopic/round09_newtopic_i03_report.md`, `results/round9/newtopic/i03/`).

## 3. Corrections and withdrawn readings

- Interval 2's report called F1 "not found in print and not a direct case of the spiked separable theorem". The second half stands for Ding and Yang's theorem, but interval 3 found that F1 is a direct case of Liu et al. once one conditions on the features. The reading that F1 is a candidate core is withdrawn (interval 3 report, section 3).
- In interval 2, F1's subagent first stopped the track and a fresh checker overturned the stop. Interval 3 restored a stop on other grounds. The stop rules themselves worked as written.

## 4. Carried forward

- **For the paper.** Nothing from this track is a candidate core. If the project wants it, F1's ridge-over-least-squares comparison can be a remark citing Liu et al. (option O2, not chosen).
- **Lesson for later searches.** In every interval, candidates that a first literature search found open fell to a deeper second search, often to papers outside the field first searched (random-matrix signal processing for F1). Directions the session generates itself in random-matrix and spatial statistics sit in well-mined ground. A later search should start from a problem someone has met in practice (option O3), run the deep search before any derivation, and include signal-processing and econometrics venues.
- **Open decisions**, all Nicolas's and unchanged by this track: D1 (venue and lead result) and D4 (how the round 9 branches reach `main`), in `CLAUDE.md`.

## 5. Read first next round

The three interval reports named in section 2 and this report. For F1 also read `results/round9/newtopic/i03/audit/audit_F1_corollary.md`.
