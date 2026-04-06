from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v118d_cpo_add_vs_entry_time_split_validation_v1 import (
    V118DCpoAddVsEntryTimeSplitValidationAnalyzer,
)


def test_v118d_add_vs_entry_time_split_validation() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V118DCpoAddVsEntryTimeSplitValidationAnalyzer(repo_root=repo_root).analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
    )
    assert result.summary["split_count"] == 3
    assert result.summary["mean_test_balanced_accuracy"] > 0
    assert result.summary["min_test_balanced_accuracy"] <= result.summary["mean_test_balanced_accuracy"]
