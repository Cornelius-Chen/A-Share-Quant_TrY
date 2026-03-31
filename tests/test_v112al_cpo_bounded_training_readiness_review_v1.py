from pathlib import Path

from a_share_quant.strategy.v112al_cpo_bounded_training_readiness_review_v1 import (
    V112ALCPOBoundedTrainingReadinessReviewAnalyzer,
    load_json_report,
)


def test_v112al_readiness_review_attributes_bottleneck_and_scope() -> None:
    analyzer = V112ALCPOBoundedTrainingReadinessReviewAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112al_phase_charter_v1.json")),
        dataset_assembly_payload=load_json_report(
            Path("reports/analysis/v112aj_cpo_bounded_label_draft_dataset_assembly_v1.json")
        ),
        feature_binding_payload=load_json_report(
            Path("reports/analysis/v112ak_cpo_bounded_feature_binding_review_v1.json")
        ),
        feature_family_payload=load_json_report(
            Path("reports/analysis/v112af_cpo_feature_family_design_review_v1.json")
        ),
        daily_board_payload=load_json_report(
            Path("reports/analysis/v112v_cpo_daily_board_chronology_operationalization_v1.json")
        ),
        future_calendar_payload=load_json_report(
            Path("reports/analysis/v112w_cpo_future_catalyst_calendar_operationalization_v1.json")
        ),
    )
    assert result.summary["truth_candidate_row_count"] == 7
    assert result.summary["core_label_count"] == 3
    assert result.summary["guarded_label_count"] == 5
    assert result.summary["bounded_training_pilot_lawful_now"] is True
    assert result.summary["bounded_training_pilot_scope"] == "extremely_small_core_skeleton_only"
    assert result.summary["primary_bottleneck_layer"] == "feature_implementation"
    assert result.summary["secondary_bottleneck_layer"] == "row_geometry"
    assert result.summary["daily_board_operational_gap_count"] == 3
    assert result.summary["future_calendar_operational_gap_count"] == 3
    quiet_row = next(row for row in result.not_yet_trainable_rows if row["item_name"] == "quiet_window_survival_label")
    assert quiet_row["primary_blocker_layer"] == "row_geometry"
    impl_row = next(row for row in result.layer_readiness_rows if row["layer_name"] == "feature_implementation")
    assert impl_row["readiness_posture"] == "partial_with_active_operational_gaps"
