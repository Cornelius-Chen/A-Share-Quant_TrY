from __future__ import annotations

from a_share_quant.strategy.v12_bounded_training_pilot_v1 import (
    V12BoundedTrainingPilotAnalyzer,
)


def test_v12_bounded_training_pilot_produces_report_only_summary() -> None:
    opening_payload = {
        "opening_edge": {
            "specialist_assignment_layer": "late_mover",
            "specialist_permission_allowed": True,
            "specialist_triggered_entries": ["confirmation_entry", "second_breakout"],
            "specialist_passed_filters": ["strict_short_term_bullish", "medium_term_uptrend"],
        },
        "anchor_blockers": [
            {"permission_allowed": True, "assignment_layer": "junk", "emitted_actions": []},
            {"permission_allowed": True, "assignment_layer": "junk", "emitted_actions": []},
        ],
    }
    persistence_payload = {
        "persistence_edge": {
            "specialist_assignment_layer": "late_mover",
            "specialist_position_qty": 100,
            "specialist_holding_health_score": 3.5,
        },
        "anchor_divergence": [
            {"assignment_layer": "junk", "exit_should_exit": True},
            {"assignment_layer": "junk", "exit_should_exit": True},
        ],
    }
    carry_payload = {
        "schema_rows": [
            {
                "basis_advantage_bps": 300.0,
                "challenger_carry_days": 1,
                "same_exit_date": True,
                "pnl_delta_vs_closest": 800.0,
            },
            {
                "basis_advantage_bps": 320.0,
                "challenger_carry_days": 1,
                "same_exit_date": True,
                "pnl_delta_vs_closest": 820.0,
            },
        ]
    }

    result = V12BoundedTrainingPilotAnalyzer().analyze(
        opening_payloads=[("open_1", opening_payload), ("open_2", opening_payload)],
        persistence_payloads=[("persist_1", persistence_payload)],
        carry_payload=carry_payload,
    )

    assert result.summary["pilot_posture"] == "open_v12_bounded_training_pilot_as_report_only"
    assert result.summary["allow_strategy_training_now"] is False
    assert result.summary["allow_news_branch_training_now"] is False
    assert result.summary["sample_count"] == 5
    assert set(result.summary["class_labels"]) == {
        "opening_led",
        "persistence_led",
        "carry_row_present",
    }
