from pathlib import Path

from a_share_quant.strategy.v112av_phase_charter_v1 import (
    V112AVPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112av_phase_charter_opens_after_v112au() -> None:
    analyzer = V112AVPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112au_phase_closure_payload=load_json_report(Path("reports/analysis/v112au_phase_closure_check_v1.json")),
    )
    assert result.summary["do_open_v112av_now"] is True
