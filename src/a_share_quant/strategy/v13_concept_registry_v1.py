from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V13ConceptRegistryReport:
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


class V13ConceptRegistryAnalyzer:
    """Build the first bounded concept registry from seed, source, and confidence rules."""

    def analyze(
        self,
        *,
        concept_seed_payload: dict[str, Any],
        concept_source_fill_payload: dict[str, Any],
        concept_mapping_confidence_payload: dict[str, Any],
    ) -> V13ConceptRegistryReport:
        seed_rows = list(concept_seed_payload.get("seed_rows", []))
        source_rows = list(concept_source_fill_payload.get("fill_rows", []))
        confidence_summary = dict(concept_mapping_confidence_payload.get("summary", {}))

        seed_by_lane = {str(row.get("lane_id", "")): row for row in seed_rows}
        registry_rows: list[dict[str, Any]] = []
        for source_row in source_rows:
            lane_id = str(source_row.get("lane_id", ""))
            seed_row = dict(seed_by_lane.get(lane_id, {}))
            source_fill_status = str(source_row.get("source_fill_status", ""))
            mapped_context_name = str(source_row.get("mapped_context_name", ""))

            # Current bounded concept rows have theme-scope and resolved source support,
            # but still lack explicit symbol-link proof such as primary business or
            # confirmed investment-holding documentation. Keep them below core_confirmed.
            if source_fill_status == "resolved_official_or_high_trust" and mapped_context_name:
                provisional_mapping_class = "provisional_market_confirmed_indirect"
                registry_allowed_for_bounded_context = True
            else:
                provisional_mapping_class = "watch_only"
                registry_allowed_for_bounded_context = False

            registry_rows.append(
                {
                    "lane_id": lane_id,
                    "symbol": str(source_row.get("symbol", "")),
                    "strategy_name": str(seed_row.get("strategy_name", "")),
                    "slice_name": str(seed_row.get("slice_name", "")),
                    "lane_outcome_label": str(source_row.get("lane_outcome_label", "")),
                    "concept_name": mapped_context_name,
                    "mapping_source": str(seed_row.get("mapping_source", "")),
                    "source_authority_tier": str(source_row.get("source_authority_tier", "")),
                    "policy_scope": str(source_row.get("policy_scope", "")),
                    "execution_strength": str(source_row.get("execution_strength", "")),
                    "rumor_risk_level": str(source_row.get("rumor_risk_level", "")),
                    "primary_source_ref": str(source_row.get("primary_source_ref", "")),
                    "persistence_class": str(source_row.get("persistence_class", "")),
                    "symbol_link_mode": "pending_manual_assignment",
                    "mapping_confidence_status": "provisional_pending_link_mode",
                    "final_mapping_class": provisional_mapping_class,
                    "allowed_for_bounded_context": registry_allowed_for_bounded_context,
                }
            )

        allowed_rows = [row for row in registry_rows if bool(row["allowed_for_bounded_context"])]
        summary = {
            "acceptance_posture": "open_v13_concept_registry_v1_as_bounded_provisional_registry",
            "row_count": len(registry_rows),
            "allowed_for_bounded_context_count": len(allowed_rows),
            "provisional_market_confirmed_indirect_count": sum(
                1 for row in registry_rows if row["final_mapping_class"] == "provisional_market_confirmed_indirect"
            ),
            "pending_manual_link_mode_count": sum(
                1 for row in registry_rows if row["symbol_link_mode"] == "pending_manual_assignment"
            ),
            "core_confirmed_count": sum(
                1 for row in registry_rows if row["final_mapping_class"] == "core_confirmed"
            ),
            "confidence_rules_frozen": bool(
                confidence_summary.get("acceptance_posture")
                == "freeze_v13_concept_mapping_confidence_and_symbol_link_rules_v1"
            ),
            "ready_for_bounded_link_mode_assignment_next": len(registry_rows) > 0,
        }
        interpretation = [
            "The first bounded concept registry should be consumable but still conservative.",
            "Because current rows are theme-scoped and source-resolved but do not yet carry explicit symbol-link proof, they remain provisional and indirect rather than core-confirmed.",
            "The next legal action is bounded manual link-mode assignment, not strategy integration or wide concept expansion.",
        ]
        return V13ConceptRegistryReport(
            summary=summary,
            registry_rows=registry_rows,
            interpretation=interpretation,
        )


def write_v13_concept_registry_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V13ConceptRegistryReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
