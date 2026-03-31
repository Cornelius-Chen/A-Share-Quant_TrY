from __future__ import annotations

from a_share_quant.strategy.v14_phase_closure_check_v1 import V14PhaseClosureCheckAnalyzer


def test_v14_phase_closure_check_enters_waiting_state_after_bounded_success() -> None:
    result = V14PhaseClosureCheckAnalyzer().analyze(
        phase_charter_payload={"summary": {"do_open_v14_now": True, "acceptance_posture": "open_v14_context_consumption_pilot"}},
        bounded_discrimination_payload={"summary": {"stable_discrimination_present": True, "acceptance_posture": "open_v14_bounded_discrimination_check_v1_as_report_only_review", "concept_depth_difference_present": True}},
        phase_check_payload={"summary": {"acceptance_posture": "keep_v14_active_but_bounded_as_context_consumption_pilot", "do_integrate_into_strategy_now": False, "promote_context_now": False}},
    )

    assert result.summary["acceptance_posture"] == "close_v14_as_bounded_context_consumption_success"
    assert result.summary["v14_success_criteria_met"] is True
    assert result.summary["enter_v14_waiting_state_now"] is True
