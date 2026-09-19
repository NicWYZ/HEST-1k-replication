# Evidence: HEST issue #126, retrieved 2026-09-19 via the GitHub REST API

Cited by the collaborator's reply in issue #133 as the original report. Saved because the
cross-reference needs explaining: #126 concerns the SAME STUDY but its Visium HD samples
(TENX153-156, TENX128), none of which are in HEST-bench; our COAD samples TENX147/148/149
are that study's Xenium In Situ arm, added in v1.3.0.

- number: 126
- state: closed
- title: IMPORTANT: Patient ID Confusion and Duplicate Samples in HEST-1k Visium HD Colon Cancer Data
- created: 2026-01-12T09:42:19Z
- author: alexaex

## Body

```
I have checked 5 Visium HD Colon Cancer samples. The IDs of these samples in HEST-1k are:
1. TENX156 (P1 CRC)
2. TENX155 (P2 CRC)
3. TENX154 (P5 CRC)
4. TENX153 (Healthy) (P3 NAT)
5. TENX128

The `HEST_v1_1_2_0` metadata indicates that samples 1, 2, 3, and 4 originate from the same patient, patient 1. However, these samples (1, 2, 3, and 4) come from the study "Characterization of immune cell populations in the tumor microenvironment of colorectal cancer using high definition spatial profiling", which states that the 3 colon cancer samples and 2 healthy adjacent slices were obtained from 5 different patients (3 women and 2 men). One Healthy sample is not recorded in HEST-1k; is it possible it was excluded because it is an adjacent slice?

Additionally, I checked the summary from 10x Genomics and found that `TENX128` is actually part of the "Characterization of immune cell populations in the tumor microenvironment of colorectal cancer using high definition spatial profiling" study as well. This sample `TENX128` is identical to the P2 sample (TENX155) in that study, though their source links are different.

<img width="1281" height="589" alt="Image" src="https://github.com/user-attachments/assets/63cda7cd-a584-4a3a-8eec-5b2fdda9474a" />

My questions are listed here:
1. Why are TENX156, 155, 154, and 153 attributed to the same patient (patient 1) in HEST-1k?
2. Since the P2 sample (TENX155) is actually TENX128, why does HEST-1k contain duplicate samples? You can verify this against the data summary provided by 10x Genomics.
3. Are all image patches standardized to the same physical resolutions (e.g., `112um x 112um`) and subsequently resized to a fixed pixel resolution (e.g., `224x224`)?


Thanks for your time!
```

## Comment — alexaex (NONE), 2026-01-12

```
<img width="2442" height="115" alt="Image" src="https://github.com/user-attachments/assets/c2c422be-f768-4b88-9e80-1eeddf154aac" />

Thanks for the Microsoft Excel. I’ve recorded the sample info and put it here.

btw, the Visium HD Breast Cancer data (3 samples: Fresh Frozen, Fixed Frozen, and one Fresh Frozen Ultima Sequencing) appears to be correct. 
```

## Comment — pauldoucet (COLLABORATOR), 2026-01-12

```
Thanks for reporting this mistake @alexaex, 

Indeed the patient information for study "Characterization of immune cell..." is wrong and has been replaced in dataset version v1.2.1.

We try not to include duplicates in HEST, however it seems like TENX155 and TENX128 were both mistakenly included despite being exact duplicates. We'll remove one of them in the future.

Yes, all image patches are standardized to the same physical resolution 112um x 112um and subsequently resized to 224x224 pixels. See [this discussion](https://github.com/mahmoodlab/HEST/issues/86), we provide methods to patch at a different resolution.
```
