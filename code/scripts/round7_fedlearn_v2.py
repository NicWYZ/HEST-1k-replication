#!/usr/bin/env python
"""Round 7 federated learning track, V2: the simulated federation (plan amendment A7).

(a) Sources: KIDNEY_POP54 (cordeliers_ccRCC against indiana_nontumour) and BREAST_XENIUM (10x Genomics
against the unresolved bioRxiv study), 10 within-center hold-out draws. (b) Pseudo-centers: 10
random partitions of the donor units of CCRCC, INDIANA_KIDNEY and LUNG_XENIUM into 3 centers, one
hold-out draw per partition.

Arms. local (the center's own training donors), federated (all centers' training donors, equal to
the pooled exact head), intercept (federated slopes from within-center centred sums plus a center
intercept), centred (each center's embeddings centred on that center's mean before basis and ridge).
At prediction the centred arm subtracts the test center's mean embedding over all of its spots,
which uses no label and is a transductive step.

Schemes. within: held-out donors of each center. loco: train on the other centers' donors, test on
every donor of the left-out center; the local arm there is the mean of the training centers' own
heads' metrics.

One job per task, all three encoders. Writes into its working directory
(results/round7/fedlearn/V2/<task>/): v2_genes.json, v2_summary.csv and v2_paired.csv first, then
v2_rows.csv, PROVENANCE.txt and _provenance.json.
"""
import argparse
import json
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import round7_fedlearn_common as C  # noqa: E402
import round7_fedlearn_design as D  # noqa: E402
import round7_fedlearn_head as H  # noqa: E402

CENTER_KIND = {"cordeliers_ccRCC": "lab (Sorbonne, Centre de Recherche des Cordeliers)",
               "indiana_nontumour": "study (kidney atlas; Washington University and Indiana University samples)",
               "10x_genomics": "lab (10x Genomics, both spellings)",
               "study_biorxiv_2025": "study (unresolved bioRxiv 10.64898/2025.12.08.692193)"}


def sub(st, idx):
    """Stats restricted to the expression columns idx."""
    return H.Stats(st.n, st.sx, st.sy[idx], st.Sxx, st.Sxy[:, idx])


class Task:
    """Loaded samples of one task and encoder, with per-sample sums on the loaded genes."""

    def __init__(self, td, sids, enc, genes):
        self.genes = list(genes)
        self.data = H.load_samples(td, sids, enc, self.genes)
        self.st = {s: H.Stats.of(self.data[s][0], self.data[s][1]) for s in sids}

    def stats(self, sids, gidx):
        return sub(H.total([self.st[s] for s in sids]), gidx)

    def mean_x(self, sids):
        t = H.total([self.st[s] for s in sids])
        return t.sx / t.n

    def test(self, sids, gidx):
        X = np.vstack([self.data[s][0] for s in sids])
        Y = np.vstack([self.data[s][1][:, gidx] for s in sids])
        sl = np.concatenate([[s] * len(self.data[s][0]) for s in sids])
        return X, Y, sl


def score(Y, P, sl):
    ws, nsl = H.within_slide(Y, P, sl)
    return dict(within_slide=ws, n_test_slides_scored=nsl, pooled_pearson=H.pooled_pearson(Y, P))


def within_rows(T, train, held, allc, gidx):
    st = {c: T.stats(v, gidx) for c, v in train.items()}
    fed = H.fit_exact(H.total(list(st.values())))
    icp = H.fit_intercept(st)
    cen = H.fit_centred(st)
    rows = []
    for c in train:
        X, Y, sl = T.test(held[c], gidx)
        loc = H.fit_exact(st[c])
        n_tr = int(st[c].n)
        n_all = int(sum(s.n for s in st.values()))
        preds = {"local": (loc.predict(X), n_tr), "federated": (fed.predict(X), n_all),
                 "intercept": (icp.predict(X, center=c), n_all),
                 "centred": (cen.predict(X - T.mean_x(allc[c])), n_all)}
        for arm, (P, ntr) in preds.items():
            rows.append(dict(scheme="within", center=c, arm=arm, n_train_spots=ntr, n_test_spots=len(Y),
                             **score(Y, P, sl)))
    return rows


def loco_rows(T, allc, c, gidx):
    """Leave center c out: train on every donor of the other centers, test on every donor of c."""
    rows = []
    for _ in (c,):
        others = [k for k in allc if k != c]
        st = {k: T.stats(allc[k], gidx) for k in others}
        X, Y, sl = T.test(allc[c], gidx)
        fed = H.fit_exact(H.total(list(st.values())))
        icp = H.fit_intercept(st)
        cen = H.fit_centred(st)
        n_all = int(sum(s.n for s in st.values()))
        loc_scores = [score(Y, H.fit_exact(st[k]).predict(X), sl) for k in others]
        loc = {m: float(np.mean([d[m] for d in loc_scores])) for m in ("within_slide", "pooled_pearson")}
        loc["n_test_slides_scored"] = loc_scores[0]["n_test_slides_scored"]
        rows.append(dict(scheme="loco", center=c, arm="local", n_train_spots=int(np.mean([st[k].n for k in others])),
                         n_test_spots=len(Y), **loc))
        for arm, P in (("federated", fed.predict(X)), ("intercept", icp.predict(X)),
                       ("centred", cen.predict(X - T.mean_x(allc[c])))):
            rows.append(dict(scheme="loco", center=c, arm=arm, n_train_spots=n_all, n_test_spots=len(Y),
                             **score(Y, P, sl)))
    return rows


def designs(task, td, sids):
    """List of dicts: draw, allc (center -> all sids), held (center -> held-out sids),
    train (center -> training sids), design label, whether loco is run for this draw."""
    units = D.units_of(td, sids)
    out = []
    if task in ("KIDNEY_POP54", "BREAST_XENIUM"):
        allc = D.sources(task, td, sids)
        cu = {c: sorted({u for u, ss in units.items() if set(ss) & set(v)}) for c, v in allc.items()}
        for c in cu:
            for u in cu[c]:
                assert set(units[u]) <= set(allc[c]), f"donor unit {u} spans centers"
        for d in range(D.N_HOLD_DRAWS_A):
            held, train = {}, {}
            for c in allc:
                h, t = D.holdout("V2a-hold", cu[c], task, d, c)
                held[c] = [s for u in h for s in units[u]]
                train[c] = [s for u in t for s in units[u]]
            out.append(dict(design="a_sources", draw=d, allc=allc, held=held, train=train, loco=(d == 0)))
    else:
        for p, part in enumerate(D.partitions(task, units)):
            allc = {c: [s for u in us for s in units[u]] for c, us in part.items()}
            held, train = {}, {}
            for c, us in part.items():
                h, t = D.holdout("V2b-hold", us, task, p, c)
                held[c] = [s for u in h for s in units[u]]
                train[c] = [s for u in t for s in units[u]]
            out.append(dict(design="b_pseudo", draw=p, allc=allc, held=held, train=train, loco=True))
    return out


def summarise(R):
    """Center-averaged metric per draw, then mean and sd over draws; paired differences of every arm
    against local and against federated, per draw."""
    keys = ["task", "design", "encoder", "scheme", "arm"]
    per_draw = (R.groupby(keys + ["draw"], sort=True)[["within_slide", "pooled_pearson"]].mean().reset_index())
    S = (per_draw.groupby(keys, sort=True)
         .agg(n_draws=("draw", "size"), within_slide_mean=("within_slide", "mean"),
              within_slide_sd=("within_slide", "std"), pooled_pearson_mean=("pooled_pearson", "mean"),
              pooled_pearson_sd=("pooled_pearson", "std")).reset_index())
    pv = per_draw.pivot_table(index=["task", "design", "encoder", "scheme", "draw"], columns="arm",
                              values=["within_slide", "pooled_pearson"])
    prs = []
    for (m, arm) in pv.columns:
        for ref in ("local", "federated"):
            if arm == ref or (m, ref) not in pv.columns:
                continue
            dlt = (pv[(m, arm)] - pv[(m, ref)]).rename("diff").reset_index()
            for g, h in dlt.groupby(["task", "design", "encoder", "scheme"], sort=True):
                prs.append(dict(zip(["task", "design", "encoder", "scheme"], g), metric=m, arm=arm, minus=ref,
                                n_draws=len(h), mean_diff=h["diff"].mean(), sd_diff=h["diff"].std(),
                                n_positive=int((h["diff"] > 0).sum())))
    return S, pd.DataFrame(prs)


def gene_plan(task, td, td_cc, des):
    """Genes loaded, and per draw and scheme the indices fitted. BREAST_XENIUM selects per fit on the
    training samples within its 151-gene panel; the others use one fixed set."""
    if task != "BREAST_XENIUM":
        genes, note = D.gene_set(task, td, clone_td_ccrcc=td_cc)
        return genes, note, lambda key, tr: list(range(len(genes))), {}
    panel = list(td["target_genes"]["list"])
    cache = {}

    def idx(key, tr):
        k = tuple(sorted(tr))
        if k not in cache:
            g, _ = H.select_genes(td, list(k), "uni_v2")
            cache[k] = g
        return [panel.index(g) for g in cache[k]]
    return panel, "get_k_genes per fit on the training samples, within the 151-gene panel", idx, cache


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame-id", required=True)
    ap.add_argument("--task", required=True, choices=list(D.TASKS))
    ap.add_argument("--clone", default=C.CLONE)
    a = ap.parse_args()
    out = os.getcwd()
    C.stamp_dir(out, a.frame_id, note=f"round 7 fedlearn V2 {a.task}")
    t0 = time.time()
    td = H.load_td(a.clone, D.TASKS[a.task])
    td_cc = H.load_td(a.clone, D.TASKS["CCRCC"])
    sids = D.task_samples(td)
    des = designs(a.task, td, sids)
    genes, gnote, gidx_for, cache = gene_plan(a.task, td, td_cc, des)
    # fix every gene set before any fit, from uni_v2's patched spots
    gsel = {}
    for d in des:
        gsel[(d["draw"], "within")] = gidx_for(("within", d["draw"]), [s for v in d["train"].values() for s in v])
        if d["loco"]:
            for c in d["allc"]:
                gsel[(d["draw"], "loco", c)] = gidx_for(("loco", d["draw"], c),
                                                        [s for k, v in d["allc"].items() if k != c for s in v])
    json.dump(dict(task=a.task, gene_note=gnote, loaded_genes=genes,
                   gene_sets={"|".join(map(str, k)): [genes[i] for i in v] for k, v in gsel.items()},
                   designs=[dict(design=d["design"], draw=d["draw"], centers={c: dict(all=d["allc"][c], held=d["held"][c])
                                                                               for c in d["allc"]}) for d in des]),
              open("v2_genes.json", "w"), indent=1)
    rows = []
    for enc in D.ENCODERS:
        T = Task(td, sids, enc, genes)
        for d in des:
            base = dict(task=a.task, design=d["design"], encoder=enc, draw=d["draw"])
            for r in within_rows(T, d["train"], d["held"], d["allc"], gsel[(d["draw"], "within")]):
                rows.append({**base, **r})
            if d["loco"]:
                for c in d["allc"]:
                    for r in loco_rows(T, d["allc"], c, gsel[(d["draw"], "loco", c)]):
                        rows.append({**base, **r})
        print(enc, "done", round(time.time() - t0), flush=True)
        del T
    R = pd.DataFrame(rows)
    R["center_kind"] = R.center.map(lambda c: CENTER_KIND.get(c, "pseudo-center (random partition of donor units)"))
    S, Pd = summarise(R)
    S.to_csv("v2_summary.csv", index=False)
    Pd.to_csv("v2_paired.csv", index=False)
    R.to_csv("v2_rows.csv", index=False)
    here = os.path.dirname(os.path.abspath(__file__))
    C.write_provenance(out, "V2", a.frame_id, " ".join([sys.executable] + sys.argv),
                       dict(task=a.task, n_partitions=D.N_PARTITIONS, k_centers=D.K_CENTERS,
                            n_hold_draws_a=D.N_HOLD_DRAWS_A, k=H.K_PC, lam_num=H.LAM_NUM),
                       [os.path.abspath(__file__), C.__file__, H.__file__, D.__file__,
                        os.path.join(here, "round2_r2_gene_check.py")])
    print("wall", round(time.time() - t0, 1))


if __name__ == "__main__":
    main()
