from pathlib import Path

from a_share_quant.strategy.v112ap_cpo_bounded_secondary_widen_pilot_v1 import (
    V112APCPOBoundedSecondaryWidenPilotAnalyzer,
)
from a_share_quant.strategy.v112ap_phase_charter_v1 import load_json_report


def test_v112ap_secondary_widen_keeps_core_and_learns_guarded() -> None:
    analyzer = V112APCPOBoundedSecondaryWidenPilotAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112ap_phase_charter_v1.json")),
        role_patch_payload=load_json_report(Path("reports/analysis/v112ao_cpo_role_layer_patch_pilot_v1.json")),
        dataset_assembly_payload=load_json_report(
            Path("reports/analysis/v112aj_cpo_bounded_label_draft_dataset_assembly_v1.json")
        ),
        binding_review_payload=load_json_report(
            Path("reports/analysis/v112ak_cpo_bounded_feature_binding_review_v1.json")
        ),
        cycle_reconstruction_payload=load_json_report(
            Path("reports/analysis/v112z_bounded_cycle_reconstruction_pass_v1.json")
        ),
    )
    assert result.summary["core_target_count"] == 3
    assert result.summary["guarded_target_count"] == 3
    assert result.summary["formal_training_still_forbidden"] is True
    assert result.summary["guarded_targets_learnable_count"] >= 1
