from __future__ import annotations

from a_share_quant.strategy.missed_reentry_chain_analysis import MissedReentryChainAnalyzer


def test_missed_reentry_chain_analyzer_identifies_complete_incumbent_side_chain() -> None:
    timeline_payload = {
        "candidate_records": [
            {
                "candidate_name": "shared_default",
                "strategy_name": "mainline_trend_a",
                "symbol": "300750",
                "daily_records": [
                    {
                        "trade_date": "2024-02-05",
                        "permission_allowed": True,
                        "approved_sector_id": "BK1173",
                        "emitted_actions": ["buy"],
                        "position_qty": 0,
                        "exit_reason": None,
                    },
                    {
                        "trade_date": "2024-02-06",
                        "permission_allowed": True,
                        "approved_sector_id": "BK0895",
                        "emitted_actions": ["sell"],
                        "position_qty": 100,
                        "exit_reason": "new_sector_approved",
                    },
                ],
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
                "strategy_name": "mainline_trend_a",
                "symbol": "300750",
                "daily_records": [
                    {
                        "trade_date": "2024-02-05",
                        "permission_allowed": False,
                        "approved_sector_id": None,
                        "emitted_actions": [],
                        "position_qty": 0,
                        "exit_reason": None,
                    },
                    {
                        "trade_date": "2024-02-06",
                        "permission_allowed": True,
                        "approved_sector_id": "BK0895",
                        "emitted_actions": [],
                        "position_qty": 0,
                        "exit_reason": None,
                    },
                ],
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
    path_payload = {
        "detailed_shifts": [
            {
                "strategy_name": "mainline_trend_a",
                "trade_date": "2024-02-05",
                "difference_types": ["permission", "approved_sector", "emitted_actions"],
            },
            {
                "strategy_name": "mainline_trend_a",
                "trade_date": "2024-02-06",
                "difference_types": ["emitted_actions", "position_qty", "exit_reason"],
            },
        ]
    }

    result = MissedReentryChainAnalyzer().analyze(
        timeline_payload=timeline_payload,
        path_payload=path_payload,
        symbol="300750",
        incumbent_name="shared_default",
        challenger_name="buffer_only_012",
        missed_buy_date="2024-02-05",
        position_gap_date="2024-02-06",
    )

    assert result.summary["complete_chain_count"] == 1
    assert result.summary["incumbent_missed_cycle_total_pnl"] == 90.0
    assert result.chain_rows[0]["missed_buy_triggered"] is True
    assert result.chain_rows[0]["position_gap_triggered"] is True
    assert result.chain_rows[0]["net_chain_pnl_delta"] == -90.0
