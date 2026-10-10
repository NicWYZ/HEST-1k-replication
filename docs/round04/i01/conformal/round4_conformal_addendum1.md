# Round 4, the conformal track, addendum 1 (interval 1)

30 September 2026. Written by the oversight chat for the conformal session, handed over by Nicolas. It answers the five points in section 8 of `docs/round04/tracks/conformal/round4_conf_plan.md`, settles which GHCP pool rule is primary, says how the rest of the lower-bound cap may be used, and records a change of ACS source. Transcribe it into the plan as section 10 before acting on any of it. It does not move the C2 gate, and nothing in it starts C3.

**The gate rule, in the wording Nicolas approved.** Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. This track's gates are C2 (the go or no-go) and C4. Contact with anyone outside the project is never the session's decision.

---

## 1. The five points in plan section 8

All five are right.

1. **C1 acceptance with no donor effect.** Evaluate every method against its own expected coverage under no donor effect. For HCP that is its $(1-\alpha)(K+1)/K$ calibration level where finite. For one-per-donor it is $\lceil (K+1)(1-\alpha)\rceil/(K+1)$. The literal reading is reported beside it, as the plan proposes.
2. **The C0 anchor against `a4b_summary.csv`.** Accepted as done. That means the per-encoder comparison at $10^{-12}$ plus the check that the summary is the mean of the three committed tables.
3. **Prediction C3.3.** It will be scored "not tested", since none of C3's tasks is block-calibrated.
4. **Lung $K = 8$.** Right. HCP is finite only at $\alpha = 0.2$ at $K = 6$ and at $K = 8$, and both rows are reported.
5. **"Within-slide" on lung.** It means within-donor, the donor's own core or cores, as the plan says.

The conventions in plan section 7 are accepted as written. This includes the primary and secondary readings of criterion (b) where the reference price is infinite. The criterion itself is unchanged.

## 2. The GHCP pool rule

The C1 code-path check records a difference between the restricted-pool size in the paper (its equation 8) and the one in the released code (`soham-penn/hierarchical_CP`). The primary implementation in C1, C2 and C3 is the rule for which the paper's validity theorem is stated. The other rule runs as a secondary variant in `c1_ghcp_reproduction.csv` and in every C1 cell at $\alpha = 0.1$. The C2 report does four things here.

- It shows the difference on one small worked example.
- It says which rule the theorem covers, quoting the paper's statement.
- It says whether the two rules' coverage differs by more than Monte Carlo error in any cell.
- It records the repository commit read.

If the paper does not say which rule its theorem covers, record that under escalations, keep the paper's rule as primary, and continue.

## 3. The lower-bound scoping

The statement came early, and stopping there was within the rule. The remaining cap, to 3 October, may be used on the items below, in this order. Mark each derived, conjectured or failed in `docs/round04/i01/conformal/round4_conf_lower_bound.md`, and stop at the cap wherever you are.

1. Write step 3 of Proposition 2, the equivariance construction, in full.
2. Check whether randomised HCP attains Proposition 1's floor with equality.
3. Attempt case 3 ($|J_h| = 1$) of the section 5 argument.
4. Attempt the finite-$N_k$ version, with the distance check widened by a DKW band.

Do not search the literature for whether the propositions are known. The oversight chat does that before the C2 decision.

**One added candidate, K6, the switch rule of section 5.** Run it with finite $N_k$, with $d$ widened by $2\epsilon_N$ from a DKW band at level $0.01$, and $\delta$ from the probe's worst configuration at that $d$. It goes through the C1 grid at $\alpha = 0.1$ behind the C1 interface, with its assumptions and guarantee in the docstring before it runs. It is scored against the fixed criterion. Part (c) is marked unmet unless items 3 and 4 above are derived. Cap one day, taken from the candidate budget. The criterion is not changed by adding it.

**Prediction C2.6**, written now. K6 covers at least 0.89 in every cell and meets (b) only in cells with between-donor share 0.1, so it fails (b) overall, and its price of validity equals HCP's at shares 0.3 and 0.5.

## 4. The ACS source has changed

The `ppi_py` census file that the PPI track fetched in Q0 has no state or PUMA, so it cannot serve C3. The PPI track is now fetching the 2018 ACS PUMS person file, 1-Year, for the 50 states and DC, through `folktables`, into `results/round4/ppi/Q0_setup/acs_pums2018/` on Longleaf, with every column kept. 2018 is the year of the GHCP authors' released ACS example.

In C3, and not before the C2 memo, read that directory read-only and record the PPI commit whose provenance it carries. `whose()` will return `sibling`, and this addendum is the permission to read it. Reproduce the GHCP paper's ACS numbers by applying the released code's own processing (its `real_data/acs/` scripts and their defaults, at the commit already recorded) to that file. Confirm from the released loader that the year and horizon match, and record it as an escalation if they do not. Do not use the `ppi_py` file.

## 5. Two procedural points

- **Pull requests.** Opening the gate pull request through GitHub's REST API, as plan section 9 proposes, is accepted. Record the route used in the report.
- **The instruction document.** The full instruction document is now on `main` at `docs/round04/i01/conformal/round4_conformal_track.md`. It is not added to this branch, and the proposal in the plan's header needs no further action.
