from pathlib import Path

from a_share_quant.strategy.v112aw_cpo_branch_guarded_admission_review_v1 import (
    V112AWCPOBranchGuardedAdmissionReviewAnalyzer,
    load_json_report,
)


def test_v112aw_branch_admission_is_partial_and_guarded() -> None:
    analyzer = V112AWCPOBranchGuardedAdmissionReviewAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112aw_phase_charter_v1.json")),
        widen_payload=load_json_report(Path("reports/analysis/v112au_cpo_bounded_row_geometry_widen_pilot_v1.json")),
        branch_patch_payload=load_json_report(Path("reports/analysis/v112av_cpo_branch_role_geometry_patch_pilot_v1.json")),
        dataset_assembly_payload=load_json_report(Path("reports/analysis/v112aj_cpo_bounded_label_draft_dataset_assembly_v1.json")),
    )
    assert result.summary["guarded_training_context_admissible_count"] == 3
    assert result.summary["retained_review_only_count"] == 1
