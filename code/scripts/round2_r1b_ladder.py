"""Round 2 R1b, Decision 2: the four-rung R2 ladder and the four-cause deficit figure.

Stage: R1b, the four-rung R2 ladder (round2_R1_decisions.md Decision 2).

Reads the per-(encoder, task, fold, gene) metrics written by round2_r1b_heads.py and
decomposes the R2 deficit without refitting anything. Expects a DataFrame `D` in scope with
columns: encoder, task, fold, head, pearson, r2, mse, mean_pred, mean_target, std_pred,
std_target, n_test.

The algebra. With b = mean(yhat) - mean(y), rho = s_yhat / s_y and r = Pearson, on the test
fold

    R2 = 2*r*rho - rho^2 - b^2 / s_y^2

which is exact for the population-sd convention used when the metrics were written. The four
rungs fix successively more of it:

    faithful        as observed on the nointercept head
    train-mean      as observed on the intercept head (level from the training fold)
    oracle level    b := 0, level read off the TEST fold      -> 2*r*rho - rho^2
    oracle + scale  b := 0 and rho := r, the maximum over both -> r^2

r^2 is therefore the ceiling any level-and-scale recalibration of this head can reach, and
the gap from it to 1 is the encoder's pattern limit.
"""
import numpy as np
import pandas as pd

HEAD_F, HEAD_I = "nointercept", "intercept"
HEAD_64 = "intercept_f64"


def identity_check(d):
    """Verify R2 = 2*r*rho - rho^2 - b^2/s_y^2 on the stored columns."""
    rho = d.std_pred / d.std_target
    b = d.mean_pred - d.mean_target
    pred = 2 * d.pearson * rho - rho ** 2 - (b ** 2) / (d.std_target ** 2)
    err = (pred - d.r2).abs()
    return float(err.median()), float(err.max())


def ladder(D):
    out = {}
    for head, name in ((HEAD_F, "faithful"), (HEAD_I, "train-mean intercept"),
                       (HEAD_64, "intercept_f64")):
        s = D[D["head"] == head]
        if len(s):
            out[name] = float(s.r2.median())

    # oracle rungs are computed on the head that has the level fixed correctly
    s = D[D["head"] == HEAD_64] if (D["head"] == HEAD_64).any() else D[D["head"] == HEAD_I]
    rho = (s.std_pred / s.std_target).values
    r = s.pearson.values
    out["oracle level"] = float(np.median(2 * r * rho - rho ** 2))
    out["oracle level and optimal scale"] = float(np.median(r ** 2))
    return out, float(np.median(rho)), float(np.median(r))


def run(D, outdir="."):
    med, mx = identity_check(D[D["head"] == HEAD_64]) if (D["head"] == HEAD_64).any() \
        else identity_check(D[D["head"] == HEAD_I])
    print(f"identity check |R2_reconstructed - R2_stored|: median {med:.3e} max {mx:.3e}")

    rungs, med_rho, med_r = ladder(D)
    print("\n=== four-rung ladder (median over encoder x fold x gene) ===")
    for k, v in rungs.items():
        print(f"  {k:<34} {v:+.4f}")
    print(f"\nmedian rho (s_pred/s_target) = {med_rho:.4f}   median r = {med_r:.4f}")
    print(f"rho/r = {med_rho/med_r:.3f}  -> "
          f"{'OVER-dispersed: scale miscalibration' if med_rho > med_r*1.05 else 'near-optimal scale'}")

    rows = []
    for enc, g in D.groupby("encoder"):
        rr, rho_e, r_e = ladder(g)
        rows.append(dict(encoder=enc, median_rho=rho_e, median_r=r_e, rho_over_r=rho_e / r_e, **rr))
    per_enc = pd.DataFrame(rows).set_index("encoder")
    per_enc.to_csv(f"{outdir}/r1b_ladder_by_encoder.csv")

    rows = []
    for task, g in D.groupby("task"):
        rr, rho_t, r_t = ladder(g)
        rows.append(dict(task=task, median_rho=rho_t, median_r=r_t, **rr))
    per_task = pd.DataFrame(rows).set_index("task")
    per_task.to_csv(f"{outdir}/r1b_ladder_by_task.csv")
    print("\nby task:")
    print(per_task.round(4).to_string())
    return rungs, per_task, per_enc, med_rho, med_r


def figure(rungs, med_rho, med_r, n_enc, outdir="."):
    """Waterfall: the R2 deficit assigned to four named causes."""
    import matplotlib as mpl
    import matplotlib.pyplot as plt

    faith = rungs["faithful"]
    lvl = rungs.get("intercept_f64", rungs["train-mean intercept"])
    orc = rungs["oracle level"]
    ceil_ = rungs["oracle level and optimal scale"]

    steps = [
        ("faithful head\n(no intercept)", faith, "#7A7A7A"),
        ("+ intercept\nlevel from training", lvl, "#C1272D"),
        ("+ oracle level\nslide-level mean shift", orc, "#E8A33D"),
        ("+ optimal scale\ncalibration", ceil_, "#2E6E8E"),
        ("pattern ceiling $r^2$\n(encoder limit)", ceil_, "#2E6E8E"),
    ]
    causes = [
        ("level", faith, lvl, "#C1272D", "fixed by an intercept"),
        ("slide-level mean shift", lvl, orc, "#E8A33D", "needs slide information \u2014 Topics A and B"),
        ("scale", orc, ceil_, "#2E6E8E", "needs calibration \u2014 Topic A"),
    ]

    fig, ax = plt.subplots(figsize=(7.6, 4.0))
    for i, (lo, hi, col, lab) in enumerate(
            [(c[1], c[2], c[3], c[0]) for c in causes]):
        ax.barh(i, hi - lo, left=lo, height=0.6, color=col, edgecolor="white", linewidth=0.8)
        ax.text(hi + 0.012, i, f"+{hi-lo:.3f}", va="center", fontsize=7, color=col)
    ax.axvline(0, color="0.35", lw=0.8)
    ax.axvline(ceil_, color="#2E6E8E", lw=0.8, ls=":")
    ax.set_yticks(range(len(causes)))
    ax.set_yticklabels([f"{c[0]}\n{c[4]}" for c in causes], fontsize=7)
    ax.set_xlabel("median $R^2$ (median over encoders, folds and genes)")
    ax.set_title("The $R^2$ deficit of the benchmark head, assigned to four causes:\n"
                 f"from {faith:.2f} to a pattern ceiling of {ceil_:+.2f}",
                 loc="left")
    ax.text(ceil_ + 0.012, len(causes) - 0.45,
            f"$r^2$ = {ceil_:.3f}\nceiling for any\nrecalibration of\nthis head",
            fontsize=6.5, color="#2E6E8E", va="top")
    ax.text(0.0, -0.27,
            f"n = {n_enc} encoders x 29 folds x 50 genes. Rungs are exact algebra on the stored "
            f"columns, not refits: with b the level offset, rho the scale ratio\nand r the "
            f"correlation, $R^2 = 2r\\rho - \\rho^2 - b^2/s_y^2$. Median observed "
            f"$\\rho$ = {med_rho:.3f} against median $r$ = {med_r:.3f}, so the head is "
            f"over-dispersed\nrelative to its own signal. The oracle rung reads the test fold's "
            f"own gene mean and is diagnostic, not a usable model.",
            transform=ax.transAxes, fontsize=6, color="0.4", va="top")
    fig.savefig(f"{outdir}/fig_r1b_four_causes.png", dpi=300, bbox_inches="tight")

    r_ = fig.canvas.get_renderer()
    t_ = [(t, t.get_window_extent(r_)) for t in fig.findobj(mpl.text.Text)
          if t.get_text().strip() and t.get_visible()]
    print("overlaps:", [(a.get_text()[:20], b.get_text()[:20])
                        for i, (a, ba) in enumerate(t_) for b, bb in t_[i+1:] if ba.overlaps(bb)])
    return fig
