from pathlib import Path

from a_share_quant.strategy.v112af_cpo_feature_family_design_review_v1 import (
    V112AFCPOFeatureFamilyDesignReviewAnalyzer,
    load_json_report,
)


def test_v112af_feature_family_design_review_compresses_candidates() -> None:
    analyzer = V112AFCPOFeatureFamilyDesignReviewAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112af_phase_charter_v1.json")),
        registry_schema_payload=load_json_report(Path("reports/analysis/v112q_cpo_information_registry_schema_v1.json")),
        labeling_review_payload=load_json_report(Path("reports/analysis/v112ab_cpo_bounded_labeling_review_v1.json")),
        dynamic_role_payload=load_json_report(Path("reports/analysis/v112ad_dynamic_role_transition_feature_review_v1.json")),
        brainstorm_payload=load_json_report(Path("reports/analysis/v112ae_feature_brainstorm_integration_v1.json")),
    )
    assert result.summary["feature_family_count"] == 6
    assert result.summary["design_ready_feature_count"] == 14
    assert result.summary["overlay_only_feature_count"] == 4
    anchor_row = next(row for row in result.feature_design_rows if row["feature_name"] == "anchor_distance_state")
    assert "anchor_event_overlap_daily" in anchor_row["duplicate_guard"]
    assert anchor_row["candidate_tier"] == "design_ready_review_candidate"
