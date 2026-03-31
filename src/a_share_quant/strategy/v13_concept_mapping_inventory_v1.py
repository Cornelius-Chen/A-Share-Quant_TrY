from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V13ConceptMappingInventoryReport:
    summary: dict[str, Any]
    inventory_sections: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "inventory_sections": self.inventory_sections,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V13ConceptMappingInventoryAnalyzer:
    """Freeze the first bounded concept-mapping framework for V1.3."""

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        catalyst_schema_payload: dict[str, Any],
        catalyst_fill_payload: dict[str, Any],
    ) -> V13ConceptMappingInventoryReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        schema_summary = dict(catalyst_schema_payload.get("summary", {}))
        fill_summary = dict(catalyst_fill_payload.get("summary", {}))

        ready_now = bool(charter_summary.get("do_open_v13_now")) and bool(
            schema_summary.get("contains_source_authority_tier")
        )

        inventory_sections = [
            {
                "section_name": "mapping_mode",
                "field_count": 6,
                "fields": [
                    "primary_business",
                    "investment_holding",
                    "supply_chain",
                    "order_or_customer",
                    "platform_or_ecosystem",
                    "rumor_only",
                ],
                "reading": "Concept stock mapping must separate business truth from looser market-facing associations.",
            },
            {
                "section_name": "source_quality",
                "field_count": 4,
                "fields": [
                    "official_announcement",
                    "company_confirmation",
                    "high_trust_market_source",
                    "weak_market_rumor",
                ],
                "reading": "Concept mappings need explicit source-quality tags so rumor-like mappings never get treated like confirmed ones.",
            },
            {
                "section_name": "market_confirmation",
                "field_count": 5,
                "fields": [
                    "board_breadth_confirmed",
                    "leader_confirmed",
                    "turnover_confirmed",
                    "followthrough_days",
                    "reacceleration_present",
                ],
                "reading": "A concept mapping only becomes research-relevant when the market actually confirms it as a live board or theme trade.",
            },
            {
                "section_name": "point_in_time_rules",
                "field_count": 4,
                "fields": [
                    "mapping_start_date",
                    "mapping_end_date",
                    "mapping_confidence",
                    "concept_scope",
                ],
                "reading": "Concept membership must be treated as point-in-time and bounded, not as a permanent static tag.",
            },
        ]
        summary = {
            "acceptance_posture": (
                "freeze_v13_concept_mapping_inventory_v1"
                if ready_now
                else "hold_v13_concept_mapping_inventory_until_charter_is_open"
            ),
            "section_count": len(inventory_sections),
            "mapping_mode_count": 6,
            "requires_point_in_time_mapping": True,
            "requires_market_confirmation_layer": True,
            "market_context_fill_available": bool(fill_summary.get("market_context_filled_count", 0) > 0),
            "ready_for_bounded_concept_seed_next": ready_now,
        }
        interpretation = [
            "V1.3 should begin from concept-mapping infrastructure because concept stocks in A-share often trade on market-recognized theme overlays rather than on static industry labels.",
            "That means the first bounded inventory must freeze mapping modes, source quality, point-in-time bounds, and market-confirmation requirements before any larger registry build starts.",
            "The next legal action after this inventory is a bounded concept-seed, not direct ingestion or direct model work.",
        ]
        return V13ConceptMappingInventoryReport(
            summary=summary,
            inventory_sections=inventory_sections,
            interpretation=interpretation,
        )


def write_v13_concept_mapping_inventory_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V13ConceptMappingInventoryReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
