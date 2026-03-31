from __future__ import annotations

from a_share_quant.strategy.v112o_phase_charter_v1 import V112OPhaseCharterAnalyzer


def test_v112o_phase_charter_opens_after_v112n_waiting_state() -> None:
    result = V112OPhaseCharterAnalyzer().analyze(
        v112n_phase_closure_payload={"summary": {"enter_v112n_waiting_state_now": True}},
        owner_reprioritizes_to_cpo=True,
    )

    assert result.summary["do_open_v112o_now"] is True
    assert result.summary["selected_archetype"] == "optical_link_price_and_demand_upcycle"
