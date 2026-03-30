from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.common.config import load_yaml_config


@dataclass(slots=True)
class CatalystEventRegistrySourceFillReport:
    summary: dict[str, Any]
    fill_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "fill_rows": self.fill_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class CatalystEventRegistrySourceFillAnalyzer:
    """Apply a first bounded official/high-trust source fill over the market-context catalyst registry."""

    def analyze(
        self,
        *,
        market_context_fill_payload: dict[str, Any],
        source_entries: list[dict[str, Any]],
    ) -> CatalystEventRegistrySourceFillReport:
        entry_map = {
            str(entry["lane_id"]): dict(entry)
            for entry in source_entries
        }
        fill_rows: list[dict[str, Any]] = []
        resolved_count = 0
        unresolved_count = 0

        for row in list(market_context_fill_payload.get("fill_rows", [])):
            lane_id = str(row.get("lane_id", ""))
            source_entry = entry_map.get(lane_id)
            if source_entry is None:
                fill_rows.append(
                    {
                        **row,
                        "source_fill_status": "unresolved",
                        "source_authority_tier": "unresolved",
                        "primary_source_ref": "",
                        "policy_scope": "unresolved",
                        "execution_strength": "unresolved",
                        "rumor_risk_level": "unresolved",
                    }
                )
                unresolved_count += 1
                continue

            fill_rows.append(
                {
                    **row,
                    "source_fill_status": str(source_entry["source_fill_status"]),
                    "source_authority_tier": str(source_entry["source_authority_tier"]),
                    "primary_source_ref": str(source_entry["primary_source_ref"]),
                    "policy_scope": str(source_entry["policy_scope"]),
                    "execution_strength": str(source_entry["execution_strength"]),
                    "rumor_risk_level": str(source_entry["rumor_risk_level"]),
                    "source_fill_notes": str(source_entry.get("notes", "")),
                }
            )
            if str(source_entry["source_fill_status"]) == "resolved_official_or_high_trust":
                resolved_count += 1
            else:
                unresolved_count += 1

        summary = {
            "fill_posture": "open_catalyst_event_registry_source_fill_v1_as_partial_source_layer",
            "row_count": len(fill_rows),
            "resolved_source_count": resolved_count,
            "unresolved_source_count": unresolved_count,
            "full_source_coverage_present": unresolved_count == 0,
            "ready_for_bounded_catalyst_context_audit": resolved_count > 0,
        }
        interpretation = [
            "The first source fill should accept partial coverage instead of forcing weak guesses onto every lane.",
            "Rows with clear official or high-trust industry context can now move beyond market-context-only status, while unresolved rows stay explicitly unresolved.",
            "This keeps the catalyst branch honest and still lets a first bounded context audit open later.",
        ]
        return CatalystEventRegistrySourceFillReport(
            summary=summary,
            fill_rows=fill_rows,
            interpretation=interpretation,
        )


def write_catalyst_event_registry_source_fill_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: CatalystEventRegistrySourceFillReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def load_catalyst_event_registry_source_fill_config(
    path: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]], Path, str]:
    payload = load_yaml_config(path)
    market_context_fill_payload = load_json_report(Path(payload["paths"]["market_context_fill_report"]))
    source_entries = list(payload["source_entries"])
    reports_dir = Path(payload["paths"]["reports_dir"])
    report_name = str(payload["report"]["name"])
    return market_context_fill_payload, source_entries, reports_dir, report_name
