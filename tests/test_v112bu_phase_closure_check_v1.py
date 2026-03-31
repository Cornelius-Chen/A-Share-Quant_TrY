from pathlib import Path

from a_share_quant.strategy.v112bu_phase_closure_check_v1 import (
    V112BUPhaseClosureCheckAnalyzer,
    load_json_report,
)


def test_v112bu_phase_closure_runs() -> None:
    analyzer = V112BUPhaseClosureCheckAnalyzer()
    result = analyzer.analyze(
        phase_check_payload=load_json_report(Path("reports/analysis/v112bu_phase_check_v1.json")),
    )
    assert result.summary["v112bu_success_criteria_met"] is True
