from __future__ import annotations

from a_share_quant.strategy.v18a_phase_charter_v1 import V18APhaseCharterAnalyzer


def test_v18a_phase_charter_opens_after_v17_waiting_state_with_sample_breadth_targets() -> None:
    result = V18APhaseCharterAnalyzer().analyze(
        v17_phase_closure_payload={"summary": {"enter_v17_waiting_state_now": True}},
        v17_feature_promotion_gap_review_payload={
            "review_rows": [
                {"feature_name": "single_pulse_support", "primary_shortfall": "sample_breadth_gap"},
                {"feature_name": "policy_followthrough_support", "primary_shortfall": "sample_breadth_gap"},
            ]
        },
    )

    assert result.summary["acceptance_posture"] == "open_v18a_sample_breadth_expansion"
    assert result.summary["do_open_v18a_now"] is True
    assert result.summary["sample_breadth_target_feature_count"] == 2
    assert result.summary["recommended_first_action"] == "freeze_v18a_sample_breadth_protocol_v1"
