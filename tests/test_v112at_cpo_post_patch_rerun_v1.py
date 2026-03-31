from pathlib import Path

from a_share_quant.strategy.v112at_cpo_post_patch_rerun_v1 import (
    V112ATCPOPostPatchRerunAnalyzer,
    load_json_report,
)


def test_v112at_post_patch_rerun_keeps_current_rows_stable() -> None:
    analyzer = V112ATCPOPostPatchRerunAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112at_phase_charter_v1.json")),
        widen_pilot_payload=load_json_report(Path("reports/analysis/v112ap_cpo_bounded_secondary_widen_pilot_v1.json")),
        dataset_assembly_payload=load_json_report(Path("reports/analysis/v112aj_cpo_bounded_label_draft_dataset_assembly_v1.json")),
        cycle_reconstruction_payload=load_json_report(Path("reports/analysis/v112z_bounded_cycle_reconstruction_pass_v1.json")),
    )
    assert result.summary["core_targets_stable_after_post_patch_rerun"] is True
    assert result.summary["guarded_targets_stable_after_post_patch_rerun"] is True
    assert result.summary["allow_row_geometry_widen_now"] is True
