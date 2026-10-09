import sys, os, zlib, json
import numpy as np, pandas as pd
from scipy import stats
sys.path.insert(0, os.environ["SNAP"] + "/code/scripts")
import round4_ppi_q2_masking as Q2
import round5_ppi_balance as BAL
import round5_ppi_e4_selection as E4
from round5_ppi_e2_regimeB import load_arm
vtag, nL, ND, NC = "ACS_STATES", 8, 200, 2000
pq = os.environ["PQ"]
Q2.THETA2_KIND = "mean"
data = load_arm(pq, "package", vtag); pdata = load_arm(pq, "permuted", vtag)
donors = data["donors"]; Gall = len(donors)
rows = []
for est in Q2.ESTS:
    _, fb, ok = E4.donor_arrays(data, est); _, fp, _ = E4.donor_arrays(pdata, est)
    vid = np.flatnonzero(ok); G = len(vid); fperm = fp[vid]; ng = fperm.shape[1]
    M = np.bincount(np.asarray(data["didx"]), minlength=Gall)[vid]
    masks = np.zeros((ND * NC, Gall), bool)
    for d in range(ND):
        Ld = Q2.B1.draw_L(list(donors), nL, "q2|%s|nL%d|d%d" % (vtag, nL, d))
        masks[d * NC, np.isin(donors, Ld)] = True
        for k in range(1, NC):
            perm = np.random.default_rng(zlib.crc32(("r5e4c|%s|nL%d|d%d|k%d" % (vtag, nL, d, k)).encode())).permutation(Gall)
            masks[d * NC + k, perm[:nL]] = True
    mv = masks[:, vid]; nlab = mv.sum(1)
    if (nlab < 2).any(): mv = mv & (nlab >= 2)[:, None]
    with np.errstate(invalid="ignore", divide="ignore"):
        dist = BAL.mahalanobis_pool(mv, fperm[:, :, None])
    dist[nlab < 2] = np.inf
    sel, thr, nmiss = BAL.d2_select(dist, ND, NC, 0.01)
    inc = np.zeros((ND, G, ng)); inc0 = np.zeros((ND, G))
    for d in range(ND):
        inc[d] = mv[d * NC + sel[d]].T
        inc0[d] = mv[d * NC]
    f = inc.mean(0)            # (G, ng) inclusion frequency over the accepted draws
    f0 = inc0.mean(0)
    fmed = np.median(f, axis=1)
    sp_med = stats.spearmanr(fmed, M)
    sp_each = [stats.spearmanr(f[:, j], M)[0] for j in range(min(ng, 5))]
    sp0 = stats.spearmanr(f0, M)
    for i in range(G):
        r = dict(vtag=vtag, estimand=est, n_L=nL, p_a=0.01, balance="perm", G=G, n_genes=ng, donor=str(np.asarray(donors)[vid][i]),
                 M_g=int(M[i]), nominal_nL_over_G=nL / G, incl_freq_median_over_genes=float(fmed[i]), incl_freq_D0=float(f0[i]))
        for j in range(min(ng, 5)): r["incl_freq_gene%d" % (j + 1)] = float(f[i, j])
        rows.append(r)
    rows.append(dict(vtag=vtag, estimand=est, n_L=nL, p_a=0.01, balance="perm", G=G, n_genes=ng, donor="SUMMARY", nominal_nL_over_G=nL / G,
                     incl_freq_median_over_genes=float(fmed.mean()), spearman_incl_vs_M=float(sp_med[0]), spearman_p=float(sp_med[1]),
                     spearman_incl_vs_M_genes1to5=json.dumps([float(x) for x in sp_each]), spearman_D0_incl_vs_M=float(sp0[0]),
                     incl_min=float(fmed.min()), incl_max=float(fmed.max()), n_no_accept=int(nmiss), M_min=int(M.min()), M_max=int(M.max())))
pd.DataFrame(rows).to_csv("e4_perm_inclusion__%s.csv" % vtag, index=False)
print("done", len(rows))
