#!/usr/bin/env python
"""Round 2, R2 step 1: reproduce HEST's shipped 50-gene lists exactly.

Oversight directive D2. The within-fold comparison is uninterpretable unless the
reimplementation can reproduce the shipped `var_50genes.json`, so this runs first.

Transcribed from `code/HEST/src/hest/utils.py::get_k_genes`, criteria='var', k=50,
min_cells_pct=0.10. Four details the plan's paraphrase omits and which decide the result:

  1. per sample, `sc.pp.filter_genes(min_cells=np.ceil(0.10 * n_obs))` -- ceil, on the
     sample's own spot count;
  2. the common-gene intersection is `np.intersect1d`, which SORTS, so the shipped order is
     alphabetical-after-intersection rather than AnnData order;
  3. the stacked matrix is cast to float32 before log1p;
  4. selection is `var_names[highly_variable][:k]`, i.e. in the sorted common-gene order,
     not in ranked-variance order.

Spot set. The shipped lists were produced by `get_k_genes_from_df`, which reads
`aligned_adata.h5ad` from the processed HEST-1k tree. The benchmark `adata/*.h5ad` is a
strict subset of those spots (round 1's OD1: 92.4% overall, 57.8% for SKCM). Per D2 this
tries the benchmark adata first and reports per task; the caller falls back to
aligned_adata only for the tasks that fail.

Usage: round2_r2_gene_check.py [--adata-dir-name adata]
"""
import argparse
import json
import os
import sys
import time

import numpy as np
import pandas as pd
import scanpy as sc

ROOT = "/work/users/w/e/weiyang/hest_replication"
BD = f"{ROOT}/bench_data"
OUT = f"{ROOT}/results/round2/R2_fold_hvg"
K = 50
MIN_CELLS_PCT = 0.10


def get_k_genes(adata_list, k=K, min_cells_pct=MIN_CELLS_PCT):
    """Verbatim reimplementation of HEST's get_k_genes(criteria='var')."""
    common_genes = None
    for adata in adata_list:
        my = adata.copy()
        if min_cells_pct:
            sc.pp.filter_genes(my, min_cells=np.ceil(min_cells_pct * len(my.obs)))
        curr = np.array(my.to_df().columns)
        common_genes = curr if common_genes is None else np.intersect1d(common_genes, curr)

    common_genes = [g for g in common_genes if "BLANK" not in g and "Control" not in g]

    stacked = None
    for adata in adata_list:
        df = adata.to_df()[common_genes]
        stacked = df if stacked is None else pd.concat([stacked, df])

    st = sc.AnnData(stacked.astype(np.float32))
    sc.pp.filter_genes(st, min_cells=0)
    sc.pp.log1p(st)
    sc.pp.highly_variable_genes(st, n_top_genes=k)
    return st.var_names[st.var["highly_variable"]][:k].tolist(), len(common_genes)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--adata-dir-name", default="adata",
                    help="'adata' for the benchmark files; 'aligned_adata' for the D2 fallback")
    ap.add_argument("--tasks", default="", help="comma-separated subset; default all")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)

    tasks = ([t for t in a.tasks.split(",") if t] or
             sorted(d for d in os.listdir(BD) if os.path.isdir(f"{BD}/{d}")))
    rows = []
    for task in tasks:
        adir = f"{BD}/{task}/{a.adata_dir_name}"
        shipped_path = f"{BD}/{task}/var_50genes.json"
        if not (os.path.isdir(adir) and os.path.exists(shipped_path)):
            print(f"[skip] {task}: no {a.adata_dir_name}/ or var_50genes.json", flush=True)
            continue
        shipped = json.load(open(shipped_path))["genes"]
        paths = sorted(f"{adir}/{f}" for f in os.listdir(adir) if f.endswith(".h5ad"))
        t0 = time.time()
        ads = [sc.read_h5ad(p) for p in paths]
        n_spots = [int(x.n_obs) for x in ads]
        got, n_common = get_k_genes(ads)
        del ads

        set_eq = set(got) == set(shipped)
        order_eq = got == shipped
        missing = sorted(set(shipped) - set(got))
        extra = sorted(set(got) - set(shipped))
        rows.append(dict(task=task, spot_set=a.adata_dir_name, n_samples=len(paths),
                         n_spots_total=sum(n_spots), n_common_genes=n_common,
                         n_shipped=len(shipped), n_reproduced=len(got),
                         n_intersect=len(set(got) & set(shipped)),
                         set_equal=set_eq, order_equal=order_eq,
                         missing=";".join(missing), extra=";".join(extra),
                         seconds=round(time.time() - t0, 1)))
        print(f"[{task}] {a.adata_dir_name}: {len(paths)} samples, {sum(n_spots):,} spots, "
              f"{n_common} common genes -> set_equal={set_eq} order_equal={order_eq} "
              f"overlap {len(set(got) & set(shipped))}/50  ({time.time()-t0:.0f}s)", flush=True)
        if not set_eq:
            print(f"    missing from mine: {missing}", flush=True)
            print(f"    extra in mine    : {extra}", flush=True)
        elif not order_eq:
            first = next(i for i, (x, y) in enumerate(zip(got, shipped)) if x != y)
            print(f"    same set, order differs from position {first}: "
                  f"mine {got[first]!r} vs shipped {shipped[first]!r}", flush=True)
        json.dump({"genes": got}, open(f"{OUT}/reproduced__{a.adata_dir_name}__{task}.json", "w"))

    df = pd.DataFrame(rows)
    tag = a.adata_dir_name
    df.to_csv(f"{OUT}/d2_reproduction_check__{tag}.csv", index=False)
    n_ok = int(df.order_equal.sum()) if len(df) else 0
    print(f"\n=== D2 reproduction check on '{tag}' ===")
    print(df[["task", "n_samples", "n_spots_total", "n_common_genes", "n_intersect",
              "set_equal", "order_equal"]].to_string(index=False))
    print(f"\nexact (set AND order): {n_ok}/{len(df)} tasks")
    print(f"set-equal only       : {int(df.set_equal.sum()) if len(df) else 0}/{len(df)} tasks")
    failed = df[~df.order_equal].task.tolist() if len(df) else []
    if failed:
        print(f"FAILED_TASKS:{','.join(failed)}")
        print("-> per D2, rerun these on aligned_adata.h5ad (benchmark samples only). "
              "Failure on BOTH spot sets is a stop-and-report escalation.")
    else:
        print("-> gate PASSES on this spot set; the within-fold comparison may proceed.")

    with open(f"{OUT}/PROVENANCE__d2_{tag}.txt", "w") as f:
        f.write(f"Round 2, R2 step 1 - D2 reproduction check, spot set '{tag}'\n"
                f"slurm_job_id      : {os.environ.get('SLURM_JOB_ID','NA')}\n"
                f"slurm_partition   : {os.environ.get('SLURM_JOB_PARTITION','NA')}\n"
                f"node              : {os.environ.get('SLURMD_NODENAME','NA')}\n"
                f"date              : {time.strftime('%Y-%m-%dT%H:%M:%S%z')}\n"
                f"repo_commit       : {os.popen(f'git -C {ROOT} rev-parse HEAD').read().strip()}\n"
                f"script            : code/scripts/round2_r2_gene_check.py\n"
                f"command_line      : {' '.join(sys.argv)}\n"
                f"config_hash       : getkgenes-var-k50-mincells0.10-{tag}\n"
                f"config            : criteria=var k=50 min_cells_pct=0.10 "
                f"intersect=np.intersect1d(sorted) dtype=float32 "
                f"selection=var_names[highly_variable][:50]\n"
                f"scanpy_version    : {sc.__version__}\n"
                f"exact_tasks       : {n_ok}/{len(df)}\n"
                f"decisions         : round2_R1_decisions.md directive D2\n")


if __name__ == "__main__":
    main()
