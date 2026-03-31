from __future__ import annotations

from a_share_quant.strategy.v13_phase_closure_check_v1 import (
    V13PhaseClosureCheckAnalyzer,
)


def test_v13_phase_closure_check_enters_waiting_state_after_bounded_success() -> None:
    charter_payload = {"summary": {"do_open_v13_now": True, "acceptance_posture": "open"}}
    reclass_payload = {"summary": {"acceptance_posture": "reclass", "core_confirmed_count": 2, "market_confirmed_indirect_count": 1}}
    usage_payload = {"summary": {"acceptance_posture": "rules", "bounded_context_primary_count": 2, "strategy_integration_allowed_count": 0}}

    result = V13PhaseClosureCheckAnalyzer().analyze(
        phase_charter_payload=charter_payload,
        concept_registry_reclassification_payload=reclass_payload,
        concept_registry_usage_rules_payload=usage_payload,
    )

    assert result.summary["acceptance_posture"] == "close_v13_as_bounded_context_infrastructure_success"
    assert result.summary["v13_success_criteria_met"] is True
    assert result.summary["enter_v13_waiting_state_now"] is True
