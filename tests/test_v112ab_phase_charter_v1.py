from pathlib import Path

from a_share_quant.strategy.v112ab_phase_charter_v1 import (
    V112ABPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112ab_phase_charter_opens_after_v112aa() -> None:
    analyzer = V112ABPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112aa_phase_closure_payload=load_json_report(Path("reports/analysis/v112aa_phase_closure_check_v1.json"))
    )
    assert result.summary["do_open_v112ab_now"] is True
