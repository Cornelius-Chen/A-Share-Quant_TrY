from __future__ import annotations

from a_share_quant.strategy.v112b_pilot_dataset_freeze_v1 import (
    V112BPilotDatasetFreezeAnalyzer,
)


def test_v112b_dataset_freeze_marks_rows_as_trainable() -> None:
    result = V112BPilotDatasetFreezeAnalyzer().analyze(
        phase_charter_payload={"summary": {"ready_for_dataset_freeze_next": True}},
        pilot_dataset_draft_payload={
            "dataset_rows": [
                {"symbol": "300308", "cycle_window": {"first_markup_start": "2023-02"}, "label_set": ["a"]},
                {"symbol": "300502", "cycle_window": {"first_markup_start": "2023-02"}, "label_set": ["a"]},
                {"symbol": "300394", "cycle_window": {"first_markup_start": "2023-02"}, "label_set": ["a"]},
            ]
        },
    )

    assert result.summary["dataset_row_count"] == 3
    assert all(row["training_readiness"] == "frozen_for_report_only_baseline" for row in result.dataset_rows)
    assert result.dataset_rows[0]["name"] == "中际旭创"
