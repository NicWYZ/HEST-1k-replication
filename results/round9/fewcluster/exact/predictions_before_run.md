# Track fewcluster, step I2-6, predictions written before the run

*26 October 2026, second session, before any code for I2-6 was written. The exact tuned frontier $\kappa^\dagger(f, G, n, \alpha)$ is the smallest max-share of a population least-squares residual for which more than a fraction $\alpha$ of samples have residuals exactly affine in the predictions (`docs/round09/i02/fewcluster/round09_fewcluster_tuned.md`). The two-piece search of I2-2 gave upper bounds.*

- **E1.** At small sizes ($G \le 10$) the exact algorithm agrees with brute force over all affine structures to $10^{-6}$ in every case tried.
- **E2.** At $G = 24$, $n = 8$, $\alpha = 0.10$ with standard normal predictions, the exact $\kappa^\dagger$ is within 15% below the two-piece upper bound (that is, the two-piece family is nearly extremal), averaged over at least 10 draws of $f$.
- **E3.** On the real tasks, the exact median $\kappa^\dagger$ over genes is below 0.10 on CCRCC and INDIANA_KIDNEY at $n = 8$, and below 0.16 on LUNG_XENIUM at $n = 6$, so the conclusion that essentially every gene is beyond the tuned frontier is unchanged.
