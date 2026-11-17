"""b1 helpers: md5 ledger of every input a b1 script reads. No numbers are computed here."""
import hashlib, os

R = "/work/users/w/e/weiyang/hest_replication/results"
F = R + "/round10/final_runs"
CLONE = "/work/users/w/e/weiyang/hest_code/round11-closeout"

_read = []


def md5(p, chunk=1 << 22):
    h = hashlib.md5()
    with open(p, "rb") as fh:
        while True:
            b = fh.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def note_input(p):
    if p not in _read:
        _read.append(p)
    return p


def write_inputs(out):
    with open(os.path.join(out, "inputs_md5.txt"), "w") as fh:
        for p in _read:
            fh.write(f"{md5(p)}  {p}\n")
