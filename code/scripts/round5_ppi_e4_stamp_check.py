"""Interval 2 ownership stamps: every _provenance.json under E3a_crossfit, E3_twolevel and E4_selection
against the frame id assigned to its unit. Writes results/round5/ppi/E4_selection/e4_stamp_check.csv."""
import glob
import json

import pandas as pd

R = "results/round5/ppi"
LEAD = "e5d5217d-4382-43ce-9cdc-7b08d2cba953"
ASSIGNED = {
    ("E3a_crossfit", "sim"): "8e4c25dc-7878-42d0-a510-40ed4f9f09ab",
    ("E3a_crossfit", "masking"): "e0a5318b-d655-4447-bae7-1ebf9a13a8ba",
    ("E3_twolevel", "sim"): "36b341f6-6721-445f-96c9-728b95656e50",
    ("E3_twolevel", "ACS_CA_PUMA"): "86eb9455-9252-46aa-bb5d-499c479e998c",
    ("E3_twolevel", "ACS_STATES"): "6d4efab2-c8da-40d8-abe0-1c235cc0fe33",
    ("E3_twolevel", "INDIANA_KIDNEY"): "a15bd597-4032-4f15-bbfe-d9a6ffd0f7a0",
    ("E3_twolevel", "CCRCC"): "041af7f3-ba1d-4e51-8896-41f176a1eff3",
    ("E3_twolevel", "CCRCC_merged"): "46478f5b-a377-4727-bba7-0b8d8e6a14c2",
    ("E3_twolevel", "LUNG_XENIUM"): "0338b880-cf9f-4973-82b4-4574228837f1",
    ("E4_selection", "sim"): "7b2177fb-1911-42e8-a26a-d044bb18743a",
    ("E4_selection", "CCRCC"): "90692378-8750-4a5a-9138-5a6e4303b86e",
    ("E4_selection", "CCRCC_merged"): "8c024daa-3eaf-4b5e-8406-fc169826f5a4",
    ("E4_selection", "INDIANA_KIDNEY"): "808b4d85-6ba7-40d5-baf9-0405f52f230e",
    ("E4_selection", "LUNG_XENIUM"): "a05b21b6-9d7e-49cb-89f2-e2ebdcf12c9d",
    ("E4_selection", "ACS_STATES"): "1ccf1e77-fb81-4888-9583-6c4e01dd15a5",
    ("E4_selection", "ACS_CA_PUMA"): "9df81990-4c4b-4816-a7eb-d1cac6f47af3",
}


def main():
    rows = []
    for f in sorted(glob.glob(f"{R}/E3a_crossfit/**/_provenance.json", recursive=True)
                    + glob.glob(f"{R}/E3_twolevel/**/_provenance.json", recursive=True)
                    + glob.glob(f"{R}/E4_selection/**/_provenance.json", recursive=True)):
        parts = f[len(R) + 1:].split("/")
        stage, unit = parts[0], parts[1]
        fid = json.load(open(f)).get("frame_id")
        if "_inclusion" in f or "r5e3sim_final" in f:
            assigned, kind = LEAD, "lead run"
        elif "_superseded" in f:
            assigned, kind = ASSIGNED.get((stage, unit)), "superseded run, unit reassigned on rerun"
        else:
            assigned, kind = ASSIGNED.get((stage, unit)), "unit"
        rows.append(dict(stage=stage, unit=unit, path=f, frame_id=fid, assigned=assigned, kind=kind,
                         match=fid == assigned, stamped_with_lead=fid == LEAD))
    d = pd.DataFrame(rows)
    d.to_csv(f"{R}/E4_selection/e4_stamp_check.csv", index=False)
    print(d.groupby(["stage", "kind", "match", "stamped_with_lead"]).size().to_string())
    print(d[(~d["match"]) & (d["kind"] == "unit")].groupby(["stage", "unit", "frame_id"]).size().to_string())


if __name__ == "__main__":
    main()
