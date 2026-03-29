from __future__ import annotations

from a_share_quant.strategy.trigger_priority_analysis import TriggerPriorityAnalyzer


def test_trigger_priority_analyzer_prioritizes_incumbent_only_cycles_when_they_dominate_damage() -> None:
    timeline_payload = {
        "candidate_records": [
            {
                "candidate_name": "shared_default",
                "strategy_name": "a",
                "symbol": "300750",
                "closed_trades": [
                    {
                        "entry_date": "2024-02-06",
                        "exit_date": "2024-02-07",
                        "quantity": 100,
                        "entry_price": 10.0,
                        "exit_price": 11.0,
                        "pnl": 90.0,
                    }
                ],
            },
            {
                "candidate_name": "buffer_only_012",
                "strategy_name": "a",
                "symbol": "300750",
                "closed_trades": [
                    {
                        "entry_date": "2024-01-22",
                        "exit_date": "2024-01-23",
                        "quantity": 100,
                        "entry_price": 9.0,
                        "exit_price": 9.5,
                        "pnl": 40.0,
                    }
                ],
            },
        ]
    }
    taxonomy_payload = {
        "taxonomy_rows": [
            {"symbol": "300750", "trigger_type": "early_buy_trigger"},
            {"symbol": "300750", "trigger_type": "forced_sell_trigger"},
            {"symbol": "300750", "trigger_type": "missed_buy_trigger"},
            {"symbol": "300750", "trigger_type": "position_gap_exit_trigger"},
        ]
    }

    result = TriggerPriorityAnalyzer().analyze(
        timeline_payload=timeline_payload,
        taxonomy_payload=taxonomy_payload,
        symbol="300750",
        incumbent_name="shared_default",
        challenger_name="buffer_only_012",
    )

    assert result.summary["incumbent_unique_total_pnl"] == 90.0
    assert result.summary["challenger_unique_total_pnl"] == 40.0
    assert result.trigger_family_priority[0]["trigger_family"] == "missed_buy_trigger"
