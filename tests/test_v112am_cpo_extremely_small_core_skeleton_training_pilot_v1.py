from pathlib import Path

from a_share_quant.strategy.v112am_cpo_extremely_small_core_skeleton_training_pilot_v1 import (
    V112AMCPOExtremelySmallCoreSkeletonTrainingPilotAnalyzer,
    load_json_report,
)


def test_v112am_training_pilot_runs_on_core_skeleton_only() -> None:
    analyzer = V112AMCPOExtremelySmallCoreSkeletonTrainingPilotAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112am_phase_charter_v1.json")),
        readiness_review_payload=load_json_report(
            Path("reports/analysis/v112al_cpo_bounded_training_readiness_review_v1.json")
        ),
        dataset_assembly_payload=load_json_report(
            Path("reports/analysis/v112aj_cpo_bounded_label_draft_dataset_assembly_v1.json")
        ),
        cycle_reconstruction_payload=load_json_report(
            Path("reports/analysis/v112z_bounded_cycle_reconstruction_pass_v1.json")
        ),
    )
    assert result.summary["truth_candidate_row_count"] == 7
    assert result.summary["target_count"] == 3
    assert result.summary["model_count"] == 6
    assert result.summary["formal_training_still_forbidden"] is True
    assert result.summary["bounded_training_pilot_scope"] == "extremely_small_core_skeleton_only"
    assert result.summary["sample_count"] >= 40
    assert {row["target_name"] for row in result.target_rows} == {
        "phase_progression_label",
        "role_state_label",
        "catalyst_sequence_label",
    }
