> **Closed record of a reading task, dated 2026-09-18.** Round-2 R5's provenance reading of the four
> IDC Xenium samples, run in parallel with the R4 cluster stage. Closed: nothing in it is maintained,
> and the questions it left open are now stage D3's in `docs/round3_execution_plan.md`. Its findings
> are not restated here and are not revised; where later work reads a source differently, the later
> reading governs. HEST v1.3.0's inventory in `results/round3/D0_inventory/hest_inventory.csv` gives
> TENX95 and TENX99 siblings under other sample ids and different patient labels, which reopens the
> question this document answered from the vendor pages. **Stage D3 has since found this document's
> § 1 table wrong on one row, and the finding is an escalation awaiting the A3 gate.** The table
> assigns TENX95 to the entire-sample-area dataset as Replicate 2; HEST's release tables, identically
> in all five releases, assign that row to TENX98 and put TENX95 in the pre-designed-panel dataset,
> so the same-donor pairing this document reports for TENX95 and TENX99 rests on a misassignment
> (`results/round3/D3_audit/d3_notes.md` § 2). Two further cautions for anyone reading its
> numbers: its 60 claims pass the numeric-claim sweep only because D0 committed HEST's release
> tables, which its citation of `HEST_v1_1_0.csv` now resolves against, and most of those matches
> are to unrelated samples' values rather than to the quantity the text means
> (`results/round3/H0_housekeeping/r5_sweep_triage.md`). Read the passes as unchecked, not as
> verified.

# R5 — Provenance of the four HEST-1k IDC Xenium samples (TENX95, TENX99, NCBI783, NCBI785)

**Where the numbers in this document come from.** This was a reading task, so most of its values were
read from sources outside the repository (vendor dataset pages, GEO records, the raw GEO-deposited
`gene_panel.json` files, and the Janesick et al. paper), listed in § 5. Two repository files carry
the same quantities as this document states them and are the checkable record of the panel and
resolution claims below: the per-sample panel composition (entries, control probes, real genes,
extras) is [`r5_idc_panels_observed.csv`](../results/round2/R5b_audit/r5_idc_panels_observed.csv),
the pairwise shared-entry counts, including the intersection over all four samples, are
[`r5_idc_panel_pairs.csv`](../results/round2/R5b_audit/r5_idc_panel_pairs.csv), and the per-sample
pixel size is [`sample_metadata.csv`](../results/tailored/integrity/sample_metadata.csv), which
carries it at full stored precision where the table in § 1 rounds it. Values this document
takes from a source outside the repository, including the panel-designer gene counts, the vendor's
per-replicate cell and transcript metrics and HEST's own table counts, are not in any repository file
and are declared in `.verify-exceptions`.

**Scope.** Literature/database reading task, run in parallel with the R4 cluster stage. No compute
was performed; every claim below is sourced to a specific record (DOI, GEO accession, 10x Genomics
dataset page, or the HEST-1k GitHub repository) and dated as of the fetch in this session
(2026-09-18). Where a source was silent on a question, the corresponding cell reads **"not stated
in sources consulted"** rather than an inferred value, per this project's standing rule.

**Network note.** `huggingface.co` (for HEST-1k's own metadata CSV) and `www.10xgenomics.com` were
reached with one-time network-access approvals early in this task. After that, the lead session
instructed that further blocked domains should NOT be requested and should instead be logged as
unreachable; NCBI/GEO, PubMed Central, Crossref and arXiv were confirmed reachable throughout. The
gated Hugging Face metadata CSV (`HEST_v1_1_0.csv`) could not be read (HTTP 401 — dataset requires
an accepted-terms account token, which was not available); the GitHub code/issue search API was used
as a substitute route into the HEST-1k repository and was sufficient to resolve the questions below.

## 1. Provenance table

One row per sample; one column per variable that differs across the four. "Not stated" means no
source consulted (see §5) gives that value — it is not an inferred absence.

| Variable | TENX95 | TENX99 | NCBI783 | NCBI785 |
|---|---|---|---|---|
| Generating lab | 10x Genomics (public dataset release) | 10x Genomics (public dataset release) | 10x Genomics, Computational Biology dept., Pleasanton CA (GEO submitter S. R. Williams et al.) | 10x Genomics, Computational Biology dept., Pleasanton CA (GEO submitter S. R. Williams et al.) |
| Study / accession | 10x Genomics dataset *"FFPE Human Breast Using the Entire Sample Area"*, Replicate 2 — 10xgenomics.com/datasets/ffpe-human-breast-using-the-entire-sample-area-1-standard (published 2023-01-22) | Same dataset, Replicate 1 | GEO **GSM7780155**, subseries **GSE243168** *"…[Xenium]"*, superseries **GSE243280**; Janesick et al. 2023, *Nat Commun* 14:8353, doi:10.1038/s41467-023-43458-x — described in the deposit as **"Sample #2"** | GEO **GSM7780153** ("Rep 1") or **GSM7780154** ("Rep 2") — the two are indistinguishable from the sources reached — same subseries/superseries/paper, described as **"Sample #1"** |
| Donor | Donor Count = 1 (10x page metadata) — **same donor as TENX99** | Donor Count = 1 — **same donor as TENX95** | Distinct from Sample #1: block collected 2009-07-24 | Distinct from Sample #2: block collected 2021-07-26 |
| Tissue block | Single FFPE resected breast tumor mass, Infiltrating Ductal Carcinoma, from Avaden Biosciences — **the same physical block as TENX99** | Same physical block as TENX95 | Sample #2: FFPE block, AJCC pT2 pN1a pMX, ER−/HER2+/PR−, from Discovery Life Sciences | Sample #1: FFPE block, TNM T2N1M0 Stage II-B, ER+/HER2+/PR−, from Discovery Life Sciences |
| Section / replicate | Replicate 2 of 2 (serial 5 µm section) | Replicate 1 of 2 (892,966 cells / 105.58M transcripts detected onboard — matches the raw-data cell count for TENX99 independently reported in a HEST GitHub issue) | Single section — no Xenium replicate was cut for Sample #2 | One of two Xenium replicates cut from Sample #1; the other replicate is separately ingested by HEST-1k as sample id **NCBI784**, which is *not* used in the 4-sample IDC task |
| Gene panel | Pre-designed commercial **Xenium Human Breast Gene Expression Panel v1**, 280 real gene targets, no add-on; byte-identical panel file to TENX99 | Byte-identical to TENX95 | Base panel **"hBreast_320g"** (design **PD_266**, 280 real genes) **+ an 8-probe "Breast Cancer Tumor Microenvironment" add-on** — confirmed from the raw GEO `gene_panel.json` to consist of 8 `antisense_*` control-style probes, not additional biological targets | Custom prototype panel **"hBreast_320g" (design PD_260)**, confirmed from the raw GEO `gene_panel.json` to carry **313 real gene targets** — 280 shared with the commercial/PD_266 base plus (per that file) **33** genes not present in Sample #2's panel; HEST's own ingested files report **41** unique add-on real genes for this sample (see §3 — the 33 vs. 41 gap is not fully resolved) |
| Scan instrument (Xenium fluorescence step) | Not stated to be a prototype; page lists product "In Situ Gene Expression", software "Xenium Onboard Analysis", instrument "Xenium Analyzer" (production-line naming) | Same as TENX95 | Explicitly stated in the paper's Methods: **"the Xenium workflow using in-development chemistry and a prototype instrument and consumables"** | Same explicit prototype-instrument statement (applies to the whole study, both samples) |
| H&E scanner model | not stated in sources consulted | not stated in sources consulted | not stated in sources consulted | not stated in sources consulted |
| Nominal objective magnification | not stated in sources consulted | not stated in sources consulted | not stated in sources consulted | not stated in sources consulted |
| Pixel size (HEST file, µm/px) | 0.2125 | 0.2125 | 0.2740 | 0.3639 |

No source consulted (10x dataset pages, the Janesick et al. Methods, or the associated GEO sample
records) states an H&E scanner model or a nominal objective magnification for any of the four
samples. The GEO `Sample_scan_protocol` field for the Janesick Xenium runs reads only **"Xenium In
Situ Analyzer"**, which describes the Xenium fluorescence-imaging instrument, not the H&E
brightfield scan. **The cause of the pixel-size difference (0.2125 vs. 0.2740 vs. 0.3639 µm/px) is
not stated in any source reached in this task.** This is reported as an honest gap, not inferred
from the pixel-size ratios.

## 2. Per-pair conclusions (all six pairs)

**TENX95 vs TENX99 — same donor, same tissue block.** 10x's own dataset-page metadata states
`donorCount: 1` for the "FFPE Human Breast Using the Entire Sample Area" dataset that contains both
replicates; the page's own framing (comparing "Replicate 1" vs "Replicate 2" metrics to show
"reproducibility of data generated by the platform") describes two serial sections of one block, not
two patients. They carry byte-identical gene panels (280 real genes, no add-on) and identical pixel
size (0.2125 µm/px). The only sourced differences are the replicate number and the resulting
cell/transcript yield (892,966 cells / 105.58M transcripts for Rep 1 vs. 885,523 cells / 100.63M
transcripts for Rep 2, per 10x's own reported metrics). **These two samples are sections of the same
block from a single donor — they are not independent patients**, contradicting the "2 patients"
description in the HEST-1k paper's own text for this pair.

**NCBI783 vs NCBI785 — different donor, different block.** These map to Janesick et al.'s "Sample
#2" and "Sample #1" respectively (different GEO records, different collection dates — 2009-07-24 vs.
2021-07-26 — and different pathologist-assigned stage/receptor status). They also differ in gene
panel (NCBI783: 280 real genes + 8 antisense-probe add-on = 288; NCBI785: 280 shared genes + a
larger add-on of real target genes, 321 per HEST's ingested files) and in pixel size (0.2740 vs.
0.3639). **This pair is a genuine two-patient contrast** — unlike the TENX pair — but it is confounded
by panel identity and pixel size on top of patient identity, so it is not a clean single-variable
contrast either.

**TENX95 vs NCBI783.** Same ultimate generating organization (10x Genomics staff conducted both the
public dataset release and the Janesick study). Differ in: donor/block (Avaden-sourced block vs.
Janesick's Sample #2 block), collection date and publication, gene panel (280-gene commercial v1 vs.
280-gene PD_266 base + 8-probe antisense add-on — 533/541 total-entry overlap per the corrected
pairwise check), pixel size (0.2125 vs. 0.2740), and Xenium-instrument generation (no "prototype"
language for TENX95 vs. an explicit "prototype instrument" statement for NCBI783).

**TENX95 vs NCBI785.** Same generating organization. Differ in: donor/block, collection
date/publication, gene panel (280-gene commercial v1 vs. the larger custom PD_260 panel with a real
gene add-on — only 500/541 total-entry overlap, the largest panel gap of any pair), pixel size (0.2125
vs. 0.3639, the largest pixel-size gap of any pair), and instrument generation (production vs.
stated prototype).

**TENX99 vs NCBI783.** Same conclusions as TENX95 vs NCBI783 (TENX99 is the other replicate of the
identical TENX block/panel).

**TENX99 vs NCBI785.** Same conclusions as TENX95 vs NCBI785 (largest panel gap and largest
pixel-size gap of any pair).

## 3. The panel-heterogeneity finding, reconciled against sources

The task brief was corrected twice during this round; the final, authoritative counts (supplied by
the lead session from a full pairwise gene-list computation) are:

| sample | entries | control probes | real genes | extras over the 500-entry intersection |
|---|---|---|---|---|
| NCBI783 | 541 | 253 | 288 | 33 control probes + 8 `antisense_*` probes |
| NCBI785 | 541 | 220 | 321 | 0 control probes + 41 real add-on genes |
| TENX95 | 541 | 261 | 280 | 41 control probes + 0 real |
| TENX99 | 541 | 261 | 280 | 41 control probes + 0 real |

**This settles the question in favor of explanation (a): the panel difference is real, not a
file-processing artefact.** Fetching the raw, GEO-deposited `gene_panel.json` files for the three
Xenium runs in Janesick et al.'s deposit (GSM7780153 "Rep 1", GSM7780154 "Rep 2", both design
`PD_260`/"hBreast_320g"; and GSM7780155, design `PD_266`/"hBreast_320g" base + design `PD_269`
add-on named **"Breast Cancer Tumor Microenvironment"**) shows:

- TENX95/TENX99 (280 real genes, no add-on) match the commercial, pre-designed **Xenium Human
  Breast Gene Expression Panel v1** with no custom add-on — consistent with the 10x dataset page's
  own statement that this dataset "were generated with the pre-designed Xenium Human Breast Gene
  Expression Panel (v1)."
- GSM7780155's raw panel file has exactly 280 base genes + an 8-target add-on, and **all 8 add-on
  targets are named `antisense_*`** (e.g. `antisense_ADCY4`, `antisense_BCL2L15`) — control-style
  probes, not new biological targets. This is an exact match to NCBI783's corrected real-gene count
  (280 + 8 = 288), which identifies **NCBI783 = GSM7780155 ("Sample #2")**.
- GSM7780153/GSM7780154's raw panel file (design `PD_260`, "hBreast_320g") lists **313** real gene
  targets, of which 280 are shared with GSM7780155's base panel and **33** are unique to this design
  — including every one of the twelve example genes originally flagged as NCBI785's "extra" genes
  (AHSP, BTNL9, CCL20, CD1C, CD3D, CD8B, CLCA2, CLDN4, CLDN5, CRHBP, CSF3, CYP1A1 all appear in this
  33-gene set and nowhere in GSM7780155's panel). This identifies **NCBI785 as one of the two Sample
  #1 Xenium replicates (GSM7780153 or GSM7780154)** — consistent with §1's tissue-block finding.

**Residual, unresolved discrepancy:** the raw panel-designer file gives Sample #1 a 33-gene add-on
over the shared 280-gene base, but HEST's own ingested files report a 41-gene add-on for NCBI785 (321
real genes total, not 313). The direction and gene identity of the difference (Sample #1 genuinely
carries extra real genes the other three panels lack) is corroborated by two independent sources —
the raw GEO panel-designer JSON and HEST's ingested gene lists — but the exact **count** (33 vs. 41)
does not match. This 8-gene gap could not be resolved from the sources reached in this task (it would
require diffing the specific per-GSM *processed* Xenium output feature list — not the panel-designer
file — against HEST's ingestion code, which was not accessible in this pass). It is reported here as
an open discrepancy rather than resolved by inference.

**Bottom line for the benchmark:** panel identity is a genuine, sourced, additional variable in the
IDC contrast — a fifth axis of difference on top of tissue block/donor, scan resolution, and (for the
NCBI pair) Xenium-instrument generation. TENX95/TENX99 share one panel (280 genes, no add-on);
NCBI783 carries that same 280-gene base plus an 8-probe antisense QC add-on; NCBI785 carries the
280-gene base plus a substantially larger, genuinely different set of real target genes not measured
by any of the other three samples.

## 4. Escalation

**TENX95 and TENX99 — the two samples HEST-1k's own text describes as "2 patients" — are in fact two
serial sections of a single tissue block from a single donor**, per 10x Genomics' own dataset-page
metadata (`donorCount: 1`). This is the same kind of finding that led to this project's earlier
withdrawal of the "institution shift" label: a benchmark contrast is treating same-patient material
as independent. Per the project's escalation rule, this is recorded here rather than halting work,
but it should be weighed before TENX95/TENX99 are used as if they were two independent samples in any
downstream split (institution, resolution, or otherwise).

## 5. Sources consulted

- Jaume, G. et al. *HEST-1k: A Dataset for Spatial Transcriptomics and Histology Image Analysis*, NeurIPS 2024 / arXiv:2406.16192 (paper text, Table A4, and the IDC task description).
- Janesick, A. et al. *High resolution mapping of the tumor microenvironment using integrated single-cell, spatial and in situ analysis*, Nat Commun 14, 8353 (2023). doi:10.1038/s41467-023-43458-x (full text and Methods, fetched via Unpaywall/open access).
- GEO records: GSE243280 (SuperSeries), GSE243168 ("…[Xenium]" SubSeries), GSM7780153, GSM7780154, GSM7780155 (`ncbi.nlm.nih.gov/geo`, brief text records).
- Raw GEO-deposited Xenium `gene_panel.json` files for GSM7780153, GSM7780154, GSM7780155 (`ftp.ncbi.nlm.nih.gov/geo/samples/...`).
- 10x Genomics dataset page: *FFPE Human Breast Using the Entire Sample Area* (10xgenomics.com/datasets/ffpe-human-breast-using-the-entire-sample-area-1-standard), including its embedded structured metadata (`donorCount`, per-replicate metrics table).
- 10x Genomics support documentation on pre-designed Xenium v1 panels (negative control probe/codeword conventions).
- mahmoodlab/HEST GitHub repository: `tutorials/4-Running-HEST-Benchmark.ipynb` (task/sample-ID table) and `src/hest/subtyping/atlas.py` (confirms a third Janesick sample id, **NCBI784**, exists in HEST-1k but is excluded from the 4-sample IDC task).
- Corrected pairwise gene-panel overlap and real-gene/control-probe counts supplied by the lead session from a full computation over the four samples' shipped gene lists (used as the authoritative "observed" data reconciled against the sources above).

## 6. What I could not establish

- **HEST_v1_1_0.csv** (HEST-1k's own per-sample metadata table on Hugging Face) — the dataset is
  gated (`gated: "auto"`) and returned HTTP 401 without an accepted-terms account token; not
  available in this environment. This would likely have given a direct, single-source confirmation
  of donor/source-publication fields instead of the multi-source triangulation used here.
- Which of GSM7780153 ("Rep 1") or GSM7780154 ("Rep 2") specifically corresponds to NCBI785, versus
  the excluded NCBI784 — both are Sample #1 replicates with identical panels, so this does not affect
  any conclusion above, but the specific mapping is not determinable from the sources reached.
  Following the lead session's steering, this was not chased further with a network-access request.
- The exact 33-vs-41 gap in NCBI785's add-on gene count (§3) — not resolved; would require the
  processed per-sample Xenium feature list (not the panel-designer JSON) and/or HEST's ingestion code.
- H&E scanner model and nominal objective magnification for any of the four samples — not stated in
  any source consulted; not inferred from the pixel-size values.
- The stated cause of the pixel-size difference (0.2125 vs. 0.2740 vs. 0.3639 µm/px) — not stated in
  any source consulted.
- HEST-1k's Table A4 reports **n = 4** Xenium samples for this publication (Breast, Janesick et al.),
  but GEO's GSE243168 subseries lists only **3** Xenium GSM records, and HEST's own `atlas.py` names
  only 3 sample ids (NCBI783/784/785). This numerical discrepancy (4 vs. 3) is noted but not resolved
  from the sources reached.
