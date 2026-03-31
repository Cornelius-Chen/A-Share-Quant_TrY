from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V13ConceptRegistryUsageRulesReport:
    summary: dict[str, Any]
    usage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "usage_rows": self.usage_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V13ConceptRegistryUsageRulesAnalyzer:
    """Freeze bounded usage rules for reclassified concept-registry rows."""

    def analyze(self, *, reclassified_registry_payload: dict[str, Any]) -> V13ConceptRegistryUsageRulesReport:
        registry_rows = list(reclassified_registry_payload.get("registry_rows", []))
        usage_rows: list[dict[str, Any]] = []
        for row in registry_rows:
            final_mapping_class = str(row.get("final_mapping_class", ""))
            if final_mapping_class == "core_confirmed":
                usage_mode = "bounded_context_primary"
                can_drive_context = True
                can_override_market_confirmation = False
            elif final_mapping_class == "market_confirmed_indirect":
                usage_mode = "bounded_context_secondary"
                can_drive_context = True
                can_override_market_confirmation = False
            else:
                usage_mode = "not_allowed"
                can_drive_context = False
                can_override_market_confirmation = False

            usage_rows.append(
                {
                    **dict(row),
                    "usage_mode": usage_mode,
                    "can_drive_bounded_context": can_drive_context,
                    "can_override_market_confirmation": can_override_market_confirmation,
                    "allowed_for_strategy_integration": False,
                }
            )

        summary = {
            "acceptance_posture": "freeze_v13_bounded_concept_registry_usage_rules_v1",
            "row_count": len(usage_rows),
            "bounded_context_primary_count": sum(
                1 for row in usage_rows if row.get("usage_mode") == "bounded_context_primary"
            ),
            "bounded_context_secondary_count": sum(
                1 for row in usage_rows if row.get("usage_mode") == "bounded_context_secondary"
            ),
            "strategy_integration_allowed_count": sum(
                1 for row in usage_rows if bool(row.get("allowed_for_strategy_integration"))
            ),
            "ready_for_phase_closure_check_next": len(usage_rows) > 0,
        }
        interpretation = [
            "Core-confirmed concept rows may drive bounded context first, while indirect rows stay secondary.",
            "Even after reclassification, no concept row is allowed to integrate into the strategy mainline.",
            "These usage rules are the bounded contract that keeps V1.3 as infrastructure rather than signal promotion.",
        ]
        return V13ConceptRegistryUsageRulesReport(
            summary=summary,
            usage_rows=usage_rows,
            interpretation=interpretation,
        )


def write_v13_concept_registry_usage_rules_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V13ConceptRegistryUsageRulesReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
