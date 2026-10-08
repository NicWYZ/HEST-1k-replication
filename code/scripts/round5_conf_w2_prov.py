#!/usr/bin/env python
"""Round 5, W2 part 1: write the stamp and PROVENANCE.txt of an output directory from the job.

Calls round5_conf_io.stamp (the longleaf-provenance format, frame id from R5CONF_FRAME_ID) and
round5_conf_io.write_provenance. Extra key=value pairs are recorded; --scripts lists staged scripts
whose md5 is recorded next to the main script's.
Usage: round5_conf_w2_prov.py --out DIR --stage NAME --main SCRIPT [--note TXT] [--scripts A,B]
         [--cfg JSON] [--stamp-only] [k=v ...]
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import round5_conf_io as IO5  # noqa: E402


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--stage", required=True)
    p.add_argument("--main", required=True)
    p.add_argument("--note", default="")
    p.add_argument("--scripts", default="")
    p.add_argument("--cfg", default="{}")
    p.add_argument("--stamp-only", action="store_true")
    p.add_argument("--ghcp-code", default="")
    a, rest = p.parse_known_args()
    IO5.stamp(a.out, "W2 part 1", a.note or a.stage)
    if a.stamp_only:
        return 0
    extra = dict(x.split("=", 1) for x in rest if "=" in x)
    for s in [x for x in a.scripts.split(",") if x]:
        extra[f"staged_md5_{os.path.basename(s)}"] = IO5.md5(s)
    if a.ghcp_code:
        extra["ghcp_commit"] = IO5.clone_head(a.ghcp_code)
        for f in ("code/marginal/run_section_3_1.py", "code/marginal/run_true_marginal_latent_intercept_rf_experiments.py",
                  "code/marginal/run_true_marginal_latent_intercept_experiments.py", "code/shared/dgp/experiments.py",
                  "methods/donor_hcp.py", "methods/sample_hcp.py", "scores.py"):
            extra["released_md5_" + f.replace("/", "_")] = IO5.md5(os.path.join(a.ghcp_code, f))
    extra["R5CONF_FRAME_ID"] = os.environ.get("R5CONF_FRAME_ID", "")
    IO5.write_provenance(a.out, a.stage, a.main, json.loads(a.cfg), extra=extra)
    return 0


if __name__ == "__main__":
    sys.exit(main())
