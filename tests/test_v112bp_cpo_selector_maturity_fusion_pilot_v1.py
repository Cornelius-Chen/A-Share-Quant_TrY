from pathlib import Path

from a_share_quant.strategy.v112bp_cpo_selector_maturity_fusion_pilot_v1 import (
    V112BPCpoSelectorMaturityFusionPilotAnalyzer,
    load_json_report,
)


def test_v112bp_fusion_pilot_runs_and_stays_bounded() -> None:
    analyzer = V112BPCpoSelectorMaturityFusionPilotAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112bp_phase_charter_v1.json")),
        oracle_benchmark_payload=load_json_report(Path("reports/analysis/v112be_cpo_oracle_upper_bound_benchmark_v1.json")),
        aggressive_pilot_payload=load_json_report(Path("reports/analysis/v112bf_cpo_aggressive_no_leak_black_box_portfolio_pilot_v1.json")),
        neutral_pilot_payload=load_json_report(Path("reports/analysis/v112bh_cpo_neutral_selective_no_leak_portfolio_pilot_v1.json")),
        ranker_search_payload=load_json_report(Path("reports/analysis/v112bk_cpo_tree_ranker_search_v1.json")),
        market_overlay_payload=load_json_report(Path("reports/analysis/v112bd_market_regime_overlay_feature_review_v1.json")),
        internal_maturity_payload=load_json_report(Path("reports/analysis/v112bo_cpo_internal_maturity_overlay_review_v1.json")),
        training_layer_payload=load_json_report(Path("reports/analysis/v112az_cpo_bounded_training_layer_extension_v1.json")),
        cycle_reconstruction_payload=load_json_report(Path("reports/analysis/v112z_bounded_cycle_reconstruction_pass_v1.json")),
    )
    assert result.summary["no_leak_enforced"] is True
    assert result.summary["formal_signal_generation_now"] is False
    assert result.gate_decision_rows
