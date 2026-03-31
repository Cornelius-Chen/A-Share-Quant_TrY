from pathlib import Path

from a_share_quant.strategy.v112bt_phase_check_v1 import (
    V112BTPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112bt_phase_check_runs() -> None:
    analyzer = V112BTPhaseCheckAnalyzer()
    result = analyzer.analyze(
        extraction_payload=load_json_report(Path("reports/analysis/v112bt_phase_conditioned_veto_and_eligibility_extraction_v1.json")),
    )
    assert result.summary["ready_for_phase_closure_next"] is True
