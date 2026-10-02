| task | predictor | $n_L$ | unit $R^2$ (outcome) | cluster $R^2$ (outcome) | $1-R^2_{\text{cl}}$ (donor $z$) | ratio, donor, (c) | ratio, donor, (d1) | ratio, donor, (d2) | ratio, spot, (c) |
|---|---|---|---|---|---|---|---|---|---|
| CCRCC | hoptimus0 | 16 | 0.083 | 0.076 | 0.713 | 1.186 | 1.184 | 1.086 | 0.742 |
| CCRCC | uni_v2 | 16 | 0.085 | 0.128 | 0.561 | 1.133 | 1.181 | 1.130 | 0.770 |
| CCRCC | resnet50 | 16 | 0.058 | 0.049 | 0.800 | 1.156 | 1.162 | 1.068 | 0.823 |
| CCRCC | permuted | 16 | 0.000 | 0.015 | 0.981 | 1.018 | 1.010 | 1.000 | 0.891 |
| CCRCC_merged | hoptimus0 | 16 | 0.083 | 0.082 | 0.744 | 1.342 | 1.358 | 1.182 | 0.919 |
| CCRCC_merged | uni_v2 | 16 | 0.085 | 0.140 | 0.571 | 1.152 | 1.278 | 1.136 | 0.955 |
| CCRCC_merged | resnet50 | 16 | 0.057 | 0.049 | 0.780 | 1.270 | 1.234 | 1.056 | 1.001 |
| CCRCC_merged | permuted | 16 | 0.000 | 0.047 | 0.914 | 1.024 | 1.000 | 1.000 | 1.257 |
| INDIANA_KIDNEY | hoptimus0 | 16 | 0.046 | 0.115 | 0.814 | 1.098 | 1.122 | 1.016 | 0.857 |
| INDIANA_KIDNEY | uni_v2 | 16 | 0.053 | 0.112 | 0.861 | 1.124 | 1.086 | 1.017 | 0.785 |
| INDIANA_KIDNEY | resnet50 | 16 | 0.019 | 0.074 | 0.949 | 1.090 | 1.039 | 1.000 | 0.848 |
| INDIANA_KIDNEY | permuted | 16 | 0.000 | 0.021 | 0.964 | 1.068 | 1.007 | 1.001 | 0.909 |
| LUNG_XENIUM | hoptimus0 | 12 | 0.374 | 0.222 | 0.270 | 1.527 | 1.578 | 1.429 | 1.459 |
| LUNG_XENIUM | uni_v2 | 12 | 0.373 | 0.230 | 0.286 | 1.624 | 1.671 | 1.448 | 1.568 |
| LUNG_XENIUM | resnet50 | 12 | 0.257 | 0.196 | 0.346 | 1.374 | 1.432 | 1.295 | 1.632 |
| LUNG_XENIUM | permuted | 12 | 0.000 | 0.064 | 0.967 | 1.123 | 1.005 | 1.000 | 1.426 |
| ACS_STATES | package | 16 | 0.621 | 0.569 | 0.297 | 0.494 | 0.519 | 0.601 | 0.100 |
| ACS_STATES | permuted | 16 | 0.000 | 0.001 | 0.961 | 1.010 | 1.011 | 0.986 | 0.107 |
| ACS_CA_PUMA | package | 16 | 0.612 | 0.951 | 0.120 | 0.155 | 0.157 | 0.182 | 0.002 |
| ACS_CA_PUMA | permuted | 16 | 0.000 | 0.004 | 1.000 | 1.034 | 0.996 | 0.993 | 0.013 |

Source `results/round4/ppi/Q2_theory/q2_report_numbers.csv` (names `Q2.1|...`) and `q2_cluster_r2.csv` (scale `log1p_y`, median over genes); $\theta_3$, $m$ = all, largest $n_L$, superpopulation target, CR1.
