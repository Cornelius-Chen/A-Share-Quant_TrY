from pathlib import Path

from a_share_quant.strategy.v113c_bounded_state_usage_review_v1 import (
    V113CBoundedStateUsageReviewAnalyzer,
    load_json_report,
)


def test_v113c_bounded_state_usage_review_v1_keeps_usage_schema_only() -> None:
    result = V113CBoundedStateUsageReviewAnalyzer().analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v113c_phase_charter_v1.json")),
        driver_review_payload=load_json_report(Path("reports/analysis/v113b_candidate_mainline_driver_review_v1.json")),
    )
    assert result.summary["reviewed_high_priority_driver_count"] == 4
    assert result.summary["drivers_allowed_for_schema_review_only"] == 4
    assert result.summary["formal_driver_promotion_now"] is False
    assert result.summary["model_usage_now"] is False
