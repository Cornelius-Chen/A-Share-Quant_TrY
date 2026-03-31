from __future__ import annotations

from a_share_quant.strategy.v18b_feature_admission_gate_review_v1 import (
    V18BFeatureAdmissionGateReviewAnalyzer,
)


def test_v18b_feature_admission_gate_review_keeps_collection_closed() -> None:
    result = V18BFeatureAdmissionGateReviewAnalyzer().analyze(
        sample_admission_protocol_payload={
            "summary": {"ready_for_per_feature_admission_gate_review_next": True},
            "protocol": {
                "target_feature_rows": [
                    {
                        "feature_name": "single_pulse_support",
                        "candidate_source_pool": "closed_opening_led_lanes_with_context_rows",
                    }
                ]
            },
        },
        breadth_entry_design_payload={
            "entry_rows": [
                {
                    "feature_name": "single_pulse_support",
                    "candidate_source_pool": "closed_opening_led_lanes_with_context_rows",
                    "sample_limit": 3,
                }
            ]
        },
    )

    assert result.summary["acceptance_posture"] == "open_v18b_feature_admission_gate_review_v1_as_bounded_review"
    assert result.summary["reviewed_feature_count"] == 1
    assert result.summary["admission_gate_ready_count"] == 1
    assert result.summary["allow_sample_collection_now"] is False
