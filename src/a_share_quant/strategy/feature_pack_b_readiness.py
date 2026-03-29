from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class FeaturePackBReadinessReport:
    summary: dict[str, Any]
    track_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "track_rows": self.track_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class FeaturePackBReadinessAnalyzer:
    """Turn feature-pack-a triage results into concrete feature-pack-b tracks."""

    def analyze(
        self,
        *,
        triage_report_path: Path,
        recheck_report_path: Path,
    ) -> FeaturePackBReadinessReport:
        triage_payload = load_json_report(triage_report_path)
        recheck_payload = load_json_report(recheck_report_path)
        recheck_rows = list(recheck_payload.get("case_rows", []))
        by_case: dict[str, list[dict[str, Any]]] = {}
        for row in recheck_rows:
            by_case.setdefault(str(row["case_name"]), []).append(row)

        track_rows = []
        for triage_row in triage_payload.get("case_rows", []):
            case_name = str(triage_row["case_name"])
            case_rows = by_case.get(case_name, [])
            track_rows.append(self._analyze_track(triage_row, case_rows))

        track_rows.sort(key=lambda row: (-float(row["priority_score"]), str(row["case_name"])))
        summary = {
            "track_count": len(track_rows),
            "recommended_execution_order": [row["case_name"] for row in track_rows],
            "first_track": track_rows[0]["case_name"] if track_rows else None,
            "first_track_reason": track_rows[0]["priority_reason"] if track_rows else None,
        }
        interpretation = [
            "Run the cleaner hierarchy/approval track first when concept coverage is zero and the edge is already visible without theme support.",
            "Run the concept-supported hierarchy track second when the remaining uncertainty is about how concept support should bridge into hierarchy admission.",
            "Feature-pack-b should stay sequential: prove one track, then decide whether the second track still changes the family boundary.",
        ]
        return FeaturePackBReadinessReport(
            summary=summary,
            track_rows=track_rows,
            interpretation=interpretation,
        )

    def _analyze_track(
        self,
        triage_row: dict[str, Any],
        case_rows: list[dict[str, Any]],
    ) -> dict[str, Any]:
        classification = str(triage_row["triage_classification"])
        late_quality_straddles = sum(bool(row.get("late_quality_straddle")) for row in case_rows)
        non_junk_straddles = sum(bool(row.get("non_junk_straddle")) for row in case_rows)
        permission_split_rows = sum(
            row.get("incumbent_permission_allowed") != row.get("challenger_permission_allowed")
            for row in case_rows
        )
        fallback_rows = sum(
            str(row.get("challenger_assignment_reason")) in {"fallback_to_junk", "low_composite_or_low_resonance"}
            for row in case_rows
        )
        concept_supported_late_rows = sum(
            float(row.get("concept_support", 0.0)) >= 0.2 and bool(row.get("late_quality_straddle"))
            for row in case_rows
        )
        concept_supported_non_junk_rows = sum(
            float(row.get("concept_support", 0.0)) >= 0.2 and bool(row.get("non_junk_straddle"))
            for row in case_rows
        )

        if classification == "hierarchy_approval_edge":
            dominant_bottleneck = "late_quality_and_permission_edge"
            if permission_split_rows > late_quality_straddles:
                dominant_bottleneck = "permission_edge"
            priority_score = 0.9 + (late_quality_straddles * 0.02) + (permission_split_rows * 0.01)
            priority_reason = "cleanest non-concept edge; best first target for a narrow feature-pack-b"
            recommended_focus = [
                "fallback_reason_score",
                "approval_hysteresis_state",
                "switch_buffer_pressure",
                "late_mover_quality_margin",
                "non_junk_composite_margin",
            ]
        elif classification == "concept_supported_hierarchy_edge":
            dominant_bottleneck = "concept_to_hierarchy_bridge"
            if concept_supported_non_junk_rows > concept_supported_late_rows:
                dominant_bottleneck = "concept_to_non_junk_bridge"
            priority_score = 0.7 + (concept_supported_late_rows * 0.03) + (concept_supported_non_junk_rows * 0.02)
            priority_reason = "strong second target after the cleaner hierarchy edge is settled"
            recommended_focus = [
                "primary_concept_support_margin",
                "secondary_concept_support_margin",
                "concept_rotation_pressure",
                "concept_concentration_ratio",
                "late_mover_quality_margin",
            ]
        else:
            dominant_bottleneck = "manual_review"
            priority_score = 0.2
            priority_reason = "classification is not clean enough for automatic feature-pack-b promotion"
            recommended_focus = list(triage_row.get("next_focus_features", []))

        return {
            "case_name": str(triage_row["case_name"]),
            "triage_classification": classification,
            "dominant_bottleneck": dominant_bottleneck,
            "late_quality_straddles": late_quality_straddles,
            "non_junk_straddles": non_junk_straddles,
            "permission_split_rows": permission_split_rows,
            "fallback_rows": fallback_rows,
            "concept_supported_late_rows": concept_supported_late_rows,
            "concept_supported_non_junk_rows": concept_supported_non_junk_rows,
            "recommended_focus_features": recommended_focus,
            "priority_score": round(priority_score, 6),
            "priority_reason": priority_reason,
        }


def write_feature_pack_b_readiness_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: FeaturePackBReadinessReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
