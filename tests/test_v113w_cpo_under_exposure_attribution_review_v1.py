from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v113w_cpo_under_exposure_attribution_review_v1 import (
    V113WCPOUnderExposureAttributionReviewAnalyzer,
    load_json_report,
)


def test_v113w_cpo_under_exposure_attribution_review() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V113WCPOUnderExposureAttributionReviewAnalyzer()
    result = analyzer.analyze(
        v113v_payload=load_json_report(repo_root / "reports/analysis/v113v_cpo_full_board_execution_main_feed_replay_v1.json"),
    )

    assert result.summary["strategy_curve"] > 1.0
    assert result.summary["board_equal_weight_curve"] > result.summary["strategy_curve"]
    assert result.summary["top_opportunity_miss_count"] >= 1
