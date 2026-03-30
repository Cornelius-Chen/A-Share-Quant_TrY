from __future__ import annotations

from a_share_quant.strategy.v12_training_readiness_check_v1 import (
    V12TrainingReadinessCheckAnalyzer,
)


def test_v12_training_readiness_check_keeps_branch_report_only_when_rows_are_thin() -> None:
    pilot_payload = {
        "summary": {
            "sample_count": 10,
            "class_labels": ["carry_row_present", "opening_led", "persistence_led"],
            "overall_accuracy": 1.0,
        },
        "sample_rows": [
            {"sample_id": "o1", "label": "opening_led", "f": 1.0},
            {"sample_id": "o2", "label": "opening_led", "f": 2.0},
            {"sample_id": "p1", "label": "persistence_led", "f": 3.0},
            {"sample_id": "c1", "label": "carry_row_present", "f": 4.0},
            {"sample_id": "c2", "label": "carry_row_present", "f": 4.0},
        ],
    }

    result = V12TrainingReadinessCheckAnalyzer().analyze(pilot_payload=pilot_payload)

    assert (
        result.summary["acceptance_posture"]
        == "keep_v12_training_branch_report_only_and_expand_samples_first"
    )
    assert result.summary["perfect_micro_accuracy_present"] is True
    assert result.summary["carry_duplicate_row_count"] == 1
    assert result.summary["ready_for_next_bounded_model_work"] is False
    assert result.summary["allow_strategy_training_now"] is False
