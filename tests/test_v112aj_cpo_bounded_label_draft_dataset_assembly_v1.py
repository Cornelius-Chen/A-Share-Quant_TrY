from pathlib import Path

from a_share_quant.strategy.v112aj_cpo_bounded_label_draft_dataset_assembly_v1 import (
    V112AJCPOBoundedLabelDraftDatasetAssemblyAnalyzer,
    load_json_report,
)


def test_v112aj_dataset_assembly_preserves_truth_vs_context_split() -> None:
    analyzer = V112AJCPOBoundedLabelDraftDatasetAssemblyAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112aj_phase_charter_v1.json")),
        cohort_map_payload=load_json_report(Path("reports/analysis/v112aa_cpo_bounded_cohort_map_v1.json")),
        labeling_review_payload=load_json_report(Path("reports/analysis/v112ab_cpo_bounded_labeling_review_v1.json")),
        owner_review_payload=load_json_report(Path("reports/analysis/v112ai_cpo_label_draft_integrity_owner_review_v1.json")),
    )
    assert result.summary["dataset_row_count"] == 20
    assert result.summary["truth_candidate_row_count"] == 7
    assert result.summary["context_only_row_count"] == 13
    assert result.summary["ready_label_count"] == 3
    assert result.summary["guarded_label_count"] == 5
    row_300308 = next(row for row in result.dataset_draft_rows if row["symbol"] == "300308")
    assert row_300308["include_in_truth_candidate_rows"] is True
    row_000070 = next(row for row in result.dataset_draft_rows if row["symbol"] == "000070")
    assert row_000070["include_in_truth_candidate_rows"] is False
    bundle = next(row for row in result.label_bundle_rows if row["label_name"] == "branch_upgrade_label")
    assert bundle["dataset_bundle_posture"] == "exclude_from_truth_candidate_bundle"
