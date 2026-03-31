from pathlib import Path

from a_share_quant.strategy.v112aw_phase_charter_v1 import (
    V112AWPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112aw_phase_charter_opens_after_v112av() -> None:
    analyzer = V112AWPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112av_phase_closure_payload=load_json_report(Path("reports/analysis/v112av_phase_closure_check_v1.json")),
    )
    assert result.summary["do_open_v112aw_now"] is True
