from __future__ import annotations

from a_share_quant.strategy.v14_phase_charter_v1 import V14PhaseCharterAnalyzer


def test_v14_phase_charter_opens_after_v13_infrastructure_closure() -> None:
    result = V14PhaseCharterAnalyzer().analyze(
        v13_phase_closure_payload={"summary": {"enter_v13_waiting_state_now": True}},
        concept_usage_rules_payload={"summary": {"row_count": 4, "strategy_integration_allowed_count": 0}},
        catalyst_context_audit_payload={"summary": {"context_separation_present": True, "keep_branch_report_only": True}},
    )

    assert result.summary["acceptance_posture"] == "open_v14_context_consumption_pilot"
    assert result.summary["do_open_v14_now"] is True
    assert result.summary["recommended_first_action"] == "freeze_v14_context_consumption_protocol_v1"
