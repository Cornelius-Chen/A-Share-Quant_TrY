from __future__ import annotations

from a_share_quant.strategy.trigger_taxonomy_analysis import TriggerTaxonomyAnalyzer


def test_trigger_taxonomy_analyzer_classifies_repair_relevant_trigger_types() -> None:
    payload = {
        "trigger_date_rows": [
            {
                "symbol": "300750",
                "strategy_name": "a",
                "trade_date": "2024-01-19",
                "action_state_types": ["emitted_actions"],
                "difference_types": ["approved_sector", "emitted_actions"],
                "incumbent_emitted_actions": [],
                "challenger_emitted_actions": ["buy"],
                "incumbent_position_qty": 0,
                "challenger_position_qty": 0,
            },
            {
                "symbol": "300750",
                "strategy_name": "a",
                "trade_date": "2024-01-22",
                "action_state_types": ["emitted_actions", "position_qty"],
                "difference_types": ["emitted_actions", "position_qty"],
                "incumbent_emitted_actions": [],
                "challenger_emitted_actions": ["sell"],
                "incumbent_position_qty": 0,
                "challenger_position_qty": 100,
            },
            {
                "symbol": "300750",
                "strategy_name": "a",
                "trade_date": "2024-02-05",
                "action_state_types": ["emitted_actions"],
                "difference_types": ["permission", "emitted_actions"],
                "incumbent_emitted_actions": ["buy"],
                "challenger_emitted_actions": [],
                "incumbent_position_qty": 0,
                "challenger_position_qty": 0,
            },
        ]
    }

    result = TriggerTaxonomyAnalyzer().analyze(payload=payload, symbol="300750")

    assert result.trigger_leaderboard[0]["count"] == 1
    assert {row["trigger_type"] for row in result.taxonomy_rows} == {
        "early_buy_trigger",
        "forced_sell_trigger",
        "missed_buy_trigger",
    }
