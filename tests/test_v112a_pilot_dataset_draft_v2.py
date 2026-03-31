from __future__ import annotations

from a_share_quant.strategy.v112a_pilot_dataset_draft_v2 import (
    V112APilotDatasetDraftV2Analyzer,
)


def test_v2_marks_price_inferred_rows_for_owner_calibration() -> None:
    result = V112APilotDatasetDraftV2Analyzer().analyze(
        pilot_dataset_draft_v1_payload={
            "dataset_rows": [
                {
                    "symbol": "300308",
                    "name": "中际旭创",
                    "final_role_label_cn": "龙头/核心受益股",
                    "include_in_first_pilot": True,
                    "cycle_window": {"major_markup_start": "2025-06"},
                    "cycle_notes": "owner",
                    "label_set": ["x"],
                    "training_readiness": "ready_for_next_labeling_step",
                    "pending_fields": [],
                    "owner_notes": "ok",
                },
                {
                    "symbol": "300502",
                    "name": "新易盛",
                    "final_role_label_cn": "高弹性核心受益股",
                    "include_in_first_pilot": True,
                    "cycle_window": {},
                    "cycle_notes": "",
                    "label_set": ["x"],
                    "training_readiness": "pending_more_owner_input",
                    "pending_fields": ["cycle_window"],
                    "owner_notes": "",
                },
                {
                    "symbol": "300394",
                    "name": "天孚通信",
                    "final_role_label_cn": "上游核心器件平台受益股",
                    "include_in_first_pilot": True,
                    "cycle_window": {},
                    "cycle_notes": "",
                    "label_set": ["x"],
                    "training_readiness": "pending_more_owner_input",
                    "pending_fields": ["cycle_window"],
                    "owner_notes": "",
                },
            ]
        },
        price_cycle_inference_payload={
            "inferred_rows": [
                {
                    "symbol": "300502",
                    "suggested_cycle_window": {"major_markup_start": "2025-06"},
                    "notes_cn": "n1",
                },
                {
                    "symbol": "300394",
                    "suggested_cycle_window": {"major_markup_start": "2025-07"},
                    "notes_cn": "n2",
                },
            ]
        },
    )

    row_map = {row["symbol"]: row for row in result.dataset_rows}
    assert row_map["300308"]["training_readiness"] == "ready_for_next_labeling_step"
    assert row_map["300502"]["training_readiness"] == "price_inferred_waiting_owner_calibration"
    assert row_map["300394"]["cycle_window"]["major_markup_start"] == "2025-07"
