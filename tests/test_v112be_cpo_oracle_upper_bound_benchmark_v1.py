from pathlib import Path

from a_share_quant.strategy.v112be_cpo_oracle_upper_bound_benchmark_v1 import (
    V112BECPOOracleUpperBoundBenchmarkAnalyzer,
    load_json_report,
)


def test_v112be_oracle_benchmark_produces_upper_bound_trace() -> None:
    analyzer = V112BECPOOracleUpperBoundBenchmarkAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112be_phase_charter_v1.json")),
        v112bc_protocol_payload=load_json_report(Path("reports/analysis/v112bc_cpo_portfolio_objective_protocol_v1.json")),
        v112bb_pilot_payload=load_json_report(Path("reports/analysis/v112bb_cpo_default_10_row_guarded_layer_pilot_v1.json")),
        training_layer_payload=load_json_report(Path("reports/analysis/v112az_cpo_bounded_training_layer_extension_v1.json")),
        cycle_reconstruction_payload=load_json_report(Path("reports/analysis/v112z_bounded_cycle_reconstruction_pass_v1.json")),
    )
    assert result.summary["trade_count"] > 0
    assert result.summary["future_information_allowed"] is True
