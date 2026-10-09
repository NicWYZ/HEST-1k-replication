"""Interval 3 ownership stamps (plan 8.3 item 1): every _provenance.json under
results/round5/ppi/E4b_rejective/<unit dir>/ against the frame id assigned to that unit in
e4b_assigned_frame_ids.csv. The lead's own runs (tests, pilot) carry the lead's id. Writes
results/round5/ppi/E4b_rejective/e4b_stamp_check.csv and exits non-zero on any mismatch."""
import glob
import json
import sys

import pandas as pd

R = "results/round5/ppi/E4b_rejective"
LEAD = "e5d5217d-4382-43ce-9cdc-7b08d2cba953"


def main():
    a = pd.read_csv(f"{R}/e4b_assigned_frame_ids.csv").set_index("unit_dir")["frame_id"].to_dict()
    rows = []
    for f in sorted(glob.glob(f"{R}/**/_provenance.json", recursive=True)):
        unit = f[len(R) + 1:].split("/")[0]
        fid = json.load(open(f)).get("frame_id")
        assigned = a.get(unit, LEAD)
        rows.append(dict(unit_dir=unit, path=f, frame_id=fid, assigned=assigned, match=fid == assigned))
    d = pd.DataFrame(rows)
    d.to_csv(f"{R}/e4b_stamp_check.csv", index=False)
    print(d.groupby(["unit_dir", "match"]).size().to_string())
    return 0 if d["match"].all() else 1


if __name__ == "__main__":
    sys.exit(main())
