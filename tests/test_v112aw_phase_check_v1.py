from pathlib import Path

from a_share_quant.strategy.v112aw_phase_check_v1 import (
    V112AWPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112aw_phase_check_keeps_formal_training_closed() -> None:
    analyzer = V112AWPhaseCheckAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112aw_phase_charter_v1.json")),
        admission_review_payload=load_json_report(Path("reports/analysis/v112aw_cpo_branch_guarded_admission_review_v1.json")),
    )
    assert result.summary["formal_training_now"] is False
