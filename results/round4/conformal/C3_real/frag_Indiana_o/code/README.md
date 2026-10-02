# Indiana o sweep (frame 37664027-917b-4af5-b46c-c441036d6333)

Task INDIANA_KIDNEY, K = 10 calibration donors, 3 calibration draws per fold, 20 label draws, o in (5,10,25,50,100,200),
alpha in (0.1, 0.2), score abs only (no CQR, no scaled score, no candidates, no repeated subsampling), encoders
hoptimus0, uni_v2, resnet50. Driver run_indiana_o.py calls round4_conf_c3 (md5 2d8418677cf8290eec89a14c315b92cd) unedited.
Assumptions and guarantees of every method are in the module docstring (METHODS section) and are the ones that apply here:

- o = 0: pooled (no guarantee for a new donor), hcp (coverage >= 1-alpha under hierarchical exchangeability of donors; infinite iff 1/(K+1) > alpha),
  one_per (valid per single subsampling; the 200-draw average is a summary, not a conformal set).
- o > 0 ghcp_r05 (eq. 8 pool, primary), ghcp_r05code (released code's pool, alpha 0.1 only), ghcp, ghcp_noad, ghcp_r05_noad:
  GHCP Algorithm 1, coverage >= 1-alpha under A1 group exchangeability, A2 sizes exchangeable with and independent of the group
  laws, A3 within-group exchangeability. A1 and A2 are not established for real donors (size tied to slide count).
- within (Std-CP): floor(o/2) labelled spots recentre, the rest calibrate |r-c|; marginal guarantee over the labelled draw;
  infinite when 1/(o-floor(o/2)+1) > alpha.
- within_plain: all o labelled spots calibrate |r|, no recentring; q = ceil((o+1)(1-alpha))-th smallest; same marginal
  guarantee, finite from o = 9 at alpha 0.1 and o = 4 at alpha 0.2; only the mean over the 20 label draws is comparable to it.
- recentred: pooled cross-donor quantile of the K calibration donors' |r|, shifted by the labelled spots' mean residual; no guarantee.
Tie convention: QTOL (relative 1e-12) primary; `finite_code` carries the released code's upward-tie finiteness.
Evaluation spots exclude the o labelled ones; o leaving fewer than 10 evaluation spots is skipped (recorded in skipped_o.json).
