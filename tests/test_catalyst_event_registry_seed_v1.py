from __future__ import annotations

from a_share_quant.strategy.catalyst_event_registry_seed_v1 import (
    CatalystEventRegistrySeedAnalyzer,
)


def test_catalyst_event_registry_seed_builds_bounded_lane_sample() -> None:
    opening_reports = [
        (
            "reports/analysis/opening_002371.json",
            {
                "summary": {
                    "strategy_name": "mainline_trend_c",
                    "window_start": "2024-06-05",
                    "window_end": "2024-06-07",
                    "opening_trade_date": "2024-06-05",
                },
                "opening_edge": {"specialist_assignment_reason": "highest_late_mover_score"},
            },
        )
    ]
    persistence_reports = [
        (
            "reports/analysis/persistence_300502.json",
            {
                "summary": {
                    "strategy_name": "mainline_trend_c",
                    "window_start": "2024-06-14",
                    "window_end": "2024-06-19",
                    "persistence_trade_date": "2024-06-17",
                },
                "persistence_edge": {"specialist_exit_reason": "structure_intact"},
            },
        )
    ]
    carry_schema_payload = {
        "schema_rows": [
            {
                "strategy_name": "mainline_trend_b",
                "trigger_date": "2024-11-05",
                "challenger_entry_date": "2024-11-05",
                "challenger_exit_date": "2024-11-07",
                "challenger_carry_days": 1,
                "basis_advantage_bps": 333.4258,
            }
        ]
    }

    result = CatalystEventRegistrySeedAnalyzer().analyze(
        opening_reports=opening_reports,
        persistence_reports=persistence_reports,
        carry_schema_payload=carry_schema_payload,
    )

    assert result.summary["seed_row_count"] == 3
    assert result.summary["opening_seed_count"] == 1
    assert result.summary["persistence_seed_count"] == 1
    assert result.summary["carry_seed_count"] == 1
    assert result.summary["ready_for_first_manual_or_semimanual_event_fill"] is True
