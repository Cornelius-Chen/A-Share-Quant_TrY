from __future__ import annotations

from a_share_quant.strategy.v112a_label_review_sheet_v1 import V112ALabelReviewSheetAnalyzer


def test_v112a_label_review_sheet_exposes_owner_correction_fields() -> None:
    result = V112ALabelReviewSheetAnalyzer().analyze(
        pilot_object_pool_payload={
            "summary": {"ready_for_label_review_sheet_next": True},
            "object_rows": [
                {
                    "symbol": "300502",
                    "name": "新易盛",
                    "pool_role_guess": "core_beta_beneficiary",
                }
            ],
        },
        training_protocol_payload={
            "protocol": {
                "feature_blocks": {
                    "catalyst_state": [],
                    "earnings_transmission_bridge": [],
                }
            }
        },
    )

    assert result.summary["review_row_count"] == 1
    assert result.summary["owner_review_required_count"] == 1
