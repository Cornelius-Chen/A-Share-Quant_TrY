from pathlib import Path

from a_share_quant.strategy.v112bo_phase_check_v1 import (
    V112BOPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112bo_phase_check_accepts_overlay_review() -> None:
    analyzer = V112BOPhaseCheckAnalyzer()
    result = analyzer.analyze(
        overlay_review_payload=load_json_report(Path("reports/analysis/v112bo_cpo_internal_maturity_overlay_review_v1.json")),
    )
    assert result.summary["ready_for_phase_closure_next"] is True
