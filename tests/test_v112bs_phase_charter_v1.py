from pathlib import Path

from a_share_quant.strategy.v112bs_phase_charter_v1 import (
    V112BSPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112bs_phase_charter_opens() -> None:
    analyzer = V112BSPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112br_phase_closure_payload=load_json_report(Path("reports/analysis/v112br_phase_closure_check_v1.json")),
        v112bq_phase_closure_payload=load_json_report(Path("reports/analysis/v112bq_phase_closure_check_v1.json")),
    )
    assert result.summary["do_open_v112bs_now"] is True
