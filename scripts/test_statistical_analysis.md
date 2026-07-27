# Statistical Validation Protocol

This document outlines the testing protocols established in Sprint 79.3 to mathematically verify the calculations and assumptions underlying the AgileGraph statistical analysis chapter.

## 1. Bootstrap Confidence Interval Verification
1. Open the raw arrays generated during the benchmark evaluation (`/results/raw_logits.csv`).
2. Run the validation script: `python -m scripts.verify_bootstrap --metric f1 --iterations 10000 --seed 42`.
3. **Verify**: The script must return `[0.878, 0.909]` for the F1-Score.
4. **Why**: Ensures that the reported confidence intervals were consistently generated using identical non-parametric bootstrapping vectors, guarding against manual calculation errors.

## 2. Hypothesis Test Execution
1. Utilize the paired nominal label vectors (`agilegraph_preds`, `gat_preds`, `true_labels`).
2. Run the SciPy statistical validation module: `python -m scripts.run_mcnemar`.
3. **Verify**: The module must output a $\chi^2$ value of `24.15` and a p-value `< 0.001`.
4. **Why**: Proves that the exact implementation of McNemar's test matches standard academic assumptions (without continuity corrections improperly applied).

## 3. Effect Size & Agreement Calculation Verification
1. Run the effect size module: `python -m scripts.calculate_effect_sizes`.
2. **Verify Cohen's d**: The module must divide the difference in means by the pooled standard deviation to arrive at `1.08` for the F1-Score effect size.
3. **Verify Cohen's Kappa**: The module must execute `sklearn.metrics.cohen_kappa_score` and yield `0.785`.
4. **Why**: Guarantees that the reported "Large" effect sizes and "Substantial" agreement ranks mathematically comply with standard psychometric / statistical thresholds rather than subjective interpretations.

## 4. Robustness Stability Verification
1. Assess the 10 distinct evaluation trials located in `/results/trials/`.
2. Execute: `python -m scripts.calculate_variance`.
3. **Verify**: The output standard deviation divided by the mean (Coefficient of Variation) must accurately match the reported `1.4%` for AgileGraph and `4.8%` for CodeBERT.
