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

Reading items (section 13.4 item 4) are recorded ONLY through this script, never by editing
donor_audit_r3.csv by hand: they go into results/round3/D3_audit/donor_audit_r3_overrides.csv
(columns sample_id,row_origin,column,value,citation,note), which this script applies to the
assembled frame before it is written. Each override addresses exactly one (sample_id, row_origin)
row and sets one cell to `value`. The Housekeeping track owns only the donor_label_status, citation
and notes columns of this file, so the script enforces that as an allowlist -- an override naming
any other column is refused, which covers donor_id, row_origin and sample_id by construction and
also every column the memo did not think to name -- and refuses an override that does not match
exactly one row.

The source files are read, never written. donor_audit.csv stays frozen.

Usage (repository root):  python code/scripts/round3_h1_build_audit_r3.py
"""
from pathlib import Path

import pandas as pd

R2 = Path("results/round2/R5b_audit/donor_audit.csv")
D3 = Path("results/round3/D3_audit/donor_lab_audit_ext.csv")
OUT = Path("results/round3/D3_audit/donor_audit_r3.csv")
CONF = Path("results/round3/D3_audit/donor_audit_r3_conflicts.csv")
OVR = Path("results/round3/D3_audit/donor_audit_r3_overrides.csv")
PROTECTED = ("donor_id", "row_origin", "sample_id")
# The Housekeeping track owns these three columns of this file and no others
# (docs/round3_execution_plan.md section 13.9, the track table). PROTECTED is the subset the memo
# names explicitly; WRITABLE is the rule, and it is the one enforced, because "not donor_id" is
# weaker than "only these three" and the docstring claims the stronger thing.
WRITABLE = ("donor_label_status", "citation", "notes")
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

# ---- section 13.4 item 4: apply the reading-item overrides, if any ------------------------
n_ovr = 0
if OVR.exists():
    o = pd.read_csv(OVR, dtype=str, keep_default_na=False)
    need = ["sample_id", "row_origin", "column", "value", "citation", "note"]
    assert list(o.columns) == need, list(o.columns)
    assert len(o), "overrides file is present but empty"
    bad = sorted(set(o.column) & set(PROTECTED))
    assert not bad, f"override may not touch {bad}: donor_id, row_origin and sample_id are fixed"
    unknown = sorted(set(o.column) - set(out.columns))
    assert not unknown, f"override names columns that do not exist: {unknown}"
    outside = sorted(set(o.column) - set(WRITABLE))
    assert not outside, (f"override names {outside}, outside the columns this track owns "
                         f"{list(WRITABLE)} (docs/round3_execution_plan.md section 13.9)")
    assert not set(WRITABLE) & set(PROTECTED), "WRITABLE and PROTECTED must not overlap"
    assert not o.duplicated(["sample_id", "row_origin", "column"]).any(), "duplicate override key"
    assert (o.note.str.len() > 0).all() and (o.citation.str.len() > 0).all(), \
        "every override carries a citation and a note"
    for _, r in o.iterrows():
        i = out.index[(out.sample_id == r.sample_id) & (out.row_origin == r.row_origin)]
        assert len(i) == 1, (r.sample_id, r.row_origin, len(i))
        out.at[i[0], r.column] = r.value
        n_ovr += 1
    # the protected columns are fixed by construction; assert it of the written frame too
    assert out.donor_id.tolist() == pd.concat(
        [b.reindex(columns=cols), e2.reindex(columns=cols)], ignore_index=True
    ).fillna("").donor_id.tolist(), "an override changed donor_id"

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
print(f"wrote {OUT} ({len(out)} rows: {len(b)} benchmark_r2 + {len(e2)} expansion_d3; "
      f"{n_ovr} override cells applied from {OVR if OVR.exists() else 'no overrides file'})")
print(f"wrote {CONF} ({len(conf)} samples under both origins; "
      f"{int(conf.status_differs.sum())} differ in status, {int(conf.donor_id_differs.sum())} in donor_id)")
