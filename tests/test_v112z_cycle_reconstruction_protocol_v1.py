from pathlib import Path

from a_share_quant.strategy.v112z_cycle_reconstruction_protocol_v1 import (
    V112ZCycleReconstructionProtocolAnalyzer,
    load_json_report,
)


def test_v112z_protocol_freezes_reconstruction_entry() -> None:
    analyzer = V112ZCycleReconstructionProtocolAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112z_phase_charter_v1.json")),
        readiness_payload=load_json_report(Path("reports/analysis/v112u_cpo_foundation_readiness_review_v1.json")),
        adjacent_probe_payload=load_json_report(Path("reports/analysis/v112y_cpo_adjacent_role_split_sidecar_probe_v1.json")),
        spillover_probe_payload=load_json_report(Path("reports/analysis/v112x_cpo_spillover_factor_candidacy_review_v1.json")),
    )
    assert result.summary["foundation_ready_for_bounded_cycle_reconstruction"] is True
    assert result.summary["split_ready_adjacent_asset_count"] == 6
    assert result.summary["bounded_spillover_factor_candidate_count"] == 2
