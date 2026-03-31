from __future__ import annotations

from a_share_quant.strategy.v14_bounded_discrimination_check_v1 import (
    V14BoundedDiscriminationCheckAnalyzer,
)


def test_v14_bounded_discrimination_check_confirms_directional_separation() -> None:
    result = V14BoundedDiscriminationCheckAnalyzer().analyze(
        context_feature_schema_payload={"summary": {"ready_for_bounded_discrimination_check_next": True}},
        concept_usage_rules_payload={
            "usage_rows": [
                {"lane_outcome_label": "opening_led", "usage_mode": "bounded_context_secondary"},
                {"lane_outcome_label": "persistence_led", "usage_mode": "bounded_context_primary"},
                {"lane_outcome_label": "carry_row_present", "usage_mode": "bounded_context_primary"},
            ]
        },
        catalyst_context_audit_payload={
            "audit_rows": [
                {"lane_outcome_label": "opening_led", "persistence_classes": ["single_pulse"]},
                {"lane_outcome_label": "persistence_led", "persistence_classes": ["multi_day_reinforcement"]},
                {"lane_outcome_label": "carry_row_present", "persistence_classes": ["policy_followthrough"]},
            ]
        },
    )

    assert result.summary["acceptance_posture"] == "open_v14_bounded_discrimination_check_v1_as_report_only_review"
    assert result.summary["stable_discrimination_present"] is True
    assert result.summary["promote_context_now"] is False
    assert result.summary["ready_for_v14_phase_check_next"] is True
