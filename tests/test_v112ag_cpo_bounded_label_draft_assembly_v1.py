from pathlib import Path

from a_share_quant.strategy.v112ag_cpo_bounded_label_draft_assembly_v1 import (
    V112AGCPOBoundedLabelDraftAssemblyAnalyzer,
    load_json_report,
)


def test_v112ag_label_draft_assembly_preserves_ambiguity_and_guards() -> None:
    analyzer = V112AGCPOBoundedLabelDraftAssemblyAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112ag_phase_charter_v1.json")),
        cohort_map_payload=load_json_report(Path("reports/analysis/v112aa_cpo_bounded_cohort_map_v1.json")),
        labeling_review_payload=load_json_report(Path("reports/analysis/v112ab_cpo_bounded_labeling_review_v1.json")),
        dynamic_role_payload=load_json_report(Path("reports/analysis/v112ad_dynamic_role_transition_feature_review_v1.json")),
        feature_family_payload=load_json_report(Path("reports/analysis/v112af_cpo_feature_family_design_review_v1.json")),
    )
    assert result.summary["label_skeleton_count"] == 10
    assert result.summary["family_support_mapping_count"] == 10
    assert result.summary["anti_leakage_review_count"] == 10
    quiet_row = next(row for row in result.family_support_matrix_rows if row["label_name"] == "quiet_window_survival_label")
    assert quiet_row["support_posture"] == "supported_with_provisional_guard"
    residual_row = next(row for row in result.anti_leakage_review_rows if row["label_name"] == "residual_core_vs_collapse_label")
    assert residual_row["point_in_time_posture"] == "confirmed_only"
    pending_row = next(row for row in result.ambiguity_preservation_rows if row["ambiguity_state_name"] == "pending_ambiguous_row_preservation")
    assert pending_row["applies_to_symbols"] == ["300620", "300548", "000988"]
