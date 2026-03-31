from pathlib import Path

from a_share_quant.strategy.v112z_operational_charter_v1 import (
    V112ZOperationalCharterAnalyzer,
    load_json_report,
)


def test_v112z_operational_charter_freezes_dual_track_goal() -> None:
    analyzer = V112ZOperationalCharterAnalyzer()
    result = analyzer.analyze(
        protocol_payload=load_json_report(Path("reports/analysis/v112z_cycle_reconstruction_protocol_v1.json")),
        training_protocol_payload=load_json_report(Path("reports/analysis/v112_training_protocol_v1.json")),
        sidecar_v1_payload=load_json_report(Path("reports/analysis/v112d_sidecar_pilot_v1.json")),
        gbdt_v2_payload=load_json_report(Path("reports/analysis/v112g_gbdt_pilot_v2.json")),
    )
    assert result.summary["cycle_absorption_is_primary_objective"] is True
    assert result.summary["black_box_primary_family"] == "hist_gradient_boosting_classifier"
    assert result.summary["owner_facing_narrative_required"] is True
    assert result.summary["formal_training_still_forbidden"] is True
