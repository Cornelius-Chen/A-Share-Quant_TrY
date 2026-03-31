from pathlib import Path

from a_share_quant.strategy.v112x_phase_check_v1 import (
    V112XPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112x_phase_check_keeps_training_closed() -> None:
    analyzer = V112XPhaseCheckAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112x_phase_charter_v1.json")),
        factor_review_payload=load_json_report(Path("reports/analysis/v112x_cpo_spillover_factor_candidacy_review_v1.json")),
    )
    assert result.summary["allow_auto_training_now"] is False
    assert result.summary["ready_for_phase_closure_next"] is True
