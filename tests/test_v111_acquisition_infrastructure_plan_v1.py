from __future__ import annotations

from a_share_quant.strategy.v111_acquisition_infrastructure_plan_v1 import (
    V111AcquisitionInfrastructurePlanAnalyzer,
)


def test_v111_acquisition_infrastructure_plan_freezes_reusable_upstream_rules() -> None:
    result = V111AcquisitionInfrastructurePlanAnalyzer().analyze(
        phase_charter_payload={"summary": {"do_open_v111_now": True}}
    )

    assert result.summary["acceptance_posture"] == "freeze_v111_acquisition_infrastructure_plan_v1"
    assert result.summary["acquisition_scope_count"] >= 4
    assert result.summary["ready_for_bounded_first_pilot_next"] is True
