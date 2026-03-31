from __future__ import annotations

from a_share_quant.strategy.v113f_label_review_sheet_v1 import V113FLabelReviewSheetAnalyzer


def test_v113f_label_review_sheet_exposes_owner_correction_fields() -> None:
    result = V113FLabelReviewSheetAnalyzer().analyze(
        pilot_object_pool_payload={
            "summary": {"ready_for_label_review_sheet_next": True},
            "object_rows": [
                {
                    "symbol": "002085",
                    "name": "万丰奥威",
                    "pool_role_guess": "leader",
                    "role_guess_reason": "dense seed",
                    "first_seen_in_local_mapping": "2024-01-02",
                    "last_seen_in_local_mapping": "2024-12-31",
                }
            ],
        },
        pilot_protocol_payload={
            "labeling_protocol": {
                "label_blocks": {
                    "state_label": [],
                    "role_label": [],
                    "strength_labels": [],
                    "driver_presence_review_flags": [],
                }
            }
        },
    )

    assert result.summary["review_row_count"] == 1
    assert result.review_rows[0]["role_correction_status"] == "owner_review_needed"
