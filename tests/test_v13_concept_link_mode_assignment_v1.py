from __future__ import annotations

from a_share_quant.strategy.v13_concept_link_mode_assignment_v1 import (
    V13ConceptLinkModeAssignmentAnalyzer,
)


def test_v13_concept_link_mode_assignment_upgrades_rows_by_link_mode() -> None:
    registry_payload = {
        "registry_rows": [
            {
                "lane_id": "a",
                "symbol": "002049",
                "final_mapping_class": "provisional_market_confirmed_indirect",
                "allowed_for_bounded_context": True,
            },
            {
                "lane_id": "b",
                "symbol": "300750",
                "final_mapping_class": "provisional_market_confirmed_indirect",
                "allowed_for_bounded_context": True,
            },
        ]
    }
    assignments = [
        {
            "lane_id": "a",
            "symbol_link_mode": "platform_or_ecosystem",
            "assignment_basis": "indirect",
            "assignment_source_ref": "ref_a",
            "assignment_notes": "",
        },
        {
            "lane_id": "b",
            "symbol_link_mode": "primary_business",
            "assignment_basis": "direct",
            "assignment_source_ref": "ref_b",
            "assignment_notes": "",
        },
    ]

    result = V13ConceptLinkModeAssignmentAnalyzer().analyze(
        registry_payload=registry_payload,
        assignments=assignments,
    )

    assert result.summary["acceptance_posture"] == "open_v13_concept_link_mode_assignment_v1_as_bounded_manual_assignment"
    assert result.summary["core_confirmed_count"] == 1
    assert result.summary["market_confirmed_indirect_count"] == 1
    assert result.summary["pending_manual_assignment_count"] == 0
