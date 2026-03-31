from __future__ import annotations

from a_share_quant.strategy.v13_concept_mapping_inventory_v1 import (
    V13ConceptMappingInventoryAnalyzer,
)


def test_v13_concept_mapping_inventory_freezes_first_inventory() -> None:
    phase_charter_payload = {
        "summary": {
            "do_open_v13_now": True,
        }
    }
    catalyst_schema_payload = {
        "summary": {
            "contains_source_authority_tier": True,
        }
    }
    catalyst_fill_payload = {
        "summary": {
            "market_context_filled_count": 6,
        }
    }

    result = V13ConceptMappingInventoryAnalyzer().analyze(
        phase_charter_payload=phase_charter_payload,
        catalyst_schema_payload=catalyst_schema_payload,
        catalyst_fill_payload=catalyst_fill_payload,
    )

    assert result.summary["acceptance_posture"] == "freeze_v13_concept_mapping_inventory_v1"
    assert result.summary["requires_point_in_time_mapping"] is True
    assert result.summary["requires_market_confirmation_layer"] is True
    assert result.summary["ready_for_bounded_concept_seed_next"] is True
