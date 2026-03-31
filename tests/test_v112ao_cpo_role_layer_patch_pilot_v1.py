from pathlib import Path

from a_share_quant.strategy.v112ao_cpo_role_layer_patch_pilot_v1 import (
    V112AOCPORoleLayerPatchPilotAnalyzer,
)
from a_share_quant.strategy.v112ao_phase_charter_v1 import load_json_report


def test_v112ao_role_patch_improves_or_preserves_role_layer() -> None:
    analyzer = V112AOCPORoleLayerPatchPilotAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112ao_phase_charter_v1.json")),
        prior_training_pilot_payload=load_json_report(
            Path("reports/analysis/v112am_cpo_extremely_small_core_skeleton_training_pilot_v1.json")
        ),
        prior_result_review_payload=load_json_report(
            Path("reports/analysis/v112an_cpo_core_skeleton_pilot_result_review_v1.json")
        ),
        dataset_assembly_payload=load_json_report(
            Path("reports/analysis/v112aj_cpo_bounded_label_draft_dataset_assembly_v1.json")
        ),
        cycle_reconstruction_payload=load_json_report(
            Path("reports/analysis/v112z_bounded_cycle_reconstruction_pass_v1.json")
        ),
    )
    assert result.summary["patch_feature_count"] == 8
    assert result.summary["formal_training_still_forbidden"] is True
    assert result.summary["role_state_gbdt_accuracy_after_patch"] >= result.summary["role_state_gbdt_accuracy_before_patch"]
    assert result.role_patch_family_rows
