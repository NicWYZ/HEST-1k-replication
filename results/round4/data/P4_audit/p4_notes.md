# P4 notes: source-record audit of set L, the 24 lung Xenium samples

Round 4, stage P, sub-stage P4. Reading audit, one day cap. Every statement below
is from a publication, a GEO record or the 10x file CDN, not from HEST's fields.
The verdicts are in `p4_verdicts.csv`; the merged file is `donor_audit_r4.csv`.

## 1. The four dataset titles are three source records and one unreadable page

| samples | source | what it is |
|---|---|---|
| NCBI856 to NCBI884 (20) | Nat Genet 2025, doi:10.1038/s41588-025-02080-x, PMC11906353, and GEO GSE250346 | Vanderbilt and Norton Thoracic explant lung, Xenium run at TGen |
| NCBI885, NCBI886 | bioRxiv 2026-01-08, doi:10.64898/2026.01.07.698201, PMC12803277, and GEO GSE315411 | dual-chemistry method paper, same laboratory |
| TENX118 | 10x file CDN run record for region `Human_Lung_Cancer` | vendor demonstration dataset |
| TENX141 | nothing readable | the 10x dataset page returns HTTP 429 behind the origin's bot challenge |

## 2. Twenty-two of the 24 sit on a slide that carries more than one donor

The 20 fibrosis samples are cores in tissue microarrays. The publication states
that multiple samples were placed on a single Xenium slide of 10.45 mm by
22.45 mm using a TMA design, in a 3 by 3 pattern for 3 mm cores or 2 by 2 for
5 mm cores, and that 45 lung tissue cores were run on four TMAs of three to nine
samples each plus one replicate TMA of 17. The instrument output file name in
each GEO record carries the slide id, which gives the grouping directly.

| slide | donors run on it (all GEO regions) | of which in set L | set-L samples |
|---|---|---|---|
| 0003392 | 4 | 4 | 4 |
| 0003400 | 5 | 5 | 8 |
| 0003789 | 6 | 2 | 2 |
| 0003817 | 4 | 4 | 6 |

HEST's sample for each of the 20 is the single-donor core region, so the image
holds one donor. The slide does not. Anything that treats slide as a nuisance
level, or that assumes one slide is one donor, is wrong on this set.

NCBI885 and NCBI886 are worse, and they are the kidney papilla lesson at set
scale. GSE315411's overall design states 17 lung samples in one 3 by 6 TMA of
3 mm cores designed to fill the Xenium capture area, with three serial sections
on three slides, and the preprint states that each slide contained samples from
17 individuals. HEST's image for NCBI885 is 89999 by 45984 px at 0.251692 um,
which is 22.65 mm by 11.57 mm, and for NCBI886 91799 by 46959 px at 0.251733 um,
which is 23.11 mm by 11.82 mm. Both are the whole capture area. So each of these
two HEST samples contains up to 17 donors' tissue, and the two are serial
sections of one block, so they share the same 17 people. Neither can be a donor
unit and neither should be treated as one section of one person.

The remaining two, TENX118 and TENX141, are `unknown` rather than `yes`, and the
file records them that way: 22 of the 24 rows are multi_donor_capture_area yes
and 2 are unknown. For TENX118 the run is named `Human Multi-Tissue Cancer
(FFPE)` and the CDN shows a single region, `Human_Lung_Cancer`, with
region_area 30.261 mm2 against a 234.6 mm2 capture area, so other tissue
occupied the rest of the slide, but no source reached states whether that tissue
came from other donors. For TENX141 no source record could be read at all, so
nothing is established about its slide in either direction. Neither sample is
evidence for the multi-donor pattern, and neither is evidence against it.

## 3. HEST splits four donors into eight patient labels

The publication's naming rule is explicit. Sample names encode the collection
site (Vanderbilt University 'VU'; Translational Genomics Research Institute
'T'), the disease status ('HD' healthy donor, 'ILD' interstitial lung disease),
a unique number assigned to the patient, and where applicable whether the
section was less or more affected. Replicate healthy cores are suffixed A and B,
replicate disease cores 1 and 2. The number is therefore the patient.

| source donor | set-L samples | HEST patient labels |
|---|---|---|
| VUILD96 | NCBI856, NCBI857 | Patient 26, Patient 25 |
| VUILD91 | NCBI858, NCBI859 | Patient 24, Patient 23 |
| VUILD78 | NCBI860, NCBI861 | Patient 22, Patient 21 |
| TILD117 | NCBI881, NCBI882 | Patient 2, Patient 1 |
| VUHD116 | NCBI875, NCBI876 | Patient 7, Patient 7 |

Four donors carry two HEST labels each, so those eight rows are `contradicted`.
VUHD116 is the one multi-section donor HEST labels correctly. Grouping on HEST's
patient label would give 21 donor keys on 24 samples and would put two sections
of one person on opposite sides of a donor split, which is the failure round 3
measured on CCRCC and Indiana.

## 4. Donor units the audit supports

Fifteen, from the 20 fibrosis samples. NCBI885, NCBI886, TENX118 and TENX141
carry no resolvable donor and are excluded. The plan predicted 21 donor keys,
which is HEST's count, not the source's.

The lead reports that NCBI865 failed P1's subset relation. NCBI865 is
VUILD110LA and it is that donor's only sample in set L, so dropping it drops the
donor with it: **15 donor units with NCBI865, 14 without**.

## 5. Instrument, imaging and preservation

All 22 TGen samples were run on the same physical instrument, serial XETG00048,
but not in the same generation. The 20 fibrosis samples were acquired on
instrument software 1.1.2.4 with onboard analysis xenium-1.1.0.2. NCBI885 and
NCBI886 were acquired on software 3.4.1.0 with analysis xenium-3.3.0.1, as the
V1 decoding pass of a co-hybridised V1-plus-Prime-5K preparation, two and a half
years later. TENX118 was run on a different instrument, serial XETG00105, whose
`instrument_sw_version` is the string `Development` rather than a numbered
release, with analysis xenium-2.0.0.6-35-ga7e17149a and multimodal segmentation.

Preservation is FFPE with a 5 um section for all 22 TGen samples, stated in both
publications and in every GEO record. TENX118's `preservation_method` field is
FFPE. TENX141 is unread.

The post-Xenium H&E was scanned on a Leica Biosystems Aperio CS2 for all 22 TGen
samples. The Nat Genet methods state a x20 objective. The same laboratory's 2026
methods state 40X, reached with a 20X objective and a doubler inserted, on the
same scanner model. The two source statements differ from each other, and HEST
records 40x for the 20 samples whose primary publication says x20.

## 6. Pixel size

The Nat Genet methods state that the registered H&E was scaled at 0.2125 um per
pixel to match the Xenium cell centroid coordinates. HEST's estimated and
embedded values for all 20 are 0.212500 and 0.212500015937501, so HEST agrees
with the source to six decimals. That is the one part of prediction 1 that holds,
and it holds only within this arm.

The Fishing preprint and GSE315411 state no pixel size, so HEST's 0.251692 and
0.251733 for NCBI885 and NCBI886 are unchecked.

TENX118's run record states `pixel_size` 0.2125, which is the Xenium
morphology-image raster. HEST's estimated 0.273856 and embedded 0.273771
describe a different raster. The source's `region_area` is 30.261 mm2. HEST's
image at its own 0.273856 um implies a 3.17 by 12.35 mm bounding box, 39.16 mm2,
which can contain that region; at 0.2125 um it would imply 23.58 mm2, which
cannot. So the geometry supports HEST's value as the pixel size of the image
HEST actually holds, and the 0.2125 in the source describes the Xenium
morphology image. This is recorded as two different images rather than a
contradicted number, and it is the ambiguity round 3's D3 listed as unchecked.

## 7. Laboratory

Two, not one. Twenty-two of the 24 were generated in the Banovich Lab at the
Translational Genomics Research Institute in Phoenix, which is also HEST's
`lab_provisional` for them and is the GEO submitting laboratory in both series.
Tissue for the 20 was collected at Vanderbilt University Medical Center and
Norton Thoracic Institute, and the cores for NCBI885 and NCBI886 were selected
by a pediatric lung pathology team at the University of Washington and Seattle
Children's. TENX118 is a 10x Genomics vendor dataset. TENX141's laboratory rests
only on the vendor domain of the page HEST cites, which is unreadable, so its
`lab_label_status` is `unverifiable`.

## 8. Disease is not fixed across set L

Per-sample clinical diagnosis from the GEO records of the 20: idiopathic
pulmonary fibrosis (7 samples), sarcoidosis (2), interstitial pneumonia with
autoimmune features (2), interstitial lung disease with no subtype stated (2),
chronic hypersensitivity pneumonitis (1), connective tissue disease associated
ILD (1), and control lung declined for organ donation (5). NCBI885 and NCBI886
state no per-core diagnosis. TENX118 is lung cancer. A lung task built on set L
holds organ, platform vendor and preservation fixed, and does not hold disease
fixed.

## 9. What a later stage should check and this audit could not

Each of the 20 HEST images is a rectangle around one core, and some of those
rectangles are larger than the core. NCBI856 is 17136 by 24809 px at 0.2125 um,
which is 3.64 mm by 5.27 mm, against a 3 mm core. Whether a rectangle reaches
into a neighbouring core, and therefore whether any patch at a sample's edge
contains a second donor's tissue, cannot be settled by reading. It needs the
patch coordinates against the core geometry, which is a P3 or P5 check on the
downloaded data, not a source-record question. Flagged as an escalation.
