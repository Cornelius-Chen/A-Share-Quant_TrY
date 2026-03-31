from __future__ import annotations

from a_share_quant.strategy.v13_concept_mapping_confidence_v1 import (
    V13ConceptMappingConfidenceAnalyzer,
)


def test_v13_concept_mapping_confidence_freezes_rules() -> None:
    phase_check_payload = {
        "summary": {
            "acceptance_posture": "keep_v13_active_but_bounded_as_context_infrastructure",
        }
    }
    concept_inventory_payload = {
        "summary": {
            "requires_point_in_time_mapping": True,
        }
    }
    concept_source_fill_payload = {
        "summary": {
            "row_count": 4,
        }
    }

    result = V13ConceptMappingConfidenceAnalyzer().analyze(
        phase_check_payload=phase_check_payload,
        concept_inventory_payload=concept_inventory_payload,
        concept_source_fill_payload=concept_source_fill_payload,
    )

    assert result.summary["acceptance_posture"] == "freeze_v13_concept_mapping_confidence_and_symbol_link_rules_v1"
    assert result.summary["symbol_link_mode_count"] == 6
    assert result.summary["requires_market_confirmation_for_tradable_context"] is True
    assert result.summary["ready_for_bounded_concept_registry_next"] is True
