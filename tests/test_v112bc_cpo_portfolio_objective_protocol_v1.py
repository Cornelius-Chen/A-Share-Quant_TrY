from pathlib import Path

from a_share_quant.strategy.v112bc_cpo_portfolio_objective_protocol_v1 import (
    V112BCCPOPortfolioObjectiveProtocolAnalyzer,
    load_json_report,
)


def test_v112bc_protocol_freezes_tracks_and_stop_rule() -> None:
    analyzer = V112BCCPOPortfolioObjectiveProtocolAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112bc_phase_charter_v1.json")),
        v112bb_pilot_payload=load_json_report(Path("reports/analysis/v112bb_cpo_default_10_row_guarded_layer_pilot_v1.json")),
        v112z_operational_charter_payload=load_json_report(Path("reports/analysis/v112z_operational_charter_v1.json")),
    )
    assert result.summary["objective_track_count"] == 3
    assert result.summary["marginal_stop_threshold"] == 0.005
