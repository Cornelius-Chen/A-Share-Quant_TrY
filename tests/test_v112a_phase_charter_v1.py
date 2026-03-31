from __future__ import annotations

from a_share_quant.strategy.v112a_phase_charter_v1 import V112APhaseCharterAnalyzer


def test_v112a_phase_charter_opens_after_v112_waiting_state() -> None:
    result = V112APhaseCharterAnalyzer().analyze(
        v112_phase_closure_payload={"summary": {"enter_v112_waiting_state_now": True}},
        owner_phase_switch_approved=True,
    )

    assert result.summary["acceptance_posture"] == "open_v112a_bounded_pilot_data_assembly"
    assert result.summary["do_open_v112a_now"] is True
