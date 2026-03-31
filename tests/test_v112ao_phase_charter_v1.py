from pathlib import Path

from a_share_quant.strategy.v112ao_phase_charter_v1 import (
    V112AOPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112ao_phase_charter_opens_after_v112an() -> None:
    analyzer = V112AOPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112an_phase_closure_payload=load_json_report(Path("reports/analysis/v112an_phase_closure_check_v1.json")),
    )
    assert result.summary["do_open_v112ao_now"] is True
    assert "role-state separation" in result.charter["mission"]
