from __future__ import annotations

from a_share_quant.strategy.v18b_phase_charter_v1 import V18BPhaseCharterAnalyzer


def test_v18b_phase_charter_opens_after_v18a_waiting_state_with_entry_rows() -> None:
    result = V18BPhaseCharterAnalyzer().analyze(
        v18a_phase_closure_payload={"summary": {"enter_v18a_waiting_state_now": True}},
        v18a_breadth_entry_design_payload={
            "summary": {"entry_row_count": 2},
            "entry_rows": [
                {"feature_name": "single_pulse_support"},
                {"feature_name": "policy_followthrough_support"},
            ],
        },
    )

    assert result.summary["acceptance_posture"] == "open_v18b_breadth_sample_admission_gate"
    assert result.summary["do_open_v18b_now"] is True
    assert result.summary["breadth_entry_row_count"] == 2
    assert result.summary["recommended_first_action"] == "freeze_v18b_sample_admission_protocol_v1"
