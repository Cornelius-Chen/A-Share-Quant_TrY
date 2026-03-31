from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V13ConceptLinkModeAssignmentReport:
    summary: dict[str, Any]
    assignment_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "assignment_rows": self.assignment_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V13ConceptLinkModeAssignmentAnalyzer:
    """Apply bounded manual link-mode assignments to the provisional concept registry."""

    def analyze(
        self,
        *,
        registry_payload: dict[str, Any],
        assignments: list[dict[str, Any]],
    ) -> V13ConceptLinkModeAssignmentReport:
        registry_rows = list(registry_payload.get("registry_rows", []))
        registry_by_lane = {str(row.get("lane_id", "")): dict(row) for row in registry_rows}

        assignment_rows: list[dict[str, Any]] = []
        for item in assignments:
            lane_id = str(item.get("lane_id", ""))
            registry_row = dict(registry_by_lane.get(lane_id, {}))
            if not registry_row:
                raise ValueError(f"Lane {lane_id} is not present in the bounded concept registry.")

            symbol_link_mode = str(item.get("symbol_link_mode", ""))
            if symbol_link_mode not in {
                "primary_business",
                "investment_holding",
                "supply_chain",
                "order_or_customer",
                "platform_or_ecosystem",
                "rumor_only",
            }:
                raise ValueError(f"Unsupported symbol_link_mode for {lane_id}: {symbol_link_mode}")

            if symbol_link_mode == "primary_business":
                final_mapping_class = "core_confirmed"
                mapping_confidence_status = "manually_confirmed_primary_business"
            elif symbol_link_mode in {"investment_holding", "supply_chain", "order_or_customer", "platform_or_ecosystem"}:
                final_mapping_class = "market_confirmed_indirect"
                mapping_confidence_status = "manually_confirmed_indirect_link"
            else:
                final_mapping_class = "rumor_only_unconfirmed"
                mapping_confidence_status = "manual_assignment_low_confidence"

            assignment_rows.append(
                {
                    **registry_row,
                    "symbol_link_mode": symbol_link_mode,
                    "mapping_confidence_status": mapping_confidence_status,
                    "final_mapping_class": final_mapping_class,
                    "allowed_for_bounded_context": final_mapping_class
                    in {"core_confirmed", "market_confirmed_indirect"},
                    "assignment_basis": str(item.get("assignment_basis", "")),
                    "assignment_source_ref": str(item.get("assignment_source_ref", "")),
                    "assignment_notes": str(item.get("assignment_notes", "")),
                }
            )

        summary = {
            "acceptance_posture": "open_v13_concept_link_mode_assignment_v1_as_bounded_manual_assignment",
            "row_count": len(assignment_rows),
            "core_confirmed_count": sum(1 for row in assignment_rows if row["final_mapping_class"] == "core_confirmed"),
            "market_confirmed_indirect_count": sum(
                1 for row in assignment_rows if row["final_mapping_class"] == "market_confirmed_indirect"
            ),
            "rumor_only_unconfirmed_count": sum(
                1 for row in assignment_rows if row["final_mapping_class"] == "rumor_only_unconfirmed"
            ),
            "allowed_for_bounded_context_count": sum(
                1 for row in assignment_rows if bool(row["allowed_for_bounded_context"])
            ),
            "pending_manual_assignment_count": 0,
            "ready_for_registry_reclassification_next": len(assignment_rows) > 0,
        }
        interpretation = [
            "This bounded manual assignment step upgrades the concept registry only where symbol-link proof is explicit enough to justify it.",
            "Primary-business links can now become `core_confirmed`, while ecosystem or indirect relationships remain `market_confirmed_indirect`.",
            "The branch is still bounded: this is registry hygiene, not strategy integration.",
        ]
        return V13ConceptLinkModeAssignmentReport(
            summary=summary,
            assignment_rows=assignment_rows,
            interpretation=interpretation,
        )


def write_v13_concept_link_mode_assignment_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V13ConceptLinkModeAssignmentReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
