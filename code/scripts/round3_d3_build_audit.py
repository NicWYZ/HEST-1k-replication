"""Round 3, stage D3. Assemble results/round3/D3_audit/donor_lab_audit_ext.csv.

This is a READING stage. Every per-sample verdict below was read from the source
record named in the row's `citation` field during the D3 session; this script only
joins those verdicts to HEST's own fields in
results/round3/D0_inventory/hest_inventory.csv so that the HEST-side columns
(hest_patient, hest_dataset_title, hest_subseries, resolution_uncertain_hest,
pixel_size_um_estimated, pixel_size_um_embedded, magnification_hest) cannot drift
from the inventory. No network access and no computation.

Run from the repository root.
"""

import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone

import pandas as pd

ROOT = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
INV = os.path.join(ROOT, "results/round3/D0_inventory/hest_inventory.csv")
MEMBERS = os.path.join(ROOT, "results/round3/D0_inventory/expansion_set_members.csv")
OUTDIR = os.path.join(ROOT, "results/round3/D3_audit")

# ---------------------------------------------------------------- citations

CIT = {
    "biomarker": (
        "Janesick AS, Kravitz SN, Stauffer W, Valencia M, Taylor SEB. "
        "'Biomarker Quantification in Breast Cancer using Xenium In Situ.' bioRxiv "
        "10.64898/2025.12.08.692193, posted 2025-12-11 (Crossref record read "
        "2026-09-22 via api.crossref.org; JATS full text via "
        "biorxiv.org/content/early/2025/12/11/2025.12.08.692193.source.xml); "
        "Methods sections 'Biomaterials' and 'Serial Section IHC and Post-Xenium H&E'; "
        "Supplemental Table S1 in supplementary file media-1.xlsx (692193_file03.xlsx)"
    ),
    "tenx_cdn": (
        "10x Genomics per-run metadata files "
        "{n}_experiment.xenium and {n}_metrics_summary.csv at "
        "https://cf.10xgenomics.com/samples/xenium/1.0.2/{n}/ (read 2026-09-22)"
    ),
    "qust": (
        "QuST (arXiv:2406.01613), Data Availability section, which quotes the tissue "
        "description printed on each 10x Genomics Xenium breast dataset page; used "
        "because www.10xgenomics.com itself returned an HTTP 429 bot challenge "
        "('Vercel Security Checkpoint') on every attempt in this session and in round 2"
    ),
    "janesick23": (
        "Janesick A et al., Nat Commun 14:8353 (2023), doi:10.1038/s41467-023-43458-x, "
        "Methods 'Samples and sample collection' (Sample #1, Sample #2) and 'Xenium "
        "sample preparation'; PMC10730913 full text read 2026-09-22"
    ),
    "geo243168": (
        "GEO subseries GSE243168 / superseries GSE243280 sample records "
        "(ncbi.nlm.nih.gov/geo/query/acc.cgi), subseries strings as ingested by HEST"
    ),
    "gse183456": (
        "GEO series GSE183456 'Spatial localization with Spatial Transcriptomics for an "
        "atlas of healthy and injured cell states and niches in the human kidney "
        "[Visium ST]', per-sample records and Series_overall_design / "
        "Sample_extract_protocol_ch1, read 2026-09-22 via "
        "ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE183456&targ=gsm&form=text&view=full"
    ),
    "lake23": (
        "Lake BB et al., 'An atlas of healthy and injured cell states and niches in the "
        "human kidney', Nature 619:585-594 (2023), doi:10.1038/s41586-023-05769-3, "
        "Methods '10x Visium spatial transcriptomics: Preparation, imaging and "
        "sequencing'; PMC10356613 full text read 2026-09-22"
    ),
    "gse231630": (
        "GEO series GSE231630 per-sample records (disease, tissue source, storage and "
        "the free-text description naming every tissue piece inside each fiducial "
        "zone), read 2026-09-22 via ncbi.nlm.nih.gov/geo/query/acc.cgi"
    ),
    "papilla23": (
        "Canela VH et al., 'A spatially anchored transcriptomic atlas of the human "
        "kidney papilla identifies significant immune injury in patients with stone "
        "disease', Nat Commun 14:4140 (2023), doi:10.1038/s41467-023-38975-8, Methods "
        "(Visium imaging); PMC10356953 full text read 2026-09-22"
    ),
    "gse175540": (
        "GEO series GSE175540 'Tertiary lymphoid structures generate and propagate "
        "anti-tumor antibody-producing plasma cells in renal cell cancer', series and "
        "per-sample records, read 2026-09-22 via ncbi.nlm.nih.gov/geo/query/acc.cgi"
    ),
    "kth21": (
        "Gracia Villacampa E et al., 'Genome-wide spatial expression profiling in "
        "formalin-fixed tissues', Cell Genomics 1(3):100065 (2021), PMID 36776149, "
        "PMC9903805 full text read 2026-09-22 (organoid section)"
    ),
    "none": "no source record reached; see d3_notes.md",
}

# ------------------------------------------------- breast Xenium, 11 biomarker

# Supplemental Table S1 of the biomarker preprint, one row per section.
# The HEST subseries string 'Section N, pos' maps onto the preprint's '#SN-Pos'.
BIOMARKER = {
    # sample_id: (section, disease, staging, grade, hormone)
    "TENX191": ("S1-Top", "IDC", "T3 N0 M0", "G3", "HER2-Neg"),
    "TENX192": ("S1-Middle", "DCIS", "T2 N0 M0", "G2", "ER+/PR+/HER2-2+"),
    "TENX193": ("S1-Bottom", "DCIS", "T1c N0 M0", "G3", "HER2-1+"),
    "TENX195": ("S2-Middle", "DCIS", "T1c N1 MX", "G2", "HER2-2+"),
    "TENX196": ("S2-Bottom", "DCIS", "Tis NX MX", "G3", "HER2-3+"),
    "TENX197": ("S3-Top", "CCH/DCIS", "Tis N0", "G2", "ER+/PR+/HER2-1+"),
    "TENX198": ("S3-Middle", "DCIS", "T4b N3a M1", "G2", "ER+/PR+/HER2-2+"),
    "TENX199": ("S3-Bottom", "DCIS", "TX NX M0", "G2", "ER-/PR-/HER2-2+"),
    "TENX200": ("S4-Top", "IDC", "Tis NX MX", "G3", "ER+/PR+/HER2-1+"),
    "TENX201": ("S4-Middle", "IDC", "T2 N0 MX", "not stated", "ER+/PR+/HER2-2+"),
    "TENX202": ("S4-Bottom", "DCIS", "T4a N2a", "G3", "HER2-1+"),
}

# ------------------------------------------------- breast Xenium, 7 10x/Janesick

TENX_RUN = {
    "TENX95": ("Xenium_V1_FFPE_Human_Breast_IDC", "human_breast_ffpe_predesigned_and_addon",
               "0002429", "SIM1", "2022-11-10T00:30:50Z", 574852, 90361596.31),
    "TENX97": ("Xenium_V1_FFPE_Human_Breast_IDC_With_Addon", "human_breast_ffpe_predesigned_and_addon",
               "0002807", "SIM2", "2022-11-10T00:30:51Z", 574527, 96168606.39),
    "TENX98": ("Xenium_V1_FFPE_Human_Breast_IDC_Big_2", "human_breast_ffpe_large_sections",
               "0002169", "SIM2", "2022-12-02T22:21:44Z", 885523, 221212452.52),
    "TENX99": ("Xenium_V1_FFPE_Human_Breast_IDC_Big_1", "human_breast_ffpe_large_sections",
               "0002178", "SIM1", "2022-12-02T22:21:44Z", 892966, 228050907.80),
}

# ------------------------------------------------- kidney Visium, Lake atlas 23

LAKE = {  # hest subseries -> (gsm, disease, tissue source, donor specimen)
    "21-015": ("GSM6047778", "Reference (deceased-donor nephrectomy)", "Nephrectomy", "21-015"),
    "21-019": ("GSM6047779", "Reference (deceased-donor nephrectomy)", "Nephrectomy", "21-019"),
    "IU-F52": ("GSM6047775", "Reference (deceased-donor nephrectomy)", "Nephrectomy", "IU-F52"),
    "IU-F59": ("GSM6047774", "Reference (deceased-donor nephrectomy)", "Nephrectomy", "IU-F59"),
    "IU-M32": ("GSM6047777", "Reference (deceased-donor nephrectomy)", "Nephrectomy", "IU-M32"),
    "IU-M61": ("GSM6047776", "Reference (deceased-donor nephrectomy)", "Nephrectomy", "IU-M61"),
    "IU-13437": ("GSM6047780", "Diabetic Kidney Disease (DKD)", "Biopsy", "IU-13437"),
    "27-10066": ("GSM6047790", "Diabetic Kidney Disease (DKD)", "Biopsy", "27-10066"),
    "28-12265-Cortex": ("GSM6047786", "Diabetic Kidney Disease (DKD)", "Biopsy", "28-12265"),
    "28-12265-Medulla": ("GSM6047787", "Diabetic Kidney Disease (DKD)", "Biopsy", "28-12265"),
    "29-10012": ("GSM6047782", "Diabetic Kidney Disease (DKD)", "Biopsy", "29-10012"),
    "29-10013": ("GSM6047781", "Diabetic Kidney Disease (DKD)", "Biopsy", "29-10013"),
    "29-10280": ("GSM6047783", "Diabetic Kidney Disease (DKD)", "Biopsy", "29-10280"),
    "29-10282": ("GSM6047789", "Diabetic Kidney Disease (DKD)", "Biopsy", "29-10282"),
    "29-10404": ("GSM6047785", "Diabetic Kidney Disease (DKD)", "Biopsy", "29-10404"),
    "31-10042": ("GSM6047788", "Diabetic Kidney Disease (DKD)", "Biopsy", "31-10042"),
    "31-10221": ("GSM6047784", "Diabetic Kidney Disease (DKD)", "Biopsy", "31-10221"),
    "30-10125": ("GSM6047792", "Acute Kidney Injury (AKI)", "Biopsy", "30-10125"),
    "30-10631": ("GSM6047794", "Acute Kidney Injury (AKI)", "Biopsy", "30-10631"),
    "30-10929": ("GSM6047795", "Acute Kidney Injury (AKI)", "Biopsy", "30-10929"),
    "32-10003": ("GSM6047796", "Acute Kidney Injury (AKI)", "Biopsy", "32-10003"),
    "32-10074": ("GSM6047791", "Acute Kidney Injury (AKI)", "Biopsy", "32-10074"),
    "33-10331": ("GSM6047793", "Acute Kidney Injury (AKI)", "Biopsy", "33-10331"),
}

# ------------------------------------------------- kidney Visium, papilla 7

PAPILLA = {  # hest subseries -> (gsm, disease, donors on the slide, donor used)
    "20-0034": ("GSM6250307", "Reference (papillary nephrectomy)", ["20-0034"], "20-0034"),
    "KRP428": ("GSM6250308", "Calcium oxalate stone disease", ["KRP428"], "KRP428"),
    "KRP449": ("GSM6250309", "Calcium oxalate stone disease",
               ["KRP449", "KRP440 (brushite, spots not used)"], "KRP449"),
    "KRP429": ("GSM6250310", "Calcium oxalate stone disease",
               ["KRP429", "KRP478 (spots not used)"], "KRP429"),
    "KRP446 (M) - KRP462 (F) - KRP475 (F)": (
        "GSM7166168", "Calcium oxalate stone disease",
        ["KRP446", "KRP462", "KRP475"], "KRP446+KRP462+KRP475"),
    "F59 - F63": ("GSM7166169", "Calcium oxalate stone disease",
                  ["F59", "F63"], "F59+F63"),
    "M50": ("GSM7166170", "Calcium oxalate stone disease", ["M50"], "M50"),
}

KEYENCE = "Keyence BZ-X810 with Nikon 10x CFI Plan Fluor objective"


def build():
    inv = pd.read_csv(INV, low_memory=False).set_index("id")
    members = pd.read_csv(MEMBERS)
    kidney = members.loc[members.set_name == "institution_kidney_visium", "sample_id"].tolist()

    breast = sorted(
        inv.index[
            inv.organ.astype(str).str.contains("Breast", case=False, na=False)
            & inv.st_technology.astype(str).str.contains("Xenium", na=False)
            & (inv.oncotree_code.astype(str) == "IDC")
        ]
    )
    assert len(breast) == 18, len(breast)
    assert len(kidney) == 54, len(kidney)
    extras = ["NCBI538", "NCBI539", "NCBI540", "TENX71"]

    rows = []

    def base(sid, set_name):
        r = inv.loc[sid]
        return dict(
            set_name=set_name,
            sample_id=sid,
            hest_patient=r.patient if pd.notna(r.patient) else "",
            hest_dataset_title=r.dataset_title,
            hest_subseries=r.subseries if pd.notna(r.subseries) else "",
            hest_source_page=(r.download_page_link1 if isinstance(r.download_page_link1, str)
                              and r.download_page_link1.strip() not in ("", "None (internal)")
                              else (r.study_link if pd.notna(r.study_link) else "")),
            hest_lab_provisional=r.lab_provisional,
            pixel_size_um_estimated=r.pixel_size_um_estimated,
            pixel_size_um_embedded=r.pixel_size_um_embedded,
            magnification_hest=r.magnification if pd.notna(r.magnification) else "",
            resolution_uncertain_hest=bool(r.resolution_uncertain),
            in_benchmark=bool(r.in_benchmark),
        )

    # ---- breast Xenium, the 11 biomarker sections -------------------------
    for sid, (sec, dis, stage, grade, horm) in BIOMARKER.items():
        d = base(sid, "institution_breast_xenium")
        d.update(
            source_url="https://doi.org/10.64898/2025.12.08.692193",
            donor_statement=(
                "Methods, Biomaterials: 'Human breast FFPE-preserved blocks were obtained from "
                "Avaden, BioIVT, and Discovery Life Sciences. The sample set comprised 11 blocks "
                "representing a range of breast cancer stages and grades, including both DCIS and "
                "invasive lesions, as well as one normal breast tissue sample (see Supplemental "
                "Table S1).' Results: variance 'was calculated across tumor cells from all 11 "
                "breast cancer sections (excluding normal - #S2-Top)'. Supplemental Table S1 gives "
                f"one disease, stage, grade and hormone status per section; {sec} is "
                f"{dis}, {stage}, {grade}, {horm}. Twelve sections, twelve distinct clinical "
                "profiles, eleven cancer blocks plus one normal."
            ),
            donor_id=f"breastXen_biomarker_{sec}",
            donor_label_status="contradicted",
            lab="10x Genomics",
            lab_label_status="verified",
            disease=dis,
            region="not stated in source",
            preservation="FFPE",
            scanner="Olympus VS200 (post-Xenium H&E); Xenium Analyzer, onboard analysis v4.0",
            pixel_size_source=(
                "not stated in source; source states the H&E scanner (Olympus VS200) and the "
                "VSI-to-OME.tif conversion in QuPath 0.5.1 but no pixel size or objective"
            ),
            resolution_uncertain_rederived="unresolved",
            notes=(
                f"HEST calls this section '{d['hest_subseries']}' and labels it "
                f"'{d['hest_patient']}', grouping the three sections of each Section number under "
                "one patient. The source does not support that grouping: it states eleven cancer "
                "blocks for the eleven cancer sections, and Supplemental Table S1 gives each "
                "section its own stage, grade and hormone status. The natural reading is that "
                "S1 to S4 are the four Xenium slides and top/middle/bottom are the three tissue "
                "pieces on each slide, so this set contributes eleven donors, not four. The source "
                "states blocks rather than donors, so the one-donor-per-block step is not "
                "positively stated; it is the reading the clinical table supports. HEST also "
                "assigns oncotree IDC to all eleven, which Table S1 contradicts for eight of them. "
                "The twelfth section, S2-Top (normal breast), is not in HEST; the TENX194 id is "
                "absent from every release table."
            ),
            citation=CIT["biomarker"],
        )
        rows.append(d)

    # ---- breast Xenium, the four 10x vendor Xenium runs --------------------
    vendor_block = {
        "TENX95": ("breastXen_10x_BioIVT_block", "BioIVT"),
        "TENX97": ("breastXen_10x_BioIVT_block", "BioIVT"),
        "TENX98": ("breastXen_10x_Avaden_block", "Avaden Biosciences"),
        "TENX99": ("breastXen_10x_Avaden_block", "Avaden Biosciences"),
    }
    for sid in ["TENX95", "TENX97", "TENX98", "TENX99"]:
        region, run, slide, cassette, t0, ncells, area = TENX_RUN[sid]
        donor, provider = vendor_block[sid]
        partner = {"TENX95": "TENX97", "TENX97": "TENX95",
                   "TENX98": "TENX99", "TENX99": "TENX98"}[sid]
        d = base(sid, "institution_breast_xenium")
        d.update(
            source_url=f"https://cf.10xgenomics.com/samples/xenium/1.0.2/{region}/{region}_experiment.xenium",
            donor_statement=(
                f"experiment.xenium for region '{region}': run_name '{run}', slide_id {slide}, "
                f"cassette {cassette}, run_start_time {t0}, num_cells {ncells}, pixel_size 0.2125, "
                "instrument_sn XETG00001, instrument_sw_version 1.0.0.3. metrics_summary.csv gives "
                f"region_area {area:.0f} um2. The two regions of run '{run}' are the two members "
                f"of this pair; {sid} and {partner} are the pair. The dataset page's tissue "
                f"description, quoted in the QuST data-availability section, names {provider} as "
                "the tissue provider for this dataset. No donor identifier appears in any file "
                "reached."
            ),
            donor_id=donor,
            donor_label_status="verified",
            lab="10x Genomics",
            lab_label_status="verified",
            disease="Infiltrating ductal carcinoma" + (
                "; the dataset description quoted by QuST for the custom add-on dataset reads "
                "'Infiltrating ductal carcinoma, Ductal carcinoma in situ'" if sid in ("TENX95", "TENX97") else ""),
            region="not stated in source",
            preservation="FFPE",
            scanner="Xenium Analyzer, instrument_sn XETG00001, instrument sw 1.0.0.3",
            pixel_size_source=(
                "source states pixel_size 0.2125 um in experiment.xenium (Xenium morphology image); "
                "HEST's estimated pixel size is 0.2125, identical"
            ),
            resolution_uncertain_rederived="False",
            notes=(
                f"HEST maps {sid} to '{d['hest_dataset_title']}' / '{d['hest_subseries']}', the "
                "same mapping in all five release tables v1_1_0 to v1_3_0. The vendor's "
                "'Replicate 1' and 'Replicate 2' are the two large sections of the 'entire sample "
                "area' run, which HEST ingests as TENX99 and TENX98; TENX95 and TENX97 are the "
                "pre-designed-panel and custom-add-on regions of a separate November 2022 run on a "
                "different tissue provider's block. HEST's patient 1 for TENX98/TENX99 and patient "
                "2 for TENX95/TENX97 therefore agree with the source. "
                + ("HEST's pixel_size_um_embedded is 1.0 for this sample, a fallback value, which "
                   "is what raised HEST's resolution_uncertain flag; the source states 0.2125 and "
                   "HEST's own estimate is 0.2125, so the flag clears."
                   if sid in ("TENX95", "TENX99") else
                   "HEST's embedded and estimated pixel sizes already agree at 0.2125.")
            ),
            citation=CIT["tenx_cdn"].format(n=region) + " | " + CIT["qust"],
        )
        rows.append(d)

    # ---- breast Xenium, the three Janesick samples ------------------------
    jan = {
        "NCBI783": ("Sample #2", "breastXen_Janesick_Sample2",
                    "AJCC pT2 pN1a pMX, ER-/HER2+/PR-", "2009-07-24"),
        "NCBI784": ("Sample #1 (Rep 2)", "breastXen_Janesick_Sample1",
                    "TNM T2N1M0, ER+/HER2+/PR-", "2021-07-26"),
        "NCBI785": ("Sample #1 (Rep 1)", "breastXen_Janesick_Sample1",
                    "TNM T2N1M0, ER+/HER2+/PR-", "2021-07-26"),
    }
    for sid, (label, donor, clin, coll) in jan.items():
        d = base(sid, "institution_breast_xenium")
        d.update(
            source_url="https://doi.org/10.1038/s41467-023-43458-x",
            donor_statement=(
                "Methods, Samples and sample collection: Sample #1 is 'A single formalin-fixed, "
                "paraffin-embedded (FFPE) breast cancer tissue block (TNM stage T2N1M0, "
                "ER+/HER2+/PR-) ... collected on 2021-07-26 and obtained from Discovery Life "
                "Sciences'; Sample #2 is a block '(AJCC pathologic stage pT2 pN1a pMX, ER-/HER2+/"
                "PR-) ... collected on 2009-07-24 and obtained from Discovery Life Sciences'. The "
                "Results call Sample #2 'a different biological section (different donor)'. The "
                "Xenium experiment was 'performed in replicate on two serial sections'. This "
                f"sample is {label}, {clin}, collected {coll}."
            ),
            donor_id=donor,
            donor_label_status="verified",
            lab="10x Genomics Inc., Pleasanton CA",
            lab_label_status="verified",
            disease="Invasive ductal carcinoma",
            region="not stated in source",
            preservation="FFPE",
            scanner=(
                "Xenium prototype instrument and in-development chemistry (source's words); "
                "post-Xenium IF on a Zeiss Axioimager with a 40x dipping objective; no H&E "
                "brightfield scanner stated"
            ),
            pixel_size_source="not stated in source for the H&E image",
            resolution_uncertain_rederived=("True" if sid == "NCBI784" else "unresolved"),
            notes=(
                "HEST's patient 4 for NCBI784 and NCBI785 and patient 5 for NCBI783 agree with the "
                "source: NCBI784/785 are the two Xenium replicates of Sample #1 and NCBI783 is "
                "Sample #2. "
                + ("NCBI784's HEST pixel_size_um_embedded 0.2125 and estimated 0.363788 disagree "
                   "by 41.6 per cent, and the source states neither, so the uncertainty stands. "
                   "NCBI784's embedded value also equals NCBI785's estimated value, which looks "
                   "like an off-by-one in HEST's own metadata rather than a property of the image."
                   if sid == "NCBI784" else
                   "The source states no H&E pixel size or objective, so the flag cannot be "
                   "re-derived either way from source; HEST's own embedded and estimated values "
                   "agree to within 0.03 per cent.")
            ),
            citation=CIT["janesick23"] + " | " + CIT["geo243168"],
        )
        rows.append(d)

    # ---- kidney Visium, Lake atlas 23 -------------------------------------
    for sid in kidney:
        sub = inv.loc[sid, "subseries"]
        if sub in LAKE:
            gsm, dis, tsrc, donor = LAKE[sub]
            shared = (sub.startswith("28-12265"))
            reg = ("Cortex" if sub.endswith("Cortex") else
                   "Medulla" if sub.endswith("Medulla") else
                   "not stated per sample in source")
            d = base(sid, "institution_kidney_visium")
            d.update(
                source_url="https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE183456",
                donor_statement=(
                    f"{gsm} title '{sub}', characteristics disease '{dis.split(' (')[0]}', tissue "
                    f"source '{tsrc}', storage 'OCT at -80C'. Lake et al. Methods: 'Nephrectomy "
                    "(n = 6), AKI (n = 6) and CKD (n = 11) samples were sectioned at 10 um "
                    "thickness from OCT-compound-embedded blocks. These 23 samples represent 22 "
                    "participants because 2 samples (1 cortex and 1 medulla) were obtained from "
                    "the same participant with CKD.'"
                    + (" This sample is one of that pair." if shared else "")
                ),
                donor_id=f"kidVis_atlas_{donor}",
                donor_label_status="verified",
                lab="Indiana University (Eadon laboratory)",
                lab_label_status="contradicted",
                disease=dis,
                region=reg,
                preservation="Fresh frozen, OCT-embedded, stored at -80 C, 10 um sections",
                scanner=KEYENCE,
                pixel_size_source=(
                    "source states instrument and objective only; no number in GSE183456 or Lake "
                    "et al. The same laboratory's papilla paper states 0.7547 um/pixel for the "
                    "identical instrument and objective, and HEST's estimate here is "
                    f"{inv.loc[sid, 'pixel_size_um_estimated']:.6f}, within 0.7 per cent of it"
                ),
                resolution_uncertain_rederived="False",
                notes=(
                    "HEST attributes this sample to Washington University School of Medicine. The "
                    "source contradicts that for the generating laboratory: GSE183456's "
                    "contributors are Michael Eadon, Ricardo Melo Ferreira and Ying-Hua Cheng and "
                    "its contact institute is Indiana University, and the Visium imaging used "
                    "Indiana's Keyence BZ-X810. Washington University is where the Lake et al. "
                    "atlas's senior authorship sits, not where this subseries was generated. "
                    "Specimen provenance is mixed: GSE183456's extract protocol states that four "
                    "reference nephrectomies (18-0006, 19-F52, 19-M61, 19-M32) and one CKD biopsy "
                    "(20-13437) came from the Biopsy Biobank Cohort of Indiana and 'All remaining "
                    "samples were provided by the Kidney Precision Medicine Project', a "
                    "multi-site consortium. HEST's magnification 20x is contradicted; the source "
                    "states a 10x objective. "
                    + ("HEST labels both 28-12265 samples Patient 13, which matches the source's "
                       "statement that one participant contributed a cortex and a medulla sample."
                       if shared else "")
                    + (" This sample shares every shipped component with NCBI599 from the earlier "
                       "Indiana study 'Integration of spatial and single cell transcriptomics "
                       "localizes epithelial-immune cross-talk in kidney injury', per D0's "
                       "duplicate_groups.csv, so the same physical sample is in HEST twice under "
                       "two study titles." if sid == "NCBI714" else "")
                ),
                citation=CIT["gse183456"] + " | " + CIT["lake23"],
            )
            rows.append(d)
        elif sub in PAPILLA:
            gsm, dis, on_slide, donor = PAPILLA[sub]
            multi = len(on_slide) > 1
            # Two shapes of multi-piece slide. 'composite': the study separated the
            # spots of every piece and kept them all, so the HEST sample is a
            # several-donor mixture. 'coresident': a second donor's piece sat in the
            # same fiducial zone and the study used only the named sample's spots,
            # so whether HEST's ingested spots are restricted the same way is not
            # stated by any source reached. Both fail the single-donor test.
            composite = "+" in donor
            coresident = multi and not composite
            d = base(sid, "institution_kidney_visium")
            d.update(
                source_url="https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE231630",
                donor_statement=(
                    f"{gsm} title '{sub}', characteristics disease '{dis}', tissue source "
                    "'Papillary Nephrectomy', storage 'OCT at -80C'. Pieces inside the fiducial "
                    f"zone per the GEO description: {'; '.join(on_slide)}."
                ),
                donor_id=f"kidVis_papilla_{donor}",
                donor_label_status=("contradicted" if multi else "verified"),
                lab="Indiana University (Eadon laboratory)",
                lab_label_status="verified",
                disease=dis,
                region="Renal papilla",
                preservation="Fresh frozen, OCT-embedded, stored at -80 C, 10 um sections",
                scanner=KEYENCE,
                pixel_size_source=(
                    "source states 'H&E-stained sections were imaged with a Keyence BZ-X810 "
                    "microscope equipped with a Nikon 10x CFI Plan Fluor objective at 0.7547 "
                    "um/pixel and image resolution of 1920x1440'; HEST's estimate here is "
                    f"{inv.loc[sid, 'pixel_size_um_estimated']:.6f}, within 0.7 per cent"
                ),
                resolution_uncertain_rederived="False",
                notes=(
                    "HEST carries no patient label for this sample. "
                    + (f"The capture area holds {len(on_slide)} tissue pieces from different "
                       "donors and the study separated their spots during processing, but HEST "
                       "ingests the whole capture area as one sample, so this HEST sample is not "
                       "one donor and must not be used as a donor unit. "
                       if composite else "")
                    + ("A second donor's tissue piece sat in the same fiducial zone and the "
                       "study states that only the named sample's spots 'were used in the "
                       "conduct of this experiment'. That is a statement about the study's own "
                       "analysis, not about HEST's ingestion, and no source reached says whether "
                       "HEST's spot set for this sample is restricted the same way. So this "
                       "sample cannot be treated as one donor either, for a different reason "
                       "than the three-piece and two-piece composites: the risk here is "
                       "contamination by a second donor's spots rather than a known mixture. "
                       if coresident else "")
                    + "HEST's magnification 20x is contradicted; the source states a 10x "
                      "objective. HEST's pixel_size_um_embedded 0.352778 disagrees with its own "
                      "estimate by 53 per cent and with the source's stated 0.7547, so the "
                      "embedded value is the wrong one and the uncertainty flag clears."
                ),
                citation=CIT["gse231630"] + " | " + CIT["papilla23"],
            )
            rows.append(d)
        else:  # the 24 Sorbonne ccRCC samples
            title = sub.replace("ccRCC tumor ", "")
            pres = "FFPE" if title.startswith("ffpe") else "Fresh frozen"
            d = base(sid, "institution_kidney_visium")
            d.update(
                source_url="https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE175540",
                donor_statement=(
                    f"GSE175540 sample '{sub}', characteristics 'disease state: renal cell "
                    "cancer', 'tissue: ccRCC tumor'. The series record states no donor, patient or "
                    "participant identifier for any of its 24 samples. Series_overall_design reads "
                    "'Spatial transcriptomics of fresh frozen ccRCC human tumors' and "
                    "'*** Raw data has not been submitted at this time due to patient privacy "
                    "concerns ***'."
                ),
                donor_id=f"ccRCC_{title}",
                donor_label_status="unverifiable",
                lab="INSERM UMR-S 1138, Centre de Recherche des Cordeliers, Paris",
                lab_label_status="verified",
                disease="Clear cell renal cell carcinoma",
                region="not stated in source",
                preservation=pres,
                scanner="not stated in source",
                pixel_size_source="not stated in any source reached",
                resolution_uncertain_rederived="not_derivable",
                notes=(
                    f"HEST labels this sample '{d['hest_patient']}', one patient per sample across "
                    "INT1 to INT24. GSE175540 is silent on donor identity, so that labelling is "
                    "not positively sourced; round 2's donor_audit.csv records it as verified "
                    "against the same accession, which is stronger than the record supports. The "
                    "sample names carry a cohort letter and a number, and exactly one number "
                    "repeats across preservation types, ffpe_c_2 and frozen_c_2 (HEST INT24 and "
                    "INT4); whether those are one donor cannot be settled from the record. "
                    "Preservation is not fixed inside this arm: twelve sample titles begin ffpe_ "
                    "and twelve begin frozen_, while the series design line says fresh frozen for "
                    "all of them, and HEST's own preservation_method field is empty for all 24. "
                    "Meylan et al. 2022 Immunity is not open access, so no methods text was "
                    "reached and no scanner or pixel size could be established."
                ),
                citation=CIT["gse175540"],
            )
            rows.append(d)

    # ---- the four held-out kidney additions -------------------------------
    for sid in extras:
        d = base(sid, "kidney_visium_cell_extras")
        if sid.startswith("NCBI"):
            n = inv.loc[sid, "subseries"]
            d.update(
                source_url="https://pubmed.ncbi.nlm.nih.gov/36776149/",
                donor_statement=(
                    "The study states 'we used non-infected, PFA-fixed lung and kidney organoids "
                    "embedded in optimal cutting temperature embedding medium (OCT)', that "
                    "'between 6 and 8 organoids (<1 mm in diameter) were embedded together to fit "
                    "within a single capture area (<42.25 mm2)', and that '3 tissue sections' were "
                    "collected from the tissue block containing kidney organoids."
                ),
                donor_id="kidney_organoid_block_KTH",
                donor_label_status="unverifiable",
                lab="KTH Royal Institute of Technology / SciLifeLab (Lundeberg laboratory)",
                lab_label_status="verified",
                disease="not applicable, organoid material",
                region="not applicable, organoid material",
                preservation="PFA-fixed, OCT-embedded",
                scanner="not stated in the span read",
                pixel_size_source="not stated in the span read",
                resolution_uncertain_rederived="unresolved",
                notes=(
                    f"Answered: this is fixed organoid material, not patient tissue. HEST's "
                    f"subseries '{n}' is literal. The three HEST samples NCBI538, NCBI539 and "
                    "NCBI540 are the three consecutive sections of one organoid block, so they are "
                    "three sections of the same material rather than three independent units, and "
                    "each section carries 6 to 8 separate organoids. HEST's disease_state "
                    "'Treated' and organ 'Kidney' are misleading for any analysis that treats "
                    "these as kidney tissue. HEST's pixel_size_um_embedded is missing for all "
                    "three, which is why resolution_uncertain is set."
                ),
                citation=CIT["kth21"],
            )
        else:
            d.update(
                source_url="https://www.10xgenomics.com/datasets/human-kidney-11-mm-capture-area-ffpe-2-standard",
                donor_statement=(
                    "not reached. The only source HEST names is the 10x Genomics dataset page, "
                    "which returned an HTTP 429 bot challenge on every attempt."
                ),
                donor_id="",
                donor_label_status="unverifiable",
                lab="10x Genomics (vendor release)",
                lab_label_status="unverifiable",
                disease="Healthy (HEST field; no source reached)",
                region="not reached",
                preservation="FFPE (HEST field; no source reached)",
                scanner="not reached",
                pixel_size_source="not reached",
                resolution_uncertain_rederived="not_derivable",
                notes=(
                    "Not resolved. The generating laboratory is 10x Genomics in the sense that 10x "
                    "released the dataset, which is what HEST's vendor_product_page basis already "
                    "says; whether 10x also generated the tissue and who provided it could not be "
                    "established because www.10xgenomics.com is behind a bot challenge and this "
                    "Visium dataset has no GEO accession. The Xenium file CDN route that settled "
                    "TENX95 to TENX99 does not apply, since those metadata files are Xenium-"
                    "specific. HEST's embedded 0.264583 and estimated 0.273722 differ by 3.4 per "
                    "cent, below HEST's own flagging threshold."
                ),
                citation=CIT["none"],
            )
        rows.append(d)

    cols = [
        "set_name", "sample_id", "in_benchmark", "hest_patient", "source_url",
        "donor_statement", "donor_id", "donor_label_status",
        "lab", "lab_label_status", "hest_lab_provisional",
        "disease", "region", "preservation", "scanner",
        "pixel_size_um_estimated", "pixel_size_um_embedded", "magnification_hest",
        "pixel_size_source", "resolution_uncertain_hest", "resolution_uncertain_rederived",
        "notes", "hest_dataset_title", "hest_subseries", "hest_source_page", "citation",
    ]
    out = pd.DataFrame(rows)[cols].sort_values(["set_name", "sample_id"]).reset_index(drop=True)
    assert len(out) == 76, len(out)
    assert out.citation.str.len().min() > 20
    assert out.sample_id.is_unique
    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, "donor_lab_audit_ext.csv")
    out.to_csv(path, index=False)
    return out, path


def provenance(out, path):
    cfg = {"inventory": os.path.relpath(INV, ROOT),
           "members": os.path.relpath(MEMBERS, ROOT),
           "n_rows": int(len(out))}
    blob = json.dumps(cfg, sort_keys=True).encode()
    commit = subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"],
                            capture_output=True, text=True).stdout.strip()
    sha = hashlib.sha256(open(path, "rb").read()).hexdigest()
    txt = f"""dir              : {os.path.relpath(OUTDIR, ROOT)}
stage            : round3 D3 (donor and laboratory audit of the expansion sets against source records)
script           : code/scripts/round3_d3_build_audit.py
created          : {datetime.now(timezone.utc).astimezone().isoformat()}
slurm_job_id     : none (local reading stage, no cluster job)
slurm_partition  : none
node             : not recorded (local sandbox; host identity is masked)
platform         : {platform.platform()}
python           : {platform.python_version()}
executable       : {sys.executable}
commit           : {commit}
command_line     : {' '.join([sys.executable] + sys.argv)}
pythonhashseed   : {os.environ.get('PYTHONHASHSEED', 'unset')}
config           : {json.dumps(cfg, sort_keys=True)}
config_hash      : sha256:{hashlib.sha256(blob).hexdigest()[:32]}
downloads        : none by this script. The reading itself fetched api.crossref.org,
                   api.biorxiv.org, www.biorxiv.org, eutils.ncbi.nlm.nih.gov,
                   www.ncbi.nlm.nih.gov/geo, cf.10xgenomics.com (granted during the
                   stage) and Unpaywall. www.10xgenomics.com returned HTTP 429 on
                   every attempt and is recorded as unreachable.

Files and checksums (sha256, first 16 hex):

  {sha[:16]}  {os.path.getsize(path):>9,}  donor_lab_audit_ext.csv
"""
    open(os.path.join(OUTDIR, "PROVENANCE.txt"), "w").write(txt)


if __name__ == "__main__":
    o, p = build()
    provenance(o, p)
    print(len(o), p)
    print(o.donor_label_status.value_counts().to_dict())
    print(o.lab_label_status.value_counts().to_dict())
    print(o.resolution_uncertain_rederived.value_counts().to_dict())
