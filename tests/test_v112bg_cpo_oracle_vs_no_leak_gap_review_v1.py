from pathlib import Path

from a_share_quant.strategy.v112bg_cpo_oracle_vs_no_leak_gap_review_v1 import (
    V112BGCPOOracleVsNoLeakGapReviewAnalyzer,
    load_json_report,
)


def test_v112bg_gap_review_produces_neutral_recommendation() -> None:
    analyzer = V112BGCPOOracleVsNoLeakGapReviewAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112bg_phase_charter_v1.json")),
        oracle_benchmark_payload=load_json_report(Path("reports/analysis/v112be_cpo_oracle_upper_bound_benchmark_v1.json")),
        aggressive_pilot_payload=load_json_report(Path("reports/analysis/v112bf_cpo_aggressive_no_leak_black_box_portfolio_pilot_v1.json")),
        v112bc_protocol_payload=load_json_report(Path("reports/analysis/v112bc_cpo_portfolio_objective_protocol_v1.json")),
    )
    assert result.summary["open_neutral_selective_track_next"] is True
    assert result.summary["recommended_probability_margin_floor"] >= 0.08
