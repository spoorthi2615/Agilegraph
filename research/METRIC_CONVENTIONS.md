# Metric Reporting Conventions

AgileGraph standardizes its metric reporting on a single canonical F1 score to prevent metric drift and confusion across documents. 

| Metric | Source | Meaning | Where it appears |
|---|---|---|---|
| **Bootstrapped Mean & CI** (e.g., 0.913) | `research/statistical_results.json` | 1,000-iteration bootstrap resample of the model's predictions | **Canonical headline number.** Used universally in README, status-and-limitations.md, benchmark-study.md, ablation-study.md, statistical-analysis.md, and all viva/defense materials |

Previously, a raw 5-fold mean (e.g., 0.859 ± 0.049) was reported in certain variance tables, leading to metric drift where readers copying "the F1 score" would get different numbers depending on the file. To eliminate this ambiguity, all generation scripts have been updated to report the Bootstrapped Mean & 95% Confidence Interval.

Any script or document that reports a Full Model F1 number MUST call `report_helpers.get_f1_for_model()` to guarantee the bootstrap-first canonical metric is used.

Last reconciled: Auto-updated.
