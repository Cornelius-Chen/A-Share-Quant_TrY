from __future__ import annotations

from a_share_quant.strategy.v112a_pilot_dataset_draft_v3 import (
    V112APilotDatasetDraftV3Analyzer,
)


def test_v3_marks_all_rows_for_owner_calibration() -> None:
    result = V112APilotDatasetDraftV3Analyzer().analyze(
        pilot_dataset_draft_v1_payload={
            "dataset_rows": [
                {"symbol": "300308", "label_set": ["x"], "include_in_first_pilot": True},
                {"symbol": "300502", "label_set": ["x"], "include_in_first_pilot": True},
                {"symbol": "300394", "label_set": ["x"], "include_in_first_pilot": True},
            ]
        },
        price_cycle_inference_v2_payload={
            "inferred_rows": [
                {"symbol": "300308", "name": "中际旭创", "final_role_label_cn": "龙头/核心受益股", "suggested_cycle_window": {"a": "1"}, "reference_owner_cycle_window": {"b": "2"}, "notes_cn": "n1"},
                {"symbol": "300502", "name": "新易盛", "final_role_label_cn": "高弹性核心受益股", "suggested_cycle_window": {"a": "1"}, "reference_owner_cycle_window": {}, "notes_cn": "n2"},
                {"symbol": "300394", "name": "天孚通信", "final_role_label_cn": "上游核心器件平台受益股", "suggested_cycle_window": {"a": "1"}, "reference_owner_cycle_window": {}, "notes_cn": "n3"},
            ]
        },
    )

    assert result.summary["unified_price_inferred_count"] == 3
    assert all(row["training_readiness"] == "unified_price_inferred_waiting_owner_calibration" for row in result.dataset_rows)
