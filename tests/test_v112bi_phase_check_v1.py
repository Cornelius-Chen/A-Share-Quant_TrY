from pathlib import Path

from a_share_quant.strategy.v112bi_phase_check_v1 import (
    V112BIPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112bi_phase_check_accepts_ranker_pilot() -> None:
    analyzer = V112BIPhaseCheckAnalyzer()
    result = analyzer.analyze(
        ranker_pilot_payload=load_json_report(Path("reports/analysis/v112bi_cpo_cross_sectional_ranker_pilot_v1.json")),
    )
    assert result.summary["ready_for_phase_closure_next"] is True
