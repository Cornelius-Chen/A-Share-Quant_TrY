from __future__ import annotations

from a_share_quant.strategy.v19_breadth_rereview_protocol_v1 import (
    V19BreadthRereviewProtocolAnalyzer,
)


def test_v19_breadth_rereview_protocol_freezes_targets() -> None:
    result = V19BreadthRereviewProtocolAnalyzer().analyze(
        v19_phase_charter_payload={
            "summary": {
                "do_open_v19_now": True,
                "target_feature_names": ["single_pulse_support", "policy_followthrough_support"],
            }
        },
        v17_feature_promotion_gap_review_payload={
            "review_rows": [
                {"feature_name": "single_pulse_support", "primary_shortfall": "sample_breadth_gap"},
                {"feature_name": "policy_followthrough_support", "primary_shortfall": "sample_breadth_gap"},
            ]
        },
        v18c_screened_collection_payload={
            "collection_rows": [
                {"feature_name": "single_pulse_support", "admission_status": "admit"},
                {"feature_name": "policy_followthrough_support", "admission_status": "admit"},
            ]
        },
    )

    assert result.summary["acceptance_posture"] == "freeze_v19_breadth_rereview_protocol_v1"
    assert result.summary["target_feature_count"] == 2
    assert result.summary["ready_for_per_feature_breadth_rereview_next"] is True
