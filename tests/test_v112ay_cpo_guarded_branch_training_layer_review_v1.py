from pathlib import Path

from a_share_quant.strategy.v112ay_cpo_guarded_branch_training_layer_review_v1 import (
    V112AYCPOGuardedBranchTrainingLayerReviewAnalyzer,
    load_json_report,
)


def test_v112ay_branch_training_layer_review_preserves_partial_split() -> None:
    analyzer = V112AYCPOGuardedBranchTrainingLayerReviewAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112ay_phase_charter_v1.json")),
        branch_admission_payload=load_json_report(Path("reports/analysis/v112aw_cpo_branch_guarded_admission_review_v1.json")),
        guarded_branch_pilot_payload=load_json_report(Path("reports/analysis/v112ax_cpo_guarded_branch_admitted_pilot_v1.json")),
    )
    assert result.summary["guarded_training_layer_admissible_count"] == 3
    assert result.summary["branch_rows_retained_review_only_count"] == 1
