# CLAUDE.md

**Whose file this is.** This is the operating file of the research session that works on branch `claude-science-fewcluster`, round 9's track `fewcluster` (option B, valid inference with few labelled clusters under skewed cluster contributions). That session is an independent investigator. Its starting point is the track's brief, `docs/round09/i01/fewcluster/round09_fewcluster_brief.md`. It had no part in the work recorded here and is not asked to continue anyone's plan. It studies the project as it stands, judges it on its merits, plans its own work and carries it out. This file holds the project's current state, how the record is kept, the standards of evidence and Nicolas's preferences. The record itself is in `docs/`. The session keeps this file and `docs/` current as it works, so that a fresh session can pick the project up from the repository alone.

**Last updated:** 2026-10-27, night (fewcluster session; track closed at Nicolas's request, closing report `docs/round09/i04/fewcluster/round09_fewcluster_closing_report.md`; the clone is `~/hest-1k/HEST-1k-fewcluster`)

The project is Nicolas Weiyang Zhang's first-year biostatistics PhD project at UNC Chapel Hill, in Dr. Hongtu Zhu's lab and supervised by Dr. Daiwei (David) Zhang. The advisors want methods, not applied analysis, with a submittable paper by spring 2027. The paper in preparation is "Labelling budgets for prediction-powered inference with clustered data". Labels are expensive and machine-learning predictions are free. Units come in clusters, such as donors in spatial transcriptomics or states in census data, and only a few clusters, often 4 to 16 of 15 to 50, can be labelled. The questions are how to spend a labelling budget (whole clusters, or a few units in every cluster), which clusters to label, how to make valid inference with prediction-powered inference (PPI) at so few clusters, and how to build prediction sets for a new cluster. The applications are HEST-1k spatial transcriptomics (pathology foundation-model predictions of gene expression) and ACS PUMS 2018 income by state.

## 1. Session protocol

**At the start of a session**

1. Check where you are. This session works in `~/hest-1k/HEST-1k-fewcluster` on branch `claude-science-fewcluster`. The Claude Science project instructions name another folder and branch, and the kickoff message overrides them. If you were started in `~/hest-1k/HEST-1k-Claude-Science`, on `claude-science`, or without access to `~/hest-1k/HEST-1k-fewcluster`, stop and ask Nicolas, who creates the clone (`git clone` does not run inside the sandbox) and grants the folder. Do not work in another track's clone.
2. Fetch the repository, check out `claude-science-fewcluster`, and read this file in full. Then read the brief, `docs/round09/i01/fewcluster/round09_fewcluster_brief.md`.
3. Check for staleness before trusting section 2. Run `git fetch origin --prune --tags`, then `python3 code/scripts/state_check.py --standing-dirs reference superseded`. Read every commit on this branch after the last change to this file, and correct section 2 first.
4. Note where you run. Data and compute are described in sections 8 and 9.
5. Read `docs/README.md`, the current round's `README.md` and `masterplan.md`, and the documents section 2 names. For history, read `docs/progress-log.md` and follow it to the files. Do not rely on memory or reconstruct history from summaries.

**During a session.** Write your steps into section 3 before starting them. After a context compaction, re-read sections 2 and 3. Before a long or risky step, refresh section 2 so a fresh session could resume from it alone, and bump "Last updated". When Nicolas states a preference, a rule, an answer or a decision, record it in this file or in `docs/` in the same session, since a chat is visible neither to the next session nor to another account.

**At each milestone,** such as a plan, a result, a written report or a change of direction, put the document in its place under `docs/` (section 7), add its row to the round's `README.md`, add a dated entry to `docs/progress-log.md`, and update sections 2 and 3 here, all in the same commit. Run the state check before committing.

**Rounds.** Work is planned one round at a time through the `/project-state-keeping` skill. This track works inside round 9, whose masterplan (`docs/round09/masterplan.md`) is shared with track `newtopic`. The track files its documents by interval under `docs/round09/i<KK>/fewcluster/` (starting at `i01`) and longer-lived track material under `docs/round09/tracks/<track>/` with `<track>` = `fewcluster`, and closes itself with a closing report in a new interval folder after its last working one, as the masterplan says. It may append amendments to the masterplan that concern its own track only. Round 9 closes through the skill once both tracks have closed and Nicolas has decided how the branches are merged, in whichever session he asks. If this track's work outgrows round 9, ask Nicolas before opening a round 10 on this branch.

**Where commits go.** Commit to `claude-science-fewcluster` only. Do not commit to `claude-science`, `claude-science-newtopic` or any other branch. Do not commit to `main`, rebase, squash, amend or force-push. Nicolas decides later how the branch reaches `main`.

## 2. Current state (27 October 2026, track closed)

- **Track `fewcluster` is closed.** Nicolas asked for the close on 27 October. The closing report is `docs/round09/i04/fewcluster/round09_fewcluster_closing_report.md`, and it is the place to start. It lists what the track established, the corrections, the decisions carried forward and what to read first. No work is running and no step is open on this branch.
- **What the track produced.** There are three theorems, all proved twice and not found in print (provisionally). Theorem 1 is the fixed-coefficient frontier (`docs/round09/i01/fewcluster/round09_fewcluster_frontier.md`). Theorem 2 is the tuned-coefficient frontier with an exact algorithm (`docs/round09/i02/fewcluster/round09_fewcluster_tuned.md`). Theorem 3 is the stratified frontier, with the comparison of labelling whole clusters against a few units in every cluster on ACS and HEST (`docs/round09/i03/fewcluster/round09_fewcluster_stratified.md`). Alongside them are a partial answer on critical values, a check of Williams' estimator, a side result on the median, a paper outline and a first draft (`docs/round09/tracks/fewcluster/paper_draft_v0.md`).
- **Round 9** stays open until both tracks have closed and Nicolas has decided how the branches reach `main` (masterplan, D4). Track `newtopic` closed on its own branch on 27 October. The round closes through `/project-state-keeping` in whichever session Nicolas asks.
- **Background** for anyone reopening the PPI paper. Round 8's positioning note (`docs/round08/i01/positioning/round08_positioning_note.md`) is the account of what was in print before this track. This track's position note (`docs/round09/i02/fewcluster/round09_fewcluster_position.md`) and closing report update it for the frontiers.
- **Decisions that are Nicolas's,** with the default until he decides. D1 to D6 are the round 9 masterplan's, and V, S and X are from the closing report.

| # | Decision | Default |
|---|---|---|
| D1 | Whether the frontiers become the paper's theory section, with regime A against regime B as its main design result | open, likely with David and Dr. Zhu |
| D2 | Whether the prediction-set half stays in the PPI paper (R8-1) | the draft defers it to separate work |
| D3 | Contacting anyone outside the project (including Paul and Kuchibhotla about the median result) | no contact |
| D4 | How the round 9 branches reach `main` | each stays on its branch |
| D5 | Whether earlier rounds' estimands, on log1p of unnormalized counts, are redefined | keep them and state that they partly measure sequencing depth |
| D6 | Whether round 8 is closed formally | it stays open |
| V | Whether bounding each cluster's share of the design variance is defensible for the applications | regime B's numbers are stated under it |
| S | Obtaining nine paywalled sources (`docs/round09/i03/fewcluster/round09_fewcluster_nov12.md`) | verdicts stay provisional |
| X | Deleting the paper full texts that checkers saved to the project's private artifact store | kept |

- **Next action.** None on this branch until Nicolas answers D1. If the track is reopened, the closing report's section 4 lists the open technical items, starting with draft v1.

## 3. Steps

The track's steps (S0 to I3-5) moved to `docs/progress-log.md` at the close, in the entry of 27 October headed "Track fewcluster closed". The steps of round 9's preparation are on branch `claude-science` (its `CLAUDE.md`, section 3, and `docs/progress-log.md`).

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
- **Two independent tracks (26 October).** He deferred option A, because it rests on results already in hand, and asked that the project be made ready for two separate sessions, one on option B and one on option C. The two sessions are independent investigators. They are not overseen by and do not report back to the claude-science session. This branch is the fewcluster session's.
- **Choice of direction (25 October, to the claude-science session; for this branch narrowed on 26 October).** For this branch the choice is narrowed to option B by the 26 October split. The session may reshape its direction within that option, and tells Nicolas before dropping it. The original rule follows. After the direction scan he left the choice to the session. It may pursue the prediction-set topic, few-cluster inference or a fresh topic based on the data in hand, and asks him only when it needs access that is gated by his approval.

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
- **Track files.** Scripts are `code/scripts/round9_fewcluster_<stage>.py`. Aggregates and novelty-check logs go under `results/round9/<track>/` with `<track>` = `fewcluster`. The round 9 scan's logs (`results/round9/scan/`, one queries and one candidates CSV per checker and a structured JSON of verdicts) are a usable template.
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
- **This branch's clone** is `~/hest-1k/HEST-1k-fewcluster` on Nicolas's Mac. Branch `claude-science`'s clone is `~/hest-1k/HEST-1k-Claude-Science`; do not work in it.
- **Outputs on Longleaf** go under `/work/users/w/e/weiyang/hest_replication/results/round9/fewcluster/`, so they do not mix with round 9's preparation (`/work/users/w/e/weiyang/hest_replication/results/round9/claude_science/`) or the other track's. Aggregates that enter the repository go under `results/round9/<track>/` with `<track>` = `fewcluster`.

## 9. Environment and git

- **People.** Nicolas (Longleaf ONYEN `weiyang`, Slurm accounts `rc_htzhu_pi` and `rc_tengfei_pi`). Dr. Hongtu Zhu, the PI. Dr. Daiwei (David) Zhang, Nicolas's supervisor.
- **Compute.** Longleaf, reached with Nicolas's account. The environment is described in `env/`.
- **Git.** The repository is `NicWYZ/HEST-1k-replication` and is public. This session commits to `claude-science-fewcluster` (section 1) as `git -c user.name="NicWYZ" -c user.email="NicWYZ@users.noreply.github.com" commit`, and pushes to `origin claude-science-fewcluster` after each milestone, in a cell that declares the GitHub credential.
- **Network.** Domains outside the sandbox allowlist need Nicolas's approval through a network-access request. OpenAlex needs the stored OpenAlex credential, which he approves once per session. Search subagents can use web search without approval.
- **Longleaf files.** The compute target's notes give the partition, account and time limits. Downloads from the scratch root `/work/users/w/e/weiyang/.claude-science-scratch/` need no approval, and downloads from other paths raise an approval card, so jobs copy their small outputs there.
- **Data usable locally.** The donor-level aggregates of round 9's preparation are in the repository in `results/round9/diagnostics/`, `results/round9/between/`, `results/round9/stud/`, `results/round9/norm/` and `results/round9/probe/` and need no Longleaf access. Per-spot data stay on Longleaf.

**Claude environment.** What a session needs that the repository cannot hold. A new account recreates these and nothing else.

| Need | Where it is set | Required for |
|---|---|---|
| The Claude Science project and its instructions | the Claude Science project settings (no copy in the repository yet). The project instructions name `~/hest-1k/HEST-1k-Claude-Science` and branch `claude-science` as the working directory; for this track the session's kickoff message overrides that with `~/hest-1k/HEST-1k-fewcluster` and `claude-science-fewcluster` | every session |
| Access to `~/hest-1k/HEST-1k-fewcluster` | granted to the session on Nicolas's Mac | reading and writing the clone |
| Skill `project-state-keeping` | the account's skills | opening and closing rounds, the state check |
| Access to Longleaf under ONYEN `weiyang` | Nicolas's machine and UNC accounts | runs on HEST-1k data |
| GitHub access to `NicWYZ/HEST-1k-replication` | the clone's git configuration on the Mac | committing and pushing the branch |
