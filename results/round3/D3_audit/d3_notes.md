# D3 — donor and laboratory audit of the expansion sets, against source records

**Scope.** Reading stage, no compute. One row per sample in
`donor_lab_audit_ext.csv`: the 18 breast Xenium IDC samples, the 54 kidney Visium
samples of the analysis set, and the four held-out kidney additions, 76 rows. Every
verdict cites the record it was read from, in the row's `citation` field. Where a
source says nothing on a question the cell says so rather than carrying an inferred
value. The builder `code/scripts/round3_d3_build_audit.py` joins these verdicts to
HEST's own fields from `results/round3/D0_inventory/hest_inventory.csv` so the
HEST-side columns cannot drift; it performs no network access and no inference.

`results/round2/R5b_audit/donor_audit.csv` was not modified. Two findings below bear
on benchmark samples and are recorded as escalations in section 6.

## 1. Breast Xenium IDC — the eleven TENX191 to TENX202 samples

The inventory's `study_link` for these eleven is
`https://www.biorxiv.org/content/10.64898/2025.12.08.692193v1`. The prefix 10.64898 is
not bioRxiv's familiar 10.1101, but it resolves: Crossref and the bioRxiv details API
both return the record, and the JATS source XML is served at
`biorxiv.org/content/early/2025/12/11/2025.12.08.692193.source.xml`. The preprint is
Janesick AS, Kravitz SN, Stauffer W, Valencia M, Taylor SEB, *Biomarker Quantification
in Breast Cancer using Xenium In Situ*, posted 11 December 2025, corresponding author
institution 10x Genomics.

**Laboratory.** 10x Genomics. Corresponding-author institution on the bioRxiv record;
the acknowledgements thank named 10x Genomics colleagues; the H&E images and alignment
files are hosted on a 10x dataset page. `lab_label_status` is verified. HEST's
`lab_provisional` for these eleven reads `unresolved: <the bioRxiv URL>`, so this
resolves an open field rather than contradicting one.

**Scanner.** Stated: post-Xenium H&E slides "were imaged on an Olympus VS200 scanner",
converted VSI to OME.tif in QuPath 0.5.1. Instrument operation followed the Xenium
Analyzer user guide with onboard analysis software version 4.0. No objective
magnification and no pixel size are stated anywhere in the preprint or its supplement.

**Section provenance, and the donor finding.** The Methods say the set "comprised 11
blocks representing a range of breast cancer stages and grades, including both DCIS and
invasive lesions, as well as one normal breast tissue sample", that H&E images exist
"for all 12 sections", and that the analysis ran "across tumor cells from all 11 breast
cancer sections (excluding normal - #S2-Top)". Supplemental Table S1 lists twelve
sections, S1-Top through S4-Bottom, each with its own disease, TNM stage, grade and
hormone status:

| section | HEST id | disease | stage | grade | hormone status |
|---|---|---|---|---|---|
| S1-Top | TENX191 | IDC | T3 N0 M0 | G3 | HER2-Neg |
| S1-Middle | TENX192 | DCIS | T2 N0 M0 | G2 | ER+/PR+/HER2-2+ |
| S1-Bottom | TENX193 | DCIS | T1c N0 M0 | G3 | HER2-1+ |
| S2-Top | *absent from HEST* | Normal | NA | — | HER2-Neg |
| S2-Middle | TENX195 | DCIS | T1c N1 MX | G2 | HER2-2+ |
| S2-Bottom | TENX196 | DCIS | Tis NX MX | G3 | HER2-3+ |
| S3-Top | TENX197 | CCH/DCIS | Tis N0 | G2 | ER+/PR+/HER2-1+ |
| S3-Middle | TENX198 | DCIS | T4b N3a M1 | G2 | ER+/PR+/HER2-2+ |
| S3-Bottom | TENX199 | DCIS | TX NX M0 | G2 | ER-/PR-/HER2-2+ |
| S4-Top | TENX200 | IDC | Tis NX MX | G3 | ER+/PR+/HER2-1+ |
| S4-Middle | TENX201 | IDC | T2 N0 MX | not stated | ER+/PR+/HER2-2+ |
| S4-Bottom | TENX202 | DCIS | T4a N2a | G3 | HER2-1+ |

Eleven cancer sections, eleven cancer blocks, twelve distinct clinical profiles. The
missing twelfth is the normal sample S2-Top, and the missing HEST id is TENX194, which
appears in none of the five release tables. The eleven ingested samples are exactly the
eleven cancer sections.

HEST labels these eleven `Patient 1` to `Patient 4`, grouping the three sections of each
Section number together. That grouping is **contradicted**: the source gives each
section its own block and its own clinical profile. The natural reading of the naming is
that S1 to S4 are the four Xenium slides and top, middle and bottom are the three tissue
pieces placed on each slide, which is consistent with a Xenium slide's imageable area
and with the eleven-blocks statement. The step the source does not take explicitly is
from block to donor: it says eleven blocks, not eleven donors, and the biobank sources
(Avaden, BioIVT, Discovery Life Sciences) are given for the set as a whole rather than
per section. Eleven distinct donors is the reading the clinical table supports and is
what `donor_id` carries, one per section; it is not a quoted statement.

This changes the expansion set's donor count for this source from four to eleven. It is
not a benchmark escalation, because none of the eleven is in the benchmark.

**Disease is not fixed.** HEST assigns oncotree code IDC to all eleven. Table S1 makes
three of them IDC (S1-Top, S4-Top, S4-Middle), seven DCIS, and one CCH/DCIS. Any round-3
document that describes the breast Xenium set as holding disease fixed across its two
sources is wrong: one source is seven-eighths in-situ disease and the other is invasive
carcinoma throughout. § 12.6's description of this cell as "disease, platform and
preservation fixed" holds for platform and preservation only.

## 2. Breast Xenium IDC — the TENX95 / TENX97 / TENX98 / TENX99 question

**The memo's reading is correct and round 2's is wrong.** HEST maps the four ids like
this, identically in all five release tables `HEST_v1_1_0` through `HEST_v1_3_0` in
`results/round3/D0_inventory/release_tables/`:

| HEST id | dataset title | subseries | HEST patient |
|---|---|---|---|
| TENX95 | FFPE Human Breast with Pre-designed Panel | Tissue sample 1 | patient 2 |
| TENX97 | FFPE Human Breast with Custom Add-on Panel | Tissue sample 1 | patient 2 |
| TENX98 | FFPE Human Breast using the Entire Sample Area | Replicate 2 | patient 1 |
| TENX99 | FFPE Human Breast using the Entire Sample Area | Replicate 1 | patient 1 |

So the vendor's "Replicate 1" and "Replicate 2" name the two large sections of the
*entire sample area* dataset, which HEST ingests as TENX99 and TENX98. Round 2's
`docs/r5_idc_provenance.md` states in its § 1 table that TENX95 is that dataset's
Replicate 2 and TENX99 its Replicate 1, and concludes in its § 4 escalation that
TENX95 and TENX99 are two serial sections of one block. Round 2's own extracted
`results/round2/R5b_audit/hest_source_map.csv` already carried the correct titles, so
the error was in the document, not in the extraction.

**Primary confirmation.** `www.10xgenomics.com` is behind a bot challenge that returns
HTTP 429 with a "Vercel Security Checkpoint" body on every attempt, in this session as
in round 2's four logged attempts, so the dataset pages themselves remain unread. The
dataset file CDN `cf.10xgenomics.com` was reachable after a one-time access grant, and
it serves the per-run metadata that the pages summarise:

| region | run_name | slide_id | cassette | run start | cells | region area (µm²) | panel |
|---|---|---|---|---|---|---|---|
| Xenium_V1_FFPE_Human_Breast_IDC | human_breast_ffpe_predesigned_and_addon | 0002429 | SIM1 | 2022-11-10T00:30:50Z | 574,852 | 90,361,596 | hBreast_v1, 280 + 0 |
| Xenium_V1_FFPE_Human_Breast_IDC_With_Addon | human_breast_ffpe_predesigned_and_addon | 0002807 | SIM2 | 2022-11-10T00:30:51Z | 574,527 | 96,168,606 | V2RIPM hBreast_v1_AddOn100g, 280 + 100 |
| Xenium_V1_FFPE_Human_Breast_IDC_Big_1 | human_breast_ffpe_large_sections | 0002178 | SIM1 | 2022-12-02T22:21:44Z | 892,966 | 228,050,908 | hBreast_v1, 280 + 0 |
| Xenium_V1_FFPE_Human_Breast_IDC_Big_2 | human_breast_ffpe_large_sections | 0002169 | SIM2 | 2022-12-02T22:21:44Z | 885,523 | 221,212,453 | hBreast_v1, 280 + 0 |

Two runs, two regions each. The "large sections" run's regions are 2.4 times the area of
the November run's and are the ones the page calls Replicate 1 and Replicate 2. Round 2
quoted 892,966 cells for "Replicate 1" and 885,523 for "Replicate 2"; those are Big_1
and Big_2, so round 2 had the vendor's numbers right and the HEST ids attached to them
wrong. The same CDN route also shows the January 2023 datasets were run on a production
instrument, `instrument_sn` XETG00001, software 1.0.0.3, whereas the Janesick preview
replicates carry `instrument_sn` "Xenium prototype instrument" and software
"Development" — a real instrument-generation difference between the 10x vendor samples
and the Janesick samples inside this set.

**Which block is which.** The vendor pages' tissue descriptions could not be read
directly. The QuST paper (arXiv:2406.01613) quotes them in its data-availability
section: the *entire sample area* dataset is a 5 µm section of an infiltrating ductal
carcinoma resected tumour mass from Avaden Biosciences, and the *custom add-on panel*
dataset a 5 µm section of infiltrating ductal carcinoma with ductal carcinoma in situ
from BioIVT. That is a secondary source quoting a primary page, and it is labelled as
such in the citation column. It also explains round 2's Avaden attribution: Avaden
belongs to the entire-sample-area block, that is TENX98 and TENX99, not TENX95.

**Answer.** The replicate pair is TENX98 and TENX99, from the Avaden block. TENX95 and
TENX97 are two sections of a separate BioIVT block run five weeks earlier, differing
from each other in panel (pre-designed 280 against 280 plus a 100-gene add-on) and in
slide, not in donor. HEST's patient 1 and patient 2 labels for the four agree with the
source and are recorded as verified. Consequence for the benchmark IDC task, which uses
TENX95, TENX99, NCBI783 and NCBI785: those four are four distinct donors, and round 2's
escalation that two of them share a block does not hold.

**The three Janesick samples.** Nat Commun 14:8353 (2023) states Sample #1 as an FFPE
block, TNM T2N1M0, ER+/HER2+/PR−, collected 2021-07-26, from Discovery Life Sciences,
with Xenium "performed in replicate on two serial sections"; Sample #2 as a block, AJCC
pT2 pN1a pMX, ER−/HER2+/PR−, collected 2009-07-24, from the same provider, and calls it
"a different biological section (different donor)". HEST's subseries assign NCBI785 to
Rep 1 and NCBI784 to Rep 2 of Sample #1, and NCBI783 to Sample #2. Patient 4 for the two
replicates and patient 5 for Sample #2 are verified. The paper states no H&E brightfield
scanner and no H&E pixel size; the 40x dipping objective it names is on a Zeiss
Axioimager used for the post-Xenium immunofluorescence, not the H&E scan, and the
"~200 nm per-pixel" figure describes the Xenium Analyzer's imager.

**Donor structure of the 18-sample set as audited.** Fifteen donor groups: eleven
biomarker sections, the Avaden block (TENX98, TENX99), the BioIVT block (TENX95,
TENX97), Janesick Sample #1 (NCBI784, NCBI785) and Janesick Sample #2 (NCBI783). Not
the "two sources with four donors each" of § 12.6. And both sources are the same
generating laboratory, 10x Genomics, so a `source_out` arm on this set separates two
studies from one company, not two laboratories. Under § 12.5's rule, no report may call
it a laboratory term.

## 3. Kidney Visium — the Washington University and Indiana samples

**The laboratory attribution is wrong for 23 of 54 samples.** HEST attributes the 23
samples NCBI692 to NCBI714 to Washington University School of Medicine. The GEO record
they come from, GSE183456, *Spatial localization with Spatial Transcriptomics for an
atlas of healthy and injured cell states and niches in the human kidney [Visium ST]*,
lists contributors Michael Eadon, Ricardo Melo Ferreira and Ying-Hua Cheng, and a
contact institute of **Indiana University**. Its overall design describes the same
imaging setup as the papilla study's, a Keyence BZ-X810 with a Nikon 10× CFI Plan Fluor
objective. Washington University is where the parent atlas paper's senior authorship
sits; it is not where this subseries was generated. `lab_label_status` is contradicted
for all 23. The other 31 kidney samples are verified: the seven papilla samples are
Indiana as HEST says, and the 24 ccRCC samples are the Cordeliers group in Paris, which
GSE175540 gives as UMR-S 1138 Centre de Recherche des Cordeliers and HEST records as
Sorbonne Université, the same unit under a different name.

**Consequence.** § 12.6's "Washington University against Indiana pair" is not a
laboratory contrast. Both arms were generated by the same Indiana laboratory on the same
instrument with the same objective. This is the round-1 failure mode repeating: an
institution label taken from a paper's senior affiliation rather than from the record of
who ran the assay. The kidney set's only defensible source axis is tumour against
non-tumour, that is the 24 Cordeliers ccRCC samples against the 30 Indiana samples,
which is what § 12.5 already calls `population_out`; and that contrast is confounded by
preservation (see below), by disease, and by anatomical region.

**Specimen provenance inside the 23.** GSE183456's extract protocol states that four
reference tissues (18-0006, 19-F52, 19-M61, 19-M32) from deceased-donor nephrectomies
and one CKD biopsy (20-13437) came from the Biopsy Biobank Cohort of Indiana, and that
"All remaining samples were provided by the Kidney Precision Medicine Project", a
multi-site consortium. The GEO sample titles use a different form of the same ids
(IU-F52, IU-M61, IU-M32, IU-13437), so the biobank list and the sample list do not line
up one to one; 18-0006 has no obvious counterpart among the six reference titles. What
this means for the audit is that specimen collection for most of the 23 was distributed
across KPMP recruitment sites while generation was at Indiana, so "institution" is two
different things for these samples and the file records the generating laboratory.

**Per-sample disease, donor and region.** From the 23 GEO sample records: six Reference
(deceased-donor nephrectomy), eleven Diabetic Kidney Disease, six Acute Kidney Injury.
Lake et al.'s Methods give the same split as "Nephrectomy (n = 6), AKI (n = 6) and CKD
(n = 11)" and state that "These 23 samples represent 22 participants because 2 samples
(1 cortex and 1 medulla) were obtained from the same participant with CKD". That pair is
NCBI702 (28-12265-Cortex) and NCBI701 (28-12265-Medulla), which HEST already labels
Patient 13 twice. All 23 donor labels are verified. Region is stated per sample only for
that pair; the paper says of the 23 that "18 samples were composed of only cortex, 4
samples were a combination of cortex and medulla and 1 sample was completely medulla"
without naming which, so the other 21 rows read "not stated per sample in source".
Preservation for all 23: fresh frozen, OCT-embedded, stored at −80 °C, 10 µm sections.

**One sample is in HEST twice.** NCBI714 (IU-F59) shares every shipped component with
NCBI599, from the earlier Indiana study *Integration of spatial and single cell
transcriptomics localizes epithelial-immune cross-talk in kidney injury*, per D0's
`duplicate_groups.csv` (same expression file, same WSI, same patches, same pixel size
0.757192, same 3,007 spots). The same physical sample sits in HEST under two study
titles, one attributed to Indiana and one to Washington University. NCBI599 is not in
any round-3 set, so nothing needs to change, but it is a second illustration that HEST's
study-level attribution does not track the generating laboratory.

**The papilla samples, and the four slides that are not one donor.** The seven papilla
samples come from GSE231630, contact institute Indiana University, Michael Eadon.
Disease from the GEO records: 20-0034 is Reference, a papillary nephrectomy; the other
six are calcium oxalate stone disease. Region is renal papilla for all seven;
preservation is fresh frozen, OCT at −80 °C. **Four of the seven are not single-donor
samples**, in two different ways. Only NCBI562 (M50), NCBI567 (KRP428) and NCBI568
(20-0034) are verified single-donor samples, the three the GEO description calls "Single
sample".

Known mixtures, where the study kept every piece's spots and separated them itself:

- **NCBI564** ("KRP446 (M) - KRP462 (F) - KRP475 (F)"): the GEO description reads "Three
  samples included within the fiducial zone", from three different donors, and says
  "Spots associated to each sample were separated during data processing". HEST ingests
  the whole capture area as one sample, so this HEST sample is a three-donor mixture.
- **NCBI563** ("F59 - F63"): "Two samples included within the fiducial zone", two donors,
  again separated during the study's processing but not in HEST.

Co-resident second donor, where the study restricted its own analysis but HEST's
ingestion is not described:

- **NCBI566** (KRP449) and **NCBI565** (KRP429): each capture area carried a second
  donor's piece (KRP440, a brushite case, and KRP478), and the GEO description states
  that only the named sample's spots "were used in the conduct of this experiment". That
  is a statement about the study's analysis, not about HEST's ingestion, and no source
  reached says whether HEST's spot set for these two is restricted the same way.

All four are marked `contradicted` in the audit file and none of the four may be used as
a donor unit. The distinction matters for how a downstream stage would remedy it: for
NCBI563 and NCBI564 the defect is a known mixture that could in principle be split by
re-deriving the per-piece spot assignment, whereas for NCBI565 and NCBI566 the defect is
an unquantified risk of contamination by a second donor's spots, which cannot be checked
without a per-spot comparison against the study's own restricted spot list. Neither
remedy was attempted inside the cap. An earlier draft of this section recorded NCBI565
and NCBI566 as verified; that was wrong and contradicted the audit file's own verdicts.

The papilla study's "F59" and the atlas's "IU-F59" share a string. They are different
specimen types in different cohorts, a calcium-oxalate papilla and a reference
nephrectomy, and no source consulted links them to one donor. They are left as separate
donors and the coincidence is recorded here rather than acted on.

**The 24 Cordeliers ccRCC samples.** GSE175540's per-sample records give only "disease
state: renal cell cancer" and "tissue: ccRCC tumor". The series states no donor,
patient or participant identifier, and notes that raw data were withheld for patient
privacy. HEST labels them Patient 1 to Patient 24, one per sample; the record neither
supports nor contradicts that, so all 24 are `unverifiable` here. Round 2's
`donor_audit.csv` records the same 24 as `verified` against the same accession, which is
stronger than the record supports; see escalation 6.2. The sample names carry a cohort
letter and a number, and exactly one number repeats across preservation types,
`ffpe_c_2` and `frozen_c_2`, which are HEST INT24 and INT4. Whether those two are one
donor profiled twice cannot be settled: Meylan et al. 2022 *Immunity* is not open access
(Unpaywall reports no OA location, there is no PMC record), and HEST's download link for
these samples is "None (internal)".

**Preservation is not fixed inside the ccRCC arm.** Twelve of the 24 sample titles begin
`ffpe_` and twelve begin `frozen_`, while the series' own overall-design line says
"Spatial transcriptomics of fresh frozen ccRCC human tumors" for all of them. HEST's
`preservation_method` field is empty for all 24. The file records the title-derived
value and flags the internal contradiction in the source. Any kidney arm that puts these
24 against the 30 Indiana samples differs in tumour status, laboratory, country,
anatomical region, disease, and preservation for half of one arm.

## 4. `resolution_uncertain` re-derived from source

Across the 72 samples of the two analysis sets, plus the four extras:

| re-derived | n | what it means |
|---|---|---|
| False | 34 | the source states a pixel size or an instrument-plus-objective that HEST's estimate matches |
| True | 1 | the source is silent and HEST's own two values disagree materially |
| unresolved | 16 | the source states neither a pixel size nor an objective; HEST's flag can be neither confirmed nor cleared |
| not_derivable | 25 | no source record reached at all on imaging |

Thirty-two samples that HEST flags `resolution_uncertain = True` clear against source:
TENX95, TENX99, and all thirty kidney Visium samples from the two Indiana studies. The
mechanism differs between them.

- **TENX95 and TENX99.** HEST's `pixel_size_um_embedded` is 1.0 for both, a fallback
  value, against an estimated 0.2125; that 370 per cent disagreement is what set the
  flag. The Xenium run metadata states `pixel_size` 0.2125 µm for all four of the 10x
  breast runs, and HEST's estimate is 0.2125 exactly. Their siblings TENX97 and TENX98
  carry 0.2125 in both fields and were never flagged. The flag is an artefact of the
  embedded field, not a property of the image.
- **The thirty Indiana kidney samples.** All thirty carry
  `pixel_size_um_embedded = 0.352778` against estimates in the range 0.756615 to
  0.759491, a 53 per cent disagreement, which set the flag. The papilla paper states
  outright that "H&E-stained sections were imaged with a Keyence BZ-X810 microscope
  equipped with a Nikon 10× CFI Plan Fluor objective at 0.7547 µm/pixel and image
  resolution of 1920×1440". Every one of the thirty estimates is within 0.7 per cent of
  0.7547, so it is the embedded value that is wrong. For the seven papilla samples the
  number comes from their own paper. For the 23 atlas samples GSE183456 and Lake et al.
  state the same instrument and the same objective but no number, so the numeric
  comparison borrows the sibling paper's figure from the same laboratory; that is
  recorded in each row's `pixel_size_source` rather than presented as a statement of
  the atlas.

HEST's `magnification` field reads 20x for all thirty Indiana kidney samples. Both
sources state a 10× objective. That field is contradicted for all thirty.

One sample moves the other way in effect: **NCBI784** keeps `True`. Its embedded 0.2125
and estimated 0.363788 differ by 41.6 per cent, the Janesick paper states no H&E pixel
size or scanner, and its embedded value happens to equal NCBI785's estimated value,
which looks like an off-by-one in HEST's metadata rather than a property of either
image. It is the one sample where the flag is both set and unresolvable from source.

The 25 `not_derivable` rows are the 24 ccRCC samples and TENX71: no methods text and no
vendor page was reached for either. The 16 `unresolved` rows are the eleven biomarker
sections (Olympus VS200 stated, no objective or pixel size), NCBI783 and NCBI785, and
the three KTH organoid samples.

## 5. The four held-out kidney additions

**NCBI538, NCBI539, NCBI540 — fixed organoid material, not tissue.** HEST's subseries
strings are literally `PFA fixed kidney_organoid_1`, `_2`, `_3`. Gracia Villacampa et
al., *Cell Genomics* 1(3):100065 (2021), PMC9903805, confirms: "we used non-infected,
PFA-fixed lung and kidney organoids embedded in optimal cutting temperature embedding
medium (OCT)"; "between 6 and 8 organoids (<1 mm in diameter) were embedded together to
fit within a single capture area (<42.25 mm²)"; and "3 tissue sections" were collected
from the block containing kidney organoids. So the three HEST samples are three
consecutive sections of one organoid block, not three independent units, and each
section carries six to eight separate organoids. HEST's `disease_state` "Treated" and
organ "Kidney" would mislead any analysis that treated them as kidney tissue. All three
are marked unverifiable on donor, because the organoid line's source is not stated in
the spans read. `pixel_size_um_embedded` is missing for all three, which is why HEST
flags them uncertain.

**TENX71 — not resolved.** The only source HEST names is the 10x Genomics dataset page
*Human Kidney, 11 mm Capture Area (FFPE)*, and `www.10xgenomics.com` is behind the same
bot challenge. This Visium dataset has no GEO accession, and the Xenium file-CDN route
that settled TENX95 to TENX99 does not apply, since those metadata files are
Xenium-specific. The generating laboratory is 10x Genomics in the sense that 10x
released the dataset, which is what HEST's `vendor_product_page` basis already says;
whether 10x also generated the tissue, and who provided it, could not be established.

## 6. Escalations

**6.1 Round 2's IDC escalation is withdrawn, and its provenance document is wrong.**
`docs/r5_idc_provenance.md` § 4 records that TENX95 and TENX99 are two serial sections of
one block from one donor, and `results/round2/R5b_audit/donor_audit.csv` gives both the
donor id `IDC_JanesickSample1` with status `contradicted`. Section 2 above shows the
mapping behind that conclusion is wrong in all five HEST release tables: TENX95 is the
pre-designed-panel dataset and TENX98, not TENX95, is the entire-sample-area Replicate 2.
The benchmark IDC task's four samples are four distinct donors. This **would change a
benchmark sample's donor label**, so per § 12.7 it is recorded here and in the A3 report
and `donor_audit.csv` is left frozen. Until the decision is taken, IDC folds built on
`donor_audit.csv` are grouping two donors as one, which makes IDC's `donor` design a
3-donor rather than a 4-donor design and merges the TENX95 and TENX99 folds.
`docs/r5_idc_provenance.md` is owned by the Housekeeping track this interval; this
finding reaches it through the lead, not through this track.

**6.2 CCRCC's donor labels are not sourced.** `donor_audit.csv` records all 24 CCRCC
samples as `verified` against GSE175540. That series states no donor identifier of any
kind. The grouping is not contradicted and no number changes if it is right, but it is
not evidence-backed, and one pair (`ffpe_c_2` and `frozen_c_2`, HEST INT24 and INT4)
shares a cohort letter and number across preservation types and could be one donor
profiled twice. CCRCC is the task with the largest K in the benchmark, so if that pair
merged, its `donor` design would go from six calibration units to five. Not resolvable
without the paper, which is paywalled. Recorded, not acted on.

**6.3 Two round-3 set descriptions do not survive the audit.** § 12.6 describes the
breast Xenium cell as "18 samples from two sources with four donors each, disease,
platform and preservation fixed", and names "the Washington University against Indiana
pair" for kidney. Sections 1 to 3 above contradict the donor count (fifteen groups, not
eight), the disease-fixed claim (the biomarker source is mostly DCIS), and the kidney
laboratory pair (one laboratory, not two). These are descriptions rather than committed
numbers, but D4 reads its contrasts off this file, so they are flagged here.

## 7. Sources that were unreachable

- **`www.10xgenomics.com`** — every dataset page. HTTP 429 with a "Vercel Security
  Checkpoint" body on all four attempts in this session, matching round 2's four logged
  attempts in `results/round2/R5b_audit/idc_fetch_log.tsv`. This is the origin's bot
  protection, not the sandbox allowlist, so no network-access request would help, and no
  header was changed to work around it. Affects: the tissue descriptions and donor-count
  metadata for TENX95, TENX97, TENX98, TENX99 (worked around via the file CDN and the
  QuST quotation) and the whole of TENX71 (not worked around).
- **`support.10xgenomics.com`** — blocked by the sandbox allowlist. Not requested: the
  file CDN answered the question it would have.
- **Meylan et al. 2022, *Immunity*, doi:10.1016/j.immuni.2022.02.001** — not open
  access. Unpaywall reports no OA location, Semantic Scholar returns only a DOI
  redirect, and there is no PMC record. Affects the 24 ccRCC samples' donor identity,
  scanner and pixel size.
- **`HEST_v1_1_0.csv` on Hugging Face** — gated, as round 2 recorded. Not needed this
  time: `results/round3/D0_inventory/release_tables/` holds all five release tables
  locally.

`cf.10xgenomics.com` was blocked by the allowlist and was granted on one request; it
supplied the decisive evidence in section 2.

## 8. What was not checked

- Whether HEST's ingested image for each Xenium sample is the post-Xenium H&E or the
  Xenium DAPI morphology image. The pixel-size comparison in section 4 assumes HEST's
  estimate refers to the same image the source describes; for TENX95 to TENX99 the
  source's 0.2125 µm is the Xenium morphology pixel size, and HEST's estimate equals it
  exactly, which is consistent with but does not prove that reading.
- Anatomical region for 21 of the 23 atlas kidney samples. The paper gives the counts
  (18 cortex, 4 cortex-and-medulla, 1 medulla) but not the assignment, and the
  per-sample GEO records do not carry a region field. A KPMP Data Atlas query might
  resolve it; not attempted inside the cap.
- Donor identity for the KTH organoid line, and whether the three organoid sections
  share a differentiation batch beyond sharing a block.
- Sex, age and ancestry fields present in some GEO records were not carried into the
  audit file; they are not needed for donor grouping and are not requested.
- No gene-panel recomputation. Round 2's panel counts in
  `results/round2/R5b_audit/r5_idc_panels_observed.csv` were read but not re-derived,
  and the CDN's `panel_num_targets_custom` values (0 for the pre-designed and
  large-section runs, 100 for the add-on run, 33 for the Janesick preview runs) are
  recorded here as a source statement without being reconciled against those counts.
  That reconciliation is a separate question from donor and laboratory labels.
- Nothing was written to `results/round2/R5b_audit/`, to `docs/r5_idc_provenance.md`, or
  to any file outside `results/round3/D3_audit/` and the builder script. No git command
  was run.
