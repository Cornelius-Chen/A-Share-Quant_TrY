from __future__ import annotations

from a_share_quant.strategy.v112p_phase_charter_v1 import V112PPhaseCharterAnalyzer


def test_v112p_phase_charter_opens_after_v112o_waiting_state() -> None:
    result = V112PPhaseCharterAnalyzer().analyze(
        v112o_phase_closure_payload={"summary": {"enter_v112o_waiting_state_now": True}},
        owner_requests_full_information_map=True,
    )

    assert result.summary["do_open_v112p_now"] is True
    assert result.summary["selected_archetype"] == "optical_link_price_and_demand_upcycle"
