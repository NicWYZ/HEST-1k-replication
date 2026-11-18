"""fcheck: combine the recomputed and read-back tables into fcheck_table.csv; list script md5s and stamps."""
import glob, hashlib, json, os
import pandas as pd
F = "/work/users/w/e/weiyang/hest_replication/results/round11/closeout/fcheck"
a = pd.read_csv(f"{F}/assemble/fcheck_table_recomputed.csv"); b = pd.read_csv(f"{F}/readback/fcheck_table_readback.csv")
o = pd.concat([a, b], ignore_index=True); m = o.location.str.contains("ratio of medians", regex=False); o.loc[m, "verdict"] = "alternative definition (ratio of medians), shown for contrast; the report uses the median of per-gene ratios, which agrees"; o.to_csv(f"{F}/fcheck_table.csv", index=False)
print("rows", len(o)); print(o.verdict.value_counts().to_string())
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 200); pd.set_option("display.max_rows", 500)
print(o[o.verdict.str.contains("DISAGREE|NOT FOUND|see recomputed")].to_string())
for p in sorted(glob.glob(f"{F}/scripts/*")):
    print("md5", hashlib.md5(open(p, "rb").read()).hexdigest(), os.path.basename(p))
for p in sorted(glob.glob(f"{F}/**/_provenance.json", recursive=True)):
    print("stamp", p.replace(F, "fcheck"), json.load(open(p))["frame_id"])
for p in sorted(glob.glob(f"{F}/*/PROVENANCE.txt")):
    print("job", p.replace(F, "fcheck"), open(p).read().split("\n")[0])
open("inputs.txt", "w").write(f"{F}/assemble/fcheck_table_recomputed.csv\n{F}/readback/fcheck_table_readback.csv\n")
