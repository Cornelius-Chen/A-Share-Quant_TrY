from pathlib import Path

from a_share_quant.strategy.v112bj_phase_check_v1 import (
    V112BJPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112bj_phase_check_accepts_teacher_gate_line() -> None:
    analyzer = V112BJPhaseCheckAnalyzer()
    result = analyzer.analyze(
        teacher_gate_pilot_payload=load_json_report(Path("reports/analysis/v112bj_cpo_neutral_teacher_gate_pilot_v1.json")),
    )
    assert result.summary["ready_for_phase_closure_next"] is True
