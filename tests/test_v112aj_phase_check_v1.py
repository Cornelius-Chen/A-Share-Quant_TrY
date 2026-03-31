from pathlib import Path

from a_share_quant.strategy.v112aj_phase_check_v1 import (
    V112AJPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112aj_phase_check_keeps_training_closed() -> None:
    analyzer = V112AJPhaseCheckAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112aj_phase_charter_v1.json")),
        dataset_assembly_payload=load_json_report(Path("reports/analysis/v112aj_cpo_bounded_label_draft_dataset_assembly_v1.json")),
    )
    assert result.summary["allow_auto_training_now"] is False
    assert result.summary["recommended_next_posture"] == "bounded_feature_binding_review_before_any_training_readiness_claim"
