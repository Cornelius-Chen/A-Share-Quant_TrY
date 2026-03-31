from pathlib import Path

from a_share_quant.strategy.v112bq_phase_check_v1 import (
    V112BQPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112bq_phase_check_accepts_completed_sweep() -> None:
    analyzer = V112BQPhaseCheckAnalyzer()
    result = analyzer.analyze(
        gate_precision_payload=load_json_report(Path("reports/analysis/v112bq_cpo_gate_precision_sweep_v1.json")),
    )
    assert result.summary["ready_for_phase_closure_next"] is True

