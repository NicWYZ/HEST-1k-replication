#!/usr/bin/env python
"""Round 5 W2 part 2, item 1: build the released census pipeline's input on Longleaf.

Runs the released download_acs_ca_pums.main() unmodified (commit d1a69f4a). The only thing set from
outside is the module attribute OUT_PATH, so that the output goes under this job's directory and not
into the read-only code clone. The released main() reads folktables' cache_dir = OUT_PATH.parent /
folktables_cache. That directory is a real directory here holding one symlink to the raw California
person file, which is what folktables looks for (2018/1-Year/psam_p06.csv). The raw file exists, so
folktables does not download; if it were missing the download would land in this job's directory and
the job asserts afterwards that the cache holds only the symlink.
No data are downloaded.
"""
import hashlib, importlib.util, json, os, sys
import round5_conf_io as IO

RAW = "/work/users/w/e/weiyang/hest_replication/results/round4/ppi/Q0_setup/acs_pums2018"
GHCP = "/work/users/w/e/weiyang/hest_code/ghcp_code"
OUT = sys.argv[1]


def md5f(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def main():
    os.makedirs(OUT, exist_ok=True)
    IO.stamp(OUT, "round5-conformal W2 part2", "census input built from raw 2018 person file with released download_acs_ca_pums.main()")
    man = json.load(open(f"{RAW}/raw_manifest.json"))
    ent = [e for e in (man if isinstance(man, list) else man.get("files", man.get("entries", []))) if e.get("fips") == "06"]
    assert len(ent) == 1, "manifest entry for California not found"
    src = f"{RAW}/raw/2018/1-Year/psam_p06.csv"
    m_src = md5f(src)
    print("raw psam_p06 md5", m_src, "manifest", ent[0]["md5"], flush=True)
    assert m_src == ent[0]["md5"], "raw California file does not match raw_manifest.json"
    data = os.path.join(OUT, "data")
    cache = os.path.join(data, "folktables_cache", "2018", "1-Year")
    os.makedirs(cache, exist_ok=True)
    link = os.path.join(cache, "psam_p06.csv")
    if not os.path.islink(link):
        os.symlink(src, link)
    spec = importlib.util.spec_from_file_location("download_acs_ca_pums", f"{GHCP}/real_data/acs/download_acs_ca_pums.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    from pathlib import Path
    mod.OUT_PATH = Path(data) / "acs_data_all50states.csv"
    mod.main()
    left = sorted(os.listdir(cache))
    assert left == ["psam_p06.csv"], f"cache holds extra files {left}"
    out = str(mod.OUT_PATH)
    import pandas as pd
    n = len(pd.read_csv(out))
    m_out = md5f(out)
    print("input rows", n, "md5", m_out, flush=True)
    res = dict(rows=n, md5=m_out, raw_md5=m_src, manifest_md5=ent[0]["md5"], path=out,
               released_script_md5=md5f(f"{GHCP}/real_data/acs/download_acs_ca_pums.py"),
               data_processing_md5=md5f(f"{GHCP}/real_data/acs/data_processing.py"))
    json.dump(res, open(os.path.join(OUT, "census_input_record.json"), "w"), indent=1)
    IO.write_provenance(OUT, "W2p2_input", os.path.abspath(__file__), {"raw": src, "released_script": "download_acs_ca_pums.main()"},
                        extra={k: v for k, v in res.items()})


main()
