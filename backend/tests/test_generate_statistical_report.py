import json
import os
import sys
from pathlib import Path

# Add scripts directory to path
scripts_dir = Path(__file__).resolve().parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from generate_statistical_report import main


def test_generate_statistical_report(tmp_path, monkeypatch):
    """
    Unit test for generate_statistical_report.py to verify table_rows initialization
    and correct markdown generation without NameError.
    """
    monkeypatch.chdir(tmp_path)
    os.makedirs("research", exist_ok=True)

    # Create fixture JSON files
    results_data = {
        "run_id": "295ddf1e",
        "ablation_f1": {"Full Model": {"mean": 0.92}, "No Heuristics": {"mean": 0.85}},
    }
    stats_data = {
        "run_id": "295ddf1e",
        "Full Model": {"mean_f1": 0.92, "ci_lower": 0.90, "ci_upper": 0.94},
        "kappa": {"Full Model": {"score": 0.88}},
    }
    preds_data = {"run_id": "295ddf1e", "Full Model": [1, 0, 1], "CBOMkit Baseline": [0, 0, 1]}

    with open("research/results.json", "w") as f:
        json.dump(results_data, f)
    with open("research/statistical_results.json", "w") as f:
        json.dump(stats_data, f)
    with open("research/predictions.json", "w") as f:
        json.dump(preds_data, f)

    main()

    stat_file = Path("research/statistical-analysis.md")
    assert stat_file.exists()
    content = stat_file.read_text(encoding="utf-8")

    # Structural & Content Assertions
    assert "| Model Variant | Macro-F1 (Bootstrapped Mean & CI) | Cohen's Kappa |" in content
    assert "|---|---|---|" in content
    assert "| Full Model | 0.920 (CI [0.900, 0.940]) | 0.880 |" in content
    assert "| No Heuristics | 0.850 | 0.000 |" in content
    assert "| CBOMkit Baseline | N/A (See Benchmark) | 0.000 |" in content
    assert content.count("| Full Model |") >= 1


def test_generate_statistical_report_empty_dataset(tmp_path, monkeypatch):
    """
    Edge case test for generate_statistical_report.py with an empty dataset.
    Verifies that the script executes cleanly and outputs valid table headers without crashing.
    """
    monkeypatch.chdir(tmp_path)
    os.makedirs("research", exist_ok=True)

    results_data = {"run_id": "44136fa3", "ablation_f1": {}}
    stats_data = {"run_id": "44136fa3", "kappa": {}}
    preds_data = {"run_id": "44136fa3"}

    with open("research/results.json", "w") as f:
        json.dump(results_data, f)
    with open("research/statistical_results.json", "w") as f:
        json.dump(stats_data, f)
    with open("research/predictions.json", "w") as f:
        json.dump(preds_data, f)

    main()

    stat_file = Path("research/statistical-analysis.md")
    assert stat_file.exists()
    content = stat_file.read_text(encoding="utf-8")
    assert "| Model Variant | Macro-F1 (Bootstrapped Mean & CI) | Cohen's Kappa |" in content
    assert "|---|---|---|" in content
