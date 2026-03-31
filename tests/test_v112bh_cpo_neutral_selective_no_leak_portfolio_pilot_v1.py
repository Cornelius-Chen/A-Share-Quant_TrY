from pathlib import Path

from a_share_quant.strategy.v112bh_cpo_neutral_selective_no_leak_portfolio_pilot_v1 import (
    V112BHCpoNeutralSelectiveNoLeakPortfolioPilotAnalyzer,
    load_json_report,
)


def test_v112bh_neutral_pilot_produces_cash_selective_trace() -> None:
    analyzer = V112BHCpoNeutralSelectiveNoLeakPortfolioPilotAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112bh_phase_charter_v1.json")),
        oracle_benchmark_payload=load_json_report(Path("reports/analysis/v112be_cpo_oracle_upper_bound_benchmark_v1.json")),
        aggressive_pilot_payload=load_json_report(Path("reports/analysis/v112bf_cpo_aggressive_no_leak_black_box_portfolio_pilot_v1.json")),
        gap_review_payload=load_json_report(Path("reports/analysis/v112bg_cpo_oracle_vs_no_leak_gap_review_v1.json")),
        v112bc_protocol_payload=load_json_report(Path("reports/analysis/v112bc_cpo_portfolio_objective_protocol_v1.json")),
        training_layer_payload=load_json_report(Path("reports/analysis/v112az_cpo_bounded_training_layer_extension_v1.json")),
        cycle_reconstruction_payload=load_json_report(Path("reports/analysis/v112z_bounded_cycle_reconstruction_pass_v1.json")),
    )
    assert result.summary["no_leak_enforced"] is True
    assert result.summary["cash_ratio"] > 0.0
