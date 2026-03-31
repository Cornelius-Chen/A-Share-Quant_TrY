from pathlib import Path

from a_share_quant.strategy.v112bk_phase_charter_v1 import (
    V112BKPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112bk_phase_charter_opens_after_bi_and_bj() -> None:
    analyzer = V112BKPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112bi_phase_closure_payload=load_json_report(Path("reports/analysis/v112bi_phase_closure_check_v1.json")),
        v112bj_phase_closure_payload=load_json_report(Path("reports/analysis/v112bj_phase_closure_check_v1.json")),
    )
    assert result.summary["do_open_v112bk_now"] is True
