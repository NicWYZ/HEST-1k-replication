# D0 expansion proposal

Round 3, stage D0. Prepared for Nicolas Weiyang Zhang. Nothing has been downloaded and nothing in the repository has been modified by this memo.

All figures below were read back from the stage D0 tables committed at `9f86dbd` under `results/round3/D0_inventory/`. Each paragraph names the file it came from. Where a count is not printed directly in a table, it was recomputed from `results/round3/D0_inventory/hest_inventory.csv` and is marked as such.

## 1. What is being asked

Approve, redirect, or reject the download of a designed 86-sample subset of HEST-1k totalling about 48 GB, covering four data components and no whole-slide images. The three sets inside it are the institution set for Topic A's lab axis, the donor-power set for Topic B, and the platform-pair set for a platform-shift axis, as specified in `docs/round3_execution_plan.md` section 4.9. The download itself is stage D1 in section 4.10 and does not start until you approve.

There is one real decision in here, and it is in section 4. The handoff asked the institution set to have at least three generating laboratories with at least three donors each. That is not satisfiable anywhere in HEST-1k on the labels available now. You need to choose which half of the criterion to relax.

## 2. The release used, and what changed from the one on disk

From `results/round3/D0_inventory/inventory_report.json` and `hf_repo_state.json`. The inventory was built on `HEST_v1_3_0.csv`, sha256 `5703d7169c7a31aa4cc74a900df9179326e0cc51bda617a1cf7ac179b6ed5d63`, pulled at HuggingFace revision `7e8d5a0b0aace41d8c8ec0f6ecea80e4ad2a61ec` of `MahmoodLab/hest`. That release has 1276 samples. The file listing returned 15608 files, of which 12 are repository-level files that belong to no sample, such as the release tables themselves and the README.

The project's on-disk table, the one R5b read, is `code/HEST/assets/HEST_v1_1_0.csv` with 1229 samples. Comparing the two copies held in `results/round3/D0_inventory/release_tables/`, v1_3_0 adds 47 sample ids and drops none. Six ids that exist in both have a different patient label in the newer release. Four of them are bowel samples in the same 10x study, TENX152 through TENX155. The two that matter to this project are TENX147, which moved from Patient 1 to Patient 5, and TENX148, which moved from Patient 1 to Patient 2. TENX149 is Patient 1 in both.

## 3. The benchmark cross-check

From `results/round3/D0_inventory/inventory_report.json` and `benchmark_crosscheck.csv`. All 72 benchmark samples were found in the v1_3_0 inventory, none missing. The resolution flag agrees on all 72. Exactly two cells disagree with the metadata the benchmark used, and both are the COAD patient labels just described, TENX147 and TENX148.

This is corroboration rather than a problem. Round 2's R5b donor audit concluded independently, from 10x and GEO source records, that the three COAD slides come from three different donors and not from one. Upstream HEST has now made the same correction in its own table. The project's audit and the current release agree, and the benchmark copy the project started from is the stale one.

## 4. The institution criterion, and the decision

From `results/round3/D0_inventory/organ_technology_ranking.csv`, which has 46 organ-by-technology cells, and from `expansion_candidates.csv`.

The ranking carries two separate columns, the number of resolved laboratories holding at least three samples in the cell, and the number holding at least three HEST-labelled donors. Across all 46 cells, the largest value the donor column ever reaches is 2. Two cells reach it, Kidney on Visium and Breast on Spatial Transcriptomics. Only one cell in the whole archive has three or more laboratories at three or more samples each, and that is Kidney on Visium with four. So the criterion as written, three laboratories each with three or more donors, is not satisfiable in HEST-1k on the labels available now. Not in the chosen cell and not in any other.

Kidney on Visium holds 58 samples across five provisional laboratory attributions, of which Sorbonne Université has 24 samples and 24 donors, Washington University School of Medicine has 23 samples and 22 donors, Indiana University School of Medicine has 7 samples and no usable donor label at all, KTH Royal Institute of Technology has 3 samples and no donor labels, and a 10x vendor product page accounts for 1. The proposed institution set takes the first three of those and is 54 samples, per `expansion_candidates.csv`. KTH's three were excluded because all of their kidney Visium samples are disease state Treated, which in this cell means fixed organoid material rather than donor tissue, and the vendor page was excluded because a product page is not a generating laboratory. Both exclusions are written into the selection rule in that file.

So your reading is right. Three laboratories qualify on sample count, two of them carry donors, and the third arm has samples and no donor labels.

There is a second problem in this set that I think is more serious than the donor gap, and it is the round-2 lesson repeating. Recomputed from `results/round3/D0_inventory/expansion_set_members.csv`, the `resolution_uncertain` flag inside the institution set is constant within every laboratory. Sorbonne has 0 of 24 flagged, Washington University has 23 of 23 flagged, and Indiana has 7 of 7 flagged. A lab contrast in which one arm has embedded pixel sizes and the other two have estimated ones is also a scan-metadata contrast, which is close to the confound that forced the round-2 withdrawal.

The alignment is worth reading one level finer, because it is not symmetric across the three arms and the asymmetry decides what this set can actually measure. The flag separates Sorbonne from the other two and does not separate Washington University from Indiana. So any contrast involving Sorbonne, which is to say any contrast that has donors on both sides, is also a pixel-size-provenance contrast; and the one lab contrast in this set that is free of the flag, Washington University against Indiana, is exactly the one where an arm has no donor labels. On the labels available now the set cannot give a lab contrast that is both donor-resolvable and clean of the resolution confound. That is the strongest reason to prefer option 2 in section 9 and let D3 decide the framing, and it is a stronger argument than the donor gap on its own. It does not make the set unusable, and it means D4 cannot report a lab term from this set without the pixel-size provenance written beside it.

One more thing worth seeing before you decide. Of the institution set's 54 samples, 24 are already in the benchmark, and all 24 are the Sorbonne arm, which is the existing CCRCC task. The new evidence in this set is the Washington University and Indiana arms.

## 5. The three sets

All counts in this section are from `results/round3/D0_inventory/expansion_candidates.csv`. Per-sample membership is in `expansion_set_members.csv`, 133 rows across the three sets.

**Institution set, `institution_kidney_visium`.** Kidney on Visium, human only, duplicate ids removed, every sample from the three qualifying institutions. 54 samples, 46 HEST-labelled patients, 7 samples with no patient label, 3 cohorts, 3 provisional laboratories as listed above. 24 samples are already in the benchmark. 30 of the 54 carry an uncertain pixel size. 21.8 GB across the four components. This is the Topic A lab axis.

**Donor-power set, `donor_power_kidney_visium`.** The organ and technology cell with the most distinct labelled donors, restricted to samples that actually carry a usable label, with a donor keyed on the pair of dataset title and patient label. It lands on the same cell, Kidney on Visium, and is essentially the institution set with the unlabelled Indiana arm removed. 47 samples, 46 donors, no missing labels, 2 cohorts, Sorbonne and Washington University. 24 already in the benchmark, 23 with an uncertain pixel size, 20.0 GB. For Topic B this roughly doubles the donor count available in any current benchmark task, which is at most 24.

**Platform-pair set, `platform_pair_multitech`.** Every human sample whose publication profiled the same tissue on more than one spatial technology, selected by study rather than by organ, because a platform contrast is only interpretable inside a study that ran both platforms. 32 samples spanning bowel, breast, lung and skin, and five technologies including Visium, Visium HD, Xenium and Xenium 5k. 11 labelled patients, 5 samples with no label, 6 cohorts, 3 provisional laboratories, which are 10x Genomics with 12 samples and 6 donors, Stanford with 16 samples and 5 donors, and TGen with 4 samples and no donor labels. 5 already in the benchmark, 19 with an uncertain pixel size, 25.8 GB. This set is the weakest on donor labels and its 10x arm is a vendor company rather than an academic laboratory, so it should be read as a platform axis and not as a second institution axis.

**Union, which is the storage ask.** 86 samples, 57 labelled patients, 12 with no label, 9 cohorts, 6 provisional laboratories, 49 samples with an uncertain pixel size, 29 already in the benchmark, 47.7 GB.

## 6. The storage ask against the filesystem

From `results/round3/D0_inventory/expansion_candidates.csv` for the ask itself,
`results/round3/D0_inventory/inventory_report.json` and `storage_context.txt` for the archive and
filesystem totals, with the unit conversions and fractions recomputed from
`results/round3/D0_inventory/hest_inventory.csv`. Every converted or divided figure in this section
is recorded in `.verify-exceptions` with the raw byte value and the arithmetic it came from, since
the raw values rather than the converted ones are what the tables hold.

The ask is 47,654,363,040 bytes, so about 48 GB, for `patches/`, `st/`, `cellvit_seg/` and `metadata/` on 86 samples. The whole archive at this revision is 2.01 TB across all components. Those same four components across all 1276 samples would be 443.8 GB, so the ask is about 11 percent of the four-component archive and about 2.4 percent of the whole thing.

The reason the rest is not needed is mostly one component. Whole-slide images are 1.14 TB, about 56 percent of the archive, and the pipeline does not read them once patches exist. The four components the project does use are 22 percent of the archive, and of those the ask takes the designed 86 samples rather than all 1276.

On the filesystem, `/work` is 3.6 PB with 559 TB available at 85 percent used, and the project tree at `/work/users/w/e/weiyang/hest_replication` is currently 82.2 GB. Adding 48 GB grows the project tree by roughly 58 percent and is negligible against `/work`. The home filesystem is at 4.2 GB of a 51.2 GB soft quota and is not where this lands. No per-user `/work` quota is reported by any tool on that host, which is recorded in `storage_context.txt` and is itself a small risk, since an unreported quota is not the same as no quota.

A possible reduction. 29 of the 86 are already in the benchmark subset on disk. I did not verify that the on-disk copies are the same four components at the same revision, so I am not proposing to skip them. If D1 checks that and they match, the transfer shrinks accordingly.

## 7. Label quality, as measured

From `results/round3/D0_inventory/inventory_report.json`, `duplicate_groups.csv` and `study_affiliations.csv`, with the reuse counts recomputed from `hest_inventory.csv`.

Patient labels. Of 1276 samples, 292 carry a usable label, 870 have none at all, and 114 carry a label field that is present but is only whitespace. That third category is the dangerous one, because a non-null whitespace string passes a naive null check. The largest blocks of it are a cardiac cohort with 41, COLON MAP with 41, a lung atlas with 20 and spatialLIBD with 12.

Label reuse. Among human samples there are 78 distinct patient label strings, and 27 of them appear in more than one cohort, spanning 23 of the 29 human cohorts that carry labels at all. Strings like Patient 1 are reused freely across unrelated studies. A donor therefore has to be keyed on the pair of dataset title and patient label, not on the label string, and that is how `donor_key_provisional` is built in the inventory. Keyed that way, the 292 labelled samples resolve to 158 distinct human donor keys.

Duplicates. There are 40 groups of ids that share at least one identical file blob, and in 15 of those groups the shared blob includes the expression data, meaning the two ids are the same measurement under two names. Fourteen of the 15 are MEND and NCBI pairs in one FFPE cohort, and the fifteenth is NCBI599 and NCBI714, which sit in two different kidney cohorts. Fifteen ids are flagged as duplicates in the inventory and the candidate sets were built after removing them, so NCBI714 appears in the kidney sets and NCBI599 does not. Any expansion done outside these sets has to repeat that removal, because an undetected duplicate pair would put the same measurement in both the training and the test arm of a split.

Affiliations. Of 58 distinct studies, 41 were resolved to a last-author affiliation. Twelve could not be resolved to a publication at all, and five more resolved to a publication with no last-author affiliation recorded. Resolution went through DOI to PubMed for 21 studies, a PMCID in the link for 12, a PMID in the link for 9, Crossref for 3, and a title search for 1. Every laboratory attribution in this memo rests on that chain and none of it has been checked against a source record.

Pixel size. 1074 of the 1276 samples carry the `resolution_uncertain` flag, and 31 of the 72 benchmark samples do. This is the archive's normal state rather than a property of the chosen sets.

## 8. Recommendation

Approve the union as the download, and accept the institution set as a two-arm donor-separable contrast with a third arm that contributes samples but not donors.

The reasoning is that the alternative cells are worse on the axes that matter. Breast on Spatial Transcriptomics has 108 samples and also reaches two qualifying laboratories, but every one of its 108 samples carries an uncertain pixel size, it has 31 donors against kidney's 46, and none of it touches the existing benchmark, so it buys no continuity with round 2 and costs the same confound. Brain on Visium, which the review named as a candidate, has 42 samples and two laboratories at three or more samples but zero laboratories with three or more donors, 28 of its 42 have no patient label, and two of its five attributions are unresolved studies, so it is the weakest cell on exactly the labels this project has learned to distrust. Breast on Visium, the review's other candidate, is 8 samples, all attributed to 10x, with no donor labels, and is not viable. Lung on Xenium is clean on pixel size, with 0 of 24 uncertain and 21 donors, but it has a single qualifying laboratory, so it cannot carry a lab axis at all.

Kidney on Visium is the only cell where three laboratories exist, it has the most donors, and 24 of its samples are the CCRCC task the project already knows, which gives D4 a within-set anchor. Getting the third arm's donor labels is a reading job for D3 on 7 samples, not a reason to change cell.

Two conditions I would attach. First, D4 must not report a lab term from the institution set without the pixel-size provenance reported alongside it, given the perfect alignment in section 4. Second, if D3 cannot recover donor labels for the Indiana arm from source records, that arm stays in the set for sample-level contrasts and is excluded from anything that groups by donor, and the set is described as two donor-resolvable laboratories throughout, never as three.

## 9. The options you actually have

1. Approve as proposed. 86 samples, 47.7 GB, a kidney lab contrast with two donor-labelled arms and one arm of 7 samples without donor labels. Cost is that the handoff's criterion is met on samples and not on donors, and it has to be described that way in every downstream report.
2. Approve but wait for D3 before committing to the lab axis. Download the union anyway, since it is needed for Topic B regardless, and let the audit decide whether Indiana becomes a real third arm. This costs no extra storage and delays only the D4 framing. It also gives D3 the chance to reinstate the KTH samples or find that the Treated exclusion was right.
3. Redirect to Breast on Spatial Transcriptomics. Two laboratories, 108 samples, 31 donors, 17.3 GB. Cost is all 108 samples with an uncertain pixel size, no overlap with the benchmark, and still only two laboratories, so it does not fix the criterion either.
4. Change the axis. Drop the institution set for round 3 and keep the donor-power and platform-pair sets, which is 47 plus 32 samples before overlap. Cost is that Topic A's lab axis, which is the input to round 4, does not get measured this round.

My order is 2, then 1, then 4, and I would not take 3.

## 10. What I did not check, and what stays provisional

Every laboratory attribution in this memo comes from a publication's last-author affiliation, resolved automatically, with 41 of 58 studies resolved and none verified by hand. A last author's affiliation is not always the generating laboratory, and for multi-site studies it is often wrong. Stage D3 audits this against source records and may change any lab count here, including the count of three in the institution set.

Every donor count rests on HEST's patient field, which the benchmark cross-check has already shown to be wrong in two cells of the 72 the project knows best. The donor counts are provisional in the same way.

I did not download or open any sample. All byte counts are from the HuggingFace file listing at the recorded revision and none has been verified against a transferred file. I did not verify that the 29 union samples already in the benchmark match the on-disk copies component for component. I did not re-derive the resolution flag, only counted it. I did not check the mouse portion of the archive at all, since the sets are human only, and I did not check whether the 47 ids new in v1_3_0 affect any round-2 result, only that none were removed.
