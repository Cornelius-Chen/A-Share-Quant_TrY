from pathlib import Path

from a_share_quant.strategy.v112af_phase_check_v1 import (
    V112AFPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112af_phase_check_keeps_promotion_closed() -> None:
    analyzer = V112AFPhaseCheckAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112af_phase_charter_v1.json")),
        feature_family_review_payload=load_json_report(Path("reports/analysis/v112af_cpo_feature_family_design_review_v1.json")),
    )
    assert result.summary["allow_auto_feature_promotion_now"] is False
    assert result.summary["ready_for_phase_closure_next"] is True
