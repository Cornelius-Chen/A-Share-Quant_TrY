from __future__ import annotations

from a_share_quant.strategy.action_state_divergence_analysis import ActionStateDivergenceAnalyzer


def test_action_state_divergence_analyzer_finds_trigger_dates_only_when_actions_or_positions_change() -> None:
    result = ActionStateDivergenceAnalyzer().analyze(
        case_payloads=[
            {
                "symbol": "300750",
                "path_payload": {
                    "repeated_shift_dates": [{"trade_date": "2024-01-19", "strategy_count": 3}],
                    "detailed_shifts": [
                        {
                            "strategy_name": "mainline_trend_a",
                            "trade_date": "2024-01-19",
                            "difference_types": ["approved_sector", "emitted_actions", "position_qty"],
                            "incumbent_emitted_actions": [],
                            "challenger_emitted_actions": ["buy"],
                            "incumbent_position_qty": 0,
                            "challenger_position_qty": 100,
                        }
                    ],
                },
            },
            {
                "symbol": "002466",
                "path_payload": {
                    "repeated_shift_dates": [{"trade_date": "2024-02-05", "strategy_count": 3}],
                    "detailed_shifts": [
                        {
                            "strategy_name": "mainline_trend_a",
                            "trade_date": "2024-02-05",
                            "difference_types": ["approved_sector", "permission"],
                            "incumbent_emitted_actions": [],
                            "challenger_emitted_actions": [],
                            "incumbent_position_qty": 0,
                            "challenger_position_qty": 0,
                        }
                    ],
                },
            },
        ]
    )

    assert result.summary["triggered_symbols"] == ["300750"]
    assert result.symbol_summaries[0]["triggered_dates"] == ["2024-01-19"]
    assert result.symbol_summaries[1]["triggered_dates"] == []
