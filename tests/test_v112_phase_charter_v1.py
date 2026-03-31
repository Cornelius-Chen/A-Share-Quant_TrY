from __future__ import annotations

from a_share_quant.strategy.v112_phase_charter_v1 import V112PhaseCharterAnalyzer


def test_v112_phase_charter_opens_after_v111a_waiting_state() -> None:
    result = V112PhaseCharterAnalyzer().analyze(
        v111a_phase_closure_payload={"summary": {"enter_v111a_waiting_state_now": True}},
        owner_phase_switch_approved=True,
    )

    assert result.summary["acceptance_posture"] == "open_v112_single_price_cycle_experimental_training_pilot"
    assert result.summary["do_open_v112_now"] is True
