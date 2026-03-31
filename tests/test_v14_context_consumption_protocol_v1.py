from __future__ import annotations

from a_share_quant.strategy.v14_context_consumption_protocol_v1 import (
    V14ContextConsumptionProtocolAnalyzer,
)


def test_v14_context_consumption_protocol_stays_report_only() -> None:
    result = V14ContextConsumptionProtocolAnalyzer().analyze(
        v14_phase_charter_payload={"summary": {"do_open_v14_now": True}},
        concept_usage_rules_payload={"summary": {"row_count": 4}},
        catalyst_context_audit_payload={"summary": {"context_separation_present": True}},
    )

    assert result.summary["acceptance_posture"] == "freeze_v14_context_consumption_protocol_v1"
    assert result.summary["allow_strategy_integration_now"] is False
    assert result.summary["ready_for_bounded_context_feature_schema_next"] is True
