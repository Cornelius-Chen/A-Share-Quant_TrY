from __future__ import annotations

from a_share_quant.strategy.v112c_phase_closure_check_v1 import (
    V112CPhaseClosureCheckAnalyzer,
)


def test_v112c_phase_closure_blocks_auto_sidecar_run() -> None:
    result = V112CPhaseClosureCheckAnalyzer().analyze(
        phase_check_payload={
            "summary": {
                "hotspot_review_present": True,
                "sidecar_protocol_present": True,
                "allow_sidecar_deployment_now": False,
                "ready_for_phase_closure_next": True,
            }
        }
    )

    assert result.summary["v112c_success_criteria_met"] is True
    assert result.summary["allow_auto_sidecar_run_now"] is False
