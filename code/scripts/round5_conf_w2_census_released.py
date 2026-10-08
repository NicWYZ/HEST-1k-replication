#!/usr/bin/env python
"""Round 5 W2 part 2, item 3: the released census experiment, with the round-4 commands.

The released tree is copied under the job's output directory (the released code writes under its own
REPO_ROOT, and the original is read-only for this track). The copy is checked file by file against the
original by md5 before anything runs, so it is the released code unmodified. The census input built in
item 1 is placed at real_data/acs/data/acs_data_all50states.csv in the copy, where both released
scripts look for it. Commands are those of round 4's suite_main.log and suite_stdcp.log
(results/round4/conformal/C3_real/frag_ACS_o/ghcp_repro/), with --n_workers 4 and one alpha per job:
  1. code/marginal/run_section_3_2.py --alphas A --B 1000 --n_workers 4 --skip_stdcp
  2. code/marginal/recompute_acs_stdcp_randomized_min21.py --B 1000 --n_workers 4 --alphas A --skip_plot
"""
import hashlib, os, shutil, subprocess, sys, json
import round5_conf_io as IO

GHCP = "/work/users/w/e/weiyang/hest_code/ghcp_code"
INPUT_CSV = "/work/users/w/e/weiyang/hest_replication/results/round5/conformal/W2_ghcp_settings/part2/input/data/acs_data_all50states.csv"
alpha, out = sys.argv[1], sys.argv[2]
nw = sys.argv[3] if len(sys.argv) > 3 else "4"
KEEP = ["code", "methods", "real_data", "scores.py", "requirements.txt"]


def md5f(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def tree_md5(root):
    d = {}
    for k in KEEP:
        p = os.path.join(root, k)
        if os.path.isfile(p):
            d[k] = md5f(p)
        else:
            for dp, dn, fn in os.walk(p):
                dn[:] = [x for x in dn if x != "__pycache__"]
                for f in fn:
                    q = os.path.join(dp, f)
                    d[os.path.relpath(q, root)] = md5f(q)
    return d


os.makedirs(out, exist_ok=True)
IO.stamp(out, "round5-conformal W2 part2", f"released census experiment alpha={alpha}, round-4 commands")
tree = os.path.join(out, "ghcp_tree")
if not os.path.exists(tree):
    os.makedirs(tree)
    for k in KEEP:
        s, d = os.path.join(GHCP, k), os.path.join(tree, k)
        (shutil.copy2 if os.path.isfile(s) else lambda a, b: shutil.copytree(a, b, ignore=shutil.ignore_patterns("__pycache__")))(s, d)
a, b = tree_md5(GHCP), tree_md5(tree)
assert a == b, "copied released tree differs from the original"
os.makedirs(os.path.join(tree, "real_data", "acs", "data"), exist_ok=True)
shutil.copy2(INPUT_CSV, os.path.join(tree, "real_data", "acs", "data", "acs_data_all50states.csv"))
env = dict(os.environ, HCP_PLOTS_MARGINAL=os.path.join(out, "paper-results"), PYTHONHASHSEED="0",
           OMP_NUM_THREADS="1", MKL_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1")
env.pop("PYTHONPATH", None)
cmds = [
    [sys.executable, "-u", f"{tree}/code/marginal/run_section_3_2.py", "--alphas", alpha, "--B", "1000", "--n_workers", nw, "--skip_stdcp"],
    [sys.executable, "-u", f"{tree}/code/marginal/recompute_acs_stdcp_randomized_min21.py", "--B", "1000", "--n_workers", nw, "--alphas", alpha, "--skip_plot"],
]
for i, cmd in enumerate(cmds, 1):
    print("RUN", " ".join(cmd), flush=True)
    with open(os.path.join(out, f"cmd{i}.log"), "w") as f:
        r = subprocess.run(cmd, cwd=tree, env=env, stdout=f, stderr=subprocess.STDOUT)
    print("exit", r.returncode, flush=True)
    assert r.returncode == 0, f"command {i} failed"
extra = {"released_commit": "d1a69f4a (per round-4 record)", "tree_files_checked": len(a),
         "input_csv_md5": md5f(INPUT_CSV), "commands": " || ".join(" ".join(c) for c in cmds),
         "released_tree_md5s": json.dumps({k: v for k, v in a.items() if k.startswith("code/marginal/run_") or k.startswith("code/marginal/recompute_acs_stdcp_randomized") or k.startswith("real_data/acs/data_processing") or k == "scores.py"})}
IO.write_provenance(out, "W2p2_census_released", os.path.abspath(__file__), {"alpha": alpha, "n_workers": nw}, extra=extra)
