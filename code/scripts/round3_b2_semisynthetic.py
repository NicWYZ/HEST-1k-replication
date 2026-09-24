#!/usr/bin/env python
"""Round 3, stage B2: semi-synthetic coverage of the B1 intervals.

Stage: B2 (round3_execution_plan.md sections 4.8 and 12.5, as amended by section 13.6).
The end-of-round report is the gate; B2 itself has none.

WHY (section 4.8). B1 is one partition. Validity is a statement about repeated sampling,
so this stage repeats the labelled/unlabelled partition many times with the full-data
value held as truth. That is round 2 R5c's masking design applied to donors, and it is
what turns B1 from an estimate into a claim.

WHAT IS AND IS NOT RESAMPLED. The spots, the predictions, the morphology covariates and
therefore the full-data value theta_full are FIXED throughout; the only thing redrawn is
WHICH donors are labelled. So the coverage reported here is coverage over the labelling
mechanism with the population held fixed, which is the design-based reading of the
problem, and the estimand is the full-data value of this particular 24-donor (or
23-donor, or 4-donor, or 2-donor) population rather than a superpopulation parameter.

THIS SCRIPT EDITS NEITHER THE HARNESS NOR B1. It imports `round3_b1_ppi.py` from the same
directory as a module (which in turn imports `round3_a0_harness.py` unmodified) and calls
B1's own `cell_spot` and `cell_donor`, so a B2 coverage number cannot drift from a B1
estimate by an implementation difference: the two share one estimator, one lambda rule and
one set of three variances.

SETTINGS. --n-draws (200) labelled-donor sets per (task variant, n_L), drawn under crc32
seeds `f"{variant}|{n_L}|draw{b}"`, which makes the same draw reproducible from the seed
alone and identical across arms and estimands, so an arm comparison is paired on the
partition. Task variants and their n_L come from B1's NL_SETTINGS, which is CCRCC at 6, 8
and 12 donors with 24 donors and again with INT4 and INT24 merged, LYMPH_IDC at 2, PRAD
at 1 and 2, and IDC at 2. Arms are the three encoders plus `permuted`. Estimands and
populations are B1's.

THE PRAD SLIDE-MASKING VARIANT (section 4.8). PRAD has two donors over 23 slides. Masking
whole SLIDES inside the two donors keeps both donors in the labelled set, so G = 2 for
every draw and the donor-clustered interval has one degree of freedom whatever the number
of labelled slides. The labelled and unlabelled donor sets are then NOT disjoint, so the
separate-U-and-L cluster variance of section 4.7 does not apply and the combined form is
used instead (`cluster_variance_form = combined`, the literal string written into both
output CSVs; every other setting records `separate`); the donor-weighted population
is undefined under slide masking and is recorded as such rather than computed.

OUTPUTS under results/round3/B2_semisynthetic/:
  b2_coverage.csv     per (setting, arm, estimand, population, gene, estimator, variance):
                      empirical coverage of theta_full at nominal 1-alpha, mean and median
                      width, the share of draws with a non-finite interval, and the draw
                      count
  b2_width_ratio.csv  per (setting, arm, estimand, population, gene): the mean
                      PPI-to-classical width ratio under each variance, beside the arm's
                      pooled Pearson on the task (from b1_pred_quality) and n_L
  fig_b2_coverage.png
  PROVENANCE__b2.txt

Usage:
  round3_b2_semisynthetic.py [--n-draws 200] [--estimate] [--figures]
"""
import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time
import zlib

import numpy as np
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(_HERE, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


B1 = _load("round3_b1_ppi")
H = B1.H
ROOT = B1.ROOT

B1DIR = "results/round3/B1_ppi"
# PRAD slide-masking: numbers of labelled SLIDES, out of 23, all within the two donors.
PRAD_SLIDE_NL = (4, 8, 12)


def parse_args(argv):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--estimate", action="store_true")
    p.add_argument("--figures", action="store_true")
    p.add_argument("--out-dir", default="results/round3/B2_semisynthetic")
    p.add_argument("--b1-dir", default=B1DIR)
    p.add_argument("--n-draws", type=int, default=200)
    p.add_argument("--n-boot", type=int, default=B1.N_BOOT)
    p.add_argument("--alpha", type=float, default=B1.ALPHA)
    a = p.parse_args(argv)
    if not a.figures:
        a.estimate = True
    return a


def quality_table(b1dir):
    """Arm-by-gene and arm-by-task Pearson of the predictions B1 actually used."""
    import glob
    fs = sorted(glob.glob(f"{ROOT}/{b1dir}/b1_pred_quality__*.csv"))
    assert fs, f"no b1_pred_quality__*.csv under {b1dir}"
    d = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True)
    d = d[d["design"] == "donor"]
    per_gene = (d.groupby(["variant", "encoder", "gene"])["pearson_pooled"]
                 .mean().rename("pearson_gene").reset_index())
    per_task = (d.groupby(["variant", "encoder"])["pearson_pooled"]
                 .mean().rename("pearson_task").reset_index())
    return per_gene, per_task


def draw_sets(d, variant, n_L, n_draws, unit="donor"):
    """The n_draws labelled sets. `unit` is the donor for every setting except PRAD's
    slide-masking variant, where whole slides inside the two donors are masked."""
    out = []
    if unit == "donor":
        pool = list(map(str, d["donors"]))
    else:
        pool = list(map(str, d["slides"]))
    for b in range(n_draws):
        rng = np.random.default_rng(zlib.crc32(f"{variant}|{n_L}|draw{b}".encode()))
        out.append(sorted(rng.permutation(np.array(pool, dtype=object))[:n_L].tolist()))
    return out


def run(args):
    t0 = time.time()
    out = f"{ROOT}/{args.out_dir}"
    os.makedirs(out, exist_ok=True)
    b1 = f"{ROOT}/{args.b1_dir}"
    per_gene, per_task = quality_table(args.b1_dir)

    settings = []
    for v in B1.NL_SETTINGS:
        if not os.path.exists(f"{b1}/b1_suffstats__{v}__{B1.PERMUTE_SOURCE}.npz"):
            continue
        for n_L in B1.NL_SETTINGS[v]:
            settings.append(dict(setting=v, variant=v, n_L=n_L, unit="donor",
                                 cluster_form="separate", pops=("spot", "donor")))
    if os.path.exists(f"{b1}/b1_suffstats__PRAD__{B1.PERMUTE_SOURCE}.npz"):
        for n_L in PRAD_SLIDE_NL:
            settings.append(dict(setting="PRAD_slidemask", variant="PRAD", n_L=n_L,
                                 unit="slide", cluster_form="combined",
                                 pops=("spot",)))
    print(f"[b2] {len(settings)} settings: "
          f"{json.dumps([(s['setting'], s['n_L']) for s in settings])}", flush=True)

    arms = list(B1.ENCODERS) + ["permuted"]
    cov_rows, wr_rows = [], []
    for st in settings:
        for est in ("theta3", "theta2", "theta1"):
            for arm in arms:
              for pop in st["pops"]:
                d = B1.load_suff(b1, st["variant"], arm, est, pop)
                if d is None or not d["valid"].any():
                    continue
                sets = draw_sets(d, st["setting"], st["n_L"], args.n_draws, st["unit"])
                dnames = np.array(list(map(str, d["donors"])), dtype=object)[
                    d["donor_idx"]]
                snames = np.array(list(map(str, d["slides"])), dtype=object)
                acc = {}
                for b, S in enumerate(sets):
                    inL = (np.isin(dnames, S) if st["unit"] == "donor"
                           else np.isin(snames, S))
                    Lg = inL & d["valid"]
                    Ug = (~inL) & d["valid"]
                    if not Lg.any():
                        continue
                    if not Ug.any():
                        # Every donor labelled: the classical estimator IS the full-data
                        # value, so coverage is 1 by construction and carries no
                        # information about the interval. Flagged, not reported as a
                        # coverage result. This is B1's U-empty acceptance setting.
                        acc.setdefault((pop, "status"), []).append(
                            "U_empty_L_equals_population_coverage_degenerate")
                        continue
                    r = B1.CELL[pop](d["S1"], d["S2"], d["n_per"], d["donor_idx"],
                                     Lg, Ug, est, args.alpha, args.n_boot,
                                     f"{st['setting']}|{arm}|{est}|{pop}|"
                                     f"{st['n_L']}|draw{b}",
                                     cluster_form=st["cluster_form"])
                    if r.get("status", "ok") != "ok":
                        acc.setdefault((pop, "status"), []).append(r["status"])
                        continue
                    iv = B1.intervals(r, args.alpha)
                    for nm in ("classical", "pp"):
                        for vr in ("iid", "cluster", "boot"):
                            lo = iv[f"{nm}|{vr}|lo"]
                            hi = iv[f"{nm}|{vr}|hi"]
                            fin = np.isfinite(lo) & np.isfinite(hi)
                            acc.setdefault((pop, nm, vr, "cov"), []).append(
                                np.where(fin, (lo <= r["theta_full"])
                                         & (r["theta_full"] <= hi), np.nan))
                            acc.setdefault((pop, nm, vr, "w"), []).append(
                                np.where(fin, hi - lo, np.nan))
                            acc.setdefault((pop, nm, vr, "fin"), []).append(fin)
                    acc.setdefault((pop, "lam"), []).append(r["lambda"])
                    acc.setdefault((pop, "GL"), []).append(r["G_L"])
                    acc.setdefault((pop, "GU"), []).append(r["G_U"])
                    acc.setdefault((pop, "df"), []).append(r["df_cluster"])
                    acc.setdefault((pop, "full"), []).append(r["theta_full"])
                genes = d["genes"]
                if True:
                    if (pop, "classical", "iid", "cov") not in acc:
                        if (pop, "status") in acc:
                            cov_rows.append(dict(
                                setting=st["setting"], variant=st["variant"],
                                n_L=st["n_L"], label_unit=st["unit"], arm=arm,
                                estimand=est, population=pop, gene="ALL",
                                status=acc[(pop, "status")][0], n_draws=0))
                        continue
                    nd = len(acc[(pop, "classical", "iid", "cov")])
                    lam = np.asarray(acc[(pop, "lam")])
                    full = np.asarray(acc[(pop, "full")])[0]
                    for j, g in enumerate(genes):
                        wrow = dict(setting=st["setting"], variant=st["variant"],
                                    n_L=st["n_L"], label_unit=st["unit"], arm=arm,
                                    estimand=est, population=pop, gene=g,
                                    n_draws=nd, theta_full=float(full[j]),
                                    lambda_mean=float(np.nanmean(lam[:, j])),
                                    G_L=int(np.median(acc[(pop, "GL")])),
                                    G_U=int(np.median(acc[(pop, "GU")])),
                                    df_cluster=int(np.median(acc[(pop, "df")])),
                                    cluster_variance_form=st["cluster_form"],
                                    status="ok")
                        for nm in ("classical", "pp"):
                            for vr in ("iid", "cluster", "boot"):
                                cv = np.asarray(acc[(pop, nm, vr, "cov")])[:, j]
                                wd = np.asarray(acc[(pop, nm, vr, "w")])[:, j]
                                fn = np.asarray(acc[(pop, nm, vr, "fin")])[:, j]
                                cov_rows.append(dict(
                                    setting=st["setting"], variant=st["variant"],
                                    n_L=st["n_L"], label_unit=st["unit"], arm=arm,
                                    estimand=est, population=pop, gene=g,
                                    estimator=nm, variance=vr, n_draws=nd,
                                    n_finite=int(fn.sum()),
                                    frac_nonfinite=float(1.0 - fn.mean()),
                                    coverage=float(np.nanmean(cv)),
                                    width_mean=float(np.nanmean(wd)),
                                    width_median=float(np.nanmedian(wd)),
                                    nominal=1.0 - args.alpha,
                                    theta_full=float(full[j]),
                                    cluster_variance_form=st["cluster_form"],
                                    df_cluster=int(np.median(acc[(pop, "df")])),
                                    status="ok"))
                                if nm == "pp":
                                    wc = np.asarray(
                                        acc[(pop, "classical", vr, "w")])[:, j]
                                    rat = np.where(wc > 0, wd / wc, np.nan)
                                    wrow[f"width_ratio_{vr}"] = float(np.nanmean(rat))
                                    wrow[f"width_ratio_{vr}_median"] = float(
                                        np.nanmedian(rat))
                                    wrow[f"width_mean_pp_{vr}"] = float(np.nanmean(wd))
                                    wrow[f"width_mean_cl_{vr}"] = float(np.nanmean(wc))
                        wr_rows.append(wrow)
                print(f"[b2] {st['setting']} n_L={st['n_L']} {est} {arm} {pop}: "
                      f"{len(cov_rows)} coverage rows {time.time()-t0:.0f}s", flush=True)

    cov = pd.DataFrame(cov_rows)
    wr = pd.DataFrame(wr_rows)
    wr = wr.merge(per_gene.rename(columns={"encoder": "arm"}),
                  on=["variant", "arm", "gene"], how="left")
    wr = wr.merge(per_task.rename(columns={"encoder": "arm"}),
                  on=["variant", "arm"], how="left")
    cov.to_csv(f"{out}/b2_coverage.csv", index=False)
    print(f"[write] b2_coverage.csv ({len(cov)} rows)", flush=True)
    wr.to_csv(f"{out}/b2_width_ratio.csv", index=False)
    print(f"[write] b2_width_ratio.csv ({len(wr)} rows)", flush=True)

    cfg = dict(stage="round3_B2", script="code/scripts/round3_b2_semisynthetic.py",
               settings=[{k: (list(v) if isinstance(v, tuple) else v)
                          for k, v in s.items()} for s in settings],
               arms=arms, n_draws=args.n_draws, n_boot=args.n_boot, alpha=args.alpha,
               prad_slide_nl=list(PRAD_SLIDE_NL),
               estimator="imported from round3_b1_ppi.cell_spot / cell_donor",
               seed_source="zlib.crc32")
    blob = json.dumps(cfg, sort_keys=True)
    chash = hashlib.sha256(blob.encode()).hexdigest()[:16]
    provenance(out, cfg, blob, chash, time.time() - t0,
               ["b2_coverage.csv", "b2_width_ratio.csv"])
    print(f"\n[done] b2 {time.time()-t0:.0f}s", flush=True)
    return 0


def provenance(out, cfg, blob, chash, wall, files):
    commit = subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"],
                            capture_output=True, text=True).stdout.strip()
    paths = [os.path.abspath(__file__), os.path.join(_HERE, "round3_b1_ppi.py"),
             os.path.join(_HERE, "round3_a0_harness.py")]
    md5 = {}
    for p in paths:
        with open(p, "rb") as f:
            md5[os.path.basename(p)] = hashlib.md5(f.read()).hexdigest()
    with open(f"{out}/PROVENANCE__b2.txt", "w") as f:
        f.write(f"{'='*78}\n"
                f"Round 3, stage B2 - semi-synthetic coverage\n"
                f"slurm_job_id    : {os.environ.get('SLURM_JOB_ID','NA')}\n"
                f"slurm_partition : {os.environ.get('SLURM_JOB_PARTITION','NA')}\n"
                f"node            : {os.environ.get('SLURMD_NODENAME','NA')}\n"
                f"gpu             : {os.environ.get('CUDA_VISIBLE_DEVICES','none')}\n"
                f"date            : {time.strftime('%Y-%m-%dT%H:%M:%S%z')}\n"
                f"repo_commit     : {commit}\n"
                f"script          : code/scripts/round3_b2_semisynthetic.py\n"
                f"script_md5      : {json.dumps(md5, sort_keys=True)}\n"
                f"command_line    : {' '.join(sys.argv)}\n"
                f"pythonhashseed  : {os.environ.get('PYTHONHASHSEED','unset')}\n"
                f"wall_seconds    : {wall:.0f}\n"
                f"files_written   : {', '.join(files)}\n"
                f"config_hash     : sha256/16 {chash}\n"
                f"config          : {blob}\n"
                f"plan            : round3_execution_plan.md sections 4.8, 12.5, 13.6\n")
    print(f"[write] PROVENANCE__b2.txt (config_hash {chash})", flush=True)


PAL = {"iid": "#8C8C8C", "cluster": "#C44E52", "boot": "#4C72B0"}


def stage_figures(args):
    """fig_b2_coverage.png. Panel titles are COMPUTED from b2_coverage.csv at render
    time, so a claim-title cannot drift from the number it claims. The permuted arm is
    excluded from the mean drawn here and is reported in the table instead."""
    B1._style()
    import matplotlib.pyplot as plt
    out = f"{ROOT}/{args.out_dir}"
    cov = pd.read_csv(f"{out}/b2_coverage.csv")
    cov = cov[(cov["status"] == "ok") & (cov["arm"] != "permuted")
              & (cov["variant"] == "CCRCC") & (cov["setting"] == "CCRCC")
              & (cov["estimand"] == "theta3")]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.1), sharey=True)
    NAME = {"iid": "spot i.i.d.", "cluster": "donor cluster-robust",
            "boot": "donor bootstrap"}
    for ax, pop in zip(axes, ("spot", "donor")):
        d = cov[cov["population"] == pop]
        xs = sorted(d["n_L"].unique())
        worst = {}
        for vr in ("iid", "cluster", "boot"):
            for nm, ls, mk in (("classical", "-", "o"), ("pp", "--", "s")):
                sub = d[(d["variance"] == vr) & (d["estimator"] == nm)]
                ys = [sub[sub["n_L"] == x]["coverage"].mean() for x in xs]
                ax.plot(xs, ys, ls=ls, marker=mk, ms=3.2, color=PAL[vr], zorder=3)
                if nm == "classical":
                    worst[vr] = ys
                    ax.annotate(NAME[vr], (xs[-1], ys[-1]), xytext=(4, 0),
                                textcoords="offset points", va="center", fontsize=7,
                                color=PAL[vr])
        ax.axhline(0.90, color="#333333", lw=0.9, zorder=1)
        ax.annotate("nominal 0.90", (xs[-1], 0.90), xytext=(2, -11),
                    textcoords="offset points", fontsize=7, color="#333333")
        ax.set_xticks(xs)
        ax.set_xlim(min(xs) - 0.6, max(xs) + 7.0)
        ax.set_ylim(-0.02, 1.06)
        ax.set_xlabel("labelled donors $n_L$")
        ax.set_title(f"{'Spot' if pop == 'spot' else 'Donor'}-weighted: the i.i.d. "
                     f"interval covers\n{min(worst['iid']):.2f} to "
                     f"{max(worst['iid']):.2f}, the donor-clustered "
                     f"{min(worst['cluster']):.2f} to {max(worst['cluster']):.2f}")
    axes[0].set_ylabel("coverage of the full-data value over 200 draws")
    axes[0].text(0.03, 0.55, "circles, solid: classical\nsquares, dashed: PPI",
                 transform=axes[0].transAxes, fontsize=7, color="#333333")
    p = f"{out}/fig_b2_coverage.png"
    fig.savefig(p)
    B1.figure_provenance(out, "b2_figures", [f"{out}/b2_coverage.csv"], [p])
    print(f"[write] {os.path.basename(p)}", flush=True)
    return 0


def main(argv=None):
    args = parse_args(argv or sys.argv[1:])
    if args.figures:
        return stage_figures(args)
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
