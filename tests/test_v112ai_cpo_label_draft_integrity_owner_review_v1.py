from pathlib import Path

from a_share_quant.strategy.v112ai_cpo_label_draft_integrity_owner_review_v1 import (
    V112AICPOLabelDraftIntegrityOwnerReviewAnalyzer,
    load_json_report,
)


def test_v112ai_owner_review_tiers_labels_without_dropping() -> None:
    analyzer = V112AICPOLabelDraftIntegrityOwnerReviewAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112ai_phase_charter_v1.json")),
        label_draft_payload=load_json_report(Path("reports/analysis/v112ag_cpo_bounded_label_draft_assembly_v1.json")),
        preservation_rule_payload=load_json_report(Path("reports/analysis/v112ah_factor_candidate_preservation_rule_v1.json")),
    )
    assert result.summary["reviewed_label_count"] == 10
    assert result.summary["draft_ready_label_count"] == 3
    assert result.summary["guarded_draft_label_count"] == 5
    assert result.summary["review_only_future_target_count"] == 1
    assert result.summary["confirmed_only_review_label_count"] == 1
    assert result.summary["dropped_label_count"] == 0
    branch_row = next(row for row in result.review_rows if row["label_name"] == "branch_upgrade_label")
    assert branch_row["owner_disposition"] == "preserve_as_review_only_future_target"
