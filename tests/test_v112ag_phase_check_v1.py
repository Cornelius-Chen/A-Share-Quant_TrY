from pathlib import Path

from a_share_quant.strategy.v112ag_phase_check_v1 import (
    V112AGPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112ag_phase_check_keeps_training_closed() -> None:
    analyzer = V112AGPhaseCheckAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112ag_phase_charter_v1.json")),
        label_draft_payload=load_json_report(Path("reports/analysis/v112ag_cpo_bounded_label_draft_assembly_v1.json")),
    )
    assert result.summary["allow_auto_label_freeze_now"] is False
    assert result.summary["allow_auto_training_now"] is False
    assert result.summary["recommended_next_posture"] == "owner_review_of_bounded_label_draft_integrity"
