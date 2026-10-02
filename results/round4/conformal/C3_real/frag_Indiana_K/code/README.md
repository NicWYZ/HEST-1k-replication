# frag_Indiana_K: Indiana kidney, K = 10, o = 0 (C3, round 4, conformal track)

Written before any job ran. Session frame 37664027-917b-4af5-b46c-c441036d6333.

Design. Task INDIANA_KIDNEY, donor set 25 (one held-out donor unit per fold, 25 folds), K = 10
calibration donor units per fold, 3 calibration draws, three encoders (hoptimus0, uni_v2, resnet50),
o = 0, score abs, alpha 0.1 and 0.2, methods pooled, hcp, one_per. Expected rows per encoder
25 x 3 x 3 x 2 = 450, in total 1350. No GHCP, within, within_plain or recentred rows: those need
o > 0 and are not part of this step. No candidates, no scaled score, no repeated subsampling.
Code: round4_conf_c3.py (md5 2d8418677cf8290eec89a14c315b92cd), unchanged, called through
`load_task`, `specs`, `fit`, `o0_rows`. Quantile convention: this track's QTOL (relative 1e-12);
`finite_code` records the released code's upward tie resolution beside `finite`.

Assumptions and guarantees (module docstring).

- pooled. Split conformal on all calibration spots with equal weights, level ceil((n+1)(1-alpha)).
  Assumes spot-level exchangeability of calibration and test spots, which hierarchical data
  violate. No guarantee for a new donor.
- hcp. Lee, Barber and Willett. Calibration donor k's spots carry 1/((K+1)N_k), the test donor's
  mass 1/(K+1) sits at +inf. Assumes hierarchical exchangeability of donors and within-donor
  exchangeability. Guarantee: coverage >= 1 - alpha for any K when the assumption holds; infinite
  exactly when 1/(K+1) > alpha (K <= 8 at alpha 0.1), so finite at K = 10, although the released
  code's upward tie rule can make it infinite at alpha 0.1 (see finite_code). Real donors are not
  exchangeable in features or prediction error, so the guarantee is conditional.
- one_per. Dunn, Wasserman and Ramdas single subsampling as round 3's a4b `dwr`: one calibration
  spot per donor, ordinary conformal quantile of the K scores, repeated 200 times (crc32 seeds),
  coverage and width averaged over repetitions. Each repetition is valid under hierarchical
  exchangeability (nontrivial iff K >= 1/alpha - 1); the average is a summary of valid intervals,
  not a conformal set, and is not the paper's section 4.3 repeated subsampling.

Outputs per encoder in enc_<encoder>/: c3_o_sweep__, c3_full__, c3_by_fold__, c3_K_sweep__ tables,
_provenance.json, PROVENANCE.txt, cpu_vendor.txt. The merged c3_K_sweep__INDIANA.csv (K = 10 only,
fixed plus extra columns) and c3_by_fold__INDIANA.csv sit at the fragment root.
