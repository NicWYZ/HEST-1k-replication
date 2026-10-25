# Between-donor head test, predictions scored

Scored 25 October 2026 from between_head_medians.csv (medians over genes of out-of-sample R^2 of the donor mean) and between_head_gene_spread_lodo.csv.

- P1 held. Median LODO R^2 of the recalibrated pooled head on CCRCC and INDIANA_KIDNEY ranges from -0.097 to -0.032, at most 0.10 for every encoder.
- P2 refuted. On CCRCC the shrink-to-within head changes the median LODO R^2 by -0.028 to -0.009 against the pooled head, never by +0.05.
- P3 refuted, in the other direction from the one predicted. On LUNG_XENIUM the change is -0.183 to -0.104, a loss of more than 0.05 for every encoder.
- P4 held. With 8 training donors the change on CCRCC is -0.871 to -0.586, below 0.02.

Reading. Out of sample, no donor-level predictor beats a constant for the median gene. The gene-level spread (between_head_gene_spread_lodo.csv) shows that the pooled head beats the constant for 0.46 to 0.64 of genes and by more than 0.1 for 0.28 to 0.52, and that the shrink head beats the pooled head for at most 0.155 of genes. A between-donor head does not help at these numbers of donors.
