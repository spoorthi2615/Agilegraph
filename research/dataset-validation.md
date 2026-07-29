# Dataset Validation
    
    ## Corpus Specifications
    - **Total Repositories**: 40
    - **Cross-Validation**: 5-Fold Repo-level splits
    - **Labeling Scheme**: Binary (`PQC-Safe` vs `Legacy-Vulnerable`) deterministically derived from AST primitive matching (e.g. RSA, ECDSA -> Vulnerable).
    - **Internal Validation**: Each fold holds out 15% of its training repos for early-stopping validation to prevent data leakage.
    
    *Note: The original 10-repository corpus was found to be statistically degenerate. The 40-repo dataset ensures that single-repo anomalies cannot drag the F1 score to 0.*
    