"""Round 6 extension, cheatsheet track, C7: the analysis tables.

Runs in the container. It joins the pilot's sessions (stage C5_pilot, which
the C5 memo counts as grid sessions) with the grid's (stage C6_grid) and
writes, under /results/C7_report/

  grid.csv            one row per size: writer, predictor, bytes, audits,
                      the metric with per-slide values and the pooled value,
                      and the codebook at the same size
  comparators.csv     the C4.4 table, copied beside it
  bstar.csv           the size needed at each head's value, as a bracket
  audits.csv          one row per audit: version, violations and rules broken
  tags.csv            each final cheatsheet tagged by keyword for the
                      rubric's A1 to A7, with the counts behind each tag
  forbidden.csv       keyword counts for what the rubric forbids, as a check
                      beside the checker's verdicts
  sessions.csv        every session of both stages, with tokens, cost,
                      turns, wall time, peak context and images returned
  cost_by_role.csv    sums and means per role
  rbar_vs_size.png    the metric against the allowance, with the comparators
  PROVENANCE.txt
and /results/C6_grid/predictions.parquet and scores.csv, as C5's summary did.

A resumed writer session reports its cost as the session's running total, so
a revision's own cost is that total minus the total at the previous version.
Its token counts are the revision's own.
"""
import datetime
import glob
import json
import os
import re
import subprocess
import sys

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import round6_cheatsheet_ext_build as B  # noqa: E402
import round6_cheatsheet_ext_c5_summary as C5  # noqa: E402
import round6_cheatsheet_ext_score as S  # noqa: E402

STAGES = ("C5_pilot", "C6_grid")
OUT = "/results/C7_report"
SIZES = [0] + [2 ** k for k in range(8, 17)]
TEST = ("INT13", "INT15", "INT24")

TAGS = {
    "A1_classes": r"\b(nests?|stroma|stromal|necrosis|necrotic|lymphoid|lymphocytes?|haemorrhage|hemorrhage|capillar\w+|eosinophilic|clear[- ]cell|fibrous|fibrosis|hyalin\w+|tubules?|glomerul\w+|vessels?|sarcomatoid|granular)\b",
    "A3_gradients": r"\b(rises? with|falls? with|increases? with|decreases? with|the more|the denser|denser|proportion of|share of|scales? with|in proportion|gradient|the higher the|the lower the)\b",
    "A4_modules": r"\b(modules?|co-?var\w+|rise and fall together|together|programs?|programmes?|signatures?|gene groups?|co-?express\w+|clusters? of genes)\b",
    "A5_patients": r"\b(some patients|some sections|sections? differ|between patients|between sections|across patients|across sections|section types?|patient-level|per-section|section-level)\b",
    "A6_cautions": r"\b(staining|stain intensity|caution|beware|artefacts?|artifacts?|do not rely|unreliable|misleading|pitfalls?)\b",
    "A7_levels": r"\b(overall|on average|typical(ly)?|means?|median|quantiles?|percentiles?|pct|sd|spread|range)\b",
}
FORBIDDEN = {
    "F1_code_or_models": r"\b(regression|ridge|k-?means|nearest neighbou?rs?|classifier|fit a model|train(ed|ing)? a|algorithm|pseudocode|threshold on)\b",
    "F2_computed_measures": r"\b(RGB|HSV|HED|pixel values?|mean colou?r|pixel counts?|fraction of pixels|texture statistics?|grey-?level|gray-?level|entropy|variance of|fourier|haematoxylin channel|hematoxylin channel|optical density)\b",
    "F3_keyed": r"(?<![A-Za-z0-9_])(s\d{4}|P[1-7])(?![A-Za-z0-9_])",
    "F5_metric": r"\b(pearson|correlation metric|scor(e|ed|ing) well|rescal\w+|z-?scor\w+|standardi[sz]e your predictions)\b",
    "F6_technical": r"\b(file size|image size|scanner|batch|png|jpeg|resolution)\b",
}


def sessions():
    rows = []
    for stage in STAGES:
        man = pd.read_csv(os.path.join("/results", stage, "manifest.csv"))
        for _, r in man.iterrows():
            peak, images, tools = C5.stream_stats(os.path.join("/private/logs", stage, r["stream"]))
            d = {k: r[k] for k in man.columns if k not in ("detail",)}
            d.update(peak_context_tokens=peak, images_returned=images, tool_calls=json.dumps(tools, sort_keys=True))
            rows.append(d)
    s = pd.DataFrame(rows)
    s["cost_own_usd"] = s["cost_usd"]
    for i, r in s[s["role"] == "writer_revision"].iterrows():
        prev = s[(s["trial_id"] == r["trial_id"]) & (s["version"] == r["version"] - 1)
                 & s["role"].isin(["writer", "writer_revision"])]
        assert len(prev) == 1
        s.loc[i, "cost_own_usd"] = r["cost_usd"] - prev["cost_usd"].iloc[0]
    return s


def grid_table(sess, comp):
    genes = B.package()[0]
    rows, audits, parts, scores = [], [], [], []
    writers = {}
    for stage in STAGES:
        for f in glob.glob(os.path.join("/results", stage, "writers", "*.json")):
            w = json.load(open(f))
            writers[w["size"]] = (stage, w)
    preds = {}
    for stage in STAGES:
        for f in glob.glob(os.path.join("/results", stage, "scores", "*.json")):
            sc = json.load(open(f))
            preds[(sc["role"], sc["size"])] = (stage, sc)
            tid = sc["trial_id"]
            truth, slide, _ = B.truth_for(tid)
            pred = S.validate(pd.read_csv(os.path.join("/results", stage, "predictions_raw", f"{tid}.csv")),
                              list(truth.index), genes)
            again = S.score(pred, truth, slide)
            assert abs(again["rbar"] - sc["rbar"]) < 1e-12, tid
            scores.append({"stage": stage, "trial_id": tid, "role": sc["role"], "size": sc["size"], "writer": sc["writer"],
                           "rbar": sc["rbar"], "pooled": sc["pooled"],
                           **{f"rbar_{k}": sc["per_slide"][k] for k in TEST},
                           "n_constant_pred_cells": sc["n_constant_pred_cells"]})
            if stage == "C6_grid":
                m = json.load(open(os.path.join(B.MAPS, f"{tid}.json")))["target"]["spots"]
                d = pred.reset_index(drop=True)
                for name, col in (("barcode", [m[p][1] for p in pred.index]), ("slide", [m[p][0] for p in pred.index]),
                                  ("pid", list(pred.index)), ("trial_id", tid)):
                    d.insert(0, name, col)
                parts.append(d)
    schema = pa.schema([pa.field(c, pa.string()) for c in ("trial_id", "pid", "slide", "barcode")]
                       + [pa.field(g, pa.float64()) for g in genes])
    pq.write_table(pa.Table.from_pandas(pd.concat(parts, ignore_index=True), schema=schema, preserve_index=False),
                   "/results/C6_grid/predictions.parquet")
    sc_all = pd.DataFrame(scores).sort_values(["role", "size"])
    sc_all[sc_all["stage"] == "C6_grid"].to_csv("/results/C6_grid/scores.csv", index=False)
    cb = comp[comp["comparator"] == "codebook"].set_index("size")
    for b in SIZES:
        role = "baseline" if b == 0 else "predictor"
        stage, sc = preds[(role, b)]
        row = {"size": b, "stage": stage, "predictor": sc["trial_id"], "rbar": sc["rbar"], "pooled": sc["pooled"],
               **{f"rbar_{k}": sc["per_slide"][k] for k in TEST}, "n_constant_pred_cells": sc["n_constant_pred_cells"]}
        if b:
            wstage, w = writers[b]
            vs = [a for a in w["audits"] if "audit_id" in a]
            row.update(writer=w["writer"], bytes_v1=vs[0]["bytes_written"], bytes_v1_kept=vs[0]["bytes_kept"],
                       bytes_final=vs[-1]["bytes_kept"], share_of_allowance=vs[-1]["bytes_kept"] / b,
                       revisions=w["revisions"], final_version=w["final_version"], final_passed=w["passed"],
                       flagged=w["flagged"], violations_by_audit=" ".join(str(a["violations"]) for a in vs),
                       mechanical_flags_by_version=" ".join(str(a["mechanical_flags"]) for a in vs),
                       codebook_rbar=cb.loc[b, "rbar"], codebook_pooled=cb.loc[b, "pooled"],
                       **{f"codebook_{k}": cb.loc[b, f"rbar_{k}"] for k in TEST})
            for a in vs:
                v = json.load(open(os.path.join("/results", wstage, "verdicts", f"{a['audit_id']}.json")))
                audits.append({"size": b, "writer": w["writer"], "version": a["version"], "audit_id": a["audit_id"],
                               "bytes_written": a["bytes_written"], "bytes_kept": a["bytes_kept"],
                               "mechanical_flags": a["mechanical_flags"], "violations": len(v["violations"]),
                               "rules": " ".join(sorted(str(x["rule"]) for x in v["violations"])),
                               "pass_key": v["pass"],
                               "reasons": " | ".join(" ".join(str(x["reason"]).split()) for x in v["violations"])})
        rows.append(row)
    stage, sc = preds[("combined", 0)]
    comb = {"trial_id": sc["trial_id"], "rbar": sc["rbar"], "pooled": sc["pooled"],
            **{f"rbar_{k}": sc["per_slide"][k] for k in TEST}}
    return pd.DataFrame(rows), pd.DataFrame(audits), comb, sc_all, writers


def bstar(grid, comp):
    rows = []
    g = grid[grid["size"] > 0].sort_values("size")
    for enc in ("uni_v2", "virchow2"):
        tau = comp[(comp["comparator"] == "head_sample") & (comp["encoder"] == enc)]["rbar"].iloc[0]
        ok = g[g["rbar"] >= tau]
        if len(ok):
            b = int(ok["size"].iloc[0])
            below = int(g[g["size"] < b]["size"].max()) if (g["size"] < b).any() else 0
            rows.append({"threshold": f"{enc} head on the 3,500 writer spots", "tau": tau, "reached": True,
                         "bracket_low": below, "bracket_high": b,
                         "sizes_at_or_above": " ".join(str(int(x)) for x in ok["size"]),
                         "sizes_below_after_first": " ".join(str(int(x)) for x in g[(g["size"] > b) & (g["rbar"] < tau)]["size"])})
        else:
            rows.append({"threshold": f"{enc} head on the 3,500 writer spots", "tau": tau, "reached": False,
                         "bracket_low": int(g["size"].max()), "bracket_high": "", "sizes_at_or_above": "",
                         "sizes_below_after_first": ""})
    return pd.DataFrame(rows)


def tag_table(writers, genes):
    rows, frows = [], []
    for b, (stage, w) in sorted(writers.items()):
        text = open(os.path.join("/results", stage, "cheatsheets", w["final"]), encoding="utf-8").read()
        lines = text.split("\n")
        counts = {k: len(re.findall(p, text, flags=re.IGNORECASE)) for k, p in TAGS.items()}
        gene_re = re.compile(r"(?<![A-Za-z0-9])(" + "|".join(map(re.escape, genes)) + r")(?![A-Za-z0-9])")
        num_re = re.compile(r"(?<![A-Za-z0-9_.])\d+(?:\.\d+)?(?![A-Za-z_])")
        # A2: lines that name a tissue class, a gene and a number together
        a2 = sum(1 for l in lines if re.search(TAGS["A1_classes"], l, flags=re.IGNORECASE) and gene_re.search(l) and num_re.search(l))
        row = {"size": b, "writer": w["writer"], "file": w["final"], "bytes": len(text.encode()), "lines": len(lines),
               "genes_named": len(set(gene_re.findall(text))), "numbers": len(num_re.findall(text)),
               "A1_classes_n": counts["A1_classes"], "A2_class_gene_value_lines": a2,
               **{f"{k}_n": v for k, v in counts.items() if k != "A1_classes"}}
        row.update(A1=counts["A1_classes"] >= 3, A2=a2 >= 1, A3=counts["A3_gradients"] >= 1, A4=counts["A4_modules"] >= 1,
                   A5=counts["A5_patients"] >= 1, A6=counts["A6_cautions"] >= 1, A7=counts["A7_levels"] >= 1)
        rows.append(row)
        frows.append({"size": b, "writer": w["writer"],
                      **{k: len(re.findall(p, text, flags=0 if k == "F3_keyed" else re.IGNORECASE)) for k, p in FORBIDDEN.items()}})
    return pd.DataFrame(rows), pd.DataFrame(frows)


def figure(grid, comp, comb):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    g = grid[grid["size"] > 0].sort_values("size")
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    ax.plot(g["size"], g["rbar"], "o-", color="#1f4e79", label="cheatsheet predictor, one trial per size")
    ax.plot(g["size"], g["codebook_rbar"], "s--", color="#888888", label="size-matched codebook on uni_v2")
    base = grid[grid["size"] == 0]["rbar"].iloc[0]
    for val, lab, col, ls in ((base, "baseline, 0 bytes", "#b03a2e", ":"),
                              (comb["rbar"], "combined session", "#1e8449", "-."),
                              (comp[(comp.comparator == "head_sample") & (comp.encoder == "uni_v2")]["rbar"].iloc[0],
                               "uni_v2 head, 3,500 writer spots", "#000000", "-"),
                              (comp[(comp.comparator == "head_sample") & (comp.encoder == "virchow2")]["rbar"].iloc[0],
                               "virchow2 head, 3,500 writer spots", "#7d3c98", "-")):
        ax.axhline(val, color=col, linestyle=ls, linewidth=1.2, label=lab)
    ax.set_xscale("log", base=2)
    ax.set_xticks(g["size"])
    ax.set_xticklabels([f"{int(b):,}" for b in g["size"]], rotation=45, ha="right")
    ax.set_xlabel("cheatsheet allowance, bytes")
    ax.set_ylabel("mean within-slide Pearson over 3 test slides")
    ax.legend(fontsize=7.5, loc="lower center", bbox_to_anchor=(0.62, 0.0))
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "rbar_vs_size.png"), dpi=160)


def main():
    os.makedirs(OUT, exist_ok=True)
    comp = pd.read_csv("/results/C4_comparators/tables/comparators.csv")
    comp.to_csv(os.path.join(OUT, "comparators.csv"), index=False)
    sess = sessions()
    sess.to_csv(os.path.join(OUT, "sessions.csv"), index=False)
    md5s = [{"stage": st, "file": os.path.basename(f), "md5": C5.md5(f), "bytes": os.path.getsize(f)}
            for st in STAGES for f in sorted(glob.glob(f"/private/logs/{st}/*.stream.jsonl"))]
    pd.DataFrame(md5s)[lambda d: d["stage"] == "C6_grid"].to_csv("/results/C6_grid/transcripts_md5.csv", index=False)
    by = sess.groupby("role").agg(sessions=("trial_id", "size"), cost_usd=("cost_own_usd", "sum"),
                                  cost_mean=("cost_own_usd", "mean"), input_tokens=("input_tokens", "sum"),
                                  output_tokens=("output_tokens", "sum"), cache_read=("cache_read", "sum"),
                                  cache_write=("cache_write", "sum"), turns=("num_turns", "sum"),
                                  wall_s=("wall_s", "sum"), wall_mean_s=("wall_s", "mean"),
                                  peak_context_max=("peak_context_tokens", "max"),
                                  images_returned=("images_returned", "sum")).reset_index()
    total = by.drop(columns=["role", "cost_mean", "wall_mean_s", "peak_context_max"]).sum().to_dict()
    by = pd.concat([by, pd.DataFrame([{"role": "all", **total}])], ignore_index=True)
    by.to_csv(os.path.join(OUT, "cost_by_role.csv"), index=False)
    grid, audits, comb, sc_all, writers = grid_table(sess, comp)
    grid.to_csv(os.path.join(OUT, "grid.csv"), index=False)
    audits.to_csv(os.path.join(OUT, "audits.csv"), index=False)
    sc_all.to_csv(os.path.join(OUT, "scores_all.csv"), index=False)
    json.dump(comb, open(os.path.join(OUT, "combined.json"), "w"), indent=1)
    bs = bstar(grid, comp)
    bs.to_csv(os.path.join(OUT, "bstar.csv"), index=False)
    tags, forb = tag_table(writers, B.package()[0])
    tags = tags.merge(grid[["size", "rbar", "pooled"]], on="size")
    tags.to_csv(os.path.join(OUT, "tags.csv"), index=False)
    forb.to_csv(os.path.join(OUT, "forbidden.csv"), index=False)
    g = grid[grid["size"] > 0]
    spread = {"agents_min": g["rbar"].min(), "agents_max": g["rbar"].max(), "agents_range": g["rbar"].max() - g["rbar"].min(),
              "codebook_min": g["codebook_rbar"].min(), "codebook_max": g["codebook_rbar"].max(),
              "codebook_range": g["codebook_rbar"].max() - g["codebook_rbar"].min(),
              "codebook_min_from_512": g[g["size"] >= 512]["codebook_rbar"].min(),
              "codebook_range_from_512": g[g["size"] >= 512]["codebook_rbar"].max() - g[g["size"] >= 512]["codebook_rbar"].min(),
              "agents_range_4096_to_65536": g[g["size"] >= 4096]["rbar"].max() - g[g["size"] >= 4096]["rbar"].min(),
              "best_size": int(g.loc[g["rbar"].idxmax(), "size"]), "best_rbar": g["rbar"].max(),
              "spearman_rbar_vs_size": float(pd.Series(g["rbar"].to_numpy()).corr(pd.Series(np.log2(g["size"].to_numpy())), method="spearman"))}
    json.dump(spread, open(os.path.join(OUT, "spread.json"), "w"), indent=1)
    figure(grid, comp, comb)
    v = lambda c: subprocess.run(c, shell=True, capture_output=True, text=True).stdout.strip()  # noqa: E731
    scripts = sorted(glob.glob(os.path.join(HERE, "round6_cheatsheet_ext_*.py"))) + [os.path.join(HERE, "round6_cheatsheet_score.py"), os.path.join(HERE, "round6_cheatsheet_scan.py")]
    prov = f"""stage: STAGE
machine: Nicolas's Mac (arm64, macOS 26.6.2), in the container r6ext (image r6ext:1)
date_utc: {datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')}
code_commit: {os.environ.get('CODE_COMMIT', 'see the md5s below')}
commands: COMMANDS
PYTHONHASHSEED: {os.environ.get('PYTHONHASHSEED', 'not set')}
claude_code_version: {v('claude --version')}
served_model: {', '.join(sorted(set(sess['served_model'].astype(str))))}
effort: medium
data_package_manifest_md5: {C5.md5('/private/package/MANIFEST.tsv')}
trial_python: {v('python3 --version')}, numpy 2.5.3, pandas 3.0.5, scipy 1.18.1, Pillow 12.3.0, scikit-image 0.26.0, scikit-learn 1.9.1
script_md5:
""" + "".join(f"  {C5.md5(s)}  {os.path.basename(s)}\n" for s in scripts)
    run = "/opt/harness/bin/python -B /repo/code/scripts/round6_cheatsheet_ext_run.py C6_grid"
    open("/results/C6_grid/PROVENANCE.txt", "w").write(prov.replace("STAGE", "C6 the grid").replace(
        "COMMANDS", f"{run} grid --sizes 256 512 1024 2048 --parallel 4\n          {run} grid --sizes 8192 16384 32768 65536 --parallel 4\n          {run} combined"))
    open(os.path.join(OUT, "PROVENANCE.txt"), "w").write(prov.replace("STAGE", "C7 analysis").replace(
        "COMMANDS", "/opt/harness/bin/python -B /repo/code/scripts/round6_cheatsheet_ext_c7_analysis.py"))
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 40)
    print(grid.drop(columns=["stage", "predictor", "writer", "n_constant_pred_cells"]).round(4).to_string(index=False))
    print(comb)
    print(bs.to_string(index=False))
    print(audits.drop(columns=["reasons"]).to_string(index=False))
    print(tags.drop(columns=["file", "writer"]).round(3).to_string(index=False))
    print(forb.to_string(index=False))
    print(by.round(3).to_string(index=False))
    print(json.dumps(spread, indent=1))


if __name__ == "__main__":
    main()
