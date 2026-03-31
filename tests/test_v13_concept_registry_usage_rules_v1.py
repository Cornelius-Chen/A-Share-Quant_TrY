from __future__ import annotations

from a_share_quant.strategy.v13_concept_registry_usage_rules_v1 import (
    V13ConceptRegistryUsageRulesAnalyzer,
)


def test_v13_concept_registry_usage_rules_freeze_primary_and_secondary_usage() -> None:
    payload = {
        "registry_rows": [
            {"lane_id": "a", "final_mapping_class": "core_confirmed"},
            {"lane_id": "b", "final_mapping_class": "market_confirmed_indirect"},
        ]
    }

    result = V13ConceptRegistryUsageRulesAnalyzer().analyze(
        reclassified_registry_payload=payload,
    )

    assert result.summary["acceptance_posture"] == "freeze_v13_bounded_concept_registry_usage_rules_v1"
    assert result.summary["bounded_context_primary_count"] == 1
    assert result.summary["bounded_context_secondary_count"] == 1
    assert result.summary["strategy_integration_allowed_count"] == 0
