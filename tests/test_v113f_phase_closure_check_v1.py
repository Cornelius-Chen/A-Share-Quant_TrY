from __future__ import annotations

from a_share_quant.strategy.v113f_phase_closure_check_v1 import V113FPhaseClosureCheckAnalyzer


def test_v113f_phase_closure_enters_waiting_state_after_review_sheet_exists() -> None:
    result = V113FPhaseClosureCheckAnalyzer().analyze(
        phase_charter_payload={"summary": {"do_open_v113f_now": True, "selected_archetype": "commercial_space_mainline"}},
        phase_check_payload={"summary": {"ready_for_owner_correction_next": True, "allow_training_now": False}},
    )

    assert result.summary["v113f_success_criteria_met"] is True
    assert result.summary["enter_v113f_waiting_state_now"] is True
