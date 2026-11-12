"""Round 10, track final-runs, F3 regime B track: production configs and job scripts (plan 5d.3 (i), 5d.3 (ii),
5d.4 item 2, 5d.6 item 5).

Items and units (one Slurm job per unit; every unit writes to $BASE/F3/regimeB/<unit>/):
  regB_norm  open point 5: F2's driver (round10_final_runs_f2_regimeB.py, unchanged) on the refitted normalised-scale
             HEST files, scale 'norm_refit', cluster values v3_refit, theta3 and theta2, F2's m grid, R = 2000;
             12 units, one per (task, encoder). Configs in F3/configs/regimeB/f3_regB_norm__<unit>.json.
  e8         5d.4 item 2: this track's regime B driver (round10_final_runs_f3_regimeB.py) with all three forms, per-draw
             widths of C_fix1 and C_classical and 200 bootstrap replicates of the width ratio, on CCRCC, INDIANA_KIDNEY,
             LUNG_XENIUM (log1p, norm_refit), kidney Visium (log1p, lognorm) and ACS by state, m in
             {3, 5, 9, 10, 12, 15, 17, 20, 25, 30, 50, 100}; estimands theta3 and theta2 (ACS theta3 and mu); every
             population names F2's gene file of the same unit where F2 ran it, so rows at F2's m are checked.
  box        5d.3 (ii): round10_final_runs_f3_box.py run, the box rows for mu and the regime B coverage cells for mu
             (C_fix1) at m in {3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50, 75, 100, 150, 200, 300, 500}, every task
             (HEST four tasks on both scales, ACS, the six corpus tasks on both scales), three encoders.
  regcomp    5d.3 (i): round10_final_runs_f3_regcomp.py run, every task as in box, theta3, theta2 and mu (two
             populations of the same file, the second with round 5's theta2 kind 'mean'), R = 2000.
Splitting: --chunk <item>:<task>=<k> splits that task's m grid (e8, box) into k contiguous chunks (box rows only in
chunk 0); --split-regcomp population|budget|budget_regime sets regcomp's unit; --mem/--time <item>=<v> and
--mem-task/--time-task <item>:<task>=<v> set each job's #SBATCH values. Job scripts are templates with
COMMIT=__CODE_COMMIT__, substituted at submission.
usage: round10_final_runs_f3_regimeB_configs.py <out_root> [options]   (writes <out_root>/results/round10/...)
"""
import argparse, json, os

H = "/work/users/w/e/weiyang/hest_replication/results"
BASE = f"{H}/round10/final_runs"
CLN = "/work/users/w/e/weiyang/hest_code/round10-final-runs"
PYP = "/work/users/w/e/weiyang/hest_replication/env/miniforge3/envs/hest/bin/python"
FRAME = "2c7941c3-ecf2-4306-a6d1-ae6170b4cbe8"
ENC = ("uni_v2", "hoptimus0", "resnet50")
PQ = {"CCRCC": f"{H}/round3/B1_ppi/b1_predictions__CCRCC__{{e}}.parquet",
      "CCRCC_merged": f"{H}/round3/B1_ppi/b1_predictions__CCRCC_merged__{{e}}.parquet",
      "INDIANA_KIDNEY": f"{H}/round4/ppi/Q2_theory/predictions_INDIANA_KIDNEY/b1_predictions__INDIANA_KIDNEY__{{e}}.parquet",
      "LUNG_XENIUM": f"{H}/round4/ppi/Q2_theory/predictions/b1_predictions__LUNG_XENIUM__{{e}}.parquet"}
CORPUS = ("kidney__Visium", "breast__Spatial_Transcriptomics", "bowel__Visium", "brain__Visium", "breast__Xenium",
          "lung__Xenium")
F2_M = [3, 4, 6, 8, 10, 15, 20, 30]
E8_M = [3, 5, 9, 10, 12, 15, 17, 20, 25, 30, 50, 100]
BOX_M = [3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50, 75, 100, 150, 200, 300, 500]
CORE = ["round5_ppi_twolevel.py", "round5_ppi_e3_twolevel.py", "round5_ppi_e2_regimeB.py", "round5_ppi_estimator.py",
        "round4_ppi_estimator.py", "round4_ppi_q2_masking.py", "round4_ppi_q3_regimes.py", "round3_b1_ppi.py"]
F2_S = ["round10_final_runs_f2_regimeB.py", "round10_final_runs_estimators.py"] + CORE
RB_S = ["round10_final_runs_f3_regimeB.py"] + F2_S
RC_S = ["round10_final_runs_f3_regcomp.py"] + F2_S
BX_S = ["round10_final_runs_f3_box.py", "round9_fewcluster_box.py", "round9_fewcluster_strat_frontier.py"] + RB_S


def norm_pq(t, e):
    return f"{BASE}/F2/refit_norm/{t}__{e}/norm/b1_predictions__{t}__{e}.parquet"


def hest_pop(t, e, scale, ests=("theta3", "theta2"), kind=None, **kw):
    d = dict(task=t, vtag=t, encoder=e, arm=e, scale=scale, source="r5",
             parquet=PQ[t].format(e=e) if scale == "log1p" else norm_pq(t, e), estimands=list(ests),
             cluster_values=(f"{BASE}/F2/cluster_values_v1/cluster_values__{t}.parquet" if scale == "log1p"
                             else f"{BASE}/F2/cluster_values_v3_refit/cluster_values__{t}.parquet"))
    if kind:
        d["theta2_kind"] = kind
    d.update(kw)
    return d


def acs_pop(ests=("theta3", "theta2"), **kw):
    d = dict(task="ACS_STATES", vtag="ACS_STATES", encoder="pkg", arm="package", scale="log_income", source="r5",
             theta2_kind="mean", parquet=f"{H}/round4/ppi/Q2_theory/predictions/ACS_STATES.parquet", estimands=list(ests),
             cluster_values=f"{BASE}/F2/cluster_values_v1b_acs/cluster_values__ACS_STATES.parquet")
    d.update(kw)
    return d


def corpus_pop(task, e, scale, ests=("theta3", "theta2"), kind=None, **kw):
    pre = {"log1p": ("y_log1p__", "f_log1p__"), "lognorm": ("y_lognorm__", "f_lognorm__")}[scale]
    d = dict(task=task, vtag=task, encoder=e, arm=e, scale=scale, source="corpus",
             path=f"{BASE}/F1/predict/{task}__{e}/pred__{task}__{e}__donor.parquet",
             morph_path=f"{BASE}/F2/morphology/{task}/morphology__{task}.parquet", y_prefix=pre[0], f_prefix=pre[1],
             donor_col="donor_id", estimands=list(ests),
             cluster_values=f"{BASE}/F2/cluster_values_v2_corpus/cluster_values__{task}.parquet")
    if kind:
        d["theta2_kind"] = kind
    d.update(kw)
    return d


def f2_genes(task, e):
    return f"{BASE}/F2/regimeB/{task}__{e}/regimeB_genes.parquet"


def all_pops(mu_only=False):
    """(task, encoder, scale, base population builder) for every task of 5d.3."""
    out = []
    for t in PQ:
        for e in ENC:
            for sc in ("log1p", "norm_refit"):
                out.append((t, e, sc, lambda ests, kind=None, t=t, e=e, sc=sc, **kw: hest_pop(t, e, sc, ests, kind, **kw)))
    out.append(("ACS_STATES", "pkg", "log_income", lambda ests, kind=None, **kw: acs_pop(ests, **kw)))
    for t in CORPUS:
        for e in ENC:
            for sc in ("log1p", "lognorm"):
                out.append((t, e, sc, lambda ests, kind=None, t=t, e=e, sc=sc, **kw: corpus_pop(t, e, sc, ests, kind, **kw)))
    return out


def chunks(grid, k):
    k = max(1, int(k)); n = len(grid)
    b = [round(i * n / k) for i in range(k + 1)]
    return [grid[b[i]:b[i + 1]] for i in range(k) if b[i + 1] > b[i]]


def job_script(unit, note, cfgpaths, steps, scripts, mem="16G", tmin=60, cpus=2, extra_inputs=()):
    L = ["#SBATCH --partition=general", "#SBATCH --account=rc_htzhu_pi", f"#SBATCH --cpus-per-task={cpus}",
         f"#SBATCH --mem={mem}", f"#SBATCH --time={tmin}", "set -u", f"UNIT={unit}", f"CLONE={CLN}", f"BASE={BASE}",
         "COMMIT=__CODE_COMMIT__", "SNAP=$BASE/_snapshots/$COMMIT", f"PY={PYP}", f"FRAME={FRAME}", "HJ=$PWD",
         "OUT=$BASE/F3/regimeB/$UNIT", "START=$(date -Iseconds)",
         'case "$COMMIT" in __*) echo "COMMIT placeholder not substituted"; exit 4;; esac',
         'mkdir -p "$BASE/_snapshots"', 'exec 9>"$BASE/_snapshots/.lock"; flock 9', 'if [ ! -d "$SNAP" ]; then',
         '  mkdir -p "$SNAP.tmp" && git -C "$CLONE" archive "$COMMIT" code | tar -x -C "$SNAP.tmp"',
         "  (cd \"$SNAP.tmp\" && find code -type f -name '*.py' | sort | xargs md5sum > MD5SUMS)",
         '  chmod -R a-w "$SNAP.tmp" && mv "$SNAP.tmp" "$SNAP"', 'fi', 'flock -u 9',
         'if [ -e "$OUT" ]; then echo "OUT exists: $OUT, refusing"; exit 3; fi', 'mkdir -p "$OUT"',
         'cat > "$OUT/_provenance.json" <<PROVEOF', '{', '  "writer": "claude-science",', '  "project_id": "proj_8450e231133d",',
         '  "frame_id": "$FRAME",', '  "track": "final-runs",',
         '  "plan": "docs/round10/tracks/final-runs/round10_final_runs_plan.md",', f'  "note": "{note}",',
         '  "host": "$(hostname)",', '  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"', '}', 'PROVEOF']
    cfgn = []
    for cp in cfgpaths:
        n = os.path.basename(cp); cfgn.append(n)
        L.append(f'git -C "$CLONE" show $COMMIT:{cp} > "$OUT/{n}"')
    L += ['cd "$OUT"',
          'export PYTHONHASHSEED=0 PYTHONPATH=$SNAP/code/scripts OMP_NUM_THREADS=%d OPENBLAS_NUM_THREADS=%d MKL_NUM_THREADS=%d'
          % (cpus, cpus, cpus), 'set +e', 'RC=0', 'CMDS=""']
    for i, cmd in enumerate(steps):
        log = f"stdout{'' if i == 0 else i + 1}.log"
        L += [f'CMD{i}="{cmd}"', f'CMDS="$CMDS${{CMDS:+ ; }}$CMD{i}"', f'$PY -u $SNAP/code/scripts/$CMD{i} > {log} 2>&1',
              'R_=$?; [ $R_ -ne 0 ] && RC=$R_', f'echo "step {i} rc $R_" >> stdout.log']
    L += ['set -e', 'ST=COMPLETED; [ $RC -eq 0 ] || ST=FAILED_rc$RC',
          "INPUTS=$($PY -c \"import json,os,sys\nout=sys.argv[1]; s=set()\ndef w(x):\n    if isinstance(x,dict): [w(v) for v in x.values()]\n"
          "    elif isinstance(x,list): [w(v) for v in x]\n    elif isinstance(x,str) and x.startswith('/work/') and not x.startswith(out) "
          "and os.path.isfile(x): s.add(x)\nfor p in sys.argv[2:]: w(json.load(open(p)))\nprint(' '.join(sorted(s)))\" \"$OUT\" "
          + " ".join(f'"$OUT/{n}"' for n in cfgn) + ")",
          "$PY $SNAP/code/scripts/round10_final_runs_provenance.py \"$OUT\" F3 $UNIT $COMMIT $SNAP \"$START\" $ST --frame $FRAME "
          "--command \"$CMDS\" --config '{\"stage\":\"F3\",\"unit\":\"'$UNIT'\",\"commit\":\"'$COMMIT'\"}' --scripts "
          + " ".join("code/scripts/" + s for s in sorted(set(scripts))) + " --inputs "
          + " ".join(f'"$OUT/{n}"' for n in cfgn) + " $INPUTS" + "".join(" " + x for x in extra_inputs),
          'cd "$OUT"; for g in $(find . -maxdepth 2 -type f \\( -name "*.json" -o -name "*.csv" -o -name "*.txt" -o -name "*.log" \\) '
          '-size -20M); do [ -e "$g" ] && cp "$g" "$HJ/$(echo ${g#./} | tr / _)"; done; true',
          'tail -40 stdout.log; for f in stdout*.log; do [ -e "$f" ] && tail -15 "$f"; done; true', 'exit $RC']
    return "\n".join(L) + "\n"


def kv(items):
    d = {}
    for s in items or []:
        k, v = s.split("=", 1); d[k] = v
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out_root")
    ap.add_argument("--items", default="regB_norm,e8,box,regcomp")
    ap.add_argument("--chunk", action="append", default=[])
    ap.add_argument("--split-regcomp", default="budget", choices=("population", "budget", "budget_regime"))
    ap.add_argument("--mem", action="append", default=[]); ap.add_argument("--time", action="append", default=[])
    ap.add_argument("--mem-task", action="append", default=[]); ap.add_argument("--time-task", action="append", default=[])
    ap.add_argument("--cpus", type=int, default=2)
    a = ap.parse_args()
    items = a.items.split(","); CH = kv(a.chunk); MEM = kv(a.mem); TIM = kv(a.time); MT = kv(a.mem_task); TT = kv(a.time_task)
    rel_cfg = "results/round10/final_runs/F3/configs"; rel_js = "results/round10/final_runs/job_scripts"
    for sub in ("regimeB", "regcomp", "box"):
        os.makedirs(os.path.join(a.out_root, rel_cfg, sub), exist_ok=True)
    os.makedirs(os.path.join(a.out_root, rel_js), exist_ok=True)
    index = []

    def res(item, task):
        return (MT.get(f"{item}:{task}", MEM.get(item, "16G")), int(TT.get(f"{item}:{task}", TIM.get(item, 60))))

    def emit(item, prefix, sub, unit, cfg, steps_fn, scripts, note, task):
        cp = f"{rel_cfg}/{sub}/f3_{prefix}__{unit}.json"
        open(os.path.join(a.out_root, cp), "w", newline="\n").write(json.dumps(cfg, indent=1) + "\n")
        mem, tmin = res(item, task)
        js = f"job_f3_{prefix}_{unit}.sh"
        full = f"{prefix}__{unit}"
        txt = job_script(full, note, [cp], steps_fn(os.path.basename(cp)), scripts, mem=mem, tmin=tmin, cpus=a.cpus)
        open(os.path.join(a.out_root, rel_js, js), "w", newline="\n").write(txt)
        index.append(dict(item=item, unit=full, task=task, config=cp, job_script=f"{rel_js}/{js}", mem=mem, time_min=tmin,
                          cells=cfg.get("_cells")))

    if "regB_norm" in items:
        for t in PQ:
            for e in ENC:
                u = f"{t}__{e}"
                cfg = dict(stage="F3", unit=f"regB_norm__{u}", R=2000, m_grid=F2_M, populations=[hest_pop(t, e, "norm_refit")])
                cfg["_cells"] = 2 * len(F2_M) - 1
                emit("regB_norm", "regB_norm", "regimeB", u, cfg,
                     lambda n: [f"round10_final_runs_f2_regimeB.py $OUT/{n} $OUT"], F2_S,
                     f"F3 open point 5, regime B on norm_refit, {u}", t)
    if "e8" in items:
        specs = []
        for t in ("CCRCC", "INDIANA_KIDNEY", "LUNG_XENIUM"):
            for e in ENC:
                specs.append((t, e, "log1p", hest_pop(t, e, "log1p", f2_genes=f2_genes(t, e))))
                specs.append((t, e, "norm_refit", hest_pop(t, e, "norm_refit")))
        for e in ENC:
            for sc in ("log1p", "lognorm"):
                specs.append(("kidney__Visium", e, sc, corpus_pop("kidney__Visium", e, sc, f2_genes=f2_genes("kidney__Visium", e))))
        specs.append(("ACS_STATES", "pkg", "log_income", acs_pop(f2_genes=f2_genes("ACS_STATES", "pkg"))))
        for t, e, sc, pop in specs:
            for ci, mg in enumerate(chunks(E8_M, CH.get(f"e8:{t}", 1))):
                u = f"{t}__{e}__{sc}" + (f"__c{ci}" if CH.get(f"e8:{t}", "1") != "1" else "")
                cfg = dict(stage="F3", unit=f"regB_e8__{u}", R=2000, forms=["C_fix1", "C_ppi", "C_classical"],
                           widths_forms=["C_fix1", "C_classical"], wr_boot=200, m_grid=mg,
                           f2_summary=f"{CLN}/results/round10/final_runs/F2/aggregate_regimeB/f2_regimeB_summary.csv",
                           populations=[pop], _cells=2 * len(mg))
                emit("e8", "regB_e8", "regimeB", u, cfg, lambda n: [f"round10_final_runs_f3_regimeB.py run $OUT/{n} $OUT"], RB_S,
                     f"F3 5d.4 item 2, E8 regime B side, {u}", t)
    if "box" in items:
        for t, e, sc, mk in all_pops():
            for ci, mg in enumerate(chunks(BOX_M, CH.get(f"box:{t}", 1))):
                u = f"{t}__{e}__{sc}" + (f"__c{ci}" if CH.get(f"box:{t}", "1") != "1" else "")
                cfg = dict(stage="F3", unit=f"box__{u}", R=2000, forms=["C_fix1"], m_grid=mg, box=(ci == 0),
                           populations=[mk(("theta2",), kind="mean")], _cells=len(mg))
                emit("box", "box", "box", u, cfg, lambda n: [f"round10_final_runs_f3_box.py run $OUT/{n} $OUT"], BX_S,
                     f"F3 5d.3 (ii), box rows and mu coverage, {u}", t)
    if "regcomp" in items:
        for t, e, sc, mk in all_pops():
            ests = ("theta3", "mu") if t == "ACS_STATES" else ("theta3", "theta2", "mu")
            pops = []
            if t == "ACS_STATES":
                pops = [mk(("theta3", "theta2"))]
            else:
                pops = [mk(("theta3", "theta2")), mk(("theta2",), kind="mean")]
            if a.split_regcomp == "population":
                parts = [("all", {})]
            elif a.split_regcomp == "budget":
                parts = [(f"B{b}", dict(budgets=[b])) for b in (2400, 4800, 9600)]
            else:
                parts = [(f"B{b}_{r}", dict(budgets=[b], regimes=[r])) for b in (2400, 4800, 9600) for r in ("A", "B")]
            for pn, flt in parts:
                u = f"{t}__{e}__{sc}__{pn}"
                cfg = dict(stage="F3", unit=f"regcomp__{u}", R=2000, populations=pops, estimands_reported=list(ests), **flt)
                emit("regcomp", "regcomp", "regcomp", u, cfg, lambda n: [f"round10_final_runs_f3_regcomp.py run $OUT/{n} $OUT"],
                     RC_S, f"F3 5d.3 (i), regime A against regime B cost-matched, {u}", t)
    ip = os.path.join(a.out_root, rel_cfg, "regimeB", "f3_production_index.json")
    json.dump(dict(items=items, args=vars(a), units=index), open(ip, "w", newline="\n"), indent=1)
    print(len(index), "units;", {it: sum(1 for x in index if x["item"] == it) for it in items})


if __name__ == "__main__":
    main()
