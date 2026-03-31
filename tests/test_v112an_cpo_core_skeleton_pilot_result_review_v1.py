from pathlib import Path

from a_share_quant.strategy.v112an_cpo_core_skeleton_pilot_result_review_v1 import (
    V112ANCPOCoreSkeletonPilotResultReviewAnalyzer,
    load_json_report,
)


def test_v112an_result_review_explains_pilot_layers() -> None:
    analyzer = V112ANCPOCoreSkeletonPilotResultReviewAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112an_phase_charter_v1.json")),
        training_pilot_payload=load_json_report(
            Path("reports/analysis/v112am_cpo_extremely_small_core_skeleton_training_pilot_v1.json")
        ),
        dataset_assembly_payload=load_json_report(
            Path("reports/analysis/v112aj_cpo_bounded_label_draft_dataset_assembly_v1.json")
        ),
        cycle_reconstruction_payload=load_json_report(
            Path("reports/analysis/v112z_bounded_cycle_reconstruction_pass_v1.json")
        ),
    )
    assert result.summary["family_ablation_count"] == 12
    assert result.summary["best_family_for_phase"] in {
        "chronology_price_geometry_family",
        "catalyst_presence_family",
    }
    assert result.summary["best_family_for_role_state"] == "role_prior_family"
    assert result.summary["formal_training_still_forbidden"] is True
    assert result.summary["correction_bucket_count"] > 0
    assert result.role_confusion_rows
