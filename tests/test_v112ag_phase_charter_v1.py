from pathlib import Path

from a_share_quant.strategy.v112ag_phase_charter_v1 import (
    V112AGPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112ag_phase_charter_opens_label_draft_assembly() -> None:
    analyzer = V112AGPhaseCharterAnalyzer()
    result = analyzer.analyze(
        cohort_map_payload=load_json_report(Path("reports/analysis/v112aa_cpo_bounded_cohort_map_v1.json")),
        labeling_review_payload=load_json_report(Path("reports/analysis/v112ab_cpo_bounded_labeling_review_v1.json")),
        dynamic_role_payload=load_json_report(Path("reports/analysis/v112ad_dynamic_role_transition_feature_review_v1.json")),
        feature_family_payload=load_json_report(Path("reports/analysis/v112af_cpo_feature_family_design_review_v1.json")),
    )
    assert result.summary["do_open_v112ag_now"] is True
    assert result.summary["recommended_first_action"] == "freeze_v112ag_cpo_bounded_label_draft_assembly_v1"
