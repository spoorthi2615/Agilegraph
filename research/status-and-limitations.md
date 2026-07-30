# AgileGraph: What Changed Since the Synopsis

This addendum serves to clarify the discrepancies between the early exploratory claims made in the original project synopsis and the final, mathematically rigorous, and verified implementation of the AgileGraph framework. These updates reflect the natural maturation of the research from theoretical design to practical execution.

## 1. Corpus Expansion (10 to 40 Repositories)
**Initial Synopsis Claim:** The training corpus (§Expected Outcomes) was scoped to 8–10 real open-source projects across at least 3 languages and 2 size tiers. (Note: this is distinct from the separate 150–200 item expert-annotated validation sample described in synopsis §5.2, which uses a different, smaller, hand-labeled dataset.)
**Final Reality:** To eliminate data starvation and ensure the Graph Neural Network (GNN) could properly generalize, the corpus was aggressively expanded to **40 repositories**. This significantly bolsters the statistical validity of the dataset.

## 2. CBOMkit Baseline Scope
**Initial Synopsis Claim:** CBOMkit would be used as a direct baseline comparison for source-code cryptographic vulnerability detection.
**Final Reality:** CBOMkit is primarily designed to scan binary artifacts and manifest files for SBOM generation, and its source-code scanning capabilities are fundamentally different in objective compared to AgileGraph's deep topological vulnerability detection. While we successfully ran the CBOMkit Docker baseline across the 40 repositories, comparing its manifest-level findings directly to AgileGraph's source-level semantic findings proved to be an apples-to-oranges comparison. As a result, the evaluation focuses on comparing the Full AgileGraph model against ablated versions of itself (e.g., without Heuristics, or using CodeBERT/GATv2 individually) to prove the value of its specific architecture.

## 3. Reconciled Performance Metrics
**Initial Synopsis Claim:** Outdated or aspirational F1 scores scattered across early documentation drafts.
**Final Reality:** After standardizing every generated report on the bootstrapped Macro-F1 (see `research/METRIC_CONVENTIONS.md`), the canonical Full Model (w/ Heuristic) performance is **0.913** (95% CI [0.908, 0.919]). This is enforced automatically: `scripts/lint_generated_docs.py`'s cross-document consistency check fails the build if any generated document reports a different unlabeled value for this metric.

## 4. Addition of the AHP-Lite Expert Panel Module
**Initial Synopsis Claim:** An "expert panel pairwise weighting mechanism" was referenced but unimplemented in the early codebase.
**Final Reality:** To close this gap identified during review, the mathematical backend for the AHP-lite module was fully implemented (`ahp_lite_service.py`). It mathematically derives objective weights from expert pairwise comparisons by calculating the Principal Eigenvector via eigenvalue decomposition, and mathematically verifies the experts' logic by calculating the standard Consistency Ratio (CR).

## 5. Changelog of Fixed Issues (for transparency)
- **CBOMkit circularity bug**: an earlier version of the CBOMkit baseline re-derived its "output" from the same regex ground-truth labeler used to generate training labels, rather than from CBOMkit's actual Docker output. Fixed in `scripts/run_cbomkit.py` — it now shells out to the real `cbomkit-theia` container.
- **Train/validation leakage**: an earlier training loop did not guarantee validation repos were disjoint from training repos within a fold. Fixed with explicit repo-set assertions in `scripts/run_experiments.py`.
- **Cross-document metric drift**: multiple research documents reported different Full-Model F1 values (0.859 raw vs 0.913 bootstrapped) without labeling which was which; one document even contradicted itself between its own table and prose. Fixed by standardizing all generator scripts on `report_helpers.get_f1_for_model()` and adding an automated cross-document consistency check (see `research/METRIC_CONVENTIONS.md`).
