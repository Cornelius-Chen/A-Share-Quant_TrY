from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class FeaturePackATriageReport:
    summary: dict[str, Any]
    case_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "case_rows": self.case_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class FeaturePackATriageAnalyzer:
    """Split feature-pack-a suspects into the smallest plausible next refinement tracks."""

    def analyze(self, *, recheck_report_path: Path) -> FeaturePackATriageReport:
        payload = load_json_report(recheck_report_path)
        rows = list(payload.get("case_rows", []))
        grouped: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            grouped.setdefault(str(row["case_name"]), []).append(row)

        case_rows = [self._analyze_case(case_name, case_rows) for case_name, case_rows in sorted(grouped.items())]
        classification_counts: dict[str, int] = {}
        for row in case_rows:
            classification = str(row["triage_classification"])
            classification_counts[classification] = classification_counts.get(classification, 0) + 1

        summary = {
            "case_count": len(case_rows),
            "classification_counts": classification_counts,
            "next_step": "split_feature_pack_b_by_case_type" if case_rows else "no_cases",
            "recommended_tracks": sorted({str(row["recommended_track"]) for row in case_rows}),
        }
        interpretation = [
            "A hierarchy/approval-edge case should not be advanced with more concept features first.",
            "A concept-supported hierarchy case deserves concept-aware hierarchy features before replay resumes.",
            "The purpose of triage is to split the next feature cycle, not to reopen the replay queue.",
        ]
        return FeaturePackATriageReport(
            summary=summary,
            case_rows=case_rows,
            interpretation=interpretation,
        )

    def _analyze_case(self, case_name: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
        row_count = len(rows)
        late_quality_straddles = sum(bool(row.get("late_quality_straddle")) for row in rows)
        non_junk_straddles = sum(bool(row.get("non_junk_straddle")) for row in rows)
        top_score_straddles = sum(bool(row.get("top_score_straddle")) for row in rows)
        permission_split_rows = sum(
            row.get("incumbent_permission_allowed") != row.get("challenger_permission_allowed")
            for row in rows
        )
        zero_concept_rows = sum(float(row.get("concept_support", 0.0)) <= 0.0 for row in rows)
        concept_active_rows = sum(float(row.get("concept_support", 0.0)) >= 0.2 for row in rows)
        avg_concept_support = round(
            sum(float(row.get("concept_support", 0.0)) for row in rows) / max(row_count, 1),
            6,
        )
        max_concept_count = max(int(row.get("concept_count", 0)) for row in rows) if rows else 0
        max_concentration = round(
            max(float(row.get("concept_concentration_ratio", 0.0)) for row in rows) if rows else 0.0,
            6,
        )

        if zero_concept_rows == row_count and (late_quality_straddles or non_junk_straddles or permission_split_rows):
            triage_classification = "hierarchy_approval_edge"
            recommended_track = "feature_pack_b_hierarchy_approval"
            next_focus = [
                "fallback_reason_score",
                "approval_hysteresis_state",
                "switch_buffer_pressure",
                "late_mover_quality_margin",
                "non_junk_composite_margin",
            ]
        elif concept_active_rows == row_count and max_concept_count >= 2 and (
            late_quality_straddles or non_junk_straddles
        ):
            triage_classification = "concept_supported_hierarchy_edge"
            recommended_track = "feature_pack_b_concept_supported_hierarchy"
            next_focus = [
                "primary_concept_support_margin",
                "secondary_concept_support_margin",
                "concept_rotation_pressure",
                "concept_concentration_ratio",
                "late_mover_quality_margin",
            ]
        else:
            triage_classification = "undetermined_feature_edge"
            recommended_track = "manual_review_before_feature_pack_b"
            next_focus = [
                "manual_case_review",
                "threshold_edge_replay",
            ]

        return {
            "case_name": case_name,
            "row_count": row_count,
            "datasets": sorted({str(row["dataset_name"]) for row in rows}),
            "strategies": sorted({str(row["strategy_name"]) for row in rows}),
            "symbols": sorted({str(row["symbol"]) for row in rows}),
            "mechanism_types": sorted({str(row["mechanism_type"]) for row in rows}),
            "late_quality_straddles": late_quality_straddles,
            "non_junk_straddles": non_junk_straddles,
            "top_score_straddles": top_score_straddles,
            "permission_split_rows": permission_split_rows,
            "zero_concept_rows": zero_concept_rows,
            "concept_active_rows": concept_active_rows,
            "avg_concept_support": avg_concept_support,
            "max_concept_count": max_concept_count,
            "max_concept_concentration_ratio": max_concentration,
            "triage_classification": triage_classification,
            "recommended_track": recommended_track,
            "next_focus_features": next_focus,
        }


def write_feature_pack_a_triage_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: FeaturePackATriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
