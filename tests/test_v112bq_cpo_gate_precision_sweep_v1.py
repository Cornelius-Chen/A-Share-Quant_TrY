from pathlib import Path

from a_share_quant.strategy.v112bq_cpo_gate_precision_sweep_v1 import (
    V112BQCPOGatePrecisionSweepAnalyzer,
    load_json_report,
)


def test_v112bq_gate_precision_sweep_runs_and_returns_non_cash_candidate() -> None:
    analyzer = V112BQCPOGatePrecisionSweepAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112bq_phase_charter_v1.json")),
        fusion_pilot_payload=load_json_report(Path("reports/analysis/v112bp_cpo_selector_maturity_fusion_pilot_v1.json")),
        neutral_pilot_payload=load_json_report(Path("reports/analysis/v112bh_cpo_neutral_selective_no_leak_portfolio_pilot_v1.json")),
        teacher_decomposition_payload=load_json_report(Path("reports/analysis/v112bn_teacher_decomposition_gate_search_v1.json")),
        gap_review_payload=load_json_report(Path("reports/analysis/v112bg_cpo_oracle_vs_no_leak_gap_review_v1.json")),
        internal_maturity_payload=load_json_report(Path("reports/analysis/v112bo_cpo_internal_maturity_overlay_review_v1.json")),
        regime_gate_payload=load_json_report(Path("reports/analysis/v112bl_cpo_regime_aware_gate_pilot_v1.json")),
        training_layer_payload=load_json_report(Path("reports/analysis/v112az_cpo_bounded_training_layer_extension_v1.json")),
        cycle_reconstruction_payload=load_json_report(Path("reports/analysis/v112z_bounded_cycle_reconstruction_pass_v1.json")),
    )
    assert result.summary["no_leak_enforced"] is True
    assert result.summary["best_trade_count"] > 0
    assert result.trade_rows

