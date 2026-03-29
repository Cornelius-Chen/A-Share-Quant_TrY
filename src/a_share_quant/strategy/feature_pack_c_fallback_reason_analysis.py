from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class FeaturePackCFallbackReasonAnalysisReport:
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


def _positive_deficit(margin: float) -> float:
    return round(max(0.0, -margin), 6)


class FeaturePackCFallbackReasonAnalyzer:
    """Decompose fallback rows into local causal deficit types."""

    def analyze(
        self,
        *,
        recheck_payload: dict[str, Any],
        case_names: list[str],
    ) -> FeaturePackCFallbackReasonAnalysisReport:
        case_rows: list[dict[str, Any]] = []
        dominant_counts: dict[str, int] = {}
        approval_active_count = 0
        concept_supported_count = 0

        for row in recheck_payload.get("case_rows", []):
            case_name = str(row.get("case_name"))
            if case_name not in case_names:
                continue

            late_deficit = _positive_deficit(float(row.get("challenger_late_quality_margin", 0.0)))
            non_junk_deficit = _positive_deficit(float(row.get("challenger_non_junk_margin", 0.0)))
            resonance_deficit = _positive_deficit(float(row.get("challenger_resonance_margin", 0.0)))
            top_score_deficit = _positive_deficit(float(row.get("challenger_top_score_gap", 0.0)))
            margin_deficit = _positive_deficit(float(row.get("challenger_margin_gap", 0.0)))

            components = {
                "late_quality": late_deficit,
                "non_junk": non_junk_deficit,
                "resonance": resonance_deficit,
                "top_score": top_score_deficit,
                "score_margin": margin_deficit,
            }
            dominant_component = max(components, key=lambda key: components[key])
            if components[dominant_component] <= 0:
                dominant_component = "none"
            dominant_counts[dominant_component] = dominant_counts.get(dominant_component, 0) + 1

            approval_edge_active = top_score_deficit > 0 or margin_deficit > 0
            concept_supported = float(row.get("concept_support", 0.0)) > 0
            if approval_edge_active:
                approval_active_count += 1
            if concept_supported:
                concept_supported_count += 1

            case_rows.append(
                {
                    "case_name": case_name,
                    "trigger_date": row.get("trigger_date"),
                    "mechanism_type": row.get("mechanism_type"),
                    "challenger_assignment_reason": row.get("challenger_assignment_reason"),
                    "dominant_component": dominant_component,
                    "late_quality_deficit": late_deficit,
                    "non_junk_deficit": non_junk_deficit,
                    "resonance_deficit": resonance_deficit,
                    "top_score_deficit": top_score_deficit,
                    "score_margin_deficit": margin_deficit,
                    "approval_edge_active": approval_edge_active,
                    "concept_supported": concept_supported,
                    "fallback_reason_score": row.get("fallback_reason_score"),
                }
            )

        case_rows.sort(key=lambda item: (str(item["case_name"]), str(item["trigger_date"])))
        summary = {
            "case_count": len(case_names),
            "row_count": len(case_rows),
            "dominant_component_counts": dominant_counts,
            "approval_edge_active_count": approval_active_count,
            "concept_supported_count": concept_supported_count,
            "recommended_first_feature_group": self._recommended_first_group(
                dominant_counts=dominant_counts,
                approval_active_count=approval_active_count,
                concept_supported_count=concept_supported_count,
            ),
        }
        interpretation = [
            "Feature-pack-c should start by decomposing fallback rows into causal deficit types rather than widening thresholds again.",
            "If late-quality deficits dominate, the next useful feature group is likely late-quality residual structure rather than generic concept support.",
            "Approval-edge activation matters only when score deficits co-occur with fallback rows; otherwise the blocker is mostly hierarchy-side.",
        ]
        return FeaturePackCFallbackReasonAnalysisReport(
            summary=summary,
            case_rows=case_rows,
            interpretation=interpretation,
        )

    def _recommended_first_group(
        self,
        *,
        dominant_counts: dict[str, int],
        approval_active_count: int,
        concept_supported_count: int,
    ) -> str:
        late_count = dominant_counts.get("late_quality", 0)
        non_junk_count = dominant_counts.get("non_junk", 0)
        resonance_count = dominant_counts.get("resonance", 0)
        if late_count >= max(non_junk_count, resonance_count) and approval_active_count > 0:
            return "fallback_reason_decomposition_plus_late_quality_residuals"
        if late_count >= max(non_junk_count, resonance_count):
            return "late_quality_residual_components"
        if concept_supported_count > 0:
            return "concept_support_excess_to_late_threshold"
        return "fallback_reason_decomposition"


def write_feature_pack_c_fallback_reason_analysis_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: FeaturePackCFallbackReasonAnalysisReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
