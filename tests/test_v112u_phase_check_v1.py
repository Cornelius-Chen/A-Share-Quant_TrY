from pathlib import Path

from a_share_quant.strategy.v112u_phase_check_v1 import (
    V112UPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112u_phase_check_keeps_training_closed() -> None:
    analyzer = V112UPhaseCheckAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112u_phase_charter_v1.json")),
        readiness_review_payload=load_json_report(Path("reports/analysis/v112u_cpo_foundation_readiness_review_v1.json")),
    )
    assert result.summary["allow_auto_training_now"] is False
    assert result.summary["foundation_is_complete_enough_for_bounded_research"] is True
