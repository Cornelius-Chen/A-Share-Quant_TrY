from pathlib import Path

from a_share_quant.strategy.v112ap_phase_check_v1 import (
    V112APPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112ap_phase_check_preserves_report_only_boundary() -> None:
    analyzer = V112APPhaseCheckAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112ap_phase_charter_v1.json")),
        widen_pilot_payload=load_json_report(Path("reports/analysis/v112ap_cpo_bounded_secondary_widen_pilot_v1.json")),
    )
    assert result.summary["allow_auto_training_now"] is False
    assert result.summary["ready_for_phase_closure_next"] is True
