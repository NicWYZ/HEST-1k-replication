#!/usr/bin/env python
"""Recompute every pooled number in docs/round3_final_report.md that is not already a cell of a
per-track pooled-number table.

The per-track tables are script-generated and are cited directly by the report:
  results/round3/A4_scores/a4b_summary.csv          (round3_a4b_hcp.py --summary)
  results/round3/B1_ppi/b1b2_report_numbers.csv     (round3_b1_ppi.py --report-numbers)
  results/round3/D4_expansion/d4_pooled_numbers.csv (round3_d4_consolidate.py)
This script adds the numbers the report pools ACROSS rows of committed tables in a way those
tables do not store (for example B2 coverage by setting, averaged over genes, estimands and
arms), plus the interval-3 job table read from a raw sacct dump.

Output: results/round3/final_report/final_report_numbers.csv (name, value, rule, source) and
results/round3/final_report/interval3_jobs.csv. Reads committed CSVs only; fits nothing.

Usage, from the repository root:
  python code/scripts/round3_final_report_numbers.py
"""
from __future__ import annotations

import os
import sys

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
R3 = os.path.join(ROOT, "results", "round3")
OUT = os.path.join(R3, "final_report")

rows: list[dict] = []


def add(name, value, rule, source):
    rows.append({"name": name, "value": value, "rule": rule, "source": source})


def b2_by_setting():
    src = "B2_semisynthetic/b2_coverage.csv"
    b = pd.read_csv(os.path.join(R3, src))
    b = b[(b.estimator == "classical") & (b.status == "ok")]
    for var, g in b.groupby("variance"):
        add(f"b2_classical_{var}_coverage_pooled", g.coverage.mean(),
            "mean over classical cells with status ok", src)
    enc = b[b.arm.isin(["hoptimus0", "uni_v2", "resnet50"])]
    t = enc.groupby(["setting", "population", "n_L", "variance"]).coverage.mean()
    for (setting, pop, nl, var), v in t.items():
        add(f"b2_classical_{var}_coverage__{setting}__{pop}__nL{nl}", v,
            "mean over genes, estimands and the three encoder arms; classical estimator", src)


def b2_width_by_arm():
    src = "B2_semisynthetic/b2_width_ratio.csv"
    w = pd.read_csv(os.path.join(R3, src))
    w = w[(w.estimand == "theta3") & (w.status == "ok")]
    for setting in ["CCRCC", "CCRCC_merged", "LYMPH_IDC"]:
        t = w[w.setting == setting].groupby(["population", "arm"]).width_ratio_cluster.mean()
        for (pop, arm), v in t.items():
            add(f"b2_width_ratio_cluster_theta3__{setting}__{pop}__{arm}", v,
                "mean PPI-to-classical cluster width ratio over genes and n_L, theta3", src)


def layout_spot_sets():
    src = "D4_expansion/d4_layout_spot_sets.csv"
    s = pd.read_csv(os.path.join(R3, src))
    one = s[s.encoder == s.encoder.iloc[0]]
    # the spot sets are encoder-independent; assert it rather than assume it
    for col in ["n_bench_patch", "n_hest_patch", "n_bench_only", "n_hest_only"]:
        per_enc = s.groupby("encoder")[col].sum()
        assert per_enc.nunique() == 1, (col, per_enc.to_dict())
    add("layout_spots_benchmark", int(one.n_bench_patch.sum()), "sum over 24 CCRCC samples, one encoder", src)
    add("layout_spots_hest", int(one.n_hest_patch.sum()), "sum over 24 CCRCC samples, one encoder", src)
    add("layout_spots_benchmark_only", int(one.n_bench_only.sum()), "sum over 24 CCRCC samples", src)
    add("layout_spots_hest_only", int(one.n_hest_only.sum()), "sum over 24 CCRCC samples", src)
    add("layout_spots_hest_share_pct", 100 * one.n_hest_patch.sum() / one.n_bench_patch.sum(),
        "100 * hest / benchmark", src)


def interval3_jobs():
    """Parse the raw sacct dump into the interval's job table, with the track per job."""
    raw = os.path.join(OUT, "interval3_sacct.txt")
    tracks = os.path.join(OUT, "interval3_job_tracks.csv")
    if not (os.path.exists(raw) and os.path.exists(tracks)):
        print("interval3 job table skipped: sacct dump or track map absent", file=sys.stderr)
        return
    j = pd.read_csv(raw, sep="|", dtype=str)
    j = j[~j.JobID.str.contains(r"\.", regex=True)]  # allocation rows only
    batch = pd.read_csv(raw, sep="|", dtype=str)
    batch = batch[batch.JobID.str.endswith(".batch")].copy()
    batch["JobID"] = batch.JobID.str.replace(".batch", "", regex=False)
    j = j.drop(columns=["MaxRSS"]).merge(batch[["JobID", "MaxRSS"]], on="JobID", how="left")
    m = pd.read_csv(tracks, dtype=str)
    j = m.merge(j, on="JobID", how="left", validate="one_to_one")
    assert j.State.notna().all(), j[j.State.isna()].JobID.tolist()
    j.to_csv(os.path.join(OUT, "interval3_jobs.csv"), index=False)
    for track, g in j.groupby("track"):
        add(f"jobs_{track}_n", len(g), "count of Slurm jobs", "final_report/interval3_jobs.csv")
        add(f"jobs_{track}_completed", int((g.State == "COMPLETED").sum()), "State == COMPLETED",
            "final_report/interval3_jobs.csv")
    add("jobs_total", len(j), "count of Slurm jobs", "final_report/interval3_jobs.csv")
    add("jobs_account_rc_htzhu_pi", int((j.Account == "rc_htzhu_pi").sum()), "Account == rc_htzhu_pi",
        "final_report/interval3_jobs.csv")

    def gb(x):
        if not isinstance(x, str) or not x:
            return float("nan")
        u = x[-1].upper()
        v = float(x[:-1]) if u in "KMGT" else float(x)
        return v * {"K": 1 / 1024 ** 2, "M": 1 / 1024, "G": 1.0, "T": 1024.0}.get(u, 1 / 1024 ** 3)

    j["max_rss_gb"] = j.MaxRSS.map(gb)
    j.to_csv(os.path.join(OUT, "interval3_jobs.csv"), index=False)
    for track, g in j.groupby("track"):
        add(f"jobs_{track}_peak_rss_gb", g.max_rss_gb.max(), "max over jobs of batch-step MaxRSS",
            "final_report/interval3_jobs.csv")
    add("jobs_on_spill", int((j.Partition == "spill").sum()), "Partition == spill",
        "final_report/interval3_jobs.csv")


def main():
    os.makedirs(OUT, exist_ok=True)
    b2_by_setting()
    b2_width_by_arm()
    layout_spot_sets()
    interval3_jobs()
    out = pd.DataFrame(rows)
    assert out.name.is_unique
    out.to_csv(os.path.join(OUT, "final_report_numbers.csv"), index=False)
    print(f"wrote {len(out)} rows")


if __name__ == "__main__":
    main()
