from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V13ConceptRegistryReclassificationReport:
    summary: dict[str, Any]
    registry_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "registry_rows": self.registry_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V13ConceptRegistryReclassificationAnalyzer:
    """Apply bounded manual link-mode assignments to the provisional concept registry."""

    def analyze(
        self,
        *,
        concept_registry_payload: dict[str, Any],
        link_mode_assignment_payload: dict[str, Any],
    ) -> V13ConceptRegistryReclassificationReport:
        registry_rows = list(concept_registry_payload.get("registry_rows", []))
        assignment_rows = list(link_mode_assignment_payload.get("assignment_rows", []))

        registry_by_lane = {str(row.get("lane_id", "")): dict(row) for row in registry_rows}
        reclassified_rows: list[dict[str, Any]] = []
        for assigned_row in assignment_rows:
            lane_id = str(assigned_row.get("lane_id", ""))
            if lane_id not in registry_by_lane:
                raise ValueError(f"Lane {lane_id} is not present in the bounded concept registry.")
            reclassified_rows.append({**registry_by_lane[lane_id], **dict(assigned_row)})

        summary = {
            "acceptance_posture": "open_v13_concept_registry_reclassification_v1_as_bounded_reclassified_registry",
            "row_count": len(reclassified_rows),
            "core_confirmed_count": sum(
                1 for row in reclassified_rows if row.get("final_mapping_class") == "core_confirmed"
            ),
            "market_confirmed_indirect_count": sum(
                1 for row in reclassified_rows if row.get("final_mapping_class") == "market_confirmed_indirect"
            ),
            "rumor_only_unconfirmed_count": sum(
                1 for row in reclassified_rows if row.get("final_mapping_class") == "rumor_only_unconfirmed"
            ),
            "allowed_for_bounded_context_count": sum(
                1 for row in reclassified_rows if bool(row.get("allowed_for_bounded_context"))
            ),
            "provisional_row_count": sum(
                1
                for row in reclassified_rows
                if str(row.get("final_mapping_class", "")).startswith("provisional_")
            ),
            "ready_for_usage_rules_next": len(reclassified_rows) > 0,
        }
        interpretation = [
            "The concept registry is now reclassified with explicit link-mode proof instead of staying fully provisional.",
            "Core-confirmed rows remain bounded infrastructure artifacts, not direct strategy features.",
            "The next legal step is to freeze how core-confirmed and market-confirmed-indirect rows may be consumed.",
        ]
        return V13ConceptRegistryReclassificationReport(
            summary=summary,
            registry_rows=reclassified_rows,
            interpretation=interpretation,
        )


def write_v13_concept_registry_reclassification_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V13ConceptRegistryReclassificationReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
