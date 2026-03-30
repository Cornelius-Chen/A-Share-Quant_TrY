from __future__ import annotations

from a_share_quant.strategy.v12_carry_row_hunting_strategy_v1 import (
    V12CarryRowHuntingStrategyAnalyzer,
)


def test_v12_carry_row_hunting_strategy_prioritizes_basis_and_duration_after_opening_first_lane() -> None:
    v4_manifest_payload = {
        "manifest_rows": [
            {"symbol": "601919", "target_row_diversity": "exit_alignment_diversity", "carry_row_hypothesis": "checked"},
            {"symbol": "000725", "target_row_diversity": "basis_spread_diversity", "carry_row_hypothesis": "basis"},
            {"symbol": "601127", "target_row_diversity": "carry_duration_diversity", "carry_row_hypothesis": "duration"},
            {"symbol": "600570", "target_row_diversity": "cross_dataset_carry_reuse", "carry_row_hypothesis": "reuse"},
        ]
    }
    v4_first_lane_payload = {
        "summary": {
            "top_driver": "601919",
        }
    }
    training_manifest_payload = {
        "manifest_rows": [
            {"class_name": "carry_row_present", "additional_rows_needed": 2},
        ]
    }

    result = V12CarryRowHuntingStrategyAnalyzer().analyze(
        v4_manifest_payload=v4_manifest_payload,
        v4_first_lane_payload=v4_first_lane_payload,
        training_manifest_payload=training_manifest_payload,
    )

    assert result.summary["do_open_new_refresh_now"] is False
    assert result.summary["do_widen_replay_now"] is False
    assert result.summary["recommended_next_symbol"] == "000725"
    assert result.hunt_rows[0]["target_row_diversity"] == "basis_spread_diversity"
