from pathlib import Path

from a_share_quant.strategy.v112aw_phase_closure_check_v1 import (
    V112AWPhaseClosureCheckAnalyzer,
    load_json_report,
)


def test_v112aw_phase_closure_moves_to_next_posture() -> None:
    analyzer = V112AWPhaseClosureCheckAnalyzer()
    result = analyzer.analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v112aw_phase_check_v1.json")),
    )
    assert result.summary["v112aw_success_criteria_met"] is True
