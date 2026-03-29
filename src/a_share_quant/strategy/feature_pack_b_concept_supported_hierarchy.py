from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class FeaturePackBConceptSupportedHierarchyReport:
    summary: dict[str, Any]
    case_row: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "case_row": self.case_row,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class FeaturePackBConceptSupportedHierarchyAnalyzer:
    """Focus track B on the concept-supported hierarchy suspect after track A is settled."""

    def analyze(self, *, recheck_report_path: Path, case_name: str) -> FeaturePackBConceptSupportedHierarchyReport:
        payload = load_json_report(recheck_report_path)
        rows = [row for row in payload.get("case_rows", []) if str(row["case_name"]) == case_name]
        if not rows:
            raise ValueError(f"Case {case_name} not found in {recheck_report_path}")

        late_quality_straddles = sum(bool(row.get("late_quality_straddle")) for row in rows)
        non_junk_straddles = sum(bool(row.get("non_junk_straddle")) for row in rows)
        concept_supported_late_rows = sum(
            float(row.get("concept_support", 0.0)) >= 0.2 and bool(row.get("late_quality_straddle"))
            for row in rows
        )
        concept_supported_non_junk_rows = sum(
            float(row.get("concept_support", 0.0)) >= 0.2 and bool(row.get("non_junk_straddle"))
            for row in rows
        )
        avg_concept_support = round(
            sum(float(row.get("concept_support", 0.0)) for row in rows) / len(rows),
            6,
        )
        avg_primary_weight = round(
            sum(float(row.get("primary_concept_weight", 0.0)) for row in rows) / len(rows),
            6,
        )
        avg_concentration = round(
            sum(float(row.get("concept_concentration_ratio", 0.0)) for row in rows) / len(rows),
            6,
        )
        avg_late_margin = round(
            sum(float(row.get("challenger_late_quality_margin", 0.0)) for row in rows) / len(rows),
            6,
        )
        avg_non_junk_margin = round(
            sum(float(row.get("challenger_non_junk_margin", 0.0)) for row in rows) / len(rows),
            6,
        )

        dominant_bridge = "concept_to_late_mover"
        if concept_supported_non_junk_rows > concept_supported_late_rows:
            dominant_bridge = "concept_to_non_junk"
        elif concept_supported_non_junk_rows == concept_supported_late_rows and avg_non_junk_margin < avg_late_margin:
            dominant_bridge = "concept_to_non_junk"

        summary = {
            "case_name": case_name,
            "row_count": len(rows),
            "dominant_bridge": dominant_bridge,
            "late_quality_straddles": late_quality_straddles,
            "non_junk_straddles": non_junk_straddles,
            "concept_supported_late_rows": concept_supported_late_rows,
            "concept_supported_non_junk_rows": concept_supported_non_junk_rows,
            "avg_concept_support": avg_concept_support,
            "avg_primary_concept_weight": avg_primary_weight,
            "avg_concept_concentration_ratio": avg_concentration,
            "avg_challenger_late_quality_margin": avg_late_margin,
            "avg_challenger_non_junk_margin": avg_non_junk_margin,
            "recommended_focus": [
                "primary_concept_support_margin",
                "secondary_concept_support_margin",
                "concept_rotation_pressure",
                "concept_concentration_ratio",
                "late_mover_quality_margin",
                "non_junk_composite_margin",
            ],
        }
        interpretation = [
            "Track B should stay concept-aware: the question is not whether hierarchy matters, but how concept support should bridge into hierarchy admission.",
            "When concept-supported late rows and non-junk rows both appear, the dominant bridge should be chosen by the tighter negative margin.",
            "This track should not open a replay loop; it should only decide which concept-to-hierarchy bridge deserves the next feature pack.",
        ]
        return FeaturePackBConceptSupportedHierarchyReport(
            summary=summary,
            case_row={"case_name": case_name, "rows": rows},
            interpretation=interpretation,
        )


def write_feature_pack_b_concept_supported_hierarchy_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: FeaturePackBConceptSupportedHierarchyReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
