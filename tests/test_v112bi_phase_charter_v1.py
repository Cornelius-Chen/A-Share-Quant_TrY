from pathlib import Path

from a_share_quant.strategy.v112bi_phase_charter_v1 import (
    V112BIPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112bi_phase_charter_opens_after_bh_and_bc() -> None:
    analyzer = V112BIPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112bh_phase_closure_payload=load_json_report(Path("reports/analysis/v112bh_phase_closure_check_v1.json")),
        v112bc_phase_closure_payload=load_json_report(Path("reports/analysis/v112bc_phase_closure_check_v1.json")),
    )
    assert result.summary["do_open_v112bi_now"] is True
