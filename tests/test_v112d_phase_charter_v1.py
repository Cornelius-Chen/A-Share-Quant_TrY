from __future__ import annotations

from a_share_quant.strategy.v112d_phase_charter_v1 import V112DPhaseCharterAnalyzer


def test_v112d_phase_charter_opens_after_v112c_closure() -> None:
    result = V112DPhaseCharterAnalyzer().analyze(
        v112c_phase_closure_payload={"summary": {"v112c_success_criteria_met": True}}
    )

    assert result.summary["do_open_v112d_now"] is True
    assert result.summary["ready_for_sidecar_pilot_next"] is True
