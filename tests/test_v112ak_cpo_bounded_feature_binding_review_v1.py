from pathlib import Path

from a_share_quant.strategy.v112ak_cpo_bounded_feature_binding_review_v1 import (
    V112AKCPOBoundedFeatureBindingReviewAnalyzer,
    load_json_report,
)


def test_v112ak_feature_binding_review_surfaces_row_level_blockers() -> None:
    analyzer = V112AKCPOBoundedFeatureBindingReviewAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112ak_phase_charter_v1.json")),
        dataset_assembly_payload=load_json_report(Path("reports/analysis/v112aj_cpo_bounded_label_draft_dataset_assembly_v1.json")),
        label_draft_payload=load_json_report(Path("reports/analysis/v112ag_cpo_bounded_label_draft_assembly_v1.json")),
    )
    assert result.summary["truth_candidate_row_count"] == 7
    assert result.summary["evaluated_binding_count"] == 56
    assert result.summary["direct_bindable_count"] == 21
    assert result.summary["guarded_bindable_count"] == 17
    assert result.summary["row_specific_blocked_count"] == 18
    quiet_row = next(
        row for row in result.binding_rows if row["symbol"] == "300308" and row["label_name"] == "quiet_window_survival_label"
    )
    assert quiet_row["binding_posture"] == "row_specific_not_currently_bindable"
    spill_row = next(
        row for row in result.binding_rows if row["symbol"] == "603083" and row["label_name"] == "spillover_maturity_boundary_label"
    )
    assert spill_row["binding_posture"] == "row_specific_not_currently_bindable"
