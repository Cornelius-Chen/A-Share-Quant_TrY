from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class CatalystEventRegistrySchemaReport:
    summary: dict[str, Any]
    schema_sections: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "schema_sections": self.schema_sections,
            "interpretation": self.interpretation,
        }


class CatalystEventRegistrySchemaAnalyzer:
    """Freeze the first bounded catalyst/context registry schema."""

    def analyze(self) -> CatalystEventRegistrySchemaReport:
        identity_fields = [
            "lane_id",
            "dataset_name",
            "slice_name",
            "strategy_name",
            "symbol",
            "event_date",
            "window_start",
            "window_end",
        ]
        catalyst_fields = [
            "event_scope",
            "event_type",
            "source_authority_tier",
            "policy_scope",
            "execution_strength",
            "rumor_risk_level",
            "source_tier",
            "primary_source_ref",
        ]
        persistence_fields = [
            "persistence_class",
            "reinforcement_count",
            "confirmation_delay_days",
            "followthrough_window_days",
            "board_pulse_breadth_class",
            "turnover_concentration_class",
        ]
        price_shape_fields = [
            "first_impulse_return_pct",
            "consolidation_days_after_pulse",
            "retrace_depth_vs_ma5",
            "retrace_depth_vs_ma10",
            "reacceleration_present",
            "reacceleration_delay_days",
        ]
        label_fields = [
            "lane_outcome_label",
            "context_posture",
            "notes",
        ]

        schema_sections = [
            {
                "section_name": "identity",
                "field_count": len(identity_fields),
                "fields": identity_fields,
                "reading": "Identity fields tie each catalyst row to a frozen lane and a bounded event window.",
            },
            {
                "section_name": "catalyst_source",
                "field_count": len(catalyst_fields),
                "fields": catalyst_fields,
                "reading": "Catalyst-source fields separate state policy, local policy, official notices, company announcements, media, and rumor-like pulses.",
            },
            {
                "section_name": "persistence_context",
                "field_count": len(persistence_fields),
                "fields": persistence_fields,
                "reading": "Persistence fields capture whether the catalyst is a one-day pulse or a reinforced multi-day context with board confirmation.",
            },
            {
                "section_name": "price_shape_proxy",
                "field_count": len(price_shape_fields),
                "fields": price_shape_fields,
                "reading": "Price-shape proxy fields capture the impulse, consolidation, retrace, and reacceleration pattern after the first catalyst pulse.",
            },
            {
                "section_name": "lane_labels",
                "field_count": len(label_fields),
                "fields": label_fields,
                "reading": "Lane labels preserve the already-frozen lane reading so the catalyst branch explains rather than relitigates the lane.",
            },
        ]

        summary = {
            "schema_posture": "freeze_catalyst_event_registry_schema_v1",
            "section_count": len(schema_sections),
            "total_field_count": sum(int(section["field_count"]) for section in schema_sections),
            "contains_source_authority_tier": True,
            "contains_execution_strength": True,
            "contains_rumor_risk_level": True,
            "contains_consolidation_days_after_pulse": True,
            "contains_reacceleration_present": True,
            "ready_for_bounded_registry_seeding": True,
        }
        interpretation = [
            "Catalyst schema v1 should model source quality, execution strength, and persistence, not just a generic policy/news label.",
            "The most important additions are authority tier, rumor risk, consolidation days, and reacceleration markers because these can separate single-pulse openings from carry-capable contexts.",
            "This schema remains report-only until a bounded catalyst registry shows that these fields change a later factor decision.",
        ]
        return CatalystEventRegistrySchemaReport(
            summary=summary,
            schema_sections=schema_sections,
            interpretation=interpretation,
        )


def write_catalyst_event_registry_schema_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: CatalystEventRegistrySchemaReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
