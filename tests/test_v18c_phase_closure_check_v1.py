from __future__ import annotations

from a_share_quant.strategy.v18c_phase_closure_check_v1 import V18CPhaseClosureCheckAnalyzer


def test_v18c_phase_closure_check_enters_waiting_state_after_bounded_collection_success() -> None:
    result = V18CPhaseClosureCheckAnalyzer().analyze(
        phase_charter_payload={
            "summary": {
                "do_open_v18c_now": True,
                "acceptance_posture": "open_v18c_screened_bounded_collection",
            }
        },
        screened_collection_payload={
            "summary": {
                "admitted_case_count": 3,
                "targets_with_admitted_cases_count": 2,
                "sample_limit_breaches": 0,
            }
        },
        phase_check_payload={
            "summary": {
                "acceptance_posture": "keep_v18c_active_but_bounded_as_screened_collection",
                "promote_retained_now": False,
                "do_integrate_into_strategy_now": False,
            }
        },
    )

    assert result.summary["acceptance_posture"] == "close_v18c_as_bounded_screened_collection_success"
    assert result.summary["v18c_success_criteria_met"] is True
    assert result.summary["enter_v18c_waiting_state_now"] is True
