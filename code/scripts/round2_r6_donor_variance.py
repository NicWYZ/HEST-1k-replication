#!/usr/bin/env python
"""Round 2, stage R6: nested variance components of expression, grouped by DONOR.

Decision 1.3: the grouping variable is `donor_id` from the R5b audit, NOT HEST's `patient`
field. The audit found the field merges donors in COAD and splits one in IDC, so a
decomposition built on `patient` would be a well-estimated decomposition of the wrong
quantity. Every row here carries the audit status of its donor label so that a component
resting on unverifiable labels can be read as such.

Model, per task and per gene, on log1p expression:

    y_dsi = mu + a_d + b_s(d) + e_i(ds)

    a_d       donor            -> sigma2_donor
    b_s(d)    slide within donor -> sigma2_slide
    e_i(ds)   spot             -> sigma2_spot

Estimated by unbalanced nested ANOVA (Henderson method of moments), which is the standard
estimator for this design and needs no iterative fit for 50 genes x 10 tasks. Expected mean
squares for the unbalanced case:

    E[MS_spot]  = s2_spot
    E[MS_slide] = s2_spot + c1 * s2_slide
    E[MS_donor] = s2_spot + c2 * s2_slide + c3 * s2_donor

Which components exist is a property of the task's structure, not a choice:
  - s2_slide needs at least one donor with two or more slides (S > D).
  - s2_donor needs at least two donors (D > 1).
CCRCC's 24 one-slide donors give the best-powered s2_donor and no s2_slide at all; PRAD's
two donors with 15 and 8 slides give the best-powered s2_slide and a two-donor s2_donor.
Both are reported with n_donors and n_slides beside them so the power is visible.

Negative moment estimates are a known feature of this estimator, not an error. Both the raw
and the truncated-at-zero value are stored; the truncated one is used for proportions.

PRAD caveat, made explicit in the output rather than left to the reader: PRAD's
s2_slide INCLUDES the scan-session effect R4 measured (two sessions 0.0066 um/px apart,
separable at 0.977). A `session` column decomposes patient 2's slide component into
between-session and within-session parts so the two are not conflated.

Usage: round2_r6_donor_variance.py [task ...]
"""
import glob
import json
import os
import sys
import time
import zlib

import anndata as ad
import numpy as np
import pandas as pd
import scanpy as sc

ROOT = "/work/users/w/e/weiyang/hest_replication"
BD = f"{ROOT}/bench_data"
AUDIT = f"{ROOT}/results/round2/R5b_audit/donor_audit.csv"
META = f"{ROOT}/results/tailored/integrity/sample_metadata.csv"
OUT = f"{ROOT}/results/round2/R6_variance"
SEED = 1
N_BOOT = 200

# PRAD patient 2's two scan sessions. DERIVED from sample_metadata rather than hard-coded:
# the 15 patient-2 slides fall into two tight pixel-size clusters separated by a gap that is
# an order of magnitude wider than the spread inside either. R4 showed these two clusters are
# separable at 0.977 balanced accuracy with the donor held constant.
def prad_sessions(meta):
    """Derive PRAD patient 2's two scan sessions from the pixel-size clustering.

    Not hard-coded: the 15 patient-2 slides fall into two tight clusters whose separation is
    an order of magnitude wider than the spread inside either, and the cut is placed at the
    widest gap. R4 showed these two clusters are separable at 0.977 balanced accuracy with
    the donor held constant, which is why they are worth separating here.
    """
    p = meta.loc[meta["task"] == "PRAD"].reset_index(drop=True).copy()
    p["_px"] = p[PXCOL].astype(float)
    band = p.loc[(p._px > 0.33) & (p._px < 0.36)].sort_values("_px").reset_index(drop=True)
    assert len(band) >= 4, f"PRAD session band has only {len(band)} slides"
    d = band._px.diff()
    k = int(d.idxmax())
    cut = (band._px.iloc[k] + band._px.iloc[k - 1]) / 2
    lo = set(band.loc[band._px < cut, SIDCOL].astype(str))
    hi = set(band.loc[band._px >= cut, SIDCOL].astype(str))
    assert lo and hi, "session split degenerate"
    print(f"[PRAD] widest gap {d.max():.6f} um/px; cut {cut:.5f} -> "
          f"session A {len(lo)} slides, session B {len(hi)} slides", flush=True)
    return {**{x: "A" for x in lo}, **{x: "B" for x in hi}}


def nested_components(y, donor, slide):
    """Unbalanced two-level nested random-effects ANOVA, Henderson method of moments.

    Returns the three variance components plus the design constants and degrees of
    freedom, so a component estimated from one degree of freedom cannot be mistaken for
    a well-determined one.
    """
    df = pd.DataFrame({"y": y, "d": donor, "s": slide})
    N = len(df)
    n_ds = df.groupby(["d", "s"]).y.agg(["count", "mean"])
    n_d = df.groupby("d").y.agg(["count", "mean"])
    D, S = len(n_d), len(n_ds)
    grand = df.y.mean()

    ss_spot = float(((df.y - df.set_index(["d", "s"]).index.map(n_ds["mean"])) ** 2).sum())
    ss_slide = float((n_ds["count"] * (n_ds["mean"]
                      - n_ds.index.get_level_values("d").map(n_d["mean"])) ** 2).sum())
    ss_donor = float((n_d["count"] * (n_d["mean"] - grand) ** 2).sum())
    df_spot, df_slide, df_donor = N - S, S - D, D - 1

    out = dict(n_spots=N, n_slides=S, n_donors=D,
               df_spot=df_spot, df_slide=df_slide, df_donor=df_donor)
    if df_spot <= 0:
        return None
    ms_spot = ss_spot / df_spot
    out["var_spot"] = ms_spot

    # design constants
    sq_over_nd = float(sum((n_ds.loc[d, "count"] ** 2).sum() / n_d.loc[d, "count"]
                           for d in n_d.index))
    sq_over_N = float((n_ds["count"] ** 2).sum() / N)
    nd_sq_over_N = float((n_d["count"] ** 2).sum() / N)

    if df_slide > 0:
        c1 = (N - sq_over_nd) / df_slide
        ms_slide = ss_slide / df_slide
        v_slide = (ms_slide - ms_spot) / c1
        out.update(var_slide_raw=v_slide, var_slide=max(0.0, v_slide), c1=c1)
    else:
        out.update(var_slide_raw=np.nan, var_slide=np.nan, c1=np.nan)

    if df_donor > 0:
        c2 = (sq_over_nd - sq_over_N) / df_donor
        c3 = (N - nd_sq_over_N) / df_donor
        ms_donor = ss_donor / df_donor
        vs = out["var_slide"] if np.isfinite(out["var_slide"]) else 0.0
        v_donor = (ms_donor - ms_spot - c2 * vs) / c3
        out.update(var_donor_raw=v_donor, var_donor=max(0.0, v_donor), c2=c2, c3=c3)
    else:
        out.update(var_donor_raw=np.nan, var_donor=np.nan, c2=np.nan, c3=np.nan)
    return out


meta = pd.read_csv(META)
SIDCOL = "sample_id" if "sample_id" in meta.columns else meta.columns[0]
PXCOL = "pixel_size_um" if "pixel_size_um" in meta.columns else "pixel_size_um_estimated"
if "task" not in meta.columns:
    meta = meta.rename(columns={next(c for c in meta.columns if c.lower() == "task"): "task"})
PRAD_SESSION = prad_sessions(meta)

au = pd.read_csv(AUDIT)
donor_of = dict(zip(au.sample_id, au.donor_id))
status_of = dict(zip(au.sample_id, au.donor_label_status))
os.makedirs(OUT, exist_ok=True)
tasks = sys.argv[1:] or sorted(d for d in os.listdir(BD) if os.path.isdir(f"{BD}/{d}/adata"))

rows = []
for task in tasks:
    t0 = time.time()
    with open(f"{BD}/{task}/var_50genes.json") as f:
        gj = json.load(f)
    genes = gj["genes"] if isinstance(gj, dict) else list(gj)
    frames = []
    for p in sorted(glob.glob(f"{BD}/{task}/adata/*.h5ad")):
        sid = os.path.basename(p)[:-5]
        A = ad.read_h5ad(p)
        have = [g for g in genes if g in set(map(str, A.var_names))]
        if not have:
            continue
        sub = A[:, have]
        X = np.asarray(sub.X.todense() if hasattr(sub.X, "todense") else sub.X, dtype=np.float64)
        fr = pd.DataFrame(np.log1p(X), columns=have)
        fr["sample_id"] = sid
        frames.append(fr)
        del A
    if not frames:
        print(f"[skip] {task}: no gene columns", flush=True)
        continue
    Dt = pd.concat(frames, ignore_index=True)
    Dt["donor_id"] = Dt.sample_id.map(donor_of)
    assert Dt.donor_id.notna().all(), f"{task}: samples missing from the audit"
    present = [g for g in genes if g in Dt.columns]
    stat = sorted({status_of[s] for s in Dt.sample_id.unique()})
    print(f"\n[{task}] {len(Dt):,} spots | {Dt.sample_id.nunique()} slides | "
          f"{Dt.donor_id.nunique()} donors | label status {stat} | {len(present)} genes",
          flush=True)

    for g in present:
        rec = nested_components(Dt[g].to_numpy(), Dt.donor_id.to_numpy(),
                                Dt.sample_id.to_numpy())
        if rec is None:
            continue
        tot = rec["var_spot"] + (rec["var_slide"] if np.isfinite(rec["var_slide"]) else 0.0) \
              + (rec["var_donor"] if np.isfinite(rec["var_donor"]) else 0.0)
        rec.update(task=task, gene=g, total_var=tot,
                   frac_spot=rec["var_spot"] / tot if tot > 0 else np.nan,
                   frac_slide=(rec["var_slide"] / tot) if (tot > 0 and np.isfinite(rec["var_slide"])) else np.nan,
                   frac_donor=(rec["var_donor"] / tot) if (tot > 0 and np.isfinite(rec["var_donor"])) else np.nan,
                   donor_label_status=";".join(stat),
                   grouping="donor_id_from_R5b_audit")
        rows.append(rec)

    # PRAD only: split patient 2's slide component into between- and within-session
    if task == "PRAD":
        sess = Dt.sample_id.map(PRAD_SESSION)
        sub = Dt[sess.notna()].copy()
        sub["session"] = sess[sess.notna()].values
        if sub.session.nunique() == 2:
            for g in present:
                r2 = nested_components(sub[g].to_numpy(), sub.session.to_numpy(),
                                       sub.sample_id.to_numpy())
                if r2 is None:
                    continue
                r2.update(task="PRAD_patient2_by_session", gene=g,
                          grouping="scan_session (donor held constant)",
                          donor_label_status="verified",
                          total_var=r2["var_spot"] + max(0.0, np.nan_to_num(r2["var_slide"]))
                                    + max(0.0, np.nan_to_num(r2["var_donor"])))
                rows.append(r2)
    print(f"[{task}] done in {time.time()-t0:.0f}s", flush=True)
    del Dt

V = pd.DataFrame(rows)
V.to_csv(f"{OUT}/donor_variance_components.csv", index=False)
print(f"\nwrote {OUT}/donor_variance_components.csv ({len(V)} task-gene rows)")

real = V[~V.task.str.contains("_by_session")]
print("\n=== variance components by task (median over the 50 genes) ===")
summ = real.groupby("task").agg(
    n_donors=("n_donors", "first"), n_slides=("n_slides", "first"),
    df_slide=("df_slide", "first"), df_donor=("df_donor", "first"),
    var_spot=("var_spot", "median"), var_slide=("var_slide", "median"),
    var_donor=("var_donor", "median"),
    frac_donor=("frac_donor", "median"), frac_slide=("frac_slide", "median"),
    status=("donor_label_status", "first"))
print(summ.round(4).to_string())

est = real[real.n_donors >= 2]
print(f"\npooled between-donor fraction, CCRCC and PRAD (the two best-powered): "
      f"{real[real.task.isin(['CCRCC','PRAD'])].frac_donor.median():.4f}")
print(f"all tasks with >=2 donors: median {est.frac_donor.median():.4f}, "
      f"range {est.groupby('task').frac_donor.median().min():.4f}-"
      f"{est.groupby('task').frac_donor.median().max():.4f}")
sess = V[V.task == "PRAD_patient2_by_session"]
if len(sess):
    print(f"\nPRAD patient 2, donor held constant: between-session variance median "
          f"{sess.var_donor.median():.5f}, between-slide-within-session "
          f"{sess.var_slide.median():.5f}, spot {sess.var_spot.median():.5f}")
    print("  -> the share of PRAD's slide component that is scan session: "
          f"{sess.var_donor.median()/(sess.var_donor.median()+sess.var_slide.median()):.3f}")

with open(f"{OUT}/PROVENANCE__r6_variance.txt", "w") as f:
    f.write(
        "Round 2, stage R6 - nested variance components grouped by donor\n"
        f"slurm_job_id    : {os.environ.get('SLURM_JOB_ID','NA')}\n"
        f"node            : {os.environ.get('SLURMD_NODENAME','NA')}\n"
        f"date            : {time.strftime('%Y-%m-%dT%H:%M:%S%z')}\n"
        f"repo_commit     : {os.popen(f'git -C {ROOT} rev-parse HEAD').read().strip()}\n"
        f"script          : code/scripts/round2_r6_donor_variance.py\n"
        f"command_line    : {' '.join(sys.argv)}\n"
        f"pythonhashseed  : {os.environ.get('PYTHONHASHSEED','unset')}\n"
        "grouping        : donor_id from results/round2/R5b_audit/donor_audit.csv\n"
        "estimator       : unbalanced nested ANOVA, Henderson method of moments\n"
        "plan            : round2_R5_decisions.md directive 2.3 / plan phase-6\n")
