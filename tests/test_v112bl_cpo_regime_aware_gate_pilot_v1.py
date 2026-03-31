from pathlib import Path

from a_share_quant.strategy.v112bl_cpo_regime_aware_gate_pilot_v1 import (
    V112BLCpoRegimeAwareGatePilotAnalyzer,
    load_json_report,
)


def test_v112bl_regime_aware_gate_pilot_produces_report_only_trace() -> None:
    analyzer = V112BLCpoRegimeAwareGatePilotAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112bl_phase_charter_v1.json")),
        oracle_benchmark_payload=load_json_report(Path("reports/analysis/v112be_cpo_oracle_upper_bound_benchmark_v1.json")),
        aggressive_pilot_payload=load_json_report(Path("reports/analysis/v112bf_cpo_aggressive_no_leak_black_box_portfolio_pilot_v1.json")),
        neutral_pilot_payload=load_json_report(Path("reports/analysis/v112bh_cpo_neutral_selective_no_leak_portfolio_pilot_v1.json")),
        ranker_pilot_payload=load_json_report(Path("reports/analysis/v112bi_cpo_cross_sectional_ranker_pilot_v1.json")),
        v112bc_protocol_payload=load_json_report(Path("reports/analysis/v112bc_cpo_portfolio_objective_protocol_v1.json")),
        v112bg_gap_review_payload=load_json_report(Path("reports/analysis/v112bg_cpo_oracle_vs_no_leak_gap_review_v1.json")),
        market_regime_overlay_payload=load_json_report(Path("reports/analysis/v112bd_market_regime_overlay_feature_review_v1.json")),
        training_layer_payload=load_json_report(Path("reports/analysis/v112az_cpo_bounded_training_layer_extension_v1.json")),
        cycle_reconstruction_payload=load_json_report(Path("reports/analysis/v112z_bounded_cycle_reconstruction_pass_v1.json")),
    )
    assert result.summary["no_leak_enforced"] is True
    assert result.summary["teacher_decision_row_count"] > 0
    assert len(result.comparison_rows) >= 4
