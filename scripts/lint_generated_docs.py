import os
import sys
import re
from pathlib import Path

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
        "research/ablation-study.md"
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
            # This is a basic catch-all for regressions, not a full NLP parser.
            for word in direction_words:
                if word in line_lower:
                    # Find numbers like 0.853 or .484
                    numbers = [float(match) for match in re.findall(r'\b0\.\d{3}\b', line)]
                    if len(numbers) >= 2:
                        n1, n2 = numbers[0], numbers[1]
                        
                        # Example: "A outperformed B (0.853 vs 0.793)"
                        if word in ["outperformed", "beat", "defeat", "exceed", "surpass", "higher than"]:
                            if n1 <= n2:
                                print(f"❌ LINT ERROR in {doc}:{line_num}: Found '{word}' but first number ({n1}) is not greater than second number ({n2}).")
                                passed = False
                        elif word in ["underperformed", "lower than", "worse"]:
                            if n1 >= n2:
                                print(f"❌ LINT ERROR in {doc}:{line_num}: Found '{word}' but first number ({n1}) is not less than second number ({n2}).")
                                passed = False
    
    if passed:
        print("✅ Linter passed: No conflicting hardcoded directional claims found.")
        return True
    else:
        return False

if __name__ == "__main__":
    if not lint_docs():
        sys.exit(1)
