from __future__ import annotations

from a_share_quant.strategy.v112g_phase_closure_check_v1 import V112GPhaseClosureCheckAnalyzer


def test_v112g_phase_closure_enters_waiting_state() -> None:
    result = V112GPhaseClosureCheckAnalyzer().analyze(
        phase_check_payload={"summary": {"ready_for_phase_closure_next": True, "feature_schema_v2_present": True, "gbdt_v2_present": True}}
    )

    assert result.summary["v112g_success_criteria_met"] is True
    assert result.summary["enter_v112g_waiting_state_now"] is True
