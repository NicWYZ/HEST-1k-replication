"""Round 10, track final-runs, stage F1.4c: a task definition for a corpus group without one, by the corpus's rule.

The federated corpus defines tasks only for organ and platform groups with at least 3 centers
(NicWYZ/ST-Fed-Learn, code/scripts/round1_data_b5_tasks.py, genes_for). Breast Spatial Transcriptomics has 2 centers
and passes the 10-donor criterion after the audit, so its gene set is built here by the same rule, copied from
genes_for: genes_intersection = the Ensembl ids in every member's panel (registry/panel_<id>.parquet), and genes_top50 =
the 50 of those with the highest mean over members of each member's mean log(1 + 1e4 y / n) over all its spots, with n
the spot's total over its full panel. Anchor: the same function is first run on the corpus's kidney__Visium members and
must return that task file's genes_top50 in the same order and genes_intersection as the same set.
The new task file is written to <outdir> only (never into the corpus), with the members' paths from samples.parquet.
Usage: round10_final_runs_f1_task_build.py <corpus_data_dir> <organ> <platform> <donor_map.csv> <outdir>
"""
import json, os, sys
import anndata as ad, numpy as np, pandas as pd

ENCS = ["uni_v2", "hoptimus0", "resnet50", "virchow2", "phikon_v2"]


def genes_for(members, DATA):
    panel_genes = {p: set(pd.read_parquet(f"{DATA}/registry/panel_{p}.parquet").ensembl_id) for p in members.panel_id.unique()}
    gi = sorted(set.intersection(*[panel_genes[p] for p in members.panel_id.unique()]))
    if not gi:
        return gi, []
    sums, n = pd.Series(0.0, index=gi), 0
    for r in members.itertuples():
        A = ad.read_h5ad(r.expr_path); lib = np.asarray(A.X.sum(1)).ravel()
        B = A[:, A.var.ensembl_id.isin(gi)]; idx = B.var.ensembl_id.values
        Y = np.log1p(1e4 * B.X.toarray() / np.maximum(lib, 1)[:, None]); s_ = pd.Series(Y.mean(0), index=idx)
        s_ = s_[~s_.index.duplicated()]; sums = sums.add(s_.reindex(gi).fillna(0)); n += 1
    return gi, (sums / max(n, 1)).sort_values(ascending=False).index[:50].tolist()


def main():
    DATA, organ, platform, dmap, out = sys.argv[1:6]; os.makedirs(out, exist_ok=True)
    S = pd.read_parquet(f"{DATA}/registry/samples.parquet")
    K = json.load(open(f"{DATA}/tasks/kidney__Visium.json"))
    kid = S[S.sample_id.isin([s['sample_id'] for s in K['samples']])]
    gi_k, top_k = genes_for(kid, DATA)
    anchor = dict(task='kidney__Visium', members=len(kid), top50_equal_in_order=top_k == K['genes_top50'],
                  intersection_equal=set(gi_k) == set(K['genes_intersection']), n_top50=len(top_k), n_intersection=len(gi_k))
    print(json.dumps(anchor, indent=1))
    dm = pd.read_csv(dmap, dtype=str)
    g = S[(S.organ == organ) & (S.platform == platform) & S.sample_id.isin(dm.sample_id)]
    assert len(g) == len(dm), 'donor map samples missing from the registry'
    gi, top = genes_for(g, DATA)
    name = organ.replace(' ', '_') + '__' + platform.replace(' ', '_').replace("'", '')
    samples = [dict(sample_id=r.sample_id, center_id=r.center_id, donor_id=r.donor_id, platform=r.platform, organ=r.organ,
                    vendor_lab=r.vendor_lab, expr_path=r.expr_path, patch_path=r.patch_path,
                    emb_paths={e: getattr(r, f'emb_path_{e}') for e in ENCS},
                    emb_exists={e: os.path.exists(getattr(r, f'emb_path_{e}')) for e in ENCS}) for r in g.itertuples()]
    T = dict(name=name, kind='within_organ_platform_round10', organ=organ, platform=platform, n_centers=int(g.center_id.nunique()),
             genes_intersection=gi, genes_top50=top, samples=samples, designs=[],
             built_by='round10_final_runs_f1_task_build.py with the rule of round1_data_b5_tasks.py genes_for')
    json.dump(T, open(os.path.join(out, f'{name}.json'), 'w'), indent=1)
    summ = dict(anchor=anchor, task=name, samples=len(samples), centers=T['n_centers'], n_intersection=len(gi), n_top50=len(top),
                all_embeddings=bool(all(all(s['emb_exists'][e] for e in ('uni_v2', 'hoptimus0', 'resnet50')) for s in samples)))
    json.dump(summ, open(os.path.join(out, 'task_build_summary.json'), 'w'), indent=1); print(json.dumps(summ, indent=1))


if __name__ == '__main__':
    main()
