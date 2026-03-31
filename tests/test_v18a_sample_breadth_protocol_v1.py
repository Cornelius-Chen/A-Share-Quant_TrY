from __future__ import annotations

from a_share_quant.strategy.v18a_sample_breadth_protocol_v1 import (
    V18ASampleBreadthProtocolAnalyzer,
)


def test_v18a_sample_breadth_protocol_freezes_target_features() -> None:
    result = V18ASampleBreadthProtocolAnalyzer().analyze(
        v18a_phase_charter_payload={
            "summary": {
                "do_open_v18a_now": True,
                "target_feature_names": ["single_pulse_support", "policy_followthrough_support"],
            }
        },
        v17_feature_promotion_gap_review_payload={
            "review_rows": [
                {
                    "feature_name": "single_pulse_support",
                    "primary_shortfall": "sample_breadth_gap",
                    "minimum_evidence_path": "bounded_multi_sample_review",
                },
                {
                    "feature_name": "policy_followthrough_support",
                    "primary_shortfall": "sample_breadth_gap",
                    "minimum_evidence_path": "bounded_additional_followthrough_case_review",
                },
            ]
        },
    )

    assert result.summary["acceptance_posture"] == "freeze_v18a_sample_breadth_protocol_v1"
    assert result.summary["target_feature_count"] == 2
    assert result.summary["allowed_evidence_sample_type_count"] == 2
    assert result.summary["ready_for_breadth_entry_design_next"] is True
