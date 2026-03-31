from __future__ import annotations

from a_share_quant.strategy.v111_phase_closure_check_v1 import V111PhaseClosureCheckAnalyzer


def test_v111_phase_closure_check_enters_waiting_state_after_design_success() -> None:
    result = V111PhaseClosureCheckAnalyzer().analyze(
        phase_charter_payload={"summary": {"do_open_v111_now": True}},
        infrastructure_plan_payload={
            "summary": {
                "acquisition_scope_count": 4,
                "family_novelty_rule_count": 4,
                "ready_for_bounded_first_pilot_next": True,
            }
        },
        phase_check_payload={
            "summary": {
                "allow_strategy_integration_now": False,
            }
        },
    )

    assert result.summary["acceptance_posture"] == "close_v111_as_sustained_acquisition_infrastructure_success"
    assert result.summary["enter_v111_waiting_state_now"] is True
