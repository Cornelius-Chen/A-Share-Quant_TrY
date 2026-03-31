from pathlib import Path

from a_share_quant.strategy.v112s_phase_charter_v1 import (
    V112SPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112s_phase_charter_opens_after_v112r() -> None:
    analyzer = V112SPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112r_phase_closure_payload=load_json_report(Path("reports/analysis/v112r_phase_closure_check_v1.json"))
    )
    assert result.summary["do_open_v112s_now"] is True
