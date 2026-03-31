from pathlib import Path

from a_share_quant.strategy.v112av_cpo_branch_role_geometry_patch_pilot_v1 import (
    V112AVCPOBranchRoleGeometryPatchPilotAnalyzer,
    load_json_report,
)


def test_v112av_branch_patch_improves_role_state() -> None:
    analyzer = V112AVCPOBranchRoleGeometryPatchPilotAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112av_phase_charter_v1.json")),
        widen_pilot_payload=load_json_report(Path("reports/analysis/v112au_cpo_bounded_row_geometry_widen_pilot_v1.json")),
        dataset_assembly_payload=load_json_report(Path("reports/analysis/v112aj_cpo_bounded_label_draft_dataset_assembly_v1.json")),
        cycle_reconstruction_payload=load_json_report(Path("reports/analysis/v112z_bounded_cycle_reconstruction_pass_v1.json")),
    )
    assert result.summary["role_state_patch_gain"] >= 0.0
    assert result.summary["guarded_targets_stable_after_branch_patch"] is True
