from __future__ import annotations

from a_share_quant.strategy.v112_phase_closure_check_v1 import (
    V112PhaseClosureCheckAnalyzer,
)


def test_v112_phase_closure_check_closes_after_definition_success() -> None:
    result = V112PhaseClosureCheckAnalyzer().analyze(
        phase_charter_payload={"summary": {"do_open_v112_now": True}},
        phase_check_payload={
            "summary": {
                "ready_for_bounded_pilot_data_assembly_next": True,
                "allow_strategy_integration_now": False,
                "allow_black_box_deployment_now": False,
            }
        },
    )

    assert result.summary["v112_success_criteria_met"] is True
    assert result.summary["enter_v112_waiting_state_now"] is True
    assert result.summary["allow_auto_training_now"] is False
