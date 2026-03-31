from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V13ConceptContextAuditReport:
    summary: dict[str, Any]
    audit_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "audit_rows": self.audit_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V13ConceptContextAuditAnalyzer:
    """Run the first bounded audit on the concept-focused source layer."""

    def analyze(self, *, concept_source_fill_payload: dict[str, Any]) -> V13ConceptContextAuditReport:
        fill_rows = list(concept_source_fill_payload.get("fill_rows", []))
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in fill_rows:
            grouped[str(row.get("lane_outcome_label", ""))].append(row)

        audit_rows = []
        for label, rows in sorted(grouped.items()):
            audit_rows.append(
                {
                    "lane_outcome_label": label,
                    "row_count": len(rows),
                    "authority_tiers": sorted({str(row.get("source_authority_tier", "")) for row in rows}),
                    "persistence_classes": sorted({str(row.get("persistence_class", "")) for row in rows}),
                    "context_names": sorted({str(row.get("mapped_context_name", "")) for row in rows}),
                }
            )

        separation_present = len({tuple(row["persistence_classes"]) for row in audit_rows}) == len(audit_rows)
        summary = {
            "acceptance_posture": "open_v13_concept_context_audit_v1_as_bounded_report_only_check",
            "row_count": len(fill_rows),
            "class_count": len(audit_rows),
            "all_rows_resolved_source": all(
                str(row.get("source_fill_status", "")) == "resolved_official_or_high_trust" for row in fill_rows
            ),
            "concept_context_separation_present": separation_present,
            "promote_concept_branch_now": False,
        }
        interpretation = [
            "The first concept-context audit should stay bounded and report-only.",
            "Its job is to check whether theme-scoped concept rows remain separable by persistence class and source layer after concept-focused filtering.",
            "Even if separation is present, promotion is still disallowed at this stage.",
        ]
        return V13ConceptContextAuditReport(
            summary=summary,
            audit_rows=audit_rows,
            interpretation=interpretation,
        )


def write_v13_concept_context_audit_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V13ConceptContextAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
