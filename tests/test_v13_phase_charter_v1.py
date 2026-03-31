from __future__ import annotations

from a_share_quant.strategy.v13_phase_charter_v1 import V13PhaseCharterAnalyzer


def test_v13_phase_charter_opens_from_v12_waiting_state() -> None:
    v12_waiting_state_payload = {
        "summary": {
            "enter_explicit_waiting_state_now": True,
        }
    }
    catalyst_schema_payload = {
        "summary": {
            "ready_for_bounded_registry_seeding": True,
        }
    }
    catalyst_audit_payload = {
        "summary": {
            "context_separation_present": True,
        }
    }
    catalyst_phase_check_payload = {
        "summary": {
            "context_separation_present": True,
            "keep_branch_report_only": True,
        }
    }

    result = V13PhaseCharterAnalyzer().analyze(
        v12_waiting_state_payload=v12_waiting_state_payload,
        catalyst_schema_payload=catalyst_schema_payload,
        catalyst_audit_payload=catalyst_audit_payload,
        catalyst_phase_check_payload=catalyst_phase_check_payload,
    )

    assert result.summary["acceptance_posture"] == "open_v13_catalyst_and_concept_context_infrastructure"
    assert result.summary["do_open_v13_now"] is True
    assert result.summary["recommended_first_action"] == "freeze_v13_concept_mapping_inventory_v1"
