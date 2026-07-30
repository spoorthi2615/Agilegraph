# Metric Reporting Conventions

AgileGraph reports two related but distinct F1 numbers. Both are legitimate; they
must never be swapped or presented as interchangeable without a label.

| Number | Source | Meaning | Where it appears |
|---|---|---|---|
| **0.913** (bootstrapped mean, CI [0.908, 0.919]) | `research/statistical_results.json` | 1,000-iteration bootstrap resample of the Full Model's predictions | **Canonical headline number.** README, status-and-limitations.md, benchmark-study.md, ablation-study.md, any viva/defense materials |
| 0.859 ± 0.049 (raw 5-fold mean) | `research/results.json` | Simple mean/std across the 5 CV folds, no resampling | Only in `statistical-analysis.md`'s per-fold variance table, explicitly labeled "raw per-fold mean" |

Any script or document that reports a Full Model F1 number MUST call
`report_helpers.get_f1_for_model()` (bootstrap-first) unless it is specifically
presenting per-fold raw variance, in which case it must use the words
"raw per-fold mean" adjacent to the number.

Last reconciled: [Date inserted post-Task 3b.6]
