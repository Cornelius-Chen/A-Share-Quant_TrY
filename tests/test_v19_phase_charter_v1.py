from __future__ import annotations

from a_share_quant.strategy.v19_phase_charter_v1 import V19PhaseCharterAnalyzer


def test_v19_phase_charter_opens_after_v18c_waiting_state_with_breadth_evidence() -> None:
    result = V19PhaseCharterAnalyzer().analyze(
        v18c_phase_closure_payload={"summary": {"enter_v18c_waiting_state_now": True}},
        v18c_screened_collection_payload={
            "collection_rows": [
                {"feature_name": "single_pulse_support", "admission_status": "admit"},
                {"feature_name": "policy_followthrough_support", "admission_status": "admit"},
            ]
        },
    )

    assert result.summary["acceptance_posture"] == "open_v19_breadth_evidence_rereview"
    assert result.summary["do_open_v19_now"] is True
    assert result.summary["breadth_target_feature_count"] == 2
    assert result.summary["recommended_first_action"] == "freeze_v19_breadth_rereview_protocol_v1"
