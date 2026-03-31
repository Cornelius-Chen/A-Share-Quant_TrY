from pathlib import Path

from a_share_quant.strategy.v112ar_phase_check_v1 import V112ARPhaseCheckAnalyzer
from a_share_quant.strategy.v112ar_phase_charter_v1 import load_json_report


def test_v112ar_phase_check_keeps_row_widen_blocked() -> None:
    analyzer = V112ARPhaseCheckAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112ar_phase_charter_v1.json")),
        patch_spec_payload=load_json_report(Path("reports/analysis/v112ar_cpo_feature_implementation_patch_spec_v1.json")),
    )
    assert result.summary["allow_row_geometry_widen_now"] is False
    assert result.summary["ready_for_phase_closure_next"] is True
