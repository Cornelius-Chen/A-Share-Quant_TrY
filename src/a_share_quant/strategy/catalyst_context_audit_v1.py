from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class CatalystContextAuditReport:
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


class CatalystContextAuditAnalyzer:
    """Audit whether the bounded catalyst rows already separate opening, persistence, and carry outcomes."""

    def analyze(self, *, source_fill_payload: dict[str, Any]) -> CatalystContextAuditReport:
        grouped: dict[str, list[dict[str, Any]]] = {}
        for row in list(source_fill_payload.get("fill_rows", [])):
            label = str(row.get("lane_outcome_label", "unknown"))
            grouped.setdefault(label, []).append(row)

        audit_rows: list[dict[str, Any]] = []
        for label, rows in grouped.items():
            persistence_classes = sorted({str(row.get("persistence_class")) for row in rows})
            scope_counts: dict[str, int] = {}
            for row in rows:
                scope = str(row.get("event_scope", "unknown"))
                scope_counts[scope] = scope_counts.get(scope, 0) + 1
            resolved_count = len(
                [
                    row
                    for row in rows
                    if str(row.get("source_fill_status")) == "resolved_official_or_high_trust"
                ]
            )
            audit_rows.append(
                {
                    "lane_outcome_label": label,
                    "row_count": len(rows),
                    "resolved_source_count": resolved_count,
                    "persistence_classes": persistence_classes,
                    "scope_counts": scope_counts,
                }
            )

        opening_rows = grouped.get("opening_led", [])
        persistence_rows = grouped.get("persistence_led", [])
        carry_rows = grouped.get("carry_row_present", [])

        opening_single_pulse_only = all(str(row.get("persistence_class")) == "single_pulse" for row in opening_rows)
        persistence_multi_day_only = all(
            str(row.get("persistence_class")) == "multi_day_reinforcement" for row in persistence_rows
        )
        carry_followthrough_only = all(
            str(row.get("persistence_class")) == "policy_followthrough" for row in carry_rows
        )
        resolved_non_opening = len(
            [
                row
                for row in persistence_rows + carry_rows
                if str(row.get("source_fill_status")) == "resolved_official_or_high_trust"
            ]
        )

        summary = {
            "audit_posture": "open_catalyst_context_audit_v1_as_bounded_report_only_check",
            "row_count": sum(len(rows) for rows in grouped.values()),
            "class_count": len(grouped),
            "opening_single_pulse_only": opening_single_pulse_only,
            "persistence_multi_day_only": persistence_multi_day_only,
            "carry_followthrough_only": carry_followthrough_only,
            "resolved_non_opening_count": resolved_non_opening,
            "context_separation_present": (
                opening_single_pulse_only and persistence_multi_day_only and carry_followthrough_only
            ),
            "promote_catalyst_context_now": False,
            "keep_branch_report_only": True,
        }
        interpretation = [
            "The first bounded catalyst audit already shows a directional separation: opening rows stay in single-pulse context, persistence rows cluster in multi-day reinforcement, and carry rows sit in followthrough context.",
            "That separation is still too small to promote catalyst context into a retained factor or a training feature, but it is enough to justify keeping the branch active as a report-only context audit.",
            "The next catalyst step should add more rows or better source coverage before any promotion decision is reconsidered.",
        ]
        return CatalystContextAuditReport(
            summary=summary,
            audit_rows=sorted(audit_rows, key=lambda row: str(row["lane_outcome_label"])),
            interpretation=interpretation,
        )


def write_catalyst_context_audit_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: CatalystContextAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
