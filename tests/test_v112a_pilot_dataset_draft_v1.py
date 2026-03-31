from __future__ import annotations

from a_share_quant.strategy.v112a_pilot_dataset_draft_v1 import (
    V112APilotDatasetDraftAnalyzer,
)


def test_v112a_pilot_dataset_draft_marks_partial_readiness() -> None:
    result = V112APilotDatasetDraftAnalyzer().analyze(
        owner_correction_integration_payload={
            "summary": {"ready_for_partial_pilot_dataset_draft_next": True},
            "integrated_rows": [
                {
                    "symbol": "300308",
                    "name": "中际旭创",
                    "final_role_label_cn": "龙头/核心受益股",
                    "include_in_first_pilot": True,
                    "cycle_window_defined": True,
                    "cycle_window": {"major_markup_start": "2025-06"},
                    "cycle_notes": "x",
                    "still_pending_fields": [],
                    "owner_notes": "y",
                },
                {
                    "symbol": "300394",
                    "name": "天孚通信",
                    "final_role_label_cn": "上游核心器件平台受益股",
                    "include_in_first_pilot": True,
                    "cycle_window_defined": False,
                    "cycle_window": {},
                    "cycle_notes": "",
                    "still_pending_fields": ["cycle_window"],
                    "owner_notes": "",
                },
            ],
        },
        training_protocol_payload={"protocol": {"label_set": ["a", "b", "c"]}},
    )

    assert result.summary["resolved_training_row_count"] == 1
    assert result.summary["pending_training_row_count"] == 1
