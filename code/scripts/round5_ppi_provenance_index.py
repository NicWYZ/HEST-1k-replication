#!/usr/bin/env python
"""Round 5 PPI track: provenance index (plan section 7.3 item 6, memo section 4 item 6).

One row per job and script over every E0, E1, E2, E3a, E3 and E4 job.

Inputs
  results/round5/ppi/provenance_raw/*.txt   one Longleaf PROVENANCE.txt record per file, named
                                            <job id>__<path tag>.txt; the first line "#source: <path>"
                                            gives the file on Longleaf the record was read from.
  results/round5/ppi/**/PROVENANCE.txt      local copies (E3a/E3/E4 came back from Longleaf; the
                                            local simulation runs have platform local).
  results/round5/ppi/{r5ppi_slurm_jobs.csv,unit_job_ledgers/*.csv,**/job_ledger*.csv}
                                            job ledgers, used only to list jobs without a record.
Outputs
  results/round5/ppi/provenance_index.csv
  results/round5/ppi/provenance_index_failures.csv   rows failing check 1 or check 2

Checks (against the hash of the branch tip, recorded in head_tested)
  check 1  the recorded commit is an ancestor of (or equal to) head_tested
  check 2  the record's md5 equals the md5 of `git show <recorded_commit>:<script_path>`;
           on failure md5_matches_commits lists the commits of the branch, from
           `git log --format=%H <branch> -- <path>`, at which the script has that md5.

Record formats
  new  (E3a onward): platform, snapshot_commit, "scripts_executed (md5, path relative to snapshot)".
  old  (E0 to E2):   stage first, script_md5 with absolute paths on Longleaf, code_clone_HEAD and
                     uploaded_scripts_local_commit (and, from E2, e2_scripts_local_commit).
       Recorded commit of an old record: the commit the script was uploaded from
       (uploaded_e2_scripts_local_commit / e2_scripts_local_commit for round5_ppi_e2_* scripts when
       present, else uploaded_scripts_local_commit); for scripts read from the Longleaf clone
       (path under hest_code/round5-ppi/code/scripts) and for records with no upload commit,
       code_clone_HEAD. A clone HEAD that was unreadable (git off the path) is noted; the
       clone HEAD is also tested (check1_clone_head) but does not enter the failure file.
       Old records give paths on Longleaf; the repo path is the file of that basename at the
       recorded commit (code/scripts/ preferred).
"""
import argparse, csv, glob, hashlib, os, re, subprocess, sys
from collections import defaultdict

STAGES = ("E0", "E1", "E2", "E3a", "E3", "E4")
_git_cache = {}


def git(repo, *args, text=True):
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=text)
    return r


def blob_md5(repo, commit, path):
    key = (commit, path)
    if key not in _git_cache:
        r = git(repo, "show", f"{commit}:{path}", text=False)
        _git_cache[key] = hashlib.md5(r.stdout).hexdigest() if r.returncode == 0 else None
    return _git_cache[key]


_tree_cache = {}


def tree_files(repo, commit):
    if commit not in _tree_cache:
        r = git(repo, "ls-tree", "-r", "--name-only", commit)
        _tree_cache[commit] = r.stdout.split("\n") if r.returncode == 0 else []
    return _tree_cache[commit]


_blob_index = {}


def md5_blob_index(repo, branch):
    """md5 -> sorted repo paths, over every version of every file under code/ on the branch."""
    if not _blob_index:
        out = git(repo, "rev-list", "--objects", branch, "--", "code").stdout.splitlines()
        shas = {}
        for l in out:
            if " " in l:
                sha, path = l.split(" ", 1)
                shas.setdefault(sha, set()).add(path)
        for sha, paths in shas.items():
            b = git(repo, "cat-file", "blob", sha, text=False)
            if b.returncode == 0:
                _blob_index.setdefault(hashlib.md5(b.stdout).hexdigest(), set()).update(paths)
    return _blob_index


def full_hash(repo, c):
    if not c or not re.fullmatch(r"[0-9a-f]{7,40}", c):
        return None
    r = git(repo, "rev-parse", "--verify", "--quiet", c + "^{commit}")
    return r.stdout.strip() or None


def split_records(text):
    text = text.replace("\r", "")
    first = next((l for l in text.splitlines() if l.strip()), "")
    pat = r"(?m)^(?=platform:)" if first.startswith("platform:") else r"(?m)^(?=stage:)"
    return [p for p in re.split(pat, text) if p.strip()]


def parse_record(text):
    rec = {"scripts": []}
    mode = None
    for line in text.splitlines():
        if line.startswith("#source:"):
            rec["source"] = line.split(":", 1)[1].strip()
            continue
        m = re.match(r"^(\w[\w ]*?)(?: \(.*\))?:\s?(.*)$", line)
        if m and not line.startswith(" "):
            k, v = m.group(1), m.group(2).strip()
            mode = k if k in ("script_md5", "scripts_executed", "inputs") else None
            if k in ("script_md5", "scripts_executed", "inputs"):
                continue
            rec.setdefault(k, v)
            continue
        if mode in ("script_md5", "scripts_executed"):
            m2 = re.match(r"^\s+([0-9a-f]{32})\s+(\S.*)$", line)
            if m2:
                rec["scripts"].append((m2.group(1), m2.group(2).strip()))
    rec["fmt"] = "new" if "snapshot_commit" in rec else "old"
    return rec


def norm_stage(s, relpath):
    m = re.match(r"^(E\d+a?)(?![0-9A-Za-z])", s or "")
    if m:
        return m.group(1)
    m = re.search(r"(?:^|/)(E\d+a?)_", relpath)
    return m.group(1) if m else (s or "")


def build(repo, ppi, branch, out_index, out_fail):
    head = git(repo, "rev-parse", branch).stdout.strip()
    assert head, "cannot resolve " + branch
    raw_dir = os.path.join(ppi, "provenance_raw")
    sources = []  # (rec, file_for_index, kind)
    for f in sorted(glob.glob(os.path.join(raw_dir, "*.txt"))):
        txt = open(f).read()
        src = ""
        if txt.startswith("#source:"):
            first, txt = txt.split("\n", 1)
            src = first.split(":", 1)[1].strip()
        for part in split_records(txt):
            r = parse_record(part)
            r["longleaf_path"] = src
            sources.append((r, os.path.relpath(f, repo), "longleaf"))
    for f in sorted(glob.glob(os.path.join(ppi, "**", "PROVENANCE*.txt"), recursive=True)):
        for part in split_records(open(f).read()):
            sources.append((parse_record(part), os.path.relpath(f, repo), "localcopy"))

    rows, keys = [], {}
    for rec, pfile, kind in sources:
        jid = rec.get("slurm_job_id")
        local_dir = os.path.relpath(os.path.dirname(os.path.join(repo, pfile)), ppi)
        if kind == "longleaf":
            src_rel = rec["longleaf_path"].split("results/round5/ppi/")[-1]
            tdir = os.path.dirname(src_rel)
        else:
            tdir = local_dir
        plat_field = rec.get("platform", "")
        platform = "local" if plat_field.startswith("local") else "Longleaf"
        if not jid:
            assert platform == "local", pfile
            jid = "local:" + tdir
        stage = norm_stage(rec.get("stage", ""), tdir)
        unit = rec.get("unit") or tdir
        notes = []
        if "_superseded" in tdir:
            notes.append("superseded run")
        if rec.get("status") and rec["status"] != "COMPLETED":
            notes.append("status " + rec["status"])
        if rec.get("exit_code_of_run") not in (None, "0") and "exit_code_of_run" in rec:
            notes.append("exit_code_of_run " + rec["exit_code_of_run"])
        if rec["fmt"] == "old":
            notes.append("old-format record (code_clone_HEAD / uploaded_scripts_local_commit)")
        if "slurm_job_id_note" in rec:
            notes.append("slurm_job_id_note: " + rec["slurm_job_id_note"])
        clone_head = rec.get("code_clone_HEAD", "")
        clone_full = full_hash(repo, clone_head) if clone_head else None
        if rec["fmt"] == "old" and clone_head and not clone_full:
            notes.append("code_clone_HEAD unreadable (git off the path in the job)")
        for md5, spath in rec["scripts"]:
            base = os.path.basename(spath)
            if rec["fmt"] == "new":
                rc_raw, rpath = rec["snapshot_commit"], spath
            else:
                e2c = rec.get("uploaded_e2_scripts_local_commit") or rec.get("e2_scripts_local_commit")
                upc = rec.get("uploaded_scripts_local_commit")
                hs = re.findall(r"[0-9a-f]{40}", upc or "")
                if len(hs) == 2:
                    if re.search(r"\(E2 scripts\);", upc):      # "H1 (E2 scripts); H2 (common, estimator)"
                        e2c, upc = hs[0], hs[1]
                    else:                                        # "H1 (E2 scripts: H2)"
                        upc, e2c = hs[0], hs[1]
                elif hs:
                    upc = hs[0]
                if "/hest_code/round5-ppi/code/scripts/" in spath:
                    rc_raw, why = clone_head, "script read from the Longleaf clone"
                elif base.startswith("round5_ppi_e2_") and e2c:
                    rc_raw, why = e2c, ""
                elif upc:
                    rc_raw, why = upc, ""
                else:
                    rc_raw, why = clone_head, "no upload commit recorded, clone HEAD used"
                notes_row = [why] if why else []
                rpath = None
            rc = full_hash(repo, rc_raw) if rc_raw else None
            rn = list(notes) + (notes_row if rec["fmt"] == "old" else [])
            if rec["fmt"] == "old":
                if len(re.findall(r"[0-9a-f]{40}", rec.get("uploaded_scripts_local_commit", ""))) == 2:
                    rn.append("upload-commit field gives two commits (annotated by script group): " + rec["uploaded_scripts_local_commit"])
                cands = [p for p in tree_files(repo, rc) if os.path.basename(p) == base] if rc else []
                pref = [p for p in cands if p.startswith("code/scripts/")]
                cands = pref or cands
                if len(cands) == 1:
                    rpath = cands[0]
                elif cands:
                    rpath = cands[0]
                    rn.append("ambiguous path at recorded commit; first used")
                else:
                    rpath = spath.split("results/round5/ppi/")[-1] if "results/round5/ppi/" in spath else base
                    rn.append("not a repository file at the recorded commit (ad hoc script of the lead, path as recorded on Longleaf)")
            c1 = bool(rc) and git(repo, "merge-base", "--is-ancestor", rc, head).returncode == 0
            if not rc:
                rn.append("recorded commit not resolvable in this repository (%s)" % rc_raw)
            blob = blob_md5(repo, rc, rpath) if rc else None
            c2 = blob == md5
            mm = ""
            if not c2:
                if blob is None:
                    rn.append("script absent at recorded commit")
                else:
                    rn.append("md5 at recorded commit differs")
                if not rpath.startswith("code/"):
                    same = sorted(md5_blob_index(repo, branch).get(md5, []))
                    if same:
                        rn.append("md5 identical to a version of " + ", ".join(same) + " on the branch")
                hist = git(repo, "log", "--format=%H", branch, "--", rpath).stdout.split()
                mm = ";".join(h for h in hist if blob_md5(repo, h, rpath) == md5)
            c1h = ""
            if rec["fmt"] == "old" and clone_full:
                c1h = git(repo, "merge-base", "--is-ancestor", clone_full, head).returncode == 0
            row = dict(job_id=jid, platform=platform, stage=stage, unit=unit, script_path=rpath, md5=md5,
                       recorded_commit=rc or rc_raw or "", provenance_file=pfile, head_tested=head,
                       check1_ancestor=c1, check2_md5=c2, md5_matches_commits=mm,
                       clone_head_recorded=clone_full or clone_head, check1_clone_head=c1h,
                       stage_recorded=rec.get("stage", ""), record_format=rec["fmt"],
                       note="; ".join(rn))
            k = (jid, rpath, md5, row["recorded_commit"])
            if k in keys:
                kept = keys[k]
                kept["_dups"].append(pfile)
                continue
            row["_dups"] = []
            keys[k] = row
            rows.append(row)
    for r in rows:
        extra = r.pop("_dups")
        if extra:
            r["note"] = (r["note"] + "; " if r["note"] else "") + "same record also read at " + " | ".join(extra)
    cols = ["job_id", "platform", "stage", "unit", "script_path", "md5", "recorded_commit", "provenance_file",
            "head_tested", "check1_ancestor", "check2_md5", "md5_matches_commits", "note",
            "clone_head_recorded", "check1_clone_head", "stage_recorded", "record_format"]
    # memo section 2 and plan 7.3 item 6 describe three records naming 8b879bb for the levelcheck and
    # report_extra scripts; the records themselves name one commit per job (E4 report escalation 7)
    memo = {"4203320": "8b879bb", "4203540": "4f52b0c", "4203742": "f75950f"}
    for r in rows:
        if r["job_id"] in memo:
            r["note"] = (r["note"] + "; " if r["note"] else "") + (
                "memo-named record: the memo lists the E2 diag records as naming 8b879bb for levelcheck and "
                f"report_extra; this job's own record names {memo[r['job_id']]} (E4 report escalation 7)")
    order = {s: i for i, s in enumerate(STAGES)}
    rows.sort(key=lambda r: (order.get(r["stage"], 99), r["platform"], r["job_id"], r["unit"], r["script_path"]))
    with open(out_index, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
        w.writeheader(); w.writerows(rows)
    fails = [r for r in rows if not (r["check1_ancestor"] and r["check2_md5"])]
    with open(out_fail, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
        w.writeheader(); w.writerows(fails)
    return rows, fails, head


def ledger_job_ids(ppi):
    files = [os.path.join(ppi, "r5ppi_slurm_jobs.csv")]
    files += glob.glob(os.path.join(ppi, "unit_job_ledgers", "*.csv"))
    files += glob.glob(os.path.join(ppi, "**", "job_ledger*.csv"), recursive=True)
    ids = defaultdict(set)
    for f in sorted(set(files)):
        for r in csv.DictReader(open(f)):
            j = (r.get("job_id") or "").strip()
            if j:
                ids[j].add(os.path.relpath(f, ppi) + " [" + (r.get("state") or "") + "]")
    return ids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--branch", default="round5-ppi")
    a = ap.parse_args()
    repo = os.path.abspath(a.repo)
    ppi = os.path.join(repo, "results/round5/ppi")
    rows, fails, head = build(repo, ppi, a.branch, os.path.join(ppi, "provenance_index.csv"),
                              os.path.join(ppi, "provenance_index_failures.csv"))
    jobs = {r["job_id"] for r in rows}
    print("head_tested", head, "rows", len(rows), "jobs", len(jobs), "failing", len(fails))
    raw = sorted(glob.glob(os.path.join(ppi, "provenance_raw", "*.txt")))
    summ = [("rows", len(rows)), ("jobs", len(jobs)),
            ("jobs_longleaf", len({r["job_id"] for r in rows if r["platform"].lower() == "longleaf"})),
            ("jobs_local", len({r["job_id"] for r in rows if r["platform"].lower() == "local"})),
            ("longleaf_records", len(raw)), ("longleaf_provenance_files", len({open(f).readline().strip() for f in raw})),
            ("rows_failing_check1", sum(1 for r in rows if not r["check1_ancestor"])),
            ("rows_failing_check2", sum(1 for r in rows if not r["check2_md5"])),
            ("records_naming_8b879bb", sum("8b879bb" in open(f).read() for f in raw))]
    with open(os.path.join(ppi, "provenance_index_summary.csv"), "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n"); w.writerow(["name", "value"]); w.writerows(summ)
    missing = {j: s for j, s in ledger_job_ids(ppi).items() if j not in jobs}
    for j, s in sorted(missing.items()):
        print("ledger job without provenance record:", j, sorted(s))


if __name__ == "__main__":
    main()
