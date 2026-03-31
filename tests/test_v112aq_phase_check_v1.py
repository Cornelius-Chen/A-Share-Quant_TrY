from pathlib import Path

from a_share_quant.strategy.v112aq_phase_check_v1 import V112AQPhaseCheckAnalyzer
from a_share_quant.strategy.v112aq_phase_charter_v1 import load_json_report


def test_v112aq_phase_check_keeps_row_widen_closed() -> None:
    analyzer = V112AQPhaseCheckAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112aq_phase_charter_v1.json")),
        patch_review_payload=load_json_report(Path("reports/analysis/v112aq_cpo_feature_implementation_patch_review_v1.json")),
    )
    assert result.summary["allow_row_geometry_widen_now"] is False
    assert result.summary["ready_for_phase_closure_next"] is True
