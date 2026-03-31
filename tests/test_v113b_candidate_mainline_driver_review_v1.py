from pathlib import Path

from a_share_quant.strategy.v113b_candidate_mainline_driver_review_v1 import (
    V113BCandidateMainlineDriverReviewAnalyzer,
    load_json_report,
)


def test_v113b_candidate_mainline_driver_review_v1_keeps_promotion_closed() -> None:
    result = V113BCandidateMainlineDriverReviewAnalyzer().analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v113b_phase_charter_v1.json")),
        state_schema_payload=load_json_report(Path("reports/analysis/v113a_theme_diffusion_state_schema_v1.json")),
    )
    assert result.summary["candidate_driver_count_reviewed"] == 10
    assert result.summary["bounded_state_usage_ready_count"] == 4
    assert result.summary["formal_driver_promotion_now"] is False
