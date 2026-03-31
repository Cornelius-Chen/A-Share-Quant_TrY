from __future__ import annotations

from a_share_quant.strategy.v112_pilot_cycle_selection_v1 import (
    V112PilotCycleSelectionAnalyzer,
)


def test_v112_pilot_cycle_selection_prefers_earnings_transmission_family() -> None:
    result = V112PilotCycleSelectionAnalyzer().analyze(
        phase_charter_payload={"summary": {"do_open_v112_now": True}},
    )

    assert result.summary["selected_primary_family"] == "earnings_transmission_carry"
    assert result.summary["selected_pilot_cycle"] == "optical_link_price_and_demand_upcycle"
    assert result.summary["ready_for_training_protocol_next"] is True
