# Evidence: HEST issue #133, retrieved 2026-09-19 via the GitHub REST API

Saved so the citation in docs/hest_bench_issue_draft.md and the R5b audit is checkable
without re-fetching. Retrieved with an authenticated GET to
api.github.com/repos/mahmoodlab/HEST/issues/133 and .../comments.

- number: 133
- state: closed
- title: Question about COAD patient split consistency after adding TENX147/148/149 in HEST v1.3.0
- created: 2026-03-22T08:52:34Z
- author: hrterry
- comments: 2

## Body

```
Hi,

Thanks for maintaining and updating the HEST dataset — it’s been very useful for our research.
I have a question regarding the COAD samples and the corresponding split definition in HEST-bench, after the recent update to v1.3.0.

In HEST v1.1.0, the following samples were not included:

* TENX147
* TENX148
* TENX149

In **HEST v1.3.0**, these samples are now added under COAD, and according to the metadata:

* TENX147 → patient 5
* TENX148 → patient 2
* TENX149 → patient 1

This suggests that these three samples correspond to **three different patients**.

However, in previous [issues](https://github.com/mahmoodlab/HEST/issues/87) about **HEST-bench**, it was stated that:

* TENX111 corresponds to one patient
* TENX147/148/149 correspond to **another single patient**

This seems inconsistent with the updated metadata, where:

* TENX147/148/149 are now mapped to **different patients**

I have the following questions:
* Should the train/test split in HEST-bench (for COAD) be updated accordingly to reflect the corrected patient identities?
* Do the updated HEST-Benchmark results (03.04.26) still follow the original split definition, or were the splits recomputed after incorporating the new samples and metadata?

Thanks in advance for your clarification!

Best,
Haron

```

## Comment — pauldoucet (COLLABORATOR), 2026-03-22

```
Hello Haron,
Thanks for reaching out. Indeed, the patient information for this cohort was wrong in HEST v1.1.0 (as reported in [this issue](https://github.com/mahmoodlab/HEST/issues/126)) and was corrected in HEST v1.3.0.

We chose not to update HEST-bench COAD splits as we're still satisfying the core requirement of ensuring the same patient does not appear in both the train and test splits for any given fold,

Best,
Paul
```

## Comment — hrterry (NONE), 2026-03-22

```
Thanks for the quick clarification! This makes perfect sense, and we really appreciate you confirming the split logic.
```
