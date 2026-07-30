# AgileGraph: What Changed Since the Synopsis

This addendum serves to clarify the discrepancies between the early exploratory claims made in the original project synopsis and the final, mathematically rigorous, and verified implementation of the AgileGraph framework. These updates reflect the natural maturation of the research from theoretical design to practical execution.

## 1. Corpus Expansion (10 to 40 Repositories)
**Initial Synopsis Claim:** The dataset was scoped to 8–10 expert-annotated Java repositories.
**Final Reality:** To eliminate data starvation and ensure the Graph Neural Network (GNN) could properly generalize, the corpus was aggressively expanded to **40 repositories**. This significantly bolsters the statistical validity of the dataset.

## 2. CBOMkit Baseline Scope
**Initial Synopsis Claim:** CBOMkit would be used as a direct baseline comparison for source-code cryptographic vulnerability detection.
**Final Reality:** CBOMkit is primarily designed to scan binary artifacts and manifest files for SBOM generation, and its source-code scanning capabilities are fundamentally different in objective compared to AgileGraph's deep topological vulnerability detection. While we successfully ran the CBOMkit Docker baseline across the 40 repositories, comparing its manifest-level findings directly to AgileGraph's source-level semantic findings proved to be an apples-to-oranges comparison. As a result, the evaluation focuses on comparing the Full AgileGraph model against ablated versions of itself (e.g., without Heuristics, or using CodeBERT/GATv2 individually) to prove the value of its specific architecture.

## 3. Reconciled Performance Metrics
**Initial Synopsis Claim:** Outdated or aspirational F1 scores scattered across early documentation drafts.
**Final Reality:** After patching a rigorous 5-fold cross-validation pipeline with strict Train/Validation isolation (preventing any data leakage), the final, mathematically verified performance for the Full Model (w/ Heuristics) is a **Macro-F1 score of 0.859**. This single source of truth is now perfectly synchronized across all generated research reports and the README.

## 4. Addition of the AHP-Lite Expert Panel Module
**Initial Synopsis Claim:** An "expert panel pairwise weighting mechanism" was referenced but unimplemented in the early codebase.
**Final Reality:** To close this gap identified during review, the mathematical backend for the AHP-lite module was fully implemented (`ahp_lite_service.py`). It mathematically derives objective weights from expert pairwise comparisons by calculating the Principal Eigenvector via eigenvalue decomposition, and mathematically verifies the experts' logic by calculating the standard Consistency Ratio (CR).
