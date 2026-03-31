from __future__ import annotations

from a_share_quant.strategy.v113f_phase_charter_v1 import V113FPhaseCharterAnalyzer


def test_v113f_phase_charter_opens_after_v113e_waiting_state() -> None:
    result = V113FPhaseCharterAnalyzer().analyze(
        v113e_phase_closure_payload={"summary": {"enter_v113e_waiting_state_now": True}},
        owner_phase_switch_approved=True,
    )

    assert result.summary["do_open_v113f_now"] is True
    assert result.summary["selected_archetype"] == "commercial_space_mainline"
