"""Round 11, track closeout, A6 and B2: split conformal coverage under round 3's designs for the arms R10, P and E.

The fold enumeration, calibration-unit rule, calibration draws, size matching, conformal quantile, per-gene coverage
and the aggregation into a1_by_task are round 3's: round3_a0_harness.main is imported and run unchanged, with three
substitutions made on the imported module before it runs.

  loader   harness.load_task is replaced by one that reads the corpus task's samples (round11_closeout_predict.load_sample,
           the loader of A5) for the arm's encoders and context, and returns both scales as one outcome matrix whose
           genes are named `log1p|<gene>` and `lognorm|<gene>` (log(1 + y), and log(1 + 1e4 y / n) with n the spot's
           total over its full measured panel, as round 10's corpus files define them). Coordinates are those of the
           first encoder's embedding file, aligned by barcode.
  head     harness.fit_base is replaced by the arm's head.
             r10      the harness's own head (StandardScaler, PCA 256 with random_state 1, Cholesky ridge with
                      intercept) with the penalty computed per scale, 100 / (256 * genes per scale), so each scale's
                      columns get exactly the fit the harness gives that scale alone (ridge columns are independent).
                      The first fit of a run is checked against harness.fit_base on the log1p half (1e-8), where the
                      features number at most 4096 (R10; E's memory would double, and the selftest covers its code).
             ridgecv  A3's estimator: ridge with intercept on the features standardised with the moments of the rows
                      each fit sees, no PCA, the penalty chosen per gene and scale from alpha = n_fit * 10^k,
                      k in {-6, -5.5, ..., 1}, by the smallest summed squared error over inner folds, then refitted on
                      the whole proper training set. Inner folds group the proper training set's donors into 5 folds
                      dealt in order of zlib.crc32(donor) (round11_closeout_predict.inner_groups_for), or, in the center
                      design, each training center is an inner fold. The donor (or center) of each training row comes
                      from the training mask that harness.apply_size_match returned for the fit, recorded by a wrapper.
           harness.scaler_pca_saw_only_T is wrapped so that its check is computed for the ridgecv head as well: the
           standardisation's mean and variance must equal those of the proper training set exactly; there is no PCA.
  summary  harness._summaries is wrapped to write its tables once per scale (suffix __log1p, __lognorm), from the
           per-gene rows of that scale only. The per-gene parquet holds both scales.

Designs. CCRCC runs on round 3's own task definition (results/round3/task_defs/CCRCC.json: its samples, donors and
folds; designs enumerated `random`, `patient`, `donor` as round 3's A1 did). A corpus task gets a task definition
written to the job directory: `donor` leaves one donor out; `slide_out` leaves one slide out and is enumerated only
where some donor has more than one slide; `random` takes the test sizes of the `donor` folds (as the harness's
`patient` folds) with --n-repeats repeats each. The center design is the harness's `donor` design on a task definition
whose donor label is the sample's center (--unit center), run in its own invocation.

Split by fold (added 17 November under the QUEUE reply, plan section 6). With --fold-shard k/K a run enumerates every
cell exactly as an unsplit run does, so the harness's size match (one n_match per task, the minimum over every cell
enumerated) is the same, and then keeps only the cells whose fold of the fitted design is the k-th of every K in
the sorted list of that design's folds (k counted from 0); the cells of designs enumerated but not fitted are kept
in shard 0 only, so that the merged calibration-unit file has each once. Seeds are keyed by fold, design, repeat
and draw, never by a cell's position, so a cell's fit is the one the unsplit run makes. A shard also writes its
per-gene rows at float64 (pergene_f64<suffix>.parquet) and shard.json (the order of every enumerated cell, its
folds, n_match). `merge` joins the shards in the original cell order and writes the harness's tables through the
same summary code, so the merged directory holds what the unsplit run would have written.

Usage:
  round11_closeout_conformal.py selftest
  round11_closeout_conformal.py anchor <round3_task_def.json> <encoder>
  round11_closeout_conformal.py run --arm R10|P|E --task-json T --donor-map M --designs D1,D2 --fit-designs D
        [--map-task T] [--samples a,b] [--only-mapped] [--genes-from-parquet p] [--round3-td p] [--unit donor|center]
        [--n-repeats 1] [--tag NAME] [--fold-shard k/K]
  round11_closeout_conformal.py merge <shard_dir> [<shard_dir> ...]     (run inside the merged output directory)
  round11_closeout_conformal.py compare <dir_a> <dir_b>                  (every table of two runs, cell by cell)
Outputs are the harness's, in the job's directory (its --out-dir is the job directory relative to the project root).
"""
import argparse, json, os, sys, zlib
import numpy as np, pandas as pd

import round3_a0_harness as H
import round11_closeout_predict as P

ARMS = {'R10': ('uni_v2', 'none', 'r10'), 'P': ('uni_v2', 'ring1', 'ridgecv'),
        'E': ('uni_v2+hoptimus0+virchow2', 'ring1', 'r10')}
STATE = dict(groups=None, last_T=None, head='r10', inner='donor', g_per_scale=None, checked=False, chosen=[], shard=None)
_orig = dict(fit_base=H.fit_base, scaler=H.scaler_pca_saw_only_T, summaries=H._summaries,
             apply_size_match=H.apply_size_match, load_task=H.load_task,
             size_match_groups=H.size_match_groups)


# ------------------------------------------------------------------------------------------------ heads
class IdentityPipe:
    """Stands where the harness expects its scaler-PCA pipeline: the ridgecv head standardises inside predict."""
    def __init__(self, model):
        self.model = model

    def transform(self, X):
        return X


class RidgeCVHead:
    def fit(self, X, Y, groups, inner_mode):
        X = X.astype(np.float64, copy=False); Y = Y.astype(np.float64, copy=False)
        units = sorted(set(groups.tolist()))
        inner = P.inner_groups_for(units, 'center' if inner_mode == 'center' else 'donor')
        K = len(P.KGRID); sse = np.zeros((K, Y.shape[1]))
        for grp in inner:
            hm = np.isin(groups, grp); fm = ~hm
            fi = self._eig(X[fm], Y[fm])
            Zh = ((X[hm] - fi['mu']) / fi['sd']) @ fi['V']; Yc = Y[hm] - fi['ym']
            for a_i, kk in enumerate(P.KGRID):
                Pr = Zh @ (fi['VTb'] / (fi['w'][:, None] + fi['n'] * 10.0 ** kk))
                sse[a_i] += ((Yc - Pr) ** 2).sum(0)
        best = np.argmin(sse, axis=0)
        fo = self._eig(X, Y)
        al = fo['n'] * 10.0 ** P.KGRID[best]
        self.B = fo['V'] @ (fo['VTb'] / (fo['w'][:, None] + al[None, :]))
        self.mu, self.var, self.sd, self.ym, self.n = fo['mu'], fo['var'], fo['sd'], fo['ym'], fo['n']
        self.chosen = P.KGRID[best]
        return self

    @staticmethod
    def _eig(X, Y):
        mu = X.mean(axis=0); var = X.var(axis=0); sd = np.sqrt(var); sd = np.where(sd == 0, 1.0, sd)
        Z = (X - mu) / sd
        w, V = np.linalg.eigh(Z.T @ Z); w = np.maximum(w, 0)
        ym = Y.mean(axis=0)
        return dict(mu=mu, var=var, sd=sd, w=w, V=V, ym=ym, n=X.shape[0], VTb=V.T @ (Z.T @ (Y - ym)))

    def predict(self, X):
        return ((X - self.mu) / self.sd) @ self.B + self.ym


def fit_r10(Xtr, Ytr, g_per_scale):
    from sklearn.decomposition import PCA
    from sklearn.linear_model import Ridge
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
    pipe = Pipeline([("scaler", StandardScaler()), ("PCA", PCA(n_components=min(H.LATENT, Xtr.shape[1]), random_state=H.SEED))])
    A = pipe.fit_transform(Xtr.astype(np.float64, copy=False))
    alpha = H.ALPHA_NUM / (A.shape[1] * g_per_scale)
    reg = Ridge(alpha=alpha, random_state=0, fit_intercept=True, solver="cholesky").fit(A, Ytr.astype(np.float64, copy=False))
    return pipe, A, reg, alpha


def fit_base_arm(Xtr, Ytr):
    if STATE['head'] == 'r10':
        pipe, A, reg, alpha = fit_r10(Xtr, Ytr, STATE['g_per_scale'])
        if not STATE['checked'] and Xtr.shape[1] <= 4096:   # the per-scale penalty gives the harness's own fit of
            # the log1p half; skipped for E's 11,264 features, whose memory would double (the selftest covers the code)
            g = STATE['g_per_scale']
            p0, A0, r0, _ = _orig['fit_base'](Xtr, Ytr[:, :g])
            d = float(np.abs(reg.predict(A)[:, :g] - r0.predict(A0)).max())
            print(f'[check] two-scale r10 head against harness fit_base on log1p: max abs diff {d:.3e}', flush=True)
            assert d < 1e-8, d
            STATE['checked'] = True
        return pipe, A, reg, alpha
    T = STATE['last_T']; assert T is not None and int(T.sum()) == Xtr.shape[0]
    m = RidgeCVHead().fit(Xtr, Ytr, STATE['groups'][T], STATE['inner'])
    STATE['chosen'].append(m.chosen)
    return IdentityPipe(m), None, m, None


def scaler_check(pipe, Xtr):
    if not isinstance(pipe, IdentityPipe):
        return _orig['scaler'](pipe, Xtr)
    Xd = Xtr.astype(np.float64, copy=False); m = pipe.model
    return dict(n_samples_seen=int(m.n), pca_n_samples=int(m.n),   # no PCA in this head
                max_abs_scaler_mean_minus_T=float(np.max(np.abs(m.mu - Xd.mean(axis=0)))),
                max_abs_scaler_var_minus_T=float(np.max(np.abs(m.var - Xd.var(axis=0)))),
                max_abs_pca_mean_minus_T=0.0, head='ridgecv_no_pca')


def apply_size_match(spec, task):
    T = _orig['apply_size_match'](spec, task)
    STATE['last_T'] = T
    return T


def cell_key(design, fold, repeat, cal_draw):
    return f'{design}\t{fold}\t{int(repeat)}\t{int(cal_draw)}'


def size_match_groups_shard(specs, mode):
    """The harness's size match over every enumerated cell, then the cells of this shard only (in place)."""
    _orig['size_match_groups'](specs, mode)
    k, K, fit = STATE['shard']
    order = [cell_key(s['design'], s['fold'], s['repeat'], s['cal_draw']) for s in specs]
    assert len(set(order)) == len(order), 'cell keys are not unique'
    folds = sorted({str(s['fold']) for s in specs if s['design'] in fit})
    mine = {f for i, f in enumerate(folds) if i % K == k}
    keep = [s for s in specs if (s['design'] in fit and str(s['fold']) in mine) or (s['design'] not in fit and k == 0)]
    json.dump(dict(k=k, K=K, fit_designs=sorted(fit), cell_order=order, folds_all=folds, folds_mine=sorted(mine),
                   n_match=sorted({-1 if s['n_match'] is None else int(s['n_match']) for s in specs}),
                   n_cells_enumerated=len(specs), n_cells_kept=len(keep)), open('shard.json', 'w'), indent=1)
    print(f'[shard] {k}/{K}: {len(mine)} of {len(folds)} folds of {sorted(fit)}, {len(keep)} of {len(specs)} cells kept', flush=True)
    specs[:] = keep


def pg_schema64():
    import pyarrow as pa
    t = {'repeat': pa.int64(), 'cal_draw': pa.int64(), 'n_test': pa.int64(), 'n_covered': pa.int64(),
         'slide_ge_min_spots': pa.bool_(), 'quantile_infinite': pa.bool_()}
    flt = {'coverage', 'width_mean', 'interval_score', 'miss_above', 'miss_below', 'q_alpha_reported', 'q_alpha_stored'}
    return pa.schema([(c, t.get(c, pa.float64() if c in flt else pa.string())) for c in H.PG_COLS])


def write_pg64(out, suf, pg):
    import pyarrow as pa, pyarrow.parquet as pq
    sch = pg_schema64(); d = pg[H.PG_COLS].copy()
    for f in sch:
        if f.type == pa.string():
            if not d[f.name].map(lambda v: v is None or isinstance(v, str)).all():
                print(f'[warn] pergene_f64: {f.name} has values that are neither strings nor None; stored as str', flush=True)
                d[f.name] = d[f.name].map(lambda v: v if v is None else str(v))
    pq.write_table(pa.Table.from_pandas(d, schema=sch, preserve_index=False), f'{out}/pergene_f64{suf}.parquet')
    print(f'[write] pergene_f64{suf}.parquet ({len(d):,} rows, float64, explicit schema)', flush=True)


def summaries_by_scale(out, suf, pg, cal, args):
    if STATE['shard'] is not None and len(pg):
        write_pg64(out, suf, pg)
    if not len(pg) or not pg['gene'].astype(str).str.contains('|', regex=False).any():
        return _orig['summaries'](out, suf, pg, cal, args)
    sc = pg['gene'].astype(str).str.split('|', n=1).str[0]
    for s in sorted(set(sc)):
        print(f'[summaries] scale {s}', flush=True)
        _orig['summaries'](out, f'{suf}__{s}', pg[sc == s].reset_index(drop=True), cal, args)


# ------------------------------------------------------------------------------------------------ loader
def load_corpus(td, enc):
    r = td['_r11']
    T = json.load(open(r['task_json']))
    by_id = {s['sample_id']: s for s in T['samples']}
    ids = sorted(s['sample_id'] for s in td['samples'])
    encoders = r['encoders']; genes = r['genes']
    Xs, Ys, samp, bcs, xys = [], [], [], [], []
    for sid in ids:
        s = by_id[sid]
        F, Y, b, lib, nd, _ = P.load_sample(s, encoders, r['context'], genes)
        _, b0, xy0 = P.read_emb(s['emb_paths'][encoders[0]])
        pos = pd.Index(b0).get_indexer(b); assert (pos >= 0).all()
        lib = np.asarray(lib, dtype=np.float64)
        Ys.append(np.hstack([np.log1p(Y), np.log1p(1e4 * Y / np.maximum(lib, 1)[:, None])]))
        Xs.append(F); xys.append(xy0[pos]); samp += [sid] * len(b); bcs += list(b)
    samp = np.array(samp); unit_of = {s['sample_id']: s['donor_id'] for s in td['samples']}
    STATE['groups'] = np.array([unit_of[s] for s in samp], dtype=object)
    STATE['g_per_scale'] = len(genes)
    names = [f'log1p|{g}' for g in r['gene_labels']] + [f'lognorm|{g}' for g in r['gene_labels']]
    X = np.vstack(Xs); Yv = np.vstack(Ys)
    print(f'[load_corpus] {len(ids)} samples, {X.shape[0]} spots x {X.shape[1]} features, {Yv.shape[1]} outcomes', flush=True)
    return X, Yv, samp, np.array(bcs, dtype=object), np.vstack(xys), names


def map_genes(T, parquet):
    """round11_closeout_predict's mapping of a HEST file's symbols to Ensembl ids, as a function."""
    import anndata as ad, pyarrow.parquet as pq
    syms = [n[3:] for n in pq.read_schema(parquet).names if n.startswith('y__')]
    A0 = ad.read_h5ad(T['samples'][0]['expr_path'], backed='r')
    cands = [('var_names', pd.Index(A0.var_names.astype(str)))]
    cands += [(k, pd.Index(A0.var[k].astype(str))) for k in A0.var.columns if A0.var[k].dtype == object or str(A0.var[k].dtype) == 'category']
    best = max(cands, key=lambda kv: kv[1].isin(syms).sum())
    ens = pd.Index(A0.var['ensembl_id'].astype(str))
    m = {s_: ens[best[1].get_loc(s_)] for s_ in syms if s_ in best[1] and isinstance(best[1].get_loc(s_), (int, np.integer))}
    gs = [s_ for s_ in syms if s_ in m]
    return gs, [m[s_] for s_ in gs]


def build_td(a):
    encs, context, head = ARMS[a.arm]
    T = json.load(open(a.task_json))
    if a.samples:
        keep = set(a.samples.split(',')); T['samples'] = [s for s in T['samples'] if s['sample_id'] in keep]
        assert len(T['samples']) == len(keep), 'unknown sample ids'
    dmf = pd.read_csv(a.donor_map, dtype=str)
    if a.map_task:
        dmf = dmf[dmf['task'] == a.map_task]
    dm = dmf.drop_duplicates('sample_id').set_index('sample_id')['donor_id']
    if a.only_mapped:
        T['samples'] = [s for s in T['samples'] if s['sample_id'] in dm.index]
    if a.genes_from_parquet:
        labels, genes = map_genes(T, a.genes_from_parquet)
    else:
        genes = [str(g) for g in T['genes_top50']]; labels = genes
    r11 = dict(task_json=a.task_json, encoders=encs.split('+'), context=context, head=head, genes=genes,
               gene_labels=labels, unit=a.unit, arm=a.arm)
    if a.round3_td:
        td = json.load(open(a.round3_td))
        ids = {s['sample_id'] for s in td['samples']}
        miss = ids - {s['sample_id'] for s in T['samples']}
        assert not miss, f'round 3 samples absent from the corpus task: {sorted(miss)}'
        td['_r11'] = r11; td['label_set'] = f"{td['label_set']}_corpus_{a.arm}"
        return td
    samples, center_of = [], {}
    for s in sorted(T['samples'], key=lambda s: s['sample_id']):
        assert s['sample_id'] in dm.index, s['sample_id']
        d = dm[s['sample_id']]; c = str(s['center_id']); center_of[s['sample_id']] = c
        u = c if a.unit == 'center' else d
        samples.append(dict(sample_id=s['sample_id'], donor_id=u, hest_patient=u, donor_label_status='corpus',
                            resolution_group=c, session=None, true_donor=d))
    ids = [s['sample_id'] for s in samples]; unit = {s['sample_id']: s['donor_id'] for s in samples}
    units = sorted(set(unit.values()))
    donor_folds = [dict(fold=u, test=[i for i in ids if unit[i] == u], train=[i for i in ids if unit[i] != u]) for u in units]
    slide_folds = [dict(fold=i, test=[i], train=[j for j in ids if j != i]) for i in ids]
    td = dict(task_def_version=1, task=a.tag or T['name'], label_set=f"corpus_{a.unit}_{a.arm}", source='corpus',
              samples=samples, target_genes=dict(list=labels, n=len(labels)),
              folds=dict(patient=donor_folds, donor=donor_folds, slide_out=slide_folds, random=dict(n_repeats=a.n_repeats)),
              _r11=r11)
    td['_r11']['slide_out_degenerate'] = all(len(f['test']) == 1 for f in donor_folds)
    td['_r11']['n_units'] = len(units)
    return td


def run(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--arm', required=True, choices=sorted(ARMS)); ap.add_argument('--task-json', required=True)
    ap.add_argument('--donor-map', required=True); ap.add_argument('--designs', required=True)
    ap.add_argument('--fit-designs', required=True); ap.add_argument('--map-task', default='')
    ap.add_argument('--samples', default=''); ap.add_argument('--only-mapped', action='store_true')
    ap.add_argument('--genes-from-parquet', default=''); ap.add_argument('--round3-td', default='')
    ap.add_argument('--unit', default='donor', choices=['donor', 'center']); ap.add_argument('--n-repeats', type=int, default=1)
    ap.add_argument('--tag', default=''); ap.add_argument('--fold-shard', default='')
    a = ap.parse_args(argv)
    td = build_td(a)
    designs = a.designs.split(',')
    if 'slide_out' in designs and td['_r11'].get('slide_out_degenerate'):
        print('[designs] slide_out is degenerate (every donor has one slide); not enumerated', flush=True)
        designs = [d for d in designs if d != 'slide_out']
    fit = [d for d in a.fit_designs.split(',') if d in designs]
    assert fit, f'no fitted design left of {a.fit_designs} in {designs}'
    if a.unit == 'center':
        assert designs == ['donor'] and td['_r11']['n_units'] >= 3, (designs, td['_r11'].get('n_units'))
    tdp = os.path.abspath(f"td__{td['task']}__{a.unit}__{a.arm}.json")
    json.dump(td, open(tdp, 'w'), indent=1)
    STATE.update(head=td['_r11']['head'], inner='center' if a.unit == 'center' else 'donor')
    H.load_task = load_corpus; H.fit_base = fit_base_arm; H.scaler_pca_saw_only_T = scaler_check
    H.apply_size_match = apply_size_match; H._summaries = summaries_by_scale
    if a.fold_shard:
        k, K = (int(x) for x in a.fold_shard.split('/')); assert 0 <= k < K, a.fold_shard
        STATE['shard'] = (k, K, set(fit)); H.size_match_groups = size_match_groups_shard
    os.environ['GIT_OPTIONAL_LOCKS'] = '0'
    label = f"{a.arm}{'_center' if a.unit == 'center' else ''}"
    argv_h = [label, '--task-def', tdp, '--out-dir', os.path.relpath(os.getcwd(), H.ROOT), '--designs', ','.join(designs),
              '--fit-designs', ','.join(fit), '--scores', 'abs', '--tag', f"__{td['task']}"]
    print('[harness]', ' '.join(argv_h), flush=True)
    rc = H.main(argv_h)
    if STATE['chosen']:
        ch = np.concatenate(STATE['chosen'])
        json.dump(dict(fits=len(STATE['chosen']), log10_alpha_over_n_quantiles={str(q): float(np.quantile(ch, q)) for q in (0, .1, .5, .9, 1)}),
                  open('ridgecv_chosen_alpha.json', 'w'), indent=1)
    return rc


def anchor(td_path, enc):
    os.environ['GIT_OPTIONAL_LOCKS'] = '0'
    argv_h = [enc, '--task-def', td_path, '--out-dir', os.path.relpath(os.getcwd(), H.ROOT), '--designs', 'random,patient,donor',
              '--fit-designs', 'random,donor', '--scores', 'abs', '--tag', '__anchor']
    print('[harness, unchanged]', ' '.join(argv_h), flush=True)
    return H.main(argv_h)


def selftest():
    rng = np.random.default_rng(zlib.crc32(b'r11c_conformal_selftest'))
    # 1. the ridgecv head against round11_closeout_predict.ridgecv_fold
    n, p, g = 900, 30, 4
    X = rng.normal(size=(n, p)) * rng.uniform(0.5, 3, p) + rng.normal(size=p)
    Yv = X @ rng.normal(size=(p, g)) * 0.1 + rng.normal(size=(n, g))
    unit = np.array([f'd{i % 15}' for i in range(n)], dtype=object)
    Tg = {'s': Yv}; S = P.Suff(X, Tg, unit)
    tr_units = [f'd{i}' for i in range(15) if i not in (2, 7, 11)]; te = ~np.isin(unit, tr_units)
    ref, _ = P.ridgecv_fold(S, X, Tg, unit, tr_units, te, P.inner_groups_for(tr_units, 'donor'))
    trm = ~te
    mine = RidgeCVHead().fit(X[trm], Yv[trm], unit[trm], 'donor').predict(X[te])
    d1 = float(np.abs(mine - ref['s']).max())
    print(f'selftest ridgecv head against predict.ridgecv_fold: {d1:.3e}')
    # 2. the two-scale r10 head against the harness's fit_base, each half
    n, p, g = 1200, 300, 5
    X = rng.normal(size=(n, p)); Y2 = X[:, :2 * g] * 0.3 + rng.normal(size=(n, 2 * g))
    pipe, A, reg, _ = fit_r10(X[:900], Y2[:900], g)
    d2 = 0.0
    for h in (slice(0, g), slice(g, 2 * g)):
        p0, A0, r0, _ = _orig['fit_base'](X[:900], Y2[:900, h])
        d2 = max(d2, float(np.abs(reg.predict(pipe.transform(X[900:]))[:, h] - r0.predict(p0.transform(X[900:]))).max()))
    print(f'selftest two-scale r10 head against harness fit_base: {d2:.3e}')
    assert d1 < 1e-8 and d2 < 1e-8, (d1, d2)
    print('selftest passed')
    return 0


def _order_by_cells(df, pos):
    key = [cell_key(*r) for r in df[['design', 'fold', 'repeat', 'cal_draw']].itertuples(index=False)]
    idx = np.array([pos[x] for x in key])
    return df.iloc[np.argsort(idx, kind='mergesort')].reset_index(drop=True)


def merge(dirs):
    """Join the shards of one split run into the cwd, as the unsplit run would have written it."""
    import glob, hashlib
    import pyarrow.parquet as pq
    sh = [json.load(open(f'{d}/shard.json')) for d in dirs]
    K = sh[0]['K']
    assert sorted(s['k'] for s in sh) == list(range(K)) and all(s['K'] == K for s in sh), 'shards incomplete or repeated'
    for s in sh[1:]:
        for f in ('cell_order', 'folds_all', 'n_match', 'fit_designs'):
            assert s[f] == sh[0][f], f'shards disagree on {f}'
    mine = [f for s in sh for f in s['folds_mine']]
    assert sorted(mine) == sh[0]['folds_all'] and len(set(mine)) == len(mine), 'folds not partitioned'
    f64 = [glob.glob(f'{d}/pergene_f64*.parquet') for d in dirs]
    assert all(len(x) == 1 for x in f64), f64
    names = {os.path.basename(x[0]) for x in f64}; assert len(names) == 1, names
    suf = names.pop()[len('pergene_f64'):-len('.parquet')]
    pos = {c: i for i, c in enumerate(sh[0]['cell_order'])}
    pg = _order_by_cells(pd.concat([pq.read_table(x[0]).to_pandas() for x in f64], ignore_index=True), pos)
    rd = lambda p: pd.read_csv(p, dtype={'fold': str})
    cal = _order_by_cells(pd.concat([rd(f'{d}/a1_calibration_units{suf}.csv') for d in dirs], ignore_index=True), pos)
    h3 = _order_by_cells(pd.concat([rd(f'{d}/h3_disjointness{suf}.csv') for d in dirs], ignore_index=True), pos)
    assert len(cal) == len(pos), (len(cal), len(pos))
    out = os.getcwd()
    cal.to_csv(f'{out}/a1_calibration_units{suf}.csv', index=False)
    h3.to_csv(f'{out}/h3_disjointness{suf}.csv', index=False)
    print(f'[merge] {K} shards, {len(pg):,} per-gene rows, {len(cal)} cells, {len(h3)} fits; suffix {suf}', flush=True)
    summaries_by_scale(out, suf, pg, cal, None)
    H._parquet(out, suf, pg, H.PG_COLS)
    md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()
    rec = []
    for d, s in zip(dirs, sh):
        runs = open(f'{d}/runs.txt').read().strip() if os.path.exists(f'{d}/runs.txt') else ''
        rec.append(dict(dir=d, k=s['k'], runs=runs, files={os.path.basename(p): md5(p) for p in sorted(glob.glob(f'{d}/*'))
                                                         if os.path.isfile(p)}))
    json.dump(dict(K=K, suffix=suf, shards=rec), open(f'{out}/merge.json', 'w'), indent=1)
    print('[merge] done', flush=True)
    return 0


def compare(a, b):
    """Every a1_*, h3_* and calibration-unit table, and the per-gene parquet, of two runs: identical up to 1e-12."""
    import glob
    import pyarrow.parquet as pq
    fa = sorted(os.path.basename(p) for p in glob.glob(f'{a}/a1_*.csv') + glob.glob(f'{a}/h3_*.csv') + glob.glob(f'{a}/pergene__*.parquet'))
    fb = sorted(os.path.basename(p) for p in glob.glob(f'{b}/a1_*.csv') + glob.glob(f'{b}/h3_*.csv') + glob.glob(f'{b}/pergene__*.parquet'))
    assert fa == fb and fa, (fa, fb)
    worst, bad = 0.0, []
    for n in fa:
        if n.endswith('.parquet'):
            x, y = pq.read_table(f'{a}/{n}').to_pandas(), pq.read_table(f'{b}/{n}').to_pandas()
        else:
            x, y = pd.read_csv(f'{a}/{n}', dtype={'fold': str}), pd.read_csv(f'{b}/{n}', dtype={'fold': str})
        if list(x.columns) != list(y.columns) or len(x) != len(y):
            bad.append(f'{n}: shape or columns differ'); continue
        dmax = 0.0
        for c in x.columns:
            if pd.api.types.is_numeric_dtype(x[c]) and pd.api.types.is_numeric_dtype(y[c]) and not pd.api.types.is_bool_dtype(x[c]):
                u, v = x[c].to_numpy(float), y[c].to_numpy(float)
                if not np.array_equal(np.isnan(u), np.isnan(v)):
                    bad.append(f'{n}.{c}: missing values differ'); continue
                m = ~np.isnan(u)
                dmax = max(dmax, float(np.abs(u[m] - v[m]).max()) if m.any() else 0.0)
            elif not (x[c].astype(str) == y[c].astype(str)).all():
                bad.append(f'{n}.{c}: values differ')
        worst = max(worst, dmax)
        print(f'[compare] {n}: {len(x)} rows, max abs numeric difference {dmax:.3e}', flush=True)
    print(f'[compare] {len(fa)} files; worst {worst:.3e}; {len(bad)} mismatches', flush=True)
    for x in bad:
        print('  ', x, flush=True)
    return 0 if (not bad and worst <= 1e-12) else 1


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'selftest':
        sys.exit(selftest())
    if cmd == 'anchor':
        sys.exit(anchor(sys.argv[2], sys.argv[3]))
    if cmd == 'merge':
        sys.exit(merge(sys.argv[2:]))
    if cmd == 'compare':
        sys.exit(compare(sys.argv[2], sys.argv[3]))
    sys.exit(run(sys.argv[2:]))
