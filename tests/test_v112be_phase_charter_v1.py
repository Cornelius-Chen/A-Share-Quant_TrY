from pathlib import Path

from a_share_quant.strategy.v112be_phase_charter_v1 import (
    V112BEPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112be_phase_charter_opens_oracle_benchmark() -> None:
    analyzer = V112BEPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112bc_phase_closure_payload=load_json_report(Path("reports/analysis/v112bc_phase_closure_check_v1.json")),
        v112bd_phase_closure_payload=load_json_report(Path("reports/analysis/v112bd_phase_closure_check_v1.json")),
        v112bb_phase_closure_payload=load_json_report(Path("reports/analysis/v112bb_phase_closure_check_v1.json")),
    )
    assert result.summary["do_open_v112be_now"] is True
