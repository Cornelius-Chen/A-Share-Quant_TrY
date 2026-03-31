from pathlib import Path

from a_share_quant.strategy.v112u_cpo_foundation_readiness_review_v1 import (
    V112UCPOFoundationReadinessReviewAnalyzer,
    load_json_report,
)


def test_v112u_readiness_review_marks_research_ready_but_not_training_ready() -> None:
    analyzer = V112UCPOFoundationReadinessReviewAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112u_phase_charter_v1.json")),
        schema_payload=load_json_report(Path("reports/analysis/v112q_cpo_information_registry_schema_v1.json")),
        adjacent_payload=load_json_report(Path("reports/analysis/v112r_adjacent_cohort_validation_v1.json")),
        chronology_payload=load_json_report(Path("reports/analysis/v112s_cpo_chronology_normalization_v1.json")),
        spillover_payload=load_json_report(Path("reports/analysis/v112t_cpo_spillover_truth_check_v1.json")),
    )
    assert result.summary["foundation_is_complete_enough_for_bounded_research"] is True
    assert result.summary["foundation_is_complete_enough_for_formal_training"] is False
    assert result.summary["remaining_material_gap_count"] == 4
