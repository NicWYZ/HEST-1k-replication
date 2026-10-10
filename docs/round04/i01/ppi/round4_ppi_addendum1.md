# Round 4, the PPI track, addendum 1 (interval 1)

30 September 2026. Written by the oversight chat for the PPI session, handed over by Nicolas. It answers the eight points in section 8 of `docs/round04/tracks/ppi/round4_ppi_plan.md`, settles two questions from Q0, and replaces the ACS source. Transcribe it into the plan as section 11 before acting on any of it. It does not move the Q1 gate, and nothing in it starts Q2.

**The gate rule, in the wording Nicolas approved.** Report-and-wait means that no stage after the gated stage starts until the oversight chat has reviewed the report and replied. Not the dependent stages only, and not the expensive ones only. Every stage. Nothing after the gate is set up, staged or piloted. Inside an interval there are no interim reports and no interim stop conditions; anything that would have halted work is handled under the decision boundaries, recorded in an "Escalations" section of the next report, and work continues. Contact with anyone outside the project is never the session's decision.

---

## 1. The eight points in plan section 8

All eight are right. What follows says what changes and when.

1. **The $r = 0$ cells.** Use a predictor drawn independently of $y$ with the same structure, $\hat y_{gi} = \nu + p_g + d_{gi}$, with $p_g \sim N(0, \sigma_u^2)$ and $d_{gi} \sim N(0, \sigma_e^2)$ independent of everything else, so that the predictor has the same between-donor share $\rho$ as the outcome. Record the construction in `docs/round04/tracks/ppi/round4_ppi_estimator_definition.md` and in the report.
2. **The $r = 0$ acceptance band.** Score the 0.89 to 0.91 band only on the variants the predictions call valid (CR2 with Satterthwaite at every $G_L$, CR1 at $G_L \ge 6$, and the bootstrap-$t$), with the Monte Carlo standard error beside every cell. Report the other variants against their own predictions, Q1.1 and Q1.2, and not against the band.
3. **Q1.5.** Score it as written. You are right that $\sigma_a^2 = \sigma_u^2/2$ fixes the cluster-level $R^2$ at $2/3$ in every cell. The axis that varies it belongs in Q2 and will be in the Q1 decision memo. Nothing in Q1 changes.
4. **$V_U$ and the rectifier's cluster component.** Both corrections are accepted for the Q2 theory document. The Q1 memo will restate the theorem with the $G_U$ condition. Nothing in Q1 changes.
5. **The ACS fetch.** Your reading was correct. Section 4 below is a second, explicit authorisation for one more download.
6. **The design-based variance when $U$ is the complement of $L$.** This is the one that changes Q1 now. Section 2 below.
7. **Q4 placement.** Accepted as the plan places it.
8. **Lung and $n_L = 16$.** Accepted. Run lung at the $n_L$ values that leave at least two unlabelled donors, and record the counts.

## 2. The design-based arm uses the textbook difference estimator

For the design-based target the population is the fixed set of $G$ donors, and predictions are available on every spot of every donor. The primary estimator in the design arm is therefore the difference estimator with predictions over the whole population. The only randomness is which $n_L$ of the $G$ donors are labelled, and the finite-population correction is then exact for the mean.

**Donor-weighted.** With $\bar y_g$ and $\bar{\hat y}_g$ the donor means,

$$\hat\theta = \frac{\lambda}{G}\sum_{g=1}^{G}\bar{\hat y}_g + \frac{1}{n_L}\sum_{g \in L}\big(\bar y_g - \lambda\,\bar{\hat y}_g\big), \qquad \widehat{\text{Var}}(\hat\theta) = \Big(1 - \frac{n_L}{G}\Big)\frac{s_r^2}{n_L},$$

where $s_r^2$ is the sample variance of the labelled donors' rectifier means $\bar y_g - \lambda\bar{\hat y}_g$, with a $t_{n_L - 1}$ reference.

**Spot-weighted.** With $N$ the total spot count and $R_g = \sum_{i \in g}(y_i - \lambda\hat y_i)$ the donor's rectifier total,

$$\hat\theta = \frac{\lambda}{N}\sum_{i=1}^{N}\hat y_i + \frac{G}{N\,n_L}\sum_{g \in L} R_g, \qquad \widehat{\text{Var}}(\hat\theta) = \Big(1 - \frac{n_L}{G}\Big)\frac{G^2}{N^2}\frac{s_R^2}{n_L},$$

with $s_R^2$ the sample variance of the labelled donors' $R_g$.

**$\theta_3$.** Apply the same two forms to the per-spot influence contributions. The morphology covariate is known on every spot, so $A$ is computed over all $N$ spots rather than estimated from $L$.

**What else this changes in Q1.**

- B1's complement form, $\lambda\bar{\hat y}_U + \bar r_L$ with $U$ the unlabelled donors, stays as a named legacy variant (`form = complement`) with its own coverage in the design arm, so the report can say how much of B2's over-coverage each form explains.
- The superpopulation arm is unchanged. $U$ is $G_U$ fresh donors independent of $L$, and no correction is applied.
- The design arm has no random unlabelled term, so the Welch-Satterthwaite combination and the $G_U$ axis apply to the superpopulation arm only. Score Q1.4 there.
- Score Q1.3 with the textbook form as primary, and report the complement form beside it.
- The three $\lambda$ rules are unchanged and apply to both forms.
- Every row carries a `form` column (`textbook` or `complement`) beside `target`.

`docs/round04/tracks/ppi/round4_ppi_estimator_definition.md` states both forms and says which is used for which target.

## 3. The permuted predictor's $\lambda$ on $\theta_2$

Q0 found that B1's spot-level tuning gives the permuted predictor a donor-weighted $\lambda$ with median 1.0, 0.86 and 0.46 for $\theta_2$ at $n_L = 6$, 8 and 12, where it should be near 0. The Q1 report explains why. Add one real-data check to Q1, capped at half a day. On CCRCC with the permuted predictor, for $\theta_2$ and $\theta_3$ at $n_L \in \{6, 8, 12\}$ and 200 draws, compute $\lambda$ under rules (a), (b) and (c). Report the median and interquartile range per rule in `results/round4/ppi/Q1_estimator/q1_permuted_lambda.csv`. The prediction, written now, is that rules (b) and (c) give a median within 0.1 of 0 in every cell and rule (a) reproduces Q0's figures.

## 4. The ACS source, replaced

Q0 found that the `ppi_py` census file has no state, PUMA or year, so the clustered ACS units cannot run from it. That file stays where it is and is not used for any clustered unit.

**Authorisation.** This addendum authorises one download, and only this one. Pull the 2018 ACS PUMS person file, 1-Year horizon, for the 50 states and DC, through `folktables` (`ACSDataSource(survey_year='2018', horizon='1-Year', survey='person').get_data(states=[...], download=True)`). You may install `folktables` into the track's environment. 2018 is the year the GHCP authors' released code (`soham-penn/hierarchical_CP`) uses for their ACS example with states as groups, so the conformal track can reproduce their numbers from the same file.

**Where it goes.** The raw files go to `results/round4/ppi/Q0_setup/acs_pums2018/raw/` on Longleaf, with every column kept and nothing committed. A parquet with an explicit `pa.schema` of all columns sits beside them. `PROVENANCE.txt` names the source URLs, the `folktables` version and the md5 of every downloaded file. Stamp the directory. The committed record is `acs_pums2018_inventory.json`, with rows per state, the column list and the md5s. Ask for 32 GB of memory.

**The task definition.** Write `results/round4/ppi/Q0_setup/acs_pums_task_def.json` in the A0 format.

- Population. The folktables ACSIncome filter, which is `AGEP > 16`, `PINCP > 100`, `WKHP > 0` and `PWGTP >= 1`. Survey weights are not used, and the task file says so. The design-based target is the finite population of sampled persons that pass the filter.
- Outcome and covariate. The outcome is $\log$ `PINCP`. The $\theta_3$ covariate is `AGEP`, standardised.
- Clusters. States (`ST`, 51 levels), and in a second setting PUMAs within the state with the most persons after the filter, named from the file.
- Predictor. A gradient-boosted regression of $\log$ `PINCP` on the ACSIncome features other than the state (`AGEP`, `COW`, `SCHL`, `MAR`, `OCCP`, `POBP`, `RELP`, `WKHP`, `SEX`, `RAC1P`). Cross-fit it over five folds of states, with each state assigned to a fold by `zlib.crc32` of its code, so every person's prediction comes from a model that never saw their state. This is the analogue of the harness's donor mode on HEST. Use library defaults with no tuning, and record the library, version and settings.
- Descriptive record. Record the predictor's unit-level, within-state and state-level $R^2$ in the inventory as a description of what was built. It is not a Q2 result.

**If the network refuses.** Record the refusal and stop this unit. Nicolas will run the fetch script on his own machine and upload the files, so write the fetch as a standalone script with no Longleaf dependency.

**Time.** Half a day, capped, in parallel with Q1. It is reported in the Q1 report under Q0. The ACS units of Q2 and Q4 read this file, not the `ppi_py` one.

## 5. Two procedural points

- **Provenance frame ids.** The lung wrapper's stamp carries the lead's frame id. Leave it as it is. Every later fan-out stamps from the sub-agent's own process, and the lead checks the frame id on each hand-back before commit.
- **Pull requests.** Opening the gate pull request through GitHub's REST API, as plan section 10 proposes, is accepted. Record the route used in the report.
