from __future__ import annotations

from a_share_quant.strategy.v18b_sample_admission_protocol_v1 import (
    V18BSampleAdmissionProtocolAnalyzer,
)


def test_v18b_sample_admission_protocol_freezes_target_features() -> None:
    result = V18BSampleAdmissionProtocolAnalyzer().analyze(
        v18b_phase_charter_payload={
            "summary": {
                "do_open_v18b_now": True,
                "target_feature_names": ["single_pulse_support", "policy_followthrough_support"],
            }
        },
        v18a_breadth_entry_design_payload={
            "entry_rows": [
                {
                    "feature_name": "single_pulse_support",
                    "candidate_source_pool": "closed_opening_led_lanes_with_context_rows",
                    "sample_limit": 3,
                },
                {
                    "feature_name": "policy_followthrough_support",
                    "candidate_source_pool": "closed_followthrough_like_lanes_with_policy_or_industry_context",
                    "sample_limit": 3,
                },
            ]
        },
    )

    assert result.summary["acceptance_posture"] == "freeze_v18b_sample_admission_protocol_v1"
    assert result.summary["target_feature_count"] == 2
    assert result.summary["allow_sample_collection_now"] is False
    assert result.summary["ready_for_per_feature_admission_gate_review_next"] is True
