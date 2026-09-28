# P6 lead verification (2026-09-28)

Checked by the lead from the handed-back files, the task definitions and round 2's tables; not
from the track's prose.

- Reproduction: p6_check_reproduction.csv 5/5 set_equal and order_equal; p6_check_indiana_folds.csv
  55/55 set, order and common equal (25 pool, 30 random).
- Lists, recomputed from the genes__*.csv copies: fold keys equal each task definition's donor folds
  on all six tasks (CCRCC 24, PRAD 2, READ 2, LYMPH_IDC 4, HCC 2, INDIANA_KIDNEY 25); 50 in 200 in
  500 on every fold; 0 duplicate genes; minimum length 50/200/500 everywhere except
  INDIANA_KIDNEY fold kidVis_atlas_IU-F59 (199 at 200, 494 at 500).
- Presence: p6_acceptance.csv 18 rows, n_absent 0, n_empty_folds 0, 974,818 checks. Presence was
  not recomputed locally (the h5ad files are on Longleaf).
- Prediction 4 inputs: top-50 overlap with shipped CCRCC 42.71, HCC 24.00, LYMPH_IDC 21.00,
  READ 16.50, PRAD 11.00, pooled 35.65 (34 folds); round 2's fold_hvg__hoptimus0.csv over the five
  tasks gives mean 24.69, sd 11.13, 16 folds.
- Job accounting: the track's p6_sacct.csv holds job-level rows only, where MaxRSS is blank (the
  reviewer's warning). p6_sacct_lead.psv is the lead's sacct query including the .batch steps: the
  MaxRSS values the track reported are confirmed, all jobs on rc_htzhu_pi and partition spill.
  Corrections: job 2777221 elapsed 00:00:27 (reported 00:00:29), MaxRSS 1226684K (reported n/a).
- ESCALATION for P7: the Xenium panel intersections in p6_xenium_panels.csv count negative-control
  features as genes: 61 (NegControlCodeword 41, NegControlProbe 20) on BREAST_XENIUM, COAD, LUNG,
  PAAD and SKCM, and 220 on IDC (plus 159 BLANK codewords). So do round 2's recorded intersections
  and round 3 D4's BREAST_XENIUM.json target_genes list (151 = 90 genes + 61 controls). D4's breast
  heads are NOT affected: HEST's min_cells filter leaves n_common_genes = 90 and no control feature
  appears in any of d4_breast_fold_genes.csv's 40 selections. Round-3 files are not changed.
- Duplicate hand-back versions: the later versions were staged; the script is md5
  03ecb15ccdf71dd22d05f2802f28f0ce, the version that ran verify 2777221.
