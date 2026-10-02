"""Lung theta3: slide-clustered to donor-clustered CR1 variance ratio of the all-labelled classical
estimate (and of the rectifier z - f), per gene, per encoder, both populations. Diagnostic, no interval."""
import sys, json, os, numpy as np, pandas as pd
sys.path.insert(0, "/Users/nicolaszhang/HEST-1k-replication-PPI/code/scripts")
import round4_ppi_q2_masking as Q2
td = json.load(open("/Users/nicolaszhang/HEST-1k-replication-PPI/results/round4/data/P5_task/LUNG_XENIUM.json"))
slide_of = {s["donor_id"]: s["slide_id"] for s in td["samples"]}
assert all(len({x["slide_id"] for x in td["samples"] if x["donor_id"] == d}) == 1 for d in slide_of)
def var_pair(q, sl):
    """q (G, genes) per-cluster-donor influence totals; sl slide index per donor."""
    G = q.shape[0]; S = sl.max() + 1
    qs = np.zeros((S, q.shape[1])); np.add.at(qs, sl, q)
    vd, vs = (q ** 2).sum(0), (qs ** 2).sum(0)
    return vd * G / (G - 1), vs * S / (S - 1), vd, vs
out = []
for arm, enc in (("uni_v2","uni_v2"),("hoptimus0","hoptimus0"),("resnet50","resnet50"),("permuted","resnet50")):
    pq = f"{sys.argv[1]}/b1_predictions__LUNG_XENIUM__{enc}.parquet"
    data = Q2.load(pq, arm, "LUNG_XENIUM")
    donors = list(data["donors"]); sl_names = sorted(set(slide_of.values()))
    sl_all = np.array([sl_names.index(slide_of[d]) for d in donors])
    for pop in ("donor", "spot"):
        z, zf, valid = Q2.z_arrays(data, "theta3", pop)
        G = len(donors); n = np.bincount(data["didx"], minlength=G).astype(float)
        for kind, x in (("estimate", z), ("rectifier_z_minus_f", z - zf)):
            Sx = np.zeros((G, x.shape[1])); np.add.at(Sx, data["didx"], x)
            v = np.asarray(valid, bool)
            Sx, nn, sl = Sx[v], n[v], sl_all[v]
            _, sl = np.unique(sl, return_inverse=True)
            if pop == "donor":
                t = Sx / nn[:, None]; th = t.mean(0); q = (t - th) / len(nn)
            else:
                th = Sx.sum(0) / nn.sum(); q = (Sx - nn[:, None] * th) / nn.sum()
            cd, cs, ud, us = var_pair(q, sl)
            for gi, g in enumerate(data["genes"]):
                out.append(dict(arm=arm, population=pop, quantity=kind, gene=g, G_donor=len(nn), n_slides=int(sl.max()+1),
                                var_donor_cr1=cd[gi], var_slide_cr1=cs[gi], ratio_cr1=cs[gi]/cd[gi], ratio_uncorrected=us[gi]/ud[gi]))
    print(arm, "done", flush=True)
d = pd.DataFrame(out)
d.to_csv("q4_two_way_lung_slide_per_gene.csv", index=False)
s = d.groupby(["arm","population","quantity"]).agg(G_donor=("G_donor","first"), n_slides=("n_slides","first"), n_genes=("gene","nunique"),
    ratio_cr1_median=("ratio_cr1","median"), ratio_cr1_q25=("ratio_cr1",lambda x: x.quantile(.25)), ratio_cr1_q75=("ratio_cr1",lambda x: x.quantile(.75)),
    ratio_uncorrected_median=("ratio_uncorrected","median"), var_donor_cr1_median=("var_donor_cr1","median"), var_slide_cr1_median=("var_slide_cr1","median")).reset_index()
s.to_csv("q4_two_way_lung_slide_summary.csv", index=False)
print(s.to_string())
