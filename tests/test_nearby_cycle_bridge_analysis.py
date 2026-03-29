from __future__ import annotations

from a_share_quant.strategy.nearby_cycle_bridge_analysis import NearbyCycleBridgeAnalyzer


def test_nearby_cycle_bridge_analyzer_labels_avoided_and_reduced_loss_cycles() -> None:
    cycle_delta_payload = {
        "incumbent_only_cycles": [
            {"entry_date": "2024-01-01", "exit_date": "2024-01-02", "pnl": -10.0, "holding_days": 1},
            {"entry_date": "2024-01-05", "exit_date": "2024-01-06", "pnl": -20.0, "holding_days": 1},
        ]
    }
    timeline_payload = {
        "candidate_records": [
            {
                "candidate_name": "shared_default",
                "strategy_name": "mainline_trend_b",
                "closed_trades": [],
            },
            {
                "candidate_name": "theme_strict_quality_branch",
                "strategy_name": "mainline_trend_b",
                "closed_trades": [
                    {"entry_date": "2024-01-05", "exit_date": "2024-01-07", "pnl": -5.0, "holding_days": 2}
                ],
            },
        ]
    }

    result = NearbyCycleBridgeAnalyzer().analyze(
        cycle_delta_payload=cycle_delta_payload,
        timeline_payload=timeline_payload,
        strategy_name="mainline_trend_b",
        incumbent_name="shared_default",
        challenger_name="theme_strict_quality_branch",
        bridge_days=1,
    )

    assert result.summary["avoided_cycle_count"] == 1
    assert result.summary["reduced_loss_cycle_count"] == 1
    assert result.bridged_cycles[0]["classification"] == "avoided_cycle"
