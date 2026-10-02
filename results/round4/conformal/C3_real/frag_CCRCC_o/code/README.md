# frag_CCRCC_o: CCRCC o axis (round 4, conformal track, C3)

Written by frame 37664027-917b-4af5-b46c-c441036d6333 before any job ran. Methods are those of
`round4_conf_c3.py` (md5 2d8418677cf8290eec89a14c315b92cd), whose module docstring is the authority;
this file restates assumption and guarantee for the methods reported here.

Design: CCRCC at K = 10, donor sets 24 and 23_merged, encoders hoptimus0, uni_v2, resnet50, 3
calibration draws, $o \in \{5,10,25,50,100,200\}$, 20 label draws, $\alpha \in \{0.1, 0.2\}$, absolute score.
Quantile convention: $Q_\beta(\nu)=\inf\{t:\nu((-\infty,t])\ge\beta\}$ with relative tolerance $10^{-12}$;
`finite_code` records the finiteness under the released code's upward tie rule.
Evaluation spots at o > 0 are the test donor's other spots; a value of o leaving fewer than 10 is
skipped and listed in `run_info.json` (`skipped_o`).

| method | assumption | guarantee |
|---|---|---|
| pooled (o=0) | spot exchangeability of calibration and test spots | none for a new donor |
| hcp (o=0) | hierarchical exchangeability of donors | coverage >= 1-alpha under the assumption; infinite iff 1/(K+1) > alpha |
| one_per (o=0) | as hcp, one calibration spot per donor, 200 draws averaged | each draw valid under the assumption; the average is a summary, not a conformal set |
| ghcp, ghcp_noad (eta 0) | A1 group exchangeability, A2 sizes exchangeable and independent of group laws, A3 within-group exchangeability | coverage >= 1-alpha under A1-A3 (Thm 2.1); A1, A2 not established on real donors |
| ghcp_r05, ghcp_r05_noad (eta 0.5, eq. 8 pool) | as ghcp | Cor 2.6; primary eta 0.5 variant |
| ghcp_r05code (alpha 0.1 only) | as ghcp, pool one group larger as in the released code | secondary; pool rule not the paper's |
| within | labelled and evaluation spots exchangeable within donor (true by construction of the random label draw) | >= 1-alpha marginal over the label draw; infinite when 1/(o-floor(o/2)+1) > alpha |
| within_plain | as within; all o labelled spots calibrate $|r|$, no recentring | >= 1-alpha marginal over the label draw and an evaluation spot; finite from o=9 (alpha 0.1), o=4 (alpha 0.2); only the mean over the 20 draws is comparable to the guarantee |
| recentred | calibration donors' scores are a fair proxy for the test donor's centred scores (they are not) | none |

Row design per fit: 6 rows at o=0 (3 methods x 2 alphas) and, per admissible o and label draw, 15 rows
(7 non-code methods x 2 alphas + ghcp_r05code at alpha 0.1). Checked in the job before writing.
`draw` = cal_draw*20 + label_draw at o>0, cal_draw at o=0 (module convention).

Jobs: `run_ccrcc_o.py <task> <enc> <shard> <n_shards> <out>`, folds split by index mod 2.
C3.4 (CQR top-decile diagnostic): `run_c34.py`, README section added there.

## C3.4 (CQR top-decile diagnostic), `run_c34.py`

Heads: `round3_a4_scores.fit_cqr` and `cqr_predict`, imported unmodified, round 3 A4's scope: 6 evenly
spaced genes (`gene_subset`), quantiles 0.05 and 0.95, HiGHS, T pre-subsampled to 2500 spots (every fit fell
back, as in round 3), calibration draw 0 only, CCRCC donor set 24, K = 10, alpha = 0.1, 24 folds, 3 encoders.
Top decile = bin 9 of ten per-gene quantile bins of the base head's prediction pooled over the 24 test folds.
GHCP with the CQR score runs without within-group adaptation (the adaptation shrinks a mean of signed residuals,
undefined for the signed CQR score); the paired abs rows use the same no-adaptation form and the same seeds.
Assumptions and guarantees are those of the host method. Files: `c3_c34_top_decile__CCRCC.csv` (pooled
spot-gene counts over folds and 20 label draws), `c3_c34_rows__CCRCC.csv` (per fold and draw).

## Run notes

Shards: 2-way fold split (index mod 2) for the first attempt; the seven shards that hit the 55 min wall were rerun as
4-way shards (s and s+2 of 4 for a failed s of 2). 23_merged hoptimus0 shard 0of2 hit the wall after its outputs were
written (all rows present, row check passed) and was kept; its two queued reruns were cancelled.
Merged tables `*__CCRCC.csv` are concatenations of the shard tables, merged locally.
