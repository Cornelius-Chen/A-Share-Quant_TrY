from __future__ import annotations

from a_share_quant.strategy.v18c_phase_charter_v1 import V18CPhaseCharterAnalyzer


def test_v18c_phase_charter_opens_after_v18b_waiting_state_with_ready_gates() -> None:
    result = V18CPhaseCharterAnalyzer().analyze(
        v18b_phase_closure_payload={"summary": {"enter_v18b_waiting_state_now": True}},
        v18b_feature_admission_gate_review_payload={
            "summary": {"admission_gate_ready_count": 2},
            "review_rows": [
                {"feature_name": "single_pulse_support", "admission_gate_ready": True},
                {"feature_name": "policy_followthrough_support", "admission_gate_ready": True},
            ],
        },
    )

    assert result.summary["acceptance_posture"] == "open_v18c_screened_bounded_collection"
    assert result.summary["do_open_v18c_now"] is True
    assert result.summary["admission_gate_ready_count"] == 2
    assert result.summary["recommended_first_action"] == "freeze_v18c_screened_collection_protocol_v1"
