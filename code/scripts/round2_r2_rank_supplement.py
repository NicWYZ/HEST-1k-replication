#!/usr/bin/env python
"""Round 2, R2 supplement: selection-protocol sensitivity with the GENE SET HELD FIXED.

Why this exists. R2 compared the shipped 50 genes against 50 selected inside each fold, and
found a gap of +0.009 on average. That gap is NOT interpretable as leakage, because the two
arms have different targets: they share only about 27 of 50 genes, and the difference in
intrinsic predictability between the two exclusive sets tracks the gap and exceeds it on the
two tasks that cleared the escalation threshold. Selection acts THROUGH which genes are
chosen, so no design comparing two different gene lists can separate protocol from
composition.

This supplement removes that confound by holding the gene set fixed. The 50 genes are always
the shipped 50. Only the DATA the ranking sees varies:

  all_spot    the ranking statistic computed over every spot, which is what the benchmark did
  fold_train  the same statistic computed over this fold's TRAINING spots only

and the question is how much the RANKING of those same 50 genes moves. A high rank
correlation means the protocol barely matters once the gene set is fixed, which would confirm
that R2's gap was gene-set composition. A low one means the protocol does move the ranking and
the composition effect is downstream of a real protocol effect.

The ranking statistic is scanpy's normalised dispersion, exactly as the benchmark's
get_k_genes uses it: stack the spots over the common genes, log1p, then
highly_variable_genes. Computed over the FULL common-gene matrix and only then restricted to
the shipped 50, because the normalised dispersion depends on the mean-expression binning over
all genes, which is how selection actually happened.

Usage: round2_r2_rank_supplement.py <encoder>
"""
import glob
import json
import os
import sys
import time

import anndata as ad
import numpy as np
import pandas as pd
import scanpy as sc
from scipy.stats import kendalltau, spearmanr

ROOT = "/work/users/w/e/weiyang/hest_replication"
BD = f"{ROOT}/bench_data"
OUT = f"{ROOT}/results/round2/R2_fold_hvg"
enc = sys.argv[1] if len(sys.argv) > 1 else "hoptimus0"
os.makedirs(OUT, exist_ok=True)


def disp(adatas, k=50, min_cells_pct=0.10):
    """The benchmark's own ranking statistic, reproducing get_k_genes step for step.

    The step that matters and that a paraphrase omits: genes are dropped per slide when
    expressed in fewer than ceil(min_cells_pct * n_spots) of THAT slide's spots, BEFORE the
    across-slide intersection. Leaving it out changes the candidate pool, which changes the
    mean-expression binning that normalised dispersion is computed against, which changes
    the ranking. It is decisive on the Visium tasks (tens of thousands of candidate genes)
    and nearly irrelevant on the Xenium panels (a few hundred, all well expressed) -- which
    is exactly the pattern the first pass showed when it was omitted.

    Returns (dispersions_norm over the surviving common genes, the top-k set, n_spots).
    """
    common = None
    for A in adatas:
        a = A.copy()
        if min_cells_pct:
            sc.pp.filter_genes(a, min_cells=int(np.ceil(min_cells_pct * len(a.obs))))
        g = np.array(a.to_df().columns)
        common = g if common is None else np.intersect1d(common, g)
    common = [g for g in common if "BLANK" not in g and "Control" not in g]
    stacked = pd.concat([A.to_df()[common] for A in adatas])
    sa = sc.AnnData(stacked.astype(np.float32))
    sc.pp.filter_genes(sa, min_cells=0)
    sc.pp.log1p(sa)
    sc.pp.highly_variable_genes(sa, n_top_genes=k)
    top = sa.var_names[sa.var["highly_variable"]][:k].tolist()
    return (pd.Series(sa.var["dispersions_norm"].values, index=sa.var_names), top, len(stacked))


rows = []
tasks = sorted(d for d in os.listdir(BD)
               if os.path.isdir(f"{BD}/{d}") and os.path.isdir(f"{BD}/{d}/adata"))
for task in tasks:
    shipped = json.load(open(f"{BD}/{task}/var_50genes.json"))["genes"]
    parts = {}
    for p in sorted(glob.glob(f"{BD}/{task}/adata/*.h5ad")):
        parts[os.path.basename(p)[:-5]] = ad.read_h5ad(p)
    if not parts:
        continue
    # the common-gene set the benchmark would have used, with its own control-probe filter

    d_all, top_all, n_all = disp(list(parts.values()))
    # sanity: the all-spot arm should recover the shipped list, since that is how it
    # was made. A failure here means the statistic is not the benchmark's.
    n_recovered = len(set(top_all) & set(shipped))


    for sp in sorted(glob.glob(f"{BD}/{task}/splits/test_*.csv")):
        k = int(os.path.basename(sp).split("_")[1].split(".")[0])
        test_ids = {os.path.basename(x).replace(".h5ad", "")
                    for x in pd.read_csv(sp)["expr_path"]}
        train = [A for sid, A in parts.items() if sid not in test_ids]
        assert train, f"{task} fold {k}: no training samples"
        d_tr, top_tr, n_tr = disp(train)
        # a shipped gene can drop out of the training arm's candidate pool entirely
        # (the min_cells filter, or the held-out slide's panel). Rank on the survivors and
        # record how many there are, rather than silently dropping or imputing them.
        surv = [g for g in shipped if g in d_tr.index and g in d_all.index]
        r_tr = d_tr.loc[surv].rank(ascending=False)

        r_all = d_all.loc[surv].rank(ascending=False)
        rho = spearmanr(r_all.values, r_tr.values).statistic
        tau = kendalltau(r_all.values, r_tr.values).statistic
        moved = int((r_all - r_tr).abs().gt(5).sum())
        # would the fold-internal ranking still have picked these 50 as its own top 50?
        top50_tr = set(top_tr)
        rows.append(dict(
            encoder=enc, task=task, fold=k,
            n_train_samples=len(train), n_train_spots=n_tr, n_all_spots=n_all,
            n_common_genes=len(d_tr), n_shipped_ranked=len(surv),
            spearman_rank=float(rho), kendall_rank=float(tau),
            max_rank_shift=int((r_all - r_tr).abs().max()),
            n_genes_moving_over_5_ranks=moved,
            n_shipped_in_fold_top50=len(top50_tr & set(shipped)),
            n_shipped_recovered_allspot=n_recovered))
        print(f"[{task}] fold {k}: spearman {rho:.4f}, kendall {tau:.4f}, "
              f"max shift {int((r_all-r_tr).abs().max())}, "
              f"{len(top50_tr & set(shipped))}/50 shipped in the fold's own top 50 "
              f"(all-spot arm recovers {n_recovered}/50)",
              flush=True)

d = pd.DataFrame(rows)
d.to_csv(f"{OUT}/rank_supplement__{enc}.csv", index=False)
print(f"\nwrote {OUT}/rank_supplement__{enc}.csv ({len(d)} folds)")
print("\n=== rank correlation of the SHIPPED 50, all-spot versus fold-internal ranking ===")
print(d.groupby("task")[["spearman_rank", "kendall_rank", "n_shipped_in_fold_top50"]]
      .agg(["mean", "min"]).round(4).to_string())
print(f"\npooled spearman: mean {d.spearman_rank.mean():.4f}, "
      f"sd {d.spearman_rank.std():.4f}, min {d.spearman_rank.min():.4f}")
print(f"shipped genes still in the fold's own top 50: mean "
      f"{d.n_shipped_in_fold_top50.mean():.1f}/50, min {d.n_shipped_in_fold_top50.min()}/50")

with open(f"{OUT}/PROVENANCE__rank_supplement.txt", "w") as f:
    f.write(
        "Round 2, R2 supplement - fixed-list ranking sensitivity\n"
        f"slurm_job_id    : {os.environ.get('SLURM_JOB_ID','NA')}\n"
        f"node            : {os.environ.get('SLURMD_NODENAME','NA')}\n"
        f"date            : {time.strftime('%Y-%m-%dT%H:%M:%S%z')}\n"
        f"repo_commit     : {os.popen(f'git -C {ROOT} rev-parse HEAD').read().strip()}\n"
        f"script          : code/scripts/round2_r2_rank_supplement.py\n"
        f"command_line    : {' '.join(sys.argv)}\n"
        f"pythonhashseed  : {os.environ.get('PYTHONHASHSEED', 'unset')}\n"
        "statistic       : scanpy normalised dispersion, as get_k_genes uses it\n"
        "plan            : round2_R5_decisions.md directive 2.6 / plan phase-4b\n")
