from pathlib import Path

from a_share_quant.strategy.v112af_phase_charter_v1 import (
    V112AFPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112af_phase_charter_opens_on_frozen_inputs() -> None:
    analyzer = V112AFPhaseCharterAnalyzer()
    result = analyzer.analyze(
        registry_schema_payload=load_json_report(Path("reports/analysis/v112q_cpo_information_registry_schema_v1.json")),
        labeling_review_payload=load_json_report(Path("reports/analysis/v112ab_cpo_bounded_labeling_review_v1.json")),
        dynamic_role_payload=load_json_report(Path("reports/analysis/v112ad_dynamic_role_transition_feature_review_v1.json")),
        brainstorm_payload=load_json_report(Path("reports/analysis/v112ae_feature_brainstorm_integration_v1.json")),
    )
    assert result.summary["do_open_v112af_now"] is True
