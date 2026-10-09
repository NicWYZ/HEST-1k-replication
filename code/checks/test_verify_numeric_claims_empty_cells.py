"""Fixture test for verify_numeric_claims: a text column with an empty cell.

Under pandas 3 a missing cell in a string column stays a float NaN after
astype(str), which used to raise a TypeError and mark the whole file unreadable.
Run from the repository root: python3 code/checks/test_verify_numeric_claims_empty_cells.py
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import verify_numeric_claims as v  # noqa: E402


def main():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "fixture.csv")
        with open(path, "w") as f:
            f.write("task,note,value\n")
            f.write("a,range 0.25 to 0.40,1.5\n")
            f.write("b,,2.5\n")
        fv = v._file_values_uncached(path)
        tagged = [x for _, x in fv.tagged]
        assert 0.25 in tagged and 0.40 in tagged, "numbers in the text column were not read"
    print("ok: a text column with an empty cell is read")


if __name__ == "__main__":
    main()
