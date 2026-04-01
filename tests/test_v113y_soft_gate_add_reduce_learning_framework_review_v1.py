from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v113y_soft_gate_add_reduce_learning_framework_review_v1 import (
    V113YSoftGateAddReduceLearningFrameworkReviewAnalyzer,
    load_json_report,
)


def test_v113y_soft_gate_add_reduce_learning_framework_review() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V113YSoftGateAddReduceLearningFrameworkReviewAnalyzer()
    result = analyzer.analyze(
        v113x_payload=load_json_report(repo_root / "reports/analysis/v113x_probability_expectancy_sizing_framework_review_v1.json"),
    )

    assert result.summary["binary_gate_replacement_ready"] is True
    assert result.summary["learning_scope_first"] == "position_sizing_and_add_reduce_not_end_to_end_stock_picking"
    assert any(row["learning_problem"] == "add_when_correct" for row in result.add_reduce_learning_rows)
