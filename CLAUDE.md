# CLAUDE.md

**Whose file this is.** This is the operating file of the research session that works on branch `claude-science-newtopic`, round 9's track `newtopic` (option C, a fresh direction outside clustered PPI and hierarchical conformal prediction, from the data in hand). That session is an independent investigator. Its starting point is the track's brief, `docs/round09/i01/newtopic/round09_newtopic_brief.md`. It had no part in the work recorded here and is not asked to continue anyone's plan. It studies the project as it stands, judges it on its merits, plans its own work and carries it out. This file holds the project's current state, how the record is kept, the standards of evidence and Nicolas's preferences. The record itself is in `docs/`. The session keeps this file and `docs/` current as it works, so that a fresh session can pick the project up from the repository alone.

**Last updated:** 2026-10-26 (written by the claude-science session when it cut this branch from `claude-science`; the track has not started)

The project is Nicolas Weiyang Zhang's first-year biostatistics PhD project at UNC Chapel Hill, in Dr. Hongtu Zhu's lab and supervised by Dr. Daiwei (David) Zhang. The advisors want methods, not applied analysis, with a submittable paper by spring 2027. The paper in preparation is "Labelling budgets for prediction-powered inference with clustered data". Labels are expensive and machine-learning predictions are free. Units come in clusters, such as donors in spatial transcriptomics or states in census data, and only a few clusters, often 4 to 16 of 15 to 50, can be labelled. The questions are how to spend a labelling budget (whole clusters, or a few units in every cluster), which clusters to label, how to make valid inference with prediction-powered inference (PPI) at so few clusters, and how to build prediction sets for a new cluster. The applications are HEST-1k spatial transcriptomics (pathology foundation-model predictions of gene expression) and ACS PUMS 2018 income by state.

## 1. Session protocol

**At the start of a session**

1. Fetch the repository, check out `claude-science-newtopic`, and read this file in full. Then read the brief, `docs/round09/i01/newtopic/round09_newtopic_brief.md`.
2. Check for staleness before trusting section 2. Run `git fetch origin --prune --tags`, then `python3 code/scripts/state_check.py --standing-dirs reference superseded`. Read every commit on this branch after the last change to this file, and correct section 2 first.
3. Note where you run. Data and compute are described in sections 8 and 9.
4. Read `docs/README.md`, the current round's `README.md` and `masterplan.md`, and the documents section 2 names. For history, read `docs/progress-log.md` and follow it to the files. Do not rely on memory or reconstruct history from summaries.

**During a session.** Write your steps into section 3 before starting them. After a context compaction, re-read sections 2 and 3. Before a long or risky step, refresh section 2 so a fresh session could resume from it alone, and bump "Last updated". When Nicolas states a preference, a rule, an answer or a decision, record it in this file or in `docs/` in the same session, since a chat is visible neither to the next session nor to another account.

**At each milestone,** such as a plan, a result, a written report or a change of direction, put the document in its place under `docs/` (section 7), add its row to the round's `README.md`, add a dated entry to `docs/progress-log.md`, and update sections 2 and 3 here, all in the same commit. Run the state check before committing.

**Rounds.** Work is planned one round at a time through the `/project-state-keeping` skill. This track works inside round 9, whose masterplan (`docs/round09/masterplan.md`) is shared with track `fewcluster`. The track files its documents by interval under `docs/round09/i<KK>/newtopic/` (starting at `i01`) and longer-lived track material under `docs/round09/tracks/<track>/` with `<track>` = `newtopic`, and closes itself with a closing report in its last interval folder. Round 9 closes through the skill once both tracks have closed and Nicolas has decided how the branches are merged. If this track's work outgrows round 9, ask Nicolas before opening a round 10 on this branch.

**Where commits go.** Commit to `claude-science-newtopic` only. Do not commit to `claude-science`, `claude-science-fewcluster` or any other branch. Do not commit to `main`, rebase, squash, amend or force-push. Nicolas decides later how the branch reaches `main`.

## 2. Current state (26 October 2026)

- **Background: round 8 is open** (`docs/round08/masterplan.md`, `docs/round08/README.md`). Its one piece of work, a check of every claim of the PPI paper against the survey-sampling literature and newer PPI work, is done. Its report is the positioning note, `docs/round08/i01/positioning/round08_positioning_note.md`, the current account of what the paper can and cannot claim. Read it in full before anything else. Its search logs and a numerical check are in `results/round8/positioning/`. No other work is running, and nothing has been started since the note.
- **Where the paper stands.** Nicolas's summary is that every result the project has produced on the PPI paper has turned out, on checking against the literature, to be someone else's. The note's verdicts are these.
  - Classical or in print are the design-target gain formula (a regression estimator on cluster-level values), the comparison of labelling whole clusters against a few units in every cluster with costs, the level term and the regression form with a cluster-specific intercept, the optimal number of units per cluster with a predictor (Snijders 2001, Raudenbush 1997), the interval for rejective (Mahalanobis-balanced) selection of clusters (Yang, Qu and Li, JASA 2023, appendix A5), and the small-sample cluster-robust correction (Bell and McCaffrey 2002).
  - Partly in print are design-based inference after prediction-guided selection (in print for units, not for a few whole clusters), cube sampling of clusters with simulated pair probabilities (Breidt and Chauvet 2011, Chauvet 2011), and the failure of weighting under rejective selection (Legg and Yu 2010 for units).
  - The estimator used since round 5 (`docs/round05/tracks/ppi/round5_ppi_estimator_definition.md`) is, for an even number of labelled clusters, Williams' (1961) exactly unbiased split-sample regression estimator with the factor $1 - n/G$ missing from its correction term. Writing its two parts as $T_1$ and $T_2$,
$$
\hat\theta_{\text{round 5}} = T_1 - T_2, \qquad \hat\theta_{\text{Williams}} = T_1 - \Big(1 - \frac{n}{G}\Big)T_2 ,
$$
so the round-5 estimator has a design bias of $\{(n/G)/(1 - n/G)\}\,\text{Cov}(c', \bar f_L)$. Under the round-5 coefficient rule (slope clipped to $[0, 1]$, zero below six clusters) the bias is small except near a census (note, section 3.2).
  - What is left is empirical. It consists of the comparison of selection designs at few clusters on real tasks (round 7), the map of which prediction-set method is narrowest by the number of labelled units in the target cluster (round 5), and splitting one labelling budget between inference and prediction sets, which no search found in print. The paper has no methodological core of its own yet.
- **Older accounts.** `docs/round07/oversight/round07_ppi_results_explained.md` and `docs/round07/oversight/round07_ppi_positioning.md` predate round 8 and still call several of these results the paper's own. The note lists the corrections in its section 5.
- **Open scientific questions,** from the note's sections 6.2 to 6.5 and earlier rounds. None has been started.
  1. A methodological core. The note proposes three directions, each to be checked against the literature first. One is exact or finite-sample design-based inference after prediction-guided selection of few clusters, where every interval and coverage guarantee found so far is asymptotic (randomization inference over the selection design, and the constrained-randomization literature for cluster randomized trials with few clusters). Another is the selection design as the object of a theory, choosing inclusion probabilities and balance variables for a few clusters to minimise the design variance of PPI while keeping the design measurable. The third is a theory for splitting one labelling budget between inference and prediction sets.
  2. Fixing the estimator. Compare the round-5 estimator, Williams' estimator with two groups, Williams' estimator averaged over splits (or Sanguiao Sande and Zhang's Rao-Blackwellised form), the fold-wise cross-fitted form (Lu et al. 2025, An et al. 2026) and a global coefficient, at 4 to 16 labelled clusters, with bias, variance and coverage. Williams' form needs a variance estimator that does not assume a small sampling fraction.
  3. Smaller items. Yang, Qu and Li's non-normal quantile in place of the $t$ reference for the rejective interval, and Aronow and Samii's conservative variance under rejective selection.
  4. Whether the prediction-set half stays in the PPI paper or becomes a separate paper. It is among the few parts untouched by prior work.
- **Sources not yet read.** Ten (Cochran 1977, Särndal, Swensson and Wretman 1992, Valliant, Dever and Kreuter 2018, Mickey 1959, Breidt and Chauvet 2011, Fattorini 2006, Fuller 2009, the JASA version of Yang, Qu and Li, Broska, Howes and van Loon 2025, Moerbeek 2006), listed with access links in the note's section 7. Nicolas may supply them. Paper PDFs he supplies go in `~/hest-1k/ppi_conf_papers/` on his Mac, outside the repository.
- **Decisions that are Nicolas's,** with the default until he decides.

| # | Decision | Default |
|---|---|---|
| D1 | Which venue, and which result the paper leads with | open until a round 9 track produces a candidate; option A deferred on 26 October |
| D2 | Whether the prediction-set half stays in the PPI paper | it stays until decided |
| D3 | Contacting anyone outside the project (authors such as GHCP's, advisors, collaborators) | no contact |
| D4 | How this branch and the round 9 track branches reach `main` | each stays on its branch |
| D5 | Whether earlier rounds' estimands, on log1p of unnormalized counts, are redefined | keep them and state that they partly measure sequencing depth |
| D6 | Whether round 8 is closed formally (needs a ruling on its positioning note) | it stays open |

- **Round 9 is open** (`docs/round09/masterplan.md`, `docs/round09/README.md`). Its preparation on branch `claude-science` (`docs/round09/00_prep/`) checked about twenty candidate directions for a methodological core with independent subagents, and none survived with a substantive open remainder (verdicts in `results/round9/scan/scan_structured_results.json`). It found where donor-level information lies in spatial transcriptomics. A shared technical factor carries 0.650 of between-donor variance on CCRCC, histology predictions carry little donor-level information for most genes, and one technical-outlier donor breaks few-cluster intervals and hierarchical conformal coverage, which a probe of three spots per donor reveals (`round09_stud_and_depth.md`, `round09_normalization_check.md`, `round09_probe_designs.md`).
- **This track.** On 26 October Nicolas deferred option A (a design and empirical paper on those results) and asked for two separate, independent sessions, one on option B and one on option C. This branch is track `newtopic`, option C, a fresh direction outside clustered PPI and hierarchical conformal prediction, from the data in hand. Its brief is `docs/round09/i01/newtopic/round09_newtopic_brief.md`. The track has not started. Nothing has been planned, run or checked on this branch beyond what it inherited from `claude-science`.
- **The other track.** Track `fewcluster` runs at the same time on branch `claude-science-fewcluster`. The two tracks are independent. Neither reports to the other or to the claude-science session, and neither edits the other's files. Each reports to Nicolas only, at significant results or roadblocks.
- **Next action.** Read the brief and the documents it names, then plan the track's first interval in section 3 and in `docs/round09/i01/newtopic/`, with a novelty check by independent subagents before any result is built on.

## 3. Steps

Steps of this track, with stable IDs, checked when done with a one-line note (date, commit, what was done, key numbers). They move to the progress log when the track closes. The steps of round 9's preparation are on branch `claude-science` (its `CLAUDE.md`, section 3, and `docs/progress-log.md`).

- [x] **S0 Branch cut.** 26 October. Cut from `claude-science` at the commit that opened round 9 (bd4af6ba), with this file and the brief written by the claude-science session.

## 4. Working preferences (Nicolas's)

- **Writing.** Plain, natural prose. No em-dashes. No sentence that states something, then a colon, then the explanation. No compressed or clever phrasing, and no inflated length (by 4 October).
- **Math.** Rendered LaTeX, each `$$` on its own line. In a derivation, show every expression that carries the argument and skip only the algebra between displayed lines, saying what kind of step was skipped. Never describe a derivation in words in place of its formulas (by 4 October). When he asks how something works, derive it slowly and step by step.
- **Numbers.** At the precision the comparison needs, with the relative scale stated. Full precision stays in files.
- **Aims.** Minimal biology by design. Expression is a signal to predict, calibrate and use for inference. His career goal is quantitative research in finance, so directions are judged by how well their skills transfer. He prefers ML venues (NeurIPS, ICML, AISTATS) or top statistics journals, and wants the paper's scope broad and useful beyond spatial transcriptomics.
- **Thoroughness.** "Thoroughness always comes first" (19 October).
- **Project state.** The state and context of the project live in the repository, not in any session's memory, so a fresh session can pick it up and get up to speed. The record is kept with `/project-state-keeping` (24 October). `docs/` is filed chronologically by round, interval and track, with each round's masterplan at the round level.
- **Literature.** Papers a session cannot retrieve go to Nicolas as one list of at most 10, each with a link through UNC Chapel Hill's library proxy (`https://login.libproxy.lib.unc.edu/login?url=https://doi.org/<DOI>`) or to a free version, and he supplies them (13 October).
- **Decisions.** He makes the decisions at his level and wants to be told which need David or Dr. Zhu.
- **Autonomy and novelty (24 October, said to the claude-science session; it applies to every research session).** The session explores directions, derives and validates results on its own, and reports to him only at significant roadblocks or significant results. The end goal is a statistics-forward methodological paper in spatial transcriptomics. A literature check for novelty is a hard rule, run by subagents continually while the work goes on, because the model is prone to rediscovering results it has absorbed from its training data.
- **Two independent tracks (26 October).** He deferred option A, because it rests on results already in hand, and asked that the project be made ready for two separate sessions, one on option B and one on option C. The two sessions are independent investigators. They are not overseen by and do not report back to the claude-science session. This branch is the newtopic session's.
- **Choice of direction (25 October, to the claude-science session).** After the direction scan he left the choice to the session. It may pursue the prediction-set topic, few-cluster inference or a fresh topic based on the data in hand, and asks him only when it needs access that is gated by his approval.

## 5. Standards of evidence

These are not preferences. The record depends on them.

1. Every number is read back from its file before it is asserted, and a derived value is recomputed before it is stated.
2. Predictions are written before a run and scored afterwards as held, partly held, refuted or not tested.
3. Nothing is claimed as new without a literature check, covering the survey-sampling literature as well as the machine-learning one. Most claims the project made fell to that check.
4. Written reports are not edited after they are committed. Corrections go in a later document and in the round's reading guide.
5. Details of unpublished manuscripts by others (title, authors, methods, results) stay out of this repository, which is public. The repository records that a check was made and its verdict (13 October).
6. Gated data never enter the repository.
7. Contacting anyone outside the project is Nicolas's decision.

## 6. Delegation

Independent, checkable jobs (searches, extracting numbers, recomputing a headline, sweeps of numeric claims) can go to subagents, several at once when they do not depend on each other. A check of an important result is done by a fresh agent that has not seen the work. Workers do not commit, and their output is read against the files before it is used.

## 7. Conventions

- **Filing.** Every document has one place by round, interval and track (`docs/README.md`, "How the folders work"), with a file name carrying the full prefix, such as `round09_<track>_<stage>.md`, so every name is unique. Results go under `results/roundN/<track>/`, scripts under `code/scripts/`.
- **The history's vocabulary.** Rounds 1 to 8 were run by a coordinating chat (the "oversight chat") and by separate sessions that ran experiments (the "execution sessions"), linked by instructions, decision memos and gate reports. That vocabulary describes how the past work was organised. It places no obligations on this session.
- **Corrections in the history.** Read a round's reading guide ("Corrections and withdrawn readings") before trusting a number from inside it.
- **Tags.** `[proposed]` marks a suggestion Nicolas has not accepted. `[verify]` marks a statement written from memory.
- **Before every commit,** run the state check (section 1). `code/scripts/verify_numeric_claims.py` checks that a number in a markdown document appears in the file it cites.

## 8. Where things are

```
CLAUDE.md                 this file
README.md                 the repository's public entry point, with the benchmark work of rounds 1 and 2
docs/README.md            the reading guide, with the layout and one row per round
docs/progress-log.md      what happened and why, newest first
docs/moved.md             old path to new path, from the reorganisation of 9 October
docs/reference/           methods derived from scratch, concepts explained
docs/superseded/          two working documents a later one replaced, each bannered
docs/roundNN/             one round, with README.md, masterplan.md, 00_prep/, iKK/<track>/, tracks/, oversight/
code/scripts/             every script; results/ the outputs by round; figures/ the figures; env/ the environment
```

- **History by round.** Rounds 1 to 3 (12 to 24 September) replicated and instrumented the HEST-1k benchmark (Jaume et al., NeurIPS 2024) on Longleaf, then ran first experiments on two topics that were retired. Round 4 (28 September to 3 October) moved to labelling budgets for PPI with clustered data, with a data pull and tracks on inference and on prediction sets (HCP and GHCP). Round 5 (7 to 9 October) gave the design-target interval, the regression form with a cluster intercept, balanced selection of clusters and the prediction-set map. Round 6 (11 to 13 October) was a side experiment on language-model cheatsheets, which moved to the private repository `NicWYZ/textual-st-histology` and is outside this project. Round 7 (13 to 15 October) studied inference after histology-guided selection of clusters (rejective, cube, mixture and k-center designs, and Broska and Howes's cluster-robust PPI), and ran a separate federated learning line for expression prediction, closed with a decision report. Round 8 is section 2.
- **Data.** The HEST-1k benchmark data are gated (`MahmoodLab/hest-bench`) and are not in this repository. They sit on Longleaf under `/work/users/w/e/weiyang/hest_replication` (`MANIFEST.md`, `bench_data/INVENTORY.md`), whose working tree is at tag `round4-data-v2`. The raw ACS PUMS 2018 fetch is at `~/hest-1k/acs_pums2018` on Nicolas's Mac, outside the repository.
- **This branch's clone** is `~/hest-1k/HEST-1k-round9-newtopic` on Nicolas's Mac. Branch `claude-science`'s clone is `~/hest-1k/HEST-1k-Claude-Science`; do not work in it.
- **Outputs on Longleaf** go under `/work/users/w/e/weiyang/hest_replication/results/round9/newtopic/`, so they do not mix with round 9's preparation (`/work/users/w/e/weiyang/hest_replication/results/round9/claude_science/`) or the other track's. Aggregates that enter the repository go under `results/round9/<track>/` with `<track>` = `newtopic`.

## 9. Environment and git

- **People.** Nicolas (Longleaf ONYEN `weiyang`, Slurm accounts `rc_htzhu_pi` and `rc_tengfei_pi`). Dr. Hongtu Zhu, the PI. Dr. Daiwei (David) Zhang, Nicolas's supervisor.
- **Compute.** Longleaf, reached with Nicolas's account. The environment is described in `env/`.
- **Git.** The repository is `NicWYZ/HEST-1k-replication` and is public. This session commits to `claude-science-newtopic` (section 1).

**Claude environment.** What a session needs that the repository cannot hold. A new account recreates these and nothing else.

| Need | Where it is set | Required for |
|---|---|---|
| The Claude Science project and its instructions | the Claude Science project settings (no copy in the repository yet). The project instructions name `~/hest-1k/HEST-1k-Claude-Science` and branch `claude-science` as the working directory; for this track the session's kickoff message overrides that with `~/hest-1k/HEST-1k-round9-newtopic` and `claude-science-newtopic` | every session |
| Access to `~/hest-1k/HEST-1k-round9-newtopic` | granted to the session on Nicolas's Mac | reading and writing the clone |
| Skill `project-state-keeping` | the account's skills | opening and closing rounds, the state check |
| Access to Longleaf under ONYEN `weiyang` | Nicolas's machine and UNC accounts | runs on HEST-1k data |
| GitHub access to `NicWYZ/HEST-1k-replication` | the clone's git configuration on the Mac | committing and pushing the branch |
