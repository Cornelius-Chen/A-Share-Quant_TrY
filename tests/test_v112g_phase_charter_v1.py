from __future__ import annotations

from a_share_quant.strategy.v112g_phase_charter_v1 import V112GPhaseCharterAnalyzer


def test_v112g_phase_charter_opens_after_v112f_closure() -> None:
    result = V112GPhaseCharterAnalyzer().analyze(
        v112f_phase_closure_payload={"summary": {"v112f_success_criteria_met": True}}
    )

    assert result.summary["do_open_v112g_now"] is True
    assert result.summary["ready_for_feature_schema_v2_next"] is True
