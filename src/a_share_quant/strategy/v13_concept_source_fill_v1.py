from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V13ConceptSourceFillReport:
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


class V13ConceptSourceFillAnalyzer:
    """Lift bounded concept seed rows onto the existing catalyst source layer."""

    def analyze(
        self,
        *,
        concept_seed_payload: dict[str, Any],
        source_fill_payload: dict[str, Any],
    ) -> V13ConceptSourceFillReport:
        seed_rows = list(concept_seed_payload.get("seed_rows", []))
        source_fill_rows = list(source_fill_payload.get("fill_rows", []))
        source_by_lane = {str(row.get("lane_id", "")): row for row in source_fill_rows}

        fill_rows: list[dict[str, Any]] = []
        for seed_row in seed_rows:
            lane_id = str(seed_row.get("lane_id", ""))
            source_row = dict(source_by_lane.get(lane_id, {}))
            if not source_row:
                continue
            fill_rows.append(
                {
                    "lane_id": lane_id,
                    "symbol": str(source_row.get("symbol", "")),
                    "lane_outcome_label": str(source_row.get("lane_outcome_label", "")),
                    "mapped_context_name": str(source_row.get("mapped_context_name", "")),
                    "source_authority_tier": str(source_row.get("source_authority_tier", "")),
                    "policy_scope": str(source_row.get("policy_scope", "")),
                    "execution_strength": str(source_row.get("execution_strength", "")),
                    "rumor_risk_level": str(source_row.get("rumor_risk_level", "")),
                    "primary_source_ref": str(source_row.get("primary_source_ref", "")),
                    "source_fill_status": str(source_row.get("source_fill_status", "")),
                    "persistence_class": str(source_row.get("persistence_class", "")),
                }
            )

        resolved_rows = [
            row for row in fill_rows if str(row.get("source_fill_status", "")) == "resolved_official_or_high_trust"
        ]
        unresolved_rows = [row for row in fill_rows if row not in resolved_rows]
        summary = {
            "acceptance_posture": "open_v13_concept_source_fill_v1_as_bounded_theme_source_layer",
            "row_count": len(fill_rows),
            "resolved_source_count": len(resolved_rows),
            "unresolved_source_count": len(unresolved_rows),
            "all_rows_theme_scoped": True,
            "ready_for_concept_context_audit_next": len(fill_rows) > 0,
        }
        interpretation = [
            "The first concept-source layer should reuse the already bounded catalyst source fill instead of starting a new source-hunting workflow.",
            "That keeps V1.3 narrow while still telling us whether the concept-focused rows already have high-trust support.",
            "The next legal action after this layer is a bounded concept-context audit.",
        ]
        return V13ConceptSourceFillReport(
            summary=summary,
            fill_rows=fill_rows,
            interpretation=interpretation,
        )


def write_v13_concept_source_fill_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V13ConceptSourceFillReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
