#!/usr/bin/env python
"""Round 4, PPI track, stage Q0: data wrappers for the lung Xenium task and Xenium control features.

Stage: r4ppi_Q0, unit "lung wrapper" (docs/decisions/round4_ppi_track.md, "The lung task, as
delivered" and "Xenium control features").

round3_d4_sets.py is imported unchanged and is not edited. Its `load_set` asserts that each
sample's embedding-file barcodes are a subset of the expression barcodes and raises on NCBI865
(embedding file 2,143 rows, one barcode, 051x019, dropped in the task file). The lung reader here
removes `dropped_patch_barcodes` (top level of LUNG_XENIUM.json) from the embedding rows by
barcode first, and only then asserts the subset relation. `load_set` is never called on lung by
this module; `load_lung` is the drop-first counterpart and reuses `patched_barcodes` from round 3.

Where round3_d4_sets is found: directory in env R4PPI_CODE_DIR, else this file's directory.
"""
import importlib.util
import json
import os
import re
import sys

import anndata as ad
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_CODE = os.environ.get("R4PPI_CODE_DIR", _HERE)
CONTROL_PREFIXES = ("NegControl", "UnassignedCodeword", "BLANK")

_D4 = None


def d4():
    """round3_d4_sets, imported by path (it imports its own siblings by path as well)."""
    global _D4
    if _D4 is None:
        p = os.path.join(_CODE, "round3_d4_sets.py")
        if _CODE not in sys.path:
            sys.path.insert(0, _CODE)
        spec = importlib.util.spec_from_file_location("round3_d4_sets", p)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        _D4 = m
    return _D4


def read_task(path):
    with open(path) as f:
        return json.load(f)


def dropped_for(td, sid):
    """Barcodes to remove for `sid` (empty list when none). Top-level key of the task file."""
    return [str(b) for b in (td.get("dropped_patch_barcodes") or {}).get(sid, [])]


def expression_barcodes(td, sid):
    A = ad.read_h5ad(f"{d4().ROOT}/{td['paths']['adata'].format(sample_id=sid)}", backed="r")
    try:
        return set(map(str, A.obs_names))
    finally:
        A.file.close()


def read_patched(td, sid, enc, apply_drop=True):
    """(barcodes, X, xy, n_raw, n_removed) of the embedding file, drop list applied by barcode."""
    bc, X, xy = d4().patched_barcodes(td, sid, enc)
    n_raw = len(bc)
    drop = set(dropped_for(td, sid)) if apply_drop else set()
    keep = np.array([b not in drop for b in bc], dtype=bool)
    n_removed = int((~keep).sum())
    if apply_drop:
        assert n_removed == len(drop), (
            f"{sid}/{enc}: drop list has {len(drop)} barcodes, {n_removed} found in the embedding file")
    return [b for b, k in zip(bc, keep) if k], X[keep], xy[keep], n_raw, n_removed


def assert_subset(bc, expr_bc, sid):
    """The relation round 3's load_set asserts: patch barcodes are a subset of expression barcodes."""
    assert set(bc) <= expr_bc, f"{sid}: patch barcode not in expression"


def check_sample(td, sid, enc, apply_drop=True):
    """Row counts and the subset relation for one sample and encoder; does not raise on failure."""
    bc, X, xy, n_raw, n_removed = read_patched(td, sid, enc, apply_drop=apply_drop)
    E = expression_barcodes(td, sid)
    missing = sorted(set(bc) - E)
    return dict(sample_id=sid, encoder=enc, rows_embedding_file=n_raw, rows_removed=n_removed,
                rows_after=len(bc), n_expr_spots=len(E), subset_ok=len(missing) == 0,
                n_missing=len(missing), missing_examples=";".join(missing[:3]))


def load_lung(td, enc, genes_union):
    """Drop-first counterpart of round3_d4_sets.load_set: same returns, same order of samples.
    X, Yraw (patched spots x genes_union, raw counts), samp, bc, xy."""
    ids = sorted(s["sample_id"] for s in td["samples"])
    Xs, Ys, samp, bcs, xys = [], [], [], [], []
    for sid in ids:
        bc, X, xy, _, _ = read_patched(td, sid, enc, apply_drop=True)
        A = ad.read_h5ad(f"{d4().ROOT}/{td['paths']['adata'].format(sample_id=sid)}")
        assert set(bc) <= set(map(str, A.obs_names)), f"{sid}: patch barcode not in expression"
        sub = A[bc, genes_union]
        assert sub.n_obs == len(bc), (
            f"{sid}: selecting {len(bc)} patch barcodes returned {sub.n_obs} expression rows; "
            f"the expression file's barcode index is not unique")
        Yr = sub.X.toarray() if hasattr(sub.X, "toarray") else np.asarray(sub.X)
        Xs.append(X)
        Ys.append(np.asarray(Yr, dtype=np.float32))
        samp += [sid] * len(bc)
        bcs += bc
        xys.append(xy)
        del A, sub
    return (np.vstack(Xs), np.vstack(Ys), np.array(samp), np.array(bcs, dtype=object),
            np.vstack(xys))


_CTRL = re.compile("^(" + "|".join(CONTROL_PREFIXES) + ")")


def filter_xenium_controls(names):
    """Remove names starting NegControl, UnassignedCodeword or BLANK. Returns (kept, n_removed)."""
    names = list(names)
    kept = [g for g in names if not _CTRL.match(str(g))]
    return kept, len(names) - len(kept)


def lung_sample_table(td):
    """Per lung sample: sample_id, donor_id, slide_id, core_diameter_mm_source."""
    cd = td["expansion"]["core_diameter_mm_source"]
    return [dict(sample_id=s["sample_id"], donor_id=s["donor_id"], slide_id=s.get("slide_id"),
                 core_diameter_mm_source=cd.get(s["sample_id"])) for s in td["samples"]]
