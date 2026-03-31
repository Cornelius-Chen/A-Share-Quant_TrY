from pathlib import Path

from a_share_quant.strategy.v112au_cpo_bounded_row_geometry_widen_pilot_v1 import (
    V112AUCPOBoundedRowGeometryWidenPilotAnalyzer,
    load_json_report,
)


def test_v112au_row_geometry_widen_keeps_stack_stable() -> None:
    analyzer = V112AUCPOBoundedRowGeometryWidenPilotAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112au_phase_charter_v1.json")),
        post_patch_rerun_payload=load_json_report(Path("reports/analysis/v112at_cpo_post_patch_rerun_v1.json")),
        dataset_assembly_payload=load_json_report(Path("reports/analysis/v112aj_cpo_bounded_label_draft_dataset_assembly_v1.json")),
        cycle_reconstruction_payload=load_json_report(Path("reports/analysis/v112z_bounded_cycle_reconstruction_pass_v1.json")),
    )
    assert result.summary["row_count_after_widen"] == 11
    assert result.summary["added_branch_row_count"] == 4
    assert result.summary["core_targets_stable_after_row_widen"] is False
    assert result.summary["guarded_targets_stable_after_row_widen"] is True
