from __future__ import annotations

from a_share_quant.strategy.family_candidate_shortlist import FamilyCandidateShortlistAnalyzer


def test_shortlist_filters_and_ranks_candidates() -> None:
    analyzer = FamilyCandidateShortlistAnalyzer()
    result = analyzer.analyze(
        report_specs=[
            {
                "report_path": "reports/analysis/theme_q4_trade_divergence_quality_b_v1.json",
                "dataset_name": "theme_research_v4",
                "slice_name": "2024_q4",
                "strategy_name": "mainline_trend_b",
            }
        ],
        excluded_symbols=[
            {
                "dataset_name": "theme_research_v4",
                "slice_name": "2024_q4",
                "strategy_name": "mainline_trend_b",
                "symbol": "300750",
            }
        ],
        min_positive_delta=50.0,
    )
    assert result.summary["candidate_count"] >= 1
    assert result.shortlist_rows[0]["symbol"] == "300759"
    assert result.shortlist_rows[0]["shortlist_score"] > 0
