"""Count D2 draws with no accepted candidate (d2_select's third return, discarded by the sim). Snapshot 81ec444 modules, same pools and populations."""
import sys, itertools, json, numpy as np
sys.path.insert(0, "/tmp/r5ppi_snapshots/81ec444ab5b8d205dc3ca73b76c51783848c599b/code/scripts")
import round5_ppi_e4_sim as S, round5_ppi_balance as BAL
from round5_ppi_e1_sim import populations, R2_GRID, LAMSTAR
G = int(sys.argv[1]); out = []
for nL in S.NL:
    masks = S.pool(G, nL, 1000, 1000)
    flat = masks.reshape(-1, G).astype(float)
    for R2, ls, law in itertools.product(R2_GRID, LAMSTAR, S.LAWS):
        z, f = populations(G, R2, ls, 0.0, law); fc = f - f.mean(0)
        dist = ((flat @ fc) / nL) ** 2 / f.var(0, ddof=1)[None, :]
        for pa in (0.1, 0.01):
            _, thr, nm = BAL.d2_select(dist, 1000, 1000, pa)
            out.append(dict(G=G, n_L=nL, R2=R2, lambda_star=ls, law=law, p_a=pa, n_missing=nm))
json.dump(out, open(f"{sys.argv[2]}/d2_misses_G{G}.json", "w"))
