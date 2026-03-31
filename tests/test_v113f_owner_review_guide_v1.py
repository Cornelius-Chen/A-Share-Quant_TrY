from __future__ import annotations

from a_share_quant.strategy.v113f_owner_review_guide_v1 import V113FOwnerReviewGuideAnalyzer


def test_v113f_owner_review_guide_translates_role_and_evidence() -> None:
    result = V113FOwnerReviewGuideAnalyzer().analyze(
        pilot_object_pool_payload={
            "object_rows": [
                {
                    "symbol": "002085",
                    "name": "bad",
                    "pool_role_guess": "leader",
                    "local_evidence_status": "dense_local_commercial_space_mapping",
                    "role_guess_reason": "clean seed",
                }
            ]
        },
        review_sheet_payload={
            "review_rows": [
                {"symbol": "002085", "cycle_window_start_guess": "2024-01-02", "cycle_window_end_guess": "2024-12-31"}
            ]
        },
    )

    assert result.summary["guide_row_count"] == 1
    assert result.guide_rows[0]["display_name"] == "万丰奥威"
    assert result.guide_rows[0]["current_role_guess_cn"] == "龙头"
