# Round 5, the inference track, the E2 decision memo

8 October 2026. Written by the oversight chat after reading `docs/round05/i01/ppi/round5_ppi_E2_report.md` at tag `round5-ppi-E2` (`b4e8ef5`, pull request #15), `docs/round05/tracks/ppi/round5_ppi_theory.md` section 1 and `docs/round05/tracks/ppi/round5_ppi_plan.md`, and checking the report against `e1_sim_grid.csv`, `e1_report_numbers.csv`, `e2_regimeB_grid.csv`, `e2_decomposition.csv`, `diag/e2_theta2_rare_group.csv` and every committed `PROVENANCE.txt` under `results/round5/ppi/`. Nicolas hands this to the inference session in full. Transcribe it into `docs/round05/tracks/ppi/round5_ppi_plan.md` as section 7, and commit this memo unchanged as `docs/round05/i02/ppi/round5_ppi_E2_decisions.md`, before anything in it runs. Interval 2 (E3a, E3 and E4, ending at the E4 gate) starts when both are committed locally.

**The gate rule, in the wording Nicolas approved.** Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. Contact with anyone outside the project is never the session's decision.

This track's gates are E2, E4 and E5.

---

## 1. Acceptance

The E2 report is accepted. Every number I checked reads back as quoted, and the predictions are scored as the report scores them. The report is careful where it matters most. It tested the mechanism it proposed for $\theta_2$, said which facts did not fit it, and did not stretch the $\theta_3$ result to $\theta_2$. The pairing check it added was a good idea.

Nicolas merges pull request #15 after reading this memo. Nothing is pushed to `round5-ppi` until that merge has happened (section 4 item 1).

## 2. What I checked, and two things the report did not say

**The provenance of the uploaded scripts.** The committed `PROVENANCE.txt` files carry 17 records of a `round5_ppi_*.py` script and its md5. Every one of the 17 md5s equals the md5 of that script at some commit of the branch, and every local commit they name is an ancestor of the tag. Three records name commit `8b879bb` for `round5_ppi_e2_levelcheck.py` and `round5_ppi_e2_report_extra.py`, which are not in that commit. They were committed at the same md5 in the next two commits, `4f52b0c` and `f75950f`. So the scripts that ran are the scripts that were committed, but the record points at the wrong commit. That is the weakness of uploading scripts loose, and section 4 replaces that route. The unit-level `PROVENANCE.txt` files stay on Longleaf, so the 17 records cover only the lead's jobs. Section 4 item 6 asks for the rest.

**Where the tuned interval loses coverage in E1.** Under the normal law the shortfall is not spread over the grid. It sits where the sampling fraction $n_L/G$ is large and the two halves' coefficients differ. At $\lambda^\star = 0.6$ and $G = 15$ the final interval covers 0.870, 0.867 and 0.840 at $n_L = 6$, 8 and 12 in its worst cell, against 0.894 to 0.900 for the classical interval, and the worst ratio of estimated to empirical variance is 0.69 at $n_L = 12$. At $G = 51$ the worst coverage is 0.880 at $n_L = 6$ and 0.885 to 0.890 above it. At $\lambda^\star = 1.2$, where both halves clip at 1 and the coefficient is effectively fixed, the worst coverage at $G = 15$ is 0.881 (`results/round5/ppi/E1_interval/e1_sim_grid.csv`, minimum over $R^2$ and $\kappa$ of `coverage_mean`, rule `c_crossfit_design`, interval `textbook_t|fpc|lin`). Within $G = 15$ the shortfall grows with $R^2$, from 0.876 at $R^2 = 0$ to 0.840 at $R^2 = 0.9$ for $n_L = 12$.

The oversight chat's reading is that the cross-fitting term escapes the finite-population factor. Write $c = (\lambda_A + \lambda_B)/2$ and $d = (\lambda_B - \lambda_A)/2$, where $\lambda_A$ is estimated on half $A$ and applied to half $B$, and the reverse. Then the estimator of section 2.3 of the brief is

$$
\hat\theta = \bar z_L - c\,(\bar f_L - \bar F) - \frac{d}{2}\,(\bar f_A - \bar f_B)
$$

The first two terms behave like a mean of a fixed rectifier over a simple random sample, and their variance carries the factor $(1 - n_L/G)$. The last term is a difference between the two halves of the sample, and its variance does not shrink as $n_L$ approaches $G$. The current variance estimate includes $d^2 s_f^2$ inside $s_e^2$ and multiplies it by $(1 - n_L/G)$, so it misses about a fraction $n_L/G$ of that term. At $G = 15$ and $n_L = 12$ that is 80% of it. This predicts what the grid shows. The loss grows with $n_L/G$, vanishes when both halves clip to the same value, and grows with $R^2$, because the true residual variance shrinks while the cross-fitting term does not. Lung has 15 donors, and its real-task coverage at $n_L = 12$ is 0.86 to 0.87 against 0.885 for the classical interval (`results/round4/ppi/Q4a_recompute/q4a_table61.csv`). Unit E3a below tests this.

**How rare the groups of $\theta_2$ are.** The report's mechanism for $\theta_2$ is right in outline, and the files show how extreme it is. On kidney cancer 11 of 23 valid donors have a group that is less than 5% of their spots, and the rarest is 0.07% (`results/round5/ppi/E2_regimeB/diag/e2_theta2_rare_group.csv`, `min_min_pi`), which on a donor of the task's median size, 2,893 spots, would be two spots, each carrying a weight near 1,400. With simple random draws inside the donor such a group is missed in almost every draw and dominates the estimate in the few draws that hit it. That gives a sampling distribution with a long tail, a variance estimate that is right on average and too small in the typical draw, and under-coverage. Round 4's regime B rows for $\theta_2$ and its regime A rows for $\theta_2$ with $m <$ all used the same draw, so they carry the same problem.

## 3. Readings for the paper

1. **The design-target interval.** With every unit of a labelled cluster labelled, the final interval covers within about 0.01 of nominal when the population is normal and the sampling fraction is small. Its shortfall on the real tasks has two sources. The larger is the classical $t$ interval's own under-coverage when cluster contributions are skewed, which the tuning does not cause and Johnson's correction does not repair. The median absolute skewness of the slope contributions is 1.76 on kidney cancer, 0.87 on lung and 0.60 on Indiana, and a gene's coverage falls with its skewness (`e1_report_numbers.csv`, `e1_real_coverage_vs_skewness.csv`). The smaller source is the cross-fitting term of section 2, which matters when most clusters are labelled. The paper states both.
2. **The level term in regime B.** Section 2.4 of the brief holds for the slope. Against the round-4 classical estimator, the constant predictor gives a width ratio of 0.81 to 0.82 on kidney cancer, 0.85 to 0.86 on Indiana, 0.57 to 0.59 on lung and 0.12 to 0.13 on census income. Measured against the constant predictor, the encoders' width is 0.98 to 1.04 on the three kidney tasks, 0.74 to 0.84 on lung, and 0.60 to 0.64 for the package predictor on census income (`results/round5/ppi/E2_regimeB/e2_decomposition.csv`, $\theta_3$, donor-weighted, design target, $m \ge 5$). So in regime B the encoders add nothing measurable on the Visium tasks once the level is removed, and they remove a sixth to a quarter of the width on lung and over a third on census income. Every round-4 statement of what predictions buy in regime B is superseded by these numbers, after E3 restates them against the classical estimator of the chosen form.
3. **The constant predictor is the control.** The permuted predictor carries the level and also unit-level noise, so it understates the level term by 0.06 to 0.10 on kidney cancer and lung. From now on the constant predictor is the primary control and the permuted predictor is reported beside it.
4. **The group difference under simple random draws inside a cluster.** A within-cluster design that ignores a known rare group gives intervals that under-cover however the variance is estimated, down to 0.23 on lung at two units per donor (`e2_regimeB_grid.csv`). This is a finding for the paper's design section, and it is why section 5 changes the draw.

## 4. How code reaches Longleaf, how the branch reaches GitHub, and what both tracks share

This section is word for word the same in the inference track's E2 decision memo and the prediction-set track's W2 decision memo, so the two tracks work the same way. It replaces the sentence of each instruction document that says the Longleaf clone is updated "by fast-forward from your pushed branch", and any plan extension or practice that says otherwise.

1. **GitHub sees one push per gate.** At a gate you commit the report, tag it, push the branch and the tag together, and open one pull request into `main`. Nothing is pushed between gates. Nicolas merges the pull request with a merge commit after the gate report has been reviewed. Do not push the branch again until that pull request is merged, because a push to a branch with an open pull request adds its commits to that pull request.
2. **Commits reach Longleaf as a git bundle.** In the local clone, create it with `git bundle create <file> <last delivered commit>..<your branch>`. Copy the file to Longleaf by the route you already use for inputs. A short Slurm job then runs, in your Longleaf code clone (`/work/users/w/e/weiyang/hest_code/round5-ppi/` or `/work/users/w/e/weiyang/hest_code/round5-conformal/`), `git bundle verify <file>`, `git fetch <file> <your branch>` and `git merge --ff-only FETCH_HEAD`, and prints the new HEAD. If the fast-forward fails, the job changes nothing and the failure is recorded. The clone never fetches from GitHub, is never rebased or reset, and never has another branch checked out.
3. **Jobs run from a fixed snapshot of a delivered commit.** The same delivery job writes the delivered commit's `code/` directory to `/work/users/w/e/weiyang/hest_code/<your branch>_snapshots/<full commit hash>/` with `git -C <clone> archive <commit> code | tar -x -C <that directory>`, and then removes write permission from it. A job puts that snapshot's `code/scripts` on `PYTHONPATH`, runs its scripts from there, and runs from its own output directory. It never runs scripts from the clone itself, and no script is copied loose into a job directory. Because a snapshot never changes, a new delivery can be made while jobs are still running on an earlier snapshot. Committed data files that a job reads, such as a round-4 table, are read from the clone, since no track changes them. Nothing is edited on Longleaf. A fix is a new local commit, a new delivery and a new snapshot.
4. **Each delivery is one row of `code_deliveries.csv`** in your results directory (`results/round5/ppi/` or `results/round5/conformal/`), with the date, the Slurm job id, the clone's HEAD before and after, the bundle's md5, the commits it carried and the snapshot's path.
5. **Every job records** the commit of the snapshot it ran from and the md5 of each script it executed. A commit that changes only documents or results need not be delivered.
6. **Before each gate push, two checks go into the report.** Every commit recorded in any `PROVENANCE.txt` of the interval is an ancestor of the gate tag. And every script md5 in any of them equals the md5 of that script at the commit the record names. List any record that fails either check. `provenance_index.csv` in your results directory has one row per job and script, with the job id, the unit, the script path, the md5, the recorded commit and the result of both checks. Commit the index, including rows for units whose own `PROVENANCE.txt` stays on Longleaf.
7. **Results** computed on Longleaf come back to the local clone by the route already in use and are committed there.
8. **Only the lead cancels a Slurm job,** and only after confirming with `squeue -u weiyang` and the track's job ledger that the job is the track's own. A sub-agent never runs `scancel`. It asks the lead.
9. **Files both tracks would otherwise edit.** Each track declares the exceptions of its numeric-claim sweep in its own file, `.verify-exceptions-round5-ppi` or `.verify-exceptions-round5-conformal`, and sweeps its own documents with `--exceptions` pointing at that file. Lines already in `.verify-exceptions` stay there. The README is swept by the oversight chat, not by the tracks. Neither track edits any other file outside its own areas.

**What this means for this track now.** Extension 1 of `docs/round05/tracks/ppi/round5_ppi_plan.md` is replaced. The Longleaf clone is at `d82c3f3`. The first delivery of interval 2 carries everything from `d82c3f3` to the commit that adds this memo, and makes the first snapshot. From then on no job runs an uploaded script. For E0 to E2 the records stay as they are. At the E4 gate, `provenance_index.csv` also carries rows for every E0 to E2 job, read from the Longleaf `PROVENANCE.txt` files, with the two checks applied. The three records of section 2 that name `8b879bb` are listed there as failing the second check, with the commit that does hold each script beside them.

## 5. Interval 2

### E3a. The cross-fitting term (half a day; first in the interval)

Write section 2.0 of `docs/round05/tracks/ppi/round5_ppi_theory.md` before any E3a job. Derive the design variance of the estimator in the form of section 2, keeping the dependence between the halves' coefficients and the halves' means, and say how much of the last term the current estimate misses. Propose an estimate that applies the finite-population factor to the first two terms only. The oversight chat's candidate is

$$
\widehat{\text{Var}}_{\text{xf}} = \Big(1 - \frac{n_L}{G}\Big)\frac{s_e^2}{n_L} + \frac{n_L}{G}\cdot\frac{d^2\,s_f^2}{n_L}
$$

with $s_f^2$ the labelled clusters' sample variance of $\bar f_g$. Derive it or correct it. If the derivation does not close, stop and report.

Add the corrected interval as `textbook_t|fpc|lin|xf` to `round5_ppi_estimator.py`. Rerun E1's normal and skewed grids at every $G$ with both intervals, on the same seeds. Then rerun the masking with every unit labelled, $n_L \in \{6, 8, 12, 16\}$, $\theta_3$ and $\theta_2$, donor-weighted, design target, rules `none` and `c_crossfit_design`, on all six tasks with both intervals.

**Acceptance.** When both halves get the same coefficient, $d = 0$ and the two intervals are identical. Under rule `none` they are identical. The rows of `textbook_t|fpc|lin` reproduce E1 and `q4a_table61.csv` exactly.

**Predictions.**

1. E3a.1. Under the normal law at $\lambda^\star = 0.6$, $G = 15$ and $n_L = 12$, the corrected interval's ratio of estimated to empirical variance is 0.90 to 1.05 in every cell, against 0.69 to 0.91 now, and its coverage is at least 0.88.
2. E3a.2. At $G = 51$ the two intervals' coverages differ by less than 0.01 in every cell, and at $\lambda^\star = 1.2$ by less than 0.005.
3. E3a.3. On lung at $n_L = 12$ the corrected interval's median coverage is within 0.015 of the classical interval's 0.885.

If the acceptance passes, E3 and E4 report the corrected interval as the primary design-target interval and the uncorrected one beside it. If it does not, they use `textbook_t|fpc|lin` as now and the failure is an escalation.

### E3. As instructed, with these changes

1. **Stratified draws for $\theta_2$.** Every $\theta_2$ row with $m <$ all, in regime B and in regime A, uses a draw stratified by group inside each cluster. The groups are the neoplastic-dominant and the stromal-dominant spots, which are known for every spot without labels. Each cluster gets $\lfloor m/2 \rfloor$ units from one group and $\lceil m/2 \rceil$ from the other, with the larger share going to the rarer group, each capped at the group's size, and any shortfall given to the other group. A group smaller than its share is labelled completely and contributes no sampling variance. The smallest $m$ for $\theta_2$ is 4, since each group needs two labelled units for a variance. Units in neither group are not labelled for $\theta_2$. Under this draw, form C for $\theta_2$ is the difference of the two groups' labelled means of $y - \lambda^{w}_g \hat y$ plus $\lambda^{w}_g$ times the difference of their all-unit means of $\hat y$, with design variance $\sum_h (1 - m_h/M_h)\,s_h^2/m_h$ over the two groups. Write this in theory section 2 item 1. Rerun the $\theta_2$ rows of E2 under the stratified draw as part of E3's small-$m$ runs. The simple random rows of E2 stay as the record of the failure.
2. **The constant predictor is the primary control** (section 3 item 3). The permuted predictor is reported beside it.
3. **The regime comparison without predictions.** Add to `e3_regime_comparison.csv` the ratio of regime B to regime A width with the classical estimator of form C in both, beside the same ratio with the two-level estimator. This separates what the design buys from what the predictor buys.
4. **The masking grid** carries the interval chosen by E3a.

Everything else in E3 is as the brief says. E3's acceptance checks are unchanged. Check 3 now covers the stratified $\theta_2$ form too. Under form C, a predictor constant within a cluster leaves the stratified $\theta_2$ estimate unchanged.

**Further predictions.**

1. E3.6. Under the stratified draw, the design-target coverage of $\theta_2$ in regime B is 0.86 to 0.92 for every $m \ge 6$ on every tissue task and arm, and 0.83 to 0.92 at $m = 4$.
2. E3.7. On the kidney tasks the ratio of regime B to regime A width is within 0.10 of the same ratio computed with the classical estimator of form C in both. On lung and census income the two-level ratio is lower than the classical one by 0.05 to 0.20.

### E4. As instructed

E4 uses the design-target interval chosen by E3a. Nothing else changes.

## 6. Answers to the escalations

1. **`results/round4/` unstamped.** Accepted as recorded. The md5 match is the right test for an input.
2. **E1 acceptance check 3 in 3 of 1,440 cells.** Accepted. All three are under log-normal laws with extreme skewness, and every normal-law cell passes.
3. **Plan extensions.** Extension 1 is replaced by section 4. Extensions 2 and 3 stand.
4. **$\theta_2$ in regime B.** Section 5, E3 item 1.
5. **Lung provenance with git off the path.** Accepted. Section 4 item 6 records the HEAD for those jobs from the clone's state.
6. **Process.** Sub-agents report to the lead and to no one else, Nicolas included. The lead decides what goes to Nicolas. Put this sentence in every brief of interval 2.

The heavy-law outlier of section 6.1 of the report is not pursued.

## 7. What the E4 report adds

Beside the format of section 8 of the brief, the E4 report carries the delivery ledger and the two checks of section 4 item 6, the E3a derivation and results, the stratified $\theta_2$ results, and an updated `e3_superseded_round4_numbers.csv` that includes the round-4 regime B and regime A $\theta_2$ rows with $m <$ all.
