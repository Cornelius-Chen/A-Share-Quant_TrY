from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V14BoundedDiscriminationCheckReport:
    summary: dict[str, Any]
    discrimination_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "discrimination_rows": self.discrimination_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V14BoundedDiscriminationCheckAnalyzer:
    """Check whether the bounded V1.4 context features add stable report-only discrimination."""

    def analyze(
        self,
        *,
        context_feature_schema_payload: dict[str, Any],
        concept_usage_rules_payload: dict[str, Any],
        catalyst_context_audit_payload: dict[str, Any],
    ) -> V14BoundedDiscriminationCheckReport:
        schema_summary = dict(context_feature_schema_payload.get("summary", {}))
        usage_rows = list(concept_usage_rules_payload.get("usage_rows", []))
        audit_rows = list(catalyst_context_audit_payload.get("audit_rows", []))

        if not bool(schema_summary.get("ready_for_bounded_discrimination_check_next")):
            raise ValueError("V1.4 context feature schema must explicitly allow a bounded discrimination check next.")

        primary_usage_by_label: dict[str, int] = {}
        secondary_usage_by_label: dict[str, int] = {}
        for row in usage_rows:
            label = str(row.get("lane_outcome_label", ""))
            usage_mode = str(row.get("usage_mode", ""))
            if usage_mode == "bounded_context_primary":
                primary_usage_by_label[label] = primary_usage_by_label.get(label, 0) + 1
            elif usage_mode == "bounded_context_secondary":
                secondary_usage_by_label[label] = secondary_usage_by_label.get(label, 0) + 1

        persistence_class_by_label: dict[str, list[str]] = {}
        for row in audit_rows:
            label = str(row.get("lane_outcome_label", ""))
            persistence_class_by_label[label] = list(row.get("persistence_classes", []))

        discrimination_rows: list[dict[str, Any]] = []
        for label in ("opening_led", "persistence_led", "carry_row_present"):
            persistence_classes = persistence_class_by_label.get(label, [])
            discrimination_rows.append(
                {
                    "lane_outcome_label": label,
                    "single_pulse_support": "single_pulse" in persistence_classes,
                    "multi_day_reinforcement_support": "multi_day_reinforcement" in persistence_classes,
                    "policy_followthrough_support": "policy_followthrough" in persistence_classes,
                    "concept_confirmation_depth_mode": (
                        "primary"
                        if primary_usage_by_label.get(label, 0) > 0
                        else "secondary"
                        if secondary_usage_by_label.get(label, 0) > 0
                        else "none"
                    ),
                    "concept_indirectness_mode": (
                        "indirect_present"
                        if secondary_usage_by_label.get(label, 0) > 0
                        else "core_only"
                        if primary_usage_by_label.get(label, 0) > 0
                        else "none"
                    ),
                }
            )

        opening_row = next(row for row in discrimination_rows if row["lane_outcome_label"] == "opening_led")
        persistence_row = next(row for row in discrimination_rows if row["lane_outcome_label"] == "persistence_led")
        carry_row = next(row for row in discrimination_rows if row["lane_outcome_label"] == "carry_row_present")

        stable_discrimination_present = (
            opening_row["single_pulse_support"]
            and not opening_row["multi_day_reinforcement_support"]
            and not opening_row["policy_followthrough_support"]
            and persistence_row["multi_day_reinforcement_support"]
            and carry_row["policy_followthrough_support"]
        )

        summary = {
            "acceptance_posture": "open_v14_bounded_discrimination_check_v1_as_report_only_review",
            "class_count": len(discrimination_rows),
            "stable_discrimination_present": stable_discrimination_present,
            "opening_single_pulse_supported": opening_row["single_pulse_support"],
            "persistence_multi_day_supported": persistence_row["multi_day_reinforcement_support"],
            "carry_followthrough_supported": carry_row["policy_followthrough_support"],
            "concept_depth_difference_present": (
                opening_row["concept_confirmation_depth_mode"] != persistence_row["concept_confirmation_depth_mode"]
                or opening_row["concept_confirmation_depth_mode"] != carry_row["concept_confirmation_depth_mode"]
            ),
            "promote_context_now": False,
            "ready_for_v14_phase_check_next": True,
        }
        interpretation = [
            "The first bounded discrimination check confirms whether report-only catalyst and concept context separate opening, persistence, and carry in a stable directional way.",
            "A positive result still does not justify strategy integration or retained-feature promotion; it only proves bounded consumption value.",
            "The next legal step is a V1.4 phase-level check, not a model or signal upgrade.",
        ]
        return V14BoundedDiscriminationCheckReport(
            summary=summary,
            discrimination_rows=discrimination_rows,
            interpretation=interpretation,
        )


def write_v14_bounded_discrimination_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V14BoundedDiscriminationCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
