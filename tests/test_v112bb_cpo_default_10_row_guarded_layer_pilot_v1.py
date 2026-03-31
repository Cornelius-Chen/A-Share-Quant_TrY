from pathlib import Path

from a_share_quant.strategy.v112bb_cpo_default_10_row_guarded_layer_pilot_v1 import (
    V112BBCPODefault10RowGuardedLayerPilotAnalyzer,
    load_json_report,
)


def test_v112bb_establishes_default_10_row_pilot() -> None:
    analyzer = V112BBCPODefault10RowGuardedLayerPilotAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112bb_phase_charter_v1.json")),
        training_layer_extension_payload=load_json_report(Path("reports/analysis/v112az_cpo_bounded_training_layer_extension_v1.json")),
        cycle_reconstruction_payload=load_json_report(Path("reports/analysis/v112z_bounded_cycle_reconstruction_pass_v1.json")),
        v112am_pilot_payload=load_json_report(Path("reports/analysis/v112am_cpo_extremely_small_core_skeleton_training_pilot_v1.json")),
        v112ap_pilot_payload=load_json_report(Path("reports/analysis/v112ap_cpo_bounded_secondary_widen_pilot_v1.json")),
        v112ax_pilot_payload=load_json_report(Path("reports/analysis/v112ax_cpo_guarded_branch_admitted_pilot_v1.json")),
    )
    assert result.summary["default_10_row_pilot_established"] is True
    assert result.summary["core_targets_stable_vs_7_row_baseline"] is True
    assert result.summary["guarded_targets_stable_vs_7_row_guarded_baseline"] is True
