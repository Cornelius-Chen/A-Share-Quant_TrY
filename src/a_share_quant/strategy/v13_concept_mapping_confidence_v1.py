from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V13ConceptMappingConfidenceReport:
    summary: dict[str, Any]
    rule_sections: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "rule_sections": self.rule_sections,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V13ConceptMappingConfidenceAnalyzer:
    """Freeze concept mapping confidence and symbol-link rules for V1.3."""

    def analyze(
        self,
        *,
        phase_check_payload: dict[str, Any],
        concept_inventory_payload: dict[str, Any],
        concept_source_fill_payload: dict[str, Any],
    ) -> V13ConceptMappingConfidenceReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        inventory_summary = dict(concept_inventory_payload.get("summary", {}))
        source_fill_summary = dict(concept_source_fill_payload.get("summary", {}))

        ready_now = (
            str(phase_summary.get("acceptance_posture", ""))
            == "keep_v13_active_but_bounded_as_context_infrastructure"
            and bool(inventory_summary.get("concept_mapping_inventory_frozen", False) or inventory_summary.get("requires_point_in_time_mapping"))
            and bool(source_fill_summary.get("row_count", 0) > 0)
        )

        rule_sections = [
            {
                "section_name": "symbol_link_modes",
                "rule_count": 6,
                "rules": [
                    {"link_mode": "primary_business", "default_confidence_tier": "core_confirmed"},
                    {"link_mode": "investment_holding", "default_confidence_tier": "high_but_indirect"},
                    {"link_mode": "supply_chain", "default_confidence_tier": "high_if_confirmed"},
                    {"link_mode": "order_or_customer", "default_confidence_tier": "medium_to_high"},
                    {"link_mode": "platform_or_ecosystem", "default_confidence_tier": "medium"},
                    {"link_mode": "rumor_only", "default_confidence_tier": "low_untradable_without_market_confirmation"},
                ],
                "reading": "Different concept-link types should map to different default confidence tiers rather than share one generic concept tag.",
            },
            {
                "section_name": "source_lift_rules",
                "rule_count": 4,
                "rules": [
                    {"source_quality": "official_announcement", "confidence_lift": "plus_two"},
                    {"source_quality": "company_confirmation", "confidence_lift": "plus_two"},
                    {"source_quality": "high_trust_market_source", "confidence_lift": "plus_one"},
                    {"source_quality": "weak_market_rumor", "confidence_lift": "minus_two"},
                ],
                "reading": "Source quality can raise or lower confidence, but rumor-like mappings should remain capped even with market excitement.",
            },
            {
                "section_name": "market_confirmation_gates",
                "rule_count": 4,
                "rules": [
                    {"gate": "board_breadth_confirmed", "effect": "required_for_market_confirmed_status"},
                    {"gate": "leader_confirmed", "effect": "raises_concept_tradability"},
                    {"gate": "turnover_confirmed", "effect": "raises_market_recognition"},
                    {"gate": "followthrough_or_reacceleration", "effect": "required_for_carry_capable_reading"},
                ],
                "reading": "Concept mapping confidence should not become tradable context until the market confirms the theme beyond a single isolated stock move.",
            },
            {
                "section_name": "final_mapping_classes",
                "rule_count": 4,
                "rules": [
                    {"final_class": "core_confirmed", "allowed_for_bounded_context": True},
                    {"final_class": "market_confirmed_indirect", "allowed_for_bounded_context": True},
                    {"final_class": "watch_only", "allowed_for_bounded_context": False},
                    {"final_class": "rumor_only_unconfirmed", "allowed_for_bounded_context": False},
                ],
                "reading": "Only confirmed or market-confirmed indirect mappings should survive into bounded research context; weak mappings stay watch-only.",
            },
        ]

        summary = {
            "acceptance_posture": (
                "freeze_v13_concept_mapping_confidence_and_symbol_link_rules_v1"
                if ready_now
                else "hold_v13_concept_mapping_confidence_until_inputs_are_ready"
            ),
            "section_count": len(rule_sections),
            "symbol_link_mode_count": 6,
            "final_mapping_class_count": 4,
            "requires_market_confirmation_for_tradable_context": True,
            "ready_for_bounded_concept_registry_next": ready_now,
        }
        interpretation = [
            "V1.3 should not treat every concept relationship equally: primary business, investment holding, supply-chain exposure, and rumor-only links carry different default confidence.",
            "A bounded concept system also needs explicit source lifts and market-confirmation gates so that concept tags become usable only after both source quality and market behavior are checked.",
            "This artifact stays replay-independent and prepares the next legal step: a bounded concept registry built on these confidence rules.",
        ]
        return V13ConceptMappingConfidenceReport(
            summary=summary,
            rule_sections=rule_sections,
            interpretation=interpretation,
        )


def write_v13_concept_mapping_confidence_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V13ConceptMappingConfidenceReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
