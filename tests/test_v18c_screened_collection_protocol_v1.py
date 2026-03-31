from __future__ import annotations

from a_share_quant.strategy.v18c_screened_collection_protocol_v1 import (
    V18CScreenedCollectionProtocolAnalyzer,
)


def test_v18c_screened_collection_protocol_freezes_ready_targets() -> None:
    result = V18CScreenedCollectionProtocolAnalyzer().analyze(
        v18c_phase_charter_payload={
            "summary": {"do_open_v18c_now": True}
        },
        v18a_breadth_entry_design_payload={
            "entry_rows": [
                {
                    "feature_name": "single_pulse_support",
                    "candidate_source_pool": "closed_opening_led_lanes_with_context_rows",
                    "sample_limit": 3,
                    "breadth_entry_mode": "bounded_additional_opening_cases",
                },
                {
                    "feature_name": "policy_followthrough_support",
                    "candidate_source_pool": "closed_followthrough_like_lanes_with_policy_or_industry_context",
                    "sample_limit": 3,
                    "breadth_entry_mode": "bounded_additional_followthrough_cases",
                },
            ]
        },
        v18b_feature_admission_gate_review_payload={
            "review_rows": [
                {"feature_name": "single_pulse_support", "admission_gate_ready": True},
                {"feature_name": "policy_followthrough_support", "admission_gate_ready": True},
            ]
        },
    )

    assert result.summary["acceptance_posture"] == "freeze_v18c_screened_collection_protocol_v1"
    assert result.summary["target_feature_count"] == 2
    assert result.summary["ready_for_screened_collection_next"] is True
