"""Round 10, track final-runs, F3 open point 3 (plan, section 5d.6 item 3): regime A configs that add the bootstrap
arms for hoptimus0 and resnet50.

usage: round10_final_runs_f3_reruns_boot_configs.py <regimeA_config_dir> <dst_dir> whole|parts [max_genes]
Reads every F2 regime A config f2_regimeA__<unit>.json whose `select.encoder` is hoptimus0 or resnet50 (30 units) and
writes, with everything else unchanged, `boot_select.encoder` = uni_v2, pkg, hoptimus0, resnet50 (the estimands stay
theta3, theta2 and mu). Seeds in round10_final_runs_f2_regimeA.py depend only on the population and n_L, so a config
that selects fewer populations reproduces the same rows for those populations.
  whole  one config per unit, f3_rerun_boot__<unit>.json;
  parts  configs that split each unit by estimand group (mu; theta2; theta3 with theta1, which has no bootstrap arm)
         and, within a group, into contiguous chunks of at most max_genes genes (default 120) in the script's own sorted
         gene order: f3_rerun_boot__<unit>__<group>[__g<k>of<K>].json, with `select.gene` listing the chunk. The gene
         lists come from the unit's cluster values after its own `select`.
Writes boot_configs_manifest.csv (config, unit, estimands, genes, boot populations) beside the configs.
"""
import glob, json, math, os, sys
import numpy as np, pandas as pd

src, dst, mode = sys.argv[1:4]
max_genes = int(sys.argv[4]) if len(sys.argv) > 4 else 120
os.makedirs(dst, exist_ok=True)
ENC = ['hoptimus0', 'resnet50']
GROUPS = [('mu', ['mu']), ('theta2', ['theta2']), ('theta3', ['theta3', 'theta1'])]
BOOT_EST = {'theta3', 'theta2', 'mu'}
rows = []
units = []
for p in sorted(glob.glob(os.path.join(src, 'f2_regimeA__*.json'))):
    c = json.load(open(p)); unit = os.path.basename(p)[len('f2_regimeA__'):-5]
    enc = (c.get('select') or {}).get('encoder') or []
    if c.get('anchor_r9') or unit.startswith('smoke') or not enc or not set(enc) <= set(ENC):
        continue
    units.append(unit)
    base = dict(c)
    base['stage'] = 'F3-reruns-boot'
    base['f2_regimeA_config'] = 'results/round10/final_runs/F2/configs/regimeA/' + os.path.basename(p)
    bs = dict(c['boot_select']); bs['encoder'] = ['uni_v2', 'pkg', 'hoptimus0', 'resnet50']; base['boot_select'] = bs
    if mode == 'whole':
        o = dict(base); o['unit'] = f'rerun_boot__{unit}'
        name = f'f3_rerun_boot__{unit}.json'
        json.dump(o, open(os.path.join(dst, name), 'w', newline='\n'), indent=1)
        rows.append(dict(config=name, unit=unit, estimands='all', genes=np.nan, boot_populations=np.nan))
        continue
    cv = pd.concat([pd.read_parquet(q, columns=['task', 'encoder', 'scale', 'estimand', 'gene']) for q in c['cluster_values']], ignore_index=True)
    for k, v in (c.get('select') or {}).items():
        cv = cv[cv[k].isin(v)]
    for gname, ests in GROUPS:
        x = cv[cv.estimand.isin(ests)]
        genes = sorted(x.gene.unique().tolist())
        if not genes:
            continue
        K = max(1, math.ceil(len(genes) / max_genes))
        for i, chunk in enumerate(np.array_split(np.array(genes, dtype=object), K)):
            o = dict(base); sel = dict(c.get('select') or {}); sel['estimand'] = ests
            if K > 1:
                sel['gene'] = [str(g) for g in chunk]
            o['select'] = sel
            suffix = f'__{gname}' + (f'__g{i}of{K}' if K > 1 else '')
            o['unit'] = f'rerun_boot__{unit}{suffix}'
            name = f'f3_rerun_boot__{unit}{suffix}.json'
            json.dump(o, open(os.path.join(dst, name), 'w', newline='\n'), indent=1)
            xs = x[x.gene.isin(set(chunk))]
            pops = xs[['task', 'encoder', 'scale', 'estimand', 'gene']].drop_duplicates()
            rows.append(dict(config=name, unit=unit, estimands='+'.join(ests), genes=len(chunk),
                             boot_populations=int(pops.estimand.isin(BOOT_EST).sum()), populations=len(pops)))
pd.DataFrame(rows).to_csv(os.path.join(dst, 'boot_configs_manifest.csv'), index=False)
print(len(units), 'units;', len(rows), 'configs written to', dst)
assert len(units) == 30, f'expected 30 units, found {len(units)}'
