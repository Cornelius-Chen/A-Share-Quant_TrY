from pathlib import Path

from a_share_quant.strategy.v112be_phase_check_v1 import (
    V112BEPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112be_phase_check_accepts_oracle_trace() -> None:
    analyzer = V112BEPhaseCheckAnalyzer()
    result = analyzer.analyze(
        oracle_benchmark_payload=load_json_report(Path("reports/analysis/v112be_cpo_oracle_upper_bound_benchmark_v1.json")),
    )
    assert result.summary["ready_for_phase_closure_next"] is True
