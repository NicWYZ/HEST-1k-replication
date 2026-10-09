"""Round 5 PPI, interval 2, stage E4 on the real tasks: which clusters to label.

Brief section 6, E4; designs, estimators and intervals in round5_ppi_balance.py. One task and arm
per call. theta3 and theta2 (the mean on ACS), donor-weighted, design target, every unit of a
labelled donor labelled, n_L in {4, 6, 8, 12} (n_L <= G - 2 as round 4), 200 accepted draws.

Balance variables (none computed from a label):
    own      the estimand's own fbar_g, one variable per gene (one design per gene)
    pcF<k>   the first k principal components (k = 1, 2, 3) of the G x genes matrix of fbar_g,
             genes standardised, one design for all genes
    pcE<k>   the first k principal components of the donors' mean embeddings (round-4 Q5
             q5_mean_embeddings parquets, array column 'mean_embedding'), the arm's encoder
             (resnet50 for permuted); tissue tasks only
    perm     the permuted predictor's fbar_g, per gene (the control)
Designs: D0; D1 on the first variable of own, pcF, pcE and perm; D2 with p_a in {0.1, 0.01} on
every balance variable; and D2 with the threshold at infinity on own ('D2_inf'), which must equal D0.

Draws: candidate 0 of draw d is round 4's draw (round3_b1_ppi.draw_L with 'q2|<vtag>|nL<n>|d<d>'),
candidates k >= 1 permutations under 'r5e4c|<vtag>|nL<n>|d<d>|k<k>'; 2,000 candidates per draw. The
cross-fit seed of rule c_crossfit_design is round 4's 'q2|<vtag>|nL<n>|m0|d<d>|<est>|donor|<rule>' under
D0 and D2, and 'r5e4x|<vtag>|nL<n>|d<d>|<est>|<balance>' under D1 (two per stratum by
'r5e4D1|<vtag>|nL<n>|d<d>|<est>|<balance>').

Output: e4_selection__<vtag>__<arm>.csv (one row per estimand, design, balance, p_a, n_L, rule and
interval, with medians over genes) and e4_selection_genes__<vtag>__<arm>.csv.gz.
"""
import argparse
import json
import os
import time
import zlib

import numpy as np
import pandas as pd

import round4_ppi_q2_masking as Q2
import round5_ppi_balance as BAL
from round5_ppi_e2_regimeB import load_arm, ACS

NL = (4, 6, 8, 12)
N_CAND = 2000
RULES = ("none", "c_crossfit_design")


def pcs(X, k):
    Xc = X - X.mean(0)
    sd = Xc.std(0, ddof=1)
    Xs = Xc / np.where(sd > 0, sd, 1.0)
    U, s, _ = np.linalg.svd(Xs, full_matrices=False)
    return U[:, :k] * s[:k]


def donor_arrays(data, est):
    z, zf, ok = Q2.z_arrays(data, est, "donor")
    G = len(data["donors"])
    S = Q2.donor_sums(z, zf, data["didx"], G)
    return S["Sz"] / S["n"], S["Sf"] / S["n"], ok


def embeddings(root, vtag, enc, donors):
    p = os.path.join(root, f"results/round4/ppi/Q5_joint/q5_mean_embeddings__{vtag}__{enc}.parquet")
    if not os.path.exists(p):
        return None
    e = pd.read_parquet(p)
    key = next((c for c in e.columns if c in ("mean_embedding_row_key", "row_key", "donor", "donor_id", "key")), None)
    if key is not None:
        e = e.set_index(key)
    e.index = e.index.astype(str)
    e = e.reindex([str(d) for d in donors])
    # the round-4 parquet stores each donor's mean embedding as one array-valued column
    # ('mean_embedding', over joined spots); count columns such as n_spots are not embeddings
    col = "mean_embedding" if "mean_embedding" in e.columns else None
    if col is None:
        arr = [c for c in e.columns if e[c].dtype == object and hasattr(e[c].dropna().iloc[0], "__len__")]
        col = arr[0] if arr else None
    if col is None:
        raise ValueError(f"no array-valued embedding column in {p}: {list(e.columns)}")
    if e[col].isna().any():
        return None
    return np.stack([np.asarray(v, float) for v in e[col]])


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--parquet", required=True)
    p.add_argument("--perm-parquet", required=True, help="the base parquet of the permuted control")
    p.add_argument("--vtag", required=True)
    p.add_argument("--arm", required=True)
    p.add_argument("--root", default="/work/users/w/e/weiyang/hest_replication")
    p.add_argument("--draws", type=int, default=200)
    p.add_argument("--n-cand", type=int, default=N_CAND)
    p.add_argument("--nl-grid", default=",".join(map(str, NL)))
    p.add_argument("--theta2-kind", default="neo_minus_stroma", choices=("neo_minus_stroma", "mean"))
    p.add_argument("--max-genes", type=int, default=0)
    p.add_argument("--out-dir", default=".")
    a = p.parse_args(argv)
    np.seterr(all="ignore")
    Q2.THETA2_KIND = a.theta2_kind
    t0 = time.time()
    data = load_arm(a.parquet, a.arm, a.vtag)
    pdata = load_arm(a.perm_parquet, "permuted", a.vtag)
    if a.max_genes:
        for dd in (data, pdata):
            dd["genes"] = dd["genes"][:a.max_genes]
            dd["Y"], dd["P"] = dd["Y"][:, :a.max_genes], dd["P"][:, :a.max_genes]
    donors = data["donors"]
    Gall = len(donors)
    enc = "resnet50" if a.arm == "permuted" else a.arm
    emb = None if a.vtag in ACS else embeddings(a.root, a.vtag, enc, donors)
    rows, generows = [], []
    for est in Q2.ESTS:
        zbar_all, fbar_all, ok = donor_arrays(data, est)
        _, fperm_all, _ = donor_arrays(pdata, est)
        vid = np.flatnonzero(ok)
        G = len(vid)
        zbar, fbar, fperm = zbar_all[vid], fbar_all[vid], fperm_all[vid]
        ng = zbar.shape[1]
        theta = zbar.mean(0)
        bal = {"own": fbar[:, :, None], "perm": fperm[:, :, None]}
        for k in (1, 2, 3):
            # one design for all genes: a single column, broadcast to the genes after selection
            bal[f"pcF{k}"] = pcs(fbar, k)[:, None, :]
            if emb is not None and np.isfinite(emb[vid]).all():
                bal[f"pcE{k}"] = pcs(emb[vid], k)[:, None, :]
        for nL in map(int, a.nl_grid.split(",")):
            if nL > Gall - 2:
                continue
            # candidate pool over all donors, restricted to valid ones
            masks = np.zeros((a.draws * a.n_cand, Gall), bool)
            for d in range(a.draws):
                Ld = Q2.B1.draw_L(list(donors), nL, f"q2|{a.vtag}|nL{nL}|d{d}")
                masks[d * a.n_cand, np.isin(donors, Ld)] = True
                for k in range(1, a.n_cand):
                    perm = np.random.default_rng(zlib.crc32(f"r5e4c|{a.vtag}|nL{nL}|d{d}|k{k}".encode())).permutation(Gall)
                    masks[d * a.n_cand + k, perm[:nL]] = True
            mv = masks[:, vid]
            nlab = mv.sum(1)
            if (nlab < 2).any():
                mv = mv & (nlab >= 2)[:, None]      # such candidates get an infinite distance below
            designs = [("D0", "none", 1.0)]
            for b in ("own",) + tuple(x for x in bal if x != "own"):
                for pa in (0.1, 0.01):
                    designs.append(("D2", b, pa))
            designs.append(("D2_inf", "own", 1.0))
            dists = {}
            for b in bal:
                with np.errstate(invalid="ignore", divide="ignore"):
                    dd = BAL.mahalanobis_pool(mv, bal[b])
                dd[nlab < 2] = np.inf
                dists[b] = dd
            for dname, b, pa in designs:
                acc = {}
                if dname == "D0":
                    sel = np.zeros((a.draws, ng), int)
                    thr, nmiss = np.full(ng, np.inf), 0
                else:
                    sel, thr, nmiss = BAL.d2_select(dists[b], a.draws, a.n_cand, pa)
                for d in range(a.draws):
                    Lm = mv[d * a.n_cand + sel[d]].T if dname != "D0" else mv[d * a.n_cand][:, None]
                    Lm = np.ascontiguousarray(np.broadcast_to(Lm, (G, ng)))
                    if Lm.sum(0).min() < 2:
                        continue
                    for rule in RULES:
                        out, lam = BAL.estimate_srs_like(zbar, fbar, Lm, rule, f"q2|{a.vtag}|nL{nL}|m0|d{d}|{est}|donor|{rule}")
                        for iv, (th, v, df) in out.items():
                            acc.setdefault((rule, iv), []).append((th, v, df))
                summarise(acc, theta, dict(vtag=a.vtag, arm=a.arm, estimand=est, G=G, n_L=nL, design=dname,
                                           balance=b, p_a=pa, n_no_accept=nmiss), data["genes"], rows, generows)
            # D1
            for fam in ("own", "pcF1", "pcE1", "perm"):
                if fam not in bal or nL < 4 or nL % 2:
                    continue
                st = BAL.d1_strata(bal[fam][:, :, 0], nL)
                st_full = np.ascontiguousarray(np.broadcast_to(st, (G, ng)))
                acc = {}
                for d in range(a.draws):
                    rng = np.random.default_rng(zlib.crc32(f"r5e4D1|{a.vtag}|nL{nL}|d{d}|{est}|{fam}".encode()))
                    Lm = np.ascontiguousarray(np.broadcast_to(BAL.d1_draw(st, rng), (G, ng)))
                    for rule in RULES:
                        out, lam = BAL.estimate_d1(zbar, fbar, Lm, st_full, rule, f"r5e4x|{a.vtag}|nL{nL}|d{d}|{est}|{fam}")
                        for iv, (th, v, df) in out.items():
                            acc.setdefault((rule, iv), []).append((th, v, np.broadcast_to(df, (ng,))))
                summarise(acc, theta, dict(vtag=a.vtag, arm=a.arm, estimand=est, G=G, n_L=nL, design="D1",
                                           balance=fam.rstrip("1") if fam != "own" else "own", p_a=np.nan,
                                           n_no_accept=0), data["genes"], rows, generows)
            print(f"{est} nL{nL} {time.time() - t0:.0f}s", flush=True)
    os.makedirs(a.out_dir, exist_ok=True)
    tag = f"{a.vtag}__{a.arm}"
    pd.DataFrame(rows).to_csv(os.path.join(a.out_dir, f"e4_selection__{tag}.csv"), index=False)
    pd.DataFrame(generows).to_csv(os.path.join(a.out_dir, f"e4_selection_genes__{tag}.csv.gz"), index=False)
    json.dump(dict(vtag=a.vtag, arm=a.arm, draws=a.draws, n_cand=a.n_cand, n_rows=len(rows),
                   embeddings=emb is not None, wall_s=time.time() - t0),
              open(os.path.join(a.out_dir, f"e4_selection_summary__{tag}.json"), "w"), indent=1)
    return 0


def summarise(acc, theta, cell, genes, rows, generows):
    from scipy import stats
    import round5_ppi_estimator as R5
    for (rule, iv), L in acc.items():
        th = np.array([x[0] for x in L]); v = np.array([x[1] for x in L])
        df = np.array([np.broadcast_to(x[2], th.shape[1:]) for x in L])
        q = stats.t.ppf(1 - R5.ALPHA / 2, df)
        se = np.sqrt(np.maximum(v, 0))
        cov = (np.abs(th - theta[None, :]) <= q * se).mean(0)
        ev = th.var(0, ddof=1)
        mv = v.mean(0)
        w = (2 * q * se).mean(0)
        okg = np.isfinite(ev) & (ev > 0)
        rows.append(dict(cell, rule=rule, interval=iv, n_draws=len(L), n_genes=int(okg.sum()),
                         emp_var_median=float(np.median(ev[okg])) if okg.any() else np.nan,
                         est_var_over_emp_var_median=float(np.median(mv[okg] / ev[okg])) if okg.any() else np.nan,
                         coverage_median=float(np.median(cov[okg])) if okg.any() else np.nan,
                         coverage_mean=float(np.mean(cov[okg])) if okg.any() else np.nan,
                         width_median=float(np.median(w[okg])) if okg.any() else np.nan))
        for j, g in enumerate(genes):
            if okg[j]:
                generows.append(dict(cell, rule=rule, interval=iv, gene=g, emp_var=ev[j], est_var=mv[j],
                                     coverage=cov[j], width=w[j]))


if __name__ == "__main__":
    raise SystemExit(main())
