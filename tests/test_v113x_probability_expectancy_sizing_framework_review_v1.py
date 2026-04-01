from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v113x_probability_expectancy_sizing_framework_review_v1 import (
    V113XProbabilityExpectancySizingFrameworkReviewAnalyzer,
    load_json_report,
)


def test_v113x_probability_expectancy_sizing_framework_review() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V113XProbabilityExpectancySizingFrameworkReviewAnalyzer()
    result = analyzer.analyze(
        v113v_payload=load_json_report(repo_root / "reports/analysis/v113v_cpo_full_board_execution_main_feed_replay_v1.json"),
        v113w_payload=load_json_report(repo_root / "reports/analysis/v113w_cpo_under_exposure_attribution_review_v1.json"),
    )

    assert result.summary["framework_ready_for_replay_injection_next"] is True
    assert result.summary["recommended_two_line_strong_board_min_gross_exposure"] == 0.50
    assert any(row["default_expression"] == "high_expression" for row in result.source_sizing_rows)
