from pathlib import Path

from a_share_quant.strategy.v112br_phase_charter_v1 import (
    V112BRPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112br_phase_charter_opens_from_prerequisites() -> None:
    analyzer = V112BRPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112bq_phase_closure_payload=load_json_report(Path("reports/analysis/v112bq_phase_closure_check_v1.json")),
        v112bp_phase_closure_payload=load_json_report(Path("reports/analysis/v112bp_phase_closure_check_v1.json")),
        v112bo_phase_closure_payload=load_json_report(Path("reports/analysis/v112bo_phase_closure_check_v1.json")),
    )
    assert result.summary["do_open_v112br_now"] is True
