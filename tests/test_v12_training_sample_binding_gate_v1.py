from __future__ import annotations

from a_share_quant.strategy.v12_training_sample_binding_gate_v1 import (
    V12TrainingSampleBindingGateAnalyzer,
)


def test_v12_training_sample_binding_gate_rejects_current_opening_first_lanes() -> None:
    manifest_payload = {
        "summary": {
            "opening_count_frozen": True,
        },
        "manifest_rows": [
            {"class_name": "opening_led", "additional_rows_needed": 0},
            {"class_name": "persistence_led", "additional_rows_needed": 2},
            {"class_name": "carry_row_present", "additional_rows_needed": 2},
        ],
    }
    v3_first_lane_payload = {
        "summary": {
            "dataset_name": "market_research_v3_factor_diversity_seed",
            "slice_name": "2024_q4",
            "top_driver": "002049",
            "opening_present": True,
            "persistence_present": False,
            "lane_changes_carry_reading": False,
        }
    }
    v4_first_lane_payload = {
        "summary": {
            "dataset_name": "market_research_v4_carry_row_diversity_refresh",
            "slice_name": "2024_q2",
            "top_driver": "601919",
            "opening_present": True,
            "persistence_present": False,
            "lane_changes_carry_reading": False,
        }
    }

    result = V12TrainingSampleBindingGateAnalyzer().analyze(
        manifest_payload=manifest_payload,
        v3_first_lane_payload=v3_first_lane_payload,
        v4_first_lane_payload=v4_first_lane_payload,
    )

    assert result.summary["allow_binding_current_opening_led_rows"] is False
    assert result.summary["allow_binding_future_clean_persistence_rows"] is True
    assert result.summary["allow_binding_future_true_carry_rows"] is True
    assert result.summary["current_bindable_row_count"] == 0
    assert result.summary["current_non_bindable_row_count"] == 2
