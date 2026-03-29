from __future__ import annotations

from a_share_quant.strategy.damage_transition_analysis import DamageTransitionAnalyzer


def test_damage_transition_analyzer_separates_damage_and_latent_cases() -> None:
    result = DamageTransitionAnalyzer().analyze(
        case_payloads=[
            {
                "symbol": "300750",
                "timeline_payload": {
                    "comparison_records": [
                        {
                            "strategy_name": "a",
                            "incumbent_fill_count": 3,
                            "challenger_fill_count": 4,
                            "incumbent_trade_count": 2,
                            "challenger_trade_count": 3,
                            "pnl_delta": -530.7,
                        }
                    ]
                },
                "path_payload": {
                    "repeated_shift_dates": [{"trade_date": "2024-01-19", "strategy_count": 3}],
                    "detailed_shifts": [
                        {
                            "trade_date": "2024-01-19",
                            "difference_types": ["approved_sector", "permission", "emitted_actions", "position_qty"],
                        }
                    ],
                },
            },
            {
                "symbol": "002466",
                "timeline_payload": {
                    "comparison_records": [
                        {
                            "strategy_name": "a",
                            "incumbent_fill_count": 2,
                            "challenger_fill_count": 2,
                            "incumbent_trade_count": 2,
                            "challenger_trade_count": 2,
                            "pnl_delta": 0.0,
                        }
                    ]
                },
                "path_payload": {
                    "repeated_shift_dates": [{"trade_date": "2024-02-05", "strategy_count": 3}],
                    "detailed_shifts": [
                        {
                            "trade_date": "2024-02-05",
                            "difference_types": ["approved_sector", "permission"],
                        }
                    ],
                },
            },
        ]
    )

    assert result.summary["damage_case_symbols"] == ["300750"]
    assert result.symbol_cases[0]["case_class"] == "damage_case"
    assert result.symbol_cases[1]["case_class"] == "latent_approval_permission_case"
