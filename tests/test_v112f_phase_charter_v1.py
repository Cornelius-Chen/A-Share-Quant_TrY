from __future__ import annotations

from a_share_quant.strategy.v112f_phase_charter_v1 import V112FPhaseCharterAnalyzer


def test_v112f_phase_charter_opens_after_v112e_closure() -> None:
    result = V112FPhaseCharterAnalyzer().analyze(
        v112e_phase_closure_payload={"summary": {"v112e_success_criteria_met": True}}
    )

    assert result.summary["do_open_v112f_now"] is True
    assert result.summary["ready_for_refinement_design_next"] is True
