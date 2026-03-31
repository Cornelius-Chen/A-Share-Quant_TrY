from pathlib import Path

from a_share_quant.strategy.v112ad_dynamic_role_transition_feature_review_v1 import (
    V112ADDynamicRoleTransitionFeatureReviewAnalyzer,
    load_json_report,
)


def test_v112ad_feature_review_keeps_dynamic_roles_review_only() -> None:
    analyzer = V112ADDynamicRoleTransitionFeatureReviewAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112ad_phase_charter_v1.json")),
        reconstruction_payload=load_json_report(Path("reports/analysis/v112z_bounded_cycle_reconstruction_pass_v1.json")),
        cohort_map_payload=load_json_report(Path("reports/analysis/v112aa_cpo_bounded_cohort_map_v1.json")),
        unsupervised_probe_payload=load_json_report(Path("reports/analysis/v112ac_unsupervised_role_challenge_probe_v1.json")),
    )
    assert result.summary["transition_event_count"] == 7
    assert result.summary["dynamic_feature_count"] == 10
    assert result.summary["formal_training_still_forbidden"] is True
