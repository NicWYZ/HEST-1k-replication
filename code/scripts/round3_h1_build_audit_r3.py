"""Build the round-3 donor audit file, results/round3/D3_audit/donor_audit_r3.csv.

Instruction: docs/decisions/round3_A3_decisions.md section 2.1, transcribed in
docs/round3_execution_plan.md section 13.2 item 1, with the flagged point of section 13.10 item 2.

Rule, applied literally:
  * the 72 benchmark rows of results/round2/R5b_audit/donor_audit.csv, unchanged except IDC, where
    TENX95 and TENX99 receive distinct donor_id values (D3's) and donor_label_status 'verified',
    citing D3's rows;
  * then the 76 rows of results/round3/D3_audit/donor_lab_audit_ext.csv appended.
Every row carries `row_origin` ('benchmark_r2' or 'expansion_d3'). 28 samples appear under both
origins, and their two rows disagree; both are kept and no status is chosen between them. The
disagreements are listed in donor_audit_r3_conflicts.csv. Stages that group benchmark tasks use the
benchmark_r2 rows; stages that group expansion sets use the expansion_d3 rows.

The source files are read, never written. donor_audit.csv stays frozen.

Usage (repository root):  python code/scripts/round3_h1_build_audit_r3.py
"""
from pathlib import Path

import pandas as pd

R2 = Path("results/round2/R5b_audit/donor_audit.csv")
D3 = Path("results/round3/D3_audit/donor_lab_audit_ext.csv")
OUT = Path("results/round3/D3_audit/donor_audit_r3.csv")
CONF = Path("results/round3/D3_audit/donor_audit_r3_conflicts.csv")
IDC_FIX = ["TENX95", "TENX99"]
MEMO = "docs/decisions/round3_A3_decisions.md section 2.1"

b = pd.read_csv(R2, dtype=str, keep_default_na=False)
e = pd.read_csv(D3, dtype=str, keep_default_na=False)
assert len(b) == 72 and b.sample_id.is_unique, (len(b), b.sample_id.duplicated().sum())
assert len(e) == 76 and e.sample_id.is_unique, (len(e), e.sample_id.duplicated().sum())

b = b.copy()
d3 = e.set_index("sample_id")
for sid in IDC_FIX:
    i = b.index[(b.sample_id == sid) & (b.task == "IDC")]
    assert len(i) == 1, sid
    i = i[0]
    old_id, old_status = b.at[i, "donor_id"], b.at[i, "donor_label_status"]
    b.at[i, "donor_id"] = d3.at[sid, "donor_id"]
    b.at[i, "donor_label_status"] = "verified"
    b.at[i, "source_url"] = d3.at[sid, "source_url"]
    b.at[i, "donor_statement"] = d3.at[sid, "donor_statement"]
    b.at[i, "correction"] = (
        f"round 3: donor_id {old_id} -> {d3.at[sid, 'donor_id']}, status {old_status} -> verified, "
        f"per {MEMO}; evidence is D3's row for {sid} in {D3} (citation column there)")
assert b.loc[b.sample_id.isin(IDC_FIX), "donor_id"].nunique() == 2
assert b[b.task == "IDC"].donor_id.nunique() == 4, "IDC must be four distinct donors"

b.insert(0, "row_origin", "benchmark_r2")
e2 = e.copy()
e2.insert(0, "row_origin", "expansion_d3")
cols = list(b.columns) + [c for c in e2.columns if c not in b.columns]
out = pd.concat([b.reindex(columns=cols), e2.reindex(columns=cols)], ignore_index=True).fillna("")
assert len(out) == 148 and not out.duplicated(["row_origin", "sample_id"]).any()
OUT.write_text(out.to_csv(index=False))

both = sorted(set(b.sample_id) & set(e.sample_id))
rows = []
for sid in both:
    rb = out[(out.sample_id == sid) & (out.row_origin == "benchmark_r2")].iloc[0]
    rd = out[(out.sample_id == sid) & (out.row_origin == "expansion_d3")].iloc[0]
    rows.append({
        "sample_id": sid, "task": rb["task"], "set_name": rd["set_name"],
        "donor_id_benchmark_r2": rb["donor_id"], "donor_id_expansion_d3": rd["donor_id"],
        "status_benchmark_r2": rb["donor_label_status"], "status_expansion_d3": rd["donor_label_status"],
        "donor_id_differs": rb["donor_id"] != rd["donor_id"],
        "status_differs": rb["donor_label_status"] != rd["donor_label_status"],
        "resolution": "unresolved; both rows kept (docs/round3_execution_plan.md section 13.10 item 2)",
    })
conf = pd.DataFrame(rows)
CONF.write_text(conf.to_csv(index=False))
print(f"wrote {OUT} ({len(out)} rows: {len(b)} benchmark_r2 + {len(e2)} expansion_d3)")
print(f"wrote {CONF} ({len(conf)} samples under both origins; "
      f"{int(conf.status_differs.sum())} differ in status, {int(conf.donor_id_differs.sum())} in donor_id)")
