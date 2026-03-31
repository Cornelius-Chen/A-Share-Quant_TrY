from __future__ import annotations

from a_share_quant.strategy.v112d_phase_closure_check_v1 import (
    V112DPhaseClosureCheckAnalyzer,
)


def test_v112d_phase_closure_blocks_auto_deployment() -> None:
    result = V112DPhaseClosureCheckAnalyzer().analyze(
        phase_check_payload={"summary": {"sidecar_pilot_present": True, "allow_sidecar_deployment_now": False, "ready_for_phase_closure_next": True}}
    )

    assert result.summary["v112d_success_criteria_met"] is True
    assert result.summary["allow_auto_sidecar_deployment_now"] is False
