from __future__ import annotations

from a_share_quant.strategy.v112a_phase_closure_check_v1 import V112APhaseClosureCheckAnalyzer


def test_v112a_phase_closure_check_closes_after_review_sheet_exists() -> None:
    result = V112APhaseClosureCheckAnalyzer().analyze(
        phase_charter_payload={"summary": {"do_open_v112a_now": True}},
        phase_check_payload={"summary": {"ready_for_owner_correction_next": True, "allow_training_now": False}},
    )

    assert result.summary["v112a_success_criteria_met"] is True
    assert result.summary["enter_v112a_waiting_state_now"] is True
