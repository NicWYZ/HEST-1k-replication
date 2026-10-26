# Round 9, masterplan

*Written on 26 October 2026 by the claude-science session through the `project-state-keeping` skill, after Nicolas's decision of the same day. Living while the round runs. Amendments are appended at the end with their date, and the text above them is not rewritten. It is frozen at the round's close.*

## Why this round

Round 8's positioning note (`docs/round08/i01/positioning/round08_positioning_note.md`) left the PPI paper with no methodological core of its own. The claude-science session then spent round 9's preparation looking for one (`docs/round09/00_prep/`). About twenty candidate directions were each checked by an independent subagent, and none survived with a substantive open remainder (`round09_direction_scan.md`, its addendum, `round09_stud_and_depth.md`, `round09_probe_novelty.md`; every verdict is in `results/round9/scan/scan_structured_results.json`). The data work found where donor-level information lies in spatial transcriptomics. A shared technical factor dominates between-donor variation on Visium, histology predictions carry little donor-level information for most genes, and one technical-outlier donor breaks few-cluster intervals and hierarchical conformal coverage, which a probe of a few spots per donor reveals (`round09_stud_and_depth.md`, `round09_normalization_check.md`, `round09_probe_designs.md`).

The scan's section 4 gave Nicolas options. On 26 October he deferred option A (a design and empirical paper built on the results already in hand) and asked for two separate sessions, one on option B and one on option C, each independent.

## Goal

Each track looks for a methodological contribution that survives the literature check, with a formal result and a test on the project's data, toward a statistics-forward paper submittable by spring 2027.

## Tracks

The two tracks run in parallel in separate sessions, on separate branches and working copies. Each session is an independent investigator. It reads its brief, plans its own work, keeps its own state in its branch's `CLAUDE.md`, and reports to Nicolas only, at significant results or roadblocks. Neither track reports to the other or to the claude-science session, and neither edits the other's files.

| Track | Option | Branch | Brief | Writes to |
|---|---|---|---|---|
| `fewcluster` | B. Valid inference with few labelled clusters under skewed cluster contributions, with predictions free for every cluster | `claude-science-fewcluster` | `i01/fewcluster/round09_fewcluster_brief.md` | `docs/round09/tracks/fewcluster/`, `docs/round09/iKK/fewcluster/`, `results/round9/fewcluster/`, `code/scripts/round9_fewcluster_*` |
| `newtopic` | C. A fresh direction outside clustered PPI and hierarchical conformal prediction, from the data in hand | `claude-science-newtopic` | `i01/newtopic/round09_newtopic_brief.md` | `docs/round09/tracks/newtopic/`, `docs/round09/iKK/newtopic/`, `results/round9/newtopic/`, `code/scripts/round9_newtopic_*` |

Each session also keeps `docs/round09/README.md`, `docs/progress-log.md` and `docs/README.md` current on its own branch. Those shared files will differ between the branches, and Nicolas decides how the branches are merged (D4).

**Option A** is deferred. Its material is `round09_probe_designs.md` and the files it cites, on every branch.

## Schedule

No date was set. The target is a submittable paper by spring 2027.

## Open questions

| # | Question | Default | Who decides |
|---|---|---|---|
| D1 | Which result the paper leads with | open until a track produces a candidate | Nicolas, possibly with David |
| D2 | Whether the prediction-set half stays in the PPI paper | it stays until decided | Nicolas |
| D3 | Contacting anyone outside the project | no contact | Nicolas |
| D4 | How the branches reach `main` | each stays on its branch | Nicolas |
| D5 | Whether earlier rounds' estimands, on log1p of unnormalized counts, are redefined | keep them and state that they partly measure sequencing depth | Nicolas, likely with David |
| D6 | Whether round 8 is closed formally (it needs a ruling on its positioning note) | it stays open | Nicolas |

## What closes the round

Each track's session closes its own track with a closing report in its next interval folder. The round closes through `/project-state-keeping` once both tracks have closed and their branches are merged, as Nicolas decides.

## Amendments

None yet.
