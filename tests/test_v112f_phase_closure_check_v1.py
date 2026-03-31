from __future__ import annotations

from a_share_quant.strategy.v112f_phase_closure_check_v1 import V112FPhaseClosureCheckAnalyzer


def test_v112f_phase_closure_enters_waiting_state() -> None:
    result = V112FPhaseClosureCheckAnalyzer().analyze(
        phase_check_payload={
            "summary": {
                "ready_for_phase_closure_next": True,
                "refinement_design_present": True,
                "primary_bottleneck_type": "feature_definition_or_non_redundancy_gap",
            }
        }
    )

    assert result.summary["v112f_success_criteria_met"] is True
    assert result.summary["enter_v112f_waiting_state_now"] is True
