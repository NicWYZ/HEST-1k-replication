# F4 LLGCLUSTER, predictions written before the data check (27 Oct 2026)

Status when written. The Gaussian simulation (script f_LLGCLUSTER_sim.py) had been launched but not read. The derivation (note, section 2) had been done. These predictions are for the data check only: (a) semi-synthetic runs on real CCRCC uni_v2 patch embeddings with simulated f, donor shift eta_d and noise e, and (b) ACS PUMS 2018 with states as groups and log wage as outcome.

## Semi-synthetic on real embeddings (x = real uni_v2 embeddings, donors as groups, train on a random half of donors, test on the other half)
- D1. At a CCRCC-like donor-shift share, the pooled iid bound B = (R2_oos + L)/(1 + L) exceeds the total population R2 (the one that counts eta as noise) in at most 10 percent of replications, and its mean sits below the target.
- D2. The bound does not over-claim the within-donor population R2 in more than 5 percent of replications at any shift share in {0, CCRCC-like, 0.6}.
- D3. The replication-to-replication standard deviation of B under donor shifts is at least 1.5 times that of the iid twin (same marginal variance, shift replaced by per-spot noise) at the CCRCC-like share, because only about 12 test donors carry the shift.
- D4. Because real embeddings carry donor-specific mean shifts (large eigen-directions that ridge shrinks), B is not larger relative to its target than in the Gaussian exchangeable case. In other words real embeddings make the bound more conservative, not less.

## ACS PUMS 2018 (states as groups, log wage, dummy/numeric covariates; no ground truth, so only comparisons)
- D5. With N of about 1000 training rows (about 40 per state, 25 random training states) and a few hundred covariate columns, L lies between 0.2 and 3.
- D6. The bound computed on within-state demeaned data (B_dm) exceeds the pooled bound B in more than 90 percent of random state splits, with the gap about equal to the between-state share of the variance of log wage divided by one minus that share, times (1 - B).
- D7. Validity of the bound cannot be tested on ACS because the population R2 is unknown (scored "not tested" in advance).

## Scoring convention
held / partly held / refuted / not tested, in the note.
