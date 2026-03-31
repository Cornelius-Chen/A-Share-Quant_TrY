from __future__ import annotations

from a_share_quant.strategy.v13_concept_registry_reclassification_v1 import (
    V13ConceptRegistryReclassificationAnalyzer,
)


def test_v13_concept_registry_reclassification_applies_assignment_rows() -> None:
    registry_payload = {
        "registry_rows": [
            {"lane_id": "a", "symbol": "000001", "final_mapping_class": "provisional_market_confirmed_indirect"},
            {"lane_id": "b", "symbol": "000002", "final_mapping_class": "provisional_market_confirmed_indirect"},
        ]
    }
    assignment_payload = {
        "assignment_rows": [
            {"lane_id": "a", "final_mapping_class": "core_confirmed", "allowed_for_bounded_context": True},
            {"lane_id": "b", "final_mapping_class": "market_confirmed_indirect", "allowed_for_bounded_context": True},
        ]
    }

    result = V13ConceptRegistryReclassificationAnalyzer().analyze(
        concept_registry_payload=registry_payload,
        link_mode_assignment_payload=assignment_payload,
    )

    assert (
        result.summary["acceptance_posture"]
        == "open_v13_concept_registry_reclassification_v1_as_bounded_reclassified_registry"
    )
    assert result.summary["core_confirmed_count"] == 1
    assert result.summary["market_confirmed_indirect_count"] == 1
    assert result.summary["provisional_row_count"] == 0
