from pathlib import Path

from a_share_quant.strategy.v112v_phase_check_v1 import (
    V112VPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112v_phase_check_keeps_training_closed() -> None:
    analyzer = V112VPhaseCheckAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112v_phase_charter_v1.json")),
        operationalization_payload=load_json_report(
            Path("reports/analysis/v112v_cpo_daily_board_chronology_operationalization_v1.json")
        ),
    )
    assert result.summary["allow_auto_training_now"] is False
    assert result.summary["ready_for_phase_closure_next"] is True
