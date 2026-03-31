from pathlib import Path

from a_share_quant.strategy.v112ai_phase_check_v1 import (
    V112AIPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112ai_phase_check_keeps_training_closed() -> None:
    analyzer = V112AIPhaseCheckAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112ai_phase_charter_v1.json")),
        owner_review_payload=load_json_report(Path("reports/analysis/v112ai_cpo_label_draft_integrity_owner_review_v1.json")),
    )
    assert result.summary["allow_auto_training_now"] is False
    assert result.summary["recommended_next_posture"] == "bounded_label_draft_dataset_assembly_with_ready_and_guarded_labels_only"
