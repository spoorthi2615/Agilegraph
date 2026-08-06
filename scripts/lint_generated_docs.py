import os
import sys
import re

# Canonical model names that must resolve to one consistent value doc-wide.
TRACKED_MODEL_NAMES = [
    "Full Model (w/ Heuristic)",
    "- Heterogeneous",
    "- GATv2",
    "- CodeBERT",
    "- Heuristic Feature",
    "Majority Class Baseline",
]

def check_cross_doc_consistency(doc_paths):
    """
    Scans all generated docs for lines that mention a tracked model name
    followed by a bolded or plain F1-style float (0.XXX) within the same
    line, and asserts every doc reports the SAME value for the SAME model
    name. Per Task 3b.1, the canonical value is the bootstrapped mean from
    statistical_results.json; any doc reporting the raw 5-fold mean for a
    tracked model MUST have the words "raw" or "per-fold" within the same
    line, or this check fails.
    """
    from pathlib import Path
    number_pattern = re.compile(r'\b0\.\d{3}\b')
    findings = {}  # model_name -> {value: [(doc, line_num, raw_line)]}

    for doc in doc_paths:
        path = Path(doc)
        if not path.exists():
            continue
        for line_num, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            for model_name in TRACKED_MODEL_NAMES:
                if model_name in line:
                    numbers = number_pattern.findall(line)
                    if not numbers:
                        continue
                    is_labeled_raw = ("raw" in line.lower()) or ("per-fold" in line.lower())
                    value = numbers[0]  # first number on the line, closest to the model name
                    findings.setdefault(model_name, {}).setdefault(value, []).append((doc, line_num, is_labeled_raw))

    passed = True
    for model_name, value_map in findings.items():
        # Separate labeled-raw occurrences from unlabeled (canonical) occurrences
        unlabeled_values = {v: locs for v, locs in value_map.items()
                             if any(not is_raw for (_, _, is_raw) in locs)}
        if len(unlabeled_values) > 1:
            passed = False
            print(f"[X] CROSS-DOC DRIFT: '{model_name}' reports different UNLABELED "
                  "(i.e. claimed-canonical) values across documents:")
            for value, locs in unlabeled_values.items():
                for doc, line_num, is_raw in locs:
                    if not is_raw:
                        print(f"     {value}  <-  {doc}:{line_num}")
            print("   Fix: every unlabeled occurrence must equal the canonical "
                  "bootstrapped value in research/METRIC_CONVENTIONS.md, or be "
                  "explicitly labeled 'raw'/'per-fold'.")

    if passed:
        print("[OK] Cross-document consistency check passed: every tracked model "
              "reports one canonical value everywhere it isn't explicitly labeled raw.")
    return passed

def lint_docs():
    """
    Secondary safety net: Scans generated markdown docs for hardcoded directional words
    and ensures the adjacent numeric F1 scores mathematically match the direction.
    """
    doc_paths = [
        "README.md",
        "research/statistical-analysis.md",
        "research/dataset-validation.md",
        "research/benchmark-study.md",
        "research/ablation-study.md",
        "research/status-and-limitations.md",
    ]
    
    # We look for lines containing a directional word AND two floating point numbers.
    direction_words = ["outperformed", "underperformed", "beat", "defeat", "exceed", "surpass", "higher than", "lower than"]
    
    passed = True
    
    for doc in doc_paths:
        if not os.path.exists(doc):
            continue
            
        with open(doc, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            
        for line_num, line in enumerate(lines, 1):
            line_lower = line.lower()
            
            # Simple heuristic: if a sentence has a directional word and two numbers, verify it.
            for word in direction_words:
                if word in line_lower:
                    # Find numbers like 0.853 or .484
                    numbers = [float(match) for match in re.findall(r'\b0\.\d{3}\b', line)]
                    if len(numbers) >= 2:
                        n1, n2 = numbers[0], numbers[1]
                        
                        # Example: "A outperformed B (0.853 vs 0.793)"
                        if word in ["outperformed", "beat", "defeat", "exceed", "surpass", "higher than"]:
                            if n1 <= n2:
                                print(f"[X] LINT ERROR in {doc}:{line_num}: Found '{word}' but first number ({n1}) is not greater than second number ({n2}).")
                                passed = False
                        elif word in ["underperformed", "lower than", "worse"]:
                            if n1 >= n2:
                                print(f"[X] LINT ERROR in {doc}:{line_num}: Found '{word}' but first number ({n1}) is not less than second number ({n2}).")
                                passed = False
    
    if passed:
        print("[OK] Linter passed: No conflicting hardcoded directional claims found.")
    return passed

def main():
    doc_paths = [
        "README.md",
        "research/statistical-analysis.md",
        "research/dataset-validation.md",
        "research/benchmark-study.md",
        "research/ablation-study.md",
        "research/status-and-limitations.md",
    ]
    ok1 = lint_docs()
    ok2 = check_cross_doc_consistency(doc_paths)
    if not (ok1 and ok2):
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
