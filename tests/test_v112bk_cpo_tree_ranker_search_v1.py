from pathlib import Path

from a_share_quant.strategy.v112bk_cpo_tree_ranker_search_v1 import (
    V112BKCpoTreeRankerSearchAnalyzer,
    load_json_report,
)


def test_v112bk_tree_ranker_search_produces_variant_rows() -> None:
    analyzer = V112BKCpoTreeRankerSearchAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112bk_phase_charter_v1.json")),
        oracle_benchmark_payload=load_json_report(Path("reports/analysis/v112be_cpo_oracle_upper_bound_benchmark_v1.json")),
        aggressive_pilot_payload=load_json_report(Path("reports/analysis/v112bf_cpo_aggressive_no_leak_black_box_portfolio_pilot_v1.json")),
        neutral_pilot_payload=load_json_report(Path("reports/analysis/v112bh_cpo_neutral_selective_no_leak_portfolio_pilot_v1.json")),
        training_layer_payload=load_json_report(Path("reports/analysis/v112az_cpo_bounded_training_layer_extension_v1.json")),
        cycle_reconstruction_payload=load_json_report(Path("reports/analysis/v112z_bounded_cycle_reconstruction_pass_v1.json")),
    )
    assert result.summary["no_leak_enforced"] is True
    assert result.summary["variant_count"] >= 2
