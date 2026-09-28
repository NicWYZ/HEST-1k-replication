
import h5py, json, csv, hashlib, sys, os
EXT = "/work/users/w/e/weiyang/hest_replication/hest_ext/lung_xenium"
sel = [r for r in csv.DictReader(open("/work/users/w/e/weiyang/hest_replication/results/round4/data/P1_selection/selection.csv")) if r["set"] == "L"]
assert len(sel) == 24
def names(g):
    if "_index" in g.attrs:
        k = g.attrs["_index"]; k = k.decode() if isinstance(k, bytes) else k
        a = g[k][:]
    else:
        a = g["_index"][:]
    return [x.decode() if isinstance(x, (bytes,)) else str(x) for x in a]
rows, sets = [], {}
for r in sel:
    sid = r["sample_id"]; p = f"{EXT}/st/{sid}.h5ad"
    with h5py.File(p, "r") as f:
        g = names(f["var"]); n_obs = len(names(f["obs"]))
    sets[sid] = g
    rows.append(dict(sample_id=sid, n_genes=len(g), n_expr_spots=n_obs,
                     genes_sha1=hashlib.sha1("\n".join(sorted(g)).encode()).hexdigest()[:12]))
inter = sorted(set.intersection(*[set(v) for v in sets.values()]))
os.makedirs("out", exist_ok=True)
with open("out/lung_panels.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
json.dump({s: sorted(v) for s, v in sets.items()}, open("out/lung_genes_by_sample.json", "w"))
json.dump(dict(n_intersection=len(inter), genes=inter), open("out/lung_intersection_panel.json", "w"))
print("n_intersection", len(inter), "panel sizes", sorted({r["n_genes"] for r in rows}))
