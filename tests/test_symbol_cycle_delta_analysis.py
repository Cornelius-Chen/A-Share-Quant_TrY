from __future__ import annotations

from a_share_quant.strategy.symbol_cycle_delta_analysis import SymbolCycleDeltaAnalyzer


def test_symbol_cycle_delta_analyzer_separates_unique_cycles() -> None:
    payload = {
        "candidate_records": [
            {
                "candidate_name": "shared_default",
                "strategy_name": "mainline_trend_b",
                "closed_trades": [
                    {"entry_date": "2024-01-01", "exit_date": "2024-01-02", "pnl": -10.0, "holding_days": 1},
                    {"entry_date": "2024-01-03", "exit_date": "2024-01-04", "pnl": 5.0, "holding_days": 1},
                ],
            },
            {
                "candidate_name": "theme_strict_quality_branch",
                "strategy_name": "mainline_trend_b",
                "closed_trades": [
                    {"entry_date": "2024-01-03", "exit_date": "2024-01-04", "pnl": 7.0, "holding_days": 2},
                    {"entry_date": "2024-01-05", "exit_date": "2024-01-06", "pnl": 3.0, "holding_days": 1},
                ],
            },
        ]
    }

    result = SymbolCycleDeltaAnalyzer().analyze(
        payload=payload,
        strategy_name="mainline_trend_b",
        incumbent_name="shared_default",
        challenger_name="theme_strict_quality_branch",
    )

    assert result.summary["incumbent_only_cycle_count"] == 1
    assert result.summary["challenger_only_cycle_count"] == 1
    assert result.summary["matched_cycle_count"] == 1
    assert result.incumbent_only_cycles[0]["entry_date"] == "2024-01-01"
