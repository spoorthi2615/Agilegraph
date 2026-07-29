---
name: regenerate-research-doc
description: Automates the generation of research markdown documents from JSON results files to prevent metrics drift.
---

# Regenerate Research Doc Skill

## Context
When writing research papers, benchmark studies, or ablation studies, the metrics (F1 scores, Kappa, p-values) change frequently as models are re-trained or evaluated. If these numbers are hand-edited into markdown documents, they will inevitably drift and become inconsistent with the actual code output.

## Rule
**Never manually edit evaluation metrics (F1, Accuracy, Kappa, p-values, etc.) directly into a markdown document.**

## Execution Pattern
1. Ensure the metrics are exported to a stable JSON file (e.g., `research/results.json` or `research/statistical_results.json`).
2. Write a Python script (e.g., `scripts/generate_benchmark_report.py`) that reads the JSON files and programmatically constructs the Markdown string.
3. The script should explicitly write out the full Markdown document and overwrite the existing one.
4. Add the generated Markdown document and the generator script to the drift-checking mechanism (e.g., `scripts/check_doc_drift.py`) so that the pipeline fails if the docs are out of date with the code.

By following this pattern, you ensure that every number in every document is directly traceable to a live evaluation run.
