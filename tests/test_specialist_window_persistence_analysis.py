from __future__ import annotations

from a_share_quant.strategy.specialist_window_persistence_analysis import SpecialistWindowPersistenceAnalyzer


def test_specialist_window_persistence_analyzer_finds_first_hold_while_anchors_sell() -> None:
    payload = {
        "candidate_records": [
            {
                "candidate_name": "shared_default",
                "strategy_name": "mainline_trend_c",
                "daily_records": [
                    {
                        "trade_date": "2024-02-22",
                        "position_qty": 100,
                        "holding_should_hold": True,
                        "holding_health_score": 2.5,
                        "exit_should_exit": True,
                        "exit_reason": "assignment_became_junk",
                        "emitted_actions": ["sell"],
                        "assignment_layer": "junk",
                        "assignment_reason": "fallback_to_junk",
                    }
                ],
            },
            {
                "candidate_name": "buffer_only_012",
                "strategy_name": "mainline_trend_c",
                "daily_records": [
                    {
                        "trade_date": "2024-02-22",
                        "position_qty": 100,
                        "holding_should_hold": True,
                        "holding_health_score": 2.5,
                        "exit_should_exit": True,
                        "exit_reason": "assignment_became_junk",
                        "emitted_actions": ["sell"],
                        "assignment_layer": "junk",
                        "assignment_reason": "fallback_to_junk",
                    }
                ],
            },
            {
                "candidate_name": "baseline_expansion_branch",
                "strategy_name": "mainline_trend_c",
                "daily_records": [
                    {
                        "trade_date": "2024-02-22",
                        "position_qty": 100,
                        "holding_should_hold": True,
                        "holding_health_score": 3.5,
                        "exit_should_exit": False,
                        "exit_reason": "structure_intact",
                        "emitted_actions": [],
                        "assignment_layer": "late_mover",
                        "assignment_reason": "late_mover_quality_fallback",
                    }
                ],
            },
        ]
    }

    result = SpecialistWindowPersistenceAnalyzer().analyze(
        payload=payload,
        strategy_name="mainline_trend_c",
        specialist_candidate="baseline_expansion_branch",
        anchor_candidates=["shared_default", "buffer_only_012"],
        window_start="2024-02-21",
        window_end="2024-02-29",
    )

    assert result.summary["specialist_preserved_window"] is True
    assert result.summary["persistence_trade_date"] == "2024-02-22"
    assert result.persistence_edge is not None
    assert result.persistence_edge["specialist_exit_should_exit"] is False
    assert len(result.anchor_divergence) == 2
