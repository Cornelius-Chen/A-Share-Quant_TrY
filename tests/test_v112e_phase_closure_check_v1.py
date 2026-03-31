from __future__ import annotations

from a_share_quant.strategy.v112e_phase_closure_check_v1 import (
    V112EPhaseClosureCheckAnalyzer,
)


def test_v112e_phase_closure_blocks_auto_escalation() -> None:
    result = V112EPhaseClosureCheckAnalyzer().analyze(
        phase_check_payload={"summary": {"attribution_review_present": True, "allow_model_deployment_now": False, "ready_for_phase_closure_next": True}}
    )

    assert result.summary["v112e_success_criteria_met"] is True
    assert result.summary["allow_auto_model_escalation_now"] is False
