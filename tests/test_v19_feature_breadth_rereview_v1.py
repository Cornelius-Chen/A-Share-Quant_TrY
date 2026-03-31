from __future__ import annotations

from a_share_quant.strategy.v19_feature_breadth_rereview_v1 import (
    V19FeatureBreadthRereviewAnalyzer,
)


def test_v19_feature_breadth_rereview_refreshes_shortfalls_without_promotion() -> None:
    result = V19FeatureBreadthRereviewAnalyzer().analyze(
        breadth_rereview_protocol_payload={
            "summary": {"ready_for_per_feature_breadth_rereview_next": True},
            "protocol": {
                "target_feature_rows": [
                    {
                        "feature_name": "single_pulse_support",
                        "prior_primary_shortfall": "sample_breadth_gap",
                    },
                    {
                        "feature_name": "policy_followthrough_support",
                        "prior_primary_shortfall": "sample_breadth_gap",
                    },
                ]
            },
        },
        feature_promotion_gap_review_payload={
            "review_rows": [
                {"feature_name": "single_pulse_support", "primary_shortfall": "sample_breadth_gap"},
                {"feature_name": "policy_followthrough_support", "primary_shortfall": "sample_breadth_gap"},
            ]
        },
        screened_collection_payload={
            "collection_rows": [
                {"feature_name": "single_pulse_support", "admission_status": "admit", "symbol": "002371", "lane_id": "a"},
                {"feature_name": "single_pulse_support", "admission_status": "admit", "symbol": "002049", "lane_id": "b"},
                {"feature_name": "policy_followthrough_support", "admission_status": "admit", "symbol": "300750", "lane_id": "c"},
                {"feature_name": "policy_followthrough_support", "admission_status": "admit", "symbol": "300750", "lane_id": "d"},
            ]
        },
    )

    assert result.summary["acceptance_posture"] == "open_v19_feature_breadth_rereview_v1_as_bounded_rereview"
    assert result.summary["reviewed_feature_count"] == 2
    assert result.summary["shortfall_changed_count"] == 1
    assert result.summary["promotion_ready_now_count"] == 0
