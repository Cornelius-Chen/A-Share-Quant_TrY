from pathlib import Path

from a_share_quant.strategy.v112bu_phase_check_v1 import (
    V112BUPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112bu_phase_check_runs() -> None:
    analyzer = V112BUPhaseCheckAnalyzer()
    result = analyzer.analyze(
        control_pilot_payload=load_json_report(Path("reports/analysis/v112bu_phase_conditioned_control_pilot_v1.json")),
    )
    assert result.summary["ready_for_phase_closure_next"] is True
