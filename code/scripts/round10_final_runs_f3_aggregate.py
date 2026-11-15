"""Round 10, track final-runs, stage F3: the aggregate tables of plan section 5d.8, step 5.

Usage: round10_final_runs_f3_aggregate.py <F3_results_dir> <out_dir>
  <F3_results_dir>  the committed F3 aggregates (results/round10/final_runs/F3 of a commit, extracted by
                    `git archive <commit> results/round10/final_runs/F3`)
  <out_dir>         where the tables are written (committed as results/round10/final_runs/F3/aggregate/)

Every table is a selection or a summary over cells of a committed item aggregate. Nothing is re-estimated
and no bulk file is read. Verdicts are copied from the item outputs. Where the item's own table and its
stated rule allow, the verdict is re-derived beside it (column verdict_rederived), so a disagreement shows.

Outputs: f3_predictions.csv (one row per prediction of plan 5d.7, plus descriptive rows for open points 1
and 6), one table per item over every axis the item varied (t*.csv), f3_aggregate_manifest.json (each
output with its row count, each input with its md5).

The mu note. Regime B's mu is the donor mean over morphology-joined spots, while the committed mu cluster
values (regime A's side of regcomp) average all spots, so on every HEST and HEST-1k corpus population the
regcomp mu rows compare two estimands (regcomp's cv_max_rel up to 0.269, f3_regcomp_checks.json; the lead's
check unit regimeB/regcomp_mu_check confirmed it on CCRCC uni_v2). ACS by state carries no morphology join
and its mu matches. The regcomp tables keep the mu rows with mu_estimand_mismatch = True for estimand mu on
any task other than ACS_STATES, and every regcomp summary excludes those rows.
"""
import hashlib, json, os, sys, traceback
import numpy as np
import pandas as pd

F3, out = sys.argv[1:3]
os.makedirs(out, exist_ok=True)
REL = 'results/round10/final_runs/F3'
HEST = ['CCRCC', 'CCRCC_merged', 'INDIANA_KIDNEY', 'LUNG_XENIUM']
MAP_ALIASES = ['CCRCC_23merged']  # the map's name for CCRCC_merged (23 donors)
CORPUS = ['kidney__Visium', 'breast__Spatial_Transcriptomics', 'bowel__Visium', 'brain__Visium',
          'breast__Xenium', 'lung__Xenium']
TASKS = HEST + MAP_ALIASES + ['ACS_STATES'] + CORPUS
inputs, outputs, errors, log = {}, {}, [], []
PRED = []


def note(s):
    log.append(s); print(s, flush=True)


def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def path(rel):
    p = os.path.join(F3, rel)
    if rel not in inputs:
        inputs[rel] = md5(p)
    return p


def csv(rel, **kw):
    return pd.read_csv(path(rel), **kw)


def js(rel):
    with open(path(rel)) as f:
        return json.load(f)


def src(rel):
    return f'{REL}/{rel}'


def wr(df, name):
    df.to_csv(os.path.join(out, name), index=False)
    outputs[name] = int(len(df))
    note(f'wrote {name}: {len(df)} rows')


def order(df, extra=()):
    df = df.copy()
    keys = []
    if 'task' in df.columns:
        df['_o'] = df.task.map({t: i for i, t in enumerate(TASKS)}).fillna(len(TASKS))
        keys = ['_o', 'task']
    keys += [c for c in extra if c in df.columns]
    df = df.sort_values(keys, kind='stable') if keys else df
    return df.drop(columns=[c for c in ['_o'] if c in df.columns]).reset_index(drop=True)


def kv(d):
    out_ = []
    for k, v in d.items():
        if isinstance(v, (float, np.floating)):
            v = repr(float(v))
        out_.append(f'{k}={v}')
    return '; '.join(out_)


def pred(prediction, scored_on, verdict, rederived, numbers, source, rule=''):
    PRED.append({'prediction': prediction, 'scored_on': scored_on, 'verdict': verdict,
                 'verdict_rederived': rederived,
                 'agree': (None if rederived in (None, '', 'not re-derivable') or verdict == 'descriptive'
                           or str(verdict).startswith('not scored') else bool(str(verdict) == str(rederived))),
                 'numbers': kv(numbers), 'source_file': source, 'rederive_rule': rule})


def section(fn):
    try:
        fn()
    except Exception:
        tb = traceback.format_exc()
        errors.append(f'{fn.__name__}: {tb.strip().splitlines()[-1]}')
        note(f'SECTION FAILED {fn.__name__}\n{tb}')
    return fn


def combine(vs):
    vs = list(vs)
    if any(v == 'refuted' for v in vs):
        return 'refuted'
    if any(v == 'partly held' for v in vs):
        return 'partly held'
    return 'held'


def three_way(d, se):
    """d = signed distance to the threshold (positive on the holding side); a distance within 2 se is partly held."""
    if not np.isfinite(se):
        return 'held' if d > 0 else 'refuted'
    if d > 2 * se:
        return 'held'
    if d < -2 * se:
        return 'refuted'
    return 'partly held'


# ============================================================ 5d.1 the prediction-set map, P10.3
@section
def map_p103():
    p = csv('map/map_aggregate/map_p103.csv')
    ov = js('map/map_aggregate/map_p103_overall.json')
    rows = []
    for _, r in p.iterrows():
        if r.part == 1:
            d = r.margin - r.threshold
        else:
            d = r.threshold - abs(r.margin - 1.0)
        rows.append(three_way(d, r.se))
    p['verdict_rederived'] = rows
    p['agree'] = p.verdict == p.verdict_rederived
    wr(p, 't01_map_p103.csv')
    for (part, task), g in p.groupby(['part', 'task']):
        key = f'part{part}_{task}'
        v = ov.get(key, 'missing')
        if part == 1:
            i = g.margin.idxmin()
            nums = {'o_grid': ','.join(str(int(x)) for x in g.o), 'stat': g.stat.iloc[0],
                    'min_margin': g.loc[i, 'margin'], 'se_at_min': g.loc[i, 'se'], 'o_at_min': int(g.loc[i, 'o']),
                    'median_hcp': g.median_A.iloc[0], 'threshold': g.threshold.iloc[0],
                    'rows_held': int((g.verdict == 'held').sum()), 'rows': len(g), 'n_folds': int(g.n_folds.iloc[0])}
            rule = 'every o >= 9 of part 1: margin hcp - within_full > 0, partly held if within 2 se'
        else:
            i = (g.margin - 1).abs().idxmin()
            nums = {'o_grid': ','.join(str(int(x)) for x in g.o), 'stat': g.stat.iloc[0],
                    'min_ratio': g.margin.min(), 'max_ratio': g.margin.max(), 'se_at_min': g.loc[i, 'se'],
                    'threshold': g.threshold.iloc[0], 'rows_refuted': int((g.verdict == 'refuted').sum()),
                    'rows': len(g), 'n_folds': int(g.n_folds.iloc[0])}
            rule = 'o in 9,10,12,15: |within_full/within_plain - 1| <= 0.02, partly held if within 2 se'
        pred(f'P10.3 part {part}, {task}', '5d.1', v, combine(g.verdict_rederived), nums,
             src('map/map_aggregate/map_p103_overall.json'), rule)


@section
def map_tables():
    m = csv('map/map_aggregate/map_by_task.csv')
    sel = m[m.method.isin(['hcp', 'within_full', 'within_plain']) & np.isclose(m.alpha, 0.1)]
    wr(order(sel, ['encoder', 'scale', 'part', 'method', 'K', 'o']), 't02_map_by_task_p103_methods_alpha01.csv')
    g = m.groupby(['task', 'encoder', 'scale', 'part', 'method', 'alpha'], dropna=False)
    s = g.agg(cells=('o', 'size'), K_values=('K', lambda x: ','.join(str(int(v)) for v in sorted(x.unique()))),
              o_min=('o', 'min'), o_max=('o', 'max'),
              coverage_mean_min=('coverage_mean', 'min'), coverage_mean_median=('coverage_mean', 'median'),
              coverage_mean_max=('coverage_mean', 'max'), coverage_min_min=('coverage_min', 'min'),
              width_median_median_median=('width_median_median', 'median'),
              finite_mean_min=('finite_mean', 'min'),
              cells_not_all_finite=('finite_mean', lambda x: int((x < 1).sum()))).reset_index()
    wr(order(s, ['encoder', 'scale', 'part', 'method', 'alpha']), 't03_map_methods_summary.csv')


@section
def map_acs():
    a = csv('map/acs_prod/acs_o_sweep.csv')
    keys = ['task', 'label_set', 'encoder', 'method', 'score', 'alpha', 'o', 'K']
    s = a.groupby(keys, dropna=False).agg(n_folds=('fold', 'nunique'), n_rows=('fold', 'size'),
                                          coverage_mean=('coverage', 'mean'), coverage_min=('coverage', 'min'),
                                          width_median_median=('width_median', 'median'),
                                          width_mean_mean=('width_mean', 'mean'), finite_mean=('finite', 'mean'),
                                          k_meets_alpha01=('k_meets_alpha01', 'first')).reset_index()
    wr(order(s, ['label_set', 'method', 'score', 'alpha', 'K', 'o']), 't04_map_acs_o_sweep_summary.csv')


@section
def item7():
    s = csv('map/i7_aggregate/scores_by_task.csv')
    wr(order(s, ['encoder', 'method', 'score', 'o']), 't05_item7_scores_by_task.csv')
    mg = csv('map/i7_aggregate/scores_margins.csv')
    wr(order(mg, ['encoder', 'method', 'o', 'score', 'vs']), 't06_item7_scores_margins.csv')
    js('map/i7_aggregate/scores_checks.json')


# ============================================================ 5d.2 the institution axis, FR8
@section
def institution():
    fr8 = csv('institution/production/inst_fr8.csv')
    bc = csv('institution/production/inst_by_center.csv')
    sm = csv('institution/production/inst_summary.csv')
    wr(order(sm, ['encoder', 'scale', 'arm', 'alpha']), 't07_institution_summary.csv')
    wr(order(bc, ['encoder', 'scale', 'arm', 'alpha', 'center_unit']), 't08_institution_by_center.csv')
    rows = []
    for _, r in fr8.iterrows():
        h = bc[(bc.task == 'kidney__Visium') & (bc.encoder == 'uni_v2') & (bc.scale == 'log1p')
               & np.isclose(bc.alpha, 0.2) & (bc.arm == r.arm)]
        val = float(h.coverage_median_gene.median()) if len(h) else np.nan
        holds_re = (val < r.threshold) if r.comparison == 'lt' else (val >= r.threshold)
        v = 'held' if bool(r.holds) else 'refuted'
        vr = ('held' if holds_re else 'refuted') if np.isfinite(val) else 'not re-derivable'
        rr = r.to_dict(); rr.update({'value_rederived': val, 'n_centers_rederived': len(h),
                                     'verdict': v, 'verdict_rederived': vr})
        rows.append(rr)
        pred(f'FR8 clause {int(r.clause)}', '5d.2', v, vr,
             {'arm': r.arm, 'value': r.value, 'value_rederived': val, 'threshold': r.threshold,
              'comparison': r.comparison, 'n_centers': int(r.n_centers), 'per_center': r.per_center},
             src('institution/production/inst_fr8.csv'),
             'kidney__Visium uni_v2 log1p alpha 0.2: median over centers of coverage_median_gene (inst_by_center.csv)')
    wr(pd.DataFrame(rows), 't09_institution_fr8.csv')


# ============================================================ 5d.3 (i) regime A against regime B, R10-F3a
RC = 'regimeB/aggregate_v1/regcomp/'


def mu_flag(df):
    df = df.copy()
    df['mu_estimand_mismatch'] = (df.estimand == 'mu') & (df.task != 'ACS_STATES')
    return df


def narrow_summary(g):
    return pd.Series({'n': len(g), 'B_narrower': int((g.median_ratio_mean_width < 1).sum()),
                      'share_B_narrower_cells': float((g.median_ratio_mean_width < 1).mean()),
                      'median_ratio_mean_width': float(g.median_ratio_mean_width.median()),
                      'median_ratio_median_width': float(g.median_ratio_median_width.median()),
                      'median_share_genes_B_narrower': float(g.share_B_narrower.median()),
                      'cov_A_median': float(g.cov_A.median()), 'cov_A_min': float(g.cov_A.min()),
                      'cov_B_median': float(g.cov_B.median()), 'cov_B_min': float(g.cov_B.min()),
                      'mcse_cov_A_max': float(g.mcse_cov_A.max()), 'mcse_cov_B_max': float(g.mcse_cov_B.max())})


@section
def regcomp():
    ck = js(RC + 'f3_regcomp_checks.json')
    a = mu_flag(csv(RC + 'f3_regcomp_r10f3a.csv'))
    wr(order(a, ['encoder', 'scale', 'n_L_A', 'budget_A', 'c']), 't11_regcomp_r10f3a_primary.csv')
    prim = a[(a.pair == 'fix1') & (a.estimand == 'theta3') & np.isclose(a.c, 10) & ~a.mu_estimand_mismatch]
    n = len(prim); k = int((prim.median_ratio_mean_width < 1).sum()); share = k / n if n else np.nan
    pc = ck['r10f3a']['primary']
    pred('R10-F3a', '5d.3 (i)', ck['r10f3a']['verdict'], 'held' if share >= 0.8 else 'refuted',
         {'n': pc['n'], 'B_narrower': pc['B_narrower'], 'share': pc['share'], 'median_ratio': pc['median_ratio'],
          'n_rederived': n, 'B_narrower_rederived': k, 'share_rederived': share, 'threshold': 0.8,
          'round5_E3_4': '210 of 232 (C_ppi)'},
         src(RC + 'f3_regcomp_checks.json'),
         'fix1, theta3, c 10, HEST tasks with CCRCC_merged and ACS: share of comparisons with median mean-width ratio < 1 >= 0.8')
    c = mu_flag(csv(RC + 'f3_regcomp_comparisons.csv'))
    note(f'regcomp comparisons: {len(c)} rows, mu rows flagged {int(c.mu_estimand_mismatch.sum())}')
    wr(order(c, ['encoder', 'scale', 'estimand', 'pair', 'c', 'n_L_A', 'budget_A']), 't10_regcomp_comparisons.csv')
    k_ = c[~c.mu_estimand_mismatch]
    s = k_.groupby(['task', 'scale', 'estimand', 'pair', 'c'])[['median_ratio_mean_width', 'median_ratio_median_width', 'share_B_narrower', 'cov_A', 'cov_B', 'mcse_cov_A', 'mcse_cov_B']].apply(narrow_summary).reset_index()
    wr(order(s, ['scale', 'estimand', 'pair', 'c']), 't12_regcomp_summary_by_task.csv')
    s2 = k_.groupby(['task', 'encoder', 'scale', 'estimand', 'pair'])[['median_ratio_mean_width', 'median_ratio_median_width', 'share_B_narrower', 'cov_A', 'cov_B', 'mcse_cov_A', 'mcse_cov_B']].apply(narrow_summary).reset_index()
    wr(order(s2, ['encoder', 'scale', 'estimand', 'pair']), 't12b_regcomp_summary_by_task_encoder.csv')
    h = k_[k_.task.isin(HEST + ['ACS_STATES'])]
    s3 = h.groupby(['scale', 'estimand', 'pair', 'c', 'n_L_A', 'budget_A'])[['median_ratio_mean_width', 'median_ratio_median_width', 'share_B_narrower', 'cov_A', 'cov_B', 'mcse_cov_A', 'mcse_cov_B']].apply(narrow_summary).reset_index()
    wr(s3.sort_values(['scale', 'estimand', 'pair', 'c', 'n_L_A', 'budget_A']), 't13_regcomp_summary_by_design_hest_acs.csv')
    # the "beside" rows of the item's checks, recomputed with the mu rows excluded
    hc = c[c.task.isin(HEST + ['ACS_STATES']) & np.isclose(c.c, 10)]
    defs = {'norm_refit_fix1_theta3': (hc.pair == 'fix1') & (hc.estimand == 'theta3') & (hc.scale == 'norm_refit'),
            'fix1_theta2': (hc.pair == 'fix1') & (hc.estimand == 'theta2'),
            'fix1_mu': (hc.pair == 'fix1') & (hc.estimand == 'mu'),
            'ppi_theta3_log1p': (hc.pair == 'ppi') & (hc.estimand == 'theta3') & hc.scale.isin(['log1p', 'log_income']),
            'classical_theta3_log1p': (hc.pair == 'classical') & (hc.estimand == 'theta3') & hc.scale.isin(['log1p', 'log_income'])}
    rows = []
    for name, msk in defs.items():
        g = hc[msk]; gk = g[~g.mu_estimand_mismatch]
        com = ck['r10f3a']['beside'].get(name, {})
        rows.append({'group': name, 'rows_all': len(g), 'rows_mu_mismatch_excluded': int(g.mu_estimand_mismatch.sum()),
                     'n': len(gk), 'B_narrower': int((gk.median_ratio_mean_width < 1).sum()),
                     'share': float((gk.median_ratio_mean_width < 1).mean()) if len(gk) else np.nan,
                     'median_ratio': float(gk.median_ratio_mean_width.median()) if len(gk) else np.nan,
                     'n_committed': com.get('n'), 'B_narrower_committed': com.get('B_narrower'),
                     'share_committed': com.get('share'), 'median_ratio_committed': com.get('median_ratio')})
    g = c[c.pair == 'fix1']; gk = g[~g.mu_estimand_mismatch]; com = ck['r10f3a']['beside'].get('fix1_all_tasks_all_c', {})
    rows.append({'group': 'fix1_all_tasks_all_c', 'rows_all': len(g), 'rows_mu_mismatch_excluded': int(g.mu_estimand_mismatch.sum()),
                 'n': len(gk), 'B_narrower': int((gk.median_ratio_mean_width < 1).sum()),
                 'share': float((gk.median_ratio_mean_width < 1).mean()), 'median_ratio': float(gk.median_ratio_mean_width.median()),
                 'n_committed': com.get('n'), 'B_narrower_committed': com.get('B_narrower'),
                 'share_committed': com.get('share'), 'median_ratio_committed': com.get('median_ratio')})
    wr(pd.DataFrame(rows), 't14_regcomp_beside_mu_excluded.csv')


# ============================================================ 5d.3 (ii) and 5d.5, V and FR7
BX = 'regimeB/aggregate_v1/box/'


@section
def box():
    ck = js(BX + 'f3_box_checks.json')['fr7']
    c1 = csv(BX + 'f3_fr7_clause1.csv')
    c2 = csv(BX + 'f3_fr7_clause2.csv')
    c1['within_rederived'] = (c1.median_coverage - 0.90).abs() <= 0.03 + 1e-12
    wr(order(c1, ['source', 'encoder', 'scale', 'estimand', 'm']), 't17_box_fr7_clause1.csv')
    c2['strictly_larger_rederived'] = c2.median_m_unbounded > c2.median_m_bounded
    wr(order(c2), 't18_box_fr7_clause2.csv')
    pr = c1[c1.primary.astype(str) == 'True']
    v1 = 'held' if (len(pr) and pr.within_rederived.all()) else 'refuted'
    pred('FR7 clause 1', '5d.3 (ii)', ck['clause1']['verdict'], v1,
         {'cells': ck['clause1']['cells'], 'within': ck['clause1']['within'], 'max_abs_dev': ck['clause1']['max_abs_dev'],
          'cov_min': ck['clause1']['cov_range'][0], 'cov_max': ck['clause1']['cov_range'][1],
          'cells_rederived': len(pr), 'within_rederived': int(pr.within_rederived.sum()),
          'max_abs_dev_rederived': float((pr.median_coverage - 0.9).abs().max())},
         src(BX + 'f3_box_checks.json'), 'primary rows of f3_fr7_clause1.csv: |median coverage - 0.90| <= 0.03 in every cell')
    v2 = 'held' if c2.strictly_larger_rederived.all() else 'refuted'
    pred('FR7 clause 2', '5d.3 (ii)', ck['clause2']['verdict'], v2,
         {'tasks': ck['clause2']['tasks'], 'strictly_larger': ck['clause2']['strictly_larger'],
          'tasks_rederived': len(c2), 'strictly_larger_rederived': int(c2.strictly_larger_rederived.sum())},
         src(BX + 'f3_box_checks.json'), 'per task (uni_v2, primary scale, mu): median unbounded m > median bounded m')
    pred('FR7', '5d.3 (ii)', ck['verdict'], 'held' if (v1 == 'held' and v2 == 'held') else 'refuted',
         {'clause1': ck['clause1']['verdict'], 'clause2': ck['clause2']['verdict']},
         src(BX + 'f3_box_checks.json'), 'both clauses hold')
    ts = csv(BX + 'f3_box_task_summary.csv')
    wr(order(ts, ['encoder', 'scale', 'lambda', 'scope']), 't15_box_task_summary_bounded_unbounded.csv')
    cv = csv(BX + 'f3_box_coverage_summary.csv')
    wr(order(cv, ['encoder', 'scale', 'm']), 't16_box_coverage_by_m_long.csv')
    w = cv.pivot_table(index=['task', 'encoder', 'scale'], columns='m', values='median_coverage', aggfunc='first')
    w.columns = [f'cov_m{int(x)}' for x in w.columns]
    w = w.reset_index()
    keep = ['task', 'encoder', 'scale', 'lambda', 'scope', 'genes', 'Lambda0_median',
            'median_m_bounded', 'median_m_unbounded', 'n_none_bounded', 'n_none_unbounded',
            'median_coverage_at_bounded', 'median_coverage_at_unbounded',
            'median_v_max_at_bounded', 'median_v_max_at_unbounded',
            'median_Gstar_B_at_bounded', 'median_Gstar_B_at_unbounded',
            'spearman_cov_GstarB_bounded', 'spearman_cov_GstarB_unbounded',
            'median_kappa_e_regimeA', 'median_Gstar_e_regimeA']
    v = ts[[k for k in keep if k in ts.columns]].merge(w, on=['task', 'encoder', 'scale'], how='left')
    wr(order(v, ['encoder', 'scale', 'lambda', 'scope']), 't16b_V_side_by_side.csv')


# ============================================================ 5d.3 (iii) allocation
@section
def allocation():
    r = csv('allocation/aggregate/f3_allocation_rows.csv')
    wr(order(r, ['encoder', 'scale', 'estimand', 'gene_scope', 'n_L']), 't19_allocation_rows.csv')
    v = csv('allocation/aggregate/f3_allocation_vs_r5.csv')
    wr(order(v, ['encoder', 'form', 'n_L']), 't20_allocation_vs_r5.csv')
    agg = {f'{c}_median': (c, 'median') for c in ['one_minus_R2_w', 'one_minus_R2_c', 'rho_c', 'm_star_classical_cd10',
                                                   'm_star_PP_cd10', 'm_star_classical_cd100', 'm_star_PP_cd100',
                                                   'm_star_classical_cd1000', 'm_star_PP_cd1000', 'ratio_PP_over_classical']}
    agg.update({'cells': ('task', 'size'), 'ratio_PP_over_classical_min': ('ratio_PP_over_classical', 'min'),
                'ratio_PP_over_classical_max': ('ratio_PP_over_classical', 'max')})
    s = r.groupby(['task', 'scale', 'estimand', 'gene_scope', 'n_L'], dropna=False).agg(**agg).reset_index()
    wr(order(s, ['scale', 'estimand', 'gene_scope', 'n_L']), 't21_allocation_summary_over_encoders.csv')


# ============================================================ 5d.3 (iv) balance, P10.1 part 2
@section
def balance():
    p = csv('balance/aggregate/f3_p101_part2.csv')
    D = ['D0_classical', 'D2_rej_t', 'cube_S4b']
    rows = []
    for _, r in p.iterrows():
        tied, swaps = [], []
        for i in range(3):
            for j in range(i + 1, 3):
                a, b = D[i], D[j]
                d7 = r[f'r7_{a}'] - r[f'r7_{b}']; d10 = r[f'r10_{a}'] - r[f'r10_{b}']
                if abs(d7) < 0.01:
                    tied.append(f'{a}/{b}')
                elif np.sign(d7) != np.sign(d10):
                    swaps.append(f'{a}/{b}')
        vr = 'held' if not swaps else 'refuted'
        rr = r.to_dict(); rr.update({'tied_rederived': ';'.join(tied), 'swaps_rederived': ';'.join(swaps),
                                     'verdict_rederived': vr})
        rows.append(rr)
        pred(f'P10.1 part 2, p_a {r.p_a}, {r.family}', '5d.3 (iv)', r.verdict, vr,
             {'n_cells': int(r.n_cells), **{f'r7_{d}': r[f'r7_{d}'] for d in D}, **{f'r10_{d}': r[f'r10_{d}'] for d in D},
              'resolved_swaps': r.resolved_swaps, 'tied_in_reference': r.tied_in_reference},
             src('balance/aggregate/f3_p101_part2.csv'),
             "tissue rows n_L 8, wr_D0cl: every design pair not tied in round 7 (|diff| >= 0.01) keeps round 7's order")
    wr(pd.DataFrame(rows), 't24_balance_p101_part2.csv')
    m = csv('balance/aggregate/f3_balance_matched.csv')
    m['interval_formed'] = m.coverage.notna()
    wr(m.sort_values(['domain', 'scale', 'gene_scope', 'n_L', 'p_a', 'dname']), 't22_balance_matched.csv')
    lm = csv('balance/aggregate/f3_balance_limits.csv')
    lm['no_interval_formed'] = (lm.n_L == 4) & lm.dname.str.startswith('D2lim')
    lm['interval_formed'] = lm.coverage.notna()
    note(f'balance limits: n_L 4 D2lim rows {int(lm.no_interval_formed.sum())}, '
         f'of which without coverage {int((lm.no_interval_formed & ~lm.interval_formed).sum())}; '
         f'rows without coverage overall {int((~lm.interval_formed).sum())}')
    wr(lm.sort_values(['domain', 'scale', 'gene_scope', 'n_L', 'p_a', 'dname']), 't23_balance_limits.csv')
    c = csv('balance/aggregate/f3_balance_cells.csv')
    keys = ['scale', 'estimand', 'gene_scope', 'n_L', 'design', 'balance', 'p_a', 'estimator', 'variance']
    s = c.groupby(keys, dropna=False).agg(cells=('task', 'size'), tasks=('task', 'nunique'),
                                         coverage_median_median=('coverage_median', 'median'),
                                         coverage_median_min=('coverage_median', 'min'),
                                         share_formed_min=('share_formed_min', 'min'),
                                         wr_D0cl_median=('wr_D0cl', 'median'), wr_D0same_median=('wr_D0same', 'median'),
                                         share_abs_bias_z_gt3_max=('share_abs_bias_z_gt3', 'max')).reset_index()
    wr(s.sort_values(keys, na_position='first'), 't25_balance_cells_summary.csv')
    s2 = c.groupby(['task', 'scale', 'estimand', 'n_L', 'design', 'balance', 'p_a', 'estimator'], dropna=False).agg(
        cells=('encoder', 'size'), coverage_median_median=('coverage_median', 'median'),
        wr_D0cl_median=('wr_D0cl', 'median'), wr_D0same_median=('wr_D0same', 'median')).reset_index()
    wr(order(s2, ['scale', 'estimand', 'n_L', 'design', 'balance', 'p_a', 'estimator']), 't25b_balance_by_task.csv')


# ============================================================ 5d.3 (v) take-all
@section
def takeall():
    c = csv('takeall/aggregate/f3_takeall_cells.csv')
    wr(order(c, ['encoder', 'scale', 'estimand', 'gene_scope', 'k', 'n_L', 'method']), 't26_takeall_cells.csv')
    s = c.groupby(['scale', 'estimand', 'gene_scope', 'k', 'n_L', 'method'], dropna=False).agg(
        cells=('task', 'size'), tasks=('task', 'nunique'), median_coverage_median=('median_coverage', 'median'),
        median_coverage_min=('median_coverage', 'min'), p10_coverage_min=('p10_coverage', 'min'),
        median_wr_D0_median=('median_wr_D0', 'median'), median_wr_D0same_median=('median_wr_D0same', 'median')).reset_index()
    wr(s, 't27_takeall_summary.csv')
    wr(csv('takeall/aggregate/f3_takeall_vs_r9.csv'), 't28_takeall_vs_r9.csv')


# ============================================================ 5d.4 E8
@section
def e8():
    j = csv('e8/e8_joint.csv')
    og = j.on_o_grid.astype(str) == 'True'
    drop = [c for c in ['guarantee', 'diff_seed_tag'] if c in j.columns]
    on = j[og].drop(columns=drop)
    wr(order(on, ['encoder', 'scale', 'estimand', 'm', 'part', 'K']), 't29_e8_joint_on_grid.csv')
    # off-grid rows (m not on the map's o grid) carry no set by construction; the set counts are over on-grid rows
    j['_off'] = ~og
    j['_noset'] = og & j.overall_method.isna()
    j['_nonoextra'] = og & j.noextra_method.isna()
    j['_nofinite_noextra'] = og & ~np.isfinite(pd.to_numeric(j.noextra_width_median, errors='coerce'))
    keys = ['task', 'encoder', 'scale', 'estimand']
    s = j.groupby(keys).agg(rows=('m', 'size'), rows_off_grid=('_off', 'sum'),
                            on_grid_rows_without_valid_set=('_noset', 'sum'),
                            on_grid_rows_without_noextra_set=('_nonoextra', 'sum'),
                            on_grid_rows_without_finite_noextra_set=('_nofinite_noextra', 'sum')).reset_index()
    s['rows_on_grid'] = s.rows - s.rows_off_grid
    tot = {'task': 'ALL', 'encoder': '', 'scale': '', 'estimand': ''}
    tot.update({c: int(s[c].sum()) for c in s.columns if c.startswith('rows') or c.startswith('on_grid')})
    s = pd.concat([order(s, ['encoder', 'scale', 'estimand']), pd.DataFrame([tot])], ignore_index=True)
    wr(s, 't30_e8_row_counts.csv')
    o = j[og]
    s2 = o.groupby(['task', 'encoder', 'scale', 'estimand', 'm']).agg(
        rows=('K', 'size'), K_values=('K', lambda x: ','.join(str(v) for v in sorted(x.unique()))),
        regB_wr_fix1=('regB_wr_fix1', 'first'), regB_wr_se=('regB_wr_se', 'first'),
        regB_cov_fix1=('regB_cov_fix1', 'first'),
        overall_width_median_min=('overall_width_median', 'min'),
        noextra_width_median_min=('noextra_width_median', 'min'),
        diff_width_median_median=('diff_width_median', 'median'),
        share_overall_needs_extra=('overall_needs_extra_labels', lambda x: float((x.astype(str) == 'True').mean()))).reset_index()
    wr(order(s2, ['encoder', 'scale', 'estimand', 'm']), 't31_e8_on_grid_by_m.csv')
    js('e8/e8_checks.json')
    rb = 'regimeB/aggregate_v1/regimeB/'
    wr(csv(rb + 'f3_e8_f2check.csv'), 't32_e8_regB_f2check.csv')
    wr(order(csv(rb + 'f3_e8_wr.csv'), ['encoder', 'scale', 'estimand', 'm', 'form']), 't33_e8_regB_width_ratio.csv')


# ============================================================ 5d.6 open points
@section
def op1():
    s = js('reruns/limits_g1/f3_limits_g1_summary.json')
    r = csv('reruns/limits_g1/f3_limits_g1_compare_r07.csv')
    wr(r, 't34_op1_limits_ranges_all_vs_noG1.csv')
    wr(csv('reruns/limits_g1/f3_limits_g1_compare_r07b.csv'), 't35_op1_width_ratio_by_n_all_vs_noG1.csv')
    wr(csv('reruns/limits_g1/f3_limits_g1_dropped_cells.csv'), 't36_op1_dropped_cells.csv')
    anc = s.get('anchor', {})
    k = r[r.arm == 'kluger_ptd|cluster_boot'].set_index('n')
    nums = {'cells': s.get('cells'), 'cells_G_minus_n_eq_1': s.get('cells_G_minus_n_eq_1'),
            'anchors_bytes_identical': ','.join(f'{a}={v.get("bytes_identical")}' for a, v in anc.items() if isinstance(v, dict))}
    for n_ in (4, 16):
        if n_ in k.index:
            nums[f'kluger_n{n_}_median_all'] = k.loc[n_, 'median__all']; nums[f'kluger_n{n_}_median_noG1'] = k.loc[n_, 'median__noG1']
            nums[f'kluger_n{n_}_min_all'] = k.loc[n_, 'min__all']; nums[f'kluger_n{n_}_min_noG1'] = k.loc[n_, 'min__noG1']
    r['d_median'] = (r['median__noG1'] - r['median__all']).abs()
    nums['max_abs_change_median_any_arm_n'] = float(r.d_median.max())
    pred('Open point 1 (limits summaries without the G - n = 1 cells)', '5d.6 item 1', 'descriptive', None, nums,
         src('reruns/limits_g1/f3_limits_g1_summary.json'))


@section
def op2():
    t = csv('toy/grid/f3_toy_grid.csv')
    ts = js('toy/grid/toy_summary.json')
    wr(t.sort_values(['kind', 'coef', 'Gs', 'M0', 'm']), 't37_op2_toy_grid.csv')
    wr(order(csv('toy/heterogeneity/f3_heterogeneity_by_population.csv'), ['source', 'encoder', 'scale']),
       't38_op2_heterogeneity_by_population.csv')
    th = t[(t.kind == 'theta3') & (t.coef == 'fixed1')]
    lo = th[th.frac <= 0.05]; hi = th[th.frac >= 0.4]
    c1 = bool(len(lo)) and bool((lo.V_ratio >= 0.95).all())
    c2 = bool(len(hi)) and bool((hi.V_ratio < 0.85).all())
    half = th[np.isclose(th.frac, 0.5)].sort_values('M0')
    rise = []
    for gs, g in half.groupby('Gs'):
        if len(g) > 1:
            rise.append(bool(np.all(np.diff(g.V_ratio.values) > 0)))
    contra = any(rise)
    vr = 'held' if (c1 and c2 and not contra) else 'refuted'
    pred('Open point 2 (toy shortfall driven by the sampling fraction)', '5d.6 item 2',
         'not scored in the item output', vr,
         {'rows_theta3_fixed1': len(th), 'rows_frac_le_005': len(lo),
          'min_V_ratio_frac_le_005': float(lo.V_ratio.min()) if len(lo) else np.nan,
          'rows_frac_ge_04': len(hi), 'max_V_ratio_frac_ge_04': float(hi.V_ratio.max()) if len(hi) else np.nan,
          'frac05_V_ratio_by_Gs_M0': ';'.join(f'Gs{int(r.Gs)}_M0{int(r.M0)}={r.V_ratio:.6g}' for _, r in half.iterrows()),
          'rises_with_M0_at_frac05': contra, 'anchor_first_row_exact': ts.get('first_row_exact')},
         src('toy/grid/f3_toy_grid.csv'),
         'theta3, fixed coefficient: V_ratio >= 0.95 wherever m/M0 <= 0.05, < 0.85 wherever m/M0 >= 0.4, and no rise with M0 at m/M0 = 0.5')


@section
def op3():
    s = js('reruns/prod_aggregate/f3_prod_scores.json')['item3_prediction']
    b = csv('reruns/prod_aggregate/f3_boot_vs_uni_v2.csv')
    wr(csv('reruns/prod_aggregate/f3_boot_score_table.csv'), 't39_op3_boot_score_table.csv')
    b = b[b.encoder != 'uni_v2']
    sh = b.assign(w=b.d_cov.abs() <= 0.02 + 1e-12).groupby('arm').w.agg(['size', 'mean'])
    vr = 'held' if (len(sh) and (sh['mean'] >= 0.8).all()) else 'refuted'
    nums = {}
    for a in s['by_arm']:
        nums[f'{a["arm"]}_share'] = a['share_within_002']; nums[f'{a["arm"]}_cells'] = a['cells']
    col = b.groupby('arm').within_002.apply(lambda x: float((x.astype(str) == 'True').mean()))
    for arm, r in sh.iterrows():
        nums[f'{arm}_share_rederived_le002'] = r['mean']; nums[f'{arm}_cells_rederived'] = int(r['size'])
        nums[f'{arm}_share_within_002_column'] = col.get(arm)
    pred('Open point 3 (bootstrap arms under hoptimus0 and resnet50)', '5d.6 item 3', s['verdict'], vr, nums,
         src('reruns/prod_aggregate/f3_prod_scores.json'),
         'per arm, share of (task, scale, estimand, n_L, encoder) cells with |d_cov| <= 0.02 is >= 0.8 (the item column within_002 counts the boundary differently, both shown)')


@section
def op4():
    s = js('reruns/prod_aggregate/f3_prod_scores.json')['item4_prediction']
    r = csv('reruns/prod_aggregate/f3_limits_norm_refit_ranking.csv')
    wr(r, 't40_op4_limits_norm_refit_ranking.csv')
    g = r[r.reference == s.get('primary', 'F2_all_other_scales')]
    ident = {n_: bool((g[g.n == n_].rank_ref == g[g.n == n_].rank_norm_refit).all()) for n_ in (4, 8)}
    k4 = g[(g.n == 4) & (g.av == 'kluger_ptd|cluster_boot')]
    klow = bool(len(k4)) and bool(k4.rank_norm_refit.iloc[0] == g[g.n == 4].rank_norm_refit.min())
    if ident[4] and ident[8] and klow:
        vr = 'held'
    elif klow and (ident[4] or ident[8]):
        vr = 'partly held'
    else:
        vr = 'refuted'
    sc = s['scores'][s.get('primary', 'F2_all_other_scales')]
    pred('Open point 4 (limits arms on norm_refit)', '5d.6 item 4', s['verdict'], vr,
         {'n4_identical': sc['n4']['ranking_identical'], 'n8_identical': sc['n8']['ranking_identical'],
          'n8_kendall_tau': sc['n8']['kendall_tau'], 'kluger_lowest_n4': sc['n4']['kluger_lowest_norm_refit'],
          'n4_identical_rederived': ident[4], 'n8_identical_rederived': ident[8], 'kluger_lowest_n4_rederived': klow,
          'reference': s.get('primary')},
         src('reruns/prod_aggregate/f3_prod_scores.json'),
         'ranking by median coverage identical at n 4 and n 8 with Kluger lowest at n 4: held; one of the two: partly held')


@section
def op5():
    ck = js('regimeB/aggregate_v1/regimeB/f3_regB_checks.json')['op5']
    s = csv('regimeB/aggregate_v1/regimeB/f3_op5_score.csv')
    s['ok_both_rederived'] = ((s.median_ev_over_var >= 0.93) & (s.median_ev_over_var <= 1.05)
                              & ((s.median_coverage - 0.90).abs() <= 0.03 + 1e-12))
    wr(order(s, ['encoder', 'estimand', 'm']), 't41_op5_regB_norm_refit_score.csv')
    wr(order(csv('regimeB/aggregate_v1/regimeB/f3_regB_norm_summary.csv'), ['encoder', 'estimand', 'm', 'form']),
       't42_op5_regB_norm_refit_summary.csv')
    sc = s[s.task.isin(['CCRCC', 'INDIANA_KIDNEY', 'LUNG_XENIUM']) & (s.m >= 6) & (s.form == 'C_fix1')]
    vr = 'held' if (len(sc) and sc.ok_both_rederived.all()) else 'refuted'
    pred('Open point 5 (regime B on the HEST normalised scale)', '5d.6 item 5', ck['verdict'], vr,
         {'cells': ck['cells'], 'cells_ok_both': ck['cells_ok_both'], 'ev_min': ck['ev_range'][0], 'ev_max': ck['ev_range'][1],
          'cov_min': ck['cov_range'][0], 'cov_max': ck['cov_range'][1],
          'cells_rederived': len(sc), 'cells_ok_both_rederived': int(sc.ok_both_rederived.sum()),
          'CCRCC_merged_ok_both_beside': int(s[(s.task == 'CCRCC_merged') & (s.m >= 6)].ok_both_rederived.sum())},
         src('regimeB/aggregate_v1/regimeB/f3_regB_checks.json'),
         'CCRCC, INDIANA_KIDNEY, LUNG_XENIUM, C_fix1, m >= 6: 0.93 <= median E(V)/Var <= 1.05 and |median coverage - 0.90| <= 0.03')


@section
def op6():
    r = csv('reruns/r9g42/f3_r9g42_scores_side_by_side.csv')
    js('reruns/r9g42/f3_r9g42_summary.json')
    wr(r, 't43_op6_r9g42_scores_side_by_side.csv')
    same = (r.holds__all.astype(str) == r.holds__r9g42.astype(str))
    pred('Open point 6 (LUNG_XENIUM on round 9 42-gene subset)', '5d.6 item 6', 'descriptive', None,
         {'clauses': len(r), 'same_holds_at_both_scopes': int(same.sum()),
          'differing': ';'.join(f'{a}|{b}' for a, b in zip(r.prediction[~same], r.clause[~same]))},
         src('reruns/r9g42/f3_r9g42_scores_side_by_side.csv'))


@section
def op7():
    s = js('reruns/kappa_rise/f3_kappa_rise_summary.json')
    c = csv('reruns/kappa_rise/f3_kappa_rise_cells.csv')
    wr(csv('reruns/kappa_rise/f3_kappa_rise_counts.csv'), 't44_op7_kappa_rise_counts.csv')
    wr(csv('reruns/kappa_rise/f3_kappa_rise_by_G1.csv'), 't45_op7_kappa_rise_by_G1.csv')
    gen = (c.p_perm_two_sided < 0.05) & (c.fitted_rise_iqr >= 0.01)
    wr(order(c[c.classification == 'genuine_rise'], ['encoder', 'scale', 'estimand', 'n']), 't46_op7_genuine_rise_cells.csv')
    N = s['cells']; k = int(gen.sum())
    p = s['prediction']
    pred('Open point 7 (cells where coverage rises with kappa(e))', '5d.6 item 7', p['verdict'],
         'held' if k / N < 0.1 else 'refuted',
         {'genuine': p['genuine'], 'cells': p['cells'], 'share': p['share'], 'genuine_rederived': k,
          'share_rederived': k / N, 'classified_genuine_in_cells_table': int((c.classification == 'genuine_rise').sum()),
          'cells_examined': len(c)},
         src('reruns/kappa_rise/f3_kappa_rise_summary.json'),
         'genuine rise = permutation p < 0.05 and fitted rise over the IQR >= 0.01; share of 1,722 cells < 0.1')


# ============================================================ predictions and manifest
order_p = ['P10.1', 'P10.3', 'FR7', 'FR8', 'R10-F3a', 'Open point']
P = pd.DataFrame(PRED)
if len(P):
    P['_o'] = P.prediction.map(lambda s: next((i for i, k in enumerate(order_p) if s.startswith(k)), 99))
    P = P.sort_values('_o', kind='stable').drop(columns='_o')
wr(P, 'f3_predictions.csv')
dis = P[(P.agree == False)] if len(P) else P  # noqa: E712
note(f'predictions {len(P)}; verdict_rederived disagreements {len(dis)}')
for _, r in dis.iterrows():
    note(f'  DISAGREE {r.prediction}: verdict {r.verdict} rederived {r.verdict_rederived}')
man = {'script': 'round10_final_runs_f3_aggregate.py', 'F3_results_dir': F3,
       'mu_note': ('regcomp rows with estimand mu on any task other than ACS_STATES carry mu_estimand_mismatch = True '
                   'and are excluded from every regcomp summary; basis results/round10/final_runs/F3/regimeB/aggregate_v1/'
                   'regcomp/f3_regcomp_checks.json (cv_max_rel) and the lead check unit regimeB/regcomp_mu_check'),
       'outputs': {k: {'rows': v} for k, v in sorted(outputs.items())},
       'inputs': {f'{REL}/{k}': v for k, v in sorted(inputs.items())},
       'predictions': len(P), 'disagreements': int(len(dis)), 'section_errors': errors}
man['outputs']['f3_aggregate_manifest.json'] = {'rows': None}
with open(os.path.join(out, 'f3_aggregate_manifest.json'), 'w') as f:
    json.dump(man, f, indent=1, default=str)
note(f'wrote f3_aggregate_manifest.json: {len(outputs)} tables, {len(inputs)} inputs, {len(errors)} section errors')
for e in errors:
    note(f'  ERROR {e}')
sys.exit(1 if errors else 0)
