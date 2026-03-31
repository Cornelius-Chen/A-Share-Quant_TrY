from __future__ import annotations

from a_share_quant.strategy.v13_phase_check_v1 import V13PhaseCheckAnalyzer


def test_v13_phase_check_keeps_branch_active_but_bounded() -> None:
    phase_charter_payload = {
        "summary": {
            "acceptance_posture": "open_v13_catalyst_and_concept_context_infrastructure",
            "do_open_v13_now": True,
            "recommended_first_action": "freeze_v13_concept_mapping_inventory_v1",
        }
    }
    concept_inventory_payload = {
        "summary": {
            "acceptance_posture": "freeze_v13_concept_mapping_inventory_v1",
            "requires_point_in_time_mapping": True,
            "requires_market_confirmation_layer": True,
        }
    }
    concept_audit_payload = {
        "summary": {
            "acceptance_posture": "open_v13_concept_context_audit_v1_as_bounded_report_only_check",
            "concept_context_separation_present": True,
            "promote_concept_branch_now": False,
        }
    }

    result = V13PhaseCheckAnalyzer().analyze(
        phase_charter_payload=phase_charter_payload,
        concept_inventory_payload=concept_inventory_payload,
        concept_audit_payload=concept_audit_payload,
    )

    assert result.summary["acceptance_posture"] == "keep_v13_active_but_bounded_as_context_infrastructure"
    assert result.summary["do_expand_v13_widely_now"] is False
    assert result.summary["do_integrate_into_strategy_now"] is False
