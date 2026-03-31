from pathlib import Path

from a_share_quant.strategy.v112aa_phase_closure_check_v1 import (
    V112AAPhaseClosureCheckAnalyzer,
    load_json_report,
)


def test_v112aa_phase_closure_enters_waiting_state() -> None:
    analyzer = V112AAPhaseClosureCheckAnalyzer()
    result = analyzer.analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v112aa_phase_check_v1.json"))
    )
    assert result.summary["enter_v112aa_waiting_state_now"] is True
    assert result.summary["allow_auto_training_now"] is False
