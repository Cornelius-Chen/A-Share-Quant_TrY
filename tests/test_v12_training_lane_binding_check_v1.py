from __future__ import annotations

from a_share_quant.strategy.v12_training_lane_binding_check_v1 import (
    V12TrainingLaneBindingCheckAnalyzer,
)


def test_v12_training_lane_binding_check_rejects_frozen_opening_and_keeps_future_bind_paths() -> None:
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
    candidate_payloads = [
        (
            "reports/analysis/current_opening.json",
            {
                "summary": {
                    "dataset_name": "market_research_v4_carry_row_diversity_refresh",
                    "slice_name": "2024_q2",
                    "top_driver": "601919",
                    "opening_present": True,
                    "persistence_present": False,
                    "lane_changes_carry_reading": False,
                }
            },
        ),
        (
            "reports/analysis/future_persistence.json",
            {
                "summary": {
                    "dataset_name": "future_dataset",
                    "slice_name": "future_slice",
                    "top_driver": "000001",
                    "opening_present": False,
                    "persistence_present": True,
                    "lane_changes_carry_reading": False,
                }
            },
        ),
    ]

    result = V12TrainingLaneBindingCheckAnalyzer().analyze(
        manifest_payload=manifest_payload,
        candidate_payloads=candidate_payloads,
    )

    assert result.summary["bindable_persistence_count"] == 1
    assert result.summary["bindable_carry_count"] == 0
    assert result.summary["ready_to_expand_training_sample_now"] is True
    assert result.candidate_rows[0]["binding_outcome"] == "reject_opening_class_frozen"
    assert result.candidate_rows[1]["binding_outcome"] == "bind_as_persistence_led"
