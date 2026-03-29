from __future__ import annotations

from a_share_quant.strategy.symbol_path_shift_analysis import SymbolPathShiftAnalyzer


def test_symbol_path_shift_analyzer_detects_repeated_shift_dates() -> None:
    payload = {
        "candidate_records": [
            {
                "candidate_name": "shared_default",
                "strategy_name": "mainline_trend_a",
                "daily_records": [
                    {
                        "trade_date": "2024-01-22",
                        "permission_allowed": False,
                        "approved_sector_id": None,
                        "assignment_layer": "leader",
                        "assignment_reason": "x",
                        "emitted_actions": [],
                        "pending_buy": False,
                        "pending_sell": False,
                        "position_qty": 0,
                        "exit_reason": None,
                    }
                ],
            },
            {
                "candidate_name": "buffer_only_012",
                "strategy_name": "mainline_trend_a",
                "daily_records": [
                    {
                        "trade_date": "2024-01-22",
                        "permission_allowed": False,
                        "approved_sector_id": None,
                        "assignment_layer": "leader",
                        "assignment_reason": "x",
                        "emitted_actions": ["sell"],
                        "pending_buy": False,
                        "pending_sell": False,
                        "position_qty": 100,
                        "exit_reason": "attack_permission_removed",
                    }
                ],
            },
            {
                "candidate_name": "shared_default",
                "strategy_name": "mainline_trend_b",
                "daily_records": [
                    {
                        "trade_date": "2024-01-22",
                        "permission_allowed": False,
                        "approved_sector_id": None,
                        "assignment_layer": "leader",
                        "assignment_reason": "x",
                        "emitted_actions": [],
                        "pending_buy": False,
                        "pending_sell": False,
                        "position_qty": 0,
                        "exit_reason": None,
                    }
                ],
            },
            {
                "candidate_name": "buffer_only_012",
                "strategy_name": "mainline_trend_b",
                "daily_records": [
                    {
                        "trade_date": "2024-01-22",
                        "permission_allowed": False,
                        "approved_sector_id": None,
                        "assignment_layer": "leader",
                        "assignment_reason": "x",
                        "emitted_actions": ["sell"],
                        "pending_buy": False,
                        "pending_sell": False,
                        "position_qty": 100,
                        "exit_reason": "attack_permission_removed",
                    }
                ],
            },
        ]
    }

    result = SymbolPathShiftAnalyzer().analyze(
        payload=payload,
        incumbent_name="shared_default",
        challenger_name="buffer_only_012",
    )

    assert result.summary["most_repeated_shift_date"]["trade_date"] == "2024-01-22"
    assert result.repeated_shift_dates[0]["strategy_count"] == 2
