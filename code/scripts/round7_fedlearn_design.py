"""Round 7 federated learning track, interval i02: tasks, gene sets, test donors, partitions and
sources, shared by F3.0, V1, V2, V3 and V4 (plan amendments A3, A6, A7).

Every random choice is seeded by round7_fedlearn_head.rng_for from strings naming the task, the
design and the draw, so any job recomputes the same designs.
"""
import numpy as np

import round7_fedlearn_head as H

ENCODERS = ("hoptimus0", "resnet50", "uni_v2")
TASKS = {
    "CCRCC": "results/round3/task_defs/CCRCC.json",
    "INDIANA_KIDNEY": "results/round3/D4_expansion/task_defs/INDIANA_KIDNEY.json",
    "LUNG_XENIUM": "results/round4/data/P5_task/LUNG_XENIUM.json",
    "KIDNEY_POP54": "results/round3/D4_expansion/task_defs/KIDNEY_POP54.json",
    "BREAST_XENIUM": "results/round3/D4_expansion/task_defs/BREAST_XENIUM.json",
}
N_PARTITIONS = 10
K_CENTERS = 3
N_HOLD_DRAWS_A = 10


def task_samples(td):
    """Samples used, in sorted order. KIDNEY_POP54 drops the samples excluded from donor units."""
    s = [x for x in td["samples"] if not (td["task"] == "KIDNEY_POP54" and x.get("excluded_from_donor_units"))]
    return sorted(x["sample_id"] for x in s)


def units_of(td, sids):
    du = H.donor_units(td)
    out = {}
    for s in sids:
        out.setdefault(du[s], []).append(s)
    return {u: sorted(v) for u, v in sorted(out.items())}


def v1_split(task, units):
    """Fixed quarter of donor units as the V1 test set, at least three."""
    names = sorted(units)
    n_test = max(3, int(round(len(names) / 4)))
    rng = H.rng_for("V1-test", task)
    test = sorted(rng.choice(names, size=n_test, replace=False).tolist())
    pool = [u for u in names if u not in test]
    return test, pool


def v1_sizes(n_pool):
    s, n = [], 1
    while n < n_pool:
        s.append(n)
        n *= 2
    s.append(n_pool)
    return s


def gene_set(task, td, clone_td_ccrcc=None, enc="uni_v2"):
    """Target genes per amendment A3. Returns (genes, note)."""
    if task == "CCRCC":
        return list(td["target_genes"]["list"]), "benchmark genes (var_50genes.json)"
    if task == "KIDNEY_POP54":
        return list(clone_td_ccrcc["target_genes"]["list"]), "CCRCC benchmark genes (F2 memo)"
    if task in ("INDIANA_KIDNEY", "LUNG_XENIUM"):
        sids = task_samples(td)
        units = units_of(td, sids)
        _, pool = v1_split(task, units)
        pool_sids = [s for u in pool for s in units[u]]
        genes, n_common = H.select_genes(td, pool_sids, enc)
        return genes, f"get_k_genes on V1's training pool ({len(pool_sids)} samples, {n_common} common genes)"
    raise ValueError(task)


def partitions(task, units):
    """N_PARTITIONS random partitions of donor units into K_CENTERS near-equal centers."""
    names = sorted(units)
    out = []
    for p in range(N_PARTITIONS):
        perm = H.rng_for("V2b-partition", task, p).permutation(names)
        out.append({f"c{j}": sorted(x.tolist()) for j, x in enumerate(np.array_split(perm, K_CENTERS))})
    return out


def holdout(tag, center_units, *key):
    """A quarter of a center's donor units, rounded and at least one, held out."""
    names = sorted(center_units)
    n = max(1, int(round(len(names) / 4)))
    if len(names) <= n:
        n = len(names) - 1
    hold = sorted(H.rng_for(tag, *key).choice(names, size=n, replace=False).tolist())
    return hold, [u for u in names if u not in hold]


def sources(task, td, sids):
    """V2(a) centers: dict center -> sample ids."""
    by = {}
    for s in td["samples"]:
        if s["sample_id"] not in sids:
            continue
        if task == "KIDNEY_POP54":
            c = s["population"]
        elif task == "BREAST_XENIUM":
            c = "study_biorxiv_2025" if str(s.get("source", "")).startswith("unresolved") else "10x_genomics"
        else:
            raise ValueError(task)
        by.setdefault(c, []).append(s["sample_id"])
    return {k: sorted(v) for k, v in sorted(by.items())}
