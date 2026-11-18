# A7: what each encoder's published description states about its pretraining data

*17 November 2026. Task A7 of track `closeout` (brief, section 4, standard 8). Searched by sub-agent frame `c9016697-c909-435e-82fc-ebfb9daaa857/a7`, which opened every source below; the three model cards were reopened by a second fetch to confirm the table's facts (result at the end). Summaries are in the track's own words. No phrase is quoted, because the fetch tool's quoted phrases were not checked against the pages.*

The encoders behind the arms are `uni_v2` (`R10`, `P`, `E`), `hoptimus0` (`E`) and `virchow2` (`V`, `E`).

| Encoder | Pretraining data, as stated | Public datasets named among the pretraining sources | Decontamination statement | Anything on the HEST cohorts used here |
|---|---|---|---|---|
| UNI2-h (`uni_v2`) | Over 200 million tiles from H&E and IHC slides from Mass General Brigham. The model card gives the slide count as over 350,000 in one section and over 300,000 in another [1] | None. TCGA, CPTAC and PANDA appear on the card only as datasets for which embeddings are released [1] | None on the card [1] | Nothing |
| UNI v1 (context only; not used here) | Mass-100K: 100,426 H&E slides of 20 tissue types from MGH, BWH and GTEx, of which 24,782 are GTEx autopsy slides [2] | GTEx [2] | TCGA, CPTAC and PAIP were deliberately left out so that they could serve for external evaluation [2] | Nothing about HEST, Visium or Xenium. GTEx includes kidney, colon, brain and lung tissue, but the paper links GTEx to no HEST cohort, and whether UNI2-h's data includes GTEx is not stated [1, 2] |
| H-optimus-0 (`hoptimus0`) | A proprietary collection of more than 500,000 H&E slides from many body sites, with at most 3 slides per patient (1.5 on average) [4, 5] | None named. TCGA and Camelyon appear only as evaluation benchmarks [4, 5] | None [4, 5] | Nothing |
| Virchow2 (`virchow2`) | 3.1 million slides of 225,401 patients from Memorial Sloan Kettering Cancer Center, nearly 200 tissue types, H&E and IHC. About 15% of the slides (57% of the patients) are consultation cases that outside institutions sent to MSKCC [6, 7] | None. The paper's data table lists MSKCC as the only source [7] | No explicit statement. A figure caption notes that some evaluation data shares no patients with the training data, which concerns evaluation sets [7] | Nothing. The outside consultation cases are not identified, so overlap with any public cohort can be neither confirmed nor ruled out |

**Reading for the report.** For each cohort the project embeds (ccRCC Visium, Indiana / KPMP kidney Visium, kidney, bowel and brain Visium, lung Xenium), none of the three descriptions says anything. None names a public dataset among UNI2-h's, H-optimus-0's or Virchow2's pretraining sources. Overlap is therefore not stated, which is weaker than ruled out: H-optimus-0's sources are not named at all, and Virchow2 includes unidentified outside cases.

## Sources

1. MahmoodLab, *UNI2-h* model card, Hugging Face, 2025. https://huggingface.co/MahmoodLab/UNI2-h. Read level: model card.
2. Chen RJ, Ding T, Lu MY, Williamson DFK, Jaume G, et al., Mahmood F. "Towards a general-purpose foundation model for computational pathology." *Nature Medicine*, 2024. DOI 10.1038/s41591-024-02857-3, opened at https://pmc.ncbi.nlm.nih.gov/articles/PMC11403354/. Read level: full text, partly (the first 40% of the text, which holds the Methods and Discussion passages used here).
3. Chen RJ et al. "A General-Purpose Self-Supervised Model for Computational Pathology." arXiv 2308.15474, 2023. Read level: abstract only. Names no data source.
4. Bioptimus, *H-optimus-0* model card, Hugging Face, 2024. https://huggingface.co/bioptimus/H-optimus-0. Read level: model card.
5. Bioptimus, `releases/models/h-optimus/v0` README, GitHub, 2024. https://github.com/bioptimus/releases/tree/main/models/h-optimus/v0. Read level: model card.
6. Paige, *Virchow2* model card, Hugging Face, 2024. https://huggingface.co/paige-ai/Virchow2. Read level: model card.
7. Zimmermann E, Vorontsov E, Viret J, Casson A, Zelechowski M, Shaikovski G, Tenenholtz N, Hall J, Fuchs T, Fusi N, Liu S, Severson K. "Virchow2: Scaling Self-Supervised Mixed Magnification Models in Pathology." arXiv 2408.00738, 2024. https://arxiv.org/html/2408.00738. Read level: full text (an appendix tail not read).

**Not found.** H-optimus-0 has no technical report, and UNI2-h has no paper; their model cards are their only published descriptions of the pretraining data.

**Second fetch of the model cards (17 November).** A separate fetch reopened [1], [4] and [6] (each gated for the weights, the card text readable) and agrees: UNI2-h, over 200 million tiles from Mass General Brigham slides, the slide count given as over 350,000 and as over 300,000 in two sections; H-optimus-0, a proprietary collection of more than 500,000 H&E slides, no source named; Virchow2, an internal set of 3.1 million slides from MSKCC. No card names a public dataset as pretraining data, states a decontamination rule or mentions spatial transcriptomics, Visium, Xenium or HEST.
