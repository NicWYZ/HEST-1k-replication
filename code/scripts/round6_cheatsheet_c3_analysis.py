"""Round 6 cheatsheet track, C3: analysis of the C2 grid for the closing report.

Reads only committed files: the C2 manifest, scores and cheatsheets, the C0
comparators, the C1 pilot's manifest and projection, and the pilot re-read
under rule (b). Writes, under results/round6/cheatsheet/C3_report/,

  grid.csv              rbar per arm and size (one replicate, Opus, medium), with the
                        allowance, bytes written and the comparators at that size
  bstar.csv             b*(0.8) and b* at the benchmark heads' rbar, as brackets
  arm_differences.csv   A - B, A - C and B - C at each size
  effort.csv            Opus's four pilot slots, medium (C2) beside high (C1, rules a and b)
  pilot_reference_points.csv  Haiku's and Sonnet's high-effort pilot values
  cost_by_role.csv      tokens, cost, turns and wall time per role, against the C1 projection
  cost_totals.csv       totals and the stage's wall-clock span
  scan_counts.csv       per trial, refused network attempts, outside paths, credential-folder
                        references and system paths (C1 memo, section 4, item 2)
  cheatsheet_tags.csv   tags by script for every C1 and C2 cheatsheet, and rbar by tag
  predictions.csv       C.1 to C.8 against outcomes
  headline_values.csv   derived values the report quotes (differences, gaps, ratios, counts)
  rbar_vs_bytes.png     rbar against the allowance and against bytes written

    python round6_cheatsheet_c3_analysis.py
"""
import os
import re

import numpy as np
import pandas as pd

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
R = os.path.join(REPO, "results/round6/cheatsheet")
OUT = os.path.join(R, "C3_report")
SIZES = [0, 4096, 32768, 262144, "inf"]
SIZE_LABEL = {0: "0", 4096: "4096", 32768: "32768", 262144: "262144", "inf": "inf"}


def load():
    m = pd.read_csv(os.path.join(R, "C2_grid/manifest.csv"))
    assert len(m) == 20 and (m["status"] == "done").all()
    assert set(m["served_model"]) == {"claude-opus-5-5"} and set(m["effort"]) == {"medium"}
    comp = pd.read_csv(os.path.join(R, "C0_comparators/comparators.csv"))
    pm = pd.read_csv(os.path.join(R, "C1_pilot/manifest.csv"))
    proj = pd.read_csv(os.path.join(R, "C1_pilot/c1_projection.csv"))
    ref = pd.read_csv(os.path.join(R, "C2_grid/pilot_reference.csv"))
    return m, comp, pm, proj, ref


def size_key(s):
    s = str(s)
    return "inf" if s == "inf" else int(float(s))


def grid(m, comp):
    w = m[m["role"] == "writer"].set_index("slot")
    rows = []
    for arm in ("A", "B", "C"):
        for b in SIZES:
            if b == 0:
                slot = "opus.baseline.AB.0.r1" if arm in ("A", "B") else "opus.baseline.C.0.r1"
            elif b == "inf":
                slot = f"opus.combined.{arm}.inf.r1"
            else:
                slot = f"opus.predictor.{arm}.{b}.r1"
            r = m[m["slot"] == slot].iloc[0]
            wb = np.nan
            if b not in (0, "inf"):
                wslot = f"opus.writer.{'B' if arm == 'B' else 'AC'}.{b}.r1"
                wb = w.loc[wslot, "bytes_written"]
                assert w.loc[wslot, "trial_id"] == r["writer_trial_id"]
            c = comp[comp["arm"] == arm]
            head_u = c[(c.comparator == "benchmark_head") & (c.encoder == "uni_v2")]["rbar"].iloc[0]
            head_h = c[(c.comparator == "benchmark_head") & (c.encoder == "hoptimus1")]["rbar"].iloc[0]
            cb = c[(c.comparator == "codebook") & (c["size"].astype(str).str.replace(".0", "", regex=False) == str(b))]
            rows.append({"arm": arm, "size": SIZE_LABEL[b], "slot": slot, "trial_id": r["trial_id"],
                         "writer_trial_id": r["writer_trial_id"] if isinstance(r["writer_trial_id"], str) else "",
                         "bytes_written": wb, "rbar": r["rbar"], "head_uni_v2": head_u, "head_hoptimus1": head_h,
                         "codebook_uni_v2": cb["rbar"].iloc[0] if len(cb) else np.nan,
                         "codebook_k": cb["k"].iloc[0] if len(cb) else np.nan})
    return pd.DataFrame(rows)


def bracket(vals, tau):
    """Smallest grid size whose rbar reaches tau, as (previous size, that size]."""
    prev = None
    for b in SIZES:
        if vals[b] >= tau:
            return f"({SIZE_LABEL[prev]}, {SIZE_LABEL[b]}]" if prev is not None else f"<= {SIZE_LABEL[b]}"
        prev = b
    return "not reached"


def bstar(g):
    rows = []
    for arm, d in g.groupby("arm"):
        vals = {size_key(s): v for s, v in zip(d["size"], d["rbar"])}
        for name, tau in (("0.8", 0.8), ("head_uni_v2", d["head_uni_v2"].iloc[0]),
                          ("head_hoptimus1", d["head_hoptimus1"].iloc[0])):
            rows.append({"arm": arm, "threshold": name, "tau": tau, "bracket": bracket(vals, tau)})
        # the codebook against the same thresholds, at finite sizes only
        cvals = {size_key(s): v for s, v in zip(d["size"], d["codebook_uni_v2"]) if size_key(s) not in (0, "inf")}
        for name, tau in (("0.8", 0.8), ("head_uni_v2", d["head_uni_v2"].iloc[0])):
            hit = [b for b in (4096, 32768, 262144) if cvals[b] >= tau]
            rows.append({"arm": arm, "threshold": f"codebook vs {name}", "tau": tau,
                         "bracket": f"first reached at {hit[0]}" if hit else "not reached"})
    return pd.DataFrame(rows)


def arm_diffs(g):
    p = g.pivot(index="size", columns="arm", values="rbar").reindex([SIZE_LABEL[b] for b in SIZES])
    out = pd.DataFrame({"size": p.index, "A": p["A"].values, "B": p["B"].values, "C": p["C"].values})
    out["A_minus_B"] = out["A"] - out["B"]
    out["A_minus_C"] = out["A"] - out["C"]
    out["B_minus_C"] = out["B"] - out["C"]
    out["note"] = ["A and B share the S1* baseline; C has its own on S2*", "", "", "",
                   "combined sessions, no cheatsheet"]
    return out


def effort(m, ref, pm):
    pairs = [("opus.baseline.AB.0.r1", "baseline"), ("opus.writer.B.32768.r1", "writer"),
             ("opus.predictor.B.32768.r1", "predictor"), ("opus.combined.B.inf.r1", "combined")]
    pmi = pm.set_index("trial_id")
    rows = []
    for slot, role in pairs:
        med = m[m["slot"] == slot].iloc[0]
        rf = ref[ref["slot"] == slot].iloc[0]
        ta, tb = rf["trial_rule_a"], rf["trial_rule_b"]
        rows.append({
            "slot": slot, "role": role,
            "medium_trial": med["trial_id"], "medium_rbar": med["rbar"], "medium_cost_usd": med["cost_usd"],
            "medium_turns": med["turns"], "medium_wall_s": med["wall_s"], "medium_bytes_written": med["bytes_written"],
            "high_trial_rule_a": ta, "high_rbar_rule_a": pmi.loc[ta, "rbar"],
            "high_cost_rule_a": pmi.loc[ta, "cost_usd"], "high_turns_rule_a": pmi.loc[ta, "turns"],
            "high_wall_rule_a": pmi.loc[ta, "wall_s"],
            "high_trial_rule_b": tb, "high_rbar_rule_b": pmi.loc[tb, "rbar"],
            "high_cost_rule_b": pmi.loc[tb, "cost_usd"], "high_turns_rule_b": pmi.loc[tb, "turns"],
            "high_wall_rule_b": pmi.loc[tb, "wall_s"], "high_bytes_written": pmi.loc[tb, "bytes_written"],
        })
    e = pd.DataFrame(rows)
    e["diff_rbar_vs_rule_b"] = e["medium_rbar"] - e["high_rbar_rule_b"]
    e["diff_rbar_vs_rule_a"] = e["medium_rbar"] - e["high_rbar_rule_a"]
    e["cost_ratio_vs_rule_b"] = e["medium_cost_usd"] / e["high_cost_rule_b"]
    return e


def pilot_points(ref, pm):
    pmi = pm.set_index("trial_id")
    rows = []
    for _, r in ref.iterrows():
        if r["model"] == "claude-opus-5-5":
            continue
        rows.append({"slot": r["slot"], "model": r["model"], "role": r["role"], "rbar_rule_a": r["rbar_rule_a"],
                     "rbar_rule_b": r["rbar_rule_b"], "trial_rule_b": r["trial_rule_b"],
                     # a predictor's point sits at its writer's bytes
                     "bytes_written": pmi.loc[pmi.loc[r["trial_rule_b"], "writer_trial_id"], "bytes_written"]
                     if r["role"] == "predictor" else pmi.loc[r["trial_rule_b"], "bytes_written"]})
    return pd.DataFrame(rows)


def costs(m, proj):
    tok = ["input_tokens", "output_tokens", "cache_read", "cache_write"]
    g = m.groupby("role").agg(n=("trial_id", "size"), **{t: (t, "sum") for t in tok},
                              cost_usd=("cost_usd", "sum"), turns=("turns", "sum"), wall_s=("wall_s", "sum"))
    g["cost_per_trial"] = g["cost_usd"] / g["n"]
    g["wall_per_trial_s"] = g["wall_s"] / g["n"]
    p = proj[proj["model"] == "opus"].set_index("role")
    g["c1_cost_per_trial_high"] = p["cost_per_counted_usd"]
    g["c1_wall_per_trial_high_s"] = p["wall_per_counted_s"]
    g["c1_projected_cost_this_grid"] = g["n"] * g["c1_cost_per_trial_high"]
    g["c1_projected_wall_this_grid_s"] = g["n"] * g["c1_wall_per_trial_high_s"]
    g["cost_ratio_c2_to_c1"] = g["cost_per_trial"] / g["c1_cost_per_trial_high"]
    g = g.reset_index()
    span = (pd.to_datetime(m["finished_utc"]).max() - pd.to_datetime(m["started_utc"]).min()).total_seconds()
    tot = pd.DataFrame([{
        "trials": len(m), "cost_usd": m["cost_usd"].sum(), "turns": m["turns"].sum(),
        "wall_s_summed": m["wall_s"].sum(), "wall_clock_span_s": span,
        "first_start_utc": m["started_utc"].min(), "last_finish_utc": m["finished_utc"].max(),
        "c1_projected_cost_this_grid": g["c1_projected_cost_this_grid"].sum(),
        "c1_projected_wall_this_grid_s": g["c1_projected_wall_this_grid_s"].sum(),
        "c1_projected_cost_full_opus_grid_high": proj[proj["model"] == "opus"]["projected_cost_usd"].sum(),
        **{t: m[t].sum() for t in ["input_tokens", "output_tokens", "cache_read", "cache_write"]},
    }])
    return g, tot


def scan_counts(m):
    hits = pd.read_csv(os.path.join(R, "C2_grid/scan_hits.csv"))
    sys_paths = hits[hits["kind"] == "path_system"].groupby("trial_id").size()
    out = m[["trial_id", "slot", "role", "scan_excluding_hits", "scan_network_attempts", "scan_outside_paths",
             "scan_credential_refs"]].copy()
    out["scan_system_paths"] = out["trial_id"].map(sys_paths).fillna(0).astype(int)
    out["kinds_seen"] = out["trial_id"].map(hits.groupby("trial_id")["kind"].apply(lambda s: ";".join(sorted(set(s)))))
    return out


GENE_LINE = re.compile(r"^\s*[A-Z][A-Z0-9]{1,9}\b(?:[\s|:,]+-?\d*\.?\d+){3,}")
VISUAL = re.compile(r"\b(white|nucle\w*|lymphocyt\w*|pigment\w*|keratin\w*|stroma\w*|vessel\w*|eosin\w*|"
                    r"cytoplasm|tissue fraction|hematox\w*|RBC|blood)\b", re.I)
NUMBER = re.compile(r"\d+\.?\d*")
CODE = re.compile(r"^\s*(def |import |from \w+ import|for .* in .*:|return )|```|\bcoef\w*\b|\bintercept\b|\bweights?\b", re.I)


def tag(text):
    lines = text.splitlines()
    gene_rows = sum(1 for l in lines if GENE_LINE.match(l))
    visual_num = sum(1 for l in lines if VISUAL.search(l) and NUMBER.search(l))
    prose = sum(1 for l in lines if len(re.findall(r"[A-Za-z]{3,}", l)) >= 6)
    code = sum(1 for l in lines if CODE.search(l))
    # rows of values for individual spots: an encoded row (a long run without spaces of mixed
    # symbols) or a reference row with its own ID and many numbers
    per_spot = sum(1 for l in lines if re.search(r"\S{40,}", l) and not re.search(r"[a-z]{4,}\s[a-z]{4,}", l)) \
        + sum(1 for l in lines if re.match(r"^\s*REF\b", l))
    return {
        "prose": prose >= 10,
        "numbers_keyed_to_visual_features": visual_num >= 5,
        "per_cluster_values": gene_rows >= 40,
        "code_or_coefficients": code >= 3,
        "values_keyed_to_individual_patches": per_spot >= 100,
        "n_prose_lines": prose, "n_visual_number_lines": visual_num, "n_gene_rows": gene_rows,
        "n_code_lines": code, "n_per_spot_rows": per_spot,
    }


def tags(m, pm):
    rows = []
    for stage, man in (("C1_pilot", pm), ("C2_grid", m)):
        w = man[(man["role"] == "writer") & (man["status"] == "done")]
        for _, r in w.iterrows():
            p = os.path.join(R, stage, "cheatsheets", f"{r['trial_id']}.txt")
            t = tag(open(p, encoding="utf-8", errors="replace").read())
            preds = man[(man["writer_trial_id"] == r["trial_id"]) & (man["status"] == "done")]
            for _, q in (preds.iterrows() if len(preds) else [(None, None)]):
                rows.append({"stage": stage, "writer_trial_id": r["trial_id"], "writer_slot": r["slot"],
                             "model": r["model"], "bytes_kept": r["bytes_kept"], **t,
                             "predictor_slot": q["slot"] if q is not None else "",
                             "predictor_rbar": q["rbar"] if q is not None else np.nan})
    return pd.DataFrame(rows)


def predictions(g, e):
    v = {(r.arm, r.size): r.rbar for r in g.itertuples()}
    head = {a: g[g.arm == a]["head_uni_v2"].iloc[0] for a in "ABC"}
    rows = []
    b0 = v[("A", "0")]
    rows.append(("C.1", "At b = 0, Opus's rbar on S1* is between 0.05 and 0.35, and Haiku's is below Opus's",
                 f"Opus at medium {b0:.3f} (at high in C1, 0.502); Haiku's pilot value is at high effort",
                 "refuted", "the range clause fails at both efforts; the Haiku clause compares across efforts and is not tested at medium"))
    c = [v[("C", s)] for s in ("4096", "32768", "262144")]
    rows.append(("C.2", "In arm C no model reaches the uni_v2 comparator's rbar on S2* at any finite size",
                 f"Opus {c[0]:.3f}, {c[1]:.3f}, {c[2]:.3f} against {head['C']:.3f}",
                 "held" if max(c) < head["C"] else "refuted", "for Opus only; the margin at 262144 is under 0.05"))
    ci = v[("C", "inf")]
    rows.append(("C.3", "In arm C Opus's combined session is above its own 262,144-byte value and below the uni_v2 comparator",
                 f"combined {ci:.3f}, 262144 {c[2]:.3f}, head {head['C']:.3f}",
                 "partly held" if (ci < head["C"]) != (ci > c[2]) else ("held" if ci > c[2] else "refuted"),
                 "below the head, but not above the 262144 value"))
    a32, a262 = v[("A", "32768")], v[("A", "262144")]
    rows.append(("C.4", "In arm A no model reaches 0.8 at 32,768 bytes, and at least one reaches it at 262,144",
                 f"Opus {a32:.3f} at 32768, {a262:.3f} at 262144",
                 "held" if a32 < 0.8 <= a262 else "refuted", "for Opus only"))
    b32, b262 = v[("B", "32768")], v[("B", "262144")]
    k1, k2 = abs(b262 - b32) <= 0.05, b262 < a262
    rows.append(("C.5", "In arm B, rbar at 262,144 is within 0.05 of 32,768 and below arm A at 262,144",
                 f"B {b32:.3f} and {b262:.3f} (difference {b262 - b32:.3f}); A at 262144 {a262:.3f}",
                 "held" if k1 and k2 else ("partly held" if k1 or k2 else "refuted"),
                 "the first clause fails, the second holds"))
    rows.append(("C.6", "Replicate means ordered Opus, Sonnet, Haiku in two thirds of arm and size pairs",
                 "only Opus ran in C2", "not tested", "C1 memo, section 4"))
    sc = e[e["role"] != "writer"]
    d = sc["diff_rbar_vs_rule_b"]
    rows.append(("C.7", "At Opus's four pilot slots, medium is within 0.08 of the high-effort reference",
                 "; ".join(f"{r.role} {r.medium_rbar:.3f} vs {r.high_rbar_rule_b:.3f}" for r in sc.itertuples())
                 + "; the writer slot has no score of its own",
                 "held" if (d.abs() <= 0.08).all() else "refuted",
                 "scored on the three slots with a score; the baseline is within 0.08 by under 0.01"))
    ratio = e["medium_cost_usd"].mean() / e["high_cost_rule_b"].mean()
    ratio_a = e["medium_cost_usd"].mean() / e["high_cost_rule_a"].mean()
    rows.append(("C.8", "Opus's cost per trial at medium is at most two thirds of high, averaged over the four slots",
                 f"ratio {ratio:.2f} against the rule (b) references, {ratio_a:.2f} against rule (a)",
                 "held" if max(ratio, ratio_a) <= 2 / 3 else "refuted", ""))
    return pd.DataFrame(rows, columns=["id", "prediction", "outcome", "score", "note"])


def figure(g, pp, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    col = {"A": "#2a78d6", "B": "#eb6834", "C": "#1baf7a"}
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), sharey=True)
    for ax, xkey, title in ((axes[0], "allowance", "against the allowance"),
                            (axes[1], "bytes_written", "against bytes written")):
        for arm in "ABC":
            d = g[(g.arm == arm) & g["size"].isin(["4096", "32768", "262144"])]
            x = d["size"].astype(int) if xkey == "allowance" else d["bytes_written"]
            ax.plot(x, d["rbar"], color=col[arm], lw=2, marker="o", ms=8, label=f"arm {arm}")
            ax.axhline(d["head_uni_v2"].iloc[0], color=col[arm], lw=1, ls="--")
            ax.annotate(f"{arm}", (list(x)[-1], list(d["rbar"])[-1]), xytext=(6, 0), textcoords="offset points",
                        va="center", color="#333333", fontsize=9)
        if xkey == "bytes_written":
            o = pp[pp["role"] == "predictor"]
            for r in o.itertuples():
                ax.plot(r.bytes_written, r.rbar_rule_b, marker="s", ms=8, color="#999999", ls="none")
        ax.set_xscale("log", base=2)
        ax.set_title(title, fontsize=10)
        ax.set_xlabel("bytes (log scale)")
        ax.grid(axis="y", color="#e5e5e5", lw=0.8)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    axes[0].set_ylabel("mean Pearson r over 50 genes, 500 scored spots")
    axes[0].legend(frameon=False, fontsize=9, loc="lower right")
    fig.text(0.01, 0.01, "Opus 5.5, medium effort, one trial per point. Dashed lines: uni_v2 benchmark head per arm. "
             "Grey squares: Haiku and Sonnet arm B pilot predictors at high effort.", fontsize=8, color="#555555")
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(path, dpi=150)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    m, comp, pm, proj, ref = load()
    g = grid(m, comp)
    g.to_csv(os.path.join(OUT, "grid.csv"), index=False)
    bstar(g).to_csv(os.path.join(OUT, "bstar.csv"), index=False)
    arm_diffs(g).to_csv(os.path.join(OUT, "arm_differences.csv"), index=False)
    e = effort(m, ref, pm)
    e.to_csv(os.path.join(OUT, "effort.csv"), index=False)
    pp = pilot_points(ref, pm)
    pp.to_csv(os.path.join(OUT, "pilot_reference_points.csv"), index=False)
    cr, ct = costs(m, proj)
    cr.to_csv(os.path.join(OUT, "cost_by_role.csv"), index=False)
    ct.to_csv(os.path.join(OUT, "cost_totals.csv"), index=False)
    scan_counts(m).to_csv(os.path.join(OUT, "scan_counts.csv"), index=False)
    tags(m, pm).to_csv(os.path.join(OUT, "cheatsheet_tags.csv"), index=False)
    predictions(g, e).to_csv(os.path.join(OUT, "predictions.csv"), index=False)
    figure(g, pp, os.path.join(OUT, "rbar_vs_bytes.png"))
    v = {(r.arm, r.size): r.rbar for r in g.itertuples()}
    hc = g[g.arm == "C"]["head_uni_v2"].iloc[0]
    cfin = [v[("C", s)] for s in ("4096", "32768", "262144")]
    sc = e[e["role"] != "writer"]
    pw = pm[(pm["role"] == "writer") & (pm["status"] == "done")]["bytes_written"]
    hv = {
        "C_gain_4096_over_baseline": v[("C", "4096")] - v[("C", "0")],
        "C_head_minus_262144": hc - v[("C", "262144")],
        "C_head_minus_lowest_finite": hc - min(cfin),
        "B_minus_C_4096_abs": abs(v[("B", "4096")] - v[("C", "4096")]),
        "medium_minus_high_abs_min": sc["diff_rbar_vs_rule_b"].abs().min(),
        "medium_minus_high_abs_max": sc["diff_rbar_vs_rule_b"].abs().max(),
        "medium_over_high_cost_mean_ratio_rule_b": e["medium_cost_usd"].mean() / e["high_cost_rule_b"].mean(),
        "medium_over_high_cost_mean_ratio_rule_a": e["medium_cost_usd"].mean() / e["high_cost_rule_a"].mean(),
        "pilot_writer_bytes_min": pw.min(), "pilot_writer_bytes_max": pw.max(),
        "prediction_rows": 14 * 500 * 50,
    }
    pd.DataFrame({"name": list(hv), "value": list(hv.values())}).to_csv(os.path.join(OUT, "headline_values.csv"), index=False)
    print("written to", OUT)
