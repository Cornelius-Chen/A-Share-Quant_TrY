from pathlib import Path

from a_share_quant.strategy.v112r_phase_check_v1 import (
    V112RPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112r_phase_check_keeps_training_closed() -> None:
    analyzer = V112RPhaseCheckAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112r_phase_charter_v1.json")),
        validation_payload=load_json_report(Path("reports/analysis/v112r_adjacent_cohort_validation_v1.json")),
    )
    assert result.summary["allow_auto_training_now"] is False
    assert result.summary["ready_for_phase_closure_next"] is True
