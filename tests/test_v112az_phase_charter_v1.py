from pathlib import Path

from a_share_quant.strategy.v112az_phase_charter_v1 import (
    V112AZPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112az_phase_charter_opens_after_v112ay() -> None:
    analyzer = V112AZPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112ay_phase_closure_payload=load_json_report(Path("reports/analysis/v112ay_phase_closure_check_v1.json")),
    )
    assert result.summary["do_open_v112az_now"] is True
