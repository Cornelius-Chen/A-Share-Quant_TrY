from __future__ import annotations

from a_share_quant.strategy.specialist_window_opening_analysis import SpecialistWindowOpeningAnalyzer


def test_specialist_window_opening_analyzer_finds_first_specialist_only_buy() -> None:
    payload = {
        "candidate_records": [
            {
                "candidate_name": "shared_default",
                "strategy_name": "mainline_trend_c",
                "daily_records": [
                    {
                        "trade_date": "2024-01-10",
                        "permission_allowed": True,
                        "assignment_layer": "junk",
                        "assignment_reason": "fallback_to_junk",
                        "triggered_entries": ["mid_trend_follow"],
                        "passed_filters": ["medium_term_uptrend"],
                        "emitted_actions": [],
                    }
                ],
            },
            {
                "candidate_name": "buffer_only_012",
                "strategy_name": "mainline_trend_c",
                "daily_records": [
                    {
                        "trade_date": "2024-01-10",
                        "permission_allowed": True,
                        "assignment_layer": "junk",
                        "assignment_reason": "fallback_to_junk",
                        "triggered_entries": ["mid_trend_follow"],
                        "passed_filters": ["medium_term_uptrend"],
                        "emitted_actions": [],
                    }
                ],
            },
            {
                "candidate_name": "baseline_expansion_branch",
                "strategy_name": "mainline_trend_c",
                "daily_records": [
                    {
                        "trade_date": "2024-01-10",
                        "permission_allowed": True,
                        "assignment_layer": "late_mover",
                        "assignment_reason": "late_mover_quality_fallback",
                        "triggered_entries": ["mid_trend_follow"],
                        "passed_filters": ["medium_term_uptrend"],
                        "emitted_actions": ["buy"],
                    }
                ],
            },
        ]
    }

    result = SpecialistWindowOpeningAnalyzer().analyze(
        payload=payload,
        strategy_name="mainline_trend_c",
        specialist_candidate="baseline_expansion_branch",
        anchor_candidates=["shared_default", "buffer_only_012"],
        window_start="2024-01-10",
        window_end="2024-01-18",
    )

    assert result.summary["specialist_opened_window"] is True
    assert result.summary["opening_trade_date"] == "2024-01-10"
    assert result.opening_edge is not None
    assert result.opening_edge["specialist_assignment_layer"] == "late_mover"
    assert len(result.anchor_blockers) == 2
