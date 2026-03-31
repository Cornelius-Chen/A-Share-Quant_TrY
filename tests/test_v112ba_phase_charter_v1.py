from pathlib import Path

from a_share_quant.strategy.v112ba_phase_charter_v1 import (
    V112BAPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112ba_phase_charter_opens_after_v112az() -> None:
    analyzer = V112BAPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112az_phase_closure_payload=load_json_report(Path("reports/analysis/v112az_phase_closure_check_v1.json")),
    )
    assert result.summary["do_open_v112ba_now"] is True
