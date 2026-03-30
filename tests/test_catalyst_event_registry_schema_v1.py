from __future__ import annotations

from a_share_quant.strategy.catalyst_event_registry_schema_v1 import (
    CatalystEventRegistrySchemaAnalyzer,
)


def test_catalyst_event_registry_schema_v1_freezes_authority_and_shape_fields() -> None:
    result = CatalystEventRegistrySchemaAnalyzer().analyze()

    assert result.summary["schema_posture"] == "freeze_catalyst_event_registry_schema_v1"
    assert result.summary["ready_for_bounded_registry_seeding"] is True
    assert result.summary["contains_source_authority_tier"] is True
    assert result.summary["contains_execution_strength"] is True
    assert result.summary["contains_rumor_risk_level"] is True
    assert result.summary["contains_consolidation_days_after_pulse"] is True
    assert result.summary["contains_reacceleration_present"] is True
    assert result.summary["total_field_count"] >= 20
