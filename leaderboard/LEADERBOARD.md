# CanFraudBench Leaderboard

Ranked by **E-23 overall status first**, then mean per-slice recall, then AUC.
A high AUC does **not** lift a model that fails a governance dimension.

## Track A — Synthetic Identity
| Rank | Model | E-23 | Mean Typology Recall | AUC | ECE | PSI | AIR | Failing dim |
|---|---|---|---|---|---|---|---|---|
| 1 | reference_logreg (calibrated, stdlib) | **FAIL** | 0.949 | 0.969 | 0.001 | 0.001 | 0.593 | fairness (AIR<0.80) |

## Track B — Document & Presentation Attack
| Rank | Model | E-23 | Mean Attack Recall | AUC | ECE | PSI | AIR | Failing dim |
|---|---|---|---|---|---|---|---|---|
| 1 | reference_scorer (metadata heuristic) | **FAIL** | 0.490 | 0.892 | 0.182 | 0.000 | 0.952 | calibration (ECE>0.10) |

> Both reference models post a strong AUC yet **fail overall** on a governance
> dimension. That contrast — discrimination without governance is not a passing
> model — is the benchmark's core lesson and its most forwardable result.
