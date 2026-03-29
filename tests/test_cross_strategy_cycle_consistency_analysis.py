from __future__ import annotations

from a_share_quant.strategy.cross_strategy_cycle_consistency_analysis import (
    CrossStrategyCycleConsistencyAnalyzer,
)


def test_detects_identical_negative_cycle_map() -> None:
    payloads = [
        {
            "summary": {"strategy_name": "mainline_trend_b"},
            "mechanism_rows": [
                {
                    "mechanism_type": "entry_suppression_avoidance",
                    "cycle_sign": "negative",
                    "incumbent_cycle": {"entry_date": "2024-08-01", "exit_date": "2024-08-02"},
                },
                {
                    "mechanism_type": "earlier_exit_loss_reduction",
                    "cycle_sign": "negative",
                    "incumbent_cycle": {"entry_date": "2024-08-09", "exit_date": "2024-08-14"},
                },
            ],
        },
        {
            "summary": {"strategy_name": "mainline_trend_c"},
            "mechanism_rows": [
                {
                    "mechanism_type": "entry_suppression_avoidance",
                    "cycle_sign": "negative",
                    "incumbent_cycle": {"entry_date": "2024-08-01", "exit_date": "2024-08-02"},
                },
                {
                    "mechanism_type": "earlier_exit_loss_reduction",
                    "cycle_sign": "negative",
                    "incumbent_cycle": {"entry_date": "2024-08-09", "exit_date": "2024-08-14"},
                },
            ],
        },
    ]

    result = CrossStrategyCycleConsistencyAnalyzer().analyze(report_payloads=payloads)

    assert result.summary["identical_negative_cycle_map"] is True
    assert result.summary["shared_negative_mechanism_count"] == 2
