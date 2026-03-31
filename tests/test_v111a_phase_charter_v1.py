from __future__ import annotations

from a_share_quant.strategy.v111a_phase_charter_v1 import V111APhaseCharterAnalyzer


def test_v111a_phase_charter_opens_owner_reviewed_first_pilot() -> None:
    result = V111APhaseCharterAnalyzer().analyze(
        v111_phase_closure_payload={"summary": {"ready_for_bounded_first_pilot_next": True}},
        owner_phase_switch_approved=True,
    )

    assert result.summary["acceptance_posture"] == "open_v111a_bounded_first_catalyst_acquisition_pilot"
    assert result.summary["do_open_v111a_now"] is True
    assert result.charter["owner_reviewed_exception_phase"] is True
